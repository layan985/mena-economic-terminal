# Canonical data contract

## Required fields

| Field | Rule |
| --- | --- |
| `observation_id` | Deterministic SHA-256 of the natural identity; computed on ingest |
| `series_id` | Stable namespaced identifier; title changes never change this ID |
| `indicator` | Human-queryable family such as `unemployment` |
| `value` | Finite numeric value; missing values are represented by absence plus coverage metadata |
| `unit` | Explicit canonical unit |
| `country` | ISO-3 uppercase code |
| `entity` | `TOTAL`, firm ID, security ID, commodity or another typed entity |
| `period` | Canonical reference period |
| `frequency` | Daily, weekly, monthly, quarterly, annual or event |
| `release_time` | Timezone-aware publication time |
| `vintage` | Date of the captured information set |
| `revision` | Non-negative revision sequence within the source release lineage |
| `source` | Publishing institution or documented primary source |
| `source_url` | Canonical publisher location |
| `source_document` | Exact release, filing, response or artifact location |
| `retrieval_timestamp` | Timezone-aware capture time |
| `transformation` | `identity` or a reproducible named formula |
| `license` | Explicit rights/terms label; never silently assumed |
| `license_url` | Terms or license location, when available |
| `source_hash` | SHA-256 of the exact source artifact/response |
| `git_commit` | Full 40-character commit that produced a verified row |
| `quality_status` | `fixture`, `verified` or `quarantined` |
| `notes` | Material qualifications; empty when none |

## Invariants

- `release_time <= retrieval_timestamp`.
- `vintage >= date(release_time)`.
- Verified rows require a full Git commit and resolved license.
- Revisions append; they never mutate prior values.
- Each raw source artifact is hashed before parsing.
- Every transformed value names its transformation and retains parent lineage in production.
- Estimates, seasonal adjustments and source-supplied imputations must be carried as quality dimensions, not discarded.

## Missingness

Do not encode unavailable values as zero, empty string or a fabricated numeric sentinel. Coverage tables record why a series-period is absent: not released, not collected, suppressed, not applicable, parsing failure or licensing restriction.

## Firm and person entities

Canonical IDs must be separate from labels. Names are time-varying aliases. Ownership relationships have effective dates, source documents and confidence; they are not columns overwritten with a current owner.
