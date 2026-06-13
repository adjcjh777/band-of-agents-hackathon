from __future__ import annotations

from trustroom.band.adapter import MockBandAdapter
from trustroom.models import (
    AnswerLineage,
    AnswerDraft,
    ApprovalDecision,
    ApprovalDecisionValue,
    BusinessOwner,
    EvidenceCandidate,
    EventType,
    ExecutionMode,
    FinalSubmissionPack,
    LineageStep,
    QuestionItem,
    ReviewDecision,
    ReviewStatus,
    RiskLevel,
    Run,
    RunState,
    TimelineEvent,
    TrustRoomModel,
)
from trustroom.sample_loader import KnowledgeSnippet, SamplePack, load_default_sample_pack
from trustroom.state_machine import assess_answer_gate


ORCHESTRATOR = "trustroom-orchestrator-agent"
DECOMPOSER = "requirement-decomposer-agent"
EVIDENCE_RETRIEVER = "evidence-retriever-agent"
ANSWER_DRAFTER = "answer-drafter-agent"
COMPLIANCE_REVIEWER = "compliance-review-agent"
SME_APPROVER = "sme-approver"

SAMPLE_DRAFT_TEXT: dict[str, str] = {
    "Q-001": (
        "Customer documents are encrypted with TLS 1.3 in transit and AES-256 at rest. "
        "Key operations are separated from application operator access."
    ),
    "Q-002": (
        "A current SOC 2 Type II summary is available for approved prospects, and a bridge letter can be shared "
        "through the controlled reviewer workflow."
    ),
    "Q-003": (
        "Workspace administrators can configure artifact and source-upload retention windows of 30, 90, 180 or "
        "365 days based on the customer's policy."
    ),
    "Q-004": (
        "We can support a region-restricted pilot workflow, while any unconditional EU-only processing commitment "
        "requires legal approval."
    ),
    "Q-005": (
        "The product can generate PDF risk summaries from approved templates, and those summaries must be reviewed "
        "before external sharing."
    ),
    "Q-006": (
        "We should not commit to an incident-response notification target in the customer pack until the policy owner "
        "confirms the current incident-response language."
    ),
    "Q-007": (
        "Subprocessors are reviewed quarterly, and material updates are published to the customer trust center after "
        "security review."
    ),
    "Q-008": (
        "A controlled pilot is typically planned for 21 to 30 days once security review, workspace configuration and "
        "buyer acceptance testing are complete."
    ),
}


class MockRunResult(TrustRoomModel):
    run: Run
    events: list[TimelineEvent]
    questions: list[QuestionItem]
    evidence: list[EvidenceCandidate]
    drafts: list[AnswerDraft]
    reviews: list[ReviewDecision]
    approvals: list[ApprovalDecision]
    final_pack: FinalSubmissionPack
    lineage: list[AnswerLineage]


