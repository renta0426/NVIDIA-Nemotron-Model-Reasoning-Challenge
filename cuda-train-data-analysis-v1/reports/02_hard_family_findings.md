# cuda-train-data-analysis-v1 hard-family findings

## Binary

| template_subtype | bit_simple_family | bit_independent_unique | bit_bijection_unique | bit_boolean2_unique | bit_boolean3_unique | bit_affine_unique | bit_byte_transform_unique | teacher_solver_candidate | rows |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bit_other | unknown | False | False | False | False | False | False |  | 1063 |
| bit_other | unknown | False | False | False | False | True | False |  | 138 |
| bit_other | unknown | False | False | False | False | True | False | binary_affine_xor | 128 |
| bit_other | unknown | False | False | True | False | True | False | binary_two_bit_boolean | 62 |
| bit_other | unknown | False | False | True | False | False | False | binary_two_bit_boolean | 57 |
| bit_permutation_inversion | unknown | True | True | False | False | False | False | binary_bit_permutation_bijection | 25 |
| bit_permutation_inversion | unknown | True | True | False | False | True | False | binary_bit_permutation_bijection | 11 |
| bit_other | unknown | False | False | False | True | False | False | binary_three_bit_boolean | 9 |
| bit_permutation_inversion | unknown | False | False | False | False | False | False |  | 9 |
| bit_other | rshift | False | False | False | False | False | True | binary_byte_transform | 7 |
| bit_other | unknown | False | False | True | True | False | False | binary_two_bit_boolean | 7 |
| bit_permutation_inversion | lrot | True | True | False | False | False | True | binary_bit_permutation_bijection | 7 |
| bit_permutation_inversion | rrot | True | True | False | False | False | True | binary_bit_permutation_bijection | 7 |
| bit_other | unknown | False | False | False | True | True | False | binary_three_bit_boolean | 6 |
| bit_other | unknown | False | False | True | True | True | False | binary_two_bit_boolean | 6 |
| bit_permutation_inversion | lrot | True | True | False | False | True | True | binary_bit_permutation_bijection | 6 |
| bit_permutation_inversion | unknown | True | True | True | False | False | False | binary_bit_permutation_bijection | 6 |
| bit_permutation_inversion | unknown | True | True | True | False | True | False | binary_bit_permutation_bijection | 6 |
| bit_permutation_inversion | rrot | True | True | False | False | True | True | binary_bit_permutation_bijection | 5 |
| bit_permutation_inversion | unknown | True | False | False | False | False | False |  | 5 |

## Text

| template_subtype | teacher_solver_candidate | selection_tier | analysis_notes | rows |
| --- | --- | --- | --- | --- |
| text_monoalphabetic |  | answer_only_keep | text_answer_completion | 971 |
| text_monoalphabetic | text_char_substitution | verified_trace_ready | text_exact | 605 |

## Symbol

| template_subtype | teacher_solver_candidate | selection_tier | analysis_notes | rows |
| --- | --- | --- | --- | --- |
| glyph_len5 |  | manual_audit_priority | symbol_audit_needed | 823 |
| numeric_2x2 |  | manual_audit_priority | symbol_audit_needed | 509 |
| numeric_2x2 | symbol_numeric_operator_formula | verified_trace_ready | symbol_numeric_formula_exact | 109 |
| numeric_2x2 | symbol_numeric_operator_formula | answer_only_keep | symbol_numeric_formula_low_shot | 104 |
| numeric_2x2 |  | exclude_suspect | symbol_audit_needed | 10 |

