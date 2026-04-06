# `nemotron-sft-lora-with-cot-v2` binary bias specialized 深掘り分析

## 対象

- benchmark result:
  - `baseline/nemotron-sft-lora-with-cot-v2/result/phase0_offline_eval_binary_bias_specialized/`
- 主参照 artifact:
  - `reports/binary_bias_specialized_eval_summary.md`
  - `reports/binary_bias_specialized_manifest.md`
  - `artifacts/binary_bias_specialized_eval_row_level.csv`
  - `artifacts/binary_bias_specialized_eval_raw_outputs.csv`
  - `artifacts/binary_bias_teacher_style_summary.json`
  - `artifacts/binary_bias_bucket_accuracy.csv`
  - `artifacts/binary_bias_bucket_tier_accuracy.csv`
  - `artifacts/binary_bias_exposure_accuracy.csv`
- 比較対象:
  - `baseline/nemotron-sft-lora-with-cot-v2/result/reports/binary_hard_set_summary.md`
  - `cuda-train-data-analysis-v1/bit_synth_exact_trace_cot_v1/result/v1_binary/reports/binary_bias_specialized_eval_summary.md`
  - `baseline/cot/binary_synthetic_data_approaches_history.md`

## README 前提

`README.md` の Evaluation は **Accuracy** で、最終回答は `\boxed{}` 優先抽出、失敗時は heuristic / last-number fallback に落ちる。  
binary は exact string が必要なので、この benchmark では **rule induction** と **final boxed commit** の両方が問われる。(`README.md:31-46`)

## 結論

この specialized benchmark における `nemotron-sft-lora-with-cot-v2` baseline の binary 性能は **`190/563 = 0.3375`** で、通常の 60 問 binary watch (`29/60 = 0.4833`) よりかなり厳しい。  
ただし中身を見ると、「binary が全体に弱い」ではなく、**`bijection` / `byte_transform` / 一部 boolean は強い一方、structured formula 系が大きな穴**になっている。

最重要な観察は次の 4 点。

1. **boxing はかなり機能している**  
   `boxed_non_empty` が `452/563`、`last_number` は `109/563`。しかも `last_number` は **`0/109`** で、正答はほぼ boxed primary path に依存している。
2. **主ボトルネックは structured rule content**  
   `binary_structured_byte_formula = 18/87`, `abstract = 16/73`, `not_formula = 1/25` と低い。
3. **通常 60 問より難しいのは、manual だけでなく verified hard structured を大量に含むから**  
   `verified_trace_ready` でも specialized では `143/373 = 0.3834` に落ちる。
4. **bit_synth exact-trace v1 と比べると、v2 は boxing / closure は強いが、structured / affine の rule induction で負けている**  
   specialized では v2 が `0.3375`、v1 が `0.3925`。

要するに、この baseline は **「箱に入れて終える」能力はかなり持っているが、hard structured binary を正しく決め切る教師が足りない**。

## 1. Topline

`binary_bias_specialized_eval_summary.md` と `binary_bias_teacher_style_summary.json` の要点は以下。

| metric | value | 読み方 |
| --- | ---: | --- |
| rows | `563` | 60 問 watch よりかなり広い binary slice |
| accuracy | `0.3375` | `190/563` |
| contains_boxed_literal_rate | `0.8064` | 出力の大半は literal な `\boxed{}` を含む |
| gold_anywhere_rate | `0.5222` | 本文のどこかに gold 相当が現れる率は過半 |
| last_bit8_exact_rate | `0.3410` | 最後の 8-bit 候補が gold と一致する率 |
| mean_raw_output_chars | `12138.7` | 依然として長文化しやすい |
| mean_bit_fragment_count | `72.85` | binary 断片の散布が多い |

補足:

- `contains_oxed_literal_rate = 0.8064` も同値だが、raw text の byte を見るとこの run は `92, 98, 111, 120` (`\boxed`) であり、**v1 の backspace bug ではない**。ここでは `boxed` が `oxed` を部分文字列として含むため同率に見えているだけと読むのが安全。

## 2. 通常の 60 問 binary watch より何が厳しいか

同じ adapter の通常 benchmark は `29/60 = 0.4833` だった。specialized set は次のように落ちる。

| slice | normal binary watch | specialized | delta |
| --- | ---: | ---: | ---: |
| overall | `0.4833` | `0.3375` | `-0.1458` |
| `verified_trace_ready` | `0.7000` | `0.3834` | `-0.3166` |
| `answer_only_keep` | `0.4000` | `0.2867` | `-0.1133` |
| `manual_audit_priority` | `0.3500` | `0.1000` | `-0.2500` |
| `bit_other` | `0.5217` | `0.3394` | `-0.1823` |
| `bit_structured_byte_formula` | `0.3571` | `0.2332` | `-0.1239` |

ここから分かるのは、specialized set は単に manual を増やしただけではないということ。

- `verified_trace_ready` が `0.70 -> 0.3834` まで落ちる
- `bit_structured_byte_formula` が大量に入り、しかも safe / abstract / not-formula の hard side が濃い
- `bit_permutation_inversion` は逆に `50/62 = 0.8065` と強く、**binary 全体が難化しているのではなく、structured hard side が強く sampled されている**

