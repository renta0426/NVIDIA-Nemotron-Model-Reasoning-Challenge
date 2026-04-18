# v20-v5 総点検と 0.88 到達戦略 再考メモ

> 目的: v1-v5 の corrective 実験を踏まえ、なぜ 0.88 に届いていないのかを整理し、次に取るべき「大きい」戦略を定義する。
> 根拠の一次資料は `A-Open-ProgressPrizePublication/README.md`、`A-Open-ProgressPrizePublication/データ戦略を理解する.md`、`A-Open-ProgressPrizePublication/学習SFTパイプライン.md`、`cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md`、および各 version results に置く。

## 1. 先に結論

現状の v1-v5 は、**binary frontier と answer surface の両方を同時に押し上げる新しい教師設計**になっていない。
やってきたことの多くは、

- 既存の verified binary をどう再配分するか
- guardrail をどこまで戻すか
- 短縮 trace をどこまで薄くできるか

の調整であり、0.85 から 0.88 へ行くための **新しい programmatic insight** や **新しい teacher architecture** にはまだ踏み込めていない。

今回の総点検からの主判断は次の通り。

1. `v20` の本質は依然として正しい。
   - deterministic CoT
   - bit を主戦場にする
   - boxed-first extraction を壊さない
   - tokenization weakness を補助データで補う

2. ただし `v20` の teacher は一枚岩ではない。
   - easy family では非常に強い
   - binary hard slice では長すぎる / 抽象度が粗い / query-specific closure が弱い
   - symbol / cryptarithm は public evidence 自体が足りない

3. `v1-v5` が証明したのは「微調整の限界」であって、「方針の正しさ」ではない。
   - v1: binary overlay は効く
   - v2: guardrail は局所回復する
   - v3: binary を強くすると surface が壊れる
   - v4: public 向けの最良バランスは作れた
   - v5: local 安定化はできたが binary public edge を失った

4. `baseline/nemotron-sft-lora-with-cot-v2/artifacts/train_split_with_cot.csv` は、**置き換え先としては弱い**。
   ただし、**short / model-native / boxed-friendly な文体 donor** としては有望。

5. `FINAL_SUMMARY_REPORT.md` にはまだ活用余地が大きい。
   ただし、それは「answer_only / manual をそのまま full CoT にする」ことではない。
   必要なのは、tier ごとに役割を分けた **multi-lane teacher design** である。

要するに、次の本命は `v5b` のような延長戦ではなく、

**「deterministic exact teacher」と「model-native short closure teacher」を分離した v6 相当の新設計**

である。

## 2. v20 をどう理解し直すべきか

`A-Open-ProgressPrizePublication/README.md` が言っていることはかなり一貫している。

- 上振れの主因は `bit_manipulation`
- 評価契約は boxed-first extraction
- RL ではなく SFT
- min logprob を見る
- symbol split / concat / spelling は Nemotron の弱点
- より高いスコアには programmatic insight が要る

加えて `A-Open-ProgressPrizePublication/データ戦略を理解する.md` と `A-Open-ProgressPrizePublication/学習SFTパイプライン.md` を合わせて読むと、v20 の強みは次の 2 本立てである。

1. **exact teacher の強さ**
   - numeral / gravity / unit / cipher は deterministic rule が強い
   - bit も solve できる slice には明確な teacher がある

2. **token weakness 対策の補助データ**
   - matching / spelling / concatenation / splitting / lstrip
   - reasoning の難所を task decomposition して別 supervision にしている

つまり v20 は「長い CoT を丸ごと信じる」設計ではない。むしろ

- exact teacher
- token-level weakness repair

の二層構造だった。

ここを忘れて、v1-v5 で overlay の比率だけ調整しても、0.88 に必要な structural gain には届きにくい。

## 3. v1-v5 は何を証明したか

### 3.1 スコア推移

| version | validation | proxy | public leaderboard | 主な意味 |
| --- | ---: | ---: | ---: | --- |
| v20 | `837/950 = 0.8811` | `176/200 = 0.8800` | README: `0.84-0.85` | easy は強いが binary frontier は不足 |
| v1 | `838/950 = 0.8821` | `178/200 = 0.8900` | Git 上未記録 | binary overlay は効いた |
| v2 | `839/950 = 0.8832` | `176/200 = 0.8800` | ユーザー報告 `0.83-0.84` | guardrail は効くが binary を戻した |
| v3_mainline | `801/950 = 0.8432` | `180/200 = 0.9000` | ユーザー報告 `0.84-0.85` | binary は強いが boxed surface 崩壊 |
| v4_mainline | `813/950 = 0.8558` | `179/200 = 0.8950` | ユーザー報告 `0.85 x3, 0.86 x2` | public 向け最良バランス |
| v5a_mainline | `829/950 = 0.8726` | `173/200 = 0.8650` | ユーザー報告 `0.85 x2` | local easy 回復、binary public edge 喪失 |

