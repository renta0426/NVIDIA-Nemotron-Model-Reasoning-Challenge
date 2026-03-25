# cuda-train-data-analysis-v1 binary cluster notes

## Unresolved binary cluster summary

| num_examples | bit_simple_family | bit_no_candidate_positions | bit_multi_candidate_positions | bit_boolean2_unique | bit_boolean3_unique | bit_affine_unique | bit_byte_transform_unique | rows |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 10 | unknown | 8 | 0 | False | False | False | False | 53 |
| 9 | unknown | 7 | 0 | False | False | False | False | 44 |
| 8 | unknown | 4 | 0 | False | False | False | False | 38 |
| 7 | unknown | 4 | 0 | False | False | False | False | 37 |
| 8 | unknown | 2 | 0 | False | False | False | False | 36 |
| 8 | unknown | 5 | 0 | False | False | False | False | 36 |
| 10 | unknown | 7 | 0 | False | False | False | False | 36 |
| 7 | unknown | 5 | 0 | False | False | False | False | 35 |
| 7 | unknown | 6 | 0 | False | False | False | False | 35 |
| 7 | unknown | 1 | 0 | False | False | False | False | 34 |
| 7 | unknown | 2 | 0 | False | False | False | False | 34 |
| 7 | unknown | 3 | 0 | False | False | False | False | 34 |
| 7 | unknown | 7 | 0 | False | False | False | False | 33 |
| 8 | unknown | 8 | 0 | False | False | False | False | 32 |
| 8 | unknown | 3 | 0 | False | False | False | False | 30 |
| 8 | unknown | 6 | 0 | False | False | False | False | 30 |
| 8 | unknown | 7 | 0 | False | False | False | False | 30 |
| 9 | unknown | 5 | 0 | False | False | False | False | 30 |
| 8 | unknown | 1 | 0 | False | False | False | False | 29 |
| 9 | unknown | 6 | 0 | False | False | False | False | 28 |
| 9 | unknown | 3 | 0 | False | False | False | False | 26 |
| 10 | unknown | 3 | 0 | False | False | False | False | 24 |
| 7 | unknown | 8 | 0 | False | False | False | False | 23 |
| 9 | unknown | 8 | 0 | False | False | False | False | 22 |
| 10 | unknown | 5 | 0 | False | False | False | False | 22 |

## Top binary manual-audit queue

| id | num_examples | bit_simple_family | bit_no_candidate_positions | bit_multi_candidate_positions | hard_score | answer |
| --- | --- | --- | --- | --- | --- | --- |
| a63f9c85 | 7 | unknown | 0 | 1 | 3.0 | 11111111 |
| 892d73b5 | 9 | unknown | 0 | 2 | 5.0 | 00010101 |
| 209e62c5 | 8 | unknown | 0 | 2 | 3.0 | 01111001 |
| 9984fc0f | 7 | unknown | 0 | 2 | 3.0 | 01111110 |
| 9bfb1cc6 | 7 | unknown | 0 | 2 | 3.0 | 10001101 |
| a7cbf6fd | 7 | unknown | 0 | 2 | 3.0 | 01100000 |
| b43d9cd5 | 7 | unknown | 0 | 2 | 3.0 | 11100100 |
| f9fee551 | 7 | unknown | 0 | 2 | 3.0 | 00011010 |
| f8640728 | 8 | unknown | 0 | 5 | 3.0 | 00000000 |
| 4ac6f0cb | 10 | unknown | 1 | 0 | 8.0 | 10100101 |
| 16e151ec | 10 | unknown | 1 | 0 | 6.0 | 00011000 |
| 1deaf759 | 10 | unknown | 1 | 0 | 6.0 | 10100111 |
| 25764d5f | 10 | unknown | 1 | 0 | 6.0 | 00001000 |
| 264b2118 | 10 | unknown | 1 | 0 | 6.0 | 00010100 |
| 48db5ccf | 10 | unknown | 1 | 0 | 6.0 | 01101110 |
| 62dba403 | 10 | unknown | 1 | 0 | 6.0 | 10011001 |
| 6686f0de | 10 | unknown | 1 | 0 | 6.0 | 10110111 |
| 7a5d00a7 | 10 | unknown | 1 | 0 | 6.0 | 11110011 |
| 835c56b6 | 10 | unknown | 1 | 0 | 6.0 | 01110100 |
| 845fee60 | 10 | unknown | 1 | 0 | 6.0 | 01110000 |
| 89dfa4c2 | 10 | unknown | 1 | 0 | 6.0 | 00111010 |
| 8f07a84d | 10 | unknown | 1 | 0 | 6.0 | 11101000 |
| 06667a93 | 9 | unknown | 1 | 0 | 5.0 | 10100011 |
| 0a1326f4 | 9 | unknown | 1 | 0 | 5.0 | 10010110 |
| 20052c2f | 9 | unknown | 1 | 0 | 5.0 | 01100110 |

Observation: simple byte transforms (shift/rotate/mask) recover a small extra slice, but the dominant unresolved cluster still has no single-bit candidate on at least one output position, so the remaining rules likely need broader boolean/circuit families or richer non-local byte transforms.
