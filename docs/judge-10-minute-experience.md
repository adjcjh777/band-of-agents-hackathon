# RFP TrustRoom 10-Minute Judge Experience

本页给评委一条固定路线：10 分钟内看懂业务问题、Band 多 Agent 协作方式、证据审查、人审边界、最终提交包和 replay fallback。RFP TrustRoom 当前是 hackathon demo / working prototype。

## 0:00-1:00 Case Brief

看点：这不是通用 chatbot，而是 B2B RFP / security questionnaire 响应协作室。

- Sample buyer: Acme Financial Services.
- Request: 回答 SOC 2、数据保留、SLA、PDF 风险摘要、部署边界等 8 个问卷项。
- Business pressure: 48 小时内交付可信回答包。
- TrustRoom route: Executive Decision -> Run Trace -> Business Milestones -> Agent Handoff Chain -> Representative Item Traces -> Blocked Impact Path -> Final Pack -> Replay / Live boundary.

## 1:00-2:30 Dashboard First View

打开：

```bash
uv run uvicorn trustroom.web.app:app --host 127.0.0.1 --port 8000
```

访问：

```text
http://127.0.0.1:8000/runs/demo/replay
```

第一屏应立即看到：

- Executive Decision: 7/8 answers can enter the pack; Q-006 stays excluded.
- Submission Readiness / Evidence Coverage / Approval Queue: 当前 run 的业务状态、证据健康和人审门槛。
- Run Trace: 30 秒内看懂 roles、handoffs、one core Q-004 review loop、valid approvals、Final Pack 和 `REPLAY` mode。
- Business Milestones: intake、triage、evidence、draft、review loop、human approval、final pack 的状态。
- Agent Handoff Chain: orchestrator -> decomposer -> retriever -> drafter -> reviewer -> human approver -> final pack 的 sender / receiver / event refs。

页面上必须出现 `REPLAY` 标识。Replay 是 fallback，不是 live Band 运行。

## 2:30-4:30 Run Trace And Agent Handoff

优先看 `Run Trace` 和 `Agent Handoff Chain`，不要先滚完整 raw event log。评委应能看到至少 3 个专职 Agent 和一个 human approver：

- `trustroom-orchestrator`: 创建 run，分派任务，维护状态。
- `requirement-decomposer-agent`: 把 RFP / questionnaire 拆成可回答 item。
- `evidence-retriever-agent`: 找证据、标注 freshness 和 gap。
- `answer-drafter-agent`: 只基于证据起草回答。
- `compliance-review-agent`: 对 unsupported / stale / high-risk 进行 request_changes、blocked 或 needs_human_approval。
- `sme-approver`: human approval gate，不伪装成 autonomous agent。

评委要能看到 Band 协作语义：@mention、handoff、共享上下文、review loop、状态变化。当前 replay mirror 展示的是同一条协作链路的本地可复现证据。

## 4:30-6:30 Representative Item Traces

看 `Representative Item Traces`，用三条 item chain 解释系统价值：

- Q-002: high-risk SOC 2 answer 有 current evidence、bounded wording、valid scoped SME approval，最终 included。
- Q-004: compliance reviewer request_changes，evidence retriever 补充 region-restricted processing 证据，answer drafter 生成 revised bounded draft，legal reviewer approval 后 included。
- Q-006: incident response evidence stale/conflicting，review 需要 human approval，但没有 valid approval，因此 final pack excluded。

再看 `Blocked Impact Path`：

- stale/conflicting incident evidence -> review blocker -> no valid human approval -> final pack excluded -> policy owner next action。

这条路径是 demo 的关键：TrustRoom 不只是生成答案，而是把不能对客户承诺的内容挡在提交包外。

## 6:30-7:45 Reviewer Matrix And Approval Workbench

重点看两类问题：

- Supported answer: 有 current evidence、review 通过、可进入 Final Pack。
- Risky answer: stale / missing / unsupported evidence 触发 request_changes、blocked 或 human approval。

Reviewer Decision Matrix 展示每条 answer 的 draft、evidence title/snippet/freshness、review status、approval status、gate reasons 和 evidence lineage。Approval Workbench 展示 approval scope、validity / expiry label、approved evidence refs 和 required follow-up。Approved evidence refs 是 reviewer-visible context，不是当前版本的 machine-enforced evidence-set gate。

高风险项不能自动进入 Final Pack。只有 valid scoped approval 或明确 blocker 后，最终包才允许生成。

## 7:45-8:45 Final Pack

Final Pack 应展示：

- 已纳入 answer IDs。
- 被阻塞 item IDs。
- evidence index。
- audit event IDs。
- readiness summary。

这证明 TrustRoom 不是只生成文本，而是保留回答、证据、审批、审计的同源关系。

## 8:45-9:20 Governed Evolution

看 Governed Evolution 区域：

- Workflow improvement agent 从 reviewer friction 中提出改进建议。
- Challenge generator 生成 stress test，验证未来 prompt 不会绕过 human approval。
- 改进必须经过 review，不能自动修改高风险流程。

## 9:00-10:00 Live Path Versus Replay Fallback

当前可独立验收的是 mock/replay 主路径。Band live path 已验证 REST room / participants / @mention / event boundary，但 SDK/WebSocket Remote Agent 自动接收并回复仍需单独通过后，才能把它作为完整 live autonomous workflow 演示。

Live path 目标：

- 真实 Band room。
- 至少 3 个 Remote Agents。
- @mention handoff 和 reviewer loop。
- 脱敏 live evidence packet。
- SDK/WebSocket autonomous replies，不能只靠手动或 REST smoke 替代。

Replay fallback 目标：

- 没有外部 API 也能复现同一条 demo 主链路。
- 明确标注 replay。
- 不把 replay 说成 live。

## What The Judge Should Notice

- Band is the coordination layer: the visible path is sender -> receiver handoff, shared object refs, review loop and task state, not a single chatbot answer.
- Business value is concrete: a Proposal Lead sees what can be sent, what is blocked, who owns it and why.
- Risk control is real in the sample workflow: Q-006 is excluded because stale/conflicting evidence and missing approval are not papered over.
- Human-in-the-loop is explicit: Q-002 and Q-004 approvals are scoped and valid for this sample, while Q-006 has no valid approval.
- Presentation is honest: `/runs/demo/replay` is a replay fallback with redacted refs; REST live boundary and autonomous live replies are separate evidence gates.
- Originality is in the enterprise workflow: RFP intake, evidence health, reviewer challenge, approval validity, final pack and governed evolution live in one room.

## No-Overclaim Boundary

禁止把当前 demo 描述为：production、enterprise-ready deployment、fully automated compliance、legal advice、certified security product。

可以准确描述为：hackathon demo / working prototype，展示了 RFP TrustRoom 的 mock/replay 主链路、证据同源、review loop、human approval、Final Pack 和 Governed Evolution；Band REST live boundary 已验证，但完整 autonomous live replies 仍是 live gate。
