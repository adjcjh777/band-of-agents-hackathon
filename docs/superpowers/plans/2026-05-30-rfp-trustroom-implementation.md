# RFP TrustRoom Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Update this document after every task attempt.

**Goal:** Build the RFP TrustRoom hackathon MVP: sample RFP/questionnaire intake, mock/replay multi-agent workflow, dashboard, evaluation checks, Band live adapter, and submission-ready demo evidence.

**Architecture:** Start with a deterministic local mock/replay path so the demo works before Band access is finalized. Keep Band live integration behind an adapter; the dashboard renders the same run state from live, mock, or replay events.

**Tech Stack:** Python 3.11, uv, FastAPI, Jinja2 templates, Pydantic models, pytest, JSONL replay store, Band SDK after kickoff access is confirmed.

---

## Goal Execution Contract

- The long-running `codex goal` should read this file first, complete the next unchecked task, update the checkboxes, run the listed verification, commit, and push.
- Do not read, edit, stage, or commit `pilotdeck/`.
- Before edits: `git status --short --branch && git pull --ff-only`.
- After edits: run the task verification plus `git diff --check`.
- Every commit must include only files for the completed task.
- If a task is blocked, write the blocker under that task and continue only if the next task is independent.
- Never commit `.env`, `agent_config.yaml`, API keys, true room IDs, true agent keys, or private customer data.

## Model Routing Rules

| Work type | Default model | Why | Escalate when |
|---|---|---|---|
| Sample RFP/questionnaire/knowledge fixtures, submission copy, runbook prose | 5.3codex spark | Cheap, creative/document-heavy, low architectural risk | Output contradicts PRD or needs security/compliance judgment |
| Isolated modules, schema tests, fixture evals, prompt templates, small scripts | 5.4 | Good balance for code with bounded files | Cross-module state or flaky tests appear |
| Main Codex implementation: scaffold, state machine, API, dashboard integration, deployment | 5.5 中 | Needs repo context and implementation judgment | Architecture has to change or debugging repeats twice |
| Band live integration, final security/no-secret review, public repo conversion, hard blockers | 5.5 超高 | Highest risk, external dependencies, expensive mistakes | Use sparingly; do not use for docs or fixture drafting |

Target split: Codex Pro handles about 60% of main implementation and final review. Claude Code + mimo token plan handles about 40% of sample data, long-context prompts, fixture evals, local debugging support, and docs. All auxiliary outputs entering this repo must be reviewed by Codex before final submission.

## Todo Board

- [x] T0: Repo scaffold and dependency baseline
- [ ] T1: Core contracts and state machine
- [ ] T2: Sample packs and replay fixture
- [ ] T3: Mock agent runner
- [ ] T4: Evaluation and readiness checks
- [ ] T5: FastAPI dashboard MVP
- [ ] T6: Agent prompts and task envelopes
- [ ] T7: Band adapter interface and live integration
- [ ] T8: Judge docs, demo runbook, and evidence report
- [ ] T9: Deployment and public submission hardening
- [ ] T10: Final end-to-end rehearsal

## File Map

- Create `pyproject.toml`: uv project metadata and dependencies.
- Create `src/trustroom/models.py`: Pydantic data contracts for runs, items, evidence, drafts, reviews, and timeline events.
- Create `src/trustroom/state_machine.py`: allowed state transitions and final pack gating.
- Create `src/trustroom/sample_loader.py`: loads local sample packs.
- Create `src/trustroom/replay.py`: reads/writes replay JSONL.
- Create `src/trustroom/agents/mock_runner.py`: deterministic local multi-agent workflow.
- Create `src/trustroom/agents/prompts/*.md`: agent role prompts and output schemas.
- Create `src/trustroom/band/adapter.py`: live/mock Band boundary.
- Create `src/trustroom/web/app.py`: FastAPI app.
- Create `src/trustroom/web/templates/*.html`: dashboard pages.
- Create `samples/acme-security-rfp/*`: first fictional sample pack.
- Create `samples/fintech-vendor-ddq/*`: second fictional sample pack.
- Create `reports/trustroom_replay.example.jsonl`: committed replay fixture.
- Create `scripts/check_trustroom_readiness.py`: local readiness gate.
- Create `scripts/run_trustroom_replay.py`: CLI replay runner.
- Create `tests/**`: focused unit and integration tests.
- Modify `.gitignore`: keep secrets ignored, but allow committed example replay files.
- Modify `README.md`: add setup, run, replay, and demo commands.

