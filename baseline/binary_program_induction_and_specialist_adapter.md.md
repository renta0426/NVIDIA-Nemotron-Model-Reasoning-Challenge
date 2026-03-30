まず外部の事実関係と、似た成功パターンをざっと当たりにいきます。特に  
1) Nemotron / 評価仕様上の制約  
2) reasoning LoRA で起きやすい multi-task interference  
3) binary 系のような algorithmic task に効く学習設計  
を確認します。以下、かなり本気で「次に何をやるべきか」を整理します。  
結論から言うと、**今の壁は「binary をもっと混ぜれば解ける」種類ではない**です。  
やるべきなのは、

1. **学習パイプラインのミスマッチ修正**  
2. **binary を “自然言語CoT問題” ではなく “プログラム同定問題” として再設計**  
3. **他タスクを落とさないために、単一SFT一本勝負をやめて specialist adapter + merge に寄せる**  

です。

---

# まず全体診断

あなたの資料から見ると、現状の停滞はかなり筋が通っています。

- `FINAL_SUMMARY_REPORT.md` より、学習に安全な core は  
  - `verified_trace_ready = 6,486`
  - `answer_only_keep = 1,397`
  - 合計 `7,883`
- そのうち binary は
  - `1,004 verified`
  - `281 answer_only`
  - `302 manual`
  - `15 exclude`

一方で今の学習は、

- **600件だけ**
- **各 family 100 件均等**
- **verified only**
- **2 epoch**
- **自然文っぽい短い rule-based CoT**
- **単一 LoRA**

です。  
これは「ベースラインとしては優秀」ですが、**0.85-0.9 を狙う設計ではない**です。

特に厳しいのは次の3点です。

---

## 問題1: 600件均等サンプルは、今の目的に対して小さすぎる

`build_rule_based_training_dataset.py` は 6 family × 100 の完全均等です。  
これは比較のためには綺麗ですが、**難易度差・データ量差・干渉リスク**を無視しています。

- easy family は 100 でも十分
- binary は 100 では全然足りない
- symbol もたぶんまだ弱い
- しかも `answer_only_keep` を完全に捨てている

つまり今の 600-row セットは、  
**「全体の粗い底上げ」には効いても、難所突破には設計上向いていない**です。

---

## 問題2: binary 用の教師が「正しいっぽいが学習上は弱い」

今の binary trace は例えば

> The examples match the verified bit rule X. Applying that same transformation to query gives answer.

という形式です。  
これは**人が読むと正しい**ですが、モデル学習上は弱いです。

なぜなら binary の本質は、

- rule 名を知ることではなく
- **query に具体適用して**
- **8bit を壊さず出すこと**

だからです。

つまり binary では
- 「rule が何か」
- 「query の各中間変換が何か」
- 「最終 8bit が何か」

が必要で、今の trace はその中で一番大事な  
**“適用過程” がほぼ欠けている**。

これは他タスクではそこまで致命傷にならないが、binary では致命傷になりやすいです。

---

## 問題3: binary を強化すると他が落ちるのは、かなり自然

これは異常ではなく、**典型的な gradient interference / catastrophic forgetting** です。

特に今の設定だと、

- rank 32 の単一 LoRA
- all-linear で全層広く更新
- 1つの adapter に全 task を押し込む
- binary だけ大量混入すると、出力スタイル・内部回路が変わる

ので、binary 改善と引き換えに

- text の復号
- unit / gravity の整形
- symbol の既存規則

が落ちるのはかなりあり得ます。

なのでこの問題は  
**「binary データ量をもっと増やす」だけでは解けません。**  
**学習方式を変える必要があります。**

---

# 重要な戦略転換

## 結論
今後は **1本の学習ループで全部解決しようとしない** 方がいいです。

狙うべき設計は：

### レイヤーA: まず general adapter を作る
- easy family と既に強い family を安定して解かせる
- formatting を安定化
- 既存 0.65-0.7 をベースアップ

### レイヤーB: binary specialist adapter を別で作る
- binary だけに集中
- trace は自然文ではなく executable scratchpad/DSL
- 可能なら synthetic / solver / RL もここに入れる

### レイヤーC: 最後に merge / compress する
- general を壊さず binary を足す
- 最終提出は rank<=32 の単一 LoRA に圧縮

