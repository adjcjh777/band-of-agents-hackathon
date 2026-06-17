# RFP TrustRoom Product Improvement Backlog

Date: 2026-06-17

This backlog translates the current product-manager review into concrete, prioritized work. It intentionally separates submission-critical polish from post-submit SaaS direction, and keeps the public replay/live/no-overclaim boundary intact.

## Product North Star

RFP TrustRoom should make every RFP / security-questionnaire answer traceable to evidence, review, approval and final-pack decision, so risky commitments do not quietly enter the customer package.

## Priority Board

| Priority | ID | Work item | Product outcome | Owner | Status |
|---|---|---|---|---|---|
| P0 | PM-01 | Make Final Pack Decision the primary product moment | A reviewer instantly sees what can be sent, what is held back and who must unblock it | Codex controller | complete |
| P0 | PM-02 | Compress the product promise into one verifiable sentence | All public copy and video narration align around evidence, review, approval and safe final-pack decision | Codex controller | complete |
| P0 | PM-03 | Turn Q-006 into the memorable buyer-safe story | The demo's strongest moment is the unsafe answer being excluded, not merely flagged | Codex controller + UI/UX review | complete |
| P1 | PM-04 | Add responsibility / SLA / next-step queue semantics | The dashboard feels like a workbench teams can use the next morning | Codex controller | complete |
| P1 | PM-05 | Make Approval Workbench read like an approval product | Reviewers see scope, expiry, allowed wording, prohibited wording, evidence refs and owner | Codex controller | complete |
| P1 | PM-06 | Translate Answer Lineage into business language | Non-technical reviewers can follow where an answer came from, who changed it and why it is safe or blocked | Codex controller | complete |
| P2 | PM-07 | Clarify agent roles without over-personalizing them | Judges understand specialized roles while the product still feels enterprise-grade | UI/UX agent + Codex | complete |
| P2 | PM-08 | Evolve Handoff Trace into a lightweight collaboration map | Users can inspect by answer, agent, blocker or final-pack status | Codex controller | complete |
| P2 | PM-09 | Productize the replay/live boundary copy | Boundary language feels confident and truthful instead of apologetic | Scout + Codex | complete |
| P3 | PM-10 | Add workspace / project-list concept | TrustRoom scales from one demo run to multiple RFPs/questionnaires | Future product task | later |
| P3 | PM-11 | Add evidence library direction | SOC 2, ISO, DPA, architecture and incident evidence become reusable product assets | Future product task | later |
| P3 | PM-12 | Expand export workflow | Customer-safe export, internal appendix, blocked exceptions and evidence index become first-class outputs | Future product task | later |

## Detailed Todo

### PM-01 Make Final Pack Decision The Primary Product Moment

Status: complete in PM-R1.

Goal: make the first-screen Final Pack area answer four questions without scrolling deeply:

- What can be sent to the customer?
- What is held outside?
- Why is it held outside?
- Who must unblock it?

Acceptance:

- [x] The `/runs/demo/replay` first-screen route shows a compact Customer Export / Held Outside / Owner Action decision summary.
- [x] `Q-006` remains excluded from the customer answer body.
- [x] Copy avoids production, formal audit, compliance certification and complete autonomous live workflow claims.
- [x] `tests/test_web_app.py` locks the new decision text.

### PM-02 Compress The Product Promise Into One Verifiable Sentence

Status: complete in PM-R2.

Goal: align README, submission copy, video script and dashboard around the same promise:

> Every answer carries evidence, review, approval and final-pack decision context, so risky commitments stay out of the customer package.

Acceptance:

- [x] Submission copy and video script use this frame or an equivalent sentence.
- [x] No formal audit / production compliance language is introduced.

### PM-03 Turn Q-006 Into The Memorable Buyer-Safe Story

Status: complete in PM-R3.

Goal: make the Q-006 storyline unmistakable:

`risky incident-response wording -> stale/conflicting evidence -> no valid approval -> excluded from customer pack -> policy owner action`

Acceptance:

- [x] Q-006 appears in Executive Decision, Final Pack Decision, Representative Item Traces and Blocked Impact Path.
- [x] Q-006 never appears as customer-submittable answer body.
- [x] The replay route now contains a buyer-safe story block that makes the exclusion path legible in one scan.

