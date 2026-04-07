# `verified_trace_ready && bit_structured_byte_formula` 出力変化の深掘り分析

## 対象と問い

- 評価前提:
  - `README.md` の Evaluation は **Accuracy** で、最終解答は `\boxed{}` 優先抽出、binary は exact string 判定。
- 比較対象:
  - `baseline/nemotron-sft-lora-with-cot-v2/result/origin/phase0_offline_eval_binary_bias_specialized/artifacts/binary_bias_specialized_eval_row_level.csv`
  - `baseline/nemotron-sft-lora-with-cot-v2/result/v2/phase0_offline_eval_binary_bias_specialized/artifacts/binary_bias_specialized_eval_row_level.csv`
- 学習方針:
  - `baseline/nemotron-sft-lora-with-cot-v2/TRAIN_SPLIT_WITH_COT_V2_STRATEGY.md`
  - 追加 414 行はすべて unused `verified_trace_ready` の structured binary で、teacher 形式は
    `Check examples:` / `So the verified rule is ...` / `Query x = ...` / `Constraints: ...`
    を持つ short exact-trace だった。

今回の問いは、

> `verified_trace_ready && bit_structured_byte_formula` は正答率だけでなく、生成される文章の傾向にも何も変化がないのか

である。

## 結論

**「何も変化がない」は明確に否。出力はかなり大きく変化している。**  
ただし、その変化は **strategy で追加した synthetic teacher の定型句への接近ではなく**、既存の
`We need to infer ...` 系テンプレートを保ったまま、

- 冒頭をより単純な generic start に寄せる
- `Let’s analyze.` を増やす
- boxed 到達率を少し上げる
- しかし hardest structured slice の content error はあまり直らない

という方向だった。

要するに、今回の v2 は **teacher style transfer には失敗気味だが、出力 rewrite 自体は大きく起きている**。  
しかもその rewrite は、改善行では「短く boxed に戻る」、悪化行では「長くなって fallback に落ちる」という非対称な形を取っている。

## 1. まず、target slice 全体の挙動はどう変わったか

対象 slice は **`selection_tier = verified_trace_ready` かつ `template_subtype = bit_structured_byte_formula`** の 185 行。

| metric | origin | v2 | delta |
| --- | ---: | ---: | ---: |
| accuracy | `35/185 = 0.1892` | `34/185 = 0.1838` | `-0.0054` |
| has_boxed | `135/185 = 0.7297` | `143/185 = 0.7730` | `+0.0433` |
| fallback = `last_number` | `50/185 = 0.2703` | `42/185 = 0.2270` | `-0.0433` |
| contains_so_rule | `17/185 = 0.0919` | `28/185 = 0.1514` | `+0.0595` |
| contains_constraints | `0/185 = 0.0000` | `1/185 = 0.0054` | `+0.0054` |
| gold_anywhere | `83/185 = 0.4486` | `86/185 = 0.4649` | `+0.0163` |
| mean_raw_output_chars | `14337.5` | `14499.6` | `+162.1` |
| median_raw_output_chars | `14401` | `14666` | `+265` |
| mean_bit_fragment_count | `79.66` | `86.74` | `+7.08` |

ここで重要なのは、

1. **boxed 到達率は上がっている**
2. **`contains_so_rule` も増えている**
3. **それでも正答率は微減**

という点。  
つまり、表面的な format / phrasing 改善だけでは hardest structured slice を押し切れていない。

### 1.1 `gold_anywhere` は「正解に辿り着きやすくなった」の意味か

**限定的には yes だが、直接そう解釈するのは危険**。  
`README.md` の採点は `\boxed{}` 優先抽出なので、`gold_anywhere` は **出力のどこかで一度 gold 文字列に触れた率**であって、**最終的に採点される答えへ正しく commit した率**そのものではない。

target slice では次のようになる。

| run | `gold_anywhere = yes` の正答率 | `gold_anywhere = no` の正答率 | `gold_anywhere but wrong` |
| --- | ---: | ---: | ---: |
| origin | `35/83 = 0.4217` | `0/102 = 0.0000` | `48` |
| v2 | `34/86 = 0.3953` | `0/99 = 0.0000` | `52` |

