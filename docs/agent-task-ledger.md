# Agent Task Ledger

最后更新：2026-05-31

本台账是 Codex + Claude Code 并行执行的单一事实来源。任何 agent 开始写文件前，必须先在 Active File Locks 表中拥有一条 `active` 锁。

## Ledger Rules

- 只有 Codex controller 可以新增、关闭或修改 active locks。
- `planned` 行只是建议，不代表可以动手。
- `active`、`review`、`ready-to-merge` 行会被 `scripts/check_dual_agent_protocol.py` 校验。
- Agent 返回后必须用 `scripts/check_dual_agent_changes.py --task "<Task>"` 校验包括未跟踪文件在内的 changed paths。
- `Locked paths` 必须写精确文件或目录，多个路径用逗号分隔。
- 共享入口文件默认 Codex controller 锁定。
- 每个任务完成后，把状态改为 `complete`，记录实际测试命令和集成结论。

## Active File Locks

| Task | Owner | Branch | Status | Locked paths | Review owner | Required checks |
|---|---|---|---|---|---|---|
| T1 Enterprise domain contracts and state machine | Codex | `feature/trustroom-governed-evolution-spec` | complete | `src/trustroom/models.py`, `src/trustroom/state_machine.py`, `tests/test_models.py`, `tests/test_state_machine.py`, `docs/superpowers/plans/2026-05-30-rfp-trustroom-implementation.md` | Codex | `uv run pytest tests/test_models.py tests/test_state_machine.py -v`; `uv run pytest -v`; `git diff --check` |
| T3 Primary enterprise sample pack and replay fixture | Codex | `feature/trustroom-governed-evolution-spec` | complete | `samples/acme-security-rfp/`, `reports/trustroom_replay.example.jsonl`, `src/trustroom/sample_loader.py`, `tests/test_sample_loader.py`, `docs/superpowers/plans/2026-05-30-rfp-trustroom-implementation.md` | Codex | `uv run pytest tests/test_sample_loader.py -v`; `uv run pytest -v`; `git diff --check` |
| T2 Band-compatible adapter and event mirror | Codex | `feature/trustroom-governed-evolution-spec` | complete | `src/trustroom/band/adapter.py`, `tests/test_band_adapter.py`, `docs/superpowers/plans/2026-05-30-rfp-trustroom-implementation.md` | Codex | `uv run pytest tests/test_band_adapter.py -v`; `.env.example` non-secret template handled by Codex controller; `rg -n "BAND_.*=.+[A-Za-z0-9]{12,}" .env.example README.md src tests`; `uv run pytest -v`; `git diff --check` |
| T4 Deterministic mock agent runner with review loop | Codex | `feature/trustroom-governed-evolution-spec` | complete | `src/trustroom/agents/mock_runner.py`, `tests/test_mock_runner.py`, `docs/superpowers/plans/2026-05-30-rfp-trustroom-implementation.md` | Codex | `uv run pytest tests/test_mock_runner.py -v`; `uv run pytest -v`; `git diff --check` |
| T7 Enterprise dashboard MVP | Codex | `feature/trustroom-governed-evolution-spec` | complete | `src/trustroom/web/app.py`, `src/trustroom/web/templates/`, `tests/test_web_app.py`, `pyproject.toml`, `uv.lock`, `docs/superpowers/plans/2026-05-30-rfp-trustroom-implementation.md` | Codex | `uv run pytest tests/test_web_app.py -v`; `uv run uvicorn trustroom.web.app:app --reload`; browser or curl `/health`; `uv run pytest -v`; `git diff --check` |
| T6 Readiness, safety and no-secret gates | Codex | `feature/trustroom-governed-evolution-spec` | complete | `src/trustroom/readiness.py`, `scripts/check_trustroom_readiness.py`, `scripts/check_no_secrets.py`, `tests/test_readiness.py`, `tests/test_no_secrets.py`, `docs/superpowers/plans/2026-05-30-rfp-trustroom-implementation.md` | Codex | `uv run python scripts/check_trustroom_readiness.py`; `uv run python scripts/check_no_secrets.py`; `uv run pytest tests/test_readiness.py tests/test_no_secrets.py -v`; `uv run pytest -v`; `git diff --check` |
| T8 Agent prompts and task envelopes | Codex | `feature/trustroom-governed-evolution-spec` | complete | `src/trustroom/agents/prompts/`, `docs/agent-task-envelopes.md`, `tests/test_agent_prompts.py`, `docs/superpowers/plans/2026-05-30-rfp-trustroom-implementation.md` | Codex | `uv run pytest tests/test_agent_prompts.py -v`; `rg` forbidden overclaim terms in prompts and envelope docs; `rg` Band handoff terms in prompts; `uv run pytest -v`; `git diff --check` |
| T10 Judge docs, demo runbook and evidence report | Codex | `feature/trustroom-governed-evolution-spec` | complete | `docs/judge-10-minute-experience.md`, `docs/demo-runbook.md`, `docs/demo-evidence-report.md`, `docs/superpowers/plans/2026-05-30-rfp-trustroom-implementation.md` | Codex | `rg` no-overclaim terms in judge docs; `rg` demo readiness terms in judge docs; `uv run python scripts/check_trustroom_readiness.py`; `uv run python scripts/check_no_secrets.py`; `uv run pytest -v`; `git diff --check` |

