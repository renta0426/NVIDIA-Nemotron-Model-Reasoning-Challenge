# `train_rule_based_cot_baseline.ipynb` 学習モデル Phase 0 Result 0 詳細分析

## 前提

- この結果は `baseline/cot/phase0_offline_eval/infer_rule_based_adapter_phase0_offline_eval.ipynb` で生成された `result/0` を対象にしている。
- 評価前提は `README.md` の Accuracy / `\boxed{}` 優先抽出 / fallback 抽出 / 数値相対誤差 `1e-2` に合わせた `Phase 0 Offline Eval` 準拠である。(`README.md:31-46`, `baseline/cot/phase0_offline_eval/result/0/reports/phase0_eval_manifest.md:1-30`)
- 本メモでは既存 summary に加えて、`phase0_eval_row_level.csv` / `phase0_eval_raw_outputs.csv` を再集計して、失敗の質を掘り下げた。(`baseline/cot/phase0_offline_eval/result/0/artifacts/phase0_eval_row_level.csv`, `baseline/cot/phase0_offline_eval/result/0/artifacts/phase0_eval_raw_outputs.csv`)

## 結論

この adapter の Phase 0 スコアは `216/320 = 0.6750` で、`roman` と `unit` はほぼ飽和している一方、`binary` と `symbol` が強いボトルネックになっている。特に `binary` は `0.1833`、`symbol` は `0.4333` しか出ていない。(`baseline/cot/phase0_offline_eval/result/0/reports/phase0_eval_summary.md:3-86`)

さらに重要なのは、104 件の誤答のうち 85 件が `last_number` fallback に落ちており、単純な「内容が少し違った」失敗ではなく、「長く考えた末に最終答えを boxed で安定提示できていない」失敗が支配的である点である。再集計すると誤答 104 件の内訳は `numeric_fallback=85`, `boxed=15`, `boxed_empty=4` だった。(`baseline/cot/phase0_offline_eval/result/0/artifacts/phase0_eval_row_level.csv`)

要するに、このモデルは

1. 易しい family はかなり解ける
2. しかし hard family ほど出力が極端に長文化する
3. 長文化したケースでは final answer emission が壊れやすい
4. とくに binary / symbolic exact-string 問題では、その崩れがそのまま Accuracy 崩壊に直結する

という状態にある。

## 1. スコア全体像

### セット別

| set | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `general_stable_set` | 200 | 179 | 0.8950 |
| `binary_hard_set` | 60 | 11 | 0.1833 |
| `symbol_watch_set` | 60 | 26 | 0.4333 |

(`baseline/cot/phase0_offline_eval/result/0/reports/general_stable_set_summary.md:3-68`, `baseline/cot/phase0_offline_eval/result/0/reports/binary_hard_set_summary.md:3-66`, `baseline/cot/phase0_offline_eval/result/0/reports/symbol_watch_set_summary.md:3-64`)

### family 別

| family | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `roman` | 50 | 50 | 1.0000 |
| `unit` | 50 | 49 | 0.9800 |
| `gravity` | 50 | 43 | 0.8600 |
| `text` | 50 | 37 | 0.7400 |
| `symbol` | 60 | 26 | 0.4333 |
| `binary` | 60 | 11 | 0.1833 |

(`baseline/cot/phase0_offline_eval/result/0/reports/phase0_eval_summary.md:9-18`)

### subtype 別で特に弱いところ

- `bit_structured_byte_formula`: `1/14 = 0.0714`
- `bit_other`: `10/46 = 0.2174`
- `glyph_len5`: `0/20 = 0.0000`
- `numeric_2x2`: `26/40 = 0.6500`

(`baseline/cot/phase0_offline_eval/result/0/reports/phase0_eval_summary.md:20-31`)

この時点で、binary は「全般的に弱い」が、特に structured byte formula が壊滅的で、symbol は「numeric っぽい部分はそこそこ解けるが、glyph 文字列は全滅」という分離がはっきり出ている。

## 2. 最大の問題は reasoning より final answer emission の不安定さ

再集計すると、family ごとの `has_boxed` と正答率は次の通りだった。

| family | boxed rate | boxed accuracy | unboxed accuracy |
| --- | ---: | ---: | ---: |
| `binary` | 0.2167 | 0.8462 | 0.0000 |
| `gravity` | 0.8800 | 0.9545 | 0.1667 |
| `roman` | 1.0000 | 1.0000 | - |
| `symbol` | 0.5833 | 0.7429 | 0.0000 |
| `text` | 0.8600 | 0.8810 | 0.0000 |
| `unit` | 0.9800 | 1.0000 | 0.0000 |

