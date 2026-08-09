"""Optional read-only HTTP API. Install the `api` extra to use it."""

from __future__ import annotations

import os

from .client import MenaClient


def create_app(database: str | None = None):
    try:
        from fastapi import FastAPI, HTTPException
    except ImportError as exc:
        raise RuntimeError("Install with `pip install menaecon[api]`") from exc

    client = MenaClient(database or os.environ.get("MENAEON_DATABASE"))
    app = FastAPI(title="MENA Economic Observatory API", version="0.1.0")

    @app.get("/health")
    def health():
        return {"status": "ok", "counts": client.warehouse.count_by_status()}

    @app.get("/v1/observations/{indicator}")
    def observations(indicator: str, country: str, vintage: str, series_id: str | None = None):
        try:
            result = client.get(
                indicator, country=country, vintage=vintage, series_id=series_id
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return {
            "indicator": indicator,
            "country": country.upper(),
            "vintage": vintage,
            "count": len(result),
            "data": result.to_dicts(),
        }

    return app
