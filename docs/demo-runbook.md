# RFP TrustRoom Demo Runbook

本 runbook 面向录屏、现场演示和本地复现。默认走 replay fallback；只有在真实 Band credentials、Remote Agents 和官方 access 已确认后，才切到 live path。

## Preflight

```bash
uv sync
uv run python scripts/check_trustroom_readiness.py
uv run python scripts/check_no_secrets.py
uv run pytest -v
```

通过标准：

- Readiness 输出 question_count、Evidence Coverage、high_risk_count 和 replay_event_count。
- No-secret gate 不发现 `.env`、agent key、API key、真实 room id 或私密日志。
- pytest 全绿；已知 FastAPI / Starlette httpx deprecation warning 不影响 demo。

## Replay Fallback Path

启动 dashboard：

```bash
uv run uvicorn trustroom.web.app:app --host 127.0.0.1 --port 8000
```

打开：

```text
http://127.0.0.1:8000/runs/demo/replay
```

讲解顺序：

1. Case Brief: 解释 Acme RFP / security questionnaire 场景。
2. Submission Readiness: 说明当前 run 是否可提交。
3. Evidence Coverage: 指出哪些回答有证据，哪些是显式 gap。
4. Approval Queue: 展示 human approval 处理高风险承诺。
5. Risk Flags: 展示 stale / missing / unsupported evidence。
6. Band Timeline: 解释 @mention、handoff、review loop。
7. Final Pack: 展示 answer pack、blocked items、evidence index。
8. Governed Evolution: 展示从 reviewer friction 到改进建议和 stress test 的闭环。

必须口头说明：当前页面是 REPLAY fallback，不是 live Band room。

## Live Path

仅在以下条件全部满足时运行：

- Band credentials 已由用户提供并保存在本机安全 secret 文件中。
- Kickoff access code 和官方 live integration 规则已确认。
- 至少 3 个 Remote Agents 已创建。
- 所有 live room id、agent key、API key 已脱敏，不进入 Git。

Live 讲解顺序与 replay 相同，但需要额外展示 Band room 中的 @mention handoff、agent replies、reviewer request_changes 和 human approval。若 live path 卡住，立即切回 replay fallback 并说明原因。

## Five-Minute Video Structure

0:00-0:25 Pain: RFP / security questionnaire 需要 sales、security、product、legal、SME 反复协调，容易证据过期和过度承诺。

0:25-0:55 Solution: RFP TrustRoom 用 Band 做协作层，让 orchestrator、decomposer、retriever、drafter、reviewer 和 human approver 共享同一条审计链。

0:55-2:45 Demo: 打开 dashboard 第一屏，依次展示 Submission Readiness、Evidence Coverage、Approval Queue、Risk Flags 和 Final Pack。

2:45-3:45 Agent Workflow: 讲 Band @mention handoff、证据检索、答案起草、review 打回和 human approval。

3:45-4:25 Governed Evolution: 展示 reviewer friction 如何变成受控改进建议和 stress test。

4:25-5:00 Boundary And Value: 说明这是 hackathon demo / working prototype；价值是更快响应、证据可追溯、风险受控、replay fallback 可验收。

## Failure Handling

- Dashboard 不启动：先跑 `uv sync`，再确认端口 8000 未被占用，可换 `--port 8001`。
- Readiness fail：打开输出中的 issue code，只修 sample/replay/gate，不能删掉风险项来假装通过。
- No-secret fail：停止演示，清理 secret 或私密日志，不提交。
- Live Band fail：切 replay fallback，明确说明 live path 暂不可用。
- Human approval 缺失：不要把高风险项放进 Final Pack，保留 Approval Queue 或 blocked 状态。

## No-Overclaim Boundary

禁止在录屏或提交文案中使用这些承诺：production、enterprise-ready deployment、fully automated compliance、legal advice、certified。

允许说：RFP TrustRoom 是 hackathon demo / working prototype；replay fallback 复现同一条主链路；live Band path 将在 credentials 和官方规则确认后接入。