(`baseline/cot/phase0_offline_eval/result/0/artifacts/phase0_eval_row_level.csv`)

この表が示していることはかなり強い。

- `binary`, `symbol`, `text` は **boxed できなかった瞬間に実質全滅**。
- `gravity` も unboxed だと `1/6` しか拾えていない。
- 逆に boxed できたケースでは多くの family で高確率に当たる。

つまり、この adapter は「問題の核心をある程度掴んでいても、採点器が拾える final answer へ安定着地できない」症状が非常に強い。

## 3. 長文化と誤答が強く結びついている

正解時と不正解時の `raw_output` 文字数を比べると差が大きい。

| family | correct 平均長 | incorrect 平均長 |
| --- | ---: | ---: |
| `binary` | 8120 | 17504 |
| `gravity` | 9445 | 16498 |
| `symbol` | 2143 | 22902 |
| `text` | 7968 | 19516 |
| `unit` | 2658 | 432 |

(`baseline/cot/phase0_offline_eval/result/0/artifacts/phase0_eval_raw_outputs.csv`, `baseline/cot/phase0_offline_eval/result/0/artifacts/phase0_eval_row_level.csv`)

特に深刻なのは以下。

- `binary`: 60 件中 50 件が 1 万文字超、49 件が 1.5 万文字超
- `symbol`: 60 件中 33 件が 1 万文字超、21 件が 2 万文字超、5 件が 3 万文字超
- `text`: 50 件中 21 件が 1 万文字超、11 件が 2 万文字超

(`baseline/cot/phase0_offline_eval/result/0/artifacts/phase0_eval_raw_outputs.csv`)

このモデルは hard family に入ると「考え続ける」方向へ崩れやすく、README 準拠評価ではそのまま `last_number` fallback に吸われる。したがって、ここでの主問題は「もっと長く考えさせる」ことではなく、「短く、確実に boxed final answer を出させる」ことである。

## 4. binary の崩れ方

### 4.1 スコア面

- 全体: `11/60 = 0.1833`
- `verified_trace_ready`: `7/20 = 0.3500`
- `answer_only_keep`: `3/20 = 0.1500`
- `manual_audit_priority`: `1/20 = 0.0500`
- `bit_structured_byte_formula`: `1/14 = 0.0714`

(`baseline/cot/phase0_offline_eval/result/0/reports/binary_hard_set_summary.md:3-66`)

`verified_trace_ready` に限定しても 0.35 しかない。つまり「trace 教師として比較的安全」と判定した行を学習させた程度では、binary を安定攻略できていない。

### 4.2 失敗類型

再集計した 60 行の binary failure kind は以下だった。

- `correct`: 11
- `unboxed_binary_present`: 47
- `boxed_binary_wrong`: 2

(`baseline/cot/phase0_offline_eval/result/0/artifacts/phase0_eval_row_level.csv`)

この 47 件は「8-bit らしき binary 断片は本文に出るが、boxed final answer として安定提出できていない」ケースである。実際、binary では

- `boxed_non_empty`: 13 行中 11 正解
- `last_number`: 47 行中 0 正解

だった。(`baseline/cot/phase0_offline_eval/result/0/artifacts/phase0_eval_row_level.csv`)

つまり binary の主障害はほぼ明確で、**boxed できた時は強いが、boxed できないと 0 点** である。

### 4.3 ただし extractor だけ直しても足りない

binary の 49 誤答に対して、`gold_answer` が raw output のどこかに出ていたのは 12 件しかなかった。さらに raw output に出た 8-bit 候補列のうち

- 最初の 8-bit 候補が gold と一致: 0 件
- 最後の 8-bit 候補が gold と一致: 2 件

だった。(`baseline/cot/phase0_offline_eval/result/0/artifacts/phase0_eval_raw_outputs.csv`)

これは大事で、binary 失敗の大半は「正しい 8-bit を一度は出していたのに extractor が拾い損ねた」ではない。むしろ、

- 推論途中の partial number (`1`, `010`, `179`) を最後に残す
- 複数候補を延々と検討し、最後に 8-bit final answer を固定しない
- boxed しても内容自体が 1 bit ずれている

が主流である。

### 4.4 代表例

