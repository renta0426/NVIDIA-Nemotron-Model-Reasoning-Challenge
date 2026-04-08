# Proof-First Solver Factory Routing Plan に対する v3f 実験フィードバック

## 1. 対象

- plan:
  - `cuda-train-data-analysis-v1/proof_first_solver_factory_routing/plan.md`
- route-aware delta draft:
  - `cuda-train-data-analysis-v1/proof_first_solver_factory_routing/artifacts/binary_route_aware_delta.csv`
- 比較参照:
  - `README.md`
  - `baseline/nemotron-sft-lora-with-cot-v2/result/origin/reports/phase0_eval_summary.md`
  - `baseline/nemotron-sft-lora-with-cot-v2/result/origin/reports/binary_hard_set_summary.md`
  - `baseline/nemotron-sft-lora-with-cot-v2/result/origin/phase0_offline_eval_binary_bias_specialized/reports/binary_bias_specialized_deep_analysis.md`
  - `baseline/nemotron-sft-lora-with-cot-v2/result/v2/phase0_offline_eval_binary_bias_specialized/reports/binary_bias_specialized_verified_structured_text_shift_analysis.md`
  - `baseline/nemotron-sft-lora-with-cot-v2/result/v3f/phase0_offline_eval/reports/phase0_eval_summary.md`
  - `baseline/nemotron-sft-lora-with-cot-v2/result/v3f/phase0_offline_eval/reports/binary_hard_set_summary.md`
  - `baseline/nemotron-sft-lora-with-cot-v2/result/v3f/phase0_offline_eval_binary_bias_specialized/reports/binary_bias_specialized_origin_v2_comparison.md`

本メモの目的は、`Proof-First Solver Factory Routing` の発想を **今回の v3f 実験結果に照らしてどう評価するか** を明確にすることである。

## 2. 結論

この plan は、**方向性としてはかなり正しい**。特に次の 4 点は、v3f 実験結果によって強く支持された。

1. **replacement ではなく augmentation で入れるべき**
2. **最優先で守るべきは boxed close である**
3. **hard family を binary と symbol に限定して深く触る設計は正しい**
4. **structured binary と bit_other を 2 正面で扱う設計は正しい**

一方で、**現時点の route-aware delta をそのまま mainline 学習へ入れるのは危険**でもある。

理由は 3 つある。

1. `binary_route_aware_delta.csv` のうち `80/197` 行は `coarse + route_closure_only` で、しかも文面がほぼ同型の generic closure-only だから、**proof-first というより boxed short-answer bias の補助データに近い**
2. v3f 実験では、boxed は改善したが binary60 は `29/60 -> 27/60` に落ち、**format ではなく content miss が増える副作用**が見えた
3. v2 text-shift 分析では、**teacher phrase の直接 transfer はほぼ起きず**、効いたのは phrase そのものではなく short closure / rule commitment の方だった

したがって、plan 自体は採用価値が高いが、実装は次のように読むべきである。

- **plan は採用**
- **ただし current delta は mainline 投入前に再設計が必要**
- **特に coarse route_closure_only を主役にしてはいけない**

## 3. v3f 実験がこの plan を支持する点

### 3.1 boxed-first を守る設計は正しい

README.md の評価契約は boxed 抽出優先であり、plan もここを最優先条件としている。今回の v3f はこの判断を強く支持した。

観測された事実は次の通り。

| metric | origin | v3f |
| --- | ---: | ---: |
| specialized `contains_boxed_literal_rate` | `0.8064` | `1.0000` |
| binary60 `boxed_extraction_success_rate` | `0.8333` | `1.0000` |
| binary60 `format_failure_rate` | `0.1667` | `0.0000` |

このため plan の

1. boxed final answer を絶対に壊さない
2. binary boxed extraction success を v2 未満へ落とさない

という不変条件は妥当である。むしろ、**ここを軽く見る案は捨ててよい**。

### 3.2 hard family に限定して route-aware を入れる方針は正しい

v3f の実験結果では、easy family はほぼ不変だった一方、差が出たのは hard family だった。

| family / benchmark | origin | v3f |
| --- | ---: | ---: |
| overall local320 | `249/320 = 0.7781` | `249/320 = 0.7781` |
| binary hard 60 | `29/60 = 0.4833` | `27/60 = 0.4500` |
| symbol watch 60 | `22/60 = 0.3667` | `24/60 = 0.4000` |
| text 50 | `49/50 = 0.9800` | `49/50 = 0.9800` |
| unit 50 | `49/50 = 0.9800` | `49/50 = 0.9800` |

