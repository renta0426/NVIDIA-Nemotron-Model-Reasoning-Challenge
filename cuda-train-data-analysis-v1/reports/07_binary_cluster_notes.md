# cuda-train-data-analysis-v1 binary cluster notes

## Unresolved binary cluster summary

| num_examples | bit_simple_family | bit_no_candidate_positions | bit_multi_candidate_positions | bit_boolean2_unique | bit_boolean3_unique | bit_boolean4_unique | bit_affine_unique | bit_byte_transform_unique | rows |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 10 | unknown | 8 | 0 | False | False | False | False | False | 11 |
| 9 | unknown | 7 | 0 | False | False | False | False | False | 9 |
| 8 | unknown | 7 | 0 | False | False | False | False | False | 6 |
| 8 | unknown | 8 | 0 | False | False | False | False | False | 6 |
| 7 | unknown | 7 | 0 | False | False | False | False | False | 5 |
| 7 | unknown | 8 | 0 | False | False | False | False | False | 5 |
| 10 | unknown | 7 | 0 | False | False | False | False | False | 5 |
| 7 | unknown | 6 | 0 | False | False | False | False | False | 4 |
| 8 | unknown | 5 | 0 | False | False | False | False | False | 3 |
| 9 | unknown | 5 | 0 | False | False | False | False | False | 3 |
| 9 | unknown | 8 | 0 | False | False | False | False | False | 3 |
| 7 | unknown | 1 | 2 | False | False | False | False | False | 2 |
| 7 | unknown | 3 | 0 | False | False | False | False | False | 2 |
| 7 | unknown | 6 | 1 | False | False | False | False | False | 2 |
| 7 | unknown | 0 | 1 | False | False | False | False | False | 1 |
| 7 | unknown | 2 | 0 | False | False | False | False | False | 1 |
| 7 | unknown | 2 | 1 | False | False | False | False | False | 1 |
| 7 | unknown | 4 | 1 | False | False | False | False | False | 1 |
| 7 | unknown | 6 | 2 | False | False | False | False | False | 1 |
| 7 | unknown | 7 | 1 | False | False | False | False | False | 1 |
| 8 | unknown | 1 | 0 | False | False | False | False | False | 1 |
| 8 | unknown | 2 | 0 | False | False | False | False | False | 1 |
| 8 | unknown | 3 | 0 | False | False | False | False | False | 1 |
| 8 | unknown | 3 | 2 | False | False | False | False | False | 1 |
| 8 | unknown | 4 | 0 | False | False | False | False | False | 1 |

## Top binary manual-audit queue

| id | num_examples | bit_simple_family | bit_no_candidate_positions | bit_multi_candidate_positions | hard_score | answer |
| --- | --- | --- | --- | --- | --- | --- |
| a63f9c85 | 7 | unknown | 0 | 1 | 3.0 | 11111111 |
| 264b2118 | 10 | unknown | 1 | 0 | 6.0 | 00010100 |
| 6adef1ef | 8 | unknown | 1 | 0 | 3.0 | 11111101 |
| b45003a6 | 7 | unknown | 1 | 2 | 3.0 | 00110110 |
| e5bb9b26 | 7 | unknown | 1 | 2 | 3.0 | 11110001 |
| 0df8306a | 8 | unknown | 2 | 0 | 3.0 | 10000000 |
| e3590284 | 7 | unknown | 2 | 0 | 3.0 | 11111111 |
| d9ce7d0d | 7 | unknown | 2 | 1 | 3.0 | 00000111 |
| 405262aa | 8 | unknown | 3 | 0 | 3.0 | 00000100 |
| 13c8ae90 | 7 | unknown | 3 | 0 | 3.0 | 00110000 |
| 3a7dd604 | 7 | unknown | 3 | 0 | 3.0 | 01001010 |
| 78616706 | 8 | unknown | 3 | 2 | 3.0 | 00000111 |
| 2a5d4790 | 8 | unknown | 4 | 0 | 3.0 | 11111111 |
| 693bb27c | 7 | unknown | 4 | 1 | 3.0 | 00001111 |
| 5a6dd286 | 9 | unknown | 5 | 0 | 5.0 | 10111100 |
| 626a2762 | 9 | unknown | 5 | 0 | 5.0 | 01000101 |
| 98e1a8b4 | 9 | unknown | 5 | 0 | 5.0 | 01111110 |
| 2f270b32 | 8 | unknown | 5 | 0 | 3.0 | 11111011 |
| 31063a4d | 8 | unknown | 5 | 0 | 3.0 | 00000000 |
| 4b8f6727 | 8 | unknown | 5 | 0 | 3.0 | 11010110 |
| ed5c81ae | 8 | unknown | 5 | 0 | 3.0 | 00100000 |
| 069dbaab | 10 | unknown | 6 | 0 | 6.0 | 00010000 |
| 5d060d45 | 10 | unknown | 6 | 0 | 6.0 | 00000000 |
| 0f8fe647 | 9 | unknown | 6 | 0 | 5.0 | 00110101 |
| ec46d596 | 8 | unknown | 6 | 0 | 3.0 | 10111111 |

Observation: the structured-byte library now stays on the conservative repeated binary family (`xor`/`and`/`or` plus selected `choose`/`majority` over `x`, `rol/ror`, `shl/shr`, `reverse`, `nibble_swap`) and the shift span reaches `1..7`, which recovers a much larger exact slice. For training use, a leave-one-out re-audit keeps only self-independent structured families in `verified_trace_ready`; thinner singleton or prompt-exact rows now fall back to `answer_only_keep`.