def run_mock_trustroom(sample: SamplePack | None = None) -> MockRunResult:
    sample = sample or load_default_sample_pack()
    adapter = MockBandAdapter(mode=ExecutionMode.MOCK)
    run = Run(
        run_id="run-acme-mock",
        case_id=sample.case.case_id,
        mode=ExecutionMode.MOCK,
        state=RunState.INTAKE,
        band_room_label="mock-band-room-run-acme-mock",
    )
    adapter.create_room(run_id=run.run_id, case_name=sample.case.case_name)

    adapter.record_event(
        run_id=run.run_id,
        sender="sales-engineer",
        receiver=ORCHESTRATOR,
        event_type=EventType.INTAKE,
        task_state=RunState.INTAKE,
        payload_summary="Sample RFP, questionnaire and knowledge snippets selected for deterministic mock run.",
        related_object_ids=[sample.case.case_id],
    )
    adapter.mention_agent(
        run_id=run.run_id,
        sender=ORCHESTRATOR,
        agent_name=DECOMPOSER,
        instruction="Triage the questionnaire into owners, risk levels and evidence needs.",
        task_state=RunState.TRIAGE,
        related_object_ids=[question.item_id for question in sample.questions],
    )

    evidence = _evidence_from_knowledge(sample.knowledge)
    adapter.record_event(
        run_id=run.run_id,
        sender=DECOMPOSER,
        receiver=EVIDENCE_RETRIEVER,
        event_type=EventType.HANDOFF,
        task_state=RunState.EVIDENCE,
        payload_summary="Decomposer hands off 8 RFP items, including high-risk SOC 2, EU residency and incident commitments.",
        related_object_ids=[question.item_id for question in sample.questions],
    )
    adapter.record_event(
        run_id=run.run_id,
        sender=EVIDENCE_RETRIEVER,
        receiver=ANSWER_DRAFTER,
        event_type=EventType.EVIDENCE_FOUND,
        task_state=RunState.DRAFTING,
        payload_summary="Evidence retriever returns current evidence, stale evidence, conflicting evidence and explicit gaps.",
        related_object_ids=[candidate.evidence_id for candidate in evidence],
    )

    drafts = _draft_answers(sample.questions, evidence)
    adapter.record_event(
        run_id=run.run_id,
        sender=ANSWER_DRAFTER,
        receiver=COMPLIANCE_REVIEWER,
        event_type=EventType.DRAFT_CREATED,
        task_state=RunState.REVIEW,
        payload_summary="Answer drafter creates evidence-linked drafts and flags high-risk items for review.",
        related_object_ids=[draft.answer_id for draft in drafts],
    )
    adapter.record_event(
        run_id=run.run_id,
        sender=COMPLIANCE_REVIEWER,
        receiver=ANSWER_DRAFTER,
        event_type=EventType.REVIEW_DECISION,
        task_state=RunState.REVIEW,
        payload_summary="Reviewer requests changes: EU residency wording needs safer boundary language before approval.",
        related_object_ids=["Q-004", "A-004"],
    )
    adapter.record_event(
        run_id=run.run_id,
        sender=COMPLIANCE_REVIEWER,
        receiver=EVIDENCE_RETRIEVER,
        event_type=EventType.HANDOFF,
        task_state=RunState.EVIDENCE,
        payload_summary="Reviewer loops Q-004 back to evidence retriever for region-processing clarification.",
        related_object_ids=["Q-004"],
    )
    adapter.record_event(
        run_id=run.run_id,
        sender=EVIDENCE_RETRIEVER,
        receiver=ANSWER_DRAFTER,
        event_type=EventType.EVIDENCE_FOUND,
        task_state=RunState.DRAFTING,
        payload_summary="Retriever confirms a safe pilot-region statement and keeps unconditional residency out of scope.",
        related_object_ids=["EV-004", "EV-009"],
    )

    revised_q4 = _draft_for_question(
        next(question for question in sample.questions if question.item_id == "Q-004"),
        evidence,
        answer_id="A-004R",
        draft_text=SAMPLE_DRAFT_TEXT["Q-004"],
    )
    drafts = [draft for draft in drafts if draft.item_id != "Q-004"] + [revised_q4]
    adapter.record_event(
        run_id=run.run_id,
        sender=ANSWER_DRAFTER,
        receiver=COMPLIANCE_REVIEWER,
        event_type=EventType.DRAFT_CREATED,
        task_state=RunState.REVIEW,
        payload_summary="Answer drafter submits revised Q-004 language with explicit approval boundary.",
        related_object_ids=[revised_q4.answer_id],
    )

    reviews = _review_drafts(drafts)
    approvals = _approval_decisions()
    adapter.record_event(
        run_id=run.run_id,
        sender=COMPLIANCE_REVIEWER,
        receiver=SME_APPROVER,
        event_type=EventType.REVIEW_DECISION,
        task_state=RunState.APPROVAL,
        payload_summary="Reviewer sends SOC 2, EU residency and stale incident response commitments to human approval.",
        related_object_ids=["Q-002", "Q-004", "Q-006"],
    )
    adapter.record_event(
        run_id=run.run_id,
        sender=SME_APPROVER,
        receiver=ORCHESTRATOR,
        event_type=EventType.HUMAN_APPROVAL,
        task_state=RunState.APPROVAL,
        payload_summary="SME approves SOC 2 and region-boundary wording, but leaves stale incident response commitment blocked.",
        related_object_ids=["Q-002", "Q-004", "Q-006"],
    )

    final_pack = _build_mock_final_pack(
        run=run.model_copy(update={"state": RunState.SUBMISSION_PACK}),
        questions=sample.questions,
        evidence=evidence,
        drafts=drafts,
        reviews=reviews,
        approvals=approvals,
    )
    adapter.record_event(
        run_id=run.run_id,
        sender=ORCHESTRATOR,
        receiver="sales-engineer",
        event_type=EventType.FINAL_PACK_CREATED,
        task_state=RunState.SUBMISSION_PACK,
        payload_summary="Final pack contains included answers, evidence index and explicit blockers for unsafe commitments.",
        related_object_ids=final_pack.included_answer_ids + final_pack.blocked_item_ids,
    )
    lineage = _build_answer_lineage(
        pack=final_pack,
        questions=sample.questions,
        evidence=evidence,
        drafts=drafts,
        reviews=reviews,
        approvals=approvals,
    )

    return MockRunResult(
        run=run.model_copy(update={"state": RunState.SUBMISSION_PACK}),
        events=adapter.get_room_timeline(run.run_id),
        questions=sample.questions,
        evidence=evidence,
        drafts=drafts,
        reviews=reviews,
        approvals=approvals,
        final_pack=final_pack,
        lineage=lineage,
    )