ここから分かることは 2 つある。

1. **この slice では `gold_anywhere` は必要条件にかなり近い**  
   gold に一度も触れていない行は、origin / v2 ともに **全滅**だった。
2. **ただし十分条件ではない**  
   v2 では `gold_anywhere` 行が `83 -> 86` に増えたのに、`gold_anywhere but wrong` も `48 -> 52` に増えている。  
   つまり **途中で gold 候補に触れる頻度は増えたが、それを final box に正しく固定する力はむしろ弱い**。

したがって `gold_anywhere_rate` 上昇は、

- **「候補生成や途中到達は少し近づいた」**

という弱いプラスシグナルではあるが、

- **「正解に辿り着きやすくなった」**

の強い証拠ではない。  
今回の v2 は、むしろ **gold に触れてから取りこぼす行が増えた**と読むのが実態に近い。

## 2. 出力は本当に変わっているのか

ペア比較すると、変化はかなり大きい。

| paired metric | value |
| --- | ---: |
| same prediction | `49/185 = 0.2649` |
| same raw output | `0/185 = 0.0000` |
| raw output similarity mean | `0.0524` |
| raw output similarity median | `0.0495` |

この slice では **raw output 完全一致が 0 行**で、prediction 一致も 26.5% しかない。  
したがって、「文章傾向が変わっていない」は成立しない。**モデルはほぼ全行で別の文章を書いている。**

ただし、その「変わり方」は teacher 由来の新テンプレートではなく、**同じ generic scaffold の再書き換え**に近い。

## 3. synthetic teacher の定型句は transfer したか

strategy 上、追加 414 行の synthetic teacher は全行で同じ定型句を持っていた。

| phrase | added 414 train rows | origin target | v2 target |
| --- | ---: | ---: | ---: |
| `Check examples:` | `414/414 = 1.0000` | `14/185 = 0.0757` | `9/185 = 0.0486` |
| `So the verified rule is` | `414/414 = 1.0000` | `0/185 = 0.0000` | `0/185 = 0.0000` |
| `Constraints:` | `414/414 = 1.0000` | `0/185 = 0.0000` | `3/185 = 0.0162` |
| `leading zeros` | `414/414 = 1.0000` | `15/185 = 0.0811` | `18/185 = 0.0973` |
| `exact 8-bit` | `414/414 = 1.0000` | `0/185 = 0.0000` | `0/185 = 0.0000` |
| `Query x =` | `414/414 = 1.0000` | `0/185 = 0.0000` | `0/185 = 0.0000` |
| `box_only_final` | `414/414 = 1.0000` | `0/185 = 0.0000` | `0/185 = 0.0000` |
| `final box` | `414/414 = 1.0000` | `0/185 = 0.0000` | `0/185 = 0.0000` |

さらに、added rows の冒頭は **414/414 が `Check examples:`** だったが、target eval 出力の
`starts_check_examples_rate` は origin / v2 ともに **`0.0`**。

結論として、**teacher phrase の直接転写はほぼ起きていない**。  
追加データは出力内容を変えているが、**期待した表層テンプレートをそのままは学習していない**。

## 4. では何に寄ったのか

行頭を見ると、v2 は明確に簡素化・標準化している。

### origin の主要行頭

- `28` 行: `We need to infer the transformation rule from examples. 8-bit input -> 8-bit output. Let's inspect patterns.`
- `23` 行: `We need to infer the transformation rule from examples. 8-bit input -> 8-bit output. Likely each output bit is some func...`
- `19` 行: `We need to infer the transformation rule from examples. 8-bit input -> 8-bit output. Let's list bits positions 0-7.`

### v2 の主要行頭

- `102` 行: `We need to infer the transformation rule from examples. 8-bit input -> 8-bit output.`
- `62` 行: `We need to infer the transformation rule from examples. Let’s analyze.`

つまり v2 は、

