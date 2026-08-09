# Release gates

## Gate A — source legality and identity

- Canonical publisher and dataset identified.
- Access and redistribution terms recorded by dataset, not guessed from the institution.
- Entity, unit and methodology definitions archived.
- Release calendar and timezone behavior documented.

## Gate B — technical provenance

- Raw artifact or permitted canonical reference retained.
- SHA-256 verified before parse.
- Retrieval timestamp and request parameters preserved.
- Adapter deterministic under a clean rerun.

## Gate C — economic validity

- Units, scaling, seasonal adjustment and nominal/real status checked.
- At least 20 randomly selected observations compared with source documents.
- Revision behavior and historical-vintage availability tested.
- Cross-source differences explained rather than averaged away.

## Gate D — independence

- Non-author reviewer reruns ingestion.
- Reviewer signs sample comparison and no-leakage test.
- Known failures and coverage gaps are public.

## Gate E — public release

- Zero `fixture` or `quarantined` rows in release export.
- Zero unresolved license values.
- Full Git commit on every row.
- Checksums, changelog, schema, catalog and citation metadata included.
- Frozen version tag and DOI archive created only after all prior gates pass.
