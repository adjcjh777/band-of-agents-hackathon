from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from trustroom.agents.mock_runner import run_mock_trustroom
from trustroom.customer_export import build_customer_export
from trustroom.models import (
    AnswerDraft,
    ApprovalDecision,
    ApprovalDecisionValue,
    ApprovalValidity,
    EvidenceFreshness,
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
    EventType.OWNER_REVIEW_SUGGESTION.value,
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


@app.get("/api/runs/demo/customer-export")
def demo_customer_export_api(include_review_appendix: bool = False) -> JSONResponse:
    return _customer_export_response(
        mode=ExecutionMode.MOCK,
        include_review_appendix=include_review_appendix,
    )


@app.get("/api/runs/demo/replay/customer-export")
def replay_customer_export_api(include_review_appendix: bool = False) -> JSONResponse:
    return _customer_export_response(
        mode=ExecutionMode.REPLAY,
        include_review_appendix=include_review_appendix,
    )


@app.get("/runs/demo/customer-export")
def demo_customer_export_page(request: Request, include_review_appendix: bool = False):
    return _render_customer_export(
        request,
        mode=ExecutionMode.MOCK,
        include_review_appendix=include_review_appendix,
    )


@app.get("/runs/demo/replay/customer-export")
def replay_customer_export_page(request: Request, include_review_appendix: bool = False):
    return _render_customer_export(
        request,
        mode=ExecutionMode.REPLAY,
        include_review_appendix=include_review_appendix,
    )


def _render_run(request: Request, *, mode: ExecutionMode):
    context = _dashboard_context(mode=mode)
    return templates.TemplateResponse(request, "run.html", context)


def _customer_export_response(
    *,
    mode: ExecutionMode,
    include_review_appendix: bool,
) -> JSONResponse:
    export = _customer_export_for_mode(
        mode=mode,
        include_review_appendix=include_review_appendix,
    )
    return JSONResponse(export.model_dump(mode="json"))


def _render_customer_export(
    request: Request,
    *,
    mode: ExecutionMode,
    include_review_appendix: bool,
):
    export = _customer_export_for_mode(
        mode=mode,
        include_review_appendix=include_review_appendix,
    )
    return templates.TemplateResponse(
        request,
        "customer_export.html",
        {
            "title": "RFP TrustRoom · Customer Export",
            "export": export,
            "mode_label": mode.value.upper(),
            "is_replay": mode == ExecutionMode.REPLAY,
            "dashboard_path": "/runs/demo/replay" if mode == ExecutionMode.REPLAY else "/runs/demo",
            "appendix_toggle_path": _customer_export_path(
                mode=mode,
                include_review_appendix=not include_review_appendix,
            ),
            "api_path": _customer_export_api_path(
                mode=mode,
                include_review_appendix=include_review_appendix,
            ),
            "include_review_appendix": include_review_appendix,
            "sample_boundary": "Sample evidence is fictional and redacted; it demonstrates review traceability, not a formal audit.",
        },
    )


def _customer_export_for_mode(
    *,
    mode: ExecutionMode,
    include_review_appendix: bool,
):
    result = _mock_result_for_mode(mode=mode)
    return build_customer_export(
        result,
        include_review_appendix=include_review_appendix,
    )


def _mock_result_for_mode(*, mode: ExecutionMode):
    sample = load_default_sample_pack()
    result = run_mock_trustroom(sample)
    if mode != ExecutionMode.REPLAY:
        return result
    return result.model_copy(
        update={
            "run": result.run.model_copy(update={"mode": ExecutionMode.REPLAY}),
            "final_pack": result.final_pack.model_copy(update={"mode": ExecutionMode.REPLAY}),
        }
    )


def _dashboard_context(*, mode: ExecutionMode) -> dict[str, Any]:
    sample = load_default_sample_pack()
    result = _mock_result_for_mode(mode=mode)
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
    suggestion_by_item_id = {
        suggestion.item_id: suggestion
        for suggestion in result.owner_review_suggestions
    }
    lineage_by_item_id = {lineage.item_id: lineage for lineage in result.lineage}
    evidence_by_item_id: dict[str, list[Any]] = defaultdict(list)
    for candidate in result.evidence:
        evidence_by_item_id[candidate.item_id].append(candidate)

    answers = []
    for draft in sorted(result.drafts, key=lambda item: item.item_id):
        question = question_by_id[draft.item_id]
        review = review_by_item_id.get(draft.item_id)
        approval = approval_by_item_id.get(draft.item_id)
        suggestion = suggestion_by_item_id.get(draft.item_id)
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
        if suggestion is not None:
            trace_ids.append(suggestion.suggestion_id)
        evidence_cards = [
            {
                "evidence_id": candidate.evidence_id,
                "title": candidate.source_title,
                "snippet": candidate.snippet,
                "freshness": candidate.freshness_label.value,
                "freshness_marked_by": candidate.freshness_marked_by,
                "freshness_marked_at": candidate.freshness_marked_at.strftime("%Y-%m-%dT%H:%MZ"),
                "confidence": f"{candidate.confidence:.0%}",
                "action": _evidence_action(candidate.freshness_label.value),
            }
            for candidate in item_evidence
        ]
        final_pack_status = "included" if status == "ready" else "excluded"
        final_pack_reason = _final_pack_reason(
            status=status,
            risk=question.risk_level.value,
            approval_role=approval.reviewer_role if approval else None,
            approval_reason=approval.reason if approval else None,
            gate_reasons=gate.reasons,
            freshness=freshness,
            freshness_rollup=gate.freshness_rollup.value,
        )
        lineage = lineage_by_item_id[draft.item_id]
        suggestion_card = (
            {
                "suggestion_id": suggestion.suggestion_id,
                "status": suggestion.status.value,
                "proposed_by": suggestion.proposed_by,
                "owner_role": suggestion.owner_role,
                "suggested_evidence_ids": suggestion.suggested_evidence_ids,
                "replaces_evidence_ids": suggestion.replaces_evidence_ids,
                "reason": suggestion.reason,
                "scope": suggestion.scope,
                "created_at": suggestion.created_at.strftime("%Y-%m-%dT%H:%MZ"),
            }
            if suggestion is not None
            else None
        )
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
                "freshness_rollup": gate.freshness_rollup.value,
                "review_status": review.status.value if review else "not_started",
                "review_reason": review.reason if review else "Review has not started.",
                "review_decision_id": review.decision_id if review else None,
                "approval_decision": approval.decision.value if approval else None,
                "approval_role": approval.reviewer_role if approval else None,
                "approval_owner": _approval_owner_label(approval.reviewer_role) if approval else None,
                "approval_decision_id": approval.decision_id if approval else None,
                "approval_reason": approval.reason if approval else None,
                "approval_scope": approval.scope if approval else None,
                "approval_validity": approval.validity.value if approval else None,
                "approval_expires_at_label": approval.expires_at_label if approval else None,
                "approved_evidence_ids": approval.approved_evidence_ids if approval else [],
                "owner_review_suggestion": suggestion_card,
                "visibility_mode": result.final_pack.visibility_mode.value,
                "final_pack_status": final_pack_status,
                "gate_reasons": gate.reasons,
                "final_pack_reason": final_pack_reason,
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
                        "status": _lineage_status_label(step.status),
                        "object_ids": step.object_ids,
                        "owner": step.owner,
                        "reason": _lineage_reason_label(step.reason),
                    }
                    for step in lineage.steps
                ],
                "business_lineage": _business_lineage_summary(
                    question=question,
                    evidence=item_evidence,
                    review=review,
                    approval=approval,
                    draft=draft,
                    status=status,
                    final_pack_status=final_pack_status,
                    final_pack_reason=final_pack_reason,
                    gate_reasons=gate.reasons,
                    freshness_rollup=gate.freshness_rollup.value,
                ),
                "answer_id": draft.answer_id,
            }
        )

    approval_queue = []
    for review in result.reviews:
        if review.status == ReviewStatus.NEEDS_HUMAN_APPROVAL:
            approval = approval_by_item_id.get(review.item_id)
            suggestion = suggestion_by_item_id.get(review.item_id)
            approval_role = approval.reviewer_role if approval else "security policy owner"
            approval_scope = approval.scope if approval else ""
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
                    "approval_role": approval_role,
                    "approval_owner": _approval_owner_label(approval_role),
                    "approval_reason": approval.reason if approval else "",
                    "approval_scope": approval_scope,
                    "approval_validity": approval.validity.value if approval else "missing",
                    "approval_expires_at_label": approval.expires_at_label if approval else "",
                    "approved_evidence_ids": approval.approved_evidence_ids if approval else [],
                    "allowed_wording": _approval_allowed_wording(
                        item_id=review.item_id,
                        approval_valid=approval_valid,
                        approval_scope=approval_scope,
                    ),
                    "prohibited_wording": _approval_prohibited_wording(review.item_id),
                    "context_boundary": (
                        "Approved evidence refs are reviewer context, not a machine-enforced evidence-set gate."
                    ),
                    "owner_review_suggestion": (
                        {
                            "suggestion_id": suggestion.suggestion_id,
                            "status": suggestion.status.value,
                            "proposed_by": suggestion.proposed_by,
                            "owner_role": suggestion.owner_role,
                            "suggested_evidence_ids": suggestion.suggested_evidence_ids,
                            "replaces_evidence_ids": suggestion.replaces_evidence_ids,
                            "reason": suggestion.reason,
                            "scope": suggestion.scope,
                        }
                        if suggestion is not None
                        else None
                    ),
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
    responsibility_queue = _responsibility_queue(answers=answers, approval_queue=approval_queue)
    decision_state = _decision_state(readiness=readiness, total_questions=total_questions, next_actions=next_actions)
    final_pack_decision = _final_pack_decision(answers=answers, readiness=readiness, total_questions=total_questions)
    q006_buyer_safe_story = _q006_buyer_safe_story(
        answers=answers,
        owner_review_suggestions=[
            {
                "suggestion_id": suggestion.suggestion_id,
                "item_id": suggestion.item_id,
                "status": suggestion.status.value,
                "proposed_by": suggestion.proposed_by,
                "owner_role": suggestion.owner_role,
                "suggested_evidence_ids": suggestion.suggested_evidence_ids,
                "replaces_evidence_ids": suggestion.replaces_evidence_ids,
                "reason": suggestion.reason,
                "scope": suggestion.scope,
            }
            for suggestion in result.owner_review_suggestions
        ],
    )
    run_trace = _run_trace_summary(
        timeline=timeline,
        answers=answers,
        approval_queue=approval_queue,
        owner_review_suggestions=[
            {
                "suggestion_id": suggestion.suggestion_id,
                "item_id": suggestion.item_id,
                "status": suggestion.status.value,
                "proposed_by": suggestion.proposed_by,
                "owner_role": suggestion.owner_role,
                "suggested_evidence_ids": suggestion.suggested_evidence_ids,
                "replaces_evidence_ids": suggestion.replaces_evidence_ids,
                "reason": suggestion.reason,
                "scope": suggestion.scope,
            }
            for suggestion in result.owner_review_suggestions
        ],
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
        "band_evidence_mode": {
            "label": "REST smoke verified",
            "note": "Replay fallback · autonomous pending",
        },
        "readiness": readiness,
        "total_questions": total_questions,
        "evidence_coverage": {
            "current": evidence_counter["current"],
            "stale": evidence_counter["stale"],
            "missing": evidence_counter["missing"],
            "conflicting": evidence_counter["conflicting"],
            "unknown": evidence_counter["unknown"],
            "covered_items": sum(1 for question in result.questions if evidence_by_item_id[question.item_id]),
            "total_evidence": len(result.evidence),
        },
        "approval_queue": approval_queue,
        "risk_flags": [
            risk["next_action"]
            for risk in risk_register[:3]
        ],
        "responsibility_queue": responsibility_queue,
        "next_actions": next_actions,
        "owner_summary": owner_summary,
        "risk_register": risk_register,
        "final_pack": result.final_pack,
        "final_pack_decision": final_pack_decision,
        "q006_buyer_safe_story": q006_buyer_safe_story,
        "review_appendix_visibility_mode": result.final_pack.visibility_mode.value,
        "customer_export_path": _customer_export_path(
            mode=mode,
            include_review_appendix=False,
        ),
        "customer_export_appendix_path": _customer_export_path(
            mode=mode,
            include_review_appendix=True,
        ),
        "customer_export_api_path": _customer_export_api_path(
            mode=mode,
            include_review_appendix=True,
        ),
        "owner_review_suggestions": [
            {
                "suggestion_id": suggestion.suggestion_id,
                "item_id": suggestion.item_id,
                "status": suggestion.status.value,
                "proposed_by": suggestion.proposed_by,
                "owner_role": suggestion.owner_role,
                "suggested_evidence_ids": suggestion.suggested_evidence_ids,
                "replaces_evidence_ids": suggestion.replaces_evidence_ids,
                "reason": suggestion.reason,
                "scope": suggestion.scope,
                "created_at": suggestion.created_at.strftime("%Y-%m-%dT%H:%MZ"),
            }
            for suggestion in result.owner_review_suggestions
        ],
        "answers": answers,
        "run_trace": run_trace,
        "timeline": timeline,
        "evolution_events": evolution_events,
    }


