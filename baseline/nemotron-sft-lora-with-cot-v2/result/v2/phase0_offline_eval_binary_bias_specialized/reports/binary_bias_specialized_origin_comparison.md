# `train_split_with_cot_v2.csv` 学習版 binary bias specialized 比較レポート

## 対象と前提

- 変更前比較元:
  - `baseline/nemotron-sft-lora-with-cot-v2/result/origin/phase0_offline_eval_binary_bias_specialized/reports/binary_bias_specialized_deep_analysis.md`
  - `baseline/nemotron-sft-lora-with-cot-v2/result/origin/phase0_offline_eval_binary_bias_specialized/reports/binary_bias_specialized_eval_summary.md`
- 変更後比較対象:
  - `baseline/nemotron-sft-lora-with-cot-v2/result/v2/phase0_offline_eval_binary_bias_specialized/reports/binary_bias_specialized_eval_summary.md`
  - `baseline/nemotron-sft-lora-with-cot-v2/result/v2/phase0_offline_eval_binary_bias_specialized/reports/binary_bias_specialized_manifest.md`
  - 両 run の `artifacts/binary_bias_specialized_eval_row_level.csv`
- 学習方針:
  - `baseline/nemotron-sft-lora-with-cot-v2/TRAIN_SPLIT_WITH_COT_V2_STRATEGY.md`

`README.md` の Evaluation では **Accuracy** が採用され、最終解答は `\boxed{}` 優先で抽出される。binary は exact string 判定なので、この比較でも **boxed で閉じる能力**と**box の中身を正しく 8-bit で出す能力**を分けて見る必要がある。

今回の `train_split_with_cot_v2.csv` 方針は、既存 v2 の boxing を壊さず、unused `verified_trace_ready` の `bit_structured_byte_formula` 系 414 行を追加して hardest structured binary を補強する、という保守的 augmentation だった。

## 結論

`train_split_with_cot_v2.csv` 学習版の specialized score は **`204/563 = 0.3623`** で、origin の **`190/563 = 0.3375`** から **`+14` 問 / `+0.0248`** 改善した。  
ただし改善の主因は、strategy が主ターゲットに置いた **hardest verified structured binary の明確な改善ではなく**、`bit_other`、`bit_permutation_inversion`、`no_solver_answer_only`、`supported_affine_xor` など周辺 bucket の積み上げだった。

要点は次の 4 つ。

1. **README 前提で重要な boxing は壊れていないどころか少し改善した**  
   `boxed_non_empty` は `452 -> 462` 行、同 slice の正答率も `0.4204 -> 0.4394`。fallback `last_number` は依然ほぼ死んでおり、boxed primary path 依存という origin 分析の前提は変わらない。
2. **全体改善は出たが、狙い撃ちした verified structured slice は net で伸びていない**  
   `verified_trace_ready && bit_structured_byte_formula` は `35/185 = 0.1892` から `34/185 = 0.1838` へ微減。
3. **structured の中でも抽象系は少し改善、safe / not-formula は悪化**  
   `binary_structured_byte_formula_abstract` は `16/73 -> 18/73`、一方で `binary_structured_byte_formula` は `18/87 -> 16/87`、`binary_structured_byte_not_formula` は `1/25 -> 0/25`。
4. **strategy の「boxing を守る」は達成、「hardest structured verified を押し上げる」は未達**  
   今回の v2 は方向性としては安全だが、specialized benchmark 上では狙ったボトルネックへの効きがまだ弱い。

## 1. Topline 差分

| metric | origin | v2 | delta |
| --- | ---: | ---: | ---: |
| overall accuracy | `190/563 = 0.3375` | `204/563 = 0.3623` | `+0.0248` |
| contains_so_rule_rate | `0.1510` | `0.2078` | `+0.0568` |
| contains_constraints_rate | `0.0000` | `0.0018` | `+0.0018` |
| contains_boxed_literal_rate | `0.8064` | `0.8206` | `+0.0142` |
| gold_anywhere_rate | `0.5222` | `0.5542` | `+0.0320` |
| last_bit8_exact_rate | `0.3410` | `0.3659` | `+0.0249` |
| mean_raw_output_chars | `12138.7` | `12000.9` | `-137.8` |
| mean_bit_fragment_count | `72.85` | `77.08` | `+4.23` |

読み方:

- `contains_so_rule_rate` の上昇から、strategy で足した short exact-trace の文体が一部 transfer した兆候はある。
- ただし `starts_check_examples_rate` は両者とも `0.0` で、strategy の teacher 文頭がそのまま強く定着したとは言いにくい。
- `gold_anywhere_rate` と `last_bit8_exact_rate` がともに改善しており、**中身の候補生成自体は少し良くなった**。

## 2. origin 深掘り分析の仮説と、v2 実測の照合

origin 側 deep analysis と `TRAIN_SPLIT_WITH_COT_V2_STRATEGY.md` は、実質的に次の 4 仮説を置いていた。

