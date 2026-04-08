# `train_split_with_cot_v3f_safe_plus_notformula.csv` 学習版 binary bias specialized 比較レポート

## 対象と前提

- 今回の学習データ:
  - `baseline/nemotron-sft-lora-with-cot-v2/artifacts/train_split_with_cot_v3f_safe_plus_notformula.csv`
- 比較元:
  - `baseline/nemotron-sft-lora-with-cot-v2/result/origin/phase0_offline_eval_binary_bias_specialized/reports/binary_bias_specialized_deep_analysis.md`
  - `baseline/nemotron-sft-lora-with-cot-v2/result/origin/phase0_offline_eval_binary_bias_specialized/reports/binary_bias_specialized_eval_summary.md`
  - `baseline/nemotron-sft-lora-with-cot-v2/result/v2/phase0_offline_eval_binary_bias_specialized/reports/binary_bias_specialized_eval_summary.md`
- 今回の比較対象:
  - `baseline/nemotron-sft-lora-with-cot-v2/result/v3f/phase0_offline_eval_binary_bias_specialized/reports/binary_bias_specialized_eval_summary.md`
  - `baseline/nemotron-sft-lora-with-cot-v2/result/v3f/phase0_offline_eval/reports/phase0_eval_summary.md`
  - 各 run の `artifacts/binary_bias_specialized_eval_summary.json` と row-level CSV

`README.md` の Evaluation は **Accuracy** で、最終解答は `\boxed{}` 優先抽出、binary は exact string 判定である。したがって今回の比較も、

1. **boxed で確実に閉じるか**
2. **box の中身を exact 8-bit で当てるか**

を分けて見る。

なお `result/v2` 配下には specialized artifact はあるが、同階層の `phase0_offline_eval` 一式は見当たらなかった。そのため **320 問 phase0 比較は origin と v3f のみ**、**563 問 binary bias specialized 比較は origin / v2 / v3f の 3 者比較**で行う。

## 結論

`train_split_with_cot_v3f_safe_plus_notformula.csv` 学習版の binary bias specialized score は **`238/563 = 0.4227`** で、

- origin の **`190/563 = 0.3375`** から **`+48` 問 / `+0.0852`**
- v2 の **`204/563 = 0.3623`** から **`+34` 問 / `+0.0604`**

改善した。

これは origin deep analysis が主ボトルネックと特定していた **structured binary** に対して、v2 よりも明確に効いている。特に `binary_structured_byte_formula` が **`18/87 -> 34/87`**、`dominant_structured_safe` が **`35/120 -> 53/120`** と大きく伸びており、v2 比較でもそれぞれ **`+18` 問**、**`+20` 問**の上積みになっている。

一方で、通常 320 問 phase0 の topline は **`249/320 = 0.7781`** で origin と同値だった。内訳は、

- binary hard set: **`29/60 -> 27/60`** で `-2`
- symbol watch set: **`22/60 -> 24/60`** で `+2`
- general stable set: **`198/200 -> 198/200`** で横ばい

となっており、**specialized binary の改善をそのまま通常 320 問の topline 増加には変換できていない**。

要するに今回の v3f は、

1. **563 問 specialized では明確な勝ち**
2. **origin deep analysis が指摘した structured gap には実際に効いた**
3. **ただし通常 60 問 binary watch ではまだ退行が残る**
4. **320 問 overall は symbol 改善で binary 退行を相殺して同値**

という評価になる。

## 1. Topline 差分

### 1.1 binary bias specialized

| run | correct / rows | accuracy | delta vs origin | delta vs v2 |
| --- | ---: | ---: | ---: | ---: |
| `origin` | `190/563` | `0.3375` | `-` | `-0.0248` |
| `v2` | `204/563` | `0.3623` | `+0.0248` | `-` |
| `v3f` | `238/563` | `0.4227` | `+0.0852` | `+0.0604` |

### 1.2 phase0 local320

| run | overall | general stable | binary hard | symbol watch |
| --- | ---: | ---: | ---: | ---: |
| `origin` | `249/320 = 0.7781` | `198/200 = 0.9900` | `29/60 = 0.4833` | `22/60 = 0.3667` |
| `v3f` | `249/320 = 0.7781` | `198/200 = 0.9900` | `27/60 = 0.4500` | `24/60 = 0.4000` |

phase0 は完全に横ばいで、**specialized 改善の果実は主に 563 問 binary hard benchmark に出ている**。

## 2. origin deep analysis の仮説に対して何が起きたか

origin deep analysis の主張は要約すると次の 3 点だった。

1. **boxing は重要だが、主ボトルネックは structured content error**
2. **`binary_structured_byte_formula` / `abstract` / `not_formula` が最大の穴**
3. **fallback はほぼ効かないので、boxed primary path を壊してはいけない**

今回の v3f 実測は、このうち 1 と 2 をかなり強く支持しつつ、3 をさらに極端な形で満たした。

### 2.1 structured gap は本当に縮んだ

