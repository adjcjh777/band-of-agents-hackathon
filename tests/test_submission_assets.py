from __future__ import annotations

import importlib.util
import struct
import zipfile
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "check_submission_assets.py"
SPEC = importlib.util.spec_from_file_location("check_submission_assets", MODULE_PATH)
check_submission_assets = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(check_submission_assets)


def test_real_submission_assets_pass_contract() -> None:
    assert check_submission_assets.validate_submission_assets() == []


def test_missing_submission_assets_fail_closed(tmp_path: Path) -> None:
    issues = check_submission_assets.validate_submission_assets(
        asset_dir=tmp_path,
        checklist_path=Path("docs/submission-checklist.md"),
    )

    assert any("required asset missing" in issue for issue in issues)
    assert any("rfp-trustroom-cover.png" in issue for issue in issues)


def test_submission_copy_positive_overclaim_fails_closed(tmp_path: Path) -> None:
    asset_dir = _write_valid_asset_pack(tmp_path)
    (asset_dir / "submission-copy.md").write_text(
        "\n".join(
            [
                "Replay and live modes are available.",
                "This is a production deployment with complete autonomous live workflow.",
                "A public-safe fallback is still visible.",
            ]
        ),
        encoding="utf-8",
    )

    issues = check_submission_assets.validate_submission_assets(
        asset_dir=asset_dir,
        checklist_path=Path("docs/submission-checklist.md"),
    )

    assert any("production deployment" in issue for issue in issues)
    assert any("complete autonomous live workflow" in issue for issue in issues)


def test_mixed_boundary_and_positive_overclaim_line_fails_closed(tmp_path: Path) -> None:
    asset_dir = _write_valid_asset_pack(tmp_path)
    (asset_dir / "submission-copy.md").write_text(
        "\n".join(
            [
                "Replay and live boundaries are visible.",
                "This is not just a demo; it is a production deployment.",
                "Complete autonomous live replies remain a separate gate.",
            ]
        ),
        encoding="utf-8",
    )

    issues = check_submission_assets.validate_submission_assets(
        asset_dir=asset_dir,
        checklist_path=Path("docs/submission-checklist.md"),
    )

    assert any("production deployment" in issue for issue in issues)
    assert not any("complete autonomous live replies" in issue for issue in issues)


def test_pptx_embedded_object_fails_closed(tmp_path: Path) -> None:
    asset_dir = _write_valid_asset_pack(tmp_path)
    with zipfile.ZipFile(asset_dir / "rfp-trustroom-submission-deck.pptx", "a") as deck:
        deck.writestr("ppt/embeddings/oleObject1.bin", b"embedded")

    issues = check_submission_assets.validate_submission_assets(
        asset_dir=asset_dir,
        checklist_path=Path("docs/submission-checklist.md"),
    )

    assert any("suspicious embedded object" in issue for issue in issues)


def _write_valid_asset_pack(tmp_path: Path) -> Path:
    asset_dir = tmp_path / "submission-assets"
    asset_dir.mkdir()
    (asset_dir / "rfp-trustroom-cover.png").write_bytes(_png_header(width=1920, height=1080))
    (asset_dir / "rfp-trustroom-submission-deck.pdf").write_bytes(b"%PDF-1.4\n% test\n")
    _write_pptx(asset_dir / "rfp-trustroom-submission-deck.pptx")
    (asset_dir / "video-script-shot-list.md").write_text(
        "This is a hackathon working prototype. Replay is the public-safe fallback. "
        "Live autonomous replies remain a separate gate.",
        encoding="utf-8",
    )
    (asset_dir / "submission-copy.md").write_text(
        "The public-safe replay route is visible. Live Band REST evidence was verified separately; "
        "complete autonomous live replies remain a separate gate.",
        encoding="utf-8",
    )
    for filename in (
        "dashboard-replay-first-screen.png",
        "run-trace-route.png",
        "representative-traces.png",
    ):
        (asset_dir / filename).write_bytes(b"not empty")
    return asset_dir


def _png_header(*, width: int, height: int) -> bytes:
    return (
        check_submission_assets.PNG_SIGNATURE
        + struct.pack(">I", 13)
        + b"IHDR"
        + struct.pack(">II", width, height)
        + b"\x08\x02\x00\x00\x00"
    )


def _write_pptx(path: Path) -> None:
    with zipfile.ZipFile(path, "w") as deck:
        deck.writestr("[Content_Types].xml", "<Types />")
        for slide_number in range(1, 9):
            deck.writestr(f"ppt/slides/slide{slide_number}.xml", "<p:sld />")
