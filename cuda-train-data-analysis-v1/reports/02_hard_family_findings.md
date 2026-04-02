# cuda-train-data-analysis-v1 hard-family findings

## Binary

| template_subtype | bit_simple_family | bit_independent_unique | bit_bijection_unique | bit_boolean2_unique | bit_boolean3_unique | bit_boolean4_unique | bit_affine_unique | bit_byte_transform_unique | bit_hybrid_consensus_ready | selection_tier | analysis_notes | teacher_solver_candidate | rows |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bit_structured_byte_formula | unknown | False | False | False | False | False | False | False | False | verified_trace_ready | bit_structured_byte_exact | binary_structured_byte_formula | 410 |
| bit_structured_byte_formula | unknown | False | False | False | False | False | False | False | False | answer_only_keep | bit_prompt_local_current_consensus_answer_only |  | 193 |
| bit_structured_byte_formula | unknown | False | False | False | False | False | False | False | False | verified_trace_ready | bit_structured_byte_abstract_exact | binary_structured_byte_formula_abstract | 126 |
| bit_other | unknown | False | False | False | False | False | False | False | False | manual_audit_priority | bit_audit_needed |  | 119 |
| bit_other | unknown | False | False | False | False | False | True | False | False | verified_trace_ready | bit_exact | binary_affine_xor | 112 |
| bit_other | unknown | False | False | False | False | False | False | False | False | answer_only_keep | bit_prompt_local_nested_support3_or_abstract_answer_only |  | 106 |
| bit_other | unknown | False | False | False | False | False | False | False | False | answer_only_keep | bit_prompt_local_current_consensus_answer_only |  | 61 |
| bit_other | unknown | False | False | True | False | False | True | False | False | verified_trace_ready | bit_exact | binary_two_bit_boolean | 59 |
| bit_other | unknown | False | False | True | False | False | False | False | False | verified_trace_ready | bit_exact | binary_two_bit_boolean | 52 |
| bit_structured_byte_formula | unknown | False | False | False | False | False | True | False | False | verified_trace_ready | bit_structured_byte_exact | binary_structured_byte_formula | 36 |
| bit_structured_byte_formula | unknown | False | False | False | False | False | True | False | False | answer_only_keep | bit_prompt_local_current_consensus_answer_only |  | 27 |
| bit_structured_byte_formula | unknown | False | False | False | False | False | True | False | False | verified_trace_ready | bit_structured_byte_abstract_exact | binary_structured_byte_formula_abstract | 26 |
| bit_permutation_inversion | unknown | True | True | False | False | False | False | False | False | verified_trace_ready | bit_exact | binary_bit_permutation_bijection | 25 |
| bit_structured_byte_formula | unknown | False | False | False | False | False | False | False | False | verified_trace_ready | bit_not_structured_byte_exact | binary_structured_byte_not_formula | 23 |
| bit_other | unknown | False | False | False | False | False | True | False | False | manual_audit_priority | bit_audit_needed |  | 18 |
| bit_other | unknown | False | False | False | False | False | True | False | False | answer_only_keep | bit_prompt_local_nested_support3_or_abstract_answer_only |  | 16 |
| bit_other | unknown | False | False | False | False | False | True | False | True | verified_trace_ready | bit_exact | binary_affine_xor | 16 |
| bit_other | unknown | False | False | False | False | False | False | False | True | answer_only_keep | bit_prompt_local_current_consensus_answer_only |  | 14 |
| bit_permutation_inversion | unknown | True | True | False | False | False | True | False | False | verified_trace_ready | bit_exact | binary_bit_permutation_bijection | 11 |
| bit_other | unknown | False | False | False | True | False | False | False | False | verified_trace_ready | bit_exact | binary_three_bit_boolean | 9 |

## Text

| template_subtype | teacher_solver_candidate | selection_tier | analysis_notes | rows |
| --- | --- | --- | --- | --- |
| text_monoalphabetic |  | answer_only_keep | text_answer_completion | 971 |
| text_monoalphabetic | text_char_substitution | verified_trace_ready | text_exact | 605 |

## Symbol

| template_subtype | teacher_solver_candidate | selection_tier | analysis_notes | rows |
| --- | --- | --- | --- | --- |
| glyph_len5 |  | answer_only_keep | symbol_glyph_training_answer_only | 470 |
| glyph_len5 |  | answer_only_keep | symbol_glyph_grouped_exact_answer_only | 275 |
| numeric_2x2 |  | answer_only_keep | symbol_reverse_operator_spec_consensus | 198 |
| numeric_2x2 |  | answer_only_keep | symbol_numeric_no_same_op_training_answer_only | 136 |
| numeric_2x2 | symbol_numeric_operator_formula | answer_only_keep | symbol_numeric_formula_low_shot | 114 |
| numeric_2x2 | symbol_numeric_operator_formula | verified_trace_ready | symbol_numeric_formula_exact | 110 |
| numeric_2x2 |  | answer_only_keep | symbol_reverse_manual_exact_answer_only | 76 |
| glyph_len5 |  | answer_only_keep | symbol_glyph_grouped_small_set_answer_only | 43 |
| glyph_len5 |  | answer_only_keep | symbol_glyph_grouped_single_example_small_set_answer_only | 35 |
| numeric_2x2 |  | manual_audit_priority | symbol_audit_needed | 26 |
| numeric_2x2 |  | answer_only_keep | symbol_operator_spec_consensus | 21 |
| numeric_2x2 |  | answer_only_keep | symbol_reverse_small_core_digit_answer_only | 9 |
| numeric_2x2 |  | exclude_suspect | symbol_audit_needed | 9 |
| numeric_2x2 |  | answer_only_keep | symbol_manual_prompt_exact_answer_only | 6 |
| numeric_2x2 |  | answer_only_keep | symbol_reverse_digit_reversal_answer_only | 4 |
| numeric_2x2 |  | answer_only_keep | symbol_minus_direct_plain_subfamily | 3 |
| numeric_2x2 |  | answer_only_keep | symbol_reverse_max_mod_min_answer_only | 3 |
| numeric_2x2 |  | answer_only_keep | symbol_reverse_negative_x_minus_y_answer_only | 3 |
| numeric_2x2 |  | answer_only_keep | symbol_star_prefix_if_negative_subfamily | 3 |
| numeric_2x2 |  | answer_only_keep | symbol_current_max_mod_min_answer_only | 2 |

