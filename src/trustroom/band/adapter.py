from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Protocol

from trustroom.models import EventType, ExecutionMode, RunState, TimelineEvent, Visibility


@dataclass(frozen=True)
class BandRoom:
    run_id: str
    room_label: str
    case_name: str
    mode: ExecutionMode
    live_ref: str | None = None


class BandAdapter(Protocol):
    def create_room(self, *, run_id: str, case_name: str) -> BandRoom:
        ...

    def send_message(
        self,
        *,
        run_id: str,
        sender: str,
        receiver: str,
        message: str,
        task_state: RunState,
    ) -> TimelineEvent:
        ...

    def mention_agent(
        self,
        *,
        run_id: str,
        sender: str,
        agent_name: str,
        instruction: str,
        task_state: RunState,
        related_object_ids: list[str] | None = None,
    ) -> TimelineEvent:
        ...

    def record_event(
        self,
        *,
        run_id: str,
        sender: str,
        receiver: str,
        event_type: EventType,
        task_state: RunState,
        payload_summary: str,
        related_object_ids: list[str] | None = None,
        band_message_ref: str | None = None,
        visibility: Visibility = "judge_view",
    ) -> TimelineEvent:
        ...

    def get_room_timeline(self, run_id: str) -> list[TimelineEvent]:
        ...

    def redact_ref(self, raw_ref: str | None) -> str:
        ...


class MockBandAdapter:
    def __init__(self, mode: ExecutionMode = ExecutionMode.MOCK) -> None:
        if mode == ExecutionMode.LIVE:
            raise ValueError("MockBandAdapter cannot run in live mode")
        self.mode = mode
        self._rooms: dict[str, BandRoom] = {}
        self._timelines: dict[str, list[TimelineEvent]] = {}

    def create_room(self, *, run_id: str, case_name: str) -> BandRoom:
        room = BandRoom(
            run_id=run_id,
            room_label=f"mock-band-room-{run_id}",
            case_name=case_name,
            mode=self.mode,
        )
        self._rooms[run_id] = room
        self._timelines.setdefault(run_id, [])
        return room

    def send_message(
        self,
        *,
        run_id: str,
        sender: str,
        receiver: str,
        message: str,
        task_state: RunState,
    ) -> TimelineEvent:
        return self.record_event(
            run_id=run_id,
            sender=sender,
            receiver=receiver,
            event_type=EventType.TASK_ASSIGNED,
            task_state=task_state,
            payload_summary=message,
        )

    def mention_agent(
        self,
        *,
        run_id: str,
        sender: str,
        agent_name: str,
        instruction: str,
        task_state: RunState,
        related_object_ids: list[str] | None = None,
    ) -> TimelineEvent:
        return self.record_event(
            run_id=run_id,
            sender=sender,
            receiver=agent_name,
            event_type=EventType.HANDOFF,
            task_state=task_state,
            payload_summary=instruction,
            related_object_ids=related_object_ids,
        )

    def record_event(
        self,
        *,
        run_id: str,
        sender: str,
        receiver: str,
        event_type: EventType,
        task_state: RunState,
        payload_summary: str,
        related_object_ids: list[str] | None = None,
        band_message_ref: str | None = None,
        visibility: Visibility = "judge_view",
    ) -> TimelineEvent:
        self._require_room(run_id)
        timeline = self._timelines.setdefault(run_id, [])
        event_id = f"EVT-{len(timeline) + 1:04d}"
        raw_ref = band_message_ref or f"{run_id}:{event_id}:{sender}:{receiver}"
        event = TimelineEvent(
            event_id=event_id,
            run_id=run_id,
            sender=sender,
            receiver=receiver,
            event_type=event_type,
            task_state=task_state,
            payload_summary=payload_summary,
            related_object_ids=related_object_ids or [],
            band_message_ref=self.redact_ref(raw_ref),
            visibility=visibility,
        )
        timeline.append(event)
        return event

    def get_room_timeline(self, run_id: str) -> list[TimelineEvent]:
        self._require_room(run_id)
        return list(self._timelines[run_id])

    def redact_ref(self, raw_ref: str | None) -> str:
        if not raw_ref:
            return "band-ref:none"
        digest = hashlib.sha256(raw_ref.encode("utf-8")).hexdigest()[:12]
        return f"band-ref:{digest}"

    def _require_room(self, run_id: str) -> None:
        if run_id not in self._rooms:
            raise KeyError(f"no mock Band room exists for run {run_id!r}")
