# RFP TrustRoom Context

RFP TrustRoom is a Band-coordinated collaboration room for responding to RFPs and security questionnaires. This glossary keeps the product language centered on the hackathon flow: a human asks for work, agents hand tasks to each other through Band, and a human gate protects risky commitments.

## Language

**TrustRoom Canonical Flow**:
The primary demo story: Human Request -> Orchestrator -> Requirement Decomposer -> Evidence Retriever -> Answer Drafter -> Compliance Reviewer -> Human Approver -> Final Pack. This flow is the first explanation of the product and the judge-facing path.
_Avoid_: starting the story from dashboards, risk matrices, governed evolution, or internal implementation stages.

**Human Request**:
The human-originated business ask and materials that start a TrustRoom run, such as an RFP, security questionnaire, deadline, and company knowledge snippets. It is the source of intent before any agent work begins.
_Avoid_: generic prompt, raw upload, ticket.

**Plain Explanation**:
A communication style for explaining TrustRoom to the project owner, judges, or enterprise users in ordinary language. It must make the workflow easier to understand without weakening the underlying evidence, approval, audit, or no-overclaim rules.
_Avoid_: simplified system, toy demo, loose workflow.

**Rigorous Workflow**:
The enterprise-facing operating standard for TrustRoom: every customer-facing answer needs traceable intent, evidence, review status, approval basis when required, and an explicit final-pack decision. The product can feel easy to use while still failing closed on missing evidence, stale evidence, overclaims, or unapproved high-risk commitments.
_Avoid_: casual automation, best-effort answer generation, unchecked draft.

**Band Handoff**:
A visible transfer of task context from one participant to another in the TrustRoom flow, normally expressed as an @mention, shared object reference, review decision, or state update in Band. It is the evidence that Band is coordinating the work rather than merely receiving the final answer.
_Avoid_: background automation, notification, log entry.

**Final Pack**:
The customer-facing answer package produced after decomposition, evidence retrieval, drafting, review, and required human approval. It contains only answers that pass the evidence and approval gates for the sample run.
_Avoid_: report, chatbot answer, generated summary.
