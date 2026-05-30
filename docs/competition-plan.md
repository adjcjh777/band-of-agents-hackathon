# 参赛作战计划

## 推荐打法

主赛道：Track 1 + Track 2 混合，但讲述时以 Track 1 的企业业务价值为主。

推荐项目：LaunchRoom，企业软件发布 / 产品上线多 Agent 作战室。

一句话：当一个团队准备发布新功能时，LaunchRoom 让 PM、工程、QA、合规/风险 Agent 通过 Band 在同一个 room 内协作，自动完成需求澄清、实现计划、风险审查、测试策略、发布 go/no-go 建议，并留下可审计协作记录。

为什么适合这个比赛：

- 满足至少 3 个 Agent，且 Band 位于核心协作层。
- 很容易演示 task handoff、shared context、@mention routing、review/veto、human approval。
- 和 Codeband 的软件开发方向天然相关，但不只是复刻 Codeband，而是补上企业发布决策与可审计流程。
- 能同时拿 Application of Technology、Presentation、Business Value、Originality 四项分。

## 从飞书项目继承的打法

这次不要只做“功能清单”，要沿用飞书 AI 挑战赛后期最有效的参赛结构：

- README 顶部先讲当前状态、能说什么、不能说什么。
- 单独准备 `judge-10-minute-experience.md`，让评委按固定路线看懂产品。
- 单独准备 `demo-runbook.md`，把 5 分钟录屏脚本和 live 失败 fallback 写死。
- 每条 live 证据都要能回放：Band room 的消息、event、handoff、state、final decision 要能导出到本地 replay。
- 真实 Band / API 不稳时，回退 replay，但不能把 replay 说成 live。
- 评委材料用人话讲业务问题；room id、agent id、trace id 只放审计详情。

## Demo 剧本

输入：用户提交一个上线请求，例如“我们要发布一个支持企业客户导入合同 PDF 并生成风险摘要的功能，请评估是否可以本周上线”。

1. Orchestrator Agent 创建 Band room，说明目标、截止时间和输出格式。
2. Product/Research Agent 澄清业务目标、用户价值、成功指标。
3. Engineering Agent 拆实现计划、依赖、风险和可完成范围。
4. QA Agent 生成测试矩阵、回归点、demo smoke test。
5. Risk/Compliance Agent 检查数据、权限、审计、人工确认点。
6. Orchestrator 汇总 go/no-go，必要时 @mention Risk Agent 或 Human Approver 请求最终判断。
7. Dashboard 展示 Band 协作时间线、每个 Agent 产物、阻塞项、最终发布建议。

关键：录屏中必须露出 Band room 的消息和事件，不然评委看不见“Band 是核心协作层”。

## 技术结构

最小可行架构：

- Web demo：FastAPI 或 Next.js，展示请求入口、协作状态、最终报告。
- Agent runtime：Python + Band SDK。
- Agents：
  - `pilot-orchestrator`
  - `product-research-agent`
  - `engineering-plan-agent`
  - `qa-review-agent`
  - `risk-compliance-agent`
- Band 层：
  - Chat room 作为每次发布评审的工作区。
  - @mention 路由任务。
  - Agent events 记录工具调用、思考摘要、错误、进度。
  - add participant / lookup peers 用来体现动态招募。
- Evidence store：
  - 本地 SQLite 或 JSONL 保存每次 run 的 mirror timeline，方便 dashboard 快速渲染。
  - 不存 API keys，不存敏感输入。

可选加分：

- 用 AI/ML API 驱动某个专职 Agent，争取 Best Use of AI/ML API partner prize。
- 用 Codeband 做代码改动/评审的参考实现或子流程，但主 demo 不依赖 Codeband 完整跑起来。
- 支持“风险升级”：Risk Agent 触发 Human approval，需要人工点 approve 才能出 go decision。

## 倒排计划

2026-05-30 至 2026-06-11：开赛前准备

- 完成 Band 账号、Discord、lablab、AI/ML API 访问。
- 读完 Band SDK setup、Connect Any Agent、Agent API、Testing Agents。
- 本地建 repo skeleton，不接真实 Band key 也能跑 mock demo。
- 准备 2 个企业案例脚本：软件发布、合规审查。
- 准备封面视觉草图和 5 分钟 demo 大纲。

