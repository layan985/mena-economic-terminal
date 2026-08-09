#!/usr/bin/env python3
"""Fail closed if a warehouse is not safe to publish."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from menaecon.validation import ValidationError, validate_rows
from menaecon.warehouse import Warehouse


def verify(database: Path, backend: str = "auto") -> dict[str, object]:
    warehouse = Warehouse(database, backend=backend)
    rows = warehouse.all_rows()
    problems: list[str] = []
    if not rows:
        problems.append("warehouse is empty")
    try:
        validate_rows(rows)
    except ValidationError as exc:
        problems.extend(exc.errors)
    counts = warehouse.count_by_status()
    if counts.get("fixture", 0):
        problems.append(f"contains {counts['fixture']} fixture rows")
    if counts.get("quarantined", 0):
        problems.append(f"contains {counts['quarantined']} quarantined rows")
    if counts.get("verified", 0) != len(rows):
        problems.append("every release row must be verified")
    return {"ok": not problems, "rows": len(rows), "status_counts": counts, "problems": problems}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", required=True, type=Path)
    parser.add_argument("--backend", choices=["auto", "sqlite", "duckdb"], default="auto")
    args = parser.parse_args()
    report = verify(args.database, args.backend)
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
