# cuda-train-data-analysis-v1 manual curation pass1

## Current exact string-template-backed symbol rows

| selection_tier | symbol_numeric_formula_name | symbol_same_operator_example_count | rows |
| --- | --- | --- | --- |
| answer_only_keep | concat_xy | 1 | 19 |
| answer_only_keep | concat_yx | 1 | 19 |
| verified_trace_ready | concat_xy | 2 | 16 |
| verified_trace_ready | concat_yx | 2 | 12 |
| answer_only_keep | abs_diff_2d | 1 | 8 |
| verified_trace_ready | abs_diff_2d | 2 | 4 |
| verified_trace_ready | concat_yx | 3 | 4 |
| verified_trace_ready | abs_diff_2d_op_suffix | 2 | 1 |
| verified_trace_ready | concat_xy | 3 | 1 |
| verified_trace_ready | concat_yx | 4 | 1 |

## Promoted symbol rows

| id | selection_tier | symbol_query_operator | symbol_numeric_formula_name | symbol_same_operator_example_count | answer | query_raw |
| --- | --- | --- | --- | --- | --- | --- |
| 16699d43 | answer_only_keep | + | abs_diff_2d | 1 | 10 | 67+57 |
| 74b9b0ec | answer_only_keep | [ | abs_diff_2d | 1 | 16 | 22[38 |
| 86cda2ec | answer_only_keep | - | abs_diff_2d | 1 | 13 | 26-39 |
| 9cb03277 | answer_only_keep | ! | abs_diff_2d | 1 | 26 | 52!78 |
| 9d4ae6b8 | answer_only_keep | - | abs_diff_2d | 1 | 16 | 51-35 |
| bad6f95d | answer_only_keep | - | abs_diff_2d | 1 | 41 | 54-95 |
| e518256e | answer_only_keep | " | abs_diff_2d | 1 | 84 | 94"10 |
| e836fb20 | answer_only_keep | - | abs_diff_2d | 1 | 68 | 89-21 |
| 047c4111 | answer_only_keep | $ | concat_xy | 1 | 2596 | 25$96 |
| 2a73a462 | answer_only_keep | : | concat_xy | 1 | 9302 | 93:02 |
| 35a89469 | answer_only_keep | [ | concat_xy | 1 | 9525 | 95[25 |
| 372bb422 | answer_only_keep | ( | concat_xy | 1 | 7560 | 75(60 |
| 37a2a7ff | answer_only_keep | / | concat_xy | 1 | 8483 | 84/83 |
| 43837c5b | answer_only_keep | * | concat_xy | 1 | 4572 | 45*72 |
| 5a763686 | answer_only_keep | & | concat_xy | 1 | 7495 | 74&95 |
| 605e1c08 | answer_only_keep | " | concat_xy | 1 | 1020 | 10"20 |
| 6dda26c0 | answer_only_keep | [ | concat_xy | 1 | 4643 | 46[43 |
| 6e60b0c5 | answer_only_keep | ) | concat_xy | 1 | 9555 | 95)55 |
| 71e02000 | answer_only_keep | $ | concat_xy | 1 | 3767 | 37$67 |
| 8d2546a5 | answer_only_keep | - | concat_xy | 1 | 1211 | 12-11 |
| 963bdc67 | answer_only_keep | \ | concat_xy | 1 | 9973 | 99\73 |
| a19a75ba | answer_only_keep | # | concat_xy | 1 | 2655 | 26#55 |
| b193f06a | answer_only_keep | } | concat_xy | 1 | 3182 | 31}82 |
| c7bcab48 | answer_only_keep | # | concat_xy | 1 | 5899 | 58#99 |
| dc7a5e7b | answer_only_keep | @ | concat_xy | 1 | 4445 | 44@45 |
| e7cf0394 | answer_only_keep | ] | concat_xy | 1 | 9783 | 97]83 |
| ee9239e9 | answer_only_keep | * | concat_xy | 1 | 2629 | 26*29 |
| 2cc274cb | answer_only_keep | + | concat_yx | 1 | 6821 | 21+68 |
| 3831c67a | answer_only_keep | * | concat_yx | 1 | 5146 | 46*51 |
| 4aeed935 | answer_only_keep | * | concat_yx | 1 | 1455 | 55*14 |
| 4df01584 | answer_only_keep | + | concat_yx | 1 | 1935 | 35+19 |
| 69aa57b3 | answer_only_keep | + | concat_yx | 1 | 4472 | 72+44 |
| 6f1211e2 | answer_only_keep | * | concat_yx | 1 | 6745 | 45*67 |
| 743a293d | answer_only_keep | + | concat_yx | 1 | 2432 | 32+24 |
| 76d2ee64 | answer_only_keep | + | concat_yx | 1 | 9402 | 02+94 |
| 8021718e | answer_only_keep | * | concat_yx | 1 | 6479 | 79*64 |
| 84af5d7e | answer_only_keep | + | concat_yx | 1 | 6155 | 55+61 |
| 88b43464 | answer_only_keep | + | concat_yx | 1 | 5311 | 11+53 |
| 90d57388 | answer_only_keep | + | concat_yx | 1 | 2615 | 15+26 |
| a8e5eca1 | answer_only_keep | * | concat_yx | 1 | 4274 | 74*42 |
| aa7f06f4 | answer_only_keep | ? | concat_yx | 1 | 3212 | 12?32 |
| aa8c76a1 | answer_only_keep | * | concat_yx | 1 | 0861 | 61*08 |
| ab7809d1 | answer_only_keep | + | concat_yx | 1 | 2572 | 72+25 |
| cd9d50e2 | answer_only_keep | + | concat_yx | 1 | 5293 | 93+52 |
| e70d5739 | answer_only_keep | + | concat_yx | 1 | 6257 | 57+62 |
| f28681ad | answer_only_keep | * | concat_yx | 1 | 4314 | 14*43 |
| 0a15c5c7 | verified_trace_ready | - | abs_diff_2d | 2 | 43 | 79-36 |
| 75032b65 | verified_trace_ready | & | abs_diff_2d | 2 | 27 | 52&25 |
| 878c843c | verified_trace_ready | / | abs_diff_2d | 2 | 35 | 80/45 |
| c7420a23 | verified_trace_ready | $ | abs_diff_2d | 2 | 33 | 42$75 |
| 824d4bcb | verified_trace_ready | : | abs_diff_2d_op_suffix | 2 | 64: | 24:88 |
| 6b393b81 | verified_trace_ready | > | concat_xy | 3 | 4046 | 40>46 |
| 0cd170a0 | verified_trace_ready | ^ | concat_xy | 2 | 9814 | 98^14 |
| 1c48f9aa | verified_trace_ready | { | concat_xy | 2 | 8610 | 86{10 |
| 27cec7a9 | verified_trace_ready | : | concat_xy | 2 | 3341 | 33:41 |
| 2f485a40 | verified_trace_ready | + | concat_xy | 2 | 1867 | 18+67 |
| 3580648f | verified_trace_ready | - | concat_xy | 2 | 2640 | 26-40 |
| 3efc46c1 | verified_trace_ready | [ | concat_xy | 2 | 3964 | 39[64 |
| 4895b955 | verified_trace_ready | ( | concat_xy | 2 | 4796 | 47(96 |
| 54c9bde5 | verified_trace_ready | - | concat_xy | 2 | 3064 | 30-64 |
| 680f19b3 | verified_trace_ready | ? | concat_xy | 2 | 9756 | 97?56 |
| 76e6f646 | verified_trace_ready | { | concat_xy | 2 | 6557 | 65{57 |
| 91488dc9 | verified_trace_ready | ? | concat_xy | 2 | 3431 | 34?31 |
| a8e033fe | verified_trace_ready | ? | concat_xy | 2 | 6854 | 68?54 |
| dbd0e3c9 | verified_trace_ready | * | concat_xy | 2 | 5631 | 56*31 |
| dfec0ed4 | verified_trace_ready | * | concat_xy | 2 | 9370 | 93*70 |
| f7d90ae3 | verified_trace_ready | / | concat_xy | 2 | 9819 | 98/19 |
| f94810f5 | verified_trace_ready | { | concat_xy | 2 | 1592 | 15{92 |
| 552e14d7 | verified_trace_ready | + | concat_yx | 4 | 1756 | 56+17 |
| 41e6cbfc | verified_trace_ready | + | concat_yx | 3 | 9318 | 18+93 |
| 52c62a3e | verified_trace_ready | * | concat_yx | 3 | 1292 | 92*12 |
| 7c72ad99 | verified_trace_ready | * | concat_yx | 3 | 2733 | 33*27 |
| 8321a400 | verified_trace_ready | * | concat_yx | 3 | 6915 | 15*69 |
| 383889e1 | verified_trace_ready | " | concat_yx | 2 | 5185 | 85"51 |
| 427ba852 | verified_trace_ready | * | concat_yx | 2 | 2214 | 14*22 |
| 4d8f8111 | verified_trace_ready | + | concat_yx | 2 | 7601 | 01+76 |
| 791fc537 | verified_trace_ready | ` | concat_yx | 2 | 5342 | 42`53 |
| 8dea05d7 | verified_trace_ready | + | concat_yx | 2 | 3907 | 07+39 |
| 9760032a | verified_trace_ready | + | concat_yx | 2 | 9372 | 72+93 |
| 99e2cf41 | verified_trace_ready | + | concat_yx | 2 | 4415 | 15+44 |

## Binary rows now excluded

| id | answer | auto_solver_predicted_answer | bit_no_candidate_positions | audit_reasons |
| --- | --- | --- | --- | --- |
| ae93aec4 | 00011000 | 10011000 | 1 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_affine_low_gap_mismatch |
| 084a4496 | 11000111 | 11100111 | 1 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_affine_low_gap_mismatch |
| 5a0c141c | 01010000 | 01000000 | 1 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_affine_low_gap_mismatch |
| 934a2c55 | 00101011 | 00101111 | 1 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_affine_low_gap_mismatch |
| bf002000 | 11001000 | 11011000 | 1 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_affine_low_gap_mismatch |
| eeb60061 | 00000101 | 10010101 | 1 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_affine_low_gap_mismatch |
| 26410094 | 10010000 | 11010000 | 1 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_affine_low_gap_mismatch |
| 2d74e088 | 10001100 | 10011101 | 1 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_affine_low_gap_mismatch |
| 8f6d4fb3 | 00101011 | 00111011 | 1 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_affine_low_gap_mismatch |
| 978c688b | 11010111 | 11110111 | 1 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_affine_low_gap_mismatch |
| c3207775 | 11111001 | 01011001 | 1 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_affine_low_gap_mismatch |

## Binary affine mismatch rows still kept manual

| id | answer | auto_solver_predicted_answer | bit_no_candidate_positions | audit_reasons |
| --- | --- | --- | --- | --- |
| 009a74b6 | 11111011 | 11000011 | 5 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous |
| 069dbaab | 00010000 | 11011100 | 6 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous |
| 0a195a74 | 01010010 | 01011011 | 4 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous |
| 0a50c4a8 | 00001101 | 00111111 | 5 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous |
| 111296b0 | 01001101 | 01001100 | 2 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous |
| 3aec6985 | 01000100 | 01000110 | 2 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous |
| 4a374160 | 00000110 | 01000110 | 2 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous |
| 5d77eff6 | 00011100 | 00011000 | 8 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous |
| 7403ef93 | 10011101 | 10011100 | 4 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous |
| 74e525f0 | 01001000 | 01101000 | 4 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous |
| 789b83ce | 00001110 | 00011111 | 4 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous |
| 851a22cb | 00001010 | 10001010 | 3 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous |
| 9b1761fb | 10000000 | 00000000 | 8 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous |
| a5749dc0 | 00000000 | 00000010 | 7 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous |
| b3785949 | 11100011 | 11100001 | 2 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous |
| b8954f14 | 11000011 | 11100011 | 2 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous |
| c4a6d52b | 01000010 | 11100010 | 2 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous |
| cf447906 | 10000111 | 10000100 | 6 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous |
| e5d0d497 | 01101101 | 01100100 | 5 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous |
| fb5a7b9e | 11111010 | 11011010 | 2 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous |

## Glyph rows still kept manual

| id | hard_score | answer | query_raw | audit_reasons |
| --- | --- | --- | --- | --- |
| f4f92956 | 7.0 | (`)) | ()"%} | symbol_length_mismatch\|symbol_solver_unverified |
| 64553a64 | 5.0 | }#' | !@"`/ | symbol_length_mismatch\|symbol_solver_unverified |
| 97abca56 | 5.0 | `#:: | (:*`' | symbol_length_mismatch\|symbol_solver_unverified |
| a77be9fa | 5.0 | [" | {>\|$[ | symbol_length_mismatch\|symbol_solver_unverified |
| afdb7326 | 5.0 | %\ | @^%(^ | symbol_length_mismatch\|symbol_solver_unverified |

Decision summary: current pass1 safely keeps only exact `numeric_2x2` string-template rows (`concat_xy`, `concat_yx`, `abs_diff_2d`, `abs_diff_2d_op_suffix`) on the promotion list. Binary low-gap rows with unique affine rules that still contradict the gold answer now move to `exclude_suspect`; broader affine mismatches and glyph coarse-consistent rows stay manual.