- 旧来の `We need to infer...` はそのまま維持
- その後ろの具体的な「inspect patterns / list bits / likely function」部分を削る
- 一部を `Let’s analyze.` に寄せる

という **generic start への mode collapse** を起こしている。

`we need to infer` 自体は origin / v2 ともに **185/185** で不変だった。  
したがって、変化はテンプレートの土台ではなく **2 文目以降の書き方**に集中している。

## 5. 改善行と悪化行では、変化の向きが違う

### 5.1 outcome category

| category | rows |
| --- | ---: |
| stay wrong | `136` |
| regressed | `15` |
| improved | `14` |
| stay correct | `20` |

### 5.2 改善行

| metric | origin improved rows | v2 improved rows |
| --- | ---: | ---: |
| boxed rows | `8/14` | `14/14` |
| `last_number` rows | `6/14` | `0/14` |
| contains_so_rule | `2/14` | `6/14` |
| mean_raw_output_chars | `15581.1` | `12301.6` |
| mean_bit_fragment_count | `68.29` | `80.71` |

改善行では、v2 は **boxed を回復し、`last_number` 落ちを消し、平均 3,279 文字ほど短く**なっている。  
つまり良い変化は、**短く閉じて final box に到達する**方向。

### 5.3 悪化行

| metric | origin regressed rows | v2 regressed rows |
| --- | ---: | ---: |
| boxed rows | `15/15` | `9/15` |
| `last_number` rows | `0/15` | `6/15` |
| contains_so_rule | `3/15` | `1/15` |
| mean_raw_output_chars | `11470.6` | `15099.1` |
| mean_bit_fragment_count | `71.67` | `107.53` |

悪化行では逆に、v2 は **boxed を失い、`last_number` に落ち、平均 3,628 文字ほど長く**なっている。  
つまり悪い変化は、**長文化して bit fragment をばらまきながら最後に崩れる**方向。

### 5.4 ここから分かること

同じ「文章が変わる」でも、

- **改善**は `shorter + boxed + rule closure`
- **悪化**は `longer + fragment scatter + fallback`

に対応している。  
したがって次の改善は、単なる style control ではなく **長文化と unboxed 終了を抑える制御**が重要になる。

## 6. solver family ごとの text shift

| solver | metric | origin | v2 |
| --- | --- | ---: | ---: |
| `binary_structured_byte_formula` | accuracy | `18/87 = 0.2069` | `16/87 = 0.1839` |
|  | boxed rows | `66` | `71` |
|  | `last_number` rows | `21` | `16` |
|  | contains_so_rule | `7` | `15` |
|  | mean_raw_output_chars | `14197.4` | `13927.0` |
| `binary_structured_byte_formula_abstract` | accuracy | `16/73 = 0.2192` | `18/73 = 0.2466` |
|  | boxed rows | `52` | `57` |
|  | `last_number` rows | `21` | `16` |
|  | contains_so_rule | `9` | `12` |
|  | mean_raw_output_chars | `14124.9` | `14616.7` |
| `binary_structured_byte_not_formula` | accuracy | `1/25 = 0.0400` | `0/25 = 0.0000` |
|  | boxed rows | `17` | `15` |
|  | `last_number` rows | `8` | `10` |
|  | contains_so_rule | `1` | `1` |
|  | mean_raw_output_chars | `15445.9` | `16150.3` |

ここで重要なのは、

1. **safe formula**  
   boxed は増え、`so_rule` も倍増したのに accuracy は落ちている。  
   → **表層 style は改善しても、中身の rule induction はまだ wrong**。
2. **abstract**  
   boxed / `so_rule` ともに増えて accuracy も微増。  
   → 追加データは **abstract 側には一部効いている**。
3. **not_formula**  
   boxed も減り、`last_number` も増え、accuracy は 0。  
   → **teacher 形式が not-formula にほぼ効いていない**。

## 7. style feature と正答率の関係

README 前提では boxed が必要条件だが、target slice でもその傾向は極端にはっきり出る。

### 7.1 boxed / no box

