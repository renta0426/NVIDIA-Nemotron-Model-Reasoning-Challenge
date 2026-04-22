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

## 12. v6 として何を実験すべきか

前提として、週に `3-4` run しか回せないなら、理想的な一変数ずつの対照実験はできない。
したがって v6 は、

- **証拠が強い変更は束ねて mainline へ入れる**
- **不確実性が高い軸だけを別 run で切る**
- **低期待値の枝は mainline から外す**

という run 設計にするべきである。

### 12.1 v6 で mainline に必ず入れるべき部分

これは「対照実験に回す候補」ではなく、v1-v5 の証拠から見て **入れない理由の方が弱い変更** である。

#### A. `v5a Stage C` 相当の easy-family surface stabilizer

残す対象:

- numeral boxed closure
- unit tail stabilization
- gravity fragile tail
- cipher final boxed closure

理由:

- v3 で guardrail を薄くすると numeral / boxed surface が崩壊した
- v5a では repeated `52` 行程度の小さな lane で numeral / unit を有意に回復できた
- ここは cheap で再現性が高く、削る合理性が薄い

結論:

- **v6 では Stage C は fixed component とみなす**
- ここを毎回いじって比較するのは run の無駄

#### B. exact binary closure lane の拡張

必須対象:

- `binary_structured_byte_formula`
- `binary_bit_permutation_bijection`
- `binary_bit_permutation_independent`
- `binary_prompt_local_stage2_unique_exact`
- `binary_four_bit_boolean`

理由:

- v1-v5 で persistent hard core が消えていない
- v5a は family-level short trace に寄せすぎて permutation / structured-byte を落とした
- `FINAL_SUMMARY` の strict verified pool には未活用の余地がまだある

結論:

- **v6 mainline は binary の量を増やすのではなく、query-specific exact closure を持つ teacher を増やす**

#### C. anti-`default 1` counterexample lane

対象:

- proxy / validation で `default 1` を繰り返し出した hard binary rows
- 近傍 family の exact positive / negative contrast pair

理由:

- `default 1` は v20, v4, v5 で何度も再発している代表 failure mode
- これは generic binary 増量ではなく、**明示的な counterexample supervision** を入れる方が筋がよい

結論:

- **v6 では anti-`default 1` は独立 lane として mainline に含める**

#### D. minimal symbol-prefix repair lane

対象:

- v4 で効いた prefix / suffix / operator-preservation 型の極小 repair

理由:

- v5a でここを抜くと `numeric_2x2` や symbol prefix の小回帰が起きた
- ただし broad symbol mainline は低期待値

結論:

- **v6 では broad symbol ではなく minimal repair だけ戻す**

### 12.2 v6 で mainline に入れない部分

run 数が少ない以上、ここを mainline に混ぜると解釈不能になる。

#### A. `cryptarithm_guess` の大規模強化

理由:

- strict verified 化の証拠がない
- local heuristic を積んでも generator evidence gap は埋まっていない
- run 予算に対して EV が低い

#### B. `answer_only_keep` の full CoT teacher 化

理由:

- reasoning teacher としては unsafe
- surface lane と reasoning lane が再び混ざる

#### C. easy family の本体 CoT の再設計

理由:

- 既に高得点
- 壊したときのコストが大きい
- easy family は preservation lane として扱う方が得

#### D. `train_split_with_cot.csv` への全面置換

理由:

- baseline 系全体スコアが低い
- donor としては有用だが、teacher の置換先ではない

### 12.3 v6 で分離して比較すべき 3 つの不確実軸

週 `3-4` run しかないなら、厳密な全組み合わせ比較はやらない。切るべき軸は次の 3 つに限る。

#### 軸1. short closure rewrite は効くか

問い:

- exact teacher を baseline / LLM 風の短い boxed-friendly closure に rewrite すると、binary content を保ったまま public に効くか

理由:

- これは v6 の本質的な新規性
- ただしまだ未検証

#### 軸2. token-skill auxiliary を modernized すると binary を壊さず効くか

問い:

- v20 augmentations の現代化が、current direct-training path でも効くか

理由:

- README の弱点認識とは整合する
- ただし binary mainline と混ぜたときの干渉は未測定

#### 軸3. binary の追加予算は permutation 重視と structured-byte 重視のどちらが高 EV か

