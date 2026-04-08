# `train_split_with_cot_v3f_safe_plus_notformula.csv` 学習版の効果・副作用・次戦略

## 対象と前提

- 比較対象:
  - `baseline/nemotron-sft-lora-with-cot-v2/result/origin/reports/phase0_eval_summary.md`
  - `baseline/nemotron-sft-lora-with-cot-v2/result/origin/reports/binary_hard_set_summary.md`
  - `baseline/nemotron-sft-lora-with-cot-v2/result/origin/reports/symbol_watch_set_summary.md`
  - `baseline/nemotron-sft-lora-with-cot-v2/result/origin/phase0_offline_eval_binary_bias_specialized/reports/binary_bias_specialized_deep_analysis.md`
  - `baseline/nemotron-sft-lora-with-cot-v2/result/v2/phase0_offline_eval_binary_bias_specialized/reports/binary_bias_specialized_verified_structured_text_shift_analysis.md`
  - `baseline/nemotron-sft-lora-with-cot-v2/result/v3f/phase0_offline_eval/reports/phase0_eval_summary.md`
  - `baseline/nemotron-sft-lora-with-cot-v2/result/v3f/phase0_offline_eval/reports/binary_hard_set_summary.md`
  - `baseline/nemotron-sft-lora-with-cot-v2/result/v3f/phase0_offline_eval/reports/symbol_watch_set_summary.md`
  - `baseline/nemotron-sft-lora-with-cot-v2/result/v3f/phase0_offline_eval_binary_bias_specialized/reports/binary_bias_specialized_eval_summary.md`
  - `baseline/nemotron-sft-lora-with-cot-v2/result/v3f/phase0_offline_eval_binary_bias_specialized/reports/binary_bias_specialized_origin_v2_comparison.md`
- 学習 notebook:
  - `baseline/nemotron-sft-lora-with-cot-v2/nemotron-sft-lora-with-cot-v2.ipynb`
- 学習データ:
  - `baseline/nemotron-sft-lora-with-cot-v2/artifacts/train_split_with_cot_v3f_safe_plus_notformula.csv`

`README.md` の Evaluation は **Accuracy** で、最終解答は `\boxed{}` 優先抽出、binary は exact string 判定である。したがって今回も、

1. **当初の狙いだった structured binary 改善が実際に出たか**
2. **boxed path に崩れがないか**
3. **他 family を壊していないか**

を中心に見る。

## 結論

v3f は、**当初の狙いだった hardest structured binary の改善には明確に成功した**。specialized 563 問では `190/563 = 0.3375` から `238/563 = 0.4227` へ伸び、特に `binary_structured_byte_formula` と `dominant_structured_safe` が大きく改善している。

ただし副作用もあり、**通常 60 問 binary hard watch は `29/60 -> 27/60` に下がった**。この退行は boxed 崩れではなく、むしろ boxed は強化された一方で **format は正しいが中身が wrong** な誤答が増えたことによる。

Text Encryption を `700 -> 600` に減らした影響については、local320 の text family は origin / v3f ともに `49/50 = 0.9800` で、**少なくとも現在の観測範囲では text 低下の兆候は見えない**。

今回の成果から見える次の大幅改善戦略は、**v3f の safe structured 改善と boxed 安定化を残したまま、`supported_not_structured` と binary60 content miss を回収する二段構え**である。特に v2 の text-shift 分析を踏まえると、次に触るべきは safe/not-formula の phrase 量ではなく、**abstract 110 行の旧 template drift と、not-formula 専用 teacher の再設計**である。

## 1. v3f は当初の狙い通りに効いたか

### 1.1 狙いの中心だった structured binary は改善した

v3f の当初の狙いは、origin / v2 が苦しんでいた **structured binary** の補強だった。この点は specialized 563 問で明確に達成している。