| run | boxed accuracy | no-box accuracy |
| --- | ---: | ---: |
| origin | `35/135 = 0.2593` | `0/50 = 0.0000` |
| v2 | `34/143 = 0.2378` | `0/42 = 0.0000` |

**no-box は両 run とも全滅**。  
したがってこの slice では、README 的にも boxed 到達は依然として絶対条件。

### 7.2 explicit rule commitment

| run | `contains_so_rule` accuracy | no `so_rule` accuracy |
| --- | ---: | ---: |
| origin | `7/17 = 0.4118` | `28/168 = 0.1667` |
| v2 | `9/28 = 0.3214` | `25/157 = 0.1592` |

`so_rule` を含む行は、両 run で slice 平均よりかなり高い。  
これは **「rule を言い切る」出力が成功と相関する**ことを示す。

ただし v2 は `contains_so_rule` を増やしたのに全体が伸びていないため、現状は

- rule commitment 自体は良い兆候
- しかし commitment される rule の内容がまだ wrong

という段階にある。

### 7.3 boxed count

| run | 1 box | 2 boxes |
| --- | ---: | ---: |
| origin | `10/48 = 0.2083` | `25/84 = 0.2976` |
| v2 | `8/59 = 0.1356` | `25/83 = 0.3012` |

target slice でも **2-box が最も強い**。  
しかも v2 では 1-box accuracy がかなり落ちている一方、2-box は維持されている。  
よって改善は、generic one-box 化より **途中の closure を経て最後の box に落とす形**の方が有望と読める。

## 8. 代表例

### 改善例

1. `0ba9af93` (`binary_structured_byte_formula_abstract`)  
   origin は boxed だが `11111011` と誤答、v2 は boxed のまま `11110110` に修正。  
   冒頭は両者とも generic だが、v2 の方が短くまとまっている。
2. `2817d770` (`binary_structured_byte_formula`)  
   origin `01001110` → v2 `01100110`。両者 boxed。  
   「teacher phrase transfer」ではなく **content correction** が起きた例。

### 悪化例

1. `01d894fb` (`binary_structured_byte_formula_abstract`)  
   origin は correct boxed `11000000`、v2 は長文化して unboxed `1` へ崩壊。  
   **format regression 型**。
2. `17fd9612` (`binary_structured_byte_formula`)  
   両者 boxed だが、origin correct `00011010` に対し v2 は `01101000`。  
   **content drift 型**。
3. `f9c59b61` (`binary_structured_byte_not_formula`)  
   両者 boxed だが、origin correct `01001011` に対し v2 は `11001011`。  
   **not-formula content miss 型**。

## 9. 次の改善に直結する示唆

この分析から、次にやるべきことはかなり具体的になった。

1. **teacher 形式の「表層句」ではなく、「rule commitment の中身」を学習させる必要がある**  
   `So the verified rule is ...` という phrase 自体は transfer していないが、`contains_so_rule` が高正答率と相関している。  
   次は phrase 模倣ではなく、**正しい rule を短く断言してから box に落とす supervision** を強めるべき。
2. **safe formula と not-formula を分けて扱うべき**  
   abstract だけ改善し、safe / not-formula は未改善または悪化。  
   `binary_structured_byte_not_formula` は teacher を別設計にしないと厳しい。
3. **長文化抑制は重要**  
   改善行は短くなり、悪化行は長くなる。  
   hardest structured slice では、長い探索文は content drift / fallback と強く結びついている。
4. **2-box の維持を優先**  
   2-box は origin / v2 ともに約 30% で最強。  
   1-box は v2 でむしろ崩れているので、generic one-box を増やすより **「途中で rule を閉じて、最後にもう一度 boxed final」** を安定化した方がよい。
5. **今回の v2 は style rewrite は起こせると分かった**  
   0 行 raw 一致、same prediction 26.5% なので、adapter はこの slice にちゃんと影響している。  
   問題は「影響していない」ことではなく、**影響の向きが teacher 形式の本質に届いていない**こと。

## 最終結論

`verified_trace_ready && bit_structured_byte_formula` は、**正答率だけでなく文章傾向も大きく変化している**。  
ただしその変化は、

