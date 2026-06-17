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
    assert "Band Evidence" in response.text
    assert "Paths" in response.text
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
    assert "Band Evidence" in response.text
    assert "Human Gates" in response.text
    assert "Human approval" in response.text
    assert "Governed Evolution" in response.text
    assert "Demo-Safe Replay / Live Gate" in response.text
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
    assert "Orchestrator @ Decomposer" in response.text
    assert "Decomposer @ Retriever" in response.text
    assert "Reviewer @ Owner" in response.text
    assert "REST smoke verified" in response.text
    assert "Public replay · live gated" in response.text
    assert "Public replay is the demo-safe evidence path. Live Band mode is separately gated." in response.text
    assert "connected-peer autonomous replies remain pending" in response.text
    assert "Q-002 · included" in response.text
    assert "Q-004 · included" in response.text
    assert "Q-006 · excluded" in response.text
    assert "Policy owner must confirm incident response wording before this answer can be sent." in response.text


def test_replay_route_surfaces_customer_pack_decision_summary() -> None:
    response = client.get("/runs/demo/replay")

    assert response.status_code == 200
    assert "Customer Export" in response.text
    assert "7/8 answers enter the customer export" in response.text
    assert "Answer body is safe to send with evidence and approval refs." in response.text
    assert "<strong>Q-006</strong> · stale evidence EV-006 blocks final pack entry" in response.text
    assert "conflicting evidence EV-010 blocks final pack entry" in response.text
    assert "review status needs_human_approval blocks final pack entry" in response.text
    assert "Human decision keeps unsafe wording out" in response.text
    assert "Customer Export contains included answers only; blocked items stay in the review appendix until a human owner decision." in response.text


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
    assert "Included after SME Approver approval" in response.text
    assert "Included after Legal Reviewer approval" in response.text
    assert "Approval scope:" in response.text
    assert "SOC 2 summary availability and bridge-letter sharing for approved prospects in this Acme sample pack." in response.text
    assert "Valid for Acme sample pack only; renew before quoting a future SOC 2 period." in response.text
    assert "Region-restricted pilot wording only; does not approve an unconditional EU-only processing promise." in response.text
    assert "Valid for this sample replay until legal policy language changes." in response.text
    assert "EV-012-Q-004" in response.text
    assert "Hackathon demo / working prototype only." in response.text


def test_replay_route_makes_approval_workbench_product_readable() -> None:
    response = client.get("/runs/demo/replay")

    assert response.status_code == 200
    assert 'id="approval-workbench"' in response.text
    assert 'href="#approval-workbench">Approvals</a>' in response.text
    assert "Human approval product" in response.text
    assert "Scope, expiry, allowed wording and prohibited wording are visible before final-pack inclusion." in response.text
    assert "Approval scope" in response.text
    assert "Validity / expiry" in response.text
    assert "Allowed wording" in response.text
    assert "Prohibited wording" in response.text
    assert "Approved evidence refs are reviewer context, not a machine-enforced evidence-set gate." in response.text
    assert "SOC 2 summary availability and bridge-letter sharing for approved prospects." in response.text
    assert "Do not imply public SOC 2 distribution, certification, or blanket access." in response.text
    assert "Bounded region-restricted pilot wording from the legal approval scope." in response.text
    assert "Do not promise unconditional EU-only processing." in response.text
    assert "No customer wording is approved yet." in response.text
    assert "Do not commit to an incident-response notification target until policy owner approval." in response.text
    assert "No approved evidence refs are attached yet." in response.text


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
    assert "Business readout" in response.text
    assert "Question answered" in response.text
    assert "Evidence confidence" in response.text
    assert "Review / approval" in response.text
    assert "Risk contained" in response.text
    assert "SME Approver approved scoped wording" in response.text
    assert "Legal Reviewer approved scoped wording" in response.text
    assert "Security owns Q-006; support request, high risk" in response.text
    assert "Evidence mix includes conflicting, stale refs; freshness rollup is conflicting" in response.text
    assert "requires human approval; no valid scoped approval is attached yet." in response.text
    assert "Final pack excluded" in response.text
    assert "stale evidence, conflicting evidence and missing scoped human approval keep this answer out" in response.text
    assert "Needs human approval" in response.text
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
    assert "Role Map" in response.text
    assert "Workflow roles are shown by responsibility first; human approval gates are not presented as autonomous agents." in response.text
    assert "Breaks the questionnaire into answer tasks with owner and risk context." in response.text
    assert "Attaches approved evidence refs and labels freshness before drafting." in response.text
    assert "Writes bounded answer copy that stays tied to evidence and review limits." in response.text
    assert "Challenges risky wording, requests clarification and blocks unsafe commitments." in response.text
    assert "sample human gates, not autonomous agents." in response.text
    assert "SME Approver (human gate) → trustroom-orchestrator-agent" in response.text
    assert "Collaboration Map" in response.text
    assert "answer · agent · blocker · final-pack status" in response.text
    assert "By answer" in response.text
    assert "By agent" in response.text
    assert "By blocker" in response.text
    assert "By final-pack status" in response.text
    assert "Q-004: review loop -&gt; legal gate -&gt; included" in response.text
    assert "Q-006: blocker -&gt; policy owner -&gt; excluded" in response.text
    assert "stale/conflicting evidence plus missing scoped human approval keeps it out" in response.text
    assert "7 answers included; 1 held outside customer materials." in response.text
    assert "Business Milestones" in response.text
    assert "Representative Item Traces" in response.text
    assert "Blocked Impact Path" in response.text
    assert "Public replay is the demo-safe evidence path. Live Band mode is separately gated." in response.text
    assert re.search(r"Review loops</span>\s*<strong>1</strong>", response.text)
    assert "<summary>handoff detail</summary>" in response.text
    assert "<summary>show handoffs</summary>" in response.text
    assert "requirement-decomposer-agent → evidence-retriever-agent" in response.text
    assert "evidence-retriever-agent → answer-drafter-agent" in response.text
    assert "answer-drafter-agent → compliance-review-agent" in response.text
    assert "compliance-review-agent → evidence-retriever-agent" in response.text
    assert "EVT-009" in response.text
    assert "Q-004" in response.text
    assert "Reviewer loop, legal approval." in response.text
    assert "Legal Reviewer approved scoped sample wording: Legal approved bounded region-processing language." in response.text
    assert "APP-Q-004" in response.text
    assert "Q-006" in response.text
    assert "stale/conflicting incident evidence" in response.text
    assert "no valid human approval" in response.text
    assert "final pack excluded" in response.text
    assert "Current evidence still gates Final Pack entry." in response.text
    assert "Owner review suggestion" in response.text
    assert "evidence-retriever-agent proposed replacement evidence EV-013" in response.text
    assert "replacement suggestion ORS-Q-006 is proposed" in response.text


