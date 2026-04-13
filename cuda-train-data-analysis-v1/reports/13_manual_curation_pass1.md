# cuda-train-data-analysis-v1 manual curation pass1

## Current exact formula-backed symbol rows

| selection_tier | symbol_numeric_formula_name | symbol_same_operator_example_count | rows |
| --- | --- | --- | --- |
| answer_only_keep | concat_xy | 1 | 19 |
| answer_only_keep | concat_yx | 1 | 19 |
| verified_trace_ready | concat_xy | 2 | 16 |
| answer_only_keep | comp99_abs_diff_2d | 1 | 14 |
| verified_trace_ready | concat_yx | 2 | 12 |
| answer_only_keep | abs_diff_2d | 1 | 9 |
| verified_trace_ready | abs_diff_2d | 2 | 4 |
| verified_trace_ready | concat_yx | 3 | 4 |
| verified_trace_ready | comp99_abs_diff_2d | 2 | 2 |
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
| d3092ac1 | answer_only_keep | - | abs_diff_2d | 1 | -7 | 92-63 |
| e518256e | answer_only_keep | " | abs_diff_2d | 1 | 84 | 94"10 |
| e836fb20 | answer_only_keep | - | abs_diff_2d | 1 | 68 | 89-21 |
| 13892a7c | answer_only_keep | - | comp99_abs_diff_2d | 1 | -85 | 61-47 |
| 1bc85bd9 | answer_only_keep | - | comp99_abs_diff_2d | 1 | 93 | 16-22 |
| 2049f01d | answer_only_keep | - | comp99_abs_diff_2d | 1 | 23 | 52-75 |
| 33093ed0 | answer_only_keep | - | comp99_abs_diff_2d | 1 | -72 | 07-79 |
| 3a8a4ebc | answer_only_keep | ' | comp99_abs_diff_2d | 1 | '54 | 74'29 |
| 5c008804 | answer_only_keep | @ | comp99_abs_diff_2d | 1 | 52 | 83@36 |
| 6b769a9e | answer_only_keep | + | comp99_abs_diff_2d | 1 | +92 | 24+17 |
| 8d652f91 | answer_only_keep | - | comp99_abs_diff_2d | 1 | 4 | 97-57 |
| c7a7b13a | answer_only_keep | - | comp99_abs_diff_2d | 1 | 35 | 93-29 |
| cde9f7ba | answer_only_keep | [ | comp99_abs_diff_2d | 1 | 81 | 15[33 |
| d17d3a7a | answer_only_keep | - | comp99_abs_diff_2d | 1 | -01 | 66-67 |
| debff779 | answer_only_keep | - | comp99_abs_diff_2d | 1 | 94 | 36-41 |
| e247d364 | answer_only_keep | ! | comp99_abs_diff_2d | 1 | 11 | 65!76 |
| ef6bc241 | answer_only_keep | $ | comp99_abs_diff_2d | 1 | $55 | 73$29 |
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
| b655eee9 | verified_trace_ready | - | comp99_abs_diff_2d | 2 | -92 | 76-83 |
| cb2fdb6b | verified_trace_ready | - | comp99_abs_diff_2d | 2 | 54 | 08-53 |
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

## Binary rows now excluded

| id | answer | auto_solver_predicted_answer | bit_no_candidate_positions | audit_reasons |
| --- | --- | --- | --- | --- |
| ae93aec4 | 00011000 | 10011000 | 1 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_boolean4_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous\|bit_affine_low_gap_mismatch |
| bf002000 | 11001000 | 11011000 | 1 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_boolean4_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous\|bit_affine_low_gap_mismatch |
| 26410094 | 10010000 | 11010000 | 1 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_boolean4_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous\|bit_affine_low_gap_mismatch |
| 2d74e088 | 10001100 | 10011101 | 1 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_boolean4_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous\|bit_affine_low_gap_mismatch |
| 8f6d4fb3 | 00101011 | 00111011 | 1 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_boolean4_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous\|bit_affine_low_gap_mismatch |
| 978c688b | 11010111 | 11110111 | 1 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_boolean4_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous\|bit_affine_low_gap_mismatch |
| c3207775 | 11111001 | 01011001 | 1 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_boolean4_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous\|bit_affine_low_gap_mismatch |

## Binary affine mismatch rows still kept manual

| id | answer | auto_solver_predicted_answer | bit_no_candidate_positions | audit_reasons |
| --- | --- | --- | --- | --- |
| 069dbaab | 00010000 | 11011100 | 6 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_boolean4_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous |
| 9b1761fb | 10000000 | 00000000 | 8 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_boolean4_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous |
| 87c4e31b | 00010111 | 00000101 | 8 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_boolean4_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous |
| 8b434583 | 01001111 | 01000101 | 7 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_boolean4_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous |
| 2f270b32 | 11111011 | 11110011 | 5 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_boolean4_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous |
| a48b8329 | 00110101 | 00111110 | 7 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_boolean4_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous |

## Glyph rows promoted as answer-only training labels

| id | hard_score | answer | query_raw |
| --- | --- | --- | --- |
| 4bb8c6cd | 9.0 | ]}\! | ]}*\! |
| 50ba5396 | 9.0 | \]]@ | }&(\" |
| 56efc838 | 9.0 | }$?( | ()*?} |
| 71d91445 | 9.0 | } | \"/@\| |
| a40497f9 | 9.0 | %]\< | <%*]\ |
| d7e5414c | 9.0 | \|%\\ | #[}@[ |
| 10a94678 | 8.0 | ""\} | ">*)\ |
| 193c21d5 | 8.0 | }>[[ | >\|*%{ |
| 2e9973b7 | 8.0 | )\?% | )\+?% |
| 3cc03e36 | 8.0 | }\|(# | #/*\|# |
| 60ed3f31 | 8.0 | @%:\ | @%*:\ |
| 65b13ba2 | 8.0 | ]/"} | #@{]" |
| 7138d71a | 8.0 | \ | ^]-'% |
| 7933172a | 8.0 | ^/&` | %#+^` |
| 7a65a8eb | 8.0 | }'#' | '(*?? |
| 82b32563 | 8.0 | ^\%\ | %\+^\ |
| 8326116b | 8.0 | {{@? | #:*#\ |
| 98eed496 | 8.0 | ^[}` | ^[>}` |
| b50cf853 | 8.0 | \|?"} | \|?*"} |
| c37e694c | 8.0 | {&\\ | /{*{\ |

Decision summary: current pass1 safely keeps exact `numeric_2x2` prompt-backed rows on the promotion list, moves remaining non-suspect `glyph_len5` rows and non-suspect `numeric_2x2` same-op-zero rows to `answer_only_keep` as raw final-answer supervision, and still sends only clear rule-vs-gold contradictions to `exclude_suspect`.

