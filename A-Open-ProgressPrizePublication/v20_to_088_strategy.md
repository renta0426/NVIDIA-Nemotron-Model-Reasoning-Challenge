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

## Priority 1: 今回の完全再現では bit / symbol を先に直す

**狙い**  
今回の Kaggle 直学習 run が落としている **binary と symbol の hard slice** を直接減らす。

**やること**

1. **bit_structured_byte_formula / bit_other 専用 trace を作る**
   - 特に `num_examples=10`、`prompt_len=500-599` を優先
   - 現行 trace のどこで token を使いすぎるかを min-logprob だけでなく **token 長**でも監査する

2. **text ではなく token 直接生成へ寄せる**
   - README の提案そのまま
   - 少なくとも binary trace は **token-aware / compact representation** に切り替える

3. **symbol corrective data を本流に入れる**
   - `glyph_len5`、`numeric_2x2`、quote / paren / slash contamination を直す短い corrective trace を追加する

4. **easy family の guardrail を作る**
   - roman / gravity / unit / text_monoalphabetic は **validation と proxy で 100% を維持**する
   - ここを 1 件でも落としたら promote しない

**期待効果**

- proxy の主要 miss を直接削る
- 今回の再現系で実際にボトルネックになっている slice に学習予算を集中できる

## Priority 2: 元の Tinker 系に戻るなら alignment-only 改善

**狙い**  
README の勝ち筋そのものを使う場合に、Tinker→submission 変換で生じる loss を回収する。

**やること**

1. **SVD misalignment を減らす**
   - README が提案している **post-finetune to align the weights** を最優先で試す
   - 変換後 adapter に対し、**loss が増えた token だけを再学習**する短い corrective SFT をかける

2. **rank 16 → lossless upscale line を再検証**
   - README では 0.82 にとどまったが、当時は token-level corrective tuning が未実施
   - zero-pad path 単体でなく、**変換後 corrective tuning とセット**で再試行する価値がある

**期待効果**

- public leaderboard と local のズレを縮める
- 「既に解けるのに落としている」失点を回収できる

## Priority 3: symbol auxiliary を本流に統合

README と `04-10-04-15`, `04-10-04-33` から、著者自身も post-v20 で

- spelling
- splitting
- concatenation
- matching
- lstrip

を足し始めています。  
したがって方向性は合っています。問題は **本流スコアにどう効かせるか** です。

**やること**

1. `glyph_len5` 系を直接作る  
2. symbol 出力の quote / paren / slash 混入を防ぐ短い corrective trace を足す  
3. `numeric_2x2` の symbol → char 展開をより deterministic にする

**期待効果**

- proxy の symbol `0.75` を `0.85+` へ押し上げられる可能性がある
- README の「Nemotron の character conversion が弱い」に正面から対応できる

## Priority 4: validation 設計を先に改善する

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

## 実行順の提案

1. **bit trace compact化 run**
   - `bit_structured_byte_formula` と `bit_other` のみ集中的に改善

2. **symbol auxiliary corrective run**
   - `glyph_len5` と quote/paren contamination を直す

3. **全部入り再学習**
   - 上の改善を統合した本命 run

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

## 要するに

v20 は **「解法が弱い」より「解けるものを submission 側で落とす」「bit と symbol の hard slice がまだ残っている」** モデルです。  
したがって 0.88 を狙うなら、

- **まず alignment**
- **次に bit の compact trace**
- **最後に symbol auxiliary**

の順が最も筋がいい。
