from __future__ import annotations

from trustroom.readiness import scan_no_secrets


def main() -> int:
    hits = scan_no_secrets()
    if not hits:
        print("No secret-like values found.")
        return 0

    print("Secret-like values found:")
    for hit in hits:
        print(f"- {hit.source}:{hit.line_number} [{hit.pattern_name}] {hit.match}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
