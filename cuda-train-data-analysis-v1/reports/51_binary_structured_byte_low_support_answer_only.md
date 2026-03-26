# cuda-train-data-analysis-v1 binary structured-byte low-support answer-only recovery

## Purpose

Revisit the structured-byte residual after reports 43 / 45 / 47.

The previous binary abstract rule only promoted singleton rows when the backing abstract family was strong enough for `verified_trace_ready`:

- `support >= 12`
- `distinct exact >= 6`
- `error = 0`

That left a thinner tail of singleton exact formulas whose abstract families were still **empirically clean**, but not strong enough for trace-level promotion.

## Rule

Promote a structured-byte row to `answer_only_keep` when all of the following hold:

1. `bit_structured_formula_match_count == 1`
2. `bit_structured_formula_prediction_count == 1`
3. exact structured formula prediction matches gold on train
4. backing abstract family has:
   - `error_rows == 0`
   - `support_rows >= 4`
   - `distinct_exact >= 2`
5. row is still `manual_audit_priority`

This is intentionally weaker than the verified abstract rule.

Because the family evidence is thinner than the `support>=12 / distinct>=6` verified threshold, these rows are promoted only to **answer-only**, not to `verified_trace_ready`.

## Recovered rows

| id | query | answer | exact formula | abstract family | support | distinct exact |
| --- | --- | --- | --- | --- | ---: | ---: |
| `22b516b3` | `01101111` | `11111111` | `or(rol3,shl1)` | `or(rol,shl)` | 7 | 4 |
| `e20aa7b7` | `10011010` | `01111101` | `or(rol1,shl2)` | `or(rol,shl)` | 7 | 4 |
| `105c8b72` | `11110101` | `00100101` | `xor(nibble_swap,shr1)` | `xor(nibble_swap,shr)` | 6 | 2 |
| `837d7158` | `11101101` | `00110100` | `and(ror3,shr1)` | `and(ror,shr)` | 5 | 4 |
| `888069cb` | `01001101` | `00000010` | `and(ror2,shr1)` | `and(ror,shr)` | 5 | 4 |
| `f5cb333a` | `10010010` | `00000000` | `and(ror1,shr3)` | `and(ror,shr)` | 5 | 4 |
| `13f76716` | `01000101` | `01111100` | `xor(nibble_swap,shl3)` | `xor(nibble_swap,shl)` | 5 | 3 |
| `733a819b` | `10111100` | `00111011` | `xor(nibble_swap,shl2)` | `xor(nibble_swap,shl)` | 5 | 3 |
| `ba73cc70` | `11110101` | `00011101` | `and(nibble_swap,shr2)` | `and(nibble_swap,shr)` | 4 | 3 |
| `dde0558e` | `11110001` | `00011000` | `and(nibble_swap,shr1)` | `and(nibble_swap,shr)` | 4 | 3 |
| `820c588f` | `00101000` | `00000000` | `and(nibble_swap,shl3)` | `and(nibble_swap,shl)` | 4 | 2 |

## Why answer-only, not verified

These rows are still singleton exact formulas.

So even though the backing abstract families are empirically clean, the trace evidence is not broad enough to claim the stronger `verified_trace_ready` label used in report 45.

The conservative interpretation is:

- the answer is reliable enough to keep
- the exact reasoning trace is still thinner than we want for verified supervision

## Residual after recovery

Structured-byte residual shrinks from:

- `20 manual + 4 exclude`

to:

- `9 manual + 4 exclude`

The remaining blocked rows are the genuinely hard tail:

- contaminated `ror` / `xor(ror,shr)` families
- singleton abstract families with support `1`
- the one remaining ambiguous multi-pred row `5a6dd286`

## Counts after recovery

- overall: `6081 verified / 1137 answer_only / 2256 manual / 26 exclude`
- binary: `599 verified / 33 answer_only / 955 manual / 15 exclude`

## Artifact

- `artifacts/binary_structured_byte_low_support_answer_only_candidates_v1.csv`

## Decision

Adopt this thin-family recovery as `answer_only_keep` only.

This keeps report 45's strict verified threshold intact, while still harvesting a safe answer-level gain from abstract families that are empirically zero-error but too small for trace-level promotion.
