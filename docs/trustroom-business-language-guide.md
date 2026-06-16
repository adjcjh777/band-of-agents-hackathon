# RFP TrustRoom 业务语言说明书

本说明书定义 TrustRoom 的受控业务语言。它用于 UI 文案、demo 讲稿、agent handoff 消息、提交材料、证据说明和后台审计摘要，目标是让企业用户和评委用同一套词理解：人类提出什么业务请求，哪些 Agent 互相 @ 并交接任务，哪些证据支持回答，哪里被审查或阻塞，哪些内容最终进入 Final Pack。

这不是实现规格，也不是法律、合规或生产部署声明。TrustRoom 当前仍应被描述为 hackathon demo / working prototype，并保持 live path 与 replay fallback 的边界。

## 1. 核心产品句

标准说法：

> RFP TrustRoom 是一个 Band-coordinated collaboration room：人类提交 RFP / 安全问卷和知识材料后，Orchestrator 将任务 @ 给专职 Agent；Agent 之间通过可见 handoff 交接问题、证据、草稿和审查意见；高风险或缺证据回答进入 human approval；只有证据和审批通过的内容进入 Final Pack。

禁止把主线说成：

- 一个通用 chatbot。
- 一个自动生成 RFP 的工具。
- 一个生产级合规系统。
- 一个只给评委看的展示页。
- 一个隐藏运行、只展示最终结果的自动化脚本。

## 2. 写作原则

1. 从 Human Request 开始，不从 dashboard、指标或内部实现开始。
2. 每句话优先写业务角色和业务对象，再写技术机制。
3. 每个关键状态都必须能回答：谁交给谁、交付什么对象、状态如何变化、结果或 blocker 是什么。
4. 每个面向客户的答案都要能追到 evidence freshness、review status、approval basis 和 final-pack decision。
5. 展开项展示可审计证据，不展示完整 chain-of-thought。
6. backend audit access 只给授权操作者看，并且必须脱敏 secret、真实 room id、agent key、原始私密日志。
7. replay fallback 不能被描述成 live autonomous proof。
8. 不承诺生产部署、法律意见、合规认证、长期 SLA 或企业级合规已完成。

## 3. 受控词表

| Canonical Term | 严格含义 | 推荐使用场景 | 避免说法 |
|---|---|---|---|
| Human Request | 人类发起的业务请求和材料，包括 RFP、安全问卷、截止时间、输出要求、知识片段 | 第一屏、demo 开头、run 创建 | prompt、ticket、raw upload |
| Request Summary | TrustRoom 对 Human Request 的业务理解摘要 | 第一屏、intake 结果、录屏主线 | classifier result、upload list |
| TrustRoom Canonical Flow | Human Request -> Orchestrator -> Requirement Decomposer -> Evidence Retriever -> Answer Drafter -> Compliance Reviewer -> Human Approver -> Final Pack | 产品解释、评委路径、说明书 | internal pipeline、magic workflow |
| Visible Handoff Chain | 用户可见的 agent-to-agent 交接链路 | Agent Handoff Chain、录屏、judge route | hidden agent run、raw logs only |
| Handoff Summary | 单次 handoff 的折叠摘要，只含六字段 | 默认卡片、timeline compact view | full transcript、debug dump |
| Handoff Evidence Detail | 单次 handoff 展开后的证据细节 | drill-down、审计证明、评委检查 | chain-of-thought、unredacted logs |
| Rigorous Workflow | 企业级运行标准：意图、证据、审查、审批、最终纳入都可追溯 | 产品价值、企业用户说明 | casual automation、unchecked draft |
| Full-Picture First View | 第一屏展示 Human Request、submission state、key blocker、开头 handoff | reviewer cockpit 首页 | metric wall、chat wall |
| Full-Picture Workflow View | 普通产品体验中展示完整流程，不是 judge-only 页面 | demo route、企业审阅路径 | judge-only page、opaque final answer |
| Final Pack | 通过证据和审批 gate 后的客户提交包 | 输出区、视频结尾、README | chatbot answer、generic report |
| Backend Audit Access | 授权后台诊断视图，展示脱敏 payload、object refs、tool outputs、timestamps、decision summaries | 运维/审计说明 | public CoT、secret dump |

## 4. 角色命名规范

自动 Agent 使用固定角色名，不使用泛化的 bot / AI assistant：

