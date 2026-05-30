from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from check_dual_agent_changes import get_changed_paths, get_current_branch, validate_changed_paths
from check_dual_agent_protocol import (
    DEFAULT_LEDGER,
    DEFAULT_PROTOCOL,
    ActiveLock,
    parse_active_locks,
    validate as validate_protocol,
)


ROOT = Path(__file__).resolve().parents[1]
STRICT_EMPTY_MCP_CONFIG = '{"mcpServers":{}}'
DEFAULT_MAX_BUDGET_USD = "0.15"


@dataclass(frozen=True)
class DispatchContext:
    repo: Path
    ledger: Path
    protocol: Path
    task: str
    lock: ActiveLock
    current_branch: str


def read_prompt(args: argparse.Namespace) -> str:
    if args.prompt_file:
        return Path(args.prompt_file).read_text(encoding="utf-8")
    if args.prompt:
        return args.prompt
    raise ValueError("provide --prompt or --prompt-file")


def matching_lock(active_locks: list[ActiveLock], task: str) -> ActiveLock:
    matches = [lock for lock in active_locks if lock.task == task]
    if not matches:
        raise ValueError(f"no active lock found for task {task!r}")
    if len(matches) > 1:
        raise ValueError(f"multiple active locks found for task {task!r}")
    return matches[0]


def build_context(repo: Path, ledger: Path, protocol: Path, task: str) -> DispatchContext:
    protocol_errors = validate_protocol(ledger, protocol)
    if protocol_errors:
        raise ValueError("protocol check failed: " + "; ".join(protocol_errors))

    active_locks = parse_active_locks(ledger)
    lock = matching_lock(active_locks, task)
    if lock.owner != "Claude Code":
        raise ValueError(f"task {task!r} owner must be Claude Code, got {lock.owner!r}")

    current_branch = get_current_branch(repo)
    preflight_errors = validate_changed_paths(
        get_changed_paths(repo),
        active_locks,
        task=task,
        current_branch=current_branch,
    )
    if preflight_errors:
        raise ValueError("changed-file preflight failed: " + "; ".join(preflight_errors))

    return DispatchContext(
        repo=repo,
        ledger=ledger,
        protocol=protocol,
        task=task,
        lock=lock,
        current_branch=current_branch,
    )


def build_controller_prompt(context: DispatchContext, task_prompt: str) -> str:
    locked_paths = ", ".join(f"`{path}`" for path in context.lock.locked_paths)
    required_checks = context.lock.required_checks
    return f"""你是 Claude Code implementer，通过 Codex controller 派发执行一个受限任务。

必须遵守：
- 仓库：{context.repo}
- 当前任务：{context.task}
- 当前分支：{context.current_branch}
- 只允许修改 locked paths：{locked_paths}
- 必须遵守 AGENTS.md、docs/dual-agent-operating-protocol.md、docs/agent-task-ledger.md。
- 不要读取、修改、提交或引用 pilotdeck/。
- 不要提交 .env、agent_config.yaml、API key、真实 room id、真实 agent key、敏感日志。
- MiMo v2.5 Pro 没有多模态能力；不要承担截图、视觉、Chrome 登录态页面检查。
- 需要改 locked paths 之外的文件时立即停止并返回 NEEDS_CONTEXT。
- 完成后运行 required checks：{required_checks}
- 还必须运行：uv run python scripts/check_dual_agent_protocol.py
- 还必须运行：uv run python scripts/check_dual_agent_changes.py --task "{context.task}"
- 还必须运行：git diff --check

返回格式必须是 JSON 对象，字段：
- status: DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT, BLOCKED
- files_modified: 字符串数组
- commands_run: 字符串数组
- risks: 字符串
- needs_codex_integration: 布尔值

任务说明：
{task_prompt}
"""


def default_allowed_tools(task: str, required_checks: str) -> list[str]:
    tools = [
        "Read",
        "Write",
        "Bash(git status --short --branch)",
        "Bash(uv run python scripts/check_dual_agent_protocol.py)",
        f'Bash(uv run python scripts/check_dual_agent_changes.py --task "{task}")',
        f"Bash(uv run python scripts/check_dual_agent_changes.py --task {task})",
        "Bash(git diff --check)",
    ]
    for command in split_required_checks(required_checks):
        tools.append(f"Bash({command})")
    return dedupe(tools)


def split_required_checks(required_checks: str) -> list[str]:
    checks = []
    for raw in required_checks.split(";"):
        command = raw.strip().strip("`").strip()
        if command:
            checks.append(command)
    return checks


def dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def build_claude_command(
    *,
    claude_bin: str,
    prompt: str,
    max_budget_usd: str,
    tools: str,
    allowed_tools: list[str],
    output_format: str,
) -> list[str]:
    return [
        claude_bin,
        "-p",
        "--no-session-persistence",
        "--strict-mcp-config",
        "--mcp-config",
        STRICT_EMPTY_MCP_CONFIG,
        "--max-budget-usd",
        max_budget_usd,
        "--tools",
        tools,
        "--allowedTools",
        ",".join(allowed_tools),
        "--output-format",
        output_format,
        prompt,
    ]


def run_postflight(context: DispatchContext) -> list[str]:
    active_locks = parse_active_locks(context.ledger)
    return validate_changed_paths(
        get_changed_paths(context.repo),
        active_locks,
        task=context.task,
        current_branch=get_current_branch(context.repo),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Safely dispatch one active ledger task to Claude Code.")
    parser.add_argument("--task", required=True, help="Active ledger task name to dispatch.")
    parser.add_argument("--prompt", help="Task prompt text.")
    parser.add_argument("--prompt-file", help="Path to a task prompt file.")
    parser.add_argument("--repo", type=Path, default=ROOT, help="Repository root.")
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER, help="Path to agent task ledger.")
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL, help="Path to dual-agent protocol.")
    parser.add_argument("--claude-bin", default="claude", help="Claude Code executable.")
    parser.add_argument("--max-budget-usd", default=DEFAULT_MAX_BUDGET_USD, help="Maximum spend for claude -p.")
    parser.add_argument("--tools", default="Read,Write,Bash", help="Claude tool list.")
    parser.add_argument("--allowed-tool", action="append", default=[], help="Additional allowed tool entry.")
    parser.add_argument("--output-format", default="json", choices=["text", "json", "stream-json"])
    parser.add_argument("--dry-run", action="store_true", help="Print command metadata without calling Claude.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        context = build_context(args.repo, args.ledger, args.protocol, args.task)
        task_prompt = read_prompt(args)
        controller_prompt = build_controller_prompt(context, task_prompt)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"Claude task preflight failed: {exc}", file=sys.stderr)
        return 1

    allowed_tools = default_allowed_tools(args.task, context.lock.required_checks) + args.allowed_tool
    command = build_claude_command(
        claude_bin=args.claude_bin,
        prompt=controller_prompt,
        max_budget_usd=args.max_budget_usd,
        tools=args.tools,
        allowed_tools=dedupe(allowed_tools),
        output_format=args.output_format,
    )

    if args.dry_run:
        print(
            json.dumps(
                {
                    "task": args.task,
                    "branch": context.current_branch,
                    "locked_paths": list(context.lock.locked_paths),
                    "claude_command": command[:-1] + ["<prompt>"],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    result = subprocess.run(command, cwd=args.repo, text=True)
    if result.returncode != 0:
        return result.returncode

    postflight_errors = run_postflight(context)
    if postflight_errors:
        print("Claude task postflight failed:", file=sys.stderr)
        for error in postflight_errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
