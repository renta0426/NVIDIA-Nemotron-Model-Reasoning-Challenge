# Phase0 バイナリ評価メトリクスバグ 再調査レポート

## 1. 目的

本レポートは、Proof-First Solver Factory Routing 実験で生成された Phase0 オフライン評価アーティファクトの再調査を記録したものです。

再調査の直接的なきっかけは、Phase0 の行レベルアーティファクトに `gold_answer != prediction` であるにもかかわらず `is_correct=True` が記録されている行が複数存在することの発見です。

この挙動は、意図されたバイナリ完全一致評価の契約と相容れず、バイナリ文字列が10進数として解析され相対許容差で比較されるという既知の Kaggle メトリクスバグによる汚染を強く示唆しています。

本レポートでは、以下の4点を省略なく記述します。

1. 本問題に関連する README 準拠の評価契約の再提示
2. バイナリ完全一致比較のもとでの正しい Phase0 スコアの再計算
3. バイナリバイアス特化プロブにおける同一汚染の有無の確認
4. 汚染された Phase0 アーティファクトを引き起こした具体的なコードパスの特定

## 2. README 準拠の評価契約

コンペティションの README は、`Accuracy`、boxed-first 抽出、`temperature=0.0`、数値回答に対する数値許容差を中心に公式評価を定義しています。

しかしバイナリ問題については、本リポジトリおよび Phase0 ノートブックにおける意図した処理はより厳格です。

1. バイナリ回答は8ビット文字列である
2. 先頭ゼロは意味を持つ
3. バイナリは数値許容差ではなく完全な文字列一致で評価されるべきである

この方針は Phase0 ノートブックのコードおよびマニフェスト設定の `binary_answers_are_string_exact = True` にも明示されています。

関連参照:

- `README.md`
- `baseline/cot/phase0_offline_eval/infer_rule_based_adapter_phase0_offline_eval.ipynb`
- `baseline/cot/phase0_offline_eval/infer_rule_based_adapter_phase0_binary_bias_specialized_eval.ipynb`

## 3. 調査対象アーティファクト

### 3.1 メイン Phase0 オフライン評価

- `cuda-train-data-analysis-v1/proof_first_solver_factory_routing/result/phase0_offline_eval/artifacts/phase0_eval_row_level.csv`
- `cuda-train-data-analysis-v1/proof_first_solver_factory_routing/result/phase0_offline_eval/artifacts/phase0_eval_summary.json`
- `cuda-train-data-analysis-v1/proof_first_solver_factory_routing/result/phase0_offline_eval/reports/phase0_eval_summary.md`

### 3.2 バイナリバイアス特化評価

- `cuda-train-data-analysis-v1/proof_first_solver_factory_routing/result/phase0_offline_eval_binary_bias_specialized/artifacts/binary_bias_specialized_eval_row_level.csv`
- `cuda-train-data-analysis-v1/proof_first_solver_factory_routing/result/phase0_offline_eval_binary_bias_specialized/artifacts/binary_bias_specialized_eval_summary.json`
- `cuda-train-data-analysis-v1/proof_first_solver_factory_routing/result/phase0_offline_eval_binary_bias_specialized/reports/binary_bias_specialized_eval_summary.md`

### 3.3 調査した評価実装

- `baseline/cot/phase0_offline_eval/build_phase0_offline_eval.py`
- `baseline/cot/phase0_offline_eval/infer_rule_based_adapter_phase0_offline_eval.ipynb`
- `baseline/cot/phase0_offline_eval/infer_rule_based_adapter_phase0_binary_bias_specialized_eval.ipynb`
- `nvidia-nemotron-metric.ipynb`
- `discussion/Competition Metric Bug: verify method fails for Binary String Problem (?).md`

## 4. 主な発見事項

メイン Phase0 アーティファクトは、バイナリメトリクスバグによって汚染されています。

バイナリバイアス特化アーティファクトは、同バグによる汚染を受けていません。

より正確には:

1. メイン Phase0 オフライン評価には、`gold_answer != prediction` であるにもかかわらず `is_correct=True` となっているバイナリ行が複数存在する
2. これらの行は、バイナリ回答が誤って `float()` に通され `math.isclose(..., rel_tol=1e-2, abs_tol=1e-5)` で比較された場合にのみ偽陽性となる
3. 特化ノートブックはすでにスコアリングをバイナリ厳格文字列比較にオーバーライドしており、サマリーは内部整合性を保っている
4. 汚染された Phase0 アーティファクトは、後のノートブックスコアリングロジックではなく `baseline/cot/phase0_offline_eval/build_phase0_offline_eval.py` の挙動と一致している

## 5. メイン Phase0 スコアの修正値