これが、  
**「binary を上げたいが他を落としたくない」**  
に対する一番本筋の解です。

---

# 優先順位つき改善プラン

---

# Phase 0. まず評価系を作り直す

これは最優先です。  
LB だけ見ていると改善方向を誤ります。

## 0-1. family別 + failure type別の offline eval を作る
最低でも以下を毎回出すべきです。

### 全体
- overall accuracy
- family別 accuracy
- template_subtype別 accuracy
- prompt長別 accuracy
- example数別 accuracy

### binary 専用
- `boxed` 抽出成功率
- extracted answer が `^[01]{8}$` を満たす率
- 先頭ゼロ保持率
- format failure率
- format OK だが中身誤り率
- solver family別精度  
  (`affine`, `structured_byte`, `boolean2`, `boolean3`, `manual-origin` など)

これをやると、binary の失敗を
- 推論失敗
- 形式失敗
- ambiguity失敗
に分けられます。

---

## 0-2. ランダム split ではなく「ルール族 holdout」を作る
binary はランダム split だと過大評価しやすいです。  
理由は、同じような family が train/valid に両方入るから。

### 推奨する split
- `bit_structured_formula_abstract_family` ベース holdout
- `teacher_solver_candidate` ベース holdout
- examples数 / gap構造 / unresolved cluster ベース holdout
- prompt signature ベース holdout

つまり、
**“同じ規則の言い換え” を跨がない validation** を作る。

これをやらないと、binary 改善っぽく見えて実際は memorization になります。

---

## 0-3. 干渉監視用の「固定 benchmark」を作る
以下 3 本を固定する。

- `General Stable Set`  
  easy family から 50-100 × 各 family
- `Binary Hard Set`  
  binary の verified / answer-only / manual近傍
- `Symbol Watch Set`  
  symbol の主要 slice

新しい実験は必ずこの3本で見る。  
binary が上がって general が落ちたら即検知できるようにする。

---

# Phase 1. 学習パイプラインの根本修正

これは binary 専用より先にやる価値があります。  
かなり高ROIです。

---

## 1-1. 「全文 loss」っぽい現状をやめて assistant-only loss にする
今の `train_rule_based_cot_baseline.py` は、  
テキスト全体を `dataset_text_field="text"` で投げています。

この形だと実質、
- user 側トークン
- assistant 側トークン
の両方に損失が乗る可能性が高いです。

これは reasoning SFT としてかなり不利です。

### なぜ悪いか
- 容量を prompt 再現に使ってしまう
- 長い prompt の比重が大きくなりすぎる
- assistant の exact output 学習が薄まる
- binary の最終 8bit 出力に必要な容量が削られる

### 方針
- **completion-only / assistant-only loss**
- 可能なら assistant mask 付き chat template を使う
- 少なくとも user tokens は loss 対象から外す

これは全 family に効くはずで、  
特に binary の exact output に効く可能性が高いです。

---

## 1-2. 学習時 chat template を推論時と一致させる
評価コードでは

- `tokenizer.apply_chat_template(...)`
- `enable_thinking=True`
- `add_generation_prompt=True`

です。

一方、学習コード側は `enable_thinking=True` を明示していません。  
ここにテンプレート差分があると、**推論時の思考モードと学習時の出力モードがズレる**可能性があります。

### 方針
- 学習時も推論時に極力合わせる
- `<think>...</think>` の delimiters が Nemotron の thinking template と整合するか確認
- 可能なら train / infer を同一 template path に統一

これは派手ではないですが、  
**「なぜか本番で出力スタイルが崩れる」系の事故を減らす**のに重要です。

---

## 1-3. まず 600件制約を外す
率直に言うと、  
**600件はベースラインには良いが、上位狙いには少なすぎる**です。

少なくとも次の3系統は作るべきです。

### dataset A: general verified
- `verified_trace_ready` を広く使う
- easy family の安定性確保

### dataset B: binary verified + binary answer-only
- binary 専用
- verified は scratchpad 付き
- answer_only は boxed-only か ultra-short

### dataset C: format hardening
- 全 family 共通
- `\boxed{}` 終了を徹底
- boxed の後ろに数字を書かない
- binary は 8bit 固定を徹底