問い:

- 限られた overlay 予算を、どちらへ厚く振るべきか

理由:

- v5a は permutation が薄すぎた
- ただし persistent hard core は structured-byte にも多い

### 12.4 週 3 run の場合の推奨編成

最も現実的な編成は次の 3 run。

#### Run 1: `v6-core`

入れるもの:

- fixed Stage C
- exact binary closure lane 拡張
- anti-`default 1` lane
- minimal symbol-prefix repair

入れないもの:

- short closure rewrite
- modernized token-skill augmentations
- risky な binary token representation 変更

役割:

- **新しい v6 の基準線**
- 以後の比較対象は全部これにする

期待:

- v4 の public edge を維持 / 超過しつつ、v5a より binary proxy を戻す

#### Run 2: `v6-core + short-closure`

Run 1 に追加:

- exact teacher から蒸留した short closure rewrite lane

役割:

- 「short closure が本当に mainline 価値を持つか」を測る

見るべき指標:

- proxy binary
- format_ok_content_wrong_rate
- numeral / unit の no-regression

#### Run 3: `v6-core + token-skill`

Run 1 に追加:

- spelling / splitting / concatenation / text-to-character / boxed closure の modernized auxiliary

役割:

- token weakness repair が current path でも効くかを測る

見るべき指標:

- symbol / text / boxed-surface failure
- binary collateral damage の有無

### 12.5 週 4 run できる場合の追加 1 本

4 本目は、次のどちらか一方だけを入れる。

#### Option A. `v6-core + permutation-heavy`

目的:

- overlay 予算を permutation / bijection に厚く寄せたときの EV を測る

向いている条件:

- `v6-core` で structured-byte は戻ったが permutation が弱い場合

#### Option B. `v6-core + structured-heavy`

目的:

- structured-byte exact closure をさらに厚くしたときの EV を測る

向いている条件:

- `default 1` rows の中心が structured-byte に残る場合

注意:

- 4 本目で binary token representation 変更まで入れるのはやりすぎ
- base64 / nibble 圧縮のような表現変更は **v6 本流ではなく v7 候補** とみなす方が安全

### 12.6 実際の優先順位

run budget が厳しいなら、v6 で優先順位は次の順。

1. `v6-core`
2. `v6-core + short-closure`
3. `v6-core + token-skill`
4. `v6-core + permutation-heavy` または `structured-heavy`

この順にする理由は単純で、

- 1本目で新しい mainline の骨格を作る
- 2本目で teacher architecture 変更の本命仮説を検証する
- 3本目で README 由来の token weakness repair を測る
- 4本目で binary 内部の予算配分を詰める

### 12.7 v6 の採用基準

採用候補にする最低条件は次のように置く。

- public: `0.86` を安定して再現し、`0.87` に触れる余地が見えること
- proxy: `179/200` 以上を最低、理想は `181/200` 以上
- proxy binary: `80/92` 以上を最低、理想は `82/92` 以上
- numeral: `145/149` 以上
- unit: `171/171` を維持
- format_ok_content_wrong_rate: v4 `0.1413` 以下へ近づくこと

要するに、v6 は「local が少し良い」では不十分で、

- binary public edge
- easy-family surface stability

を同時に満たした run だけを昇格対象にするべきである。

## 13. v6-v7-1 を踏まえた更新判断

ここまでの記述は v1-v5 を主対象としていたが、その後の `v6`, `v7`, `v7-1` まで含めると、結論はさらに強くなる。

### 13.1 もう `04-08-16-14` の配分調整だけでは 0.88 に届かない

`v6` は proxy ではこの系列の最良だった。

- proxy: `180/200 = 0.9000`
- proxy binary: `80/92 = 0.8696`

しかし public は `0.83-0.85` に留まり、`v4` の `0.85-0.86` を明確に超えなかった。

`v7` は token-safe 継承を壊した invalid run であり、これは teacher policy の失敗ではなく bundle 構築の失敗だった。

`v7-1` はその修正版で、

- validation: `839/950 = 0.8832`
- proxy: `178/200 = 0.8900`
- public: `0.84`

まで戻したが、public best には届いていない。しかも `v7-1` の改善本体は text corpus の刷新ではなく、`v4_public_base` の token-safe 継承を `298` 問ぶん回復したことだった。

