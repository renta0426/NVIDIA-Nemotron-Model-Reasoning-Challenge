# Phase 2.1 Binary Specialist Result 2_1 Merge LoRA 詳細分析

## 前提

- 対象は `baseline/cot/phase0_offline_eval/result/2_1_merge_lora` 配下の Phase 0 offline eval 結果。
- 評価基準は `README.md` の Accuracy / `\boxed{}` 優先抽出 / fallback 抽出 / numeric tolerance に合わせる。(`README.md:31-46`, `baseline/cot/phase0_offline_eval/result/2_1_merge_lora/reports/phase0_eval_manifest.md`)
- 学習 notebook の source は `baseline/cot/phase2_1_merge_lora/train-rule-based-cot-baseline_phase2_1_merge_lora.ipynb`、学習データの一次情報は `baseline/cot/phase2_1_merge_lora/artifacts/phase2_1_binary_specialist_manifest.json` を優先した。(`baseline/cot/phase2_1_merge_lora/train-rule-based-cot-baseline_phase2_1_merge_lora.ipynb:330-349`, `baseline/cot/phase2_1_merge_lora/artifacts/phase2_1_binary_specialist_manifest.json:1-64`)
- 運用上、ノートブックはローカルそのままではなく **Kaggle 環境へコピーして実行**しているため、ローカル ipynb に埋め込まれた保存済み stdout は最新実行を保証しない。したがって本メモでは **result フォルダの評価結果と manifest を一次情報**として扱う。(`User input`)
- 比較対象は `result/0`, `result/1`, `result/2`, `result/2-1`, および sister run の `result/2_2_merge_lora`。(`baseline/cot/phase0_offline_eval/result/0/reports/phase0_eval_summary.md`, `baseline/cot/phase0_offline_eval/result/1/reports/phase0_eval_summary.md`, `baseline/cot/phase0_offline_eval/result/2/reports/phase0_eval_summary.md`, `baseline/cot/phase0_offline_eval/result/2-1/reports/phase0_eval_summary.md`, `baseline/cot/phase0_offline_eval/result/2_2_merge_lora/reports/phase0_eval_summary.md`)

## 結論

この実験は、**binary を specialist 化して binary-only 1449 行へ拡張しても、hard binary の本丸を押し上げられなかった**、という結論になる。

- overall は **`200/320 = 0.6250`**
- `binary_hard_set` は **`10/60 = 0.1667`**
- `bit_structured_byte_formula` は **`2/14`**
- binary の **exact 8-bit 一致**は **`7/60`** に留まり、`result/2` の **`9/60`** を下回った
- `general_stable_set` は **`169/200`** と `result/2_2_merge_lora` よりは保ったが、mixed DSL の `190/200` からは大きく低下した

つまり今回の 2.1 は、

1. **target family の binary を伸ばすことにも失敗**
2. **mixed generalist が持っていた汎化もかなり落とした**
3. **binary specialist と言っても submission 候補としては `result/2` より明確に弱い**

という位置づけである。(`baseline/cot/phase0_offline_eval/result/2_1_merge_lora/reports/phase0_eval_summary.md`, `baseline/cot/phase0_offline_eval/result/2/reports/phase0_eval_summary.md`)

## 1. 実験内容の事実整理

### 1.1 学習データ

manifest によると、この specialist は `train_row_analysis_v1.csv` から作った **binary-only curated set 1449 行**で学習している。内訳は

- `verified_trace_ready = 1004`
- `answer_only_keep = 445`
- `assistant_style: trace_boxed = 1004`, `boxed_only = 445`

である。(`baseline/cot/phase2_1_merge_lora/artifacts/phase2_1_binary_specialist_manifest.json:2-17`)

template subtype は次の通り。

| subtype | rows |
| --- | ---: |
| `bit_structured_byte_formula` | 851 |
| `bit_other` | 508 |
| `bit_permutation_inversion` | 90 |

