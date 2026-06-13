# RFP TrustRoom Demo Evidence Report

本报告记录当前仓库中可以独立验收的 demo 证据。它用于评委材料和最终自查，不包含真实客户数据、真实 Band room id、真实 agent key 或私密日志。

## Current Evidence Packet

| Area | Evidence | Status |
|---|---|---|
| Sample intake | `samples/acme-security-rfp/` includes case, RFP, questionnaire, knowledge snippets | Ready |
| Replay mirror | `reports/trustroom_replay.example.jsonl` has 19 events | Ready |
| Domain model | `src/trustroom/models.py` and `src/trustroom/state_machine.py` model run, items, evidence, review, approval, final pack, evolution | Ready |
| Mock agents | `src/trustroom/agents/mock_runner.py` produces intake, 3+ Agent handoff, evidence, draft, review, human approval, final pack | Ready |
| Dashboard | `/runs/demo/replay` shows Executive Decision, Next Actions, Reviewer Decision Matrix, evidence freshness/detail, Approval Workbench, Risk Register, Final Pack, Band timeline, Governed Evolution | Ready |
| Readiness gates | `scripts/check_trustroom_readiness.py` checks sample size, replay load, evidence coverage, high-risk gating, no-overclaim phrases | Ready |
| No-secret gate | `scripts/check_no_secrets.py` scans for secret-like values while excluding local secret files and `pilotdeck/` | Ready |
| Agent prompts | `src/trustroom/agents/prompts/` defines role, input contract, output schema, no-overclaim boundary and Band handoff instructions | Ready |
| Task envelopes | `docs/agent-task-envelopes.md` defines @mention handoff shape and request_changes / human approval status contract | Ready |
| Live REST smoke | `scripts/run_live_band_smoke.py` can create a real Band room, add participants, send @mention handoff messages, and record a live event with redacted refs | Partial |
| Live autonomous reply smoke | `scripts/run_live_band_autonomous_smoke.py` probes for a challenge-token Remote Agent reply and separates REST smoke, room evidence and autonomous replies | Blocked until runtime peer config is ready |

## Main Demo Chain

The replay evidence covers:

1. RFP intake from fictional Acme materials.
2. Requirement decomposition into 8 questionnaire items.
3. Evidence retrieval with current, stale, missing and conflicting cases.
4. Answer drafting tied to evidence IDs.
5. Compliance review that can approve, request_changes, needs_human_approval or block.
6. Human approval for high-risk items.
7. Final Pack generation with evidence index and blockers.
8. Governed Evolution proposal and challenge generation.

This route is enough to show the product priority: RFP intake, 3+ Agent handoff, evidence retrieval, answer drafting, review loop, human approval, Final Pack and Governed Evolution. The current dashboard also makes the enterprise reviewer decision explicit: 7/8 answers can enter the draft pack, Q-006 stays excluded, Q-002 and Q-004 show approval basis, and stale/missing/conflicting evidence is visible by answer instead of hidden in aggregate metrics.

## Validation Commands

```bash
uv run python scripts/check_trustroom_readiness.py
uv run python scripts/check_no_secrets.py
uv run pytest -v
git diff --check
```

Expected current result:

- Readiness passes with at least 8 questions.
- Evidence Coverage is at least 80% or gaps are explicit.
- High-risk items are approved, routed to human approval, request_changes or blocked.
- Replay loads in under 5 seconds.
- Full pytest passes.

## Replay Versus Live Evidence

Replay evidence:

- Deterministic.
- Public-safe.
- Does not need external API access.
- Clearly labeled `REPLAY`.
- Good for judging the core workflow if live Band access is unavailable.

Live evidence target:

- Real Band room with @mention handoff.
- At least 3 Remote Agents.
- Reviewer request_changes and human approval visible in Band.
- Redacted room references and agent references only.

Current status:

- Verified: real Band REST smoke has produced a redacted evidence packet outside Git, and Chrome live verification showed the Band chat, three participants, two @mention handoff messages and a live event.
- Added: autonomous reply smoke harness exists and returns `DONE` only when a non-mention Band message includes the challenge token. Current dry-run returned `BLOCKED` because the ignored local env is missing REST base / peer directory.
- Not verified: SDK/WebSocket Remote Agents autonomously receiving @mentions and replying. Peer agents were still shown as Disconnected during the latest Chrome verification, and the new harness has not produced a real reply confirmation.
- Submission wording must keep these separate: REST live boundary is verified; replay fallback is stable; complete autonomous live Band workflow remains a gate.

## Known Gaps Before Final Submission

- Official deadline, exact submission fields, partner access details and submitted-competitor context must be rechecked on the official page immediately before final submission.
- Public GitHub strategy is unresolved: make this repo public or create a sanitized public submission repo.
- Live autonomous SDK/WebSocket replies remain pending; the smoke harness is ready, but needs runtime `BAND_REST_URL` / `BAND_API_BASE` plus `TRUSTROOM_BAND_PEERS_JSON` for a connected peer.
- Deployment URL, cover image, video and slide deck are not yet final.
- Final submission must rerun no-secret checks and review wording.

## No-Overclaim Boundary

Do not describe this evidence packet as production, enterprise-ready deployment, fully automated compliance, legal advice, certified, long-term stable, or a formal security attestation.

Accurate description: current evidence supports a hackathon demo / working prototype with deterministic replay fallback, visible Band-style agent collaboration, evidence review, human approval, Final Pack and Governed Evolution.
