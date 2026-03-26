# cuda-train-data-analysis-v1 symbol thin support2 recovery

## Purpose

Re-run the post-report-54 symbol subgroup search and harvest the last operator-local slices that still satisfy all of the following:

- same-operator examples fit one exact family
- the query split is observable from the query itself
- full-train support is zero-error
- the slice is still thin enough that it should stay `answer_only_keep`

At this stage, only two such support-2 slices remained worth adopting.

## Recovered subfamilies

### 1. `exclamation_abs_diff_2d_both_lt`

Requirements:

1. query operator is `!`
2. every same-operator example matches `abs_diff_2d`
3. query digits satisfy `x_tens < y_tens` and `x_ones < y_ones`
4. prediction is direct `abs_diff_2d`

Full-train support:

| subfamily | support | gold match | error |
| --- | ---: | ---: | ---: |
| `exclamation_abs_diff_2d_both_lt` | 2 | 2 | 0 |

Recovered row:

| id | query | answer |
| --- | --- | --- |
| `7c5c7b73` | `21!34` | `13` |

### 2. `quote_prefix_if_negative_large_positive`

Requirements:

1. query operator is `"`
2. every same-operator example matches `x_minus_y :: prefix_if_negative`
3. query satisfies `x > y` and `abs(x - y) >= 40`
4. prediction is the positive branch of `prefix_if_negative`, i.e. plain `x - y`

Full-train support:

| subfamily | support | gold match | error |
| --- | ---: | ---: | ---: |
| `quote_prefix_if_negative_large_positive` | 2 | 2 | 0 |

Recovered row:

| id | query | answer |
| --- | --- | --- |
| `b7b1d1a8` | `74"17` | `57` |

## Why these stay answer-only

Both subfamilies are still only support `2`.

That is enough for conservative answer-level recovery because the prompts are exact, the splits are query-observable, and empirical error is zero.  
But it is not enough to upgrade them to `verified_trace_ready`.

## What remains withheld

After this sweep, the only mechanical support-2 near-miss still visible in the symbol search is:

- `45dbc1cc` under `- :: y_minus_x :: plain`

It was **not** adopted because the surviving split depends on a much weaker `sum>=100` bucket and does not form as natural an operator-local branch as the recoveries above.

So the thin support-2 sweep is effectively exhausted:

- safe recovered here: `2`
- intentionally withheld near-miss: `1`

## Counts after recovery

- overall: `6081 verified / 1147 answer_only / 2246 manual / 26 exclude`
- symbol: `110 verified / 141 answer_only / 1293 manual / 11 exclude`
- pass1 manual pack: `498 rows`
  - `334` `symbol_numeric_same_op`
  - `118` `binary_low_gap`
  - `46` `symbol_glyph_multiset`

## Artifacts

- `artifacts/symbol_thin_support2_subfamily_support_v1.csv`
- `artifacts/symbol_thin_support2_subfamily_candidates_v1.csv`

## Decision

Adopt the two prompt-exact support-2 slices above as `answer_only_keep`, and keep the remaining `45dbc1cc` near-miss on hold.

This closes the current mechanizable symbol subgroup pass: what remains is mostly `:` / custom-op / operator-embedded manual tail, not another clean repeated micro-family.
