from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from trustroom.models import (
    AnswerLineage,
    ApprovalDecision,
    ApprovalDecisionValue,
    ApprovalValidity,
    BusinessOwner,
    CustomerCase,
    EvidenceCandidate,
    EvidenceFreshness,
    EventType,
    ExecutionMode,
    ExperienceLesson,
    FinalSubmissionPack,
    LessonScope,
    LessonType,
    LineageStep,
    MaterialType,
    OwnerReviewSuggestion,
    OwnerReviewSuggestionStatus,
    ProposalStatus,
    ProposalType,
    QuestionCategory,
    QuestionItem,
    ReviewAppendixExceptionItem,
    ReviewDecision,
    ReviewStatus,
    RiskLevel,
    Run,
    RunState,
    SafeBehavior,
    StressTestCase,
    StressTrapType,
    TaskEnvelope,
    TimelineEvent,
    EvolutionProposal,
)


def test_customer_case_and_run_capture_enterprise_context() -> None:
    customer_case = CustomerCase(
        case_id="case-acme",
        case_name="Acme Security RFP",
        customer_profile="Regional fintech buyer evaluating secure document workflows.",
        deadline_label="48 hours",
        material_types=[MaterialType.RFP, MaterialType.SECURITY_QUESTIONNAIRE],
        business_goal="Create an evidence-backed submission pack.",
        submission_owner="sales-engineering",
        mode=ExecutionMode.MOCK,
    )
    run = Run(
        run_id="run-demo",
        case_id=customer_case.case_id,
        mode=ExecutionMode.MOCK,
        state=RunState.INTAKE,
        band_room_label="mock-room-acme",
    )

    assert customer_case.material_types == [
        MaterialType.RFP,
        MaterialType.SECURITY_QUESTIONNAIRE,
    ]
    assert run.readiness_summary == "needs_review"
    assert run.current_blockers == []


def test_question_and_evidence_models_require_traceable_business_fields() -> None:
    item = QuestionItem(
        item_id="Q-001",
        case_id="case-acme",
        source_ref="questionnaire.csv:1",
        question_text="Do you support SOC 2 evidence for customer review?",
        category=QuestionCategory.SECURITY,
        risk_level=RiskLevel.HIGH,
        required_evidence_type="certification",
        business_owner=BusinessOwner.SECURITY,
    )
    evidence = EvidenceCandidate(
        evidence_id="EV-001",
        item_id=item.item_id,
        source_title="SOC 2 bridge letter",
        snippet="Bridge letter is available for approved prospects.",
        freshness_label=EvidenceFreshness.CURRENT,
        confidence=0.86,
    )

    assert item.status == "open"
    assert evidence.confidence == pytest.approx(0.86)
    assert evidence.freshness_marked_by == "evidence-retriever-agent"
    assert evidence.freshness_marked_at.tzinfo is not None


def test_owner_review_suggestion_starts_as_proposed() -> None:
    suggestion = OwnerReviewSuggestion(
        suggestion_id="ORS-Q-006",
        item_id="Q-006",
        proposed_by="evidence-retriever-agent",
        owner_role="security-policy-owner",
        suggested_evidence_ids=["EV-013"],
        replaces_evidence_ids=["EV-006", "EV-010"],
        reason="Replacement evidence may support safer incident-response wording.",
        scope="Q-006 only.",
    )

    assert suggestion.status == OwnerReviewSuggestionStatus.PROPOSED
    assert suggestion.suggested_evidence_ids == ["EV-013"]
    assert suggestion.replaces_evidence_ids == ["EV-006", "EV-010"]


def test_review_appendix_exception_rejects_included_inclusion() -> None:
    with pytest.raises(ValidationError):
        ReviewAppendixExceptionItem(
            question_item="Q-006",
            inclusion="included",
            reason_or_blocker="Included items must stay in the answer body, not exceptions.",
            owner="Security Policy Owner",
            next_action="No action.",
        )


def test_confidence_must_be_between_zero_and_one() -> None:
    with pytest.raises(ValidationError):
        EvidenceCandidate(
            evidence_id="EV-bad",
            item_id="Q-001",
            source_title="Bad score",
            snippet="Impossible confidence.",
            freshness_label=EvidenceFreshness.CURRENT,
            confidence=1.5,
        )


def test_final_submission_pack_preserves_readiness_and_evidence_index() -> None:
    created_at = datetime(2026, 5, 31, tzinfo=UTC)
    pack = FinalSubmissionPack(
        pack_id="pack-demo",
        run_id="run-demo",
        generated_at=created_at,
        included_answer_ids=["A-001"],
        blocked_item_ids=["Q-002"],
        readiness_summary="blocked",
        evidence_index={"Q-001": ["EV-001"]},
        audit_event_ids=["E-final"],
        mode=ExecutionMode.REPLAY,
    )

    assert pack.mode == ExecutionMode.REPLAY
    assert pack.evidence_index["Q-001"] == ["EV-001"]
    assert pack.freshness_rollup == {}
    assert pack.visibility_mode == "customer-safe"
    assert pack.blocked_item_ids == ["Q-002"]


