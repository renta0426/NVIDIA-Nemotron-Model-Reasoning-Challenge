# Symbol subtype notes

## Current split

- `glyph_len5`: 823 rows
- `numeric_2x2`: 732 rows

## glyph_len5 observations

- Query length is fixed at 5 symbolic characters.
- Answer length is not fixed: 1->50 rows, 2->230 rows, 3->268 rows, 4->275 rows.
- This strongly suggests the rule is **not** simple 1:1 character substitution.
- Immediate audit target: inspect whether outputs are produced by pair grouping, deletion, or operator-conditioned compression.

## numeric_2x2 observations

- Query pattern is effectively `ddOdd` where `d` is a digit and `O` is one symbolic operator.
- Operator distribution is broad; the largest buckets are:
  - `-`: 121
  - `+`: 116
  - `*`: 102
- Most outputs are numeric, but some operators emit an operator-prefixed answer (for example `}38`, `` `82``).
- Therefore `numeric_2x2` should be split at least by operator family before any solver attempt.

## Practical next move

1. Build per-operator audit slices for `numeric_2x2`.
2. Inspect 20-30 rows each for `-`, `+`, `*`, then the operator-prefixed cases.
3. Separately inspect `glyph_len5` for compression / pairing style rules.
