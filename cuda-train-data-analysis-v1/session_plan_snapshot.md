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
  - `verified_trace_ready`: 6,081
  - `manual_audit_priority`: 2,253
  - `answer_only_keep`: 1,140
  - `exclude_suspect`: 26
- family ごとの厳密 verified:
  - roman: 1,576 / 1,576
  - gravity: 1,597 / 1,597
  - unit: 1,594 / 1,594
  - text: 605 / 1,576
  - binary: 599 / 1,602
  - symbol: 110 / 1,555
- `binary` は affine XOR と simple byte transform（shift / rotate / mask）を足したことで 381 verified まで伸び、baseline の 306 solved を上回った。
- `binary` の residual low-gap scan では、一意 affine・他候補なし・`bit_no_candidate_positions<=1`・gold 不一致の 11 行を `exclude_suspect` へ降格した。その後、single-missing-bit / shared-varset の conservative hybrid consensus を追加し、`20` 行を `answer_only_keep` に昇格した。これで `binary` は `381 verified / 20 answer_only / 1186 manual / 15 exclude` になった。
- `symbol` は `numeric_2x2` の operator-aware formula search に加え、pass1 manual curation で exact prompt-backed 規則 `concat_xy / concat_yx / abs_diff_2d / abs_diff_2d_op_suffix / comp99_abs_diff_2d` を統合した。直近の更新では `comp99_abs_diff_2d` を operator-prefixed zero-pad まで拡張し、`b655eee9` を verified、`13892a7c` / `3a8a4ebc` / `6b769a9e` / `ef6bc241` を answer_only に昇格し、`9a9f6025` を exclude_suspect に移した。これで `symbol` は `110 verified / 114 answer_only / 1320 manual / 11 exclude` になった。
- `glyph_len5` pass1 の 46 行は dedicated recheck を行ったが、安全昇格 0 / 安全除外 0 だった。`glyph_query_consistent_v1.csv` の 5 行も coarse multiset+order model が非一意のため、全件 manual 維持とした。
- `glyph_len5` のうち `glyph_multiset_possible` は 70 行、そのうち example 出力に一貫した順序制約まで通る `glyph_order_acyclic` は 46 行で、`manual_pass1_priority_pack_v1.csv` の glyph 部分はこの 46 行に絞り込んだ。
- `text` の未verified 971 行は全件、gold answer により不足 1〜6 文字の monoalphabetic mapping を矛盾なく補完できることを確認し、`answer_only_keep` に昇格した。これで `text` は `verified=605 / answer_only=971 / manual=0` になった。
- `manual_pass1_priority_pack_v1.csv` は `525` 行まで圧縮され、内訳は `symbol_numeric_same_op=361`, `binary_low_gap=118`, `symbol_glyph_multiset=46`。
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
- `reports/40_symbol_tiny_tail_hold.md` を追加し、残る singleton / doubleton の symbol operator tail も representative rows を再読した。ここは broader family なしでは safe promotion の入口が無い long tail と判断し、manual 維持とした。
- `reports/41_symbol_broader_template_scan.md` を追加し、digit-only symbol manual rows 全体へ broader template library を当てた。`x+y`, `|x-y|`, `x*y`, pairwise digit concat 群, reversed / zero-pad variants を試しても repeated exact hit は 0 件だった。
- `reports/42_binary_hybrid_consensus_recovery.md` を追加し、single-missing-bit / shared-varset の conservative hybrid consensus を binary へ追加した。`45` 行が hybrid-ready で、そのうち既存 verified とは別に `20` 行を新規 `answer_only_keep` として安全側で回収できた。
- `reports/43_binary_structured_byte_formula_recovery.md` を追加し、structured byte formula family を binary へ追加した。semantic-dedup 後の `311` formula / `71` safe formula を使い、manual binary `189` 行を新規 `verified_trace_ready` として回収した。
- `reports/44_binary_structured_byte_tail_map.md` を追加し、structured byte residual `55` 行を category 化した。`46` 行が singleton support=1、`2` 行が same-pred multi-formula、`1` 行が ambiguous-pred、`4` 行が structured mismatch exclude で、さらに singleton のうち `37` 行は zero-error abstract family 候補だがまだ rule 化していない。
- `reports/45_binary_structured_byte_abstract_recovery.md` を追加し、abstract structured-byte family を binary へ追加した。safe abstract family `10` 個を使い、singleton structured rows `29` 行を追加 `verified_trace_ready` として回収した。
- `reports/46_binary_structured_byte_threshold_sweep.md` を追加し、abstract structured-byte threshold を緩めた場合の gain を測った。`support>=12 / distinct>=6` から `support>=5 / distinct>=4` に緩めても追加 gain は `5` 行だけで、`and(ror,shr)` と `or(rol,shl)` の薄い family に限られたため、現時点では採用しない判断にした。
- `reports/47_binary_structured_byte_multi_consensus_recovery.md` を追加し、same-pred multi-formula 行のうち safe abstract family に anchor を持つ `8b4c71ba` / `cc5011ac` を `answer_only_keep` として回収した。これで structured byte residual は `20 manual + 4 exclude` になり、残る multi-formula 行は `5a6dd286` のみ。
- これで `binary` は `599 verified / 22 answer_only / 966 manual / 15 exclude` になった。
- `reports/48_symbol_operator_embedded_scan.md` を追加し、symbol の operator-embedded output へ cross-operator prefix/suffix scan を当てた。`op_prefix_abs_diff_2d` は `81c7ba7a` / `2dd48cac` / `45dbc1cc` / `4cb5e927` を説明する near-miss だったが、`8c1529e1` の hard conflict があるため safe promotion / exclude には使わない判断にした。
- `reports/49_symbol_operator_specific_consensus_recovery.md` を追加し、operator ごとに clean support を持つ `(formula, format)` spec を足場に low-shot/ambiguous `numeric_2x2` manual 16 行を `answer_only_keep` として回収した。これで `symbol` は `110 verified / 130 answer_only / 1304 manual / 11 exclude` になった。
- `reports/50_symbol_minus_prefix_subfamily_recovery.md` を追加し、report 48 の `op_prefix_abs_diff_2d` near-miss を `-` operator の zero-error subfamily に切り分けた。`22-27 -> -05`, `15-75 -> -6`, `09-19 -> -1` の 3 行を `answer_only_keep` として追加回収し、current symbol は `110 verified / 133 answer_only / 1301 manual / 11 exclude`、overall は `6081 verified / 1126 answer_only / 2267 manual / 26 exclude` になった。
- `reports/51_binary_structured_byte_low_support_answer_only.md` を追加し、structured-byte singleton tail のうち zero-error だが thin な abstract family を `answer_only_keep` として採用した。binary manual 11 行を追加回収し、current binary は `599 verified / 33 answer_only / 955 manual / 15 exclude`、overall は `6081 verified / 1137 answer_only / 2256 manual / 26 exclude` になった。structured-byte residual は `9 manual + 4 exclude` まで縮小した。
- `reports/52_symbol_star_prefix_if_negative_recovery.md` を追加し、generalized subfamily search で `* :: x_minus_y :: prefix_if_negative` のうち `same_operator_example_count == 1` だけが `3 support / 0 error` の zero-error subgroup になることを確認した。`50*15 -> 35`, `45*32 -> 13`, `47*73 -> *26` の 3 行を `answer_only_keep` として追加回収し、current symbol は `110 verified / 136 answer_only / 1298 manual / 11 exclude`、overall は `6081 verified / 1140 answer_only / 2253 manual / 26 exclude` になった。manual pass1 pack は `503` 行（`339 symbol_numeric_same_op / 118 binary_low_gap / 46 symbol_glyph_multiset`）、current `symbol` round2 core は `283` 行。
- `reports/53_symbol_minus_direct_plain_recovery.md` を追加し、prompt の same-op `-` examples が exact direct formatter（`signed_plain` または `abs_plain`）に一致する row だけを再集計した。query の digit-order split を掛けると `minus_signed_plain_both_lt=4/0err`, `minus_signed_plain_both_gt=3/0err`, `minus_abs_plain_both_gt=3/0err` の 3 subfamily が立ち、`52-99 -> -47`, `96-74 -> 22`, `37-06 -> 31` の 3 行を `answer_only_keep` として追加回収できた。current symbol は `110 verified / 139 answer_only / 1295 manual / 11 exclude`、overall は `6081 verified / 1143 answer_only / 2250 manual / 26 exclude`、manual pass1 pack は `500` 行（`336 symbol_numeric_same_op / 118 binary_low_gap / 46 symbol_glyph_multiset`）、current `symbol` round2 core は `282` 行。
- `reports/54_binary_structured_byte_support3_answer_only.md` を追加し、structured-byte residual のうち `support=3 / distinct=3 / error=0` を満たす narrow abstract family を再評価した。current train では `and(rol,shl)` だけが該当し、`01d894fb`, `18c54744` の 2 行を `answer_only_keep` として追加回収できた。current binary は `599 verified / 35 answer_only / 953 manual / 15 exclude`、overall は `6081 verified / 1145 answer_only / 2248 manual / 26 exclude`、structured-byte residual は `7 manual + 4 exclude` に縮小した。
- `reports/55_symbol_thin_support2_recovery.md` を追加し、post-report-54 の symbol subgroup search で最後に残っていた thin support-2 slices を再評価した。`!` の `abs_diff_2d` exact example + both-lt query branch と、`"` の `x_minus_y :: prefix_if_negative` exact example + large-positive query branch がどちらも `2 support / 0 error` だったため、`7c5c7b73`, `b7b1d1a8` の 2 行を `answer_only_keep` として追加回収した。current symbol は `110 verified / 141 answer_only / 1293 manual / 11 exclude`、overall は `6081 verified / 1147 answer_only / 2246 manual / 26 exclude`、manual pass1 pack は `498` 行（`334 symbol_numeric_same_op / 118 binary_low_gap / 46 symbol_glyph_multiset`）。同時に subgroup search を再実行し、残る機械的 near-miss は `45dbc1cc` のみだが、`sum>=100` 依存で不自然なため未採用と判断した。
- `reports/56_binary_structured_byte_manual_exact_curation.md` を追加し、structured-byte residual の direct prompt reread を実施した。prompt 自体が exact structured formula を一意に示している 5 行（`1bf84ce3`, `2aa6ce6a`, `26df9536`, `d5a28743`, `9bfb1cc6`）を `verified_trace_ready` に昇格し、`8631d7b6` は `xor(ror1,shr1)` の prompt-exact prediction `10000000` と gold `00000000` が衝突するため `exclude_suspect` に移した。これで current binary は `604 verified / 35 answer_only / 947 manual / 16 exclude`、overall は `6086 verified / 1147 answer_only / 2240 manual / 27 exclude`、manual pass1 pack は `497` 行（`334 symbol_numeric_same_op / 117 binary_low_gap / 46 symbol_glyph_multiset`）になり、structured-byte residual は `5a6dd286` の `1 manual + 5 exclude` まで縮小した。
- `reports/57_symbol_colon_manual_exact_answer_only.md` を追加し、`:` residual を direct prompt reread した。`094bf548` は 3 same-op examples が plain abs-diff answer を支持し、`904e3a54` は 2 same-op examples が negative-only prefix branch を支持するため、どちらも `answer_only_keep` に昇格した。これで current symbol は `110 verified / 143 answer_only / 1291 manual / 11 exclude`、overall は `6086 verified / 1149 answer_only / 2238 manual / 27 exclude`、manual pass1 pack は `495` 行（`332 symbol_numeric_same_op / 117 binary_low_gap / 46 symbol_glyph_multiset`）になった。
- `reports/58_symbol_prefix_always_abs_tail.md` を追加し、`"` / `[` の multi-example prefix-always-abs tail を direct prompt reread した。`31eb8247`, `4c57a53f` はどちらも same-op examples `2` 本が absolute-difference + operator-always-prefix を示しており、manual から `answer_only_keep` に昇格した。これで current symbol は `110 verified / 145 answer_only / 1289 manual / 11 exclude`、overall は `6086 verified / 1151 answer_only / 2236 manual / 27 exclude`、manual pass1 pack は `493` 行（`330 symbol_numeric_same_op / 117 binary_low_gap / 46 symbol_glyph_multiset`）、current symbol round2 core は `280` 行になった。同時に manual `numeric_2x2` のうち「same-op examples が 2 本以上あり、既存 formula library が gold を支持する行」は枯渇したことを確認した。
- `reports/59_symbol_single_example_tail_hold.md` を追加し、single-example gold-hit tail `8` 行（`45dbc1cc`, `4cb5e927`, `2afebbc3`, `81c7ba7a`, `d1bd7478`, `64fe405e`, `74fff108`, `55f19327`）も全件再読した。結果は全件 hold で、safe promotion / safe exclusion ともに `0`。これにより、current symbol tail の prompt-backed arithmetic cleanup は multi-example 側・single-example 側ともに枯渇したと判断した。
- 次ステップは、symbol では残る no-example / custom-op / operator-embedded の genuinely manual tail を round2 cluster-first で読むこと。binary の structured-byte 側は broad family 問題としてはほぼ閉じており、残る `5a6dd286` は multi-pred ambiguity 専用の別問題として扱う。glyph 46 行は、新しい family 仮説が出るまで hold。
