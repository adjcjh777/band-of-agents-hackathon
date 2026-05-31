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
    assert "Submission Readiness" in response.text
    assert "Evidence Coverage" in response.text
    assert "Approval Queue" in response.text
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
