# Deployment Notes

这些说明用于把 RFP TrustRoom 作为公开安全的 hackathon demo 部署。当前公开提交路径使用 GitHub public repo + Render Web Service；默认只部署 mock/replay dashboard，不配置 Band live credentials。

## T22 Prep Status

- [x] 仓库根目录已添加 `render.yaml`，作为 public-safe Render Blueprint。
- [x] Blueprint 默认只启动 FastAPI mock/replay dashboard，不配置 Band live credentials。
- [x] Public GitHub Repository 已公开：https://github.com/adjcjh777/band-of-agents-hackathon。
- [x] `main` 默认分支已快进到最新 TrustRoom submission state，包含当前 RFP TrustRoom demo、submission assets 和 `render.yaml`。
- [x] Render Web Service 已创建：`rfp-trustroom`。
- [x] Application URL 已产生并 smoke 通过：https://rfp-trustroom.onrender.com。

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

1. 用户已明确选择 current repo public；公开仓库为 `adjcjh777/band-of-agents-hackathon`。
2. 在公开仓库中保留 `README.md`、`LICENSE`、`pyproject.toml`、`uv.lock`、`src/`、`samples/`、`reports/trustroom_replay.example.jsonl`、`docs/` 中 public-safe 文件和 `render.yaml`。
3. 不复制 `.env`、`agent_config.yaml`、真实 live evidence packet、私密报告、浏览器截图中可能包含账号信息的原图、`pilotdeck/` 或本地账号上下文。
4. 在 Render 创建 Web Service，连接 public-safe Git repo 的 `main` 分支。
5. 暂不配置 Band live env vars；先让 mock/replay route 成为稳定提交 URL。
6. 部署后验证 public URL：

```bash
curl -fsS https://rfp-trustroom.onrender.com/health
curl -fsS https://rfp-trustroom.onrender.com/runs/demo >/tmp/trustroom-demo.html
curl -fsS https://rfp-trustroom.onrender.com/runs/demo/replay >/tmp/trustroom-replay.html
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

- Public GitHub Repository 已完成，public URL 为 https://github.com/adjcjh777/band-of-agents-hackathon。
- Demo Application Platform / Application URL 已完成，Render URL 为 https://rfp-trustroom.onrender.com；最终提交前仍需再做一次 public URL smoke。
- Redacted live Band REST evidence packet 已在本机 ignored reports 中生成过；提交前仍需决定是否重新生成一份最新 evidence packet 并只引用脱敏摘要。
- SDK/WebSocket Remote Agent 自动接收并回复尚未验证；当前 smoke harness 已就绪，但需要 runtime REST base 和 connected peer directory。若赛时 live path 不稳定，演示必须明确使用 replay fallback。
- Public video URL 尚未创建；需要从 public Application URL 录制并上传公开视频。
