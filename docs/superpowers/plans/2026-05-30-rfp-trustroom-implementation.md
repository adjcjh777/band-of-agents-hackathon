# RFP TrustRoom Enterprise Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` for implementation work, or `superpowers:executing-plans` for single-agent execution. Complete one unchecked task at a time, update this file after each task attempt, and keep commits scoped.

**Goal:** Build an enterprise-user-first RFP TrustRoom working prototype: a Band-coordinated RFP / security questionnaire response workspace where sales, security, product and SME reviewers can see readiness, evidence coverage, risk, approvals, final pack status and governed workflow improvements.

**Architecture:** Start with deterministic local mock/replay so the enterprise workflow is demoable before live Band access is finalized. Keep Band integration behind an adapter. The dashboard renders the same business objects from mock, replay or live events.

**North Star:** In the first 60 seconds, an enterprise user should understand which answers are ready, which are risky, which evidence is missing or stale, who must approve, and why the final pack can or cannot be sent.

**Tech Stack:** Python 3.11, uv, FastAPI, Jinja2 templates, Pydantic models, pytest, JSONL replay store, Band SDK after official access is confirmed.

---

## Goal Execution Contract

- Read `README.md`, `docs/rfp-trustroom-prd.md`, `docs/competition-plan.md`, and `docs/superpowers/specs/2026-05-30-trustroom-governed-evolution-design.md` before starting implementation tasks.
- For Codex + Claude Code parallel work, also read `docs/dual-agent-operating-protocol.md` and `docs/agent-task-ledger.md`.
- Do not read, edit, stage, commit or cite `pilotdeck/` unless the user explicitly asks for it.
- Before edits: `git status --short --branch && git pull --ff-only`.
- Before dispatching or integrating dual-agent work: `uv run python scripts/check_dual_agent_protocol.py`.
- After a Claude Code write-capable task returns and before closing its lock: `uv run python scripts/check_dual_agent_changes.py --task "<Task>"`.
- After edits: run the task verification plus `git diff --check`.
- Commit and push the current branch. Do not assume the branch is `main`.
- Every commit must include only files for the completed task.
- If a task is blocked, write the blocker under that task and continue only if the next task is independent.
- Never commit `.env`, `agent_config.yaml`, API keys, true room ids, true agent keys, private logs or customer data.
- Claude Code uses MiMo v2.5 Pro in this setup and has no multimodal ability. Assign it bounded text/code/test/doc tasks, not Chrome, screenshot, dashboard visual QA or live Band account tasks.
- Codex controller owns file locks, shared entry files, final integration and any Chrome / multimodal / live Band validation.
- Claude Code write-capable dispatch should use `uv run python scripts/run_claude_task.py --task "<Task>" --prompt-file <file>`.
- Direct Claude Code read-only dispatch should use `claude -p --no-session-persistence --strict-mcp-config --mcp-config '{"mcpServers":{}}'` unless the task explicitly requires configured MCP access.

## Dual-Agent Execution Overlay

Coordination reset artifacts:

- `docs/dual-agent-operating-protocol.md`: canonical collaboration rules.
- `docs/agent-task-ledger.md`: active file locks, owner, branch, status and required checks.
- `scripts/check_dual_agent_protocol.py`: machine check for active lock conflicts and forbidden paths.
- `scripts/check_dual_agent_changes.py`: machine check that changed files, including untracked files, stay within active locked paths.
- `scripts/run_claude_task.py`: Codex controller wrapper for safe `claude -p` write-capable dispatch.
- `tests/test_dual_agent_protocol.py`: regression tests for the coordination guardrail.

Parallel execution rule:

- A task can start only after Codex controller adds it to the ledger as `active`.
- Two active rows cannot lock the same file or parent/child path.
- A Claude Code write-capable task is not accepted until `scripts/check_dual_agent_changes.py --task "<Task>"` confirms all changed paths are covered by that task's lock.
- Sensitive Claude Code calls should use strict empty MCP config; the verified empty config shape is `{"mcpServers":{}}`, not `{}`.
- Claude Code write-capable dispatch should default to `Read,Write` only; the controller wrapper, not Claude, runs required checks and git-related commands.
- Shared files such as `README.md`, `pyproject.toml`, `uv.lock`, `AGENTS.md` and public submission docs stay controller-owned unless the ledger explicitly assigns them.
- Claude Code can draft independent docs or code, but Codex controller integrates shared docs and final submission surfaces.
- Every agent branch must return modified files, commands run, risks and status before controller merge.

## Enterprise Product Rules

- The UI should lead with business readiness, not raw agent traces.
- The primary sample must feel like a real enterprise RFP / security questionnaire, while remaining fictional.
- Every answer must preserve source evidence, freshness and review state.
- High-risk commitments, missing evidence, stale evidence and unsupported certification claims fail closed.
- Human approval is a product feature, not an implementation afterthought.
- Governed Evolution is a controlled playbook improvement loop, not autonomous code mutation.
- Replay is an honest fallback and must be labeled as replay.

## Model Routing Rules

| Work type | Default model | Why | Escalate when |
|---|---|---|---|
| Fictional sample material, judge copy, runbook prose | 5.3codex spark | Cheap, creative, document-heavy | Output contradicts enterprise safety or PRD |
| Isolated models, schema tests, fixture evals, prompt files, small scripts | 5.4 | Good for bounded code with tests | Cross-module state or flaky behavior appears |
| Main implementation: state machine, mock runner, dashboard, adapter integration | 5.5 中 | Needs repo context and product judgment | Architecture has to change or debugging repeats twice |
| Band live integration, public repo conversion, final no-secret/security review | 5.5 超高 | External dependencies and high blast radius | Use sparingly |

