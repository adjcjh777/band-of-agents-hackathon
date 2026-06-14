# 官方页面调研：Band of Agents Hackathon

调研日期：2026-05-29

Chrome 复核：2026-05-30，用 Chrome 打开官方页面正文重新核对比赛要求。

API 文档复核：2026-06-13，用 Chrome 打开 Band 官方 API 文档与 SDK README，确认 live adapter 的接口边界。

官方页复核：2026-06-13 18:xx CST，用 Chrome 真实打开
`https://lablab.ai/ai-hackathons/band-of-agents-hackathon`，重新读取页面可见正文、资源、奖项、提交项、评审标准、日程和已提交作品列表。

## 关键事实

- 比赛名称：Band of Agents Hackathon
- 主题：Build enterprise multi-agent systems with Band and Codeband
- 时间：2026-06-12 至 2026-06-19
- 赛程：
  - 2026-06-12 23:00 CST：Hackathon Kick-off
  - 2026-06-12 23:10 CST：lablab.ai opening words
  - 2026-06-12 23:15 CST：Band opening words
  - 2026-06-12 23:20 CST：AI/ML API opening words
  - 2026-06-12 23:25 CST：Featherless opening words
  - 2026-06-12 23:30 CST：Introduction to the Challenge
  - 2026-06-12 23:35 CST：Hackathon Guide
  - 2026-06-13 00:00 CST：Discord Q&A session
  - 2026-06-12 至 2026-06-19：Online Build Phase
  - 2026-06-19 23:00 CST：End of Submissions
- 形式：完全线上，可从任何地方参加。
- 奖池：官方页当前写为总计 `$10,000+`。Main prizes 为 1st $3,500、2nd $2,500、3rd $1,500；AI/ML API partner prize 为 $1,000 cash + $1,000 credits；Featherless AI partner prize 为 1st 500 inference credits + Claw Pro plan valued at $200、2nd 300 inference credits + Claw Pro plan valued at $200、3rd 100 inference credits + Claw Pro plan valued at $200。
- 主要技术：Band、Band Documentation、Connect Any Agent、Band Agent API、Codeband、Band SDK。
- Band Pro：官方页当前给出 promo code `BANDHACK26`，可用于 1 个月 Band Pro 100% off；页面提示可能需要添加 card information，若赛后不继续使用要在下一 billing cycle 前取消。
- 技术伙伴：AI/ML API、Featherless AI。
- AI/ML API 资源：每人 $10 credits，最多 500 名参与者，有效期至比赛结束，通过 lablab.ai coupon 领取。
- Featherless AI 资源：每人 $25 credits，最多 1,000 名参与者，先到先得，激活后 1 个月有效；promo code `BOA26`，按官方 setup guide 激活。
- Partner access 注意事项：credits/promo code/setup guides/access details 由对应 partner 提供，受 availability、eligibility、platform terms、final review 影响；AI/ML API 等工具可能要求 billing/subscription setup，不继续使用时要取消服务，避免赛后收费。

## Challenge 的真实含义

官方要求参赛者构建一个跨框架多 Agent 系统，至少 3 个 Agent 通过 Band 协作，协作范围可以包括 planning、execution、review、decision-making、task handoff。

最重要的句子可以翻译成参赛准则：

- 最低门槛：至少 3 个 Agent。
- Band 不能只是壳、最终通知系统或简单输出频道。
- Agent 之间要通过 Band 进行真实协作：沟通、共享结构化上下文、委派、交接、协调状态。
- 强项目要让多 Agent 协作“可见、有用、处于核心位置”。

## 官方赛道

Track 1: Internal Enterprise Workflows

- HR、finance、procurement 工作流
- sales-to-delivery handoff
- reporting、approval、operations coordination
- customer support escalation
- cross-team operational workflows

Track 2: Multi-Agent Software Development

- planner、engineer、reviewer、tester 工作流
- cross-model code review
- multi-agent debugging/refactoring
- automated PR review and merge preparation
- QA、documentation、release coordination

