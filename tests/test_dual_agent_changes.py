from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_SCRIPT = ROOT / "scripts" / "check_dual_agent_protocol.py"
CHANGES_SCRIPT = ROOT / "scripts" / "check_dual_agent_changes.py"


def load_script(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


check_dual_agent_protocol = load_script("check_dual_agent_protocol", PROTOCOL_SCRIPT)
check_dual_agent_changes = load_script("check_dual_agent_changes", CHANGES_SCRIPT)


def lock(
    *,
    task: str = "T3",
    branch: str = "feature/claude-t3",
    locked_paths: tuple[str, ...] = ("samples/acme-security-rfp/",),
):
    return check_dual_agent_protocol.ActiveLock(
        line=20,
        task=task,
        owner="Claude Code",
        branch=branch,
        status="active",
        locked_paths=locked_paths,
        review_owner="Codex",
        required_checks="uv run python scripts/check_dual_agent_protocol.py",
    )


def test_changed_file_inside_locked_directory_passes() -> None:
    errors = check_dual_agent_changes.validate_changed_paths(
        ["samples/acme-security-rfp/case.json"],
        [lock()],
        task="T3",
        current_branch="feature/claude-t3",
    )

    assert errors == []


def test_untracked_file_outside_locked_directory_fails() -> None:
    errors = check_dual_agent_changes.validate_changed_paths(
        ["samples/acme-security-rfp/case.json", "docs/untracked-note.md"],
        [lock()],
        task="T3",
        current_branch="feature/claude-t3",
    )

    assert any("outside active locked paths" in error for error in errors)


def test_no_active_lock_fails_for_non_controller_change() -> None:
    errors = check_dual_agent_changes.validate_changed_paths(
        ["src/trustroom/models.py"],
        [],
        current_branch="feature/codex-t1",
    )

    assert any("no active locked paths" in error for error in errors)


def test_controller_ledger_change_is_allowed_by_default() -> None:
    errors = check_dual_agent_changes.validate_changed_paths(
        ["docs/agent-task-ledger.md"],
        [],
        current_branch="feature/codex-ledger",
    )

    assert errors == []


def test_branch_mismatch_fails_even_when_file_is_locked() -> None:
    errors = check_dual_agent_changes.validate_changed_paths(
        ["samples/acme-security-rfp/case.json"],
        [lock(branch="feature/claude-t3")],
        task="T3",
        current_branch="feature/other",
    )

    assert any("locked to branch" in error for error in errors)


def test_porcelain_parser_includes_untracked_and_renamed_paths() -> None:
    raw = b"?? docs/new.md\0 M src/trustroom/models.py\0R  docs/new-name.md\0docs/old-name.md\0"

    changed = check_dual_agent_changes.parse_porcelain_z(raw)

    assert changed == ["docs/new.md", "src/trustroom/models.py", "docs/new-name.md"]


def test_cli_checks_untracked_files_against_active_lock(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    docs = repo / "docs"
    docs.mkdir(parents=True)
    (docs / "dual-agent-operating-protocol.md").write_text("# Protocol\n", encoding="utf-8")
    (docs / "agent-task-ledger.md").write_text(
        "\n".join(
            [
                "# Ledger",
                "",
                "## Active File Locks",
                "",
                "| Task | Owner | Branch | Status | Locked paths | Review owner | Required checks |",
                "|---|---|---|---|---|---|---|",
                "| T3 | Claude Code | `feature/claude-t3` | active | `docs/allowed.md` | Codex | `git diff --check` |",
                "",
            ]
        ),
        encoding="utf-8",
    )

    subprocess.run(["git", "init", "-b", "feature/claude-t3"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo, check=True)
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "baseline"], cwd=repo, check=True, capture_output=True)

    (docs / "allowed.md").write_text("# Allowed\n", encoding="utf-8")
    pass_result = subprocess.run(
        [
            sys.executable,
            str(CHANGES_SCRIPT),
            "--repo",
            str(repo),
            "--ledger",
            str(docs / "agent-task-ledger.md"),
            "--task",
            "T3",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert pass_result.returncode == 0
    assert "1 changed path" in pass_result.stdout

    (docs / "outside.md").write_text("# Outside\n", encoding="utf-8")
    fail_result = subprocess.run(
        [
            sys.executable,
            str(CHANGES_SCRIPT),
            "--repo",
            str(repo),
            "--ledger",
            str(docs / "agent-task-ledger.md"),
            "--task",
            "T3",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert fail_result.returncode == 1
    assert "docs/outside.md" in fail_result.stdout
