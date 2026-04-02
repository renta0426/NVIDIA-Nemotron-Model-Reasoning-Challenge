# cuda-train-data-analysis-v1 symbol operator audit notes

## Symbol numeric operator summary

| template_subtype | symbol_query_operator | selection_tier | symbol_numeric_formula_name | rows |
| --- | --- | --- | --- | --- |
| glyph_len5 |  | answer_only_keep |  | 823 |
| numeric_2x2 | + | answer_only_keep |  | 89 |
| numeric_2x2 | * | answer_only_keep |  | 73 |
| numeric_2x2 | - | answer_only_keep |  | 72 |
| numeric_2x2 | / | answer_only_keep |  | 15 |
| numeric_2x2 | @ | answer_only_keep |  | 15 |
| numeric_2x2 | : | answer_only_keep |  | 14 |
| numeric_2x2 | % | answer_only_keep |  | 13 |
| numeric_2x2 | [ | answer_only_keep |  | 13 |
| numeric_2x2 | ` | answer_only_keep |  | 12 |
| numeric_2x2 | { | answer_only_keep |  | 12 |
| numeric_2x2 | $ | answer_only_keep |  | 11 |
| numeric_2x2 | + | answer_only_keep | concat_yx | 11 |
| numeric_2x2 | - | manual_audit_priority |  | 11 |
| numeric_2x2 | ^ | answer_only_keep |  | 11 |
| numeric_2x2 | ! | answer_only_keep |  | 10 |
| numeric_2x2 | ) | answer_only_keep |  | 10 |
| numeric_2x2 | \ | answer_only_keep |  | 10 |
| numeric_2x2 | " | answer_only_keep |  | 9 |
| numeric_2x2 | + | verified_trace_ready | concat_yx | 9 |
| numeric_2x2 | < | answer_only_keep |  | 9 |
| numeric_2x2 | } | answer_only_keep |  | 9 |
| numeric_2x2 | # | answer_only_keep |  | 8 |
| numeric_2x2 | - | answer_only_keep | comp99_abs_diff_2d | 8 |
| numeric_2x2 | ] | answer_only_keep |  | 8 |
| numeric_2x2 | & | answer_only_keep |  | 7 |
| numeric_2x2 | * | answer_only_keep | concat_yx | 7 |
| numeric_2x2 | > | answer_only_keep |  | 7 |
| numeric_2x2 | * | verified_trace_ready | concat_yx | 6 |
| numeric_2x2 | ? | answer_only_keep |  | 6 |
| numeric_2x2 | \| | answer_only_keep |  | 6 |
| numeric_2x2 | ' | answer_only_keep |  | 5 |
| numeric_2x2 | - | answer_only_keep | abs_diff_2d | 5 |
| numeric_2x2 | - | answer_only_keep | x_minus_y | 5 |
| numeric_2x2 | ( | answer_only_keep |  | 4 |
| numeric_2x2 | ( | verified_trace_ready | x_minus_y | 3 |
| numeric_2x2 | * | exclude_suspect | x_plus_y | 3 |
| numeric_2x2 | + | answer_only_keep | x_plus_y | 3 |
| numeric_2x2 | - | verified_trace_ready | x_minus_y | 3 |
| numeric_2x2 | ? | verified_trace_ready | concat_xy | 3 |

## Glyph multiset summary

| glyph_multiset_possible | glyph_order_acyclic | selection_tier | rows |
| --- | --- | --- | --- |
| False | False | answer_only_keep | 378 |
| False | True | answer_only_keep | 375 |
| True | True | answer_only_keep | 46 |
| True | False | answer_only_keep | 24 |

## Top symbol manual-audit queue

| id | template_subtype | symbol_query_operator | symbol_same_operator_example_count | hard_score | answer | query_raw |
| --- | --- | --- | --- | --- | --- | --- |
| 96efb93a | numeric_2x2 | " | 3 | 1.0 | 61 | 95"57 |
| 3b2e0cc3 | numeric_2x2 | - | 2 | 3.0 | 8 | 57-38 |
| 00d8b3db | numeric_2x2 | / | 2 | 2.0 | 17/ | 69/52 |
| 58fed63a | numeric_2x2 | - | 2 | 2.0 | 5 | 11-39 |
| 34c563c5 | numeric_2x2 | ` | 1 | 5.0 | 04` | 45`41 |
| 45076dc9 | numeric_2x2 | } | 1 | 5.0 | 6 | 56}17 |
| 07cbed38 | numeric_2x2 | } | 1 | 4.0 | 93 | 52}51 |
| 64fe405e | numeric_2x2 | < | 1 | 3.0 | 1 | 32<33 |
| 12d4a2df | numeric_2x2 | - | 1 | 2.0 | -6 | 68-08 |
| 1b6366af | numeric_2x2 | ! | 1 | 2.0 | 03! | 65!68 |
| 74fff108 | numeric_2x2 | ^ | 1 | 2.0 | 49 | 65^16 |
| 8373daa8 | numeric_2x2 | - | 1 | 2.0 | 84 | 08-23 |
| c11777c0 | numeric_2x2 | ? | 1 | 2.0 | 56 | 22?34 |
| e102a09d | numeric_2x2 | - | 1 | 2.0 | -02 | 42-44 |
| 2afebbc3 | numeric_2x2 | / | 1 | 1.0 | 16 | 18/52 |
| 49919931 | numeric_2x2 | * | 1 | 1.0 | 32 | 42*59 |
| 50adfd54 | numeric_2x2 | - | 1 | 1.0 | -75 | 42-18 |
| 87711597 | numeric_2x2 | ! | 1 | 1.0 | 01 | 49!82 |
| 891942ba | numeric_2x2 | - | 1 | 1.0 | 03 | 85-88 |
| 91b34547 | numeric_2x2 | - | 1 | 1.0 | -84 | 26-41 |
| 92471ca4 | numeric_2x2 | - | 1 | 1.0 | 36 | 02-38 |
| 9d68ef62 | numeric_2x2 | ( | 1 | 1.0 | 83( | 69(85 |
| db5a5b71 | numeric_2x2 | " | 1 | 1.0 | 31 | 58"42 |
| e2bb1d9f | numeric_2x2 | - | 1 | 1.0 | -91 | 03-94 |
| eb68289b | numeric_2x2 | - | 1 | 1.0 | -82 | 72-55 |

Observation: `numeric_2x2` is not one template; it splits by operator, and some operators are already recoverable with row-local formula search. For `glyph_len5`, the latent mapping often remains structurally unresolved, so the remaining non-suspect rows are kept only as answer-only training labels rather than trace-ready teachers.
