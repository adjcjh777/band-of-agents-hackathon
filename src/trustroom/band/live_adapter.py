from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Mapping, Protocol

from trustroom.band.adapter import BandRoom, MockBandAdapter
from trustroom.models import EventType, ExecutionMode, RunState, TimelineEvent, Visibility


class LiveBandConfigurationError(ValueError):
    pass


class LiveBandProtocolError(RuntimeError):
    pass


class BandHTTPClient(Protocol):
    def get(self, path: str, *, api_key: str) -> Mapping[str, object]:
        ...

    def post(self, path: str, payload: dict[str, object], *, api_key: str) -> Mapping[str, object]:
        ...


@dataclass(frozen=True)
class LiveBandConfig:
    rest_url: str
    agent_id: str
    api_key: str
    agent_directory: Mapping[str, str] = field(default_factory=dict)

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> LiveBandConfig:
        source = env or os.environ
        rest_url = source.get("BAND_REST_URL") or source.get("BAND_API_BASE")
        agent_id = source.get("BAND_AGENT_ID")
        api_key = source.get("BAND_AGENT_KEY")
        missing = [
            name
            for name, value in (
                ("BAND_REST_URL or BAND_API_BASE", rest_url),
                ("BAND_AGENT_ID", agent_id),
                ("BAND_AGENT_KEY", api_key),
            )
            if not value
        ]
        if missing:
            raise LiveBandConfigurationError(
                "Missing required Band live config: " + ", ".join(missing)
            )
        return cls(rest_url=rest_url.rstrip("/"), agent_id=agent_id, api_key=api_key)


class UrllibBandHTTPClient:
    def __init__(self, rest_url: str, *, timeout_seconds: float = 10.0) -> None:
        self.rest_url = rest_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def get(self, path: str, *, api_key: str) -> Mapping[str, object]:
        return self._request(path, api_key=api_key, method="GET")

    def post(self, path: str, payload: dict[str, object], *, api_key: str) -> Mapping[str, object]:
        body = json.dumps(payload).encode("utf-8")
        return self._request(path, api_key=api_key, method="POST", body=body)

    def _request(
        self,
        path: str,
        *,
        api_key: str,
        method: str,
        body: bytes | None = None,
    ) -> Mapping[str, object]:
        request = urllib.request.Request(
            f"{self.rest_url}{path}",
            data=body,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "RFP-TrustRoom-Hackathon/1.0",
                "X-API-Key": api_key,
            },
            method=method,
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.URLError as exc:
            raise LiveBandProtocolError("Band live request failed") from exc
        try:
            parsed = json.loads(raw) if raw else {}
        except json.JSONDecodeError as exc:
            raise LiveBandProtocolError("Band live response was not valid JSON") from exc
        if not isinstance(parsed, Mapping):
            raise LiveBandProtocolError("Band live response was not a JSON object")
        return parsed


