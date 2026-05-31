from __future__ import annotations

from trustroom.readiness import run_readiness_checks


def main() -> int:
    report = run_readiness_checks()
    if report.passed:
        print("TrustRoom readiness OK")
        for name, value in sorted(report.metrics.items()):
            print(f"- {name}: {value}")
        return 0

    print("TrustRoom readiness failed")
    for issue in report.issues:
        print(f"- {issue.code}: {issue.message}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
