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

- `glyph_len5` should **not** be treated as trace-ready under the current transducer probe.
- In the latest curation pass, the remaining non-suspect glyph rows were moved to `answer_only_keep`, not because the latent rule was solved, but because `README.md` scores final boxed answers and no concrete suspect signal was found.
- Human review should still focus on discovering smaller subfamilies before any further automatic solver is trusted.
