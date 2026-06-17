from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from trustroom.models import (
    ApprovalDecisionValue,
    ApprovalValidity,
    BusinessOwner,
    CustomerExport,
    CustomerExportAnswer,
    EvidenceCandidate,
    EvidenceFreshness,
    QuestionItem,
    ReviewAppendix,
    ReviewAppendixEvidenceReference,
    ReviewAppendixExceptionDetail,
    ReviewAppendixExceptionItem,
    ReviewAppendixExportDecisionValue,
    ReviewAppendixExportRecord,
    ReviewAppendixVisibilityMode,
    ReviewDecision,
    utc_now,
)
from trustroom.state_machine import assess_answer_gate

if TYPE_CHECKING:
    from trustroom.agents.mock_runner import MockRunResult
    from trustroom.models import AnswerDraft, ApprovalDecision, OwnerReviewSuggestion


DEFAULT_APPENDIX_REASON = "Customer transparency on excluded questionnaire items."


def build_customer_export(
    result: MockRunResult,
    *,
    include_review_appendix: bool = False,
    owner_role: str = "Security Policy Owner",
    appendix_reason: str = DEFAULT_APPENDIX_REASON,
    appendix_scope: str | None = None,
    export_id: str | None = None,
    generated_at: datetime | None = None,
) -> CustomerExport:
    generated_at = generated_at or utc_now()
    export_id = export_id or _default_export_id(result)
    question_by_item_id = {question.item_id: question for question in result.questions}
    review_by_answer_id = {review.answer_id: review for review in result.reviews}
    approval_by_item_id = {approval.item_id: approval for approval in result.approvals}
    included_answer_ids = set(result.final_pack.included_answer_ids)

    answer_body: list[CustomerExportAnswer] = []
    for draft in sorted(result.drafts, key=lambda item: item.item_id):
        if draft.answer_id not in included_answer_ids:
            continue
        question = question_by_item_id[draft.item_id]
        approval = approval_by_item_id.get(draft.item_id)
        answer_body.append(
            CustomerExportAnswer(
                item_id=draft.item_id,
                answer_id=draft.answer_id,
                question=question.question_text,
                answer_text=draft.draft_text,
                evidence_refs=list(result.final_pack.evidence_index.get(draft.item_id, draft.evidence_ids)),
                approval_refs=_approval_refs(approval, answer_id=draft.answer_id),
                freshness_rollup=result.final_pack.freshness_rollup.get(
                    draft.item_id,
                    EvidenceFreshness.UNKNOWN,
                ),
            )
        )

    review_appendix: ReviewAppendix | None = None
    export_record: ReviewAppendixExportRecord | None = None
    if include_review_appendix:
        exceptions = _build_review_appendix_exceptions(
            result,
            generated_at=generated_at,
        )
        review_appendix = ReviewAppendix(
            visibility_mode=ReviewAppendixVisibilityMode.CUSTOMER_SAFE,
            not_customer_submittable=True,
            exceptions=exceptions,
        )
        blocked_scope = ", ".join(result.final_pack.blocked_item_ids) or "no blocked exceptions"
        export_record = ReviewAppendixExportRecord(
            record_id=f"RAER-{export_id}",
            export_id=export_id,
            decision=ReviewAppendixExportDecisionValue.INCLUDE_APPENDIX,
            owner_role=owner_role,
            reason=appendix_reason,
            scope=appendix_scope or f"Customer Export {export_id}; exceptions {blocked_scope} only.",
            visibility_mode=ReviewAppendixVisibilityMode.CUSTOMER_SAFE,
            decided_at=generated_at,
        )

    return CustomerExport(
        export_id=export_id,
        run_id=result.run.run_id,
        final_pack_id=result.final_pack.pack_id,
        generated_at=generated_at,
        mode=result.final_pack.mode,
        answer_body=answer_body,
        review_appendix=review_appendix,
        review_appendix_export_record=export_record,
    )


