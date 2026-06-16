# RFP TrustRoom Context

RFP TrustRoom is a Band-coordinated collaboration room for responding to RFPs and security questionnaires. This glossary keeps the product language centered on the hackathon flow: a human asks for work, agents hand tasks to each other through Band, and a human gate protects risky commitments.

## Language

**TrustRoom Canonical Flow**:
The primary demo story: Human Request -> Orchestrator -> Requirement Decomposer -> Evidence Retriever -> Answer Drafter -> Compliance Reviewer -> Human Approver -> Final Pack. This flow is the first explanation of the product and the judge-facing path.
_Avoid_: starting the story from dashboards, risk matrices, governed evolution, or internal implementation stages.

**Human Request**:
The human-originated business ask and materials that start a TrustRoom run, such as an RFP, security questionnaire, deadline, and company knowledge snippets. It is the source of intent before any agent work begins.
_Avoid_: generic prompt, raw upload, ticket.

**Request Summary**:
The first-screen explanation of what TrustRoom understood from the Human Request. It should show customer goal, input materials, deadline, expected output, risk hints, and the agent chain being started.
_Avoid_: hidden classifier result, vague intent label, raw upload list.

**Question Item**:
The smallest customer-facing requirement or questionnaire unit that TrustRoom tracks through the Visible Handoff Chain. A Question Item carries the business question, evidence need, owner or reviewer context, risk status, and final-pack outcome, so users can understand why a specific customer ask is ready, needs changes, or is blocked.
_Avoid_: whole RFP as the tracking unit, raw chat message, anonymous agent step.

**Plain Explanation**:
A communication style for explaining TrustRoom to the project owner, judges, or enterprise users in ordinary language. It must make the workflow easier to understand without weakening the underlying evidence, approval, audit, or no-overclaim rules.
_Avoid_: simplified system, toy demo, loose workflow.

**Rigorous Workflow**:
The enterprise-facing operating standard for TrustRoom: every customer-facing answer needs traceable intent, evidence, review status, approval basis when required, and an explicit final-pack decision. The product can feel easy to use while still failing closed on missing evidence, stale evidence, overclaims, or unapproved high-risk commitments.
_Avoid_: casual automation, best-effort answer generation, unchecked draft.

**TrustRoom Business Language**:
The controlled product language used to describe TrustRoom runs across UI, demo narration, agent handoffs, docs, and audit surfaces. It starts from the Human Request, names the acting role, shared business object, state change, evidence or approval basis, and final-pack outcome without exposing private chain-of-thought or overstating live/production readiness.
_Avoid_: generic AI workflow, internal debug language, judge-only framing, production compliance claims.

**Band Handoff**:
A visible transfer of task context from one participant to another in the TrustRoom flow, normally expressed as an @mention, shared object reference, review decision, or state update in Band. It is the evidence that Band is coordinating the work rather than merely receiving the final answer.
_Avoid_: background automation, notification, log entry.

**Visible Handoff Chain**:
The user-facing view of agent-to-agent work in TrustRoom, showing who asked whom to do what, which shared object moved forward, what state changed, and what decision or blocker resulted. It combines a readable overview of the sequence and status with drill-down message evidence, so collaboration is visible without forcing users to parse raw logs first.
_Avoid_: hidden agent run, raw logs only, outcome-only dashboard.

**Handoff Summary**:
The collapsed view of one Band handoff. It should only show six canonical fields: From, To, Task, Shared Object, State Change, and Result / Blocker.
_Avoid_: crowded card, full transcript, internal trace dump.

**Multi-Item Handoff**:
A single Band Handoff whose task affects more than one Question Item. Its Handoff Summary still uses the six canonical fields, while the expanded view lists the affected Question Items and each item's evidence status, risk status, and final-pack impact.
_Avoid_: adding extra default fields, hiding affected items, splitting one business handoff into noisy raw-message cards.

**Handoff Evidence Detail**:
The expanded view of a handoff, used when a user or judge wants to inspect the supporting message evidence, object references, timing, decision reason, evidence freshness, or approval context behind the summary.
_Avoid_: default raw log view, hidden proof, unrelated debug detail.

**Backend Audit Access**:
A permissioned backend view for authorized operators who need deeper diagnostic trace than the normal user interface exposes. It can include message payloads, object references, tool inputs and outputs, timestamps, redacted provider metadata, and decision summaries, while keeping secrets and private raw internals out of the public demo surface.
_Avoid_: public chain-of-thought display, unrestricted log access, secret-bearing debug dump.

**Full-Picture Workflow View**:
The normal TrustRoom product experience should let enterprise users, judges, and demo viewers understand the complete workflow from Human Request through Visible Handoff Chain, evidence review, human approval, Final Pack, and replay/live boundary. It can expose redacted evidence and backend-audit excerpts in context, but it is not a separate judge-only page or unrestricted backend access.
_Avoid_: judge-only page, partial demo path, opaque final answer, secret-bearing backend access.

**Full-Picture First View**:
The first screen of the normal TrustRoom product experience. It should show the Human Request, current submission state, key blocker, and the opening steps of the Visible Handoff Chain so viewers immediately understand what happened, where the workflow stands, and how agents are collaborating.
_Avoid_: metric wall, chat wall, disconnected executive summary.

