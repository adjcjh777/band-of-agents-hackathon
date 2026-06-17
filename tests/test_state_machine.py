from __future__ import annotations

import pytest

from trustroom.models import (
    AnswerDraft,
    ApprovalDecision,
    ApprovalDecisionValue,
    ApprovalValidity,
    BusinessOwner,
    EvidenceCandidate,
    EvidenceFreshness,
    ExecutionMode,
    QuestionCategory,
    QuestionItem,
    ReviewDecision,
    ReviewStatus,
    RiskLevel,
    Run,
    RunState,
)
from trustroom.state_machine import (
    FinalPackBlocked,
    InvalidTransition,
    assess_answer_gate,
    build_final_submission_pack,
    rollup_evidence_freshness,
    transition_run,
)


def make_run(state: RunState = RunState.INTAKE) -> Run:
    return Run(
        run_id="run-demo",
        case_id="case-acme",
        mode=ExecutionMode.MOCK,
        state=state,
        band_room_label="mock-room-acme",
    )


def make_item(
    *,
    item_id: str = "Q-001",
    risk_level: RiskLevel = RiskLevel.LOW,
) -> QuestionItem:
    return QuestionItem(
        item_id=item_id,
        case_id="case-acme",
        source_ref=f"questionnaire.csv:{item_id}",
        question_text="Can Acme rely on current evidence?",
        category=QuestionCategory.SECURITY,
        risk_level=risk_level,
        required_evidence_type="policy",
        business_owner=BusinessOwner.SECURITY,
    )


def make_evidence(
    *,
    evidence_id: str = "EV-001",
    item_id: str = "Q-001",
    freshness: EvidenceFreshness = EvidenceFreshness.CURRENT,
) -> EvidenceCandidate:
    return EvidenceCandidate(
        evidence_id=evidence_id,
        item_id=item_id,
        source_title="Security policy",
        snippet="Security controls are reviewed quarterly.",
        freshness_label=freshness,
        confidence=0.92,
    )


def make_answer(
    *,
    answer_id: str = "A-001",
    item_id: str = "Q-001",
    evidence_ids: list[str] | None = None,
    risk_flags: list[str] | None = None,
) -> AnswerDraft:
    return AnswerDraft(
        answer_id=answer_id,
        item_id=item_id,
        draft_text="We maintain quarterly reviewed controls.",
        evidence_ids=evidence_ids if evidence_ids is not None else ["EV-001"],
        risk_flags=risk_flags or [],
    )


def test_valid_workflow_transition_sequence_reaches_submission_pack() -> None:
    run = make_run()

    for state in [
        RunState.TRIAGE,
        RunState.DECOMPOSITION,
        RunState.EVIDENCE,
        RunState.DRAFTING,
        RunState.REVIEW,
        RunState.APPROVAL,
        RunState.SUBMISSION_PACK,
    ]:
        run = transition_run(run, state)

    assert run.state == RunState.SUBMISSION_PACK


def test_invalid_transition_is_rejected() -> None:
    run = make_run(RunState.INTAKE)

    with pytest.raises(InvalidTransition):
        transition_run(run, RunState.SUBMISSION_PACK)


def test_high_risk_unapproved_answer_cannot_enter_final_pack() -> None:
    item = make_item(risk_level=RiskLevel.HIGH)
    evidence = make_evidence()
    answer = make_answer()
    review = ReviewDecision(
        decision_id="R-001",
        item_id=item.item_id,
        answer_id=answer.answer_id,
        reviewer_agent="compliance-review-agent",
        status=ReviewStatus.NEEDS_HUMAN_APPROVAL,
        reason="High-risk answer needs SME approval.",
    )

    gate = assess_answer_gate(item, answer, [evidence], review_decision=review)

    assert gate.can_enter_final_pack is False
    assert gate.status == "needs_review"
    assert "human approval" in " ".join(gate.reasons)

    with pytest.raises(FinalPackBlocked):
        build_final_submission_pack(
            make_run(RunState.SUBMISSION_PACK),
            questions=[item],
            evidence=[evidence],
            drafts=[answer],
            reviews=[review],
            approvals=[],
        )


