"""Adapter for CSV files already conforming to the canonical contract."""

from __future__ import annotations

import csv
from collections.abc import Iterable

from ..model import Observation
from ..validation import validate_observation
from .base import SourceArtifact


class CanonicalCsvAdapter:
    source_id = "CANONICAL_CSV"
    adapter_version = "0.1.0"

    def parse(self, artifact: SourceArtifact) -> Iterable[Observation]:
        with artifact.path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                if row.get("source_hash") != artifact.sha256:
                    raise ValueError("row source_hash does not match immutable artifact hash")
                if row.get("retrieval_timestamp") != artifact.retrieval_timestamp:
                    raise ValueError("row retrieval timestamp does not match artifact metadata")
                yield validate_observation(row)
