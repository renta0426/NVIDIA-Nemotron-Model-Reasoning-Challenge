# v20 から 0.88 を狙う戦略メモ

このメモは **`A-Open-ProgressPrizePublication/README.md`**、`A-Open-ProgressPrizePublication/adapter-validation-notebook.ipynb` の保存済み結果、`A-Open-ProgressPrizePublication/leaderboard_proxy_eval_v20/reports`、および `cuda-train-data-analysis-v1/proof_first_solver_factory_routing/build_leaderboard_proxy_dataset.py` を根拠に整理した。

## 先に結論

**重要な前提を分ける必要があります。**

1. **元の A-Open 勝ち筋そのもの（Tinker 学習 → submission 変換）を使うなら**  
   README どおり、まず **lossy SVD を含む training-serving misalignment 修正** が最優先。

2. **今回の完全再現のように、Kaggle 上で最初から提出互換 LoRA を直接学習し、Tinker→submission 変換をしていないなら**  
   SVD 変換は主因ではない。こちらでは **bit_structured_byte_formula / bit_other / glyph_len5 / numeric_2x2** を中心に、**trace 設計・token efficiency・文字/記号 conversion** を直すのが最短。

README 自身も、まず効く改善として

- SVD 由来の **training-serving misalignment 修正**
- **tokens 直接生成**
- Nemotron の **文字/記号変換能力の補強**
- **synthetic 問題生成 + held-out validation**

を挙げている。  
したがって、**元の Tinker 系なら alignment が先、今回の Kaggle 直学習系なら trace / token / symbol 側が先**です。  
どちらの場合も、**RL や蒸留より前に deterministic policy を磨く**のが本筋です。

## 3 つの評価軸をどう読むか

| 評価軸 | 保存結果 | 何を意味するか | 使い方 |
| --- | --- | --- | --- |
| README の 9500件評価 | `8340 / 9500 = 87.8%` | **学習済みデータ上の到達点**。ただし seen set なので optimistic | 上限/coverage の確認 |
| adapter validation 950件 | `837 / 950 = 88.1%` | ローカルでの **実運用寄りの挙動**。easy task はほぼ飽和、残差は bit / cryptarithm / equation | run の promote 判定 |
| leaderboard proxy 200件 | `176 / 200 = 0.8800` | hidden leaderboard gap を局所再現する **stress set**。README 契約に合わせて構築済み | どの slice を直すかの優先順位付け |

重要なのは、**proxy の 0.8800 は public leaderboard の直接予測値ではない**ことです。  
`build_leaderboard_proxy_dataset.py` は、もともと **v3f=0.715 / current=0.560 の差を再現するために設計された 200件 proxy** です。したがって proxy は「弱点の向き」を見る用途に使うべきで、絶対値をそのまま public LB に写すべきではありません。

## v20 ができていること

README とローカル検証を合わせると、v20 系は次がかなり強い。

1. **roman / numeral**
   - README training set: `1576/1576 = 100%`
   - proxy: `19/19 = 100%`
   - validation 950: `149/149 = 100%`

2. **gravity / unit_conversion**
   - README training set: `1591/1597`, `1590/1594`
   - proxy: どちらも `100%`
   - validation 950: どちらも `100%`

3. **cipher / text_monoalphabetic**
   - README training set: `1565/1576 = 99.3%`
   - proxy: `20/20 = 100%`
   - validation 950: `158/162 = 97.5%`

4. **bit の一部**
   - README training set: `1397/1602 = 87.2%`
   - proxy では `bit_permutation_inversion = 25/26 = 96.15%`
   - `binary_affine_xor = 10/10`
   - `binary_bit_permutation_bijection = 23/24`

5. **フォーマット系の最低限**
   - proxy binary metrics では
     - boxed extraction success `1.0`
     - regex exact `1.0`
     - leading zero retention `1.0`
     - format failure `0.0`

つまり、**v20 は「問題の意味を分かっている easy family」と「一部の bit family」は既にかなり強い**。

## v20 ができていないこと

### 1. 元の Tinker 系では submission 側 alignment が最大論点

README が明示している最大の弱点です。

- Tinker 学習 adapter を submission 形式へ変換する際に
  - expert unfuse
  - `gate_proj + x_proj -> in_proj` の SVD 圧縮
  - prefix rename
  - `lm_head` の扱い

が必要で、特に **SVD が lossy**。

README で観測されている症状:

- `\\boxed` を書けない
- 直前 token の反復
- template を崩す
- training では通る easy task を validation で落とす

これは **元の Tinker 系**では、新しい reasoning を発見しなくても落ちる失点です。  
ただし、**今回の完全再現ではこの変換を通していない**ので、この論点は「A-Open 原法の改善案」と「今回の Kaggle 再現の改善案」を分けて扱う必要があります。

### 2. bit の hard slice

proxy では miss 24件中 16件が binary です。

