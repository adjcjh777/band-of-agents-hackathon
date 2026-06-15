from __future__ import annotations

import argparse
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import NamedTuple


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = "docs/submission-assets"
README_FILE = "README.md"
CHECKLIST_FILE = "docs/submission-checklist.md"
SUBMISSION_COPY_FILE = f"{ASSET_DIR}/submission-copy.md"

REQUIRED_ASSETS = (
    "rfp-trustroom-cover.png",
    "rfp-trustroom-submission-deck.pdf",
    "rfp-trustroom-submission-deck.pptx",
    "video-script-shot-list.md",
    "submission-copy.md",
    "dashboard-replay-first-screen.png",
    "run-trace-route.png",
    "representative-traces.png",
)
REQUIRED_COPY_SECTIONS = (
    "Project Title",
    "Short Description",
    "Long Description",
    "Tags",
)
URL_RE = re.compile(r"https?://(?![<])[^\s)>\]}\"'`。；，：]+")
MARKDOWN_CHECK_RE = re.compile(r"^\s*[-*]\s*\[(?P<mark>[ xX])\]\s*(?P<body>.*)$")
FORBIDDEN_POSITIVE_CLAIMS = (
    "production deployment",
    "production-ready",
    "formal audit",
    "compliance certification",
    "legal advice",
    "complete autonomous live workflow",
    "complete autonomous live replies",
    "fully automated compliance",
    "enterprise-grade compliance",
)
PUBLIC_CHECKLIST_ITEMS = (
    "Video Presentation",
    "Public GitHub Repository",
    "Demo Application Platform",
    "Application URL",
)


class ReadinessReport(NamedTuple):
    status: str
    blocking_issues: list[str]
    pending_items: list[str]
    warnings: list[str]
    urls: dict[str, list[str]]


def validate_public_submission(
    repo_root: Path = ROOT,
    *,
    skip_network: bool = True,
) -> ReadinessReport:
    repo_root = Path(repo_root)
    blocking_issues: list[str] = []
    pending_items: list[str] = []
    warnings: list[str] = []

    readme_text = _read_required_text(repo_root / README_FILE, blocking_issues)
    checklist_text = _read_required_text(repo_root / CHECKLIST_FILE, blocking_issues)
    copy_text = _read_required_text(repo_root / SUBMISSION_COPY_FILE, blocking_issues)
    combined_text = "\n".join((readme_text, checklist_text, copy_text))

    _check_submission_copy_fields(copy_text, blocking_issues)
    _check_assets(repo_root / ASSET_DIR, blocking_issues)
    urls = _collect_submission_urls(readme_text, checklist_text, copy_text)
    _check_required_urls(urls, blocking_issues)
    _check_checklist_completion(checklist_text, blocking_issues, pending_items)
    _check_overclaim_boundaries(
        {
            README_FILE: readme_text,
            CHECKLIST_FILE: checklist_text,
            SUBMISSION_COPY_FILE: copy_text,
        },
        blocking_issues,
    )
    if not _has_replay_live_boundary(combined_text):
        blocking_issues.append(
            "README/checklist/submission copy must preserve replay, live, and no-overclaim boundaries"
        )
    if not skip_network:
        _check_public_url_reachability(urls, blocking_issues, warnings)

    status = "READY" if not blocking_issues and not pending_items else "BLOCKED"
    return ReadinessReport(
        status=status,
        blocking_issues=blocking_issues,
        pending_items=pending_items,
        warnings=warnings,
        urls=urls,
    )


def _read_required_text(path: Path, issues: list[str]) -> str:
    if not path.exists():
        issues.append(f"required document missing: {path}")
        return ""
    if not path.is_file():
        issues.append(f"required document is not a file: {path}")
        return ""
    if path.stat().st_size <= 0:
        issues.append(f"required document is empty: {path}")
        return ""
    return path.read_text(encoding="utf-8")


