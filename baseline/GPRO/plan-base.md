## 結論
**今の壁は「binary用CoTの書き方」ではなく、「outcome optimization と specialist化」へ軸を移すべき段階**です。  
その意味で、

- **ORPO単体** = 有望だが主に**出力規律・長文化抑制・boxed安定化**向き
- **GRPO** = うまく設計すれば**binary本丸**に一番効く可能性が高い
- ただし **いきなり real binary に GRPO 直打ち**は失敗しやすい

です。

今の実験群から導く最有効戦略は、単純化するとこれです。

> **trace-centric mixed SFT をやめて、binary を outcome-centric な specialist 学習へ切り替える。**  
> **最初は answer-only / preference / rejection で短い exact boxed 出力を作り、次に synthetic curriculum 上で GRPO、最後に general adapter と merge。**

---

# まず、今の実験が何を示しているか

あなたの結果はかなり一貫しています。

## 1. Phase 1 の勝ち筋は「general emission stabilization」だった
`result/0 -> result/1` で伸びたのは主に

- text
- gravity
- last_number 崩壊の減少

です。  
一方で binary は `11/60 -> 12/60` 程度で、本質改善ではない。

つまり **assistant-only loss 等は正しかったが、それは binary の本丸ではなかった**。

---

## 2. binary は teacher wording を変えても動いていない
`result/2` と `result/2-1` が非常に重要です。

- DSL 化しても、`verified_trace_ready` や `bit_structured_byte_formula` がほぼ改善しない
- hybrid narrative にするとむしろ `last_number` が再増加し、binary も text も崩れる

つまり、今のモデルに対しては

- natural language CoT
- DSL scratchpad
- hybrid narrative

の**表層変更は高レバレッジではない**。

これはかなり強い結論です。  
**binary のボトルネックは「trace wording」ではない**。

---

## 3. corrected metric で見ると、binary の見かけ上の改善もかなり剥がれた
あなたの再分析で重要なのはここです。

`result/2` の binary `13/60` は、exact 8-bit で見ると `9/60`。  
つまり一部は tolerance 的な見かけ改善だった。

これはかなり大きいです。  
**binary は今、実質的にはまだほぼ解けていない**と見た方がいい。

---

## 4. binary 失敗の中心は「extractor」ではなく「正しい byte を固め切れていない」
各分析で共通しているのは、

- boxed できない
- 長文化する
- gold 8-bit が raw output 内にもあまり現れない
- structured-byte slice も移らない

という点です。

つまり binary は

- 出力整形の問題もある
- でも本質はそれだけではない
- **few-shot の latent rule induction が transfer していない**

です。

---

## 5. 今の trace-safe 選別は、SFT には正しいが、outcome optimization には制約が強すぎる
ここが次の大きな転換点です。

`FINAL_SUMMARY_REPORT.md` の binary は

- `1004 verified`
- `281 answer_only`
- `302 manual`
- `15 exclude`

でした。

でもこれは**trace教師の安全性**で切っているのであって、  
**final answer 最適化の可否**とは別です。

### 重要な再解釈
- `manual_audit_priority` は「trace が unsafe / reusable rule 不明」
- しかし **train.csv の gold answer 自体はある**
- `exclude_suspect=15` 以外は、少なくとも **outcome-only 学習や reward 設計には使える可能性が高い**

つまり今までの binary 学習は、
**trace教師の都合で使えるデータを狭めすぎていた**可能性があります。

これは ORPO / GRPO にとって大きいです。

---

# では ORPO と GRPO はどうか

## 先に結論
### binary 改善の本命は **GRPO**
### ただし、**ORPO を先に cheap probe として入れる価値は高い**

---

## ORPO の位置づけ
ORPO（Odds Ratio Preference Optimization）は、ざっくり言うと

- chosen / rejected の pair が作れる
- 参照モデルなしで preference 最適化できる
- 実装が比較的軽い

という方法です。

### binary に対する強み
ORPO は binary で特に次に効きます。

- `\boxed{}` をちゃんと閉じる
- `1`, `10`, `001`, `-0` のような collapse を減らす
- 長文化を減らす
- final answer を短く安定して出す

つまり **format discipline optimizer** としてはかなり有望です。

### でも限界もある
ORPO は、
**モデルがまだ持っていない rule induction 能力を新しく作る力は弱い**です。

なので今の binary みたいに

