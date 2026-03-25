# cuda-train-data-analysis-v1 最終サマリーレポート

## 1. このフォルダの目的

このフォルダは、`try-cuda-train-data-analyst-plan.md` に基づいて実施した **学習データ分析タスクの最終成果物一式** です。

`README.md` では、このコンペの評価は **Accuracy（最終解答の正答率）** で決まり、Nemotron は最終答を `\boxed{}` に入れて出力する前提になっています。  
そのため今回の分析では、次を最優先にしました。

- 信頼できる教師データを最大化すること
- 強い教師行と曖昧な行を分離すること
- 怪しいラベルは無理に学習へ入れず除外すること
- 残る難所に対して、次の人手監査キューを明確にすること

この作業では **学習は一切実行していません**。このフォルダは分析専用です。

## 2. 最終結論の要約

`data/train.csv` の **9,500 行を全件分析** しました。

### 最終 selection tier

| selection_tier | rows | share |
| --- | ---: | ---: |
| `verified_trace_ready` | 5,862 | 61.7% |
| `answer_only_keep` | 1,075 | 11.3% |
| `manual_audit_priority` | 2,534 | 26.7% |
| `exclude_suspect` | 29 | 0.3% |

### この数字の意味

- 安全側の学習コア: `5,862 + 1,075 = 6,937` 行（`73.0%`）
- 未解決 / 要注意: `2,534 + 29 = 2,563` 行（`27.0%`）
- 結論: **かなり良いが、完璧ではない**

## 3. family ごとの最終結果

| family | total | verified | answer_only | manual | exclude | 概要 |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `roman_numeral` | 1,576 | 1,576 | 0 | 0 | 0 | 実質完了 |
| `gravity_constant` | 1,597 | 1,597 | 0 | 0 | 0 | 実質完了 |
| `unit_conversion` | 1,594 | 1,594 | 0 | 0 | 0 | 実質完了 |
| `text_decryption` | 1,576 | 605 | 971 | 0 | 0 | 未解決分は clean な answer-only に昇格 |
| `bit_manipulation` | 1,602 | 381 | 0 | 1,202 | 19 | 主要な残課題 |
| `symbol_equation` | 1,555 | 109 | 104 | 1,332 | 10 | 主要な残課題 |

### 解釈

- `roman` / `gravity` / `unit` は、curation の観点ではほぼ完成です。
- `text` は accuracy 向けの教師としてかなり良い状態ですが、`971` 行は **answer-only** であり、完全な reasoning trace 教師ではありません。
- 残る主要ボトルネックは `bit_manipulation` と `symbol_equation` です。

## 4. 今回の主な改善点

### 4.1 binary の改善

binary では、既存の単純規則だけでなく次の rule family を追加で当てました。

- bit permutation / inversion
- 2-bit boolean
- 3-bit boolean
- GF(2) affine XOR
- byte-level transform（`shift` / `rotate` / `mask`）

結果:

- 以前の solved 参照値: `306`
- 最終 verified binary: `381`
- 改善幅: `+75`
- さらに residual binary scan で、**一意 affine / low-gap / gold 不一致** の `11` 行を `exclude_suspect` へ移した

### 4.2 text の改善

今回もっとも大きかったのは text の整理です。

- 未解決 text は **壊れた cipher** ではありませんでした
- 主因は、query に必要な暗号文字が examples に 1〜6 文字足りないことでした
- そのため、`971` 行すべてを **clean answer-only** として昇格できました

結果:

- `605 verified`
- `971 answer-only`
- `0 manual`

### 4.3 symbol の改善

symbol は大きく 2 つに分かれました。

- `numeric_2x2`
- `glyph_len5`

`numeric_2x2` では、operator-aware の row-local formula search に加えて、pass1 manual curation で exact な文字列テンプレート規則（`concat_xy`, `concat_yx`, `abs_diff_2d`, `abs_diff_2d_op_suffix`）を安全側で採用しました。

