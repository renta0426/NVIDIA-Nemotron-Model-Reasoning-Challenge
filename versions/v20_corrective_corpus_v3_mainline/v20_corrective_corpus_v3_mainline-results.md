# v20_corrective_corpus_v3_mainline results

> Repository note: canonical challenge contract lives in `README.md`.
> This version prepares a **single-file corrective training bundle** for the Kaggle direct-training path and preserves the submission target as `submission.zip`.
> Measured validation / proxy / leaderboard scores for this version must be recorded here after each run.

## Purpose

- Base strategy source: `A-Open-ProgressPrizePublication/v20_to_088_strategy.md`
- README grounding:
  - `bit_manipulation` remains the main upside slice (`README.md`)
  - higher score requires new programmatic insight, so we should improve binary signal without damaging easy families
- Correction vs prior v3 ablation:
  - do **not** blacklist every `default 1` trace
  - remove only **actual metric-wrong teacher rows** from the v20 snapshot
  - allow only **teacher-correct** overlay examples into the binary corrective pack

## Implementation

- Script: `versions/v20_corrective_corpus_v3_mainline/reproduce_v20_corrective_corpus_v3_mainline.py`
- Style: single-file monolith
- Bundle:
  - `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v3_mainline_bundle.jsonl`
- Kaggle notebook path:
  - `A-Open-ProgressPrizePublication/kaggle-v20-sft-repro.ipynb`

## Current status

- Implementation: **ready**
- Bundle generation: **done**
- Teacher-correct overlay audit: **done**
- Kaggle training run: **pending**
- `submission.zip` export: **pending**

## 2026-04-16 corpus generation: `v3_mainline_default`

### Core fixes

1. Base snapshot exclusion:
   - removed metric-wrong base problem ID: `ef2fe526`
   - removed base rows: `ef2fe526`, `ef2fe526-p0`
2. Overlay correctness gate:
   - filtered out `130` teacher-incorrect binary candidates before selection
   - selected overlay rows with teacher mismatch: `0`
3. Binary emphasis:
   - `binary_structured_core = 192` unique / `768` repeated
   - `binary_other_light = 80` unique / `160` repeated
4. Guardrails kept light:
   - numeral / gravity / unit / cryptarithm symbolic at `12` unique each
   - symbol prefix at `2` unique

### Bundle summary

| Metric | Value |
| --- | ---: |
| Base examples kept | `7828` |
| Overlay examples | `990` |
| Total examples | `8818` |
| Total steps | `276` |
| Total tokens | `34,703,186` |
| Max seq len | `7971` |
| Retokenized overlay problem count | `2` |

### Selected buckets

| Bucket | Unique | Repeated |
| --- | ---: | ---: |
| binary_structured_core | `192` | `768` |
| binary_other_light | `80` | `160` |
| guardrail_numeral_subtractive | `12` | `24` |
| guardrail_gravity_fragile | `12` | `12` |
| guardrail_unit_fragile | `12` | `12` |
| guardrail_cryptarithm_symbolic | `12` | `12` |
| guardrail_symbol_prefix | `2` | `2` |

### Diagnostics

- `proxy_failed_selected = 1`
- `validation_failed_selected = 0`
- binary mandatory rows forced in:
  - structured: `0520a6ec`, `0a50c4a8`, `59c78e51`, `fa67da07`
  - other: `8e5d6fe6`, `b9500f41`, `c30a782a`

## Score ledger

| run | data change | validation | proxy | public leaderboard | notes |
| --- | --- | ---: | ---: | ---: | --- |
| v3_mainline_default | v20 minus `ef2fe526*` + teacher-correct-only binary overlay | pending | pending | pending | bundle generated; ready for Kaggle mainline run |

## Recording

All scores are recorded from measured outputs only. Update this file after each Kaggle run.