- verified slice が伸びない
- structured-byte が 0/14
- gold 8-bit そのものが出てこない

という状態に対して、**ORPO単体で大幅改善する可能性は低い**です。

### ORPO の最適な役割
- 本命ではない
- ただし **binary specialist の前処理 / 後処理**としてはかなり有効

---

## GRPO の位置づけ
GRPO は DeepSeekMath 系で有名になった、  
**複数サンプル + 相対報酬**で reasoning を押す RL 系です。

### binary に GRPO が向く理由
binary はまさに

- 正解が自動判定可能
- strict verifier が作れる
- reward hack を比較的防ぎやすい
- exact output が求められる

という **verifiable reasoning task** です。

これは GRPO 向きです。

### ただしそのままでは危険
今の policy で hard real binary にそのまま GRPO をかけると、

- correct trajectory がほぼ出ない
- sparse reward で更新が死ぬ
- format reward だけ最適化して短く wrong answer を吐く
- あるいは長文化 reward hack が起きる

可能性が高い。

### だから必要なのは
**GRPO そのもの**ではなく、  
**binary-specialist RLVR pipeline** です。

---

# 最も有効な戦略

## 一言で言うと
**「binary の CoT 改良」から撤退して、  
「binary の outcome-centric specialist adapter」へ移るべきです。**

そしてその中で、

1. **answer-only / rejection / ORPO で短い exact output policy を作る**
2. **synthetic curriculum 上で GRPO**
3. **general adapter と merge**

が最も筋が良いです。

---

# 推奨戦略の全体像

## Stage A. mixed SFT の binary trace いじりは一旦止める
今の証拠では、ここはもう low ROI です。

止める対象:
- binary trace wording 微調整
- DSL vs hybrid の再試行
- shared 900-mixture 内での binary 比率の微調整だけに期待すること

### 理由
実験結果がもう十分示しています。
- wordingで verified slice が動かない
- 長文化はむしろ harmful
- structured-byte が動かない

---

## Stage B. general adapter と binary specialist を完全分離する
これはかなり重要です。

### G: general anchor
今の `result/1` or `result/2` 系の
- assistant-only
- general stable 強い
- text/gravity/roman/unit を守れる

adapter を general anchor にする。

### B: binary specialist
別 LoRA として、
**binary だけ**を outcome-centric に鍛える。

これを同じ LoRA に上書きし続けるのが今までの問題でした。  
binary を押すと text/symbol/roman が壊れるので、**分離が必要**です。

---

## Stage C. binary 学習は trace-safe 中心から outcome-only 中心へ移す
ここが本質です。

### 使うデータ
binary では **exclude 以外ほぼ全部使う** 発想に切り替える。

推奨:
- `verified_trace_ready`: 高重み
- `answer_only_keep`: 中重み
- `manual_audit_priority`: **early positive SFT には直接入れず**, rollout で strict verifier を通過した成功軌跡か late-stage RL prompt として使う
- `exclude_suspect`: 使わない

### なぜ可能か
`manual` は trace が unsafe なだけで、  
**final answer supervision / verifier reward** には使えるからです。

これは SFT-with-trace では無理だったが、
**answer-only SFT / ORPO / GRPO では可能**です。

ここが戦略転換の核です。

---

# ORPO / GRPO をどう組み込むか

## 最適な順番
### 1. binary answer-only SFT or RFT
### 2. ORPO で format / collapse を矯正
### 3. GRPO で reasoning を押す
### 4. merge

これが一番安全です。

---

## Step 1: binary answer-only SFT / RFT
まず binary specialist の出力を基本

```text
\boxed{00110100}
```

に寄せます。

### ポイント
- verified でも trace を標準にしない
- majority を `boxed only` にする
- 必要なら少量だけ ultra-short scratchpad を混ぜる
- でも長い `<think>` は避ける
- **初期の positive teacher は `verified_trace_ready + answer_only_keep` を中心にし、`manual_audit_priority` は strict verifier を通った rollout 成功だけ採用する**

### なぜ
あなたの結果では、
**binary では trace の質改善より「短く exact に閉じる」方が圧倒的に重要**だからです。

### さらに良い案
RFT 風に、
- current best model から多サンプル生成
- strict verifier で exact success を拾う
- その成功軌跡だけで再SFT

もかなり有効です。  
GRPO前の warm start として非常に相性がいいです。

