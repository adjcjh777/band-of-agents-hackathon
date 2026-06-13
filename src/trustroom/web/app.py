from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from trustroom.agents.mock_runner import run_mock_trustroom
from trustroom.models import (
    AnswerDraft,
    ApprovalDecision,
    ApprovalDecisionValue,
    ApprovalValidity,
    EventType,
    ExecutionMode,
    ReviewStatus,
)
from trustroom.sample_loader import load_default_sample_pack, load_replay_events
from trustroom.state_machine import assess_answer_gate


TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
TRACE_ITEM_IDS = ("Q-002", "Q-004", "Q-006")
TRACE_EVENT_TYPES = {
    EventType.TASK_ASSIGNED.value,
    EventType.HANDOFF.value,
    EventType.EVIDENCE_FOUND.value,
    EventType.DRAFT_CREATED.value,
    EventType.REVIEW_DECISION.value,
    EventType.HUMAN_APPROVAL.value,
    EventType.FINAL_PACK_CREATED.value,
}

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
    draft_by_item_id = {draft.item_id: draft for draft in result.drafts}
    included = set(result.final_pack.included_answer_ids)
    blocked_items = set(result.final_pack.blocked_item_ids)
    evidence_counter = Counter(candidate.freshness_label.value for candidate in result.evidence)

    if mode == ExecutionMode.REPLAY:
        timeline = load_replay_events()
    else:
        timeline = [event.model_dump(mode="json") | {"mode_label": "MOCK"} for event in result.events]

    review_by_item_id = {review.item_id: review for review in result.reviews}
    approval_by_item_id = {approval.item_id: approval for approval in result.approvals}
    lineage_by_item_id = {lineage.item_id: lineage for lineage in result.lineage}
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
        lineage = lineage_by_item_id[draft.item_id]
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
                "approval_scope": approval.scope if approval else None,
                "approval_validity": approval.validity.value if approval else None,
                "approval_expires_at_label": approval.expires_at_label if approval else None,
                "approved_evidence_ids": approval.approved_evidence_ids if approval else [],
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
                "lineage_steps": [
                    {
                        "stage": step.stage,
                        "label": step.label,
                        "status": step.status,
                        "object_ids": step.object_ids,
                        "owner": step.owner,
                        "reason": step.reason,
                    }
                    for step in lineage.steps
                ],
                "answer_id": draft.answer_id,
            }
        )

    approval_queue = []
    for review in result.reviews:
        if review.status == ReviewStatus.NEEDS_HUMAN_APPROVAL:
            approval = approval_by_item_id.get(review.item_id)
            approval_valid = _approval_is_valid_for_answer(
                approval,
                draft_by_item_id.get(review.item_id),
            )
            approval_queue.append(
                {
                    "item_id": review.item_id,
                    "question": question_by_id[review.item_id].question_text,
                    "decision": "approved" if approval_valid else "blocked",
                    "owner": question_by_id[review.item_id].business_owner.value,
                    "reviewer": review.reviewer_agent,
                    "decision_id": review.decision_id,
                    "approval_role": approval.reviewer_role if approval else "security policy owner",
                    "approval_reason": approval.reason if approval else "",
                    "approval_scope": approval.scope if approval else "",
                    "approval_validity": approval.validity.value if approval else "missing",
                    "approval_expires_at_label": approval.expires_at_label if approval else "",
                    "approved_evidence_ids": approval.approved_evidence_ids if approval else [],
                    "required_follow_up": review.required_follow_up
                    or (approval.required_follow_up if approval else None),
                    "reason": review.reason,
                    "next_action": _next_action_for_item(
                        item_id=review.item_id,
                        owner=question_by_id[review.item_id].business_owner.value,
                        status="ready" if approval_valid else "blocked",
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
    run_trace = _run_trace_summary(
        timeline=timeline,
        answers=answers,
        approval_queue=approval_queue,
        readiness=readiness,
        total_questions=total_questions,
        mode_label=mode.value.upper(),
        is_replay=mode == ExecutionMode.REPLAY,
    )

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
        "run_trace": run_trace,
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


def _run_trace_summary(
    *,
    timeline: list[dict[str, Any]],
    answers: list[dict[str, Any]],
    approval_queue: list[dict[str, Any]],
    readiness: dict[str, int],
    total_questions: int,
    mode_label: str,
    is_replay: bool,
) -> dict[str, Any]:
    events = [_normalize_trace_event(event) for event in timeline]
    trace_events = [event for event in events if event["event_type"] in TRACE_EVENT_TYPES]
    handoff_events = [event for event in events if event["event_type"] == EventType.HANDOFF.value]
    participants = sorted(
        {
            agent
            for event in trace_events
            for agent in (event["sender"], event["receiver"])
            if agent
        }
    )
    review_loops = [
        event
        for event in events
        if "review loop" in event["payload_summary"].lower()
        or (
            event["sender"] == "compliance-review-agent"
            and event["receiver"] == "evidence-retriever-agent"
        )
    ]
    valid_approvals = sum(1 for item in approval_queue if item["decision"] == "approved")
    boundary = (
        "REPLAY fallback, not live Band; redacted event refs mirror the collaboration path."
        if is_replay
        else "MOCK local run; use replay or verified live evidence for judge-facing claims."
    )

    return {
        "boundary": boundary,
        "proof_points": [
            {
                "label": "Roles",
                "value": str(len(participants)),
                "note": "agent and human handoff participants",
            },
            {
                "label": "Handoffs",
                "value": str(len(handoff_events)),
                "note": "Band-style sender to receiver transitions",
            },
            {
                "label": "Review loops",
                "value": str(len(review_loops)),
                "note": "reviewer challenge before final wording",
            },
            {
                "label": "Valid approvals",
                "value": str(valid_approvals),
                "note": "scoped sample approvals",
            },
            {
                "label": "Final pack",
                "value": f"{readiness['ready']}/{total_questions}",
                "note": f"{readiness['blocked']} blocked item excluded",
            },
            {
                "label": "Mode",
                "value": mode_label,
                "note": "fallback trace, not autonomous live proof" if is_replay else "local deterministic run",
            },
        ],
        "milestones": _business_milestones(events, readiness, total_questions),
        "handoff_chain": _handoff_chain(events),
        "representative_traces": _representative_item_traces(events, answers),
        "blocked_impact_path": _blocked_impact_path(answers),
    }


def _normalize_trace_event(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "event_id": str(event.get("event_id") or event.get("band_message_ref") or ""),
        "sender": str(event.get("sender") or ""),
        "receiver": str(event.get("receiver") or ""),
        "event_type": str(event.get("event_type") or ""),
        "task_state": str(event.get("task_state") or ""),
        "payload_summary": str(event.get("payload_summary") or ""),
        "related_object_ids": [str(object_id) for object_id in event.get("related_object_ids", [])],
        "band_message_ref": str(event.get("band_message_ref") or event.get("event_id") or ""),
        "mode_label": str(event.get("mode_label") or ""),
    }


def _business_milestones(
    events: list[dict[str, Any]],
    readiness: dict[str, int],
    total_questions: int,
) -> list[dict[str, Any]]:
    return [
        {
            "label": "Intake",
            "status": "passed",
            "detail": "Sample RFP, questionnaire and knowledge pack entered the room.",
            "refs": _event_refs(events, task_state="intake"),
        },
        {
            "label": "Triage",
            "status": "passed",
            "detail": "Orchestrator assigned owners, risk and evidence needs for 8 items.",
            "refs": _event_refs(events, event_type=EventType.TASK_ASSIGNED.value, task_state="triage"),
        },
        {
            "label": "Evidence",
            "status": "passed",
            "detail": "Retriever surfaced current, stale, missing and conflicting evidence.",
            "refs": _event_refs(events, task_state="evidence")[:3],
        },
        {
            "label": "Draft",
            "status": "passed",
            "detail": "Answer drafter created customer-safe drafts with evidence refs.",
            "refs": _event_refs(events, event_type=EventType.DRAFT_CREATED.value)[:2],
        },
        {
            "label": "Review loop",
            "status": "review",
            "detail": "Q-004 was challenged, sent back for clarification and rewritten.",
            "refs": _event_refs(events, object_id="Q-004", text_contains="review")[:3],
        },
        {
            "label": "Human approval",
            "status": "review",
            "detail": "Q-002 and Q-004 have scoped approvals; Q-006 has no valid approval.",
            "refs": _event_refs(events, task_state="approval")[:3],
        },
        {
            "label": "Final pack",
            "status": "blocked" if readiness["blocked"] else "passed",
            "detail": f"{readiness['ready']} of {total_questions} answers included; Q-006 stays excluded.",
            "refs": _event_refs(events, event_type=EventType.FINAL_PACK_CREATED.value),
        },
    ]


def _handoff_chain(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selectors = [
        ("Assign", lambda event: event["event_type"] == EventType.TASK_ASSIGNED.value),
        (
            "Decompose",
            lambda event: event["sender"] == "requirement-decomposer-agent"
            and event["receiver"] == "evidence-retriever-agent",
        ),
        (
            "Retrieve Evidence",
            lambda event: event["sender"] == "evidence-retriever-agent"
            and event["receiver"] == "answer-drafter-agent",
        ),
        (
            "Draft",
            lambda event: event["sender"] == "answer-drafter-agent"
            and event["receiver"] == "compliance-review-agent",
        ),
        (
            "Review Loop",
            lambda event: event["sender"] == "compliance-review-agent"
            and event["receiver"] == "evidence-retriever-agent",
        ),
        ("Human Approval", lambda event: event["event_type"] == EventType.HUMAN_APPROVAL.value),
        ("Final Pack", lambda event: event["event_type"] == EventType.FINAL_PACK_CREATED.value),
    ]
    chain = []
    for label, predicate in selectors:
        event = next((candidate for candidate in events if predicate(candidate)), None)
        if event is None:
            continue
        chain.append(_trace_card(event, label=label))
    return chain


def _representative_item_traces(
    events: list[dict[str, Any]],
    answers: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    answer_by_item_id = {answer["item_id"]: answer for answer in answers}
    labels = {
        "Q-002": "SOC 2 approval path",
        "Q-004": "Region review loop",
        "Q-006": "Incident blocker path",
    }
    outcomes = {
        "Q-002": "Valid scoped SME approval; included with bridge-letter boundary.",
        "Q-004": "Reviewer challenged overbroad language; legal approved bounded pilot wording.",
        "Q-006": "Stale/conflicting evidence plus no valid approval; final pack excluded.",
    }
    traces = []
    for item_id in TRACE_ITEM_IDS:
        answer = answer_by_item_id[item_id]
        object_ids = {
            item_id,
            answer["answer_id"],
            *answer["evidence_ids"],
            *(trace_id for trace_id in answer["trace_ids"] if trace_id.startswith(("REV-", "APP-"))),
        }
        item_events = [
            _trace_card(event)
            for event in events
            if object_ids.intersection(event["related_object_ids"])
        ]
        if item_id == "Q-004":
            item_events = _prioritize_trace_cards(item_events, ("EVT-008", "EVT-009", "EVT-011", "EVT-014"))
        elif item_id == "Q-006":
            item_events = _prioritize_trace_cards(item_events, ("EVT-005", "EVT-012", "EVT-013", "EVT-014"))
        traces.append(
            {
                "item_id": item_id,
                "label": labels[item_id],
                "status": answer["final_pack_status"],
                "tone": "blocked" if answer["status"] == "blocked" else "ready",
                "outcome": outcomes[item_id],
                "events": item_events[:5],
            }
        )
    return traces


def _blocked_impact_path(answers: list[dict[str, Any]]) -> list[str]:
    q6 = next(answer for answer in answers if answer["item_id"] == "Q-006")
    return [
        "stale/conflicting incident evidence",
        q6["review_status"],
        "no valid human approval",
        "final pack excluded",
        q6["next_action"],
    ]


def _trace_card(event: dict[str, Any], *, label: str | None = None) -> dict[str, Any]:
    event_type = event["event_type"]
    tone = "handoff"
    if event_type == EventType.REVIEW_DECISION.value or "review loop" in event["payload_summary"].lower():
        tone = "review"
    elif event_type == EventType.HUMAN_APPROVAL.value:
        tone = "human"
    elif event_type == EventType.FINAL_PACK_CREATED.value:
        tone = "final"
    if "blocked" in event["payload_summary"].lower():
        tone = "blocked"
    return {
        "label": label or _trace_label(event),
        "sender": event["sender"],
        "receiver": event["receiver"],
        "event_type": event_type,
        "task_state": event["task_state"],
        "summary": event["payload_summary"],
        "refs": [event["event_id"], event["band_message_ref"], *event["related_object_ids"]],
        "tone": tone,
    }


def _trace_label(event: dict[str, Any]) -> str:
    if event["event_type"] == EventType.HANDOFF.value:
        return "Handoff"
    if event["event_type"] == EventType.HUMAN_APPROVAL.value:
        return "Human gate"
    if event["event_type"] == EventType.FINAL_PACK_CREATED.value:
        return "Final pack"
    return event["event_type"].replace("_", " ").title()


def _event_refs(
    events: list[dict[str, Any]],
    *,
    event_type: str | None = None,
    task_state: str | None = None,
    object_id: str | None = None,
    text_contains: str | None = None,
) -> list[str]:
    refs = []
    for event in events:
        if event_type is not None and event["event_type"] != event_type:
            continue
        if task_state is not None and event["task_state"] != task_state:
            continue
        if object_id is not None and object_id not in event["related_object_ids"]:
            continue
        if text_contains is not None and text_contains not in event["payload_summary"].lower():
            continue
        refs.append(event["event_id"])
    return refs


def _prioritize_trace_cards(
    cards: list[dict[str, Any]],
    preferred_refs: tuple[str, ...],
) -> list[dict[str, Any]]:
    by_ref = {card["refs"][0]: card for card in cards if card["refs"]}
    prioritized = [by_ref[ref] for ref in preferred_refs if ref in by_ref]
    rest = [card for card in cards if card not in prioritized]
    return prioritized + rest


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


def _approval_is_valid_for_answer(
    approval: ApprovalDecision | None,
    draft: AnswerDraft | None,
) -> bool:
    if approval is None:
        return False
    return (
        approval.decision == ApprovalDecisionValue.APPROVE
        and approval.validity == ApprovalValidity.VALID
        and (
            approval.answer_id is None
            or draft is not None
            and approval.answer_id == draft.answer_id
        )
    )


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
