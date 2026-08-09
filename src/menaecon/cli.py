"""Command-line interface."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from importlib.resources import files
from pathlib import Path

from .capture import capture_url, load_manifest
from .client import MenaClient
from .sources import CbjPolicyRateAdapter, DosCpiAdapter, DosUnemploymentAdapter
from .validation import ValidationError, validate_rows


def _database(args: argparse.Namespace) -> Path:
    return Path(args.database) if args.database else Path("./menaecon.db")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="menaecon", description="MENA vintage-safe data client")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="initialize a warehouse")
    init.add_argument("--database")
    init.add_argument("--backend", choices=["auto", "sqlite", "duckdb"], default="auto")
    init.add_argument("--with-fixtures", action="store_true")

    ingest = sub.add_parser("ingest", help="validate and append a CSV")
    ingest.add_argument("path")
    ingest.add_argument("--database")
    ingest.add_argument("--backend", choices=["auto", "sqlite", "duckdb"], default="auto")
    ingest.add_argument("--allow-fixtures", action="store_true")

    get = sub.add_parser("get", help="point-in-time query")
    get.add_argument("indicator")
    get.add_argument("--country", required=True)
    get.add_argument("--vintage", required=True)
    get.add_argument("--series-id")
    get.add_argument("--entity")
    get.add_argument("--database")
    get.add_argument("--backend", choices=["auto", "sqlite", "duckdb"], default="auto")
    get.add_argument("--include-fixtures", action="store_true")
    get.add_argument("--format", choices=["json", "csv"], default="json")

    validate = sub.add_parser("validate", help="validate a CSV without ingesting")
    validate.add_argument("path")

    capture = sub.add_parser("capture", help="immutably capture and quarantine a source URL")
    capture.add_argument("url")
    capture.add_argument("--source-id", required=True)
    capture.add_argument("--output-dir", required=True)
    capture.add_argument("--release-time", required=True)
    capture.add_argument("--release-time-evidence", required=True)
    capture.add_argument("--license", default="TBD")
    capture.add_argument("--license-url", default="")
    capture.add_argument("--license-evidence", default="rights review pending")

    parse = sub.add_parser("parse-jordan", help="parse a quarantined Jordan source artifact")
    parse.add_argument("manifest")
    parse.add_argument(
        "--adapter",
        choices=["dos-unemployment", "dos-cpi", "cbj-policy-rate"],
        required=True,
    )
    parse.add_argument("--database")
    parse.add_argument("--backend", choices=["auto", "sqlite", "duckdb"], default="auto")

    sub.add_parser("catalog", help="print the bundled alpha series catalog")
    sub.add_parser("sources", help="print the bundled source-onboarding registry")
    sub.add_parser("release-calendar", help="print observed source release behavior")
    sub.add_parser("jordan-discovery", help="print non-warehouse Jordan source discoveries")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "init":
            client = MenaClient(_database(args), backend=args.backend)
            inserted = 0
            if args.with_fixtures:
                fixture = files("menaecon.resources").joinpath("sample_observations.csv")
                inserted = client.warehouse.ingest_csv(fixture, allow_fixtures=True)
            print(json.dumps({"database": str(client.database), "fixture_rows": inserted}))
        elif args.command == "ingest":
            client = MenaClient(_database(args), backend=args.backend)
            inserted = client.warehouse.ingest_csv(args.path, allow_fixtures=args.allow_fixtures)
            print(json.dumps({"inserted": inserted}))
        elif args.command == "get":
            client = MenaClient(_database(args), backend=args.backend)
            result = client.get(
                args.indicator,
                country=args.country,
                vintage=args.vintage,
                series_id=args.series_id,
                entity=args.entity,
                include_fixtures=args.include_fixtures,
            )
            if args.format == "json":
                print(result.to_json())
            elif result.rows:
                writer = csv.DictWriter(sys.stdout, fieldnames=list(result.rows[0]))
                writer.writeheader()
                writer.writerows(result.rows)
        elif args.command == "validate":
            with Path(args.path).open(newline="", encoding="utf-8") as handle:
                rows = validate_rows(csv.DictReader(handle))
            print(json.dumps({"valid_rows": len(rows)}))
        elif args.command == "capture":
            artifact, manifest = capture_url(
                args.url,
                args.output_dir,
                source_id=args.source_id,
                release_time=args.release_time,
                release_time_evidence=args.release_time_evidence,
                license=args.license,
                license_url=args.license_url,
                license_evidence=args.license_evidence,
            )
            print(
                json.dumps(
                    {
                        "artifact": str(artifact.path),
                        "manifest": str(manifest),
                        "sha256": artifact.sha256,
                        "quality_status": artifact.quality_status,
                    }
                )
            )
        elif args.command == "parse-jordan":
            adapters = {
                "dos-unemployment": DosUnemploymentAdapter,
                "dos-cpi": DosCpiAdapter,
                "cbj-policy-rate": CbjPolicyRateAdapter,
            }
            artifact = load_manifest(args.manifest)
            rows = list(adapters[args.adapter]().parse(artifact))
            client = MenaClient(_database(args), backend=args.backend)
            inserted = client.warehouse.ingest(rows)
            print(
                json.dumps(
                    {
                        "inserted": inserted,
                        "quality_status": artifact.quality_status,
                        "source_hash": artifact.sha256,
                    }
                )
            )
        elif args.command in {"catalog", "sources", "release-calendar", "jordan-discovery"}:
            filenames = {
                "catalog": "series_catalog.csv",
                "sources": "source_registry.csv",
                "release-calendar": "release_calendar.csv",
                "jordan-discovery": "jordan_source_discovery.csv",
            }
            filename = filenames[args.command]
            print(files("menaecon.resources").joinpath(filename).read_text(encoding="utf-8"), end="")
        return 0
    except (ValidationError, ValueError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
