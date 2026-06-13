from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "benchmark_trustroom.py"
SPEC = importlib.util.spec_from_file_location("benchmark_trustroom", MODULE_PATH)
assert SPEC is not None
assert SPEC.loader is not None
benchmark_trustroom = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = benchmark_trustroom
SPEC.loader.exec_module(benchmark_trustroom)

main = benchmark_trustroom.main
run_benchmarks = benchmark_trustroom.run_benchmarks
threshold_failures = benchmark_trustroom.threshold_failures


def test_run_benchmarks_reports_expected_latency_sections() -> None:
    report = run_benchmarks(iterations=1)

    assert report["iterations"] == 1
    for name in [
        "sample_load_ms",
        "mock_run_ms",
        "replay_load_ms",
        "dashboard_health_ms",
        "dashboard_mock_ms",
        "dashboard_replay_ms",
    ]:
        result = report["benchmarks"][name]
        assert result["iterations"] == 1
        assert result["min_ms"] >= 0
        assert result["p50_ms"] >= 0
        assert result["p95_ms"] >= 0
        assert result["max_ms"] >= 0


def test_threshold_failures_flags_slow_p95() -> None:
    report = {
        "benchmarks": {
            "fast": {"p95_ms": 5.0},
            "slow": {"p95_ms": 200.0},
        }
    }

    assert threshold_failures(report, max_p95_ms=100.0) == [
        "slow p95_ms=200.0 exceeds 100.0"
    ]


def test_cli_returns_nonzero_when_threshold_fails(capsys) -> None:
    exit_code = main(["--iterations", "1", "--max-p95-ms", "0"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert '"passed": false' in captured.out