def _check_submission_copy_fields(copy_text: str, issues: list[str]) -> None:
    if not copy_text:
        return
    sections = {
        heading: _markdown_section(copy_text, heading).strip()
        for heading in REQUIRED_COPY_SECTIONS
    }
    for heading, body in sections.items():
        if not body:
            issues.append(f"submission copy is missing required field: {heading}")

    title = sections.get("Project Title", "")
    if title and len(_single_line(title)) > 50:
        issues.append("Project Title must be 50 characters or fewer")

    short_description = sections.get("Short Description", "")
    if short_description and len(_single_line(short_description)) > 255:
        issues.append("Short Description must be 255 characters or fewer")

    tags = [
        tag.strip()
        for tag in sections.get("Tags", "").replace("\n", ",").split(",")
        if tag.strip()
    ]
    if tags and len(tags) < 3:
        issues.append("Technology & Category Tags must include at least 3 tags")


def _markdown_section(markdown: str, heading: str) -> str:
    pattern = re.compile(
        rf"^##\s+{re.escape(heading)}\s*\n(?P<body>.*?)(?=^##\s+|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(markdown)
    return match.group("body") if match else ""


def _single_line(text: str) -> str:
    return " ".join(line.strip() for line in text.splitlines() if line.strip())


def _check_assets(asset_dir: Path, issues: list[str]) -> None:
    if not asset_dir.exists():
        issues.append(f"submission asset directory missing: {asset_dir}")
        return
    if not asset_dir.is_dir():
        issues.append(f"submission asset path is not a directory: {asset_dir}")
        return
    for filename in REQUIRED_ASSETS:
        path = asset_dir / filename
        if not path.exists():
            issues.append(f"required submission asset missing: {path}")
            continue
        if not path.is_file():
            issues.append(f"required submission asset is not a file: {path}")
            continue
        if path.stat().st_size <= 0:
            issues.append(f"required submission asset is empty: {path}")


def _collect_submission_urls(
    readme_text: str,
    checklist_text: str,
    copy_text: str,
) -> dict[str, list[str]]:
    combined = "\n".join((readme_text, checklist_text, copy_text))
    all_urls = _real_urls(combined)
    application_context = _nearby_text_for_labels(
        checklist_text + "\n" + readme_text,
        ("Application URL", "Demo Application URL"),
    )
    public_github_context = _nearby_text_for_labels(
        checklist_text + "\n" + readme_text,
        ("Public GitHub Repository", "Public GitHub URL"),
    )
    lablab_context = _nearby_text_for_labels(
        checklist_text + "\n" + readme_text,
        ("lablab.ai team/profile", "LabLab team/profile", "team/profile"),
    )
    video_context = _nearby_text_for_labels(
        checklist_text + "\n" + readme_text,
        ("Video Presentation", "public video", "公开视频"),
    )

    return {
        "all": all_urls,
        "lablab_team": [url for url in _real_urls(lablab_context) if _is_lablab_url(url)],
        "github": [url for url in _real_urls(public_github_context) if _is_github_url(url)],
        "render_application": [
            url for url in _real_urls(application_context) if _is_render_url(url)
        ],
        "application_context": _real_urls(application_context),
        "video": [url for url in _real_urls(video_context) if not _is_local_or_placeholder_url(url)],
    }


def _nearby_text_for_labels(text: str, labels: tuple[str, ...], window: int = 2) -> str:
    lines = text.splitlines()
    selected: list[str] = []
    lower_labels = tuple(label.lower() for label in labels)
    for index, line in enumerate(lines):
        lower = line.lower()
        if any(label in lower for label in lower_labels):
            selected.extend(lines[index : index + window + 1])
    return "\n".join(selected)


def _real_urls(text: str) -> list[str]:
    urls: list[str] = []
    for match in URL_RE.finditer(text):
        url = match.group(0).rstrip(".,;:。；，：`\"'")
        if not _is_local_or_placeholder_url(url):
            urls.append(url)
    return _dedupe(urls)


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def _is_local_or_placeholder_url(url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    host = (parsed.hostname or "").lower()
    return (
        not host
        or host in {"localhost", "127.0.0.1", "::1"}
        or host.endswith(".local")
        or host.endswith(".invalid")
        or "example" in host
        or "<" in url
    )


def _is_lablab_url(url: str) -> bool:
    host = (urllib.parse.urlparse(url).hostname or "").lower()
    return host == "lablab.ai" or host.endswith(".lablab.ai")


def _is_github_url(url: str) -> bool:
    host = (urllib.parse.urlparse(url).hostname or "").lower()
    return host == "github.com" or host.endswith(".github.com")


def _is_render_url(url: str) -> bool:
    host = (urllib.parse.urlparse(url).hostname or "").lower()
    return host.endswith(".onrender.com")


def _check_required_urls(urls: dict[str, list[str]], issues: list[str]) -> None:
    if not urls["lablab_team"]:
        issues.append("LabLab team/profile URL is missing")
    if not urls["github"]:
        issues.append("Public GitHub Repository URL is missing")
    if not urls["render_application"]:
        issues.append("Render Application URL is missing")

    application_urls = urls["application_context"]
    if application_urls:
        has_render = any(_is_render_url(url) for url in application_urls)
        has_lablab_only = any(_is_lablab_url(url) for url in application_urls) and not has_render
        if has_lablab_only:
            issues.append("Application URL appears to use the LabLab team/profile URL")


def _check_checklist_completion(
    checklist_text: str,
    issues: list[str],
    pending_items: list[str],
) -> None:
    lines = checklist_text.splitlines()
    for item in PUBLIC_CHECKLIST_ITEMS:
        matches = [
            index
            for index, line in enumerate(lines)
            if item.lower() in line.lower()
        ]
        if not matches:
            issues.append(f"submission checklist is missing item: {item}")
            continue
        for index in matches:
            line = lines[index]
            checked = _is_checked_checklist_line(line)
            context = _checklist_context(lines, index, item)
            urls = _real_urls(context)
            if checked and not urls:
                issues.append(
                    f"submission checklist marks {item!r} complete without a real public URL"
                )
            if item == "Application URL" and checked:
                if urls and not any(_is_render_url(url) for url in urls):
                    issues.append(
                        "submission checklist marks Application URL complete without a Render URL"
                    )
                if any(_is_lablab_url(url) for url in urls):
                    issues.append("Application URL appears to use the LabLab team/profile URL")
            if item == "Video Presentation":
                if checked and not urls:
                    issues.append(
                        "submission checklist marks Video Presentation complete without a public video URL"
                    )
                elif not checked and not urls:
                    _append_unique(
                        pending_items,
                        "Video Presentation public URL is still pending; package is not submission-ready until upload is complete",
                    )


def _checklist_context(lines: list[str], index: int, item: str) -> str:
    line = lines[index]
    if item == "Demo Application Platform":
        return "\n".join(lines[index : index + 3])
    continuation: list[str] = [line]
    for next_line in lines[index + 1 : index + 3]:
        if MARKDOWN_CHECK_RE.match(next_line):
            break
        continuation.append(next_line)
    return "\n".join(continuation)


def _is_checked_checklist_line(line: str) -> bool:
    match = MARKDOWN_CHECK_RE.match(line)
    return bool(match and match.group("mark").lower() == "x")


def _append_unique(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)


def _check_overclaim_boundaries(texts: dict[str, str], issues: list[str]) -> None:
    for label, text in texts.items():
        for line_number, line in enumerate(text.splitlines(), start=1):
            for phrase in FORBIDDEN_POSITIVE_CLAIMS:
                if _line_has_forbidden_positive_claim(line, phrase):
                    issues.append(
                        f"{label}:{line_number} makes a forbidden positive claim: {phrase!r}"
                    )


def _line_has_forbidden_positive_claim(line: str, phrase: str) -> bool:
    lower_line = line.lower()
    if phrase not in lower_line:
        return False
    for clause in _claim_clauses(lower_line):
        if phrase in clause and not _clause_is_boundary_context(clause, phrase):
            return True
    return False


def _claim_clauses(lower_line: str) -> list[str]:
    return [
        clause.strip()
        for clause in re.split(
            r"(?<=[.;:。；：])\s+|\bbut\b|\bhowever\b|不过|但是|但",
            lower_line,
        )
        if clause.strip()
    ]


def _clause_is_boundary_context(clause: str, phrase: str) -> bool:
    escaped = re.escape(phrase)
    boundary_patterns = (
        rf"\b(?:do not|don't|must not|cannot|can't|never)\s+"
        rf"(?:claim|describe|call|present|state|say|imply|use|treat as)[^.;:。；：]*\b{escaped}\b",
        rf"\b(?:no|not a|not an|not)\s+{escaped}\b",
        rf"\b{escaped}\b[^.;:。；：]*\bremain(?:s)?\s+(?:a\s+)?separate gate\b",
        rf"\b{escaped}\b[^.;:。；：]*\b(?:is|are|was|were)?\s*not\s+"
        rf"(?:claimed|verified|complete|available|done)\b",
        rf"\b{escaped}\b[^.;:。；：]*\b(?:until|unless)\b[^.;:。；：]*\b"
        rf"(?:passes?|verified|done|complete|available)\b",
        rf"(?:不得|不能|不要|不可|尚未|未|避免)[^。；：]*{escaped}",
        rf"{escaped}[^。；：]*(?:仍|尚未|未)[^。；：]*(?:单独|独立|门槛|验证|完成)",
    )
    return any(re.search(pattern, clause) for pattern in boundary_patterns)


def _has_replay_live_boundary(text: str) -> bool:
    lower = text.lower()
    return (
        "replay" in lower
        and "live" in lower
        and any(
            marker in lower
            for marker in (
                "no-overclaim",
                "working prototype",
                "separate gate",
                "不能宣称",
                "不得宣称",
            )
        )
    )


def _check_public_url_reachability(
    urls: dict[str, list[str]],
    issues: list[str],
    warnings: list[str],
) -> None:
    urls_to_check = _dedupe(
        urls["lablab_team"] + urls["github"] + urls["render_application"] + urls["video"]
    )
    if not urls_to_check:
        warnings.append("network check requested, but no public URLs were available")
        return
    for url in urls_to_check:
        try:
            _probe_url(url)
        except (OSError, ValueError, UnicodeError) as exc:
            issues.append(f"public URL is not reachable: {url} ({exc})")


def _probe_url(url: str) -> None:
    request = urllib.request.Request(
        url,
        method="HEAD",
        headers={"User-Agent": "trustroom-public-submission-ready/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            if response.status >= 400:
                raise OSError(f"HTTP {response.status}")
    except urllib.error.HTTPError as exc:
        if exc.code not in {405, 403}:
            raise OSError(f"HTTP {exc.code}") from exc
        get_request = urllib.request.Request(
            url,
            method="GET",
            headers={"User-Agent": "trustroom-public-submission-ready/1.0"},
        )
        with urllib.request.urlopen(get_request, timeout=10) as response:
            if response.status >= 400:
                raise OSError(f"HTTP {response.status}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fail-closed public submission readiness check for RFP TrustRoom."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=ROOT,
        help="Repository root to validate.",
    )
    parser.add_argument(
        "--skip-network",
        action="store_true",
        help="Skip public URL reachability probes; still validates URL presence and boundaries.",
    )
    parser.add_argument(
        "--network",
        action="store_true",
        help="Probe discovered public URLs with HEAD/GET requests.",
    )
    args = parser.parse_args(argv)

    skip_network = True
    if args.network:
        skip_network = False
    if args.skip_network:
        skip_network = True

    report = validate_public_submission(args.repo_root, skip_network=skip_network)
    print(f"Public submission readiness: {report.status}")
    if skip_network:
        print("Network checks: skipped")
    else:
        print("Network checks: enabled")

    if report.urls["lablab_team"]:
        print(f"LabLab team/profile URL: {report.urls['lablab_team'][0]}")
    if report.urls["github"]:
        print(f"Public GitHub URL: {report.urls['github'][0]}")
    if report.urls["render_application"]:
        print(f"Render Application URL: {report.urls['render_application'][0]}")

    if report.pending_items:
        print("Pending items:")
        for item in report.pending_items:
            print(f"- {item}")

    if report.warnings:
        print("Warnings:")
        for warning in report.warnings:
            print(f"- {warning}")

    if report.blocking_issues:
        print("Blocking issues:")
        for issue in report.blocking_issues:
            print(f"- {issue}")
        return 1

    print("Blocking issues: none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