つまり、`v1-v7-1` がまとめて示したのは次の一点に尽きる。

**大元コーパス `A-Open-ProgressPrizePublication/nemotron/training/sft/04-08-16-14` の比率や overlay 配分を多少いじるだけでは、official `0.88` には到達しない。**

ここで得られたのは

- どの data mix が binary output を no-box / malformed へ崩すか
- どの data mix が boxed termination を戻すか
- どの lane が easy-family を守るか

という挙動の知見であって、**新しい frontier teacher** ではない。

### 13.2 symbol は「弱い」のではなく、現手法では完全に不動

`v4`, `v6`, `v7-1` の symbol proxy `32` 行を比較すると、結果は完全一致だった。

- correct: `24/32`
- wrong: `8/32`
- version 間の improved / regressed: `0`

pattern は厳密に

- `111`: `24` 行
- `000`: `8` 行

だけで、動く row が 1 件もない。

固定 hard rows は次の `8` 件である。

- `numeric_2x2`: `8158a14c`, `878c843c`, `b7b1d1a8`, `e8de8b47`
- `glyph_len5`: `a85864a9`, `be7101dc`, `d7e5414c`, `dc240ebd`

しかもこの `8` 件はすべて

- `format_bucket = boxed`
- `fallback_type = boxed_non_empty`

で落ちている。つまり symbol の失点は boxed closure failure ではない。**中身が wrong な exact transduction failure** である。

この点で symbol は binary と違う。binary は `54/92 -> 80/92 -> 78/92` と動くが、symbol は current corrective family では全く動かない。

したがって、symbol を broad overlay の一部として混ぜ続けても EV は低い。必要なのは **symbol 専用 teacher program** であって、mainline mix の微調整ではない。

## 14. official 0.88 に向けた抜本戦略

### 14.1 全体方針

次の本命は「ratio tuning の続き」ではない。明確に次の 3 つへ切り替えるべきである。

1. `04-08-16-14` の easy-strength は preservation lane として最小限だけ残す
2. スコアの主戦場である BIT に、programmatic exact teacher を新設する
3. symbol は mainline の補修ではなく、独立の exact transduction track として切り出す

ここで重要なのは、95%以上の family を 100% に近づけることより、`bit_manipulation` と `symbol` の未解決 core を直接動かすことを優先する点である。

### 14.2 投資配分

`v4/v6/v7-1` の実績と README の主張から、次の配分が妥当である。

- `75%`: BIT mainline
- `20%`: symbol 専用 track
- `5%`: easy-family regression guardrail

この配分にする理由は明確である。

- BIT は proxy `92` 行を占め、public 変動の主因でもある
- symbol は proxy `32` 行と母数は小さいが、現手法で `0` 行しか動かず、別アーキテクチャが必要
- numeral / unit / gravity / cipher は preservation 対象であり、main investment の対象ではない

### 14.3 BIT mainline の設計

BIT 側では、ratio ではなく **teacher architecture** を更新する。

必須 lane は次の 4 本である。

#### A. exact closure lane

対象:

- `binary_structured_byte_formula`
- `binary_bit_permutation_bijection`
- `binary_bit_permutation_independent`
- `binary_prompt_local_stage2_unique_exact`
- `binary_four_bit_boolean`

要件:

- family abstraction で終わらず、query-specific closure まで書く
- persistent hard core を直接叩く
- `default 1` へ流れる余地を減らす

#### B. anti-`default 1` counterexample lane

対象:

- `101410e4`, `12154247`, `12fd5b6c`, `2230fad0`, `257e7158`, `2d790c98`, `c30a782a`
- `012fb81b`, `01e09228`, `1532c0d1`, `31966698`, `59c78e51`, `a6192d29`

要件:

- positive / negative contrast pair を明示する
- 「それっぽい 1 埋め」ではなく exact rule を選ばせる supervision を作る

#### C. model-native short closure lane

対象:

- exact teacher で解ける binary rows

要件:

- baseline/LLM 風の boxed-friendly short closure へ rewrite する
- ただし correctness は exact teacher 側で固定する
- long trace を短くすることが目的であり、LLM CoT を丸ごと採用しない

#### D. token-efficient representation side branch

README が示唆しているような

- nibble 表現
- base64 的表現
- operator-local compact notation

