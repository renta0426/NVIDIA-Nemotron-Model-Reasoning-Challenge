# Rule-Based 600 Adapter Inference Sample Analysis

## Summary

- 対象ファイル: `baseline/cot/rule_based_adapter_readme_inference_samples_rule_base-600.csv`
- 対象件数: 30 サンプル
- 一致件数: 24 / 30
- 不一致件数: 6 / 30
- 主因: binary family の最終回答フォーマット不安定による失点

このレポートは、`baseline/train_rule_based_cot_baseline.ipynb` によって学習した rule-based 600 データ版アダプタについて、README 準拠の推論方法で得たサンプル結果を整理したものである。評価の解釈は `README.md` の Evaluation セクションに従う。

README では、提出物は NVIDIA Nemotron-3-Nano-30B ベースモデルに LoRA adapter をロードし、vLLM 上で推論される。各サンプルでは最終回答を `\boxed{}` に入れるよう促され、メトリクスはまず boxed を優先して抽出し、失敗時は他のヒューリスティックや最後の数値にフォールバックする。この仕様は、特に binary family の評価に強く影響する。

## Evaluation Context From README

`README.md` の Evaluation セクションに基づく今回の分析上の重要点は以下の通り。

1. 推論は vLLM で実行される。
2. LoRA adapter は Nemotron-3-Nano-30B にロードされる。
3. モデルは最終回答を `\boxed{}` に入れることを求められる。
4. 抽出は boxed を優先する。
5. boxed が適切に出ていない場合、他のヒューリスティックや最後の数値へフォールバックする。
6. 数値問題では相対誤差許容があるが、文字列系は基本的に厳密一致が必要になる。

このため、structured な reasoning が途中で成立していても、最終回答の出し方が崩れると失点しやすい。今回の CSV はまさにその影響を示している。

## Data Reviewed

- 入力 CSV: `baseline/cot/rule_based_adapter_readme_inference_samples_rule_base-600.csv`
- サンプル family:
  - `binary`
  - `gravity`
  - `roman`
  - `symbol`
  - `text`
  - `unit`

CSV の主要カラムは以下。

- `label`: family 名
- `id`: 問題 ID
- `expected_answer`: 正解
- `extracted_answer`: README 互換抽出ロジックで得られた最終回答
- `rendered_prompt`: 実際にモデルへ与えたプロンプト
- `raw_output`: モデルの生出力

## Aggregate Results

Python の標準 `csv` モジュールで CSV を正確にパースし、family ごとの一致率を集計した。

| Family | Match | Total | Notes |
|---|---:|---:|---|
| binary | 5 | 10 | 最大の失点源 |
| gravity | 4 | 4 | 全件一致 |
| roman | 4 | 4 | 全件一致 |
| symbol | 4 | 4 | 全件一致 |
| text | 4 | 4 | 全件一致 |
| unit | 3 | 4 | 1 件のみ丸め差 |
| Total | 24 | 30 | 失点 6 件 |

失点 6 件の内訳は以下。

- binary: 5 件
- unit: 1 件

この分布から、現時点の rule-based 600 モデルは「全体的に弱い」のではなく、「binary が極端に弱い」あるいは「binary の最終回答整形が極端に不安定」とみなすのが妥当である。

## Detailed Mismatch List

### Binary mismatches

| ID | Expected | Extracted | Primary issue hypothesis |
|---|---|---|---|
| `0031df9c` | `00110100` | `1` | 抽出が短い数値断片へ崩壊 |
| `008b52fd` | `01100101` | `001` | 8-bit ではなく部分文字列を抽出 |
| `030479a6` | `01000110` | `-0` | 数値ヒューリスティックに誤フォールバック |
| `069dbaab` | `00010000` | `10` | 最終 binary 8 桁で閉じていない |
| `08615ada` | `11101111` | `10` | reasoning 末尾の断片抽出の可能性 |

### Unit mismatch

| ID | Expected | Extracted | Primary issue hypothesis |
|---|---|---|---|
| `006a46d3` | `19.00` | `18.99` | 丸め差。計算自体はほぼ正しい |

## Family-by-Family Analysis

## 1. Binary family

### Result

- 5 / 10 一致
- 全失点の大半を占める

### What is going wrong

binary では 2 種類の失敗が混在している。

1. 規則発見そのものに失敗しているケース
2. 規則発見や途中 reasoning はそれなりに成立していても、最終回答を 8-bit binary の boxed 形式で閉じられておらず、抽出で壊れるケース

今回の CSV では後者の比率が高い。

例えば mismatch 行では `extracted_answer` が `1`, `001`, `-0`, `10` といった短い断片に崩れている。これは正解の型が 8-bit 文字列であるにもかかわらず、評価器が boxed を拾えず、数値や断片へフォールバックしていることを示唆する。

### Why README matters here

README の評価仕様では、boxed が正しく出ていればその中身が優先的に採用される。一方で boxed が出ない、または boxed 内が不適切だと、最後の数値や他パターン抽出に落ちる。この仕様は decimal や text 系よりも binary に厳しい。

理由は単純で、binary では以下のような壊れ方が致命的だからである。

- `00110100` が `1` に縮退する
- `01000110` が `-0` に崩れる
- `11101111` が `10` に崩れる

数値系なら多少の丸め誤差を吸収できるが、binary 文字列ではこうした崩れは即失点になる。

### Positive signal in binary

binary が全面崩壊しているわけではない。以下のように正しく 8-bit で出せているサンプルもある。

- `04c44df4` -> `00000000`
- `06412918` -> `00010010`
- `06698d4e` -> `00110010`
- `0a195a74` -> `01010010`
- `0c7acd69` -> `11110101`

