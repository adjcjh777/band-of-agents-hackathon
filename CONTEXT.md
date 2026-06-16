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

**First-Screen Representative Paths**:
The three Question Item paths shown on the Full-Picture First View to demonstrate the main TrustRoom outcomes: one ready or approved item, one request-changes review loop, and one blocked fail-closed item. The full item list can appear in a later section or expanded view.
_Avoid_: exhaustive first-screen item table, success-only showcase, hiding blocked outcomes.

**Final Pack**:
The customer-facing answer package produced after decomposition, evidence retrieval, drafting, review, and required human approval. It contains only answers that pass the evidence and approval gates for the sample run.
_Avoid_: report, chatbot answer, generated summary.