| 仮説 | origin / strategy の根拠 | v2 実測 | 判定 |
| --- | --- | --- | --- |
| boxing を壊してはいけない | origin では `last_number 0/109` で fallback 全滅。README 的にも boxed first が最重要。 | `boxed_non_empty 452 -> 462`、同 slice 正答 `190 -> 203`、`last_number` は `0/109 -> 1/101` | **達成** |
| 追加すべきは structured verified binary | strategy は unused `verified_trace_ready` の `bit_structured_byte_formula` 414 行追加に集中。 | `verified_trace_ready && bit_structured_byte_formula` は `35/185 -> 34/185` | **未達** |
| answer-only / manual を先に増やすべきではない | origin では `answer_only 0.2867`, `manual 0.1000` と弱かった。 | `answer_only_keep` は `43/150 -> 50/150` と改善、`manual` は `4/40 -> 3/40` と悪化 | **混合** |
| structured induction を伸ばしつつ v2 の broad strength を維持する | strategy は non-binary 分布を触らず、binary hardest slice のみ追加。 | 全体は改善したが、純粋な hardest structured verified は伸びず、別 bucket の改善で稼いだ | **部分達成** |

この比較から言えるのは、**strategy の安全設計は正しかったが、specialized benchmark の主ボトルネックをまだ十分には動かせていない**ということ。

## 3. どこで伸びたか

### 3.1 selection tier

| selection tier | origin | v2 | delta |
| --- | ---: | ---: | ---: |
| `verified_trace_ready` | `143/373 = 0.3834` | `151/373 = 0.4048` | `+8` |
| `answer_only_keep` | `43/150 = 0.2867` | `50/150 = 0.3333` | `+7` |
| `manual_audit_priority` | `4/40 = 0.1000` | `3/40 = 0.0750` | `-1` |

`verified_trace_ready` が改善している点自体は strategy と整合する。  
ただし改善幅のかなりの部分が `bit_structured_byte_formula` 以外から来ているため、「verified が伸びた = 狙った structured verified が伸びた」とは読めない。

### 3.2 template subtype

| template subtype | origin | v2 | delta |
| --- | ---: | ---: | ---: |
| `bit_other` | `74/218 = 0.3394` | `81/218 = 0.3716` | `+7` |
| `bit_permutation_inversion` | `50/62 = 0.8065` | `54/62 = 0.8710` | `+4` |
| `bit_structured_byte_formula` | `66/283 = 0.2332` | `69/283 = 0.2438` | `+3` |

topline `+14` のうち、`+11` は `bit_other` と `bit_permutation_inversion` が占めている。  
strategy の主ターゲットだった `bit_structured_byte_formula` 全体も一応 `+3` だが、後述のとおり hardest verified に限ると伸びていない。

### 3.3 focus bucket

| focus bucket | origin | v2 | delta |
| --- | ---: | ---: | ---: |
| `no_solver_answer_only` | `21/70 = 0.3000` | `27/70 = 0.3857` | `+6` |
| `supported_affine_xor` | `18/60 = 0.3000` | `23/60 = 0.3833` | `+5` |
| `dominant_structured_abstract` | `19/90 = 0.2111` | `22/90 = 0.2444` | `+3` |
| `supported_bijection` | `45/50 = 0.9000` | `47/50 = 0.9400` | `+2` |
| `boolean_family` | `32/60 = 0.5333` | `33/60 = 0.5500` | `+1` |
| `rare_perm_independent` | `2/7 = 0.2857` | `3/7 = 0.4286` | `+1` |
| `dominant_structured_safe` | `35/120 = 0.2917` | `33/120 = 0.2750` | `-2` |
| `supported_not_structured` | `3/55 = 0.0545` | `2/55 = 0.0364` | `-1` |
| `no_solver_manual` | `4/40 = 0.1000` | `3/40 = 0.0750` | `-1` |

origin deep analysis が最大の穴として挙げていた `dominant_structured_safe` / `supported_not_structured` は、今回むしろ悪化している。  
一方で `dominant_structured_abstract` は改善しており、structured の中でも **abstract 側だけは前進、safe / not-formula 側はまだ不安定**という分解になる。

## 4. solver family で見ると何が起きたか

| teacher solver | origin | v2 | delta |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | `18/60 = 0.3000` | `23/60 = 0.3833` | `+5` |
| `binary_bit_permutation_bijection` | `45/50 = 0.9000` | `47/50 = 0.9400` | `+2` |
| `binary_bit_permutation_independent` | `2/7 = 0.2857` | `3/7 = 0.4286` | `+1` |
| `binary_two_bit_boolean` | `22/46 = 0.4783` | `23/46 = 0.5000` | `+1` |
| `binary_three_bit_boolean` | `10/14 = 0.7143` | `10/14 = 0.7143` | `0` |
| `binary_byte_transform` | `11/11 = 1.0000` | `11/11 = 1.0000` | `0` |
| `binary_structured_byte_formula_abstract` | `16/73 = 0.2192` | `18/73 = 0.2466` | `+2` |
| `binary_structured_byte_formula` | `18/87 = 0.2069` | `16/87 = 0.1839` | `-2` |
| `binary_structured_byte_not_formula` | `1/25 = 0.0400` | `0/25 = 0.0000` | `-1` |
| blank solver tag | `47/190 = 0.2474` | `53/190 = 0.2789` | `+6` |