def _evidence_from_knowledge(knowledge: list[KnowledgeSnippet]) -> list[EvidenceCandidate]:
    evidence: list[EvidenceCandidate] = []
    for snippet in knowledge:
        for question_id in snippet.related_question_ids:
            evidence_id = (
                snippet.evidence_id
                if len(snippet.related_question_ids) == 1
                else f"{snippet.evidence_id}-{question_id}"
            )
            evidence.append(
                EvidenceCandidate(
                    evidence_id=evidence_id,
                    item_id=question_id,
                    source_title=snippet.title,
                    snippet=snippet.snippet,
                    freshness_label=snippet.freshness_label,
                    confidence=snippet.confidence,
                )
            )
    return evidence


def _draft_answers(questions: list[QuestionItem], evidence: list[EvidenceCandidate]) -> list[AnswerDraft]:
    return [
        _draft_for_question(question, evidence, answer_id=f"A-{question.item_id.split('-')[-1]}")
        for question in questions
    ]


def _draft_for_question(
    question: QuestionItem,
    evidence: list[EvidenceCandidate],
    *,
    answer_id: str,
    draft_text: str | None = None,
) -> AnswerDraft:
    evidence_ids = [
        candidate.evidence_id
        for candidate in evidence
        if candidate.item_id == question.item_id
    ]
    risk_flags = []
    if question.required_evidence_type == "certification" and question.risk_level == RiskLevel.HIGH:
        risk_flags.append("unsupported_certification")
    if question.business_owner == BusinessOwner.SECURITY and question.item_id == "Q-006":
        risk_flags.append("sla_commitment")
    return AnswerDraft(
        answer_id=answer_id,
        item_id=question.item_id,
        draft_text=draft_text or SAMPLE_DRAFT_TEXT[question.item_id],
        evidence_ids=evidence_ids,
        risk_flags=risk_flags,
    )


def _review_drafts(drafts: list[AnswerDraft]) -> list[ReviewDecision]:
    reviews: list[ReviewDecision] = []
    for draft in drafts:
        if draft.item_id in {"Q-002", "Q-004", "Q-006"}:
            status = ReviewStatus.NEEDS_HUMAN_APPROVAL
            reason = "High-risk or stale commitment needs human approval before final pack."
            follow_up = _review_follow_up(draft.item_id)
        else:
            status = ReviewStatus.APPROVED
            reason = "Draft is grounded in current evidence."
            follow_up = None
        reviews.append(
            ReviewDecision(
                decision_id=f"REV-{draft.item_id}",
                item_id=draft.item_id,
                answer_id=draft.answer_id,
                reviewer_agent=COMPLIANCE_REVIEWER,
                status=status,
                reason=reason,
                required_follow_up=follow_up,
            )
        )
    return reviews


def _review_follow_up(item_id: str) -> str | None:
    if item_id == "Q-006":
        return "Security policy owner must confirm current incident-response notification language before customer use."
    return None


def _approval_decisions() -> list[ApprovalDecision]:
    return [
        ApprovalDecision(
            decision_id="APP-Q-002",
            item_id="Q-002",
            reviewer_role=SME_APPROVER,
            decision=ApprovalDecisionValue.APPROVE,
            reason="SME approved current SOC 2 bridge-letter wording.",
            required_follow_up="No further action for the sample pack; keep bridge-letter sharing gated to approved prospects.",
        ),
        ApprovalDecision(
            decision_id="APP-Q-004",
            item_id="Q-004",
            reviewer_role="legal-reviewer",
            decision=ApprovalDecisionValue.APPROVE,
            reason="Legal approved bounded region-processing language.",
            required_follow_up="No further action for the sample pack; preserve the unconditional residency exclusion.",
        ),
    ]