- `bit_structured_byte_formula`: `23/31 = 0.7419`
- `bit_other`: `28/35 = 0.8000`
- `binary_structured_byte_formula_abstract`: `4/7 = 0.5714`
- `teacher_solver_candidate=''`: `23/37 = 0.6216`

しかも miss は **`num_examples=10`**、**`prompt_len_bucket=500-599`** に強く偏っています。

これは README の

- 「top solutions will need to maximize their score on bit manipulation」
- 「長くなりすぎる。base64 など、少ない token 表現が必要かも」

という指摘と一致しています。

### 3. symbol / text-to-character 系

proxy の symbol family は `24/32 = 0.75` で、特に

- `glyph_len5`: `1/5 = 0.2`
- `numeric_2x2`: `23/27 = 0.8519`

が弱い。  
また失敗例を見ると、**余計な引用符・括弧・記号断片** が混ざっており、README の

- Nemotron is bad at spelling
- Nemotron is bad at splitting / concatenating symbols
- text を character に落とす能力が弱い

と合致します。

### 4. cryptarithm は依然として低い

validation 950 では miss 113件のうち

- cryptarithm_deduce miss `65`
- cryptarithm_guess miss `11`

で大半を占める。  
ただし README どおり、ここは **「そもそも deterministic CoT だけでは苦しい」領域** で、0.88 到達の最短経路としては優先度を下げるべきです。

## 文面を見てもこの戦略は妥当か

**はい。妥当です。**  
ただし、raw output を見ると **失敗の型が 2 種類**あるので、改善も 2 系統に分けるべきだと分かります。

### A. symbol 系: 記号/文字 conversion 崩れ

失敗例:

- `numeric_2x2`: gold `46` に対して pred `)46`
- `glyph_len5`: gold `(\}:` に対して pred `(\\`

これらは raw output 上でも

- 余計な operator prefix を付ける
- quote / paren / slash が混ざる
- symbol-to-letter 対応を書いている途中で template が崩れる

という形で現れています。  
これは README の

- Nemotron is bad at spelling
- Nemotron is bad at splitting / concatenating symbols
- text を characters に落とす能力が弱い

とそのまま一致します。  
したがって、**symbol auxiliary 補強**と**文字/記号 conversion の corrective tuning**は、文面から見ても正しい優先順位です。

### B. binary 系: フォーマットは正しいが内容が少しずれる

失敗例:

- `bit_other`: gold `01000110` → pred `01100110`
- `bit_structured_byte_formula`: gold `00001000` → pred `01111110`
- `bit_permutation_inversion` の near miss: gold `11101011` → pred `11101111`

ここでは raw output が

- 8-bit 形式は守れている
- leading zero も保てている
- `\\boxed` 抽出や regex の失敗ではない

一方で、**bit の中身だけが 1〜数bit ずれる**。  
つまり binary 失敗の主因は、symbol 系のような format 崩れではなく、

- trace が長くて複雑
- structured rule を compact に表現できていない
- hard slice で token budget / internal reasoning が足りない

側です。  
したがって、binary に対しては **alignment 修正だけでは不十分** で、README が提案する **token-aware / compact trace 化** が必要です。

### C. 何が alignment 由来で、何が trace 由来か

文面ベースで整理すると次の通りです。

| 失敗の見え方 | 主因候補 | 優先アクション |
| --- | --- | --- |
| `\\boxed` 崩れ、反復、template 欠落、余計な記号 prefix/suffix | training-serving misalignment / character conversion 弱さ | 変換後 corrective finetune、symbol auxiliary |
| 8-bit 形式は合っているが内容だけ間違う | bit trace / token efficiency 不足 | compact trace 化、bit hard slice 専用データ |

つまり、**文面まで見ると「alignment を直せば全部解決」ではない**。  
加えて、**今回の完全再現では SVD 変換そのものが無い**ので、ここで見えている symbol/binary の失敗は、少なくとも今回の run では **trace 設計・tokenization・文字/記号 handling の問題が主**だと読むのが自然です。

## 0.88 に向けた優先順位

## Priority 1: v1 実測後は「追加」ではなく「再配分」に切り替える

`kaggle-v20-sft-repro-0414-104905` の v1 corrective run では、

- validation: `837/950 -> 838/950`
- proxy: `176/200 -> 178/200`
- proxy binary: `76/92 -> 80/92`
- proxy symbol: `24/32 -> 23/32`

でした。  
つまり **binary gain は本物** ですが、**symbol 本流投入は効かず、numeral / gravity / unit / symbolic cryptarithm に spillover regression が出た** というのが確定した事実です。

このため次の本命は、以前考えていた「bit + symbol を全部足す」ではなく、**token budget を増やさず binary gain を残しつつ easy-family guardrail を戻す budget-neutral reallocation** に変えるべきです。

**やること**