- `109 verified`
- `104 answer-only`
- 直近の residual scan では `824d4bcb` を `verified`、`9cb03277` を `answer_only` に追加し、`4c6cf9d9` を `exclude_suspect` に落とした

`glyph_len5` では:

- `70` 行が multiset 風の粗い仮説に整合
- そのうち `46` 行は global output-order DAG にも整合
- ただし dedicated glyph pass1 recheck でも **安全昇格 0 / 安全除外 0**
- さらに exact examples-only coarse enumeration を追加した結果も、`33 query_has_unseen_chars / 12 ambiguous_multiset / 1 ambiguous_order / 0 unique_string`
- この `46` 行は、引き続き glyph 系 manual audit の最優先候補です
- つまり、現行の multiset/order 系 coarse family は round2 glyph に対して **追加回収源としてはほぼ枯れている** と判断できる

### 4.4 pass1 manual pack の圧縮

最優先で人手確認すべき pack は **558 行** まで縮みました。

- `373` 行: `symbol_numeric_same_op`
- `139` 行: `binary_low_gap`
- `46` 行: `symbol_glyph_multiset`

次の curation ループはここから始めるのが最短です。

## 5. 最終成果物一覧

### 5.1 最重要 CSV

| path | 役割 |
| --- | --- |
| `artifacts/train_row_analysis_v1.csv` | 9,500 行すべての分析台帳 |
| `artifacts/train_recommended_learning_target_v1.csv` | 推奨学習対象（`verified + answer_only`） |
| `artifacts/train_verified_trace_ready_v1.csv` | 最も信頼度の高い trace-ready 教師 |
| `artifacts/train_answer_only_keep_v1.csv` | clean な answer-only 教師 |
| `artifacts/train_manual_audit_priority_v1.csv` | まだ人手確認が必要な行 |
| `artifacts/train_exclude_suspect_v1.csv` | 学習から外すべき怪しい行 |
| `artifacts/manual_pass1_priority_pack_v1.csv` | 最初に見るべき manual review pack |
| `artifacts/teacher_coverage_recovery_v1.csv` | 過去 coverage との差分 |
| `artifacts/family_summary_v1.csv` | family ごとの最終集計 |
| `artifacts/selection_summary_v1.csv` | selection tier の最終集計 |

### 5.2 専門補助 artifacts

| path | 役割 |
| --- | --- |
| `artifacts/text_answer_completion_summary_v1.csv` | 971 行の text answer-only 昇格内訳 |
| `artifacts/binary_cluster_summary_v1.csv` | 未解決 binary のクラスタ要約 |
| `artifacts/binary_affine_low_gap_exclude_v1.csv` | 一意 affine だが gold と衝突したため `exclude_suspect` に移した binary 行 |
| `artifacts/binary_affine_mismatch_candidates_v1.csv` | affine 一意でも gold と衝突したため昇格しなかった binary 行 |
| `artifacts/binary_round2_cluster_summary_v1.csv` | `binary_low_gap` 139 行を gap 構造と uniqueness flag で round2 向けに cluster 化した台帳 |
| `artifacts/symbol_operator_summary_v1.csv` | numeric symbol の operator 別内訳 |
| `artifacts/symbol_string_template_promotions_v1.csv` | pass1 で安全昇格した `concat_xy / concat_yx` 行の一覧 |
| `artifacts/remaining_symbol_query_only_rejection_v1.csv` | query 答えだけ見ると単純算術に見えるが、prompt 証拠で却下した symbol 32 行の台帳 |
| `artifacts/remaining_symbol_known_family_mimics_v1.csv` | low-shot を含む known-family mimic 行の台帳 |
| `artifacts/remaining_symbol_mimic_union_v1.csv` | report 17 と known-family mimic を合流した `symbol` dead-end slice の union |
| `artifacts/symbol_round2_cluster_summary_v1.csv` | query-only / derived-template を除いた残差 symbol を round2 向けに cluster 化した台帳 |
| `artifacts/glyph_round2_cluster_summary_v1.csv` | glyph 46 行を答え長・重複構造ベースで round2 向けに cluster 化した台帳 |
| `artifacts/glyph_multiset_summary_v1.csv` | glyph の coarse feasibility 要約 |
| `artifacts/glyph_query_consistent_v1.csv` | query+gold を加えても coarse model に乗る 5 行 |
| `artifacts/glyph_exact_coarse_predictions_v1.csv` | round2 glyph 46 行を exact examples-only coarse model で再列挙した台帳 |
| `artifacts/symbol_tail_probe_summary_v1.csv` | 最終段階の symbol tail probe 結果 |

