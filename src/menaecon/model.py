"""Canonical observation model and deterministic identity."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass, fields
from hashlib import sha256
from typing import Any


@dataclass(frozen=True)
class Observation:
    series_id: str
    indicator: str
    value: float
    unit: str
    country: str
    entity: str
    period: str
    frequency: str
    release_time: str
    vintage: str
    revision: int
    source: str
    source_url: str
    source_document: str
    retrieval_timestamp: str
    transformation: str
    license: str
    license_url: str
    source_hash: str
    git_commit: str
    quality_status: str
    notes: str = ""
    observation_id: str = ""

    @classmethod
    def from_mapping(cls, row: Mapping[str, Any]) -> Observation:
        known = {field.name for field in fields(cls)}
        payload = {key: value for key, value in row.items() if key in known}
        payload["value"] = float(payload["value"])
        payload["revision"] = int(payload["revision"])
        payload.setdefault("entity", "")
        payload.setdefault("notes", "")
        payload.setdefault("observation_id", "")
        observation = cls(**payload)
        if observation.observation_id:
            return observation
        return cls(**{**asdict(observation), "observation_id": observation.identity()})

    def identity(self) -> str:
        natural_key = {
            "series_id": self.series_id,
            "country": self.country,
            "entity": self.entity,
            "period": self.period,
            "release_time": self.release_time,
            "vintage": self.vintage,
            "revision": self.revision,
            "source_hash": self.source_hash,
        }
        canonical = json.dumps(natural_key, sort_keys=True, separators=(",", ":"))
        return sha256(canonical.encode("utf-8")).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
