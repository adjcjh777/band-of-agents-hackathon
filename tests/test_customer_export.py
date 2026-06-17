from __future__ import annotations

from trustroom.agents.mock_runner import run_mock_trustroom
from trustroom.customer_export import build_customer_export
from trustroom.models import ReviewAppendixExportDecisionValue, ReviewAppendixVisibilityMode


def test_customer_export_body_contains_final_pack_included_answers_only() -> None:
    result = run_mock_trustroom()
    export = build_customer_export(result)

    included_items = {
        draft.item_id
        for draft in result.drafts
        if draft.answer_id in result.final_pack.included_answer_ids
    }

    assert export.review_appendix is None
    assert export.review_appendix_export_record is None
    assert {answer.item_id for answer in export.answer_body} == included_items
    assert "Q-006" not in {answer.item_id for answer in export.answer_body}
    assert all(answer.final_pack_inclusion == "included" for answer in export.answer_body)
    assert "should not commit to an incident-response notification target" not in _answer_body_text(export)


def test_customer_export_appendix_is_customer_safe_and_non_submittable() -> None:
    result = run_mock_trustroom()
    export = build_customer_export(result, include_review_appendix=True)

    assert export.review_appendix is not None
    assert export.review_appendix.visibility_mode == ReviewAppendixVisibilityMode.CUSTOMER_SAFE
    assert export.review_appendix.not_customer_submittable is True
    assert export.review_appendix_export_record is not None
    assert export.review_appendix_export_record.decision == ReviewAppendixExportDecisionValue.INCLUDE_APPENDIX
    assert export.review_appendix_export_record.owner_role == "Security Policy Owner"
    assert "Q-006 only" in export.review_appendix_export_record.scope

    q6_exception = next(
        item
        for item in export.review_appendix.exceptions
        if item.question_item == "Q-006"
    )

    assert q6_exception.inclusion == "excluded"
    assert q6_exception.owner == "Security Policy Owner"
    assert "stale evidence EV-006 blocks final pack entry" in q6_exception.reason_or_blocker
    assert "conflicting evidence EV-010 blocks final pack entry" in q6_exception.reason_or_blocker
    assert "high-risk answer requires human approval" in q6_exception.reason_or_blocker
    assert "not customer-submittable" not in _answer_body_text(export)
    assert "should not commit to an incident-response notification target" not in _answer_body_text(export)

    assert q6_exception.detail is not None
    evidence_refs = {evidence.ref for evidence in q6_exception.detail.evidence_references}
    assert {"EV-006", "EV-010", "EV-013"}.issubset(evidence_refs)
    assert q6_exception.detail.supporting_agent == "evidence-retriever-agent"
    assert all(ref.startswith("band-ref:") for ref in q6_exception.detail.redacted_audit_refs)
    assert "snippet" not in str(q6_exception.model_dump(mode="json")).lower()


def _answer_body_text(export) -> str:
    return "\n".join(answer.answer_text for answer in export.answer_body)