は試す価値がある。ただしこれは本流 mainline に直結させず、**別 branch** で比較する。

理由は、表現変更は binary だけでなく tokenizer 依存挙動全体を変えうるためである。

### 14.4 symbol 専用 track の設計

symbol は broad symbol overlay を増やすのではなく、固定 hard `8` 行を起点に exact transduction problem として再設計する。

#### A. `numeric_2x2` exact operator lane

対象 IDs:

- `8158a14c`
- `878c843c`
- `b7b1d1a8`
- `e8de8b47`

failure shape:

- boxed ではある
- operator prefix / suffix の付け方が wrong
- leading zero / numeric normalization が wrong
- ときどき operator semantics 自体が wrong

必要なのは、演算子ごとの output canonicalization を exact に教える teacher である。boxed repair を厚くしても解決しない。

#### B. `glyph_len5` exact transduction lane

対象 IDs:

- `a85864a9`
- `be7101dc`
- `d7e5414c`
- `dc240ebd`

failure shape:

- boxed ではある
- 文字列長や symbol slot が微妙に崩れる
- symbol alphabet table の写像と copy が壊れる

ここで必要なのは

- symbol alphabet table の厳密化
- per-character copy drills
- prefix / suffix preservation
- symbol sequence length commitment

である。これは numeric_2x2 と同じ teacher ではない。

#### C. symbol mini-gate を mainline から分離する

次の mainline に symbol を大きく混ぜる前に、まず次の条件を満たすべきである。

- fixed hard `8` 行で `2` 行以上の改善
- binary に悪影響がない
- boxed は元からできているので、content-only improvement が確認できる

この条件を満たせない symbol data は、本命 mainline に入れない。

### 14.5 easy-family の扱い

easy family は次の理由で main investment から外す。

- README でも主戦場は bit と明記されている
- v7-1 でも numeral 回復だけでは public を押し上げられなかった
- easy family の 100% 化は EV が低く、ratio tuning の再演になりやすい

ただし削りすぎると `v3` や `v7` 型の regression を起こすため、次の最小 guardrail は残す。

- numeral boxed closure
- unit tail stabilization
- gravity fragile tail
- cipher final boxed closure

これは新しい scoring source ではなく、既得点の保全策である。

### 14.6 次の run 編成

次の `3-4` run は、v6-core の延長ではなく **2-track + 1 guardrail** で組むべきである。

#### Run 1: BIT-core

入れるもの:

- exact binary closure lane
- anti-`default 1` lane
- short closure rewrite lane の最小版
- easy-family minimal guardrail

見たい指標:

- proxy binary `82/92` 以上
- `format_ok_content_wrong_rate` の低下
- hard watchlist の改善数

#### Run 2: SYMBOL-core

入れるもの:

- `numeric_2x2` exact operator lane
- `glyph_len5` exact transduction lane
- symbol/token copy auxiliary

見たい指標:

- fixed hard `8` 行で `2` 行以上改善
- binary collateral damage `0`

#### Run 3: BIT-core + SYMBOL-lite

条件:

- Run 2 で symbol mini-gate を通った場合だけ実施

入れるもの:

- BIT-core
- 改善が確認できた symbol lane のみ
- easy-family minimal guardrail

役割:

- symbol の改善が binary public edge を壊さないか確認する

#### Run 4: BIT representation branch

入れるもの:

- BIT-core
- token-efficient representation のみ追加

役割:

- README の「bits を少トークンで表す」仮説の独立検証

### 14.7 昇格条件

official `0.88` を狙う本命 branch として昇格させる最低条件は次のように更新すべきである。

- public: `0.86` 安定ではなく、`0.87` 接触を必須条件へ近づける
- proxy binary: `82/92` 以上
- persistent hard binary watchlist の改善が複数あること
- symbol fixed hard `8` 行のうち少なくとも `2` 行が動くこと、または symbol を外しても public が上がる明確な証拠があること
- easy-family guardrail regression が軽微であること

要するに、次に必要なのは「better mix」ではない。

**BIT は exact rule discovery teacher を作り直し、symbol は exact transduction teacher を別トラックで作り、easy family は guardrail に格下げする。**

これが、v1-v7-1 の総括として最も筋の良い official `0.88` 到達戦略である。