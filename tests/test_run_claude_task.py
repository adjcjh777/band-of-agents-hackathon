from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_SCRIPT = ROOT / "scripts" / "check_dual_agent_protocol.py"
CHANGES_SCRIPT = ROOT / "scripts" / "check_dual_agent_changes.py"
RUNNER_SCRIPT = ROOT / "scripts" / "run_claude_task.py"


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
run_claude_task = load_script("run_claude_task", RUNNER_SCRIPT)


def write_repo(tmp_path: Path, *, task_owner: str = "Claude Code") -> tuple[Path, Path, Path]:
    repo = tmp_path / "repo"
    docs = repo / "docs"
    scripts = repo / "scripts"
    docs.mkdir(parents=True)
    scripts.mkdir(parents=True)
    shutil.copy(PROTOCOL_SCRIPT, scripts / "check_dual_agent_protocol.py")
    shutil.copy(CHANGES_SCRIPT, scripts / "check_dual_agent_changes.py")
    protocol = docs / "dual-agent-operating-protocol.md"
    ledger = docs / "agent-task-ledger.md"
    protocol.write_text("# Protocol\n", encoding="utf-8")
    ledger.write_text(
        "\n".join(
            [
                "# Ledger",
                "",
                "## Active File Locks",
                "",
                "| Task | Owner | Branch | Status | Locked paths | Review owner | Required checks |",
                "|---|---|---|---|---|---|---|",
                f"| Smoke | {task_owner} | `feature/claude-smoke` | active | `docs/smoke.md` | Codex | `git diff --check` |",
                "",
            ]
        ),
        encoding="utf-8",
    )
    subprocess.run(["git", "init", "-b", "feature/claude-smoke"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo, check=True)
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "baseline"], cwd=repo, check=True, capture_output=True)
    return repo, ledger, protocol


def write_fake_claude(path: Path, *, target_file: str = "docs/smoke.md") -> Path:
    fake = path / "fake_claude.py"
    fake.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "from pathlib import Path",
                "import json",
                "import sys",
                f"Path({target_file!r}).write_text('# Smoke\\n', encoding='utf-8')",
                "print(json.dumps({'status': 'DONE', 'files_modified': ['docs/smoke.md']}))",
                "sys.exit(0)",
                "",
            ]
        ),
        encoding="utf-8",
    )
    fake.chmod(0o755)
    return fake


def test_build_claude_command_uses_strict_empty_mcp() -> None:
    command = run_claude_task.build_claude_command(
        claude_bin="claude",
        prompt="hello",
        max_budget_usd="0.15",
        tools="Read",
        allowed_tools=["Read"],
        output_format="json",
    )

    assert "--strict-mcp-config" in command
    assert command[command.index("--mcp-config") + 1] == '{"mcpServers":{}}'
    assert command[-1] == "hello"


def test_dry_run_prints_locked_paths_and_command(tmp_path: Path, capsys) -> None:
    repo, ledger, protocol = write_repo(tmp_path)

    exit_code = run_claude_task.main(
        [
            "--repo",
            str(repo),
            "--ledger",
            str(ledger),
            "--protocol",
            str(protocol),
            "--task",
            "Smoke",
            "--prompt",
            "create smoke file",
            "--dry-run",
        ]
    )

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["locked_paths"] == ["docs/smoke.md"]
    assert payload["claude_command"][-1] == "<prompt>"


def test_preflight_rejects_non_claude_owner(tmp_path: Path, capsys) -> None:
    repo, ledger, protocol = write_repo(tmp_path, task_owner="Codex")

    exit_code = run_claude_task.main(
        [
            "--repo",
            str(repo),
            "--ledger",
            str(ledger),
            "--protocol",
            str(protocol),
            "--task",
            "Smoke",
            "--prompt",
            "create smoke file",
            "--dry-run",
        ]
    )

    assert exit_code == 1
    assert "owner must be Claude Code" in capsys.readouterr().err


def test_fake_claude_write_inside_lock_passes_postflight(tmp_path: Path) -> None:
    repo, ledger, protocol = write_repo(tmp_path)
    fake_claude = write_fake_claude(tmp_path)

    exit_code = run_claude_task.main(
        [
            "--repo",
            str(repo),
            "--ledger",
            str(ledger),
            "--protocol",
            str(protocol),
            "--task",
            "Smoke",
            "--prompt",
            "create smoke file",
            "--claude-bin",
            str(fake_claude),
            "--output-format",
            "json",
            "--max-budget-usd",
            "0.01",
            "--tools",
            "Read,Write,Bash",
        ]
    )

    assert exit_code == 0
    assert (repo / "docs" / "smoke.md").exists()


def test_postflight_rejects_fake_claude_write_outside_lock(tmp_path: Path) -> None:
    repo, ledger, protocol = write_repo(tmp_path)
    context = run_claude_task.build_context(repo, ledger, protocol, "Smoke")
    fake_claude = write_fake_claude(tmp_path, target_file="docs/outside.md")
    subprocess.run([sys.executable, str(fake_claude)], cwd=repo, check=True)

    errors = run_claude_task.run_postflight(context)
    assert any("outside active locked paths" in error for error in errors)


def test_main_fails_when_fake_claude_writes_outside_lock(tmp_path: Path, capsys) -> None:
    repo, ledger, protocol = write_repo(tmp_path)
    fake_claude = write_fake_claude(tmp_path, target_file="docs/outside.md")

    exit_code = run_claude_task.main(
        [
            "--repo",
            str(repo),
            "--ledger",
            str(ledger),
            "--protocol",
            str(protocol),
            "--task",
            "Smoke",
            "--prompt",
            "create smoke file outside lock",
            "--claude-bin",
            str(fake_claude),
        ]
    )

    assert exit_code == 1
    assert "Claude task postflight failed" in capsys.readouterr().err
