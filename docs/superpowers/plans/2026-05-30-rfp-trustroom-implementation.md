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
- [ ] T5: Governed evolution engine and experience ledger
- [x] T6: Readiness, safety and no-secret gates
- [x] T7: Enterprise dashboard MVP
- [x] T8: Agent prompts and task envelopes
- [ ] T9: Band live integration
- [x] T10: Judge docs, demo runbook and evidence report
- [ ] T11: Deployment and public submission hardening
- [ ] T12: Final end-to-end rehearsal

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

- [ ] Create `src/trustroom/evolution.py`.
- [ ] Generate or validate `EvolutionProposal` records from completed run artifacts.
- [ ] Require supporting timeline event ids for every proposal.
- [ ] Implement proposal status transitions: `pending_review`, `approved`, `rejected`, `request_changes`, `deferred`.
- [ ] Implement `ExperienceLesson` activation only after human approval.
- [ ] Implement lesson rollback by marking inactive and preserving `rollback_note`.
- [ ] Create `tests/test_evolution.py`.

Verification:

- [ ] `uv run pytest tests/test_evolution.py -v` passes.
- [ ] Proposal without supporting events cannot become active.
- [ ] Proposal that weakens human approval or no-overclaim gate is rejected.
- [ ] Approved lesson can be loaded into the next run context.
- [ ] `git diff --check` exits 0.

Commit:

- [ ] `git add src/trustroom/evolution.py tests/test_evolution.py`
- [ ] `git commit -m "feat: add governed evolution ledger"`
- [ ] `git push origin $(git branch --show-current)`

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

- [ ] Re-read official Band docs with Chrome if live API details may have changed.
- [ ] Create `LiveBandAdapter` behind the same interface as `MockBandAdapter`.
- [ ] Create at least 3 Band Remote Agents for orchestrator, evidence/retrieval or drafting, and reviewer roles.
- [ ] Record a redacted live evidence packet showing room creation, @mention handoff and reviewer decision.
- [ ] Document setup in README without exposing secrets.
- [ ] Create `tests/test_live_adapter_contract.py` using mock/stubbed responses only.

Verification:

- [ ] `uv run pytest tests/test_live_adapter_contract.py -v` passes.
- [ ] Mock/replay path still passes readiness.
- [ ] Live evidence packet is redacted.
- [ ] `rg -n "agent_key|BAND_AGENT_KEY=.+|room_[A-Za-z0-9]{8,}|sk-" README.md docs reports src tests .env.example` returns no real secret.
- [ ] `git diff --check` exits 0.

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

- [ ] Add a public-safe run command to README.
- [ ] Add `LICENSE` with MIT license if not already present.
- [ ] Add deployment notes for the chosen platform.
- [ ] Decide with user: make current repo public or create a separate sanitized public submission repo.
- [ ] Run no-secret checks against staged files and submission docs.

Verification:

- [ ] `uv run python scripts/check_no_secrets.py` exits 0.
- [ ] `uv run python scripts/check_trustroom_readiness.py` exits 0.
- [ ] `git status --short --ignored` does not show secrets staged or tracked.
- [ ] `git diff --check` exits 0.

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

- [ ] Run all tests.
- [ ] Run readiness check.
- [ ] Run no-secret check.
- [ ] Start dashboard and open the demo path.
- [ ] Verify first viewport answers enterprise readiness questions.
- [ ] Verify replay fallback loads and is labeled as replay.
- [ ] Verify Band live path if credentials and official access exist.
- [ ] Verify README, judge route, runbook and submission checklist match the actual app.
- [ ] Record unresolved issues in `docs/submission-checklist.md` rather than hiding them.

Verification:

- [ ] `uv run pytest -v` passes.
- [ ] `uv run python scripts/check_trustroom_readiness.py` passes.
- [ ] `uv run python scripts/check_no_secrets.py` passes.
- [ ] Manual demo completes in under 10 minutes using either live path or replay fallback.
- [ ] `git diff --check` exits 0.

Commit:

- [ ] `git add README.md docs/submission-checklist.md docs/demo-runbook.md`
- [ ] `git commit -m "docs: record TrustRoom final rehearsal"`
- [ ] `git push origin $(git branch --show-current)`

Done when:

- The demo can be shown to a judge without relying on chat memory.
- Known gaps are explicit and do not contradict no-overclaim boundaries.

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