def test_replay_route_turns_q006_into_buyer_safe_story() -> None:
    response = client.get("/runs/demo/replay")

    assert response.status_code == 200
    assert 'id="q006-buyer-story"' in response.text
    assert 'href="#q006-buyer-story">Buyer Story</a>' in response.text
    assert "Q-006 buyer-safe story" in response.text
    assert "Unsafe incident-response wording is held outside the customer export" in response.text
    assert "risky incident-response wording" in response.text
    assert "stale/conflicting evidence" in response.text
    assert "no valid human approval" in response.text
    assert "excluded from customer pack" in response.text
    assert "policy owner action" in response.text
    assert "Customer Export stays at 7/8 until this owner decision is complete." in response.text
    assert "REV-Q-006" in response.text
    assert "ORS-Q-006" in response.text


def test_replay_route_surfaces_responsibility_queue_workbench() -> None:
    response = client.get("/runs/demo/replay")

    assert response.status_code == 200
    assert 'id="responsibility-queue"' in response.text
    assert 'href="#responsibility-queue">Work Queue</a>' in response.text
    assert "Responsibility Queue" in response.text
    assert "1 open owner action · 2 completed human gates" in response.text
    assert "Q-006 · final pack excluded" in response.text
    assert "Security Policy Owner" in response.text
    assert "SLA before customer export" in response.text
    assert "High risk" in response.text
    assert "Escalation Security leadership" in response.text
    assert "SME Approver" in response.text
    assert "Legal Reviewer" in response.text
    assert "human gate complete" in response.text
    assert "Queue fields are fictional sample workflow metadata; no live account dependency is required." in response.text


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
    assert 'id="collaboration-map"' in response.text
    assert 'href="#collaboration-map">Collab Map</a>' in response.text
    assert 'id="representative-item-traces"' in response.text
    assert 'href="#representative-item-traces">Item Traces</a>' in response.text
    assert 'id="blocked-impact-path"' in response.text
    assert 'href="#blocked-impact-path">Q-006 Blocked Path</a>' in response.text
    assert 'id="responsibility-queue"' in response.text
    assert 'href="#responsibility-queue">Work Queue</a>' in response.text
    assert 'id="approval-workbench"' in response.text
    assert 'href="#approval-workbench">Approvals</a>' in response.text
    assert 'id="final-pack"' in response.text
    assert 'href="#final-pack">Final Pack</a>' in response.text
    assert 'id="product-roadmap"' in response.text
    assert 'href="#product-roadmap">Roadmap</a>' in response.text
    assert 'id="replay-live-boundary"' in response.text
    assert 'href="#replay-live-boundary">Replay Boundary</a>' in response.text
    assert "Public replay · live gated" in response.text


def test_replay_route_surfaces_product_roadmap_without_overclaim() -> None:
    response = client.get("/runs/demo/replay")

    assert response.status_code == 200
    assert 'aria-label="Product roadmap direction"' in response.text
    assert "Workspace / Evidence / Export Roadmap" in response.text
    assert "Product direction, not a live multi-workspace deployment." in response.text
    assert "Workspace Queue" in response.text
    assert "multi-RFP queue" in response.text
    assert "Evidence Library" in response.text
    assert "SOC 2" in response.text
    assert "architecture docs" in response.text
    assert "Export Workflow" in response.text
    assert "customer-safe export" in response.text
    assert "internal review appendix" in response.text
    assert "blocked exceptions" in response.text
    assert "appendix visibility remains a human/business-owner decision" in response.text