これは binary family に必要な変換能力がゼロではないことを示す。問題は「安定して 8-bit boxed answer で閉じる最終出力契約」が守れていない点にある。

### Interpretation

この family の現状は次のように整理できる。

- reasoning 能力は部分的にある
- しかし output contract が弱い
- Kaggle README 準拠評価ではその弱さがそのまま精度損失になる

したがって binary では「もっと賢くする」前に「最後の 1 行を壊さない」改善が必要である。

## 2. Gravity family

### Result

- 4 / 4 一致

### Interpretation

gravity は今回のサンプルでは完全一致で、数値計算系として十分安定している。reasoning から final answer への接続も大きく崩れていない。

これは rule-based 600 の学習が少なくとも一部の numeric family には悪影響を与えていないことを示す。

## 3. Roman family

### Result

- 4 / 4 一致

### Interpretation

Roman numeral family では、出力形式が string exact match 型であるにもかかわらず全件一致した。これは以下の点で重要である。

1. 文字列系の厳密一致が全くできないわけではない
2. binary だけが特殊に崩れている
3. answer extraction の問題が family 特性依存である可能性が高い

Roman で安定しているなら、binary でも boxed 形式を強制できれば改善余地が大きい。

## 4. Symbol family

### Result

- 4 / 4 一致

### Interpretation

symbol family は discrete transformation 系でありながら全件一致している。したがって「離散構造に弱いから binary が落ちる」という単純な説明は不十分である。

より正確には、binary は

- 出力長が固定 8 桁
- `0` と `1` のみで構成
- 数値ヒューリスティックに誤吸収されやすい

という評価上の脆さを持つ。

## 5. Text family

### Result

- 4 / 4 一致

### Interpretation

以前の baseline 0.7 近辺モデルでは text family に hallucination 気味の出力が見られたが、今回の追加 CSV では text family が 4 / 4 一致している。少なくとも今回の rule-based 600 学習は text を壊していない。

この点は前向きな材料である。つまり score 0.64 前後という全体値だけ見ると弱く見えるが、内部的には text, symbol, roman, gravity など複数 family で十分戦えている。

## 6. Unit family

### Result

- 3 / 4 一致
- 不一致 1 件のみ

### The mismatch is low severity

`006a46d3` では、`10.9 * 1.7425 = 18.99325` を `18.99` と丸めている。期待値は `19.00` だが、計算内容自体はほぼ正しい。

この失点は binary mismatch 群と性質が異なる。

- binary: 出力形式崩壊により厳密不一致
- unit: 計算はほぼ正しいが丸めの境界差

README の記述どおり数値問題には相対誤差許容があるため、本番メトリクスではこの種の差の影響は binary より軽い可能性が高い。

## Main Conclusion

今回の追加分析から最も重要な結論は以下の通り。

### 1. 現在の rule-based 600 モデルは全面的に弱いわけではない

binary 以外は以下の通り安定している。

- gravity: 4 / 4
- roman: 4 / 4
- symbol: 4 / 4
- text: 4 / 4
- unit: 3 / 4

### 2. 最大ボトルネックは binary family

失点 6 件のうち 5 件が binary であり、これが score を大きく押し下げている。

### 3. Binary の問題は reasoning failure だけではない

むしろ今回の CSV では、README 評価仕様に対する最終 answer formatting failure の割合が高い。

### 4. したがって次の改善は binary 専用の output contract 強化が最優先

binary で必要なのは、まず以下を安定化すること。

- 最終行で 8 桁 binary を出す
- 必ず `\boxed{}` で囲う
- 余計な補足を boxed の近くに置かない
- 最後の数値ヒューリスティックに吸われないようにする

## Recommended Next Actions

## Priority 1: Binary answer formatting hardening

推論 notebook またはプロンプト側で、binary 問題に対して以下をさらに強く指示する。

1. 最終回答は必ず 8 桁の binary string のみ
2. 最終回答は必ず `\boxed{xxxxxxxx}`
3. boxed の後ろに説明を続けない
4. `0` と `1` 以外を boxed に入れない

## Priority 2: Binary-specific audit logging

次回の定性評価 CSV には以下を残すとよい。

1. raw_output の末尾数行
2. boxed 抽出結果
3. fallback 抽出結果
4. extracted_answer が boxed 由来か fallback 由来か

これにより、binary の失点を

- 推論失敗
- boxed 失敗
- fallback 誤抽出

に機械的に分類できる。

## Priority 3: Binary-heavy training reinforcement

rule-based 600 の良い部分を維持したまま、binary family を重点補強する。

候補は以下。

1. binary のみで最終 answer formatting を厳しくした学習データを増やす
2. binary の CoT を短くし、最後の boxed 出力を常に固定書式にする
3. binary family の near-miss 例を hard negative 的に再学習へ入れる

## Implications For Score Interpretation

今回の score 0.64 前後をそのまま「モデル全体の reasoning が弱い」と読むのは危険である。

より妥当な読み方は以下。

- 非 binary family は概ね良い
- binary family だけが本番評価仕様と強く衝突している
- その衝突は推論力より final answer formatting の影響が大きい

つまり、改善余地はまだ大きい。特に binary で final answer の安定化に成功すれば、現在の qualitative strength を維持したままスコアを上げられる可能性が高い。

## Final Assessment

この追加 CSV の分析から、rule-based 600 アダプタは以下の状態にあると評価する。

- numeric 系と文字列系の多くは安定
- binary が主な失点源
- binary は完全な能力不足というより、README 準拠評価に対する answer formatting failure が支配的
- 次にやるべきことは、binary 専用の output contract 強化と監査ログ追加

結論として、このモデルの現状課題は「全体性能」ではなく「binary family の最終出力品質」である。