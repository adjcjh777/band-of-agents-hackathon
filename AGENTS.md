# AGENTS.md

本文件是给 Codex / 自动执行代理看的项目规则。作用范围是本目录及其子目录。

## 语言规则

- 内部思考和对用户回复默认使用中文。
- 面向用户、队友或评委的文档优先写成清楚、直接、可执行的中文，不要堆内部术语。

## 项目边界

- 当前项目是 Band of Agents Hackathon 的参赛准备与后续实现仓库。
- 默认主线是 `RFP TrustRoom`：一个用 Band 协调多 Agent 的 RFP / 安全问卷 / 证据同源售前协作原型。
- `pilotdeck/` 是另一个 agent 的工作目录，默认不要读取、修改、提交或引用；只有用户明确要求时才处理。
- 不要提交 `.env`、`agent_config.yaml`、API key、真实 room id、真实 agent key、日志里的敏感标识或本地私密数据。

## 网页调研规则

- 如果需要详细读取网页内容，尤其是动态页面、登录态页面、需要截图/视觉确认的页面，优先使用 `@Chrome` / Chrome 插件真实打开页面读取。
- 我已经创建了 band 账号 如果你要执行操作 用 chrome 访问就行  https://app.band.ai/dashboard
- 不要只依赖 `curl`、静态 HTML、搜索摘要或搜索索引来判断页面细节；这些只能作为初筛。
- 如果 Chrome 插件无法连接或页面无法完整读取，要在结论里明确说明信息不完整，并标出哪些内容需要后续用 Chrome 或官方页面重新确认。
- 对比赛时间、规则、奖项、提交要求、赞助资源、评审标准等会变动的信息，必须以官方页面或官方文档为准，并记录读取日期。

## 参赛材料规则

- 评委材料要优先展示真实产品主路径：问题、Agent 角色、Band 协作、任务交接、审查/反驳、human approval、最终决策。
- 每个 demo 都要准备 live path 和 replay fallback；replay 不能伪装成 live。
- README、提交文案、视频讲稿和 demo 文档都必须保留 no-overclaim 边界：可以说 hackathon demo / working prototype，不能说生产部署、长期稳定运行或企业级合规已完成。
- 参考飞书 AI 挑战赛经验：尽早准备 `judge-10-minute-experience.md`、`demo-runbook.md`、证据报告、readiness check 和 replay 文件，不要最后一天才补。

## Git 规则

- 修改前先确认当前目录和分支，并执行 `git pull --ff-only`。
- 修改完成后执行必要检查，至少跑 `git diff --check`。
- 提交前确认 `pilotdeck/`、secret、日志和本地报告没有被误加入。
- 提交并推送当前分支；提交信息要简洁说明改动。

## 双 Agent 协作规则

- 涉及 Codex + Claude Code 协作、Claude 派发、worktree、文件锁、任务台账、postflight 检查或避免并行写冲突时，必须先使用 `dual-agent-coordination` skill。
- 本仓库的协作事实来源是 `docs/dual-agent-operating-protocol.md` 和 `docs/agent-task-ledger.md`；不要只依赖聊天上下文判断文件锁。
- 写入型 Claude Code 任务优先通过 `scripts/run_claude_task.py` 派发；Codex controller 负责最终检查、集成、提交和推送。
- 派发或集成前运行 `uv run python scripts/check_dual_agent_protocol.py`；Claude Code 写入任务返回后运行 `uv run python scripts/check_dual_agent_changes.py --task "<Task>"`。
- 当用户要求“规划今天任务”“给 agent 分配任务”“继续推进目标”或类似多 agent 调度时，controller 不能只在当前聊天里总结；必须通过 Agent Bus 可见投递把 bounded task 发给对应执行、测试、UI/UX、研究/探索线程。
- Agent Bus 可见投递默认使用 Codex thread delivery，例如 `codex_app.send_message_to_thread`；本地 bus 记录或口头说明不能替代目标线程可见消息。
- 如果当前 controller 会话没有可用的 `codex_app.send_message_to_thread` handler，不能把 `trigger=codex_app` 返回的 `prepared` 当作已送达。必须改用可闭环验证的 fallback：`CODEX_AGENT_BUS_TRANSPORT=exec ~/.codex/tools/codex-agent-bus/bin/agent-bus send <target> "<message>" --trigger resume --wait --timeout-sec <seconds>`，并确认目标 agent 通过 `reply_message` 或 CLI fallback `agent-bus reply <message_id> ... --trigger queue` 返回 ACK。
- Agent Bus 派发验收标准是 `delivered_at` 存在且 planner/controller inbox 收到带 `parent_message_id` 的 reply；仅有 `prepared`、仅有本地 inbox 记录或仅有 app-server `turn/start` ACK 都不能算完成派发。
- 每条派发消息必须包含 task name、owner、输入/禁止范围、locked paths 或 read-only 声明、必跑命令、PASS/BLOCKED 标准、证据落盘位置和 no-overclaim / secret / `pilotdeck/` 边界。
- 任务派发后，controller 的用户汇报必须列出已通知的 agent/thread、各自任务和当前未验证项；如果某个任务因 live 凭证、Chrome 登录态、外部表单或部署授权需要人工动作，必须明确标为 controller/user-owned gate。

## 默认入口

- 先读 `README.md`。
- 官方信息和调研：`docs/official-research.md`。
- 作战计划：`docs/competition-plan.md`。
- 项目概念：`docs/project-concept.md`。
- 提交清单：`docs/submission-checklist.md`。
- 飞书经验迁移：`docs/feishu-lessons-for-band.md`。
