## 問題整理

`README.md` の評価仕様では、最終提出は Nemotron-3-Nano-30B 用 LoRA アダプタで、正答率がそのままスコアになります。  
今回の依頼は学習ではなく `data/train.csv` 9,500 件の徹底分析であり、`try-cuda-train-result.md` が示した teacher coverage の不足、とくに `gravity/text/symbol/binary` の取りこぼし原因を洗い、最終的な学習対象抽出とデータ設定最適化につながる分析基盤を作ることです。

## 方針

1. `README.md`、`try-cuda-train-data-analyst-plan.md`、`try-cuda-train-result.md`、既存の `versions/v1` / `versions/v4` の parser・metadata・solver 実装を前提にする。
2. リポジトリ外の専用作業フォルダ `/home/renta0426/.copilot/session-state/833e73c6-310a-4ba9-89a3-7e4373bac223/files/cuda-train-data-analysis-v1/` を今回の主作業場所とし、途中結果はここへ Markdown で逐次保存する。
3. 実装は 1 ファイルの分析スクリプトに集約し、`train.csv` 全件に対して以下を出力する。
   - family / template / subfamily 相当の再分類
   - parse 可否、確信度、例数、query 抽出状況
   - 既存 solver での再現可否
   - 文字種・答え形式・長さ・丸め・特殊文字などの品質指標
   - manual audit 候補、要目視候補、怪しいラベル候補
4. 学習は一切実行しない。分析結果から「どのデータを残すか」「どの family を優先して人手監査すべきか」を明確化する。

## Todo

- `read-context`: 既読化済み。README と既存メモの確認。
- `inspect-parsers`: 既読化済み。既存 family/parser/metadata 実装の再利用候補整理。
- `create-plan`: この plan.md を作成し、作業場所を固定。
- `build-analysis-script`: 単一 Python スクリプトを作成し、分析パイプラインを実装。
- `run-analysis`: スクリプトを実行し、CSV/Markdown アーティファクトを生成。
- `summarize-results`: 中間レポートと次アクションを Markdown に書き出す。

## メモ

- `versions/v1/code/train.py` には `infer_family`、各 family parser、`build_metadata_frame`、`build_manual_audit_frame` があるため、ここを分析の主再利用元にする。
- `versions/v4/code/train.py` には `identify_bit_op` と `generator_ready` 判定があり、特に binary の「solver で一意決定できるか」を再評価するのに使える。
- 長期タスクなので、分析の節目ごとに `reports/` 以下へ Markdown を追加する。

## 進捗メモ

- 単一スクリプト `files/cuda-train-data-analysis-v1/code/train_data_analysis_v1.py` を作成し、`data/train.csv` 9,500 件を全件解析済み。
- 現時点の厳密カテゴリ分け:
  - `verified_trace_ready`: 5,863
  - `manual_audit_priority`: 2,522
  - `answer_only_keep`: 1,085
  - `exclude_suspect`: 30
- family ごとの厳密 verified:
  - roman: 1,576 / 1,576
  - gravity: 1,597 / 1,597
  - unit: 1,594 / 1,594
  - text: 605 / 1,576
  - binary: 381 / 1,602
  - symbol: 110 / 1,555
