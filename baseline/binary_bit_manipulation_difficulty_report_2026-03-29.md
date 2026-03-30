# Binary / bit_manipulation が「解くのも学習させるのも難しい」理由の調査レポート

## 0. 先に結論

`README.md` の評価仕様に従うと、このコンペは **途中の reasoning のそれっぽさ** ではなく **最終 answer の Accuracy** で決まる。しかも提出時は Nemotron-3-Nano-30B + LoRA を `vLLM` で回し、最終 answer は `\boxed{}` を優先抽出し、失敗時は他ヒューリスティックや最後の数値へフォールバックされる。  
この仕様は binary family に特に厳しい。理由は、binary の正解は `00110100` のような **8 桁固定・先頭ゼロあり・文字列 exact match** だからである。`1` や `10` へ縮退した瞬間に即失点になる。`README.md` の Evaluation と Dataset Description では、評価が Accuracy であり、train/test は rule induction 型の transformation 問題であることが明示されている。  
参照: `README.md:31-49`, `README.md:103-116`

結論を一文で言うと、binary は

1. **問題そのものが few-shot の rule induction として難しい**
2. **学習データを安全に trace 教師へ変換しにくい**
3. **評価器が output formatting failure を強く増幅する**

の三重苦である。

---

## 1. README 観点で何が binary を不利にするか

README に基づく前提は次の通り。

- 提出物は Nemotron-3-Nano-30B に LoRA adapter を載せて `vLLM` で推論される
- 各サンプルで最終 answer は `\boxed{}` に入れるよう指示される
- metric は boxed を最優先で抽出し、失敗時は他ヒューリスティックや最後の数値にフォールバックする
- 正誤は exact string match または数値誤差許容で判定される

binary はこの中で最も boxed/fallback に弱い。  
例えば decimal 系なら `18.99` と `19.00` のような近傍や数値抽出の余地があるが、binary では `00110100` が `1` に崩れた時点で救済余地がほぼない。  
参照: `README.md:31-47`

これは既存の baseline 分析でも明確に出ている。`rule_based_adapter_readme_inference_samples_rule_base-600_analysis.md` では 30 サンプル中 24 正解、失点 6 件のうち 5 件が binary で、`extracted_answer` が `1`, `001`, `-0`, `10` のような短い断片へ崩れている。  
参照: `baseline/cot/rule_based_adapter_readme_inference_samples_rule_base-600_analysis.md:52-67`, `baseline/cot/rule_based_adapter_readme_inference_samples_rule_base-600_analysis.md:71-139`, `baseline/cot/rule_based_adapter_readme_inference_samples_rule_base-600_analysis.md:217-246`

つまり README 準拠の本番評価では、binary は

- まず規則を当てる必要があり
- そのうえで
- **最後の 1 行を 8-bit binary string として壊さず boxed で閉じる**

必要がある。

---

## 2. `cuda-train-data-analysis-v1` が示す「学習しにくさ」

`cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md` の全体結論では、9,500 行全体の中で主要残課題は `bit_manipulation` と `symbol_equation` に集中している。  
そのうち binary は特に重く、family summary は次の通り。

| family | total | verified | answer_only | manual | exclude |
| --- | ---: | ---: | ---: | ---: | ---: |
| bit_manipulation | 1602 | 1004 | 281 | 302 | 15 |

参照: `cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md:55-70`, `cuda-train-data-analysis-v1/artifacts/family_summary_v1.csv:1-7`, `cuda-train-data-analysis-v1/reports/11_latest_snapshot.md:11-18`

ここで重要なのは、binary は 1,602 行のうち **strict に trace-ready と見なせるのが 1,004 行に留まり、281 行は answer-only、302 行は manual** だという点である。  
つまり前回より curated total は大きく伸びたが、それでも **598 行は trace-ready ではない**。  
他 family と比較すると異常さがわかりやすい。

- `roman_numeral`: 1,576 / 1,576 が verified
- `gravity_constant`: 1,597 / 1,597 が verified
- `unit_conversion`: 1,594 / 1,594 が verified
- `text_decryption`: 605 verified だが 971 は clean answer-only まで昇格
- `bit_manipulation`: 1,004 verified, 281 answer-only, **302 manual**

