# cuda-train-data-analysis-v1 symbol minus prefix subfamily recovery

## Purpose

Revisit the operator-embedded `-` residual that report 48 left on hold.

The global `op_prefix_abs_diff_2d` family was too noisy (`31 support / 16 errors`) to adopt directly, but the current train split still suggested a narrower possibility: a tiny `-`-only slice where the prompt examples already agree on prefixed absolute-difference formatting, and the **query digits stay in a zero-error no-borrow region**.

## Rule

Start from rows that satisfy both:

1. `symbol_equation / numeric_2x2`
2. every same-operator `-` example in the prompt matches the base template  
   `op_prefix_abs_diff_2d = "-" + zpad2(abs(x - y))`

Then split the query into two conservative subfamilies:

### 1. `minus_prefix_reverse_no_borrow_zpad2`

- query condition: `x_tens <= y_tens` and `x_ones < y_ones`
- prediction: `"-" + zpad2(y - x)`

This is the clean reverse-direction, no-borrow slice.

### 2. `minus_prefix_reverse_no_borrow_trim_zero`

- query condition: `x_tens <= y_tens` and `x_ones == y_ones`
- additional condition: `(y - x) % 10 == 0`
- prediction: `"-" + str((y - x) // 10)`

This captures the tiny repeated trim-zero formatter branch (`-10 -> -1`, `-60 -> -6`).

## Full-train support

| subfamily | support | gold match | error |
| --- | ---: | ---: | ---: |
| `minus_prefix_reverse_no_borrow_zpad2` | 4 | 4 | 0 |
| `minus_prefix_reverse_no_borrow_trim_zero` | 2 | 2 | 0 |

Both slices clear the same conservative threshold used elsewhere in this project:

- `support_rows >= 2`
- `error_rows = 0`

## Recovered manual rows

| id | query | answer | subfamily |
| --- | --- | --- | --- |
| `2dd48cac` | `22-27` | `-05` | `minus_prefix_reverse_no_borrow_zpad2` |
| `4179c322` | `15-75` | `-6` | `minus_prefix_reverse_no_borrow_trim_zero` |
| `812c12cb` | `09-19` | `-1` | `minus_prefix_reverse_no_borrow_trim_zero` |

## Why this is safer than the global near-miss

Report 48 failed because the broad cross-operator family mixed incompatible formatter branches, including hard contradictions such as `8c1529e1`.

This recovery does **not** reopen that whole family.

Instead it keeps all three conservative gates:

1. prompt-local `-` examples must already fit the prefixed abs-diff base family
2. the query must land in a query-observable zero-error subfamily
3. the subfamily must have repeated support with zero errors on full train

Because the within-row derivation is still not uniquely pinned down from a single prompt, these rows stay `answer_only_keep`, not `verified_trace_ready`.

## Counts after recovery

- overall: `6081 verified / 1126 answer_only / 2267 manual / 26 exclude`
- symbol: `110 verified / 133 answer_only / 1301 manual / 11 exclude`

## Artifacts

- `artifacts/symbol_minus_prefix_subfamily_support_v1.csv`
- `artifacts/symbol_minus_prefix_subfamily_candidates_v1.csv`

## Decision

Adopt both `-` subfamilies as conservative `answer_only_keep` recovery only.

The broader custom-operator search still looks low-yield, but this targeted follow-up shows that the operator-embedded residual was not fully exhausted: a small, query-observable `-` slice was still recoverable without relaxing the `README.md` accuracy-first bar.
