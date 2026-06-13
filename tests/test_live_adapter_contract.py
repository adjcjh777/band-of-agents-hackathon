from __future__ import annotations

import urllib.request

import pytest

from trustroom.band.live_adapter import (
    LiveBandAdapter,
    LiveBandConfig,
    LiveBandConfigurationError,
    UrllibBandHTTPClient,
)
from trustroom.models import EventType, ExecutionMode, RunState


class FakeBandHTTPClient:
    def __init__(self) -> None:
        self.requests: list[tuple[str, dict[str, object], str]] = []
        self.responses: list[dict[str, object]] = []

    def post(self, path: str, payload: dict[str, object], *, api_key: str) -> dict[str, object]:
        self.requests.append((path, payload, api_key))
        if not self.responses:
            raise AssertionError(f"no fake response queued for {path}")
        return self.responses.pop(0)


class FakeHTTPResponse:
    def __enter__(self) -> FakeHTTPResponse:
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        return None

    def read(self) -> bytes:
        return b'{"data":{"id":"chat-ok"}}'


def live_config(**overrides: object) -> LiveBandConfig:
    values: dict[str, object] = {
        "rest_url": "https://platform.dev.band.ai",
        "agent_id": "agent-self",
        "api_key": "test-key",
        "agent_directory": {"requirement-decomposer-agent": "peer-decomposer"},
    }
    values.update(overrides)
    return LiveBandConfig(**values)


def test_live_config_requires_runtime_credentials_without_echoing_values() -> None:
    with pytest.raises(LiveBandConfigurationError) as exc_info:
        LiveBandConfig.from_env({"BAND_REST_URL": "https://platform.dev.band.ai"})

    message = str(exc_info.value)
    assert "BAND_AGENT_ID" in message
    assert "BAND_AGENT_KEY" in message
    assert "https://platform.dev.band.ai" not in message


def test_urllib_client_sends_browser_safe_user_agent(monkeypatch: pytest.MonkeyPatch) -> None:
    seen_headers: dict[str, str] = {}

    def fake_urlopen(request: urllib.request.Request, timeout: float) -> FakeHTTPResponse:
        seen_headers.update(dict(request.header_items()))
        assert timeout == 10.0
        return FakeHTTPResponse()

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    response = UrllibBandHTTPClient("https://app.band.ai").post(
        "/api/v1/agent/chats",
        {"chat": {}},
        api_key="test-key",
    )

    assert response == {"data": {"id": "chat-ok"}}
    assert seen_headers["User-agent"].startswith("RFP-TrustRoom-Hackathon/")


def test_create_room_uses_agent_api_and_redacts_live_chat_ref() -> None:
    http = FakeBandHTTPClient()
    http.responses.append({"data": {"id": "chat-raw-id"}})
    adapter = LiveBandAdapter(config=live_config(), http=http)

    room = adapter.create_room(run_id="run-live", case_name="Acme Security RFP")

    assert room.mode == ExecutionMode.LIVE
    assert room.live_ref is not None
    assert room.live_ref.startswith("band-ref:")
    assert "chat-raw-id" not in room.live_ref
    assert http.requests == [
        ("/api/v1/agent/chats", {"chat": {}}, "test-key"),
    ]


def test_send_message_posts_to_chat_and_keeps_redacted_timeline() -> None:
    http = FakeBandHTTPClient()
    http.responses.extend(
        [
            {"data": {"id": "chat-raw-id"}},
            {"data": {"id": "message-raw-id", "success": True}},
        ]
    )
    adapter = LiveBandAdapter(config=live_config(), http=http)
    adapter.create_room(run_id="run-live", case_name="Acme Security RFP")

    event = adapter.send_message(
        run_id="run-live",
        sender="trustroom-orchestrator-agent",
        receiver="requirement-decomposer-agent",
        message="Please triage the questionnaire rows.",
        task_state=RunState.TRIAGE,
    )

    assert http.requests[1] == (
        "/api/v1/agent/chats/chat-raw-id/messages",
        {"message": {"content": "Please triage the questionnaire rows.", "mentions": []}},
        "test-key",
    )
    assert event.event_type == EventType.TASK_ASSIGNED
    assert event.band_message_ref.startswith("band-ref:")
    assert "message-raw-id" not in event.band_message_ref
    assert adapter.get_room_timeline("run-live") == [event]