binary は「正解ラベルがある」だけでは trace 教師として安全に使えない行が圧倒的に多い。  
参照: `cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md:57-70`, `cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md:100-120`

これは fine-tuning 観点で痛い。なぜなら README の評価は final answer Accuracy なので、binary では

- 間違った trace を混ぜると harmful
- answer-only 281 行は final answer supervision としては有用だが、trace 教師としては弱い
- しかも exact 8-bit 出力契約まで学ばせる必要がある

からである。

---

## 3. 追加集計で見える binary の難しさ

`train_row_analysis_v1.csv` を基にした追加集計では、binary の性質は次のように整理できる。

### 3.1 行数と example 数

- binary rows: **1,602**
- 各 prompt の example 数分布:
  - 7 examples: 392
  - 8 examples: 407
  - 9 examples: 408
  - 10 examples: 395

つまり「binary だけ examples が少ない」わけではない。7〜10 本がほぼ均等に与えられている。  
それでも unresolved が多いのは、**例数不足より rule space の広さと曖昧さ** が主因であることを示す。

### 3.2 answer の Hamming weight 分布

- 0 ones: 103
- 1 one: 149
- 2 ones: 220
- 3 ones: 264
- 4 ones: 334
- 5 ones: 233
- 6 ones: 189
- 7 ones: 78
- 8 ones: 32

4 ones 付近が最頻で、極端な all-zero / all-one は少数。  
これは「単純な定数出力」ではなく、広い変換族が混在していることを示唆する。

### 3.3 solver family ごとの coverage

`analyze_bit_row(...)` は binary に対して、少なくとも次を順に見る設計になっている。

- bit permutation / inversion
- bijection
- 2-bit boolean
- 3-bit boolean
- affine XOR
- byte transform
- hybrid consensus
- structured byte formula

参照: `cuda-train-data-analysis-v1/code/train_data_analysis_v1.py:1514-1715`

追加集計では各 unique flag は次だった。

- `bit_independent_unique`: 93
- `bit_bijection_unique`: 81
- `bit_boolean2_unique`: 153
- `bit_boolean3_unique`: 35
- `bit_affine_unique`: 377
- `bit_byte_transform_unique`: 52
- `bit_hybrid_consensus_ready`: 45
- `bit_structured_formula_safe`: 317

ここで重要なのは、**最も強い affine でも 377 / 1602 = 23.5% 程度しか一意に説明できない** こと。  
どの solver family も dominant ではなく、binary は多数の micro-family に割れている。

### 3.4 manual 行の内訳

manual 302 行のうち、

- `bit_no_candidate_positions <= 1`: 16 行
- 残り 286 行は 2〜8 bit が未説明
- さらに 49 行は **8 bit 全部に candidate rule が立たない**

一方で `bit_multi_candidate_positions = 0` の manual 行が大多数で、問題は「複数強い仮説が競合する」より **そもそも候補が立たない** ことにある。

これは本質的で、binary の hard part は

- 既存 family の微妙なバリエーション
- shallow local rule では表せない whole-byte / circuit-like 変換
- 例示だけでは query bit の一部が確定しない underdetermination

にある。

---

## 4. 既存分析から見える binary の本当のボトルネック

`FINAL_SUMMARY_REPORT.md` と各 binary report を合わせて読むと、binary は「簡単な rule をまだ見つけていない」だけではない。

### 4.1 easy slice はかなり刈り取られている

binary ではすでに次の recovery が入っている。

- 2-bit / 3-bit boolean
- affine XOR
- byte-level transform
- hybrid consensus
- structured byte formula
- `choose` / `majority` を含む structured-byte 拡張
- second-pass の not-structured formula
- abstract structured-byte family
- narrow support family
- direct prompt reread
- leave-one-out による training-safe 再監査

特に binary recovery は、`x`, `rol/ror`, `shl/shr`, `reverse`, `nibble_swap` を whole-byte source として組み合わせる structured family を広げ、さらに second-pass の not-structured formula まで追加している。  
そのうえで training 用には leave-one-out 再監査を掛け、self-including support や prompt-exact singleton に依存する `145` 行は `verified_trace_ready` ではなく `answer_only_keep` に戻している。  
参照: `cuda-train-data-analysis-v1/reports/11_latest_snapshot.md:28-33`, `cuda-train-data-analysis-v1/artifacts/family_summary_v1.csv:1-7`