(`baseline/cot/phase2_1_merge_lora/artifacts/phase2_1_binary_specialist_manifest.json:18-22`)

特に重要なのは、**最難所の `bit_structured_byte_formula` が学習行の過半**を占めている点である。加えて manifest は、

- binary trace は `phase2` の DSL scratchpad を再利用
- answer-only binary row は boxed-only
- `<think>` 内で最終 8-bit を繰り返さない

という設計だったことも示している。(`baseline/cot/phase2_1_merge_lora/artifacts/phase2_1_binary_specialist_manifest.json:35-46,58-64`)

### 1.2 学習設定

notebook source 上の学習設定は次だった。

- `LORA_RANK = 32`
- `NUM_EPOCHS = 2`
- `BATCH_SIZE = 1`
- `GRAD_ACCUM = 4`
- `LR = 1e-4`
- `MAX_SEQ_LEN = 2048`
- `target_modules = "all-linear"`

(`baseline/cot/phase2_1_merge_lora/train-rule-based-cot-baseline_phase2_1_merge_lora.ipynb:330-349`, `baseline/cot/phase2_1_merge_lora/train-rule-based-cot-baseline_phase2_1_merge_lora.ipynb:1218-1249`)

つまり、**変更の中心はモデル設定ではなくデータ specialization** だった。

## 2. スコア全体像

### 2.1 他 run との比較

| result | overall | general_stable | binary_hard | symbol_watch |
| --- | ---: | ---: | ---: | ---: |
| `result/0` | 0.6750 | 0.8950 | 0.1833 | 0.4333 |
| `result/1` | 0.7031 | 0.9400 | 0.2000 | 0.4167 |
| `result/2` | 0.7094 | 0.9500 | 0.2167 | 0.4000 |
| `result/2-1` | 0.6750 | 0.9200 | 0.1333 | 0.4000 |
| `result/2_1_merge_lora` | 0.6250 | 0.8450 | 0.1667 | 0.3500 |

(`baseline/cot/phase0_offline_eval/result/0/reports/phase0_eval_summary.md`, `baseline/cot/phase0_offline_eval/result/1/reports/phase0_eval_summary.md`, `baseline/cot/phase0_offline_eval/result/2/reports/phase0_eval_summary.md`, `baseline/cot/phase0_offline_eval/result/2-1/reports/phase0_eval_summary.md`, `baseline/cot/phase0_offline_eval/result/2_1_merge_lora/reports/phase0_eval_summary.md`)

binary specialist の target は binary だったが、結果は

- `result/2` 比で overall **`-27 correct`**
- `result/1` 比で overall **`-25 correct`**
- `result/0` 比でも overall **`-16 correct`**

である。binary だけを見ても **`13/60 -> 10/60`** なので、mixed DSL より悪い。(`baseline/cot/phase0_offline_eval/result/2/reports/phase0_eval_summary.md`, `baseline/cot/phase0_offline_eval/result/2_1_merge_lora/reports/phase0_eval_summary.md`)

### 2.2 family 別に何が落ちたか

`result/2 -> result/2_1_merge_lora` の family 差分は次の通り。

| family | `result/2` | `2_1_merge_lora` | delta |
| --- | ---: | ---: | ---: |
| `binary` | 0.2167 | 0.1667 | -0.0500 |
| `gravity` | 0.9400 | 0.7800 | -0.1600 |
| `roman` | 1.0000 | 1.0000 | 0.0000 |
| `symbol` | 0.4000 | 0.3500 | -0.0500 |
| `text` | 0.8600 | 0.8200 | -0.0400 |
| `unit` | 1.0000 | 0.7800 | -0.2200 |

(`baseline/cot/phase0_offline_eval/result/2/reports/phase0_eval_summary.md`, `baseline/cot/phase0_offline_eval/result/2_1_merge_lora/reports/phase0_eval_summary.md`)

row-level で見ても、`result/2` 比では