def _build_review_appendix_exceptions(
    result: MockRunResult,
    *,
    generated_at: datetime,
) -> list[ReviewAppendixExceptionItem]:
    question_by_item_id = {question.item_id: question for question in result.questions}
    draft_by_item_id = {draft.item_id: draft for draft in result.drafts}
    review_by_answer_id = {review.answer_id: review for review in result.reviews}
    approval_by_item_id = {approval.item_id: approval for approval in result.approvals}
    suggestion_by_item_id = {
        suggestion.item_id: suggestion
        for suggestion in result.owner_review_suggestions
    }
    evidence_by_id = {candidate.evidence_id: candidate for candidate in result.evidence}

    exceptions: list[ReviewAppendixExceptionItem] = []
    for item_id in result.final_pack.blocked_item_ids:
        question = question_by_item_id[item_id]
        draft = draft_by_item_id[item_id]
        review = review_by_answer_id.get(draft.answer_id)
        approval = approval_by_item_id.get(item_id)
        suggestion = suggestion_by_item_id.get(item_id)
        gate = assess_answer_gate(
            question,
            draft,
            result.evidence,
            review_decision=review,
            approval_decision=approval,
        )
        reason = "; ".join(gate.reasons) or "Excluded from Customer Export answer body."
        referenced_evidence = [
            evidence_by_id[evidence_id]
            for evidence_id in draft.evidence_ids
            if evidence_id in evidence_by_id
        ]
        owner = _owner_label(question)
        exceptions.append(
            ReviewAppendixExceptionItem(
                question_item=item_id,
                inclusion="excluded",
                reason_or_blocker=reason,
                owner=owner,
                next_action=_next_action(
                    item_id=item_id,
                    owner=owner,
                    gate_rollup=gate.freshness_rollup,
                    review=review,
                    suggestion=suggestion,
                ),
                detail=ReviewAppendixExceptionDetail(
                    supporting_agent=suggestion.proposed_by
                    if suggestion is not None
                    else review.reviewer_agent
                    if review is not None
                    else "trustroom-orchestrator-agent",
                    evidence_references=[
                        _appendix_evidence_reference(candidate)
                        for candidate in referenced_evidence
                    ],
                    handoff_summary=_handoff_summary(review=review, suggestion=suggestion),
                    decision_reason_detail=reason,
                    timestamp=generated_at,
                    redacted_audit_refs=_redacted_audit_refs(
                        result,
                        item_id=item_id,
                        answer_id=draft.answer_id,
                        review=review,
                        approval=approval,
                        suggestion=suggestion,
                    ),
                ),
            )
        )
    return exceptions


def _default_export_id(result: MockRunResult) -> str:
    customer_slug = result.run.case_id.split("-")[0].upper() or "CASE"
    return f"CE-{customer_slug}-v1"


def _approval_refs(approval: ApprovalDecision | None, *, answer_id: str) -> list[str]:
    if approval is None:
        return []
    if (
        approval.decision == ApprovalDecisionValue.APPROVE
        and approval.validity == ApprovalValidity.VALID
        and (approval.answer_id is None or approval.answer_id == answer_id)
    ):
        return [approval.decision_id]
    return []


def _appendix_evidence_reference(candidate: EvidenceCandidate) -> ReviewAppendixEvidenceReference:
    return ReviewAppendixEvidenceReference(
        ref=candidate.evidence_id,
        freshness_label=candidate.freshness_label,
        freshness_marked_by=candidate.freshness_marked_by,
        freshness_marked_at=candidate.freshness_marked_at,
    )


def _owner_label(question: QuestionItem) -> str:
    if question.business_owner == BusinessOwner.SECURITY:
        return "Security Policy Owner"
    return f"{question.business_owner.value.title()} Owner"


def _next_action(
    *,
    item_id: str,
    owner: str,
    gate_rollup: EvidenceFreshness,
    review: ReviewDecision | None,
    suggestion: OwnerReviewSuggestion | None,
) -> str:
    if item_id == "Q-006":
        return "Security Policy Owner must confirm incident-response wording before customer use."
    if suggestion is not None:
        return f"{owner} must review suggested evidence {', '.join(suggestion.suggested_evidence_ids)}."
    if gate_rollup in {
        EvidenceFreshness.STALE,
        EvidenceFreshness.MISSING,
        EvidenceFreshness.UNKNOWN,
        EvidenceFreshness.CONFLICTING,
    }:
        return f"{owner} must resolve {gate_rollup.value} evidence before inclusion."
    if review is not None and review.required_follow_up:
        return review.required_follow_up
    return f"{owner} must resolve the blocker before customer submission."


def _handoff_summary(
    *,
    review: ReviewDecision | None,
    suggestion: OwnerReviewSuggestion | None,
) -> str:
    if suggestion is not None:
        return (
            f"{suggestion.proposed_by} proposed {', '.join(suggestion.suggested_evidence_ids)} "
            f"for {suggestion.owner_role}; status remains {suggestion.status.value}."
        )
    if review is not None:
        return f"{review.reviewer_agent} held the item at {review.status.value}: {review.reason}"
    return "Final Pack excluded the item until owner review is complete."


def _redacted_audit_refs(
    result: MockRunResult,
    *,
    item_id: str,
    answer_id: str,
    review: ReviewDecision | None,
    approval: ApprovalDecision | None,
    suggestion: OwnerReviewSuggestion | None,
) -> list[str]:
    object_ids = {item_id, answer_id}
    if review is not None:
        object_ids.add(review.decision_id)
    if approval is not None:
        object_ids.add(approval.decision_id)
    if suggestion is not None:
        object_ids.add(suggestion.suggestion_id)
        object_ids.update(suggestion.suggested_evidence_ids)
        object_ids.update(suggestion.replaces_evidence_ids)

    refs: list[str] = []
    seen: set[str] = set()
    for event in result.events:
        if object_ids.isdisjoint(event.related_object_ids):
            continue
        ref = event.band_message_ref or event.event_id
        if ref in seen:
            continue
        seen.add(ref)
        refs.append(ref)
    return refs[:6]