それでも binary 最終状態はまだ `1004 verified / 281 answer_only / 302 manual / 15 exclude`。  
つまり「単純 byte transform をもう少し増やせば終わる」ではなく、「curated total は増えても trace-safe teacher はなお限定的」という段階である。

### 4.2 残差の中心は low-gap でも一意化できない cluster

round2 binary cluster map では、代表的な unresolved cluster は

- 7 examples / `bit_no_candidate_positions = 1` / `bit_multi_candidate_positions = 0`: 34 行
- 8 examples / `bit_no_candidate_positions = 1` / `bit_multi_candidate_positions = 0`: 29 行
- 9 examples / `bit_no_candidate_positions = 1` / `bit_multi_candidate_positions = 0`: 17 行

などにまとまる。  
参照: `cuda-train-data-analysis-v1/reports/22_binary_round2_cluster_map.md:1-44`

しかし top cluster / second cluster / third cluster を個別再読しても、いずれも

- unique winning family なし
- affine / boolean / byte-transform の consensus mismatch なし
- safe promotion も safe exclusion もできない

という結論だった。  
参照: `cuda-train-data-analysis-v1/reports/27_binary_top_cluster_hold.md:23-39`, `cuda-train-data-analysis-v1/reports/30_binary_second_cluster_hold.md:23-42`, `cuda-train-data-analysis-v1/reports/37_binary_third_cluster_hold.md:23-44`

要するに unresolved は「あと 1 bit 埋めれば終わり」に見えても、その 1 bit を決める reusable family が存在しない。

### 4.3 tail cluster はさらに悪い

tail cluster では `bit_multi_candidate_positions >= 1` を持つ行が増え、  
`bit_no_candidate_positions = 0` でも competing rules が残る行すらある。  
参照: `cuda-train-data-analysis-v1/reports/38_binary_tail_clusters_hold.md:25-67`

つまり binary の残差は

- top3 の low-gap cluster でさえ解けない
- tail はそれ以上に曖昧

なので、いわゆる long tail というより **構造的難問群** である。

---

## 5. なぜこのモデルにとって「解くのが難しい」のか

### 5.1 local token prediction と task structure が噛み合っていない

binary の正解は 8 文字しかないが、必要なのは short-text generation ではなく **latent byte-function identification** である。  
LLM は token continuation は得意でも、「7〜10 本の I/O 例から 8-bit transformation program を同定する」作業は本質的に program induction であり、free-form CoT と相性がよいとは限らない。

### 5.2 leading zero がある exact string は自然言語モデルに不利

`00110100` のような出力は、

- 自然言語として意味が薄い
- token prior が弱い
- 途中 reasoning の数字断片と混線しやすい
- 最後の extraction heuristic に吸われやすい

ため、正しい内部計算をしていても answer extraction で落ちやすい。  
baseline sample で `1`, `001`, `-0`, `10` へ崩れるのは、この種の failure を実例で示している。  
参照: `baseline/cot/rule_based_adapter_readme_inference_samples_rule_base-600_analysis.md:98-139`

### 5.3 binary は「1 byte 全体」を見る必要がある

簡単な row は permutation / inversion / affine で落ちるが、難しい row は whole-byte formula や circuit-like rule が必要になる。  
実際、structured-byte recovery で大きく回収できたこと自体が、bit-wise local reasoning だけでは足りない証拠である。  
参照: `cuda-train-data-analysis-v1/reports/43_binary_structured_byte_formula_recovery.md:83-95`

### 5.4 few-shot examples が十分でも一意化できない

7〜10 examples は与えられているのに unresolved が多い。  
これは data scarcity ではなく **identifiability scarcity**、つまり「与えられた例だけでは複数の rule family を区別できない」問題である。

---

## 6. なぜ「学習させるのが難しい」のか

### 6.1 高品質 trace 教師が足りない

binary では 1,602 行中 1,004 行が verified trace-ready だが、残る 598 行は trace-ready ではない。  
この 598 行の内訳は `281 answer_only + 302 manual + 15 exclude` であり、特に answer-only の大きな塊は「答え supervision には使えるが trace 教師としては弱い」ことを意味する。  
参照: `cuda-train-data-analysis-v1/artifacts/family_summary_v1.csv:1-7`, `cuda-train-data-analysis-v1/reports/11_latest_snapshot.md:11-18,28-33`