1. **`bit_structured_byte_formula` を主軸に残す**
   - v1 で `23/31 -> 26/31` と最も素直に効いた slice
   - proxy で実際に flip した `012fb81b`, `0520a6ec`, `0a50c4a8`, `59c78e51` のような「8-bit format は守ったまま中身だけ直る」型を維持する

2. **`bit_other` は軽量化する**
   - v1 では `28/35 -> 28/35` で、改善は `c30a782a` のような一部に限られた
   - `6a333ed6` のような regression もあるので、本線より薄く持つ

3. **`numeric_2x2` / `glyph_len5` の本流 overlay はいったん外す**
   - v1 では `numeric_2x2 23/27 -> 22/27`
   - `glyph_len5 1/5 -> 1/5`
   - symbol 問題は「方向性が完全に誤り」ではないが、今回の予算制約では高 EV ではない

4. **小さい guardrail pack を別 bucket で足す**
   - numeral subtractive: `081ad3f3`
   - gravity: `0fd289d8`
   - unit: `626d6c5f`
   - symbolic cryptarithm: `065abaf6`, `0dcfd566`
   - symbol prefix: `d9bedb64`
   - これら measured regressions を mandatory anchor にしつつ、base snapshot の `min_logprob` で fragile row を少量だけ追加する

5. **overlay 総 token 数を v1 より明確に下げる**
   - v1 bundle は約 `39.0M tokens`、学習時間は約 `10.5h`
   - 上限が約 `12h` なので、「さらに足す」は危険
   - 次は **binary に厚く、他は薄く、合計は縮小** が前提

**期待効果**

- proxy binary の改善を維持する
- easy family を落とす regression を止める
- runtime 制約の中で 0.88 へ向かう次の一手にする

## Priority 2: validation 設計を先に改善する

README は「held-out validation を作るべきだった」とかなり強く反省している。  
ここは 0.88 達成のための **実装より先に必要な運用改善** です。

**やること**

1. **950 validation を正式 gate にする**
   - 1 run ごとに必ず保存
   - category / mistake csv を蓄積

2. **leaderboard proxy を slice-gate にする**
   - 全体 `0.88` だけでなく
   - binary / symbol / selection_tier / template_subtype を見る

3. **training set 9500 は upper-bound 指標に格下げ**
   - seen set の 87.8% は有用だが、promote 判定には使わない

## 今やるべきでないこと

1. **RL を主戦略にしない**
   - README は「optimal policy が分かっているなら RL は不要」と明言

2. **cryptarithm を最優先にしない**
   - 難しい割に、0.88 に対する即効性が低い

3. **既に強い easy family をいじりすぎない**
   - roman / gravity / unit / text は守る対象

4. **現時点では symbol overlay を広く増やさない**
   - v1 実測では gain より spillover risk が目立った
   - symbol は将来の別線として残すが、次 run の本流では薄く扱う

## 実行順の提案

1. **budget-neutral binary + guardrail run**
   - `bit_structured_byte_formula` を厚く
   - `bit_other` を薄く
   - numeral / gravity / unit / symbolic cryptarithm / symbol prefix の guardrail anchor を少量追加

2. **その measured run を validation / proxy / raw output で再点検**
   - binary gain が維持されたか
   - easy-family spillover が止まったか
   - `2817d770`, `065abaf6`, `0dcfd566`, `081ad3f3`, `0fd289d8`, `626d6c5f`, `d9bedb64` を watchlist として追う

3. **それでも proxy symbol が致命的なら、別線で symbol micro-run**
   - ただし本線 bundle とは分ける

4. **必要なら Tinker 系 alignment 実験を別線で回す**
   - これは「元の A-Open 勝ち筋に戻る場合」の比較線

## 0.88 到達の判定基準

public 0.88 を直接予言することはできないが、少なくとも次を満たす run だけを本命候補にするのが妥当です。

- validation 950: **0.885 以上**
- proxy 200: **0.885 以上**
- proxy binary: **0.86 以上**
- proxy symbol: **0.80 以上**
- roman / gravity / unit / text_monoalphabetic: **全維持**

この条件なら、README が指摘している misalignment 由来の無駄落ちを減らしつつ、proxy が示す hard slice にも手が入っている状態だとみなせます。

## v2 実測後の v3 方針

v2 の実測で分かったのは、**guardrail を足すこと自体は悪くないが、binary content line と同じ土俵で混ぜると harmful** ということです。

- v1 は `proxy 176 -> 178` を作れた
- v2 は `validation 838 -> 839` を作れた
- しかし v2 は `proxy 178 -> 176` で、public も下がった

したがって v3 は **v1 に戻す run ではなく、v1 の勝ち筋と v2 の学びを分離して統合する run** にする。

### v3 の設計原則

README の勝ち筋は一貫している。

1. **bit manipulation が最大の差分源**
2. **deterministic で token-aware な CoT が必要**
3. **文字/記号 handling は弱く、surface corruption が起こる**
4. **easy family を壊すと leaderboard で無駄落ちする**

