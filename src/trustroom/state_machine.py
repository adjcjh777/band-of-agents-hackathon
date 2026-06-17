from __future__ import annotations

from dataclasses import dataclass

from trustroom.models import (
    AnswerDraft,
    ApprovalDecision,
    ApprovalDecisionValue,
    ApprovalValidity,
    EvidenceCandidate,
    EvidenceFreshness,
    FinalSubmissionPack,
    QuestionItem,
    ReviewDecision,
    ReviewStatus,
    RiskLevel,
    Run,
    RunState,
)


class InvalidTransition(ValueError):
    pass


class FinalPackBlocked(ValueError):
    def __init__(self, blocked_item_ids: list[str], reasons: dict[str, list[str]]) -> None:
        self.blocked_item_ids = blocked_item_ids
        self.reasons = reasons
        detail = "; ".join(
            f"{item_id}: {', '.join(item_reasons)}"
            for item_id, item_reasons in reasons.items()
        )
        super().__init__(f"final pack blocked: {detail}")


@dataclass(frozen=True)
class AnswerGate:
    item_id: str
    answer_id: str
    can_enter_final_pack: bool
    status: str
    reasons: list[str]
    freshness_rollup: EvidenceFreshness


ALLOWED_TRANSITIONS: dict[RunState, set[RunState]] = {
    RunState.INTAKE: {RunState.TRIAGE},
    RunState.TRIAGE: {RunState.DECOMPOSITION},
    RunState.DECOMPOSITION: {RunState.EVIDENCE},
    RunState.EVIDENCE: {RunState.DRAFTING},
    RunState.DRAFTING: {RunState.REVIEW},
    RunState.REVIEW: {
        RunState.EVIDENCE,
        RunState.DRAFTING,
        RunState.APPROVAL,
    },
    RunState.APPROVAL: {
        RunState.DRAFTING,
        RunState.REVIEW,
        RunState.SUBMISSION_PACK,
    },
    RunState.SUBMISSION_PACK: {RunState.POST_RUN_REVIEW},
    RunState.POST_RUN_REVIEW: {RunState.EVOLUTION_REVIEW},
    RunState.EVOLUTION_REVIEW: {RunState.INTAKE},
}


REVIEW_BLOCKING_STATUSES = {
    ReviewStatus.BLOCKED,
    ReviewStatus.REQUEST_CHANGES,
    ReviewStatus.NEEDS_HUMAN_APPROVAL,
    ReviewStatus.NEEDS_REVIEW,
}

FRESHNESS_ROLLUP_PRIORITY = (
    EvidenceFreshness.CONFLICTING,
    EvidenceFreshness.MISSING,
    EvidenceFreshness.STALE,
    EvidenceFreshness.UNKNOWN,
    EvidenceFreshness.CURRENT,
)


def transition_run(run: Run, next_state: RunState) -> Run:
    allowed = ALLOWED_TRANSITIONS.get(run.state, set())
    if next_state not in allowed:
        raise InvalidTransition(f"cannot transition run {run.run_id} from {run.state} to {next_state}")
    return run.model_copy(update={"state": next_state})


def _approved(approval_decision: ApprovalDecision | None, answer: AnswerDraft) -> bool:
    if approval_decision is None:
        return False
    return (
        approval_decision.decision == ApprovalDecisionValue.APPROVE
        and approval_decision.validity == ApprovalValidity.VALID
        and (
            approval_decision.answer_id is None
            or approval_decision.answer_id == answer.answer_id
        )
    )


def _approval_blocking_reasons(
    approval_decision: ApprovalDecision | None,
    answer: AnswerDraft,
    *,
    missing_reason: str,
) -> list[str]:
    if approval_decision is None:
        return [missing_reason]

    reasons: list[str] = []
    if approval_decision.decision != ApprovalDecisionValue.APPROVE:
        reasons.append(
            f"human approval {approval_decision.decision_id} is {approval_decision.decision.value}"
        )
    if approval_decision.validity == ApprovalValidity.EXPIRED:
        reasons.append(
            f"human approval {approval_decision.decision_id} expired and cannot unblock final pack entry"
        )
    elif approval_decision.validity == ApprovalValidity.OUT_OF_SCOPE:
        reasons.append(
            f"human approval {approval_decision.decision_id} is out of scope for this answer"
        )
    if approval_decision.answer_id is not None and approval_decision.answer_id != answer.answer_id:
        reasons.append(
            f"human approval {approval_decision.decision_id} applies to {approval_decision.answer_id}, not {answer.answer_id}"
        )
    return reasons or [missing_reason]


def _evidence_by_id(evidence: list[EvidenceCandidate]) -> dict[str, EvidenceCandidate]:
    return {candidate.evidence_id: candidate for candidate in evidence}


def rollup_evidence_freshness(evidence: list[EvidenceCandidate]) -> EvidenceFreshness:
    if not evidence:
        return EvidenceFreshness.MISSING
    labels = {candidate.freshness_label for candidate in evidence}
    for label in FRESHNESS_ROLLUP_PRIORITY:
        if label in labels:
            return label
    return EvidenceFreshness.UNKNOWN


