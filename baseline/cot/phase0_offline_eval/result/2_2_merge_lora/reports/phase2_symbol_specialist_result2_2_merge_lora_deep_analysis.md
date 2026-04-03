# Phase 2.2 Symbol Specialist Result 2_2 Merge LoRA 詳細分析

## 前提

- 対象は `baseline/cot/phase0_offline_eval/result/2_2_merge_lora` 配下の Phase 0 offline eval 結果。
- 評価基準は `README.md` の Accuracy / `\boxed{}` 優先抽出 / fallback 抽出 / numeric tolerance に合わせる。(`README.md:31-46`, `baseline/cot/phase0_offline_eval/result/2_2_merge_lora/reports/phase0_eval_manifest.md`)
- 学習 notebook の source は `baseline/cot/phase2_2_merge_lora/train-rule-based-cot-baseline_phase2_2_merge_lora.ipynb`、学習データの一次情報は `baseline/cot/phase2_2_merge_lora/artifacts/phase2_2_symbol_specialist_manifest.json` を優先した。(`baseline/cot/phase2_2_merge_lora/train-rule-based-cot-baseline_phase2_2_merge_lora.ipynb:330-349`, `baseline/cot/phase2_2_merge_lora/artifacts/phase2_2_symbol_specialist_manifest.json:1-84`)
- 運用上、ノートブックはローカルそのままではなく **Kaggle 環境へコピーして実行**しているため、ローカル ipynb に残る stdout を provenance の一次情報とはみなさない。本メモでは **result フォルダと manifest** を優先した。(`User input`)
- 比較対象は `result/2`, `result/2-1`, `result/2_1_merge_lora` を主に使う。(`baseline/cot/phase0_offline_eval/result/2/reports/phase0_eval_summary.md`, `baseline/cot/phase0_offline_eval/result/2-1/reports/phase0_eval_summary.md`, `baseline/cot/phase0_offline_eval/result/2_1_merge_lora/reports/phase0_eval_summary.md`)

## 結論

この実験は、**symbol のうち `numeric_2x2` には少し効いたが、`glyph_len5` を全く動かせず、non-symbol family の劣化の方が大きかった**、という結論になる。

- overall は **`193/320 = 0.6031`**
- `symbol_watch_set` は **`25/60 = 0.4167`**
- その内訳は `numeric_2x2 = 25/40`, `glyph_len5 = 0/20`
- `verified_trace_ready` は **`15/15`**
- `answer_only_keep` は **`10/15`**
- `manual_audit_priority` は **`0/30`**

つまり 2.2 specialist は、

1. **curated 済み numeric symbol の exploitation は少し上手い**
2. **glyph は 823 行学習しても 0/20 のまま**
3. **general families を落として overall が崩れる**

という run だった。(`baseline/cot/phase0_offline_eval/result/2_2_merge_lora/reports/phase0_eval_summary.md`, `baseline/cot/phase0_offline_eval/result/2_2_merge_lora/reports/symbol_watch_set_summary.md`)

## 1. 実験内容の事実整理

### 1.1 学習データ

manifest によると、この specialist は **symbol-only curated set 1520 行**で学習している。内訳は

- `verified_trace_ready = 110`
- `answer_only_keep = 1410`
- `assistant_style: trace_boxed = 110`, `boxed_only = 1410`

である。(`baseline/cot/phase2_2_merge_lora/artifacts/phase2_2_symbol_specialist_manifest.json:5-17`)

template subtype は次の通り。

| subtype | rows |
| --- | ---: |
| `glyph_len5` | 823 |
| `numeric_2x2` | 697 |

(`baseline/cot/phase2_2_merge_lora/artifacts/phase2_2_symbol_specialist_manifest.json:18-21`)

さらに verified / answer-only の内訳は、

- verified は **`numeric_2x2` の 110 行のみ**
- `glyph_len5` 823 行は **すべて answer-only**

だった。(`baseline/cot/phase2_2_merge_lora/artifacts/phase2_2_symbol_specialist_manifest.json:55-67`)

つまりこの実験は、**trace-safe な symbol teacher を増やした実験ではなく、answer-only を大量投入した specialist** に近い。

### 1.2 学習設定

notebook source 上の主要設定は次だった。

- `LORA_RANK = 32`
- `NUM_EPOCHS = 2`
- `BATCH_SIZE = 1`
- `GRAD_ACCUM = 4`
- `LR = 1e-4`
- `MAX_SEQ_LEN = 2048`