v3 ではこの4点をそのまま corpus 設計に落とす。

### v3 は 3 ライン構成にする

#### 1. `binary_precision_core`

主戦場。ここに overlay 予算の大半を使う。

- 目的:
  - v1 で効いた `bit_structured_byte_formula` の gain を維持・拡張
  - `bit_permutation_inversion` / `binary_bit_permutation_bijection` の v2 regression を戻す
  - `default 1` / operator drift を起こす trace を避ける
- 選定根拠:
  - v1-only proxy wins:
    - `012fb81b`
    - `0520a6ec`
    - `c30a782a`
  - v2 regressions:
    - `8e5d6fe6`
    - `b9500f41`
    - validation side: `0dd5caf4`, `1496dfeb`, `17fd9612`
- 追加ルール:
  - `default 1` を含む raw output へ落ちやすい trace は blacklist / low-repeat 扱い
  - `AND-NOT15 -> AND-NOT25` のような index drift が出た family は priority 監査対象にする

#### 2. `surface_boxed_repair`

small but mandatory. ここは **reasoning を変えるためではなく、最後の answer surface を壊さないため** の line。

- 目的:
  - `\\boxed` / terminal answer surface の崩れを修正
  - reasoning 自体は合っている easy family の「最後だけ壊れる」失点を止める
- 代表対象:
  - symbolic boxing failures:
    - `0133bcec`
    - `065abaf6`
    - `0dcfd566`
  - numeral ending corruption:
    - `1112ec96`
    - `18840879`
  - unit tail corruption:
    - `0a0698b2`
- 制約:
  - repeat 数は小さくする
  - binary core より強くしない
  - 「guardrail 全般」ではなく **final answer surface repair** に限定する

#### 3. `easy_family_preservation`

これは改善線ではなく **副作用防止線**。

- 対象:
  - numeral subtractive
  - gravity multiplication tail
  - unit decimal formatting
  - text/cipher final boxing
- 目的:
  - v2 のような `\\box` 終端や `44. -revised` を防ぐ
  - v1/v2 のどちらにもなかった無駄落ちを抑える
- 実装方針:
  - 少数 anchor + 低 repeat
  - raw output 上で「reasoning は合っているのに answer surface だけ壊れた」例を優先

### v3 でやらないこと

1. **broad symbol overlay を戻さない**
   - `numeric_2x2` / `glyph_len5` は v1 でも効率が悪かった
   - ここは main-line ではなく将来の別線

2. **guardrail を広く一般化しない**
   - v2 の失敗は「guardrail が多すぎた」より、**guardrail が binary core と干渉した**こと
   - だから v3 は guardrail を「surface repair」に限定する

3. **cryptarithm 全体を本命にしない**
   - 一部の malformed boxing 回収は行う
   - ただし solve-rate を大きく押し上げる主戦場にはしない

### v3 の token budget

v3 は「v1 に戻す」のでも「v2 をさらに削る」のでもない。

- v1 bundle: `39.03M tokens`, `301` steps
- v2 bundle: `32.08M tokens`, `267` steps

v3 では次を狙う。

- 目標 token:
  - **`34M-36M`**
- 目標 steps:
  - **`275-285`**
- overlay 配分の目安:
  - `binary_precision_core`: **70-80%**
  - `surface_boxed_repair`: **10-15%**
  - `easy_family_preservation`: **10-15%**

意図は、**v1 の binary 圧をある程度戻しつつ、v2 の surface repair を低副作用で残す** こと。

### v3 の昇格条件

v2 で分かった通り、validation 微増だけでは promote できない。  
v3 は **proxy 主導**で判定する。

最低条件:

- validation 950:
  - **`839/950` 以上**
- proxy 200:
  - **`179/200` 以上**
- proxy binary:
  - **`79/92` 以上を最低**
  - 本命昇格は **`80/92` 以上**
- proxy `bit_structured_byte_formula`:
  - **`26/31` 以上**
- proxy `bit_permutation_inversion`:
  - **v2 の `25/26 -> 24/26` 悪化を戻す**
- numeral / gravity / unit / text:
  - **v20 からの純減を許さない**

つまり v3 は、

- `validation が少し上がった`
- でも `proxy binary が下がった`

という v2 型の run を **不合格** にする。

### v3 の具体的な watchlist

#### 絶対に守るべき gain / regression

- binary gain を維持したい:
  - `012fb81b`
  - `0520a6ec`
  - `c30a782a`
- v2 regression を戻したい:
  - `8e5d6fe6`
  - `b9500f41`
  - `0dd5caf4`
  - `1496dfeb`
  - `17fd9612`
- surface repair で守りたい:
  - `0133bcec`
  - `065abaf6`
  - `0dcfd566`
  - `1112ec96`
  - `18840879`
  - `0a0698b2`

この watchlist を通して、

- **bit content gain**
- **terminal surface stability**
- **easy-family no-regression**