### PM-04 Add Responsibility / SLA / Next-Step Queue Semantics

Status: complete in PM-R4.

Goal: move from static demo evidence to an operational work queue.

Potential fields:

- Assignee.
- Due window.
- Risk level.
- Unblock action.
- Escalation role.

Acceptance:

- [x] Existing sample data remains fictional.
- [x] No new live-account dependency.
- [x] Replay route shows assignee, SLA / due window, risk, unblock action and escalation role for human-gated items.

### PM-05 Make Approval Workbench Read Like An Approval Product

Status: complete in PM-R5.

Goal: make human approval semantics clearer.

Potential fields:

- Approval scope.
- Expiry / validity.
- Allowed wording.
- Prohibited wording.
- Evidence refs.
- Approval owner.

Acceptance:

- [x] Approval evidence refs remain reviewer context, not a machine-enforced evidence-set gate.
- [x] Q-004 legal approval and Q-002 SME approval stay scoped sample approvals.
- [x] Approval Workbench exposes scope, validity / expiry, allowed wording, prohibited wording, evidence refs and approval owner.

### PM-06 Translate Answer Lineage Into Business Language

Status: complete in PM-R6.

Goal: reduce internal-event reading burden.

Questions to answer:

- Which question produced this answer?
- Which evidence supports it?
- Who challenged or approved it?
- Which risk was contained?

Acceptance:

- [x] Existing lineage remains traceable.
- [x] UI copy becomes easier for non-technical reviewers.
- [x] Evidence lineage includes a business readout for question, evidence confidence, review / approval and contained risk.

### PM-07 Clarify Agent Roles Without Over-Personalizing Them

Status: complete in PM-R7.

Goal: keep agent collaboration understandable and enterprise-safe.

Role copy:

- Decomposer: breaks questionnaire into answer tasks.
- Retriever: attaches approved evidence.
- Drafter: writes bounded answer.
- Reviewer: challenges risky wording.
- Human Approver: approves scoped commitments.

Acceptance:

- [x] `sme-approver` is not presented as an autonomous agent in the role map or approval-facing copy.
- [x] Role Map explains decomposer, retriever, drafter, reviewer and human approver responsibilities.

### PM-08 Evolve Handoff Trace Into A Lightweight Collaboration Map

Status: complete in PM-R8.

Goal: let reviewers investigate the workflow by object, not only by timeline order.

Potential filters:

- By answer.
- By agent.
- By blocker.
- By final-pack status.

Acceptance:

- [x] Raw event log remains available as detail.
- [x] Main route stays compact for video.
- [x] Collaboration Map supports answer, agent, blocker and final-pack-status inspection lenses.

### PM-09 Productize The Replay / Live Boundary Copy

Status: complete in PM-R9.

Goal: make the boundary confident:

> Public replay is the demo-safe evidence path. Live Band mode is separately gated.

Acceptance:

- [x] Replay is never described as live.
- [x] Autonomous replies remain pending unless connected-peer challenge-token evidence exists.
- [x] UI and submission copy use the public replay / separately gated live mode framing.

### PM-10 Add Workspace / Project-List Concept

Goal: future SaaS direction for multiple RFPs/questionnaires.

Acceptance:

- Not submission-critical.
- Should not delay video or final form.

### PM-11 Add Evidence Library Direction

Goal: make evidence a reusable company asset.

Potential evidence types:

- SOC 2.
- ISO.
- DPA.
- Architecture docs.
- Incident policy.

Acceptance:

- Fictional public-safe data only.

### PM-12 Expand Export Workflow

Goal: make the output feel real:

- Customer-safe export.
- Internal review appendix.
- Blocked exceptions.
- Evidence index.

Acceptance:

- Blocked/pending content remains controlled by human/business-owner visibility decisions.

## Current Execution Order

1. PM-01 Final Pack Decision primary product moment.
2. PM-02 Product promise alignment.
3. PM-03 Q-006 buyer-safe story.
4. PM-04 to PM-06 operational workbench polish.
5. PM-07 to PM-09 collaboration/boundary polish.
6. PM-10 to PM-12 post-submit SaaS direction.
