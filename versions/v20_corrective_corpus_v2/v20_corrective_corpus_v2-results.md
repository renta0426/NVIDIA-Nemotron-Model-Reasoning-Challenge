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
- Corrective training run: **pending**
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
