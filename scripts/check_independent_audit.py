#!/usr/bin/env python3
"""Score a completed blind audit without weakening independence requirements."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path


def _read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def score(packet: Path, answer_key: Path, *, implementer: str) -> dict[str, object]:
    coded = _read(packet)
    answers = {row["sample_id"]: float(row["expected_value"]) for row in _read(answer_key)}
    problems: list[str] = []
    if len(coded) != 20:
        problems.append(f"packet must contain 20 rows; found {len(coded)}")
    coded_ids = [row.get("sample_id", "") for row in coded]
    if len(set(coded_ids)) != len(coded_ids):
        problems.append("sample IDs are not unique")
    if set(coded_ids) != set(answers):
        problems.append("packet and answer-key sample IDs differ")

    reviewers = {row.get("reviewer_name", "").strip() for row in coded}
    reviewers.discard("")
    if len(reviewers) != 1:
        problems.append("exactly one named reviewer must sign every row")
    reviewer = next(iter(reviewers), "")
    if reviewer.casefold() == implementer.strip().casefold():
        problems.append("reviewer must be independent of the implementer")

    value_matches = 0
    scope_matches = 0
    mismatches: list[str] = []
    for row in coded:
        sample_id = row.get("sample_id", "")
        try:
            value = float(row.get("coder_value", ""))
        except ValueError:
            problems.append(f"{sample_id}: coder_value is missing or non-numeric")
            continue
        expected = answers.get(sample_id)
        if expected is not None and abs(value - expected) <= 1e-9:
            value_matches += 1
        else:
            mismatches.append(sample_id)
        if row.get("coder_scope_match", "").strip().casefold() in {"yes", "true", "1"}:
            scope_matches += 1
        else:
            problems.append(f"{sample_id}: scope was not confirmed")
        try:
            datetime.fromisoformat(row.get("reviewed_at", "").replace("Z", "+00:00"))
        except ValueError:
            problems.append(f"{sample_id}: reviewed_at must be ISO-8601")

    n = len(coded)
    value_agreement = value_matches / n if n else 0.0
    scope_agreement = scope_matches / n if n else 0.0
    if mismatches:
        problems.append(f"value mismatches: {', '.join(mismatches)}")
    return {
        "ok": not problems and n == 20 and value_agreement == 1.0 and scope_agreement == 1.0,
        "reviewer": reviewer,
        "sample_size": n,
        "value_agreement": value_agreement,
        "scope_agreement": scope_agreement,
        "mismatches": mismatches,
        "problems": problems,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("packet", type=Path)
    parser.add_argument("answer_key", type=Path)
    parser.add_argument("--implementer", required=True)
    args = parser.parse_args()
    report = score(args.packet, args.answer_key, implementer=args.implementer)
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
