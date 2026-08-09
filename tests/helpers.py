from __future__ import annotations

from hashlib import sha256


def valid_row(**overrides):
    payload = {
        "series_id": "labor.unemployment.total",
        "indicator": "unemployment",
        "value": 20.0,
        "unit": "percent",
        "country": "JOR",
        "entity": "TOTAL",
        "period": "2025-Q4",
        "frequency": "quarterly",
        "release_time": "2026-02-15T08:00:00+03:00",
        "vintage": "2026-02-15",
        "revision": 0,
        "source": "Test source",
        "source_url": "https://example.org/data",
        "source_document": "https://example.org/data/release.csv",
        "retrieval_timestamp": "2026-02-15T09:00:00+03:00",
        "transformation": "identity",
        "license": "CC-BY-4.0",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "source_hash": sha256(b"source release").hexdigest(),
        "git_commit": "a" * 40,
        "quality_status": "verified",
        "notes": "",
    }
    payload.update(overrides)
    return payload
