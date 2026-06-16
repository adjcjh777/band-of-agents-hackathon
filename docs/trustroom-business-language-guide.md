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
| Question Item / Requirement Item | TrustRoom 默认追踪的最小客户问题或需求单位 | Handoff Chain、item trace、review blocker、Final Pack inclusion | whole RFP tracking、raw chat message、anonymous agent step |
| TrustRoom Canonical Flow | Human Request -> Orchestrator -> Requirement Decomposer -> Evidence Retriever -> Answer Drafter -> Compliance Reviewer -> Human Approver -> Final Pack | 产品解释、评委路径、说明书 | internal pipeline、magic workflow |
| Visible Handoff Chain | 用户可见的 agent-to-agent 交接链路 | Agent Handoff Chain、录屏、judge route | hidden agent run、raw logs only |
| Handoff Summary | 单次 handoff 的折叠摘要，只含六字段 | 默认卡片、timeline compact view | full transcript、debug dump |
| Multi-Item Handoff | 一次影响多个 Question Item 的 handoff，折叠态仍保持六字段 | batch decomposition、batch evidence retrieval、review challenge affecting multiple items | crowded default card、hidden affected items |
| Handoff Evidence Detail | 单次 handoff 展开后的证据细节 | drill-down、审计证明、评委检查 | chain-of-thought、unredacted logs |
| Rigorous Workflow | 企业级运行标准：意图、证据、审查、审批、最终纳入都可追溯 | 产品价值、企业用户说明 | casual automation、unchecked draft |
| Full-Picture First View | 第一屏展示 Human Request、submission state、key blocker、开头 handoff | reviewer cockpit 首页 | metric wall、chat wall |
| Key Blocker | 第一屏展示的单个最高客户交付影响 blocker | first viewport blocker card、submission state | latest blocker、easy technical issue、multiple first-screen blockers |
| Owner Review Suggestion | Agent 给 human/business owner 的审核建议，不是审批 | blocker next action、approval workbench、handoff detail | agent approval、automatic sign-off |
| Owner Review Suggestion Status | Agent 建议的轻量审核状态，只跟踪建议本身 | expanded suggestion detail、audit trail | heavyweight workflow、accepted-as-approval |
| Owner Review Decision | owner 对 Agent 建议的最小回应记录：decision + reason + scope | owner response、approval workbench、audit trail | reasonless decision、blanket approval、long memo |
| Owner Review Reason | Owner Review Decision 里的短原因原文，前台不强制固定选项 | owner response、demo proof、audit trail | mandatory dropdown taxonomy、empty approval |
| Human Approval | 允许高风险 Question Item / answer 进入 Final Pack 的正式人类 gate | approval workbench、Final Pack gate、audit trail | suggestion acceptance、informal comment、blanket approval |
| Human Approval Record | Human Approval 的最小正式记录：approver_role + decision + scope + reason + validity | approval workbench、Final Pack gate、audit trail | scopeless approval、permanent-by-implication approval |
| Human Approval Decision | Human Approval Record 里的正式审批值，只能是 approved / request_changes / rejected | approval workbench、Final Pack gate、audit trail | pending-as-permission、suggestion status mixed into approval |
| Final Pack Inclusion | Question Item / answer 相对于 Final Pack 的交付处置，只能是 included / excluded / pending | Final Pack、item trace、answer table、demo ending | passed / failed、silent omission |
| Final Pack Exceptions | Final Pack 旁边的例外区块，展示 excluded / pending items 的原因、owner、next action | Final Pack view、reviewer view、demo full picture | mixing into included answers、hidden blocked items |
| Customer Export | 从 Final Pack 生成的客户可提交输出；正文默认只含 Included Answers | customer-facing export、submission body | blocked / pending items in answer body、unmarked exceptions |
| Review Appendix | Customer Export 或 reviewer package 里的非提交附录，用于透明展示 Final Pack Exceptions | customer transparency appendix、internal review package | unlabeled exception list、customer-submittable answer body |
| First-Screen Representative Paths | 第一屏展示三条代表性 Question Item 路径：ready / request_changes / blocked | first viewport handoff preview、demo opening | exhaustive item table、success-only showcase |
| Full-Picture Workflow View | 普通产品体验中展示完整流程，不是 judge-only 页面 | demo route、企业审阅路径 | judge-only page、opaque final answer |
| Final Pack | 通过证据和审批 gate 后的客户提交包 | 输出区、视频结尾、README | chatbot answer、generic report |
| Backend Audit Access | 授权后台诊断视图，展示脱敏 payload、object refs、tool outputs、timestamps、decision summaries | 运维/审计说明 | public CoT、secret dump |

