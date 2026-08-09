# Governance

## Roles

- **Maintainer:** reviews code and schema changes; cannot self-approve a production source onboarding.
- **Source steward:** owns release calendars, source terms, adapter health and anomaly review for a source family.
- **Independent reviewer:** reproduces a sample and signs the source-onboarding checklist.
- **Data user representative:** reports usability failures and breaking-change risks.

## Two-person rule

No new source family becomes `verified` through founder-only review. One person implements the adapter; another checks an independently selected sample against the original documents.

## Change control

- Patch: parser correction or metadata clarification without semantic change.
- Minor: new source/series or backward-compatible field.
- Major: changed vintage, identity, unit or query semantics.

Schema proposals require a migration, before/after examples, compatibility statement, validation changes and a documented decision. Public corrections receive an incident ID and changelog entry.

## Neutrality

The Lab publishes methods, uncertainty and correction history. It does not suppress a valid observation because it conflicts with a preferred political or economic narrative.
