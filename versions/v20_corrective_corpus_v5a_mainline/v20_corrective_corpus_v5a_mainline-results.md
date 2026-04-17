# v20_corrective_corpus_v5a_mainline results

## Status

- 状態: canonical v5a bundle 再生成済み、学習・評価は未実施
- 生成日時: 2026-04-17 UTC
- run name: `canonical_build`

## Intent

v5a は v4 の微修正ではなく、

- Stage A: verified binary core
- Stage C: short easy-family boxed-surface stabilizer

のみを使う初回本命 mainline として作成した。

Stage B の binary answer-only bridge は入れていない。

今回の canonical build では、

- Stage A を verified_trace_ready 限定に固定
- Stage A supervision を短い family/query/closure trace に置換
- Stage C supervision を tail-only boxed stabilizer に置換
- overlay を base token 再利用ではなく全件 retokenize に固定

まで反映した。

## Generated artifacts

- generator: `versions/v20_corrective_corpus_v5a_mainline/reproduce_v20_corrective_corpus_v5a_mainline.py`
- selection csv: `versions/v20_corrective_corpus_v5a_mainline/outputs/canonical_build/artifacts/corrective_selection.csv`
- summary json: `versions/v20_corrective_corpus_v5a_mainline/outputs/canonical_build/artifacts/corrective_overlay_summary.json`
- report md: `versions/v20_corrective_corpus_v5a_mainline/outputs/canonical_build/reports/corrective_overlay_report.md`
- training bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v5a_mainline_bundle.jsonl`

## Data summary

- selected unique rows: `244`
- selected repeated rows: `622`
- base examples: `7828`
- total examples: `8450`
- total steps: `265`
- total tokens: `28,043,350`
- max seq len: `7971`

### Selected unique rows by bucket

- `binary_verified_core`: `192`
- `surface_numeral_boxed`: `34`
- `surface_cipher_boxed`: `6`
- `surface_unit_tail`: `6`
- `easy_gravity_fragile`: `6`

### Repeated rows by bucket

- `binary_verified_core`: `570`
- `surface_numeral_boxed`: `34`
- `surface_cipher_boxed`: `6`
- `surface_unit_tail`: `6`
- `easy_gravity_fragile`: `6`

## Canonical validation

- canonical checks: `pass`
- mandatory anchor missing: `0`
- Stage A non-verified rows: `0`
- Stage B-like contamination in Stage A: `0`
- unexpected Stage C categories: `0`
- Stage A max think lines: `4`
- Stage C max think lines: `3`
- retokenized overlay problem count: `244`
- retokenized overlay example count: `622`

### Stage A family distribution

- `xor(shl,shr)`: `99`
- `choose(shl,shr,rol)`: `18`
- `choose(shl,shr,ror)`: `16`
- `majority(ror,shl,shr)`: `16`
- `majority(rol,shl,shr)`: `16`
- `xor(ror,shl)`: `10`
- `or(rol,shr)`: `8`
- `or(ror,shr)`: `3`

### Overlay style counts

- `trace_family_commit`: `192`
- `trace_query_commit`: `192`
- `trace_closure_commit`: `186`
- `surface_boxed_tail`: `52`

### Overlay token share by bucket

- `binary_verified_core`: `0.9613`
- `surface_numeral_boxed`: `0.0222`
- `easy_gravity_fragile`: `0.0060`
- `surface_cipher_boxed`: `0.0055`
- `surface_unit_tail`: `0.0049`

## Notes

- README 評価契約の boxed-first / `max_lora_rank=32` / `max_tokens=7680` / `max_num_seqs=64` / `max_model_len=8192` を summary に埋め込んで確認した。
- v4 実測を current reference として使い、binary は verified のみを採用した。
- current v4 で proxy fail / validation fail に当たる binary row を優先しつつ、`abstract_support >= 20` と family quota を併用した。
- numeral mandatory anchor は 34 件すべて保持した。
- cryptarithm / broad symbol は v5a から外した。
- easy family は boxed surface stabilizer として短く入れている。
- bundle 生成時の overlay は row ごとに再 token 化され、旧 provisional build にあった base synthetic token 再利用は除去した。

## Score record

- local validation: 未計測
- proxy: 未計測
- public leaderboard: 未計測