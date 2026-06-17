# RFP TrustRoom 今日待办总清单

日期：2026-06-17

## 当前基线

- Public GitHub Repository 已完成：https://github.com/adjcjh777/band-of-agents-hackathon。
- Render Application URL 已完成：https://rfp-trustroom.onrender.com。
- LabLab team/profile 已完成：https://lablab.ai/ai-hackathons/band-of-agents-hackathon/rfp-trustroom。
- Cover image、8 页 slide deck PDF/PPTX、submission copy、video script/shot list 已完成。
- Public submission readiness 当前只因 `Video Presentation` URL 缺失保持 `BLOCKED`，不是代码或部署硬阻塞。
- Live Band REST room / participants / @mention / event boundary 已验证；connected-peer autonomous challenge-token replies 仍未通过，不能宣称完整 live autonomous workflow。
- Agent Bus 已恢复可验证闭环：`codex_app` handler 不可用时必须用 `CODEX_AGENT_BUS_TRANSPORT=exec` + `agent-bus send --trigger resume --wait`，并以 target reply 作为派发成功标准。

## 过往开发历程摘要

1. 领域模型与安全边界
   - 建立 RFP / security questionnaire / evidence / approval / final pack 的 typed model。
   - 加入 fail-closed readiness、secret scan、out-of-scope approval gate。

2. Mock / replay 主路径
   - 构建 deterministic mock runner，覆盖 requirement decomposition、evidence retrieval、answer drafting、compliance review、human approval 和 final-pack decision。
   - 固化 `reports/trustroom_replay.example.jsonl`，让评委可在 public-safe replay 中看完整协作链。

3. Band 协作证据
   - 建立 Band REST adapter 与 live smoke harness。
   - 已证明真实 Band REST room、participants、@mention handoff 和 event 写入边界。
   - autonomous reply harness 已 fail-closed，但因 runtime REST base / peer directory / connected peer readiness 缺失仍是 optional pending gate。

4. 企业 reviewer cockpit
   - 从最初 event log 升级到 Executive Decision、Run Trace proof strip、Business Milestones、Agent Handoff Chain、Representative Item Traces、Q-006 Blocked Impact Path、Approval Workbench、Final Pack。
   - Q-002 / Q-004 / Q-006 形成三条可讲故事的代表路径：approved、review-loop + legal approval、fail-closed blocked。

5. 提交包装
   - 完成 public repo、Render public-safe deployment、LabLab team page。
   - 完成 cover、deck、script、submission copy、asset validators 和 public submission readiness checker。
   - 目前真正提交层 blocker 只剩 public/unlisted video URL 与 final official-page/form gate。

6. Agent Bus / 多 agent 协作
   - 注册 planner、executor、tester、UI/UX、scout。
   - 发现 `trigger=codex_app` 在当前 controller 会话只生成 `prepared` payload，不能自动可见投递。
   - 修复 Agent Bus prompt，加入 CLI fallback reply；验证 tester、executor、UI/UX、scout 均能通过 `exec` transport 收到 ping 并返回 ACK。

## 今日总目标

用最小代码风险继续打磨企业级 RFP TrustRoom：让 public demo、视频录制、提交清单、最终官方页核验和 no-overclaim 边界达到可提交状态。原则是“不做更差”：只做能提升评委理解、提交可靠性或验证严谨性的改动；不新增大 UI 面、不追未验证 partner tech、不把 replay 伪装成 live。

## 今日任务矩阵

### P0-A Final Video URL Gate

Owner：controller / user-owned gate，UI/UX 辅助 rehearsal。

目标：
- 从 public Application URL 录制 5 分钟以内 video presentation。
- 视频必须展示 public-safe replay route，而不是 localhost。
- 视频必须口头和视觉保留 replay/live/autonomous boundary。

输入：
- `https://rfp-trustroom.onrender.com/runs/demo/replay`
- `docs/submission-assets/video-script-shot-list.md`
- `docs/submission-assets/rfp-trustroom-cover.png`
- `docs/submission-assets/rfp-trustroom-submission-deck.pdf`