## Todo Board

- [x] T0: Repo scaffold and dependency baseline
- [x] T0.5: Enterprise architecture and plan alignment
- [x] T1: Enterprise domain contracts and state machine
- [x] T2: Band-compatible adapter and event mirror
- [x] T3: Primary enterprise sample pack and replay fixture
- [x] T4: Deterministic mock agent runner with review loop
- [x] T5: Governed evolution engine and experience ledger
- [x] T6: Readiness, safety and no-secret gates
- [x] T7: Enterprise dashboard MVP
- [x] T8: Agent prompts and task envelopes
- [ ] T9: Band live integration
- [x] T10: Judge docs, demo runbook and evidence report
- [ ] T11: Deployment and public submission hardening
- [ ] T12: Final end-to-end rehearsal
- [x] T14: Official page refresh and multi-agent execution alignment
- [x] T15: Live autonomous reply smoke harness
- [x] T16: Enterprise reviewer cockpit polish
- [x] T17: Enterprise answer copy and SME follow-up polish
- [x] T18: Evidence lineage drilldown

## File Map

- `src/trustroom/models.py`: enterprise domain contracts.
- `src/trustroom/state_machine.py`: workflow transitions and final pack gating.
- `src/trustroom/band/adapter.py`: mock/replay/live Band boundary.
- `src/trustroom/replay.py`: JSONL replay read/write.
- `src/trustroom/sample_loader.py`: fictional sample pack loader.
- `src/trustroom/agents/mock_runner.py`: deterministic multi-agent workflow.
- `src/trustroom/evolution.py`: proposal validation, lesson activation and rollback.
- `src/trustroom/readiness.py`: business readiness checks.
- `src/trustroom/web/app.py`: FastAPI routes.
- `src/trustroom/web/templates/*.html`: enterprise dashboard.
- `src/trustroom/agents/prompts/*.md`: agent prompts and output schemas.
- `samples/acme-security-rfp/*`: primary fictional enterprise case.
- `samples/fintech-vendor-ddq/*`: optional later sample, not on the critical path.
- `reports/trustroom_replay.example.jsonl`: committed replay fixture.
- `scripts/run_trustroom_replay.py`: CLI replay runner.
- `scripts/check_trustroom_readiness.py`: local readiness gate.
- `scripts/check_no_secrets.py`: public submission safety gate.
- `docs/judge-10-minute-experience.md`, `docs/demo-runbook.md`, `docs/demo-evidence-report.md`: submission support.

## T0: Repo Scaffold And Dependency Baseline

Recommended model: 5.5 中.

Status: complete in commit `4199ed7`.

Done when:

- Fresh checkout can install dependencies with `uv sync`.
- Repo contains project directories and no secret-like files.

## T0.5: Enterprise Architecture And Plan Alignment

Recommended model: 5.5 中.

Status: complete when this plan and the governed evolution spec are committed.

Boundary:

- Documentation only.
- Do not implement code or create sample data.

Todo:

- [x] Read the project directory except `pilotdeck/`.
- [x] Update the governed evolution spec with enterprise user frame, value criteria, business-facing dashboard requirements and domain additions.
- [x] Rewrite this implementation plan so tasks build the enterprise workflow before polish.
- [x] Keep the scope to RFP TrustRoom, not a generic self-evolving agent platform.

Verification:

- [x] `git diff --check` exits 0.
- [x] Spec and plan both mention enterprise readiness, evidence coverage, approval queue and no-overclaim boundaries.

Commit:

- [x] `git add docs/superpowers/specs/2026-05-30-trustroom-governed-evolution-design.md docs/superpowers/plans/2026-05-30-rfp-trustroom-implementation.md`
- [x] `git commit -m "docs: align TrustRoom plan with enterprise workflow"`
- [x] `git push origin current_branch`

Done when:

- A future agent can implement from this plan without relying on chat history.

## T1: Enterprise Domain Contracts And State Machine

Recommended model: 5.5 中. Use 5.4 for isolated tests after contracts are defined.

Boundary:

- Implement data contracts and state transitions only.
- Do not call LLMs, Band or render dashboard pages.

Todo:

- [x] Create `src/trustroom/models.py`.
- [x] Add models: `CustomerCase`, `Run`, `QuestionItem`, `EvidenceCandidate`, `AnswerDraft`, `ReviewDecision`, `ApprovalDecision`, `FinalSubmissionPack`, `TimelineEvent`, `TaskEnvelope`, `EvolutionProposal`, `ExperienceLesson`, `StressTestCase`.
- [x] Add enums for mode, run state, risk level, evidence freshness, review status, approval decision, proposal status and event type.
- [x] Create `src/trustroom/state_machine.py` with allowed states: `intake`, `triage`, `decomposition`, `evidence`, `drafting`, `review`, `approval`, `submission_pack`, `post_run_review`, `evolution_review`.
- [x] Enforce rule: high-risk, missing-evidence, stale-evidence or unsupported-certification items cannot enter final pack unless explicitly approved or resolved.
- [x] Create `tests/test_models.py`.
- [x] Create `tests/test_state_machine.py`.

Verification:

- [x] `uv run pytest tests/test_models.py tests/test_state_machine.py -v` passes.
- [x] Tests include a high-risk unapproved answer and expect finalization to fail.
- [x] Tests include a low-risk answer with current evidence and expect finalization to pass.
- [x] Tests include a stale evidence answer and expect `needs_review` or blocked behavior.
- [x] `git diff --check` exits 0.

Commit:

- [x] `git add src/trustroom/models.py src/trustroom/state_machine.py tests/test_models.py tests/test_state_machine.py`
- [x] `git commit -m "feat: add TrustRoom enterprise contracts"`
- [x] `git push origin $(git branch --show-current)`

Done when:

- Enterprise workflow objects are typed and final-pack gating is enforced by tests.

## T2: Band-Compatible Adapter And Event Mirror

Recommended model: 5.5 中 for adapter design, 5.4 for tests.

Boundary:

- Build the mock/replay/live boundary.
- Do not implement real Band API calls yet.

Todo:

- [x] Create `src/trustroom/band/adapter.py`.
- [x] Define adapter methods: `create_room`, `send_message`, `mention_agent`, `record_event`, `get_room_timeline`, `redact_ref`.
- [x] Implement `MockBandAdapter` using in-memory or JSONL-backed timeline events.
- [x] Ensure adapter emits mode-independent `TimelineEvent` records.
- [x] Create `tests/test_band_adapter.py`.
- [x] Add `.env.example` with non-secret variable names only: `BAND_API_BASE`, `BAND_AGENT_ID`, `BAND_AGENT_KEY`.

Verification:

- [x] `uv run pytest tests/test_band_adapter.py -v` passes.
- [x] Tests prove sender, receiver, event type, task state and redacted Band reference are preserved.
- [x] `rg -n "BAND_.*=.+[A-Za-z0-9]{12,}" .env.example README.md src tests` returns no real-looking secret.
- [x] `git diff --check` exits 0.

Commit:

- [x] `git add src/trustroom/band/adapter.py tests/test_band_adapter.py .env.example`
- [x] `git commit -m "feat: add Band adapter boundary"`
- [x] `git push origin $(git branch --show-current)`

Done when:

- Mock and replay can share the same event boundary that live Band will later use.

## T3: Primary Enterprise Sample Pack And Replay Fixture

Recommended model: 5.3codex spark for draft fixture text, then 5.4 for validation.

Boundary:

- Fictional data only.
- Do not use real customer names, copied questionnaires, true policies or private company docs.
- Do not build the optional second sample yet unless the primary path is complete.

Todo:

- [x] Create `samples/acme-security-rfp/case.json` with customer profile, deadline, submission owner and business goal.
- [x] Create `samples/acme-security-rfp/rfp.md` with at least 8 realistic fictional customer requirements.
- [x] Create `samples/acme-security-rfp/questionnaire.csv` with at least 8 rows and columns `id,question,category,risk_hint,required_evidence_type,business_owner`.
- [x] Create `samples/acme-security-rfp/knowledge.json` with at least 12 evidence snippets, including current, stale, missing and conflicting cases.
- [x] Create `src/trustroom/sample_loader.py`.
- [x] Create `tests/test_sample_loader.py`.
- [x] Create `reports/trustroom_replay.example.jsonl` with a complete business workflow: intake, triage, 3+ agent handoffs, one review loop, human approval, final pack, evolution proposal and accepted lesson.

Verification:

- [x] `uv run pytest tests/test_sample_loader.py -v` passes.
- [x] `wc -l reports/trustroom_replay.example.jsonl` is at least 18.
- [x] `rg -n "real customer|API key|room_|agent_key|secret" samples reports` returns no sensitive-looking placeholder.
- [x] Replay includes `REPLAY` mode, evidence coverage, approval queue and final pack events.
- [x] `git diff --check` exits 0.

Commit:

- [x] `git add samples/acme-security-rfp reports/trustroom_replay.example.jsonl src/trustroom/sample_loader.py tests/test_sample_loader.py`
- [x] `git commit -m "feat: add TrustRoom enterprise sample"`
- [x] `git push origin $(git branch --show-current)`

Done when:

- One strong enterprise sample is better than two thin samples.

## T4: Deterministic Mock Agent Runner With Review Loop

Recommended model: 5.5 中.

Boundary:

- Deterministic local workflow only.
- Do not call real Band, external LLMs or internet APIs.

Todo:

- [x] Create `src/trustroom/agents/mock_runner.py`.
- [x] Implement deterministic roles: orchestrator, requirement decomposer, evidence retriever, answer drafter, compliance reviewer, SME approver.
- [x] Include one non-linear loop: reviewer sends item back to retriever or drafter.
- [x] Include one escalation scenario for high-risk SLA, unsupported certification or stale policy.
- [x] Make runner output typed `TimelineEvent` records and `FinalSubmissionPack`.
- [x] Create `tests/test_mock_runner.py`.

Verification:

- [x] `uv run pytest tests/test_mock_runner.py -v` passes.
- [x] Test confirms at least 3 distinct agent senders.
- [x] Test confirms a reviewer-to-retriever or reviewer-to-drafter loop.
- [x] Test confirms high-risk item requires SME approval before final pack inclusion.
- [x] Test confirms final pack has evidence index and blockers.
- [x] `git diff --check` exits 0.

Commit:

- [x] `git add src/trustroom/agents/mock_runner.py tests/test_mock_runner.py`
- [x] `git commit -m "feat: add TrustRoom mock agent workflow"`
- [x] `git push origin $(git branch --show-current)`

Done when:

- The enterprise collaboration path is visible without external services.

## T5: Governed Evolution Engine And Experience Ledger

Recommended model: 5.5 中 for design, 5.4 for unit tests.

Boundary:

- Implement proposal and lesson logic only.
- Do not implement source-code rewriting, model training or automatic deployment.

Todo:

- [x] Create `src/trustroom/evolution.py`.
- [x] Generate or validate `EvolutionProposal` records from completed run artifacts.
- [x] Require supporting timeline event ids for every proposal.
- [x] Implement proposal status transitions: `pending_review`, `approved`, `rejected`, `request_changes`, `deferred`.
- [x] Implement `ExperienceLesson` activation only after human approval.
- [x] Implement lesson rollback by marking inactive and preserving `rollback_note`.
- [x] Create `tests/test_evolution.py`.

Verification:

- [x] `uv run pytest tests/test_evolution.py -v` passes.
- [x] Proposal without supporting events cannot become active.
- [x] Proposal that weakens human approval or no-overclaim gate is rejected.
- [x] Approved lesson can be loaded into the next run context.
- [x] `git diff --check` exits 0.

Commit:

- [x] `git add src/trustroom/evolution.py tests/test_evolution.py`
- [x] `git commit -m "feat: add governed evolution ledger"`
- [x] `git push origin $(git branch --show-current)`

Done when:

- Governed Evolution is a tested product loop, not just copy in the spec.

## T6: Readiness, Safety And No-Secret Gates

Recommended model: 5.4.

Boundary:

- Local checks only.
- Do not add production monitoring or heavyweight benchmark tooling.

Todo:

- [x] Create `src/trustroom/readiness.py`.
- [x] Create `scripts/check_trustroom_readiness.py`.
- [x] Check primary sample loads and has 8+ question items.
- [x] Check replay loads in under 5 seconds.
- [x] Check evidence coverage is at least 80% or items are explicitly `needs_review` / `blocked`.
- [x] Check 100% high-risk items are `needs_human_approval`, `approved`, `request_changes` or `blocked`.
- [x] Check no-overclaim words are caught: `production-ready`, `certified`, `fully compliant`, `guaranteed`, `enterprise-grade compliance`.
- [x] Create `scripts/check_no_secrets.py`.
- [x] Create `tests/test_readiness.py` and `tests/test_no_secrets.py`.

Verification:

- [x] `uv run python scripts/check_trustroom_readiness.py` exits 0.
- [x] `uv run python scripts/check_no_secrets.py` exits 0.
- [x] `uv run pytest tests/test_readiness.py tests/test_no_secrets.py -v` passes.
- [x] Temporarily injecting an unapproved high-risk item makes readiness fail; do not commit the injected failure.
- [x] `git diff --check` exits 0.

Commit:

- [x] `git add src/trustroom/readiness.py scripts/check_trustroom_readiness.py scripts/check_no_secrets.py tests/test_readiness.py tests/test_no_secrets.py`
- [x] `git commit -m "feat: add TrustRoom readiness gates"`
- [x] `git push origin $(git branch --show-current)`

Done when:

- One command can protect the enterprise demo from unsafe claims and broken workflow state.

## T7: Enterprise Dashboard MVP

Recommended model: 5.5 中. Use 5.3codex spark only for copy after rendering works.

Boundary:

- Render local mock/replay data in an enterprise-useful dashboard.
- Do not introduce a new frontend build system unless unavoidable.

Todo:

- [x] Create `src/trustroom/web/app.py` with routes `/`, `/runs/demo`, `/runs/demo/replay`, `/health`.
- [x] Create `src/trustroom/web/templates/base.html`, `index.html`, `run.html`.
- [x] First viewport: Case Brief, Submission Readiness, Evidence Coverage, Approval Queue, Risk Flags and Final Pack.
- [x] Secondary sections: Answer Pack, Band Collaboration Timeline, Governed Evolution, Replay / Live Evidence.
- [x] Add clear `MOCK`, `REPLAY` or `LIVE` badge.
- [x] Create `tests/test_web_app.py` using FastAPI TestClient.

Verification:

- [x] `uv run pytest tests/test_web_app.py -v` passes.
- [x] `uv run uvicorn trustroom.web.app:app --reload` starts without import errors.
- [x] Browser or curl check: `/health` returns OK.
- [x] `/runs/demo/replay` includes "RFP TrustRoom", "Submission Readiness", "Evidence Coverage", "Approval Queue", "Human approval", "Governed Evolution" and "REPLAY".
- [x] `git diff --check` exits 0.

Commit:

- [x] `git add src/trustroom/web tests/test_web_app.py pyproject.toml uv.lock`
- [x] `git commit -m "feat: add TrustRoom enterprise dashboard"`
- [x] `git push origin $(git branch --show-current)`

Done when:

- A sales or security reviewer can understand the case status before reading raw timeline events.

## T8: Agent Prompts And Task Envelopes

Recommended model: 5.4 for prompt structure; 5.3codex spark for wording variants.

Boundary:

- Define prompts, output schemas and Band task envelopes.
- Do not call external LLMs yet.

Todo:

- [x] Create `src/trustroom/agents/prompts/orchestrator.md`.
- [x] Create `src/trustroom/agents/prompts/requirement_decomposer.md`.
- [x] Create `src/trustroom/agents/prompts/evidence_retriever.md`.
- [x] Create `src/trustroom/agents/prompts/answer_drafter.md`.
- [x] Create `src/trustroom/agents/prompts/compliance_reviewer.md`.
- [x] Create `src/trustroom/agents/prompts/workflow_improvement.md`.
- [x] Create `src/trustroom/agents/prompts/challenge_generator.md`.
- [x] Each prompt must include role, enterprise job, input contract, output JSON schema, refusal/no-overclaim boundary and Band handoff instruction.
- [x] Create `docs/agent-task-envelopes.md`.

Verification:

- [x] `uv run pytest tests/test_agent_prompts.py -v` passes.
- [x] `rg -n "production deployment|legal advice|certification|fully compliant" src/trustroom/agents/prompts docs/agent-task-envelopes.md` shows these are forbidden, not promised.
- [x] `rg -n "@mention|handoff|evidence|human approval|request_changes" src/trustroom/agents/prompts` returns hits in each prompt.
- [x] `git diff --check` exits 0.

Commit:

- [x] `git add src/trustroom/agents/prompts docs/agent-task-envelopes.md tests/test_agent_prompts.py`
- [x] `git commit -m "docs: add TrustRoom agent prompts"`
- [x] `git push origin $(git branch --show-current)`

Done when:

- Another agent can implement live or LLM-backed agents without inventing roles or weakening enterprise gates.

## T9: Band Live Integration

Recommended model: 5.5 超高 for live integration.

Boundary:

- Implement live adapter only after official access is confirmed.
- Do not commit credentials, true room ids or true agent keys.

Todo:

- [x] Re-read official Band docs with Chrome if live API details may have changed.
- [x] Create `LiveBandAdapter` behind the same interface as `MockBandAdapter`.
- [x] Create at least 3 Band Remote Agents for orchestrator, evidence/retrieval or drafting, and reviewer roles.
- [x] Record a redacted live REST evidence packet showing room creation, @mention handoff and reviewer decision.
- [ ] Verify SDK/WebSocket Remote Agents autonomously receive @mentions and reply.
- [x] Document setup in README without exposing secrets.
- [x] Create `tests/test_live_adapter_contract.py` using mock/stubbed responses only.

Current note:

- 2026-06-13: Codex completed the credential-free live REST adapter contract and official API doc refresh. The real Band Remote Agent creation and redacted live evidence packet are intentionally still unchecked because they require runtime credentials / one-time API keys and must not be copied into repo files.
- 2026-06-13 later: real Band REST smoke and Chrome live verification passed. Evidence remains redacted/ignored outside Git. Peer agents still showed Disconnected, so complete autonomous SDK/WebSocket replies remain unchecked.
- 2026-06-13 T15: autonomous reply smoke harness now exists and fails closed, but the current ignored env dry-run is still blocked by missing REST base / peer directory. It has not produced a real SDK/WebSocket autonomous reply confirmation.

Verification:

- [x] `uv run pytest tests/test_live_adapter_contract.py -v` passes.
- [x] Mock/replay path still passes readiness.
- [x] Live REST evidence packet is redacted.
- [ ] SDK/WebSocket autonomous reply path is verified with a real Remote Agent reply.
- [x] `uv run python scripts/check_no_secrets.py` exits 0.
- [x] `git diff --check` exits 0.

Commit:

- [ ] `git add src/trustroom/band README.md tests/test_live_adapter_contract.py reports`
- [ ] `git commit -m "feat: add Band live adapter"`
- [ ] `git push origin $(git branch --show-current)`

Done when:

- Live Band is a narrow optional path, and the demo remains safe if live access fails.

## T10: Judge Docs, Demo Runbook And Evidence Report

Recommended model: 5.3codex spark for drafts, 5.4 for consistency review, Codex final review before commit.

Boundary:

- Write judge-facing docs for the exact implemented MVP.
- Do not invent features that are absent from dashboard, replay or live evidence.

Todo:

- [x] Create `docs/judge-10-minute-experience.md`.
- [x] Create `docs/demo-runbook.md`.
- [x] Create `docs/demo-evidence-report.md`.
- [x] Include enterprise route: Case Brief -> Readiness -> Evidence -> Approval -> Final Pack -> Evolution.
- [x] Include live path and replay fallback, clearly labeled.
- [x] Include no-overclaim language: hackathon demo / working prototype only.
- [x] Include 5-minute video structure aligned with RFP TrustRoom.

Verification:

- [x] `rg -n "production|enterprise-ready deployment|fully automated compliance|legal advice|certified" docs/judge-10-minute-experience.md docs/demo-runbook.md docs/demo-evidence-report.md` returns no overclaim unless listed as forbidden wording.
- [x] `rg -n "Submission Readiness|Evidence Coverage|Approval Queue|replay|fallback|Band|human approval|Governed Evolution" docs/judge-10-minute-experience.md docs/demo-runbook.md docs/demo-evidence-report.md` returns useful hits.
- [x] `git diff --check` exits 0.

Commit:

- [x] `git add docs/judge-10-minute-experience.md docs/demo-runbook.md docs/demo-evidence-report.md`
- [x] `git commit -m "docs: add TrustRoom judge materials"`
- [x] `git push origin $(git branch --show-current)`

Done when:

- A fresh evaluator can run the demo route from docs without chat context.

## T11: Deployment And Public Submission Hardening

Recommended model: 5.5 中 for deployment; 5.5 超高 for final public repo and secret audit.

Boundary:

- Make demo runnable in a public-safe way.
- Do not switch the current private repository to public until the user explicitly approves.

Todo:

- [x] Add a public-safe run command to README.
- [x] Add `LICENSE` with MIT license if not already present.
- [x] Add deployment notes for the chosen platform.
- [ ] Decide with user: make current repo public or create a separate sanitized public submission repo.
- [x] Run no-secret checks against staged files and submission docs.

Verification:

- [x] `uv run python scripts/check_no_secrets.py` exits 0.
- [x] `uv run python scripts/check_trustroom_readiness.py` exits 0.
- [x] `git status --short --ignored` does not show secrets staged or tracked.
- [x] `git diff --check` exits 0.

Commit:

- [ ] `git add README.md LICENSE docs/submission-checklist.md`
- [ ] `git commit -m "chore: harden TrustRoom submission"`
- [ ] `git push origin $(git branch --show-current)`

