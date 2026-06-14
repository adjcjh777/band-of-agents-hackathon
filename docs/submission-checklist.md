# 提交清单

## 账户与社区

- [x] lablab.ai team/profile 页面已创建：https://lablab.ai/ai-hackathons/band-of-agents-hackathon/rfp-trustroom。
- [ ] 已加入 lablab.ai Discord。
- [x] Band 账号已创建。
- [ ] 已加入 Band Discord。
- [x] 已用 Chrome 复核官方页面当前 kickoff / schedule / submit / prize / partner 信息。
- [ ] AI/ML API coupon 已领取并记录 billing/subscription 取消提醒。官方页当前写明每人 $10 credits，最多 500 名参与者，有效期至比赛结束。
- [ ] Featherless AI coupon 已领取并记录到期/取消提醒。官方页当前写明 promo code `BOA26`，每人 $25 credits，最多 1,000 名参与者，激活后 1 个月有效。
- [ ] Band Pro promo code `BANDHACK26` 已按需兑换，并确认 100% off 与取消提醒。

## 技术准备

- [x] Python 3.11+。
- [x] uv。
- [ ] Band SDK 可安装。
- [x] 至少 3 个 Band Remote Agents 已创建。Chrome 复核 Band Agents 页面可见 TrustRoom remote agents。
- [x] Orchestrator Agent 的 UUID 和 API key 已安全保存在本机 ignored `.env`，未进入 Git。
- [x] `.env` 已加入 `.gitignore`。
- [x] `agent_config.yaml` 已加入 `.gitignore`。
- [ ] 能在 Band room 中 @mention 一个 Agent 并收到自主回复。当前已有 fail-closed smoke harness，但本机 dry-run 仍因缺少 REST base / peer directory 返回 `BLOCKED`。
- [ ] 能完成 3 个 Agent 的端到端自主协作。当前已验证真实 Band room、3 participants、2 条 @mention handoff 和 live event；peer agents 仍显示 Disconnected，尚未用新 harness 验证 SDK/WebSocket 自动回复。
- [x] 有 mock mode，防止现场 Band/API 波动。
- [x] 有 replay fallback，且 dashboard 明确标注 `REPLAY`。
- [x] 已准备 public-safe Render Blueprint：`render.yaml` 默认只部署 mock/replay FastAPI dashboard，不写入 Band live credentials。

## Demo 验收

- [x] Demo 第一屏能看懂业务问题。
- [x] Demo 中明确出现至少 3 个 Agent 角色。
- [x] Demo 展示 Band room 或 Band 协作日志。
- [x] 有任务交接：A Agent 的输出成为 B Agent 的输入。
- [x] 有 reviewer / risk / QA 的反驳、补证据或 veto。
- [x] 有最终业务产物：answer pack、security questionnaire 回答表、evidence index。
- [x] 有 human approval 或 escalation。
- [x] 有审计时间线。
- [x] 有 T20 Run Trace / Agent Handoff Chain，不用读完整 19 条 raw event 也能看懂 Band-style 协作链。
- [x] 有 Representative Item Traces：Q-002 approved path、Q-004 review loop、Q-006 fail-closed blocker。
- [x] 有 Q-006 Blocked Impact Path：stale/conflicting evidence -> no valid approval -> final pack excluded -> policy owner next action。
- [x] 有 live path 和 replay fallback 的明确标注。
- [x] 有 no-overclaim 页面：说明这是 hackathon demo，不是生产部署。
- [x] 评委不需要理解内部 UUID / trace id 也能看懂主线。

## 提交材料

