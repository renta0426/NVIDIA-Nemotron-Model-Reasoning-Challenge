# cuda-train-data-analysis-v1 symbol round2 cluster map

## Purpose

After pass1, exclude all manual rows whose query answer only mimics already-known simple families or already-rejected high-shot arithmetic lookalikes, then map the remaining `symbol_numeric_same_op` rows into operator-specific residual clusters for round2 manual reading.

## Scope

- remaining post-mimic-exclusion `symbol_numeric_same_op` rows: `19`
- excluded known/query-only mimic union: `41` rows
- grouped by operator, answer length, operator-char embedding, and same-operator example count bucket.

## Top clusters

| symbol_query_operator | answer_len | answer_has_operator_char | same_operator_bucket | rows | representative_ids |
| --- | --- | --- | --- | --- | --- |
| - | 3 | True | 1 | 6 | e102a09d,50adfd54,91b34547,e2bb1d9f,eb68289b |
| - | 1 | False | 2 | 2 | 3b2e0cc3,58fed63a |
| ! | 2 | False | 1 | 1 | 87711597 |
| " | 2 | False | 1 | 1 | db5a5b71 |
| ( | 3 | False | 1 | 1 | 9d68ef62 |
| * | 2 | False | 1 | 1 | 49919931 |
| - | 2 | False | 1 | 1 | 8373daa8 |
| / | 2 | False | 1 | 1 | 2afebbc3 |
| < | 1 | False | 1 | 1 | 64fe405e |
| ? | 2 | False | 1 | 1 | c11777c0 |
| } | 1 | False | 1 | 1 | 45076dc9 |
| } | 2 | False | 1 | 1 | 07cbed38 |
| - | 2 | True | 1 | 1 | 12d4a2df |

## Reading order

1. `*` with 4-digit answers
2. `+` with 3-digit answers
3. `-` with 3-digit answers
4. clusters whose answers embed the operator character

## Notes

- This map excludes the full union of report 17 plus the extra low-shot/known-family mimic slice.
- The excluded union now removes many dead-end `abs_diff_2d` / `abs_diff_2d_op_suffix` / `comp99_abs_diff_2d` lookalikes before round2 starts.
- Use the representative IDs as the first prompts to read when beginning round2 manual clustering.