def test_low_risk_answer_with_current_evidence_can_enter_final_pack() -> None:
    item = make_item(risk_level=RiskLevel.LOW)
    evidence = make_evidence()
    answer = make_answer()
    review = ReviewDecision(
        decision_id="R-001",
        item_id=item.item_id,
        answer_id=answer.answer_id,
        reviewer_agent="compliance-review-agent",
        status=ReviewStatus.APPROVED,
        reason="Grounded in current policy evidence.",
    )

    gate = assess_answer_gate(item, answer, [evidence], review_decision=review)
    pack = build_final_submission_pack(
        make_run(RunState.SUBMISSION_PACK),
        questions=[item],
        evidence=[evidence],
        drafts=[answer],
        reviews=[review],
        approvals=[],
    )

    assert gate.can_enter_final_pack is True
    assert pack.included_answer_ids == [answer.answer_id]
    assert pack.blocked_item_ids == []
    assert pack.readiness_summary == "ready"


def test_stale_evidence_answer_needs_review_and_blocks_finalization() -> None:
    item = make_item(item_id="Q-002", risk_level=RiskLevel.LOW)
    evidence = make_evidence(
        evidence_id="EV-002",
        item_id=item.item_id,
        freshness=EvidenceFreshness.STALE,
    )
    answer = make_answer(answer_id="A-002", item_id=item.item_id, evidence_ids=["EV-002"])
    review = ReviewDecision(
        decision_id="R-002",
        item_id=item.item_id,
        answer_id=answer.answer_id,
        reviewer_agent="compliance-review-agent",
        status=ReviewStatus.APPROVED,
        reason="Reviewer missed stale evidence in this fixture.",
    )

    gate = assess_answer_gate(item, answer, [evidence], review_decision=review)

    assert gate.can_enter_final_pack is False
    assert gate.status == "needs_review"
    assert any("stale" in reason for reason in gate.reasons)
    assert gate.freshness_rollup == EvidenceFreshness.STALE


def test_non_current_evidence_blocks_even_with_human_approval() -> None:
    item = make_item(item_id="Q-002", risk_level=RiskLevel.HIGH)
    stale = make_evidence(
        evidence_id="EV-002",
        item_id=item.item_id,
        freshness=EvidenceFreshness.STALE,
    )
    current = make_evidence(
        evidence_id="EV-013",
        item_id=item.item_id,
        freshness=EvidenceFreshness.CURRENT,
    )
    answer = make_answer(
        answer_id="A-002",
        item_id=item.item_id,
        evidence_ids=["EV-002", "EV-013"],
    )
    approval = ApprovalDecision(
        decision_id="H-002",
        item_id=item.item_id,
        answer_id=answer.answer_id,
        reviewer_role="security-policy-owner",
        decision=ApprovalDecisionValue.APPROVE,
        reason="Owner approved replacement direction.",
        scope="Q-002 only.",
        approved_evidence_ids=["EV-013"],
    )

    gate = assess_answer_gate(item, answer, [stale, current], approval_decision=approval)

    assert gate.can_enter_final_pack is False
    assert gate.freshness_rollup == EvidenceFreshness.STALE
    assert any("stale evidence EV-002 blocks final pack entry" in reason for reason in gate.reasons)


def test_unknown_evidence_freshness_blocks_final_pack() -> None:
    item = make_item(item_id="Q-009", risk_level=RiskLevel.LOW)
    evidence = make_evidence(
        evidence_id="EV-009",
        item_id=item.item_id,
        freshness=EvidenceFreshness.UNKNOWN,
    )
    answer = make_answer(answer_id="A-009", item_id=item.item_id, evidence_ids=["EV-009"])

    gate = assess_answer_gate(item, answer, [evidence])

    assert gate.can_enter_final_pack is False
    assert gate.freshness_rollup == EvidenceFreshness.UNKNOWN
    assert any("unknown evidence freshness EV-009 blocks final pack entry" in reason for reason in gate.reasons)


def test_evidence_freshness_rollup_is_conservative() -> None:
    item_id = "Q-010"
    evidence = [
        make_evidence(evidence_id="EV-current", item_id=item_id, freshness=EvidenceFreshness.CURRENT),
        make_evidence(evidence_id="EV-unknown", item_id=item_id, freshness=EvidenceFreshness.UNKNOWN),
        make_evidence(evidence_id="EV-conflict", item_id=item_id, freshness=EvidenceFreshness.CONFLICTING),
    ]

    assert rollup_evidence_freshness(evidence) == EvidenceFreshness.CONFLICTING


