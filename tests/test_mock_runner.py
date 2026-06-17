from __future__ import annotations

from trustroom.agents.mock_runner import run_mock_trustroom
from trustroom.models import EventType, ExecutionMode, OwnerReviewSuggestionStatus, ReviewStatus, RiskLevel, TimelineEvent
from trustroom.readiness import find_overclaim_phrases


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


def test_mock_runner_outputs_customer_safe_non_generic_answer_copy() -> None:
    result = run_mock_trustroom()
    drafts_by_item = {draft.item_id: draft for draft in result.drafts}

    assert all(
        not draft.draft_text.startswith("Draft answer for")
        for draft in result.drafts
    )
    assert all(not find_overclaim_phrases(draft.draft_text) for draft in result.drafts)
    assert "bridge letter" in drafts_by_item["Q-002"].draft_text
    assert "approved prospects" in drafts_by_item["Q-002"].draft_text
    assert "unconditional EU-only processing commitment requires legal approval" in drafts_by_item["Q-004"].draft_text
    assert "should not commit" in drafts_by_item["Q-006"].draft_text
    assert "72 hour" not in drafts_by_item["Q-006"].draft_text.lower()


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


def test_high_risk_approvals_and_blockers_have_actionable_follow_up() -> None:
    result = run_mock_trustroom()
    approvals_by_item = {approval.item_id: approval for approval in result.approvals}
    reviews_by_item = {review.item_id: review for review in result.reviews}

    assert approvals_by_item["Q-002"].answer_id == "A-002"
    assert approvals_by_item["Q-002"].approved_evidence_ids == ["EV-002", "EV-012-Q-002"]
    assert "Acme sample pack" in approvals_by_item["Q-002"].scope
    assert "renew before quoting a future SOC 2 period" in approvals_by_item["Q-002"].expires_at_label
    assert approvals_by_item["Q-002"].required_follow_up is not None
    assert "bridge-letter sharing gated" in approvals_by_item["Q-002"].required_follow_up
    assert approvals_by_item["Q-004"].answer_id == "A-004R"
    assert approvals_by_item["Q-004"].approved_evidence_ids == ["EV-004", "EV-012-Q-004"]
    assert "does not approve an unconditional EU-only processing promise" in approvals_by_item["Q-004"].scope
    assert "sample replay" in approvals_by_item["Q-004"].expires_at_label
    assert approvals_by_item["Q-004"].required_follow_up is not None
    assert "unconditional residency exclusion" in approvals_by_item["Q-004"].required_follow_up
    assert reviews_by_item["Q-006"].required_follow_up is not None
    assert "Security policy owner" in reviews_by_item["Q-006"].required_follow_up


def test_mock_runner_creates_owner_review_suggestion_for_replacement_evidence() -> None:
    result = run_mock_trustroom()
    suggestions_by_item = {
        suggestion.item_id: suggestion
        for suggestion in result.owner_review_suggestions
    }

    suggestion = suggestions_by_item["Q-006"]

    assert suggestion.status == OwnerReviewSuggestionStatus.PROPOSED
    assert suggestion.proposed_by == "evidence-retriever-agent"
    assert suggestion.suggested_evidence_ids == ["EV-013"]
    assert suggestion.replaces_evidence_ids == ["EV-006", "EV-010"]
    assert "owner review" in suggestion.reason
    assert any(
        event.event_type == EventType.OWNER_REVIEW_SUGGESTION
        and "EV-013" in event.related_object_ids
        for event in result.events
    )


def test_mock_runner_builds_answer_lineage_for_reviewer_drilldown() -> None:
    result = run_mock_trustroom()
    lineage_by_item = {lineage.item_id: lineage for lineage in result.lineage}

    assert set(lineage_by_item) >= {"Q-002", "Q-004", "Q-006"}
    assert [step.stage for step in lineage_by_item["Q-004"].steps] == [
        "question",
        "evidence",
        "draft",
        "review",
        "approval",
        "final_pack",
    ]
    q4_steps = {step.stage: step for step in lineage_by_item["Q-004"].steps}
    assert q4_steps["evidence"].object_ids == ["EV-004", "EV-012-Q-004"]
    assert q4_steps["approval"].object_ids == ["APP-Q-004"]
    assert "Scope:" in q4_steps["approval"].reason
    assert "Validity: valid" in q4_steps["approval"].reason
    assert "Covered evidence: EV-004, EV-012-Q-004" in q4_steps["approval"].reason
    assert q4_steps["final_pack"].status == "included"

    q6_steps = {step.stage: step for step in lineage_by_item["Q-006"].steps}
    assert q6_steps["evidence"].status == "rollup:conflicting; conflicting:1, current:2, stale:1"
    assert q6_steps["approval"].status == "missing"
    assert q6_steps["final_pack"].status == "excluded"
    assert "conflicting evidence EV-010 blocks final pack entry" in q6_steps["final_pack"].reason


def test_final_pack_has_evidence_index_and_blockers() -> None:
    result = run_mock_trustroom()

    assert result.final_pack.readiness_summary == "blocked"
    assert result.final_pack.evidence_index
    assert result.final_pack.freshness_rollup["Q-006"] == "conflicting"
    assert result.final_pack.visibility_mode == "customer-safe"
    assert "Q-006" in result.final_pack.blocked_item_ids
    assert len(result.final_pack.included_answer_ids) >= 7