- [x] Project Title，不超过 50 字符更稳。见 `docs/submission-assets/submission-copy.md`。
- [x] Short Description，不超过 255 字符。见 `docs/submission-assets/submission-copy.md`。
- [x] Long Description，至少 100 words。见 `docs/submission-assets/submission-copy.md`。
- [x] Technology & Category Tags。见 `docs/submission-assets/submission-copy.md`。
- [x] Cover Image，建议 16:9。`docs/submission-assets/rfp-trustroom-cover.png` 为 1920x1080。
- [ ] Video Presentation，官方指南建议 5 分钟以内。脚本和 shot list 已完成：`docs/submission-assets/video-script-shot-list.md`；公开视频 URL 尚未上传。
- [x] Slide Presentation。`docs/submission-assets/rfp-trustroom-submission-deck.pdf` 和 `.pptx` 已生成。
- [x] Public GitHub Repository。https://github.com/adjcjh777/band-of-agents-hackathon，默认分支 `main` 已更新到当前提交。
- [x] Demo Application Platform。Render Web Service：`rfp-trustroom`。
- [x] Application URL。https://rfp-trustroom.onrender.com，`/health`、`/runs/demo`、`/runs/demo/replay` public smoke 通过。
- [x] README 包含 setup、architecture、demo script、known limitations。
- [x] License 使用 MIT 或兼容 MIT。
- [x] `docs/judge-10-minute-experience.md` 或等价材料。
- [x] `docs/demo-runbook.md` 或等价材料。
- [x] `reports/trustroom_replay.example.jsonl` 或录屏中可见的 Band live evidence。

## 2026-06-14 当前阻塞项

- Live Band autonomous replies：真实 Band REST smoke 已完成并生成 redacted evidence；autonomous reply smoke harness 已完成，但当前 dry-run 缺少 `BAND_REST_URL` / `BAND_API_BASE` 和 `TRUSTROOM_BAND_PEERS_JSON`，提交前仍需用 connected peer 跑通 SDK/WebSocket 远程 Agent 自动处理与回复。
- Video Presentation：脚本已完成，但公开视频尚未录制、上传或生成 URL。
- Partner prize strategy：AI/ML API / Featherless AI 可以作为加分项，但不要牺牲 Band 协作主线；只有真实接入并能演示时才写入主 claims。
- Final official page gate：提交前再次用 Chrome 打开官方页确认 deadline、奖项、提交字段、partner terms 和已提交作品竞争态。

## 2026-06-14 Public URL Smoke

- LabLab team/profile URL：https://lablab.ai/ai-hackathons/band-of-agents-hackathon/rfp-trustroom。
- Public GitHub Repository：`gh repo view` 确认为 `PUBLIC`，默认分支 `main` 指向最新已推送 TrustRoom submission state。
- Public GitHub URL：https://github.com/adjcjh777/band-of-agents-hackathon。
- Render service：`rfp-trustroom`，Free instance，branch `main`，未配置 Band live credentials。
- Application URL：https://rfp-trustroom.onrender.com。
- `curl -fsS https://rfp-trustroom.onrender.com/health`：200 / `{"status":"ok"}`。
- `curl -fsS https://rfp-trustroom.onrender.com/runs/demo`：200，包含 `MOCK`、Run Trace、Agent Handoff Chain、Final Pack、replay/live boundary。
- `curl -fsS https://rfp-trustroom.onrender.com/runs/demo/replay`：200，包含 `REPLAY`、Executive Decision、Run Trace、Representative Item Traces、Q-006 Blocked Impact Path、Final Pack、no-overclaim footer。
- Chrome public URL smoke：desktop 1440x900 和 mobile 390x844 均无 console warning/error、无 page error、无横向溢出。截图：`/tmp/trustroom-public-render-desktop.png`、`/tmp/trustroom-public-render-mobile.png`。

## 2026-06-13 Final Rehearsal Record

