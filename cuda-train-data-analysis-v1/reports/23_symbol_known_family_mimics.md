# cuda-train-data-analysis-v1 symbol known-family mimic audit

## Purpose

Collect the full union of query-only and known-family mimic rows so round2 can deprioritize these dead ends before operator-specific manual reading.

## Scope

- total mimic-union rows: `67`
- sources: report 17 high-shot arithmetic lookalikes + extra known-family / low-shot mimic rows

## Breakdown

| query_only_matching_families | rejection_reason | rows |
| --- | --- | --- |
| abs_diff_2d | low_shot_format_ambiguous | 16 |
| comp99_abs_diff_2d | same_operator_examples_conflict | 12 |
| x_plus_y | same_operator_examples_conflict | 11 |
| abs_diff_2d\|x_minus_y | same_operator_examples_conflict | 9 |
| abs_diff_2d | low_shot_example_conflict | 4 |
| abs_diff_2d\|x_minus_y | query_format_ambiguous | 4 |
| abs_diff_2d | same_operator_examples_conflict | 3 |
| x_minus_y | same_operator_examples_conflict | 3 |
| abs_diff_2d_op_suffix | low_shot_example_conflict | 2 |
| abs_diff_2d_op_suffix | same_operator_examples_conflict | 2 |
| abs_diff_2d | query_format_ambiguous | 1 |

## Source split

- report 17 rows: `43`
- extra known-family rows (union minus report 17): `24`

## Interpretation

- high-shot rows can still be wrong because same-op examples conflict or leave format unresolved.
- low-shot rows can still be wrong because one example is not enough to prove the intended format, even if the query answer looks familiar.
- the union now also absorbs the new `comp99_abs_diff_2d` dead-end lookalikes, so excluding it from the round2 reading list keeps the residual cluster map focused on the true unknown core.

