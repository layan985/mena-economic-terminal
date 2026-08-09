# Source strategy

The bundled source registry is an onboarding queue, not a declaration that every listed source has been ingested or may be redistributed.

## Source hierarchy

1. National statistical office, central bank, regulator, exchange or filing authority.
2. Official international harmonizer with preserved original definitions.
3. Licensed market/data provider with redistribution constraints represented in access policy.
4. Primary company filing or policy document.
5. Secondary source only when the primary source is unavailable and the limitation is explicit.

## Vintage classes

| Class | Meaning | Permitted use |
| --- | --- | --- |
| Native vintage | Publisher exposes historical releases/snapshots | Real-time research after release-time audit |
| Captured vintage | Lab begins prospective immutable captures | Real-time research only from first verified capture forward |
| Reconstructed | Historical document archive rebuilt after the fact | Allowed with reconstruction flag and uncertainty |
| Current only | Only latest value is available | Descriptive use; excluded from pseudo-real-time claims |

## First source families

- Central Bank of Jordan statistical database and monetary releases.
- Jordan Department of Statistics labor and CPI releases.
- ILOSTAT harmonized labor layer.
- UN Comtrade trade data with reporter/classification/estimation metadata intact.
- World Bank and IMF layers for cross-country comparison, labeled separately from national releases.

No adapter is promoted from `source_discovery` until access terms, vintage behavior, release time and document retention are reviewed.
