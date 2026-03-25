# cuda-train-data-analysis-v1 glyph round2 cluster map

## Purpose

Map the 46 `symbol_glyph_multiset` rows into small structural clusters so round2 can start from repetition patterns instead of re-reading the full list blindly.

## Scope

- glyph round2 rows: `46`
- grouped by answer length, unique-character counts, and repeated-character signatures in query/answer.

## Top clusters

| answer_len | query_unique | answer_unique | query_repeats | answer_repeats | rows | representative_ids |
| --- | --- | --- | --- | --- | --- | --- |
| 2 | 5 | 2 | - | - | 6 | e582df31,26a2a1b8,a77be9fa,177f0c22,82c9f137 |
| 4 | 5 | 4 | - | - | 5 | 0d4b2baa,1d10ccaf,24b2d8eb,52f499f4,2d624cab |
| 3 | 5 | 3 | - | - | 4 | 64553a64,1a28140b,2e1b9d84,0dce4039 |
| 2 | 4 | 2 | ^ | - | 3 | 9fdb18b7,afdb7326,93e6d0c0 |
| 3 | 4 | 3 | ! | - | 2 | 02664ad5,b4b73143 |
| 4 | 5 | 3 | - | ^ | 2 | e401ee4f,fc137acd |
| 1 | 4 | 1 | $ | - | 1 | 6c7f24b7 |
| 1 | 4 | 1 | ] | - | 1 | 76587d66 |
| 2 | 3 | 2 | @ | - | 1 | 58eadc55 |
| 2 | 3 | 2 | ^ | - | 1 | 28b0ff48 |
| 2 | 4 | 2 | # | - | 1 | 42bde66c |
| 2 | 4 | 2 | $ | - | 1 | ae6be599 |
| 2 | 4 | 2 | ) | - | 1 | c69b17bf |
| 2 | 4 | 2 | ? | - | 1 | 86ccbdf7 |
| 2 | 4 | 2 | { | - | 1 | c9780577 |
| 3 | 3 | 3 | $\| | - | 1 | 1545b8f1 |
| 3 | 3 | 3 | ` | - | 1 | 8962872b |
| 3 | 4 | 2 | ) | & | 1 | 3b7148f6 |
| 3 | 4 | 2 | < | @ | 1 | fc2b2fc9 |
| 3 | 4 | 3 | / | - | 1 | dc93896e |
| 3 | 4 | 3 | @ | - | 1 | e5d6e090 |
| 3 | 4 | 3 | \ | - | 1 | 771472d6 |
| 4 | 4 | 2 | ) | /@ | 1 | 0625f633 |
| 4 | 4 | 3 | " | ` | 1 | 51352792 |
| 4 | 4 | 3 | ) | > | 1 | eb1a62f7 |

## Reading order

1. short-answer clusters (`answer_len` 1-2)
2. clusters with repeated output characters
3. clusters with repeated query characters but diverse outputs

## Notes

- This map does not claim any new safe family; it is a navigation artifact for manual round2 reading.
- report 16 still stands: the coarse multiset+order model is not unique enough for automatic promotion/exclusion.

