# RFP TrustRoom 5-Minute Video Script And Shot List

Status: draft-ready for recording. Record the public-safe replay route from the deployed Application URL: `https://rfp-trustroom.onrender.com/runs/demo/replay`.

## Route

0:00-0:20 Hook / pain
- Visual: cover image or slide 1.
- Say: B2B RFP and security questionnaires are not one chatbot or one audit dashboard problem; they are cross-team evidence, wording, approval and final-pack decision workflows.

0:20-0:45 Solution / roles
- Visual: Band coordination layer slide.
- Say: RFP TrustRoom uses Band as the coordination layer for specialized agents and a human approver, carrying handoffs, shared object references, task state, reviewer challenges and approval context.

0:45-1:15 Executive Decision
- Visual: /runs/demo/replay first screen.
- Say: Seven answers can enter the pack; Q-006 is excluded; the customer pack is not auto-sent.

1:15-1:55 Run Trace + Business Milestones
- Visual: Run Trace proof strip and milestones.
- Say: The judge route exposes roles, handoffs, review loop, approvals, final pack and replay mode without reading raw logs.

1:55-2:35 Agent Handoff Chain
- Visual: Agent Handoff Chain.
- Say: Band-style handoffs move shared object refs and task state from orchestrator to decomposer, retriever, drafter, reviewer and human approver.

2:35-3:25 Representative Item Traces
- Visual: Q-002, Q-004 and Q-006 traces.
- Say: Q-002 is an approved path; Q-004 shows review loop -> legal approval -> included; Q-006 shows fail-closed exclusion.

3:25-4:05 Q-006 Blocked Impact Path
- Visual: stale/conflicting evidence -> needs approval -> no valid approval -> final pack excluded -> policy owner next action.
- Say: This is the enterprise buyer value moment: unsafe incident-response language stays out of the customer pack.

4:05-4:35 Final Pack
- Visual: Final Pack / Evidence Index / Approval Workbench.
- Say: The result is not just generated copy; it is an answer pack with evidence and approval context.

4:35-5:00 Boundary / value
- Visual: replay/live boundary and no-overclaim footer.
- Say: This is a hackathon working prototype. Replay is the public-safe fallback. Band REST room and handoff boundary were separately verified; autonomous live replies remain a separate gate. The value is the final-pack decision: the room shows what is safe to send and what must wait for policy-owner approval.

## Recording notes

- Do not scroll continuously through the entire dashboard.
- Use browser zoom around 90-100%.
- Hide bookmarks, account tabs and anything that could expose raw ids or account data.
- Avoid showing live Band account pages unless sanitized.
- Do not claim more than the public-safe replay deployment. Keep live REST evidence and autonomous live replies as separate, bounded claims.