Done when:

- Repo can be shared safely after the user chooses the public repo strategy.

## T12: Final End-To-End Rehearsal

Recommended model: 5.5 超高 for final review, with 5.3codex spark only for caption/copy tweaks.

Boundary:

- Verify the complete judging path.
- Do not add new architecture or major features.

Todo:

- [x] Run all tests.
- [x] Run readiness check.
- [x] Run no-secret check.
- [x] Start dashboard and open the demo path.
- [x] Verify first viewport answers enterprise readiness questions.
- [x] Verify replay fallback loads and is labeled as replay.
- [ ] Verify Band live path if credentials and official access exist.
- [x] Verify README, judge route, runbook and submission checklist match the actual app.
- [x] Record unresolved issues in `docs/submission-checklist.md` rather than hiding them.

Current note:

- 2026-06-13: Replay rehearsal passed in Browser at `/runs/demo/replay`; mock route passed at `/runs/demo`; `/health` returned 200 via curl and tests. REST live smoke and Chrome live verification later passed, but autonomous SDK/WebSocket replies are not yet verified. Final rehearsal must present replay fallback honestly unless that gate passes.

Verification:

- [x] `uv run pytest -v` passes.
- [x] `uv run python scripts/check_trustroom_readiness.py` passes.
- [x] `uv run python scripts/check_no_secrets.py` passes.
- [x] Manual demo completes in under 10 minutes using either live path or replay fallback.
- [x] `git diff --check` exits 0.

Commit:

- [ ] `git add README.md docs/submission-checklist.md docs/demo-runbook.md`
- [ ] `git commit -m "docs: record TrustRoom final rehearsal"`
- [ ] `git push origin $(git branch --show-current)`

Done when:

- The demo can be shown to a judge without relying on chat memory.
- Known gaps are explicit and do not contradict no-overclaim boundaries.

## T14: Official Page Refresh And Multi-Agent Execution Alignment

Recommended model: 5.5 中.

Boundary:

- Documentation and coordination only.
- Do not change application code, credentials, dependency locks, live room ids, true agent keys or `pilotdeck/`.
- Use Chrome for official page facts, because competition terms can change.

Todo:

- [x] Re-read the official lablab Band of Agents page with Chrome on 2026-06-13.
- [x] Update official facts: `$10,000+` prize pool, AI/ML API + Featherless AI partners, Band Pro `BANDHACK26`, Featherless `BOA26`, submission deadline and schedule.
- [x] Align README, official research, competition plan, submission checklist, judge route, runbook, evidence report, deployment notes and project concept with current evidence.
- [x] Keep live REST smoke, replay fallback and autonomous SDK/WebSocket replies separate in public claims.
- [x] Dispatch next tasks to executor and tester through Agent Bus visible thread messages.
- [x] Close this ledger task after checks pass and task dispatch is complete.

Verification:

- [x] Chrome official page reread completed.
- [x] `uv run python scripts/check_dual_agent_protocol.py` passes after adding T14 active lock.
- [x] `uv run python scripts/check_no_secrets.py` exits 0.
- [x] `uv run python scripts/check_trustroom_readiness.py` exits 0.
- [x] `git diff --check` exits 0.

Done when:

- Future agents can pick up from docs without relying on chat.
- Executor has a bounded live/autonomous reply task.
- Tester has a bounded fresh-checkout/readiness/browser/submission audit task.

## T15: Live Autonomous Reply Smoke Harness

Recommended model: 5.5 超高 for live integration.

Owner:

- Agent Bus executor thread `019ec04e-8a30-7430-af1c-a192ed9c14f4`.

Boundary:

- Allowed locked paths are `scripts/run_live_band_autonomous_smoke.py`, `tests/test_live_band_autonomous_smoke.py`, `src/trustroom/band/live_adapter.py`, and `tests/test_live_adapter_contract.py`.
- Do not edit docs, README, `.env`, `agent_config.yaml`, true room ids, true agent keys, API keys, live logs or `pilotdeck/`.
- Real credentials may only be read from the user-controlled ignored environment, never printed or committed.

Todo:

- [x] Create a narrow autonomous live smoke harness that verifies Remote Agents can receive @mentions through SDK/WebSocket and send replies, or returns a precise blocked status if the platform/account is not ready.
- [x] Keep REST smoke, Band room evidence and autonomous replies as separate result fields.
- [x] Add tests with stubs/fakes only; tests must not require real Band credentials.
- [x] Preserve existing REST live smoke behavior.

Current note:

- 2026-06-13: Agent Bus executor implemented `scripts/run_live_band_autonomous_smoke.py` on `feature/trustroom-live-autonomous-replies`; Codex controller merged it and added fail-closed peer-resolution handling. The harness returns `DONE` only when a non-mention Band message contains the challenge token; missing credentials, missing peer directory, unresolved peer handles or no reply return `BLOCKED`.
- 2026-06-13 dry-run against the ignored local env returned `BLOCKED` because `BAND_REST_URL` / `BAND_API_BASE` and `TRUSTROOM_BAND_PEERS_JSON` were not available. This does not verify real SDK/WebSocket autonomous replies.

Verification:

- [x] `uv run pytest tests/test_live_band_autonomous_smoke.py tests/test_live_adapter_contract.py -v` passes.
- [x] `uv run pytest tests/test_live_band_smoke.py -v` passes.
- [x] `uv run python scripts/check_no_secrets.py` exits 0.
- [x] `git diff --check` exits 0.

Done when:

- Executor/controller integration returns either `DONE` with redacted evidence path / summary, or `BLOCKED` with exact missing Band/SDK/WebSocket condition. Current integration result is `DONE_WITH_CONCERNS`: harness complete, real autonomous reply still unverified.