| solver family | origin | v2 | v3f | delta v3f-origin | delta v3f-v2 |
| --- | ---: | ---: | ---: | ---: | ---: |
| `binary_structured_byte_formula` | `18/87 = 0.2069` | `16/87 = 0.1839` | `34/87 = 0.3908` | `+0.1839` | `+0.2069` |
| `binary_structured_byte_formula_abstract` | `16/73 = 0.2192` | `18/73 = 0.2466` | `21/73 = 0.2877` | `+0.0685` | `+0.0411` |
| `binary_structured_byte_not_formula` | `1/25 = 0.0400` | `0/25 = 0.0000` | `1/25 = 0.0400` | `+0.0000` | `+0.0400` |

targeted slice 全体で見ると、

- origin: **`35/185 = 0.1892`**
- v2: **`34/185 = 0.1838`**
- v3f: **`56/185 = 0.3027`**

であり、v3f は **origin 比 `+21` 問 / `+0.1135`、v2 比 `+22` 問 / `+0.1189`** と、今回狙っていた structured verified 系をはっきり押し上げた。

### 2.2 ただし not-formula はまだ未解決

`binary_structured_byte_not_formula` は **`1/25`** のままで、origin と同値、v2 の全滅からは戻したが breakthrough ではない。今回の gain は主に

- `safe formula`
- `abstract`

から来ており、**safe-plus-notformula という命名に対して、実際の大きな改善は safe 側に偏っている**。

## 3. どの bucket で伸びたか

### 3.1 focus bucket

| focus bucket | origin | v2 | v3f | delta v3f-origin | delta v3f-v2 |
| --- | ---: | ---: | ---: | ---: | ---: |
| `dominant_structured_safe` | `35/120 = 0.2917` | `33/120 = 0.2750` | `53/120 = 0.4417` | `+0.1500` | `+0.1667` |
| `dominant_structured_abstract` | `19/90 = 0.2111` | `22/90 = 0.2444` | `28/90 = 0.3111` | `+0.1000` | `+0.0667` |
| `supported_affine_xor` | `18/60 = 0.3000` | `23/60 = 0.3833` | `26/60 = 0.4333` | `+0.1333` | `+0.0500` |
| `boolean_family` | `32/60 = 0.5333` | `33/60 = 0.5500` | `37/60 = 0.6167` | `+0.0834` | `+0.0667` |
| `rare_perm_independent` | `2/7 = 0.2857` | `3/7 = 0.4286` | `4/7 = 0.5714` | `+0.2857` | `+0.1428` |
| `supported_bijection` | `45/50 = 0.9000` | `47/50 = 0.9400` | `47/50 = 0.9400` | `+0.0400` | `+0.0000` |
| `no_solver_manual` | `4/40 = 0.1000` | `3/40 = 0.0750` | `6/40 = 0.1500` | `+0.0500` | `+0.0750` |
| `no_solver_answer_only` | `21/70 = 0.3000` | `27/70 = 0.3857` | `26/70 = 0.3714` | `+0.0714` | `-0.0143` |
| `rare_byte_transform` | `11/11 = 1.0000` | `11/11 = 1.0000` | `10/11 = 0.9091` | `-0.0909` | `-0.0909` |
| `supported_not_structured` | `3/55 = 0.0545` | `2/55 = 0.0364` | `1/55 = 0.0182` | `-0.0363` | `-0.0182` |

v3f の topline 改善は、**`dominant_structured_safe` と `dominant_structured_abstract` の二枚看板**が牽引している。これは origin deep analysis の「structured が穴」という診断に対する、かなり直接的な改善と言ってよい。

一方で `supported_not_structured` は悪化し、`rare_byte_transform` も 1 問落としている。したがって v3f は **全 binary family を均一に改善したのではなく、structured formula 系を中心に再配分した run** と読むべきである。

### 3.2 exposure band

| exposure band | origin | v2 | v3f | delta v3f-origin | delta v3f-v2 |
| --- | ---: | ---: | ---: | ---: | ---: |
| `dominant` | `54/210 = 0.2571` | `55/210 = 0.2619` | `81/210 = 0.3857` | `+0.1286` | `+0.1238` |
| `supported` | `98/225 = 0.4356` | `105/225 = 0.4667` | `111/225 = 0.4933` | `+0.0577` | `+0.0266` |
| `underrepresented` | `25/110 = 0.2273` | `30/110 = 0.2727` | `32/110 = 0.2909` | `+0.0636` | `+0.0182` |
| `rare` | `13/18 = 0.7222` | `14/18 = 0.7778` | `14/18 = 0.7778` | `+0.0556` | `+0.0000` |

もっとも重要なのは `dominant` の大幅改善で、specialized set の中心難所に効いている。

## 4. selection tier で見る改善源

