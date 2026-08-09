"""Contracts for source-specific ingestion adapters."""

from .base import Adapter, SourceArtifact
from .csv_adapter import CanonicalCsvAdapter

__all__ = ["Adapter", "CanonicalCsvAdapter", "SourceArtifact"]
