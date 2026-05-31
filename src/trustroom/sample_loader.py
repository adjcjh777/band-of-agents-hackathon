from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from pydantic import Field

from trustroom.models import (
    CustomerCase,
    EvidenceFreshness,
    QuestionCategory,
    QuestionItem,
    RiskLevel,
    TrustRoomModel,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SAMPLE_DIR = ROOT / "samples" / "acme-security-rfp"
REPLAY_FIXTURE_PATH = ROOT / "reports" / "trustroom_replay.example.jsonl"
QUESTIONNAIRE_COLUMNS = [
    "id",
    "question",
    "category",
    "risk_hint",
    "required_evidence_type",
    "business_owner",
]


class KnowledgeSnippet(TrustRoomModel):
    evidence_id: str
    title: str
    snippet: str
    freshness_label: EvidenceFreshness
    category: QuestionCategory
    related_question_ids: list[str]
    confidence: float = Field(ge=0.0, le=1.0)


class SamplePack(TrustRoomModel):
    case: CustomerCase
    rfp_markdown: str
    questions: list[QuestionItem]
    knowledge: list[KnowledgeSnippet]

    @property
    def evidence_coverage(self) -> dict[str, int]:
        question_ids = {question.item_id for question in self.questions}
        explicit_gap_labels = {
            EvidenceFreshness.MISSING,
            EvidenceFreshness.STALE,
            EvidenceFreshness.CONFLICTING,
        }
        covered_or_explicit_gap = {
            question_id
            for snippet in self.knowledge
            for question_id in snippet.related_question_ids
            if question_id in question_ids
            and (
                snippet.freshness_label == EvidenceFreshness.CURRENT
                or snippet.freshness_label in explicit_gap_labels
            )
        }
        return {
            "total_questions": len(question_ids),
            "covered_or_explicit_gap": len(covered_or_explicit_gap),
        }


def load_sample_pack(sample_dir: Path | str) -> SamplePack:
    sample_path = Path(sample_dir)
    case = CustomerCase.model_validate_json((sample_path / "case.json").read_text(encoding="utf-8"))
    rfp_markdown = (sample_path / "rfp.md").read_text(encoding="utf-8")
    questions = _load_questions(sample_path / "questionnaire.csv", case.case_id)
    knowledge = [
        KnowledgeSnippet.model_validate(item)
        for item in json.loads((sample_path / "knowledge.json").read_text(encoding="utf-8"))
    ]
    return SamplePack(
        case=case,
        rfp_markdown=rfp_markdown,
        questions=questions,
        knowledge=knowledge,
    )


def load_default_sample_pack() -> SamplePack:
    return load_sample_pack(DEFAULT_SAMPLE_DIR)


def load_replay_events(path: Path | str = REPLAY_FIXTURE_PATH) -> list[dict[str, Any]]:
    replay_path = Path(path)
    events: list[dict[str, Any]] = []
    for line_number, line in enumerate(replay_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        event = json.loads(line)
        if "event_id" not in event:
            raise ValueError(f"replay line {line_number} is missing event_id")
        events.append(event)
    return events


def _load_questions(path: Path, case_id: str) -> list[QuestionItem]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != QUESTIONNAIRE_COLUMNS:
            raise ValueError(f"questionnaire columns must be {QUESTIONNAIRE_COLUMNS}")
        return [
            QuestionItem(
                item_id=row["id"],
                case_id=case_id,
                source_ref=f"{path.name}:{line_number}",
                question_text=row["question"],
                category=row["category"],
                risk_level=RiskLevel(row["risk_hint"]),
                required_evidence_type=row["required_evidence_type"],
                business_owner=row["business_owner"],
            )
            for line_number, row in enumerate(reader, start=2)
        ]
