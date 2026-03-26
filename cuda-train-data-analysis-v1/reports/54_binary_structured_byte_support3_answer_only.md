# cuda-train-data-analysis-v1 binary structured-byte support3 answer-only recovery

## Purpose

Revisit the last clean structured-byte tail after reports 45, 47, and 51.

Report 51 already promoted thin zero-error abstract families when:

- `support >= 4`
- `distinct exact >= 2`
- `error = 0`

That still left one very small but unusually clean family on the table:

- abstract family support is only `3`
- but all `3` supporting rows come from **different exact formulas**
- and the family remains zero-error

## Rule

Promote a structured-byte row to `answer_only_keep` when all of the following hold:

1. `bit_structured_formula_match_count == 1`
2. `bit_structured_formula_prediction_count == 1`
3. exact structured prediction matches gold
4. backing abstract family has:
   - `error_rows == 0`
   - `support_rows == 3`
   - `distinct_exact == 3`
5. row is still `manual_audit_priority`

This is narrower than report 51, not broader in spirit:

- only one tiny zero-error family qualifies
- every support row uses a different exact formula

## Recovered rows

| id | query | answer | exact formula | abstract family |
| --- | --- | --- | --- | --- |
| `01d894fb` | `01111000` | `11000000` | `and(rol3,shl2)` | `and(rol,shl)` |
| `18c54744` | `11001001` | `00000000` | `and(rol1,shl2)` | `and(rol,shl)` |

The third support row in the same abstract family is already:

- `7fae2ece` → `verified_trace_ready`

So the family evidence is:

- support `3`
- distinct exact `3`
- error `0`

## Why answer-only, not verified

This family is still too small for the stronger verified threshold from report 45.

But unlike a generic `support=3` relaxation, this slice is protected by the extra `distinct_exact == 3` gate, so it does not depend on one exact formula repeating three times.  
Per `README.md`, final score is direct answer accuracy, so the conservative reading is:

- answers are reliable enough to keep
- trace evidence is still too thin for verified supervision

## Residual after recovery

Structured-byte residual shrinks again:

- before: `9 manual + 4 exclude`
- after: `7 manual + 4 exclude`

The remaining blocked rows are now concentrated in:

- contaminated `ror` / `xor(ror,shr)` families
- singleton abstract families with support `1`
- the one ambiguous multi-pred row `5a6dd286`

## Counts after recovery

- overall: `6081 verified / 1145 answer_only / 2248 manual / 26 exclude`
- binary: `599 verified / 35 answer_only / 953 manual / 15 exclude`

## Artifact

- `artifacts/binary_structured_byte_support3_answer_only_candidates_v1.csv`

## Decision

Adopt this `support=3 / distinct=3 / error=0` slice as `answer_only_keep` only.

This keeps the binary tail policy conservative: we are not relaxing all thin families, only the one remaining family where every supporting row is a different exact formula and the empirical error is still zero.