- `uv run pytest -v`：100 passed，1 个 FastAPI / Starlette deprecation warning，不影响 demo。
- `uv run python scripts/check_trustroom_readiness.py`：OK，question_count 8，evidence_coverage_ratio 1.0，replay_event_count 19。
- `uv run python scripts/check_no_secrets.py`：OK。
- `uv run uvicorn trustroom.web.app:app --host 127.0.0.1 --port 8000`：本地服务启动成功。
- Browser smoke：`/runs/demo/replay` 包含 `REPLAY`、Executive Decision、Run Trace、Business Milestones、Agent Handoff Chain、Representative Item Traces、Blocked Impact Path、Reviewer Decision Matrix、Approval Workbench、Final Pack、Event Log Detail、Governed Evolution，并显示 `fallback, not live Band`；浏览器 error logs 为空，无横向溢出。
- Browser smoke：`/runs/demo` mock route 可打开，包含 `MOCK`、Submission Readiness、Final Pack、Band Collaboration Timeline；浏览器 error logs 为空。
- Local benchmark：`uv run python scripts/benchmark_trustroom.py --iterations 10` 通过。p95：`sample_load_ms=0.194`、`mock_run_ms=0.721`、`replay_load_ms=0.065`、`dashboard_health_ms=3.126`、`dashboard_mock_ms=4.271`、`dashboard_replay_ms=1.643`。
- Live Band smoke：`BAND_API_BASE=https://app.band.ai TRUSTROOM_BAND_PEERS_JSON=<public handles> uv run python scripts/run_live_band_smoke.py` 通过，生成 ignored redacted evidence `reports/live_band_smoke.20260613T062919Z.json`。
- Live Band latency：`create_room=555.691ms`、`mention_requirement-decomposer-agent=1605.576ms`、`mention_evidence-retriever-agent=1020.1ms`、`record_review_event=518.993ms`。
- Chrome live verification：Band Chats 页面可见 live `New Session`，参与者为 `trustroom-orchestrator`、`requirement-decomposer-agent`、`evidence-retriever-agent`，消息区显示两条真实 @mention handoff；Participants panel 显示 remote agents 当前 `Disconnected`。
- Live Band boundary：已验证真实 Band REST room / participant / message / event path；尚未验证 SDK/WebSocket 远程 Agent 自动接收并回复。提交时必须继续把 replay fallback、REST smoke 和 autonomous live agent 区分表述。
- Live autonomous reply harness：`scripts/run_live_band_autonomous_smoke.py` 已集成，stubbed tests 通过；当前 ignored `.env` dry-run 返回 `BLOCKED`，缺少 REST base / peer directory，未形成真实 autonomous reply evidence。

## 建议提交文案草稿

Project Title:

RFP TrustRoom

Short Description:

A multi-agent RFP and security questionnaire response room where specialized AI agents coordinate through Band to draft answers, verify evidence, review risk, and produce a traceable submission pack.

Long Description 草稿：

RFP TrustRoom turns a messy B2B RFP and security questionnaire response into a coordinated multi-agent workflow. A human uploads customer requirements, questionnaire rows, and company knowledge snippets, then specialized agents for requirement decomposition, evidence retrieval, answer drafting, and compliance review collaborate through a Band room. They share structured context, hand off tasks, challenge unsupported claims, escalate high-risk answers to a human SME, and produce a submission pack with a traceable event timeline. Band is the core collaboration layer: agents are routed with @mentions, exchange state, recruit reviewers when needed, and post events that make the workflow transparent. The result is a practical enterprise workflow for teams that need faster proposal responses without losing evidence quality, traceability, or human control.

Technology tags:

Band, Band SDK, multi-agent systems, enterprise workflow, RFP response, security questionnaire, evidence management, AI agents, traceability, human-in-the-loop, Python, FastAPI

## 视频结构

0:00-0:25 痛点：RFP 和安全问卷卡在售前、产品、安全、法务、SME 跨角色沟通。

0:25-0:55 解决方案：RFP TrustRoom 的 Agent 角色和 Band 协作层。

0:55-3:30 Demo：打开 `/runs/demo/replay`，按 Executive Decision -> Run Trace -> Agent Handoff Chain -> Representative Item Traces -> Blocked Impact Path -> Reviewer Matrix -> Final Pack 展示 Band-style 协作、交接、审查和升级。

3:30-4:20 技术结构：Band room、Agent API、SDK、events、dashboard。

4:20-5:00 商业价值与下一步：更快售前响应、证据可追溯、风险可控、可扩展到 vendor due diligence / procurement。

## 飞书经验带来的额外提交 gate

- [ ] 录屏前跑一遍 readiness check。
- [ ] 录屏前确认所有 secret、真实用户 ID、真实 room id 已脱敏或不展示。
- [ ] 如果 live demo 卡住，视频里切 replay fallback，并口头说明 replay / live 的区别。
- [ ] 最终长描述里避免 production、enterprise-ready deployment、fully automated compliance 这类过度承诺词。
- [ ] 提交前再次用 Chrome 打开官方页面确认 deadline、提交字段、奖项和 partner access 没有变化。
