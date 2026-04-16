# v20_corrective_corpus_v2 results

> Repository note: canonical challenge contract lives in `README.md`.
> This version prepares a **single-file corrective training bundle** for the Kaggle direct-training path and preserves the submission target as `submission.zip`.
> Measured validation / proxy / leaderboard scores for this version must be recorded here after each run.

## Purpose

- Base strategy source: `A-Open-ProgressPrizePublication/v20_to_088_strategy.md`
- Focus:
  - keep the proven `bit_structured_byte_formula` gain
  - keep a lighter `bit_other` line
  - remove the expensive ineffective symbol main-line overlay
  - add small guardrail anchors for measured regressions in numeral / gravity / unit / symbolic cryptarithm / symbol prefix
- Rationale from `A-Open-ProgressPrizePublication/README.md` and the v1 measured run:
  - binary remains the best upside
  - token budget is constrained by Kaggle runtime
  - easy-family regressions must be actively prevented

## Implementation

- Script: `versions/v20_corrective_corpus_v2/reproduce_v20_corrective_corpus_v2.py`
- Style: single-file monolith
- Inputs:
  - `cuda-train-data-analysis-v1/artifacts/train_recommended_learning_target_v1.csv`
  - `versions/v20_corrective_corpus_v1/outputs/smoke_with_validation/artifacts/corrective_selection.csv`
  - `A-Open-ProgressPrizePublication/result/results-v20/validation.csv`
  - `A-Open-ProgressPrizePublication/result/results-v20-kaggle-v20-sft-repro-0414-104905/validation.csv`
  - `A-Open-ProgressPrizePublication/result/leaderboard_proxy_eval_v20/artifacts/leaderboard_proxy_eval_row_level.csv`
  - `A-Open-ProgressPrizePublication/result/leaderboard_proxy_eval_kaggle-v20-sft-repro-0414-104905/artifacts/leaderboard_proxy_eval_row_level.csv`
- Outputs:
  - `corrective_selection.csv`
  - `corrective_overlay_unique.jsonl`
  - `corrective_overlay_repeated.jsonl`
  - `anchor_watchlist.csv`
  - `corrective_overlay_summary.json`
  - `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v2_bundle.jsonl`

## Current status

- Implementation: **ready**
- Corpus generation smoke: **done**
- Corpus generation with bundle: **done**
- Corrective training run: **done**
- `submission.zip` export: **pending**

## Strategy delta vs v1

- Keep:
  - `binary_structured_core`
  - `binary_other_light`
- Add:
  - `guardrail_numeral_subtractive`
  - `guardrail_gravity_fragile`
  - `guardrail_unit_fragile`
  - `guardrail_cryptarithm_symbolic`
  - `guardrail_symbol_prefix`
- Remove from main-line:
  - broad `numeric_2x2`
  - broad `glyph_len5`

The design target is not a larger overlay. It is a **smaller, more selective reallocation** after the v1 measured result showed:

- binary proxy improved materially
- symbol did not improve
- easy-family regressions appeared

## 2026-04-15 corpus generation smoke: `smoke_bundle_v2`

Commands:

```bash
uv run python -m py_compile versions/v20_corrective_corpus_v2/reproduce_v20_corrective_corpus_v2.py
uv run python versions/v20_corrective_corpus_v2/reproduce_v20_corrective_corpus_v2.py --run-name smoke_bundle_v2
uv run python versions/v20_corrective_corpus_v2/reproduce_v20_corrective_corpus_v2.py --run-name smoke_bundle_v2 --write-training-bundle
```

Observed summary:

- unique rows: `322`
- repeated rows: `690`
- selected buckets:
  - `binary_structured_core = 160`
  - `binary_other_light = 64`
  - `guardrail_numeral_subtractive = 24`
  - `guardrail_gravity_fragile = 24`
  - `guardrail_unit_fragile = 24`
  - `guardrail_cryptarithm_symbolic = 24`
  - `guardrail_symbol_prefix = 2`
- repeated overlay buckets:
  - `binary_structured_core = 480`
  - `binary_other_light = 64`
  - `guardrail_numeral_subtractive = 48`
  - `guardrail_gravity_fragile = 24`
  - `guardrail_unit_fragile = 24`
  - `guardrail_cryptarithm_symbolic = 48`
  - `guardrail_symbol_prefix = 2`