このため、plan が easy family 全面改修ではなく、**binary と symbol に route-aware 改善を集中する**読みになっている点は正しい。

### 3.3 binary を structured と bit_other の 2 正面で扱う設計は正しい

plan の重要な洞察は、binary を structured formula だけに寄せすぎないことだった。これは v3f 実験でそのまま裏づけられた。

v3f は specialized 563 問では structured 改善に成功したが、public 60-row 側では `bit_other` が落ちた。

| slice | origin | v3f |
| --- | ---: | ---: |
| specialized overall | `190/563 = 0.3375` | `238/563 = 0.4227` |
| `binary_structured_byte_formula` | `18/87 = 0.2069` | `34/87 = 0.3908` |
| `dominant_structured_safe` | `35/120 = 0.2917` | `53/120 = 0.4417` |
| binary60 `bit_other` | `24/46 = 0.5217` | `22/46 = 0.4783` |

つまり、**structured の深さ改善だけでは public/test 分布全体に勝ち切れない**。plan が

1. structured verified を厚くする深さの改善
2. bit_other exact / consensus / answer-only を増やす幅の改善

を両立させようとしているのは、今回の実験から見ても筋が良い。

### 3.4 answer-only rescue を lane 分離する設計は正しい

v3f では `verified_trace_ready` の gain が主成分だったが、`answer_only_keep` も改善している。

| tier | origin | v3f |
| --- | ---: | ---: |
| `verified_trace_ready` | `143/373 = 0.3834` | `180/373 = 0.4826` |
| `answer_only_keep` | `43/150 = 0.2867` | `52/150 = 0.3467` |

この点から、plan の

- verified は route plus executable trace
- answer_only は route_closure_only / route_query_commit
- manual は raw trace 化しない

という lane 分離自体は合理的である。

## 4. v3f 実験がこの plan に与える警告

### 4.1 boxed を守るだけでは勝てない

今回の v3f は boxed を強く改善したが、binary60 は逆に落ちた。原因は boxed 崩れではなく **content miss** の増加である。

| metric | origin | v3f |
| --- | ---: | ---: |
| binary60 overall | `29/60 = 0.4833` | `27/60 = 0.4500` |
| binary60 `format_failure_rate` | `0.1667` | `0.0000` |
| binary60 `format_ok_content_wrong_rate` | `0.44` | `0.55` |

これは plan に対して次の警告を与える。

> route_closure_only を増やしすぎると、boxed は守れても content error を増やす危険がある。

特に binary では、**route token と closure 契約だけでは solver lock にならない**。

### 4.2 teacher phrase の直接 transfer を期待してはいけない

v2 の text-shift 分析では、追加 teacher の `Check examples:` や `So the verified rule is` はほぼ転写されなかった。一方で、出力全体は変化していた。

ここから分かることは明確である。

1. route token や証拠 phrase は、書けばそのまま真似されるとは限らない
2. 効くのは phrase 自体というより、**その phrase が担っている solver lock の情報量**である
3. plan の真価は route token の存在そのものではなく、**short executable trace の中身**にある

したがって、この plan を進める場合も、route phrase の見た目を目的化してはいけない。

### 4.3 proof-first なのに current coarse delta は prove していない

`binary_route_aware_delta.csv` の実体を集計すると次の通りだった。

| field | value |
| --- | ---: |
| rows | `197` |
| `route_granularity = exact` | `117` |
| `route_granularity = coarse` | `80` |
| `assistant_style = route_trace_full` | `106` |
| `assistant_style = route_trace_sanitized` | `11` |
| `assistant_style = route_closure_only` | `80` |
| `source_selection_tier = verified_trace_ready` | `117` |
| `source_selection_tier = answer_only_keep` | `80` |
| `template_subtype = bit_other` | `132` |
| `template_subtype = bit_structured_byte_formula` | `33` |
| `template_subtype = bit_permutation_inversion` | `32` |

この分布自体は悪くない。むしろ良い点もある。

1. **exact-route verified が 117 行ある**
2. **bit_other 132 行で幅改善を見ている**
3. **affine_xor / bijection / two_bit_boolean など current blind spot 以外にも route を広げている**

しかし attached CSV の coarse 80 行は、本文がほぼすべて次の骨格で固定されている。

1. `Route: bit_manipulation`
2. `Route granularity: coarse`
3. `Use the same hidden bit rule that is consistent with the given examples.`
4. `Apply it to the query byte ...`
5. `Constraints: exact_8bit, leading_zeros, box_only_final.`

これは **proof-first というより route_closure_only** であり、plan の中核だった

- family lock
- short evidence
- executable rule

が coarse lane では落ちている。