- 改善: `15`
- 退行: `42`

で、内訳は

- 改善: `text +7`, `binary +4`, `gravity +3`, `symbol +1`
- 退行: `unit +11`, `gravity +11`, `text +9`, `binary +7`, `symbol +4`

だった。つまり **binary specialist という名前に反して、binary で勝ち越していない**。むしろ `unit` と `gravity` の取りこぼしが overall を大きく押し下げている。(`baseline/cot/phase0_offline_eval/result/2_1_merge_lora/artifacts/phase0_eval_row_level.csv`, `baseline/cot/phase0_offline_eval/result/2/artifacts/phase0_eval_row_level.csv`)

## 3. 肝心の binary はどう壊れたか

### 3.1 binary の位置づけ

binary の推移だけを抜くと次の通り。

| result | official-like binary | exact 8-bit | tolerance-only |
| --- | ---: | ---: | ---: |
| `result/0` | 11 | 11 | 0 |
| `result/1` | 12 | 10 | 2 |
| `result/2` | 13 | 9 | 4 |
| `result/2-1` | 8 | 8 | 0 |
| `result/2_1_merge_lora` | 10 | 7 | 3 |

(`baseline/cot/phase0_offline_eval/result/0/artifacts/phase0_eval_row_level.csv`, `baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_eval_row_level.csv`, `baseline/cot/phase0_offline_eval/result/2/artifacts/phase0_eval_row_level.csv`, `baseline/cot/phase0_offline_eval/result/2-1/artifacts/phase0_eval_row_level.csv`, `baseline/cot/phase0_offline_eval/result/2_1_merge_lora/artifacts/phase0_eval_row_level.csv`)

ポイントは 2 つある。

1. binary specialist は **official-like でも exact でも `result/2` に負ける**
2. `official 10/60` のうち **`3/60` は tolerance-only** であり、strict な 8-bit closure はさらに弱い

つまり「binary-only にしたから 8-bit exactness が強化された」とは読めない。

### 3.2 subtype / tier 別

`result/2_1_merge_lora` の binary 詳細は次だった。

| slice | correct / rows | accuracy |
| --- | ---: | ---: |
| `bit_other` | 8 / 46 | 0.1739 |
| `bit_structured_byte_formula` | 2 / 14 | 0.1429 |
| `verified_trace_ready` | 7 / 20 | 0.3500 |
| `answer_only_keep` | 2 / 20 | 0.1000 |
| `manual_audit_priority` | 1 / 20 | 0.0500 |

(`baseline/cot/phase0_offline_eval/result/2_1_merge_lora/reports/binary_hard_set_summary.md:15-20,44-66`)

ここで重要なのは、

- `verified_trace_ready` は **`7/20`** で `result/2` と同じ
- `answer_only_keep` は **`2/20`** で `result/2` と同じ
- `manual_audit_priority` だけは **`4/20 -> 1/20`** へ悪化

という点である。つまり今回の specialist は、**見込みのある verified core をさらに押し上げたのではなく、mixed DSL が偶然拾えていた hard slice を落とした** と読む方が自然である。(`baseline/cot/phase0_offline_eval/result/2/reports/binary_hard_set_summary.md`, `baseline/cot/phase0_offline_eval/result/2_1_merge_lora/reports/binary_hard_set_summary.md`)

### 3.3 failure shape

binary 60 行を再集計すると、failure shape は次だった。

- `correct`: `10`
- `binary_absent`: `48`
- `unboxed_binary_present`: `1`
- `boxed_binary_wrong`: `1`

(`baseline/cot/phase0_offline_eval/result/2_1_merge_lora/artifacts/phase0_eval_row_level.csv`)

つまり binary specialist の binary 誤答は、`result/2` のような

- 8-bit っぽい候補は出る
- ただし boxed / exact が崩れる

というより、**そもそも最終 prediction 側に 8-bit byte が残っていない** ケースが大半である。

誤答バケットを全体で見ると

