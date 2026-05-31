from __future__ import annotations

from trustroom.agents.mock_runner import run_mock_trustroom
from trustroom.readiness import find_overclaim_phrases, run_readiness_checks


def test_default_trustroom_readiness_passes() -> None:
    report = run_readiness_checks()

    assert report.passed is True
    assert report.metrics["question_count"] >= 8
    assert report.metrics["replay_event_count"] >= 18
    assert report.metrics["evidence_coverage_ratio"] >= 0.8


def test_overclaim_phrase_detection_catches_forbidden_words() -> None:
    hits = find_overclaim_phrases(
        "This is production-ready, certified and fully compliant with guaranteed outcomes."
    )

    assert {"production-ready", "certified", "fully compliant", "guaranteed"} <= set(hits)


def test_unapproved_high_risk_item_in_final_pack_fails_readiness() -> None:
    result = run_mock_trustroom()
    bad_pack = result.final_pack.model_copy(
        update={
            "included_answer_ids": result.final_pack.included_answer_ids + ["A-006"],
            "blocked_item_ids": [],
            "readiness_summary": "ready",
        }
    )
    bad_result = result.model_copy(update={"final_pack": bad_pack})

    report = run_readiness_checks(mock_result=bad_result)

    assert report.passed is False
    assert any("Q-006" in issue.message for issue in report.issues)
