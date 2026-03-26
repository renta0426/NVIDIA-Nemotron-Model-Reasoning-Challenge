# cuda-train-data-analysis-v1 symbol `*` prefix-if-negative recovery

## Purpose

Revisit the unresolved `symbol_equation / numeric_2x2` `*` tail after report 36.

Report 36 checked the 3-digit non-embedded `*` cluster and found no reusable product-like family.  
This follow-up uses a different entry point: a generalized search over existing operator-aware winning specs, looking for **query-observable zero-error subfamilies** that stay within the `README.md` accuracy-first bar.

## Rule

Start from rows that satisfy all of the following:

1. `symbol_equation / numeric_2x2`
2. query operator is `*`
3. `same_operator_example_count == 1`
4. the single same-operator example supports  
   `x_minus_y :: prefix_if_negative`

Interpret the formatter as:

- if `x >= y`, predict plain `x - y`
- if `x < y`, predict `"*" + str(y - x)`

This is the exact operator-local branch that explains:

- `28*78 = *50`
- `23*98 = *75`
- `97*75 = 22`

while still staying below trace-level confidence.

## Why the subgroup is needed

The broader `* :: x_minus_y :: prefix_if_negative` slice is **not** globally safe.

There is a hard conflict inside the operator:

- `6f37d7be`: `92*91 -> 01`

Its same-operator evidence count is `2`, and the same winning spec predicts `1`, not `01`.

So the safe recovery is **not** the whole `*` family.  
It is only the narrower `same_operator_example_count == 1` subgroup.

## Full-train support

| subfamily | support | gold match | error |
| --- | ---: | ---: | ---: |
| `star_prefix_if_negative_same_bucket1` | 3 | 3 | 0 |

Conservative adoption rule:

- `support_rows >= 3`
- `error_rows = 0`

## Recovered manual rows

| id | query | answer |
| --- | --- | --- |
| `157228d7` | `50*15` | `35` |
| `cf84c023` | `45*32` | `13` |
| `d22f2d08` | `47*73` | `*26` |

## Why this stays answer-only

Each recovered row still has only one same-operator example.

So although the operator-local subgroup is repeated and zero-error on train, the prompt evidence is still thinner than we want for `verified_trace_ready`.  
Per `README.md`, final score is direct answer accuracy, so the conservative interpretation is:

- the answers are safe enough to keep
- the reasoning trace is still too thin to certify as verified supervision

## Counts after recovery

- overall: `6081 verified / 1140 answer_only / 2253 manual / 26 exclude`
- symbol: `110 verified / 136 answer_only / 1298 manual / 11 exclude`
- pass1 manual pack: `503 rows`
  - `339` `symbol_numeric_same_op`
  - `118` `binary_low_gap`
  - `46` `symbol_glyph_multiset`

## Artifacts

- `artifacts/symbol_star_prefix_if_negative_support_v1.csv`
- `artifacts/symbol_star_prefix_if_negative_candidates_v1.csv`

## Decision

Adopt the `*` same-bucket-1 prefix-if-negative slice as `answer_only_keep` only.

This does **not** contradict report 36.  
Report 36 rejected a different `*` residual (`3`-digit non-embedded outputs) that still had no reusable family. The new gain comes from a narrower operator-local subtraction branch that only became visible after scanning winning-spec subfamilies directly.
