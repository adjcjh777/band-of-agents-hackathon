from __future__ import annotations

import csv
import json
from pathlib import Path

from trustroom.models import EvidenceFreshness, EventType, ExecutionMode, RiskLevel
from trustroom.sample_loader import (
    DEFAULT_SAMPLE_DIR,
    REPLAY_FIXTURE_PATH,
    load_default_sample_pack,
    load_replay_events,
    load_sample_pack,
)


def test_default_sample_pack_loads_enterprise_case() -> None:
    sample = load_default_sample_pack()

    assert sample.case.case_id == "acme-security-rfp"
    assert sample.case.mode == ExecutionMode.REPLAY
    assert len(sample.questions) >= 8
    assert len(sample.knowledge) >= 12
    assert sample.rfp_markdown.startswith("# Acme Financial Services")


def test_questionnaire_has_required_columns_and_risk_mix() -> None:
    questionnaire_path = DEFAULT_SAMPLE_DIR / "questionnaire.csv"
    with questionnaire_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)

    assert reader.fieldnames == [
        "id",
        "question",
        "category",
        "risk_hint",
        "required_evidence_type",
        "business_owner",
    ]
    assert len(rows) >= 8
    assert {row["risk_hint"] for row in rows} >= {
        RiskLevel.LOW.value,
        RiskLevel.MEDIUM.value,
        RiskLevel.HIGH.value,
    }


def test_knowledge_fixture_contains_current_stale_missing_and_conflicting_cases() -> None:
    sample = load_sample_pack(DEFAULT_SAMPLE_DIR)
    freshness_labels = {snippet.freshness_label for snippet in sample.knowledge}

    assert EvidenceFreshness.CURRENT in freshness_labels
    assert EvidenceFreshness.STALE in freshness_labels
    assert EvidenceFreshness.MISSING in freshness_labels
    assert EvidenceFreshness.CONFLICTING in freshness_labels
    assert sample.evidence_coverage["total_questions"] >= 8
    assert sample.evidence_coverage["covered_or_explicit_gap"] == sample.evidence_coverage["total_questions"]


def test_replay_fixture_covers_main_demo_chain() -> None:
    events = load_replay_events(REPLAY_FIXTURE_PATH)

    assert len(events) >= 18
    assert all(event["mode_label"] == "REPLAY" for event in events)
    assert {event["event_type"] for event in events} >= {
        EventType.INTAKE.value,
        EventType.HANDOFF.value,
        EventType.EVIDENCE_FOUND.value,
        EventType.DRAFT_CREATED.value,
        EventType.REVIEW_DECISION.value,
        EventType.HUMAN_APPROVAL.value,
        EventType.FINAL_PACK_CREATED.value,
        EventType.EVOLUTION_PROPOSED.value,
        EventType.LESSON_ACCEPTED.value,
    }

    agents = {
        value
        for event in events
        for value in (event["sender"], event["receiver"])
        if value.endswith("-agent")
    }
    assert len(agents) >= 3
    assert any(
        event["sender"] == "compliance-review-agent"
        and event["receiver"] in {"evidence-retriever-agent", "answer-drafter-agent"}
        for event in events
    )
    assert any("approval queue" in event["payload_summary"].lower() for event in events)
    assert any("evidence coverage" in event["payload_summary"].lower() for event in events)
    assert any("final pack" in event["payload_summary"].lower() for event in events)


def test_replay_fixture_is_jsonl_and_contains_no_forbidden_placeholders() -> None:
    forbidden_terms = ("real customer", "API key", "room_", "agent_key", "secret")
    raw_text = REPLAY_FIXTURE_PATH.read_text(encoding="utf-8")

    assert not any(term in raw_text for term in forbidden_terms)
    for line in raw_text.splitlines():
        assert json.loads(line)

    sample_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in Path("samples/acme-security-rfp").glob("*")
        if path.is_file()
    )
    assert not any(term in sample_text for term in forbidden_terms)