def test_unsupported_certification_requires_explicit_human_approval() -> None:
    item = make_item(item_id="Q-003", risk_level=RiskLevel.MEDIUM)
    evidence = make_evidence(evidence_id="EV-003", item_id=item.item_id)
    answer = make_answer(
        answer_id="A-003",
        item_id=item.item_id,
        evidence_ids=["EV-003"],
        risk_flags=["unsupported_certification"],
    )
    approval = ApprovalDecision(
        decision_id="H-003",
        item_id=item.item_id,
        answer_id=answer.answer_id,
        reviewer_role="security-reviewer",
        decision=ApprovalDecisionValue.APPROVE,
        reason="Reviewer confirms the answer avoids certification overclaim.",
        scope="Certification boundary for this answer only.",
        approved_evidence_ids=["EV-003"],
    )

    gate_without_approval = assess_answer_gate(item, answer, [evidence])
    gate_with_approval = assess_answer_gate(
        item,
        answer,
        [evidence],
        approval_decision=approval,
    )

    assert gate_without_approval.can_enter_final_pack is False
    assert gate_with_approval.can_enter_final_pack is True


def test_expired_high_risk_approval_cannot_unblock_final_pack() -> None:
    item = make_item(item_id="Q-004", risk_level=RiskLevel.HIGH)
    evidence = make_evidence(evidence_id="EV-004", item_id=item.item_id)
    answer = make_answer(answer_id="A-004R", item_id=item.item_id, evidence_ids=["EV-004"])
    approval = ApprovalDecision(
        decision_id="H-004",
        item_id=item.item_id,
        answer_id=answer.answer_id,
        reviewer_role="legal-reviewer",
        decision=ApprovalDecisionValue.APPROVE,
        reason="Legal approved an older answer.",
        scope="Region-processing wording for an earlier review cycle.",
        expires_at_label="Expired after policy refresh.",
        validity=ApprovalValidity.EXPIRED,
        approved_evidence_ids=["EV-004"],
    )

    gate = assess_answer_gate(
        item,
        answer,
        [evidence],
        approval_decision=approval,
    )

    assert gate.can_enter_final_pack is False
    assert any("expired" in reason for reason in gate.reasons)


def test_out_of_scope_high_risk_approval_cannot_unblock_final_pack() -> None:
    item = make_item(item_id="Q-006", risk_level=RiskLevel.HIGH)
    evidence = make_evidence(evidence_id="EV-006", item_id=item.item_id)
    answer = make_answer(answer_id="A-006", item_id=item.item_id, evidence_ids=["EV-006"])
    approval = ApprovalDecision(
        decision_id="H-006",
        item_id=item.item_id,
        answer_id=answer.answer_id,
        reviewer_role="security-policy-owner",
        decision=ApprovalDecisionValue.APPROVE,
        reason="Approver only covered a different support commitment.",
        scope="Premium uptime wording only; incident notification language remains out of scope.",
        validity=ApprovalValidity.OUT_OF_SCOPE,
        approved_evidence_ids=["EV-010"],
    )

    gate = assess_answer_gate(
        item,
        answer,
        [evidence],
        approval_decision=approval,
    )

    assert gate.can_enter_final_pack is False
    assert any("out of scope" in reason for reason in gate.reasons)


def test_answer_specific_approval_cannot_unblock_changed_answer() -> None:
    item = make_item(item_id="Q-002", risk_level=RiskLevel.HIGH)
    evidence = make_evidence(evidence_id="EV-002", item_id=item.item_id)
    answer = make_answer(answer_id="A-002-revised", item_id=item.item_id, evidence_ids=["EV-002"])
    approval = ApprovalDecision(
        decision_id="H-002",
        item_id=item.item_id,
        answer_id="A-002",
        reviewer_role="sme-approver",
        decision=ApprovalDecisionValue.APPROVE,
        reason="SME approved the original wording only.",
        scope="Original SOC 2 bridge-letter wording.",
        approved_evidence_ids=["EV-002"],
    )

    gate = assess_answer_gate(
        item,
        answer,
        [evidence],
        approval_decision=approval,
    )

    assert gate.can_enter_final_pack is False
    assert any("applies to A-002, not A-002-revised" in reason for reason in gate.reasons)