### 3.2 実験系列から分かること

#### A. binary は確かに最大レバー

`v1` と `v4` は proxy / public を押し上げたが、どちらも主因は binary だった。
一方 `v5a` は numeral / unit を回復したが public は上がらなかった。

これは hidden/public 側が、依然として

- numeral の小回復
- unit の小回復

よりも、**binary frontier の content correctness** を強く見ていることを示す。

#### B. しかし binary を強くするだけでも勝てない

`v3_mainline` は proxy 最高だったが、validation / public は崩れた。
理由は boxed surface の系統崩壊。

つまり必要なのは

- binary content gain
- boxed / terminal answer stability

の両立であって、片方だけでは足りない。

#### C. ここまでは「配分の最適化」であり「新しい解法」ではない

v1-v5 の多くは

- structured を増やす
- guardrail を戻す
- short trace にする
- symbol repair を入れる / 抜く

という再配分だった。

これは局所改善には効くが、0.03 の public gap を埋めるには弱い。

## 4. なぜ 0.88 に届かないのか

### 4.1 本丸の binary hard core が解けていない

validation を 6 run 横断で見ると、**全 run で誤答のままの bit 行が 12 行**ある。

- `000b53cf`
- `0245b9bb`
- `0311b798`
- `048cc279`
- `04d8c3e6`
- `06881e47`
- `0ec17d2e`
- `1126e314`
- `12154247`
- `132ec6ae`
- `16db2c74`
- `172d2417`

proxy でも、`v20` / `v4` / `v5` をまたいで **13 行の binary hard row が一貫して落ち続けている**。

- `bit_other`: `101410e4`, `12154247`, `12fd5b6c`, `2230fad0`, `257e7158`, `2d790c98`, `c30a782a`
- `bit_structured_byte_formula`: `012fb81b`, `01e09228`, `1532c0d1`, `31966698`, `59c78e51`, `a6192d29`

つまり、現在の corrective は「binary を少し押す」ことはできても、**persistent hard core を消す新しい binary teacher** にはなっていない。

### 4.2 `default 1` failure mode が再帰している

proxy binary wrong rows に `default 1` が出る割合は依然高い。

- v20: `16/16`
- v4: `12/13`
- v5a: `14/18`

これは format failure ではなく **content drift** の信号である。
`v5a` で binary format は 100% 維持されたのに proxy binary が落ちたのは、この failure mode を抑え切れていないため。

### 4.3 surface lane が独立していない

`v3_mainline` では numeral が `116/149` まで崩れ、`v5a` では `139/149` まで戻した。
この往復が示しているのは、current corpus が

- reasoning content lane
- answer surface lane

をまだ十分分離できていないこと。

v20 README でも boxed-first extraction は契約の中核なのに、実験側はまだ binary 強化と boxed closure を同じ data-mix の中で押し引きしている。

### 4.4 `FINAL_SUMMARY` の余地は大きいが、同時に evidence gap も大きい

`cuda-train-data-analysis-v1/artifacts/train_recommended_learning_target_v1.csv` の strict handoff は `9363` 行あり、内訳は次。

| family | verified | answer_only |
| --- | ---: | ---: |
| bit_manipulation | `1229` | `271` |
| text_decryption | `605` | `971` |
| symbol_equation | `110` | `1410` |
| roman_numeral | `1576` | `0` |
| gravity_constant | `1597` | `0` |
| unit_conversion | `1594` | `0` |

余地は大きい。しかし `FINAL_SUMMARY_REPORT.md` と追加監査メモが示す通り、`symbol_equation` は simple promotion できない。

- `glyph_len5` は `823` 行が answer-only
- `numeric_2x2` は `587` 行が answer-only
- `cryptarithm_guess` / `equation_numeric_guess` は public な generator evidence が足りず strict verified 化が詰まっている

つまり「まだ answer_only が多いから全部 teacher 化すればよい」は誤り。
この残差は **データ不足というより evidence gap** である。

### 4.5 今の corrective は行単位すぎる