### Visible Handoff Chain 的追踪单位

默认以 Question Item / Requirement Item 组织 handoff 链路，而不是以整份 RFP、单条聊天消息或单个 Agent run 组织。

推荐展示逻辑：

> Q-006 这个客户问题，从需求拆解到证据检索、回答起草、合规审查、人类审批阻塞和 Final Pack 排除，经历了哪些 handoff、证据状态和决策。

这样用户看到的是“这个客户问题为什么能答或不能答”，评委看到的是“Band 如何让 Agent 围绕共享业务对象互相 @、交接和更新状态”。

### 第一屏代表路径规则

Full-Picture First View 默认不展示全部 Question Items。第一屏只展示三条代表性 Question Item 路径，用来快速说明 TrustRoom 的 outcome diversity：

- ready / approved item：证明系统能产出可提交答案。
- request_changes item：证明 agent 间存在审查、反驳和返工。
- blocked item：证明 fail-closed gate 会阻止不安全答案进入 Final Pack。

完整 Question Item 列表放在展开区或后续 section。第一屏的目标是让用户先理解全貌，而不是被全量表格淹没。

### Key Blocker 选择规则

如果同时存在多个 blocker，Full-Picture First View 只展示一个 Key Blocker。选择标准是对 Final Pack 客户交付影响最大，而不是最新、最显眼或技术上最容易解释。

优先级：

1. `Final Pack exclusion`
2. `missing valid human approval`
3. `stale/conflicting evidence`
4. `request_changes`
5. `owner/deadline missing`

其他 blockers 放在展开列表或后续 section。Key Blocker 的标准句式必须回答：哪个 Question Item 受影响、为什么不能进入客户交付、下一步由谁处理。

Key Blocker 的 next action 第一责任人必须是 human / business owner。Agent 可以提供 Owner Review Suggestion，例如建议 scoped wording、替代证据、审批问题或下一步动作，但该建议不能替代 owner review，也不能让 item 自动进入 Final Pack。

标准句式：

> Key Blocker: Q-006 stays out of the Final Pack because incident-response evidence is stale/conflicting and no valid human approval covers the proposed wording; policy owner must approve scoped wording or provide current evidence.

Owner Review Suggestion 标准句式：

> Agent suggestion for owner review: evidence-retriever-agent found a current incident-response policy candidate and recommends the Security Policy Owner review whether it covers Q-006 scoped wording; Final Pack inclusion remains blocked until owner approval.

Owner Review Suggestion 只需要 4 个轻量状态。它们用于展开区和审计，不要求第一屏展示完整状态机：

| Status | 含义 | 边界 |
|---|---|---|
| `proposed` | Agent 已提出建议，等待 owner 审核 | 不能进入 Final Pack |
| `accepted` | owner 接受该建议作为可用方向 | 不等于最终 approval |
| `rejected` | owner 明确拒绝该建议 | item 继续 blocked 或返工 |
| `needs_revision` | owner 要 Agent 补证据、改措辞或缩小 scope | 回到 evidence / drafting / review |

默认 UI 只需要显示当前 status、owner、next action；完整状态历史放在展开项或 backend audit。这样底层严谨，但用户不会被流程细节拖慢。

Owner 对 Agent 建议做出 `accepted`、`rejected` 或 `needs_revision` 时，必须留下 Owner Review Decision。最小字段只有三项：

| Field | 含义 | 示例 |
|---|---|---|
| `decision` | owner 对建议的处理结果 | `accepted` |
| `reason` | 一句业务原因 | Current incident-response policy covers the scoped wording. |
| `scope` | 该决定适用的边界 | Applies only to Q-006 scoped wording with evidence `EV-IR-2026`. |

标准句式：

