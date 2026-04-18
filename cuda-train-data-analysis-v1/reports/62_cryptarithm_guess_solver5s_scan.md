# cuda-train-data-analysis-v1 cryptarithm guess solver 5s scan

## Purpose

Re-test the most plausible remaining escape hatch for the `90% verified` target:

- maybe some `cryptarithm_guess` rows are still prompt-solvable
- even though the query operator is unseen
- because the example constraints collapse to a unique or near-unique answer anyway

To check that, run the existing published `cryptarithm_deduce.py` solver on the full `cryptarithm_guess` split with a more patient per-row timeout and inspect whether any exact gold matches look strict enough for `verified_trace_ready`.

## Slice scanned

- category: `cryptarithm_guess`
- rows: `164`
- solver:
  - published `A-Open-ProgressPrizePublication/nemotron/investigators/cryptarithm_deduce.py`
  - unique-mapping branch first
  - non-unique fallback second
  - `max_solutions = 1000`
  - per-row timeout: `5s`

## Result

- timeouts: `2`
- non-null predictions: `39`
- exact gold matches: `4`

Matched rows:

| id | prediction | mode | answer_count | top_count | total_solutions |
| --- | --- | --- | ---: | ---: | ---: |
| `31678582` | `<:)` | `unique` | 5 | 1 | 5 |
| `55f4fa64` | `{{!?` | `unique` | 32 | 21 | 95 |
| `6cc5dafb` | `)(` | `unique` | 5 | 1 | 5 |
| `bbcd608d` | `''[` | `unique` | 5 | 1 | 5 |

## Critical observation

There were **zero** strict singleton matches:

- exact gold matches with `answer_count = 1`: `0`

Three of the four matched rows are especially weak:

- `answer_count = 5`
- `top_count = 1`
- `total_solutions = 5`

So the gold answer was only one of several equally supported answers.

The remaining row (`55f4fa64`) is stronger than that, but still not strict:

- `answer_count = 32`
- `top_count = 21`
- `total_solutions = 95`

That is answer-level consensus, not trace-safe uniqueness.

## Interpretation

This matters because the category-level ceiling report showed that we would need at least `9` defensible `cryptarithm_guess` verified promotions to break `90%` overall.

This scan does **not** get close:

- only `4` gold matches in total
- and none of them are singleton / uniquely forced by the solver

So even a deeper prompt-only replay of the current cryptarithm solver does not yield the missing verified tranche.

## Decision

Do not promote any `cryptarithm_guess` rows from this scan to `verified_trace_ready`.

The scan is still useful because it narrows the remaining evidence gap:

- the bottleneck is not just runtime
- the bottleneck is unresolved answer ambiguity under the prompt itself

That keeps the 90% target blocked unless some stronger external source fixes query-operator semantics for part of `cryptarithm_guess`.