v1-v5 は数百行単位の overlay に強く依存していた。
しかし persistent failure は row-local tweak ではなく、次の能力不足として見えている。

1. binary query-specific closure
2. permutation / bijection exactness
3. symbol / character conversion
4. boxed terminal commitment

これは row の再配分より、**teacher の種類を分けるべき問題**である。

## 5. 1:1 artificial CoT trace は高品質か

### 5.1 結論

**一部では非常に高品質、しかし universal teacher としては不十分。**

### 5.2 高品質な領域

人手 / solver 生成の 1:1 trace は、少なくとも次の family では依然として最強クラスである。

- numeral
- gravity
- unit
- cipher
- verified な bit family

理由は単純で、**programmatic policy が明示できる**から。
README の勝ち筋もまさにここに乗っていた。

### 5.3 不十分な領域

ただし A-Open reasoning の trace はかなり長い。

集計結果:

- A-Open reasoning 全体: median `3818` chars / `162` lines
- baseline `train_split_with_cot.csv`: median `1013` chars / `66` lines

カテゴリ別では A-Open binary reasoning が平均 `8778` chars / `820` lines と極端に長い。

この長さは

- token budget
- exact closure の崩れ
- query tail の drift

に弱い。

したがって「高品質か」という問いへの正確な答えは、

- **policy teacher としては高品質**
- **training target としては長すぎることが多い**

である。

## 6. baseline の大規模モデル CoT の方が良いか

### 6.1 そのまま置き換える案には反対

`baseline/nemotron-sft-lora-with-cot-v2` 系の記録は、全体置換案に不利である。

- public: `0.70-0.72`
- proxy: `0.6650`
- local320: `0.7781`

これは v20 / v4 / v5 系より明確に低い。
したがって **full replacement teacher としては不採用** が妥当。

### 6.2 ただし、style donor としては有望

baseline 系には強みもある。

- 短い
- model-native phrasing
- boxed path が安定しやすい
- structured binary specialized では一定の改善を出した

実際、baseline 系の v3f は

- boxed 崩れではなく
- format は正しいが中身が wrong

という状態まで持っていった。これは **closure / output style teacher としての価値**を示している。

従って最も筋が良いのは、

**A-Open exact teacher を、baseline/LLM 的な short closure style に蒸留し直すこと**

である。

言い換えると、`train_split_with_cot.csv` は答えではないが、

- 文体
- closure
- token-efficient phrasing

の参考実装としてはかなり重要。

## 7. `FINAL_SUMMARY_REPORT.md` からまだ何を改善できるか

### 7.1 できること

#### A. verified binary の広い再設計

strict verified bit は `1229` 行あるが、v1-v5 の mainline が濃く使ったのはその一部だけだった。
特に活かし切れていないのは次。

- `binary_bit_permutation_bijection`
- `binary_bit_permutation_independent`
- `binary_structured_byte_formula_abstract`
- `binary_prompt_local_stage2_unique_exact`
- `binary_four_bit_boolean`

ここは **unused verified pool の row expansion** と **query-specific exact closure teacher** を作る余地がある。

#### B. answer_only を full CoT ではなく別 lane にする

`answer_only` はまだ大量にある。

- text `971`
- symbol `1410`
- bit `271`

ただしこれは full reasoning teacher ではない。使うなら

- boxed-only final answer stabilization
- short closure
- character/symbol conversion drills
- prefix/suffix preservation drills

のような **surface / token skill lane** に落とすべき。

#### C. text / symbol の補助データはまだ改善できる

README 自身が Nemotron の弱点として挙げているのは

- spelling
- splitting
- concatenating symbols
- text to characters

であり、ここは現 corrective 系が十分に攻めていない。

v20 の augmentations は方向性が正しかった。問題は、current direct-training 系でそれを **binary corrective と一緒に再設計できていない**こと。

### 7.2 できないこと

#### A. `cryptarithm_guess` を local heuristic だけで strict verified に上げること

追加監査では次が確認済み。

- `equation_numeric_guess` global exact scan: strict promotion `0`
- `cryptarithm_guess` published solver replay: strict singleton `0`
- `cryptarithm_guess` extended solver replay: gold match `0`
- public generator source search: authoritative semantics source 未発見

よって、ここは大きな本命 lane ではない。
mainline budget を burn する優先度は低い。

#### B. `answer_only` をそのまま reasoning teacher とみなすこと

これは誤学習の危険が大きい。

## 8. 0.88 を狙う次の大きい戦略