2026-06-12：Kick-off

- 参加 23:00 CST Hackathon Kick-off；记录 kickoff 中公布的 access code、限制、提交细则、准确 deadline/timezone。
- 23:10-23:30 CST 重点听 lablab.ai opening words、Band opening words、Challenge introduction、Hackathon Guide。
- 2026-06-13 00:00 CST 参加 Discord Q&A，确认页面里 X402 段落是否与本赛事有关。
- 立即确认页面中 X402 文字是否只是污染。
- 建 3-5 个 Band Remote Agents，拿到 credentials，写入本机 secret 文件。
- 跑通一个 Agent 收消息并回复。

2026-06-13：端到端主链路

- 创建 room -> Orchestrator @mention 3 个 Agent -> 产出报告。
- Dashboard 展示 run timeline。
- 写最小 README 和 setup。
- 导出一份 `reports/launchroom_replay.jsonl`，保证没有 live 环境也能演示同一条协作链路。
- 起草 `docs/judge-10-minute-experience.md` 和 `docs/demo-runbook.md`。

2026-06-14 至 2026-06-15：做成产品

- 加入状态机：intake、analysis、review、approval、final。
- 加入测试/风险矩阵。
- 加入错误恢复和重新运行。
- 保存协作日志用于演示。

2026-06-16：打磨可视化和商业故事

- Dashboard 做成评委能 60 秒看懂。
- 补业务指标：减少协调会议、提高发布审查一致性、留下审计链。
- 准备 5 分钟视频脚本。

2026-06-17：稳定性与部署

- 部署 demo URL。
- 公共 GitHub 清理 secret。
- 写一键运行脚本和 sample data。
- 做 smoke test：本地、线上、空 key 失败提示。

2026-06-18：提交材料

- 录制视频。
- 生成 slide。
- 生成 cover image。
- 完成 Short Description、Long Description、Technology Tags。

2026-06-19：提交日

- 上午完成最终提交。
- 下午只做 bugfix，不做架构变动。
- 保留一份离线视频和截图，防止 live demo 波动。

## 评审对齐矩阵

Application of Technology

- 展示 Band room。
- 展示至少 3 个 Agent 被 @mention 并执行不同职责。
- 展示 shared context、handoff、state、review/veto。
- 展示 Agent event 或 timeline。

Presentation

- 先讲企业痛点，再讲 Agent 角色，再放 demo。
- 每个 Agent 产物必须短而清楚。
- 让评委知道 Band 的作用：不是聊天 UI，而是协作、路由、记忆、审计层。
- 不让评委先看内部 UUID、API key、trace 原始字段；这些放 technical appendix。

Business Value

- 不说“提升效率”这种空话。
- 量化故事：一次发布评审通常需要 PM、工程、QA、合规来回沟通，LaunchRoom 把它压缩为一次可审计流程。
- 强调企业能接受：human approval、审计日志、风险项、可追溯上下文。

Originality

- 动态招募专职 Agent。
- Risk Agent 可以 veto 或要求补证据。
- QA Agent 可以把失败项打回 Engineering Agent。
- Human 不是旁观者，而是最终审批节点。

## 当前最大风险

- Band access / promo code kickoff 才公布，开赛前不能假设所有 API 都可用。
- 页面 schedule 仍写 To be announced，必须在 kickoff 重新确认具体时间。
- X402 文字疑似页面污染，不能误选赛道。
- AI/ML API credits 可能涉及 billing/subscription，领取后要留意取消续费。
- 公开 GitHub 必须确认没有 `.env`、`agent_config.yaml`、API key、私有日志。
- 官方提交要求 Public GitHub Repository；当前准备仓库是 private，提交前必须切 public 或创建公开脱敏提交仓库。

## no-overclaim 边界

可以说：

- LaunchRoom 是 hackathon demo / working prototype。
- 至少 3 个 Agent 通过 Band 协作，Band 是核心协作层。
- Demo 展示了可见的 @mention routing、task handoff、review/veto、human approval 和 final decision。

不能说：

- 已经生产部署到真实企业。
- 已完成长期稳定运行。
- 已覆盖所有 Agent 框架和所有企业流程。
- 已完成企业级权限、审计、合规、SLA。
- replay 或 mock path 等同真实 Band live path。