### 5.1 公式記録済み Phase0 スコア

保存された Phase0 サマリーは現在以下を報告しています。

- overall: `251 / 320 = 0.7844`
- binary: `29 / 60 = 0.4833`
- symbol: `24 / 60 = 0.4000`
- general stable set: `198 / 200 = 0.9900`

### 5.2 バイナリ完全一致比較による修正済み Phase0 スコア

8ビット文字列の厳格一致でバイナリ正解を再計算すると以下となります。

- overall: `241 / 320 = 0.7531`
- binary: `19 / 60 = 0.3167`
- symbol: `24 / 60 = 0.4000`
- general stable set: `198 / 200 = 0.9900`

汚染によってメイン Phase0 の overall スコアが `10` 行分、binary スコアが `10` 行分、過大計上されていたことになります。

### 5.3 差分サマリー

| メトリクス | 記録値 | 修正値 | 差分 |
| --- | ---: | ---: | ---: |
| overall 正解数 | 251 | 241 | -10 |
| overall 精度 | 0.7844 | 0.7531 | -0.0313 |
| binary 正解数 | 29 | 19 | -10 |
| binary 精度 | 0.4833 | 0.3167 | -0.1666 |
| symbol 正解数 | 24 | 24 | 0 |
| symbol 精度 | 0.4000 | 0.4000 | 0.0000 |
| general stable 正解数 | 198 | 198 | 0 |
| general stable 精度 | 0.9900 | 0.9900 | 0.0000 |

## 6. メイン Phase0 における偽陽性の確定一覧

以下の行が、汚染されたバイナリメトリクスのもとでの偽陽性です。

| benchmark_index | id | gold_answer | prediction | selection_tier | template_subtype | teacher_solver_candidate |
| ---: | --- | --- | --- | --- | --- | --- |
| 6 | `00066667` | `10010111` | `10001101` | `verified_trace_ready` | `bit_other` | `binary_affine_xor` |
| 15 | `bdb93228` | `11111101` | `11101111` | `verified_trace_ready` | `bit_other` | `binary_affine_xor` |
| 16 | `3564baf1` | `10101101` | `10101111` | `verified_trace_ready` | `bit_other` | `binary_affine_xor` |
| 31 | `021ed764` | `11111101` | `11111110` | `answer_only_keep` | `bit_structured_byte_formula` | `` |
| 32 | `02324ba1` | `11101011` | `11111110` | `answer_only_keep` | `bit_structured_byte_formula` | `` |
| 33 | `88fff090` | `01101000` | `01100001` | `answer_only_keep` | `bit_structured_byte_formula` | `` |
| 47 | `08b2b48d` | `10101011` | `10111111` | `manual_audit_priority` | `bit_other` | `` |
| 50 | `0a6d48aa` | `11100011` | `11111111` | `manual_audit_priority` | `bit_other` | `` |
| 59 | `12fd5b6c` | `11001111` | `11000010` | `manual_audit_priority` | `bit_other` | `` |
| 60 | `143627c4` | `11001001` | `11111111` | `manual_audit_priority` | `bit_other` | `` |

これらの行が `+10` 汚染の直接的な発生源です。

## 7. 修正済みメイン Phase0 バイナリ内訳

### 7.1 selection_tier 別

| selection_tier | 記録 正解/行数 | 記録 精度 | 修正 正解/行数 | 修正 精度 |
| --- | ---: | ---: | ---: | ---: |
| `verified_trace_ready` | 13 / 20 | 0.6500 | 10 / 20 | 0.5000 |
| `answer_only_keep` | 10 / 20 | 0.5000 | 7 / 20 | 0.3500 |
| `manual_audit_priority` | 6 / 20 | 0.3000 | 2 / 20 | 0.1000 |

### 7.2 template_subtype 別

| template_subtype | 記録 正解/行数 | 記録 精度 | 修正 正解/行数 | 修正 精度 |
| --- | ---: | ---: | ---: | ---: |
| `bit_other` | 23 / 46 | 0.5000 | 16 / 46 | 0.3478 |
| `bit_structured_byte_formula` | 6 / 14 | 0.4286 | 3 / 14 | 0.2143 |

### 7.3 teacher_solver_candidate 別

| teacher_solver_candidate | 記録 正解/行数 | 記録 精度 | 修正 正解/行数 | 修正 精度 |
| --- | ---: | ---: | ---: | ---: |
| `binary_affine_xor` | 13 / 20 | 0.6500 | 10 / 20 | 0.5000 |
| `` | 16 / 40 | 0.4000 | 9 / 40 | 0.2250 |

### 7.4 バイナリフォーマットメトリクス

