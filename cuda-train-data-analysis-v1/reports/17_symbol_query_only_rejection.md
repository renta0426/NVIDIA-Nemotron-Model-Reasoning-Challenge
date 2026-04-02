# cuda-train-data-analysis-v1 symbol query-only arithmetic rejection

## Purpose

Review manual `symbol_numeric_same_op` rows whose gold query answer superficially matches `x_plus_y`, `x_minus_y`, `abs_diff_2d`, or `comp99_abs_diff_2d`, and verify whether prompt evidence really makes them safe promotions.

## Decision

- rows checked: `1`
- `same_operator_examples_conflict`: `1`
- `query_format_ambiguous`: `0`
- promoted rows: `0`
- decision: keep all of these rows in `manual_audit_priority`.

## Breakdown

| query_only_matching_families | rejection_reason | rows |
| --- | --- | --- |
| comp99_abs_diff_2d | same_operator_examples_conflict | 1 |

## Representative rows

| id | query_raw | query_only_matching_families | rejection_reason | candidate_predictions | prompt_example_lines |
| --- | --- | --- | --- | --- | --- |

## Full rejected slice

| id | query_raw | answer | query_only_matching_families | same_operator_example_count | candidate_prediction_count | rejection_reason |
| --- | --- | --- | --- | --- | --- | --- |
| 96efb93a | 95"57 | 61 | comp99_abs_diff_2d | 3 | 0 | same_operator_examples_conflict |

Interpretation: these rows look temptingly recoverable if you only inspect the query answer, but that is not enough. Most rows contradict their same-operator examples outright; the rest still leave sign, zero-pad, or complement-formatting unresolved, so using the gold answer as a tie-break would be unsafe supervision under the `README.md` accuracy regime.

