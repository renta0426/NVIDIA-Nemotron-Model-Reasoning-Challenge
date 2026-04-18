# cuda-train-data-analysis-v1 cryptarithm guess extended solver scan

## Purpose

One remaining possibility was that the interrupted local scratch work might still recover a strict tranche of `cryptarithm_guess` rows that the published `cryptarithm_deduce.py` solver misses.

So this pass re-ran the full `cryptarithm_guess` split with a broader local solver family:

- addition / abs-diff / multiplication
- signed subtraction in both directions
- concatenation / reverse concatenation
- reversed operands
- reversed outputs
- non-unique symbol-to-digit assignment

This is broader than the published solver and directly tests whether the missing `>= 9` verified rows are hiding behind a solver-capability gap rather than a data-evidence gap.

## Slice scanned

- category: `cryptarithm_guess`
- rows: `164`
- per-row timeout: `20s`
- search style:
  - non-unique mapping allowed
  - operator families extended beyond the published solver
  - query operator allowed to range over the extended family when unseen

## Result

- timeouts: `37`
- non-null predictions: `92`
- exact gold matches: `0`
- strict singleton matches: `0`
- strict dominant matches: `0`

So the broader local solver did **not** produce even one defensible promotion candidate.

## Interpretation

This is strong negative evidence against the idea that `cryptarithm_guess` is blocked merely by an underpowered local solver.

Compared with the earlier published-solver replay:

- the broader solver returned **more** non-null answers
- but those extra answers did **not** improve gold agreement at all

That pattern is exactly what we would expect when the real bottleneck is missing query-operator evidence rather than missing arithmetic primitives.

## Decision

Do not promote any `cryptarithm_guess` rows from this scan.

Together with:

- `reports/60_symbol_verified_ceiling_from_problem_categories.md`
- `reports/62_cryptarithm_guess_solver5s_scan.md`
- `reports/63_official_generator_source_search.md`

this pass supports the same conclusion:

- the remaining gap is evidence-shaped, not solver-shaped
- and `symbol_equation >= 90% verified` is not defensible under the current strict standard