def test_task_envelope_and_timeline_event_make_handoff_visible() -> None:
    envelope = TaskEnvelope(
        task_id="task-evidence",
        run_id="run-demo",
        sender="trustroom-orchestrator",
        receiver="evidence-retriever-agent",
        task_state=RunState.EVIDENCE,
        objective="Find current evidence for Q-001.",
        input_object_ids=["Q-001"],
        expected_output="EvidenceCandidate[]",
    )
    event = TimelineEvent(
        event_id="E-001",
        run_id="run-demo",
        sender=envelope.sender,
        receiver=envelope.receiver,
        event_type=EventType.HANDOFF,
        task_state=RunState.EVIDENCE,
        payload_summary="Evidence retrieval started for Q-001.",
        related_object_ids=envelope.input_object_ids,
        band_message_ref="mock:handoff:E-001",
    )

    assert event.receiver == "evidence-retriever-agent"
    assert event.event_type == EventType.HANDOFF
    assert event.visibility == "judge_view"


def test_review_and_approval_models_separate_agent_review_from_human_decision() -> None:
    review = ReviewDecision(
        decision_id="R-001",
        item_id="Q-001",
        answer_id="A-001",
        reviewer_agent="compliance-review-agent",
        status=ReviewStatus.NEEDS_HUMAN_APPROVAL,
        reason="High-risk compliance commitment requires SME approval.",
    )
    approval = ApprovalDecision(
        decision_id="H-001",
        item_id="Q-001",
        answer_id="A-001",
        reviewer_role="sme-approver",
        decision=ApprovalDecisionValue.APPROVE,
        reason="SME approved current bridge-letter wording.",
        scope="Bridge-letter wording for approved prospects only.",
        expires_at_label="Valid until the next SOC 2 period changes.",
        approved_evidence_ids=["EV-001"],
    )

    assert review.status == ReviewStatus.NEEDS_HUMAN_APPROVAL
    assert approval.decision == ApprovalDecisionValue.APPROVE
    assert approval.validity == ApprovalValidity.VALID
    assert approval.answer_id == "A-001"
    assert approval.approved_evidence_ids == ["EV-001"]
    assert "approved prospects" in approval.scope


def test_answer_lineage_preserves_traceable_enterprise_chain() -> None:
    lineage = AnswerLineage(
        item_id="Q-004",
        answer_id="A-004R",
        steps=[
            LineageStep(
                stage="question",
                label="Question intake",
                status="high risk",
                object_ids=["questionnaire.csv:5", "Q-004"],
                owner="legal",
                reason="Customer asks for region-restricted workflow.",
            ),
            LineageStep(
                stage="evidence",
                label="Evidence set",
                status="current, missing",
                object_ids=["EV-004", "EV-009"],
                reason="Evidence includes a current pilot design note and explicit gap note.",
            ),
            LineageStep(
                stage="approval",
                label="Human approval",
                status="approve",
                object_ids=["APP-Q-004"],
                owner="legal-reviewer",
                reason="Legal approved bounded region-processing language.",
            ),
            LineageStep(
                stage="final_pack",
                label="Final pack decision",
                status="included",
                object_ids=["pack-run-acme-mock"],
                reason="Included after legal-reviewer approval.",
            ),
        ],
    )

    assert lineage.steps[0].stage == "question"
    assert lineage.steps[-1].status == "included"
    assert "APP-Q-004" in lineage.steps[2].object_ids


def test_answer_lineage_requires_at_least_one_step() -> None:
    with pytest.raises(ValidationError):
        AnswerLineage(item_id="Q-006", answer_id="A-006", steps=[])


def test_governed_evolution_models_are_human_reviewable() -> None:
    proposal = EvolutionProposal(
        proposal_id="P-001",
        run_id="run-demo",
        proposal_type=ProposalType.REVIEWER_GATE,
        target_component="compliance-review-agent",
        problem_statement="SLA commitments were not routed to SME review early enough.",
        supporting_event_ids=["E-review-001"],
        proposed_change="Route SLA commitments to human approval before final pack.",
        expected_effect="Reduce late-stage request_changes loops.",
        risk_level=RiskLevel.MEDIUM,
        evaluation_plan="Replay the SLA fixture and confirm high-risk items require approval.",
    )
    lesson = ExperienceLesson(
        lesson_id="L-001",
        source_proposal_id=proposal.proposal_id,
        accepted_by="evolution-reviewer",
        scope=LessonScope.RISK_LEVEL,
        lesson_type=LessonType.APPROVAL_POLICY,
        instruction="High-risk SLA commitments require SME approval.",
        applies_when="risk_level == high and category == support",
    )
    stress_test = StressTestCase(
        case_id="ST-001",
        generated_from_lesson_ids=[lesson.lesson_id],
        question_text="Can you guarantee 99.99% uptime for all customers?",
        category=QuestionCategory.SUPPORT,
        risk_hint=RiskLevel.HIGH,
        trap_type=StressTrapType.SLA_COMMITMENT,
        expected_safe_behavior=SafeBehavior.NEEDS_HUMAN_APPROVAL,
    )

    assert proposal.status == ProposalStatus.PENDING_REVIEW
    assert lesson.active is True
    assert stress_test.generated_from_lesson_ids == ["L-001"]
