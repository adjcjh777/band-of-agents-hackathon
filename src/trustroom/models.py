from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


ReadinessSummary = Literal["ready", "needs_review", "blocked"]
Visibility = Literal["judge_view", "technical_appendix"]
LineageStage = Literal["question", "evidence", "draft", "review", "approval", "final_pack"]
FinalPackInclusion = Literal["included", "excluded", "pending"]
FinalPackExceptionInclusion = Literal["excluded", "pending"]


class TrustRoomModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class MaterialType(str, Enum):
    RFP = "rfp"
    SECURITY_QUESTIONNAIRE = "security_questionnaire"
    POLICY_SNIPPETS = "policy_snippets"
    PRIOR_ANSWERS = "prior_answers"


class ExecutionMode(str, Enum):
    LIVE = "live"
    MOCK = "mock"
    REPLAY = "replay"


class RunState(str, Enum):
    INTAKE = "intake"
    TRIAGE = "triage"
    DECOMPOSITION = "decomposition"
    EVIDENCE = "evidence"
    DRAFTING = "drafting"
    REVIEW = "review"
    APPROVAL = "approval"
    SUBMISSION_PACK = "submission_pack"
    POST_RUN_REVIEW = "post_run_review"
    EVOLUTION_REVIEW = "evolution_review"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class EvidenceFreshness(str, Enum):
    CURRENT = "current"
    STALE = "stale"
    MISSING = "missing"
    UNKNOWN = "unknown"
    CONFLICTING = "conflicting"


class ReviewAppendixVisibilityMode(str, Enum):
    CUSTOMER_SAFE = "customer-safe"
    INTERNAL_REVIEW = "internal-review"


class ReviewAppendixExportDecisionValue(str, Enum):
    INCLUDE_APPENDIX = "include_appendix"
    OMIT_APPENDIX = "omit_appendix"


class ReviewStatus(str, Enum):
    NOT_STARTED = "not_started"
    APPROVED = "approved"
    REQUEST_CHANGES = "request_changes"
    BLOCKED = "blocked"
    NEEDS_HUMAN_APPROVAL = "needs_human_approval"
    NEEDS_REVIEW = "needs_review"


class ApprovalDecisionValue(str, Enum):
    APPROVE = "approve"
    REQUEST_CHANGES = "request_changes"
    REJECT = "reject"
    DEFER = "defer"


class ApprovalValidity(str, Enum):
    VALID = "valid"
    EXPIRED = "expired"
    OUT_OF_SCOPE = "out_of_scope"


class ProposalStatus(str, Enum):
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUEST_CHANGES = "request_changes"
    DEFERRED = "deferred"


class EventType(str, Enum):
    INTAKE = "intake"
    TASK_ASSIGNED = "task_assigned"
    HANDOFF = "handoff"
    EVIDENCE_FOUND = "evidence_found"
    DRAFT_CREATED = "draft_created"
    REVIEW_DECISION = "review_decision"
    HUMAN_APPROVAL = "human_approval"
    FINAL_PACK_CREATED = "final_pack_created"
    EVOLUTION_PROPOSED = "evolution_proposed"
    LESSON_ACCEPTED = "lesson_accepted"
    OWNER_REVIEW_SUGGESTION = "owner_review_suggestion"
    STRESS_TEST_GENERATED = "stress_test_generated"
    STATE_CHANGED = "state_changed"
    REQUEST_CHANGES = "request_changes"


class QuestionCategory(str, Enum):
    SECURITY = "security"
    PRIVACY = "privacy"
    PRODUCT = "product"
    LEGAL = "legal"
    SUPPORT = "support"
    COMMERCIAL = "commercial"


class BusinessOwner(str, Enum):
    SALES = "sales"
    SECURITY = "security"
    PRODUCT = "product"
    LEGAL = "legal"
    SME = "sme"


class QuestionStatus(str, Enum):
    OPEN = "open"
    EVIDENCE_READY = "evidence_ready"
    NEEDS_REVIEW = "needs_review"
    BLOCKED = "blocked"
    APPROVED = "approved"


class ProposalType(str, Enum):
    PROMPT_CHANGE = "prompt_change"
    ROUTING_RULE = "routing_rule"
    TASK_SCHEMA_CHANGE = "task_schema_change"
    REVIEWER_GATE = "reviewer_gate"
    EVIDENCE_RULE = "evidence_rule"
    STRESS_TEST = "stress_test"
    NO_OVERCLAIM_RULE = "no_overclaim_rule"


class OwnerReviewSuggestionStatus(str, Enum):
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"