## T16: Enterprise Reviewer Cockpit Polish

Recommended model: 5.5 中 for product judgment plus bounded web/test edits.

Owner:

- Codex controller thread `019ec041-0e14-7e23-9f27-be6890b12288`.

Boundary:

- Allowed locked paths are `src/trustroom/web/app.py`, `src/trustroom/web/templates/`, `tests/test_web_app.py`, `README.md`, `docs/demo-runbook.md`, `docs/demo-evidence-report.md`, this plan and `docs/agent-task-ledger.md`.
- Do not edit `pilotdeck/`, live credentials, ignored local evidence, `agent_config.yaml` or submission assets in this task.
- Keep the UI honest: sample evidence is fictional/redacted, replay is a fallback, and this is not a formal audit or production GRC workflow.

Agent feedback integrated:

- Enterprise Sales Engineer / Proposal Lead: first-screen decision strip, next actions, case brief derived from sample data, owner accountability and final-pack explanation.
- Enterprise Security Reviewer / SME Approver: reviewer decision matrix, evidence title/snippet/freshness/confidence, approval basis, Q-006 gate reasons and per-answer trace chips.

Todo:

- [x] Replace hard-coded dashboard brief fields with sample-derived case, customer, materials, deadline and owner context.
- [x] Add a first-screen decision strip that tells the proposal lead whether the pack is sendable, sendable with exclusions or blocked.
- [x] Promote blocked next actions above raw metrics, including Q-006 policy-owner follow-up.
- [x] Add reviewer decision matrix rows with draft, risk, evidence detail, review status, human approval basis, final-pack status and trace IDs.
- [x] Surface stale, missing and conflicting evidence without hiding it behind global coverage counts.
- [x] Add reviewer-facing UI contract tests for Q-002, Q-004 and Q-006.

Current note:

- 2026-06-13: `/runs/demo/replay` now reads as an enterprise approval cockpit: 7/8 answers can enter the pack, Q-006 is explicitly excluded, Q-002 and Q-004 show approval basis, and evidence cards show `Incident Response Policy v2024.11`, `Support Addendum Draft` and `EU Residency Gap Note` with freshness and action copy.

Verification:

- [x] `uv run pytest tests/test_web_app.py -v` passes.
- [x] Browser/local server smoke confirms `/runs/demo/replay` renders the decision matrix and evidence cards.
- [x] Mobile browser smoke confirms no horizontal overflow.
- [x] `uv run python scripts/check_no_secrets.py` exits 0.
- [x] `uv run python scripts/check_trustroom_readiness.py` exits 0.
- [x] `uv run pytest -v` passes.
- [x] `git diff --check` exits 0.

Done when:

- Proposal lead and SME reviewer can answer from the first two screens: can this pack move forward, what is excluded, who owns the blocker, which evidence supports each answer, and who approved high-risk language.

## T17: Enterprise Answer Copy And SME Follow-Up Polish

Recommended model: 5.5 中 for product and risk wording.

Owner:

- Codex controller thread `019ec041-0e14-7e23-9f27-be6890b12288`.

Boundary:

- Allowed locked paths are `src/trustroom/agents/mock_runner.py`, `tests/test_mock_runner.py`, `tests/test_web_app.py`, this plan and `docs/agent-task-ledger.md`.
- Do not touch live Band credentials, deployment, public submission claims, `pilotdeck/`, `README.md` or top-level submission docs in this task.
- Keep every sample answer fictional, bounded and customer-safe; Q-006 must remain blocked and must not quote an unapproved notification target.

Todo:

- [x] Replace generic `Draft answer for Q-* grounded in available evidence.` text with evidence-backed answer copy for all sample questions.
- [x] Preserve Q-004 bounded region-processing language and Q-006 blocked incident-response boundary.
- [x] Add SME / reviewer follow-up text for high-risk approval records and blocked Q-006.
- [x] Extend tests so generic draft copy cannot return silently.
- [x] Extend web contract tests for visible SME follow-up text.

Verification:

- [x] `uv run pytest tests/test_mock_runner.py tests/test_web_app.py -v` passes.
- [x] Chrome/Playwright `/runs/demo/replay` smoke passes with customer-safe answer copy visible.
- [x] `uv run python scripts/check_no_secrets.py` exits 0.
- [x] `uv run python scripts/check_trustroom_readiness.py` exits 0.
- [x] `uv run pytest -v` passes.
- [x] `git diff --check` exits 0.

Done when:

- A proposal lead or SME reviewer can read the sample answer text itself, not just the evidence IDs, and see which answers are safe to send, approved with boundaries or blocked pending owner confirmation.

## T18: Evidence Lineage Drilldown

Recommended model: 5.5 中 for cross-module product workflow.

Owner:

- Codex controller thread `019ec041-0e14-7e23-9f27-be6890b12288`.

Research source:

- GitHub Product Research Agent thread `019ec159-c870-71d3-bbb2-65d1f086014a` recommended a lightweight DataHub/OpenMetadata-style answer lineage: Answer -> Evidence -> Review -> Approval -> Final Pack.

Boundary:

- Allowed locked paths are `src/trustroom/models.py`, `src/trustroom/agents/mock_runner.py`, `src/trustroom/web/app.py`, `src/trustroom/web/templates/base.html`, `src/trustroom/web/templates/run.html`, `tests/test_models.py`, `tests/test_mock_runner.py`, `tests/test_web_app.py`, this plan and `docs/agent-task-ledger.md`.
- Do not edit live Band credentials, deployment, public submission claims, official page docs, `pilotdeck/`, or ignored evidence reports.
- Keep lineage as demo/sample traceability, not formal audit evidence.

