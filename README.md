# MENA Economic Terminal

Economic datasets usually give you the latest revised observation. That is a problem for forecasting: a model evaluated on today's data may be using information that did not exist when the forecast was supposedly made. This repository is my attempt to preserve the publication history of MENA macroeconomic series so that historical information sets can be reconstructed.

## Current status

**v0.2.0a1 is a completed executable software alpha.** The query, capture, provenance, validation and source-adapter machinery is versioned and frozen; regional data coverage remains an ongoing collection problem rather than a software-release blocker. See [RELEASE_STATUS.md](RELEASE_STATUS.md).

The first real source adapter is Jordanian unemployment data.

As of 10 August 2026:

- point-in-time queries exclude releases and revisions published after the requested date;
- the Q1 2026 Jordan unemployment PDF has been captured, hashed, and parsed;
- that observation is still quarantined because reuse rights are unresolved and the blind source check is unsigned;
- the repository therefore contains no public row presented as verified official data;
- CPI and policy-rate parser code exists, but those sources are not a finished regional database;
- fixtures are synthetic and appear in queries only when explicitly requested.

[RESULTS.md](RESULTS.md) records what has and has not worked. The reasoning behind the first source choices is in [notes/](notes/).

## Why vintages matter

Suppose an unemployment estimate for Q1 is released in June and revised in September. A query with a June cutoff must return the June value, even if the warehouse also contains the September revision.

```python
from menaecon import MenaClient

mena = MenaClient("./warehouse.db")
result = mena.get(
    "unemployment",
    country="JOR",
    vintage="2026-06-30",
)
```

The tests in [tests/test_vintages.py](tests/test_vintages.py) check that future releases remain invisible.

## Install the alpha

The package is not on PyPI.

```bash
python -m pip install -e .
menaecon init --database ./warehouse.db --with-fixtures
menaecon get unemployment --country JOR --vintage 2026-06-01 \
  --database ./warehouse.db --include-fixtures
```

`--include-fixtures` matters: without it, the synthetic demo rows are not returned as if they were observations.

## Adding a source

The source document is captured before it is parsed:

```bash
menaecon capture \
  "https://dosweb.dos.gov.jo/databank/News/Unemployment/2026/unemp_Q1_2026_en.pdf" \
  --source-id JOR_DOS \
  --output-dir raw/JOR_DOS/unemployment \
  --release-time "2026-06-17T12:08:09+03:00" \
  --release-time-evidence "publisher archive page timestamp"
```

The returned manifest stores the requested URL, retrieval time, content type, byte length, and SHA-256 hash. Parsing the file does not make the resulting row verified. Rights, release-time evidence, and a source-document comparison are separate checks.

## Observation fields

Each stored observation includes the value and reference period, when it was released, which vintage it belongs to, the source document, retrieval time, transformation, license note, and file hash. The full schema is in [docs/DATA_CONTRACT.md](docs/DATA_CONTRACT.md).

The main code is under [src/menaecon/](src/menaecon/); source-specific parsers are under [src/menaecon/sources/](src/menaecon/sources/); and leakage, validation, and round-trip tests are under [tests/](tests/).

## Known limitation

The rights-pending 51-cell Jordan transcription is not distributed in this repository. A 20-cell blind review packet is included, but it has not been signed by an independent reviewer. Until those questions are resolved, the Jordan row remains quarantined regardless of whether the parser passes.

See [DATA_RIGHTS.md](DATA_RIGHTS.md) and [docs/JORDAN_SOURCE_AUDIT.md](docs/JORDAN_SOURCE_AUDIT.md).
