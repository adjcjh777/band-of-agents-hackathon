from __future__ import annotations

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
    assert "Submission Readiness" in response.text
    assert "Evidence Coverage" in response.text
    assert "Approval Queue" in response.text
    assert "Reviewer Decision Matrix" in response.text
    assert "Final Pack" in response.text
    assert "MOCK" in response.text


def test_replay_route_is_clearly_labeled_and_contains_judge_signals() -> None:
    response = client.get("/runs/demo/replay")

    assert response.status_code == 200
    assert "RFP TrustRoom" in response.text
    assert "Submission Readiness" in response.text
    assert "Evidence Coverage" in response.text
    assert "Approval Queue" in response.text
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
    assert "7 of 8 answers can enter the pack; 1 blocker must stay out." in response.text
    assert "Policy owner must confirm incident response wording before this answer can be sent." in response.text


def test_replay_route_surfaces_reviewer_evidence_matrix() -> None:
    response = client.get("/runs/demo/replay")

    assert response.status_code == 200
    assert "Reviewer Decision Matrix" in response.text
    assert "Incident Response Policy v2024.11" in response.text
    assert "Support Addendum Draft" in response.text
    assert "EU Residency Gap Note" in response.text
    assert "stale evidence EV-006 needs review or human approval" in response.text
    assert "conflicting evidence EV-010 needs review" in response.text
    assert "missing" in response.text
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