## 3. 何が解けていて、何が解けていないか

### 3.1 focus bucket

| bucket | correct / rows | accuracy | 読み方 |
| --- | ---: | ---: | --- |
| `rare_byte_transform` | `11/11` | `1.0000` | 完全に押し切っている |
| `supported_bijection` | `45/50` | `0.9000` | permutation bijection は非常に強い |
| `boolean_family` | `32/60` | `0.5333` | boolean 系は過半 |
| `no_solver_answer_only` | `21/70` | `0.3000` | answer-only hard は 3 割止まり |
| `supported_affine_xor` | `18/60` | `0.3000` | affine_xor は watch よりかなり弱い |
| `dominant_structured_safe` | `35/120` | `0.2917` | safe structured でも 3 割弱 |
| `dominant_structured_abstract` | `19/90` | `0.2111` | abstract structured はさらに弱い |
| `no_solver_manual` | `4/40` | `0.1000` | manual hard はほぼ未解決 |
| `supported_not_structured` | `3/55` | `0.0545` | 最大の穴 |

### 3.2 exposure band

| exposure | correct / rows | accuracy | 読み方 |
| --- | ---: | ---: | --- |
| `rare` | `13/18` | `0.7222` | 決まり切った rare family は強い |
| `supported` | `98/225` | `0.4356` | supported family は中位 |
| `dominant` | `54/210` | `0.2571` | dominant structured 群が重い |
| `underrepresented` | `25/110` | `0.2273` | 薄い family は弱い |

つまりこの model は、

- **明示的な solver family を持つ permutation / transform には強い**
- **structured formula / not-formula / no-solver 群では急落する**

というかなりはっきりした形をしている。

## 4. solver family で見ると穴がさらに明確

| teacher solver | correct / rows | accuracy |
| --- | ---: | ---: |
| `binary_byte_transform` | `11/11` | `1.0000` |
| `binary_bit_permutation_bijection` | `45/50` | `0.9000` |
| `binary_three_bit_boolean` | `10/14` | `0.7143` |
| `binary_two_bit_boolean` | `22/46` | `0.4783` |
| `binary_affine_xor` | `18/60` | `0.3000` |
| `binary_bit_permutation_independent` | `2/7` | `0.2857` |
| `binary_structured_byte_formula_abstract` | `16/73` | `0.2192` |
| `binary_structured_byte_formula` | `18/87` | `0.2069` |
| `binary_structured_byte_not_formula` | `1/25` | `0.0400` |

この順序は重要で、今回の baseline は

- **copy / rotate / bijection / simple boolean** はかなり学習できている
- しかし **byte formula を examples から再構成する型**になると一気に弱い

特に `binary_structured_byte_not_formula` の `1/25` は、現行 `train_split_with_cot.csv` の strongest blind spot とみなしてよい。

## 5. selection tier から見えること

| tier | correct / rows | accuracy |
| --- | ---: | ---: |
| `verified_trace_ready` | `143/373` | `0.3834` |
| `answer_only_keep` | `43/150` | `0.2867` |
| `manual_audit_priority` | `4/40` | `0.1000` |

`verified > answer_only > manual` の序列自体は自然だが、specialized では **verified でも 4 割未満** まで落ちる。

これは、今回の benchmark が

- easy verified を測っているのではなく
- **verified の中でも structured 側の hardest slice** を多く含んでいる

ことを意味する。

また bucket tier を見ると、

- `dominant_structured_safe`: `answer_only_keep 17/33 = 0.5152`, `verified 18/87 = 0.2069`
- `dominant_structured_abstract`: `answer_only_keep 3/17 = 0.1765`, `verified 16/73 = 0.2192`
- `supported_not_structured`: `answer_only_keep 2/30 = 0.0667`, `verified 1/25 = 0.0400`

となっており、answer-only は一部 safe structured で多少効くが、**not-formula や hard structured を根本解決するほどではない**。

## 6. 失敗は format だけではない

### 6.1 fallback の内訳

| fallback | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `boxed_non_empty` | `452` | `190` | `0.4204` |
| `last_number` | `109` | `0` | `0.0000` |
| `boxed_empty` | `2` | `0` | `0.0000` |

ここはかなり強いシグナルで、**fallback に落ちた瞬間に全滅**している。  
したがって README 準拠では、specialized benchmark でも primary path はやはり `\boxed{}`。

### 6.2 ただし boxed できても content が足りない

`boxed_non_empty` が 452 行あるのに正解は 190 行しかない。つまり main failure は

1. box に入れられない failure
2. **box には入れたが中身が wrong**

の両方だが、数量としては後者がかなり大きい。

### 6.3 box の回数と正答率

| boxed_count | rows | correct | accuracy |
| --- | ---: | ---: | ---: |
| `2` | `313` | `152` | `0.4856` |
| `1` | `135` | `37` | `0.2741` |
| `3` | `6` | `1` | `0.1667` |
| `0` | `109` | `0` | `0.0000` |

