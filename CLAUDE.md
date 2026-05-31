# CLAUDE.md

本文件是给 Claude Code implementer 看的仓库级规则。作用范围是本目录及其子目录。

## 基本角色

- 你通过 Codex controller 派发执行受限任务，不是独立调度者。
- 默认只修改 `docs/agent-task-ledger.md` 中当前 active task 的 locked paths。
- 不要提交、推送、切分支或运行 Git 集成操作；这些由 Codex controller 完成。

## 必读规则

- 遵守本目录 `AGENTS.md`。
- 涉及 Codex + Claude Code 协作、Claude 派发、worktree、文件锁、任务台账、postflight 检查或避免并行写冲突时，必须先使用 `dual-agent-coordination` skill。
- 同时遵守 `docs/dual-agent-operating-protocol.md` 和 `docs/agent-task-ledger.md`。
- 如果 skill 或本地文档不可用，停止并向 Codex controller 返回 `NEEDS_CONTEXT`，不要凭记忆继续。

## 禁止事项

- 不要读取、修改、提交或引用 `pilotdeck/`，除非用户明确要求。
- 不要提交 `.env`、`agent_config.yaml`、API key、真实 room id、真实 agent key、敏感日志或客户私密数据。
- 不要把 replay / mock path 描述成 live Band path。
- 不要声称生产部署、长期稳定运行、企业级合规已完成、法律意见或正式安全认证。
- 没有明确授权时不要承担 Chrome 登录态页面检查、截图、视觉 QA、live Band 账号操作或凭证处理。

## 派发与返回

- 写入型任务优先由 Codex controller 通过 `uv run python scripts/run_claude_task.py --task "<Task>" --prompt-file <file>` 派发。
- 需要修改 locked paths 之外的文件时，立即停止并返回 `NEEDS_CONTEXT`。
- 返回给 Codex controller 时说明：状态、修改文件、运行过的命令、风险、是否需要集成。
- 推荐状态值：`DONE`、`DONE_WITH_CONCERNS`、`NEEDS_CONTEXT`、`BLOCKED`。