| Role | 业务责任 | 不能承担的说法 |
|---|---|---|
| `trustroom-orchestrator` | 创建 run / room，发布目标，分派任务，维护状态，汇总 Final Pack | 不能替代 human approver 做高风险批准 |
| `requirement-decomposer-agent` | 拆解 RFP 条款、问卷问题、风险等级、证据需求 | 不能宣称已经找到证据 |
| `evidence-retriever-agent` | 检索证据候选，标注来源、freshness、缺口或冲突 | 不能把 stale / missing evidence 当 current evidence |
| `answer-drafter-agent` | 基于证据起草回答，并保留 evidence refs | 不能绕过 review 直接进入 Final Pack |
| `compliance-review-agent` | 检查 overclaim、证据缺口、过期证据、审批要求 | 不能给法律意见或合规认证 |
| `Human Approver` / `SME Approver` | 人类对高风险回答做 scoped approval、request changes 或 reject | 不能伪装成 autonomous agent |

当文案需要面向业务用户时，可以使用更通俗的角色标签，但必须保留职责边界：

- Orchestrator = workflow owner
- Requirement Decomposer = requirement analyst
- Evidence Retriever = evidence owner
- Answer Drafter = proposal writer
- Compliance Reviewer = risk reviewer
- Human Approver = named business approver

## 5. Request Summary 标准字段

第一屏的 Request Summary 必须说明 TrustRoom 识别了什么，而不是只显示上传列表。

| 字段 | 含义 | 示例写法 |
|---|---|---|
| Customer Goal | 客户或销售团队想完成的业务目标 | Prepare an evidence-backed security questionnaire response for Acme. |
| Input Materials | 本次 run 使用的业务材料 | RFP markdown, security questionnaire, knowledge snippets. |
| Deadline | 需要完成或提交的时间约束 | Customer due date: Friday 17:00. |
| Expected Output | 预期交付物 | Final Pack with answers, evidence index and approval trail. |
| Risk Hints | 初始风险或注意项 | Incident response claims and regional hosting promises need review. |
| Agent Chain Started | 已启动的协作链 | Orchestrator -> Decomposer -> Retriever -> Drafter -> Reviewer -> Human Approver. |

标准句式：

> TrustRoom understood the Human Request as: prepare an evidence-backed questionnaire response, using the sample RFP and knowledge pack, with high-risk security promises routed to review before any Final Pack inclusion.

## 6. Handoff Summary 六字段

折叠态只展示这六项，保证评委和企业用户不用读 raw logs 也能看懂 agent 交接。

| 字段 | 严格定义 | 示例 |
|---|---|---|
| From | 发起交接的角色 | `trustroom-orchestrator` |
| To | 接收任务的角色 | `requirement-decomposer-agent` |
| Task | 可执行业务指令 | Decompose 8 questionnaire items and assign risk. |
| Shared Object | 被交接的业务对象 | `Q-001..Q-008`, evidence pack, draft answer, review decision |
| State Change | run 或 item 的业务状态变化 | `intake -> decomposition` |
| Result / Blocker | 交接结果、阻塞原因或下一步 | 8 items created; Q-006 flagged high risk. |

标准句式：

> `trustroom-orchestrator` @ `requirement-decomposer-agent`: decompose the Acme questionnaire into answerable items; shared object `CASE-ACME-001`; state changed from `intake` to `decomposition`; result: 8 items and 3 high-risk flags.

## 7. Handoff Evidence Detail 展开项

展开后可以显示更深证据，但仍然不是完整思考过程。

允许展示：

- supporting Band-style message summary。
- redacted `band-ref:*` 或 event ref。
- shared object ids，例如 question id、evidence id、draft id、review id、approval id。
- timestamp 或 elapsed time。
- decision reason summary。
- evidence freshness。
- approval scope、validity、expires label。
- tool input / output 的业务摘要。

禁止展示：

- chain-of-thought。
- API key、agent key、真实 room id、真实 message id。
- 未脱敏 provider metadata。
- 私密客户数据或真实日志。
- 与该 handoff 无关的 debug dump。

## 8. 状态语言

| State | 用户可见标签 | 严格含义 | 允许下一步 |
|---|---|---|---|
| `intake` | Intake | Human Request 和材料进入 TrustRoom | triage / decomposition |
| `triage` | Triage | Orchestrator 分配 owner、risk、evidence need | decomposition / evidence |
| `decomposition` | Decomposition | 问题被拆成可回答 item | evidence |
| `evidence` | Evidence | Retriever 给 item 找证据或标出缺口 | drafting / review |
| `drafting` | Drafting | Drafter 基于证据生成受控回答 | review |
| `review` | Review | Reviewer 检查 overclaim、证据状态和审批要求 | evidence / drafting / approval / blocked |
| `approval` | Human Approval | 人类对高风险项做 scoped decision | final pack / request changes / blocked |
| `submission_pack` | Final Pack | 通过 gate 的内容进入客户提交包 | export / replay / audit |

不要把 `blocked` 写成失败。标准说法是 fail-closed：系统阻止不安全答案进入 Final Pack。