### 6.2 誤った synthetic CoT が harmful になりやすい

analysis 全体の方針も、「安全に reusable な教師へ変換しない方がよい行は manual に留める」というものだった。  
これは binary に限らずだが、binary はその比率が突出して高い。  
参照: `cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md:36-54`, `cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md:113-120`

つまり binary は

- trace 教師としては汚染しやすい
- answer-only では reasoning 学習が弱い
- しかも final formatting を壊さないよう学ばせる必要がある

ので、SFT の教師設計が最も難しい family になっている。

### 6.3 family 内部の support が薄い

structured-byte report では、promote 条件に

1. exact formula が一意
2. gold と一致
3. 全 data で 2 rows 以上 support
4. 0 empirical mismatch

を課している。  
この conservative rule を通る formula が 71 family に分散している時点で、binary が many-small-families だとわかる。  
参照: `cuda-train-data-analysis-v1/reports/43_binary_structured_byte_formula_recovery.md:29-39`, `cuda-train-data-analysis-v1/reports/43_binary_structured_byte_formula_recovery.md:52-82`

支配的テンプレートが少ないため、LoRA が family-level regularity を掴みにくい。

### 6.4 少数の suspect / contradictory rows も混ざる

binary は `exclude_suspect = 15`。  
数は多くないが、exact-match task で誤ラベルを混ぜると最終出力契約を崩しやすい。  
参照: `cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md:470-475`

---

## 7. 私なら binary 問題をどう安定して解くか

### 7.1 コンペ制約を外した「最も安定な」解き方

自由に solver を使えるなら、私は LLM に free-form で直接解かせない。  
次の deterministic solver を第一候補にする。

1. prompt から `(input_byte, output_byte)` の examples と query を厳密 parse
2. rule family を簡単なものから順に総当たり
   - permutation / inversion
   - affine over GF(2)
   - 2-bit / 3-bit boolean
   - byte transforms (`rol`, `ror`, `shl`, `shr`, `reverse`, `nibble_swap`)
   - composed byte formulas (`xor`, `and`, `or`)
3. 一意に決まらない場合は restricted DSL 上で program synthesis
   - 深さ制限付き boolean circuit
   - MDL / simplest-consistent rule 優先
4. それでも複数式が残る場合は
   - query output consensus があるか確認
   - consensus がなければ ambiguous 扱い
5. 出力は **最後の 1 行だけ** `\boxed{xxxxxxxx}` に固定

要するに、binary は「言語生成」より「プログラム同定」の問題として解くべきである。

### 7.2 コンペ制約内でやるなら

本コンペは最終的に LoRA adapter 単体提出なので、外部 solver を本番時に呼べない。  
そのため実戦的には、solver は **教師生成器** として使う。

私なら次の方針を採る。

1. `verified_trace_ready` のみで binary core trace を作る
2. `answer_only_keep` は final answer 契約の補助用に少量混ぜる
3. `manual_audit_priority` は raw のまま trace 化しない
4. binary 専用の短い trace template に統一する
   - 「候補 family」
   - 「query に適用」
   - `Final: \boxed{xxxxxxxx}`
5. format hardening data を別途入れる
   - 先頭ゼロ保持
   - `\boxed{}` のみ
   - boxed の後ろに余計な数値を書かない
6. 可能なら binary family を prompt 内で router 的に強調する

### 7.3 free-form CoT より scratchpad / code-like 中間表現

binary は自然文 CoT より、次のような中間表現の方が安定する。

```text
rule = xor(shl2(x), shr1(x))
query = 11010000
apply(rule, query) = 00110100
Final: \boxed{00110100}
```

この形式なら

- reasoning と computation が分離され
- leading zero が保たれやすく
- extraction failure も減る

---

## 8. 有名 benchmark での類似性と、LLM がどう攻略したか

## 8.1 ARC-AGI

ARC-AGI は demonstration input/output から test output を exact に作る benchmark で、grid 変換版の rule induction と見なせる。  
公式 repo でも ARC は program synthesis benchmark / psychometric intelligence test と位置付けられ、train pairs を見て test output を exact に構成する形式だと説明されている。  
参照: <https://github.com/fchollet/ARC-AGI>