の3条件を同時に満たす corpus だけを v3 候補にする。

## 要するに

今回の Kaggle 直学習系で v1 実測まで踏まえると、v20 は **「binary corrective は効くが、symbol を雑に足すと easy family を壊す」** 段階にあります。  
したがって次の一手は、

- **binary reasoning を本線に戻す**
- **format / boxed repair を別 line に切り出す**
- **easy-family preservation を低 repeat で添える**
- **proxy binary を主 gate にして昇格判定する**

の順が最も筋がいい。

---

## v3 戦略レビュー（v1/v2/v20 全証拠に基づく徹底再検証）

### 1. 発見事項：`default 1` 病理は根本原因であり、学習データ品質問題である

v1/v2/v20 の 3 run で proxy binary 92 行の安定性パターンを調査した結果：

| パターン | 件数 | 内訳 |
| --- | --- | --- |
| always_correct | 72 | 3 run とも正解 |
| always_wrong | 10 | 3 run とも不正解 |
| unstable | 10 | run により正否が変わる |

全 92 binary proxy のうち不安定は 10 行（10.9%）、固定失敗は 10 行（10.9%）。

次に、各 binary proxy 行の **model 出力中の `default 1` 出現数** と正解率の関係を測定した：

| 状態 | v20 | v1 | v2 |
| --- | --- | --- | --- |
| `default 1` あり → 正解率 | 2/18 = 11.1% | 2/12 = 16.7% | 2/14 = 14.3% |
| `default 1` なし → 正解率 | 74/74 = 100% | 78/80 = 97.5% | 75/78 = 96.2% |

**`default 1` が出力に含まれると、ほぼ確実に不正解になる。** これは binary 失敗の事実上の kill switch である。

### 2. 監査補足：teacher `default 1` は自動的な誤答ではない

`A-Open-ProgressPrizePublication/nemotron/reasoning/*.txt` と `train.csv` を直接照合した監査結果は次のとおり：

| 集合 | 件数 | teacher 正答 | teacher 誤答 |
| --- | ---: | ---: | ---: |
| binary reasoning 全体で `default 1` を含む問題 | 229 | 66 | 163 |
| v20 snapshot (`04-08-16-14`) に実際に入った `default 1` base 問題 | 66 | 66 | 0 |
| v20 snapshot 上記 66 問題に対応する rows | 92 | 92 | 0 |

- binary reasoning 1602 ファイル中 **229 ファイル (14.3%)** が `default 1` を含む
- v20 学習トークンスナップショット 7830 件中 **92 件 (1.2%)** が `default 1` 問題に対応
- これら 92 rows は合計 **648,074 tokens (2.33%)** を占める
- ただし、**現 repo 上の v20 snapshot に入っている 66 base 問題はすべて teacher answer = gold** である

したがって、以前の「v20 学習に `default 1` 誤答が 92 件混入している」という主張は誤りだった。  
**`default 1` は強い危険信号だが、それ自体が teacher 誤答の十分条件ではない。**

### 3. それでも維持される強い事実

決定的に重要なのは、**always-wrong 10 行の teacher reasoning がすべて `default 1` を含み、すべて誤答**であること：

| always-wrong ID | teacher 回答 | gold 回答 | 一致 |
| --- | --- | --- | --- |
| 01e09228 | 10111001 | 10010101 | ✗ |
| 101410e4 | 10011101 | 10001101 | ✗ |
| 12154247 | 11111101 | 10111101 | ✗ |
| 12fd5b6c | 11011111 | 11001111 | ✗ |
| 1532c0d1 | 01011100 | 01001100 | ✗ |
| 2230fad0 | 01111110 | 01001010 | ✗ |
| 257e7158 | 00001111 | 00001001 | ✗ |
| 2d790c98 | 01111111 | 01111011 | ✗ |
| 31966698 | 11111111 | 11110111 | ✗ |
| a6192d29 | 01111110 | 00001000 | ✗ |

一方で、`v1_only_win` / `corrective_fixed` 側の teacher は大半が正しいが、**`012fb81b` は `default 1` なしでも teacher 誤答**である。
つまり、binary teacher 品質問題は `default 1` 一本ではなく、**`default 1` 誤答と non-d1 誤答が混在**している。

### 4. v1 / v2 の解釈は弱めるべき

raw output 上、v1 で `default 1` 出力が減り、v2 で一部戻ったこと自体は事実である：

- `c30a782a`: v20 は `default 1 = 1` → v1 は `AND-NOT07 = AND(0,NOT(1)) = 0`
- `0520a6ec`: v20 は `default 1 = 1` → v1 は `AND-NOT26 = AND(0,NOT(0)) = 0`
- `b9500f41`: v20/v1 は正常 → v2 は `default 1` に退行
- `c30a782a`: v1 は正しい演算 → v2 は `default 1` に退行

