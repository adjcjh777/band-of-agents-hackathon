from __future__ import annotations

import argparse
import re
import struct
from pathlib import Path
from zipfile import BadZipFile, ZipFile


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ASSET_DIR = ROOT / "docs" / "submission-assets"
DEFAULT_CHECKLIST = ROOT / "docs" / "submission-checklist.md"

COVER_FILE = "rfp-trustroom-cover.png"
DECK_PDF_FILE = "rfp-trustroom-submission-deck.pdf"
DECK_PPTX_FILE = "rfp-trustroom-submission-deck.pptx"
VIDEO_SCRIPT_FILE = "video-script-shot-list.md"
SUBMISSION_COPY_FILE = "submission-copy.md"
SCREENSHOT_CROPS = (
    "dashboard-replay-first-screen.png",
    "run-trace-route.png",
    "representative-traces.png",
)
REQUIRED_FILES = (
    COVER_FILE,
    DECK_PDF_FILE,
    DECK_PPTX_FILE,
    VIDEO_SCRIPT_FILE,
    SUBMISSION_COPY_FILE,
    *SCREENSHOT_CROPS,
)
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
EXPECTED_COVER_SIZE = (1920, 1080)
EXPECTED_SLIDE_COUNT = 8
SLIDE_RE = re.compile(r"^ppt/slides/slide\d+\.xml$")
REAL_URL_RE = re.compile(r"https?://(?![<])[^\s)>\],]+")

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


def validate_submission_assets(
    asset_dir: Path = DEFAULT_ASSET_DIR,
    checklist_path: Path = DEFAULT_CHECKLIST,
) -> list[str]:
    issues: list[str] = []
    asset_dir = Path(asset_dir)
    checklist_path = Path(checklist_path)

    if not asset_dir.exists():
        return [f"asset directory is missing: {asset_dir}"]
    if not asset_dir.is_dir():
        return [f"asset path is not a directory: {asset_dir}"]

    _check_required_files(asset_dir, issues)
    _check_cover_png(asset_dir / COVER_FILE, issues)
    _check_pptx_contract(asset_dir / DECK_PPTX_FILE, issues)
    _check_boundary_texts(
        asset_dir / SUBMISSION_COPY_FILE,
        asset_dir / VIDEO_SCRIPT_FILE,
        issues,
    )
    _check_public_completion_boundary(checklist_path, issues)
    return issues


def _check_required_files(asset_dir: Path, issues: list[str]) -> None:
    for filename in REQUIRED_FILES:
        path = asset_dir / filename
        if not path.exists():
            issues.append(f"required asset missing: {path}")
            continue
        if not path.is_file():
            issues.append(f"required asset is not a file: {path}")
            continue
        if path.stat().st_size <= 0:
            issues.append(f"required asset is empty: {path}")


def _check_cover_png(path: Path, issues: list[str]) -> None:
    if not path.exists() or path.stat().st_size <= 0:
        return
    try:
        width, height = read_png_dimensions(path)
    except ValueError as exc:
        issues.append(f"{path} is not a valid PNG cover: {exc}")
        return
    if (width, height) != EXPECTED_COVER_SIZE:
        issues.append(
            f"{path} must be {EXPECTED_COVER_SIZE[0]}x{EXPECTED_COVER_SIZE[1]}, got {width}x{height}"
        )


def read_png_dimensions(path: Path) -> tuple[int, int]:
    header = path.read_bytes()[:24]
    if len(header) < 24:
        raise ValueError("file is too small for a PNG IHDR header")
    if not header.startswith(PNG_SIGNATURE):
        raise ValueError("PNG signature is missing")
    ihdr_length = struct.unpack(">I", header[8:12])[0]
    if header[12:16] != b"IHDR" or ihdr_length != 13:
        raise ValueError("first chunk is not a standard IHDR chunk")
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def _check_pptx_contract(path: Path, issues: list[str]) -> None:
    if not path.exists() or path.stat().st_size <= 0:
        return
    try:
        with ZipFile(path) as deck:
            names = deck.namelist()
    except BadZipFile:
        issues.append(f"{path} is not a valid PPTX zip archive")
        return

    slide_names = sorted(name for name in names if SLIDE_RE.match(name))
    if len(slide_names) != EXPECTED_SLIDE_COUNT:
        issues.append(
            f"{path} must contain {EXPECTED_SLIDE_COUNT} slides, found {len(slide_names)}"
        )

    lower_names = [name.lower() for name in names]
    if any(name.endswith("vbaproject.bin") for name in lower_names):
        issues.append(f"{path} contains vbaProject.bin")

    suspicious = [
        name
        for name in names
        if _is_suspicious_embedded_object(name)
    ]
    if suspicious:
        issues.append(
            f"{path} contains suspicious embedded object(s): {', '.join(sorted(suspicious))}"
        )


