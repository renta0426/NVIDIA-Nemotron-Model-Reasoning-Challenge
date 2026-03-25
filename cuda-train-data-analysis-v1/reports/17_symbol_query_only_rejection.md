# cuda-train-data-analysis-v1 symbol query-only arithmetic rejection

## Purpose

Review manual `symbol_numeric_same_op` rows whose gold query answer superficially matches `x_plus_y`, `x_minus_y`, `abs_diff_2d`, or `comp99_abs_diff_2d`, and verify whether prompt evidence really makes them safe promotions.

## Decision

- rows checked: `43`
- `same_operator_examples_conflict`: `38`
- `query_format_ambiguous`: `5`
- promoted rows: `0`
- decision: keep all of these rows in `manual_audit_priority`.

## Breakdown

| query_only_matching_families | rejection_reason | rows |
| --- | --- | --- |
| comp99_abs_diff_2d | same_operator_examples_conflict | 12 |
| x_plus_y | same_operator_examples_conflict | 11 |
| abs_diff_2d\|x_minus_y | same_operator_examples_conflict | 9 |
| abs_diff_2d\|x_minus_y | query_format_ambiguous | 4 |
| abs_diff_2d | same_operator_examples_conflict | 3 |
| x_minus_y | same_operator_examples_conflict | 3 |
| abs_diff_2d | query_format_ambiguous | 1 |

## Representative rows

| id | query_raw | query_only_matching_families | rejection_reason | candidate_predictions | prompt_example_lines |
| --- | --- | --- | --- | --- | --- |
| 094bf548 | 80:32 | abs_diff_2d\|x_minus_y | query_format_ambiguous | -48\|48\|:48 | 88(64 = 8864 \|\| 27:81 = 54 \|\| 52:57 = 5 \|\| 25:81 = 56 |
| 224efda1 | 61]54 | abs_diff_2d\|x_minus_y | query_format_ambiguous | 7\|]07\|]7 | 22]67 = ]45 \|\| 39@99 = 3999 \|\| 53]91 = ]38 |
| 0641ef58 | 54-89 | x_minus_y | same_operator_examples_conflict |  | 76-68 = -91 \|\| 16-61 = -54 \|\| 39-02 = -37 \|\| 36+88 = 151 \|\| 85+12 = 97 |
| 08d8d7e1 | 65+23 | x_plus_y | same_operator_examples_conflict |  | 41+98 = 301 \|\| 94+07 = 911 \|\| 06*49 = 4906 \|\| 95*27 = 2795 |

## Full rejected slice

