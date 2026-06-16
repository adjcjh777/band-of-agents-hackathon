from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol

from trustroom.band.adapter import BandRoom
from trustroom.band.live_adapter import (
    LiveBandAdapter,
    LiveBandConfig,
    LiveBandConfigurationError,
    LiveBandProtocolError,
)
from trustroom.models import RunState, TimelineEvent

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from run_live_band_smoke import (  # noqa: E402
    _event_dict,
    _measure,
    _room_dict,
    build_live_config,
    credential_status as rest_credential_status,
    parse_peer_directory,
    runtime_env,
)


AdapterFactory = Callable[[LiveBandConfig], LiveBandAdapter]
PeerProvider = Callable[[LiveBandConfig], list[Mapping[str, object]]]


class AutonomousReplyAdapter(Protocol):
    config: LiveBandConfig

    def create_room(self, *, run_id: str, case_name: str) -> BandRoom:
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

    def list_messages(self, *, run_id: str) -> list[Mapping[str, object]]:
        ...

    def get_room_timeline(self, run_id: str) -> list[TimelineEvent]:
        ...

    def redact_ref(self, raw_ref: str | None) -> str:
        ...


def _status(state: str, **details: Any) -> dict[str, Any]:
    return {"status": state, **details}


def _message_content(message: Mapping[str, object]) -> str:
    for container_name in ["message", "data"]:
        container = message.get(container_name)
        if isinstance(container, Mapping):
            value = container.get("content") or container.get("text") or container.get("body")
            if isinstance(value, str):
                return value
    value = message.get("content") or message.get("text") or message.get("body")
    return value if isinstance(value, str) else ""


def _message_sender(message: Mapping[str, object]) -> str | None:
    for key in ["sender", "sender_id", "agent_id", "author_id", "participant_id"]:
        value = message.get(key)
        if isinstance(value, str) and value:
            return value
    nested = message.get("sender") or message.get("author")
    if isinstance(nested, Mapping):
        for key in ["id", "name", "handle"]:
            value = nested.get(key)
            if isinstance(value, str) and value:
                return value
    return None


def _message_ref(adapter: AutonomousReplyAdapter, message: Mapping[str, object]) -> str:
    raw_id = message.get("id") or message.get("message_id") or message.get("uuid")
    return adapter.redact_ref(
        str(raw_id) if raw_id else json.dumps(message, default=str, sort_keys=True)
    )


def autonomous_credential_status(
    env: Mapping[str, str],
    *,
    target_agent: str | None,
) -> dict[str, Any]:
    status = rest_credential_status(env, min_peer_agents=1)
    missing = list(status["missing"])
    invalid = list(status["invalid"])
    try:
        peer_directory = parse_peer_directory(env.get("TRUSTROOM_BAND_PEERS_JSON"))
    except Exception as exc:
        peer_directory = {}
        invalid.append(str(exc))
    if target_agent and target_agent not in peer_directory:
        invalid.append(
            f"TRUSTROOM_BAND_AUTONOMOUS_AGENT {target_agent!r} is not present in TRUSTROOM_BAND_PEERS_JSON"
        )
    resolved_target = None
    if peer_directory:
        resolved_target = target_agent or next(iter(peer_directory))
    if not resolved_target:
        missing.append("TRUSTROOM_BAND_PEERS_JSON with at least one autonomous peer agent")
    return {
        "ready": not missing and not invalid,
        "missing": missing,
        "invalid": invalid,
        "target_agent": resolved_target,
        "peer_agent_count": status["peer_agent_count"],
    }


