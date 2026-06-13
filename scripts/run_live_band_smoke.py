from __future__ import annotations

import argparse
import json
import os
import re
import time
from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from trustroom.band.adapter import BandAdapter, BandRoom
from trustroom.band.live_adapter import (
    LiveBandAdapter,
    LiveBandConfig,
    LiveBandConfigurationError,
    UrllibBandHTTPClient,
)
from trustroom.models import EventType, RunState, TimelineEvent


AdapterFactory = Callable[[LiveBandConfig], BandAdapter]
PeerProvider = Callable[[LiveBandConfig], list[Mapping[str, object]]]
UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)


def parse_peer_directory(raw_value: str | None) -> dict[str, str]:
    if not raw_value:
        return {}
    try:
        parsed = json.loads(raw_value)
    except json.JSONDecodeError as exc:
        raise ValueError("TRUSTROOM_BAND_PEERS_JSON must be valid JSON") from exc
    if not isinstance(parsed, dict):
        raise ValueError("TRUSTROOM_BAND_PEERS_JSON must be a JSON object")
    directory: dict[str, str] = {}
    for key, value in parsed.items():
        if not isinstance(key, str) or not isinstance(value, str) or not key or not value:
            raise ValueError("TRUSTROOM_BAND_PEERS_JSON must map agent names to ids")
        directory[key] = value
    return directory