ただし、**その原因を「v20 に入っていた誤答 d1 学習例の重みが下がったから」と断定する証拠はない。**
現 repo では、v20 snapshot に入っている `default 1` 例は teacher 正答だからである。

より慎重な解釈は：

- `default 1` は **推論時の failure mode** として非常に危険
- v1/v2 の corpus 変更は、その failure mode を出しやすく／出しにくくする方向に model 挙動を動かした
- しかしその機序は、**誤ラベル除去**というより **推論表現や出力分布の変化** とみなすべき

### 5. 現在の v3 に対する再評価

#### 維持してよい点

1. **3-line 分離設計は正しい** — binary content 問題と surface/format 問題は別機構
2. **proxy-led promotion は正しい** — validation より proxy/public を重く見るべき
3. **`default 1` 出力を監視対象にすることは正しい** — kill switch 的な症状として扱う価値がある

#### 現在の v3 で問題な点

1. **現行 v3 bundle は「誤答除去」ではなく、teacher 正答例 92 rows の除去になっている**
   - 除去対象 66 base 問題はすべて teacher 正答
   - そのうち `004ef7c7` と `25a8aeb1` は binary proxy でも `always_correct`
   - つまり、**安定して正しい binary 教師例を削っている**

2. **現行 v3 は binary teacher の既知誤答を取り切れていない**
   - v20 overlap には `ef2fe526` という **non-d1 誤答** が 1 件残る
   - よって「d1 を除けば残り binary は teacher 正答のみ」という前提は成立しない

3. **現行 v3 は mainline 候補としては危険**
   - 削っているのは proven-bad examples ではなく proven-correct examples
   - proxy 改善余地はあるとしても、現時点では **危険なアブレーション** であって、0.88 本命 run ではない

### 6. 修正版の方針

#### 現在の v3 bundle の扱い

- `versions/v20_corrective_corpus_v3/` は **default-1 exposure ablation** として扱う
- **0.88 を狙う本命実験としては一旦停止**する
- もし回すなら、「誤答クリーニング」ではなく「correct teacher traces を 92 rows 削ったらどうなるか」を見る危険な比較 run と明示する

#### 次に mainline でやるべきこと

1. **誤答 teacher を直接狙う**
   - snapshot に実際に入っている teacher 誤答を列挙して除去・修正する
   - 現時点で確認済みなのは `ef2fe526`（non-d1 誤答）

2. **`default 1` は「除去対象」ではなく「監視対象」に格下げする**
   - proxy raw output で `default 1` 行数を追う
   - training data 側では、`default 1` を含むから即 blacklist ではなく、teacher 正否で分ける

3. **binary 改善は ADDITIVE を再評価する**
   - unstable 10 行や `bit_structured_byte_formula` 近傍に効く正答 overlay を増やす
   - ただし v1/v2 の副作用を避けるため、easy-family 保全と同時に小さく刻む

実装メモ:

