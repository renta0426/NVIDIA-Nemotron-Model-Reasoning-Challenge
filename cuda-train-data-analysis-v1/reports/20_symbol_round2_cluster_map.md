# cuda-train-data-analysis-v1 symbol round2 cluster map

## Purpose

After pass1, exclude all manual rows whose query answer only mimics already-known simple families or already-rejected high-shot arithmetic lookalikes, then map the remaining `symbol_numeric_same_op` rows into operator-specific residual clusters for round2 manual reading.

## Scope

- remaining post-mimic-exclusion `symbol_numeric_same_op` rows: `294`
- excluded known/query-only mimic union: `67` rows
- grouped by operator, answer length, operator-char embedding, and same-operator example count bucket.

## Top clusters

| symbol_query_operator | answer_len | answer_has_operator_char | same_operator_bucket | rows | representative_ids |
| --- | --- | --- | --- | --- | --- |
| * | 4 | False | 1 | 22 | 2d3e809c,5d44a0b2,dd626fd0,15a1d279,418895f5 |
| * | 4 | False | 2 | 17 | 1580f498,4d39d098,837af955,88fe5a52,98bb54f7 |
| + | 3 | False | 1 | 14 | 4dbec546,56343b77,a7454fdb,1f0674b0,25f2f2cd |
| + | 3 | False | 2 | 14 | 50c0b6f8,5fe8d710,912d2b79,94bf323a,1497f970 |
| - | 3 | True | 1 | 14 | e102a09d,10fdae00,2dd48cac,33093ed0,45dbc1cc |
| + | 2 | False | 1 | 10 | 3013265c,30c0d5a2,49578b02,4a569495,4cf073bf |
| + | 3 | False | 3 | 8 | 0819520a,163db2d8,3ec77e36,1f4c8169,59b2cbbf |
| + | 2 | False | 2 | 7 | 2423926d,c81411a2,d033513f,2e2d60b2,3937cbf8 |
| * | 3 | False | 1 | 4 | c0f32a1e,026106f5,620c2521,759cbdde |
| * | 4 | False | 3 | 4 | 40c53743,68b9b9a8,850dc715,a9deb8b5 |
| - | 1 | False | 2 | 4 | 333d93ec,3b2e0cc3,58fed63a,b73d0898 |
| - | 2 | False | 1 | 4 | 8373daa8,3383d4ec,5d834875,fb3f7b77 |
| @ | 3 | False | 2 | 4 | 286135d3,518d8529,bf4bd858,e4b6ce82 |
| } | 3 | False | 1 | 4 | e9afa4a0,17c98340,912c6ea5,b3ae7f39 |
| - | 2 | True | 1 | 4 | 4179c322,812c12cb,d3092ac1,12d4a2df |
| $ | 3 | False | 1 | 3 | 50630ad8,11f62c83,db4383f3 |
| $ | 4 | False | 2 | 3 | 6bd59a1f,9f2fae58,bd4c584a |
| % | 4 | False | 3 | 3 | 6c9e4485,3b51288b,69197d42 |
| & | 3 | False | 1 | 3 | 2c8e2e06,1d92ba5d,bc7f14d1 |
| * | 2 | False | 1 | 3 | 49919931,49ac9daf,614408ea |
| [ | 4 | False | 1 | 3 | b3f9a15c,4f660f4b,61766c6f |
| - | 3 | True | 4+ | 3 | 4245e455,7688e06e,c541eb82 |
| ! | 4 | False | 1 | 2 | 379d18b7,3b7e71b2 |
| ! | 4 | False | 3 | 2 | 1cb4d524,7ecdae14 |
| " | 4 | False | 1 | 2 | 5f5a73ff,ddb9aafd |

## Reading order

1. `*` with 4-digit answers
2. `+` with 3-digit answers
3. `-` with 3-digit answers
4. clusters whose answers embed the operator character

## Notes

- This map excludes the full union of report 17 plus the extra low-shot/known-family mimic slice.
- The excluded union now removes many dead-end `abs_diff_2d` / `abs_diff_2d_op_suffix` / `comp99_abs_diff_2d` lookalikes before round2 starts.
- Use the representative IDs as the first prompts to read when beginning round2 manual clustering.