(`baseline/cot/phase2_2_merge_lora/train-rule-based-cot-baseline_phase2_2_merge_lora.ipynb:330-349`, `baseline/cot/phase2_2_merge_lora/train-rule-based-cot-baseline_phase2_2_merge_lora.ipynb:1218-1249`)

2.1 と同様、**主な変更は model config ではなくデータ specialization** である。

## 2. スコア全体像

### 2.1 他 run との比較

| result | overall | general_stable | binary_hard | symbol_watch |
| --- | ---: | ---: | ---: | ---: |
| `result/1` | 0.7031 | 0.9400 | 0.2000 | 0.4167 |
| `result/2` | 0.7094 | 0.9500 | 0.2167 | 0.4000 |
| `result/2-1` | 0.6750 | 0.9200 | 0.1333 | 0.4000 |
| `result/2_1_merge_lora` | 0.6250 | 0.8450 | 0.1667 | 0.3500 |
| `result/2_2_merge_lora` | 0.6031 | 0.7900 | 0.1667 | 0.4167 |

(`baseline/cot/phase0_offline_eval/result/1/reports/phase0_eval_summary.md`, `baseline/cot/phase0_offline_eval/result/2/reports/phase0_eval_summary.md`, `baseline/cot/phase0_offline_eval/result/2-1/reports/phase0_eval_summary.md`, `baseline/cot/phase0_offline_eval/result/2_1_merge_lora/reports/phase0_eval_summary.md`, `baseline/cot/phase0_offline_eval/result/2_2_merge_lora/reports/phase0_eval_summary.md`)

score だけを見ると、2.2 は

- `symbol_watch_set` で `24/60 -> 25/60` と **+1**
- しかし overall は `227/320 -> 193/320` で **-34**

となる。つまり **symbol の marginal gain より collateral damage の方がはるかに大きい**。

### 2.2 family 別差分

`result/2 -> result/2_2_merge_lora` の family 差分は次だった。

| family | `result/2` | `2_2_merge_lora` | delta |
| --- | ---: | ---: | ---: |
| `binary` | 0.2167 | 0.1667 | -0.0500 |
| `gravity` | 0.9400 | 0.7000 | -0.2400 |
| `roman` | 1.0000 | 1.0000 | 0.0000 |
| `symbol` | 0.4000 | 0.4167 | +0.0167 |
| `text` | 0.8600 | 0.7800 | -0.0800 |
| `unit` | 1.0000 | 0.6800 | -0.3200 |

(`baseline/cot/phase0_offline_eval/result/2/reports/phase0_eval_summary.md`, `baseline/cot/phase0_offline_eval/result/2_2_merge_lora/reports/phase0_eval_summary.md`)

row-level では `result/2` 比で

- 改善: `12`
- 退行: `46`

だった。内訳は

- 改善: `text +6`, `binary +3`, `gravity +2`, `symbol +1`
- 退行: `unit +16`, `gravity +14`, `text +10`, `binary +6`

で、symbol での **+1** を得るために general families を大きく削っている。(`baseline/cot/phase0_offline_eval/result/2_2_merge_lora/artifacts/phase0_eval_row_level.csv`, `baseline/cot/phase0_offline_eval/result/2/artifacts/phase0_eval_row_level.csv`)

## 3. target の symbol は何が伸びて何が伸びなかったか

### 3.1 subtype / tier 別

`result/2_2_merge_lora` の symbol 詳細は次の通り。

| slice | correct / rows | accuracy |
| --- | ---: | ---: |
| `numeric_2x2` | 25 / 40 | 0.6250 |
| `glyph_len5` | 0 / 20 | 0.0000 |
| `verified_trace_ready` | 15 / 15 | 1.0000 |
| `answer_only_keep` | 10 / 15 | 0.6667 |
| `manual_audit_priority` | 0 / 30 | 0.0000 |

(`baseline/cot/phase0_offline_eval/result/2_2_merge_lora/reports/symbol_watch_set_summary.md:15-49`)

ここで読み取れるのはかなり明確で、

1. **伸びたのは numeric core だけ**
2. **glyph は完全に据え置き**
3. **manual hard slice は全く取れない**

という 3 点である。

`result/2` と比べると、

- `numeric_2x2`: `24/40 -> 25/40`
- `glyph_len5`: `0/20 -> 0/20`
- `verified_trace_ready`: `15/15 -> 15/15`
- `answer_only_keep`: `9/15 -> 10/15`
- `manual_audit_priority`: `0/30 -> 0/30`

で、specialization が効いたのは **answer-only numeric を 1 行分だけ押し上げた** 程度に近い。(`baseline/cot/phase0_offline_eval/result/2/reports/symbol_watch_set_summary.md`, `baseline/cot/phase0_offline_eval/result/2_2_merge_lora/reports/symbol_watch_set_summary.md`)