- `numeric_fallback = 98`
- `boxed = 16`
- `boxed_empty = 4`
- `final_answer = 2`

で、README の boxed-first metric 上も **長文化して fallback に吸われる失敗** が支配的だった。(`README.md:31-46`, `baseline/cot/phase0_offline_eval/result/2_1_merge_lora/artifacts/phase0_eval_row_level.csv`)

### 3.4 長文化

binary の `raw_output` 長を再集計すると、

- binary 全体平均: `16266.7`
- binary 誤答のみ平均: `17734.9`
- binary 60 行中 `54` 行が `>10000 chars`

だった。(`baseline/cot/phase0_offline_eval/result/2_1_merge_lora/artifacts/phase0_eval_row_level.csv`)

加えて structured binary の誤答例では、

- `2630aaf8`: gold `10111110`, prediction `0`
- `0528d502`: gold `00011111`, prediction `2`
- `55f5e590`: gold `10001111`, prediction `0`
- `9dfcd4be`: gold `10101010`, prediction `0`
- `52a9d5e4`: gold `11011111`, prediction `1`

のように、**1 桁 fallback** へ潰れる例が目立つ。(`baseline/cot/phase0_offline_eval/result/2_1_merge_lora/artifacts/phase0_eval_row_level.csv`)

これは `binary_synthetic_data_approaches_history.md` がずっと指摘してきた

- binary では exact 8-bit final answer の closure が難しい
- teacher の文体変更や行数増量だけでは hard binary の本丸を押し切れない

という歴史と整合している。(`baseline/cot/binary_synthetic_data_approaches_history.md:20-31`)

### 3.5 `result/2` 比の改善例と退行例

`result/2 -> result/2_1_merge_lora` の binary 反転 ID は、

- 改善: `4`
- 退行: `7`

だった。改善例には `de11a23a`, `009a74b6`, `5f29ae58`, `bdb93228` があり、退行例には `32e5fe87`, `5356c59d`, `004ef7c7`, `101410e4`, `71e6cae8` などがある。(`baseline/cot/phase0_offline_eval/result/2_1_merge_lora/artifacts/phase0_eval_row_level.csv`, `baseline/cot/phase0_offline_eval/result/2/artifacts/phase0_eval_row_level.csv`)

要するに binary specialist は、

- 一部の binary 個別 ID は直した
- しかし net では負け越し
- 特に manual / structured 側の粘りが落ちた

という結果だった。

## 4. target 以外の副作用

### 4.1 general stable の崩れ

`general_stable_set` は

- `result/2`: `190/200 = 0.9500`
- `result/2_1_merge_lora`: `169/200 = 0.8450`

で **`-21 correct`**。(`baseline/cot/phase0_offline_eval/result/2/reports/general_stable_set_summary.md`, `baseline/cot/phase0_offline_eval/result/2_1_merge_lora/reports/general_stable_set_summary.md`)

family 別には

- `gravity`: `47 -> 39`
- `text`: `43 -> 41`
- `unit`: `50 -> 39`
- `roman`: `50 -> 50`

で、特に `unit` の落ち方が大きい。(`baseline/cot/phase0_offline_eval/result/2/reports/phase0_eval_summary.md`, `baseline/cot/phase0_offline_eval/result/2_1_merge_lora/reports/phase0_eval_summary.md`)

### 4.2 長文化は binary 以外にも波及

wrong-only の `raw_output` 平均長は次だった。

| family | wrong-only mean raw length |
| --- | ---: |
| `binary` | 17734.9 |
| `gravity` | 3018.5 |
| `symbol` | 23718.5 |
| `text` | 21981.1 |
| `unit` | 16687.5 |

(`baseline/cot/phase0_offline_eval/result/2_1_merge_lora/artifacts/phase0_eval_row_level.csv`)

特に `text` と `unit` でも誤答時に 1 万字台後半まで伸びており、binary specialist は target family だけでなく **非 target family でも「長く考えて最後を壊す」挙動を増やした** と見える。