## T0: Repo Scaffold And Dependency Baseline

Recommended model: 5.5 中. Do not delegate unless only drafting README text, which can use 5.3codex spark.

Boundary:

- Create the Python project skeleton and allow committed example replay files.
- Do not implement agents, Band live calls, or UI behavior yet.

Todo:

- [x] Create directories: `src/trustroom/`, `src/trustroom/agents/`, `src/trustroom/band/`, `src/trustroom/web/templates/`, `samples/`, `reports/`, `scripts/`, `tests/`.
- [x] Add empty `__init__.py` files under Python packages.
- [x] Add `pyproject.toml` with Python `>=3.11`, dependencies `fastapi`, `uvicorn`, `jinja2`, `pydantic`, and dev dependency `pytest`.
- [x] Modify `.gitignore` so `reports/*.example.jsonl` and `reports/.gitkeep` can be committed while other reports remain ignored.
- [x] Add `reports/.gitkeep`.
- [x] Update `README.md` with setup command `uv sync`, replay command placeholder `uv run python scripts/run_trustroom_replay.py --replay reports/trustroom_replay.example.jsonl`, and local web command `uv run uvicorn trustroom.web.app:app --reload`.

Verification:

- [x] `uv sync` succeeds.
- [x] `uv run python -c "import fastapi, pydantic, jinja2"` exits 0.
- [x] `git status --short` shows no `pilotdeck/` files.
- [x] `git diff --check` exits 0.

Commit:

- [x] `git add pyproject.toml README.md .gitignore reports/.gitkeep src tests samples scripts`
- [x] `git commit -m "chore: scaffold TrustRoom project"`
- [x] `git push origin main`

Done when:

- Fresh checkout can install dependencies with `uv sync`.
- Repo contains the intended directories and no secret-like files.

## T1: Core Contracts And State Machine

Recommended model: 5.5 中. Use 5.4 for a subagent writing isolated tests after contracts are defined.

Boundary:

- Implement data models and state transitions only.
- Do not call LLMs, Band, or render dashboard pages.

Todo:

- [ ] Create `src/trustroom/models.py` with Pydantic models: `Run`, `QuestionItem`, `EvidenceCandidate`, `AnswerDraft`, `ReviewDecision`, `TimelineEvent`, `FinalSubmissionPack`.
- [ ] Create `src/trustroom/state_machine.py` with allowed states: `intake`, `decomposition`, `evidence`, `drafting`, `review`, `approval`, `submission_pack`.
- [ ] Enforce rule: high-risk items or items with no current evidence cannot enter final pack unless review status is `approved`.
- [ ] Create `tests/test_models.py` for model validation.
- [ ] Create `tests/test_state_machine.py` for valid transitions and blocked finalization.

Verification:

- [ ] `uv run pytest tests/test_models.py tests/test_state_machine.py -v` passes.
- [ ] Test includes a high-risk unapproved answer and expects finalization to fail.
- [ ] Test includes a low-risk answer with current evidence and expects finalization to pass.
- [ ] `git diff --check` exits 0.

Commit:

- [ ] `git add src/trustroom/models.py src/trustroom/state_machine.py tests/test_models.py tests/test_state_machine.py`
- [ ] `git commit -m "feat: add TrustRoom core contracts"`
- [ ] `git push origin main`

Done when:

- Core schema covers all PRD data objects.
- Final pack gating is enforced by tests, not just documented.

## T2: Sample Packs And Replay Fixture

Recommended model: 5.3codex spark for draft fixtures, then 5.4 for schema validation and cleanup.

Boundary:

- Create fictional data only.
- Do not use real customer names, true policies, copied vendor questionnaire data, or private company docs.

Todo:

- [ ] Create `samples/acme-security-rfp/rfp.md` with at least 8 fictional customer requirements.
- [ ] Create `samples/acme-security-rfp/questionnaire.csv` with at least 8 rows and columns `id,question,category,risk_hint`.
- [ ] Create `samples/acme-security-rfp/knowledge.json` with at least 12 evidence snippets, including 2 stale snippets.
- [ ] Create `samples/fintech-vendor-ddq/` with the same three-file structure.
- [ ] Create `src/trustroom/sample_loader.py` to load a sample pack into typed models or plain validated dictionaries.
- [ ] Create `tests/test_sample_loader.py` to verify both packs load and each has at least 8 question items.
- [ ] Create `reports/trustroom_replay.example.jsonl` with one complete replay containing intake, 3+ agent handoffs, review, approval, and final pack events.

