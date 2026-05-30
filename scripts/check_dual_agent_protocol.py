from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = ROOT / "docs" / "agent-task-ledger.md"
DEFAULT_PROTOCOL = ROOT / "docs" / "dual-agent-operating-protocol.md"

ACTIVE_STATUSES = {"active", "review", "ready-to-merge"}
ALLOWED_OWNERS = {"Codex", "Claude Code"}
ALLOWED_BRANCH_PREFIXES = ("feature/", "bugfix/", "ablation/")
FORBIDDEN_LOCK_PARTS = ("pilotdeck/", ".env", "agent_config.yaml")


@dataclass(frozen=True)
class ActiveLock:
    line: int
    task: str
    owner: str
    branch: str
    status: str
    locked_paths: tuple[str, ...]
    review_owner: str
    required_checks: str


def clean_cell(value: str) -> str:
    value = value.strip()
    value = re.sub(r"`([^`]*)`", r"\1", value)
    value = value.replace("&nbsp;", " ")
    return value.strip()


def split_markdown_row(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return []
    return [cell.strip() for cell in stripped.strip("|").split("|")]


def is_separator_row(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def split_locked_paths(value: str) -> tuple[str, ...]:
    cleaned = clean_cell(value)
    cleaned = re.sub(r"<br\s*/?>", ",", cleaned)
    paths = []
    for part in cleaned.split(","):
        path = part.strip()
        if path and path.lower() not in {"none", "n/a", "-"}:
            paths.append(path)
    return tuple(paths)


def parse_active_locks(ledger_path: Path = DEFAULT_LEDGER) -> list[ActiveLock]:
    lines = ledger_path.read_text(encoding="utf-8").splitlines()
    header: list[str] | None = None
    rows: list[ActiveLock] = []

    for line_number, line in enumerate(lines, start=1):
        cells = split_markdown_row(line)
        if not cells:
            if header is not None:
                break
            continue

        if {"Task", "Owner", "Branch", "Status", "Locked paths", "Review owner", "Required checks"}.issubset(cells):
            header = cells
            continue

        if header is None or is_separator_row(cells):
            continue

        if len(cells) != len(header):
            continue

        row = dict(zip(header, cells, strict=True))
        status = clean_cell(row["Status"]).lower()
        if status not in ACTIVE_STATUSES:
            continue

        rows.append(
            ActiveLock(
                line=line_number,
                task=clean_cell(row["Task"]),
                owner=clean_cell(row["Owner"]),
                branch=clean_cell(row["Branch"]),
                status=status,
                locked_paths=split_locked_paths(row["Locked paths"]),
                review_owner=clean_cell(row["Review owner"]),
                required_checks=clean_cell(row["Required checks"]),
            )
        )

    return rows


def paths_conflict(left: str, right: str) -> bool:
    left = left.strip().rstrip("/")
    right = right.strip().rstrip("/")
    if not left or not right:
        return False
    if left == right:
        return True
    return left.startswith(f"{right}/") or right.startswith(f"{left}/")


def validate(ledger_path: Path = DEFAULT_LEDGER, protocol_path: Path = DEFAULT_PROTOCOL) -> list[str]:
    errors: list[str] = []

    if not protocol_path.exists():
        errors.append(f"missing protocol: {protocol_path}")
    if not ledger_path.exists():
        return errors + [f"missing ledger: {ledger_path}"]

    active_locks = parse_active_locks(ledger_path)
    seen_paths: list[tuple[ActiveLock, str]] = []

    for lock in active_locks:
        if lock.owner not in ALLOWED_OWNERS:
            errors.append(f"line {lock.line}: invalid owner {lock.owner!r}")
        if lock.review_owner not in ALLOWED_OWNERS:
            errors.append(f"line {lock.line}: invalid review owner {lock.review_owner!r}")
        if not lock.branch.startswith(ALLOWED_BRANCH_PREFIXES):
            errors.append(f"line {lock.line}: branch must start with feature/, bugfix/ or ablation/: {lock.branch!r}")
        if not lock.locked_paths:
            errors.append(f"line {lock.line}: active lock has no locked paths")
        if not lock.required_checks or lock.required_checks.lower() in {"none", "n/a", "-"}:
            errors.append(f"line {lock.line}: active lock must list required checks")

        for locked_path in lock.locked_paths:
            for forbidden in FORBIDDEN_LOCK_PARTS:
                if locked_path == forbidden.rstrip("/") or locked_path.startswith(forbidden):
                    errors.append(f"line {lock.line}: forbidden locked path {locked_path!r}")

            for other_lock, other_path in seen_paths:
                if paths_conflict(locked_path, other_path):
                    errors.append(
                        "file lock conflict: "
                        f"line {lock.line} {lock.task!r} locks {locked_path!r}; "
                        f"line {other_lock.line} {other_lock.task!r} locks {other_path!r}"
                    )
            seen_paths.append((lock, locked_path))

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("Dual-agent protocol check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    active_locks = parse_active_locks()
    locked_path_count = sum(len(lock.locked_paths) for lock in active_locks)
    print(f"Dual-agent protocol OK: {len(active_locks)} active lock(s), {locked_path_count} locked path(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