- selected rows still wrong in current measured run:
  - `proxy_failed_selected = 5`
  - `validation_failed_selected = 1`
- hard blacklist:
  - `binary_structured_core`: `06b5da9f`, `2817d770`
  - `binary_other_light`: `6a333ed6`

Kaggle single-file bundle:

- path: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v2_bundle.jsonl`
- base examples: `7830`
- overlay examples: `690`
- total examples: `8520`
- batch size: `32`
- total steps: `267`
- total tokens: `32083353`
- max seq len: `7971`
- retokenized overlay problems not present in base v20 snapshot: `29`

Compared with v1 bundle:

- total steps: `301 -> 267`
- total tokens: `39030839 -> 32083353`
- overlay examples: `1792 -> 690`

Artifacts:

- `versions/v20_corrective_corpus_v2/outputs/smoke_bundle_v2/artifacts/corrective_selection.csv`
- `versions/v20_corrective_corpus_v2/outputs/smoke_bundle_v2/artifacts/corrective_overlay_unique.jsonl`
- `versions/v20_corrective_corpus_v2/outputs/smoke_bundle_v2/artifacts/corrective_overlay_repeated.jsonl`
- `versions/v20_corrective_corpus_v2/outputs/smoke_bundle_v2/artifacts/anchor_watchlist.csv`
- `versions/v20_corrective_corpus_v2/outputs/smoke_bundle_v2/artifacts/corrective_overlay_summary.json`
- `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v2_bundle.jsonl`

## Measured score ledger

| run | data change | validation | proxy | public leaderboard | notes |
| --- | --- | ---: | ---: | ---: | --- |
| smoke_bundle_v2 | budget-neutral binary + guardrail corpus | pending | pending | pending | bundle generated; `32.08M` tokens / `267` steps |
| kaggle-v20-sft-repro-v2-0415 | v2 bundle on Kaggle direct SFT | `839 / 950 = 0.8832` | `176 / 200 = 0.8800` | user-reported `0.83-0.84` range | validation up vs v20 / v1, but proxy fell back to v20 and public score softened |

## 2026-04-16 measured run analysis: `kaggle-v20-sft-repro-v2-0415`

README and the A-Open publication both point to the same core truth: **bit manipulation is the main score lever**. This v2 run did improve the 950-row validation notebook style score, but the gain came from easy / formatting-sensitive slices more than from the high-value bit slice.

### Score deltas

- Validation:
  - v20: `837 / 950 = 0.8811`
  - v1: `838 / 950 = 0.8821`
  - v2: `839 / 950 = 0.8832`
- Leaderboard proxy:
  - v20: `176 / 200 = 0.8800`
  - v1: `178 / 200 = 0.8900`
  - v2: `176 / 200 = 0.8800`
- Public leaderboard:
  - user-reported: v2 dropped into the `0.83-0.84` band, slightly below the prior run

The local signal is therefore split:

- validation says **+1 vs v1**
- proxy says **-2 vs v1**, back to baseline v20
- public leaderboard also moved in the **proxy direction**, not the validation direction

### Category movement on the 950-row validation set

- Gains vs v1:
  - `cryptarithm_deduce`: `4 -> 7`
  - `gravity`: `158 -> 159`
  - total remained perfect for `cipher`, `equation_numeric_deduce`, `equation_numeric_guess`, and `cryptarithm_guess`
- Regressions vs v1:
  - `bit_manipulation`: `150 -> 149`
  - `numeral`: `148 -> 147`
  - `unit_conversion`: `171 -> 170`

Interpretation:

- the guardrail line **did** buy back several fragile easy / symbolic rows
- but it did **not** preserve the stronger bit line that made v1 interesting

### Proxy movement by family

- v20 -> v1:
  - binary: `76 -> 80`
  - symbol: `24 -> 23`
  - unit: `18 -> 17`
- v1 -> v2:
  - binary: `80 -> 77`
  - symbol: `23 -> 23`
  - unit: `17 -> 18`

Within binary, the main damage is concentrated exactly where the strategy was supposed to stay strong:

- `bit_structured_byte_formula`: `26/31` in v1-set summary for v1-equivalent run fell back to `24/31` in v2
- on solver-family rows:
  - `binary_structured_byte_formula`: `9/10 -> 7/10`
  - `binary_bit_permutation_bijection`: `24/24 -> 23/24`

So v2 did **not** mainly fail from symbol/template collapse. It mostly failed because the binary content line softened.

### What improved in raw outputs

The best v2 gains are real, but they are mostly **format/guardrail recoveries** or easy-family stabilizations:

- `0133bcec`
  - base/v1 ended with malformed `\\boxx` / `\\boxes` style endings
  - v2 cleanly finished with `\\boxed{\\([#}`
- `065abaf6`, `0dcfd566`
  - same pattern: v1 had malformed boxing and extraction failure
  - v2 returned a clean `\\boxed{...}` answer
- `081ad3f3`
  - v1 incorrectly decomposed `24` as `XXIIII -> XXIII`
  - v2 restored the subtractive step `4 -> IV`
- `0fd289d8`
  - v1 drifted into a repeated `+ 0.0000000` tail and predicted `0.000000`
  - v2 returned to the normal multiplication trace and produced `92.002`, which is correct under metric tolerance

These are good signs for the guardrail concept, but they are mostly **not the README's primary upside slice**.

### What regressed in raw outputs

The losses are much more damaging because they are mostly **bit content regressions with valid boxing still present**:

- `0520a6ec`
  - v1 used the correct first rule line `AND-NOT15`
  - v2 drifted to `AND-NOT25`, changing the first bit and outputting `01100001`
- `0dd5caf4`
  - v2 inserted `6 default 1 = 1`, turning an all-zero answer into `00000010`
- `1496dfeb`
  - v2 fell into multiple `default 1` decisions and emitted `11111100` instead of `00000000`
- `17fd9612`
  - v2 dropped the operator detail for intermediate rows (`1 05 = 0`, `2 16 = 0`, `3 27 = 0`) and lost one active bit
- `c30a782a`
  - v1 had the correct `AND-NOT` sequence; v2 inserted `default 1` at bit 3 and changed `01000110 -> 01010110`
- `b9500f41`
  - v2 inserted `4 default 1 = 1`, turning a pure permutation answer into `11111000`

This is the key point: **most of the binary regressions are not extraction failures**. The model still outputs `\\boxed{...}`. The wrong answer is produced because the step-by-step trace itself drifted to a weaker rule.

There is also one clear format-loop regression:

- `8e5d6fe6`
  - v1 returned `\\boxed{10000111}`
  - v2 looped on `OR-NOT50 = OR-NOT05 ...`, lost boxing, and the metric fell back to numeric `50`

So the binary damage is mostly **content drift**, with a small amount of **format looping**.

### Easy-family regressions in v2

v2 also introduced new easy-task extraction failures:

- `1112ec96`, `18840879`
  - the numeral reasoning is actually correct up to `Result: IV` / `Result: XC`
  - but the ending regressed from `\\boxed{...}` to `\\box`, so the metric extracted `0`
- `0a0698b2`
  - the unit-conversion arithmetic tail became `44. -revised`
  - this is not a reasoning miss; it is a response-surface corruption at the final answer

That means the guardrail pack helped some formatting-sensitive symbolic rows, but it did not fully remove formatting/template instability. It merely moved it around.

### Bottom line

v2 is **not** a good main-line promotion despite the slightly higher `839/950` validation score.

- It traded a small amount of easy/symbolic recovery for a meaningful loss of binary strength.
- The proxy benchmark, which was built to align more closely with README-style leaderboard behavior, caught that drop immediately.
- The user-reported public leaderboard decline matches the proxy, so the proxy signal looks more trustworthy than the raw validation gain here.

### Practical takeaway for the next iteration

The right next move is **not** “more guardrails”. It is:

1. restore the v1-strength binary structured line
2. keep only the tiny subset of guardrails that directly fix malformed boxing / response-surface corruption
3. avoid any corpus change that increases `default 1`, rule drift, or operator substitution on binary traces