### 3.2 `glyph_len5` が 0/20 のままである意味

`FINAL_SUMMARY_REPORT.md` は glyph について、

- trace-safe 昇格 `0`
- `exact examples-only` を追加しても unique string `0`
- current `glyph_len5` は `0 verified / 823 answer_only / 0 manual / 0 exclude`

と整理している。(`cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md:239-247`)

つまり repo の curation そのものが、**glyph は latent rule が underdetermined なので answer-only に留めるしかない** と判断している。今回の 2.2 が

- glyph 823 行を全部学習しても
- holdout glyph は `0/20`

だったのは、この整理と完全に一致する。

要するに今回の結果は、「glyph はまだ解けていない」ではなく、**現在の corpus と supervision 形式では glyph を学習 problem として定義し切れていない** ことの再確認である。

### 3.3 symbol failure shape

symbol 60 行を再集計すると、failure shape は次だった。

- `numeric2x2_unboxed_wrong`: `11`
- `numeric2x2_boxed_wrong`: `4`
- `glyph_unboxed_wrong`: `18`
- `glyph_boxed_wrong`: `2`

(`baseline/cot/phase0_offline_eval/result/2_2_merge_lora/artifacts/phase0_eval_row_level.csv`)

これは `result/2` の

- `numeric2x2_unboxed_wrong = 11`
- `numeric2x2_boxed_wrong = 5`
- `glyph_unboxed_wrong = 4`
- `glyph_boxed_wrong = 16`

とかなり違う。(`baseline/cot/phase0_offline_eval/result/2/artifacts/phase0_eval_row_level.csv`)

つまり 2.2 specialist は、symbol を

- numeric 部分では少し押し上げた
- その一方で glyph では **「boxed exactness failure」から「unboxed collapse」寄り**へ戻した

と読める。score は `0/20` のままでも、failure mode の質は良くなっていない。

### 3.4 具体例

2.2 が `2_1` より改善した numeric ID には

- `27cec7a9` -> `3341`
- `2e9639de` -> `3585`
- `7c5c7b73` -> `13`
- `9c8eef89` -> `1728`
- `f28681ad` -> `4314`

がある。(`baseline/cot/phase0_offline_eval/result/2_2_merge_lora/artifacts/phase0_eval_row_level.csv`, `baseline/cot/phase0_offline_eval/result/2_1_merge_lora/artifacts/phase0_eval_row_level.csv`)

一方で glyph の典型失敗は、

- `b13d511a` -> `1`
- `dc240ebd` -> `1`
- `d7e5414c` -> `1`
- `a85864a9` -> `your answer`
- `be7101dc` -> `1`

のような形で、**正しい記号列への close が起きていない**。(`baseline/cot/phase0_offline_eval/result/2_2_merge_lora/artifacts/phase0_eval_row_level.csv`)

### 3.5 長文化

symbol の `raw_output` 長を再集計すると、

- symbol 全体平均: `13476.7`
- symbol 誤答のみ平均: `22031.2`
- symbol 60 行中 `31` 行が `>10000 chars`
- `21` 行が `>20000 chars`

だった。(`baseline/cot/phase0_offline_eval/result/2_2_merge_lora/artifacts/phase0_eval_row_level.csv`)

したがって 2.2 でも symbol は、**specialist にしたから短く disciplined に答える** 方向へはほとんど寄っていない。

## 4. symbol 以外の副作用

### 4.1 general stable の崩れ

`general_stable_set` は

- `result/2`: `190/200 = 0.9500`
- `result/2_2_merge_lora`: `158/200 = 0.7900`

で **`-32 correct`**。(`baseline/cot/phase0_offline_eval/result/2/reports/general_stable_set_summary.md`, `baseline/cot/phase0_offline_eval/result/2_2_merge_lora/reports/general_stable_set_summary.md`)

family 別には

- `gravity`: `47 -> 35`
- `text`: `43 -> 39`
- `unit`: `50 -> 34`
- `roman`: `50 -> 50`

だった。(`baseline/cot/phase0_offline_eval/result/2/reports/phase0_eval_summary.md`, `baseline/cot/phase0_offline_eval/result/2_2_merge_lora/reports/phase0_eval_summary.md`)

特に `unit` が **`-16 correct`** と重い。

### 4.2 binary も未解決のまま

2.2 の binary は target ではないが、それでも観察価値はある。

- official-like binary: `10/60`
- exact 8-bit: `8/60`
- `bit_structured_byte_formula`: `0/14`
- tier 別: `verified 7/20`, `answer_only 2/20`, `manual 1/20`

