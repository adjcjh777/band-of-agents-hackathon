# Dual-Agent Coordination Reset Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` for implementation work, or `superpowers:executing-plans` for single-agent execution. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish a repo-local operating protocol that lets Codex and Claude Code work in parallel without file conflicts, style drift, secret leakage, or inconsistent project claims.

**Architecture:** Codex acts as controller and final integrator. Claude Code can own independent text/code slices only after the controller records file locks in the ledger. A lightweight script validates active locks before any dual-agent dispatch or branch integration.

**Tech Stack:** Markdown runbooks, Python 3.11, pytest, git branches/worktrees, existing AGENTS.md rules.

---

## Coordination Rules

- This reset is documentation and guardrail work only. Do not implement TrustRoom product features here.
- Preserve the project boundary: do not read, modify, stage, commit or cite `pilotdeck/`.
- Treat `README.md`, `pyproject.toml`, `uv.lock`, `AGENTS.md`, shared plans, and public submission docs as controller-owned unless the ledger explicitly says otherwise.
- Codex owns multimodal, Chrome, dashboard visual QA, live Band, architecture, integration and final review tasks.
- Claude Code owns bounded text/code/test tasks with no multimodal dependency and no shared-file edits.
- Both agents must use the same AGENTS.md, protocol, ledger, no-overclaim and secret rules.

## Task 1: Write The Protocol

**Files:**
- Create: `docs/dual-agent-operating-protocol.md`

- [x] Define roles for Codex controller, Codex implementer and Claude Code implementer.
- [x] Define the file-lock rule: one active writer per path or subtree.
- [x] Define branch/worktree flow, dispatch prompts, integration review and conflict handling.
- [x] State Claude Code's MiMo v2.5 Pro limitation: no multimodal or Chrome-only tasks.

## Task 2: Write The Ledger

**Files:**
- Create: `docs/agent-task-ledger.md`

- [x] Add an active lock row for this coordination reset.
- [x] Add planned owner suggestions for TrustRoom implementation tasks T1 through T12.
- [x] Include owner, branch, status, locked paths, review owner and required checks.
- [x] Make future shared-file edits controller-owned by default.

## Task 3: Add A Machine Check

**Files:**
- Create: `scripts/check_dual_agent_protocol.py`
- Create: `tests/test_dual_agent_protocol.py`

- [x] Parse the active file-lock table from `docs/agent-task-ledger.md`.
- [x] Fail on duplicate active file locks or parent/subtree lock conflicts.
- [x] Fail on forbidden locked paths: `pilotdeck/`, `.env`, `agent_config.yaml`.
- [x] Fail on invalid owner, branch prefix, missing locked paths or missing required checks.
- [x] Cover the validator with pytest tests.

## Task 4: Link The Reset Into Existing Docs

**Files:**
- Modify: `README.md`
- Modify: `docs/superpowers/plans/2026-05-30-rfp-trustroom-implementation.md`

- [x] Add the protocol and ledger to README local docs.
- [x] Add a dual-agent execution contract to the TrustRoom implementation plan.
- [x] Require the validator before dispatching or integrating dual-agent work.

## Verification

- [x] `uv run pytest tests/test_dual_agent_protocol.py -v`
- [x] `uv run python scripts/check_dual_agent_protocol.py`
- [x] `git diff --check`

## Commit

- [ ] Stage only coordination-reset files.
- [ ] Commit with `docs: add dual-agent coordination protocol`.
- [ ] Push the current branch.
