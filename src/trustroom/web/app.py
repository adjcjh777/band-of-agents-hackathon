from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from trustroom.agents.mock_runner import run_mock_trustroom
from trustroom.models import EventType, ExecutionMode, ReviewStatus
from trustroom.sample_loader import load_replay_events


TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"

app = FastAPI(title="RFP TrustRoom")
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))


@app.get("/health")
def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "title": "RFP TrustRoom",
        },
    )


@app.get("/runs/demo")
def demo_run(request: Request):
    return _render_run(request, mode=ExecutionMode.MOCK)


@app.get("/runs/demo/replay")
def replay_run(request: Request):
    return _render_run(request, mode=ExecutionMode.REPLAY)


def _render_run(request: Request, *, mode: ExecutionMode):
    context = _dashboard_context(mode=mode)
    return templates.TemplateResponse(request, "run.html", context)


def _dashboard_context(*, mode: ExecutionMode) -> dict[str, Any]:
    result = run_mock_trustroom()
    question_by_id = {question.item_id: question for question in result.questions}
    included = set(result.final_pack.included_answer_ids)
    blocked_items = set(result.final_pack.blocked_item_ids)
    approval_item_ids = {approval.item_id for approval in result.approvals}
    evidence_counter = Counter(candidate.freshness_label.value for candidate in result.evidence)

    if mode == ExecutionMode.REPLAY:
        timeline = load_replay_events()
    else:
        timeline = [event.model_dump(mode="json") | {"mode_label": "MOCK"} for event in result.events]

    answers = []
    for draft in sorted(result.drafts, key=lambda item: item.item_id):
        question = question_by_id[draft.item_id]
        if draft.answer_id in included:
            status = "ready"
        elif draft.item_id in blocked_items:
            status = "blocked"
        else:
            status = "needs review"
        answers.append(
            {
                "item_id": draft.item_id,
                "question": question.question_text,
                "risk": question.risk_level.value,
                "owner": question.business_owner.value,
                "status": status,
                "evidence_ids": draft.evidence_ids,
                "answer_id": draft.answer_id,
            }
        )

    approval_queue = []
    for review in result.reviews:
        if review.status == ReviewStatus.NEEDS_HUMAN_APPROVAL:
            approval_queue.append(
                {
                    "item_id": review.item_id,
                    "question": question_by_id[review.item_id].question_text,
                    "decision": "approved" if review.item_id in approval_item_ids else "blocked",
                    "reason": review.reason,
                }
            )

    evolution_events = [
        event
        for event in timeline
        if event["event_type"]
        in {
            EventType.EVOLUTION_PROPOSED.value,
            EventType.LESSON_ACCEPTED.value,
            EventType.STRESS_TEST_GENERATED.value,
        }
    ]

    readiness = {
        "ready": len(result.final_pack.included_answer_ids),
        "needs_review": max(0, len(result.questions) - len(result.final_pack.included_answer_ids) - len(blocked_items)),
        "blocked": len(blocked_items),
    }

    return {
        "title": "RFP TrustRoom",
        "case_name": "Acme Financial Services Security RFP",
        "deadline": "48 hours",
        "submission_owner": "Maya Chen, Sales Engineering Lead",
        "mode_label": mode.value.upper(),
        "is_replay": mode == ExecutionMode.REPLAY,
        "readiness": readiness,
        "evidence_coverage": {
            "current": evidence_counter["current"],
            "stale": evidence_counter["stale"],
            "missing": evidence_counter["missing"],
            "conflicting": evidence_counter["conflicting"],
        },
        "approval_queue": approval_queue,
        "risk_flags": [
            "Q-006 stale incident response commitment remains blocked",
            "Q-004 residency wording requires bounded legal language",
            "Q-002 certification evidence requires human approval",
        ],
        "final_pack": result.final_pack,
        "answers": answers,
        "timeline": timeline,
        "evolution_events": evolution_events,
    }
