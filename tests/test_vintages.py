from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from menaecon import MenaClient
from tests.helpers import valid_row


class VintageQueryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.client = MenaClient(Path(self.temp.name) / "warehouse.db", backend="sqlite")

    def tearDown(self):
        self.temp.cleanup()

    def test_future_revision_does_not_leak(self):
        initial = valid_row(value=21.4)
        revision = valid_row(
            value=21.1,
            release_time="2026-06-15T08:00:00+03:00",
            retrieval_timestamp="2026-06-15T09:00:00+03:00",
            vintage="2026-06-15",
            revision=1,
            source_hash="b" * 64,
        )
        self.client.warehouse.ingest([initial, revision])

        before = self.client.get(
            "unemployment", country="JOR", vintage="2026-06-01"
        ).to_dicts()
        after = self.client.get(
            "unemployment", country="JOR", vintage="2026-06-16"
        ).to_dicts()
        self.assertEqual(before[0]["value"], 21.4)
        self.assertEqual(before[0]["revision"], 0)
        self.assertEqual(after[0]["value"], 21.1)
        self.assertEqual(after[0]["revision"], 1)

    def test_fixture_rows_are_hidden_by_default(self):
        fixture = valid_row(quality_status="fixture", git_commit="UNCOMMITTED")
        self.client.warehouse.ingest([fixture], allow_fixtures=True)
        self.assertEqual(
            len(self.client.get("unemployment", country="JOR", vintage="2026-03-01")), 0
        )
        self.assertEqual(
            len(
                self.client.get(
                    "unemployment",
                    country="JOR",
                    vintage="2026-03-01",
                    include_fixtures=True,
                )
            ),
            1,
        )

    def test_fixture_requires_explicit_ingest_permission(self):
        fixture = valid_row(quality_status="fixture", git_commit="UNCOMMITTED")
        with self.assertRaisesRegex(ValueError, "allow_fixtures=True"):
            self.client.warehouse.ingest([fixture])

    def test_malformed_cutoff_never_reaches_sql(self):
        with self.assertRaises(ValueError):
            self.client.get("unemployment", country="JOR", vintage="June 2026")


if __name__ == "__main__":
    unittest.main()
