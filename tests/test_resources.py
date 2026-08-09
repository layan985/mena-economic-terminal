from __future__ import annotations

import csv
import unittest
from importlib.resources import files


def rows(filename: str):
    resource = files("menaecon.resources").joinpath(filename)
    with resource.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


class ResourceConsistencyTests(unittest.TestCase):
    def test_jordan_discoveries_reference_registered_sources_and_series(self):
        source_ids = {row["source_id"] for row in rows("source_registry.csv")}
        series_ids = {row["series_id"] for row in rows("series_catalog.csv")}
        for discovery in rows("jordan_source_discovery.csv"):
            self.assertIn(discovery["source_id"], source_ids)
            self.assertIn(discovery["series_id"], series_ids)
            self.assertIn(
                discovery["evidence_status"],
                {"discovery_only_not_warehouse", "captured_quarantined"},
            )

    def test_release_calendar_references_registered_sources_and_series(self):
        source_ids = {row["source_id"] for row in rows("source_registry.csv")}
        series_ids = {row["series_id"] for row in rows("series_catalog.csv")}
        for release in rows("release_calendar.csv"):
            self.assertIn(release["source_id"], source_ids)
            self.assertIn(release["series_id"], series_ids)
            self.assertNotEqual(release["calendar_status"], "verified_contractual")


if __name__ == "__main__":
    unittest.main()