## 9. Evidence / Review / Approval 语言

Evidence freshness：

- `current`: 证据可用于当前样例回答。
- `stale`: 证据过期或时间边界不满足。
- `missing`: 没有足够证据支持该回答。
- `unknown`: freshness 未确认。
- `conflicting`: 证据之间存在冲突，不能静默纳入。

Review status：

- `approved`: 当前证据和风险边界下可继续。
- `request_changes`: 需要补证据、改措辞或缩小承诺范围。
- `needs_human_approval`: 高风险或敏感承诺需要具名人类批准。
- `blocked`: 证据缺失、过期、冲突，或答案会 overclaim。

Approval validity：

- `valid`: 只在当前 scope、wording、evidence refs、样例 run 内有效。
- `expired`: 审批有效期已过。
- `out_of_scope`: 审批不覆盖当前 wording 或证据范围。
- `missing`: 没有附着审批记录。

标准句式：

> Q-006 is blocked because incident-response evidence is stale and conflicting, and no valid human approval covers the proposed wording. It stays out of the Final Pack.

## 10. Final Pack 语言

Final Pack 是客户提交包，不是“生成结果”。它必须说明：

- included answers。
- excluded / blocked items。
- evidence index。
- review decisions。
- approval basis。
- remaining next actions。
- replay/live boundary if used in demo context。

标准句式：

> Final Pack includes 7 of 8 answers with evidence refs and approval trail; Q-006 is excluded because stale/conflicting evidence and missing valid approval fail the gate.

## 11. Live / Replay 边界语言

允许说：

- `REPLAY fallback`: deterministic replay used for stable judge review.
- `MOCK local run`: local deterministic run, not live Band proof.
- `REST live smoke verified`: Band REST room / peer / event boundary was separately verified, when evidence exists.
- `Autonomous live replies remain blocked`: challenge-token reply evidence is missing or peer is not connected.
- `Public-safe dashboard`: no live credentials or raw identifiers are deployed.

禁止说：

- complete autonomous live Band workflow, unless challenge-token reply evidence exists.
- production-ready deployment。
- enterprise-grade compliance。
- certified security product。
- legal advice。
- guaranteed security outcomes。
- fully automated compliance approval。

## 12. 展示层级

TrustRoom 使用四层展示，不需要单独为评委做一个判断页。

| 层级 | 默认用户 | 展示内容 | 不展示 |
|---|---|---|---|
| Full-Picture First View | 企业用户、评委、demo viewer | Human Request、submission state、key blocker、开头 handoff | metric wall、raw chat wall |
| Full-Picture Workflow View | 企业用户、评委、demo viewer | Visible Handoff Chain、evidence review、approval、Final Pack、replay/live boundary | judge-only path |
| Handoff Evidence Detail | reviewer、评委、operator | 单次 handoff 的证据摘要、object refs、approval context | chain-of-thought、secret |
| Backend Audit Access | 授权 operator | 脱敏 payload、tool I/O 摘要、timestamps、decision summaries | public raw logs、secret dump |

## 13. 好 / 坏示例

| 场景 | 推荐说法 | 避免说法 |
|---|---|---|
| 第一屏 | Human Request: Acme security questionnaire; current state: draft pack ready with exclusions; key blocker: Q-006 lacks valid approval. | AI finished the task. |
| Agent 协作 | Decomposer @ Retriever with Q-001..Q-008 evidence needs; Retriever returned current, stale and missing evidence labels. | Agents talked in the background. |
| Review loop | Reviewer requested changes on Q-004 because the first draft overcommitted regional hosting. | The AI refined the answer. |
| 人审 | Legal approver gave scoped approval for Q-004 pilot wording until the stated expiry. | Legal approved the whole product. |
| 阻塞 | Q-006 stays out of the Final Pack because evidence is stale/conflicting and no valid approval exists. | The system failed Q-006. |
| Replay | This is a replay fallback that mirrors the collaboration path with redacted refs. | This is live autonomous Band proof. |

## 14. 文案检查清单

提交 UI 文案、demo 讲稿、README 或 agent message 前，逐项检查：

- 是否从 Human Request 或明确业务对象开始？
- 是否写清 From / To / Task / Shared Object / State Change / Result or Blocker？
- 是否把 Agent 角色和 Human Approver 分清？
- 是否有 evidence freshness、review status 或 approval basis？
- 是否说明哪些内容进入 Final Pack，哪些被排除？
- 是否把 blocker 写成 fail-closed，而不是模糊失败？
- 是否保留 replay/live 边界？
- 是否避免生产部署、法律意见、合规认证、enterprise-grade compliance 等 overclaim？
- 是否没有泄露 secret、真实 room id、agent key、私密日志或 chain-of-thought？