- synthetic teacher の `Check examples / So the verified rule is / Query x / Constraints` への接近ではなく
- generic `We need to infer...` を維持した rewrite と、
- boxed 到達率の小改善、
- そして改善時は短文化、悪化時は長文化

という形で出ている。

したがって次の改善は、**「teacher phrase をもっと増やす」ではなく、「正しい rule commitment を短く言い切って 2-box で閉じる」ように safe / not-formula 別で supervision を作り直すこと**が最も有望である。

## 10. v3 改善方針・実験計画

ここまでの比較を踏まえると、v3 の主眼は **`verified_trace_ready && bit_structured_byte_formula` の内容誤りを直しつつ、README 前提の boxed-first 評価を壊さないこと**に尽きる。

### 10.1 v3 の基本方針

v3 で採るべき方針は次の 5 つ。

1. **phrase imitation ではなく rule commitment quality を上げる**  
   `Check examples:` や `So the verified rule is ...` の表層転写は起きていないので、teacher phrase を増やすのではなく、**正しい rule を短く断言する supervision** を増やす。
2. **safe / abstract / not-formula を別 teacher に分ける**  
   `abstract` は微改善、`safe` は悪化、`not-formula` は `0/25` まで落ちたので、structured を一括で扱ってはいけない。
3. **model-native な冒頭に寄せる**  
   v2 で残った自然出力は `We need to infer ...` / `Let’s analyze.` 系だった。したがって teacher 冒頭はモデルの既存 scaffold に近づける。
4. **長文化を抑える**  
   改善行は短く、悪化行は長くなる。teacher も 3〜5 文程度に抑え、探索文の横流れを避ける。
5. **boxed closure は content supervision とセットで守る**  
   no-box は全滅で、`gold_anywhere` だけ増えても意味が薄い。最終的には正しい答えを boxed answer に commit させる必要がある。

### 10.2 v3 で優先して直す点

#### A. safe formula teacher の再設計

`binary_structured_byte_formula` は boxed / `contains_so_rule` が増えたのに accuracy が落ちた。  
よって v3 では、safe formula 用 teacher を

1. support を短く明示
2. bit position または byte transform を canonical に一文で固定
3. query 適用を 1 段で閉じる

形に変え、**探索風の文章ではなく deterministic な rule description** に寄せる。

#### B. abstract は維持しつつ hard-mining

`binary_structured_byte_formula_abstract` は唯一改善しているので、方向性は維持する。  
ただし量を増やすだけでなく、

- v2-only correct rows を優先参照
- origin-only correct / v2 regressed rows に近い失敗 pattern を避ける

という row-level hard-mining を入れる。

#### C. not-formula を別問題として扱う

`binary_structured_byte_not_formula` は現状 `0/25`。  
ここは safe formula と同じ teacher にせず、

1. `No single fixed byte formula fits all examples.` のように formula 仮定を先に否定
2. verified support / counterexample を短く明示
3. query ではその support に従って決める

という **counterexample-first / exclusion-first** teacher に切り替える。

#### D. closure 補助は低比率でのみ追加

`answer_only_keep` は主戦力ではないが、no-box 全滅を踏まえると closure 補助としては使える。  
したがって

- verified structured teacher を主役に据えたまま
- 低比率で boxed-only / short-rationale 補助を足す

枝は検討価値がある。

### 10.3 実験セット