- `12e947ca`: gold `00111110` に対し prediction は `1`。10-shot の長い bit reasoning を出した後、評価は `last_number` を拾っている。(`baseline/cot/phase0_offline_eval/result/0/artifacts/phase0_eval_row_level.csv:33413`)
- `de11a23a`: gold `00000001` に対し `\boxed{00000000}` 系で誤答。boxed 自体はできているが内容がずれている。(`baseline/cot/phase0_offline_eval/result/0/artifacts/phase0_eval_row_level.csv:37498`)

### 4.5 holdout の見え方

binary holdout eval は行数が小さいので過信は禁物だが、`gap_signature` fold 4 は `0/10`、`structured_family` fold 1 は `5/40 = 0.125`、`solver_family` の良い slice でも `7/20 = 0.35` が上限だった。(`baseline/cot/phase0_offline_eval/result/0/artifacts/phase0_binary_holdout_accuracy.csv:1-17`)

つまり binary の弱さは一部 fold だけの事故ではなく、広い slice に跨っている。

## 5. symbol の崩れ方

### 5.1 スコア面

- 全体: `26/60 = 0.4333`
- `numeric_2x2`: `26/40 = 0.6500`
- `glyph_len5`: `0/20 = 0.0000`
- `verified_trace_ready`: `15/15 = 1.0000`
- `answer_only_keep`: `11/15 = 0.7333`
- `manual_audit_priority`: `0/30 = 0.0000`

(`baseline/cot/phase0_offline_eval/result/0/reports/symbol_watch_set_summary.md:3-64`)

ここから読めるのは、symbol は一枚岩ではないということだ。

- `numeric_2x2` はまだ戦えている
- しかし glyph exact-string 変換は全滅
- 特に `manual_audit_priority` は 30/30 全滅

これは「数値っぽく解ける symbol」は解けるが、「記号列を exact に写像する string transduction」はまだ学習できていない、ということを意味する。

### 5.2 失敗類型

再集計した symbol 60 行の failure kind は以下。

- `correct`: 26
- `numeric2x2_unboxed_wrong`: 12
- `numeric2x2_boxed_wrong`: 2
- `glyph_boxed_wrong`: 7
- `glyph_unboxed_wrong`: 13

(`baseline/cot/phase0_offline_eval/result/0/artifacts/phase0_eval_row_level.csv`)

つまり symbol は binary より少し複雑で、

- numeric っぽいものは unboxed fallback に落ちる
- glyph は boxed しても exact string がずれる

の二重失敗になっている。

### 5.3 代表例

- `b13d511a`: gold `\&[[` に対し prediction は `&[[`。leading backslash を落としており、string exactness で負けている。(`baseline/cot/phase0_offline_eval/result/0/artifacts/phase0_eval_row_level.csv:56476`)
- `d7e5414c`: gold `|%\\` に対し prediction は `4`。記号列問題にもかかわらず `last_number` fallback が発動している。(`baseline/cot/phase0_offline_eval/result/0/artifacts/phase0_eval_row_level.csv:57320`)

symbol では「答えの意味は近いが表記だけ違う」ケースと、「そもそも numeric fallback へ崩れる」ケースが混在している。

## 6. general stable set 内の失敗も、かなりが emission 問題

`general_stable_set` 自体は `0.8950` と悪くないが、残る 21 誤答の質を見るとまだ roughness が大きい。

### gravity

- `43/50 = 0.8600` と良いが、7 誤答のうち 5 件では gold が raw output のどこかには出ていた。(`baseline/cot/phase0_offline_eval/result/0/artifacts/phase0_eval_raw_outputs.csv`)
- `1bde7dfb` は gold `38.89` なのに prediction は `3.3`。問題で与えられた query time を最後に残してしまっている。(`baseline/cot/phase0_offline_eval/result/0/artifacts/phase0_eval_row_level.csv:2`)
- `76a0c79a` は gold `11.14` だが `boxed_empty`。答えを boxed したつもりで中身が空になっている。(`baseline/cot/phase0_offline_eval/result/0/artifacts/phase0_eval_row_level.csv:2929`)

gravity は「解けていない」というより、「計算途中の値や空 box を最後に残す」失敗が目立つ。

### text

- `37/50 = 0.7400`
- 7 件が `last_number`
- 1 件が `boxed_empty`
- 13 誤答のうち gold が raw output のどこかに出ていたのは 1 件だけ

(`baseline/cot/phase0_offline_eval/result/0/reports/general_stable_set_summary.md:3-68`, `baseline/cot/phase0_offline_eval/result/0/artifacts/phase0_eval_raw_outputs.csv`)

