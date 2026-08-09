from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from scripts.check_independent_audit import score


class IndependentAuditTests(unittest.TestCase):
    def _files(self, root: Path, reviewer: str):
        packet = root / "packet.csv"
        key = root / "key.csv"
        with packet.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "sample_id", "coder_value", "coder_scope_match", "reviewer_name",
                    "reviewed_at",
                ],
            )
            writer.writeheader()
            for index in range(20):
                writer.writerow(
                    {
                        "sample_id": f"AUD-{index:03d}",
                        "coder_value": str(index),
                        "coder_scope_match": "yes",
                        "reviewer_name": reviewer,
                        "reviewed_at": "2026-08-10T12:00:00+03:00",
                    }
                )
        with key.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=["sample_id", "expected_value"])
            writer.writeheader()
            for index in range(20):
                writer.writerow({"sample_id": f"AUD-{index:03d}", "expected_value": index})
        return packet, key

    def test_perfect_external_review_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            packet, key = self._files(Path(directory), "External Reviewer")
            self.assertTrue(score(packet, key, implementer="Layan Oraidi")["ok"])

    def test_self_review_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            packet, key = self._files(Path(directory), "Layan Oraidi")
            report = score(packet, key, implementer="Layan Oraidi")
            self.assertFalse(report["ok"])
            self.assertIn("reviewer must be independent", " ".join(report["problems"]))


if __name__ == "__main__":
    unittest.main()