class LiveBandAdapter(MockBandAdapter):
    def __init__(
        self,
        *,
        config: LiveBandConfig,
        http: BandHTTPClient | None = None,
    ) -> None:
        super().__init__(mode=ExecutionMode.MOCK)
        self.mode = ExecutionMode.LIVE
        self.config = config
        self.http = http or UrllibBandHTTPClient(config.rest_url)
        self._chat_ids_by_run: dict[str, str] = {}
        self._participant_ids_added: set[tuple[str, str]] = set()

    def create_room(self, *, run_id: str, case_name: str) -> BandRoom:
        response = self.http.post(
            "/api/v1/agent/chats",
            {"chat": {}},
            api_key=self.config.api_key,
        )
        chat_id = self._extract_response_id(response, "create chat room")
        self._chat_ids_by_run[run_id] = chat_id
        room = BandRoom(
            run_id=run_id,
            room_label=f"live-band-chat-{self.redact_ref(chat_id).removeprefix('band-ref:')}",
            case_name=case_name,
            mode=ExecutionMode.LIVE,
            live_ref=self.redact_ref(chat_id),
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
        chat_id = self._require_live_chat(run_id)
        response = self.http.post(
            f"/api/v1/agent/chats/{chat_id}/messages",
            {"message": {"content": message, "mentions": []}},
            api_key=self.config.api_key,
        )
        message_id = self._extract_response_id(response, "send message")
        return self._append_event(
            run_id=run_id,
            sender=sender,
            receiver=receiver,
            event_type=EventType.TASK_ASSIGNED,
            task_state=task_state,
            payload_summary=message,
            band_message_ref=f"{chat_id}:{message_id}",
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
        chat_id = self._require_live_chat(run_id)
        participant_id = self.config.agent_directory.get(agent_name)
        if not participant_id:
            raise LiveBandConfigurationError(
                f"Missing Band participant id for agent {agent_name!r}; configure agent_directory."
            )
        self._ensure_participant(chat_id=chat_id, participant_id=participant_id)
        content = f"@{agent_name} {instruction}"
        response = self.http.post(
            f"/api/v1/agent/chats/{chat_id}/messages",
            {
                "message": {
                    "content": content,
                    "mentions": [{"id": participant_id}],
                }
            },
            api_key=self.config.api_key,
        )
        message_id = self._extract_response_id(response, "send mention")
        return self._append_event(
            run_id=run_id,
            sender=sender,
            receiver=agent_name,
            event_type=EventType.HANDOFF,
            task_state=task_state,
            payload_summary=instruction,
            related_object_ids=related_object_ids,
            band_message_ref=f"{chat_id}:{message_id}",
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
        chat_id = self._require_live_chat(run_id)
        response = self.http.post(
            f"/api/v1/agent/chats/{chat_id}/events",
            {
                "event": {
                    "content": payload_summary,
                    "message_type": "task",
                    "metadata": {
                        "run_id": run_id,
                        "sender": sender,
                        "receiver": receiver,
                        "trustroom_event_type": event_type.value,
                        "task_state": task_state.value,
                        "related_object_ids": related_object_ids or [],
                        "visibility": visibility,
                    },
                }
            },
            api_key=self.config.api_key,
        )
        event_id = self._extract_response_id(response, "record event")
        return self._append_event(
            run_id=run_id,
            sender=sender,
            receiver=receiver,
            event_type=event_type,
            task_state=task_state,
            payload_summary=payload_summary,
            related_object_ids=related_object_ids,
            band_message_ref=band_message_ref or f"{chat_id}:{event_id}",
            visibility=visibility,
        )

    def _ensure_participant(self, *, chat_id: str, participant_id: str) -> None:
        key = (chat_id, participant_id)
        if key in self._participant_ids_added:
            return
        self.http.post(
            f"/api/v1/agent/chats/{chat_id}/participants",
            {"participant": {"participant_id": participant_id}},
            api_key=self.config.api_key,
        )
        self._participant_ids_added.add(key)

    def _require_live_chat(self, run_id: str) -> str:
        self._require_room(run_id)
        try:
            return self._chat_ids_by_run[run_id]
        except KeyError as exc:
            raise LiveBandProtocolError(f"no live Band chat id exists for run {run_id!r}") from exc

    def _append_event(
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
        return super().record_event(
            run_id=run_id,
            sender=sender,
            receiver=receiver,
            event_type=event_type,
            task_state=task_state,
            payload_summary=payload_summary,
            related_object_ids=related_object_ids,
            band_message_ref=band_message_ref,
            visibility=visibility,
        )

    @staticmethod
    def _extract_response_id(response: Mapping[str, object], action: str) -> str:
        data = response.get("data")
        if not isinstance(data, Mapping):
            raise LiveBandProtocolError(f"Band response for {action} did not include data.")
        raw_id = data.get("id")
        if not isinstance(raw_id, str) or not raw_id:
            raise LiveBandProtocolError(f"Band response for {action} did not include data.id.")
        return raw_id