Chollet の原論文でも、ARC は単なる skill ではなく generalization efficiency を測る benchmark として提案されている。  
参照: <https://arxiv.org/abs/1911.01547>

LLM 側の攻略としては、近年は **program synthesis + search** が主流で、SOAR は LLM を evolutionary search に組み込み、hindsight learning で自己改善しつつ ARC-AGI public test の 52% を解いたと報告している。  
参照: <https://proceedings.mlr.press/v267/pourcel25a.html>

### Nemotron binary への示唆

- 例示から規則を読む exact-output task は、free-form CoT 単発より **search / synthesis / verification loop** が効く
- binary も同様に、latent rule を program として扱う方が自然

## 8.2 BIG-Bench Hard (特に Boolean Expressions などの symbolic reasoning)

BIG-Bench Hard は、従来 few-shot では人間平均に届かなかった 23 task をまとめた suite で、logical reasoning や boolean expressions を含む。  
repo と論文では、CoT を入れることで PaLM は 23 task 中 10、Codex は 17 task で人間平均超えまで伸びたとされる。  
参照: <https://github.com/suzgunmirac/BIG-Bench-Hard>, <https://arxiv.org/abs/2210.09261>

### Nemotron binary への示唆

- symbolic exact-match task では、few-shot だけより CoT が効く
- ただし CoT で十分なのは「中間 reasoning を言語で書けば閉じる」範囲まで
- binary の harder slice は、BBH よりさらに program-induction 寄り

## 8.3 SCAN

SCAN は command-to-action の compositional benchmark で、元論文は standard seq2seq が systematic compositionality を必要とする split で大きく失敗すると報告している。  
参照: <https://arxiv.org/abs/1711.00350>

その後 Least-to-Most Prompting は、GPT-3 code-davinci-002 に 14 exemplars だけ与えて SCAN の各 split で 99%+ を達成し、同論文中で CoT の 16% に対し大幅改善と報告した。  
参照: <https://arxiv.org/abs/2205.10625>

### Nemotron binary への示唆

- 難しい compositional task は「一発で rule を当てる」より
- **小さな subproblem に分解し順に解く** 方が安定する

binary なら

- bit-level candidate を出す
- whole-byte family を絞る
- query に適用する

という least-to-most 化が有効である。

---

## 9. 直接参考になる reasoning 手法の論文

### 9.1 Chain-of-Thought

Chain-of-Thought Prompting は arithmetic / commonsense / symbolic reasoning の広範な改善を示した。  
参照: <https://arxiv.org/abs/2201.11903>

**示唆**: binary でも中間 reasoning を出させる価値はあるが、それだけで十分とは限らない。

### 9.2 Self-Consistency

Self-Consistency は diverse reasoning paths を複数サンプルし、一貫した answer を marginalize で選ぶ方法で、複数 benchmark で CoT を改善した。  
参照: <https://arxiv.org/abs/2203.11171>

**示唆**: binary でも複数 reasoning path から answer consensus を取る発想は有効。ただし本コンペ本番は `temperature=0.0` 固定なので、そのままは使いにくい。訓練時の teacher generation では有効。

### 9.3 Scratchpads

Scratchpads は intermediate computation を明示出力させることで multi-step computation を大きく改善した。  
参照: <https://arxiv.org/abs/2112.00114>

**示唆**: binary では自然文長文 CoT より、bit table や byte transform を scratchpad 化した短い中間表現が向く。

### 9.4 PAL / Program of Thoughts

PAL は reasoning の中間表現を Python program にし、計算自体は interpreter に委譲する。  
参照: <https://arxiv.org/abs/2211.10435>

Program of Thoughts も reasoning を program 化し、計算を外部に渡すことで CoT より平均 12% 程度改善したと報告する。  
参照: <https://arxiv.org/abs/2211.12588>

**示唆**: binary はまさに PAL / PoT 向きの課題構造。  
本コンペ本番では外部 interpreter を使えないが、**solver-generated program-like traces を SFT 教師にする** のはかなり相性がよい。

---

## 10. 実務的提案

### 10.1 何をやるべきか

優先度順なら次が妥当。

