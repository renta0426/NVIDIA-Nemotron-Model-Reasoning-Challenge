# cuda-train-data-analysis-v1 symbol tail probes

## Probe summary

| probe_name | rows_checked | rows_consistent_or_recovered | notes |
| --- | --- | --- | --- |
| numeric_broader_linear_small_coeff | 4 | 0 | a,b in [-2,2], c in [-3,3], plus min/max/avg_if_int; no safe extra recoveries |
| glyph_query_answer_consistency | 0 | 0 | query+gold preserves multiset+order constraints but remains non-unique, so this probe does not create trace-safe promotions; the latest broad pass instead keeps the non-suspect residual rows as answer-only labels |

## Glyph rows whose query+gold pair still fits the coarse multiset+order model

| id | hard_score | answer | query_raw | audit_reasons |
| --- | --- | --- | --- | --- |

Interpretation: these glyph rows are still not promoted to `verified_trace_ready` because the coarse model is not unique enough to trust as supervision, even when the gold answer keeps it self-consistent. Under the latest accuracy-first policy they may still be retained as `answer_only_keep`, but not as trace teachers.
