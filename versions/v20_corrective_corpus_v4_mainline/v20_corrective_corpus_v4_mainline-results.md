# v20_corrective_corpus_v4_mainline results

> Repository note: canonical challenge contract lives in `README.md`.
> This version prepares a **single-file corrective training bundle** for the Kaggle direct-training path and preserves the submission target as `submission.zip`.
> Measured validation / proxy / leaderboard scores for this version must be recorded here after each run.

## Purpose

- Base strategy source: `A-Open-ProgressPrizePublication/v20_to_088_strategy.md`
- Additional grounding:
  - `A-Open-ProgressPrizePublication/v20_snapshot_final_summary_replacement_report.md`
  - `versions/v20_corrective_corpus_v1/v20_corrective_corpus_v1-results.md`
  - `versions/v20_corrective_corpus_v2/v20_corrective_corpus_v2-results.md`
  - `versions/v20_corrective_corpus_v3_mainline/v20_corrective_corpus_v3_mainline-results.md`
- README grounding:
  - `bit_manipulation` remains the main upside slice
  - public metric is **boxed-first extraction**
  - easy-family surface corruption must not erase binary gains

## Implementation

- Script: `versions/v20_corrective_corpus_v4_mainline/reproduce_v20_corrective_corpus_v4_mainline.py`
- Style: single-file monolith
- Added MLX measured-validation diff support:
  - `--analysis-only --measured-validation-csv <validation.csv> --measured-tag <tag>`
  - emits row-level regression packs against `base_v20`, `binary_reference_v1`, `corrective_v2`, and `corrective_v3`
- Bundle:
  - `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v4_mainline_bundle.jsonl`
- Kaggle notebook path:
  - `A-Open-ProgressPrizePublication/kaggle-v20-sft-repro.ipynb`

## Current status

- Implementation: **ready**
- Bundle generation: **done**
- Bundle audit: **done**
- Kaggle training run: **pending**
- MLX full-run against the same single-file bundle: **running**
- Validation / proxy evaluation: **pending**
- `submission.zip` export: **pending**

### Operational note

- A short-lived parallel MLX contrast run for `v3_mainline` was launched on 2026-04-17, but was stopped before its first logged train step after RAM climbed to about `483.79 / 512 GB`.
- The active MLX lane is therefore now **only** `v20_mlx_v4_mainline_mb1_nobc`.
- Disk hygiene on 2026-04-17: after bundle ingest was proven and the v3 contrast lane was aborted, the tracked `shadow_model/` and `training_bundle_tokens/` trees for `v20_mlx_v4_bundle_prepare_smoke` and `v20_mlx_v3_mainline_mb1_nobc` were pruned to reclaim local storage while preserving manifests, logs, and score ledgers.

### Live MLX progress snapshot

- run: `v20_mlx_v4_mainline_mb1_nobc`
- source bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v4_mainline_bundle.jsonl`
- latest observed train step: `181 / 271`
- latest observed train loss: `0.00047689699085237165`
- latest observed trained tokens: `19580352`
- latest observed total elapsed seconds: `55278.9592`
- note: this is only a live training snapshot from `adapter/latest_train_report.json`, **not** a measured validation score

## 2026-04-17 corpus generation: `v4_mainline_default`

### Core decisions

1. **Keep the v20 base snapshot**
   - preserve stable easy-family coverage from `04-08-16-14`
   - remove only the audited metric-wrong base problem `ef2fe526*`
2. **Keep binary overlay teacher-correct-only**
   - filtered out `130` teacher-incorrect binary candidates before selection
   - selected binary overlay rows with teacher mismatch: `0`
3. **Add explicit terminal-surface repair buckets**
   - numeral `\\boxed -> \\box` failures from v3
   - cipher backslash-wrap failures from v3
   - symbolic cryptarithm boxing corruption
   - unit answer-tail corruption
4. **Do not reintroduce broad symbol main-line overlay**
   - keep only the narrow symbol-prefix repair bucket

### Bundle summary

| Metric | Value |
| --- | ---: |
| Base examples kept | `7828` |
| Overlay examples | `808` |
| Total examples | `8636` |
| Total steps | `271` |
| Total tokens | `32,858,695` |
| Max seq len | `7971` |
| Retokenized overlay problem count | `20` |

### Selected buckets

| Bucket | Unique | Repeated |
| --- | ---: | ---: |
| binary_structured_core | `176` | `528` |
| binary_other_light | `64` | `128` |
| surface_numeral_boxed | `36` | `72` |
| surface_cipher_boxed | `8` | `24` |
| surface_cryptarithm_boxed | `12` | `24` |
| surface_unit_tail | `8` | `16` |
| surface_symbol_prefix | `2` | `4` |
| easy_gravity_fragile | `12` | `12` |

### Diagnostics

- `proxy_failed_selected = 1`
- `validation_failed_selected = 0`
- `v3_surface_box_regression_count = 38`
- binary mandatory rows forced in:
  - structured: `0520a6ec`, `0a50c4a8`, `17fd9612`, `59c78e51`, `8e5d6fe6`
  - other: `0dd5caf4`, `b9500f41`, `c30a782a`, `fa67da07`
- surface mandatory rows forced in:
  - numeral boxed repair: `34`
  - cipher boxed repair: `4`
  - cryptarithm boxed repair: `3`
  - unit tail repair: `3`
  - gravity fragile: `1`
  - symbol prefix: `1`

### Audit note

- Strategy alignment: **pass**
- Binary overlay is now fully `verified_trace_ready` only; the earlier `answer_only_keep` leak was removed.
- All mandatory IDs are present in the regenerated selection.
- `bit_permutation_inversion` support is limited to `4` rows inside `binary_other_light`, which matches the narrow binary-support intent better than leaving those proxy-important rows unbucketed.
- `surface_symbol_prefix` still contains `2` rows (`d9bedb64`, `aa251ec4`), but this remains a narrow numeric-prefix repair rather than the broad symbol overlay that v4 explicitly rejects.
- 2026-04-17 recheck found one operational gap: artifacts had been regenerated after the bucket fix, but the single-file training bundle had not yet been re-emitted. The bundle was then rebuilt with `--write-training-bundle`, and the final bundle stats above now match the shipped `v20_corrective_corpus_v4_mainline_bundle.jsonl`.

### Intent

This v4 bundle is the first corpus that explicitly combines:

- **v1** binary additive gain
- **v2** surface / guardrail necessity
- **v3** teacher-correct-only binary purity
- snapshot replacement report's **evidence-first base preservation**

The design target is not merely a higher proxy. It is a bundle that can keep proxy-level binary gains **without** reintroducing the public-score failure mode where `\\boxed` or terminal answer surface collapses on easy families.

## Score ledger

| run | data change | validation | proxy | public leaderboard | notes |
| --- | --- | ---: | ---: | ---: | --- |
| v4_mainline_default | v20 base minus `ef2fe526*` + teacher-correct-only binary overlay + explicit terminal-surface repair buckets | pending | pending | pending | bundle generated; ready for Kaggle training |
| v20_mlx_v4_mainline_mb1_nobc | same v4 single-file bundle on the MLX reproduction path with `micro_batch_size=1` and `Adam bias_correction=False` | running | pending | pending | launched 2026-04-17; pipeline log at `v20_mlx_repro_v1/outputs/v20_mlx_v4_mainline_mb1_nobc/pipeline.log`; score entry will be filled only after measured adapter-validation completes |

## Recording

All scores are recorded from measured outputs only. Update this file after each Kaggle run.
