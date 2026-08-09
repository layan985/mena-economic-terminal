from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from menaecon import MenaClient
from tests.helpers import valid_row


class RoundTripTests(unittest.TestCase):
    def test_query_result_exports_csv(self):
        with tempfile.TemporaryDirectory() as directory:
            client = MenaClient(Path(directory) / "warehouse.db", backend="sqlite")
            client.warehouse.ingest([valid_row()])
            result = client.get("unemployment", country="jor", vintage="2026-02-20")
            output = result.to_csv(Path(directory) / "export.csv")
            self.assertTrue(output.exists())
            self.assertIn("observation_id", output.read_text(encoding="utf-8"))

    def test_duplicate_identity_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            client = MenaClient(Path(directory) / "warehouse.db", backend="sqlite")
            row = valid_row()
            client.warehouse.ingest([row])
            with self.assertRaises(sqlite3.IntegrityError):
                client.warehouse.ingest([row])


if __name__ == "__main__":
    unittest.main()