- `binary` は affine XOR と simple byte transform（shift / rotate / mask）を足したことで 381 verified まで伸び、baseline の 306 solved を上回った。
- `binary` の residual low-gap scan では、一意 affine・他候補なし・`bit_no_candidate_positions<=1`・gold 不一致の 11 行を `exclude_suspect` へ降格した。これで `binary` は `381 verified / 1202 manual / 19 exclude` になった。
- `symbol` は `numeric_2x2` の operator-aware formula search に加え、pass1 manual curation で exact prompt-backed 規則 `concat_xy / concat_yx / abs_diff_2d / abs_diff_2d_op_suffix / comp99_abs_diff_2d` を統合した。直近の更新では `comp99_abs_diff_2d` を operator-prefixed zero-pad まで拡張し、`b655eee9` を verified、`13892a7c` / `3a8a4ebc` / `6b769a9e` / `ef6bc241` を answer_only に昇格し、`9a9f6025` を exclude_suspect に移した。これで `symbol` は `110 verified / 114 answer_only / 1320 manual / 11 exclude` になった。
- `glyph_len5` pass1 の 46 行は dedicated recheck を行ったが、安全昇格 0 / 安全除外 0 だった。`glyph_query_consistent_v1.csv` の 5 行も coarse multiset+order model が非一意のため、全件 manual 維持とした。
- `glyph_len5` のうち `glyph_multiset_possible` は 70 行、そのうち example 出力に一貫した順序制約まで通る `glyph_order_acyclic` は 46 行で、`manual_pass1_priority_pack_v1.csv` の glyph 部分はこの 46 行に絞り込んだ。
- `text` の未verified 971 行は全件、gold answer により不足 1〜6 文字の monoalphabetic mapping を矛盾なく補完できることを確認し、`answer_only_keep` に昇格した。これで `text` は `verified=605 / answer_only=971 / manual=0` になった。
- `manual_pass1_priority_pack_v1.csv` は `546` 行まで圧縮され、内訳は `symbol_numeric_same_op=361`, `binary_low_gap=139`, `symbol_glyph_multiset=46`。
- `reports/13_manual_curation_pass1.md`、`reports/14_symbol_residual_template_scan.md`、`reports/15_binary_residual_affine_scan.md`、`reports/16_glyph_manual_hold.md` に、今回の安全昇格・suspect 化・非昇格判断の根拠を追加した。
- `symbol_numeric_same_op` の残り 361 行について、query 答えだけ見ると `x_plus_y / x_minus_y / abs_diff_2d / comp99_abs_diff_2d` に見える 43 行を再照合したが、`38` 行は same-op examples と衝突、`5` 行は format が未確定で、追加昇格は `0` だった。`reports/17_symbol_query_only_rejection.md` と `artifacts/remaining_symbol_query_only_rejection_v1.csv` に記録した。
- さらに、非 query-only 残差の `+` 3桁 / `*` 4桁 / operator 埋め込み output について、sum/product/diff 派生 digit-feature template を総当たりしたが、追加回収は `0` だった。`reports/18_symbol_next_safe_scan.md` に記録した。
- `binary_low_gap` 139 行について、複数 solver family が同じ誤答に収束する consensus mismatch を追加探索したが `0` 行だった。unique affine 以外の安全除外候補は依然として薄い。
- `glyph_len5` 46 行も、answer 長さ 1〜2 の短答群を含めて prompt を再読したが、この時点では safe promotion / safe exclusion に繋がる exact family はまだ見えていない。
- `reports/19_pass1_completion_and_round2.md` に、pass1 がどこまで完了したかと、round2 の優先 cluster（`*`4桁, `+`3桁, `-`3桁, operator 埋め込み output）をまとめた。
- `artifacts/symbol_round2_cluster_summary_v1.csv` と `reports/20_symbol_round2_cluster_map.md` を更新し、current mimic union 67 行を除いた `symbol_numeric_same_op` 294 行の round2 入口を cluster 化した。
- その後 `artifacts/remaining_symbol_known_family_mimics_v1.csv` と `artifacts/remaining_symbol_mimic_union_v1.csv`、`reports/23_symbol_known_family_mimics.md` を更新し、report 17 の 43 行に extra known-family / low-shot mimic を足した current union `67` 行を分離した。これで `symbol` round2 の本丸は `294` 行になった。
- `artifacts/glyph_round2_cluster_summary_v1.csv` と `reports/21_glyph_round2_cluster_map.md` を追加し、`symbol_glyph_multiset` 46 行の round2 入口も長さ・重複構造ベースで cluster 化した。
- `artifacts/binary_round2_cluster_summary_v1.csv` と `reports/22_binary_round2_cluster_map.md` を追加し、`binary_low_gap` 139 行の round2 入口も gap / uniqueness flag ベースで cluster 化した。
- `artifacts/glyph_exact_coarse_predictions_v1.csv` と `reports/24_glyph_exact_coarse_scan.md` を追加し、round2 glyph 46 行を exact examples-only coarse model で再列挙した結果、`33 query_has_unseen_chars / 12 ambiguous_multiset / 1 ambiguous_order / 0 unique_string` を確認した。現行 glyph coarse family は追加回収源としてはほぼ枯れている。
- `reports/25_symbol_star4_cluster_hold.md` を追加し、round2 `symbol` の `*` 4桁 top 2 cluster（`22 + 17` 行）を代表 prompt から再読したが、`+/-/*` 混在かつ `*` 例が 1-2 個しか無く、再利用可能な exact family は見つからなかった。
- `reports/26_symbol_plus3_cluster_hold.md` を追加し、round2 `symbol` の `+` 3桁 cluster を再読したが、bucket1 は `+` 例が 1 個しかなく、bucket2/3 も同一 prompt 内で `2` 桁出力と `3` 桁出力が混在し、再利用可能な exact formatter は見つからなかった。
- `reports/27_binary_top_cluster_hold.md` を追加し、round2 `binary` の top 34-row cluster（`7 examples / 1 no-candidate / 0 multi-candidate`）を再読したが、affine / boolean / byte family のどれも unique ではなく、safe promotion / safe exclusion の両方ができないことを確認した。
- `reports/28_symbol_minus3_cluster_hold.md` を追加し、round2 `symbol` の `-` 3-character sign-embedded slice（`19` 行）を再読したが、負号が query-only になっている行が多く、high-shot rows でも signed/unsigned output や zero-pad が揺れており、再利用可能な exact family は見つからなかった。
- `reports/29_symbol_plus2_cluster_hold.md` を追加し、round2 `symbol` の `+` 2-digit slice（`19` 行）を再読したが、high-shot rows でも `2` 桁出力と `3` 桁出力が混在し、最も単純に見える `4cf073bf` ですら `08` の zero-pad が prompt から一意化できないため、safe promotion は `0` だった。
- `reports/30_binary_second_cluster_hold.md` を追加し、round2 `binary` の second-largest 29-row cluster（`8 examples / 1 no-candidate / 0 multi-candidate`）を再読したが、top cluster と同様に no unique solver / no consensus mismatch で、safe promotion / safe exclusion の両方ができないことを確認した。
- `reports/31_symbol_comp99_abs_diff_recovery.md` を更新し、`comp99_abs_diff_2d` family を operator-prefixed zero-pad まで広げて累計 `2 verified + 9 answer_only + 1 exclude` を確定した。
- `reports/32_symbol_small_custom_op_hold.md` を追加し、current `$ / @ / } / &` の small custom-op cluster を再読したが、cluster 内で output style が崩れており、既存 prefix family を超える安全な再利用規則は見つからなかった。
- `reports/33_symbol_custom4_cluster_hold.md` を追加し、current `! / " / $ / % / [` の 4桁 custom-op cluster `19` 行を再読した。さらに raw digits・pair sums/diffs/products・2-digit `x/y/x+y/|x-y|/x*y` の simple digit-template probe を当てても full-string family は 0 件で、全件 manual 維持とした。
- `reports/34_symbol_minus1_bucket2_hold.md` を追加し、`-` の 1-digit unsigned bucket2 `4` 行も再読した。2 same-op examples ずつあるため本命候補として見たが、row-local subtraction / digit-difference / digit-sum 系 probe でも exact match は 0 件で、全件 manual 維持とした。
- `reports/35_symbol_minus2_unsigned_hold.md` を追加し、`-` の 2-digit unsigned bucket1 `4` 行も再読した。各 row が same-op example を 1 本しか持たず、その唯一の例も query で subtraction family から外れるため、single-example subtraction trap と判断して manual 維持とした。
- `reports/36_symbol_star3_hold.md` を追加し、`*` の 3-digit bucket1 `4` 行も再読した。各 row が `*` example を 1 本しか持たず、simple product-like probe でも exact match は 0 件で、low-shot dead end と判断して manual 維持とした。
- `reports/37_binary_third_cluster_hold.md` を追加し、binary round2 の第3 cluster（`17` 行, `9 examples / 1 no-candidate / 0 multi-candidate`）も再読した。shift-like / inversion-like partial structure は見えるが、current solver family のどれも unique ではなく、safe exclusion も無いので manual 維持とした。
- `reports/38_binary_tail_clusters_hold.md` を追加し、binary round2 の残り小 cluster も representative rows を再読した。`bit_multi_candidate_positions >= 1` や `bit_no_candidate_positions = 0` でも競合候補が残るタイプが中心で、top3 よりさらに曖昧な tail と判断して manual 維持とした。
- `reports/39_symbol_star4_bucket3_hold.md` を追加し、`*` の 4-digit bucket3 `4` 行も再読した。3 same-op examples ずつある最後の有望 `*` residual だったが、simple product-like probe は 0 件で、これも manual 維持とした。
- 次ステップは、`symbol_numeric_same_op` core `294` 行のうち残る singleton / doubleton 級の operator-specific tail をどう束ねるか見直し、それでも前進しない場合は binary で **より広い boolean/circuit family か non-local byte transform family** を仮説化すること。glyph 46 行は、新しい family 仮説が出るまで hold。
