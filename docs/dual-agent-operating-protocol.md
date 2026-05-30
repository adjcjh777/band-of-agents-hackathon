# Codex + Claude Code 双 Agent 协作协议

最后更新：2026-05-30

本协议用于 `RFP TrustRoom` 后续开发。目标不是让两个模型同时自由改仓库，而是让它们在同一套项目规则、代码风格和验收标准下并行处理互不冲突的任务。

## 0. 不可变项目边界

- 必须遵守本目录 `AGENTS.md`。
- 默认不要读取、修改、提交或引用 `pilotdeck/`。
- 不要提交 `.env`、`agent_config.yaml`、API key、真实 room id、真实 agent key、敏感日志或客户私密数据。
- 评委材料必须保留 no-overclaim 边界：可以说 hackathon demo / working prototype，不能说生产部署、长期稳定运行或企业级合规已经完成。
- 需要详细读取 Band 或比赛网页时，Codex 使用 Chrome 插件真实打开页面；Claude Code 不承担这类任务。
- `README.md`、`pyproject.toml`、`uv.lock`、`AGENTS.md`、共享计划、公开提交文案默认由 Codex controller 统一修改。

## 1. 角色分工

### Codex Controller

Codex controller 是唯一调度者和集成者，默认由当前 Codex 会话承担。

职责：

- 读取当前计划、拆分任务、决定 owner。
- 在 `docs/agent-task-ledger.md` 记录文件锁、分支、状态和检查命令。
- 派发 Codex 或 Claude Code 任务前运行 `uv run python scripts/check_dual_agent_protocol.py`。
- Claude Code 返回后运行 `uv run python scripts/check_dual_agent_changes.py --task "<Task>"`，确认包括未跟踪文件在内的所有改动都落在 active lock 内。
- 合并任何 agent 分支前检查实际改动是否落在文件锁内。
- 执行最终测试、secret 检查、`git diff --check`、commit 和 push。

### Codex Implementer

适合任务：

- 架构判断、跨模块实现、状态机和集成逻辑。
- Dashboard、截图、视觉验收、Chrome 页面检查。
- Band live integration、外部 API 连接、最终演示路线。
- 高风险 review、no-secret / no-overclaim 最终闸门。

限制：

- 不能跳过 ledger 直接修改共享文件。
- 不能把 replay 或 mock path 说成 live path。

### Claude Code Implementer

当前 Claude Code 使用 MiMo v2.5 Pro，没有多模态能力。

适合任务：

- 独立 Python 模块、测试、脚本。
- Fictional sample、prompt、runbook、judge docs 初稿。
- 静态代码审查、文档一致性检查、边界条件测试。

不适合任务：

- Chrome 登录态页面检查。
- 截图/视觉判断。
- Dashboard 像素级 QA。
- live Band 凭证、账号、room 操作。
- 需要同时理解多处共享文件的大范围重构。

## 2. 文件锁规则

核心规则：同一时间每个路径或目录子树只能有一个 active writer。

文件锁写在 `docs/agent-task-ledger.md` 的 Active File Locks 表里。状态含义：

- `planned`：只是建议分工，不代表可以动手。
- `active`：owner 可以修改 locked paths。
- `review`：owner 已推分支，controller 正在检查。
- `ready-to-merge`：检查通过，等待合并。
- `complete`：已集成或本地任务已结束。
- `blocked`：停止执行，等待重新拆分或人工决定。

路径冲突判定：

- `src/trustroom/models.py` 与同一路径冲突。
- `src/trustroom/` 与 `src/trustroom/models.py` 冲突。
- `docs/` 与 `docs/demo-runbook.md` 冲突。
- 两个 agent 都要改共享入口文件时，必须拆成“一个 agent 写草稿文件，Codex controller 最后搬运到共享文件”。

禁止锁定：

- `pilotdeck/`
- `.env`
- `agent_config.yaml`
- 任何真实凭证、真实 room id、真实 agent key、私有日志路径

## 3. 分支与 worktree

默认做法：

1. Codex controller 在当前仓库确认 `git status --short --branch` 和 `git pull --ff-only`。
2. 对并行任务，从同一个 base SHA 创建短分支：
   - Codex 分支：`feature/codex-<task-name>`
   - Claude Code 分支：`feature/claude-<task-name>`
   - Bug 修复使用 `bugfix/<task-name>`
   - 消融实验使用 `ablation/<task-name>`
3. 并行执行时优先使用独立 worktree；如果只在一个工作区内操作，不能同时运行两个会写文件的 agent。
4. 每个分支只提交它在 ledger 中锁定的文件。
5. controller 一次只集成一个分支。合并前必须检查 diff、测试和文件锁。

不允许：