## 6. 実行ファイル概要

### `code/train_data_analysis_v1.py`

このファイルが **全分析をまとめた単一実装** です。

主な責務:

- `versions/v1/code/train.py` の parser / metadata を再利用
- family ごとに各行を解析
- `verified_trace_ready` / `answer_only_keep` / `manual_audit_priority` / `exclude_suspect` を割り当て
- `artifacts/` に CSV を出力
- `reports/` に Markdown レポートを出力

主要関数:

- `analyze_bit_row(...)`
- `analyze_text_row(...)`
- `analyze_symbol_row(...)`
- `analyze_row(...)`
- `build_reports(...)`
- `run_analysis(...)`
- `main()`

### 再実行コマンド例

```bash
cd /home/renta0426/kaggle/NVIDIA-Nemotron-Model-Reasoning-Challenge
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=.venv/lib/python3.12/site-packages \
python3 cuda-train-data-analysis-v1/code/train_data_analysis_v1.py \
  --repo-root /home/renta0426/kaggle/NVIDIA-Nemotron-Model-Reasoning-Challenge \
  --out-root /home/renta0426/kaggle/NVIDIA-Nemotron-Model-Reasoning-Challenge/cuda-train-data-analysis-v1
```

## 7. 各レポートの概要

| report | 内容 |
| --- | --- |
| `reports/00_kickoff.md` | 初期スコープと制約の確認 |
| `reports/01_overview.md` | 初回の全体像と高優先 manual 行 |
| `reports/02_hard_family_findings.md` | binary / text / symbol の solver 調査 |
| `reports/03_curation_recommendations.md` | selection tier ごとの使い方 |
| `reports/04_mid_results.md` | 改善前半時点の中間スナップショット |
| `reports/05_symbol_split_notes.md` | symbol が `numeric_2x2` と `glyph_len5` に分かれることの整理 |
| `reports/06_text_unknown_notes.md` | text answer-completion の最終整理 |
| `reports/07_binary_cluster_notes.md` | 未解決 binary のクラスタと上位 manual 候補 |
| `reports/08_symbol_operator_notes.md` | numeric operator 別の内訳と glyph 要約 |
| `reports/09_manual_pass1_pack.md` | 最初に着手すべき manual pack |
| `reports/10_glyph_probe_notes.md` | 失敗した simple transducer 方向の記録 |
| `reports/10_glyph_order_probe.md` | multiset + order DAG に整合する glyph 候補 |
| `reports/11_latest_snapshot.md` | 最終状態を最短で確認できるスナップショット |
| `reports/12_symbol_tail_probes.md` | 最終段階の symbol 残差 probe |
| `reports/13_manual_curation_pass1.md` | pass1 で安全昇格した symbol 行と、昇格しなかった binary/glyph の根拠 |
| `reports/14_symbol_residual_template_scan.md` | residual scan で採用 / 不採用 / suspect 化した symbol 行の根拠 |
| `reports/15_binary_residual_affine_scan.md` | binary low-gap の residual scan で除外した 11 行と、保留行の根拠 |
| `reports/16_glyph_manual_hold.md` | glyph pass1 46 行を全件 manual 維持にした根拠 |
| `reports/17_symbol_query_only_rejection.md` | query 答えだけでは救えそうに見える 32 行を、same-op 照合で全却下した根拠 |
| `reports/18_symbol_next_safe_scan.md` | query-only 却下後の残差に対して次の safe family を探したが、derived template 探索でも 0 件だった記録 |
| `reports/19_pass1_completion_and_round2.md` | pass1 の完了範囲と、round2 で最初に読むべき残差 cluster をまとめた要約 |
| `reports/20_symbol_round2_cluster_map.md` | mimic union を除いた `symbol_numeric_same_op` 317 行を operator / answer 長 / 埋め込み有無で cluster 化した round2 入口 |
| `reports/21_glyph_round2_cluster_map.md` | `symbol_glyph_multiset` 46 行を長さ・重複署名で cluster 化した round2 入口 |
| `reports/22_binary_round2_cluster_map.md` | `binary_low_gap` 139 行を gap / uniqueness 構造で cluster 化した round2 入口 |
| `reports/23_symbol_known_family_mimics.md` | report 17 と extra known-family mimic を合流した `symbol` mimic union の整理 |
| `reports/24_glyph_exact_coarse_scan.md` | round2 glyph 46 行を exact examples-only coarse model で再列挙し、0 unique string を確認した report |
| `reports/25_symbol_star4_cluster_hold.md` | round2 `symbol` の `*` 4桁 top 2 cluster（39 行）を再読し、依然 manual hold とした根拠 |
| `reports/26_symbol_plus3_cluster_hold.md` | round2 `symbol` の `+` 3桁 cluster を再読し、依然 manual hold とした根拠 |
| `reports/27_binary_top_cluster_hold.md` | round2 `binary` の top 34-row cluster を再読し、依然 manual hold とした根拠 |

