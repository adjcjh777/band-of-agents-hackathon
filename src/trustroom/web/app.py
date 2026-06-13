from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from trustroom.agents.mock_runner import run_mock_trustroom
from trustroom.models import EventType, ExecutionMode, ReviewStatus
from trustroom.sample_loader import load_default_sample_pack, load_replay_events
from trustroom.state_machine import assess_answer_gate


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
    sample = load_default_sample_pack()
    result = run_mock_trustroom(sample)
    case = sample.case
    question_by_id = {question.item_id: question for question in result.questions}
    included = set(result.final_pack.included_answer_ids)
    blocked_items = set(result.final_pack.blocked_item_ids)
    approval_item_ids = {approval.item_id for approval in result.approvals}
    evidence_counter = Counter(candidate.freshness_label.value for candidate in result.evidence)

    if mode == ExecutionMode.REPLAY:
        timeline = load_replay_events()
    else:
        timeline = [event.model_dump(mode="json") | {"mode_label": "MOCK"} for event in result.events]

    review_by_item_id = {review.item_id: review for review in result.reviews}
    approval_by_item_id = {approval.item_id: approval for approval in result.approvals}
    evidence_by_item_id: dict[str, list[Any]] = defaultdict(list)
    for candidate in result.evidence:
        evidence_by_item_id[candidate.item_id].append(candidate)

    answers = []
    for draft in sorted(result.drafts, key=lambda item: item.item_id):
        question = question_by_id[draft.item_id]
        review = review_by_item_id.get(draft.item_id)
        approval = approval_by_item_id.get(draft.item_id)
        item_evidence = evidence_by_item_id[draft.item_id]
        gate = assess_answer_gate(
            question,
            draft,
            result.evidence,
            review_decision=review,
            approval_decision=approval,
        )
        if draft.answer_id in included:
            status = "ready"
        elif draft.item_id in blocked_items:
            status = "blocked"
        else:
            status = "needs review"
        freshness = sorted({candidate.freshness_label.value for candidate in item_evidence})
        trace_ids = [question.source_ref, *draft.evidence_ids]
        if review is not None:
            trace_ids.append(review.decision_id)
        if approval is not None:
            trace_ids.append(approval.decision_id)
        evidence_cards = [
            {
                "evidence_id": candidate.evidence_id,
                "title": candidate.source_title,
                "snippet": candidate.snippet,
                "freshness": candidate.freshness_label.value,
                "confidence": f"{candidate.confidence:.0%}",
                "action": _evidence_action(candidate.freshness_label.value),
            }
            for candidate in item_evidence
        ]
        final_pack_status = "included" if status == "ready" else "excluded"
        answers.append(
            {
                "item_id": draft.item_id,
                "question": question.question_text,
                "source_ref": question.source_ref,
                "category": question.category.value,
                "risk": question.risk_level.value,
                "owner": question.business_owner.value,
                "required_evidence_type": question.required_evidence_type,
                "status": status,
                "draft_text": draft.draft_text,
                "evidence_ids": draft.evidence_ids,
                "evidence_cards": evidence_cards,
                "freshness": freshness,
                "review_status": review.status.value if review else "not_started",
                "review_reason": review.reason if review else "Review has not started.",
                "review_decision_id": review.decision_id if review else None,
                "approval_decision": approval.decision.value if approval else None,
                "approval_role": approval.reviewer_role if approval else None,
                "approval_decision_id": approval.decision_id if approval else None,
                "approval_reason": approval.reason if approval else None,
                "final_pack_status": final_pack_status,
                "gate_reasons": gate.reasons,
                "final_pack_reason": _final_pack_reason(
                    status=status,
                    risk=question.risk_level.value,
                    approval_role=approval.reviewer_role if approval else None,
                    approval_reason=approval.reason if approval else None,
                    gate_reasons=gate.reasons,
                    freshness=freshness,
                ),
                "next_action": _next_action_for_item(
                    item_id=draft.item_id,
                    owner=question.business_owner.value,
                    status=status,
                    freshness=freshness,
                    review_reason=review.reason if review else "",
                ),
                "trace_ids": trace_ids,
                "answer_id": draft.answer_id,
            }
        )

    approval_queue = []
    for review in result.reviews:
        if review.status == ReviewStatus.NEEDS_HUMAN_APPROVAL:
            approval = approval_by_item_id.get(review.item_id)
            approval_queue.append(
                {
                    "item_id": review.item_id,
                    "question": question_by_id[review.item_id].question_text,
                    "decision": "approved" if review.item_id in approval_item_ids else "blocked",
                    "owner": question_by_id[review.item_id].business_owner.value,
                    "reviewer": review.reviewer_agent,
                    "decision_id": review.decision_id,
                    "approval_role": approval.reviewer_role if approval else "security policy owner",
                    "approval_reason": approval.reason if approval else "",
                    "required_follow_up": review.required_follow_up
                    or (approval.required_follow_up if approval else None),
                    "reason": review.reason,
                    "next_action": _next_action_for_item(
                        item_id=review.item_id,
                        owner=question_by_id[review.item_id].business_owner.value,
                        status="ready" if review.item_id in approval_item_ids else "blocked",
                        freshness=[
                            candidate.freshness_label.value
                            for candidate in evidence_by_item_id[review.item_id]
                        ],
                        review_reason=review.reason,
                    ),
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
    total_questions = len(result.questions)
    owner_summary = _owner_summary(answers)
    next_actions = [answer for answer in answers if answer["status"] != "ready"]
    risk_register = _risk_register(answers)
    decision_state = _decision_state(readiness=readiness, total_questions=total_questions, next_actions=next_actions)

    return {
        "title": "RFP TrustRoom",
        "case_name": case.case_name,
        "customer_profile": case.customer_profile,
        "business_goal": case.business_goal,
        "material_types": [material.value.replace("_", " ") for material in case.material_types],
        "deadline": case.deadline_label,
        "internal_review_cutoff": "approve blockers before customer send",
        "submission_owner": case.submission_owner,
        "sample_boundary": "Sample evidence is fictional and redacted; it demonstrates review traceability, not a formal audit.",
        "mode_label": mode.value.upper(),
        "is_replay": mode == ExecutionMode.REPLAY,
        "decision_state": decision_state,
        "readiness": readiness,
        "total_questions": total_questions,
        "evidence_coverage": {
            "current": evidence_counter["current"],
            "stale": evidence_counter["stale"],
            "missing": evidence_counter["missing"],
            "conflicting": evidence_counter["conflicting"],
            "covered_items": sum(1 for question in result.questions if evidence_by_item_id[question.item_id]),
            "total_evidence": len(result.evidence),
        },
        "approval_queue": approval_queue,
        "risk_flags": [
            risk["next_action"]
            for risk in risk_register[:3]
        ],
        "next_actions": next_actions,
        "owner_summary": owner_summary,
        "risk_register": risk_register,
        "final_pack": result.final_pack,
        "answers": answers,
        "timeline": timeline,
        "evolution_events": evolution_events,
    }


def _decision_state(
    *,
    readiness: dict[str, int],
    total_questions: int,
    next_actions: list[dict[str, Any]],
) -> dict[str, str]:
    if readiness["blocked"]:
        primary_action = next_actions[0]["next_action"] if next_actions else "Resolve blockers before sending."
        return {
            "label": "Draft pack ready with exclusions",
            "tone": "blocked",
            "summary": f"{readiness['ready']} of {total_questions} answers can enter the pack; {readiness['blocked']} blocker must stay out.",
            "primary_action": primary_action,
        }
    if readiness["needs_review"]:
        return {
            "label": "Needs reviewer pass",
            "tone": "review",
            "summary": f"{readiness['needs_review']} answers need review before customer delivery.",
            "primary_action": "Finish reviewer decisions, then regenerate the final pack.",
        }
    return {
        "label": "Ready to submit",
        "tone": "ready",
        "summary": f"All {total_questions} answers are approved for the current final pack.",
        "primary_action": "Export the answer pack with evidence index and approval trail.",
    }


def _next_action_for_item(
    *,
    item_id: str,
    owner: str,
    status: str,
    freshness: list[str],
    review_reason: str,
) -> str:
    if status == "ready":
        return "Keep evidence attached and preserve approval trail in the final pack."
    if item_id == "Q-006":
        return "Policy owner must confirm incident response wording before this answer can be sent."
    if "missing" in freshness:
        return f"{owner.title()} owner must replace the explicit evidence gap with approved customer-safe wording."
    if "stale" in freshness or "conflicting" in freshness:
        return f"{owner.title()} owner must refresh stale or conflicting evidence before final pack inclusion."
    if review_reason:
        return review_reason
    return f"{owner.title()} owner must resolve the blocker before submission."


def _final_pack_reason(
    *,
    status: str,
    risk: str,
    approval_role: str | None,
    approval_reason: str | None,
    gate_reasons: list[str],
    freshness: list[str],
) -> str:
    if status == "blocked":
        return "; ".join(gate_reasons) if gate_reasons else "Blocked item is excluded from the final pack."
    if approval_role and approval_reason:
        return f"Included after {approval_role} approval: {approval_reason}"
    if risk == "high":
        return "High-risk answer requires an approval record before customer delivery."
    if set(freshness) <= {"current"}:
        return "Included because current evidence supports the customer-safe draft."
    return "Included with reviewer-approved boundaries and attached evidence."


def _evidence_action(freshness: str) -> str:
    if freshness == "current":
        return "Attach to customer-safe answer."
    if freshness == "missing":
        return "Use only as an explicit gap note until approved wording exists."
    if freshness == "stale":
        return "Refresh with the policy owner before quoting a commitment."
    if freshness == "conflicting":
        return "Resolve commercial or policy conflict before customer use."
    return "Review before customer use."


def _owner_summary(answers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for answer in answers:
        owner = answer["owner"]
        record = grouped.setdefault(
            owner,
            {
                "owner": owner,
                "ready": 0,
                "needs_review": 0,
                "blocked": 0,
                "next_item": "",
            },
        )
        key = "needs_review" if answer["status"] == "needs review" else answer["status"]
        record[key] += 1
        if answer["status"] != "ready" and not record["next_item"]:
            record["next_item"] = answer["item_id"]
    return sorted(grouped.values(), key=lambda item: item["owner"])


def _risk_register(answers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    risks: list[dict[str, Any]] = []
    for answer in answers:
        freshness = set(answer["freshness"])
        if answer["risk"] == "high" or freshness.intersection({"stale", "missing", "conflicting"}):
            risks.append(
                {
                    "item_id": answer["item_id"],
                    "owner": answer["owner"],
                    "risk": answer["risk"],
                    "status": answer["status"],
                    "freshness": ", ".join(answer["freshness"]) or "none",
                    "review_status": answer["review_status"],
                    "next_action": answer["next_action"],
                }
            )
    return risks
