"""Append-only warehouse with point-in-time query semantics."""

from __future__ import annotations

import csv
import sqlite3
from collections.abc import Iterable, Mapping
from importlib.util import find_spec
from pathlib import Path
from typing import Any

from .model import Observation
from .validation import validate_rows

COLUMNS = [
    "observation_id", "series_id", "indicator", "value", "unit", "country",
    "entity", "period", "frequency", "release_time", "vintage", "revision",
    "source", "source_url", "source_document", "retrieval_timestamp",
    "transformation", "license", "license_url", "source_hash", "git_commit",
    "quality_status", "notes",
]

DDL = """
CREATE TABLE IF NOT EXISTS observations (
    observation_id TEXT PRIMARY KEY,
    series_id TEXT NOT NULL,
    indicator TEXT NOT NULL,
    value DOUBLE NOT NULL,
    unit TEXT NOT NULL,
    country TEXT NOT NULL,
    entity TEXT NOT NULL,
    period TEXT NOT NULL,
    frequency TEXT NOT NULL,
    release_time TEXT NOT NULL,
    vintage TEXT NOT NULL,
    revision INTEGER NOT NULL,
    source TEXT NOT NULL,
    source_url TEXT NOT NULL,
    source_document TEXT NOT NULL,
    retrieval_timestamp TEXT NOT NULL,
    transformation TEXT NOT NULL,
    license TEXT NOT NULL,
    license_url TEXT NOT NULL,
    source_hash TEXT NOT NULL,
    git_commit TEXT NOT NULL,
    quality_status TEXT NOT NULL,
    notes TEXT NOT NULL,
    UNIQUE(series_id, country, entity, period, vintage, revision, source_hash)
)
"""


class Warehouse:
    def __init__(self, path: str | Path, backend: str = "auto"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if backend not in {"auto", "sqlite", "duckdb"}:
            raise ValueError("backend must be auto, sqlite or duckdb")
        self.backend = backend
        if backend == "auto":
            self.backend = "duckdb" if find_spec("duckdb") else "sqlite"
        if self.backend == "duckdb" and not find_spec("duckdb"):
            raise RuntimeError("DuckDB backend requested; install with `pip install menaecon[duckdb]`")
        self.initialize()

    def connect(self):
        if self.backend == "duckdb":
            import duckdb

            return duckdb.connect(str(self.path))
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.execute(DDL)
            connection.commit()

    def ingest(
        self,
        rows: Iterable[Mapping[str, Any] | Observation],
        *,
        allow_fixtures: bool = False,
    ) -> int:
        observations = validate_rows(rows)
        if not allow_fixtures and any(row.quality_status == "fixture" for row in observations):
            raise ValueError("fixture rows require allow_fixtures=True")
        placeholders = ",".join("?" for _ in COLUMNS)
        sql = f"INSERT INTO observations ({','.join(COLUMNS)}) VALUES ({placeholders})"
        values = [[row.to_dict()[column] for column in COLUMNS] for row in observations]
        with self.connect() as connection:
            connection.executemany(sql, values)
            connection.commit()
        return len(values)

    def ingest_csv(self, path: str | Path, *, allow_fixtures: bool = False) -> int:
        with Path(path).open(newline="", encoding="utf-8") as handle:
            return self.ingest(csv.DictReader(handle), allow_fixtures=allow_fixtures)

    def query_as_of(
        self,
        indicator: str,
        *,
        country: str,
        vintage: str,
        series_id: str | None = None,
        entity: str | None = None,
        include_fixtures: bool = False,
    ) -> list[dict[str, Any]]:
        filters = [
            "indicator = ?",
            "country = ?",
            "substr(release_time, 1, 10) <= ?",
            "vintage <= ?",
            "quality_status != 'quarantined'",
        ]
        params: list[Any] = [indicator, country, vintage, vintage]
        if series_id:
            filters.append("series_id = ?")
            params.append(series_id)
        if entity is not None:
            filters.append("entity = ?")
            params.append(entity)
        if not include_fixtures:
            filters.append("quality_status = 'verified'")
        where = " AND ".join(filters)
        sql = f"""
            WITH eligible AS (
                SELECT *, ROW_NUMBER() OVER (
                    PARTITION BY series_id, country, entity, period
                    ORDER BY release_time DESC, revision DESC, vintage DESC
                ) AS release_rank
                FROM observations
                WHERE {where}
            )
            SELECT {','.join(COLUMNS)}
            FROM eligible
            WHERE release_rank = 1
            ORDER BY period, series_id, entity
        """
        with self.connect() as connection:
            cursor = connection.execute(sql, params)
            names = [description[0] for description in cursor.description]
            return [dict(zip(names, row)) for row in cursor.fetchall()]

    def count_by_status(self) -> dict[str, int]:
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT quality_status, COUNT(*) FROM observations GROUP BY quality_status"
            ).fetchall()
        return {row[0]: row[1] for row in rows}

    def all_rows(self) -> list[dict[str, Any]]:
        with self.connect() as connection:
            cursor = connection.execute(f"SELECT {','.join(COLUMNS)} FROM observations")
            names = [description[0] for description in cursor.description]
            return [dict(zip(names, row)) for row in cursor.fetchall()]
