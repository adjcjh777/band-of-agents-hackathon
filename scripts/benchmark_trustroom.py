from __future__ import annotations

import argparse
import json
import statistics
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from fastapi.testclient import TestClient

from trustroom.agents.mock_runner import run_mock_trustroom
from trustroom.sample_loader import load_default_sample_pack, load_replay_events
from trustroom.web.app import app


BenchmarkFn = Callable[[], None]


@dataclass(frozen=True)
class BenchmarkResult:
    name: str
    iterations: int
    min_ms: float
    p50_ms: float
    p95_ms: float
    max_ms: float

    def as_dict(self) -> dict[str, float | int | str]:
        return {
            "name": self.name,
            "iterations": self.iterations,
            "min_ms": round(self.min_ms, 3),
            "p50_ms": round(self.p50_ms, 3),
            "p95_ms": round(self.p95_ms, 3),
            "max_ms": round(self.max_ms, 3),
        }


def measure(name: str, fn: BenchmarkFn, *, iterations: int) -> BenchmarkResult:
    if iterations < 1:
        raise ValueError("iterations must be at least 1")
    samples: list[float] = []
    for _ in range(iterations):
        started = time.perf_counter()
        fn()
        samples.append((time.perf_counter() - started) * 1000)
    sorted_samples = sorted(samples)
    if len(sorted_samples) == 1:
        p95 = sorted_samples[0]
    else:
        p95 = statistics.quantiles(sorted_samples, n=100, method="inclusive")[94]
    return BenchmarkResult(
        name=name,
        iterations=iterations,
        min_ms=min(sorted_samples),
        p50_ms=statistics.median(sorted_samples),
        p95_ms=p95,
        max_ms=max(sorted_samples),
    )


def run_benchmarks(*, iterations: int) -> dict[str, Any]:
    client = TestClient(app)

    def assert_route(path: str) -> None:
        response = client.get(path)
        if response.status_code != 200:
            raise AssertionError(f"{path} returned {response.status_code}")

    benchmarks = [
        measure("sample_load_ms", lambda: load_default_sample_pack(), iterations=iterations),
        measure("mock_run_ms", lambda: run_mock_trustroom(), iterations=iterations),
        measure("replay_load_ms", lambda: load_replay_events(), iterations=iterations),
        measure("dashboard_health_ms", lambda: assert_route("/health"), iterations=iterations),
        measure("dashboard_mock_ms", lambda: assert_route("/runs/demo"), iterations=iterations),
        measure("dashboard_replay_ms", lambda: assert_route("/runs/demo/replay"), iterations=iterations),
    ]
    return {
        "iterations": iterations,
        "benchmarks": {result.name: result.as_dict() for result in benchmarks},
    }


def threshold_failures(report: dict[str, Any], *, max_p95_ms: float | None) -> list[str]:
    if max_p95_ms is None:
        return []
    failures: list[str] = []
    for name, result in report["benchmarks"].items():
        p95 = result["p95_ms"]
        if p95 > max_p95_ms:
            failures.append(f"{name} p95_ms={p95} exceeds {max_p95_ms}")
    return failures


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Benchmark local RFP TrustRoom demo paths.")
    parser.add_argument("--iterations", type=int, default=20)
    parser.add_argument("--max-p95-ms", type=float, default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = run_benchmarks(iterations=args.iterations)
    failures = threshold_failures(report, max_p95_ms=args.max_p95_ms)
    report["passed"] = not failures
    report["failures"] = failures
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