步骤：
1. 录制前 warm Render：访问 `/health`、`/runs/demo`、`/runs/demo/replay`。
2. Chrome desktop 视口录制，不显示 bookmarks、账号页、raw Band ids、private tabs。
3. 路线固定：cover -> Executive Decision -> Run Trace -> Agent Handoff Chain -> Representative Item Traces -> Q-006 Blocked Impact Path -> Final Pack -> Replay / Live Evidence boundary。
4. 上传为 public 或 unlisted URL。
5. 用无登录窗口或 fresh browser 打开视频 URL，确认可播放。
6. 把 video URL 写入 submission checklist / readiness source 后运行 final readiness checker。

PASS：
- 有可打开的 public/unlisted video URL。
- 视频小于或接近 5 分钟。
- 不暴露 secret、raw room id、account data。
- 不宣称 production、formal audit、compliance certification、complete autonomous live workflow。

BLOCKED：
- 视频平台需要人工登录/验证码。
- Render public URL 不稳定且 90s warm 后仍不可访问。
- 录屏暴露敏感信息，需要重录。

### P0-B Final Public Readiness Gate

Owner：executor 只在明确写锁下修改 checker/docs；tester 做只读审计。

目标：
- 视频 URL 填入后，public submission readiness 从 `BLOCKED only video pending` 变成 `READY` 或明确列出真实 blocker。

必跑命令：
- `uv run python scripts/check_public_submission_ready.py --network`
- `uv run python scripts/check_submission_assets.py`
- `uv run python scripts/check_no_secrets.py`
- `uv run python scripts/check_trustroom_readiness.py`
- `uv run pytest -v`
- `git diff --check`

PASS：
- public GitHub、LabLab team、Render Application URL、video URL 均可访问。
- readiness checker 无 blocking issues。
- submission checklist 不把 pending 项误勾完成。

BLOCKED：
- 任一 public URL 访问失败。
- video URL 需要登录。
- no-overclaim checker 发现正向过度承诺。

### P0-C Final Official Page And Form Mapping

Owner：scout read-only research；controller/user-owned form submission。

目标：
- 提交前当天用 Chrome 重新读取官方页面和 LabLab submission form。
- 把每个字段映射到最终 copy / URL / asset。

字段：
- Project Title：`RFP TrustRoom`
- Short Description：使用 `docs/submission-assets/submission-copy.md`
- Long Description：使用 `docs/submission-assets/submission-copy.md`
- Tags：保持 Band / multi-agent / enterprise workflow / RFP / security questionnaire / FastAPI 等，不加入未实现 partner tech。
- Cover Image：`docs/submission-assets/rfp-trustroom-cover.png`
- Video Presentation：待填 public/unlisted URL。
- Slide Presentation：优先 PDF，PPTX 作为 editable backup。
- Public GitHub Repository：https://github.com/adjcjh777/band-of-agents-hackathon
- Demo Application Platform：Render
- Application URL：https://rfp-trustroom.onrender.com

PASS：
- 官方页面提交字段未变化，或变化已记录并映射。
- form entry 由 controller/user 最终操作。

BLOCKED：
- 官方页面新增必填字段未准备。
- LabLab form 上传资产失败。

### P1-D UI/UX Enterprise Polish Audit

Owner：bandofagents-uiux，read-only first；只在 controller 开写锁后改 UI。

目标：
- 不做大 redesign，只检查 public route 是否更适合录屏和企业评委。

检查点：
1. 第一屏是否立即讲清 Human request -> Band handoff -> final pack decision。
2. Route nav 是否帮助录屏，不抢主叙事。
3. Q-006 blocked path 是否是最强 buyer-value moment。
4. Mobile 390px 无横向溢出。
5. 不出现 landing-page noise、过度装饰、AI sci-fi generic 图。

可用工具/技能：
- `$frontend-design`
- `@product-design`
- `@creative-production`
- Chrome desktop/mobile screenshots

PASS：
- 无 P0/P1 UI 问题。
- 如有建议，必须是小范围 copy/layout polish，并说明是否值得在提交前动手。

BLOCKED：
- 发现第一屏/视频路线严重遮挡、溢出或误导 live/replay 边界。

### P1-E Final Regression And Claims Audit

Owner：bandofagents-tester，read-only。

