# cuda-train-data-analysis-v1 binary structured byte abstract recovery

## Purpose

Recover part of the structured-byte singleton tail from report 44 without relaxing the `README.md` accuracy-first standard.

## Starting point

After report 43, the structured-byte residual was:

- `55` rows total
  - `51 manual_audit_priority`
  - `4 exclude_suspect`

Most manual residuals were **singleton exact formulas**:

- exact structured formula count = `1`
- exact prediction count = `1`
- exact support = `1`

That was still unsafe by itself because report 43 already found a concrete singleton failure (`8631d7b6`).

## Abstract family rule

Define an abstract family by dropping concrete shift indices:

- `rol1`, `rol2`, `rol3` → `rol`
- `ror1`, `ror2`, `ror3` → `ror`
- `shl1`, `shl2`, `shl3` → `shl`
- `shr1`, `shr2`, `shr3` → `shr`

Examples:

- `and(rol2,ror3)` → `and(rol,ror)`
- `xor(rol1,shr3)` → `xor(rol,shr)`

Promote a singleton exact formula row only when:

1. the row has exactly one exact structured-byte formula match
2. that exact formula has support `= 1`
3. the exact formula prediction matches gold
4. its abstract family has support `>= 12`
5. its abstract family has `distinct exact formulas >= 6`
6. its abstract family has `0` empirical errors across all unique exact-match rows

## Result

- safe abstract families: `10`
- **new verified promotions from manual**: `29`
- binary totals:
  - before this pass: `570 verified / 20 answer_only / 997 manual / 15 exclude`
  - after this pass: `599 verified / 20 answer_only / 968 manual / 15 exclude`

## Safe abstract families used for promotion

| support_rows | distinct_exact | abstract_family |
| ---: | ---: | --- |
| 21 | 8 | `xor(rol,shl)` |
| 17 | 7 | `or(rol,shr)` |
| 16 | 7 | `xor(ror,shl)` |
| 15 | 9 | `xor(rol,shr)` |
| 14 | 7 | `and(rol,ror)` |
| 14 | 7 | `or(ror,shl)` |
| 14 | 6 | `or(ror,shr)` |
| 12 | 8 | `and(rol,shr)` |
| 12 | 8 | `and(ror,shl)` |

(`xor(shl,shr)` も safe abstract family だが、今回の singleton tail 追加回収には使わなかった。)

## Representative recovered rows

| id | exact_formula | abstract_family | answer |
| --- | --- | --- | --- |
| `98c4eb34` | `and(rol2,ror1)` | `and(rol,ror)` | `00100000` |
| `cf1cca51` | `and(rol1,shr2)` | `and(rol,shr)` | `00000001` |
| `782dfb49` | `and(ror1,shl1)` | `and(ror,shl)` | `10101010` |
| `00fdc0be` | `or(ror1,shl2)` | `or(ror,shl)` | `11111111` |
| `53b84650` | `xor(rol1,shr1)` | `xor(rol,shr)` | `11111101` |
| `9c5c6401` | `xor(ror1,shl1)` | `xor(ror,shl)` | `11001100` |

## Remaining structured-byte tail

After this pass, the structured-byte residual shrinks to:

- `26` rows total
  - `22 manual_audit_priority`
  - `4 exclude_suspect`

Breakdown:

- `19` manual singleton rows still below the abstract-safe threshold
- `2` same-pred multi-formula rows
- `1` ambiguous-pred row
- `4` structured mismatch excludes

## Interpretation

This pass is materially stronger than report 43 but still conservative: it never trusts singleton exact formulas on their own, and only promotes rows whose **broader abstract family** is repeated, diverse, and empirically clean. The remaining tail is now small enough that future binary work can focus on a narrow residual instead of the previous large manual slice.
