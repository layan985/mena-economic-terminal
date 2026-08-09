from __future__ import annotations

import tempfile
import unittest
from dataclasses import replace
from hashlib import sha256
from pathlib import Path

from menaecon.ingest.base import SourceArtifact
from menaecon.sources import CbjPolicyRateAdapter, DosCpiAdapter, DosUnemploymentAdapter


def artifact(path: Path, content: str, source_id: str) -> SourceArtifact:
    path.write_text(content, encoding="utf-8")
    return SourceArtifact(
        source_id=source_id,
        path=path,
        canonical_url="https://example.org/release",
        source_document="https://example.org/release/document",
        release_time="2026-06-17T12:08:09+03:00",
        retrieval_timestamp="2026-06-17T13:00:00+03:00",
        sha256=sha256(content.encode("utf-8")).hexdigest(),
        media_type="text/plain",
        release_time_evidence="publisher page timestamp",
        license="TBD",
        license_url="",
        license_evidence="rights review pending",
    )


class JordanSourceTests(unittest.TestCase):
    def test_unemployment_parser_preserves_population_scope(self):
        text = (
            "Department of Statistics. Unemployment rate (UNRATE) for the total population in Jordan "
            "decreased to 16.1% in Q1 2026. Among Jordanian males it reached 17.9%."
        )
        with tempfile.TemporaryDirectory() as directory:
            source = artifact(Path(directory) / "release.txt", text, "JOR_DOS")
            row = next(iter(DosUnemploymentAdapter().parse(source)))
        self.assertEqual(row.series_id, "labor.unemployment.total_population")
        self.assertEqual(row.entity, "ALL_RESIDENTS")
        self.assertEqual(row.value, 16.1)
        self.assertEqual(row.period, "2026-Q1")
        self.assertEqual(row.quality_status, "quarantined")

    def test_unemployment_parser_rejects_jordanian_only_release(self):
        text = "Unemployment among Jordanian males reached 17.9% during Q1 2026."
        with tempfile.TemporaryDirectory() as directory:
            source = artifact(Path(directory) / "release.txt", text, "JOR_DOS")
            with self.assertRaisesRegex(ValueError, "total-population"):
                list(DosUnemploymentAdapter().parse(source))

    def test_unemployment_parser_ignores_comparison_period(self):
        text = (
            "Unemployment rate (UNRATE) for the total population reached 16.1% in Q1 2026, "
            "compared with Q1 2025."
        )
        with tempfile.TemporaryDirectory() as directory:
            source = artifact(Path(directory) / "release.txt", text, "JOR_DOS")
            row = next(iter(DosUnemploymentAdapter().parse(source)))
        self.assertEqual(row.period, "2026-Q1")

    def test_unemployment_parser_rejects_conflicting_primary_matches(self):
        text = (
            "Unemployment rate (UNRATE) for the total population reached 16.1% in Q1 2026. "
            "Unemployment among the Entire Population: UNRATE reached 16.2% in Q1 2026."
        )
        with tempfile.TemporaryDirectory() as directory:
            source = artifact(Path(directory) / "release.txt", text, "JOR_DOS")
            with self.assertRaisesRegex(ValueError, "2 distinct values"):
                list(DosUnemploymentAdapter().parse(source))

    def test_unemployment_parser_accepts_consistent_repeated_headline(self):
        text = (
            "Unemployment rate (UNRATE) for the total population reached 16.1% in Q1 2026. "
            "Detailed results: Unemployment among the Entire Population: UNRATE reached "
            "16.1% during Q1 2026."
        )
        with tempfile.TemporaryDirectory() as directory:
            source = artifact(Path(directory) / "release.txt", text, "JOR_DOS")
            row = next(iter(DosUnemploymentAdapter().parse(source)))
        self.assertEqual(row.value, 16.1)

    def test_cpi_parser_extracts_monthly_yoy_not_cumulative_rate(self):
        text = (
            "The Department of Statistics issued its monthly report on the Consumer Price "
            "Index of March 2026, which reached 1.87% compared to the same month in 2025. "
            "On a cumulative basis the rate was 1.36%."
        )
        with tempfile.TemporaryDirectory() as directory:
            source = artifact(Path(directory) / "release.txt", text, "JOR_DOS")
            row = next(iter(DosCpiAdapter().parse(source)))
        self.assertEqual(row.period, "2026-03")
        self.assertEqual(row.value, 1.87)
        self.assertEqual(row.unit, "percent_yoy")

    def test_cbj_policy_parser_extracts_key_rate(self):
        text = (
            "The Committee decided to maintain the key interest rate of the Central Bank "
            "at its current rate of 5.75% while keeping other instruments unchanged."
        )
        with tempfile.TemporaryDirectory() as directory:
            source = artifact(Path(directory) / "release.txt", text, "JOR_CBJ")
            source = replace(source, release_time="2026-04-30T10:00:00+03:00")
            row = next(iter(CbjPolicyRateAdapter().parse(source)))
        self.assertEqual(row.series_id, "monetary.policy_rate.cbj_main")
        self.assertEqual(row.period, "2026-04-30")
        self.assertEqual(row.value, 5.75)

    def test_cbj_html_parser_ignores_script_decoy(self):
        text = """
        <html><script>CBJ main rate at 99%</script><body>
        <p>The Committee maintained the key interest rate of the Central Bank
        at its current rate of 5.75%.</p></body></html>
        """
        with tempfile.TemporaryDirectory() as directory:
            source = artifact(Path(directory) / "release.html", text, "JOR_CBJ")
            source = replace(
                source,
                media_type="text/html",
                release_time="2026-04-30T10:00:00+03:00",
            )
            row = next(iter(CbjPolicyRateAdapter().parse(source)))
        self.assertEqual(row.value, 5.75)


if __name__ == "__main__":
    unittest.main()