現状はこれらを全部 600 件に押し込んでいるので、設計自由度が足りません。

---

## 1-4. `all-linear` 一本を疑う
binary 強化で他が落ちるなら、更新範囲が広すぎる可能性があります。

### 試すべき比較
- all-linear
- attention-only
- MLP-only
- 上位N層のみ
- 上位層 attention + MLP 限定

binary は algorithmic / circuit-like なので、  
**全層広く触るより、上位層中心の方が他タスクを壊しにくい**可能性があります。

これは後の specialist adapter 設計にも直結します。

---

# Phase 2. データ戦略の作り直し

---

## 2-1. verified と answer-only を役割分離する
`FINAL_SUMMARY_REPORT.md` の tier 設計はかなり良いです。  
問題は、今の学習がその粒度を十分活かしていないことです。

### 推奨ルール
- `verified_trace_ready`  
  → trace 教師の本体
- `answer_only_keep`  
  → final answer / formatting 安定化用
- `manual_audit_priority`  
  → 生のまま入れない
- `exclude_suspect`  
  → 入れない

これはそのままでいいです。  
ただし、**混ぜ方をもっと設計する**べきです。

---

## 2-2. trace 教師と answer-only 教師を別テンプレートにする
今後は同じ出力形式にしない方がいいです。

### trace 教師
```text
<think>
rule=...
query=...
apply(...)=...
result=...
</think>

\boxed{...}
```

### answer-only 教師
```text
\boxed{...}
```

または

```text
<think>Apply the same verified rule to the query.</think>

\boxed{...}
```

### 理由
- verified には reasoning 学習をさせたい
- answer-only では余計な hallucination を入れたくない
- binary は long CoT が逆効果になりやすい

**answer-only に雑な synthetic CoT を付けない**  
というあなたの方針は正しいです。そこは維持でいいです。

---

## 2-3. family均等サンプリングをやめる
今後は
**均等 quota** ではなく **目的別 mixture** にすべきです。

### 例
- general stability 目的: easy family 多め
- binary 改善目的: binary verified を強める
- interference 防止: non-binary replay を固定比率で混ぜる
- formatting 目的: short answer-only を必ず混ぜる

### 発想
「family を平等に扱う」のではなく  
**“性能ボトルネックに応じて配分する”**。

今は binary が壁なので、binary はデータ量だけでなく  
**データ形式の比率**も変えるべきです。

---

## 2-4. easy family は “守る” ための replay に使う
easy family はこれ以上 reasoning を深く教える対象ではなく、  
**壊さないためのアンカー**として使うのが良いです。

例えば
- roman
- gravity
- unit

は精度が高いなら、長い trace で学ばせ直すより
- short stable completion
- boxed formatting
- 数値整形
を中心に使う。

これで binary 専門化による副作用を下げられます。

---

# Phase 3. binary を「program induction」として再設計

ここが本丸です。

---

## 3-1. binary の trace を自然文から DSL/scratchpad に置き換える
今の binary trace の最大の弱点は、  
**計算の中身がほぼ無い**ことです。

binary は以下のような形式にした方がいいです。

```text
<think>
family=binary
rule=xor(rol1(x), shl2(x))
query=00110100
rol1(query)=01101000
shl2(query)=11010000
xor=10111000
result=10111000
</think>

\boxed{10111000}
```

もちろん rule が affine なら affine で、
structured byte なら structured byte でよいです。

### これの利点
- rule と適用が分かれる
- 先頭ゼロが保持されやすい
- 「それっぽい説明」で誤魔化せない
- query への concrete application を学べる

binary は自然文 CoT より、  
**短い executable scratchpad** の方が相性が良いです。

---

## 3-2. external AI CoT をそのまま教師にしない
これは既に経験済みだと思いますが、失敗理由はかなり明確です。

### 失敗理由
- 外部AIの CoT は人間にはもっともらしく見える
- でも binary では 1 bit の誤りが致命傷
- しかも自然文は execution semantics を持たない
- だから学習すると「雰囲気 reasoning」だけが増える

### 今後の方針
外部AIは使うとしても **teacher ではなく proposer** にする。

具体的には、
- AI に rule 候補を出させる
- それを DSL に変換
- 全 examples に再実行
- query でも実行
- 一致したものだけ採用

