# bit_synth_exact_trace_cot_v1_1

## 概要

- README.md の boxed-first 抽出を前提に、v1 の exact-trace 路線を維持しつつ near-miss 回収用の short/query-commit/closure-only supervision を追加した v1.1 生成版。
- 生成行数: 10000
- seed: 20260405
- 計測スコア: 未計測。学習と評価はまだ実行していないため pending。

## Style Mixture

- boxed_only_closure: 500
- trace_boxed_full: 7000
- trace_boxed_query_commit: 1000
- trace_boxed_short: 1500

## Group Counts

- binary_affine_xor: 1035
- binary_bit_permutation_bijection: 580
- binary_bit_permutation_independent: 206
- binary_byte_transform: 28
- binary_structured_byte_formula: 3806
- binary_structured_byte_formula_abstract: 2025
- binary_structured_byte_not_formula: 139
- binary_three_bit_boolean: 250
- binary_two_bit_boolean: 1931

## Training Compatibility

- 列構成は v1 と同一で、assistant_style は trace_boxed / boxed_only の既存2値に収めている。
- 既存 train-bit-synth-exact-trace-cot_merge_lora.ipynb は、DATASET_CSV と MANIFEST_JSON の差し替えだけで v1.1 を読める。

## Output Files

- CSV: cuda-train-data-analysis-v1/bit_synth_exact_trace_cot_v1_1/bit_synth_exact_trace_cot_training_data_v1_1.csv
- Manifest: cuda-train-data-analysis-v1/bit_synth_exact_trace_cot_v1_1/bit_synth_exact_trace_cot_manifest_v1_1.json
- Script: cuda-train-data-analysis-v1/bit_synth_exact_trace_cot_v1_1/generate_bit_synth_exact_trace_cot_v1_1.py