当前没有 active locks。开始下一个任务前，Codex controller 必须先在本表添加 `active` 行并运行 `uv run python scripts/check_dual_agent_protocol.py`。

## Planned TrustRoom Work Allocation

这些是建议分工，开始执行前必须复制到 Active File Locks 并改成 `active`。

| Plan Task | Suggested owner | Suggested locked paths | Why |
|---|---|---|---|
| T1 Enterprise domain contracts and state machine | Codex | `src/trustroom/models.py`, `src/trustroom/state_machine.py`, `tests/test_models.py`, `tests/test_state_machine.py` | 核心领域边界和 final-pack gating 需要强架构判断。 |
| T2 Band-compatible adapter and event mirror | Codex | `src/trustroom/band/adapter.py`, `tests/test_band_adapter.py`, `.env.example` | Band boundary 后续会接 live path，需 Codex 总控。 |
| T3 Primary enterprise sample pack and replay fixture | Claude Code | `samples/acme-security-rfp/`, `reports/trustroom_replay.example.jsonl`, `src/trustroom/sample_loader.py`, `tests/test_sample_loader.py` | Fictional sample、replay 和 loader 可独立完成，无多模态依赖。 |
| T4 Deterministic mock agent runner with review loop | Codex | `src/trustroom/agents/mock_runner.py`, `tests/test_mock_runner.py` | 多 agent 状态流和 review loop 需要跨模块一致性。 |
| T5 Governed evolution engine and experience ledger | Codex | `src/trustroom/evolution.py`, `tests/test_evolution.py` | 需要控制 no-overclaim 和 fail-closed 策略。 |
| T6 Readiness, safety and no-secret gates | Claude Code | `src/trustroom/readiness.py`, `scripts/check_trustroom_readiness.py`, `scripts/check_no_secrets.py`, `tests/test_readiness.py`, `tests/test_no_secrets.py` | 独立脚本和测试适合 Claude Code，Codex 做最终安全 review。 |
| T7 Enterprise dashboard MVP | Codex | `src/trustroom/web/app.py`, `src/trustroom/web/templates/`, `tests/test_web_app.py` | UI、视觉和浏览器验收需要 Codex。 |
| T8 Agent prompts and task envelopes | Claude Code | `src/trustroom/agents/prompts/`, `tests/test_agent_prompts.py` | 文本结构、prompt schema 和边界测试适合 Claude Code。 |
| T9 Band live integration | Codex | `src/trustroom/band/live_adapter.py`, `tests/test_live_adapter_contract.py`, `docs/official-research.md` | 需要 Chrome、Band 账号页面和 live/replay 边界判断。 |
| T10 Judge docs, demo runbook and evidence report | Claude Code draft, Codex integrate | `docs/judge-10-minute-experience.md`, `docs/demo-runbook.md`, `docs/demo-evidence-report.md` | Claude Code 可写初稿，Codex 负责 no-overclaim、Chrome 证据和最终入口一致性。 |
| T11 Deployment and public submission hardening | Codex | `scripts/`, `docs/submission-checklist.md`, deployment docs | 高风险公开提交和 secret 检查由 Codex 总控。 |
| T12 Final end-to-end rehearsal | Codex | `reports/`, `docs/demo-runbook.md`, final README updates | 需要真实演示路径、replay fallback 和视觉确认。 |

