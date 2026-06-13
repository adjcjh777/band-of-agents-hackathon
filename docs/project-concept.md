# 推荐项目概念：RFP TrustRoom

RFP TrustRoom 是 Band of Agents Hackathon 的推荐项目概念：面向 B2B 售前团队的 RFP / 安全问卷 / 证据同源协作室。

## 核心故事

企业响应客户 RFP、安全问卷或尽调材料时，售前、产品、安全、法务、交付和 SME 通常要在文档、邮件、知识库和会议中来回同步。RFP TrustRoom 把这件事变成一次可追踪的 Band 协作流程：不同专职 Agent 在同一个 room 中被 @mention、共享结构化上下文、移交任务、引用证据、发现冲突、要求人工签核，并最终形成可提交的回答包、证据索引和审计时间线。

这个方向比普通 RFP 自动起草更适合本比赛：Band 不是最后通知渠道，而是任务路由、证据交接、冲突仲裁、状态协调和 human approval 的核心协作层。

## Agent 角色

- `trustroom-orchestrator`：创建 room、导入材料、分派任务、维护状态、汇总提交包。
- `requirement-decomposer-agent`：拆解 RFP 条款、问题、评分点、截止时间和责任人。
- `evidence-retriever-agent`：从公司知识库、过往答案、安全文档和政策片段中检索可引用证据。
- `answer-drafter-agent`：基于需求和证据起草 RFP / security questionnaire 回答。
- `compliance-review-agent`：检查过度承诺、证据过期、合规风险和必须人工确认的问题。
- `sme-approver`：人类 SME 或 reviewer，对高风险回答做批准、退回或补充。

最低 demo 可以先实现前三个自动 Agent 加一个 human approval 节点，再逐步扩到五个角色。

## 端到端流程

1. 用户上传一个客户 RFP、一份安全问卷和若干公司知识库片段。
2. Orchestrator 在 Band 创建协作 room，发布目标、截止时间和输出格式。
3. Orchestrator @mention Requirement Decomposer 拆出问题清单、风险等级和责任标签。
4. Decomposer @mention Evidence Retriever 为每个问题寻找可引用证据。
5. Evidence Retriever @mention Answer Drafter，传递证据链接、来源、有效期和缺口。
6. Answer Drafter 生成回答草稿，并把高风险回答 @mention Compliance Reviewer。
7. Compliance Reviewer 发现过期证据、不可承诺条款或缺证据回答时，@mention Retriever / Drafter 返工，或 @mention SME Approver。
8. SME Approver 对高风险项 approve / request changes / reject。
9. Orchestrator 汇总最终 answer pack、security questionnaire 表格、evidence index 和 audit replay。
10. Dashboard 展示 timeline、Agent 产物、open risks、final submission pack。

## 最小实现

- Python + Band SDK 跑远程 Agent。
- FastAPI 或 Next.js 提供材料入口和 timeline API。
- SQLite/JSONL 保存每次 run 的镜像事件，方便前端渲染。
- 样例材料用 Markdown/CSV/JSON，不接真实客户系统。
- 一个简单网页展示：
  - RFP / questionnaire input
  - Agent status
  - Band collaboration timeline
  - Draft answers
  - Evidence index
  - Review / approval state
  - Final submission pack

## 成功标准

- 评委能在 60 秒内看懂“这是 B2B 售前响应 RFP / 安全问卷”。
- 评委能看到至少 3 个 Agent 通过 Band 互相协作。
- 评委能看到 Band 不是最终通知，而是任务路由、共享上下文、状态协调和审计层。
- 最终报告不是普通问答，而是带证据来源、有效期、风险项、审查意见和人工签核的提交包。
- 真实 Band 路径和 replay fallback 都能展示同一条协作时间线。
- 讲述中始终把 RFP TrustRoom 定位为 hackathon prototype，不夸成生产系统、法律意见、合规认证或自动投标系统。

## 受飞书项目启发的产品细节

- 像飞书项目的 `candidate -> active -> superseded` 一样，RFP TrustRoom 也要有清楚的状态：`intake -> decomposition -> evidence -> drafting -> review -> approval -> submission_pack`。
- 像飞书项目强调 evidence quote 一样，RFP TrustRoom 每个回答都要带来源：原始 RFP 条款、证据片段、政策文档、上游 Agent 输出或 reviewer 备注。
- 像飞书项目的 permission fail-closed 一样，高风险承诺、缺证据回答、过期政策引用不能自动通过，必须进入 human approval。
- 像飞书项目的 demo replay 一样，RFP TrustRoom 要能把一次 Band 协作导出为本地可回放 timeline。

## 后续扩展

- 接入 Google Drive / Notion / Confluence / Feishu 文档作为知识库来源。
- 支持 XLSX 安全问卷导入和导出。
- 接入 AI/ML API、Featherless AI 或 mimo token plan 驱动文档理解、证据匹配、回答起草或 review summarization；只有真实接入并可复现时才放进提交主叙事。
- 加入 policy freshness：证据过期、来源不可信或引用冲突时自动升级。
- 加入 approval policy：高风险承诺必须 human approve。
