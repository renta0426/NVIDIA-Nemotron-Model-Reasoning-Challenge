# cuda-train-data-analysis-v1 binary structured byte threshold sweep

## Purpose

Document why the current abstract structured-byte rule stops at:

- `support >= 12`
- `distinct exact formulas >= 6`
- `0 empirical errors`

instead of relaxing the threshold further.

## Threshold sweep

For singleton exact-formula rows in zero-error abstract families:

| min_support | min_distinct_exact | recovered_manual |
| ---: | ---: | ---: |
| 5 | 6 | 29 |
| 5 | 5 | 29 |
| 5 | 4 | 34 |
| 5 | 3 | 36 |
| 5 | 2 | 37 |
| 8 | 6 | 29 |
| 10 | 6 | 29 |
| 12 | 6 | 29 |
| 14 | 6 | 20 |

## Key observation

The current choice (`12 / 6`) is not arbitrary:

- lowering from `12 / 6` to `8 / 6` recovers **nothing extra**
- lowering from `12 / 6` to `5 / 4` adds only **5 more rows**
- those extra rows come from much thinner abstract families

So the first meaningful relaxation step is not a large gain; it is just a small set of lower-support families.

## Families added only by relaxation

When relaxing to around `support >= 5` and `distinct >= 4`, the main extra candidate families are:

| abstract_family | support_rows | distinct_exact | extra_manual_rows |
| --- | ---: | ---: | ---: |
| `and(ror,shr)` | 5 | 4 | 3 |
| `or(rol,shl)` | 7 | 4 | 2 |

Representative rows:

- `and(ror,shr)`:
  - `837d7158`
  - `888069cb`
  - `f5cb333a`
- `or(rol,shl)`:
  - `22b516b3`
  - `e20aa7b7`

## Why they are still held out

Even though these abstract families are currently zero-error on train:

- support is still small (`5` or `7`)
- distinct exact formulas are limited (`4`)
- the observed formula coverage is much thinner than the currently adopted families (`12+` support, `6+` distinct)

Given report 43's singleton failure and the `README.md` accuracy-first requirement, this is not yet strong enough to auto-promote.

## Decision

Keep the current abstract rule unchanged:

- use `support >= 12`
- use `distinct exact >= 6`
- require `0` empirical errors

and leave the lower-support abstract families in `manual_audit_priority` for now.
