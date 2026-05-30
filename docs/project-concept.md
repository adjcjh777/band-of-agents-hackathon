# 推荐项目概念：LaunchRoom

LaunchRoom 是 Band of Agents Hackathon 的推荐项目概念：面向企业软件发布 / 产品上线的多 Agent 作战室。

## 核心故事

企业发布一个新功能时，PM、工程、QA、合规/风险通常要在多个文档、聊天窗口和会议中来回同步。LaunchRoom 把这件事变成一次可追踪的 Band 协作流程：不同专职 Agent 在同一个 room 中被 @mention、共享上下文、移交任务、提出风险、要求补证据，并最终形成 go/no-go 发布建议。

## Agent 角色

- `launch-orchestrator`：创建 room、分派任务、维护状态、汇总最终建议。
- `product-research-agent`：明确用户问题、业务价值、成功指标。
- `engineering-plan-agent`：分析实现范围、依赖、上线风险、回滚策略。
- `qa-review-agent`：生成测试矩阵、回归风险、验收标准。
- `risk-compliance-agent`：检查数据、权限、审计、合规、人审节点。

最低 demo 可以先实现前三个 Agent，再逐步扩到五个。

## 端到端流程

1. 用户提交发布请求。
2. Orchestrator 在 Band 创建协作 room。
3. Orchestrator @mention Product Agent 产出业务摘要。
4. Product Agent @mention Engineering Agent 请求实现计划。
5. Engineering Agent @mention QA Agent 请求测试矩阵。
6. QA Agent @mention Risk Agent 请求高风险项复核。
7. Risk Agent 如发现风险，@mention Engineering Agent 要求补证据，或 @mention Human Approver。
8. Orchestrator 汇总最终 release decision。
9. Dashboard 展示 timeline、Agent 产物、open risks、final recommendation。

## 最小实现

- Python + Band SDK 跑远程 Agent。
- FastAPI 提供请求入口和 timeline API。
- SQLite/JSONL 保存每次 run 的镜像事件，方便前端渲染。
- 一个简单网页展示：
  - Release request
  - Agent status
  - Band collaboration timeline
  - Final release report

## 成功标准

- 评委能在 60 秒内看懂“这是企业发布评审”。
- 评委能看到至少 3 个 Agent 通过 Band 互相协作。
- 评委能看到 Band 不是最终通知，而是任务路由、共享上下文、状态协调和审计层。
- 最终报告不是普通总结，而是带证据、风险项、测试项和人审建议的发布决策。
- 真实 Band 路径和 replay fallback 都能展示同一条协作时间线。
- 讲述中始终把 LaunchRoom 定位为 hackathon prototype，不夸成生产系统。

## 受飞书项目启发的产品细节

- 像飞书项目的 `candidate -> active -> superseded` 一样，LaunchRoom 也要有清楚的状态：`intake -> analysis -> review -> escalation -> decision`。
- 像飞书项目强调 evidence quote 一样，LaunchRoom 每个 Agent 的结论都要带来源：原始请求、上游 Agent 输出、测试结果或风险理由。
- 像飞书项目的 permission fail-closed 一样，LaunchRoom 的 high-risk decision 不能自动 go，必须进入 human approval。
- 像飞书项目的 demo replay 一样，LaunchRoom 要能把一次 Band 协作导出为本地可回放 timeline。

## 后续扩展

- 接入 GitHub PR / issue 作为真实输入。
- 接入 Codeband，让 Engineering Agent 能派发代码任务。
- 接入 AI/ML API 驱动风险抽取或多模态文档解析。
- 加入 Slack/Feishu/Jira 的 mock connector。
- 加入 approval policy：高风险项必须 human approve。
