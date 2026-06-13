# Band of Agents Hackathon 参赛准备包

最后更新：2026-06-13

官方入口：https://lablab.ai/ai-hackathons/band-of-agents-hackathon

## 当前判断

这个比赛的核心不是“做一个 Agent 应用”，而是证明 Band 真正承担了多 Agent 协作层：Agent 之间需要通过 Band 沟通、共享结构化上下文、招募/邀请其他 Agent、移交任务、协调状态，并在 demo 中让这些行为可见。

已选主线：`RFP TrustRoom`，一个面向 B2B 售前团队的 RFP / 安全问卷 / 证据同源协作室。它把客户 RFP、security questionnaire、公司知识库、合规证据放进同一个 Band room，让需求拆解、证据检索、答案起草、合规审查和人工 SME reviewer 通过 Band 完成一次可回放的提交包生成流程。

## 2026-06-13 状态

- 官方页已用 Chrome 重新复核：比赛截止时间为 2026-06-19 23:00 CST，提交项仍是 Public GitHub Repository、Demo Application Platform、Application URL、Video Presentation、Slide Presentation、Cover Image、short/long description 和 tags。
- 官方奖池当前写为 `$10,000+`，除 AI/ML API partner prize 外，页面新增 Featherless AI partner resources/prize；Band Pro promo code `BANDHACK26`、Featherless promo code `BOA26` 已在页面可见。
- 本仓库已有 mock/replay 主路径、enterprise reviewer cockpit、T20 Run Trace / Agent Handoff Chain、readiness/no-secret gates、T13 REST live smoke harness、T15 autonomous reply smoke harness 和 Chrome live verification 记录。dashboard 已把 case brief、go/no-go decision、Run Trace proof strip、Business Milestones、Representative Item Traces、Q-006 Blocked Impact Path、evidence freshness、human approval basis 和 final-pack exclusions 放到企业 reviewer / judge 可操作的视图里。
- 当前不能宣称完整 autonomous live Band workflow：真实 REST room / participants / @mention / event smoke 已验证，但 SDK/WebSocket Remote Agent 自动接收并回复仍未用 connected peer 跑通；新 harness 当前 dry-run 返回 `BLOCKED`。
- 提交前最大未决项：public repo 策略、demo URL、cover image、5 分钟视频、slide deck、live autonomous replies 或明确 replay fallback 叙事。

## 本地文档

- [官方页面调研](docs/official-research.md)
- [参赛作战计划](docs/competition-plan.md)
- [提交清单](docs/submission-checklist.md)
- [推荐项目概念：RFP TrustRoom](docs/project-concept.md)
- [RFP TrustRoom PRD](docs/rfp-trustroom-prd.md)
- [RFP TrustRoom Enterprise Governed Evolution Spec](docs/superpowers/specs/2026-05-30-trustroom-governed-evolution-design.md)
- [RFP TrustRoom 实现任务计划](docs/superpowers/plans/2026-05-30-rfp-trustroom-implementation.md)
- [Codex + Claude Code 双 Agent 协作协议](docs/dual-agent-operating-protocol.md)
- [双 Agent 任务台账](docs/agent-task-ledger.md)
- [双 Agent 协调重置计划](docs/superpowers/plans/2026-05-30-dual-agent-coordination-reset.md)
- [飞书 AI 挑战赛经验迁移](docs/feishu-lessons-for-band.md)

## 本地运行

```bash
# 安装运行环境与依赖
uv sync
```

```bash
# 回放演示占位：用于本地复现与验收展示
uv run python scripts/run_trustroom_replay.py --replay reports/trustroom_replay.example.jsonl
```

```bash
# 双 Agent 并行前/集成前检查：确保 active 文件锁不冲突
uv run python scripts/check_dual_agent_protocol.py
```

```bash
# Claude Code 写入任务返回后检查：确保所有改动都落在该任务 locked paths 内
uv run python scripts/check_dual_agent_changes.py --task "<Task>"
```

```bash
# Codex controller 标准派发入口：读取 active lock 后安全调用 claude -p
uv run python scripts/run_claude_task.py --task "<Task>" --prompt-file /path/to/task-prompt.md
```

