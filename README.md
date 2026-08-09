# MENA Economic Observatory / Terminal

> **Research portfolio:** [layanaloreidi.online](https://layanaloreidi.online)

> **Portfolio case study:** [Contribution, public proof, claim boundaries and the next external-validation gate](docs/PORTFOLIO_CASE_STUDY.md).


The **MENA Economic Observatory / Terminal** is the public economic-data infrastructure of the **MENA Open Data & Evidence Lab**. It is designed to preserve what researchers could have known at a particular point in time—not merely the latest revised number.

This repository is an executable **v0.2.0a1 alpha**, not a claim that the regional database is already complete. It includes the canonical observation contract, a vintage-safe query engine, immutable capture tooling, strict Jordan source adapters, provenance gates, a CLI, an optional API, synthetic fixtures, tests, and the source-onboarding roadmap. No fixture, discovery or quarantined row is presented as verified official data.

## What works now

- Immutable, append-only observations with release time, vintage, revision and source hash.
- Point-in-time queries that exclude future releases and revisions.
- Python API matching the intended public interface.
- Command-line initialization, ingestion, validation, querying and catalog inspection.
- SQLite zero-dependency backend; optional DuckDB backend for analytical workloads.
- Row-level validation and quarantine-ready quality status.
- Machine-readable indicator catalog, source registry and JSON Schema.
- Content-addressed HTTP capture with SHA-256 manifests and quarantine by default.
- Strict Jordan DoS unemployment/CPI and CBJ policy-rate parsers.
- Machine-readable Jordan release-calendar audit and discovery ledger.
- Exact Q1 2026 Jordan DoS unemployment PDF capture receipt and successful real-parser result.
- A 51-cell retrospective chart transcription retained outside the public tree while reuse rights are unresolved, plus a frozen 20-cell blind review packet.
- Independent-audit scorer that rejects self-review and incomplete signatures.
- Synthetic Jordan unemployment fixture for reproducible tests and demos.
- Release gates that prevent fixtures, unlicensed material or incomplete provenance from entering a public release.

## Quick start

The package is not yet published to PyPI. Install this alpha from the repository:

```bash
python -m pip install -e .
menaecon init --database ./warehouse.db --with-fixtures
menaecon get unemployment --country JOR --vintage 2026-06-01 \
  --database ./warehouse.db --include-fixtures
```

Python:

```python
from menaecon import MenaClient

mena = MenaClient("./warehouse.db")
result = mena.get(
    "unemployment",
    country="JOR",
    vintage="2026-06-01",
)
print(result.to_dicts())
```

## Jordan source-onboarding workflow

Capture the exact publisher bytes before parsing. The capture is deliberately quarantined:

```bash
menaecon capture \
  "https://dosweb.dos.gov.jo/databank/News/Unemployment/2026/unemp_Q1_2026_en.pdf" \
  --source-id JOR_DOS \
  --output-dir raw/JOR_DOS/unemployment \
  --release-time "2026-06-17T12:08:09+03:00" \
  --release-time-evidence "publisher archive page timestamp"
```

Then parse the returned manifest:

```bash
menaecon parse-jordan raw/JOR_DOS/unemployment/ARTIFACT.pdf.manifest.json \
  --adapter dos-unemployment \
  --database warehouse.db
```

Parsing does **not** promote the observation to `verified`. Rights review, exact release-time evidence, independent source-document comparison and row-level Git provenance must be completed separately. Quarantined rows never appear in ordinary `get()` results.

The intended stable interface after the publication gates are satisfied is:

```python
from menaecon import mena

mena.get("unemployment", country="JOR", vintage="2026-06-01")
```

## The observation contract

Every observation must carry:

```text
value · country · entity · period · release_time · vintage · revision
source · source_document · retrieval_timestamp · transformation · license
source_hash · git_commit
```

The contract also requires a stable `series_id`, unit, frequency and explicit quality status. See [docs/DATA_CONTRACT.md](docs/DATA_CONTRACT.md).

## Why the vintage model matters

For each period, `get(..., vintage="2026-06-01")` returns the most recent release available by that cutoff. A revision released on June 15 is invisible to the query. This invariant is tested and is the foundation for honest rolling-origin forecasting, central-bank event studies and policy-shock measurement.

## Repository map

| Path | Purpose |
| --- | --- |
| `src/menaecon/` | Client, warehouse, capture, source adapters, validation, CLI and API |
| `src/menaecon/resources/` | Fixture, catalog, source registry and JSON Schema |
| `docs/` | Architecture, provenance, governance, gates and roadmap |
| `tests/` | No-leakage, revision, validation and round-trip tests |
| `scripts/verify_release.py` | Public-release blocker |
| `DATA_RIGHTS.md` | Boundary between MIT-licensed software and third-party data |

## Non-negotiable publication rule

An observation cannot be released as `verified` unless the source artifact is retained or its permitted canonical URL is recorded; the artifact hash is checked; retrieval time is preserved; license status is explicit; the transformation is reproducible; and the exact Git commit is attached. The release verifier fails if any public export contains fixture or quarantined rows.

## Project status

`v0.2.0a1`: first exact Jordan source capture. The Q1 2026 unemployment PDF is hashed and the real parser passes. Software and capture provenance are anchored to commit `29e916ca3350ba748f30022e0353f35de210121b`, but the official observation remains quarantined because reuse permission is unresolved and the 20-cell external audit is unsigned. The rights-pending 51-cell transcription is not distributed in the public tree. See [DATA_RIGHTS.md](DATA_RIGHTS.md) and [docs/JORDAN_SOURCE_AUDIT.md](docs/JORDAN_SOURCE_AUDIT.md).
