from __future__ import annotations

from collections.abc import Iterable

from trustroom.models import (
    EvolutionProposal,
    ExperienceLesson,
    LessonScope,
    LessonType,
    ProposalStatus,
    ProposalType,
    Run,
    TimelineEvent,
)


class ProposalValidationError(ValueError):
    pass


class LessonNotFoundError(KeyError):
    pass


GOVERNANCE_WEAKENING_PHRASES = (
    "remove human approval",
    "skip human approval",
    "bypass human approval",
    "without human approval",
    "no human approval",
    "auto-approve high-risk",
    "remove the human approval gate",
    "delete the no-overclaim",
    "remove no-overclaim",
    "disable no-overclaim",
    "skip no-overclaim",
    "without no-overclaim",
    "allow overclaim",
    "overclaim claims can pass",
    "certified and guaranteed claims can pass",
)

LESSON_TYPE_BY_PROPOSAL: dict[ProposalType, LessonType] = {
    ProposalType.PROMPT_CHANGE: LessonType.CHECKLIST,
    ProposalType.ROUTING_RULE: LessonType.ROUTING_RULE,
    ProposalType.TASK_SCHEMA_CHANGE: LessonType.CHECKLIST,
    ProposalType.REVIEWER_GATE: LessonType.APPROVAL_POLICY,
    ProposalType.EVIDENCE_RULE: LessonType.EVIDENCE_RULE,
    ProposalType.STRESS_TEST: LessonType.STRESS_TEST_SEED,
    ProposalType.NO_OVERCLAIM_RULE: LessonType.NO_OVERCLAIM_RULE,
}

LESSON_SCOPE_BY_PROPOSAL: dict[ProposalType, LessonScope] = {
    ProposalType.PROMPT_CHANGE: LessonScope.AGENT_ROLE,
    ProposalType.ROUTING_RULE: LessonScope.AGENT_ROLE,
    ProposalType.TASK_SCHEMA_CHANGE: LessonScope.GLOBAL,
    ProposalType.REVIEWER_GATE: LessonScope.RISK_LEVEL,
    ProposalType.EVIDENCE_RULE: LessonScope.CATEGORY,
    ProposalType.STRESS_TEST: LessonScope.SAMPLE_PACK,
    ProposalType.NO_OVERCLAIM_RULE: LessonScope.GLOBAL,
}


class ExperienceLedger:
    def __init__(self, *, events: Iterable[TimelineEvent] = ()) -> None:
        self._events_by_id = {event.event_id: event for event in events}
        self._proposals: dict[str, EvolutionProposal] = {}
        self._lessons: dict[str, ExperienceLesson] = {}

    def review_proposal(
        self,
        proposal: EvolutionProposal,
        *,
        decision: ProposalStatus,
        reviewer: str,
        reviewer_notes: str,
    ) -> EvolutionProposal:
        if decision == ProposalStatus.PENDING_REVIEW:
            raise ProposalValidationError("review decision must resolve pending_review")

        self.validate_proposal(proposal)
        if decision == ProposalStatus.APPROVED and not is_human_evolution_reviewer(reviewer):
            raise ProposalValidationError("approved proposals require a human evolution reviewer")

        if weakens_governance(proposal):
            reviewed = proposal.model_copy(
                update={
                    "status": ProposalStatus.REJECTED,
                    "reviewer_notes": _append_note(
                        reviewer_notes,
                        "Safety check rejected a governance-weakening change.",
                    ),
                }
            )
            self._proposals[reviewed.proposal_id] = reviewed
            return reviewed

        reviewed = proposal.model_copy(
            update={
                "status": decision,
                "reviewer_notes": reviewer_notes,
            }
        )
        self._proposals[reviewed.proposal_id] = reviewed

        if decision == ProposalStatus.APPROVED:
            lesson = lesson_from_proposal(reviewed, accepted_by=reviewer)
            self._lessons[lesson.lesson_id] = lesson

        return reviewed

    def validate_proposal(self, proposal: EvolutionProposal) -> None:
        if not proposal.supporting_event_ids:
            raise ProposalValidationError("proposal must cite at least one supporting timeline event")

        missing = [
            event_id
            for event_id in proposal.supporting_event_ids
            if event_id not in self._events_by_id
        ]
        if missing:
            raise ProposalValidationError(
                "proposal cites unknown supporting timeline event(s): "
                + ", ".join(sorted(missing))
            )

        wrong_run = [
            event_id
            for event_id in proposal.supporting_event_ids
            if self._events_by_id[event_id].run_id != proposal.run_id
        ]
        if wrong_run:
            raise ProposalValidationError(
                "proposal cites supporting timeline event(s) from a different run: "
                + ", ".join(sorted(wrong_run))
            )

    def active_lessons(self) -> list[ExperienceLesson]:
        return [lesson for lesson in self._lessons.values() if lesson.active]

    def load_active_lessons(self, run: Run) -> Run:
        return run.model_copy(
            update={"active_lessons": [lesson.lesson_id for lesson in self.active_lessons()]}
        )

    def rollback_lesson(self, lesson_id: str, *, rollback_note: str) -> ExperienceLesson:
        lesson = self._lessons.get(lesson_id)
        if lesson is None:
            raise LessonNotFoundError(lesson_id)

        rolled_back = lesson.model_copy(
            update={
                "active": False,
                "rollback_note": rollback_note,
            }
        )
        self._lessons[lesson_id] = rolled_back
        return rolled_back


def lesson_from_proposal(
    proposal: EvolutionProposal,
    *,
    accepted_by: str,
) -> ExperienceLesson:
    if proposal.status != ProposalStatus.APPROVED:
        raise ProposalValidationError("only approved proposals can become active lessons")

    return ExperienceLesson(
        lesson_id=f"lesson-{proposal.proposal_id}",
        source_proposal_id=proposal.proposal_id,
        accepted_by=accepted_by,
        scope=LESSON_SCOPE_BY_PROPOSAL[proposal.proposal_type],
        lesson_type=LESSON_TYPE_BY_PROPOSAL[proposal.proposal_type],
        instruction=proposal.proposed_change,
        applies_when=f"{proposal.target_component}: {proposal.problem_statement}",
    )


def weakens_governance(proposal: EvolutionProposal) -> bool:
    text = " ".join(
        [
            proposal.target_component,
            proposal.problem_statement,
            proposal.proposed_change,
            proposal.expected_effect,
            proposal.evaluation_plan,
        ]
    ).casefold()
    return any(phrase in text for phrase in GOVERNANCE_WEAKENING_PHRASES)


def is_human_evolution_reviewer(reviewer: str) -> bool:
    return bool(reviewer.strip()) and not reviewer.strip().casefold().endswith("-agent")


def _append_note(existing: str, note: str) -> str:
    if not existing:
        return note
    return f"{existing} {note}"