## 5. 2_2 specialist との比較

### 5.1 score 比較

| metric | `2_1_merge_lora` | `2_2_merge_lora` |
| --- | ---: | ---: |
| overall | 0.6250 | 0.6031 |
| general_stable_set | 0.8450 | 0.7900 |
| binary_hard_set | 0.1667 | 0.1667 |
| symbol_watch_set | 0.3500 | 0.4167 |

(`baseline/cot/phase0_offline_eval/result/2_1_merge_lora/reports/phase0_eval_summary.md`, `baseline/cot/phase0_offline_eval/result/2_2_merge_lora/reports/phase0_eval_summary.md`)

2.1 は overall では 2.2 を上回るが、その理由は **binary が強いからではない**。binary official score は同じ `10/60` で、むしろ exact 8-bit は

- `2_1`: `7/60`
- `2_2`: `8/60`

だった。(`baseline/cot/phase0_offline_eval/result/2_1_merge_lora/artifacts/phase0_eval_row_level.csv`, `baseline/cot/phase0_offline_eval/result/2_2_merge_lora/artifacts/phase0_eval_row_level.csv`)

### 5.2 勝ち負けの中身

row-level で `2_1` が `2_2` に勝っていたのは、

- `gravity +13`
- `unit +10`
- `text +7`

が主である。一方で `2_1` は `2_2` に対し

- `symbol -5`
- `binary` は **`5 gain / 5 loss`** で相殺

を持っていた。(`baseline/cot/phase0_offline_eval/result/2_1_merge_lora/artifacts/phase0_eval_row_level.csv`, `baseline/cot/phase0_offline_eval/result/2_2_merge_lora/artifacts/phase0_eval_row_level.csv`)

つまり 2.1 は **general families を少し多く残した specialist** であり、binary solve 力で勝ったわけではない。

## 6. 履歴に置いた時の意味

`binary_synthetic_data_approaches_history.md` は binary について、

1. short trace
2. long natural-language CoT
3. guarded 800
4. phase1 answer-only 分離
5. phase2 DSL
6. phase2 hybrid

までを整理しており、ピークは mixed DSL の **`13/60`** だった。(`baseline/cot/binary_synthetic_data_approaches_history.md:20-31`)

今回の 2.1 は、その次の試みとして

- **binary 全 curated core 1449 行**
- **verified 1004 + answer_only 445**
- **binary-only specialization**

まで踏み込んだが、それでも **`10/60`** で止まった。(`baseline/cot/phase2_1_merge_lora/artifacts/phase2_1_binary_specialist_manifest.json:5-17`, `baseline/cot/phase0_offline_eval/result/2_1_merge_lora/reports/binary_hard_set_summary.md`)

さらに `FINAL_SUMMARY_REPORT.md` は binary curated core を

- `1004 verified`
- `445 answer_only`
- `138 manual`
- `15 exclude`

まで整理しているが、同時に **answer_only は trace teacher の代替ではない** という運用も示している。(`cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md:100-122,142-174`)

今回の結果はまさにそれを裏づけていて、**answer-only を 445 行まで増やしても、binary rule induction と exact 8-bit closure は獲得できていない**。

## 7. まとめ

2.1 binary specialist から得られる実務的な結論は次の通り。

1. **binary-only へ隔離しても binary は伸びない**
2. **`bit_structured_byte_formula` の本丸は依然 unresolved**
3. **answer-only の増量は saturation している**
4. **mixed Phase 2 DSL の方が、binary でも overall でもまだ強い**
5. 次に触るべきは specialist volume ではなく、**exact 8-bit final-answer closure を壊さない生成制約か、structured binary 自体の別解法**である

少なくとも submission 候補として見る限り、`result/2_1_merge_lora` は **specialist 実験としては有意な知見があるが、性能面では `result/2` に置き換える理由はない**。
