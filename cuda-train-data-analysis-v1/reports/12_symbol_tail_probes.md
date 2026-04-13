# cuda-train-data-analysis-v1 symbol tail probes

## Probe summary

| probe_name | rows_checked | rows_consistent_or_recovered | notes |
| --- | --- | --- | --- |
| numeric_broader_linear_small_coeff | 4 | 0 | a,b in [-2,2], c in [-3,3], plus min/max/avg_if_int; no safe extra recoveries |
| glyph_query_answer_consistency | 0 | 0 | query+gold preserves multiset+order constraints but remains non-unique, so rows stay manual |

## Glyph rows whose query+gold pair still fits the coarse multiset+order model

| id | hard_score | answer | query_raw | audit_reasons |
| --- | --- | --- | --- | --- |

Interpretation: these glyph rows are still not promoted because the coarse model is not unique enough to trust as supervision, even when the gold answer keeps it self-consistent.

