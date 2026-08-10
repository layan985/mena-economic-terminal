# MENA Economic Terminal v0.2.0a1

Frozen from the public default branch on 10 August 2026.

This is a **completed executable alpha software release**. It is not a claim that regional data coverage is complete.

## Alpha release contract

The alpha includes:

- vintage-safe point-in-time queries that exclude future releases and revisions;
- immutable source capture with retrieval metadata and SHA-256 hashes;
- SQLite-backed storage and query interfaces;
- CLI and Python client interfaces;
- source registry, series catalog and machine-readable data contracts;
- Jordan unemployment/CPI/policy-rate source-adapter code;
- strict validation and quarantine states;
- automated tests for vintage leakage, validation, capture and round trips;
- a release verifier that prevents fixture/quarantined rows from being presented as verified public observations.

## Data maturity boundary

The first real Jordan unemployment source has been captured and parsed, but its observation remains quarantined while redistribution rights and independent source review are unresolved. Synthetic fixtures remain explicitly marked and cannot enter ordinary verified-data queries.

Therefore the accurate status is:

- **software alpha: complete and frozen**;
- **Jordan source onboarding: technically parsed, verification/rights pending**;
- **regional database coverage: ongoing**.

External rights determinations and an independent reviewer cannot be manufactured by the producing analyst; they remain separate release gates rather than reasons to describe the software alpha itself as unfinished.
