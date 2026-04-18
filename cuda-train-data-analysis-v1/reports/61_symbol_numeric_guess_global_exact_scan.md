# cuda-train-data-analysis-v1 numeric guess global exact scan

## Purpose

After confirming that `symbol_equation >= 90% verified` is blocked by the published `*_guess` categories, re-check whether the remaining `equation_numeric_guess` slice still hides any **strict verified** rows under a broader but still exact assumption:

- ignore operator identity entirely
- ask whether one operator-agnostic arithmetic/rendering rule fits **all prompt examples**
- and whether that same exact rule uniquely yields the query answer

If such rows existed, they would be the best remaining chance to upgrade some `same_operator_example_count = 0` numeric rows beyond `answer_only_keep`.

## Slice scanned

- input slice:
  - `symbol_equation`
  - `numeric_2x2`
  - `selection_tier = answer_only_keep`
  - `symbol_same_operator_example_count = 0`
- row count: `136`

This is exactly the current `equation_numeric_guess` answer-only slice.

## Candidate library

The scan used a compact exact library over two-digit inputs:

- concatenation / reverse concatenation
- addition / subtraction / absolute difference / multiplication
- `+1` / `-1` variants
- `max(x,y) % min(x,y)`
- reversed-input and reversed-output variants of the above

The test was intentionally strict:

1. one spec must fit **every example line** in the row
2. all surviving specs must imply the **same** query answer
3. only gold-matching rows would be considered promotion candidates

## Result

- rows with a unique operator-agnostic exact query prediction: `23`
- rows where that unique exact prediction matched gold: `0`

So the scan found **zero** new strict promotion candidates.

## Interpretation

This is useful negative evidence.

It means the remaining `equation_numeric_guess` rows are not just waiting for one more tiny exact arithmetic/template sweep. Even after dropping operator identity entirely and allowing a moderate family library, the surviving exact fits either:

- predict the wrong answer, or
- still do not collapse to the stored gold answer

So the residual `guess` slice is not a hidden cache of overlooked exact prompt-grounded rules.

## Example failure modes

Representative rows from the scan:

| id | query | gold | unique exact prediction | note |
| --- | --- | --- | --- | --- |
| `4e840a1a` | `15+53` | `38` | `69` | prompt examples support `add+1`, not the gold answer |
| `35e12b34` | `65\`48` | `041` | `17` | row-local subtraction fits examples, but not gold |
| `66a0856f` | `74[36` | `38` | `7436` | surviving exact fits are concatenation variants, not gold |
| `c6961082` | `69]99` | `6831` | no gold-matching exact singleton | investigation remains inference-shaped |

These failures reinforce that the current `answer_only_keep` assignment is already conservative: the rows may still be useful answer-level supervision, but this exact scan does not justify `verified_trace_ready`.

## Decision

Keep the `equation_numeric_guess` residual as non-verified.

Combined with the category-level ceiling report (`reports/60_symbol_verified_ceiling_from_problem_categories.md`), this scan strengthens the conclusion that 90% verified is blocked by missing evidence, not by an overlooked exact numeric pass.