| selection tier | origin | v2 | v3f | delta v3f-origin | delta v3f-v2 |
| --- | ---: | ---: | ---: | ---: | ---: |
| `verified_trace_ready` | `143/373 = 0.3834` | `151/373 = 0.4048` | `180/373 = 0.4826` | `+0.0992` | `+0.0778` |
| `answer_only_keep` | `43/150 = 0.2867` | `50/150 = 0.3333` | `52/150 = 0.3467` | `+0.0600` | `+0.0134` |
| `manual_audit_priority` | `4/40 = 0.1000` | `3/40 = 0.0750` | `6/40 = 0.1500` | `+0.0500` | `+0.0750` |

今回の gain の主成分は **`verified_trace_ready` の改善**で、これは学習データ変更の意図と整合する。v2 では `verified` の伸びが限定的だったのに対し、v3f ではこの層が明確に押し上がっている。

## 5. format / extraction の挙動変化

| metric | origin | v2 | v3f |
| --- | ---: | ---: | ---: |
| `contains_so_rule_rate` | `0.1510` | `0.2078` | `0.0000` |
| `contains_constraints_rate` | `0.0000` | `0.0018` | `0.0000` |
| `contains_boxed_literal_rate` | `0.8064` | `0.8206` | `1.0000` |
| `gold_anywhere_rate` | `0.5222` | `0.5542` | `0.4227` |
| `last_bit8_exact_rate` | `0.3410` | `0.3659` | `0.4227` |
| `mean_raw_output_chars` | `12138.7` | `12000.9` | `258.6` |
| `mean_bit_fragment_count` | `72.85` | `77.08` | `1.0` |

この変化はかなり極端で、v3f は specialized benchmark 上で **長い推論文をほぼ捨て、短い boxed answer に大きく寄った**ことを示している。

重要な読み方は次の通り。

1. `contains_boxed_literal_rate = 1.0` なので、README 前提の boxed-first 抽出に最適化された形になっている。
2. `gold_anywhere_rate = last_bit8_exact_rate = accuracy` なので、v3f は「どこか途中に正解断片が見えるが最後に崩す」タイプをかなり減らし、**最後に出した 8-bit そのものが勝敗を決める** run に変わっている。
3. `contains_so_rule_rate` や `contains_constraints_rate` は 0 に落ちており、v2 のような synthetic trace phrasing の模倣ではなく、**短く commit する回答様式**へ移ったと見るのが自然である。

この点は specialized 改善には効いているが、通常 60 問 binary watch の `29/60 -> 27/60` 退行を見ると、**短文化だけで全 binary slice を安定化できたわけではない**。

## 6. phase0 local320 でなぜ横ばいなのか

phase0 local320 では、

- binary hard set: `-2`
- symbol watch set: `+2`
- general stable set: `0`

となり、結果として overall が同値の `249/320` に留まった。

binary 60 問 summary の比較では、

- origin: `boxed_extraction_success_rate = 0.8333`, `format_failure_rate = 0.1667`, `format_ok_content_wrong_rate = 0.44`
- v3f: `boxed_extraction_success_rate = 1.0000`, `format_failure_rate = 0.0000`, `format_ok_content_wrong_rate = 0.55`

である。つまり v3f は **format failure を完全に消した代わりに、中身違いが増えた**。

specialized 563 問ではその trade-off を上回る内容改善が出たが、通常 60 問では **format 改善分より content miss の増加が重かった**ため、`27/60` に落ちたと読むのが妥当である。

## 7. 総合評価

今回の `train_split_with_cot_v3f_safe_plus_notformula.csv` 学習版は、origin deep analysis が最大ボトルネックと見ていた **structured binary** に対して、v2 よりも一段強く効いた。

特に specialized では、

- `binary_structured_byte_formula`
- `dominant_structured_safe`
- `verified_trace_ready`
- `dominant` exposure

の改善が大きく、**binary bias specialized benchmark 用の強化としては明確に成功**している。

ただし同時に、

- `supported_not_structured` は悪化
- `rare_byte_transform` は 1 問退行
- 通常 60 問 binary hard set は `29/60 -> 27/60`
- phase0 overall は `249/320` のまま

でもある。

したがって今回の v3f は、

1. **specialized binary 強化としては採用価値が高い**
2. **origin/v2 と比べて structured gap を埋める方向には実際に前進した**
3. **一方で broad binary robustness を完全には維持できていない**

というのが最終評価になる。

## 8. 次の一手

この比較から優先度が高いのは次の 3 点である。

1. **v3f の structured 改善を残したまま、`supported_not_structured` と binary60 の content miss を戻す補正を入れること**
2. **`binary_structured_byte_not_formula` を別 teacher / 別 augmentation で追加補強すること**
3. **specialized で効いた短 boxed commit を維持しつつ、通常 binary watch での過度な短文化による誤答増を抑えること**

今回の結果だけを比較評価するなら、`train_split_with_cot_v3f_safe_plus_notformula.csv` は **origin より明確に強く、v2 よりもさらに一段前進した specialized binary 改善版**である。ただし **「binary 全体の安定版」に達したとはまだ言えない**。