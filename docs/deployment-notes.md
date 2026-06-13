# Deployment Notes

这些说明用于把 RFP TrustRoom 作为公开安全的 hackathon demo 部署。当前推荐平台是 Render Web Service；在用户明确决定 public repo 策略和 demo URL 之前，不把本仓库切 public，也不声称已经完成线上部署。

## T22 Prep Status

- [x] 仓库根目录已添加 `render.yaml`，作为 public-safe Render Blueprint。
- [x] Blueprint 默认只启动 FastAPI mock/replay dashboard，不配置 Band live credentials。
- [ ] Public GitHub Repository 尚未创建或公开。
- [ ] Render Web Service 尚未由用户授权创建。
- [ ] Application URL 尚未产生。

## Public-Safe Default

默认部署只启用 `mock` / `replay` 路径，不需要 Band live credentials。这样评委可以稳定看到 Executive Decision、Run Trace、Business Milestones、Agent Handoff Chain、Representative Item Traces、Q-006 Blocked Impact Path、Reviewer Decision Matrix、Approval Workbench、Final Pack 和 Event Log Detail，同时不会暴露真实 Agent UUID、API key、room id 或 message id。

## Render Web Service

本仓库的 `render.yaml` 使用 Render Blueprint。Render 官方文档说明 Blueprint 默认使用仓库根目录的 `render.yaml`，Web Service 支持 `runtime: python`、`buildCommand`、`startCommand`、`healthCheckPath` 和 `autoDeployTrigger` 字段。

当前 Blueprint 配置：

- Service: `rfp-trustroom`
- Type: Render Web Service
- Runtime: `python`
- Plan: `free`
- Build command: `pip install uv && uv sync --frozen`
- Start command: `uv run uvicorn trustroom.web.app:app --host 0.0.0.0 --port $PORT`
- Health path: `/health`
- Auto deploy: `off`，提交前由 controller 手动触发或用户在 Render dashboard 触发，避免文档-only commit 自动发布。

部署步骤：

1. 用户明确选择 public repo 策略：当前 repo 公开，或创建脱敏 public submission repo。若无法完整审计历史，优先创建脱敏 public submission repo。
2. 在公开仓库中保留 `README.md`、`LICENSE`、`pyproject.toml`、`uv.lock`、`src/`、`samples/`、`reports/trustroom_replay.example.jsonl`、`docs/` 中 public-safe 文件和 `render.yaml`。
3. 不复制 `.env`、`agent_config.yaml`、真实 live evidence packet、私密报告、浏览器截图中可能包含账号信息的原图、`pilotdeck/` 或本地账号上下文。
4. 在 Render 创建 Blueprint / Web Service，连接 public-safe Git repo。
5. 暂不配置 Band live env vars；先让 mock/replay route 成为稳定提交 URL。
6. 部署后验证 public URL：

```bash
curl -fsS https://<service>.onrender.com/health
curl -fsS https://<service>.onrender.com/runs/demo >/tmp/trustroom-demo.html
curl -fsS https://<service>.onrender.com/runs/demo/replay >/tmp/trustroom-replay.html
```

7. 用 Chrome 桌面和移动视口打开 `/runs/demo/replay`，确认 `REPLAY fallback, not live Band`、Run Trace、Agent Handoff Chain、Representative Item Traces、Q-006 Blocked Impact Path 和 no-overclaim footer 可见，且没有 console/page errors 或横向溢出。

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
- Demo Application Platform / Application URL 尚未创建；`render.yaml` 只是部署准备，不等于已上线。
- Redacted live Band REST evidence packet 已在本机 ignored reports 中生成过；提交前仍需决定是否重新生成一份最新 evidence packet 并只引用脱敏摘要。
- SDK/WebSocket Remote Agent 自动接收并回复尚未验证；当前 smoke harness 已就绪，但需要 runtime REST base 和 connected peer directory。若赛时 live path 不稳定，演示必须明确使用 replay fallback。