```bash
# 启动本地服务
uv run uvicorn trustroom.web.app:app --reload
```

`replay` 路径基于示例事件日志做可复现演示；`live` 路径会在 Band 接入确认后通过适配器连接真实协作环境，不能把 replay 结果伪装成 live。

公开提交前的安全检查：

```bash
uv run python scripts/check_no_secrets.py
uv run python scripts/check_trustroom_readiness.py
uv run pytest -v
git diff --check
```

部署说明见 [docs/deployment-notes.md](docs/deployment-notes.md)。

## Band live path

当前仓库默认仍以 `mock` / `replay` 保证评委体验稳定。`src/trustroom/band/live_adapter.py` 提供窄 live REST boundary，用于在运行时连接 Band Agent API；它不会在仓库里保存 Agent UUID、API key、真实 room id 或真实 message id。

运行 live path 前，在本机或部署平台的 secret store 中配置：

```bash
export BAND_API_BASE="https://app.band.ai"
export BAND_AGENT_ID="<runtime-agent-id>"
export BAND_AGENT_KEY="<runtime-agent-key>"
export TRUSTROOM_BAND_PEERS_JSON='{"requirement-decomposer-agent":"@owner/requirement-decomposer-agent","evidence-retriever-agent":"@owner/evidence-retriever-agent"}'
```

`BAND_REST_URL` 也可替代 `BAND_API_BASE`。`TRUSTROOM_BAND_PEERS_JSON` 可使用公开 handle；`scripts/run_live_band_smoke.py` 会在运行时通过 Band `/peers` 解析为 UUID，并只写入脱敏 `band-ref:*` evidence。Agent UUID、API key、真实 room id 和真实 message id 不要写进 README、测试、replay、报告或源代码。live 验证失败时，demo 必须明确切回 replay fallback。

自主回复 smoke harness：

```bash
uv run python scripts/run_live_band_autonomous_smoke.py --dry-run-check
uv run python scripts/run_live_band_autonomous_smoke.py --target-agent requirement-decomposer-agent
```

该 harness 只有在 Band messages 中看到非 @mention 消息包含挑战 token 时才返回 `DONE`；缺少凭证、peer directory、peer handle 解析失败或超时无回复都会返回 `BLOCKED`。当前本机 ignored env dry-run 仍因缺少 REST base / peer directory 返回 `BLOCKED`，不能把它描述成完整 live autonomous workflow。

## 不可妥协的验收点

- 至少 3 个 Agent 通过 Band 协作。
- Band 必须在核心工作流中使用，不能只是最终通知渠道。
- Demo 必须看得见 Agent 角色、交接、共享上下文、状态变化和最终业务价值；当前主镜头应走 Executive Decision -> Run Trace -> Agent Handoff Chain -> Representative Item Traces -> Blocked Impact Path -> Final Pack。
- 提交必须包含公开视频/演示、公开 GitHub、可访问 Demo URL、封面图、短描述、长描述、技术标签。
- 代码和提交材料要保持原创，并按官方页面要求兼容 MIT 许可。

## 近期动作

1. 用 connected peer 跑通 `scripts/run_live_band_autonomous_smoke.py`，或把 REST smoke + replay fallback 的边界写进最终提交叙事。
2. 决定 public GitHub strategy：切当前仓库 public，或创建脱敏 public submission repo。
3. 部署 public-safe demo URL，默认只启用 mock/replay；live credentials 只放 secret store。
4. 产出 cover image、5 分钟 video presentation 和 slide deck。
5. 录屏主线固定为：business pain -> role map / Band room evidence -> Executive Decision -> Run Trace proof strip -> Agent Handoff Chain -> Q-006 Blocked Impact Path -> Representative Item Traces -> Final Pack -> replay/live boundary。
6. 提交前重跑 `uv run pytest -v`、`uv run python scripts/check_trustroom_readiness.py`、`uv run python scripts/check_no_secrets.py`、Chrome 官方页复核和 `git diff --check`。