def _is_suspicious_embedded_object(name: str) -> bool:
    lower = name.lower()
    return (
        lower.startswith("ppt/embeddings/")
        or "/embeddings/" in lower
        or "oleobject" in lower
        or lower.startswith("ppt/activex/")
        or "/activex/" in lower
    )


def _check_boundary_texts(copy_path: Path, script_path: Path, issues: list[str]) -> None:
    texts: list[tuple[str, str]] = []
    for path in (copy_path, script_path):
        if not path.exists() or path.stat().st_size <= 0:
            continue
        text = path.read_text(encoding="utf-8")
        texts.append((path.name, text))
        lower = text.lower()
        if "replay" not in lower:
            issues.append(f"{path} must preserve the replay boundary")
        if "live" not in lower:
            issues.append(f"{path} must preserve the live boundary")
        if not _has_no_overclaim_boundary(lower):
            issues.append(f"{path} must include a no-overclaim boundary")
        _check_forbidden_positive_claims(path, text, issues)

    if len(texts) < 2:
        return
    combined = "\n".join(text for _, text in texts).lower()
    for required in ("replay", "live", "working prototype"):
        if required not in combined:
            issues.append(f"submission text corpus must mention {required!r}")


def _has_no_overclaim_boundary(lower_text: str) -> bool:
    return any(
        marker in lower_text
        for marker in (
            "working prototype",
            "separate gate",
            "public-safe",
            "do not claim",
            "must not claim",
            "cannot be described",
            "remain a separate gate",
        )
    )


def _check_forbidden_positive_claims(path: Path, text: str, issues: list[str]) -> None:
    for line_number, line in enumerate(text.splitlines(), start=1):
        lower_line = line.lower()
        for phrase in FORBIDDEN_POSITIVE_CLAIMS:
            if phrase in lower_line and not _line_is_boundary_context(lower_line, phrase):
                issues.append(
                    f"{path}:{line_number} makes a forbidden positive claim: {phrase!r}"
                )


def _line_is_boundary_context(lower_line: str, phrase: str) -> bool:
    escaped = re.escape(phrase)
    negated_before_phrase = (
        rf"\b(?:do not|don't|must not|cannot|can't|never)\s+"
        rf"(?:claim|describe|call|present|state|say|imply|use|treat as)[^.;:]*\b{escaped}\b"
    )
    no_phrase_claimed = rf"\b(?:no|not a|not an|not)\s+{escaped}\b"
    phrase_separate_gate = rf"\b{escaped}\b[^.;:]*\bremain(?:s)?\s+(?:a\s+)?separate gate\b"
    phrase_not_claimed = rf"\b{escaped}\b[^.;:]*\b(?:is|are|was|were)?\s*not\s+(?:claimed|verified|complete|available)\b"
    conditional_gate = rf"\b{escaped}\b[^.;:]*\b(?:until|unless)\b[^.;:]*\b(?:passes?|verified|done|complete|available)\b"
    chinese_boundary = rf"(?:不得|不能|不要|不可)[^。；：]*{escaped}|{escaped}[^。；：]*(?:仍|尚未|未)[^。；：]*(?:单独|独立|门槛|验证)"
    return any(
        re.search(pattern, lower_line)
        for pattern in (
            negated_before_phrase,
            no_phrase_claimed,
            phrase_separate_gate,
            phrase_not_claimed,
            conditional_gate,
            chinese_boundary,
        )
    )


def _check_public_completion_boundary(checklist_path: Path, issues: list[str]) -> None:
    if not checklist_path.exists():
        issues.append(f"submission checklist is missing: {checklist_path}")
        return
    lines = checklist_path.read_text(encoding="utf-8").splitlines()
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
            if _line_marks_complete(line):
                nearby = "\n".join(lines[index : index + 3])
                if not _contains_real_url(nearby):
                    issues.append(
                        f"submission checklist marks {item!r} complete without a real public URL"
                    )


def _line_marks_complete(line: str) -> bool:
    normalized = line.lower().replace(" ", "")
    return "-[x]" in normalized or "*[x]" in normalized


def _contains_real_url(text: str) -> bool:
    return any(
        "<" not in match.group(0) and "example" not in match.group(0).lower()
        for match in REAL_URL_RE.finditer(text)
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate public-safe TrustRoom submission assets.")
    parser.add_argument(
        "--asset-dir",
        type=Path,
        default=DEFAULT_ASSET_DIR,
        help="Submission asset directory to validate.",
    )
    parser.add_argument(
        "--checklist",
        type=Path,
        default=DEFAULT_CHECKLIST,
        help="Submission checklist used for public URL completion boundaries.",
    )
    args = parser.parse_args(argv)

    issues = validate_submission_assets(args.asset_dir, args.checklist)
    if not issues:
        print(f"Submission assets OK: {args.asset_dir}")
        return 0

    print("Submission assets check failed:")
    for issue in issues:
        print(f"- {issue}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
