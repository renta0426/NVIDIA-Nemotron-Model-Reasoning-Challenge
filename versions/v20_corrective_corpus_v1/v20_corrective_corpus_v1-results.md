# v20_corrective_corpus_v1 results

> Repository note: canonical challenge contract lives in `README.md`.
> This version prepares a **single-file corrective overlay corpus** for the Kaggle direct-training v20 reproduction path and preserves the submission target as `submission.zip`.
> Measured leaderboard / validation scores for this version must be recorded here after each run.

## Purpose

- Base strategy source: `A-Open-ProgressPrizePublication/v20_to_088_strategy.md`
- Focus: keep the v20 base corpus fixed and add a narrow corrective overlay for:
  - `bit_structured_byte_formula`
  - `bit_other`
  - `numeric_2x2`
  - `glyph_len5`
- Rationale from `A-Open-ProgressPrizePublication/README.md`:
  - bit manipulation remains the main upside
  - token-efficient traces are likely needed for longer binary families
  - symbol / character conversion remains weak

## Implementation

- Script: `versions/v20_corrective_corpus_v1/reproduce_v20_corrective_corpus_v1.py`
- Style: single-file monolith
- Inputs:
  - `cuda-train-data-analysis-v1/artifacts/train_recommended_learning_target_v1.csv`
  - `cuda-train-data-analysis-v1/artifacts/symbol_manual_audit_queue_v1.csv`
  - `A-Open-ProgressPrizePublication/leaderboard_proxy_eval_v20/artifacts/leaderboard_proxy_eval_row_level.csv`
  - optional `validation.csv` from a real run
- Outputs:
  - `corrective_selection.csv`
  - `corrective_overlay_unique.jsonl`
  - `corrective_overlay_repeated.jsonl`
  - `anchor_watchlist.csv`
  - `corrective_overlay_summary.json`

## Current status

- Implementation: **ready**
- Corpus generation smoke: **done**
- Corrective training run: **pending**
- `submission.zip` export: **pending**

## 2026-04-14 corpus generation smoke

Commands:

```bash
python -m py_compile versions/v20_corrective_corpus_v1/reproduce_v20_corrective_corpus_v1.py
uv run python versions/v20_corrective_corpus_v1/reproduce_v20_corrective_corpus_v1.py --run-name smoke_default
uv run python versions/v20_corrective_corpus_v1/reproduce_v20_corrective_corpus_v1.py \
  --run-name smoke_with_validation \
  --validation-csv v20_mlx_repro_v1/outputs/fastbench_strat8_mt2048/adapter_validation/validation.csv
```

Observed summary:

- `smoke_default`
  - unique rows: `544`
  - repeated rows: `1792`
  - buckets:
    - `bit_structured_byte_formula = 192`
    - `bit_other = 192`
    - `symbol_numeric_2x2 = 96`
    - `symbol_glyph_len5 = 64`
  - `proxy_failed_selected = 17`
  - `validation_failed_selected = 0`
- `smoke_with_validation`
  - unique rows: `544`
  - repeated rows: `1792`
  - `proxy_failed_selected = 17`
  - `validation_failed_selected = 2`
- `smoke_bundle_for_kaggle`
  - single-file bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v1_bundle.jsonl`
  - bundle size: about `242 MB`
  - total examples: `9622`
  - total steps: `301`
  - total tokens: `39030839`
  - retokenized overlay problems not present in base v20 snapshot: `94`

Artifacts:

- `versions/v20_corrective_corpus_v1/outputs/smoke_default/artifacts/corrective_selection.csv`
- `versions/v20_corrective_corpus_v1/outputs/smoke_default/artifacts/corrective_overlay_unique.jsonl`
- `versions/v20_corrective_corpus_v1/outputs/smoke_default/artifacts/corrective_overlay_repeated.jsonl`
- `versions/v20_corrective_corpus_v1/outputs/smoke_default/artifacts/anchor_watchlist.csv`
- `versions/v20_corrective_corpus_v1/outputs/smoke_with_validation/artifacts/corrective_overlay_summary.json`
- `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v1_bundle.jsonl`

## Score ledger

| run | data change | validation | proxy | public leaderboard | notes |
| --- | --- | ---: | ---: | ---: | --- |
| smoke_default | corrective overlay corpus only | pending | pending | pending | corpus generation smoke only; no training run |
| smoke_with_validation | same overlay + local fail upweighting | pending | pending | pending | local `validation.csv` path accepted; no training run |
| smoke_bundle_for_kaggle | full v20 base + corrective overlay single-file bundle | pending | pending | pending | Kaggle upload artifact generated under `nemotron/training/sft/` |