def _dotenv_values(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip("\"'")
        if key:
            values[key] = value
    return values


def runtime_env(
    *,
    env: Mapping[str, str] | None,
    env_file: Path | None,
) -> dict[str, str]:
    values = dict(os.environ if env is None else env)
    if env is None and env_file is not None:
        for key, value in _dotenv_values(env_file).items():
            values.setdefault(key, value)
    return values


def credential_status(env: Mapping[str, str], *, min_peer_agents: int) -> dict[str, Any]:
    missing: list[str] = []
    invalid: list[str] = []
    if not (env.get("BAND_REST_URL") or env.get("BAND_API_BASE")):
        missing.append("BAND_REST_URL or BAND_API_BASE")
    for name in ["BAND_AGENT_ID", "BAND_AGENT_KEY"]:
        if not env.get(name):
            missing.append(name)
    try:
        peers = parse_peer_directory(env.get("TRUSTROOM_BAND_PEERS_JSON"))
    except ValueError as exc:
        peers = {}
        invalid.append(str(exc))
    if len(peers) < min_peer_agents:
        missing.append(
            f"TRUSTROOM_BAND_PEERS_JSON with at least {min_peer_agents} peer agent ids"
        )
    return {
        "ready": not missing and not invalid,
        "missing": missing,
        "invalid": invalid,
        "peer_agent_count": len(peers),
        "required_peer_agents": min_peer_agents,
    }

def _is_uuid(value: str) -> bool:
    return bool(UUID_RE.match(value))


def fetch_available_peers(config: LiveBandConfig) -> list[Mapping[str, object]]:
    response = UrllibBandHTTPClient(config.rest_url).get(
        "/api/v1/agent/peers",
        api_key=config.api_key,
    )
    data = response.get("data")
    if not isinstance(data, list):
        raise LiveBandConfigurationError("Band peer lookup did not return a data list.")
    peers: list[Mapping[str, object]] = []
    for item in data:
        if isinstance(item, Mapping):
            peers.append(item)
    return peers


def resolve_peer_directory(
    config: LiveBandConfig,
    peer_directory: Mapping[str, str],
    *,
    peer_provider: PeerProvider | None = None,
) -> dict[str, str]:
    if all(_is_uuid(value) for value in peer_directory.values()):
        return dict(peer_directory)
    peers = peer_provider(config) if peer_provider else fetch_available_peers(config)
    peer_index: dict[str, str] = {}
    for peer in peers:
        raw_id = peer.get("id")
        if not isinstance(raw_id, str) or not _is_uuid(raw_id):
            continue
        for field in ["handle", "name"]:
            raw_value = peer.get(field)
            if isinstance(raw_value, str) and raw_value:
                peer_index[raw_value] = raw_id
                peer_index[raw_value.removeprefix("@")] = raw_id
                peer_index[f"@{raw_value.removeprefix('@')}"] = raw_id

    resolved: dict[str, str] = {}
    for agent_name, configured_value in peer_directory.items():
        if _is_uuid(configured_value):
            resolved[agent_name] = configured_value
            continue
        candidates = [
            configured_value,
            configured_value.removeprefix("@"),
            f"@{configured_value.removeprefix('@')}",
            agent_name,
        ]
        resolved_id = next(
            (peer_index[candidate] for candidate in candidates if candidate in peer_index),
            None,
        )
        if not resolved_id:
            raise LiveBandConfigurationError(
                f"Could not resolve Band peer id for configured agent {agent_name!r}."
            )
        resolved[agent_name] = resolved_id
    return resolved


def build_live_config(
    env: Mapping[str, str],
    *,
    peer_provider: PeerProvider | None = None,
) -> LiveBandConfig:
    base_config = LiveBandConfig.from_env(env)
    peers = resolve_peer_directory(
        base_config,
        parse_peer_directory(env.get("TRUSTROOM_BAND_PEERS_JSON")),
        peer_provider=peer_provider,
    )
    return LiveBandConfig(
        rest_url=base_config.rest_url,
        agent_id=base_config.agent_id,
        api_key=base_config.api_key,
        agent_directory=peers,
    )


def _measure(
    operations: list[dict[str, Any]],
    name: str,
    fn: Callable[[], Any],
) -> Any:
    started = time.perf_counter()
    result = fn()
    operations.append(
        {
            "name": name,
            "latency_ms": round((time.perf_counter() - started) * 1000, 3),
        }
    )
    return result


def _room_dict(room: BandRoom) -> dict[str, Any]:
    return {
        "run_id": room.run_id,
        "case_name": room.case_name,
        "mode": room.mode.value,
        "room_label": room.room_label,
        "live_ref": room.live_ref,
    }


def _event_dict(event: TimelineEvent) -> dict[str, Any]:
    return event.model_dump(mode="json")


def write_evidence_report(evidence: dict[str, Any], *, reports_dir: Path) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    path = reports_dir / f"live_band_smoke.{timestamp}.json"
    path.write_text(json.dumps(evidence, indent=2, sort_keys=True), encoding="utf-8")
    return path


def run_smoke(
    *,
    env: Mapping[str, str] | None = None,
    adapter_factory: AdapterFactory | None = None,
    min_peer_agents: int = 2,
    write_report: bool = True,
    reports_dir: Path = Path("reports"),
    run_id: str | None = None,
    case_name: str = "Acme Security RFP live smoke",
    peer_provider: PeerProvider | None = None,
) -> dict[str, Any]:
    source = dict(env or os.environ)
    status = credential_status(source, min_peer_agents=min_peer_agents)
    if not status["ready"]:
        raise LiveBandConfigurationError(
            "Band live smoke is not ready: " + ", ".join(status["missing"] + status["invalid"])
        )

    config = build_live_config(source, peer_provider=peer_provider)
    adapter = adapter_factory(config) if adapter_factory else LiveBandAdapter(config=config)
    smoke_run_id = run_id or f"live-smoke-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}"
    peer_agents = list(config.agent_directory)[:min_peer_agents]
    operations: list[dict[str, Any]] = []

    room = _measure(
        operations,
        "create_room",
        lambda: adapter.create_room(run_id=smoke_run_id, case_name=case_name),
    )
    operations[-1]["band_ref"] = room.live_ref

    for agent_name in peer_agents:
        event = _measure(
            operations,
            f"mention_{agent_name}",
            lambda agent_name=agent_name: adapter.mention_agent(
                run_id=smoke_run_id,
                sender="trustroom-orchestrator-agent",
                agent_name=agent_name,
                instruction=(
                    "Live smoke: confirm receipt of the TrustRoom handoff and keep "
                    "all customer data fictional."
                ),
                task_state=RunState.TRIAGE,
                related_object_ids=["Q-001"],
            ),
        )
        operations[-1]["band_ref"] = event.band_message_ref

    review_event = _measure(
        operations,
        "record_review_event",
        lambda: adapter.record_event(
            run_id=smoke_run_id,
            sender="compliance-reviewer-agent",
            receiver="trustroom-orchestrator-agent",
            event_type=EventType.REVIEW_DECISION,
            task_state=RunState.REVIEW,
            payload_summary="Live smoke recorded reviewer checkpoint for redacted evidence.",
            related_object_ids=["Q-003"],
        ),
    )
    operations[-1]["band_ref"] = review_event.band_message_ref

    evidence = {
        "passed": True,
        "mode": "live",
        "generated_at": datetime.now(UTC).isoformat(),
        "run_id": smoke_run_id,
        "case_name": case_name,
        "agent_count": 1 + len(peer_agents),
        "peer_agents": peer_agents,
        "required_peer_agents": min_peer_agents,
        "room": _room_dict(room),
        "operations": operations,
        "timeline": [_event_dict(event) for event in adapter.get_room_timeline(smoke_run_id)],
    }
    if write_report:
        report_path = write_evidence_report(evidence, reports_dir=reports_dir)
        evidence["report_path"] = str(report_path)
    return evidence


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a redacted live Band smoke test.")
    parser.add_argument("--dry-run-check", action="store_true")
    parser.add_argument("--env-file", type=Path, default=Path(".env"))
    parser.add_argument("--reports-dir", type=Path, default=Path("reports"))
    parser.add_argument("--min-peer-agents", type=int, default=2)
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
    if args.dry_run_check:
        status = credential_status(source, min_peer_agents=args.min_peer_agents)
        print(json.dumps(status, indent=2, sort_keys=True))
        return 0 if status["ready"] else 2
    try:
        evidence = run_smoke(
            env=source,
            adapter_factory=adapter_factory,
            min_peer_agents=args.min_peer_agents,
            write_report=not args.no_write,
            reports_dir=args.reports_dir,
        )
    except (LiveBandConfigurationError, ValueError) as exc:
        print(
            json.dumps(
                {
                    "passed": False,
                    "mode": "live",
                    "error_type": exc.__class__.__name__,
                    "error": str(exc),
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 2
    except Exception as exc:
        print(
            json.dumps(
                {
                    "passed": False,
                    "mode": "live",
                    "error_type": exc.__class__.__name__,
                    "error": "Band live smoke request failed before producing evidence.",
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 1
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