class LessonScope(str, Enum):
    GLOBAL = "global"
    SAMPLE_PACK = "sample_pack"
    CATEGORY = "category"
    RISK_LEVEL = "risk_level"
    AGENT_ROLE = "agent_role"


class LessonType(str, Enum):
    CHECKLIST = "checklist"
    ROUTING_RULE = "routing_rule"
    EVIDENCE_RULE = "evidence_rule"
    NO_OVERCLAIM_RULE = "no_overclaim_rule"
    APPROVAL_POLICY = "approval_policy"
    STRESS_TEST_SEED = "stress_test_seed"


class StressTrapType(str, Enum):
    MISSING_EVIDENCE = "missing_evidence"
    STALE_EVIDENCE = "stale_evidence"
    OVERCLAIM = "overclaim"
    UNSUPPORTED_CERTIFICATION = "unsupported_certification"
    SLA_COMMITMENT = "sla_commitment"
    CONFLICTING_SOURCES = "conflicting_sources"


class SafeBehavior(str, Enum):
    NEEDS_REVIEW = "needs_review"
    NEEDS_HUMAN_APPROVAL = "needs_human_approval"
    BLOCKED = "blocked"
    REQUEST_CHANGES = "request_changes"


def utc_now() -> datetime:
    return datetime.now(UTC)


class CustomerCase(TrustRoomModel):
    case_id: str
    case_name: str
    customer_profile: str
    deadline_label: str
    material_types: list[MaterialType]
    business_goal: str
    submission_owner: str
    mode: ExecutionMode = ExecutionMode.MOCK


class Run(TrustRoomModel):
    run_id: str
    case_id: str
    mode: ExecutionMode
    state: RunState = RunState.INTAKE
    created_at: datetime = Field(default_factory=utc_now)
    band_room_label: str
    active_lessons: list[str] = Field(default_factory=list)
    current_blockers: list[str] = Field(default_factory=list)
    readiness_summary: ReadinessSummary = "needs_review"


class QuestionItem(TrustRoomModel):
    item_id: str
    case_id: str
    source_ref: str
    question_text: str
    category: QuestionCategory
    risk_level: RiskLevel
    required_evidence_type: str
    business_owner: BusinessOwner
    status: QuestionStatus = QuestionStatus.OPEN


class EvidenceCandidate(TrustRoomModel):
    evidence_id: str
    item_id: str
    source_title: str
    snippet: str
    freshness_label: EvidenceFreshness
    freshness_marked_by: str = "evidence-retriever-agent"
    freshness_marked_at: datetime = Field(default_factory=utc_now)
    confidence: float = Field(ge=0.0, le=1.0)


class AnswerDraft(TrustRoomModel):
    answer_id: str
    item_id: str
    draft_text: str
    evidence_ids: list[str] = Field(default_factory=list)
    review_status: ReviewStatus = ReviewStatus.NEEDS_REVIEW
    review_notes: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)


class ReviewDecision(TrustRoomModel):
    decision_id: str
    item_id: str
    answer_id: str
    reviewer_agent: str
    status: ReviewStatus
    reason: str
    required_follow_up: str | None = None
    created_at: datetime = Field(default_factory=utc_now)


class OwnerReviewSuggestion(TrustRoomModel):
    suggestion_id: str
    item_id: str
    proposed_by: str
    owner_role: str
    status: OwnerReviewSuggestionStatus = OwnerReviewSuggestionStatus.PROPOSED
    suggested_evidence_ids: list[str] = Field(default_factory=list)
    replaces_evidence_ids: list[str] = Field(default_factory=list)
    reason: str
    scope: str
    created_at: datetime = Field(default_factory=utc_now)


class ApprovalDecision(TrustRoomModel):
    decision_id: str
    item_id: str
    answer_id: str | None = None
    reviewer_role: str
    decision: ApprovalDecisionValue
    reason: str
    scope: str = "Current answer wording and attached evidence for this sample item."
    expires_at_label: str = "Valid for this sample run."
    validity: ApprovalValidity = ApprovalValidity.VALID
    approved_evidence_ids: list[str] = Field(default_factory=list)
    required_follow_up: str | None = None
    created_at: datetime = Field(default_factory=utc_now)


class FinalSubmissionPack(TrustRoomModel):
    pack_id: str
    run_id: str
    generated_at: datetime = Field(default_factory=utc_now)
    included_answer_ids: list[str] = Field(default_factory=list)
    blocked_item_ids: list[str] = Field(default_factory=list)
    readiness_summary: ReadinessSummary
    evidence_index: dict[str, list[str]] = Field(default_factory=dict)
    freshness_rollup: dict[str, EvidenceFreshness] = Field(default_factory=dict)
    visibility_mode: ReviewAppendixVisibilityMode = ReviewAppendixVisibilityMode.CUSTOMER_SAFE
    audit_event_ids: list[str] = Field(default_factory=list)
    mode: ExecutionMode