- 两个 agent 共享同一个 dirty worktree 写文件。
- 一个 agent 为了“顺手修一下”改未锁定文件。
- 在未更新 ledger 的情况下修改 README、依赖锁文件、AGENTS 或提交材料入口。

## 4. 派发前检查

Codex controller 派发任务前必须完成：

```bash
git status --short --branch
git pull --ff-only
uv run python scripts/check_dual_agent_protocol.py
```

如果存在未提交改动：

- 先判断是谁的改动。
- 不回滚用户改动。
- 如果改动影响目标任务，先把它写入 ledger 或停止询问。
- 如果是无关用户改动，任务只能修改自己的 locked paths，提交时不要把无关改动带进去。

## 5. Claude Code 派发模板

默认通过 `claude -p` 非交互派发 Claude Code。对只读或敏感任务，必须显式收口 MCP：

```bash
claude -p \
  --no-session-persistence \
  --strict-mcp-config \
  --mcp-config '{"mcpServers":{}}' \
  --max-budget-usd 0.15 \
  --tools "Read" \
  '<prompt>'
```

注意：`--mcp-config '{}'` 不是合法配置；必须使用 `{"mcpServers":{}}`。写入型任务只允许最小工具集合，例如 `Read,Write,Bash`，并通过 `--allowedTools` 限制 Bash 命令。

每次给 Claude Code 的 prompt 必须包含：

```text
你在 /Users/junhaocheng/working-dir/Band of Agents Hackathon 工作。
必须遵守 AGENTS.md、docs/dual-agent-operating-protocol.md、docs/agent-task-ledger.md。
当前模型是 MiMo v2.5 Pro，没有多模态能力；不要承担截图、视觉、Chrome 登录态页面检查。
不要读取、修改、提交或引用 pilotdeck/。
不要提交 .env、agent_config.yaml、API key、真实 room id、真实 agent key、敏感日志。
只允许修改 ledger 中本任务 locked paths。需要改共享文件时立即停止并报告。
保持 no-overclaim：只能说 hackathon demo / working prototype，不能说生产部署或企业级合规已完成。
完成后运行任务指定测试、uv run python scripts/check_dual_agent_protocol.py、uv run python scripts/check_dual_agent_changes.py --task "<Task>"、git diff --check。
返回：状态、修改文件、测试命令和结果、风险、是否需要 Codex controller 集成。
```

Claude Code 的返回状态只能是：

- `DONE`
- `DONE_WITH_CONCERNS`
- `NEEDS_CONTEXT`
- `BLOCKED`

## 6. Codex 自身执行模板

Codex 做实现任务前同样要读 ledger，并确认：

- 当前任务是否 active。
- locked paths 是否覆盖所有待改文件。
- 是否需要 Chrome 或多模态检查。
- 是否会触碰共享入口文件。

如果任务需要新增共享文件，先更新 ledger，再动手。

## 7. 集成与审查

agent 分支返回后，Codex controller 按顺序执行：

```bash
git fetch origin
git diff --name-only <base_sha>..<agent_branch>
uv run python scripts/check_dual_agent_protocol.py
uv run python scripts/check_dual_agent_changes.py --task "<Task>"
git diff --check
```

然后检查：

- 实际改动是否全部在 locked paths 内。不要只用 `git diff --name-only` 判定，因为它不会列出未跟踪文件；必须用 `scripts/check_dual_agent_changes.py` 覆盖 `git status --porcelain` 中的 changed paths。
- 是否误碰 `pilotdeck/`、secret、私有日志。
- 是否和 README / PRD / 计划里的 no-overclaim 边界一致。
- 是否有测试或文档证明任务完成。
- 是否需要 Codex 做视觉、Chrome、live Band 补验。

只有这些通过，才能 merge。

## 8. 冲突处理

如果发现冲突：

1. 立即停止集成。
2. 把冲突任务在 ledger 标成 `blocked`。
3. 确认是文件锁设计错误、任务边界错误，还是 agent 越界。
4. 重新拆分：
   - 一个 owner 继续持有共享文件。
   - 另一个 owner 改为写草稿、fixture、测试或 review note。
5. 重新运行 `uv run python scripts/check_dual_agent_protocol.py`。

不要把两个 agent 的冲突 patch 手工糊在一起后直接提交。

## 9. 当前推荐路线

短期内采用保守并行：

- Codex 先做 T1/T2/T4/T7/T9/T11/T12。
- Claude Code 先做 T3/T6/T8/T10 中的独立文本、测试、脚本部分。
- 所有共享文档入口、README、依赖、最终提交材料由 Codex controller 集成。

这样可以利用 Claude Code 的文本/代码吞吐，同时把多模态、Chrome、live Band 和最终一致性留给 Codex。
