# cuda-train-data-analysis-v1 symbol tail probes

## Probe summary

| probe_name | rows_checked | rows_consistent_or_recovered | notes |
| --- | --- | --- | --- |
| numeric_broader_linear_small_coeff | 180 | 0 | a,b in [-2,2], c in [-3,3], plus min/max/avg_if_int; no safe extra recoveries |
| glyph_query_answer_consistency | 823 | 5 | query+gold preserves multiset+order constraints but remains non-unique, so rows stay manual |

## Glyph rows whose query+gold pair still fits the coarse multiset+order model

| id | hard_score | answer | query_raw | audit_reasons |
| --- | --- | --- | --- | --- |
| f4f92956 | 7.0 | (`)) | ()"%} | symbol_length_mismatch\|symbol_solver_unverified |
| 64553a64 | 5.0 | }#' | !@"`/ | symbol_length_mismatch\|symbol_solver_unverified |
| 97abca56 | 5.0 | `#:: | (:*`' | symbol_length_mismatch\|symbol_solver_unverified |
| a77be9fa | 5.0 | [" | {>\|$[ | symbol_length_mismatch\|symbol_solver_unverified |
| afdb7326 | 5.0 | %\ | @^%(^ | symbol_length_mismatch\|symbol_solver_unverified |

Interpretation: these glyph rows are still not promoted because the coarse model is not unique enough to trust as supervision, even when the gold answer keeps it self-consistent.