def _final_pack_decision(
    *,
    answers: list[dict[str, Any]],
    readiness: dict[str, int],
    total_questions: int,
) -> dict[str, Any]:
    sendable = [answer for answer in answers if answer["final_pack_status"] == "included"]
    held = [answer for answer in answers if answer["final_pack_status"] != "included"]
    held_items = [
        {
            "item_id": answer["item_id"],
            "owner": answer["owner"],
            "reason": answer["final_pack_reason"],
            "next_action": answer["next_action"],
        }
        for answer in held
    ]
    return {
        "headline": f"{len(sendable)}/{total_questions} answers enter the customer export",
        "sendable_items": [answer["item_id"] for answer in sendable],
        "held_items": held_items,
        "held_count": len(held),
        "blocked_count": readiness["blocked"],
        "appendix_boundary": "Customer Export contains included answers only; blocked items stay in the review appendix until a human owner decision.",
        "next_owner_action": held_items[0]["next_action"] if held_items else "No blocked owner action remains.",
    }


def _customer_export_path(*, mode: ExecutionMode, include_review_appendix: bool) -> str:
    path = "/runs/demo/replay/customer-export" if mode == ExecutionMode.REPLAY else "/runs/demo/customer-export"
    if include_review_appendix:
        return f"{path}?include_review_appendix=true"
    return path


