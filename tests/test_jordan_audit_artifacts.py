from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path

from menaecon.validation import validate_rows

ROOT = Path(__file__).resolve().parents[1]


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


class JordanAuditArtifactTests(unittest.TestCase):
    def test_chart_transcription_is_valid_and_quarantined(self):
        rows = read_csv(ROOT / "audit/jordan_unemployment_q1_2026_population_chart.csv")
        validated = validate_rows(rows)
        self.assertEqual(len(validated), 51)
        self.assertEqual({row.quality_status for row in validated}, {"quarantined"})
        self.assertEqual({row.vintage for row in validated}, {"2026-06-17"})
        self.assertEqual(
            {row.source_hash for row in validated},
            {"b3627bd4d5e5dbfc55f289a645dbc0f2ed8924b15bab027dd4b1f4d51c633f96"},
        )

    def test_blind_packet_has_twenty_unsigned_cells(self):
        rows = read_csv(ROOT / "audit/review_packets/jordan_unemployment_blind20.csv")
        self.assertEqual(len(rows), 20)
        self.assertEqual(len({row["sample_id"] for row in rows}), 20)
        self.assertTrue(all(not row["coder_value"] for row in rows))
        self.assertTrue(all(not row["reviewer_name"] for row in rows))

    def test_status_cannot_claim_public_release(self):
        status = json.loads((ROOT / "audit/STATUS.json").read_text(encoding="utf-8"))
        self.assertTrue(status["artifact_capture"]["completed"])
        self.assertFalse(status["artifact_capture"]["raw_bytes_public"])
        self.assertFalse(status["independent_review"]["external_reviewer_signed"])
        self.assertFalse(status["git_commit"]["completed"])
        self.assertEqual(status["public_release_gate"], "blocked")


if __name__ == "__main__":
    unittest.main()
