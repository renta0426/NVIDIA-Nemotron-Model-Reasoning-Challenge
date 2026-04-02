# cuda-train-data-analysis-v1 symbol `comp99_abs_diff_2d` recovery

## Purpose

Recheck `numeric_2x2` rows whose same-operator examples support the exact two-digit complement family `99 - abs(x-y)`—either as plain zero-padded digits or as operator-prefixed zero-padded digits—and split safe promotions from unsafe lookalikes under the `README.md` accuracy-first metric.

## Decision

- rows tagged with `comp99_abs_diff_2d`: `18`
- promoted to `verified_trace_ready`: `2`
- promoted to `answer_only_keep`: `14`
- still manual after exact recheck: `1`
- query-only conflicts already captured in report 17: `1`

## Breakdown

| selection_tier | symbol_same_operator_example_count | analysis_notes | rows |
| --- | --- | --- | --- |
| answer_only_keep | 1 | symbol_numeric_formula_low_shot | 9 |
| answer_only_keep | 1 | symbol_reverse_small_core_digit_answer_only | 2 |
| verified_trace_ready | 2 | symbol_numeric_formula_exact | 2 |
| answer_only_keep | 1 | symbol_reverse_manual_exact_answer_only | 1 |
| answer_only_keep | 1 | symbol_reverse_negative_x_minus_y_answer_only | 1 |
| answer_only_keep | 1 | symbol_reverse_wrapper_only_answer_only | 1 |
| exclude_suspect | 2 | symbol_audit_needed | 1 |
| manual_audit_priority | 1 | symbol_audit_needed | 1 |

## Promoted rows

| id | selection_tier | symbol_query_operator | symbol_same_operator_example_count | answer | query_raw |
| --- | --- | --- | --- | --- | --- |
| 13892a7c | answer_only_keep | - | 1 | -85 | 61-47 |
| 1bc85bd9 | answer_only_keep | - | 1 | 93 | 16-22 |
| 2049f01d | answer_only_keep | - | 1 | 23 | 52-75 |
| 33093ed0 | answer_only_keep | - | 1 | -72 | 07-79 |
| 3a8a4ebc | answer_only_keep | ' | 1 | '54 | 74'29 |
| 5c008804 | answer_only_keep | @ | 1 | 52 | 83@36 |
| 6b769a9e | answer_only_keep | + | 1 | +92 | 24+17 |
| 8d652f91 | answer_only_keep | - | 1 | 4 | 97-57 |
| c7a7b13a | answer_only_keep | - | 1 | 35 | 93-29 |
| cde9f7ba | answer_only_keep | [ | 1 | 81 | 15[33 |
| d17d3a7a | answer_only_keep | - | 1 | -01 | 66-67 |
| debff779 | answer_only_keep | - | 1 | 94 | 36-41 |
| e247d364 | answer_only_keep | ! | 1 | 11 | 65!76 |
| ef6bc241 | answer_only_keep | $ | 1 | $55 | 73$29 |
| b655eee9 | verified_trace_ready | - | 2 | -92 | 76-83 |
| cb2fdb6b | verified_trace_ready | - | 2 | 54 | 08-53 |

## Manual rows that still do not qualify

| id | symbol_same_operator_example_count | answer | query_raw | auto_solver_predicted_answer | audit_reasons |
| --- | --- | --- | --- | --- | --- |
| 34c563c5 | 1 | 04` | 45`41 | 95 | symbol_numeric_formula_unverified |

## Query-only conflict rows

| id | query_raw | answer | same_operator_example_count | rejection_reason |
| --- | --- | --- | --- | --- |
| 96efb93a | 95"57 | 61 | 3 | same_operator_examples_conflict |

Interpretation: `comp99_abs_diff_2d` is a real prompt-backed family, but only when the same-operator examples match it exactly. The family appears both as plain zero-padded digits and as operator-prefixed zero-padded digits, and it also creates many false positives in the query answer alone, so safe recovery requires exact example consistency rather than query-only fit; anything weaker stays manual.