- corrected mainline corpus: `versions/v20_corrective_corpus_v3_mainline/reproduce_v20_corrective_corpus_v3_mainline.py`
- bundle path: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v3_mainline_bundle.jsonl`
- 現行方針:
  - v20 base から **実誤答** `ef2fe526` のみ除外
  - overlay 側は **teacher-correct-only** に限定
  - binary を v2 より強く、guardrail は軽く維持

#### v3 mainline 実測レビュー

- validation: **`801/950 = 84.3%`**
- proxy: **`180/200 = 0.9000`**
- public leaderboard: **`0.84-0.85` 程度（実測報告）**

結論として、**teacher-correct-only binary overlay 自体は効いたが、guardrail を削りすぎたため mainline 失格**。

- 良かった点:
  - proxy binary は `76/92 -> 80/92`
  - `0520a6ec`, `0dd5caf4`, `17fd9612`, `c30a782a`, `b9500f41`, `8e5d6fe6` などで `default 1` / operator drift / loop が改善
- 悪かった点:
  - validation numeral が `147/149 -> 116/149`
  - 主因は **31 行の `\\boxed -> \\box` 崩れ**で、reasoning は正しいのに answer surface だけ壊れて prediction `0`
  - 同じ surface failure が cipher 4 行、cryptarithm symbolic 3 行でも発生

つまり v3 は「binary content 改善」と引き換えに、README 評価契約で最重要の **boxed-first extraction** を落とした。  
proxy の roman / text にはこの failure mode が出ていないため、**proxy 0.900 は public readiness を過大評価**したと読むべき。

### 7. 代替レバーの検討

corpus 変更だけで 0.88 に届かない場合のバックアップ：

1. **学習率 / warmup 調整** — 同じ corpus でも最適化軌道が変われば `default 1` 抑制力が変わりうる
2. **データ順序 / curriculum** — binary 正答例を後半に集中させて最終重みへの影響を強める
3. **repeat 戦略** — `default 1` なし binary 例の repeat 数を上げて signal を強化
4. **並列実験** — d1 除去 run と d1 除去 + overlay run を同時に走らせて比較

### 8. 次の本命候補に対する promotion gates

- validation ≥ 839/950
- proxy ≥ 179/200（本命は 180+）
- proxy binary ≥ 80/92
- **proxy binary 出力中の `default 1` 出現行数: v20 の 18 → 10 以下**
- proxy `bit_structured_byte_formula` ≥ 26/31
- numeral / gravity / unit / text: v20 からの純減なし

---

## v4 戦略（README / v1-v3 実測 / snapshot replacement report を統合した本命案）

### 1. 先に結論

**v4 は「v20 base を維持しつつ、binary 改善を additive に足し、`\\boxed` 終端を別 line で明示的に守る」設計にする。**

`A-Open-ProgressPrizePublication/v20_snapshot_final_summary_replacement_report.md` が示した通り、

- snapshot 全体の wholesale replacement はしない
- `FINAL_SUMMARY` は **監査済み誤答の外科的置換** と **teacher-correct-only overlay** にだけ使う
- `default 1` は **除去条件ではなく監視条件**

が正しい。  
README の評価契約では **boxed-first extraction** が最重要なので、v4 は **binary content line** と **answer-surface line** を分離して同時に強くする必要がある。

### 2. v1-v3 を改めてどう読むか

#### v1 の学び

- 良かった点:
  - proxy `176/200 -> 178/200`
  - proxy binary `76/92 -> 80/92`
  - `bit_structured_byte_formula` `23/31 -> 26/31`
- 悪かった点:
  - symbol は改善せず
  - numeral / gravity / unit / symbolic cryptarithm に spillover regression

**解釈:**  
v1 は **binary additive overlay が効く** ことを示した。  
ただし broad symbol overlay は EV が低く、同じ bundle に混ぜると副作用が出る。

#### v2 の学び

- 良かった点:
  - validation `838 -> 839`
  - malformed boxing や easy-family tail corruption は一部回収
- 悪かった点:
  - proxy `178 -> 176`
  - public も `0.83-0.84` 側へ軟化
  - binary structured line が v1 より弱くなった

**解釈:**  
v2 は **surface / guardrail line には価値がある** ことを示した。  
ただし guardrail を本線に寄せすぎると、README で最も重要な binary leverage を失う。

#### v3 の学び

- 良かった点:
  - proxy `180/200 = 0.9000`
  - teacher-correct-only binary overlay で `default 1` / operator drift / loop を抑えられた
- 悪かった点:
  - validation `801/950 = 84.3%`
  - public `0.84-0.85`
  - numeral 31 行で `\\boxed -> \\box`
  - cipher / cryptarithm symbolic でも終端 surface が壊れた

**解釈:**  
v3 は **teacher-correct-only binary overlay 自体は正しい** ことを示した。  
しかし **surface repair を削りすぎると proxy だけ上がって public は上がらない**。  
この run は「binary gain の上限確認」としては価値があるが、本命 mainline にはできない。

### 3. snapshot replacement report から v4 に引き継ぐべきこと

`v20_snapshot_final_summary_replacement_report.md` から、v4 で固定すべき前提は次のとおり。

1. **v20 snapshot は base distribution として維持**
   - easy family は既に強く、無闇に作り直す対象ではない
2. **除外は evidence-first**
   - 現時点で base から直接除外が正当化されているのは `ef2fe526*` のような監査済み誤答に限る
3. **overlay は teacher-correct-only**
   - `FINAL_SUMMARY` は curated binary overlay の供給源として使う
4. **`default 1` は kill switch 的な推論症状として監視**
   - ただし teacher trace 側で見つかっただけで即 blacklist しない

要するに、v4 は **「snapshot を削る run」ではなく「snapshot を壊さず足す run」** に戻す。

### 4. v4 の設計原則

#### 原則 1. binary と surface を別 line にする

- binary の主要失点は **content drift**
- numeral / cipher / cryptarithm の主要失点は **terminal answer surface**

この 2 つは別機構なので、同一 bucket に押し込まず分離する。

#### 原則 2. broad symbol mainline は戻さない

v1 で `numeric_2x2` / `glyph_len5` は効率が悪かった。  
v4 では broad symbol overlay はやらず、**prefix / suffix / boxed repair に必要な最小行だけ**を使う。

#### 原則 3. proxy を主 gate にしつつ、surface gate を validation に追加する

v2 は proxy/public が同方向、v3 は proxy blind spot が出た。  
したがって v4 では **proxy 主導 + validation surface gate** の二段階判定にする。

### 5. v4 corpus 構成

#### A. `base_snapshot_core`

- v20 base を維持
- 除外は **監査済み誤答 base rows のみ**
- teacher-correct と確認済みの `default 1` snapshot rows は残す

これは snapshot replacement report の結論そのまま。

#### B. `binary_precision_additive`

ここが本線。  
狙いは **v1 の binary gain** と **v3 の teacher-correct-only purity** を両立すること。

- 対象:
  - `bit_structured_byte_formula`
  - `bit_other`
  - unstable 10 行近傍
  - measured fixes が出た solver-family 近傍
- 制約:
  - **teacher-correct-only**
  - answer-only / manual-review trace は本線に入れない
  - `default 1` を含むから除外、ではなく teacher correctness で判定

**mandatory watch IDs**

- structured:
  - `012fb81b`
  - `0520a6ec`
  - `0a50c4a8`
  - `59c78e51`
  - `fa67da07`
  - `0dd5caf4`
  - `17fd9612`
- other / permutation:
  - `c30a782a`
  - `b9500f41`
  - `8e5d6fe6`

#### C. `terminal_surface_repair`

ここは v4 の追加本命。  
binary を変えるためではなく、README の boxed-first metric に合わせて **最後の数 token を壊さないため**の line。

- numeral:
  - `00d9f682`
  - `02e4851e`
  - `188fe6d4`
  - `1112ec96`
  - `18840879`
  - `081ad3f3`
- cipher:
  - `0184a864`
  - `018c6f61`
  - `13db9692`
  - `16642d10`
- cryptarithm symbolic:
  - `0133bcec`
  - `065abaf6`
  - `0dcfd566`
- unit tail:
  - `0a0698b2`
  - `077cfc0b`
- symbol prefix:
  - `d9bedb64`

**この line で教えること**

1. `I will now return the answer in \\boxed{}` を崩さない
2. answer 本体の前後に余計な backslash / quote / paren を足さない
3. reasoning が正しく終わったら terminal answer surface を deterministic に閉じる

#### D. `easy_family_preservation_micro`

これは改善線ではなく **副作用防止線**。

- numeral
- gravity
- unit
- cipher

の stable ending を少数 anchor で保持する。  
v3 の失敗から、ここは **薄くしすぎてはいけない**。

### 6. v4 の予算配分

v1 は重すぎ、v2 は binary が薄く、v3 は surface が薄すぎた。  
v4 は中間に置く。

- 目標 total tokens:
  - **`34M-35M`**
- 目標 steps:
  - **`275-285`**
- overlay 比率の目安:
  - `binary_precision_additive`: **50-55%**
  - `terminal_surface_repair`: **20-25%**
  - `easy_family_preservation_micro`: **15-20%**
  - `symbol_prefix / misc surface anchors`: **5-10%**

つまり、**v3 ほど binary に寄せず、v2 よりは binary を厚く**する。

### 7. v4 でやらないこと

1. **snapshot 全体の再生成**
2. **`default 1` を理由にした一括除外**
3. **broad `numeric_2x2` / `glyph_len5` main-line overlay**
4. **guardrail を generic に広げること**
5. **validation のみで promote 判定**

### 8. v4 の promotion gates

README 契約と v1-v3 実測から、v4 の昇格条件は次にする。

#### 必須スコア条件

- validation: **`839/950` 以上**
- proxy: **`179/200` 以上**
- proxy binary: **`80/92` 以上**
- proxy `bit_structured_byte_formula`: **`26/31` 以上**

#### 必須安全条件

- validation `numeral`: **`147/149` 以上**
- validation `gravity`: **`159/159` 維持**
- validation `unit_conversion`: **`170/171` 以上、理想は `171/171`**
- validation `cipher`: **`158/162` 以上**
- validation 上の **`\\box` だが `\\boxed` ではない行数 = 0 を目標、最大でも 1**
- validation 上の cipher backslash-wrap 行数 = 0

#### binary failure-mode 条件

- proxy binary 出力中の `default 1` 出現行数:
  - **10 以下**
- `8e5d6fe6` のような loop 行を再発させない
- `0520a6ec`, `0dd5caf4`, `17fd9612`, `c30a782a`, `b9500f41` を watchlist で維持

### 9. v4 の実験順

本命は 1 本ではなく、**同時に 3-4 本流す**。

1. **v4a: balanced mainline**
   - binary additive + medium surface repair
2. **v4b: stronger terminal-surface**
   - v4a より `terminal_surface_repair` repeat を少し増やす
3. **v4c: stronger binary**
   - v4a より binary repeat を少し増やすが、surface repair は v3 まで削らない
4. **v4d: curriculum variant**
   - corpus 内容は v4a と同じで、binary teacher-correct rows を後半寄せにして最終重み影響を強める

### 10. v4 の最終判断

0.88 に届く可能性が最も高いのは、

- **v1 の binary frontier**
- **v2 の terminal repair の必要性**
- **v3 の teacher-correct-only binary purity**
- **snapshot replacement report の evidence-first policy**

を全部採った run です。

したがって v4 の基本判断は明確です。

**「binary を強くする」だけでは駄目で、README の boxed-first metric に対して terminal answer surface を別 line で守る run だけが 0.88 候補になる。**