| id | query_raw | answer | query_only_matching_families | same_operator_example_count | candidate_prediction_count | rejection_reason |
| --- | --- | --- | --- | --- | --- | --- |
| 094bf548 | 80:32 | 48 | abs_diff_2d\|x_minus_y | 3 | 3 | query_format_ambiguous |
| 224efda1 | 61]54 | 7 | abs_diff_2d\|x_minus_y | 2 | 3 | query_format_ambiguous |
| 2beb5851 | 10[33 | 23 | abs_diff_2d | 2 | 4 | query_format_ambiguous |
| 904e3a54 | 76:10 | 66 | abs_diff_2d\|x_minus_y | 2 | 2 | query_format_ambiguous |
| f6ca90f6 | 54{23 | 31 | abs_diff_2d\|x_minus_y | 2 | 3 | query_format_ambiguous |
| d78128b2 | 73-21 | 52 | abs_diff_2d\|x_minus_y | 4 | 0 | same_operator_examples_conflict |
| df309eeb | 02%79 | 77 | abs_diff_2d | 4 | 0 | same_operator_examples_conflict |
| 0641ef58 | 54-89 | -35 | x_minus_y | 3 | 0 | same_operator_examples_conflict |
| 42d4dcf7 | 65-57 | 91 | comp99_abs_diff_2d | 3 | 0 | same_operator_examples_conflict |
| 764b4288 | 49^76 | 72 | comp99_abs_diff_2d | 3 | 0 | same_operator_examples_conflict |
| 808a8f62 | 35-72 | 62 | comp99_abs_diff_2d | 3 | 0 | same_operator_examples_conflict |
| 80d44fe3 | 65"38 | 72 | comp99_abs_diff_2d | 3 | 0 | same_operator_examples_conflict |
| 84030b0b | 36)12 | 24 | abs_diff_2d\|x_minus_y | 3 | 0 | same_operator_examples_conflict |
| 96efb93a | 95"57 | 61 | comp99_abs_diff_2d | 3 | 0 | same_operator_examples_conflict |
| 97dee6aa | 74-03 | 71 | abs_diff_2d\|x_minus_y | 3 | 0 | same_operator_examples_conflict |
| 9d7af57b | 33`56 | 89 | x_plus_y | 3 | 0 | same_operator_examples_conflict |
| bc42e664 | 47*75 | 71 | comp99_abs_diff_2d | 3 | 0 | same_operator_examples_conflict |
| 04171e29 | 97-65 | 32 | abs_diff_2d\|x_minus_y | 2 | 0 | same_operator_examples_conflict |
| 08d8d7e1 | 65+23 | 88 | x_plus_y | 2 | 0 | same_operator_examples_conflict |
| 1ee54412 | 58-85 | 72 | comp99_abs_diff_2d | 2 | 0 | same_operator_examples_conflict |
| 1f0fbe5f | 54-68 | 14 | abs_diff_2d | 2 | 0 | same_operator_examples_conflict |
| 21261dc6 | 02-27 | -25 | x_minus_y | 2 | 0 | same_operator_examples_conflict |
| 23800316 | 44]35 | 79 | x_plus_y | 2 | 0 | same_operator_examples_conflict |
| 25eb7b03 | 54#31 | 23 | abs_diff_2d\|x_minus_y | 2 | 0 | same_operator_examples_conflict |
| 26168be6 | 23+76 | 99 | x_plus_y | 2 | 0 | same_operator_examples_conflict |
| 274def88 | 85-92 | 92 | comp99_abs_diff_2d | 2 | 0 | same_operator_examples_conflict |
| 32815b79 | 34)62 | 96 | x_plus_y | 2 | 0 | same_operator_examples_conflict |
| 348d6225 | 55+43 | 98 | x_plus_y | 2 | 0 | same_operator_examples_conflict |
| 42553fde | 04?73 | 77 | x_plus_y | 2 | 0 | same_operator_examples_conflict |
| 45df54db | 56-91 | 64 | comp99_abs_diff_2d | 2 | 0 | same_operator_examples_conflict |
| 4ff92c73 | 75-38 | 62 | comp99_abs_diff_2d | 2 | 0 | same_operator_examples_conflict |
| 5e67b1a1 | 32{31 | 63 | x_plus_y | 2 | 0 | same_operator_examples_conflict |
| 75eaf687 | 79'82 | 96 | comp99_abs_diff_2d | 2 | 0 | same_operator_examples_conflict |
| 9e5d97de | 48-31 | 79 | x_plus_y | 2 | 0 | same_operator_examples_conflict |
| 9ff6e9d2 | 65-54 | 11 | abs_diff_2d\|x_minus_y | 2 | 0 | same_operator_examples_conflict |
| a7d582da | 92-41 | 51 | abs_diff_2d\|x_minus_y | 2 | 0 | same_operator_examples_conflict |
| b4a5076f | 62<13 | 75 | x_plus_y | 2 | 0 | same_operator_examples_conflict |
| c170f7d4 | 01-16 | -15 | x_minus_y | 2 | 0 | same_operator_examples_conflict |
| c613082a | 78-47 | 31 | abs_diff_2d\|x_minus_y | 2 | 0 | same_operator_examples_conflict |
| cf517124 | 03^21 | 24 | x_plus_y | 2 | 0 | same_operator_examples_conflict |
| f0a2d457 | 86<09 | 22 | comp99_abs_diff_2d | 2 | 0 | same_operator_examples_conflict |
| fc7e53c7 | 77-35 | 42 | abs_diff_2d\|x_minus_y | 2 | 0 | same_operator_examples_conflict |
| febd3442 | 64-77 | 13 | abs_diff_2d | 2 | 0 | same_operator_examples_conflict |

Interpretation: these rows look temptingly recoverable if you only inspect the query answer, but that is not enough. Most rows contradict their same-operator examples outright; the rest still leave sign, zero-pad, or complement-formatting unresolved, so using the gold answer as a tie-break would be unsafe supervision under the `README.md` accuracy regime.