Todo:

- [x] Add typed lineage objects that connect question source, answer draft, evidence refs, review decision, approval decision and final-pack decision.
- [x] Generate lineage for every mock answer, including Q-006 excluded/fail-closed path.
- [x] Render a compact lineage drilldown in the reviewer cockpit without hiding existing evidence cards.
- [x] Add tests for Q-002/Q-004/Q-006 lineage stages and final-pack reason visibility.
- [x] Browser smoke `/runs/demo/replay` after UI changes.

Verification:

- [x] `uv run pytest tests/test_models.py tests/test_mock_runner.py tests/test_web_app.py -v` passes.
- [x] Browser smoke for `/runs/demo/replay` passes with lineage text visible.
- [x] `uv run python scripts/check_no_secrets.py` exits 0.
- [x] `uv run python scripts/check_trustroom_readiness.py` exits 0.
- [x] `uv run pytest -v` passes.
- [x] `git diff --check` exits 0.

Done when:

- Q-002, Q-004 and Q-006 each show a traceable chain from question source to evidence, review, approval or missing approval, and final-pack inclusion/exclusion reason.

T18.1 precision polish:

- [x] Tester audit noted the compact subtitle said `Answer -> Evidence -> Review -> Approval -> Final Pack` while the actual typed lineage starts at question intake and includes draft.
- [x] Subtitle and web contract test now use `Question -> Evidence -> Draft -> Review -> Approval -> Final Pack`.

## T19: Approval Scope And Expiry Gate

Recommended model: 5.5 中 for governance semantics plus bounded UI/test edits.

Owner:

- Codex controller thread `019ec041-0e14-7e23-9f27-be6890b12288`.

Research source:

- GitHub Product Research Agent thread `019ec159-c870-71d3-bbb2-65d1f086014a` recommended Temporal/Windmill/Camunda-style approval workbench concepts: scope, expiry, owner, artifact trail and fail-closed blocked items.

Boundary:

- Allowed locked paths are `src/trustroom/models.py`, `src/trustroom/state_machine.py`, `src/trustroom/agents/mock_runner.py`, `src/trustroom/web/app.py`, `src/trustroom/web/templates/base.html`, `src/trustroom/web/templates/run.html`, `tests/test_models.py`, `tests/test_state_machine.py`, `tests/test_mock_runner.py`, `tests/test_web_app.py`, this plan and `docs/agent-task-ledger.md`.
- Do not edit live Band credentials, deployment docs, public submission claims, official page docs, `pilotdeck/`, ignored evidence reports or final media assets.
- Keep the wording bounded: approval scope/expiry is demo/sample governance, not a production GRC approval engine or formal legal sign-off.

Todo:

- [x] Extend approval decisions with explicit customer-safe scope, expiry label/status and optional applicable evidence refs.
- [x] Update final-pack gate so high-risk approvals only unblock answers when the approval is still valid for the current item.
- [x] Populate Q-002 and Q-004 with scoped, valid approvals while leaving Q-006 fail-closed without approval.
- [x] Render scope/expiry/follow-up in the Approval Workbench, reviewer matrix and lineage approval step.
- [x] Add tests that expired/out-of-scope approvals fail closed and visible UI copy does not regress.
- [x] Browser smoke `/runs/demo/replay` after UI changes.

Current note:

- 2026-06-13: Q-002 and Q-004 approvals now show scope, validity, expiry label and approved evidence refs in the reviewer matrix, approval workbench and lineage step. The final-pack gate only treats `approve + valid + matching answer_id` as an unblocking human approval; expired or answer-mismatched approvals fail closed. Q-006 still has no approval record and remains excluded.

Verification:

- [x] `uv run pytest tests/test_models.py tests/test_state_machine.py tests/test_mock_runner.py tests/test_web_app.py -v` passes.
- [x] Browser smoke for `/runs/demo/replay` passes on desktop and mobile.
- [x] `uv run python scripts/check_no_secrets.py` exits 0.
- [x] `uv run python scripts/check_trustroom_readiness.py` exits 0.
- [x] `uv run pytest -v` passes.
- [x] `git diff --check` exits 0.

Done when:

- A security reviewer can see not only that a high-risk answer was approved, but exactly what sample wording/evidence the approval covers, whether it is still valid, and why unapproved or invalid approvals cannot enter the final pack.

## Suggested Short Goal Prompt

Use this when launching a long-running `codex goal`:

```text
在 /Users/junhaocheng/working-dir/Band of Agents Hackathon 执行 docs/superpowers/plans/2026-05-30-rfp-trustroom-implementation.md。每次只完成下一个未勾选任务，先 git pull --ff-only，不碰 pilotdeck/，优先做企业用户第一屏能看懂的主路径：readiness、evidence、approval、final pack、Band 协作、governed evolution。完成后更新 checkbox、运行验证、git diff --check、提交并推送当前分支。遇到 Band live access、公开 repo、真实 secret、任务边界不清时停止并记录 blocker。
```

## Self-Review Checklist

- [x] Every PRD success criterion maps to at least one task.
- [x] The plan leads with enterprise readiness, evidence, approval and final pack before judge polish.
- [x] Every task has boundary, todo, verification, commit and done conditions.
- [x] Model routing avoids 5.5 超高 for low-risk docs/fixtures.
- [x] Plan protects `pilotdeck/` and secrets.
- [x] Plan keeps replay fallback separate from live Band path.
- [x] Governed Evolution is planned as a tested, human-approved loop.