def assess_answer_gate(
    question: QuestionItem,
    answer: AnswerDraft,
    evidence: list[EvidenceCandidate],
    *,
    review_decision: ReviewDecision | None = None,
    approval_decision: ApprovalDecision | None = None,
) -> AnswerGate:
    evidence_reasons: list[str] = []
    gate_reasons: list[str] = []
    approved = _approved(approval_decision, answer)
    indexed_evidence = _evidence_by_id(evidence)
    referenced_evidence: list[EvidenceCandidate] = []
    has_missing_reference = False

    if not answer.evidence_ids:
        evidence_reasons.append("missing evidence blocks final pack entry")

    for evidence_id in answer.evidence_ids:
        candidate = indexed_evidence.get(evidence_id)
        if candidate is None:
            has_missing_reference = True
            evidence_reasons.append(f"missing evidence reference {evidence_id}")
            continue
        referenced_evidence.append(candidate)
        if candidate.item_id != question.item_id:
            evidence_reasons.append(f"evidence {evidence_id} belongs to {candidate.item_id}, not {question.item_id}")
        if candidate.freshness_label == EvidenceFreshness.STALE:
            evidence_reasons.append(f"stale evidence {evidence_id} blocks final pack entry")
        elif candidate.freshness_label == EvidenceFreshness.MISSING:
            evidence_reasons.append(f"missing evidence {evidence_id} blocks final pack entry")
        elif candidate.freshness_label == EvidenceFreshness.UNKNOWN:
            evidence_reasons.append(f"unknown evidence freshness {evidence_id} blocks final pack entry")
        elif candidate.freshness_label == EvidenceFreshness.CONFLICTING:
            evidence_reasons.append(f"conflicting evidence {evidence_id} blocks final pack entry")

    freshness_rollup = (
        EvidenceFreshness.MISSING
        if has_missing_reference or not answer.evidence_ids
        else rollup_evidence_freshness(referenced_evidence)
    )

    if question.risk_level == RiskLevel.HIGH and not approved:
        gate_reasons.extend(
            _approval_blocking_reasons(
                approval_decision,
                answer,
                missing_reason="high-risk answer requires human approval",
            )
        )

    normalized_flags = {flag.strip().lower() for flag in answer.risk_flags}
    if (
        "unsupported_certification" in normalized_flags
        and question.risk_level != RiskLevel.HIGH
        and not approved
    ):
        gate_reasons.append("unsupported certification requires human approval")

    if review_decision is not None and review_decision.status in REVIEW_BLOCKING_STATUSES and not approved:
        gate_reasons.append(f"review status {review_decision.status.value} blocks final pack entry")

    reasons = evidence_reasons + gate_reasons
    can_enter_final_pack = not reasons
    status = "ready" if can_enter_final_pack else "needs_review"
    return AnswerGate(
        item_id=question.item_id,
        answer_id=answer.answer_id,
        can_enter_final_pack=can_enter_final_pack,
        status=status,
        reasons=[] if can_enter_final_pack else reasons,
        freshness_rollup=freshness_rollup,
    )


def build_final_submission_pack(
    run: Run,
    *,
    questions: list[QuestionItem],
    evidence: list[EvidenceCandidate],
    drafts: list[AnswerDraft],
    reviews: list[ReviewDecision],
    approvals: list[ApprovalDecision],
) -> FinalSubmissionPack:
    if run.state != RunState.SUBMISSION_PACK:
        raise InvalidTransition(f"run {run.run_id} must be in submission_pack before finalization")

    question_by_id = {question.item_id: question for question in questions}
    review_by_answer_id = {review.answer_id: review for review in reviews}
    approval_by_item_id = {
        approval.item_id: approval
        for approval in approvals
        if approval.decision == ApprovalDecisionValue.APPROVE
    }

    included_answer_ids: list[str] = []
    blocked_item_ids: list[str] = []
    blocked_reasons: dict[str, list[str]] = {}
    evidence_index: dict[str, list[str]] = {}
    freshness_rollup: dict[str, EvidenceFreshness] = {}
    audit_event_ids: list[str] = []

    for draft in drafts:
        question = question_by_id.get(draft.item_id)
        if question is None:
            blocked_item_ids.append(draft.item_id)
            blocked_reasons[draft.item_id] = ["draft has no matching question item"]
            continue

        gate = assess_answer_gate(
            question,
            draft,
            evidence,
            review_decision=review_by_answer_id.get(draft.answer_id),
            approval_decision=approval_by_item_id.get(draft.item_id),
        )
        freshness_rollup[draft.item_id] = gate.freshness_rollup
        if gate.can_enter_final_pack:
            included_answer_ids.append(draft.answer_id)
            evidence_index[draft.item_id] = list(draft.evidence_ids)
        else:
            blocked_item_ids.append(draft.item_id)
            blocked_reasons[draft.item_id] = gate.reasons

    if blocked_item_ids:
        raise FinalPackBlocked(blocked_item_ids, blocked_reasons)

    audit_event_ids.extend(review.decision_id for review in reviews)
    audit_event_ids.extend(approval.decision_id for approval in approvals)

    return FinalSubmissionPack(
        pack_id=f"pack-{run.run_id}",
        run_id=run.run_id,
        included_answer_ids=included_answer_ids,
        blocked_item_ids=[],
        readiness_summary="ready",
        evidence_index=evidence_index,
        freshness_rollup=freshness_rollup,
        audit_event_ids=audit_event_ids,
        mode=run.mode,
    )
