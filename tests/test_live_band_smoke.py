from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

from trustroom.band.live_adapter import LiveBandAdapter, LiveBandConfig


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "run_live_band_smoke.py"
SPEC = importlib.util.spec_from_file_location("run_live_band_smoke", MODULE_PATH)
assert SPEC is not None
assert SPEC.loader is not None
run_live_band_smoke = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = run_live_band_smoke
SPEC.loader.exec_module(run_live_band_smoke)

main = run_live_band_smoke.main
parse_peer_directory = run_live_band_smoke.parse_peer_directory
resolve_peer_directory = run_live_band_smoke.resolve_peer_directory
run_smoke = run_live_band_smoke.run_smoke


class FakeBandHTTPClient:
    def __init__(self) -> None:
        self.requests: list[tuple[str, dict[str, object], str]] = []
        self.responses: list[dict[str, object]] = [
            {"data": {"id": "chat-raw-id"}},
            {"data": {"id": "participant-decomposer-raw"}},
            {"data": {"id": "message-decomposer-raw"}},
            {"data": {"id": "participant-retriever-raw"}},
            {"data": {"id": "message-retriever-raw"}},
            {"data": {"id": "event-review-raw"}},
        ]

    def post(self, path: str, payload: dict[str, object], *, api_key: str) -> dict[str, object]:
        self.requests.append((path, payload, api_key))
        if not self.responses:
            raise AssertionError(f"no fake response queued for {path}")
        return self.responses.pop(0)


def test_dry_run_missing_credentials_reports_names_without_values(capsys) -> None:
    exit_code = main(
        ["--dry-run-check"],
        env={
            "BAND_API_BASE": "https://platform.dev.band.ai",
            "BAND_AGENT_KEY": "dummy-key",
        },
    )
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "BAND_AGENT_ID" in captured.out
    assert "dummy-key" not in captured.out
    assert "https://platform.dev.band.ai" not in captured.out


def test_parse_peer_directory_requires_json_object() -> None:
    assert parse_peer_directory('{"requirement-decomposer-agent":"peer-raw-id"}') == {
        "requirement-decomposer-agent": "peer-raw-id"
    }
    assert parse_peer_directory("") == {}


def test_resolve_peer_directory_accepts_handles_and_names() -> None:
    config = LiveBandConfig(
        rest_url="https://app.band.ai",
        agent_id="agent-self-raw",
        api_key="dummy-key",
    )

    resolved = resolve_peer_directory(
        config,
        {
            "requirement-decomposer-agent": "@1078524540cjh/requirement-decomposer-agent",
            "evidence-retriever-agent": "evidence-retriever-agent",
        },
        peer_provider=lambda _config: [
            {
                "handle": "1078524540cjh/requirement-decomposer-agent",
                "id": "00000000-0000-4000-8000-000000000001",
                "name": "requirement-decomposer-agent",
            },
            {
                "handle": "1078524540cjh/evidence-retriever-agent",
                "id": "00000000-0000-4000-8000-000000000002",
                "name": "evidence-retriever-agent",
            },
        ],
    )

    assert resolved == {
        "requirement-decomposer-agent": "00000000-0000-4000-8000-000000000001",
        "evidence-retriever-agent": "00000000-0000-4000-8000-000000000002",
    }


def test_fake_live_smoke_writes_only_redacted_evidence() -> None:
    fake_http = FakeBandHTTPClient()

    def adapter_factory(config: LiveBandConfig) -> LiveBandAdapter:
        return LiveBandAdapter(config=config, http=fake_http)

    env = {
        "BAND_API_BASE": "https://platform.dev.band.ai",
        "BAND_AGENT_ID": "agent-self-raw",
        "BAND_AGENT_KEY": "dummy-key",
        "TRUSTROOM_BAND_PEERS_JSON": json.dumps(
            {
                "requirement-decomposer-agent": "@1078524540cjh/requirement-decomposer-agent",
                "evidence-retriever-agent": "evidence-retriever-agent",
            }
        ),
    }

    evidence = run_smoke(
        env=env,
        adapter_factory=adapter_factory,
        min_peer_agents=2,
        write_report=False,
        peer_provider=lambda _config: [
            {
                "handle": "1078524540cjh/requirement-decomposer-agent",
                "id": "00000000-0000-4000-8000-000000000001",
                "name": "requirement-decomposer-agent",
            },
            {
                "handle": "1078524540cjh/evidence-retriever-agent",
                "id": "00000000-0000-4000-8000-000000000002",
                "name": "evidence-retriever-agent",
            },
        ],
    )

    assert evidence["passed"] is True
    assert evidence["mode"] == "live"
    assert evidence["room"]["live_ref"].startswith("band-ref:")
    assert len(evidence["operations"]) >= 4
    assert len(evidence["timeline"]) == 3
    assert all(item["latency_ms"] >= 0 for item in evidence["operations"])
    dumped = json.dumps(evidence)
    for raw_value in [
        "agent-self-raw",
        "dummy-key",
        "chat-raw-id",
        "message-decomposer-raw",
        "message-retriever-raw",
        "event-review-raw",
        "00000000-0000-4000-8000-000000000001",
        "00000000-0000-4000-8000-000000000002",
    ]:
        assert raw_value not in dumped
