# Research integration contracts

## Forecasting and MarketMind

Every model run must record `information_cutoff` and query only observations whose `release_time` and `vintage` are no later than that cutoff. Training matrices should retain observation IDs so a forecast can be reconstructed from exact inputs.

```python
snapshot = mena.get("inflation", country="JOR", vintage=origin_date)
```

A model that uses today's revised history in an old forecast origin is invalid even if its feature engineering is otherwise correct.

## Central-bank NLP and event studies

Policy decisions and documents are event observations. Preserve scheduled announcement time, actual publication time, document hash, language, document version and prior-release linkage. Market windows are joined on event time, never inferred from document retrieval time.

## AI and labor paper

AI-adoption evidence is an effective-dated entity event with source document, document hash, labeler version, blinded validation status and adjudication record. Employment outcomes remain separate series. The infrastructure must not silently convert the first observed mention into a causal adoption date.

## Citation bundle

Every published result should export:

- package and dataset version;
- query parameters and cutoff;
- observation IDs and source hashes;
- code commit and environment;
- applicable license/terms notices;
- release checksum.
