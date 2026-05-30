from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from check_dual_agent_protocol import ActiveLock, DEFAULT_LEDGER, parse_active_locks


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTROLLER_ALLOWED_PATHS = ("docs/agent-task-ledger.md",)


def normalize_path(path: str) -> str:
    return path.strip().replace("\\", "/").lstrip("./").rstrip("/")


def path_is_within(path: str, allowed: str) -> bool:
    path = normalize_path(path)
    allowed = normalize_path(allowed)
    if not path or not allowed:
        return False
    if path == allowed:
        return True
    return path.startswith(f"{allowed}/")


def parse_porcelain_z(output: bytes) -> list[str]:
    entries = output.decode("utf-8", errors="replace").split("\0")
    changed: list[str] = []
    index = 0

    while index < len(entries):
        entry = entries[index]
        if not entry:
            index += 1
            continue

        status = entry[:2]
        path = entry[3:]
        if path:
            changed.append(normalize_path(path))

        if status[0] in {"R", "C"} or status[1] in {"R", "C"}:
            index += 2
        else:
            index += 1

    return changed


def get_changed_paths(repo: Path = ROOT) -> list[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    return parse_porcelain_z(result.stdout)


def get_current_branch(repo: Path = ROOT) -> str:
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def select_locks(active_locks: list[ActiveLock], task: str | None) -> list[ActiveLock]:
    if task is None:
        return active_locks
    return [lock for lock in active_locks if lock.task == task]


def validate_changed_paths(
    changed_paths: list[str],
    active_locks: list[ActiveLock],
    *,
    task: str | None = None,
    current_branch: str | None = None,
    controller_allowed_paths: tuple[str, ...] = DEFAULT_CONTROLLER_ALLOWED_PATHS,
) -> list[str]:
    errors: list[str] = []
    locks = select_locks(active_locks, task)

    if task is not None and not locks:
        errors.append(f"no active lock found for task {task!r}")

    if current_branch:
        for lock in locks:
            if lock.branch != current_branch:
                errors.append(
                    f"task {lock.task!r} is locked to branch {lock.branch!r}, "
                    f"but current branch is {current_branch!r}"
                )

    locked_paths = tuple(path for lock in locks for path in lock.locked_paths)
    allowed_paths = locked_paths + tuple(controller_allowed_paths)

    if changed_paths and not locked_paths:
        non_controller_paths = [
            path
            for path in changed_paths
            if not any(path_is_within(path, allowed) for allowed in controller_allowed_paths)
        ]
        if non_controller_paths:
            errors.append(
                "changed files exist but no active locked paths are available: "
                + ", ".join(sorted(non_controller_paths))
            )

    for changed_path in changed_paths:
        if any(path_is_within(changed_path, allowed) for allowed in allowed_paths):
            continue
        errors.append(
            f"changed path {changed_path!r} is outside active locked paths: "
            + ", ".join(locked_paths)
        )

    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify current changed files are covered by active dual-agent ledger locks."
    )
    parser.add_argument("--task", help="Require changes to match one specific active task.")
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER, help="Path to agent task ledger.")
    parser.add_argument("--repo", type=Path, default=ROOT, help="Repository root to inspect.")
    parser.add_argument(
        "--allow-controller-change",
        action="append",
        default=list(DEFAULT_CONTROLLER_ALLOWED_PATHS),
        help="Controller-owned path allowed outside the task lock. Repeatable.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    active_locks = parse_active_locks(args.ledger)
    changed_paths = get_changed_paths(args.repo)
    current_branch = get_current_branch(args.repo)

    errors = validate_changed_paths(
        changed_paths,
        active_locks,
        task=args.task,
        current_branch=current_branch,
        controller_allowed_paths=tuple(args.allow_controller_change),
    )

    if errors:
        print("Dual-agent changed-file check failed:")
        for error in errors:
            print(f"- {error}")
        if changed_paths:
            print("Changed paths:")
            for path in changed_paths:
                print(f"- {path}")
        return 1

    print(
        "Dual-agent changed-file check OK: "
        f"{len(changed_paths)} changed path(s), {len(active_locks)} active lock(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
