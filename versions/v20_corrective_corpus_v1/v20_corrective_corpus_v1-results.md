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
- Corrective training run: **one measured run recorded**
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

## 2026-04-15 measured run: `kaggle-v20-sft-repro-0414-104905`

Result sources:

- validation:
  - `A-Open-ProgressPrizePublication/result/results-v20/results.csv`
  - `A-Open-ProgressPrizePublication/result/results-v20-kaggle-v20-sft-repro-0414-104905/results.csv`
  - `A-Open-ProgressPrizePublication/result/results-v20-kaggle-v20-sft-repro-0414-104905/validation.csv`
- leaderboard proxy:
  - `A-Open-ProgressPrizePublication/result/leaderboard_proxy_eval_v20/artifacts/leaderboard_proxy_v1_set_summary.json`
  - `A-Open-ProgressPrizePublication/result/leaderboard_proxy_eval_kaggle-v20-sft-repro-0414-104905/artifacts/leaderboard_proxy_v1_set_summary.json`
  - `A-Open-ProgressPrizePublication/result/leaderboard_proxy_eval_kaggle-v20-sft-repro-0414-104905/artifacts/leaderboard_proxy_eval_row_level.csv`

Measured scores:

- validation `837 / 950 = 88.1%` -> `838 / 950 = 88.2%`
- proxy `176 / 200 = 0.8800` -> `178 / 200 = 0.8900`
- public leaderboard: **not recorded in the current Git-visible snapshot**

Category / slice deltas:

- validation:
  - `bit_manipulation` `149/169 -> 150/169`
  - `cipher` `158/162 -> 162/162`
  - `cryptarithm_deduce` `6/71 -> 4/71`
  - `gravity` `159/159 -> 158/159`
  - `numeral` `149/149 -> 148/149`
- proxy:
  - `binary` `76/92 -> 80/92`
  - `symbol` `24/32 -> 23/32`
  - `unit` `18/18 -> 17/18`
  - target buckets:
    - `bit_structured_byte_formula` `23/31 -> 26/31`
    - `bit_other` `28/35 -> 28/35`
    - `numeric_2x2` `23/27 -> 22/27`
    - `glyph_len5` `1/5 -> 1/5`

Selected-row effect:

- validation rows that were explicitly selected into the corrective overlay:
  - `67/73 -> 65/73`
  - improved rows: `1`
  - regressed rows: `3`
- proxy rows that were explicitly selected into the corrective overlay:
  - `43/60 -> 46/60`
  - improved rows: `5`
  - regressed rows: `2`
- proxy selected target buckets only:
  - `bit_structured_byte_formula` `15/23 -> 18/23`
  - `bit_other` `14/15 -> 14/15`
  - `numeric_2x2` `13/17 -> 13/17`
  - `glyph_len5` `1/5 -> 1/5`

Raw-output reading:

- intended gain is real for structured binary:
  - `012fb81b`, `0520a6ec`, `0a50c4a8`, `59c78e51` all flipped from wrong to correct in proxy under `bit_structured_byte_formula`
  - `c30a782a` flipped from wrong to correct in `bit_other`
  - these are mostly **content fixes with 8-bit formatting preserved**, matching the original hypothesis that the binary issue was trace/content rather than boxed-format failure
- major remaining binary failure modes:
  - near-miss bit errors remain (`a6192d29`, `6a333ed6`)
  - one selected structured row collapsed catastrophically to a truncated numeric answer `7` (`2817d770`)
- symbol / character conversion did not improve:
  - `numeric_2x2` regressed from `23/27` to `22/27`
  - `glyph_len5` stayed at `1/5`
  - example: `d9bedb64` changed from correct `(\`-prefixed semantics preserved as `(1)` to incorrect `1`, dropping the operator/prefix
  - example: `a85864a9` still loops on repeated `</think> \\boxed{(\\}:` fragments and truncates to `(\\`
- spillover / collateral damage is visible outside the target buckets:
  - validation cryptarithm rows `065abaf6` and `0dcfd566` collapsed to short numeric output `5` after otherwise reasonable symbolic reasoning text
  - validation numeral row `081ad3f3` regressed from correct `XXIV` to `XXIII` by switching from `IV` handling to repeated `I`
  - validation gravity row `0fd289d8` regressed from near-correct `92.002` to `0.000000`
  - proxy unit row `626d6c5f` regressed from `19.001` to `18.001`

Interpretation:

- the corrective corpus **did improve the intended binary frontier**, especially `bit_structured_byte_formula`
- however, the current overlay weighting is **too asymmetric**:
  - it helps binary enough to raise proxy overall by `+2`
  - but it does **not** fix symbol conversion
  - and it introduces small but real regressions on easy / non-target numeric-symbolic families
- the run therefore validates the core hypothesis only partially:
  - **binary corrective data works**
  - **symbol corrective data as currently constructed does not**
  - **guardrail coverage for numeral / gravity / unit / symbolic cryptarithm is insufficient**

## Score ledger

| run | data change | validation | proxy | public leaderboard | notes |
| --- | --- | ---: | ---: | ---: | --- |
| smoke_default | corrective overlay corpus only | pending | pending | pending | corpus generation smoke only; no training run |
| smoke_with_validation | same overlay + local fail upweighting | pending | pending | pending | local `validation.csv` path accepted; no training run |
| smoke_bundle_for_kaggle | full v20 base + corrective overlay single-file bundle | pending | pending | pending | Kaggle upload artifact generated under `nemotron/training/sft/` |
| kaggle-v20-sft-repro-0414-104905 | full v20 base + corrective overlay single-file bundle | `838/950 = 88.2%` | `178/200 = 0.8900` | not recorded | intended binary gain was real, but symbol stayed weak and easy-family regressions appeared |
