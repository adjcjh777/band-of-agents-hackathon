from __future__ import annotations

import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "check_public_submission_ready.py"
SPEC = importlib.util.spec_from_file_location("check_public_submission_ready", MODULE_PATH)
check_public_submission_ready = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(check_public_submission_ready)


def test_current_public_submission_package_is_known_video_pending() -> None:
    report = check_public_submission_ready.validate_public_submission(skip_network=True)

    assert report.status == "BLOCKED"
    assert report.blocking_issues == []
    assert any("Video Presentation" in item for item in report.pending_items)
    assert report.urls["lablab_team"]
    assert report.urls["github"]
    assert report.urls["render_application"]


def test_happy_path_with_video_pending_exits_zero(tmp_path: Path) -> None:
    repo_root = _write_submission_fixture(tmp_path)

    report = check_public_submission_ready.validate_public_submission(
        repo_root,
        skip_network=True,
    )

    assert report.status == "BLOCKED"
    assert report.blocking_issues == []
    assert check_public_submission_ready.main(
        ["--repo-root", str(repo_root), "--skip-network"]
    ) == 0


def test_lablab_team_url_cannot_be_application_url(tmp_path: Path) -> None:
    repo_root = _write_submission_fixture(
        tmp_path,
        application_line=(
            "- [x] Application URL。"
            "https://lablab.ai/ai-hackathons/band-of-agents-hackathon/rfp-trustroom。"
        ),
    )

    report = check_public_submission_ready.validate_public_submission(
        repo_root,
        skip_network=True,
    )

    assert any("Application URL" in issue and "Render" in issue for issue in report.blocking_issues)
    assert any("LabLab" in issue for issue in report.blocking_issues)


def test_video_checked_without_url_fails_closed(tmp_path: Path) -> None:
    repo_root = _write_submission_fixture(
        tmp_path,
        video_line="- [x] Video Presentation，official 5 minute recording is complete.",
    )

    report = check_public_submission_ready.validate_public_submission(
        repo_root,
        skip_network=True,
    )

    assert any("Video Presentation" in issue for issue in report.blocking_issues)
    assert check_public_submission_ready.main(
        ["--repo-root", str(repo_root), "--skip-network"]
    ) == 1


def test_positive_overclaim_fails_closed(tmp_path: Path) -> None:
    repo_root = _write_submission_fixture(
        tmp_path,
        extra_copy="This is a production deployment with complete autonomous live workflow.",
    )

    report = check_public_submission_ready.validate_public_submission(
        repo_root,
        skip_network=True,
    )

    assert any("production deployment" in issue for issue in report.blocking_issues)
    assert any(
        "complete autonomous live workflow" in issue for issue in report.blocking_issues
    )


def _write_submission_fixture(
    tmp_path: Path,
    *,
    application_line: str = "- [x] Application URL。https://rfp-trustroom.onrender.com public smoke passed.",
    video_line: str = (
        "- [ ] Video Presentation，script is ready in docs/submission-assets/video-script-shot-list.md; "
        "public video URL 尚未上传。"
    ),
    extra_copy: str = "",
) -> Path:
    repo_root = tmp_path / "repo"
    asset_dir = repo_root / "docs" / "submission-assets"
    asset_dir.mkdir(parents=True)

    (repo_root / "README.md").write_text(
        "\n".join(
            [
                "# RFP TrustRoom",
                "",
                "Public GitHub Repository: https://github.com/adjcjh777/band-of-agents-hackathon.",
                "Demo Application URL: https://rfp-trustroom.onrender.com.",
                "LabLab team/profile page: https://lablab.ai/ai-hackathons/band-of-agents-hackathon/rfp-trustroom.",
                "Replay is the public-safe fallback and live autonomous replies remain a separate gate.",
                "This is a hackathon working prototype with a no-overclaim boundary.",
            ]
        ),
        encoding="utf-8",
    )
    (repo_root / "docs" / "submission-checklist.md").write_text(
        "\n".join(
            [
                "# Submission Checklist",
                "",
                "- [x] LabLab team/profile URL：https://lablab.ai/ai-hackathons/band-of-agents-hackathon/rfp-trustroom。",
                video_line,
                "- [x] Public GitHub Repository。https://github.com/adjcjh777/band-of-agents-hackathon。",
                "- [x] Demo Application Platform。Render Web Service：`rfp-trustroom`。",
                application_line,
            ]
        ),
        encoding="utf-8",
    )
    (asset_dir / "submission-copy.md").write_text(
        "\n".join(
            [
                "# RFP TrustRoom Submission Copy",
                "",
                "## Project Title",
                "",
                "RFP TrustRoom",
                "",
                "## Short Description",
                "",
                "A multi-agent RFP response room where agents coordinate through Band.",
                "",
                "## Long Description",
                "",
                "RFP TrustRoom coordinates RFP and security questionnaire work through Band-style handoffs. "
                "Replay is the public-safe fallback. Live REST evidence was verified separately, and complete "
                "autonomous live replies remain a separate gate until connected peers pass the smoke test.",
                "",
                "## Tags",
                "",
                "Band, multi-agent systems, RFP response, FastAPI",
                extra_copy,
            ]
        ),
        encoding="utf-8",
    )

    for filename in check_public_submission_ready.REQUIRED_ASSETS:
        path = asset_dir / filename
        if filename == "submission-copy.md":
            continue
        path.write_bytes(b"not empty")

    return repo_root
