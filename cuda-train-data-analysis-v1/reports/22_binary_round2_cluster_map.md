# cuda-train-data-analysis-v1 binary round2 cluster map

## Purpose

Map the 139 `binary_low_gap` residuals into a compact cluster summary so round2 binary review can focus on the few non-trivial slices instead of revisiting the whole queue.

## Scope

- binary round2 rows: `139`
- grouped by example count, candidate-gap structure, uniqueness flags, and affine mismatch presence.

## Top clusters

| num_examples | bit_no_candidate_positions | bit_multi_candidate_positions | bit_boolean2_unique | bit_boolean3_unique | bit_affine_unique | bit_byte_transform_unique | has_affine_mismatch | rows | representative_ids |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 7 | 1 | 0 | False | False | False | False | False | 34 | 0b23aa7c,0cfc74d4,114a7439,12897b38,21fa96be |
| 8 | 1 | 0 | False | False | False | False | False | 29 | 07434d56,07d1cd39,0c88a3dc,0f1bc0ff,132ec6ae |
| 9 | 1 | 0 | False | False | False | False | False | 17 | 06667a93,0a1326f4,20052c2f,368f20dd,3ebd80e6 |
| 10 | 1 | 0 | False | False | False | False | False | 13 | 4ac6f0cb,16e151ec,1deaf759,25764d5f,264b2118 |
| 7 | 1 | 2 | False | False | False | False | False | 11 | 24b60af3,3e000b40,5cc4cf10,5d489e95,6eb0d262 |
| 9 | 1 | 2 | False | False | False | False | False | 6 | 034fb629,14a30d8f,7669569d,98bbac0f,9ab82dfb |
| 8 | 1 | 2 | False | False | False | False | False | 5 | 26c83e22,75cd12f1,a0d317ce,dbc197e0,e4ea8dbc |
| 7 | 0 | 2 | False | False | False | False | False | 5 | 9984fc0f,9bfb1cc6,a7cbf6fd,b43d9cd5,f9fee551 |
| 7 | 1 | 1 | False | False | False | False | False | 5 | 9238e8d6,999673ed,f290228c,f5082693,fd1d72d0 |
| 10 | 1 | 2 | False | False | False | False | False | 3 | 18544cb0,6728c338,d8457e76 |
| 7 | 1 | 3 | False | False | False | False | False | 3 | 1f69a85f,20c252d7,a169fa86 |
| 9 | 1 | 1 | False | False | False | False | False | 2 | 4736daab,78d9d61d |
| 10 | 1 | 1 | False | False | False | False | False | 1 | 5dec898e |
| 10 | 1 | 3 | False | False | False | False | False | 1 | 5fab4df0 |
| 9 | 0 | 2 | False | False | False | False | False | 1 | 892d73b5 |
| 8 | 0 | 2 | False | False | False | False | False | 1 | 209e62c5 |
| 8 | 0 | 5 | False | False | False | False | False | 1 | f8640728 |
| 7 | 0 | 1 | False | False | False | False | False | 1 | a63f9c85 |

## Reading order

1. rows with the smallest `bit_no_candidate_positions`
2. rows that still carry `bit_affine_answer_mismatch`
3. higher-example-count rows before lower-example-count rows

## Notes

- This map confirms the current picture: no new multi-solver consensus mismatch was found beyond the 11 already excluded affine low-gap rows.
- Use this only if symbol/glyph round2 stalls, because binary still looks lower ROI than the remaining symbol clusters.