つまり  
**LLM-generated CoT ではなく LLM-assisted search** にする。

---

## 3-3. unresolved binary の solver DSL をさらに広げる
あなたの現行 solver はかなり強いです。  
ただ、それでも `302 manual` 残っている。

ここは「もっと頑張って人力で見る」より  
**DSL を 1 段拡張する**方が筋がいいです。

### 優先的に追加したい候補
#### A. byte-expression 深さ拡張
現行 structured byte formula を、深さ2→3 相当に少し広げる。

候補 primitive:
- `x`
- `~x`
- `rol/ror k`
- `shl/shr k`
- `reverse`
- `nibble_swap`

候補 combine:
- `xor`
- `and`
- `or`

#### B. choose / majority の明示 family
README / prompt 文面でも示唆されているので、
- `choose(a,b,c) = (a&b) | (~a&c)`
- `majority(a,b,c) = (a&b) | (a&c) | (b&c)`

を structured primitive として明示的に扱う。

#### C. sparse bit-circuit synthesis
未解決行の「一部 bit だけ説明不能」を埋めるため、
各 output bit を
- 入力 bit
- transformed source bit
の sparse boolean expression として SAT/SMT/CEGIS で合成する。

#### D. MDL / minimal program disambiguation
複数 rule が examples に一致するなら
- 最短
- 最低深さ
- 最少 primitive 数
- family support が高い
などで順位付けし、
さらに **query answer consensus** があれば answer-only に昇格。

---

## 3-4. 「trace-ready と answer-only の中間」を増やす
binary の難所は、trace-ready 一意化できなくても  
**query の答えだけは高確度に決まる**ケースがあるはずです。

あなたはすでに consensus 系 recovery を使っていますが、  
ここをもっと体系化すると強いです。

### 新たに作る tier
実質的には answer-only 内部を分ける。

- AO-Strong  
  多数 DSL で query answer 一致
- AO-Medium  
  少数候補一致
- AO-Weak  
  query-only hit だが family support 弱い

学習では
- AO-Strong は boxed-only で使う
- AO-Medium は低ウェイト
- AO-Weak は使わない

これで binary の training signal を増やせます。

---

## 3-5. binary 用 synthetic データを本格生成する
ここはかなり大きな伸びしろです。

今の real binary は 1,602 行しかありません。  
many-small-families なので、生データだけでは足りないです。

### やるべきこと
今ある verified / structured families から
**同じ task 形式の synthetic puzzle を大量生成**する。

各 synthetic sample は
- 7〜10 examples
- query 1本
- 8bit I/O
- 例数・Hamming weight 分布を real に寄せる
- プロンプト文体を real に寄せる

### 重要
easy ルールだけ大量生成すると逆効果です。  
以下を必ず混ぜる。

- leading zero が多いケース
- 同じ Hamming weight の紛らわしいケース
- shift / rotate / reverse が競合しやすいケース
- 複数 rule が見かけ上一致しやすい near-miss ケース
- choose / majority 系
- structured byte の hard slice

### 目的
- モデルに「I/O examples から latent rule を読む」回路を作らせる
- real rows の丸暗記ではなく、**binary reasoning の inductive bias** を作る

これはかなり本命です。

---

# Phase 4. 他タスクを落とさないための adapter 戦略

ここが「binary を上げると他が落ちる」への本命対応です。

---

## 4-1. 単一 adapter 直訓練ではなく、specialist adapter を別々に作る
一番おすすめの構成です。

### Adapter G: General
- easy family + text + strong symbol slice
- formatting hardening
- 既存強み維持

### Adapter B: Binary Specialist
- binary verified
- binary answer-only
- binary synthetic
- 必要なら binary RL

### Adapter S: Symbol Specialist（必要なら）
- symbol の中でも改善余地が大きい部分のみ

---

## 4-2. 最後に merge する
最終提出は1個の LoRA である必要がありますが、  
**学習途中は複数 adapter でよい**です。

最後に
- weighted sum
- task arithmetic
- TIES / DARE / SVD merge
- rank 圧縮

で単一 LoRA にします。

### この方針の利点
- binary 強化が general を壊しにくい
- merge weight を validation で調整できる
- 「binary をどこまで足すと他が落ちるか」を可視化できる

これは今回の問題設定にかなり合っています。

