# cuda-train-data-analysis-v1 symbol single-example tail hold

## Purpose

After report 58, re-read the last manual `numeric_2x2` rows where:

- the gold answer still appears in the current prompt-backed candidate set
- but `same_operator_example_count == 1`

This is the final thin tail that still looks superficially recoverable.

## Rows checked

| id | operator | query | gold | competing candidate set |
| --- | --- | --- | --- | --- |
| `45dbc1cc` | `-` | `98-63` | `-35` | `-35`, `-6173` |
| `4cb5e927` | `-` | `69-49` | `-20` | `-20`, `20` |
| `2afebbc3` | `/` | `18/52` | `16` | `16`, `34` |
| `81c7ba7a` | `?` | `90?76` | `?14` | `14`, `?14` |
| `d1bd7478` | `:` | `37:67` | `30` | `-30`, `30`, `37`, `:30` |
| `64fe405e` | `<` | `32<33` | `1` | `-1`, `1`, `32`, `<1` |
| `74fff108` | `^` | `65^16` | `49` | `-49`, `16`, `49`, `^49` |
| `55f19327` | `:` | `77:38` | `1` | `-39`, `1`, `38`, `39`, `:39` |

## Decision

- promoted rows: `0`
- newly excluded rows: `0`
- decision: keep all `8` rows in `manual_audit_priority`

## Why they stay manual

### 1. One same-op example is still too thin

Each row has only one same-operator example, and that single example still allows multiple incompatible families.

Examples:

- `4cb5e927`: one negative `-` example cannot distinguish `prefix_always_abs` from `prefix_if_negative`
- `81c7ba7a`: one prefixed `?` example cannot prove whether positive queries should keep or drop the prefix
- `74fff108`: one positive `^` example cannot decide whether the negative branch should prefix the operator

### 2. Some rows are not even arithmetic-family unique at the answer level

- `45dbc1cc` still admits both subtraction-style and `x_mul_y_minus1` style fits
- `2afebbc3` still admits both modulo-style and absolute-difference style fits
- `55f19327` still admits modulo and difference interpretations simultaneously

### 3. README accuracy policy blocks guessy promotion

Per `README.md`, final score is direct answer accuracy.

So the curation rule here stays conservative:

- if prompt evidence does not uniquely justify the answer-level branch, do **not** promote
- if prompt evidence does not cleanly contradict gold, do **not** exclude either

## Exhaustion note

With this pass, the current prompt-backed symbol sweep is exhausted in both directions:

- multi-example gold-hit tail: already closed in report 58
- single-example gold-hit tail: now fully reviewed and held

So the remaining symbol manual queue is no longer a thin arithmetic cleanup problem.  
It is a genuinely unresolved operator-specific tail.

## Counts after hold

- overall: `6086 verified / 1151 answer_only / 2236 manual / 27 exclude`
- symbol: `110 verified / 145 answer_only / 1289 manual / 11 exclude`
- pass1 manual pack: `493 rows`
  - `330` `symbol_numeric_same_op`
  - `117` `binary_low_gap`
  - `46` `symbol_glyph_multiset`

## Decision

Close the current symbol tail cleanup loop here.

The next useful work is not another thin-family scan, but true round2 manual clustering over the remaining custom-op / operator-embedded families.
