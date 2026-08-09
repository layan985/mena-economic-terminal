"""Research-facing Python client."""

from __future__ import annotations

import csv
import json
import os
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from .warehouse import Warehouse


@dataclass(frozen=True)
class QueryResult:
    rows: list[dict[str, Any]]
    indicator: str
    country: str
    vintage: str

    def __iter__(self) -> Iterator[dict[str, Any]]:
        return iter(self.rows)

    def __len__(self) -> int:
        return len(self.rows)

    def to_dicts(self) -> list[dict[str, Any]]:
        return [dict(row) for row in self.rows]

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.rows, indent=indent, ensure_ascii=False)

    def to_csv(self, path: str | Path) -> Path:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        if not self.rows:
            output.write_text("", encoding="utf-8")
            return output
        with output.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(self.rows[0]))
            writer.writeheader()
            writer.writerows(self.rows)
        return output


class MenaClient:
    def __init__(self, database: str | Path | None = None, *, backend: str = "auto"):
        default_root = Path(os.environ.get("MENAEON_HOME", Path.home() / ".menaecon"))
        self.database = Path(database or default_root / "warehouse.db")
        self.warehouse = Warehouse(self.database, backend=backend)

    def get(
        self,
        indicator: str,
        *,
        country: str,
        vintage: str | date,
        series_id: str | None = None,
        entity: str | None = None,
        include_fixtures: bool = False,
    ) -> QueryResult:
        cutoff = vintage.isoformat() if isinstance(vintage, date) else vintage
        # Parse eagerly so malformed dates never become lexicographic SQL cutoffs.
        date.fromisoformat(cutoff)
        rows = self.warehouse.query_as_of(
            indicator,
            country=country.upper(),
            vintage=cutoff,
            series_id=series_id,
            entity=entity,
            include_fixtures=include_fixtures,
        )
        return QueryResult(rows, indicator, country.upper(), cutoff)
