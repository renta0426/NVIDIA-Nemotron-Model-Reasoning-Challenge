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
  - `verified_trace_ready`: 5,862
  - `manual_audit_priority`: 2,545
  - `answer_only_keep`: 1,075
  - `exclude_suspect`: 18
- family ごとの厳密 verified:
  - roman: 1,576 / 1,576
  - gravity: 1,597 / 1,597
  - unit: 1,594 / 1,594
  - text: 605 / 1,576
  - binary: 381 / 1,602
  - symbol: 109 / 1,555
- `binary` は affine XOR と simple byte transform（shift / rotate / mask）を足したことで 381 verified まで伸び、baseline の 306 solved を上回った。
- `symbol` は `numeric_2x2` の operator-aware formula search に加え、pass1 manual curation で exact string-template 規則 `concat_xy / concat_yx / abs_diff_2d / abs_diff_2d_op_suffix` を統合した。直近の residual scan では `824d4bcb` を verified、`9cb03277` を answer_only に昇格し、`4c6cf9d9` を exclude_suspect に降格した。これで `symbol` は `109 verified / 104 answer_only / 1332 manual / 10 exclude` になった。
- `glyph_len5` のうち `glyph_multiset_possible` は 70 行、そのうち example 出力に一貫した順序制約まで通る `glyph_order_acyclic` は 46 行で、`manual_pass1_priority_pack_v1.csv` の glyph 部分はこの 46 行に絞り込んだ。
- `text` の未verified 971 行は全件、gold answer により不足 1〜6 文字の monoalphabetic mapping を矛盾なく補完できることを確認し、`answer_only_keep` に昇格した。これで `text` は `verified=605 / answer_only=971 / manual=0` になった。
- `manual_pass1_priority_pack_v1.csv` は `569` 行まで圧縮され、内訳は `symbol_numeric_same_op=373`, `binary_low_gap=150`, `symbol_glyph_multiset=46`。
- `reports/13_manual_curation_pass1.md` と `reports/14_symbol_residual_template_scan.md` に、今回の安全昇格・suspect 化・非昇格判断の根拠を追加した。
- 次ステップは `glyph_len5` 46 行の mapping/order 一意化仮説と `binary` 150 行の low-gap 群をさらに掘りつつ、残る `symbol_numeric_same_op` 373 行から次の安全 subset を抽出すること。