1. binary の `verified_trace_ready` だけで短い solver-style trace を作る
2. binary 専用 format hardening を強化する
3. `manual_audit_priority` 全体への雑な synthetic CoT を禁止する
4. unresolved top cluster 用に、restricted DSL をもう 1 段広げる
   - low-depth boolean circuit
   - MDL ベース disambiguation
5. binary family の final answer を boxed-only で閉じる学習を別途補強する

### 10.2 やらない方がいいこと

- binary の `manual + answer_only` 598 行へ一括で自然文 CoT を付ける
- boxed の近くに説明文や数値断片を残す
- loss の低下だけで binary 改善を判断する

---

## 11. まとめ

このモデルにとって `data/train.csv` の binary が難しい理由は、単に「binary だから」ではない。

1. **few-shot で latent transformation program を同定する必要がある**
2. **family が many-small-families に分散し、dominant rule がない**
3. **1,602 行中 598 行が safe trace-ready ではなく、特に 281 行は answer-only 止まりで教師強度が弱い**
4. **README 準拠評価が final formatting failure を強く増幅する**

したがって、binary で効くのは「もっと長い自然文 CoT」よりも、

- solver-aware な teacher curation
- short scratchpad / program-like traces
- final `\boxed{xxxxxxxx}` 契約の強化
- 必要なら search / synthesis 的な発想

である。

---

## 12. 参考にした主な repo 内資料

- `README.md`
- `baseline/cot/rule_based_adapter_readme_inference_samples_rule_base-600_analysis.md`
- `cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md`
- `cuda-train-data-analysis-v1/reports/22_binary_round2_cluster_map.md`
- `cuda-train-data-analysis-v1/reports/27_binary_top_cluster_hold.md`
- `cuda-train-data-analysis-v1/reports/30_binary_second_cluster_hold.md`
- `cuda-train-data-analysis-v1/reports/37_binary_third_cluster_hold.md`
- `cuda-train-data-analysis-v1/reports/38_binary_tail_clusters_hold.md`
- `cuda-train-data-analysis-v1/reports/42_binary_hybrid_consensus_recovery.md`
- `cuda-train-data-analysis-v1/reports/43_binary_structured_byte_formula_recovery.md`
- `cuda-train-data-analysis-v1/reports/56_binary_structured_byte_manual_exact_curation.md`
- `cuda-train-data-analysis-v1/code/train_data_analysis_v1.py`
- `cuda-train-data-analysis-v1/artifacts/family_summary_v1.csv`
- `cuda-train-data-analysis-v1/artifacts/train_row_analysis_v1.csv`

## 13. 外部参考

- ARC-AGI repo: <https://github.com/fchollet/ARC-AGI>
- Chollet, *On the Measure of Intelligence*: <https://arxiv.org/abs/1911.01547>
- Pourcel et al., *Self-Improving Language Models for Evolutionary Program Synthesis: A Case Study on ARC-AGI*: <https://proceedings.mlr.press/v267/pourcel25a.html>
- BIG-Bench Hard repo: <https://github.com/suzgunmirac/BIG-Bench-Hard>
- Suzgun et al., *Challenging BIG-Bench Tasks and Whether Chain-of-Thought Can Solve Them*: <https://arxiv.org/abs/2210.09261>
- Lake and Baroni, *Generalization without systematicity: On the compositional skills of sequence-to-sequence recurrent networks*: <https://arxiv.org/abs/1711.00350>
- Zhou et al., *Least-to-Most Prompting Enables Complex Reasoning in Large Language Models*: <https://arxiv.org/abs/2205.10625>
- Wei et al., *Chain-of-Thought Prompting Elicits Reasoning in Large Language Models*: <https://arxiv.org/abs/2201.11903>
- Wang et al., *Self-Consistency Improves Chain of Thought Reasoning in Language Models*: <https://arxiv.org/abs/2203.11171>
- Nye et al., *Show Your Work: Scratchpads for Intermediate Computation with Language Models*: <https://arxiv.org/abs/2112.00114>
- Gao et al., *PAL: Program-Aided Language Models*: <https://arxiv.org/abs/2211.10435>
- Chen et al., *Program of Thoughts Prompting*: <https://arxiv.org/abs/2211.12588>