> Owner Review Decision: accepted; reason: current incident-response policy covers the scoped Q-006 wording; scope: applies only to Q-006 and evidence `EV-IR-2026`, not a blanket incident-response commitment.

Owner Review Reason 默认是短自由文本，不强制 owner 从固定选项里选择。后台或 audit 可以派生 reason category，但前台和 demo 应展示 reason 原文，证明这不是空审批。

推荐规则：

- UI：一句短 reason + scope。
- Backend / audit：可派生 reason category。
- Demo：展示 reason 原文。

避免让 owner 先选一堆下拉分类；分类服务于审计，不应该成为第一层用户负担。

### Owner Review Decision vs Human Approval

Owner Review Decision 和 Human Approval 不是同一件事。

| Concept | 回答的问题 | 结果 | 不能被误读为 |
|---|---|---|---|
| Owner Review Decision | Agent 建议是否有用，是否要接受、拒绝或修改 | suggestion 状态变化 | Final Pack 放行 |
| Human Approval | 高风险答案是否允许在特定 scope / evidence / validity 下进入 Final Pack | 正式审批 gate 通过或失败 | 泛化产品承诺 |

即使 Owner Review Decision 是 `accepted`，Question Item 仍可能因为 evidence freshness、approval validity、risk gate 或 scope 不匹配而不能进入 Final Pack。

标准句式：

> Owner accepted the Agent suggestion for Q-006 as useful, but Human Approval is still missing; Q-006 remains excluded from the Final Pack until scoped approval is recorded.

Human Approval Record 最少只需要 5 个字段：

| Field | 含义 | 示例 |
|---|---|---|
| `approver_role` | 做出正式审批的业务角色 | Security Policy Owner |
| `decision` | 正式审批结果 | `approved`, `request_changes`, or `rejected` |
| `scope` | 审批覆盖的 Question Item、wording、evidence 边界 | Applies only to Q-006 scoped wording and evidence `EV-IR-2026`. |
| `reason` | 一句业务原因 | Current policy supports the scoped incident-response statement. |
| `validity` | 有效性或过期/越界状态 | valid until the policy review date; expired; out_of_scope |

`scope` 防止把一句话的审批误读成整个产品承诺；`validity` 防止把当前审批误读成永久审批。

标准句式：

> Human Approval Record: Security Policy Owner approved Q-006 scoped wording because current incident-response policy supports it; scope is limited to evidence `EV-IR-2026`; validity ends at the next policy review.

Human Approval Decision 只保留 3 个正式值：

| Decision | 含义 | Final Pack 影响 |
|---|---|---|
| `approved` | 在指定 scope / validity 内允许该高风险答案进入后续 Final Pack gate | 可纳入，但仍要保持 evidence refs 和 no-overclaim 边界 |
| `request_changes` | 需要改 wording、补 evidence 或缩小 scope | 不能纳入，回到 drafting / evidence / review |
| `rejected` | 明确不允许当前答案进入 Final Pack | 不能纳入，保持 blocked 或另起新建议 |

不要把 `proposed`、`accepted`、`needs_revision` 等 Owner Review Suggestion 状态混入 Human Approval Decision。正式 approval gate 只回答“是否允许客户交付”。

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

Agent 可以给 human / business owner 提出 Owner Review Suggestion，但不能把 suggestion 写成 approval、sign-off 或 final-pack permission。

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

单 item 标准句式：

> `trustroom-orchestrator` @ `requirement-decomposer-agent`: decompose the Acme questionnaire into answerable items; shared object `CASE-ACME-001`; state changed from `intake` to `decomposition`; result: 8 items and 3 high-risk flags.

如果一次 handoff 同时影响多个 Question Item，默认仍展示一个 Handoff Summary，不新增第七个默认字段。展开后显示 affected Question Items 列表，并为每个 item 标出 evidence status、risk status 和 Final Pack impact。

多 item 标准句式：

> Multi-item handoff: `requirement-decomposer-agent` @ `evidence-retriever-agent`; task: retrieve evidence for 8 questionnaire items; shared object: `Q-001..Q-008`; state changed from `decomposition` to `evidence`; result: Q-001/Q-002 current, Q-006 stale/conflicting and needs review.

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

