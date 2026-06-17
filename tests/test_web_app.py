from __future__ import annotations

import re

from fastapi.testclient import TestClient

from trustroom.web.app import app


client = TestClient(app)


def test_health_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_index_links_to_demo_routes() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "RFP TrustRoom" in response.text
    assert "/runs/demo" in response.text
    assert "/runs/demo/replay" in response.text


def test_mock_demo_route_renders_enterprise_dashboard() -> None:
    response = client.get("/runs/demo")

    assert response.status_code == 200
    assert "RFP TrustRoom" in response.text
    assert "Draft pack ready with exclusions" in response.text
    assert "Sendable" in response.text
    assert "Evidence" in response.text
    assert "Human Gates" in response.text
    assert "Reviewer Decision Matrix" in response.text
    assert "Final Pack" in response.text
    assert "MOCK" in response.text


def test_replay_route_is_clearly_labeled_and_contains_judge_signals() -> None:
    response = client.get("/runs/demo/replay")

    assert response.status_code == 200
    assert "RFP TrustRoom" in response.text
    assert "Sendable" in response.text
    assert "Evidence" in response.text
    assert "Human Gates" in response.text
    assert "Human approval" in response.text
    assert "Governed Evolution" in response.text
    assert "Replay / Live Evidence" in response.text
    assert "REPLAY" in response.text


def test_replay_route_surfaces_enterprise_decision_context() -> None:
    response = client.get("/runs/demo/replay")

    assert response.status_code == 200
    assert "Acme Financial Services Security RFP" in response.text
    assert "Fictional regional financial services buyer" in response.text
    assert "Create an evidence-backed RFP and security questionnaire response pack" in response.text
    assert "security questionnaire" in response.text
    assert "Draft pack ready with exclusions" in response.text
    assert "7/8 ready · 1 blocked outside." in response.text
    assert "Human @ TrustRoom" in response.text
    assert "Decomposer @ Retriever" in response.text
    assert "Reviewer @ Owner" in response.text
    assert "Policy owner must confirm incident response wording before this answer can be sent." in response.text


def test_replay_route_surfaces_reviewer_evidence_matrix() -> None:
    response = client.get("/runs/demo/replay")

    assert response.status_code == 200
    assert "Reviewer Decision Matrix" in response.text
    assert "Incident Response Policy v2024.11" in response.text
    assert "Support Addendum Draft" in response.text
    assert "EU Residency Gap Note" in response.text
    assert "Incident Response Policy Candidate v2026.06" in response.text
    assert "stale evidence EV-006 blocks final pack entry" in response.text
    assert "conflicting evidence EV-010 blocks final pack entry" in response.text
    assert "missing" in response.text
    assert "Q-006 · security · conflicting" in response.text
    assert "Marked by evidence-retriever-agent" in response.text
    assert "questionnaire.csv:7" in response.text
    assert "REV-Q-006" in response.text


def test_replay_route_surfaces_human_approval_basis() -> None:
    response = client.get("/runs/demo/replay")

    assert response.status_code == 200
    assert "SME approved current SOC 2 bridge-letter wording." in response.text
    assert "Legal approved bounded region-processing language." in response.text
    assert "APP-Q-002" in response.text
    assert "APP-Q-004" in response.text
    assert "Included after sme-approver approval" in response.text
    assert "Included after legal-reviewer approval" in response.text
    assert "Approval scope:" in response.text
    assert "SOC 2 summary availability and bridge-letter sharing for approved prospects in this Acme sample pack." in response.text
    assert "Valid for Acme sample pack only; renew before quoting a future SOC 2 period." in response.text
    assert "Region-restricted pilot wording only; does not approve an unconditional EU-only processing promise." in response.text
    assert "Valid for this sample replay until legal policy language changes." in response.text
    assert "EV-012-Q-004" in response.text
    assert "Hackathon demo / working prototype only." in response.text


def test_replay_route_surfaces_customer_safe_answer_copy_and_followups() -> None:
    response = client.get("/runs/demo/replay")

    assert response.status_code == 200
    assert "Draft answer for" not in response.text
    assert "A current SOC 2 Type II summary is available for approved prospects" in response.text
    assert "unconditional EU-only processing commitment requires legal approval" in response.text
    assert "should not commit to an incident-response notification target" in response.text
    assert "No further action for the sample pack; keep bridge-letter sharing gated to approved prospects." in response.text
    assert "No further action for the sample pack; preserve the unconditional residency exclusion." in response.text
    assert "Security policy owner must confirm current incident-response notification language before customer use." in response.text


def test_replay_route_surfaces_answer_lineage_drilldown() -> None:
    response = client.get("/runs/demo/replay")

    assert response.status_code == 200
    assert "Evidence lineage" in response.text
    assert "Question → Evidence → Draft → Review → Approval → Final Pack" in response.text
    assert "Question intake" in response.text
    assert "Customer-safe draft" in response.text
    assert "Human approval" in response.text
    assert "Final pack decision" in response.text
    assert "EV-004" in response.text
    assert "APP-Q-004" in response.text
    assert "included" in response.text
    assert "No human approval record is attached to this answer." in response.text
    assert "excluded" in response.text
    assert "conflicting evidence EV-010 blocks final pack entry" in response.text