text は gravity より厳しい。こちらは extraction だけでなく、推論自体が長文化の末に崩れているケースが多い。

- `6de757af`: gold `the golden cat creates`、prediction 空、`boxed_empty`。(`baseline/cot/phase0_offline_eval/result/0/artifacts/phase0_eval_row_level.csv:20796`)

### unit

- `49/50 = 0.9800`
- 唯一の失敗 `e6baee52` は prediction `27.32`。出力には `<tool_call>` 断片が混じっており、最終 answer emission が壊れている。(`baseline/cot/phase0_offline_eval/result/0/artifacts/phase0_eval_row_level.csv:15636`)

## 7. なぜ baseline 学習とこの失敗がつながるのか

`baseline/cot/train_rule_based_cot_baseline.ipynb` では、学習テキストを

- user: prompt + `Put your final answer inside \boxed{}`
- assistant: `generated_cot` 全文 + `\boxed{answer}`

として組み立て、`SFTTrainer` に `dataset_text_field="text"` でそのまま渡している。(`baseline/cot/train_rule_based_cot_baseline.ipynb:362-383`, `baseline/cot/train_rule_based_cot_baseline.ipynb:471-498`)

この recipe 自体は自然だが、今回の Phase 0 挙動と突き合わせると、少なくとも以下とは整合的である。

1. モデルは長い trace を模倣する方向には強く引かれている
2. しかし final boxed answer を短く・安定して閉じる習慣は十分に固定されていない
3. そのため hard family ほど「それっぽい長考」はするが、採点に必要な exact final answer emission を落とす

この弱点を潰すために、こちらで整備した Phase 1 notebook では assistant 開始 token 以降だけを loss 対象にする masked training を実装している。(`baseline/cot/phase1_assistant_only/train_rule_based_cot_phase1_assistant_only.ipynb:770-790`, `baseline/cot/phase1_assistant_only/train_rule_based_cot_phase1_assistant_only.ipynb:808-902`)

もちろん「full-text SFT だから必ず失敗する」とまでは言えない。ただし、今回 observed された

- 長文化
- unboxed drift
- boxed empty
- last-number fallback 汚染

は、assistant-only final emission をより強く学習させたい、という Phase 1 方針をかなり強く支持している。

## 8. 以前の小サンプルは楽観的すぎた

以前の README 互換 sample 再採点では

- `rule_base-600`: `25/30 = 0.8333`
- `rule_base-800`: `24/30 = 0.8000`

で、binary もどちらも `5/10 = 0.5000`、symbol も `4/4 = 1.0000` だった。(`baseline/cot/phase0_offline_eval/reports/rule_based_adapter_readme_inference_samples_rule_base-600_summary.md:3-78`, `baseline/cot/phase0_offline_eval/reports/rule_based_adapter_readme_inference_samples_rule_base-800_summary.md:3-78`)

しかし今回の Phase 0 result 0 は

- overall `0.6750`
- binary `0.1833`
- symbol `0.4333`

である。(`baseline/cot/phase0_offline_eval/result/0/reports/phase0_eval_summary.md:3-86`)

したがって、以前の 30 行 sample は「adapter が広く安定した」という証拠にはならず、むしろ easy/curated slice に偏っていたと見るべきである。特に binary と symbol は、少数 sample の印象よりずっと厳しい。

## 9. 改善優先度

この result 0 から見た優先順位は明確である。

### 最優先

- `binary` の final 8-bit answer emission 安定化
- `symbol` の exact-string emission 安定化

### 次点

- `gravity` / `text` の long-output drift 抑制
- `boxed_empty` と `last_number` fallback 汚染の抑制

### 優先度低

- `roman`, `unit` はほぼ飽和しているので、ここをさらに詰めても全体スコア改善幅は小さい

## 10. 実務的な判断

この adapter は「何も学べていない」のではない。むしろ

- `roman` は完成
- `unit` は完成に近い
- `gravity` もかなり強い
- `text` も中位以上

まで来ている。

ただし competition 的には、`binary` と `symbol` がこのままだと致命的で、Phase 0 0.675 は 0.9 必達ラインからはまだ遠い。今やるべきは、さらに trace を長くすることではなく、

1. assistant-only loss への移行
2. binary / symbol の answer-emission discipline 強化
3. binary hard / symbol watch を昇格判定の主ゲートにする

である。

この result 0 は、その優先順位をかなり明瞭に示す失敗解析結果になっている。