Verification:

- [ ] `uv run pytest tests/test_sample_loader.py -v` passes.
- [ ] `wc -l reports/trustroom_replay.example.jsonl` is at least 12.
- [ ] `rg -n "real customer|API key|room_" samples reports` returns no sensitive-looking placeholder that could be mistaken for live data.
- [ ] `git diff --check` exits 0.

Commit:

- [ ] `git add samples reports/trustroom_replay.example.jsonl src/trustroom/sample_loader.py tests/test_sample_loader.py`
- [ ] `git commit -m "feat: add TrustRoom sample packs"`
- [ ] `git push origin main`

Done when:

- Two fictional sample packs can load locally.
- Example replay is committed despite `reports/` being generally ignored.

## T3: Mock Agent Runner

Recommended model: 5.5 中 for orchestration. 5.4 can handle individual deterministic agent functions.

Boundary:

- Build deterministic mock behavior to prove workflow shape.
- Do not connect to real Band or external LLMs.

Todo:

- [ ] Create `src/trustroom/agents/mock_runner.py`.
- [ ] Implement deterministic roles: orchestrator, requirement decomposer, evidence retriever, answer drafter, compliance reviewer, SME approver.
- [ ] Make runner output typed `TimelineEvent` records and a `FinalSubmissionPack`.
- [ ] Include at least one blocked or human-approval item in each run.
- [ ] Create `tests/test_mock_runner.py`.

Verification:

- [ ] `uv run pytest tests/test_mock_runner.py -v` passes.
- [ ] Test confirms at least 3 distinct agent senders.
- [ ] Test confirms at least one handoff from decomposer to retriever and one handoff from drafter to reviewer.
- [ ] Test confirms high-risk item requires SME approval before final pack.
- [ ] `git diff --check` exits 0.

Commit:

- [ ] `git add src/trustroom/agents/mock_runner.py tests/test_mock_runner.py`
- [ ] `git commit -m "feat: add mock TrustRoom agent runner"`
- [ ] `git push origin main`

Done when:

- `uv run pytest tests/test_mock_runner.py -v` proves the core multi-agent collaboration without external services.

## T4: Evaluation And Readiness Checks

Recommended model: 5.4. Escalate to 5.5 中 only if eval design changes data contracts.

Boundary:

- Create local checks that guard demo quality.
- Do not add production monitoring or heavyweight benchmark tooling.

Todo:

- [ ] Create `scripts/check_trustroom_readiness.py`.
- [ ] Check sample packs load.
- [ ] Check replay loads in under 5 seconds.
- [ ] Check evidence coverage is at least 80% or items are explicitly marked `needs_review`.
- [ ] Check 100% high-risk items are `needs_human_approval`, `approved`, or `blocked`.
- [ ] Check no-overclaim words are caught: `production-ready`, `certified`, `fully compliant`, `guaranteed`.
- [ ] Create `tests/test_readiness.py`.

Verification:

- [ ] `uv run python scripts/check_trustroom_readiness.py` exits 0.
- [ ] `uv run pytest tests/test_readiness.py -v` passes.
- [ ] Temporarily injecting an unapproved high-risk item makes the readiness test fail; do not commit the injected failure.
- [ ] `git diff --check` exits 0.

Commit:

- [ ] `git add scripts/check_trustroom_readiness.py tests/test_readiness.py`
- [ ] `git commit -m "feat: add TrustRoom readiness checks"`
- [ ] `git push origin main`

Done when:

- One command can tell whether the demo data and replay are safe to present.

## T5: FastAPI Dashboard MVP

Recommended model: 5.5 中. Use 5.3codex spark for copy polish only after the page renders.

Boundary:

- Render local mock/replay data in a useful dashboard.
- Do not chase a rich frontend stack or custom build system.

Todo:

- [ ] Create `src/trustroom/web/app.py` with routes `/`, `/runs/demo`, `/runs/demo/replay`, `/health`.
- [ ] Create `src/trustroom/web/templates/base.html`, `index.html`, `run.html`.
- [ ] Dashboard sections: input summary, agent status, timeline, draft answers, evidence index, review state, final submission pack.
- [ ] Add clear `MOCK` or `REPLAY` badge on non-live paths.
- [ ] Create `tests/test_web_app.py` using FastAPI TestClient.

Verification:

- [ ] `uv run pytest tests/test_web_app.py -v` passes.
- [ ] `uv run uvicorn trustroom.web.app:app --reload` starts without import errors.
- [ ] Browser or curl check: `/health` returns OK; `/runs/demo/replay` includes "RFP TrustRoom", "Evidence", "Human approval", and "REPLAY".
- [ ] `git diff --check` exits 0.

Commit:

- [ ] `git add src/trustroom/web tests/test_web_app.py README.md`
- [ ] `git commit -m "feat: add TrustRoom dashboard MVP"`
- [ ] `git push origin main`

Done when:

- A judge can open one local URL and understand the workflow without reading raw JSON.

## T6: Agent Prompts And Task Envelopes

Recommended model: 5.4 for prompt structure; 5.3codex spark for wording variants.

Boundary:

- Define prompts, output schemas, and task envelopes for each agent.
- Do not call external LLMs yet.

Todo:

- [ ] Create `src/trustroom/agents/prompts/orchestrator.md`.
- [ ] Create `src/trustroom/agents/prompts/requirement_decomposer.md`.
- [ ] Create `src/trustroom/agents/prompts/evidence_retriever.md`.
- [ ] Create `src/trustroom/agents/prompts/answer_drafter.md`.
- [ ] Create `src/trustroom/agents/prompts/compliance_reviewer.md`.
- [ ] Each prompt must include role, input contract, output JSON schema, refusal/no-overclaim boundary, and Band handoff instruction.
- [ ] Create `docs/agent-task-envelopes.md` explaining the message payload each agent sends through Band.

Verification:

- [ ] `rg -n "production deployment|legal advice|certification" src/trustroom/agents/prompts docs/agent-task-envelopes.md` shows these are forbidden, not promised.
- [ ] `rg -n "@mention|handoff|evidence|human approval" src/trustroom/agents/prompts` returns hits in each prompt.
- [ ] `git diff --check` exits 0.

Commit:

- [ ] `git add src/trustroom/agents/prompts docs/agent-task-envelopes.md`
- [ ] `git commit -m "docs: add TrustRoom agent prompts"`
- [ ] `git push origin main`

Done when:

- Another agent can implement live or LLM-backed agents by reading the prompt files without inventing roles.

## T7: Band Adapter Interface And Live Integration

Recommended model: 5.5 超高 for live integration. Use 5.5 中 for mock adapter before kickoff. Do not use 5.3 for this task.

Boundary:

- Build a narrow adapter that can be backed by mock/replay now and Band live after credentials exist.
- Do not commit credentials or true room identifiers.

Todo:

- [ ] Create `src/trustroom/band/adapter.py` with interface methods: `create_room`, `send_message`, `mention_agent`, `record_event`, `get_room_timeline`.
- [ ] Create `MockBandAdapter` that records timeline events locally.
- [ ] Create `tests/test_band_adapter.py` for mock adapter behavior.
- [ ] After kickoff, add `LiveBandAdapter` only after reading official Band docs in Chrome or official docs.
- [ ] Add `.env.example` with non-secret variable names: `BAND_API_BASE`, `BAND_AGENT_ID`, `BAND_AGENT_KEY`.
- [ ] Document live setup in README without exposing real keys.

Verification:

- [ ] `uv run pytest tests/test_band_adapter.py -v` passes.
- [ ] `rg -n "BAND_.*=.+[A-Za-z0-9]{12,}" .env.example README.md src tests` returns no real-looking secret.
- [ ] Mock path still passes: `uv run python scripts/check_trustroom_readiness.py`.
- [ ] `git diff --check` exits 0.

Commit:

- [ ] `git add src/trustroom/band/adapter.py tests/test_band_adapter.py .env.example README.md`
- [ ] `git commit -m "feat: add Band adapter boundary"`
- [ ] `git push origin main`

Done when:

- Mock adapter is tested.
- Live Band work has a safe boundary and cannot leak credentials by design.

## T8: Judge Docs, Demo Runbook, And Evidence Report

Recommended model: 5.3codex spark for draft, 5.4 for consistency review, Codex final review before commit.

Boundary:

- Write judge-facing documentation for the exact MVP.
- Do not invent features not present in dashboard or replay.

Todo:

- [ ] Create `docs/judge-10-minute-experience.md`.
- [ ] Create `docs/demo-runbook.md`.
- [ ] Create `docs/demo-evidence-report.md`.
- [ ] Include live path and replay fallback, clearly labeled.
- [ ] Include no-overclaim language: hackathon demo / working prototype only.
- [ ] Include a 5-minute video structure aligned with RFP TrustRoom.