**Key Blocker**:
The single blocker shown on the Full-Picture First View because it has the highest impact on customer delivery of the Final Pack. When multiple blockers exist, prioritize final-pack exclusion, missing valid human approval, stale or conflicting evidence, request-changes loops, then missing owner or deadline context.
_Avoid_: latest blocker, easiest technical issue, multiple competing first-screen blockers.

**Owner Review Suggestion**:
An Agent-proposed recommendation attached to a Key Blocker or Question Item for a human or business owner to review. It can suggest scoped wording, replacement evidence, approval questions, or next actions, but it does not approve the item or make it eligible for the Final Pack without owner review.
_Avoid_: agent approval, automatic sign-off, silent final-pack inclusion.

**Owner Review Suggestion Status**:
The lightweight review state of an Owner Review Suggestion: proposed, accepted, rejected, or needs_revision. The status tracks the suggestion only; accepted means the owner accepts the recommendation as useful, not that the Question Item has final approval or Final Pack permission.
_Avoid_: heavyweight workflow state machine, treating accepted as approval, forcing all statuses onto the first screen.

**Owner Review Decision**:
The minimum owner response record for an Owner Review Suggestion. It contains decision, reason, and scope, using a short business reason rather than a long approval memo; the scope keeps any acceptance or rejection tied to a specific Question Item, wording, evidence set, or time boundary.
_Avoid_: reasonless decision, broad blanket approval, long legal memo.

**Owner Review Reason**:
The short free-text business reason inside an Owner Review Decision. The user-facing workflow should not force fixed reason options; backend audit may derive a reason category later, while the original reason text remains visible for review.
_Avoid_: mandatory dropdown taxonomy, empty approval, hiding the owner’s original wording.

**Human Approval**:
The formal human gate that allows a high-risk Question Item or answer to enter the Final Pack within a stated scope, evidence set, and validity boundary. It is separate from Owner Review Decision; accepting an Agent suggestion does not grant Human Approval.
_Avoid_: suggestion acceptance, informal owner comment, blanket approval.

**Human Approval Record**:
The minimum formal approval record for a high-risk Question Item or answer to enter the Final Pack. It contains approver role, decision, scope, reason, and validity, so the approval is tied to a specific business owner, wording, evidence set, and time or scope boundary.
_Avoid_: approval without scope, permanent approval by implication, generic sign-off.

**Human Approval Decision**:
The formal decision value inside a Human Approval Record. It should only be approved, request_changes, or rejected, keeping intermediate suggestion and review-loop states out of the approval gate.
_Avoid_: pending approval as permission, mixing suggestion status into approval, ambiguous soft approval.

**Final Pack Inclusion**:
The customer-delivery disposition of a Question Item or answer relative to the Final Pack. It uses only included, excluded, or pending: included means required evidence, review, and approval gates are satisfied; excluded means the item is deliberately kept out by a blocker or rejected approval; pending means the item is waiting on evidence, owner review, or Human Approval.
_Avoid_: passed/failed language, silent omission, pretending pending work is complete.

**Final Pack Exceptions**:
A separate section beside the Final Pack that lists Question Items with excluded or pending Final Pack Inclusion. It shows why the item is not deliverable yet, who owns the next action, and what must change without treating the item as an included answer.
_Avoid_: mixing exceptions into included answers, hiding blocked items, treating exceptions as customer-approved content.

**Customer Export**:
The customer-submittable output produced from the Final Pack. By default its answer body contains only included answers; Final Pack Exceptions can appear only in a clearly marked Review Appendix when transparency is required.
_Avoid_: exporting blocked or pending items as answer body, unlabeled exceptions, treating review notes as customer-submittable content.

**Review Appendix**:
A non-submittable appendix used with a Customer Export or reviewer package to disclose Final Pack Exceptions for transparency. It labels each exception as not customer-submittable and keeps the reason, owner, and next action visible.
_Avoid_: customer answer body, unmarked exception list, hidden review-only caveat.

**Review Appendix Export Decision**:
The explicit human or business-owner decision that allows a Review Appendix to be attached to a Customer Export. It controls appendix visibility only; it is not Human Approval, does not make exceptions customer-submittable, and cannot be made automatically by an Agent.
_Avoid_: agent-added appendix, automatic exception export, treating appendix inclusion as answer approval.

**Review Appendix Export Record**:
The minimum audit record for a Review Appendix Export Decision. It contains decision, owner role, reason, and scope, tying appendix visibility to a specific human or business-owner choice and Customer Export boundary.
_Avoid_: reasonless appendix inclusion, agent-only export setting, broad reusable appendix permission.

**First-Screen Representative Paths**:
The three Question Item paths shown on the Full-Picture First View to demonstrate the main TrustRoom outcomes: one ready or approved item, one request-changes review loop, and one blocked fail-closed item. The full item list can appear in a later section or expanded view.
_Avoid_: exhaustive first-screen item table, success-only showcase, hiding blocked outcomes.

**Final Pack**:
The customer-facing answer package produced after decomposition, evidence retrieval, drafting, review, and required human approval. It contains only included answers; excluded or pending items appear separately as Final Pack Exceptions when full workflow visibility is needed.
_Avoid_: report, chatbot answer, generated summary.