(`baseline/cot/phase0_offline_eval/result/2_2_merge_lora/reports/binary_hard_set_summary.md`, `baseline/cot/phase0_offline_eval/result/2_2_merge_lora/artifacts/phase0_eval_row_level.csv`)

2.1 より format 指標は少し良い。

- boxed extraction success rate: `0.1833` vs `0.1333`
- regex exact rate: `0.3167` vs `0.1833`
- leading-zero retention: `0.3333` vs `0.2000`

(`baseline/cot/phase0_offline_eval/result/2_1_merge_lora/reports/binary_hard_set_summary.md`, `baseline/cot/phase0_offline_eval/result/2_2_merge_lora/reports/binary_hard_set_summary.md`)

しかし score は同じ `10/60` なので、**format が少し整っても reasoning 自体は進んでいない**。

### 4.3 非 target family の長文化

wrong-only の `raw_output` 平均長は次だった。

| family | wrong-only mean raw length |
| --- | ---: |
| `binary` | 16953.2 |
| `gravity` | 2340.5 |
| `symbol` | 22031.2 |
| `text` | 23732.3 |
| `unit` | 16195.1 |

(`baseline/cot/phase0_offline_eval/result/2_2_merge_lora/artifacts/phase0_eval_row_level.csv`)

`text` と `unit` でも 1.6 万〜2.3 万字級の wrong output が出ており、symbol specialist は **symbol のみを強くしたというより、他 family の answer discipline を失わせた** 影響の方が大きい。

## 5. 2_1 specialist との比較

### 5.1 2_2 が勝っているところ

`2_2_merge_lora` は `2_1_merge_lora` に対し、

- symbol overall: `21/60 -> 25/60`
- `numeric_2x2`: `21/40 -> 25/40`
- `verified_trace_ready`: `14/15 -> 15/15`
- `answer_only_keep`: `7/15 -> 10/15`

と、**symbol core の exploitation では明確に上**だった。(`baseline/cot/phase0_offline_eval/result/2_1_merge_lora/reports/symbol_watch_set_summary.md`, `baseline/cot/phase0_offline_eval/result/2_2_merge_lora/reports/symbol_watch_set_summary.md`)

### 5.2 それでも overall で負ける理由

row-level 比較では、`2_2` は `2_1` に対して

- 改善: `symbol +5`, `binary +5`, `gravity +9`, `unit +5`, `text +5`
- 退行: `gravity +13`, `unit +10`, `text +7`, `binary +5`, `symbol +1`

となっており、改善もあるが退行の方が多い。特に **symbol で +5 を取る代わりに**

- `gravity -13`
- `unit -10`
- `text -7`

を失っている。差し引きで overall は `200 -> 193` に下がる。(`baseline/cot/phase0_offline_eval/result/2_1_merge_lora/artifacts/phase0_eval_row_level.csv`, `baseline/cot/phase0_offline_eval/result/2_2_merge_lora/artifacts/phase0_eval_row_level.csv`)

要するに 2.2 は **symbol に偏った capacity allocation** であり、generalist としては 2.1 よりさらに不安定だった。

## 6. 履歴に置いた時の意味

`FINAL_SUMMARY_REPORT.md` は symbol を

- `110 verified`
- `1410 answer_only`
- `26 manual`
- `9 exclude`

まで圧縮している。(`cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md:57-70,188-217`)

このうち glyph は

- `0 verified`
- `823 answer_only`

であり、根拠の強い trace teacher は存在しない。(`cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md:239-247`)

今回の 2.2 はこの curated 全量を specialist として使ったが、結果は

- numeric では小改善
- glyph は据え置き
- manual hard slice は据え置き

だった。つまり、**symbol specialist は「curated numeric 部分の exploit」には使えても、「未解決 symbol を解く」方向には全く効いていない**。

## 7. まとめ

2.2 symbol specialist から得られる実務的な結論は次の通り。

1. **specialization が効くのは `numeric_2x2` の一部だけ**
2. **`glyph_len5` は answer-only を 823 行入れても 0/20 のまま**
3. **manual hard symbol は 0/30 のままで、難所の generalization は無い**
4. **overall では mixed DSL `result/2` より大幅に悪い**
5. したがって次に必要なのは symbol volume 追加ではなく、**glyph の latent rule を offline で特定するか、glyph を別扱いする設計**である

submission 候補として見るなら、`result/2_2_merge_lora` は **symbol 分析用の specialist 実験としては有益だが、全体性能では `result/2` を置き換えられない**。
