# Deployment Notes

这些说明用于把 RFP TrustRoom 作为公开安全的 hackathon demo 部署。当前推荐平台是 Render Web Service；在用户明确决定 public repo 策略和 demo URL 之前，不把本仓库切 public，也不声称已经完成线上部署。

## Public-Safe Default

默认部署只启用 `mock` / `replay` 路径，不需要 Band live credentials。这样评委可以稳定看到 Case Brief、Submission Readiness、Evidence Coverage、Approval Queue、Agent handoff timeline、Final Pack 和 Governed Evolution，同时不会暴露真实 Agent UUID、API key、room id 或 message id。

## Render Web Service

建议配置：

- Runtime: Python 3.11+
- Build command: `pip install uv && uv sync --frozen`
- Start command: `uv run uvicorn trustroom.web.app:app --host 0.0.0.0 --port $PORT`
- Health path: `/health`

部署前必须运行：

```bash
uv run python scripts/check_no_secrets.py
uv run python scripts/check_trustroom_readiness.py
uv run pytest -v
git diff --check
```

## Optional Live Band Configuration

只有在需要 live Band demo 且凭证已安全放进平台 secret store 时，才配置：

```bash
BAND_API_BASE=<platform REST base URL>
BAND_AGENT_ID=<runtime agent id>
BAND_AGENT_KEY=<runtime agent key>
TRUSTROOM_BAND_PEERS_JSON=<runtime peer mapping or public handles>
```

`BAND_REST_URL` 可替代 `BAND_API_BASE`。Peer Agent UUID mapping 或公开 handle 必须作为运行时安全配置传给 live smoke scripts，不能写入测试、replay、报告或源代码。

Autonomous reply verification:

```bash
uv run python scripts/run_live_band_autonomous_smoke.py --dry-run-check
uv run python scripts/run_live_band_autonomous_smoke.py --target-agent requirement-decomposer-agent
```

只有当 smoke 输出 `status: DONE` 且 `autonomous_replies.status: PASSED` 时，部署说明或提交材料才能说 SDK/WebSocket Remote Agent autonomous replies 已验证。

## Known Blockers Before Final Submission

- Public GitHub strategy 仍需用户决定：切当前仓库 public，或创建脱敏 public submission repo。
- Application URL 尚未创建。
- Redacted live Band REST evidence packet 已在本机 ignored reports 中生成过；提交前仍需决定是否重新生成一份最新 evidence packet 并只引用脱敏摘要。
- SDK/WebSocket Remote Agent 自动接收并回复尚未验证；当前 smoke harness 已就绪，但需要 runtime REST base 和 connected peer directory。若赛时 live path 不稳定，演示必须明确使用 replay fallback。
