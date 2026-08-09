# Jordan independent-review packet

## Reviewer instructions

The reviewer must not be the adapter author. Sample rows after parsing, then work from each row back to the original source document without using the normalized value as a cue where practical.

For each source family, select at least 20 observations or all observations if fewer exist. Record:

| Field | Required check |
| --- | --- |
| Source identity | Publisher and exact document match the registry |
| Value | Numeric value matches the original artifact |
| Concept | Population, adjustment, unit and transformation match |
| Period | Reference period is not confused with publication date |
| Release time | Timestamp evidence is retained and timezone is correct |
| Revision | Later source updates append rather than overwrite |
| Hash | Artifact bytes reproduce the manifest SHA-256 |
| Rights | Storage and redistribution follow recorded terms |

## Review record template

```text
reviewer_name:
reviewer_affiliation:
reviewer_contact:
source_id:
adapter_commit:
sample_seed:
population_size:
sample_size:
value_matches:
concept_matches:
period_matches:
release_time_matches:
exceptions:
decision: approve | reject | approve_with_documented_limits
signed_at:
```

## Automatic rejection conditions

- Author reviewed their own adapter.
- Sample selection was changed after mismatches were observed.
- Population scope is missing or inferred.
- Exact source bytes cannot reproduce the stored hash.
- License/terms remain `TBD`.
- Any exception was silently corrected without a retained audit trail.