バグはフォーマット挙動を変えません。正解ラベリングのみを変えます。

| バイナリメトリクス | 記録値 | 修正値 |
| --- | ---: | ---: |
| boxed_extraction_success_rate | 1.0000 | 1.0000 |
| regex_exact_rate | 1.0000 | 1.0000 |
| leading_zero_retention_rate | 0.8667 | 0.8667 |
| format_failure_rate | 0.0000 | 0.0000 |
| format_ok_content_wrong_rate | 0.5167 | 0.6833 |

これが重要な実践的含意です。バイナリブランチは見かけ上よりも実態は悪く、実際の失敗モードはさらに強く `format_ok_content_wrong` に集中しています。

## 8. バイナリバイアス特化評価の再調査

バイナリバイアス特化プロブには同じ汚染は見られません。

### 8.1 記録済み特化スコア

- overall: `234 / 563 = 0.4156`

### 8.2 修正済み特化スコア

- overall: `234 / 563 = 0.4156`

スコアの変化はありません。

### 8.3 特化スコアが汚染されていない理由

1. 特化サマリーは `accuracy = 0.4156` を報告している
2. 同サマリーは `gold_anywhere_rate = 0.4156` も報告している
3. 同サマリーは `last_bit8_exact_rate = 0.4156` も報告している
4. そのノートブックはバイナリ厳格文字列比較のために `verify_answer` を明示的にオーバーライドしている

この内部整合性こそが、汚染されたメイン Phase0 アーティファクトに欠けているものです。

### 8.4 特化 tier 別スコア

| selection_tier | 正解/行数 | 精度 |
| --- | ---: | ---: |
| `verified_trace_ready` | 175 / 373 | 0.4692 |
| `answer_only_keep` | 53 / 150 | 0.3533 |
| `manual_audit_priority` | 6 / 40 | 0.1500 |

### 8.5 特化フォーカスバケット別スコア

| v1_focus_bucket | 正解/行数 | 精度 |
| --- | ---: | ---: |
| `boolean_family` | 36 / 60 | 0.6000 |
| `dominant_structured_abstract` | 32 / 90 | 0.3556 |
| `dominant_structured_safe` | 48 / 120 | 0.4000 |
| `no_solver_answer_only` | 26 / 70 | 0.3714 |
| `no_solver_manual` | 6 / 40 | 0.1500 |
| `rare_byte_transform` | 10 / 11 | 0.9091 |
| `rare_perm_independent` | 5 / 7 | 0.7143 |
| `supported_affine_xor` | 25 / 60 | 0.4167 |
| `supported_bijection` | 42 / 50 | 0.8400 |
| `supported_not_structured` | 4 / 55 | 0.0727 |

### 8.6 特化露出バンド別スコア

| v1_exposure_band | 正解/行数 | 精度 |
| --- | ---: | ---: |
| `dominant` | 80 / 210 | 0.3810 |
| `rare` | 15 / 18 | 0.8333 |
| `supported` | 107 / 225 | 0.4756 |
| `underrepresented` | 32 / 110 | 0.2909 |

### 8.7 特化評価の解釈

バイナリバイアス特化プロブは、汚染された測定ではなく、モデルの弱点の正確な測定です。

したがって、その主要なメッセージは変わりません。

1. `supported_not_structured` は `0.0727` という壊滅的な値のまま
2. `dominant_structured_abstract` は `0.3556` と依然弱い
3. `manual_audit_priority` は `0.1500` と依然弱い
4. `supported_bijection` と `rare_byte_transform` はボトルネックではない

## 9. 根本原因分析

### 9.1 コンペティションメトリクスのバグ

`nvidia-nemotron-metric.ipynb` の公式メトリクス実装は、保存された回答と予測回答の両方を `float()` で変換したうえで `math.isclose(..., rel_tol=1e-2, abs_tol=1e-5)` で比較します。

この挙動は真の数値回答には問題ありませんが、バイナリ8ビット文字列には誤りです。

具体的な発生メカニズムの例:

- gold: `10010111`
- prediction: `10001101`

いずれも10進数整数として解析されます。

- `float("10010111") = 10010111.0`
- `float("10001101") = 10001101.0`

絶対差は `9010` です。

`10010111` 周辺の相対許容差ウィンドウは約 `100101.11` です。

`9010 < 100101.11` であるため、誤った予測が正解とカウントされます。

これはすでに以下で文書化されている公知の問題と完全に一致しています。

- `discussion/Competition Metric Bug: verify method fails for Binary String Problem (?).md`

### 9.2 リポジトリ内の汚染パス

汚染された Phase0 アーティファクトは、後のノートブックスコアリングコードが原因ではありません。

古い共有ビルドスクリプトが原因です。

