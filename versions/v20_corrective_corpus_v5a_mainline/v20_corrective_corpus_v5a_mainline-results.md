# v20_corrective_corpus_v5a_mainline results

## Status

- 状態: 学習データ生成済み、学習・評価は未実施
- 生成日時: 2026-04-17 UTC
- run name: `initial_build`

## Intent

v5a は v4 の微修正ではなく、

- Stage A: verified binary core
- Stage C: short easy-family boxed-surface stabilizer

のみを使う初回本命 mainline として作成した。

Stage B の binary answer-only bridge は初回 run では入れていない。

## Generated artifacts

- generator: `versions/v20_corrective_corpus_v5a_mainline/reproduce_v20_corrective_corpus_v5a_mainline.py`
- selection csv: `versions/v20_corrective_corpus_v5a_mainline/outputs/initial_build/artifacts/corrective_selection.csv`
- summary json: `versions/v20_corrective_corpus_v5a_mainline/outputs/initial_build/artifacts/corrective_overlay_summary.json`
- report md: `versions/v20_corrective_corpus_v5a_mainline/outputs/initial_build/reports/corrective_overlay_report.md`
- training bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v5a_mainline_bundle.jsonl`

## Data summary

- selected unique rows: `238`
- selected repeated rows: `662`
- base examples: `7828`
- total examples: `8490`
- total steps: `266`
- total tokens: `32,039,977`
- max seq len: `7971`

### Selected unique rows by bucket

- `binary_verified_core`: `192`
- `surface_numeral_boxed`: `28`
- `surface_cipher_boxed`: `6`
- `surface_unit_tail`: `6`
- `easy_gravity_fragile`: `6`

### Repeated rows by bucket

- `binary_verified_core`: `576`
- `surface_numeral_boxed`: `56`
- `surface_cipher_boxed`: `12`
- `surface_unit_tail`: `12`
- `easy_gravity_fragile`: `6`

## Notes

- v4 実測を current reference として使い、binary は verified のみを採用した。
- current v4 で proxy fail / validation fail に当たる binary row を優先しつつ、`abstract_support >= 20` を主軸にした。
- cryptarithm / broad symbol は v5a から外した。
- easy family は boxed surface stabilizer として短く入れている。

## Score record

- local validation: 未計測
- proxy: 未計測
- public leaderboard: 未計測