| slice | origin | v2 | v3f | delta v3f-origin | delta v3f-v2 |
| --- | ---: | ---: | ---: | ---: | ---: |
| overall specialized | `190/563 = 0.3375` | `204/563 = 0.3623` | `238/563 = 0.4227` | `+0.0852` | `+0.0604` |
| `binary_structured_byte_formula` | `18/87 = 0.2069` | `16/87 = 0.1839` | `34/87 = 0.3908` | `+0.1839` | `+0.2069` |
| `binary_structured_byte_formula_abstract` | `16/73 = 0.2192` | `18/73 = 0.2466` | `21/73 = 0.2877` | `+0.0685` | `+0.0411` |
| targeted structured verified 全体 | `35/185 = 0.1892` | `34/185 = 0.1838` | `56/185 = 0.3027` | `+0.1135` | `+0.1189` |
| `dominant_structured_safe` | `35/120 = 0.2917` | `33/120 = 0.2750` | `53/120 = 0.4417` | `+0.1500` | `+0.1667` |

このため、**「v3f は狙った slice に効いたのか」という問いに対しては yes** と答えてよい。

### 1.2 `verified_trace_ready` の押し上げも狙いと整合する

| selection tier | origin | v2 | v3f |
| --- | ---: | ---: | ---: |
| `verified_trace_ready` | `143/373 = 0.3834` | `151/373 = 0.4048` | `180/373 = 0.4826` |
| `answer_only_keep` | `43/150 = 0.2867` | `50/150 = 0.3333` | `52/150 = 0.3467` |
| `manual_audit_priority` | `4/40 = 0.1000` | `3/40 = 0.0750` | `6/40 = 0.1500` |

gain の主成分は `verified_trace_ready` にあり、これは v3f の augmentation 方針と素直に噛み合っている。

## 2. 悪化したポイントは何か

### 2.1 通常 60 問 binary hard watch は退行した

| metric | origin | v3f | delta |
| --- | ---: | ---: | ---: |
| binary hard set overall | `29/60 = 0.4833` | `27/60 = 0.4500` | `-0.0333` |
| `bit_other` | `24/46 = 0.5217` | `22/46 = 0.4783` | `-0.0434` |
| `bit_structured_byte_formula` | `5/14 = 0.3571` | `5/14 = 0.3571` | `0.0000` |

特に 60 問 watch では、specialized で大きく伸びた structured gain がそのまま反映されず、**`bit_other` 側の取りこぼし**が見える。

### 2.2 specialized 内でも非ターゲット弱化がある

| focus bucket | origin | v2 | v3f |
| --- | ---: | ---: | ---: |
| `supported_not_structured` | `3/55 = 0.0545` | `2/55 = 0.0364` | `1/55 = 0.0182` |
| `rare_byte_transform` | `11/11 = 1.0000` | `11/11 = 1.0000` | `10/11 = 0.9091` |
| `no_solver_answer_only` | `21/70 = 0.3000` | `27/70 = 0.3857` | `26/70 = 0.3714` |

v3f は **全 binary family を一様に改善した run ではない**。structured safe / abstract を押し上げた一方で、`supported_not_structured` はさらに悪化した。

### 2.3 overall local320 が伸びていない

| benchmark | origin | v3f | delta |
| --- | ---: | ---: | ---: |
| overall | `249/320 = 0.7781` | `249/320 = 0.7781` | `0.0000` |
| general stable | `198/200 = 0.9900` | `198/200 = 0.9900` | `0.0000` |
| binary hard | `29/60 = 0.4833` | `27/60 = 0.4500` | `-0.0333` |
| symbol watch | `22/60 = 0.3667` | `24/60 = 0.4000` | `+0.0333` |

binary 退行を symbol 改善が打ち消しており、**v3f は binary specialized 改善版だが broad local320 改善版ではない**。

## 3. Text Encryption を `700 -> 600` に減らした影響はあるか

### 3.1 まず確認できる事実

現ワークスペースの notebook スナップショットでは、`TYPE_SAMPLES` は次の通りである。

