# Phase 2.2.1 Symbol Specialist データ設計方針

## 結論

`phase2_2_1_merge_lora` は **glyph を捨てて numeric_2x2 だけに絞る quality-first symbol specialist** とする。

- `README.md` の評価は `\boxed{}` 優先の Accuracy なので、学習でも **boxed final answer の安定性** を最優先に置く。`README.md:31-46`
- `phase2_2_merge_lora` は symbol-only `1520` 行で `numeric_2x2 = 25/40` まで伸びた一方、`glyph_len5 = 0/20`、overall も `193/320` まで落ちた。`baseline/cot/phase0_offline_eval/result/2_2_merge_lora/reports/phase2_symbol_specialist_result2_2_merge_lora_deep_analysis.md`
- 同分析では、glyph `823` 行はすべて answer-only で latent rule が未解決、今必要なのは **glyph 全量投入ではなく glyph を別扱いにする設計** だと整理している。`baseline/cot/phase0_offline_eval/result/2_2_merge_lora/reports/phase2_symbol_specialist_result2_2_merge_lora_deep_analysis.md:157-175,355-363`
- `FINAL_SUMMARY_REPORT.md` でも `symbol_equation` は `110 verified / 1410 answer_only / 26 manual / 9 exclude` で、glyph は `0 verified / 823 answer_only` に留まる。つまり trace teacher の核は numeric 側にしかない。`cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md:57-70,188-247`

したがって次版は、

1. **verified numeric trace** を中核にする
2. **同一 verified source 由来の boxed-only sibling** で closure を教える
3. broad な numeric answer-only `587` 行はそのまま使わず、**formula-backed または same-operator evidence が強い高信頼 slice** だけを採る
4. glyph / manual / exclude は学習に入れない

という 4 点で組む。

## phase2_2_1 の dataset design

### 学習対象

`cuda-train-data-analysis-v1/artifacts/train_row_analysis_v1.csv` から、`family == symbol_equation` かつ `template_subtype == numeric_2x2` を母集団とする。

### 使う行

| slice | rows | 使い方 |
| --- | ---: | --- |
| verified trace core | 110 | `trace_boxed` |
| verified boxed sibling | 110 | 同一 source の `boxed_only` duplicate |
| formula-backed answer-only | 129 | `boxed_only` |
| same-op evidence >= 3 の answer-only | 62 | `boxed_only` |
| **total** | **411** |  |

高信頼 answer-only の具体ルールは次:

- `selection_tier == answer_only_keep`
- `template_subtype == numeric_2x2`
- `suspect_label == False`
- かつ以下のどちらか
  - `symbol_numeric_formula_name != ""` の formula-backed row
  - `symbol_same_operator_example_count >= 3` の multi-evidence row

この設計だと broad numeric answer-only `587` 行のうち、採用は `191` 行にとどめ、残り `396` 行は外す。

### 明示的に外す行

| slice | rows | 理由 |
| --- | ---: | --- |
| `glyph_len5` answer-only | 823 | 2.2 実測で `0/20`、verified trace も 0 |
| numeric broad answer-only residual | 396 | evidence が弱く、2.2 では marginal gain しかなかった |
| `manual_audit_priority` | 26 | `FINAL_SUMMARY_REPORT.md` でも raw teacher 化は非推奨 |
| `exclude_suspect` | 9 | 学習へ入れない |

## trace 形式

verified trace は 2.2 の自然文

`For operator X, the examples fit the verified rule ... Applying that rule to the query gives ANSWER.`

をやめて、**final answer を `<think>` に再掲しない short micro-DSL** にする。

例:

```text
<think>op="+"; query=56+17; lhs=56; rhs=17; rule=concat_yx; support=same_operator_examples_2; apply=rule(lhs,rhs); constraints=match_examples,box_only_final</think>
```

狙いは次の 2 点。

1. README の boxed-first extraction に合わせて、**最終答えは boxed 部分だけに寄せる**
2. symbol specialist の長文化を抑え、trace と final answer の役割を分ける

## 期待する比較軸

`phase2_2_1` ではまず次を見ればよい。

1. `numeric_2x2` が `25/40` を超えるか
2. `answer_only_keep` slice が 2.2 より安定するか
3. glyph を切ったことで、少なくとも symbol specialist 内部の supervision quality が明確になるか

これはまだ **glyph を解く実験ではない**。glyph は別系統で latent rule を詰めるまで切り離す。

## build コマンド

```bash
uv run python baseline/cot/phase2_2_1_merge_lora/build_phase2_2_1_symbol_specialist_dataset.py
```

生成物:

- `baseline/cot/phase2_2_1_merge_lora/artifacts/phase2_2_1_symbol_specialist_training_data.csv`
- `baseline/cot/phase2_2_1_merge_lora/artifacts/phase2_2_1_symbol_specialist_manifest.json`
