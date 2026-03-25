# Glyph probe notes

## Probe tried

- Hypothesis: each input symbol in `glyph_len5` maps row-locally to either
  - empty string, or
  - one output symbol,
  and the final answer is the concatenation across the 5 input positions.

## Result

- Tested over all `glyph_len5` rows: **0 / 823 solved**

## Interpretation

- `glyph_len5` is not a simple deletion + substitution transducer.
- The rule likely depends on
  - pair/group interactions,
  - operator-like role assignment among symbols,
  - or context-sensitive rewriting.

## Practical consequence

- `glyph_len5` should remain in `manual_audit_priority`.
- Human review should focus on discovering smaller subfamilies before any further automatic solver is trusted.
