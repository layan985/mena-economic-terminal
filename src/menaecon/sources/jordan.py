"""Strict parsers for selected Jordan official releases.

These adapters parse immutable artifacts. They deliberately reject ambiguous scope,
period and value matches rather than making economic assumptions.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from collections.abc import Iterable
from datetime import date
from html.parser import HTMLParser

from ..ingest.base import SourceArtifact
from ..model import Observation
from ..validation import validate_observation

QUARTERS = {"1": "Q1", "2": "Q2", "3": "Q3", "4": "Q4"}
MONTHS = {
    name.lower(): number
    for number, name in enumerate(
        [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December",
        ],
        start=1,
    )
}


class _VisibleTextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts: list[str] = []
        self.hidden_depth = 0

    def handle_starttag(self, tag: str, attrs):
        if tag in {"script", "style", "noscript"}:
            self.hidden_depth += 1

    def handle_endtag(self, tag: str):
        if tag in {"script", "style", "noscript"} and self.hidden_depth:
            self.hidden_depth -= 1

    def handle_data(self, data: str):
        if not self.hidden_depth:
            self.parts.append(data)


def _artifact_text(artifact: SourceArtifact) -> str:
    if artifact.media_type == "application/pdf" or artifact.path.suffix.lower() == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            if not shutil.which("pdftotext"):
                raise RuntimeError(
                    "PDF source requires `pip install menaecon[jordan]` or Poppler pdftotext"
                ) from exc
            result = subprocess.run(
                ["pdftotext", "-layout", str(artifact.path), "-"],
                check=True,
                capture_output=True,
                text=True,
                timeout=60,
            )
            return result.stdout
        return "\n".join(page.extract_text() or "" for page in PdfReader(artifact.path).pages)
    text = artifact.path.read_text(encoding="utf-8")
    if artifact.media_type == "text/html" or artifact.path.suffix.lower() in {".html", ".htm"}:
        parser = _VisibleTextParser()
        parser.feed(text)
        return " ".join(parser.parts)
    return text


def _single(pattern: str, text: str, label: str, flags: int = re.IGNORECASE | re.DOTALL):
    matches = re.findall(pattern, text, flags)
    if len(matches) != 1:
        raise ValueError(f"expected exactly one {label}; found {len(matches)}")
    return matches[0]


def _consistent(pattern: str, text: str, label: str):
    matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
    unique = list(dict.fromkeys(matches))
    if len(unique) != 1:
        raise ValueError(
            f"expected one consistent {label}; found {len(matches)} matches and "
            f"{len(unique)} distinct values"
        )
    return unique[0]


def _row(
    artifact: SourceArtifact,
    *,
    series_id: str,
    indicator: str,
    value: float,
    unit: str,
    period: str,
    frequency: str,
    entity: str,
    transformation: str = "identity",
    notes: str = "",
) -> Observation:
    return validate_observation(
        {
            "series_id": series_id,
            "indicator": indicator,
            "value": value,
            "unit": unit,
            "country": "JOR",
            "entity": entity,
            "period": period,
            "frequency": frequency,
            "release_time": artifact.release_time,
            "vintage": date.fromisoformat(artifact.release_time[:10]).isoformat(),
            "revision": 0,
            "source": artifact.source_id,
            "source_url": artifact.canonical_url,
            "source_document": artifact.source_document,
            "retrieval_timestamp": artifact.retrieval_timestamp,
            "transformation": transformation,
            "license": artifact.license,
            "license_url": artifact.license_url,
            "source_hash": artifact.sha256,
            "git_commit": artifact.git_commit,
            "quality_status": artifact.quality_status,
            "notes": notes,
        }
    )


class DosUnemploymentAdapter:
    source_id = "JOR_DOS_UNEMPLOYMENT"
    adapter_version = "0.2.0a1"

    def parse(self, artifact: SourceArtifact) -> Iterable[Observation]:
        text = " ".join(_artifact_text(artifact).split())
        # Require an explicit total-population phrase near the value. This prevents
        # Jordanian-only male/female rates from entering the total-resident series.
        value, quarter, year = _consistent(
            r"(?:"
            r"Unemployment rate\s*\(UNRATE\)\s+for the total population[^.%]{0,180}?"
            r"(?:reached|to)|"
            r"Unemployment among the Entire Population[^%]{0,100}?UNRATE\s+reached"
            r")\s+"
            r"(\d{1,2}(?:\.\d+)?)%[^.]{0,100}?\bQ([1-4])\s+(20\d{2})\b",
            text,
            "total-population unemployment rate",
        )
        yield _row(
            artifact,
            series_id="labor.unemployment.total_population",
            indicator="unemployment",
            value=float(value),
            unit="percent",
            period=f"{year}-{QUARTERS[quarter]}",
            frequency="quarterly",
            entity="ALL_RESIDENTS",
            notes="Coverage: Jordanians and non-Jordanians; source wording required by parser",
        )


class DosCpiAdapter:
    source_id = "JOR_DOS_CPI"
    adapter_version = "0.2.0a1"

    def parse(self, artifact: SourceArtifact) -> Iterable[Observation]:
        text = " ".join(_artifact_text(artifact).split())
        month_name, year, value = _single(
            r"Consumer Price Index(?:\s*\(CPI\))?\s+of\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(20\d{2}).{0,180}?(\d{1,2}(?:\.\d+)?)%\s+compared to\s+(?:the\s+)?same month",
            text,
            "monthly CPI year-on-year rate",
        )
        period = f"{year}-{MONTHS[month_name.lower()]:02d}"
        yield _row(
            artifact,
            series_id="prices.cpi.headline_yoy",
            indicator="inflation",
            value=float(value),
            unit="percent_yoy",
            period=period,
            frequency="monthly",
            entity="ALL_ITEMS",
            transformation="source_reported_yoy",
        )


class CbjPolicyRateAdapter:
    source_id = "JOR_CBJ_POLICY_RATE"
    adapter_version = "0.2.0a1"

    def parse(self, artifact: SourceArtifact) -> Iterable[Observation]:
        text = " ".join(_artifact_text(artifact).split())
        value = _single(
            r"(?:key interest rate of the Central Bank|CBJ main rate)[^.%]{0,180}?(?:rate of|at)\s+(\d{1,2}(?:\.\d+)?)%",
            text,
            "CBJ key policy rate",
        )
        effective_date = artifact.release_time[:10]
        yield _row(
            artifact,
            series_id="monetary.policy_rate.cbj_main",
            indicator="policy_rate",
            value=float(value),
            unit="percent",
            period=effective_date,
            frequency="event",
            entity="CBJ_MAIN_RATE",
            notes="Event date is release date unless separate effective-date evidence is supplied",
        )
