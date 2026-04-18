# cuda-train-data-analysis-v1 strict symbol verified ceiling

## Purpose

Re-check whether the user target of `symbol_equation verified >= 90%` is reachable **without weakening the existing verified standard**.

The relevant standard in this repo is:

- `README.md`: leaderboard score is final boxed-answer accuracy
- `FINAL_SUMMARY_REPORT.md`: `verified_trace_ready` is reserved for rows with sufficiently safe reusable trace evidence, not merely answer-level plausibility

So the question here is not "can we guess more final answers?", but "can we defend a trace-safe verified promotion?"

## Published category split

`A-Open-ProgressPrizePublication/nemotron/problems.jsonl` maps every `symbol_equation` row to one of four published categories:

| category | rows | subtype |
| --- | ---: | --- |
| `equation_numeric_deduce` | 596 | `numeric_2x2` |
| `equation_numeric_guess` | 136 | `numeric_2x2` |
| `cryptarithm_deduce` | 659 | `glyph_len5` |
| `cryptarithm_guess` | 164 | `glyph_len5` |

Total: `596 + 136 + 659 + 164 = 1555`.

In the current `train_row_analysis_v1.csv` ledger, the `glyph_len5` slice also sits entirely in the `same_operator_example_count = 0` regime, i.e. the query operator never appears verbatim in the examples.

## Ceiling arithmetic

To reach `90% verified`, `symbol_equation` needs at least:

- `ceil(1555 * 0.9) = 1400` verified rows

Two useful ceilings follow immediately.

### 1. If all published `*_guess` rows stay non-verified

Then the strict prompt-grounded ceiling is:

- `596 + 659 = 1255`
- `1255 / 1555 = 80.71%`

This is the ceiling if we refuse to treat category-level fallback guesses as trace-safe evidence.

### 2. Even if every numeric row becomes verified

Suppose we solve **all** `numeric_2x2` rows:

- `596 + 136 = 732`

and also solve **all** `cryptarithm_deduce` rows:

- `732 + 659 = 1391`
- `1391 / 1555 = 89.45%`

This is still below `90%`.

Therefore, under the current strict verified standard, the task cannot be completed unless at least:

- `1400 - 1391 = 9`

rows from `cryptarithm_guess` become defensibly verified.

## Why `guess` rows are not currently strict verified

The published reasoners in `A-Open-ProgressPrizePublication/nemotron/reasoners/` use explicit fallback assumptions on unknown query operators:

- `equation_numeric.py`
  - if the question operator is not found in the examples, it says:
    - "We will use absolute difference for the question operator."
- `cryptarithm.py`
  - if the question operator is unknown, it says:
    - "As the question operator is unknown, we default to concatenation."

These are useful answer-generation heuristics, but they are **not** strong enough to justify `verified_trace_ready`.

## Replay check on glyph rows

A replay of the existing `cryptarithm_deduce.py` solver over all `glyph_len5` rows found:

- `214` rows with some non-null prediction
- `99` exact gold matches
- `103` one-second timeouts

But those `99` matches do **not** rescue the 90% target:

- `95` are in `cryptarithm_deduce`
- `4` are in `cryptarithm_guess`
- all `99` lie in the current `same_operator_example_count = 0` glyph regime

So this replay mainly confirms the existing answer-only behavior. It does not produce a new prompt-grounded verified family.

## Case-by-case missing evidence

### 1. `equation_numeric_guess` (`136` rows)

Need:

- trustworthy auxiliary evidence for unseen query operators, or
- a generator-level proof that the fallback operator family is fixed and reusable

Absent that, published fallback-to-abs-diff behavior remains answer-level only.

### 2. `cryptarithm_deduce` (`659` rows)

Need:

- a broader cross-operator exact latent-family solver
- that proves the query operator's behavior from the examples, not by fallback

Current concat-oriented and grouped glyph passes are far from this.

### 3. `cryptarithm_guess` (`164` rows)

Need:

- external generator logic,
- or auxiliary paired evidence for unseen query operators,
- or another trustworthy source that fixes the query operator semantics row-by-row

Without that extra source, promoting even the minimum required `9` rows would be guess-shaped rather than verified.

## Decision

Do **not** claim `symbol_equation >= 90% verified` under the current strict standard.

The bottleneck is no longer "one more local sweep." It is a category-level evidence gap:

- either obtain trustworthy external generation logic for `cryptarithm_guess`
- or relax the verified definition

Until one of those happens, the conservative ledger should remain below `90%`.
