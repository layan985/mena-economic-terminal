from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from menaecon import MenaClient
from scripts.verify_release import verify
from tests.helpers import valid_row


class ReleaseGateTests(unittest.TestCase):
    def test_verified_only_warehouse_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "verified.db"
            MenaClient(database, backend="sqlite").warehouse.ingest([valid_row()])
            self.assertTrue(verify(database, "sqlite")["ok"])

    def test_fixture_warehouse_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "fixture.db"
            client = MenaClient(database, backend="sqlite")
            client.warehouse.ingest(
                [valid_row(quality_status="fixture", git_commit="UNCOMMITTED")],
                allow_fixtures=True,
            )
            report = verify(database, "sqlite")
            self.assertFalse(report["ok"])
            self.assertIn("contains 1 fixture rows", report["problems"])


if __name__ == "__main__":
    unittest.main()