def _customer_export_api_path(*, mode: ExecutionMode, include_review_appendix: bool) -> str:
    path = "/api/runs/demo/replay/customer-export" if mode == ExecutionMode.REPLAY else "/api/runs/demo/customer-export"
    if include_review_appendix:
        return f"{path}?include_review_appendix=true"
    return path


def _decision_state(
    *,
    readiness: dict[str, int],
    total_questions: int,
    next_actions: list[dict[str, Any]],
) -> dict[str, str]:
    if readiness["blocked"]:
        primary_action = "Q-006 owner review required." if next_actions else "Resolve blockers before sending."
        return {
            "label": "Draft pack ready with exclusions",
            "tone": "blocked",
            "summary": f"{readiness['ready']}/{total_questions} ready · {readiness['blocked']} blocked outside.",
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
    owner_review_suggestions: list[dict[str, Any]],
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
        if event["event_type"] == EventType.HANDOFF.value
        and event["sender"] == "compliance-review-agent"
        and event["receiver"] == "evidence-retriever-agent"
    ]
    valid_approvals = sum(1 for item in approval_queue if item["decision"] == "approved")
    boundary = (
        "REPLAY fallback, not live Band."
        if is_replay
        else "MOCK local run."
    )

    return {
        "boundary": boundary,
        "proof_points": [
            {
                "label": "Roles",
                "value": str(len(participants)),
                "note": "participants",
            },
            {
                "label": "Handoffs",
                "value": str(len(handoff_events)),
                "note": "sender → receiver",
            },
            {
                "label": "Review loops",
                "value": str(len(review_loops)),
                "note": "challenge loop",
            },
            {
                "label": "Valid approvals",
                "value": str(valid_approvals),
                "note": "scoped",
            },
            {
                "label": "Final pack",
                "value": f"{readiness['ready']}/{total_questions}",
                "note": f"{readiness['blocked']} excluded",
            },
            {
                "label": "Mode",
                "value": mode_label,
                "note": "fallback" if is_replay else "local",
            },
        ],
        "role_map": _agent_role_map(),
        "milestones": _business_milestones(events, readiness, total_questions),
        "handoff_chain": _handoff_chain(events),
        "representative_traces": _representative_item_traces(events, answers, owner_review_suggestions),
        "blocked_impact_path": _blocked_impact_path(answers, owner_review_suggestions),
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


def _agent_role_map() -> list[dict[str, str]]:
    return [
        {
            "role": "Orchestrator",
            "kind": "workflow coordinator",
            "actor": "automated workflow role",
            "responsibility": "Keeps the room state, routes handoffs and assembles the final pack decision.",
        },
        {
            "role": "Decomposer",
            "kind": "task splitter",
            "actor": "automated workflow role",
            "responsibility": "Breaks the questionnaire into answer tasks with owner and risk context.",
        },
        {
            "role": "Retriever",
            "kind": "evidence finder",
            "actor": "automated workflow role",
            "responsibility": "Attaches approved evidence refs and labels freshness before drafting.",
        },
        {
            "role": "Drafter",
            "kind": "answer writer",
            "actor": "automated workflow role",
            "responsibility": "Writes bounded answer copy that stays tied to evidence and review limits.",
        },
        {
            "role": "Reviewer",
            "kind": "risk challenger",
            "actor": "automated workflow role",
            "responsibility": "Challenges risky wording, requests clarification and blocks unsafe commitments.",
        },
        {
            "role": "Human approver",
            "kind": "approval gate",
            "actor": "human decision role",
            "responsibility": (
                "Approves scoped commitments; SME, legal and security policy approvals are represented as "
                "sample human gates, not autonomous agents."
            ),
        },
    ]


def _business_milestones(
    events: list[dict[str, Any]],
    readiness: dict[str, int],
    total_questions: int,
) -> list[dict[str, Any]]:
    return [
        {
            "label": "Intake",
            "status": "passed",
            "detail": "RFP entered the room.",
            "refs": _event_refs(events, task_state="intake"),
        },
        {
            "label": "Triage",
            "status": "passed",
            "detail": "Owners and risk assigned.",
            "refs": _event_refs(events, event_type=EventType.TASK_ASSIGNED.value, task_state="triage"),
        },
        {
            "label": "Evidence",
            "status": "passed",
            "detail": "Freshness labeled.",
            "refs": _event_refs(events, task_state="evidence")[:3],
        },
        {
            "label": "Draft",
            "status": "passed",
            "detail": "Drafts linked to refs.",
            "refs": _event_refs(events, event_type=EventType.DRAFT_CREATED.value)[:2],
        },
        {
            "label": "Review loop",
            "status": "review",
            "detail": "Q-004 challenged.",
            "refs": _event_refs(events, object_id="Q-004", text_contains="review")[:3],
        },
        {
            "label": "Human approval",
            "status": "review",
            "detail": "Q-002/Q-004 approved.",
            "refs": _event_refs(events, task_state="approval")[:3],
        },
        {
            "label": "Final pack",
            "status": "blocked" if readiness["blocked"] else "passed",
            "detail": f"{readiness['ready']}/{total_questions} included.",
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
    owner_review_suggestions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    answer_by_item_id = {answer["item_id"]: answer for answer in answers}
    suggestion_by_item_id = {
        suggestion["item_id"]: suggestion
        for suggestion in owner_review_suggestions
    }
    labels = {
        "Q-002": "SOC 2 approval path",
        "Q-004": "Region review loop",
        "Q-006": "Incident blocker path",
    }
    outcomes = {
        "Q-002": "Scoped SME approval.",
        "Q-004": "Reviewer loop, legal approval.",
        "Q-006": "Stale/conflicting; excluded.",
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
        if answer["approval_decision_id"]:
            item_events.append(_approval_trace_card(answer))
        suggestion = suggestion_by_item_id.get(item_id)
        if suggestion is not None:
            item_events.append(_owner_review_suggestion_trace_card(suggestion))
        if item_id == "Q-004":
            item_events = _prioritize_trace_cards(
                item_events,
                ("EVT-008", "EVT-009", "EVT-011", "APP-Q-004", "EVT-014"),
            )
        elif item_id == "Q-006":
            item_events = _prioritize_trace_cards(item_events, ("EVT-005", "ORS-Q-006", "EVT-012", "EVT-013", "EVT-014"))
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


def _approval_trace_card(answer: dict[str, Any]) -> dict[str, Any]:
    approval_owner = answer["approval_owner"] or "Human approver"
    return {
        "label": "Scoped approval",
        "sender": approval_owner,
        "receiver": "trustroom-orchestrator-agent",
        "event_type": EventType.HUMAN_APPROVAL.value,
        "task_state": "approval",
        "summary": f"{approval_owner} approved scoped sample wording: {answer['approval_reason']}",
        "refs": [
            answer["approval_decision_id"],
            answer["approval_validity"],
            answer["approval_expires_at_label"],
            *answer["approved_evidence_ids"],
        ],
        "tone": "human",
    }


def _owner_review_suggestion_trace_card(suggestion: dict[str, Any]) -> dict[str, Any]:
    return {
        "label": "Owner review suggestion",
        "sender": suggestion["proposed_by"],
        "receiver": suggestion["owner_role"],
        "event_type": EventType.OWNER_REVIEW_SUGGESTION.value,
        "task_state": "approval",
        "summary": (
            f"{suggestion['proposed_by']} proposed replacement evidence "
            f"{', '.join(suggestion['suggested_evidence_ids'])}; status remains {suggestion['status']}."
        ),
        "refs": [
            suggestion["suggestion_id"],
            *suggestion["suggested_evidence_ids"],
            *suggestion["replaces_evidence_ids"],
        ],
        "tone": "review",
    }


def _blocked_impact_path(
    answers: list[dict[str, Any]],
    owner_review_suggestions: list[dict[str, Any]],
) -> list[str]:
    q6 = next(answer for answer in answers if answer["item_id"] == "Q-006")
    q6_suggestion = next(
        (suggestion for suggestion in owner_review_suggestions if suggestion["item_id"] == "Q-006"),
        None,
    )
    suggestion_step = (
        f"replacement suggestion {q6_suggestion['suggestion_id']} is {q6_suggestion['status']}"
        if q6_suggestion
        else "no replacement suggestion"
    )
    return [
        f"freshness rollup {q6['freshness_rollup']}",
        "stale/conflicting incident evidence",
        suggestion_step,
        q6["review_status"],
        "no valid human approval",
        "final pack excluded",
        q6["next_action"],
    ]


def _q006_buyer_safe_story(
    answers: list[dict[str, Any]],
    owner_review_suggestions: list[dict[str, Any]],
) -> dict[str, Any]:
    q6 = next(answer for answer in answers if answer["item_id"] == "Q-006")
    q6_suggestion = next(
        (suggestion for suggestion in owner_review_suggestions if suggestion["item_id"] == "Q-006"),
        None,
    )
    suggestion_ref = q6_suggestion["suggestion_id"] if q6_suggestion else "owner review pending"
    return {
        "item_id": "Q-006",
        "headline": "Q-006 buyer-safe story",
        "summary": (
            "Unsafe incident-response wording is held outside the customer export until the "
            "Security Policy Owner confirms current wording."
        ),
        "steps": [
            {
                "label": "risky incident-response wording",
                "detail": q6["question"],
                "tone": "review",
            },
            {
                "label": "stale/conflicting evidence",
                "detail": q6["freshness_rollup"],
                "tone": "blocked",
            },
            {
                "label": "no valid human approval",
                "detail": q6["review_status"],
                "tone": "blocked",
            },
            {
                "label": "excluded from customer pack",
                "detail": q6["final_pack_reason"],
                "tone": "blocked",
            },
            {
                "label": "policy owner action",
                "detail": q6["next_action"],
                "tone": "human",
            },
        ],
        "refs": [
            q6["item_id"],
            q6["answer_id"],
            q6["review_decision_id"],
            suggestion_ref,
        ],
        "safe_boundary": "Customer Export stays at 7/8 until this owner decision is complete.",
    }


def _approval_owner_label(role: str) -> str:
    normalized = role.lower()
    if "security policy" in normalized:
        return "Security Policy Owner"
    if "legal" in normalized:
        return "Legal Reviewer"
    if "sme" in normalized:
        return "SME Approver"
    return role.replace("-", " ").title()


def _approval_allowed_wording(
    *,
    item_id: str,
    approval_valid: bool,
    approval_scope: str,
) -> str:
    if not approval_valid:
        return "No customer wording is approved yet."
    if item_id == "Q-002":
        return "SOC 2 summary availability and bridge-letter sharing for approved prospects."
    if item_id == "Q-004":
        return "Bounded region-restricted pilot wording from the legal approval scope."
    return approval_scope or "Only the scoped approval wording can be used."


def _approval_prohibited_wording(item_id: str) -> str:
    if item_id == "Q-002":
        return "Do not imply public SOC 2 distribution, certification, or blanket access."
    if item_id == "Q-004":
        return "Do not promise unconditional EU-only processing."
    if item_id == "Q-006":
        return "Do not commit to an incident-response notification target until policy owner approval."
    return "Do not expand beyond the recorded approval scope."


def _business_lineage_summary(
    *,
    question: Any,
    evidence: list[Any],
    review: Any | None,
    approval: ApprovalDecision | None,
    draft: AnswerDraft,
    status: str,
    final_pack_status: str,
    final_pack_reason: str,
    gate_reasons: list[str],
    freshness_rollup: str,
) -> list[dict[str, str]]:
    question_text = (
        f"{question.business_owner.value.title()} owns {question.item_id}; "
        f"{question.category.value} request, {question.risk_level.value} risk: {question.question_text}"
    )
    evidence_text = _business_evidence_summary(evidence, freshness_rollup)
    review_text = _business_review_summary(
        review=review,
        approval=approval,
        draft=draft,
    )
    risk_text = _business_risk_summary(
        status=status,
        final_pack_status=final_pack_status,
        final_pack_reason=final_pack_reason,
        gate_reasons=gate_reasons,
    )
    return [
        {"label": "Question answered", "text": question_text},
        {"label": "Evidence confidence", "text": evidence_text},
        {"label": "Review / approval", "text": review_text},
        {"label": "Risk contained", "text": risk_text},
    ]


def _lineage_status_label(status: str) -> str:
    label = status.replace("_", " ")
    if label.startswith("rollup:"):
        return label.replace("rollup:", "Rollup: ", 1)
    return label[:1].upper() + label[1:]


def _lineage_reason_label(reason: str) -> str:
    return reason.replace("_", " ")


def _business_evidence_summary(evidence: list[Any], freshness_rollup: str) -> str:
    if not evidence:
        return "No evidence refs are attached; the answer cannot be customer-ready."
    evidence_ids = ", ".join(candidate.evidence_id for candidate in evidence[:3])
    if len(evidence) > 3:
        evidence_ids += f" + {len(evidence) - 3} more"
    freshness = sorted({candidate.freshness_label.value for candidate in evidence})
    if freshness == [EvidenceFreshness.CURRENT.value]:
        return f"{len(evidence)} current evidence refs support the answer: {evidence_ids}."
    non_current = [label for label in freshness if label != EvidenceFreshness.CURRENT.value]
    freshness_text = ", ".join(non_current or freshness)
    return (
        f"Evidence mix includes {freshness_text} refs; freshness rollup is {freshness_rollup}, "
        "so customer wording must stay bounded until the owner resolves it."
    )


def _business_review_summary(
    *,
    review: Any | None,
    approval: ApprovalDecision | None,
    draft: AnswerDraft,
) -> str:
    if approval is not None and _approval_is_valid_for_answer(approval, draft):
        return f"{_approval_owner_label(approval.reviewer_role)} approved scoped wording: {approval.scope}"
    if review is None:
        return "No reviewer decision is attached yet."
    if review.status == ReviewStatus.REQUEST_CHANGES:
        return f"{review.reviewer_agent} challenged the draft: {review.reason}"
    if review.status == ReviewStatus.NEEDS_HUMAN_APPROVAL:
        return f"{review.reviewer_agent} requires human approval; no valid scoped approval is attached yet."
    if review.status == ReviewStatus.BLOCKED:
        return f"{review.reviewer_agent} blocked customer use: {review.reason}"
    if review.status == ReviewStatus.APPROVED:
        return f"{review.reviewer_agent} accepted the bounded draft: {review.reason}"
    return f"{review.reviewer_agent} recorded {review.status.value}: {review.reason}"


def _business_risk_summary(
    *,
    status: str,
    final_pack_status: str,
    final_pack_reason: str,
    gate_reasons: list[str],
) -> str:
    if status == "ready":
        return f"Final pack {final_pack_status}; {final_pack_reason}"
    if gate_reasons:
        return f"Final pack {final_pack_status}; {_business_blocker_summary(gate_reasons)}"
    return f"Final pack {final_pack_status}; {final_pack_reason}"


def _business_blocker_summary(gate_reasons: list[str]) -> str:
    blockers = []
    joined = " ".join(gate_reasons).lower()
    if "stale evidence" in joined:
        blockers.append("stale evidence")
    if "conflicting evidence" in joined:
        blockers.append("conflicting evidence")
    if "requires human approval" in joined or "needs_human_approval" in joined:
        blockers.append("missing scoped human approval")
    if not blockers:
        return "; ".join(reason.replace("_", " ") for reason in gate_reasons)
    if len(blockers) == 1:
        blocker_text = blockers[0]
    else:
        blocker_text = ", ".join(blockers[:-1]) + f" and {blockers[-1]}"
    verb = "keeps" if len(blockers) == 1 else "keep"
    return f"{blocker_text} {verb} this answer out of customer materials."


def _responsibility_queue(
    *,
    answers: list[dict[str, Any]],
    approval_queue: list[dict[str, Any]],
) -> dict[str, Any]:
    answer_by_item_id = {answer["item_id"]: answer for answer in answers}
    items = []
    for gate in approval_queue:
        answer = answer_by_item_id[gate["item_id"]]
        is_open = gate["decision"] != "approved" or answer["final_pack_status"] != "included"
        items.append(
            {
                "item_id": gate["item_id"],
                "state": "open" if is_open else "done",
                "state_label": "owner action open" if is_open else "human gate complete",
                "tone": "blocked" if is_open else "ready",
                "assignee": _queue_assignee(gate),
                "owner": answer["owner"].title(),
                "risk": answer["risk"],
                "due_window": "before customer export" if is_open else "complete for sample pack",
                "escalation_role": _queue_escalation_role(answer=answer, gate=gate, is_open=is_open),
                "next_action": gate["next_action"],
                "reason": answer["final_pack_reason"] if is_open else gate["approval_reason"],
                "final_pack_status": answer["final_pack_status"],
            }
        )
    items.sort(key=lambda item: (item["state"] != "open", item["item_id"]))
    open_count = sum(1 for item in items if item["state"] == "open")
    done_count = len(items) - open_count
    return {
        "summary": f"{open_count} open owner action · {done_count} completed human gates",
        "open_count": open_count,
        "done_count": done_count,
        "queue_items": items,
        "sample_boundary": "Queue fields are fictional sample workflow metadata; no live account dependency is required.",
    }


def _queue_assignee(gate: dict[str, Any]) -> str:
    role = str(gate["approval_role"]).lower()
    if "security policy" in role:
        return "Security Policy Owner"
    if "legal" in role:
        return "Legal Reviewer"
    if "sme" in role:
        return "SME Approver"
    return str(gate["approval_role"]).replace("-", " ").title()


def _queue_escalation_role(
    *,
    answer: dict[str, Any],
    gate: dict[str, Any],
    is_open: bool,
) -> str:
    if not is_open:
        return "No escalation"
    if answer["risk"] == "high" and answer["owner"] == "security":
        return "Security leadership"
    if answer["owner"] == "legal":
        return "Legal counsel"
    return _queue_assignee(gate)


def _trace_card(event: dict[str, Any], *, label: str | None = None) -> dict[str, Any]:
    event_type = event["event_type"]
    sender = event["sender"]
    receiver = event["receiver"]
    tone = "handoff"
    if event_type == EventType.REVIEW_DECISION.value or "review loop" in event["payload_summary"].lower():
        tone = "review"
    elif event_type == EventType.OWNER_REVIEW_SUGGESTION.value:
        tone = "review"
    elif event_type == EventType.HUMAN_APPROVAL.value:
        tone = "human"
        sender = f"{_approval_owner_label(sender)} (human gate)"
    elif event_type == EventType.FINAL_PACK_CREATED.value:
        tone = "final"
    if "blocked" in event["payload_summary"].lower():
        tone = "blocked"
    return {
        "label": label or _trace_label(event),
        "sender": sender,
        "receiver": receiver,
        "event_type": _trace_value_label(event_type),
        "task_state": _trace_value_label(event["task_state"]),
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


def _trace_value_label(value: str) -> str:
    return value.replace("_", " ").title()


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
    freshness_rollup: str,
) -> str:
    if status == "blocked":
        return "; ".join(gate_reasons) if gate_reasons else "Blocked item is excluded from the final pack."
    if freshness_rollup != EvidenceFreshness.CURRENT.value:
        return f"Excluded until evidence freshness rollup becomes current; current rollup is {freshness_rollup}."
    if approval_role and approval_reason:
        return f"Included after {_approval_owner_label(approval_role)} approval: {approval_reason}"
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
        if answer["risk"] == "high" or freshness.intersection({"stale", "missing", "unknown", "conflicting"}):
            risks.append(
                {
                    "item_id": answer["item_id"],
                    "owner": answer["owner"],
                    "risk": answer["risk"],
                    "status": answer["status"],
                    "freshness": ", ".join(answer["freshness"]) or "none",
                    "freshness_rollup": answer["freshness_rollup"],
                    "review_status": answer["review_status"],
                    "next_action": answer["next_action"],
                }
            )
    return risks
