# 官方页面调研：Band of Agents Hackathon

调研日期：2026-05-29

Chrome 复核：2026-05-30，用 Chrome 打开官方页面正文重新核对比赛要求。

## 关键事实

- 比赛名称：Band of Agents Hackathon
- 主题：Build enterprise multi-agent systems with Band and Codeband
- 时间：2026-06-12 至 2026-06-19
- 赛程：
  - 2026-06-12 23:00 CST：Hackathon Kick-off
  - 2026-06-12 23:10 CST：lablab.ai opening words
  - 2026-06-12 23:15 CST：Band opening words
  - 2026-06-12 23:20 CST：Introduction to the Challenge
  - 2026-06-12 23:30 CST：Hackathon Guide
  - 2026-06-13 00:00 CST：Discord Q&A session
  - 2026-06-12 至 2026-06-19：Online Build Phase
  - 2026-06-19 23:00 CST：End of Submissions
- 形式：完全线上，可从任何地方参加。
- 奖池：总计 9,500 美元。Main prizes 为 1st $3,500、2nd $2,500、3rd $1,500；AI/ML API partner prize 为 $1,000 cash + $1,000 credits。
- 主要技术：Band、Band Documentation、Connect Any Agent、Band Agent API、Codeband、Band SDK。
- 技术伙伴：AI/ML API。
- AI/ML API 资源：页面写明每人 10 美元 credits，最多 500 名参与者，promo code 在 kickoff 公布，有效期至比赛结束。
- Partner access 注意事项：credits/promo code 由 AI/ML API 提供，可能受资格、可用性、平台条款影响；AI/ML API 可能要求 billing/subscription setup，不继续使用时要取消服务，避免赛后收费。

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

注意：官方页面写的是 Public GitHub Repository。当前本地准备仓库是 private，适合赛前准备；正式提交前要么切成 public，要么准备一个脱敏公开提交仓库。

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

Chrome 复核时，页面 DOM headings 中仍能看到一段 X402 Payments / Launch & Fund Your Startup 相关内容，包括 agent-to-agent payments、consumer AI payments、B2B FinOps、on-chain commerce primitives 等标题。

判断：这段与页面标题、Challenge、技术资源、评审标准不一致，极可能是页面模板/内容混入或隐藏/错配内容。参赛准备时不把 X402 当作主赛道，除非 Kick-off Stream 或官方 Discord 后续确认。

## 竞品/队伍粗看

Chrome 复核时页面可见部分显示已有队伍，但大多数尚未提交。已有队伍描述偏泛：

- Invictus：Pushing the frontiers of technology with creativity.
- The Blos：A team of people who do not take themselves too seriously.
- inslot2525：builds AI applications, workflows and agents to solve real life problems.
- SoloRun：Build by the people for the people.

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
