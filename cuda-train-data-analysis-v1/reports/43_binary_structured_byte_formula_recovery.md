# cuda-train-data-analysis-v1 binary structured byte formula recovery

## Purpose

Probe a new binary family for the `README.md` accuracy-first setting: instead of deciding each output bit independently, model the whole output byte as a **shared formula over transformed versions of the same input byte**.

## Hypothesis

Many residual `bit_manipulation` rows looked too non-local for the existing `bit_candidate_signature` logic, but still resembled deterministic byte algebra.  
The candidate family was:

- canonical byte sources:
  - `x`
  - `rol1..7`
  - `ror1..7`
  - `shl1..3`
  - `shr1..3`
  - `reverse`
  - `nibble_swap`
- semantic dedupe over all `256` byte inputs
- binary ops:
  - `xor`
  - `and`
  - `or`
- then semantic dedupe again over the resulting byte functions

This yields `311` semantic formulas from `15` canonical source functions.

## Conservative acceptance rule

Promote a row to `verified_trace_ready` only when all of the following hold:

1. exactly **one semantic structured-byte formula** matches every example in the prompt
2. that formula predicts the gold answer for the row
3. the same formula appears as a unique exact match on **at least 2 rows** across all `bit_manipulation` data
4. that formula has **0 empirical mismatches** on those unique-match rows

This rule intentionally rejects singleton formulas and any row with multi-formula ambiguity, even if the query prediction looks plausible.

## Result

- safe structured formulas: `71`
- binary rows with any structured-byte match: `403`
  - `348 verified_trace_ready`
  - `51 manual_audit_priority`
  - `4 exclude_suspect`
- **new verified promotions from manual**: `189`
- recovered binary total:
  - before: `381 verified / 20 answer_only / 1186 manual / 15 exclude`
  - after: `570 verified / 20 answer_only / 997 manual / 15 exclude`

## Top supported formulas

| support_rows | formula |
| ---: | --- |
| 18 | `ror3` |
| 16 | `rol1` |
| 15 | `xor(shl2,shr1)` |
| 14 | `rol3` |
| 13 | `xor(shl2,shr3)` |
| 12 | `xor(shl1,shr3)` |
| 11 | `shr1` |
| 11 | `xor(shl1,shr2)` |
| 11 | `xor(shl3,shr1)` |
| 10 | `shr2` |
| 10 | `xor(shl3,shr2)` |
| 9 | `rol2` |

## Important rejected cases

- unique but unsafe mismatch:
  - `8631d7b6`
  - formula: `xor(ror1,shr1)`
  - structured formula prediction: `10000000`
  - gold: `00000000`
  - therefore support-based safe promotion must reject singleton formulas
- same-pred multi-formula rows kept out:
  - `8b4c71ba`
  - `cc5011ac`
- ambiguous-pred row kept out:
  - `5a6dd286`

## Interpretation

This is the first strong evidence that a large part of the residual binary set is not random long-tail noise but a **repeatable structured byte family** that the previous row-local bit solver missed. The safe subset is large enough to matter (`+189 verified`) and still keeps the acceptance rule strict enough to avoid the known singleton failure.

## Next step

Split the remaining structured-byte tail into:

1. singleton formulas with no cross-row support
2. multi-formula same-pred rows
3. multi-formula ambiguous-pred rows

The best next binary recovery chance is likely a stronger canonicalization / family grouping rule for group `1`, or a conservative consensus rule for group `2`.
