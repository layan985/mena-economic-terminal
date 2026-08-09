"""Validation rules for public economic observations."""

from __future__ import annotations

import math
import re
from collections.abc import Iterable, Mapping
from datetime import date, datetime, timezone
from typing import Any
from urllib.parse import urlparse

from .model import Observation

COUNTRY = re.compile(r"^[A-Z]{3}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
GIT_COMMIT = re.compile(r"^[0-9a-f]{40}$")
PERIOD = re.compile(r"^\d{4}(?:-(?:\d{2}|Q[1-4]|W\d{2})(?:-\d{2})?)?$")
FREQUENCIES = {"daily", "weekly", "monthly", "quarterly", "annual", "event"}
QUALITY = {"fixture", "verified", "quarantined"}


class ValidationError(ValueError):
    """A row failed the observation contract."""

    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


def _timestamp(value: str, field: str, errors: list[str]) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        errors.append(f"{field} must be ISO-8601")
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        errors.append(f"{field} must include a timezone")
        return None
    return parsed.astimezone(timezone.utc)


def _date(value: str, field: str, errors: list[str]) -> date | None:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        errors.append(f"{field} must be YYYY-MM-DD")
        return None


def _url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def validate_observation(row: Mapping[str, Any] | Observation) -> Observation:
    try:
        observation = row if isinstance(row, Observation) else Observation.from_mapping(row)
    except (KeyError, TypeError, ValueError) as exc:
        raise ValidationError([f"invalid or missing field: {exc}"]) from exc

    errors: list[str] = []
    if not observation.series_id or "." not in observation.series_id:
        errors.append("series_id must be namespaced, e.g. labor.unemployment.total")
    if not observation.indicator:
        errors.append("indicator is required")
    if not math.isfinite(observation.value):
        errors.append("value must be finite")
    if not observation.unit:
        errors.append("unit is required")
    if not COUNTRY.fullmatch(observation.country):
        errors.append("country must be an uppercase ISO-3 code")
    if not PERIOD.fullmatch(observation.period):
        errors.append("period must be YYYY, YYYY-MM, YYYY-Qn, YYYY-Wnn or YYYY-MM-DD")
    if observation.frequency not in FREQUENCIES:
        errors.append(f"frequency must be one of {sorted(FREQUENCIES)}")
    released = _timestamp(observation.release_time, "release_time", errors)
    retrieved = _timestamp(observation.retrieval_timestamp, "retrieval_timestamp", errors)
    vintage = _date(observation.vintage, "vintage", errors)
    if released and retrieved and released > retrieved:
        errors.append("release_time cannot be after retrieval_timestamp")
    if released and vintage and vintage < released.date():
        errors.append("vintage cannot predate release_time")
    if observation.revision < 0:
        errors.append("revision must be non-negative")
    if not observation.source:
        errors.append("source is required")
    if not _url(observation.source_url):
        errors.append("source_url must be HTTP(S)")
    if not _url(observation.source_document):
        errors.append("source_document must be HTTP(S)")
    if not observation.transformation:
        errors.append("transformation is required; use 'identity' when none")
    if not observation.license:
        errors.append("license is required")
    if observation.license_url and not _url(observation.license_url):
        errors.append("license_url must be empty or HTTP(S)")
    if not SHA256.fullmatch(observation.source_hash):
        errors.append("source_hash must be a lowercase SHA-256 digest")
    if observation.quality_status not in QUALITY:
        errors.append(f"quality_status must be one of {sorted(QUALITY)}")
    if observation.quality_status == "verified":
        if not GIT_COMMIT.fullmatch(observation.git_commit):
            errors.append("verified rows require a full 40-character Git commit")
        if observation.license.upper() in {"UNKNOWN", "TBD"}:
            errors.append("verified rows require a resolved license")
    elif observation.git_commit != "UNCOMMITTED" and not GIT_COMMIT.fullmatch(
        observation.git_commit
    ):
        errors.append("git_commit must be UNCOMMITTED or a full 40-character commit")
    if observation.observation_id and observation.observation_id != observation.identity():
        errors.append("observation_id does not match the deterministic natural-key hash")
    if errors:
        raise ValidationError(errors)
    return observation


def validate_rows(rows: Iterable[Mapping[str, Any] | Observation]) -> list[Observation]:
    validated: list[Observation] = []
    failures: list[str] = []
    for index, row in enumerate(rows, start=2):
        try:
            validated.append(validate_observation(row))
        except ValidationError as exc:
            failures.append(f"row {index}: {exc}")
    if failures:
        raise ValidationError(failures)
    return validated