---

## Step 2: ORPO で collapse を叩く
ここで ORPO が効きます。

### chosen
- `\boxed{01010101}` のような exact gold
- できれば短い completion
- `manual_audit_priority` は raw gold をそのまま chosen にせず、**rollout で strict exact を通した短い成功例**を優先する

### rejected
- current model の長い wrong output
- `1`, `10`, `001`, `-0`
- leading zero dropped
- multiple boxes
- boxed 後ろに数字が続く
- 1-bit flipした near-miss
- decimal/int 化した binary string

### 期待効果
- `last_number` 依存の減少
- 出力長の抑制
- box discipline の強化
- leading zero 保持

### でも注意
ORPO だけで structured-byte を解くのは難しい。  
これはあくまで **出力 policy を整える段階**です。

---

# Step 1 / Step 2 は GRPO の必須前提か

## 結論
**理論上は必須ではないが、この repo の binary では実務上かなり重要**です。

いきなり GRPO を始めること自体はできます。  
しかし現状の失敗は、

- `README.md` の実評価が `\boxed{}` 優先 + fallback 抽出で動く
- binary では `last_number` / long-output collapse が大きい
- `result/2-1` の hybrid のように、自然言語推論を増やすと binary も non-binary も崩れやすい
- `bit_structured_byte_formula` がまだ `0/14` で、real binary にそのまま sparse reward を当てても探索が立ち上がりにくい

という条件なので、**GRPO が「解き方」を学ぶ前に「壊れた答え方」に引っ張られる危険が高い**。

したがって Step 1 / Step 2 は、

- Step 1 で action space を `\boxed{[01]{8}}` 近傍に寄せる
- Step 2 で collapse / leading-zero drop / extra digits を先に減らす
- Step 3 で初めて reasoning/search policy を押す

という **readiness filter** として使うのがよい。

## どういう意味で「前提」なのか

### Step 1 がやること
- binary specialist の default completion を短い exact boxed byte に寄せる
- `manual_audit_priority` の unsafe trace を early positive teacher へ混ぜない
- rollout 成功例を positive teacher に再利用できる状態を作る

つまり Step 1 は、**GRPO の前に「正しい終端形」を固定する工程**です。

### Step 2 がやること
- `1`, `10`, `001`, `-0` のような collapse を chosen/rejected で直接叩く
- leading zero の保持を policy に埋め込む
- `last_number` fallback に落ちやすい長文 completion を不利にする

つまり Step 2 は、**GRPO の reward に入れる前から明らかな bad policy を先に削る工程**です。

### Step 3 が本来やること
- format 修正ではなく、答えそのものを見つける policy を押し上げる
- synthetic curriculum と verifier で structured-byte まで探索させる

したがって、この 3 つは役割が違う。  
**Step 3 単独で Step 1 / Step 2 の仕事まで兼務させると、失敗確率が高い**。

---

## Step 3: GRPO を binary specialist にだけ適用
ここが本命です。

ただし **real binary 直打ちではなく curriculum 必須**です。

### 推奨カリキュラム

#### Phase GRPO-1: synthetic easy-medium
solver で生成できる binary puzzle を大量に作る。

- affine
- byte transform
- boolean2/3
- structured byte
- choose/majority
- near-miss hard cases

### 重要
easy only ではダメです。  
必ず
- ambiguity-rich
- leading zero 多め
- family confusion 多め
を入れる。

#### Phase GRPO-2: synthetic hard + real verified
ここで real verified を混ぜる。

#### Phase GRPO-3: real all-non-exclude
最後に
- verified
- answer_only
- manual
を全部使う。

### reward 設計
初期は sparse reward だと死ぬので、2段階にするのが良いです。

#### early reward
- `+1.0` exact boxed match
- `+0.2` regex `^\s*\\boxed\{[01]{8}\}\s*$`
- `+0.1` single box only
- `-0.1` extra digits outside box
- `-0.1` length penalty
- `+ small` Hamming similarity（初期だけ）

#### late reward
- almost exact-only
- format bonus少量
- Hamming rewardは切る

### なぜ Hamming を初期だけ使うか
完全 sparse だと hard binary で何も学べないからです。  
ただし最終的には exact-only に寄せないと、1-bit near-miss に最適化される危険がある。

---

# GPRO が binary に有効かを最短で確かめる進め方