def _build_mock_final_pack(
    *,
    run: Run,
    questions: list[QuestionItem],
    evidence: list[EvidenceCandidate],
    drafts: list[AnswerDraft],
    reviews: list[ReviewDecision],
    approvals: list[ApprovalDecision],
) -> FinalSubmissionPack:
    question_by_id = {question.item_id: question for question in questions}
    review_by_answer_id = {review.answer_id: review for review in reviews}
    approval_by_item_id = {approval.item_id: approval for approval in approvals}
    included_answer_ids: list[str] = []
    blocked_item_ids: list[str] = []
    evidence_index: dict[str, list[str]] = {}

    for draft in drafts:
        question = question_by_id[draft.item_id]
        gate = assess_answer_gate(
            question,
            draft,
            evidence,
            review_decision=review_by_answer_id.get(draft.answer_id),
            approval_decision=approval_by_item_id.get(draft.item_id),
        )
        if gate.can_enter_final_pack:
            included_answer_ids.append(draft.answer_id)
            evidence_index[draft.item_id] = list(draft.evidence_ids)
        else:
            blocked_item_ids.append(draft.item_id)

    return FinalSubmissionPack(
        pack_id="pack-run-acme-mock",
        run_id=run.run_id,
        included_answer_ids=included_answer_ids,
        blocked_item_ids=blocked_item_ids,
        readiness_summary="blocked" if blocked_item_ids else "ready",
        evidence_index=evidence_index,
        audit_event_ids=[review.decision_id for review in reviews] + [approval.decision_id for approval in approvals],
        mode=run.mode,
    )


def _build_answer_lineage(
    *,
    pack: FinalSubmissionPack,
    questions: list[QuestionItem],
    evidence: list[EvidenceCandidate],
    drafts: list[AnswerDraft],
    reviews: list[ReviewDecision],
    approvals: list[ApprovalDecision],
) -> list[AnswerLineage]:
    question_by_id = {question.item_id: question for question in questions}
    review_by_answer_id = {review.answer_id: review for review in reviews}
    approval_by_item_id = {approval.item_id: approval for approval in approvals}
    evidence_by_item_id: dict[str, list[EvidenceCandidate]] = {}
    for candidate in evidence:
        evidence_by_item_id.setdefault(candidate.item_id, []).append(candidate)

    lineage: list[AnswerLineage] = []
    for draft in sorted(drafts, key=lambda item: item.item_id):
        question = question_by_id[draft.item_id]
        review = review_by_answer_id.get(draft.answer_id)
        approval = approval_by_item_id.get(draft.item_id)
        item_evidence = evidence_by_item_id.get(draft.item_id, [])
        included = draft.answer_id in pack.included_answer_ids
        gate = assess_answer_gate(
            question,
            draft,
            evidence,
            review_decision=review,
            approval_decision=approval,
        )
        lineage.append(
            AnswerLineage(
                item_id=draft.item_id,
                answer_id=draft.answer_id,
                steps=[
                    LineageStep(
                        stage="question",
                        label="Question intake",
                        status=f"{question.risk_level.value} risk",
                        object_ids=[question.source_ref, question.item_id],
                        owner=question.business_owner.value,
                        reason=question.question_text,
                    ),
                    LineageStep(
                        stage="evidence",
                        label="Evidence set",
                        status=_lineage_evidence_status(item_evidence),
                        object_ids=draft.evidence_ids,
                        owner=question.business_owner.value,
                        reason=_lineage_evidence_reason(item_evidence),
                    ),
                    LineageStep(
                        stage="draft",
                        label="Customer-safe draft",
                        status="draft_created",
                        object_ids=[draft.answer_id],
                        owner=ANSWER_DRAFTER,
                        reason=draft.draft_text,
                    ),
                    LineageStep(
                        stage="review",
                        label="Agent review",
                        status=review.status.value if review else ReviewStatus.NOT_STARTED.value,
                        object_ids=[review.decision_id] if review else [],
                        owner=review.reviewer_agent if review else COMPLIANCE_REVIEWER,
                        reason=review.reason if review else "No reviewer decision has been recorded.",
                    ),
                    LineageStep(
                        stage="approval",
                        label="Human approval",
                        status=approval.decision.value if approval else "missing",
                        object_ids=[approval.decision_id] if approval else [],
                        owner=approval.reviewer_role if approval else "policy owner",
                        reason=approval.reason if approval else "No human approval record is attached to this answer.",
                    ),
                    LineageStep(
                        stage="final_pack",
                        label="Final pack decision",
                        status="included" if included else "excluded",
                        object_ids=[pack.pack_id],
                        reason="Included in final pack."
                        if included
                        else "; ".join(gate.reasons) or "Excluded from final pack.",
                    ),
                ],
            )
        )
    return lineage


def _lineage_evidence_status(evidence: list[EvidenceCandidate]) -> str:
    if not evidence:
        return "missing"
    counts: dict[str, int] = {}
    for candidate in evidence:
        counts[candidate.freshness_label.value] = counts.get(candidate.freshness_label.value, 0) + 1
    return ", ".join(f"{label}:{count}" for label, count in sorted(counts.items()))


def _lineage_evidence_reason(evidence: list[EvidenceCandidate]) -> str:
    if not evidence:
        return "No evidence references are attached."
    return "Evidence refs: " + ", ".join(
        f"{candidate.evidence_id} ({candidate.source_title})" for candidate in evidence
    )