つまり current delta は、plan の思想そのものではなく、**その一部だけを弱い形で実装した暫定版**とみなすべきである。

### 4.4 exact route が無い coarse lane を主役にしてはいけない

今回の v3f 実験から見ると、coarse lane を厚くすると次の危険がある。

1. boxed は改善する
2. 短文化も進む
3. しかし exact solver lock が無いので content miss が残る

これは v3f で観測された

- specialized は伸びる
- binary60 では format_ok_content_wrong が増える

という形とかなり整合する。

したがって plan を実装する場合、初期 mainline は

1. exact-route verified rows を主役
2. coarse-route closure-only は低比率補助
3. coarse lane は ablation で有効性が出るまで主役化しない

にすべきである。

## 5. current binary_route_aware_delta.csv をどう見るか

### 5.1 良い点

current delta の良い点は次の通り。

1. **plan の「width」をちゃんと見ている**
   `bit_other = 132` 行で、structured だけに寄っていない。
2. **verified と answer-only を lane 分離している**
   `117` verified exact-route と `80` answer-only coarse-route に分かれている。
3. **solver family の canonical 化が進んでいる**
   `binary_affine_xor`、`binary_bit_permutation_bijection`、`binary_two_bit_boolean` など exact route が具体化されている。

これは plan の骨格にかなり忠実であり、**発想としては mainline 候補**である。

### 5.2 そのままでは危ない点

ただし mainline 学習へそのまま入れる前に、少なくとも次を直すべきである。

1. **coarse answer-only の generic repetition が強すぎる**
   80 行ほぼ同型の `Use the same hidden bit rule...` は、solver lock として弱い。
2. **proof-first の証拠が coarse lane に無い**
   `Check ex1/ex2` に相当する evidence が無いので、route だけで中身を担保できない。
3. **`bit_structured_byte_not_formula` の exact route が見えない**
   v3f の最大未解決点の一つであり、ここを coarse lane で済ませるのは弱い。
4. **abstract drift の修正が plan へまだ反映されていない**
   v2 の監査では abstract 110 行が最大 drift 源だった。plan 側もここを explicit priority に上げるべき。

## 6. この plan を今どう改訂して進めるべきか

### 6.1 採用すべき core

この plan の core はそのまま採用してよい。

1. augmentation-first
2. boxed-preservation-first
3. binary は structured と bit_other の 2 正面
4. symbol は numeric と glyph を分離
5. verified / answer-only / manual を lane 分離

### 6.2 今すぐ直すべき点

plan を実験結果に合わせるなら、次の 5 点を本文に追加・強調すべきである。

1. **route_closure_only は補助 lane であり主役ではない**
2. **exact-route verified を delta の主成分にする**
3. **`binary_structured_byte_not_formula` は explicit priority として別建てする**
4. **abstract 110 行 cleanup を binary mainline の先頭タスクへ上げる**
5. **2-box 的 rule closure を維持し、single short boxed answer への過剰 collapse を避ける**

### 6.3 推奨する実行順

今回の実験結果を踏まえると、実行順は次が最も安全である。

1. **Ablation 1: exact-route verified 117 行だけで binary delta を作る**
   まず route token と exact executable trace の純効果を見る。
2. **Ablation 2: coarse answer-only 80 行を低比率で後乗せする**
   ここで初めて closure-only の副作用を見る。
3. **Ablation 3: not-formula exact lane を別追加する**
   current unresolved bottleneck を直接叩く。
4. **Ablation 4: abstract cleanup 版へ差し替える**
   drift correction が効くかを見る。

この順にしないと、route token の効果、exact trace の効果、closure-only の効果が混ざって判別できない。

## 7. 最終評価

今回の v3f 実験から見ると、`Proof-First Solver Factory Routing Plan` は **捨てるべき案ではなく、むしろ次の本命候補である**。

ただし、その評価は

- plan の思想が正しい
- current delta のまま投入してよい

という意味ではない。

正確には次の評価になる。

1. **plan の設計思想はかなり強い**
2. **v3f の結果は boxed-preservation-first と hard-family augmentation を支持する**
3. **しかし current coarse route_closure_only は proof-first の主役には弱い**
4. **mainline へ入れるなら exact-route verified 中心に再構成すべき**

要するに、この plan は **今回の実験によって否定されたのではなく、むしろ「どう実装すれば勝ち筋になるか」が前より具体化された** と考えるのが正しい。

特に重要な更新点を一言で言うと、次の通りである。

> Proof-First Solver Factory Routing は有望だが、勝ち筋は coarse route_closure_only の量ではなく、exact route plus short executable proof の質にある。