Track 3: Regulated & High-Stakes Workflows

- healthcare coordination
- financial services approval
- legal review / contract workflows
- insurance claims / policy coordination
- compliance、risk、cybersecurity investigation

## 评审标准拆解

Application of Technology

- Band 是否作为多专职 Agent 的协调层。
- 是否有清晰 task handoff、shared context、role specialization、task state、coordination。

Presentation

- 是否清楚解释并演示问题、Agent 角色、Band 的协调作用、上下文与交接流、为用户/企业创造的价值。

Business Value

- 是否解决真实企业流程问题。
- 是否减少人工协调、改善决策、加速执行，或让复杂流程更容易运行。

Originality

- 是否超越简单 chatbot、单 Agent assistant、线性自动化。
- 是否体现 Agent 发现彼此、协调、分工、审查输出、升级问题、跨框架协作后才可能出现的新能力。

## 提交物

Basic Information

- Project Title
- Short Description
- Long Description
- Technology & Category Tags

Cover Image and Presentation

- Cover Image
- Video Presentation
- Slide Presentation

App Hosting & Code Repository

- Public GitHub Repository
- Demo Application Platform
- Application URL

注意：官方页面写的是 Public GitHub Repository。2026-06-14 用户已授权使用当前仓库公开提交路径，公开仓库为 https://github.com/adjcjh777/band-of-agents-hackathon；后续提交前仍需确认没有新增 secret、private report、raw live id 或无关目录进入公开分支。

## 官方资源读法

Band 文档显示，Band 的定位是给已有 Agent 增加 persistent identity、multi-agent coordination、structured memory、unified audit trail，而不替换 Agent 自己的运行框架、prompt、tools 或 LLM provider。

Band SDK 准备要求：

- Python 3.10+ 或 3.11+，不同文档页表述略有差异；保险按 Python 3.11+。
- uv package manager。
- Band account。
- LLM provider API key。
- Remote Agent 在 Band 平台创建后会得到 Agent UUID 和 API key；API key 只显示一次，必须安全保存。
- `.env` 和 `agent_config.yaml` 必须进 `.gitignore`。

Band API 设计：

- Request API：Agent 发命令，例如发消息、创建房间、管理参与者、标记消息已处理。
- Subscriptions API：平台向 Agent 推事件，例如新消息、参与者变化、房间加入、联系人请求。
- Agent API 视角是“我能和谁合作”；Human API 视角是“哪些资源属于我”。
- Agent 只能看到明确 mention 到它的消息，这个限制反而适合做 demo，因为我们可以用 @mention 明确展示任务路由。

2026-06-13 API 复核补充：

- 官方 API 文档当前跳转到 `docs-dev.band.ai`，页面标题仍为 Band。
- Agent API 的 REST base path 是 `/api/v1/agent`，Human API 是 `/api/v1/me`；两者不要混用。
- Agent REST 请求示例使用 `X-API-Key` 头鉴权。
- 创建 chat room 使用 `POST /api/v1/agent/chats`，请求体为 `{"chat": {}}`，响应里有 chat `data.id`。
- 发送文本消息使用 `POST /api/v1/agent/chats/{chat_id}/messages`，请求体为 `message.content` 和 `message.mentions`。
- 创建 chat event 使用 `POST /api/v1/agent/chats/{chat_id}/events`，请求体为 `event.content`、`event.message_type` 和可选 metadata。
- 添加参与者使用 `POST /api/v1/agent/chats/{chat_id}/participants`，请求体为 `participant.participant_id`。
- Agent real-time 文档列出 `chat_room:{room_id}`、`room_participants:{room_id}`、`agent_rooms:{agent_uuid}`、`agent_contacts:{agent_uuid}` 等 channel；本仓库 T9 先实现 REST live boundary，不在代码里声明已完成 WebSocket 订阅。
- SDK README 推荐通过 `band-sdk[langgraph]` 运行 Remote Agent，并从环境变量读取 Agent UUID / API key；仓库代码不得硬编码这些值。