## 結論
最短で知りたいのは、

1. **outcome-centric 学習で collapse を減らせるか**
2. **format 改善だけでなく strict exact 8-bit が少しでも動くか**
3. **その signal を持ったまま GRPO に入れるか**

です。

したがって、確認順は次がよい。

### Probe A: binary-only answer-only SFT / RFT
目的は「短い exact boxed output に閉じるか」を見ること。

見る指標:
- `Binary Hard Set` strict exact 8-bit
- `verified_trace_ready` exact
- `bit_structured_byte_formula` exact
- `last_number` 失敗数
- 平均出力長

ここで少なくとも、
- output length が縮む
- `last_number` が減る
- general / symbol を壊さない

の 3 つは確認したい。

### Probe B: binary-only ORPO
目的は「collapse を直接叩いたときに、この model が outcome learning で動くか」を見ること。

見る指標:
- strict exact 8-bit
- boxed regex rate
- leading-zero 保持
- `last_number` 失敗数
- 平均出力長

#### Probe B の読み方
- format/length は改善、exact は不変  
  → outcome 方針自体は妥当。reasoning 改善はまだ足りないので GRPO へ進む
- exact も少し動く  
  → binary で outcome-centric learning が効いている。GRPO に上げる価値が高い
- format も exact も動かない  
  → そのまま GRPO へ行かず、chosen/rejected か warm start を作り直す

### Probe C: small synthetic GRPO
ここで初めて GRPO を始める。

ただし最初は、
- real binary 直打ちではなく synthetic easy-medium
- reward は exact + format + length の early shaping
- strict exact が立ち上がったら late reward へ寄せる

とし、**small synthetic で signal が出るか**を先に見る。

### Probe D: synthetic hard + real verified GRPO
Probe C で signal が出たら、
- structured byte
- choose/majority
- ambiguity-rich
- leading-zero heavy

を増やし、そこへ real verified を混ぜる。

### Probe E: real all-non-exclude GRPO
最後に `manual_audit_priority` も late-stage prompt / rollout success 由来の positive として入れる。

## 実務上の判断
要するに、

- **「GRPO が有効か」だけを早く知りたいなら ORPO probe まででよい**
- **「binary を本当に押し上げられるか」まで見たいなら small synthetic GRPO まで入る**

この順なら、いきなり長い real-binary GRPO を回して

- exact は動かない
- output だけ長くなる
- non-binary を巻き添えで壊す

という失敗をかなり避けられる。

---

# なぜ「ORPOよりGRPOが本命」なのか

## あなたの結果が示すこと
- boxed 率だけ上げても binary verified はほぼ動かない
- wording変更では structured-byte が動かない
- gold byte 自体が出ていないことが多い

つまり binary の中心は
**「答え方」より「答えを見つける policy」**です。

### ORPO
- 答え方改善: 強い
- 答えを見つける能力: 限定的

### GRPO
- 答え方改善: reward で可能
- 答えを見つける能力: synthetic + verifier があれば押せる

なので binary の本丸に賭けるなら **GRPO > ORPO** です。

---

# ただし、最初の cheap probe としては ORPO が非常に良い
ここは実務的に重要です。

もし compute / 実装工数を抑えて判断したいなら、  
まずやるべきは **binary-only ORPO probe** です。

## ORPO probe の目的
- この model が outcome-centric 学習で動くか
- long-output collapse をどれだけ減らせるか
- answer-only / chosen-vs-rejected で binary exact が少しでも動くか

### この probe で見たい指標
- strict exact binary accuracy
- `verified_trace_ready` exact
- `structured_byte_formula` exact
- avg output length
- `last_number` rate
- `boxed regex` rate

### 判定
- format は改善するが exact が動かない  
  → reasoning 強化が必要。GRPOへ進む。
- verified / structured も少し動く  
  → outcome-centric 方針は正しい。GRPOの前段として有望。

---

# 昇格ゲートと中止条件

## 共通原則
- binary は **Kaggle mimic** と **strict exact 8-bit** を両方記録する
- candidate 昇格は **strict exact 8-bit 主体**で判断する
- `General Stable Set` と `Symbol Watch Set` を落として binary だけを上げた candidate は昇格させない

## ORPO probe の昇格ゲート
ORPO probe は、少なくとも次のどれかを満たした時だけ次段へ進める。