def wait_for_autonomous_reply(
    adapter: AutonomousReplyAdapter,
    *,
    run_id: str,
    target_agent: str,
    token: str,
    timeout_seconds: float,
    poll_interval_seconds: float,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    attempts = 0
    last_message_count = 0
    while True:
        attempts += 1
        messages = adapter.list_messages(run_id=run_id)
        last_message_count = len(messages)
        for message in messages:
            content = _message_content(message)
            if token not in content:
                continue
            if content.startswith(f"@{target_agent}"):
                continue
            return {
                "reply_seen": True,
                "attempts": attempts,
                "message_count": last_message_count,
                "reply_message_ref": _message_ref(adapter, message),
                "reply_sender_ref": adapter.redact_ref(_message_sender(message)),
            }
        if time.monotonic() >= deadline:
            return {
                "reply_seen": False,
                "attempts": attempts,
                "message_count": last_message_count,
                "blocker": (
                    "No autonomous Remote Agent reply containing the challenge token was visible "
                    "before timeout. REST room and @mention may work, but SDK/WebSocket receiving "
                    "and reply behavior is not verified."
                ),
            }
        time.sleep(poll_interval_seconds)


def write_evidence_report(evidence: dict[str, Any], *, reports_dir: Path) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    path = reports_dir / f"live_band_autonomous_smoke.{timestamp}.json"
    path.write_text(json.dumps(evidence, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _attempt_run_id(run_id: str, attempt_index: int) -> str:
    if attempt_index == 1:
        return run_id
    return f"{run_id}-retry-{attempt_index}"


def _run_autonomous_smoke_once(
    *,
    env: Mapping[str, str] | None = None,
    adapter_factory: AdapterFactory | None = None,
    peer_provider: PeerProvider | None = None,
    target_agent: str | None = None,
    timeout_seconds: float = 5.0,
    poll_interval_seconds: float = 1.0,
    run_id: str,
    smoke_attempt_index: int,
    max_smoke_attempts: int,
    case_name: str = "Acme Security RFP autonomous reply smoke",
) -> dict[str, Any]:
    source = dict(env or os.environ)
    generated_at = datetime.now(UTC).isoformat()
    status = autonomous_credential_status(source, target_agent=target_agent)
    if not status["ready"]:
        return {
            "status": "BLOCKED",
            "mode": "live",
            "generated_at": generated_at,
            "run_id": run_id,
            "smoke_attempt_index": smoke_attempt_index,
            "max_smoke_attempts": max_smoke_attempts,
            "rest_smoke": _status("BLOCKED", credential_status=status),
            "band_room_evidence": _status("NOT_RUN"),
            "autonomous_replies": _status("NOT_RUN"),
        }

    try:
        config = build_live_config(source, peer_provider=peer_provider)
        target = target_agent or next(iter(config.agent_directory))
        adapter = adapter_factory(config) if adapter_factory else LiveBandAdapter(config=config)
    except (LiveBandConfigurationError, LiveBandProtocolError) as exc:
        return {
            "status": "BLOCKED",
            "mode": "live",
            "generated_at": generated_at,
            "run_id": run_id,
            "smoke_attempt_index": smoke_attempt_index,
            "max_smoke_attempts": max_smoke_attempts,
            "target_agent": status["target_agent"],
            "rest_smoke": _status("BLOCKED", credential_status=status, blocker=str(exc)),
            "band_room_evidence": _status("NOT_RUN"),
            "autonomous_replies": _status("NOT_RUN"),
        }
    operations: list[dict[str, Any]] = []
    room: BandRoom | None = None
    mention_event: TimelineEvent | None = None

    token = f"TRUSTROOM_AUTONOMOUS_ACK_{run_id}"
    instruction = (
        "Live autonomous smoke: if this Remote Agent received the @mention through "
        f"Band SDK/WebSocket, reply in this Band room with exactly this token: {token}. "
        "Do not include customer or private data."
    )

    try:
        room = _measure(
            operations,
            "create_room",
            lambda: adapter.create_room(run_id=run_id, case_name=case_name),
        )
        operations[-1]["band_ref"] = room.live_ref
        mention_event = _measure(
            operations,
            f"mention_{target}",
            lambda: adapter.mention_agent(
                run_id=run_id,
                sender="trustroom-orchestrator-agent",
                agent_name=target,
                instruction=instruction,
                task_state=RunState.TRIAGE,
                related_object_ids=["Q-001"],
            ),
        )
        operations[-1]["band_ref"] = mention_event.band_message_ref
    except (LiveBandConfigurationError, LiveBandProtocolError) as exc:
        return {
            "status": "BLOCKED",
            "mode": "live",
            "generated_at": generated_at,
            "run_id": run_id,
            "smoke_attempt_index": smoke_attempt_index,
            "max_smoke_attempts": max_smoke_attempts,
            "target_agent": target,
            "rest_smoke": _status("BLOCKED", blocker=str(exc)),
            "band_room_evidence": _status("NOT_RUN"),
            "autonomous_replies": _status("NOT_RUN"),
        }

    rest_status = _status("PASSED", operations=operations)
    room_status = _status(
        "PASSED",
        room=_room_dict(room),
        mention_event=_event_dict(mention_event),
        timeline=[_event_dict(event) for event in adapter.get_room_timeline(run_id)],
    )
    try:
        reply_probe = wait_for_autonomous_reply(
            adapter,
            run_id=run_id,
            target_agent=target,
            token=token,
            timeout_seconds=timeout_seconds,
            poll_interval_seconds=poll_interval_seconds,
        )
    except (LiveBandConfigurationError, LiveBandProtocolError) as exc:
        reply_probe = {
            "reply_seen": False,
            "attempts": 1,
            "message_count": 0,
            "blocker": (
                "Could not inspect Band messages for an autonomous Remote Agent reply: "
                f"{exc}"
            ),
        }
    autonomous_status = _status(
        "PASSED" if reply_probe["reply_seen"] else "BLOCKED",
        target_agent=target,
        expected_token=token,
        timeout_seconds=timeout_seconds,
        poll_interval_seconds=poll_interval_seconds,
        smoke_attempt_index=smoke_attempt_index,
        max_smoke_attempts=max_smoke_attempts,
        retry_strategy="fail_fast_same_agent",
        **reply_probe,
    )
    return {
        "status": "DONE" if reply_probe["reply_seen"] else "BLOCKED",
        "mode": "live",
        "generated_at": generated_at,
        "run_id": run_id,
        "smoke_attempt_index": smoke_attempt_index,
        "max_smoke_attempts": max_smoke_attempts,
        "target_agent": target,
        "rest_smoke": rest_status,
        "band_room_evidence": room_status,
        "autonomous_replies": autonomous_status,
    }


def _should_retry_autonomous_reply(evidence: Mapping[str, Any]) -> bool:
    return (
        evidence.get("status") == "BLOCKED"
        and isinstance(evidence.get("rest_smoke"), Mapping)
        and evidence["rest_smoke"].get("status") == "PASSED"
        and isinstance(evidence.get("band_room_evidence"), Mapping)
        and evidence["band_room_evidence"].get("status") == "PASSED"
        and isinstance(evidence.get("autonomous_replies"), Mapping)
        and evidence["autonomous_replies"].get("status") == "BLOCKED"
    )


def run_autonomous_smoke(
    *,
    env: Mapping[str, str] | None = None,
    adapter_factory: AdapterFactory | None = None,
    peer_provider: PeerProvider | None = None,
    target_agent: str | None = None,
    timeout_seconds: float = 5.0,
    poll_interval_seconds: float = 1.0,
    max_attempts: int = 3,
    write_report: bool = True,
    reports_dir: Path = Path("reports"),
    run_id: str | None = None,
    case_name: str = "Acme Security RFP autonomous reply smoke",
) -> dict[str, Any]:
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")
    base_run_id = run_id or f"live-autonomous-smoke-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}"
    attempt_evidence: list[dict[str, Any]] = []
    final_evidence: dict[str, Any] | None = None

    for attempt_index in range(1, max_attempts + 1):
        final_evidence = _run_autonomous_smoke_once(
            env=env,
            adapter_factory=adapter_factory,
            peer_provider=peer_provider,
            target_agent=target_agent,
            timeout_seconds=timeout_seconds,
            poll_interval_seconds=poll_interval_seconds,
            run_id=_attempt_run_id(base_run_id, attempt_index),
            smoke_attempt_index=attempt_index,
            max_smoke_attempts=max_attempts,
            case_name=case_name,
        )
        attempt_evidence.append(final_evidence)
        if final_evidence["status"] == "DONE" or not _should_retry_autonomous_reply(final_evidence):
            break

    assert final_evidence is not None
    evidence = dict(final_evidence)
    evidence["run_id"] = base_run_id
    evidence["attempts_executed"] = len(attempt_evidence)
    evidence["max_attempts"] = max_attempts
    evidence["retry_policy"] = _status(
        "PASSED"
        if final_evidence["status"] == "DONE"
        else "EXHAUSTED"
        if len(attempt_evidence) == max_attempts and _should_retry_autonomous_reply(final_evidence)
        else "STOPPED",
        strategy="fail_fast_same_agent",
        peer_repair="diagnostic_only_after_retry_exhaustion",
        target_agent=final_evidence.get("target_agent"),
    )
    evidence["attempt_evidence"] = attempt_evidence
    if write_report:
        report_path = write_evidence_report(evidence, reports_dir=reports_dir)
        evidence["report_path"] = str(report_path)
    return evidence


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a redacted live Band autonomous Remote Agent reply smoke test."
    )
    parser.add_argument("--dry-run-check", action="store_true")
    parser.add_argument("--env-file", type=Path, default=Path(".env"))
    parser.add_argument("--reports-dir", type=Path, default=Path("reports"))
    parser.add_argument("--target-agent")
    parser.add_argument("--timeout-seconds", type=float, default=5.0)
    parser.add_argument("--poll-interval-seconds", type=float, default=1.0)
    parser.add_argument("--max-attempts", type=int, default=3)
    parser.add_argument("--no-write", action="store_true")
    return parser


def main(
    argv: list[str] | None = None,
    *,
    env: Mapping[str, str] | None = None,
    adapter_factory: AdapterFactory | None = None,
) -> int:
    args = build_parser().parse_args(argv)
    source = runtime_env(env=env, env_file=args.env_file)
    target_agent = args.target_agent or source.get("TRUSTROOM_BAND_AUTONOMOUS_AGENT")
    if args.dry_run_check:
        status = autonomous_credential_status(source, target_agent=target_agent)
        print(json.dumps(status, indent=2, sort_keys=True))
        return 0 if status["ready"] else 2
    try:
        evidence = run_autonomous_smoke(
            env=source,
            adapter_factory=adapter_factory,
            target_agent=target_agent,
            timeout_seconds=args.timeout_seconds,
            poll_interval_seconds=args.poll_interval_seconds,
            max_attempts=args.max_attempts,
            write_report=not args.no_write,
            reports_dir=args.reports_dir,
        )
    except Exception:
        print(
            json.dumps(
                {
                    "status": "FAILED",
                    "mode": "live",
                    "error": "Band autonomous smoke failed before producing redacted evidence.",
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 1
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0 if evidence["status"] == "DONE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
