# cuda-train-data-analysis-v1 symbol operator-specific consensus recovery

## Purpose

Recover low-shot or ambiguous `symbol_equation / numeric_2x2` rows using **operator-local repeated evidence**, without pretending that the exact within-row formula is uniquely identified.

## Rule

For each `numeric_2x2` row:

1. enumerate all formula/format specs that fit the row's same-operator examples
2. build a support table over the full train split keyed by:
   - `query_operator`
   - `formula_name`
   - `format_name`
3. mark an operator-specific spec as **safe** only when:
   - `support_rows >= 2`
   - `error_rows = 0`
4. for a manual row, promote to `answer_only_keep` only if:
   - at least one safe operator-specific spec matches the row
   - **all** safe matching specs imply the same query answer
   - that answer matches gold on train

This is intentionally weaker than `verified_trace_ready`: prompt-local ambiguity can remain, but the operator-local repeated evidence is strong enough to keep the answer.

## Full-train result

- recovered rows: `16`
- train errors on the promoted slice: `0`

## Recovered rows

| id | operator | query | answer | same-op examples |
| --- | --- | --- | --- | ---: |
| `03f07b43` | `` ` `` | `81\`20` | `61` | 1 |
| `0bcffccd` | `` ` `` | `44\`54` | `10` | 1 |
| `0c8a8a16` | `{` | `37{54` | `{17` | 1 |
| `224efda1` | `]` | `61]54` | `7` | 2 |
| `2beb5851` | `[` | `10[33` | `23` | 2 |
| `2c8e2e06` | `&` | `38&90` | `&52` | 1 |
| `53b48918` | `+` | `91+10` | `81` | 1 |
| `5787c3d0` | `^` | `85^86` | `^1` | 1 |
| `5dc0aca5` | `+` | `15+12` | `3` | 1 |
| `8158a14c` | `)` | `49)03` | `46` | 1 |
| `9a5b6b28` | `^` | `81^59` | `^22` | 3 |
| `9b458fbc` | `[` | `34[73` | `39` | 1 |
| `b03ab026` | `{` | `97{23` | `74` | 1 |
| `da3f727d` | `/` | `59/73` | `/14` | 1 |
| `e9afa4a0` | `}` | `13}64` | `}51` | 1 |
| `f6ca90f6` | `{` | `54{23` | `31` | 2 |

## Artifacts

- `artifacts/symbol_operator_specific_formula_support_v1.csv`
  - operator-specific spec support / error ledger
- `artifacts/symbol_operator_specific_formula_candidates_v1.csv`
  - rows touched by at least one safe operator-specific spec

## Counts after recovery

- overall: `6081 verified / 1123 answer_only / 2270 manual / 26 exclude`
- symbol: `110 verified / 130 answer_only / 1304 manual / 11 exclude`

## Interpretation

This is the first useful symbol move after the broader negative scans:

- not a new global arithmetic family
- not a query-only shortcut
- but a **cross-row, operator-local consensus rule**

It works because some operators repeatedly reuse the same rendering convention even when a single prompt by itself is still ambiguous.

## Decision

Adopt the rule as `answer_only_keep` only.

These rows now have reliable answer-level supervision, but they still do **not** have unique prompt-local derivations, so they should not be upgraded to `verified_trace_ready`.
