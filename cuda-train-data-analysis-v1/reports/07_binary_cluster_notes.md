# cuda-train-data-analysis-v1 binary cluster notes

## Unresolved binary cluster summary

| num_examples | bit_simple_family | bit_no_candidate_positions | bit_multi_candidate_positions | bit_boolean2_unique | bit_boolean3_unique | bit_affine_unique | bit_byte_transform_unique | rows |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 10 | unknown | 8 | 0 | False | False | False | False | 48 |
| 9 | unknown | 7 | 0 | False | False | False | False | 39 |
| 7 | unknown | 1 | 0 | False | False | False | False | 32 |
| 8 | unknown | 2 | 0 | False | False | False | False | 32 |
| 7 | unknown | 2 | 0 | False | False | False | False | 31 |
| 8 | unknown | 8 | 0 | False | False | False | False | 29 |
| 7 | unknown | 3 | 0 | False | False | False | False | 27 |
| 7 | unknown | 4 | 0 | False | False | False | False | 26 |
| 7 | unknown | 7 | 0 | False | False | False | False | 26 |
| 8 | unknown | 1 | 0 | False | False | False | False | 26 |
| 8 | unknown | 4 | 0 | False | False | False | False | 26 |
| 8 | unknown | 5 | 0 | False | False | False | False | 26 |
| 10 | unknown | 7 | 0 | False | False | False | False | 26 |
| 7 | unknown | 6 | 0 | False | False | False | False | 25 |
| 8 | unknown | 3 | 0 | False | False | False | False | 25 |
| 7 | unknown | 5 | 0 | False | False | False | False | 24 |
| 8 | unknown | 6 | 0 | False | False | False | False | 23 |
| 8 | unknown | 7 | 0 | False | False | False | False | 22 |
| 10 | unknown | 3 | 0 | False | False | False | False | 22 |
| 9 | unknown | 5 | 0 | False | False | False | False | 21 |
| 9 | unknown | 8 | 0 | False | False | False | False | 21 |
| 7 | unknown | 8 | 0 | False | False | False | False | 20 |
| 9 | unknown | 2 | 0 | False | False | False | False | 20 |
| 9 | unknown | 3 | 0 | False | False | False | False | 20 |
| 9 | unknown | 6 | 0 | False | False | False | False | 18 |

## Top binary manual-audit queue

| id | num_examples | bit_simple_family | bit_no_candidate_positions | bit_multi_candidate_positions | hard_score | answer |
| --- | --- | --- | --- | --- | --- | --- |
| a63f9c85 | 7 | unknown | 0 | 1 | 3.0 | 11111111 |
| 9bfb1cc6 | 7 | unknown | 0 | 2 | 3.0 | 10001101 |
| a7cbf6fd | 7 | unknown | 0 | 2 | 3.0 | 01100000 |
| f8640728 | 8 | unknown | 0 | 5 | 3.0 | 00000000 |
| 4ac6f0cb | 10 | unknown | 1 | 0 | 8.0 | 10100101 |
| 16e151ec | 10 | unknown | 1 | 0 | 6.0 | 00011000 |
| 25764d5f | 10 | unknown | 1 | 0 | 6.0 | 00001000 |
| 264b2118 | 10 | unknown | 1 | 0 | 6.0 | 00010100 |
| 835c56b6 | 10 | unknown | 1 | 0 | 6.0 | 01110100 |
| 845fee60 | 10 | unknown | 1 | 0 | 6.0 | 01110000 |
| 89dfa4c2 | 10 | unknown | 1 | 0 | 6.0 | 00111010 |
| 8f07a84d | 10 | unknown | 1 | 0 | 6.0 | 11101000 |
| 06667a93 | 9 | unknown | 1 | 0 | 5.0 | 10100011 |
| 0a1326f4 | 9 | unknown | 1 | 0 | 5.0 | 10010110 |
| 20052c2f | 9 | unknown | 1 | 0 | 5.0 | 01100110 |
| 46dd0f22 | 9 | unknown | 1 | 0 | 5.0 | 01010000 |
| 4e5df314 | 9 | unknown | 1 | 0 | 5.0 | 00100010 |
| 6cb5aff2 | 9 | unknown | 1 | 0 | 5.0 | 01111110 |
| 73d0b62c | 9 | unknown | 1 | 0 | 5.0 | 10000111 |
| c23fca57 | 9 | unknown | 1 | 0 | 5.0 | 00101100 |
| c711f9dd | 9 | unknown | 1 | 0 | 5.0 | 11000000 |
| d6f4e854 | 9 | unknown | 1 | 0 | 5.0 | 00101110 |
| e2b02e13 | 9 | unknown | 1 | 0 | 5.0 | 01111110 |
| 07d1cd39 | 8 | unknown | 1 | 0 | 3.0 | 11000000 |
| 0c88a3dc | 8 | unknown | 1 | 0 | 3.0 | 10001011 |

Observation: simple byte transforms (shift/rotate/mask) recover a small extra slice, but the dominant unresolved cluster still has no single-bit candidate on at least one output position, so the remaining rules likely need broader boolean/circuit families or richer non-local byte transforms.
