from __future__ import annotations

import pytest

from trustroom.evolution import (
    ExperienceLedger,
    ProposalValidationError,
)
from trustroom.models import (
    EventType,
    EvolutionProposal,
    ExecutionMode,
    ProposalStatus,
    ProposalType,
    RiskLevel,
    Run,
    RunState,
    TimelineEvent,
)


def _event(event_id: str, *, run_id: str = "run-demo") -> TimelineEvent:
    return TimelineEvent(
        event_id=event_id,
        run_id=run_id,
        sender="compliance-review-agent",
        receiver="workflow-improvement-agent",
        event_type=EventType.REVIEW_DECISION,
        task_state=RunState.POST_RUN_REVIEW,
        payload_summary="Reviewer found a late high-risk SLA escalation.",
        related_object_ids=["Q-006"],
        band_message_ref=f"mock:event:{event_id}",
    )


def _proposal(
    proposal_id: str = "P-001",
    *,
    run_id: str = "run-demo",
    proposal_type: ProposalType = ProposalType.REVIEWER_GATE,
    proposed_change: str = "Route high-risk SLA commitments to human approval before final pack.",
    supporting_event_ids: list[str] | None = None,
) -> EvolutionProposal:
    return EvolutionProposal(
        proposal_id=proposal_id,
        run_id=run_id,
        proposal_type=proposal_type,
        target_component="compliance-review-agent",
        problem_statement="High-risk SLA commitments reached review too late.",
        supporting_event_ids=supporting_event_ids if supporting_event_ids is not None else ["E-review"],
        proposed_change=proposed_change,
        expected_effect="Reduce late request_changes loops while preserving human approval.",
        risk_level=RiskLevel.MEDIUM,
        evaluation_plan="Replay the SLA fixture and confirm unsafe answers route to human approval.",
    )


def test_proposal_without_supporting_events_cannot_become_active_lesson() -> None:
    ledger = ExperienceLedger(events=[_event("E-review")])
    unsupported = _proposal(supporting_event_ids=[])

    with pytest.raises(ProposalValidationError, match="supporting timeline event"):
        ledger.review_proposal(
            unsupported,
            decision=ProposalStatus.APPROVED,
            reviewer="evolution-reviewer",
            reviewer_notes="Looks useful, but has no trace evidence.",
        )

    assert ledger.active_lessons() == []


@pytest.mark.parametrize(
    ("proposal_type", "proposed_change"),
    [
        (
            ProposalType.REVIEWER_GATE,
            "Remove the human approval gate for high-risk commitments to speed up submission.",
        ),
        (
            ProposalType.NO_OVERCLAIM_RULE,
            "Delete the no-overclaim checklist so certified and guaranteed claims can pass.",
        ),
    ],
)
def test_proposal_that_weakens_governance_is_rejected(
    proposal_type: ProposalType,
    proposed_change: str,
) -> None:
    ledger = ExperienceLedger(events=[_event("E-review")])
    unsafe = _proposal(
        proposal_type=proposal_type,
        proposed_change=proposed_change,
    )

    reviewed = ledger.review_proposal(
        unsafe,
        decision=ProposalStatus.APPROVED,
        reviewer="evolution-reviewer",
        reviewer_notes="Requested as an optimization.",
    )

    assert reviewed.status == ProposalStatus.REJECTED
    assert "safety" in reviewed.reviewer_notes.lower()
    assert ledger.active_lessons() == []


def test_approved_proposal_creates_lesson_and_loads_next_run_context() -> None:
    ledger = ExperienceLedger(events=[_event("E-review")])
    approved = ledger.review_proposal(
        _proposal(),
        decision=ProposalStatus.APPROVED,
        reviewer="evolution-reviewer",
        reviewer_notes="Approved for next mock run.",
    )
    next_run = Run(
        run_id="run-next",
        case_id="case-acme",
        mode=ExecutionMode.MOCK,
        state=RunState.INTAKE,
        band_room_label="mock-room-next",
    )

    run_with_lessons = ledger.load_active_lessons(next_run)

    assert approved.status == ProposalStatus.APPROVED
    assert [lesson.source_proposal_id for lesson in ledger.active_lessons()] == ["P-001"]
    assert run_with_lessons.active_lessons == ["lesson-P-001"]


def test_agent_cannot_approve_its_own_evolution_proposal() -> None:
    ledger = ExperienceLedger(events=[_event("E-review")])

    with pytest.raises(ProposalValidationError, match="human evolution reviewer"):
        ledger.review_proposal(
            _proposal(),
            decision=ProposalStatus.APPROVED,
            reviewer="workflow-improvement-agent",
            reviewer_notes="Self-approved optimization.",
        )

    assert ledger.active_lessons() == []


def test_non_approved_review_statuses_do_not_activate_lessons() -> None:
    ledger = ExperienceLedger(events=[_event("E-review")])

    for decision in (
        ProposalStatus.REJECTED,
        ProposalStatus.REQUEST_CHANGES,
        ProposalStatus.DEFERRED,
    ):
        reviewed = ledger.review_proposal(
            _proposal(proposal_id=f"P-{decision.value}"),
            decision=decision,
            reviewer="evolution-reviewer",
            reviewer_notes=f"Reviewer chose {decision.value}.",
        )
        assert reviewed.status == decision

    assert ledger.active_lessons() == []


def test_rollback_marks_lesson_inactive_and_preserves_note() -> None:
    ledger = ExperienceLedger(events=[_event("E-review")])
    ledger.review_proposal(
        _proposal(),
        decision=ProposalStatus.APPROVED,
        reviewer="evolution-reviewer",
        reviewer_notes="Approved for next mock run.",
    )

    rolled_back = ledger.rollback_lesson(
        "lesson-P-001",
        rollback_note="Readiness check failed after applying this approval policy.",
    )

    assert rolled_back.active is False
    assert rolled_back.rollback_note == "Readiness check failed after applying this approval policy."
    assert ledger.active_lessons() == []