def test_mention_agent_requires_peer_directory_entry() -> None:
    http = FakeBandHTTPClient()
    http.responses.append({"data": {"id": "chat-raw-id"}})
    adapter = LiveBandAdapter(config=live_config(agent_directory={}), http=http)
    adapter.create_room(run_id="run-live", case_name="Acme Security RFP")

    with pytest.raises(LiveBandConfigurationError):
        adapter.mention_agent(
            run_id="run-live",
            sender="trustroom-orchestrator-agent",
            agent_name="requirement-decomposer-agent",
            instruction="Please triage the questionnaire rows.",
            task_state=RunState.TRIAGE,
        )


def test_mention_agent_adds_participant_then_sends_structured_mention() -> None:
    http = FakeBandHTTPClient()
    http.responses.extend(
        [
            {"data": {"id": "chat-raw-id"}},
            {"data": {"id": "participant-id", "status": "active"}},
            {"data": {"id": "message-raw-id", "success": True}},
        ]
    )
    adapter = LiveBandAdapter(config=live_config(), http=http)
    adapter.create_room(run_id="run-live", case_name="Acme Security RFP")

    event = adapter.mention_agent(
        run_id="run-live",
        sender="trustroom-orchestrator-agent",
        agent_name="requirement-decomposer-agent",
        instruction="Please triage the questionnaire rows.",
        task_state=RunState.TRIAGE,
        related_object_ids=["Q-001"],
    )

    assert http.requests[1] == (
        "/api/v1/agent/chats/chat-raw-id/participants",
        {"participant": {"participant_id": "peer-decomposer"}},
        "test-key",
    )
    assert http.requests[2] == (
        "/api/v1/agent/chats/chat-raw-id/messages",
        {
            "message": {
                "content": "@requirement-decomposer-agent Please triage the questionnaire rows.",
                "mentions": [{"id": "peer-decomposer"}],
            }
        },
        "test-key",
    )
    assert event.event_type == EventType.HANDOFF
    assert event.related_object_ids == ["Q-001"]


def test_record_event_posts_live_event_metadata_and_redacts_response_id() -> None:
    http = FakeBandHTTPClient()
    http.responses.extend(
        [
            {"data": {"id": "chat-raw-id"}},
            {"data": {"id": "event-raw-id", "success": True}},
        ]
    )
    adapter = LiveBandAdapter(config=live_config(), http=http)
    adapter.create_room(run_id="run-live", case_name="Acme Security RFP")

    event = adapter.record_event(
        run_id="run-live",
        sender="compliance-review-agent",
        receiver="trustroom-orchestrator-agent",
        event_type=EventType.REVIEW_DECISION,
        task_state=RunState.REVIEW,
        payload_summary="SLA commitment requires SME approval.",
        related_object_ids=["Q-003"],
    )

    assert http.requests[1] == (
        "/api/v1/agent/chats/chat-raw-id/events",
        {
            "event": {
                "content": "SLA commitment requires SME approval.",
                "message_type": "task",
                "metadata": {
                    "run_id": "run-live",
                    "sender": "compliance-review-agent",
                    "receiver": "trustroom-orchestrator-agent",
                    "trustroom_event_type": "review_decision",
                    "task_state": "review",
                    "related_object_ids": ["Q-003"],
                    "visibility": "judge_view",
                },
            }
        },
        "test-key",
    )
    assert event.band_message_ref.startswith("band-ref:")
    assert "event-raw-id" not in event.band_message_ref
