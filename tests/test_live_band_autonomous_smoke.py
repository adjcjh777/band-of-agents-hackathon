from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

from trustroom.band.live_adapter import LiveBandAdapter, LiveBandConfig


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "run_live_band_autonomous_smoke.py"
SPEC = importlib.util.spec_from_file_location("run_live_band_autonomous_smoke", MODULE_PATH)
assert SPEC is not None
assert SPEC.loader is not None
run_live_band_autonomous_smoke = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = run_live_band_autonomous_smoke
SPEC.loader.exec_module(run_live_band_autonomous_smoke)

main = run_live_band_autonomous_smoke.main
run_autonomous_smoke = run_live_band_autonomous_smoke.run_autonomous_smoke


class FakeBandHTTPClient:
    def __init__(self, *, reply: bool) -> None:
        self.reply = reply
        self.requests: list[tuple[str, dict[str, object], str]] = []
        self.get_requests: list[tuple[str, str]] = []
        self.responses: list[dict[str, object]] = [
            {"data": {"id": "chat-raw-id"}},
            {"data": {"id": "participant-raw-id"}},
            {"data": {"id": "mention-message-raw-id"}},
        ]

    def post(self, path: str, payload: dict[str, object], *, api_key: str) -> dict[str, object]:
        self.requests.append((path, payload, api_key))
        if not self.responses:
            raise AssertionError(f"no fake response queued for {path}")
        return self.responses.pop(0)

    def get(self, path: str, *, api_key: str) -> dict[str, object]:
        self.get_requests.append((path, api_key))
        token = "TRUSTROOM_AUTONOMOUS_ACK_run-autonomous"
        messages: list[dict[str, object]] = [
            {
                "id": "mention-message-raw-id",
                "sender_id": "agent-self-raw",
                "content": f"@requirement-decomposer-agent {token}",
            }
        ]
        if self.reply:
            messages.append(
                {
                    "id": "reply-message-raw-id",
                    "sender_id": "peer-decomposer-raw",
                    "content": token,
                }
            )
        return {"data": messages}


def runtime_env() -> dict[str, str]:
    return {
        "BAND_API_BASE": "https://platform.dev.band.ai",
        "BAND_AGENT_ID": "agent-self-raw",
        "BAND_AGENT_KEY": "dummy-key",
        "TRUSTROOM_BAND_PEERS_JSON": json.dumps(
            {
                "requirement-decomposer-agent": "00000000-0000-4000-8000-000000000001",
            }
        ),
    }


def test_dry_run_missing_credentials_reports_blocked_names_without_values(capsys) -> None:
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


def test_autonomous_smoke_success_separates_rest_room_and_reply_statuses() -> None:
    fake_http = FakeBandHTTPClient(reply=True)

    def adapter_factory(config: LiveBandConfig) -> LiveBandAdapter:
        return LiveBandAdapter(config=config, http=fake_http)

    evidence = run_autonomous_smoke(
        env=runtime_env(),
        adapter_factory=adapter_factory,
        run_id="run-autonomous",
        timeout_seconds=0,
        poll_interval_seconds=0,
        write_report=False,
    )

    assert evidence["status"] == "DONE"
    assert evidence["rest_smoke"]["status"] == "PASSED"
    assert evidence["band_room_evidence"]["status"] == "PASSED"
    assert evidence["autonomous_replies"]["status"] == "PASSED"
    assert evidence["autonomous_replies"]["reply_seen"] is True
    assert evidence["autonomous_replies"]["reply_message_ref"].startswith("band-ref:")
    assert fake_http.get_requests == [
        ("/api/v1/agent/chats/chat-raw-id/messages", "dummy-key"),
    ]
    dumped = json.dumps(evidence)
    for raw_value in [
        "agent-self-raw",
        "dummy-key",
        "chat-raw-id",
        "participant-raw-id",
        "mention-message-raw-id",
        "reply-message-raw-id",
        "peer-decomposer-raw",
        "00000000-0000-4000-8000-000000000001",
    ]:
        assert raw_value not in dumped


def test_autonomous_smoke_blocks_when_reply_never_appears() -> None:
    fake_http = FakeBandHTTPClient(reply=False)

    def adapter_factory(config: LiveBandConfig) -> LiveBandAdapter:
        return LiveBandAdapter(config=config, http=fake_http)

    evidence = run_autonomous_smoke(
        env=runtime_env(),
        adapter_factory=adapter_factory,
        run_id="run-autonomous",
        timeout_seconds=0,
        poll_interval_seconds=0,
        write_report=False,
    )

    assert evidence["status"] == "BLOCKED"
    assert evidence["rest_smoke"]["status"] == "PASSED"
    assert evidence["band_room_evidence"]["status"] == "PASSED"
    assert evidence["autonomous_replies"]["status"] == "BLOCKED"
    assert "SDK/WebSocket" in evidence["autonomous_replies"]["blocker"]


def test_autonomous_smoke_blocks_before_rest_when_target_peer_is_not_configured() -> None:
    evidence = run_autonomous_smoke(
        env=runtime_env(),
        target_agent="evidence-retriever-agent",
        run_id="run-autonomous",
        write_report=False,
    )

    assert evidence["status"] == "BLOCKED"
    assert evidence["rest_smoke"]["status"] == "BLOCKED"
    assert evidence["band_room_evidence"]["status"] == "NOT_RUN"
    assert "TRUSTROOM_BAND_AUTONOMOUS_AGENT" in evidence["rest_smoke"]["credential_status"]["invalid"][0]


def test_autonomous_smoke_blocks_when_peer_handle_cannot_resolve() -> None:
    env = runtime_env()
    env["TRUSTROOM_BAND_PEERS_JSON"] = json.dumps(
        {"requirement-decomposer-agent": "@missing-peer-handle"}
    )

    evidence = run_autonomous_smoke(
        env=env,
        peer_provider=lambda _config: [],
        run_id="run-autonomous",
        write_report=False,
    )

    assert evidence["status"] == "BLOCKED"
    assert evidence["rest_smoke"]["status"] == "BLOCKED"
    assert evidence["band_room_evidence"]["status"] == "NOT_RUN"
    assert "Could not resolve Band peer id" in evidence["rest_smoke"]["blocker"]
    assert "@missing-peer-handle" not in json.dumps(evidence)