def test_replay_route_surfaces_agent_handoff_trace_view() -> None:
    response = client.get("/runs/demo/replay")

    assert response.status_code == 200
    assert "Run Trace" in response.text
    assert 'class="band-rail"' in response.text
    assert "Human @ TrustRoom" in response.text
    assert "Agent Handoff Chain" in response.text
    assert "Business Milestones" in response.text
    assert "Representative Item Traces" in response.text
    assert "Blocked Impact Path" in response.text
    assert "REPLAY fallback, not live Band" in response.text
    assert re.search(r"Review loops</span>\s*<strong>1</strong>", response.text)
    assert "Sender → Receiver → State change" in response.text
    assert "<summary>handoff detail</summary>" in response.text
    assert "<summary>show handoffs</summary>" in response.text
    assert "requirement-decomposer-agent → evidence-retriever-agent" in response.text
    assert "evidence-retriever-agent → answer-drafter-agent" in response.text
    assert "answer-drafter-agent → compliance-review-agent" in response.text
    assert "compliance-review-agent → evidence-retriever-agent" in response.text
    assert "EVT-009" in response.text
    assert "Q-004" in response.text
    assert "Reviewer loop, legal approval." in response.text
    assert "legal-reviewer approved scoped sample wording: Legal approved bounded region-processing language." in response.text
    assert "APP-Q-004" in response.text
    assert "Q-006" in response.text
    assert "stale/conflicting incident evidence" in response.text
    assert "no valid human approval" in response.text
    assert "final pack excluded" in response.text
    assert "Current evidence still gates Final Pack entry." in response.text
    assert "Owner review suggestion" in response.text
    assert "evidence-retriever-agent proposed replacement evidence EV-013" in response.text
    assert "replacement suggestion ORS-Q-006 is proposed" in response.text


def test_replay_route_surfaces_review_appendix_visibility_and_owner_suggestion() -> None:
    response = client.get("/runs/demo/replay")

    assert response.status_code == 200
    assert "With Appendix" in response.text
    assert "<summary>evidence refs</summary>" in response.text
    assert "<summary>review appendix</summary>" in response.text
    assert "<summary>approval basis</summary>" in response.text
    assert "Review Appendix Detail" in response.text
    assert "customer-safe" in response.text
    assert "Owner review card" in response.text
    assert "ORS-Q-006 · proposed" in response.text
    assert "suggests EV-013" in response.text
    assert "replaces EV-006" in response.text
    assert "replaces EV-010" in response.text
    assert "raw customer policy text" not in response.text


def test_customer_export_api_defaults_to_included_answer_body_only() -> None:
    response = client.get("/api/runs/demo/replay/customer-export")

    assert response.status_code == 200
    payload = response.json()
    item_ids = {answer["item_id"] for answer in payload["answer_body"]}

    assert payload["mode"] == "replay"
    assert payload["review_appendix"] is None
    assert payload["review_appendix_export_record"] is None
    assert "Q-006" not in item_ids
    assert "Q-004" in item_ids
    assert "should not commit to an incident-response notification target" not in str(payload["answer_body"])


def test_customer_export_api_includes_customer_safe_appendix_only_when_requested() -> None:
    response = client.get("/api/runs/demo/replay/customer-export?include_review_appendix=true")

    assert response.status_code == 200
    payload = response.json()
    q6_exception = next(
        item
        for item in payload["review_appendix"]["exceptions"]
        if item["question_item"] == "Q-006"
    )

    assert payload["review_appendix"]["visibility_mode"] == "customer-safe"
    assert payload["review_appendix"]["not_customer_submittable"] is True
    assert payload["review_appendix_export_record"]["decision"] == "include_appendix"
    assert payload["review_appendix_export_record"]["owner_role"] == "Security Policy Owner"
    assert q6_exception["inclusion"] == "excluded"
    assert q6_exception["owner"] == "Security Policy Owner"
    assert "conflicting evidence EV-010 blocks final pack entry" in q6_exception["reason_or_blocker"]
    assert "should not commit to an incident-response notification target" not in str(payload["answer_body"])


def test_customer_export_page_keeps_appendix_out_by_default() -> None:
    response = client.get("/runs/demo/replay/customer-export")

    assert response.status_code == 200
    assert "Customer Export" in response.text
    assert "Included Answers only" in response.text
    assert "No appendix is attached to this customer export." in response.text
    assert "A current SOC 2 Type II summary is available for approved prospects" in response.text
    assert "should not commit to an incident-response notification target" not in response.text


def test_customer_export_page_marks_requested_appendix_as_non_submittable() -> None:
    response = client.get("/runs/demo/replay/customer-export?include_review_appendix=true")

    assert response.status_code == 200
    assert "Review Appendix" in response.text
    assert "not customer-submittable" in response.text
    assert "RAER-CE-ACME-v1" in response.text
    assert "Q-006" in response.text
    assert "EV-013 · current" in response.text
    assert "should not commit to an incident-response notification target" not in response.text


def test_replay_route_provides_judge_recording_anchor_navigation() -> None:
    response = client.get("/runs/demo/replay")

    assert response.status_code == 200
    assert 'aria-label="Judge route and recording route"' in response.text
    assert 'id="executive-decision"' in response.text
    assert 'href="#executive-decision">Executive Decision</a>' in response.text
    assert 'id="run-trace"' in response.text
    assert 'href="#run-trace">Run Trace</a>' in response.text
    assert 'id="business-milestones"' in response.text
    assert 'href="#business-milestones">Milestones</a>' in response.text
    assert 'id="agent-handoff-chain"' in response.text
    assert 'href="#agent-handoff-chain">Handoff Chain</a>' in response.text
    assert 'id="representative-item-traces"' in response.text
    assert 'href="#representative-item-traces">Item Traces</a>' in response.text
    assert 'id="blocked-impact-path"' in response.text
    assert 'href="#blocked-impact-path">Q-006 Blocked Path</a>' in response.text
    assert 'id="final-pack"' in response.text
    assert 'href="#final-pack">Final Pack</a>' in response.text
    assert 'id="replay-live-boundary"' in response.text
    assert 'href="#replay-live-boundary">Replay Boundary</a>' in response.text
    assert "REPLAY fallback, not live Band" in response.text