strategy の本命だった structured 系だけを見ると、

- `abstract` は改善
- `safe formula` は悪化
- `not_formula` は全滅

で、**structured induction 問題はまだ解決していない**。  
むしろ今回の gain は `affine_xor` や blank solver tag 側にも大きく出ており、追加データが binary reasoning 全体の局所的な安定化には寄与したが、狙った hardest structured を直接押し上げるほどではなかったと読める。

## 5. strategy の主ターゲット slice だけを切り出すとどうか

`TRAIN_SPLIT_WITH_COT_V2_STRATEGY.md` の追加 414 行は、unused `verified_trace_ready` の structured binary に集中していた。  
そこで specialized benchmark 側も **`selection_tier = verified_trace_ready` かつ `template_subtype = bit_structured_byte_formula`** に限定して見る。

| slice | origin | v2 | delta |
| --- | ---: | ---: | ---: |
| verified + structured 全体 | `35/185 = 0.1892` | `34/185 = 0.1838` | `-1` |
| `binary_structured_byte_formula` | `18/87 = 0.2069` | `16/87 = 0.1839` | `-2` |
| `binary_structured_byte_formula_abstract` | `16/73 = 0.2192` | `18/73 = 0.2466` | `+2` |
| `binary_structured_byte_not_formula` | `1/25 = 0.0400` | `0/25 = 0.0000` | `-1` |

この slice では **29 行が正誤反転**したが、net は `-1`。  
特に `dominant_structured_safe` は **v2-only correct 17 行 / origin-only correct 19 行** で、改善と悪化がほぼ相殺された。

つまり、今回の追加データは

- structured abstract には多少効いた
- safe structured と not-formula にはまだ十分効いていない
- targeted slice 全体としては不安定で、再現的な押し上げには至っていない

という結果だった。

## 6. README 観点での format / extraction 評価

origin deep analysis が強調していた「format だけではなく content が足りない」という見立ては、v2 でもほぼそのまま成立する。

| fallback | origin | v2 | delta |
| --- | ---: | ---: | ---: |
| `boxed_non_empty` | `190/452 = 0.4204` | `203/462 = 0.4394` | `+13 correct` |
| `last_number` | `0/109 = 0.0000` | `1/101 = 0.0099` | `+1 correct` |

ここから分かること:

1. **依然として primary path は boxed**  
   README 前提どおり、fallback はほぼ戦力になっていない。
2. **format failure は少し減った**  
   boxed 到達率が上がり、`last_number` 落ちが `109 -> 101` に減った。
3. **しかし main bottleneck はやはり box の中身**  
   `203` 正解まで増えても、`boxed_non_empty` は `462` 行あるので、依然として半分以上は content miss。

## 7. 総合評価

今回の `train_split_with_cot_v2.csv` 学習版は、origin deep analysis が警戒していた **boxing 崩壊**を起こさずに specialized accuracy を **`0.3375 -> 0.3623`** まで押し上げた。  
この点で、strategy の「保守的 augmentation」という設計思想自体は妥当だった。

ただし、origin deep analysis と strategy が最重要 bottleneck と見ていた **hardest verified structured binary** に関しては、

- `verified + structured` 全体では微減
- `safe formula` は悪化
- `not_formula` は改善せず
- `abstract` だけが小幅改善

という結果で、**本命仮説はまだ検証成功とは言えない**。

この specialized benchmark だけを見るなら、今回の v2 は

1. **boxed-first 評価に対して安全**
2. **overall は改善**
3. **しかし hardest structured verified の攻略にはまだ届いていない**

という評価になる。

## 8. 次の一手

この比較から、次に優先すべきことは明確。

1. **`binary_structured_byte_formula` safe 側の内容誤りを直接潰す**  
   今回は safe 側が `-2` で、targeted slice の net 改善を打ち消した。
2. **`binary_structured_byte_not_formula` 用の teacher を別枠で強化する**  
   `1/25 -> 0/25` は、現行 short exact-trace だけでは not-formula を拾えていないことを示す。
3. **boxing 維持は引き続き必須**  
   README 前提では fallback に逃げられないので、今回の boxed 改善を壊す変更は避けるべき。

したがって、origin deep analysis の結論は一部更新が必要だが、根本は維持される。  
つまり **「structured verified を増やす」方向自体は正しいが、今回の 414 行 augmentation とその teacher 形式だけでは hardest slice を押し切れなかった**、というのがこの比較の最終結論である。
