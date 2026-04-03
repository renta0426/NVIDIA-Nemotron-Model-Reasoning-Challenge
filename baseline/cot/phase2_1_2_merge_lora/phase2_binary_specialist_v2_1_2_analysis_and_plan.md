# Phase 2.1.2 Binary Specialist LoRA 分析と実装計画

## 目的

`phase2_1_merge_lora` の binary-only specialist は、binary を `1449` 行まで増やしても `10/60`、exact 8-bit は `7/60` に留まりました。したがって次の `phase2_1_2_merge_lora` では、**量の追加ではなく、README.md 前提の exact 8-bit closure を高信頼 teacher でどう教えるか**に振ります。(`README.md:31-46`, `baseline/cot/phase0_offline_eval/result/2_1_merge_lora/reports/phase2_binary_specialist_result2_1_merge_lora_deep_analysis.md`)

## これまでの整理から確定していること

1. `README.md` の評価は `\boxed{}` 優先抽出なので、binary は rule 推定だけでなく **leading zero を含む 8-bit を最後に box へ閉じる discipline** が必要です。(`README.md:31-46`)
2. 長い natural-language trace は悪化要因でした。`phase2_binary_hybrid` は binary を `13/60 -> 8/60` まで落としました。(`baseline/cot/binary_synthetic_data_approaches_history.md`, `baseline/cot/phase0_offline_eval/result/2-1/reports/phase2_hybrid_result2_1_deep_analysis.md`)
3. `phase2_1_merge_lora` は `1004 verified + 445 answer_only` の binary-only curated set でしたが、`bit_structured_byte_formula` を大量投入しても `2/14` に留まりました。問題は量より **teacher quality / closure quality / subtype stratification** です。(`baseline/cot/phase2_1_merge_lora/artifacts/phase2_1_binary_specialist_manifest.json`, `cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md`)
4. `FINAL_SUMMARY_REPORT.md` は `verified_trace_ready` を trace core、`answer_only_keep` を boxed-only 補助 supervision として分ける方針を明示しています。従って broad answer-only をそのまま main train に流し込むのは避けるべきです。(`cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md:100-122`)

## v2-1-2 で採る方針

今回の `v2-1-2` は、以前の計画でいう **Exp-B: HQ verified + same-row boxed-only sibling** を concrete にした binary-only dataset です。

### 採用する設計

| 項目 | v2-1-2 の内容 |
| --- | --- |
| 学習スコープ | binary-only |
| trace core | `bit_manipulation + verified_trace_ready` を **全件 1004 行**使う |
| boxed-only | 既存 `answer_only_keep 445` は使わず、**verified 行から 445 行の sibling duplicate** を作る |
| trace 形式 | 長文化した hybrid ではなく、短い **micro-DSL** |
| final answer leakage | `<think>` に final 8-bit を再掲しない。`query == answer` 行も sanitize する |
| risky tiers | `answer_only_keep`, `manual_audit_priority`, `exclude_suspect` は main dataset から外す |

### なぜこの形か

`phase2_1_merge_lora` の 445 行は broad answer-only で、`FINAL_SUMMARY_REPORT.md` 上も trace teacher に上げない理由が残っている行です。一方、same-row sibling は **同じ prompt / 同じ gold / 同じ verified source** から boxed-only supervision だけを追加できるので、closure を教えながら label quality を落としません。(`cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md:115-122,154-173`)

## 具体的な dataset design

### 1. trace core

- source: `cuda-train-data-analysis-v1/artifacts/train_row_analysis_v1.csv`
- filter:
  - `family == bit_manipulation`
  - `selection_tier == verified_trace_ready`
  - `verified_trace_ready == true`
  - `teacher_solver_candidate != ""`
- rows: `1004`

### 2. boxed-only sibling

trace core と同じ verified source から、別 ID の boxed-only duplicate を `445` 行作ります。これで total rows は `1449` になり、2.1 と同じ行数で **質だけを差し替える** 比較ができます。

boxed-only sibling は closure を hardest subtype に寄せるため、次の quota で切ります。

| subtype | sibling quota |
| --- | ---: |
| `bit_structured_byte_formula` | 320 |
| `bit_other` | 95 |
| `bit_permutation_inversion` | 30 |

この配分は、2.1 が最も苦しんだ `bit_structured_byte_formula` に closure 予算を少し厚く張るためです。(`baseline/cot/phase0_offline_eval/result/2_1_merge_lora/reports/phase2_binary_specialist_result2_1_merge_lora_deep_analysis.md`)

### 3. trace style

binary trace は natural-language ではなく、次の micro-DSL へ寄せます。

```text
<think>rule=xor(shl1,shr4); query=10000011; step1=shl1(query)=00000110; step2=shr4(query)=00001000; apply=xor(step1,step2); constraints=exact_8bit,leading_zeros,box_only_final</think>
```

狙いは 3 つです。

1. `build_phase2_binary_dsl_dataset.py` の hybrid narrative で起きた長文化を避ける
2. rule identity と query application を残しつつ、自然言語ノイズを減らす
3. final 8-bit answer を `<think>` の中で再掲しない

## このフォルダで作るもの

| パス | 役割 |
| --- | --- |
| `baseline/cot/phase2_1_2_merge_lora/build_phase2_1_2_binary_specialist_dataset.py` | v2-1-2 dataset builder |
| `baseline/cot/phase2_1_2_merge_lora/artifacts/phase2_1_2_binary_specialist_training_data.csv` | 学習 CSV |
| `baseline/cot/phase2_1_2_merge_lora/artifacts/phase2_1_2_binary_specialist_manifest.json` | manifest |
| `baseline/cot/phase2_1_2_merge_lora/phase2_binary_specialist_v2_1_2_analysis_and_plan.md` | この分析・計画メモ |

## ここではやらないこと

今回の `v2-1-2` は **binary-only dataset** の作成までです。以前の計画で挙げた

- `result/2` からの anchored continuation
- structured-byte family ごとの専用 continuation
- risky answer-only の late-stage 注入

は次段階の実験に回します。

## ビルドコマンド

```bash
uv run python baseline/cot/phase2_1_2_merge_lora/build_phase2_1_2_binary_specialist_dataset.py --mode build-dataset
```

この builder は `artifacts/` に CSV と manifest を再生成できるようにしておく。
