# cuda-train-data-analysis-v1 binary residual affine scan

## Newly excluded low-gap affine mismatches

| id | num_examples | answer | auto_solver_predicted_answer | bit_no_candidate_positions | bit_multi_candidate_positions | audit_reasons |
| --- | --- | --- | --- | --- | --- | --- |
| ae93aec4 | 10 | 00011000 | 10011000 | 1 | 0 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous\|bit_affine_low_gap_mismatch |
| bf002000 | 9 | 11001000 | 11011000 | 1 | 0 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous\|bit_affine_low_gap_mismatch |
| 26410094 | 8 | 10010000 | 11010000 | 1 | 0 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous\|bit_affine_low_gap_mismatch |
| 2d74e088 | 7 | 10001100 | 10011101 | 1 | 0 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous\|bit_affine_low_gap_mismatch |
| 8f6d4fb3 | 8 | 00101011 | 00111011 | 1 | 0 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous\|bit_affine_low_gap_mismatch |
| 978c688b | 8 | 11010111 | 11110111 | 1 | 0 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous\|bit_affine_low_gap_mismatch |
| c3207775 | 8 | 11111001 | 01011001 | 1 | 0 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous\|bit_affine_low_gap_mismatch |

## Remaining affine mismatch rows kept manual

| id | num_examples | answer | auto_solver_predicted_answer | bit_no_candidate_positions | bit_multi_candidate_positions | audit_reasons |
| --- | --- | --- | --- | --- | --- | --- |
| 069dbaab | 10 | 00010000 | 11011100 | 6 | 0 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous |
| 7403ef93 | 10 | 10011101 | 10011100 | 4 | 0 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous |
| 9b1761fb | 10 | 10000000 | 00000000 | 8 | 0 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous |
| cf447906 | 10 | 10000111 | 10000100 | 6 | 0 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous |
| 07d61ec8 | 9 | 10111101 | 10000001 | 6 | 0 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous |
| 202af98d | 9 | 11111101 | 10010010 | 8 | 0 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous |
| 40400f33 | 9 | 11110001 | 10001011 | 7 | 0 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous |
| 7f73016f | 9 | 01010110 | 01010010 | 4 | 0 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous |
| 87c4e31b | 9 | 00010111 | 00000101 | 8 | 0 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous |
| 8b434583 | 9 | 01001111 | 01000101 | 7 | 0 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous |
| a521be72 | 9 | 11011111 | 11011110 | 3 | 0 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous |
| ab064b6a | 8 | 11111111 | 11111110 | 4 | 0 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous |
| 1282c5c5 | 8 | 00001110 | 00000001 | 6 | 0 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous |
| 2f270b32 | 8 | 11111011 | 11110011 | 5 | 0 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous |
| 9124295a | 8 | 01010101 | 00110100 | 4 | 1 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous |
| a48b8329 | 8 | 00110101 | 00111110 | 7 | 0 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous |
| c424dcd4 | 8 | 11001111 | 11000001 | 4 | 0 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous |
| e266959e | 8 | 11100110 | 10100000 | 2 | 2 | bit_no_candidate\|bit_independent_ambiguous\|bit_bijection_ambiguous\|bit_boolean2_ambiguous\|bit_boolean3_ambiguous\|bit_affine_answer_mismatch\|bit_byte_transform_ambiguous\|bit_hybrid_consensus_ambiguous |

Interpretation: rows move to `exclude_suspect` only when the affine solution is unique, no stricter solver family wins, the gap is low (`bit_no_candidate_positions <= 1`, `bit_multi_candidate_positions == 0`), and the affine answer still contradicts the gold label. More ambiguous affine mismatches remain manual.

