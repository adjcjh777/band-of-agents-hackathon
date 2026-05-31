from __future__ import annotations

from trustroom.agents.mock_runner import run_mock_trustroom
from trustroom.models import EventType, ExecutionMode, ReviewStatus, RiskLevel, TimelineEvent


def test_mock_runner_outputs_typed_timeline_events() -> None:
    result = run_mock_trustroom()

    assert result.run.mode == ExecutionMode.MOCK
    assert result.events
    assert all(isinstance(event, TimelineEvent) for event in result.events)
    assert any(event.event_type == EventType.FINAL_PACK_CREATED for event in result.events)


def test_mock_runner_has_at_least_three_distinct_agent_senders() -> None:
    result = run_mock_trustroom()
    agent_senders = {
        event.sender
        for event in result.events
        if event.sender.endswith("-agent")
    }

    assert agent_senders >= {
        "trustroom-orchestrator-agent",
        "requirement-decomposer-agent",
        "evidence-retriever-agent",
        "answer-drafter-agent",
        "compliance-review-agent",
    }


def test_mock_runner_contains_reviewer_to_retriever_loop() -> None:
    result = run_mock_trustroom()

    assert any(
        event.sender == "compliance-review-agent"
        and event.receiver == "evidence-retriever-agent"
        and event.event_type == EventType.HANDOFF
        for event in result.events
    )


def test_high_risk_stale_policy_requires_sme_approval_before_final_pack() -> None:
    result = run_mock_trustroom()
    high_risk_items = {
        item.item_id
        for item in result.questions
        if item.risk_level == RiskLevel.HIGH
    }
    approved_items = {approval.item_id for approval in result.approvals}

    assert "Q-006" in high_risk_items
    assert "Q-006" not in approved_items
    assert "Q-006" in result.final_pack.blocked_item_ids
    assert all(
        draft.item_id != "Q-006"
        for draft in result.drafts
        if draft.answer_id in result.final_pack.included_answer_ids
    )
    assert any(
        review.item_id == "Q-006"
        and review.status == ReviewStatus.NEEDS_HUMAN_APPROVAL
        for review in result.reviews
    )


def test_final_pack_has_evidence_index_and_blockers() -> None:
    result = run_mock_trustroom()

    assert result.final_pack.readiness_summary == "blocked"
    assert result.final_pack.evidence_index
    assert "Q-006" in result.final_pack.blocked_item_ids
    assert len(result.final_pack.included_answer_ids) >= 7
