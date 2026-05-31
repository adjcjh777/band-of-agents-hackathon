from __future__ import annotations

from trustroom.band.adapter import MockBandAdapter
from trustroom.models import EventType, ExecutionMode, RunState, TimelineEvent


def test_mock_adapter_creates_room_without_live_band_dependency() -> None:
    adapter = MockBandAdapter(mode=ExecutionMode.MOCK)

    room = adapter.create_room(run_id="run-demo", case_name="Acme Security RFP")

    assert room.run_id == "run-demo"
    assert room.mode == ExecutionMode.MOCK
    assert room.room_label == "mock-band-room-run-demo"
    assert room.live_ref is None


def test_record_event_preserves_sender_receiver_event_type_and_task_state() -> None:
    adapter = MockBandAdapter(mode=ExecutionMode.REPLAY)
    adapter.create_room(run_id="run-demo", case_name="Acme Security RFP")

    event = adapter.record_event(
        run_id="run-demo",
        sender="trustroom-orchestrator-agent",
        receiver="evidence-retriever-agent",
        event_type=EventType.HANDOFF,
        task_state=RunState.EVIDENCE,
        payload_summary="Send structured questionnaire rows for evidence retrieval.",
        related_object_ids=["Q-001"],
        band_message_ref="https://app.band.ai/rooms/acme-demo/messages/msg-1234567890",
    )

    assert isinstance(event, TimelineEvent)
    assert event.sender == "trustroom-orchestrator-agent"
    assert event.receiver == "evidence-retriever-agent"
    assert event.event_type == EventType.HANDOFF
    assert event.task_state == RunState.EVIDENCE
    assert event.band_message_ref.startswith("band-ref:")
    assert "msg-1234567890" not in event.band_message_ref


def test_send_message_and_mention_agent_append_ordered_timeline() -> None:
    adapter = MockBandAdapter(mode=ExecutionMode.MOCK)
    adapter.create_room(run_id="run-demo", case_name="Acme Security RFP")

    first = adapter.send_message(
        run_id="run-demo",
        sender="trustroom-orchestrator-agent",
        receiver="requirement-decomposer-agent",
        message="Please triage all questionnaire rows.",
        task_state=RunState.TRIAGE,
    )
    second = adapter.mention_agent(
        run_id="run-demo",
        sender="requirement-decomposer-agent",
        agent_name="evidence-retriever-agent",
        instruction="Retrieve current evidence for high-risk items.",
        task_state=RunState.EVIDENCE,
        related_object_ids=["Q-002", "Q-006"],
    )

    timeline = adapter.get_room_timeline("run-demo")

    assert [event.event_id for event in timeline] == [first.event_id, second.event_id]
    assert timeline[0].event_type == EventType.TASK_ASSIGNED
    assert timeline[1].event_type == EventType.HANDOFF
    assert timeline[1].receiver == "evidence-retriever-agent"


def test_redact_ref_is_stable_and_does_not_expose_raw_reference() -> None:
    adapter = MockBandAdapter()
    raw_ref = "band-live-message-abcd1234567890"

    first = adapter.redact_ref(raw_ref)
    second = adapter.redact_ref(raw_ref)

    assert first == second
    assert first.startswith("band-ref:")
    assert raw_ref not in first
