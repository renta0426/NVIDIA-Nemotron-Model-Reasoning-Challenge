# cuda-train-data-analysis-v1 hard-family findings

## Binary

| template_subtype | bit_simple_family | bit_independent_unique | bit_bijection_unique | bit_boolean2_unique | bit_boolean3_unique | bit_affine_unique | bit_byte_transform_unique | bit_hybrid_consensus_ready | selection_tier | analysis_notes | teacher_solver_candidate | rows |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bit_other | unknown | False | False | False | False | False | False | False | manual_audit_priority | bit_audit_needed |  | 851 |
| bit_structured_byte_formula | unknown | False | False | False | False | False | False | False | verified_trace_ready | bit_structured_byte_exact | binary_structured_byte_formula | 174 |
| bit_other | unknown | False | False | False | False | True | False | False | verified_trace_ready | bit_exact | binary_affine_xor | 112 |
| bit_other | unknown | False | False | False | False | True | False | False | manual_audit_priority | bit_audit_needed |  | 108 |
| bit_other | unknown | False | False | True | False | True | False | False | verified_trace_ready | bit_exact | binary_two_bit_boolean | 59 |
| bit_other | unknown | False | False | True | False | False | False | False | verified_trace_ready | bit_exact | binary_two_bit_boolean | 52 |
| bit_permutation_inversion | unknown | True | True | False | False | False | False | False | verified_trace_ready | bit_exact | binary_bit_permutation_bijection | 25 |
| bit_structured_byte_formula | unknown | False | False | False | False | False | False | False | verified_trace_ready | bit_structured_byte_abstract_exact | binary_structured_byte_formula_abstract | 25 |
| bit_other | unknown | False | False | False | False | False | False | True | answer_only_keep | bit_hybrid_consensus |  | 16 |
| bit_other | unknown | False | False | False | False | True | False | True | verified_trace_ready | bit_exact | binary_affine_xor | 16 |
| bit_structured_byte_formula | unknown | False | False | False | False | True | False | False | verified_trace_ready | bit_structured_byte_exact | binary_structured_byte_formula | 15 |
| bit_permutation_inversion | unknown | True | True | False | False | True | False | False | verified_trace_ready | bit_exact | binary_bit_permutation_bijection | 11 |
| bit_other | unknown | False | False | False | True | False | False | False | verified_trace_ready | bit_exact | binary_three_bit_boolean | 9 |
| bit_other | rshift | False | False | False | False | False | True | False | verified_trace_ready | bit_exact | binary_byte_transform | 7 |
| bit_other | unknown | False | False | False | False | True | False | False | exclude_suspect | bit_affine_low_gap_mismatch |  | 7 |
| bit_other | unknown | False | False | True | True | False | False | False | verified_trace_ready | bit_exact | binary_two_bit_boolean | 7 |
| bit_permutation_inversion | lrot | True | True | False | False | False | True | False | verified_trace_ready | bit_exact | binary_bit_permutation_bijection | 7 |
| bit_permutation_inversion | rrot | True | True | False | False | False | True | False | verified_trace_ready | bit_exact | binary_bit_permutation_bijection | 7 |
| bit_other | unknown | False | False | False | True | True | False | False | verified_trace_ready | bit_exact | binary_three_bit_boolean | 6 |
| bit_permutation_inversion | lrot | True | True | False | False | True | True | False | verified_trace_ready | bit_exact | binary_bit_permutation_bijection | 6 |

## Text

| template_subtype | teacher_solver_candidate | selection_tier | analysis_notes | rows |
| --- | --- | --- | --- | --- |
| text_monoalphabetic |  | answer_only_keep | text_answer_completion | 971 |
| text_monoalphabetic | text_char_substitution | verified_trace_ready | text_exact | 605 |

## Symbol

| template_subtype | teacher_solver_candidate | selection_tier | analysis_notes | rows |
| --- | --- | --- | --- | --- |
| glyph_len5 |  | manual_audit_priority | symbol_audit_needed | 823 |
| numeric_2x2 |  | manual_audit_priority | symbol_audit_needed | 497 |
| numeric_2x2 | symbol_numeric_operator_formula | answer_only_keep | symbol_numeric_formula_low_shot | 114 |
| numeric_2x2 | symbol_numeric_operator_formula | verified_trace_ready | symbol_numeric_formula_exact | 110 |
| numeric_2x2 |  | exclude_suspect | symbol_audit_needed | 11 |

