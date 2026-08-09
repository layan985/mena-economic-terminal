"""Source adapter protocol. Network collection remains source-specific."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from ..model import Observation


@dataclass(frozen=True)
class SourceArtifact:
    source_id: str
    path: Path
    canonical_url: str
    source_document: str
    release_time: str
    retrieval_timestamp: str
    sha256: str
    media_type: str
    release_time_evidence: str
    license: str
    license_url: str
    license_evidence: str
    git_commit: str = "UNCOMMITTED"
    quality_status: str = "quarantined"


class Adapter(Protocol):
    """An adapter parses immutable bytes; it does not fetch mutable URLs itself."""

    source_id: str
    adapter_version: str

    def parse(self, artifact: SourceArtifact) -> Iterable[Observation]: ...