- `Numeral Conversion = 300`
- `Gravitational Constant = 400`
- `Unit Conversion = 700`
- `Text Encryption = 700`
- `Bit Manipulation = 1021`
- `Equation Transformation = 200`

したがって、**現在保存されている notebook ファイル自体は `Text Encryption = 700` であり、600 は確認できない**。もし実行時に 600 へ変更していたなら、その情報は現ファイルには残っていない。

このため、Text 600 の影響評価は次の 2 層で扱うべきである。

1. **観測事実**: 現ファイルと評価 artifact から読めること
2. **仮説評価**: 実行時に本当に 600 だったとしたら何が起きうるか

### 3.2 観測事実としては text 悪化の証拠はない

| family | origin | v3f |
| --- | ---: | ---: |
| `text` | `49/50 = 0.9800` | `49/50 = 0.9800` |
| `unit` | `49/50 = 0.9800` | `49/50 = 0.9800` |
| `gravity` | `50/50 = 1.0000` | `50/50 = 1.0000` |
| `roman` | `50/50 = 1.0000` | `50/50 = 1.0000` |

少なくとも local320 では、Text Encryption を減らしたことに対応するような **text 系の observable regression は見えていない**。

### 3.3 もし本当に 600 だったなら、重み変化はこうなる

sampling 比率だけを見ると、

- origin: total `2907`, bit share `0.2088`, text share `0.2408`
- v3f with text 700: total `3321`, bit share `0.3074`, text share `0.2108`
- v3f with text 600: total `3221`, bit share `0.3170`, text share `0.1863`

である。

つまり Text を `700 -> 600` に落とすと、**binary 比率はさらに約 `+0.96` pt 上がり、text 比率は約 `-2.45` pt 下がる**。仮に実行時 600 だったなら、v3f の binary 偏重は notebook 現ファイルの 700 設定よりさらに強かったことになる。

### 3.4 実務的な判断

現時点で言えるのは次の通り。

1. **text 低下の観測証拠はない**
2. **ただし 600 vs 700 の純粋なアブレーションではないので、影響ゼロとは断定できない**
3. **現在の優先課題は text ではなく binary60 / supported_not_structured なので、次段の最優先アブレーションではない**

したがって Text 600 は、今の証拠だけなら **大きな悪影響は確認できないが、勝因と断定する材料もない** という扱いが最も妥当である。

## 4. boxed 回答に崩れはないか

### 4.1 boxed 崩れは起きていない。むしろ強化されている

README 前提では boxed path が最重要である。v3f はこの点では悪化ではなく改善している。

| metric | origin | v3f |
| --- | ---: | ---: |
| specialized `contains_boxed_literal_rate` | `0.8064` | `1.0000` |
| binary60 `boxed_extraction_success_rate` | `0.8333` | `1.0000` |
| binary60 `format_failure_rate` | `0.1667` | `0.0000` |
| binary60 `leading_zero_retention_rate` | `0.8333` | `0.8667` |

したがって **boxed 回答に崩れはないか** という問いには、**no。崩れではなく過剰適応に近い boxed 強化が起きている** と答えるのが正確である。

### 4.2 真の副作用は format ではなく content drift

| metric | origin | v3f | delta |
| --- | ---: | ---: | ---: |
| binary60 overall | `29/60 = 0.4833` | `27/60 = 0.4500` | `-0.0333` |
| binary60 `format_ok_content_wrong_rate` | `0.44` | `0.55` | `+0.11` |
| specialized `last_bit8_exact_rate` | `0.3410` | `0.4227` | `+0.0817` |
| specialized `mean_raw_output_chars` | `12138.7` | `258.6` | `-11880.1` |

この組み合わせが意味するのは、

- **specialized では短く boxed で commit する出力が効いた**
- **binary60 では短く boxed でも中身を外すケースが増えた**

ということ。副作用の本体は **boxed 崩れ** ではなく **内容誤りの増加** である。

