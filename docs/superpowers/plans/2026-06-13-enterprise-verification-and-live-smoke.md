# Enterprise Verification And Live Smoke Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add evidence-grade verification for RFP TrustRoom logic, local latency, and optional real Band live smoke without committing credentials.

**Architecture:** Keep replay/mock as the deterministic enterprise baseline. Add one local benchmark CLI for measured latency and one live smoke CLI that uses runtime-only Band credentials and writes only redacted evidence under ignored `reports/`.

**Tech Stack:** Python 3.11, standard library timers/JSON, FastAPI TestClient, existing `LiveBandAdapter`, pytest.

---

## File Map

- `scripts/benchmark_trustroom.py`: measures sample loading, mock workflow, replay loading, and dashboard endpoint latency.
- `scripts/run_live_band_smoke.py`: runtime-only live Band smoke using env credentials and redacted output.
- `src/trustroom/band/live_adapter.py`: live REST boundary fixes required for real Band requests.
- `tests/test_benchmark_trustroom.py`: verifies benchmark summary shape and threshold handling.
- `tests/test_live_band_smoke.py`: verifies missing-credential behavior and redacted evidence shape with fake adapter.
- `tests/test_live_adapter_contract.py`: verifies live REST request headers and Band-compatible event payloads.
- `README.md`: records current live Band runtime variables and handle-based peer mapping.
- `docs/submission-checklist.md`: records benchmark/live evidence status.
- `docs/agent-task-ledger.md`: tracks T13 lock and integration evidence.

### Task 1: Local Benchmark Harness

**Files:**
- Create: `scripts/benchmark_trustroom.py`
- Test: `tests/test_benchmark_trustroom.py`

- [x] **Step 1: Write tests for benchmark summary**

Create tests that call benchmark functions with a small iteration count and assert these keys exist: `sample_load_ms`, `mock_run_ms`, `replay_load_ms`, `dashboard_health_ms`, `dashboard_replay_ms`.

- [x] **Step 2: Implement benchmark CLI**

Implement functions that use `time.perf_counter`, compute min/p50/p95/max, and print JSON. The CLI should exit 0 when thresholds pass and 1 when an explicit threshold fails.

- [x] **Step 3: Run focused tests**

Run: `uv run pytest tests/test_benchmark_trustroom.py -v`

### Task 2: Live Band Smoke Harness

**Files:**
- Create: `scripts/run_live_band_smoke.py`
- Test: `tests/test_live_band_smoke.py`

- [x] **Step 1: Write tests for credential and redaction behavior**

Tests must assert missing credentials return a nonzero status without printing secret values, and fake live runs produce only `band-ref:*` references.

- [x] **Step 2: Implement live smoke CLI**

The CLI must read env vars, create a live room, optionally mention peer agents from `TRUSTROOM_BAND_PEERS_JSON`, record latency per operation, and write redacted JSON evidence to ignored `reports/`.

- [x] **Step 3: Run focused tests**

Run: `uv run pytest tests/test_live_band_smoke.py -v`

### Task 3: Evidence And Docs

**Files:**
- Modify: `docs/submission-checklist.md`
- Modify: `docs/agent-task-ledger.md`

- [x] **Step 1: Run local benchmark**

Run: `uv run python scripts/benchmark_trustroom.py --iterations 10`

- [x] **Step 2: Run live smoke if credentials exist**

Run: `uv run python scripts/run_live_band_smoke.py --dry-run-check` first. If credentials are missing, document the blocker. If present, run the real smoke and inspect the redacted evidence file.

- [x] **Step 3: Run final gates**

Run: `uv run python scripts/check_no_secrets.py`, `uv run pytest -v`, and `git diff --check`.