class CustomerExportAnswer(TrustRoomModel):
    item_id: str
    answer_id: str
    question: str
    answer_text: str
    evidence_refs: list[str] = Field(default_factory=list)
    approval_refs: list[str] = Field(default_factory=list)
    freshness_rollup: EvidenceFreshness
    final_pack_inclusion: FinalPackInclusion = "included"


class ReviewAppendixEvidenceReference(TrustRoomModel):
    ref: str
    freshness_label: EvidenceFreshness
    freshness_marked_by: str
    freshness_marked_at: datetime


class ReviewAppendixExceptionDetail(TrustRoomModel):
    supporting_agent: str
    evidence_references: list[ReviewAppendixEvidenceReference] = Field(default_factory=list)
    handoff_summary: str
    decision_reason_detail: str
    timestamp: datetime = Field(default_factory=utc_now)
    redacted_audit_refs: list[str] = Field(default_factory=list)


class ReviewAppendixExceptionItem(TrustRoomModel):
    question_item: str
    inclusion: FinalPackExceptionInclusion
    reason_or_blocker: str
    owner: str
    next_action: str
    detail: ReviewAppendixExceptionDetail | None = None


class ReviewAppendix(TrustRoomModel):
    visibility_mode: ReviewAppendixVisibilityMode = ReviewAppendixVisibilityMode.CUSTOMER_SAFE
    not_customer_submittable: bool = True
    exceptions: list[ReviewAppendixExceptionItem] = Field(default_factory=list)


class ReviewAppendixExportRecord(TrustRoomModel):
    record_id: str
    export_id: str
    decision: ReviewAppendixExportDecisionValue
    owner_role: str
    reason: str
    scope: str
    visibility_mode: ReviewAppendixVisibilityMode = ReviewAppendixVisibilityMode.CUSTOMER_SAFE
    decided_at: datetime = Field(default_factory=utc_now)


class CustomerExport(TrustRoomModel):
    export_id: str
    run_id: str
    final_pack_id: str
    generated_at: datetime = Field(default_factory=utc_now)
    mode: ExecutionMode
    answer_body: list[CustomerExportAnswer] = Field(default_factory=list)
    review_appendix: ReviewAppendix | None = None
    review_appendix_export_record: ReviewAppendixExportRecord | None = None


class LineageStep(TrustRoomModel):
    stage: LineageStage
    label: str
    status: str
    object_ids: list[str] = Field(default_factory=list)
    owner: str | None = None
    reason: str | None = None


class AnswerLineage(TrustRoomModel):
    item_id: str
    answer_id: str
    steps: list[LineageStep] = Field(min_length=1)


class TimelineEvent(TrustRoomModel):
    event_id: str
    run_id: str
    timestamp: datetime = Field(default_factory=utc_now)
    sender: str
    receiver: str
    event_type: EventType
    task_state: RunState
    payload_summary: str
    related_object_ids: list[str] = Field(default_factory=list)
    band_message_ref: str
    visibility: Visibility = "judge_view"


class TaskEnvelope(TrustRoomModel):
    task_id: str
    run_id: str
    sender: str
    receiver: str
    task_state: RunState
    objective: str
    input_object_ids: list[str] = Field(default_factory=list)
    expected_output: str
    mode: ExecutionMode = ExecutionMode.MOCK
    created_at: datetime = Field(default_factory=utc_now)


class EvolutionProposal(TrustRoomModel):
    proposal_id: str
    run_id: str
    proposed_by: str = "workflow-improvement-agent"
    proposal_type: ProposalType
    target_component: str
    problem_statement: str
    supporting_event_ids: list[str]
    proposed_change: str
    expected_effect: str
    risk_level: RiskLevel
    evaluation_plan: str
    status: ProposalStatus = ProposalStatus.PENDING_REVIEW
    reviewer_notes: str = ""


class ExperienceLesson(TrustRoomModel):
    lesson_id: str
    source_proposal_id: str
    accepted_at: datetime = Field(default_factory=utc_now)
    accepted_by: str
    scope: LessonScope
    lesson_type: LessonType
    instruction: str
    applies_when: str
    expires_at: datetime | None = None
    rollback_note: str | None = None
    active: bool = True


class StressTestCase(TrustRoomModel):
    case_id: str
    generated_from_lesson_ids: list[str] = Field(default_factory=list)
    question_text: str
    category: QuestionCategory
    risk_hint: RiskLevel
    trap_type: StressTrapType
    expected_safe_behavior: SafeBehavior