## Integration Log

| Date | Branch | Owner | Integrated by | Result | Evidence |
|---|---|---|---|---|---|
| 2026-05-31 | `feature/trustroom-governed-evolution-spec` | Codex | Codex | T10 judge docs, demo runbook and evidence report completed | `rg` no-overclaim terms in judge docs; `rg` demo readiness terms in judge docs; `uv run python scripts/check_trustroom_readiness.py`; `uv run python scripts/check_no_secrets.py`; `uv run pytest -v`; `git diff --check` |
| 2026-05-31 | `feature/trustroom-governed-evolution-spec` | Codex | Codex | T8 agent prompts and task envelopes completed | `uv run pytest tests/test_agent_prompts.py -v`; `rg` forbidden overclaim terms in prompts and envelope docs; `rg` Band handoff terms in prompts; `uv run pytest -v`; `git diff --check` |
| 2026-05-31 | `feature/trustroom-governed-evolution-spec` | Codex | Codex | T6 readiness and no-secret gates completed | `uv run python scripts/check_trustroom_readiness.py`; `uv run python scripts/check_no_secrets.py`; injected unapproved high-risk item failed readiness; `uv run pytest tests/test_readiness.py tests/test_no_secrets.py -v`; `uv run pytest -v`; `git diff --check` |
| 2026-05-31 | `feature/trustroom-governed-evolution-spec` | Codex | Codex | T7 enterprise dashboard MVP completed | `uv run pytest tests/test_web_app.py -v`; `uv run uvicorn trustroom.web.app:app --reload`; curl `/health`; Browser verified replay first viewport core metrics; `uv run pytest -v`; `git diff --check` |
| 2026-05-31 | `feature/trustroom-governed-evolution-spec` | Codex | Codex | T4 deterministic mock agent workflow completed | `uv run pytest tests/test_mock_runner.py -v`; `uv run pytest -v`; `git diff --check` |
| 2026-05-31 | `feature/trustroom-governed-evolution-spec` | Codex | Codex | T2 Band-compatible adapter boundary completed | `uv run pytest tests/test_band_adapter.py -v`; no real-looking BAND secret hits; `uv run pytest -v`; `git diff --check` |
| 2026-05-31 | `feature/trustroom-governed-evolution-spec` | Codex | Codex | T3 primary sample pack and replay fixture completed | `uv run pytest tests/test_sample_loader.py -v`; `wc -l reports/trustroom_replay.example.jsonl`; no sensitive placeholder hits; `uv run pytest -v`; `git diff --check` |
| 2026-05-31 | `feature/trustroom-governed-evolution-spec` | Codex | Codex | T1 enterprise contracts and state machine completed | `uv run pytest tests/test_models.py tests/test_state_machine.py -v`; `uv run pytest -v`; `git diff --check` |
| 2026-05-31 | `feature/claude-runner-wrapper-smoke` | Claude Code | Codex | live wrapper smoke validated | Real `scripts/run_claude_task.py` call used strict empty MCP and Claude tools `Read,Write`; Claude wrote only `docs/claude-runner-wrapper-smoke.md`; controller postflight passed; branch pushed at `b4f03a7`. |
| 2026-05-31 | `feature/trustroom-governed-evolution-spec` | Codex | Codex | safe Claude dispatch wrapper added | `scripts/run_claude_task.py` enforces active lock, branch, strict MCP, budgeted `claude -p`, and postflight changed-file checks; tests use fake Claude for locked and out-of-lock writes. |
| 2026-05-31 | `feature/claude-p-write-smoke` | Claude Code | Codex | write smoke exposed need for changed-file validator | Claude wrote a locked untracked file; follow-up adds `scripts/check_dual_agent_changes.py` so untracked paths are checked against active locks. |
| 2026-05-30 | `feature/trustroom-governed-evolution-spec` | Codex | Codex | validated locally | `uv run pytest tests/test_dual_agent_protocol.py -v`; `uv run python scripts/check_dual_agent_protocol.py`; `git diff --check` |
