# v20 corrective corpus v7 mainline results

## Status

- Created: 2026-04-20 UTC
- Generator: `versions/v20_corrective_corpus_v7_mainline/reproduce_v20_corrective_corpus_v7_mainline.py`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Parent public baselines:
  - `v4`: `0.85-0.86`
  - `v6`: `0.83-0.85`
- Intent:
  - keep v4 as the public-safe base
  - borrow only narrow binary donors from v6
  - reinforce the v6 numeral no-box failures
  - avoid broad new symbol / cryptarithm expansion

## Generation status

- Training / validation / leaderboard score: 未計測
- Output artifacts: generated under `versions/v20_corrective_corpus_v7_mainline/outputs/v7_mainline_default`
- Bundle path: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v7_mainline_bundle.jsonl`

## Generated artifacts

- `versions/v20_corrective_corpus_v7_mainline/outputs/v7_mainline_default/artifacts/corrective_selection.csv`
- `versions/v20_corrective_corpus_v7_mainline/outputs/v7_mainline_default/artifacts/corrective_overlay_unique.jsonl`
- `versions/v20_corrective_corpus_v7_mainline/outputs/v7_mainline_default/artifacts/corrective_overlay_repeated.jsonl`
- `versions/v20_corrective_corpus_v7_mainline/outputs/v7_mainline_default/artifacts/corrective_overlay_summary.json`
- `versions/v20_corrective_corpus_v7_mainline/outputs/v7_mainline_default/reports/corrective_overlay_report.md`

## Dataset composition

### Overlay mix

- `v4_public_base`: `808` repeated rows
- `v6_binary_donor`: `27` repeated rows
- `v6_numeral_surface_donor`: `10` repeated rows
- `v7_numeral_surface_synth`: `1` repeated row
- total repeated rows: `846`
- total unique rows: `338`

### Bucket footprint

- `binary_structured_core`: `528`
- `binary_other_light`: `128`
- `binary_structured_donor_exact`: `15`
- `binary_logic_donor_exact`: `6`
- `binary_permutation_donor_exact`: `6`
- `surface_numeral_boxed`: `72`
- `surface_numeral_boxed_donor`: `11`
- `surface_cipher_boxed`: `24`
- `surface_cryptarithm_boxed`: `24`
- `surface_unit_tail`: `16`
- `surface_symbol_prefix`: `4`
- `easy_gravity_fragile`: `12`

### Bundle footprint

- base examples: `7828`
- overlay examples: `846`
- total examples: `8674`
- total steps: `272`
- total tokens: `32948771`
- max sequence length: `7999`

## Strategy interpretation

- v7 keeps the whole `v4` overlay weight intact instead of thinning it. This is intentional because `v4` is the current best public baseline.
- v7 adds only `9` high-confidence binary donor IDs from `v6`: `0520a6ec`, `0a50c4a8`, `0dd5caf4`, `17fd9612`, `59c78e51`, `8e5d6fe6`, `b9500f41`, `c30a782a`, `fa67da07`.
- v7 also backfills all `11` numeral no-box IDs seen in `v6`; `10` came directly from `v6` surface rows and `1542039b` was synthesized as a short boxed-only stabilizer row.
- This keeps the change narrow: we do not add broad new symbol or cryptarithm branches beyond what `v4` already carried.

## Notes

- This version is intentionally a mixed mainline: `v4` is the public baseline, while `v6` is treated as a binary donor branch only.
- The first success criterion is not proxy leadership. It is whether the mixed corpus can preserve `v4`-class public stability while importing some of `v6`'s binary gains.
- The immediate next gate is official leaderboard calibration against `v4`, not local proxy alone.