---

## 4-3. rank 配分を“仮想的に”分割する
最終 rank<=32 制約があるので、  
感覚としては

- general 用 rank
- binary 用 rank
- symbol 用 rank

を別々に学習して、最後に rank 32 に圧縮するイメージです。

例えば発想としては
- G を rank 16
- B を rank 16
- merge 後に SVD で 32 へ
みたいな考え方です。

厳密な数値は後でよいですが、  
**1本の rank 32 に全能力を一発で入れる**よりずっと合理的です。

---

## 4-4. binary specialist は更新範囲を狭める
binary 専門 adapter では
- 上位層のみ
- MLP寄り
- あるいは一部 attention 限定

を試す価値があります。

理由は、
binary は algorithmic mapping 寄りで、  
**全層を大きくいじると文系タスクを壊しやすい**からです。

---

# Phase 5. 学習形式をタスク別に分ける

これは地味に効くと思います。

---

## 5-1. 全 family 同一出力形式をやめる
今は全部 `<think> ... </think> \boxed{}` ですが、  
最適な形式は family ごとに違う可能性が高いです。

### 推奨
- roman / gravity / unit: short think or answer-only
- text: short mapping-style think
- binary: DSL scratchpad
- symbol: operator-local short structured think
- answer-only rows: boxed-only

評価は最終 answer だけなので、  
**family に応じて最短で安定する出力形式**を採るべきです。

---

## 5-2. binary は “長文 CoT” より “短い構造化思考”
binary では、長い自然文 reasoning はむしろ危険です。

### 理由
- 数字断片が多くなる
- extraction failure の温床になる
- 8bit exact string と自然文 token prior が競合する

なので binary の教師は
- 短い
- 構造化
- 実行可能
であるべきです。

---

## 5-3. answer-only データは boxed-only を混ぜる
これは format 安定化に効きます。

特に binary では
- `\boxed{00110100}`
だけを返す訓練をかなり混ぜてよいです。

もちろん reasoning 能力が落ちないよう verified trace と併用しますが、  
**“最後は短く閉じる” 習慣** をつける意味で重要です。

---

# Phase 6. RL / preference 学習は “後段” ならかなり有望

いきなり RL に行くより、  
**SFT を整理した後で binary specialist にだけ使う**のが良いです。

---

## 6-1. binary synthetic に対する verifiable RL
binary は reward を完全自動化できます。

### reward
- exact answer: +1
- `\boxed{}` 形式: +α
- 8bit regex exact: +β
- trailing numeric noise: -γ

### 対象
- synthetic binary task
- solver で正解が完全にわかる real-like prompt

これはかなり相性が良いです。  
理由は、binary がまさに **verifiable reasoning task** だから。

---

## 6-2. DPO/ORPO で format-only を矯正
生成ミスが
- `1`
- `10`
- `-0`
みたいな collapse なら、そこは reasoning 以前に output style の問題です。

### できること
- 正解 completion: `\boxed{00110100}`
- 不正 completion: `1`, `10`, `001`, `-0`, boxed後に追加数字あり

の pair を作って DPO/ORPO する。

これは特に binary formatting に効く可能性があります。

---

## 6-3. ただし RL は単一 adapter 直上書きしない
binary RL を general adapter に直接かけると壊れやすいです。  
やるなら
- binary specialist adapter
- その後 merge
が安全です。

---

# 「今の方針がなぜ詰まっているか」の整理

あなたの現行方針が悪いというより、  
**既にやるべき easy part はかなりやり切っている**状態です。

特に詰まっている理由は以下です。

---

## A. binary の “教師の質” が足りない
単なる rule label では、モデルは query 適用を学べない。

---

## B. binary の “データ量” より “データ表現” が足りない
100例に自然文 trace を足しても効きにくい。  
必要なのは executable scratchpad。

---

## C. 単一 LoRA で全部やっている
binary のような algorithmic 専門化は、他 family を壊しやすい。

---

## D. 学習 objective がまだ最適化されていない
assistant-only loss / template一致 / format hardening が未完。

---

# 最も重要な実験順

もし私なら、次の順でやります。

---

## 実験1: 学習 plumbing 修正だけで再ベースライン
### 変更点
- assistant-only loss
- train/infer template整合
- 600件ではなく curated を広く使用
- short answer-only を混ぜる