- `baseline/cot/phase0_offline_eval/build_phase0_offline_eval.py`

この `verify_answer` 実装は以下の順で処理します。

1. `gold = str(gold).strip()`
2. `predicted = str(predicted).strip()`
3. まず `float(gold)` および `float(predicted)` を試みる
4. `math.isclose(...)` を返す
5. float 変換が失敗した場合にのみ文字列一致にフォールバック

つまりバイナリ文字列はバイナリ文字列として扱われることがなく、常に10進数として扱われます。

### 9.3 ノートブックとの乖離

後の Phase0 ノートブックはこの挙動を修正しています。

`baseline/cot/phase0_offline_eval/infer_rule_based_adapter_phase0_offline_eval.ipynb` は以下の順で処理します。

1. `gold` が `[01]+` に一致する場合はまず完全文字列比較
2. バイナリ以外の数値回答に対してのみ数値許容差
3. それ以外は文字列一致

特化ノートブックはさらに進んで、バイナリ厳格文字列比較のために `verify_answer` を再度明示的にオーバーライドします。

その結果、リポジトリには互換性のない2つのスコアリングパスが存在することになりました。

1. `build_phase0_offline_eval.py` の汚染された float-first パス
2. ノートブックの修正済みバイナリ厳格パス

メイン Phase0 アーティファクトは1番目のパスの挙動をします。

特化アーティファクトは2番目のパスの挙動をします。

## 10. メイン Phase0 アーティファクトとノートブックの主張が矛盾する理由

ノートブックのソースとマニフェストは `binary_answers_are_string_exact = True` と明示しています。

しかし保存されたメイン Phase0 の行レベルアーティファクトは、完全不一致が正解としてマークされているため、その主張と矛盾しています。

この矛盾が生じるためには、以下のいずれかが発生している必要があります。

1. メイン Phase0 アーティファクトがノートブック以前またはビルドスクリプトのスコアリングパスで生成された
2. アーティファクトが float-first verifier をインポートまたはミラーしたままのヘルパーコードで再生成された
3. アーティファクトがすでに生成された後でノートブックのテキストが更新されたが、アーティファクト自体は再スコアされなかった

挙動の正確な一致から、最も妥当な原因は、保存されたメイン Phase0 アーティファクトが `baseline/cot/phase0_offline_eval/build_phase0_offline_eval.py` または同等の float-first ロジックで生成されたというものです。

## 11. 本実験における実践的影響

### 11.1 引き続き有効な結論

以下の結論は引き続き有効です。

1. general ファミリーは安定していた
2. symbol は弱いままだが、このバイナリ固有バグの影響は受けていない
3. バイナリバイアス特化プロブは依然として本当の困難バケットを特定している
4. バイナリフォーマット品質は高かった

### 11.2 修正が必要な値

以下の値は、この Phase0 実行のメインバイナリベースラインとして使用してはなりません。

1. binary `0.4833`
2. overall `0.7844`

これらを以下に置き換える必要があります。

1. binary 修正値 `0.3167`
2. overall 修正値 `0.7531`

### 11.3 計画判断への影響

計画は以下を優先しています。

1. boxed の安定性
2. フォーマット正確性
3. `format_ok_content_wrong` の削減

修正後、バイナリブランチは当初のサマリーが示唆していたよりも3番目の基準で実質的に悪い状態に見えます。

したがって修正後の解釈は以下のとおりです。

1. boxed の挙動は本当に強かった
2. 内容の正確性は報告よりも実質的に弱かった
3. バイナリ困難ファミリーの改善は、汚染された `0.4833` ではなく修正済み `0.3167` ベースラインと比較して評価しなければならない

## 12. 最終結論

メイン Phase0 オフライン評価アーティファクトは、既知のバイナリメトリクスバグによって汚染されていました。

バイナリバイアス特化プロブは汚染されていませんでした。

具体的な根本原因は、アーティファクトを生成した Phase0 ビルドパスが `baseline/cot/phase0_offline_eval/build_phase0_offline_eval.py` の float-first verifier を使用していたのに対し、後のノートブックはすでにバイナリ厳格文字列比較に移行していたことです。

したがって本実験の正しいスコア記録は以下のとおりです。

- main Phase0 overall: `241 / 320 = 0.7531`
- main Phase0 binary: `19 / 60 = 0.3167`
- main Phase0 symbol: `24 / 60 = 0.4000`
- specialized binary probe: `234 / 563 = 0.4156`

今後、この実験を使用したいかなる比較・アブレーション判断・ルート認識デルタ分析においても、メイン Phase0 バイナリスコアは `0.4833` ではなく `0.3167` として扱わなければなりません。