**2 boxes が最も強い**のは興味深い。  
この run では、推論途中で一度 box を書き、最後にもう一度 final box を閉じるようなパターンが、single-box より安定している可能性がある。

### 6.4 長文化の影響

row-level `raw_output` を再集計すると、

- correct 平均長: `7508.0`
- wrong 平均長: `14497.5`
- correct median: `6889.5`
- wrong median: `14590.0`

で、**誤答は正答のほぼ 2 倍の長さ**になっている。  
つまり v2 baseline でも、hard binary に入ると「考え続ける」方向へ崩れやすい。

## 7. 代表例

### 7.1 強い側

| bucket | id | gold | pred | 補足 |
| --- | --- | --- | --- | --- |
| `supported_bijection` | `1054486f` | `10011110` | `10011110` | verified + bijection で素直に通る |
| `boolean_family` | `5f66eb60` | `11111111` | `11111111` | 2-box で closure が安定 |
| `no_solver_answer_only` | `10dfe5c5` | `10100000` | `10100000` | answer-only でも一部は回収 |
| `supported_not_structured` | `0528d502` | `00011111` | `00011111` | 稀に hard bucket も通る |

### 7.2 弱い側

| bucket | id | gold | pred | 補足 |
| --- | --- | --- | --- | --- |
| `supported_not_structured` | `009a74b6` | `11111011` | `00000110` | box はあるが中身が大きくズレる |
| `dominant_structured_safe` | `19f4b3d6` | `00000011` | `00000000` | answer-only structured の near-miss |
| `supported_affine_xor` | `008b52fd` | `01100101` | `00011101` | affine_xor で content miss |
| `last_number` failure | `0f7ddd75` | `11110110` | `1` | fallback に落ちた瞬間に壊れる |

## 8. bit_synth exact-trace v1 specialized との比較

同じ 563 問 specialized benchmark で、bit_synth exact-trace v1 は `0.3925`、今回の v2 baseline は `0.3375`。  
差分を bucket ごとに見ると次のようになる。

| bucket | v2 | v1 | delta (v2-v1) |
| --- | ---: | ---: | ---: |
| `no_solver_answer_only` | `0.3000` | `0.2571` | `+0.0429` |
| `boolean_family` | `0.5333` | `0.5000` | `+0.0333` |
| `no_solver_manual` | `0.1000` | `0.0750` | `+0.0250` |
| `supported_bijection` | `0.9000` | `0.8800` | `+0.0200` |
| `supported_not_structured` | `0.0545` | `0.0364` | `+0.0182` |
| `rare_byte_transform` | `1.0000` | `1.0000` | `0.0000` |
| `dominant_structured_safe` | `0.2917` | `0.4000` | `-0.1083` |
| `rare_perm_independent` | `0.2857` | `0.4286` | `-0.1429` |
| `dominant_structured_abstract` | `0.2111` | `0.3667` | `-0.1556` |
| `supported_affine_xor` | `0.3000` | `0.4833` | `-0.1833` |

row-level にも同じ傾向が出ている。

- **v2-only correct**: `58`
- **v1-only correct**: `89`

v2-only correct は `boolean_family` や `no_solver_answer_only` に多く、v1-only correct は `dominant_structured_safe` / `dominant_structured_abstract` / `supported_affine_xor` に偏る。

つまり、

- v2 baseline は **boxing と short closure** によって short-fragment failure を減らせている
- v1 exact-trace は **structured family の rule induction** でまだ優位

と読める。

## 9. この結果が `train_split_with_cot_v2.csv` 方針を支持する理由

今回の specialized eval から、次の判断はかなり強く支持される。

1. **追加すべきは structured verified binary**  
   最大の穴が `binary_structured_byte_formula` / `abstract` / `not_formula` だから。
2. **answer-only / manual を先に増やすべきではない**  
   specialized では `answer_only_keep 0.2867`, `manual 0.1000` と弱い。
3. **boxing を壊してはいけない**  
   `last_number = 0/109` なので、fallback 頼みは通用しない。
4. **v1 の強みは structured induction にあるが、そのまま置換は危険**  
   v1 は specialized で強いが、別 benchmark では boxing bug と非 binary 劣化があった。

したがって、今回作成した `train_split_with_cot_v2.csv` のように、

- 既存 v2 を温存し
- hardest `bit_structured_byte_formula` verified を追加し
- notebook 側の正しい boxing 実装を維持する

という保守的拡張は、この benchmark の観測と整合している。

## 10. 最終所見

この specialized benchmark は、`nemotron-sft-lora-with-cot-v2` baseline の binary 能力をかなり明確に分解している。

- **強み**: bijection / byte transform / 一部 boolean / box closure
- **弱み**: structured formula / abstract structured / not-formula / affine_xor
- **致命点**: fallback に落ちた 109 行は全滅

したがって次の改善は、「もっと binary を増やす」ではなく、

1. structured verified teacher の増量
2. final boxed commit の維持
3. answer-only / manual の過剰混入を避ける

の順で進めるのが最も合理的である。
