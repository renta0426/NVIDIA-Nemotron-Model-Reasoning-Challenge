# cuda-train-data-analysis-v1 binary cluster notes

## Unresolved binary cluster summary

| num_examples | bit_simple_family | bit_no_candidate_positions | bit_multi_candidate_positions | bit_boolean2_unique | bit_boolean3_unique | bit_boolean4_unique | bit_affine_unique | bit_byte_transform_unique | rows |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 9 | unknown | 7 | 0 | False | False | False | False | False | 19 |
| 10 | unknown | 8 | 0 | False | False | False | False | False | 18 |
| 8 | unknown | 7 | 0 | False | False | False | False | False | 16 |
| 8 | unknown | 5 | 0 | False | False | False | False | False | 14 |
| 10 | unknown | 7 | 0 | False | False | False | False | False | 14 |
| 7 | unknown | 7 | 0 | False | False | False | False | False | 12 |
| 8 | unknown | 6 | 0 | False | False | False | False | False | 12 |
| 7 | unknown | 5 | 0 | False | False | False | False | False | 11 |
| 7 | unknown | 6 | 0 | False | False | False | False | False | 11 |
| 8 | unknown | 8 | 0 | False | False | False | False | False | 11 |
| 7 | unknown | 4 | 0 | False | False | False | False | False | 9 |
| 7 | unknown | 8 | 0 | False | False | False | False | False | 9 |
| 9 | unknown | 6 | 0 | False | False | False | False | False | 9 |
| 7 | unknown | 2 | 0 | False | False | False | False | False | 8 |
| 8 | unknown | 4 | 0 | False | False | False | False | False | 8 |
| 9 | unknown | 8 | 0 | False | False | False | False | False | 8 |
| 9 | unknown | 5 | 0 | False | False | False | False | False | 6 |
| 7 | unknown | 3 | 0 | False | False | False | False | False | 5 |
| 7 | unknown | 6 | 1 | False | False | False | False | False | 5 |
| 10 | unknown | 6 | 0 | False | False | False | False | False | 5 |
| 7 | unknown | 2 | 1 | False | False | False | False | False | 4 |
| 9 | unknown | 3 | 0 | False | False | False | False | False | 4 |
| 9 | unknown | 5 | 0 | False | False | False | True | False | 4 |
| 7 | unknown | 0 | 2 | False | False | False | False | False | 3 |
| 7 | unknown | 1 | 0 | False | False | False | False | False | 3 |

## Top binary manual-audit queue

| id | num_examples | bit_simple_family | bit_no_candidate_positions | bit_multi_candidate_positions | hard_score | answer |
| --- | --- | --- | --- | --- | --- | --- |
| a63f9c85 | 7 | unknown | 0 | 1 | 3.0 | 11111111 |
| 9984fc0f | 7 | unknown | 0 | 2 | 3.0 | 01111110 |
| 9bfb1cc6 | 7 | unknown | 0 | 2 | 3.0 | 10001101 |
| b43d9cd5 | 7 | unknown | 0 | 2 | 3.0 | 11100100 |
| 264b2118 | 10 | unknown | 1 | 0 | 6.0 | 00010100 |
| 06667a93 | 9 | unknown | 1 | 0 | 5.0 | 10100011 |
| 4e5df314 | 9 | unknown | 1 | 0 | 5.0 | 00100010 |
| 132ec6ae | 8 | unknown | 1 | 0 | 3.0 | 11101100 |
| 6adef1ef | 8 | unknown | 1 | 0 | 3.0 | 11111101 |
| cf5b4ab4 | 8 | unknown | 1 | 0 | 3.0 | 11101100 |
| 2460c01a | 7 | unknown | 1 | 0 | 3.0 | 10111010 |
| b80795b4 | 7 | unknown | 1 | 0 | 3.0 | 00010000 |
| dbf2b40f | 7 | unknown | 1 | 0 | 3.0 | 10001101 |
| 9ab82dfb | 9 | unknown | 1 | 2 | 5.0 | 10011100 |
| b45003a6 | 7 | unknown | 1 | 2 | 3.0 | 00110110 |
| e5bb9b26 | 7 | unknown | 1 | 2 | 3.0 | 11110001 |
| 111296b0 | 10 | unknown | 2 | 0 | 6.0 | 01001101 |
| b3785949 | 10 | unknown | 2 | 0 | 6.0 | 11100011 |
| 0dcacfab | 9 | unknown | 2 | 0 | 5.0 | 10011101 |
| b76fd053 | 9 | unknown | 2 | 0 | 5.0 | 11100111 |
| 0df8306a | 8 | unknown | 2 | 0 | 3.0 | 10000000 |
| 2b3e06c9 | 8 | unknown | 2 | 0 | 3.0 | 00111111 |
| 323b9f56 | 8 | unknown | 2 | 0 | 3.0 | 01100011 |
| 06881e47 | 7 | unknown | 2 | 0 | 3.0 | 11111100 |
| 3456da40 | 7 | unknown | 2 | 0 | 3.0 | 00001111 |

Observation: the structured-byte library now stays on the conservative repeated binary family (`xor`/`and`/`or` plus selected `choose`/`majority` over `x`, `rol/ror`, `shl/shr`, `reverse`, `nibble_swap`) and the shift span reaches `1..7`, which recovers a much larger exact slice. For training use, a leave-one-out re-audit keeps only self-independent structured families in `verified_trace_ready`; thinner singleton or prompt-exact rows now fall back to `answer_only_keep`.
