from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


class JordanAuditArtifactTests(unittest.TestCase):
    def test_rights_pending_chart_is_not_public(self):
        chart = ROOT / "audit/jordan_unemployment_q1_2026_population_chart.csv"
        status = json.loads((ROOT / "audit/STATUS.json").read_text(encoding="utf-8"))
        rights = (ROOT / "DATA_RIGHTS.md").read_text(encoding="utf-8")
        self.assertFalse(chart.exists())
        self.assertEqual(status["chart_transcription"]["rows"], 51)
        self.assertFalse(status["chart_transcription"]["public_distribution"])
        self.assertIn("not covered by the MIT software license", rights)

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
        self.assertTrue(status["git_commit"]["completed"])
        self.assertEqual(
            status["git_commit"]["reference_commit"],
            "29e916ca3350ba748f30022e0353f35de210121b",
        )
        self.assertEqual(status["public_release_gate"], "blocked")


if __name__ == "__main__":
    unittest.main()