Final Pack 是客户提交包，不是“生成结果”。在产品审阅、demo 和评委查看路径里，Final Pack view 必须说明：

- included answers。
- Final Pack Exceptions。
- evidence index。
- review decisions。
- approval basis。
- remaining next actions。
- replay/live boundary if used in demo context。

Customer Export 的 answer body 范围更窄：默认只包含 Included Answers，不包含 Final Pack Exceptions。

Final Pack Inclusion 只使用三种值：

| Inclusion | 含义 | 推荐说法 |
|---|---|---|
| `included` | required evidence、review、approval gate 已满足，可以进入 Final Pack | Q-002 is included in the Final Pack with current evidence refs. |
| `excluded` | 因 blocker、rejected approval、缺失或过期证据被 fail-closed 排除 | Q-006 is excluded from the Final Pack because stale/conflicting evidence and missing valid approval fail the gate. |
| `pending` | 正在等待 evidence、owner review 或 Human Approval，尚不能视为完成 | Q-004 is pending Human Approval and cannot enter the Final Pack yet. |

不要使用 `passed` / `failed` 描述 Final Pack Inclusion。`excluded` 表示受控排除，不是系统失败；`pending` 表示等待外部或人类 gate，不是假装完成。

Final Pack 视图分成两个区块：

| 区块 | 包含内容 | 边界 |
|---|---|---|
| Included Answers | `included` items 的客户可交付回答、evidence refs、approval trail | 可以进入客户提交包 |
| Final Pack Exceptions | `excluded` / `pending` items 的 item id、reason / blocker、owner、next action | 不是客户可交付回答，不能伪装成已批准内容 |

Final Pack Exceptions 默认出现在产品审阅、demo 和评委查看路径里，用来证明 TrustRoom 没有隐藏风险项。真正的客户导出可以只导出 Included Answers；如果需要完整透明度，Exceptions 应作为附录或审阅区出现，而不是混入答案正文。

Final Pack Exceptions 标准句式：

> Final Pack Exceptions: Q-006 is excluded because incident-response evidence is stale/conflicting and no valid approval exists; owner: Security Policy Owner; next action: provide current evidence or approve scoped wording.

Customer Export 默认规则：

| Surface | 默认内容 | Exceptions 处理 |
|---|---|---|
| Product review / demo / judge view | Included Answers + Final Pack Exceptions | 必须可见，用来证明 fail-closed 全貌 |
| Customer Export answer body | Included Answers only | 不放入正文 |
| Review Appendix | 可选透明度附录 | 每个 exception 必须标记 `not customer-submittable` |

Review Appendix 标准句式：

> Review Appendix: Q-006 is not customer-submittable; it is excluded from the answer body until the Security Policy Owner provides current evidence or approves scoped wording.

Final Pack 总结标准句式：

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
| Full-Picture First View | 企业用户、评委、demo viewer | Human Request、submission state、一个 Key Blocker、三条 First-Screen Representative Paths | metric wall、raw chat wall、全量 item 表、多 blocker 并列 |
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
| 客户导出 | Customer Export answer body contains only Included Answers; Q-006 appears only in the Review Appendix as not customer-submittable. | Customer Export includes all questions, including blocked drafts. |
| Replay | This is a replay fallback that mirrors the collaboration path with redacted refs. | This is live autonomous Band proof. |

## 14. 文案检查清单

提交 UI 文案、demo 讲稿、README 或 agent message 前，逐项检查：

- 是否从 Human Request 或明确业务对象开始？
- 是否写清 From / To / Task / Shared Object / State Change / Result or Blocker？
- 是否把 Agent 角色和 Human Approver 分清？
- 是否有 evidence freshness、review status 或 approval basis？
- 是否说明哪些内容进入 Final Pack，哪些被排除？
- Customer Export answer body 是否只包含 Included Answers，且 Review Appendix 是否标记 `not customer-submittable`？
- 是否把 blocker 写成 fail-closed，而不是模糊失败？
- 是否保留 replay/live 边界？
- 是否避免生产部署、法律意见、合规认证、enterprise-grade compliance 等 overclaim？
- 是否没有泄露 secret、真实 room id、agent key、私密日志或 chain-of-thought？
