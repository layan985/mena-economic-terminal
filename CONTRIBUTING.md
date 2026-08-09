# Contributing

Open an issue before implementing a source adapter or changing schema semantics. A source-onboarding pull request must include source terms, release-time evidence, archived fixture bytes that may legally be redistributed, expected normalized rows, adapter tests, revision tests, a random-sample audit plan and a named independent reviewer.

Run:

```bash
python -m pip install -e .
python -m unittest discover -v
```

Never commit credentials, licensed raw data, personal data or source artifacts whose redistribution terms have not been resolved. Synthetic fixtures must say `SYNTHETIC FIXTURE — NOT OFFICIAL` and use `quality_status=fixture`.