## 8. 最短の読み順

時間がない場合は、次の順で読めば十分です。

1. `reports/11_latest_snapshot.md`
2. `artifacts/train_recommended_learning_target_v1.csv`
3. `artifacts/manual_pass1_priority_pack_v1.csv`
4. `reports/15_binary_residual_affine_scan.md`
5. `reports/14_symbol_residual_template_scan.md`
6. `code/train_data_analysis_v1.py`

## 9. 現状の課題

### 9.1 binary がまだ重い

- `bit_manipulation` はまだ `1,202 manual + 19 exclude`
- 2-bit / 3-bit / affine XOR / byte transform まで当てても、なお多数が未解決
- 未解決群の中心は「少なくとも一部 bit position で単純候補が立たない」ケース
- low-gap で一意 affine と gold が衝突する `11` 行は今回除外できたが、それ以外の affine mismatch は gap が大きく、まだ安全に切れない
- round2 の top binary cluster（`34` 行, `7 examples / 1 no-candidate / 0 multi-candidate`）も再読したが、affine / boolean / byte family のどれも unique ではなく、consensus mismatch も無いので safe promotion / safe exclusion の両方ができない
- つまり次は、より広い boolean/circuit family か、より複雑な non-local byte transform を考える必要がある

### 9.2 symbol がまだ重い