### 目的
まず「単純な学習ミスマッチ」を潰す。

### 期待
binary 以外も含めて全体底上げ。  
これは high ROI。

---

## 実験2: binary trace を DSL scratchpad 化
### 変更点
- binary verified のみ対象
- 自然文 trace をやめる
- rule + query apply + result を短い構造化形式にする

### 目的
binary reasoning を本当に学べる教師へ変える。

### 期待
format failure 低下 + binary精度上昇。

---

## 実験3: general adapter / binary specialist adapter を分離
### 変更点
- G と B を別学習
- merge weight を validation 探索

### 目的
binary 改善と他タスク維持を両立。

### 期待
「binary 上がると他が下がる」の本命解消。

---

## 実験4: binary synthetic を投入
### 変更点
- verified DSL family から大量生成
- real-like prompt
- leading-zero / near-miss 強化

### 目的
many-small-families に対する inductive bias 学習。

### 期待
real dataの薄さを補う。

---

## 実験5: binary specialist にだけ RL / DPO
### 変更点
- verifiable reward
- exact boxed + 8bit + no trailing noise
- specialist のみに適用

### 目的
最後の exactness を押し込む。

### 期待
特に format collapse を削る。

---

# 0.85-0.9 を目指す上での現実的な見立て

ここは重要です。

もし family が概ね均等なら、  
**binary だけ完全解決しても 0.85-0.9 に届かない可能性があります。**

なぜなら今 `0.65-0.7` なら、
- binary だけでなく
- symbol か、あるいは他の微妙な取りこぼし
も残っている可能性が高いからです。

なので戦略としては、

1. **binary を specialist 化して大きく改善**
2. **general adapter で easy family を守る**
3. **次点で symbol の specialist も作れる構造にする**

がいいです。

つまり、  
**binary は最大の壁だが、最終目標には “干渉を抑えた multi-specialist 設計” が必要**です。

---

# 実行ロードマップ案

---

## Sprint 1: すぐやるべき
- offline eval 強化
- assistant-only loss
- train/infer template整合
- 600件制約撤廃
- verified / answer-only 混合の基本設計
- binary format hardening dataset 追加

### ここで見る指標
- overall
- family別
- binary format failure率
- other family drop の有無

---

## Sprint 2: binary 教師の再設計
- binary scratchpad DSL
- verified binary 全件変換
- answer-only binary は boxed-only or ultra-short
- strong AI CoT の再利用は verifier 通過分のみ

### ここで見る指標
- binary verified slice accuracy
- 8bit regex exact率
- 先頭ゼロ保持率

---

## Sprint 3: specialist adapter + merge
- General adapter
- Binary adapter
- 必要なら Symbol adapter
- merge / SVD compress
- weight探索

### ここで見る指標
- binary gain
- non-binary retention
- merged adapter の総合点

---

## Sprint 4: synthetic + RL
- binary DSL generator
- hard-negative / ambiguity-rich prompts
- verifiable RL or DPO
- specialist のみ更新
- merge 再最適化

### ここで見る指標
- binary hardest slice
- private-like holdout
- general side-effect

---

# 特に強く推したい3つ

最後に、優先度だけ絞るならこの3つです。

---

## 最優先1: 600件均等 baseline を卒業する
今の 600件はもう役目を終えています。  
次は **7,883 curated を活かす設計** に進む段階です。

---

## 最優先2: binary trace を “説明文” から “実行痕跡” に変える
binary は自然文 CoT ではなく、
**DSL / scratchpad / query適用過程** が要る。

---

## 最優先3: binary 専門 adapter を別に作って merge する
これが  
**「binary を上げると他が落ちる」**  
への最も本質的な解法です。

---

# まとめ

あなたの現状は、かなり正しいところまで来ています。  
むしろ問題は、**今のやり方の延長では壁を越えにくい段階に入った**ことです。

次に必要なのは「もう少し頑張る」ではなく、設計の切り替えです。

## 次の設計思想
- **binary = language CoT 問題ではなく program induction**
- **一発 mixed SFT ではなく specialist 分離**
- **自然文 trace ではなく executable scratchpad**
- **verified / answer-only / format hardening を役割分離**
- **最後は merge で単一 LoRA 化**
