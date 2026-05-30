# 提交清单

## 账户与社区

- [ ] lablab.ai 已报名。
- [ ] 已加入 lablab.ai Discord。
- [ ] Band 账号已创建。
- [ ] 已加入 Band Discord。
- [ ] 已关注 kickoff 公告。
- [ ] AI/ML API 账号准备好，等待 kickoff promo code。

## 技术准备

- [ ] Python 3.11+。
- [ ] uv。
- [ ] Band SDK 可安装。
- [ ] 至少 3 个 Band Remote Agents 已创建。
- [ ] 每个 Agent 的 UUID 和 API key 已安全保存。
- [ ] `.env` 已加入 `.gitignore`。
- [ ] `agent_config.yaml` 已加入 `.gitignore`。
- [ ] 能在 Band room 中 @mention 一个 Agent 并收到回复。
- [ ] 能完成 3 个 Agent 的端到端协作。
- [ ] 有 mock mode，防止现场 Band/API 波动。

## Demo 验收

- [ ] Demo 第一屏能看懂业务问题。
- [ ] Demo 中明确出现至少 3 个 Agent 角色。
- [ ] Demo 展示 Band room 或 Band 协作日志。
- [ ] 有任务交接：A Agent 的输出成为 B Agent 的输入。
- [ ] 有 reviewer / risk / QA 的反驳、补证据或 veto。
- [ ] 有最终业务决策：go、no-go、conditional go。
- [ ] 有 human approval 或 escalation。
- [ ] 有审计时间线。
- [ ] 有 live path 和 replay fallback 的明确标注。
- [ ] 有 no-overclaim 页面：说明这是 hackathon demo，不是生产部署。
- [ ] 评委不需要理解内部 UUID / trace id 也能看懂主线。

## 提交材料

- [ ] Project Title，不超过 50 字符更稳。
- [ ] Short Description，不超过 255 字符。
- [ ] Long Description，至少 100 words。
- [ ] Technology & Category Tags。
- [ ] Cover Image，建议 16:9。
- [ ] Video Presentation，官方指南建议 5 分钟以内。
- [ ] Slide Presentation。
- [ ] Public GitHub Repository。当前准备仓库是 private，正式提交前需要切 public 或准备脱敏公开提交仓库。
- [ ] Demo Application Platform。
- [ ] Application URL。
- [ ] README 包含 setup、architecture、demo script、known limitations。
- [ ] License 使用 MIT 或兼容 MIT。
- [ ] `docs/judge-10-minute-experience.md` 或等价材料。
- [ ] `docs/demo-runbook.md` 或等价材料。
- [ ] `reports/launchroom_replay.example.jsonl` 或录屏中可见的 Band live evidence。

## 建议提交文案草稿

Project Title:

LaunchRoom

Short Description:

An enterprise release war room where specialized AI agents coordinate through Band to plan, review, test, and approve software launches with a visible audit trail.

Long Description 草稿：

LaunchRoom turns a messy enterprise software release review into a coordinated multi-agent workflow. A human submits a launch request, then specialized agents for product analysis, engineering planning, QA, and risk review collaborate through a Band room. They share structured context, hand off tasks, challenge each other, escalate risks, and produce a go/no-go release recommendation with an auditable timeline. Band is the core collaboration layer: agents are routed with @mentions, recruit peers when needed, exchange state, and post events that make the workflow transparent. The result is a practical enterprise workflow for teams that need faster release decisions without losing review quality, traceability, or human control.

Technology tags:

Band, Band SDK, multi-agent systems, enterprise workflow, release management, AI agents, audit trail, human-in-the-loop, Python, FastAPI, AI/ML API

## 视频结构

0:00-0:25 痛点：企业上线评审卡在跨角色沟通。

0:25-0:55 解决方案：LaunchRoom 的 Agent 角色和 Band 协作层。

0:55-3:30 Live demo：提交上线请求，3-4 个 Agent 通过 Band 协作、交接、审查、升级。

3:30-4:20 技术结构：Band room、Agent API、SDK、events、dashboard。

4:20-5:00 商业价值与下一步：更快发布、可审计、可控、可扩展到合规/采购/客服升级。

## 飞书经验带来的额外提交 gate

- [ ] 录屏前跑一遍 readiness check。
- [ ] 录屏前确认所有 secret、真实用户 ID、真实 room id 已脱敏或不展示。
- [ ] 如果 live demo 卡住，视频里切 replay fallback，并口头说明 replay / live 的区别。
- [ ] 最终长描述里避免 production、enterprise-ready deployment、fully automated compliance 这类过度承诺词。
- [ ] 提交前再次用 Chrome 打开官方页面确认 deadline、提交字段、奖项和 partner access 没有变化。
