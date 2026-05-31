from __future__ import annotations

from pathlib import Path

from trustroom.readiness import scan_no_secrets, scan_text_for_secrets


def test_scan_text_allows_empty_env_example_values() -> None:
    hits = scan_text_for_secrets(
        "BAND_API_BASE=\nBAND_AGENT_ID=\nBAND_AGENT_KEY=\n",
        source="fixture",
    )

    assert hits == []


def test_scan_text_detects_real_looking_band_key() -> None:
    fake_key = "abcdefghijklmnop123456"
    hits = scan_text_for_secrets(
        "BAND_" + "AGENT_KEY=" + fake_key,
        source="fixture",
    )

    assert hits
    assert hits[0].pattern_name == "band_agent_key"


def test_scan_no_secrets_ignores_forbidden_local_files_and_pilotdeck(tmp_path: Path) -> None:
    fake_key = "abcdefghijklmnop123456"
    (tmp_path / ".env").write_text("BAND_" + "AGENT_KEY=" + fake_key + "\n", encoding="utf-8")
    (tmp_path / "pilotdeck").mkdir()
    (tmp_path / "pilotdeck" / "note.md").write_text("sk-" + "abcdefghijklmnopqrstuvwxyz" + "\n", encoding="utf-8")
    (tmp_path / "safe.py").write_text("VALUE = 'demo'\n", encoding="utf-8")

    assert scan_no_secrets(tmp_path) == []
