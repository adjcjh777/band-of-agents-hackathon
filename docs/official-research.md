# 官方页面调研：Band of Agents Hackathon

调研日期：2026-05-29

## 关键事实

- 比赛名称：Band of Agents Hackathon
- 主题：Build enterprise multi-agent systems with Band and Codeband
- 时间：2026-06-12 至 2026-06-19
- 赛程：
  - 2026-06-12：Kick-off Stream
  - 2026-06-12 至 2026-06-19：Online Build Phase
  - 2026-06-19：Project Submissions Ends
- 形式：完全线上，可从任何地方参加。
- 奖池：总计 9,500 美元。
- 主要技术：Band、Band Documentation、Connect Any Agent、Band Agent API、Codeband、Band SDK。
- 技术伙伴：AI/ML API。
- AI/ML API 资源：页面写明每人 10 美元 credits，最多 500 名参与者，promo code 在 kickoff 公布，有效期至比赛结束。

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

Codeband 参考价值：

- 它是基于 Band.ai 的多模型 coding-agent 编排工具。
- 默认形态包括 conductor、planner、plan reviewer、coder、reviewer、mergemaster、watchdog。
- 亮点是 cross-model review、git worktree 隔离、risk-aware merging、headless/local/docker/distributed 运行。
- 风险是它本身已经覆盖“多 Agent 软件开发”的一部分，因此我们不要只复刻 Codeband；更好的方式是借鉴它的协作证据，把项目落到更具体企业工作流。

## 页面疑似矛盾/污染

官方页面在 Track 3 后面出现了一段 X402 Payments / Launch & Fund Your Startup 的文字，并列出了 agent-to-agent payments、consumer AI payments、B2B FinOps、on-chain commerce primitives 等内容。

判断：这段与页面标题、Challenge、技术资源、评审标准不一致，极可能是页面模板/内容混入。参赛准备时不把 X402 当作主赛道，除非 Kick-off Stream 或官方 Discord 后续确认。

## 竞品/队伍粗看

页面和搜索索引能看到已有队伍，但大多数尚未提交。已有队伍想法偏泛：

- wereadthedocs：初学者探索 agentic systems。
- The Band of Hawk：交易/投研风格，多 Agent 争论与 veto。
- HumanLoop AI：human-centered multi-agent，强调透明、可控、enterprise-ready。
- Fovea：把复杂 workflow 变简单的 AI 工具。
- AK Agents / EVOLUTICS / Invictus 等描述较泛。

机会：不要做“泛 AI 工具”或“我们很创新”的口号型项目。用一个真实企业流程、清楚的状态机、可视化审计链和 Band room 证据打穿。

## 主要来源

- https://lablab.ai/ai-hackathons/band-of-agents-hackathon
- https://docs.band.ai/welcome
- https://docs.band.ai/getting-started/connect-remote-agent
- https://docs.band.ai/api/introduction
- https://docs.band.ai/integrations/sdks/tutorials/setup
- https://docs.band.ai/integrations/sdks/tutorials/testing-agents
- https://github.com/thenvoi/codeband
- https://lablab.ai/ai-articles/hackathon-guidelines
