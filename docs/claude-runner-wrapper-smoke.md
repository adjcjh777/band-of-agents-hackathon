# Claude Runner Wrapper Smoke Test

- **branch**: `feature/claude-runner-wrapper-smoke`
- **owner**: Claude Code
- **status**: `runner-wrapper-smoke-ok`

## 说明

本测试通过 `scripts/run_claude_task.py` 调用真实 `claude -p`，验证 Claude Runner Wrapper 的基本写入功能。

测试环境配置：
- Claude 默认无 Bash 权限，仅允许 `Read,Write` 工具
- 使用 strict MCP config `{"mcpServers":{}}`
- 预算限制：`--max-budget-usd 0.15`

这是一个非产品功能测试，仅用于验证 wrapper 的文件写入能力。