### 8.1 方針転換

次は `v5b` のような連番ではなく、**teacher architecture を変える run** にすべき。

名称は何でもよいが、中身は少なくとも次の 4 lane に分ける。

### Lane 1. Exact Algorithmic Teacher

対象:

- numeral / gravity / unit / cipher
- verified binary exact families
- exact permutation / bijection
- prompt-local exact bit rows

役割:

- 「何を計算するか」を教える本丸
- content correctness を作る

実装要件:

- query-specific closure を含む
- hardest binary は family abstraction だけで済ませない
- `default 1` に逃げる余地を減らす explicit exact closure を入れる

### Lane 2. Model-Native Short Closure Teacher

対象:

- Lane 1 と同じ問題のうち、特に binary / easy family

役割:

- 出力表面を Nemotron が再現しやすい形に短縮する
- boxed final answer と terminal commitment を安定化する

作り方:

- strong LLM に短い rewrite を作らせる
- ただし答えと rule closure は solver / exact teacher で検証する
- `train_split_with_cot.csv` の文体はここで参考にする

重要なのは、**LLM CoT をそのまま teacher にしない**こと。
exact teacher を rewrite した short closure を teacher にする。

### Lane 3. Token-Skill Auxiliary Teacher

対象:

- character decomposition
- symbol split / concat
- prefix / suffix preservation
- `\boxed{}` closure
- binary leading-zero exactness

役割:

- Nemotron の tokenizer weakness を局所訓練する

ここは README の改善提案とほぼ同じで、v20 augmentations の現代化と考えればよい。

### Lane 4. Answer-Only Stabilizer

対象:

- `answer_only_keep`

役割:

- final answer の commitment だけ補強する
- reasoning teacher の代用品にはしない

形式:

- boxed-only
- short rationale + boxed
- prefix-preservation only

## 9. 次 run の具体設計

### 9.1 mainline の中核

1. `v20` base の easy families は維持
2. binary は **exact closure lane** を太くする
3. permutation / bijection 専用 lane を独立させる
4. short closure rewrite lane を binary と easy family の両方に入れる
5. symbol prefix repair を極小で戻す
6. cryptarithm guess は mainline 本命から外す

### 9.2 binary で新しく必要なこと

現状の失敗は family sampling 不足だけではない。必要なのは次。

1. **permutation/bijection 専用 teacher**
2. **structured-byte exact closure teacher**
3. **anti-`default 1` counterexample pack**
4. **prompt-local exact rowsの再活用**
5. README が示唆するような token-efficient representation の検討
   - ただしこれは別 branch で安全に比較すべき

### 9.3 評価の変え方

README の反省どおり、held-out が弱いままでは public 0.88 を狙えない。
必要なのは次。

1. binary synthetic held-out generator
2. symbol/character skill held-out generator
3. easy-family surface regression set

今の proxy は重要だが、v4 が示したように `179/200 = 0.895` でも public `0.86` にしかならない。
したがって、proxy 単独では足りない。

## 10. 実務的な推奨

### やるべきこと

1. `v5b` 的な小改修連打は止める
2. `A-Open exact teacher` と `LLM short closure teacher` の hybrid 設計へ移る
3. `FINAL_SUMMARY` の verified / answer-only を lane 別に使い分ける
4. binary permutation / structured closure を main investment にする
5. text-to-character / symbol split / boxed closure を独立補助タスクとして復活させる
6. synthetic held-out generator を先に作る

### やるべきでないこと

1. `train_split_with_cot.csv` へ全面置換すること
2. `answer_only_keep` をそのまま full CoT teacher にすること
3. `cryptarithm_guess` を mainline で大量に追うこと
4. binary と surface を同じ lane の配分問題としてだけ扱い続けること

## 11. 最終判断

0.88 に届かない理由は、「少し配分が悪いから」ではない。

**今の学習データは、exact reasoning teacher と model-native closure teacher を混同している。**

v20 は exact policy と token-skill auxiliary の二層で勝っていた。
v1-v5 はその上で row-level corrective を積んだが、

- binary hard core を消す exact teacher の更新
- Nemotron が再現しやすい short closure style の導入

が別々に設計されていないため、0.85 台で往復した。

次に必要なのは、

**「人手 / solver の correctness」と「LLM 的な短い boxed-friendly 文体」を分離して併用すること**

である。

これが、単なる v5 の延長ではなく、0.88 を狙うための最初の本当の方針転換だと判断する。