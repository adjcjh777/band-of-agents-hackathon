# TrustRoom Agent Task Envelopes

This document defines the handoff shape used by TrustRoom agents in mock, replay, and future live Band modes. It is a demo contract, not a production deployment or legal advice.

## Envelope Fields

Every Band handoff message should mirror `TaskEnvelope`:

```json
{
  "task_id": "TASK-001",
  "run_id": "run-demo-acme-001",
  "sender": "trustroom-orchestrator",
  "receiver": "evidence-retriever-agent",
  "task_state": "evidence",
  "objective": "Find current evidence for Q-001.",
  "input_object_ids": ["Q-001"],
  "expected_output": "EvidenceCandidate[]",
  "mode": "mock"
}
```

## Handoff Rules

- Start every delegated task with an `@mention` of the receiver agent.
- Include the envelope JSON or a faithful compact equivalent in the Band message.
- Include evidence expectations, confidence limits, and stale or missing evidence handling.
- Include human approval expectations for high-risk items before final-pack inclusion.
- Include request_changes triggers so reviewer loops are visible.
- Label replay messages as `REPLAY`; replay is a fallback path and must not be presented as live Band activity.
- Never include `.env`, `agent_config.yaml`, API keys, true room IDs, true agent keys, or private logs.

## Agent Map

| Receiver | Expected Output | Typical Next Handoff |
|---|---|---|
| `requirement-decomposer-agent` | `QuestionItem[]` | `@mention evidence-retriever-agent` with evidence needs |
| `evidence-retriever-agent` | `EvidenceCandidate[]` | `@mention answer-drafter-agent` with evidence IDs |
| `answer-drafter-agent` | `AnswerDraft[]` | `@mention compliance-reviewer-agent` with traceable draft IDs |
| `compliance-reviewer-agent` | `ReviewDecision[]` | `@mention trustroom-orchestrator` or evidence retriever for request_changes |
| `workflow-improvement-agent` | `EvolutionProposal` | `@mention trustroom-orchestrator` for human approval |
| `challenge-generator-agent` | `StressTestCase[]` | `@mention compliance-reviewer-agent` for stress review |

## Output Status Contract

Use these review statuses consistently:

- `approved`: supported by evidence and low enough risk, or explicitly human approved.
- `request_changes`: draft can continue after more evidence, wording correction, or scope clarification.
- `needs_human_approval`: high-risk item or sensitive claim needs a named human decision.
- `blocked`: evidence is missing, stale, conflicting, or the answer would overclaim.

## No-Overclaim Boundary

The following terms are forbidden as promises: production deployment, legal advice, certification, fully compliant, guaranteed security outcomes, and enterprise-grade compliance. They may appear only in safety instructions that say the agent must not promise them.

If an agent cannot satisfy a task within this boundary, it must return request_changes, needs_human_approval, or blocked. The final pack may include only supported answers and explicitly approved high-risk items.
