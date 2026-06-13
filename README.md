# Band of Agents Hackathon 参赛准备包

最后更新：2026-05-30

官方入口：https://lablab.ai/ai-hackathons/band-of-agents-hackathon

## 当前判断

这个比赛的核心不是“做一个 Agent 应用”，而是证明 Band 真正承担了多 Agent 协作层：Agent 之间需要通过 Band 沟通、共享结构化上下文、招募/邀请其他 Agent、移交任务、协调状态，并在 demo 中让这些行为可见。

已选主线：`RFP TrustRoom`，一个面向 B2B 售前团队的 RFP / 安全问卷 / 证据同源协作室。它把客户 RFP、security questionnaire、公司知识库、合规证据放进同一个 Band room，让需求拆解、证据检索、答案起草、合规审查和人工 SME reviewer 通过 Band 完成一次可回放的提交包生成流程。

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
export BAND_API_BASE="https://platform.dev.band.ai"
export BAND_AGENT_ID="<runtime-agent-id>"
export BAND_AGENT_KEY="<runtime-agent-key>"
```

`BAND_REST_URL` 也可替代 `BAND_API_BASE`。Peer agent 的 UUID 映射必须由运行时安全配置传入 `LiveBandConfig.agent_directory`，不要写进 README、测试、replay、报告或源代码。live 验证失败时，demo 必须明确切回 replay fallback。

## 不可妥协的验收点

- 至少 3 个 Agent 通过 Band 协作。
- Band 必须在核心工作流中使用，不能只是最终通知渠道。
- Demo 必须看得见 Agent 角色、交接、共享上下文、状态变化和最终业务价值。
- 提交必须包含公开视频/演示、公开 GitHub、可访问 Demo URL、封面图、短描述、长描述、技术标签。
- 代码和提交材料要保持原创，并按官方页面要求兼容 MIT 许可。

## 近期动作

1. 注册并确认 lablab.ai、Band、Band Discord、lablab Discord、AI/ML API 访问。
2. 开赛前先跑通 Band SDK 的最小远程 Agent：创建 Remote Agent、拿 Agent UUID/API key、`uv add "band-sdk[langgraph]"`、本地验证连接。
3. 用 `RFP TrustRoom` 先做 15 分钟 demo 剧本，而不是先写大系统：一个客户 RFP + 安全问卷进入，3-4 个 Agent 协作产出可提交回答包和证据索引。
4. Dashboard 第一屏优先展示企业用户关心的 Submission Readiness、Evidence Coverage、Approval Queue 和 Final Pack 状态，再展示 Agent timeline。
5. 开赛后第一天必须把 Band room 里的端到端协作录下来，后面所有功能都围绕这条演示链路增强。
6. 参考飞书项目的做法，第一天就补 replay fallback、评委 10 分钟体验包和 no-overclaim 边界，不等最后一天再补材料。
