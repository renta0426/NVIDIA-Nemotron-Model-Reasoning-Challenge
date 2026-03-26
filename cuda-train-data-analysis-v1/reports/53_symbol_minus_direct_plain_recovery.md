# cuda-train-data-analysis-v1 symbol `-` direct plain recovery

## Purpose

Revisit the remaining `symbol_equation / numeric_2x2` `-` tail after reports 50 and 52.

Report 50 recovered the operator-embedded `-05 / -6 / -1` branch.  
This follow-up targets a different residual: rows whose same-operator examples already show an **exact direct subtraction formatter**, but the current generic operator search still leaves them manual because the broader `-` family mixes several incompatible formatting branches.

## Rule

Parse the same-operator `-` examples inside each prompt and require that **every** such example matches one of these exact direct renderers:

1. `signed_plain`
   - render: `str(x - y)`
   - examples may be positive (`97-03 = 94`) or negative (`34-87 = -53`)
2. `abs_plain`
   - render: `str(abs(x - y))`
   - examples always drop the sign (`85-98 = 13`)

Then apply only the following query-observable zero-error subfamilies:

### 1. `minus_signed_plain_both_lt`

- prompt examples all fit `signed_plain`
- query digits satisfy `x_tens < y_tens` and `x_ones < y_ones`
- prediction: `str(x - y)`

### 2. `minus_signed_plain_both_gt`

- prompt examples all fit `signed_plain`
- query digits satisfy `x_tens > y_tens` and `x_ones > y_ones`
- prediction: `str(x - y)`

### 3. `minus_abs_plain_both_gt`

- prompt examples all fit `abs_plain`
- query digits satisfy `x_tens > y_tens` and `x_ones > y_ones`
- prediction: `str(abs(x - y))`

## Full-train support

| subfamily | support | gold match | error |
| --- | ---: | ---: | ---: |
| `minus_signed_plain_both_lt` | 4 | 4 | 0 |
| `minus_signed_plain_both_gt` | 3 | 3 | 0 |
| `minus_abs_plain_both_gt` | 3 | 3 | 0 |

Adoption rule:

- `support_rows >= 3`
- `error_rows = 0`

## Recovered manual rows

| id | query | answer | subfamily |
| --- | --- | --- | --- |
| `10fdae00` | `52-99` | `-47` | `minus_signed_plain_both_lt` |
| `56c59dfd` | `96-74` | `22` | `minus_signed_plain_both_gt` |
| `d8bc44b3` | `37-06` | `31` | `minus_abs_plain_both_gt` |

## Why this is safer than broad minus recovery

These rows do **not** rely on query-only arithmetic fit.

Each rule first requires the prompt-local `-` examples to already match an exact direct formatter, then uses only a small query-observable digit-order split to choose a zero-error branch.  
This avoids known conflicts such as:

- zero-padded positives like `36-32 = 04`
- operator-embedded negative branches like `22-27 = -05`
- contradictory label rows like `92-63 = -7`

## Why this stays answer-only

The answers are well supported, but the trace evidence is still relatively thin and formatter-specific.

Per `README.md`, final competition score is direct answer accuracy, so the conservative decision is to keep these rows as `answer_only_keep`, not `verified_trace_ready`.

## Counts after recovery

- overall: `6081 verified / 1143 answer_only / 2250 manual / 26 exclude`
- symbol: `110 verified / 139 answer_only / 1295 manual / 11 exclude`
- pass1 manual pack: `500 rows`
  - `336` `symbol_numeric_same_op`
  - `118` `binary_low_gap`
  - `46` `symbol_glyph_multiset`
- current `symbol` round2 core: `282 rows`

## Artifacts

- `artifacts/symbol_minus_direct_plain_support_v1.csv`
- `artifacts/symbol_minus_direct_plain_candidates_v1.csv`

## Decision

Adopt these three exact direct-minus subfamilies as `answer_only_keep` only.

This is a clean continuation of the post-report-50 `-` cleanup: the operator still had a small amount of recoverable tail left, but only after splitting by **prompt-exact formatter** plus **query-observable digit-order branch**.