Verification:

- [ ] `rg -n "production|enterprise-ready deployment|fully automated compliance|legal advice|certified" docs/judge-10-minute-experience.md docs/demo-runbook.md docs/demo-evidence-report.md` returns no overclaim unless listed as forbidden wording.
- [ ] `rg -n "replay|fallback|Band|human approval|evidence" docs/judge-10-minute-experience.md docs/demo-runbook.md docs/demo-evidence-report.md` returns useful hits.
- [ ] `git diff --check` exits 0.

Commit:

- [ ] `git add docs/judge-10-minute-experience.md docs/demo-runbook.md docs/demo-evidence-report.md`
- [ ] `git commit -m "docs: add TrustRoom judge materials"`
- [ ] `git push origin main`

Done when:

- A fresh evaluator can run the demo path from docs without asking for chat context.

## T9: Deployment And Public Submission Hardening

Recommended model: 5.5 中 for deployment. 5.5 超高 for final public repo and secret audit.

Boundary:

- Make demo runnable in a public-safe way.
- Do not switch the current private repository to public until the user explicitly approves.

Todo:

- [ ] Add a production-ish run command to README.
- [ ] Add `LICENSE` with MIT license if not already present.
- [ ] Add `scripts/check_no_secrets.py` to scan staged files for `.env`, API-key-like strings, true room ids, and agent keys.
- [ ] Add deployment notes for the chosen platform.
- [ ] Decide with user: make current repo public or create a separate sanitized public submission repo.

Verification:

- [ ] `uv run python scripts/check_no_secrets.py` exits 0.
- [ ] `uv run python scripts/check_trustroom_readiness.py` exits 0.
- [ ] `git status --short --ignored` does not show secrets staged or tracked.
- [ ] `git diff --check` exits 0.

Commit:

- [ ] `git add README.md LICENSE scripts/check_no_secrets.py`
- [ ] `git commit -m "chore: harden TrustRoom submission"`
- [ ] `git push origin main`

Done when:

- Repo can be shared safely after the user chooses the public repo strategy.

## T10: Final End-To-End Rehearsal

Recommended model: 5.5 超高 for final review, with 5.3codex spark only for caption/copy tweaks.

Boundary:

- Verify the complete judging path.
- Do not add new architecture or major features.

Todo:

- [ ] Run all tests.
- [ ] Run readiness check.
- [ ] Start dashboard and open the demo path.
- [ ] Verify replay fallback loads and is labeled as replay.
- [ ] Verify Band live path if credentials and official access exist.
- [ ] Verify README, judge route, runbook, and submission checklist match the actual app.
- [ ] Record unresolved issues in `docs/submission-checklist.md` rather than hiding them.

Verification:

- [ ] `uv run pytest -v` passes.
- [ ] `uv run python scripts/check_trustroom_readiness.py` passes.
- [ ] `uv run python scripts/check_no_secrets.py` passes if T9 is complete.
- [ ] Manual demo completes in under 10 minutes using either live path or replay fallback.
- [ ] `git diff --check` exits 0.

Commit:

- [ ] `git add README.md docs/submission-checklist.md docs/demo-runbook.md`
- [ ] `git commit -m "docs: record TrustRoom final rehearsal"`
- [ ] `git push origin main`

Done when:

- The demo can be shown to a judge without relying on chat memory.
- Known gaps are explicit and do not contradict no-overclaim boundaries.

## Suggested Short Goal Prompt

Use this when launching a long-running `codex goal`:

```text
在 /Users/junhaocheng/working-dir/Band of Agents Hackathon 中执行 docs/superpowers/plans/2026-05-30-rfp-trustroom-implementation.md。每次只完成下一个未勾选任务，先 git pull --ff-only，不碰 pilotdeck/，按任务建议模型派子代理，完成后更新该任务 checkbox、运行验证、git diff --check、提交并推送。遇到 Band live access、公开 repo、真实 secret、任务边界不清时停止并记录 blocker。
```

## Self-Review Checklist

- [x] Every PRD success criterion maps to at least one task.
- [x] Every task has boundary, todo, verification, commit, and done conditions.
- [x] Model routing is explicit and avoids 5.5 超高 for low-risk docs/fixtures.
- [x] Plan protects `pilotdeck/` and secrets.
- [x] Plan keeps replay fallback separate from live Band path.
