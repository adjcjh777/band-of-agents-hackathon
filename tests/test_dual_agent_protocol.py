from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "check_dual_agent_protocol.py"
SPEC = importlib.util.spec_from_file_location("check_dual_agent_protocol", SCRIPT_PATH)
assert SPEC is not None
check_dual_agent_protocol = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = check_dual_agent_protocol
SPEC.loader.exec_module(check_dual_agent_protocol)


def write_docs(tmp_path: Path, rows: list[str]) -> tuple[Path, Path]:
    docs = tmp_path / "docs"
    docs.mkdir()
    protocol_path = docs / "dual-agent-operating-protocol.md"
    ledger_path = docs / "agent-task-ledger.md"
    protocol_path.write_text("# Protocol\n", encoding="utf-8")
    ledger_path.write_text(
        "\n".join(
            [
                "# Ledger",
                "",
                "## Active File Locks",
                "",
                "| Task | Owner | Branch | Status | Locked paths | Review owner | Required checks |",
                "|---|---|---|---|---|---|---|",
                *rows,
                "",
            ]
        ),
        encoding="utf-8",
    )
    return ledger_path, protocol_path


def test_valid_independent_active_locks_pass(tmp_path: Path) -> None:
    ledger_path, protocol_path = write_docs(
        tmp_path,
        [
            "| T1 | Codex | `feature/codex-t1` | active | `src/trustroom/models.py` | Codex | `uv run pytest tests/test_models.py -v` |",
            "| T3 | Claude Code | `feature/claude-t3` | review | `samples/acme-security-rfp/` | Codex | `uv run pytest tests/test_sample_loader.py -v` |",
        ],
    )

    assert check_dual_agent_protocol.validate(ledger_path, protocol_path) == []


def test_duplicate_active_file_lock_fails(tmp_path: Path) -> None:
    ledger_path, protocol_path = write_docs(
        tmp_path,
        [
            "| T1 | Codex | `feature/codex-t1` | active | `src/trustroom/models.py` | Codex | `uv run pytest tests/test_models.py -v` |",
            "| T2 | Claude Code | `feature/claude-t2` | active | `src/trustroom/models.py` | Codex | `uv run pytest tests/test_models.py -v` |",
        ],
    )

    errors = check_dual_agent_protocol.validate(ledger_path, protocol_path)

    assert any("file lock conflict" in error for error in errors)


def test_parent_directory_lock_conflicts_with_child_path(tmp_path: Path) -> None:
    ledger_path, protocol_path = write_docs(
        tmp_path,
        [
            "| T1 | Codex | `feature/codex-src` | active | `src/trustroom/` | Codex | `uv run pytest` |",
            "| T2 | Claude Code | `feature/claude-models` | active | `src/trustroom/models.py` | Codex | `uv run pytest` |",
        ],
    )

    errors = check_dual_agent_protocol.validate(ledger_path, protocol_path)

    assert any("file lock conflict" in error for error in errors)


def test_forbidden_locked_path_fails(tmp_path: Path) -> None:
    ledger_path, protocol_path = write_docs(
        tmp_path,
        [
            "| T1 | Codex | `feature/codex-pilotdeck` | active | `pilotdeck/README.md` | Codex | `git diff --check` |",
        ],
    )

    errors = check_dual_agent_protocol.validate(ledger_path, protocol_path)

    assert any("forbidden locked path" in error for error in errors)


def test_invalid_owner_branch_and_missing_checks_fail(tmp_path: Path) -> None:
    ledger_path, protocol_path = write_docs(
        tmp_path,
        [
            "| T1 | Unknown | `main` | active | `docs/example.md` | Reviewer | none |",
        ],
    )

    errors = check_dual_agent_protocol.validate(ledger_path, protocol_path)

    assert any("invalid owner" in error for error in errors)
    assert any("invalid review owner" in error for error in errors)
    assert any("branch must start" in error for error in errors)
    assert any("must list required checks" in error for error in errors)