- `symbol_equation` は `1,332 manual + 10 exclude`
- `numeric_2x2` は operator-aware と string-template pass1 でかなり整理できたが、まだ `373` 行が pass1 に残る
- 小さい線形族（`ax + by + c`、`min/max/avg_if_int`）の追加 probe では **安全な追加回収 0**
- query 答えだけだと `x_plus_y / x_minus_y / abs_diff_2d` に見える `32` 行も再照合したが、`27` 行は same-op examples と衝突、`5` 行は符号/prefix format が一意化できず、**追加昇格 0**
- さらに、非 query-only 残差の `+` 3桁 / `*` 4桁 / operator 埋め込み output を派生 digit-feature template で総当たりしても **追加回収 0**
- report 17 の高shot mimic `32` 行に、extra known-family / low-shot mimic を足した mimic union は `56` 行となり、round2 の `symbol` 本丸は `317` 行まで圧縮できた
- round2 `*` 4桁の top 2 cluster（bucket1=`22`, bucket2=`17`）も代表 prompt を再読したが、各 row が `+/-/*` 混在で `*` 例が 1〜2 個しか無く、再利用可能な prompt-evidenced family は見つからなかった
- round2 `+` 3桁 cluster も再読したが、bucket1 は `+` 例が 1 個しかなく、bucket2/3 でも同一 prompt 内で `2` 桁出力と `3` 桁出力が混在するため、再利用可能な exact formatter は見つからなかった
- つまり残りは、より operator-specific な式族か、非線形規則の可能性が高い
- pass1 は「安全に増やせる easy slice はかなり取り切った」とみてよく、次は cluster-first の round2 manual curation が主戦場になる

### 9.3 glyph_len5 は coarse 仮説止まり

- `70` 行は multiset 仮説に整合
- `46` 行は order DAG にも整合
- ただし coarse model が **一意でない** ため、教師として昇格できない
- query+gold を足しても整合する行は `5` 行だけあったが、それでも非一意なので manual のままにしている
- dedicated glyph pass1 recheck でも、安全昇格 0 / 安全除外 0 のままだった
- exact examples-only coarse enumeration を追加しても、`33` 行は query に example 未出現記号を含み、残る `13` 行も `12 ambiguous_multiset + 1 ambiguous_order` で、**0 unique string**
- よって現行の glyph coarse abstraction は round2 46 行に対して追加回収源としては尽きており、次に進むなら別 family 仮説が必要

### 9.4 text は accuracy 向けには強いが、trace 完全性では未完

- `text` の未解決は全部 clean answer-only にできた
- ただし `971` 行は **answer-only** であり、完全な reasoning trace 教師ではない
- したがって accuracy 寄りの SFT には有用だが、trace 蒸留の純度という意味では満額ではない

### 9.5 exclude 行は少数だが重要

- `exclude_suspect = 29`
- 数は少ないが、こうした行を無理に学習へ混ぜると `README.md` の accuracy 評価に対して逆効果になりやすい
- ここは「少ないから無視」ではなく、今後も別管理を維持するのが安全

### 9.6 次の優先順位

次に触る順番は、現状では次が合理的です。

1. `artifacts/manual_pass1_priority_pack_v1.csv`
2. round2 `symbol` core `317` 行のうち、次は `-` 3桁 / operator 埋め込み output
3. `binary_low_gap` 139 行
4. `glyph_len5` 46 行は、新しい family 仮説が立つまで hold

## 10. 検証メモ

repo 反映後に次を確認しています。

- `python3 -m py_compile cuda-train-data-analysis-v1/code/train_data_analysis_v1.py`
- analysis script の smoke rerun
- `python3 -m pytest -q -k 'not test_scaffold_runbook_and_ablation_failure_logging'`

確認結果:

- `125 passed, 1 deselected`

なお full test suite では、今回の変更とは無関係の既存 failure が 1 件あります。

- `versions/v3/tests/test_candidate_promotion.py::test_scaffold_runbook_and_ablation_failure_logging`

## 11. 最終まとめ

このフォルダは、今回の train data analysis pass の **最終パッケージ** と見なしてよいです。

重要なポイントは次の 3 つです。

- **安全に学習へ回せる中核教師集合** はできた
- 不確実性は全体に散らばらず、`binary` と `symbol` に集中した
- 次の作業は `manual_pass1_priority_pack_v1.csv` から始めればよい

accuracy 重視の Nemotron fine-tuning に使う主成果物は `artifacts/train_recommended_learning_target_v1.csv` です。  
次の manual curation に使う主成果物は `artifacts/manual_pass1_priority_pack_v1.csv` です。