目标：
- 在视频 URL 写入前后各做一次 focused audit，确保 code/docs/assets 没回归。

检查：
- `uv run pytest tests/test_web_app.py tests/test_submission_assets.py tests/test_public_submission_ready.py -v`
- `uv run python scripts/check_public_submission_ready.py --skip-network`
- `uv run python scripts/check_submission_assets.py`
- `uv run python scripts/check_no_secrets.py`
- `uv run python scripts/check_trustroom_readiness.py`
- `uv run python scripts/check_dual_agent_protocol.py`
- Chrome public URL desktop/mobile smoke

PASS：
- 只剩 video URL 或 final form 这类真实外部 gate。
- no-overclaim / replay-live / autonomous-pending wording 保持严格。

BLOCKED：
- tests fail。
- public route 500 / overflow / console error。
- 文案把 replay 写成 live，或把 autonomous pending 写成 passed。

### P1-F Submission Copy And Competitor Differentiation Refresh

Owner：github-product-research-agent / scout，read-only unless controller opens docs-only lock。

目标：
- 当天复核官方 page 和 visible competitor cards。
- 保持 TrustRoom 差异化：B2B RFP + security questionnaire + evidence-backed answer pack + approval scope/expiry + Q-006 final-pack exclusion。

PASS：
- 报告官方 facts、deadline、fields、judging criteria。
- 明确是否需要调整 video wording。

BLOCKED：
- 官方页面无法读取或需要新字段。

### P2-G Optional Live Autonomous Chain

Owner：executor only after controller/user provides runtime config；tester audits evidence。

目标：
- 仅在视频和 final readiness 已稳定后 timebox。
- 目标固定为 requirement-decomposer-agent、evidence-retriever-agent、answer-drafter-agent。

前置：
- runtime-only `BAND_REST_URL` 或 `BAND_API_BASE`。
- runtime-only `TRUSTROOM_BAND_PEERS_JSON`。
- 不写入 Git，不读取/提交 `.env`、`agent_config.yaml`、raw live reports。

PASS：
- 三个固定 agent 均有 non-@mention challenge-token reply。
- 生成 ignored redacted evidence path。

BLOCKED：
- dry-run 不 ready。
- 任一 target 5s x 3 same-target fail-fast retry 超时。

### P2-H Agent Bus Hardening Follow-Up

Owner：controller / local tool maintenance。

目标：
- 记录并继续使用已验证的 Agent Bus 操作方式。

已完成：
- `build_request_prompt` / team prompts 加入 CLI fallback reply。
- Agent Bus tests：14 passed。
- tester / executor / UIUX / scout exec transport ping 均 ACK。

后续可做：
- 给 `trigger=codex_app` 增加更醒目的 warning：`prepared != delivered`。
- 持久化 transport surface，便于事后区分 `app_server_stdio_turn_start` 与 `exec_resume_noninteractive`。
- 给 Agent Bus docs 增加 `agent-bus reply` CLI 示例。

## 今日派发计划

1. `SCOUT-R6 Official page and final claims refresh`
   - Owner：github-product-research-agent
   - Scope：read-only
   - 输出：官方 fields / deadline / judging criteria / competitor signals / video wording risk。

2. `UIUX-R6 Public video rehearsal audit`
   - Owner：bandofagents-uiux
   - Scope：read-only first
   - 输出：public URL desktop/mobile visual audit、录屏路线建议、是否需要小 UI fix。

3. `TEST-R6 Final readiness regression audit`
   - Owner：bandofagents-tester
   - Scope：read-only
   - 输出：tests/checks/public smoke/no-overclaim verdict。

4. `EXEC-R6 Submission readiness support`
   - Owner：bandofagents-executor
   - Scope：standby first；只有 controller 开 locked paths 才写。
   - 输出：等待 video URL；若 URL 可用，更新 checklist/readiness docs 并跑 checks。

## 不做事项

- 不新增产品大模块。
- 不重写 dashboard 信息架构。
- 不追 AI/ML API 或 Featherless partner claim，除非真实集成并可演示。
- 不把 autonomous live replies 作为主提交 blocker。
- 不提交 raw live evidence、secret、true room/message ids。
- 不触碰 `pilotdeck/`。