### 4.3 v2 の text-shift 分析と合わせた読み

v2 の text-shift 分析では、改善行は **shorter + boxed + closure**、悪化行は **longer + fallback** だった。また 2-box が 1-box より強いことも示されていた。

この文脈で v3f を読むと、

- v3f は boxed そのものは強化した
- ただし **「正しい rule commitment を経た 2-box closure」まで保証していない**
- 結果として binary60 では **短く boxed だが wrong** が増えた

と解釈できる。

## 5. 今回の成果から見えた次の大幅改善戦略

### 5.1 維持すべき資産

次段で壊してはいけないのは次の 3 つである。

1. **specialized 563 問での structured safe 改善**
2. **boxed path の完全安定化**
3. **text / unit / gravity / roman の高スコア維持**

v3f の価値はここにあるので、次の run は「v3f を捨てて別路線」ではなく、**v3f を土台に binary broad robustness を戻す補修**であるべき。

### 5.2 次の大改善で最優先に触るべき箇所

1. **abstract 110 行の phrasing cleanup**
   v2 の synthetic CoT 監査では、safe / not-formula よりも **abstract 110 行に旧 template drift が残る**ことが明示されている。次の cleanup 対象として最優先。
2. **`binary_structured_byte_not_formula` 専用 teacher の再設計**
   v3f でも `1/25` で突破できていない。ここは safe と同型の teacher では足りない。
3. **`supported_not_structured` 回収用の別 supervision**
   v3f の最大の非ターゲット退行点であり、binary60 低下とも整合する。別 bucket として扱うべき。
4. **2-box closure を崩さない content supervision**
   単純 one-box commit を増やすより、rule closure を経て final box に落とす出力を維持する。

### 5.3 次の run 設計

大幅改善を狙うなら、次は次のような二段構えがよい。

#### Stage 1: v3f の穴埋め

- base は v3f を維持
- `abstract` 110 行を model-native phrasing に再生成
- `not_formula` 23 行を専用 teacher に差し替え
- `supported_not_structured` に対する低比率補助データを追加

狙いは、**specialized の優位を維持したまま binary60 の `bit_other` / non-structured 側を戻す**こと。

#### Stage 2: row-level regression repair

- origin-only correct / v3f regressed の binary60 行を抽出
- それに近い teacher family を hard-mine
- boxed は固定しつつ content drift を戻す

狙いは、**boxed はそのままで中身違いだけを削る**こと。

### 5.4 Text Encryption はどう扱うべきか

Text 600 の再検証は優先度中位でよい。理由は、

1. 現状 text family に observable regression がない
2. 今の主要損失は binary 側にある
3. ただし notebook スナップショットと実行条件に食い違いがあるため、再現性確認用には必要

からである。

したがって、次の大改善 run の直前か直後に、**`Text = 700` と `Text = 600` のみを変えた小さな再現 run** を 1 本だけ置くのは有益だが、最優先ではない。

## 6. 最終評価

今回の v3f は、**狙った structured binary の改善には成功した**。この点は specialized 563 問の大幅上昇と、`binary_structured_byte_formula` / `dominant_structured_safe` の改善で十分に裏づけられている。

一方で、悪影響もはっきりしている。

- boxed 崩れはない
- むしろ boxed は強化された
- しかし binary60 では **format は正しいのに中身が wrong** が増えた
- 非ターゲットでは `supported_not_structured` が悪化した

Text Encryption 600 の影響は、現 notebook ファイルでは確認できず、観測範囲では text 低下も見えていない。したがって今の主論点は text ではなく、**v3f が得た structured gain を保ったまま broad binary robustness を取り戻せるか** にある。

次の大幅改善の中心は、**v3f の boxed 安定化を維持しながら、abstract 110 行の cleanup、not-formula 専用 teacher、supported_not_structured 補修を行うこと**である。これが最も自然で、かつ今回の結果から直接つながる次の一手である。