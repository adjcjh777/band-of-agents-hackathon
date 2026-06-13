# RFP TrustRoom Demo Runbook

本 runbook 面向录屏、现场演示和本地复现。默认走 replay fallback；只有在真实 Band credentials、Remote Agents、Band room evidence 和 SDK/WebSocket autonomous replies 都稳定时，才把 live path 放进主录屏。当前已经验证 REST room / participants / @mention / event smoke，但不能把它说成完整 autonomous live agent workflow。

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
2. Executive Decision: 先讲 7/8 可进入 draft pack，Q-006 必须 excluded，不能自动发给客户。
3. Run Trace: 用 proof strip 解释 roles、handoffs、one core Q-004 review loop、valid approvals、Final Pack 和 `REPLAY` mode。
4. Business Milestones: 按 intake -> triage -> evidence -> draft -> review loop -> human approval -> final pack 讲状态转移。
5. Agent Handoff Chain: 展示 orchestrator -> decomposer -> retriever -> drafter -> reviewer -> human approver -> final pack 的 sender / receiver / event refs。
6. Representative Item Traces: 用 Q-002、Q-004、Q-006 三条链说明 approved bounded wording、review loop rewrite 和 fail-closed blocker。
7. Blocked Impact Path: 指出 Q-006 是 stale/conflicting incident evidence -> needs human approval -> no valid approval -> final pack excluded -> policy owner follow-up。
8. Reviewer Decision Matrix / Approval Workbench: 展示每条 answer 的 draft、risk、owner、evidence title/snippet/freshness、review decision、approval scope/validity 和 final-pack status。Approved evidence refs 是 reviewer-visible context，不是 machine-enforced evidence-set gate。
9. Event Log Detail / Governed Evolution: 原始 Band Collaboration Timeline 保留为 audit detail；Governed Evolution 展示 reviewer friction 到受控改进建议和 stress test 的闭环。

必须口头说明：当前页面是 REPLAY fallback，不是 live Band room。

## Live Path

仅在以下条件全部满足时运行：

- Band credentials 已由用户提供并保存在本机安全 secret 文件中。
- 至少 3 个 Remote Agents 已创建。
- SDK/WebSocket 远程 Agent 能自动接收 @mention 并回复，或演示中明确说明当前只展示 REST smoke / Band room evidence。
- 所有 live room id、agent key、API key 已脱敏，不进入 Git。

Live 讲解顺序与 replay 相同，但需要额外展示 Band room 中的 @mention handoff、agent replies、reviewer request_changes 和 human approval。若 live path 卡住，立即切回 replay fallback，并口头说明 replay / REST smoke / autonomous live workflow 的区别。

当前 live evidence 边界：

- 已有：真实 Band REST room、3 participants、2 条 @mention handoff、live event、Chrome live verification、ignored redacted evidence packet。
- 已有：`scripts/run_live_band_autonomous_smoke.py` fail-closed harness，可把 REST smoke、Band room evidence 和 autonomous replies 分开报告。
- 当前 blocked：ignored env dry-run 缺少 `BAND_REST_URL` / `BAND_API_BASE` 和 `TRUSTROOM_BAND_PEERS_JSON`，尚未形成真实 autonomous reply evidence。
- 未完成：peer agents 自动接收并回复的 SDK/WebSocket 端到端链路。
- 提交材料可说：REST live boundary 已验证，replay fallback 可复现主流程。
- 提交材料不可说：完整 autonomous live Band workflow 已稳定运行。

自主回复 smoke 命令：

```bash
uv run python scripts/run_live_band_autonomous_smoke.py --dry-run-check
uv run python scripts/run_live_band_autonomous_smoke.py --target-agent requirement-decomposer-agent
```

只有第二条命令返回 `DONE` 且输出中 `autonomous_replies.status` 为 `PASSED` 时，才能在录屏中说 autonomous Remote Agent replies 已验证。

## Five-Minute Video Structure

0:00-0:25 Pain: RFP / security questionnaire 需要 sales、security、product、legal、SME 反复协调，容易证据过期和过度承诺。

0:25-0:55 Solution: RFP TrustRoom 用 Band 做协作层，让 orchestrator、decomposer、retriever、drafter、reviewer 和 human approver 共享同一条审计链。

0:55-1:20 Executive Decision: 打开 `/runs/demo/replay`，先讲 7/8 answers can enter the pack，Q-006 stays excluded，customer pack not auto-sent。

1:20-2:10 Run Trace: 展示 `Run Trace` proof strip、`Business Milestones` 和 `Agent Handoff Chain`，让评委看到 Band-style sender -> receiver handoff、shared object refs 和 state transitions，而不是只看最终文本。

2:10-3:10 Representative Item Traces: 讲 Q-002 scoped SME approval、Q-004 request_changes -> evidence clarification -> revised bounded draft -> legal approval、Q-006 fail-closed blocker。

3:10-3:55 Reviewer Matrix And Approval Workbench: 展示 evidence title/snippet/freshness、review decision、approval scope/validity、approved evidence refs context 和 final-pack reason。

3:55-4:25 Final Pack And Governed Evolution: 展示 included answers、blocked item、evidence index、audit event refs，以及 reviewer friction 如何变成受控改进建议和 stress test。

4:25-5:00 Boundary And Value: 说明这是 hackathon demo / working prototype；价值是更快响应、证据可追溯、风险受控、replay fallback 可验收；REST live boundary 和 autonomous live replies 是分开的证据门槛。

## Failure Handling

- Dashboard 不启动：先跑 `uv sync`，再确认端口 8000 未被占用，可换 `--port 8001`。
- Readiness fail：打开输出中的 issue code，只修 sample/replay/gate，不能删掉风险项来假装通过。
- No-secret fail：停止演示，清理 secret 或私密日志，不提交。
- Live Band fail：切 replay fallback，明确说明 live path 暂不可用。
- SDK/WebSocket replies fail：不要把 REST smoke 当成 autonomous live replies；视频可展示 Band room evidence，再切 dashboard replay fallback。
- Human approval 缺失：不要把高风险项放进 Final Pack，保留 Approval Queue 或 blocked 状态。

## No-Overclaim Boundary

禁止在录屏或提交文案中使用这些承诺：production、enterprise-ready deployment、fully automated compliance、legal advice、certified。

允许说：RFP TrustRoom 是 hackathon demo / working prototype；replay fallback 复现同一条主链路；Band REST live boundary 已验证；autonomous SDK/WebSocket replies 仍需作为 live gate 单独验证。

## Final Official Page Gate

提交前最后一次用 Chrome 打开官方页，确认：

- Deadline 仍是 2026-06-19 23:00 CST。
- 提交字段仍包括 Public GitHub Repository、Demo Application Platform、Application URL、Video Presentation、Slide Presentation 和 Cover Image。
- Partner terms / prize / promo code 没有新变化。
- 已提交作品列表没有改变 RFP TrustRoom 的差异化叙事。
