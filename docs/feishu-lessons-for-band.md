# 从飞书 AI 挑战赛迁移过来的参赛打法

参考来源：`/Users/junhaocheng/feishu_ai_challenge`

这份文档不复用飞书项目的具体产品方向，也不读取/依赖 `pilotdeck/`。它只迁移上一场比赛已经验证过的参赛方法：先做评委看得懂的产品主路径，再用可复现证据、fallback 和 no-overclaim 边界保护提交质量。

## 1. 先做产品主路径，不先堆能力

飞书项目最后能讲清楚，是因为它从“普通搜索/RAG”收敛成了“企业记忆治理层”：当前结论、证据、版本、权限、审计。

Band 这次也要这样收敛：

- 不讲“我们有很多 Agent”。
- 要讲“RFP / 安全问卷响应里，多角色协作、证据复用和风险签核为什么会卡住”。
- Band 的价值不是聊天窗口，而是 Agent identity、room routing、shared context、handoff、state、audit。
- 每个 demo 动作都要回答：这个动作如果没有 Band，会不会更难做？

## 2. 评委体验必须有固定路线

飞书项目有 `judge-10-minute-experience.md` 和 `demo-runbook.md`，把现场讲什么、失败时怎么 fallback、哪些话不能说都固定下来。

Band 这次照搬这个结构，准备一条 `10 分钟评委路线`：

| 时间 | 评委看到什么 | 目的 |
|---|---|---|
| 0:00-1:00 | RFP / 安全问卷响应痛点 | 先让评委相信这是实际企业流程 |
| 1:00-2:00 | RFP TrustRoom 导入 RFP、问卷和知识库片段 | 建立具体场景 |
| 2:00-4:00 | 3 个以上 Agent 在 Band room 中被 @mention 并分工 | 证明 Band 是协作层 |
| 4:00-6:00 | Evidence / Compliance Agent 反驳、补证据或 veto | 证明不是线性自动化 |
| 6:00-7:30 | Human approval / escalation | 证明企业可控 |
| 7:30-9:00 | Dashboard 展示 timeline、state、handoff、final submission pack | 证明可观察和可审计 |
| 9:00-10:00 | 讲边界、fallback、下一步 | 避免 overclaim |

## 3. 必须有 replay fallback

飞书项目的可靠做法是：真实 Feishu/OpenClaw 可用时走 live，现场不稳时回退 `reports/demo_replay.json` 和固定脚本，同时明确 replay / sandbox / pre-production 边界。

Band 这次也要有两条路径：

- Live path：真实 Band room、真实 Remote Agents、真实 @mention / handoff / event。
- Replay path：本地 JSONL/SQLite 记录一次完整协作，dashboard 可以离线回放同一条 timeline。

要求：

- replay 不能伪装成 live。
- live 失败时不现场乱改配置。
- 录屏和提交材料优先展示稳定链路，附带说明哪些是 live、哪些是 replay。

## 4. no-overclaim 边界要提前写

飞书项目反复强调：可以说 demo / sandbox / pre-production，不能说 production live、全量 workspace、长期稳定。

Band 这次的边界：

可以说：

- 已完成 hackathon demo。
- 至少 3 个 Agent 通过 Band 协作。
- Band room / @mention / handoff / events / shared state 在 demo 中可见。
- RFP TrustRoom 展示了一个 RFP / 安全问卷响应流程的可行原型。

不能说：

- 已生产部署到企业。
- 已适配所有 Agent 框架。
- 已完成真实企业级权限/审计合规。
- Band 长期运行稳定性已验证。
- AI/ML API / Codeband / Band 所有能力都已完整接入。

## 5. 证据包比口头描述重要

飞书项目的证据结构可以迁移成 Band 版：

| 飞书项目证据 | Band 版对应物 |
|---|---|
| `reports/demo_replay.json` | `reports/trustroom_replay.jsonl` |
| readiness check | `scripts/check_trustroom_readiness.py` |
| 评委 10 分钟体验包 | `docs/judge-10-minute-experience.md` |
| benchmark report | `docs/demo-evidence-report.md` |
| no-overclaim 边界 | `README.md` 顶部和提交材料 |
| 真实 live packet | `reports/band-live-evidence-<date>/` |

最小证据字段：

- run id
- room id 或脱敏 room label
- agent name / role
- message/event timestamp
- sender / receiver
- task state
- handoff source and target
- decision / risk / blocker
- final submission pack

## 6. 评审材料要面向人，不面向内部工程字段

飞书项目的经验是：评委不需要先理解 `candidate_id`、`trace_id`、`memory_id`。工程字段放审计详情里，主答案讲人话。

Band 这次也一样：

- 页面第一屏讲“这份 RFP / 安全问卷能不能提交，哪些回答需要补证据或人工签核”。
- Agent timeline 用角色名，不用内部 UUID。
- 内部 room id、API key、agent credentials 永远不展示。
- 日志字段只在 technical appendix 里出现。

## 7. 建议新增的本地文件

后续实现时建议补这些文件：

- `docs/judge-10-minute-experience.md`
- `docs/demo-runbook.md`
- `docs/demo-evidence-report.md`
- `scripts/check_trustroom_readiness.py`
- `scripts/run_trustroom_replay.py`
- `reports/trustroom_replay.example.jsonl`

这些文件不需要开赛前全部完成，但开赛后第一天至少要有骨架。