| run | 変更内容 | 仮説 | 期待効果 | リスク |
| --- | --- | --- | --- | --- |
| `v3a-native-safe` | safe formula 281 行を model-native 冒頭 + explicit rule commitment 形式で再生成 | v2 の safe 悪化は teacher phrase mismatch と rule description の弱さが原因 | `binary_structured_byte_formula` 回復 | generic 化しすぎると supervision が弱い |
| `v3b-native-safe-abstract` | `v3a` + abstract 110 行も同形式で再生成 | abstract の改善を維持しつつ safe も戻す | target slice 全体の純増 | abstract を壊す可能性 |
| `v3c-notformula-special` | not-formula 23 行だけ counterexample-first teacher に差し替え | not-formula は別ロジックが必要 | `0/25` 脱出 | 行数が少なく効果が小さい可能性 |
| `v3d-hardmined-regression-fix` | origin-only correct / v2 regressed 近傍の training rows を優先再生成 | 実害のあった style drift を戻せる | regression 回収 | 局所最適化 |
| `v3e-closure-aux-lowratio` | `v3b` or `v3c` に少量の boxed-only / short-rationale 補助を低比率で追加 | last_number 落ちをさらに減らせる | closure 改善 | answer_only 由来の content 弱化 |
| `v3f-safe-plus-notformula` | safe と not-formula だけ別 teacher にし、abstract は v2 のまま | 問題 slice を最小変更で叩ける | リスク低めで効果確認 | gain が小さい可能性 |

### 10.4 実験優先順位

1. **`v3c-notformula-special`**  
   現状 `0/25` で最も未解決度が高い。
2. **`v3a-native-safe`**  
   safe formula 悪化を戻せるかを見る最小変更。
3. **`v3f-safe-plus-notformula`**  
   safe / not-formula を同時に叩きつつ abstract を壊さないか確認。
4. **`v3b-native-safe-abstract`**  
   safe 回復と abstract 維持を両立できるか確認。
5. **`v3e-closure-aux-lowratio`**  
   content 改善の方向が見えた後で closure 補助を載せる。
6. **`v3d-hardmined-regression-fix`**  
   最後に row-level regressed set を補修する。

### 10.5 teacher 具体案

#### safe formula 向け

1. `We infer the rule from the examples.`
2. `The rule is: ...`
3. `For the query, apply the same rule bit-by-bit and keep the exact 8-bit result with leading zeros for the final boxed answer.`

#### abstract 向け

1. `We infer the abstract bit rule from the examples.`
2. `The verified pattern is: ...`
3. `Apply that same pattern to the query and keep the exact 8-bit result for the final boxed answer.`

#### not-formula 向け

1. `No single fixed byte formula fits all examples.`
2. `The verified support is: ...`
3. `So for the query, follow that same verified support and keep the exact 8-bit result with leading zeros for the final boxed answer.`

### 10.6 v3 の評価軸

#### primary

1. `verified_trace_ready && bit_structured_byte_formula` 全体 accuracy
2. `binary_structured_byte_formula` accuracy
3. `binary_structured_byte_formula_abstract` accuracy
4. `binary_structured_byte_not_formula` accuracy

#### secondary

1. `boxed_non_empty` rate
2. `last_number` rate
3. `gold_anywhere but wrong` 件数
4. `contains_so_rule` 件数とその正答率
5. mean / median `raw_output_chars`
6. `1-box` / `2-box` の正答率

#### guardrail

1. overall specialized accuracy が v2 (`204/563`) を下回らない
2. `boxed_non_empty` が大きく悪化しない
3. `bit_other`, `bit_permutation_inversion` など非ターゲット強みを不必要に壊さない

### 10.7 v3 成功条件

最低限の成功条件は次の通り。

1. target slice `34/185` を上回る
2. `binary_structured_byte_formula` を `16/87` より改善する
3. `binary_structured_byte_not_formula` を `0/25` から脱出する
4. `last_number` を v2 の `42/185` より減らす
5. `gold_anywhere but wrong` を `52` より減らす

特に **not-formula 脱出**は、v3 が問題の本体に効いたかを見る最重要シグナルになる。

## 最終整理

v3 の主眼は **「verified structured をもっと増やす」ことではなく、solver-slice ごとに teacher を再設計すること**である。  
つまり次にやるべきことは、

1. **teacher を model-native に寄せる**
2. **safe / abstract / not-formula を分ける**
3. **正しい rule commitment を短く強くする**
4. **長文化を抑える**
5. **boxed closure を content supervision と一緒に守る**

であり、**同型 synthetic の追加量勝負ではなく、teacher 設計の質で勝つ**方向へ切り替えるべきだと結論づける。
