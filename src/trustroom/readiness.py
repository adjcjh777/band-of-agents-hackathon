from __future__ import annotations

import re
import time
from pathlib import Path

from trustroom.agents.mock_runner import MockRunResult, run_mock_trustroom
from trustroom.models import ReviewStatus, RiskLevel, TrustRoomModel
from trustroom.sample_loader import REPLAY_FIXTURE_PATH, SamplePack, load_default_sample_pack, load_replay_events


ROOT = Path(__file__).resolve().parents[2]
OVERCLAIM_PHRASES = [
    "production-ready",
    "certified",
    "fully compliant",
    "guaranteed",
    "enterprise-grade compliance",
]
SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("band_agent_key", re.compile(r"BAND_AGENT_KEY\s*=\s*[A-Za-z0-9_-]{12,}")),
    ("generic_api_key", re.compile(r"(?i)api[_-]?key\s*[:=]\s*['\"]?[A-Za-z0-9_-]{16,}")),
    ("openai_style_key", re.compile(r"sk-[A-Za-z0-9]{20,}")),
    ("band_room_id", re.compile(r"(?i)(?:room_id|band_room_id|band_room_ref)\s*[:=]\s*['\"]?room_[A-Za-z0-9]{8,}")),
    ("agent_key", re.compile(r"(?i)agent_key\s*[:=]\s*['\"]?[A-Za-z0-9_-]{12,}")),
)
EXCLUDED_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "pilotdeck",
}
EXCLUDED_FILENAMES = {".env", "agent_config.yaml"}


class GateIssue(TrustRoomModel):
    code: str
    message: str


class SecretHit(TrustRoomModel):
    source: str
    line_number: int
    pattern_name: str
    match: str


class ReadinessReport(TrustRoomModel):
    passed: bool
    issues: list[GateIssue]
    metrics: dict[str, int | float]


def run_readiness_checks(
    *,
    sample: SamplePack | None = None,
    mock_result: MockRunResult | None = None,
    replay_path: Path | str = REPLAY_FIXTURE_PATH,
    max_replay_load_seconds: float = 5.0,
) -> ReadinessReport:
    issues: list[GateIssue] = []
    sample = sample or load_default_sample_pack()
    mock_result = mock_result or run_mock_trustroom(sample)

    replay_start = time.perf_counter()
    replay_events = load_replay_events(replay_path)
    replay_elapsed = time.perf_counter() - replay_start

    question_count = len(sample.questions)
    if question_count < 8:
        issues.append(GateIssue(code="sample_too_small", message="Primary sample must include at least 8 question items."))

    if replay_elapsed > max_replay_load_seconds:
        issues.append(
            GateIssue(
                code="replay_slow",
                message=f"Replay loaded in {replay_elapsed:.3f}s, above {max_replay_load_seconds:.1f}s.",
            )
        )

    coverage = sample.evidence_coverage
    coverage_ratio = (
        coverage["covered_or_explicit_gap"] / coverage["total_questions"]
        if coverage["total_questions"]
        else 0.0
    )
    if coverage_ratio < 0.8:
        issues.append(
            GateIssue(
                code="low_evidence_coverage",
                message=f"Evidence coverage is {coverage_ratio:.0%}; expected at least 80% or explicit gaps.",
            )
        )

    issues.extend(_high_risk_gate_issues(mock_result))
    for draft in mock_result.drafts:
        hits = find_overclaim_phrases(draft.draft_text)
        if hits:
            issues.append(
                GateIssue(
                    code="overclaim_phrase",
                    message=f"{draft.answer_id} contains forbidden overclaim phrase(s): {', '.join(hits)}",
                )
            )

    return ReadinessReport(
        passed=not issues,
        issues=issues,
        metrics={
            "question_count": question_count,
            "replay_event_count": len(replay_events),
            "replay_load_seconds": round(replay_elapsed, 6),
            "evidence_coverage_ratio": round(coverage_ratio, 4),
            "high_risk_count": sum(1 for item in mock_result.questions if item.risk_level == RiskLevel.HIGH),
        },
    )


def find_overclaim_phrases(text: str) -> list[str]:
    lowered = text.lower()
    return [phrase for phrase in OVERCLAIM_PHRASES if phrase in lowered]


def scan_no_secrets(root: Path | str = ROOT) -> list[SecretHit]:
    hits: list[SecretHit] = []
    for path in _iter_scan_files(Path(root)):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        hits.extend(scan_text_for_secrets(text, source=str(path)))
    return hits


def scan_text_for_secrets(text: str, *, source: str) -> list[SecretHit]:
    hits: list[SecretHit] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for pattern_name, pattern in SECRET_PATTERNS:
            match = pattern.search(line)
            if match:
                hits.append(
                    SecretHit(
                        source=source,
                        line_number=line_number,
                        pattern_name=pattern_name,
                        match=_redact_match(match.group(0)),
                    )
                )
    return hits


def _high_risk_gate_issues(result: MockRunResult) -> list[GateIssue]:
    issues: list[GateIssue] = []
    approved_items = {approval.item_id for approval in result.approvals}
    blocked_items = set(result.final_pack.blocked_item_ids)
    review_status_by_item = {review.item_id: review.status for review in result.reviews}
    included_item_ids = {
        draft.item_id
        for draft in result.drafts
        if draft.answer_id in result.final_pack.included_answer_ids
    }
    allowed_review_statuses = {
        ReviewStatus.NEEDS_HUMAN_APPROVAL,
        ReviewStatus.REQUEST_CHANGES,
        ReviewStatus.BLOCKED,
    }

    for item in result.questions:
        if item.risk_level != RiskLevel.HIGH:
            continue
        review_status = review_status_by_item.get(item.item_id)
        safely_routed = (
            item.item_id in approved_items
            or item.item_id in blocked_items
            or review_status in allowed_review_statuses
        )
        if not safely_routed:
            issues.append(
                GateIssue(
                    code="high_risk_not_routed",
                    message=f"{item.item_id} is high risk but is not approved, request_changes, needs_human_approval or blocked.",
                )
            )
        if item.item_id in included_item_ids and item.item_id not in approved_items:
            issues.append(
                GateIssue(
                    code="unapproved_high_risk_final_pack",
                    message=f"{item.item_id} is high risk and appears in final pack without human approval.",
                )
            )
    return issues


def _iter_scan_files(root: Path):
    for path in root.rglob("*"):
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        if not path.is_file():
            continue
        if path.name in EXCLUDED_FILENAMES or path.name.startswith("secrets."):
            continue
        yield path


def _redact_match(value: str) -> str:
    if len(value) <= 12:
        return "<redacted>"
    return f"{value[:6]}...{value[-4:]}"