1. `Binary Hard Set` の **strict exact 8-bit** が `12/60` 以上  
2. `verified_trace_ready` strict exact が `8/20` 以上  
3. `bit_structured_byte_formula` strict exact が `1/14` 以上

加えて、次は必須条件とする。

- `General Stable Set >= 188/200`
- `Symbol Watch Set >= 24/60`
- `last_number` 失敗数が直近 anchor より悪化しない

## GRPO candidate の昇格ゲート
GRPO candidate は、少なくとも次を満たさない限り merge 候補にしない。

- `Binary Hard Set` strict exact が **現行 best exact** を上回る
- `verified_trace_ready` strict exact が **7/20 を上回る**
- `bit_structured_byte_formula` strict exact が **0/14 のままではない**
- `General Stable Set >= 188/200`
- `text >= 43/50`
- `gravity >= 47/50`
- `Symbol Watch Set >= 24/60`

## 明示的な中止条件
次が起きた run は、その方向を一旦止める。

- binary strict exact が動かないまま output length だけ伸びる
- `last_number` 失敗が再増加する
- hybrid narrative のように non-binary family まで巻き添え退行する
- strict exact は不変で Kaggle mimic だけが伸びる

---

# 私ならこう進める

## 最優先の戦略判断
### **shared SFT で binary trace をいじる路線は縮小**
### **binary-specialist outcome optimization に移行**

---

## 実験優先順位

### 実験1
**Binary-only answer-only specialist SFT**
- データ: binary 全 non-exclude
- 出力: 80-90% `\boxed{answer}` only
- 少量だけ短い structured one-liner
- 目的: trace を捨てて outcome-only が効くか確認

### 実験2
**Binary-only ORPO**
- chosen: gold boxed
- rejected: current model wrong outputs + synthetic hard negatives
- 目的: collapse 抑制と short exact closure

### 実験3
**Binary synthetic curriculum + RFT**
- solver-generated prompt から多サンプル
- correct だけ蒸留
- 目的: GRPO前の warm start

### 実験4
**Binary-only GRPO**
- synthetic 중심 -> real mix
- exact reward + format + length
- 目的: rule induction の本丸改善

### 実験5
**G + B merge**
- TIES / DARE / SVD 比較
- 目的: binary gain を general に持ち込む

---

# 重要な追加ポイント

## 1. binary では “reasoning trace purity” より “verifiable success density”
今までは trace-safe を重視していた。  
それは SFT CoT としては正しい。

でも今の段階では、
**binary は高品質 trace 不足ではなく、正解 trajectory 密度不足**です。

だから
- solver-generated synthetic
- rejection sampling
- verifier-based RL

が効く可能性が高い。

---

## 2. binary specialist では “短さ” を報酬に入れるべき
あなたの結果は一貫していて、

- binary/text/symbol の誤答は長い
- hybrid は長くなって悪化した

なので binary specialist は
**短いこと自体を reward / preference に入れるべき**です。

---

## 3. exact metric を主指標に固定する
今後 binary は必ず両方見るべきです。

- Kaggle mimic
- strict exact 8-bit

ただし研究・改善判断は **strict exact を主**にすべきです。  
そうしないと again pseudo-gain に騙されます。

---

## 4. 同じ枠組みは後で symbol glyph にも使える
これは副次効果ですが大きいです。

`glyph_len5` も
- trace-safe teacher が乏しい
- final answer は exact string
- train answer は known

なので、binary で outcome-centric specialist + RLVR が機能したら、  
**次に glyph に横展開できる**。

0.9 を狙うならここも後で効いてきます。

---

# 最終判断

## ORPO はやるべきか？
**Yes。**  
ただし **本命ではなく、cheap probe + format disciplinarian** として。

---

## GRPO はやるべきか？
**Yes。むしろ binary の本命はこっち。**  
ただし条件付き。

### 条件
- binary-specialist でやる
- synthetic curriculum を先に作る
- answer-only / RFT / ORPO で warm start する
- exact + shortness + box discipline の reward 設計をする
- general adapter とは分離し、最後に merge する

---

## 一番有効な戦略を一文で言うと
**binary を CoT問題として扱うのをやめ、  
全 non-exclude binary 行 + solver-generated synthetic を使った outcome-centric specialist を作り、  
RFT/ORPOで出力規律を固めた後に GRPO で exact byte reasoning を押し、最後に general adapter と mergeする。**

---
