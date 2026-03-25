# cuda-train-data-analysis-v1 symbol `comp99_abs_diff_2d` recovery

## Purpose

Recheck `numeric_2x2` rows whose same-operator examples support the exact two-digit complement family `99 - abs(x-y)`—either as plain zero-padded digits or as operator-prefixed zero-padded digits—and split safe promotions from unsafe lookalikes under the `README.md` accuracy-first metric.

## Decision

- rows tagged with `comp99_abs_diff_2d`: `18`
- promoted to `verified_trace_ready`: `2`
- promoted to `answer_only_keep`: `9`
- still manual after exact recheck: `6`
- query-only conflicts already captured in report 17: `12`

## Breakdown

| selection_tier | symbol_same_operator_example_count | analysis_notes | rows |
| --- | --- | --- | --- |
| answer_only_keep | 1 | symbol_numeric_formula_low_shot | 9 |
| manual_audit_priority | 1 | symbol_audit_needed | 6 |
| verified_trace_ready | 2 | symbol_numeric_formula_exact | 2 |
| exclude_suspect | 2 | symbol_audit_needed | 1 |

## Promoted rows

| id | selection_tier | symbol_query_operator | symbol_same_operator_example_count | answer | query_raw |
| --- | --- | --- | --- | --- | --- |
| 13892a7c | answer_only_keep | - | 1 | -85 | 61-47 |
| 1bc85bd9 | answer_only_keep | - | 1 | 93 | 16-22 |
| 3a8a4ebc | answer_only_keep | ' | 1 | '54 | 74'29 |
| 5c008804 | answer_only_keep | @ | 1 | 52 | 83@36 |
| 6b769a9e | answer_only_keep | + | 1 | +92 | 24+17 |
| c7a7b13a | answer_only_keep | - | 1 | 35 | 93-29 |
| cde9f7ba | answer_only_keep | [ | 1 | 81 | 15[33 |
| debff779 | answer_only_keep | - | 1 | 94 | 36-41 |
| ef6bc241 | answer_only_keep | $ | 1 | $55 | 73$29 |
| b655eee9 | verified_trace_ready | - | 2 | -92 | 76-83 |
| cb2fdb6b | verified_trace_ready | - | 2 | 54 | 08-53 |

## Manual rows that still do not qualify

| id | symbol_same_operator_example_count | answer | query_raw | auto_solver_predicted_answer | audit_reasons |
| --- | --- | --- | --- | --- | --- |
| 2049f01d | 1 | 23 | 52-75 | 76 | symbol_numeric_formula_unverified |
| 33093ed0 | 1 | -72 | 07-79 | 27 | symbol_numeric_formula_unverified |
| 34c563c5 | 1 | 04` | 45`41 | 95 | symbol_numeric_formula_unverified |
| 8d652f91 | 1 | 4 | 97-57 | 59 | symbol_numeric_formula_unverified |
| d17d3a7a | 1 | -01 | 66-67 | 98 | symbol_numeric_formula_unverified |
| e247d364 | 1 | 11 | 65!76 | 88 | symbol_numeric_formula_unverified |

## Query-only conflict rows

| id | query_raw | answer | same_operator_example_count | rejection_reason |
| --- | --- | --- | --- | --- |
| 42d4dcf7 | 65-57 | 91 | 3 | same_operator_examples_conflict |
| 764b4288 | 49^76 | 72 | 3 | same_operator_examples_conflict |
| 808a8f62 | 35-72 | 62 | 3 | same_operator_examples_conflict |
| 80d44fe3 | 65"38 | 72 | 3 | same_operator_examples_conflict |
| 96efb93a | 95"57 | 61 | 3 | same_operator_examples_conflict |
| bc42e664 | 47*75 | 71 | 3 | same_operator_examples_conflict |
| 1ee54412 | 58-85 | 72 | 2 | same_operator_examples_conflict |
| 274def88 | 85-92 | 92 | 2 | same_operator_examples_conflict |
| 45df54db | 56-91 | 64 | 2 | same_operator_examples_conflict |
| 4ff92c73 | 75-38 | 62 | 2 | same_operator_examples_conflict |
| 75eaf687 | 79'82 | 96 | 2 | same_operator_examples_conflict |
| f0a2d457 | 86<09 | 22 | 2 | same_operator_examples_conflict |

Interpretation: `comp99_abs_diff_2d` is a real prompt-backed family, but only when the same-operator examples match it exactly. The family appears both as plain zero-padded digits and as operator-prefixed zero-padded digits, and it also creates many false positives in the query answer alone, so safe recovery requires exact example consistency rather than query-only fit; anything weaker stays manual.