Codeband 参考价值：

- 它是基于 Band.ai 的多模型 coding-agent 编排工具。
- 默认形态包括 conductor、planner、plan reviewer、coder、reviewer、mergemaster、watchdog。
- 亮点是 cross-model review、git worktree 隔离、risk-aware merging、headless/local/docker/distributed 运行。
- 风险是它本身已经覆盖“多 Agent 软件开发”的一部分，因此我们不要只复刻 Codeband；更好的方式是借鉴它的协作证据，把项目落到更具体企业工作流。

2026-06-13 官方页新增/确认资源：

- Band Hacker Guide。
- Band Pro promo code `BANDHACK26`。
- Workshops：lablab.ai kickoff、Featherless AI quick start、BAND Multi-Agent AI Infrastructure。
- Featherless AI partner resources 与 partner prize。

## 页面疑似矛盾/污染

2026-05-30 Chrome 复核时，页面 DOM headings 中仍能看到一段 X402 Payments / Launch & Fund Your Startup 相关内容，包括 agent-to-agent payments、consumer AI payments、B2B FinOps、on-chain commerce primitives 等标题。

判断：这段与页面标题、Challenge、技术资源、评审标准不一致，极可能是页面模板/内容混入或隐藏/错配内容。参赛准备时不把 X402 当作主赛道，除非 Kick-off Stream 或官方 Discord 后续确认。

2026-06-13 Chrome 可见正文复核重点仍是 Band / Codeband / AI/ML API / Featherless AI，多 Agent enterprise workflow 约束没有转向 X402。当前计划继续不把 X402 当作主线。

## 已提交作品 / 竞品粗看

2026-05-30 Chrome 复核时页面可见部分显示已有队伍，但大多数尚未提交。已有队伍描述偏泛：

- Invictus：Pushing the frontiers of technology with creativity.
- The Blos：A team of people who do not take themselves too seriously.
- inslot2525：builds AI applications, workflows and agents to solve real life problems.
- SoloRun：Build by the people for the people.

2026-06-13 官方页已出现多个 submitted concepts / prototypes / pitches，可见方向包括：

- `KINANTI Well Ops Agent System`：油井诊断、干预计划、HSE review、可审计 diagnosis pivots。
- `AEGIS: Autonomous Financial-Crime Investigation`：15 个 specialist agents 并行调查金融犯罪，强调 evidence-grounded、adversarial verification 和 verdict citations。
- `Band Memory`：让 Planner、Executor、Reviewer 跨 session 记住决策、约定和经验。
- `Balai: Agentic Meeting Hall`：共享物业紧急事件决策 room，维修协调、报价比较、费用拆分、人审和 sealed audit trail。
- `WarRoom band of agents runs your incident response`：incident response，human 持有 destructiveness key。
- `MediChain AI — Prior Auth Review`：医疗 prior authorization 多 Agent 审查。
- `Band Decision Desk`：regulated financial decision desk。
- `Aether Flow Swarm`、`OpenMind Nexus` 等风险/文档/调查类项目。

竞争含义：

- Regulated / high-stakes 和 incident/financial/medical 方向已经很拥挤。
- RFP TrustRoom 仍有差异化：具体落在 sales/security/proposal 交付链路，评委能直接看到 enterprise workflow、evidence coverage、human approval、final pack 和 replay/live 边界。
- 需要更强展示 Band 协作证据和“不是普通文档生成器”：真实 room / @mention handoff / shared context / reviewer veto / human approval / audit replay 必须成为视频主线。

## 主要来源

- https://lablab.ai/ai-hackathons/band-of-agents-hackathon
- https://docs.band.ai/welcome
- https://docs.band.ai/getting-started/connect-remote-agent
- https://docs.band.ai/api/introduction
- https://docs.band.ai/integrations/sdks/tutorials/setup
- https://docs.band.ai/integrations/sdks/tutorials/testing-agents
- https://github.com/thenvoi/codeband
- https://lablab.ai/ai-articles/hackathon-guidelines
