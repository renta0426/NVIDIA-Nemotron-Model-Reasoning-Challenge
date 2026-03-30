2026-03-30 更新: 現在地

- 公式の判断基準は `README.md` の Evaluation / Submitting（特に 31-49 行付近）を最優先とする。
- 現在の本線は `versions/v5/code/train_transformers_submission_v5.py` に集約した **単一ファイルの Transformers + PEFT pipeline**。
- ベースモデルは `models/nemotron-3-nano-30b-a3b-bf16` を使う。6bit/MLX 系は現行本線から外す。
- `official_bf16_smoke_run3` は Kaggle 本番で受理され、スコア `0.5` を確認済み。提出互換性は通った。
- `official_bf16_pilot32_run1` と `official_bf16_run128_r16_run1` は完了済み。
- 現在は `official_bf16_run256_r16_ep2_run1` / `official_bf16_run256_r24_ep2_run1` / `official_bf16_run256_r24_ep2_len1024_run1` を MPS で並列学習中。
- `official_bf16_run256_r16_ep2_lowlr_run1` と `official_bf16_run256_r16_ep2_len1024_run1` は RAM 圧迫と early signal を見て停止済み。
- `evaluate-pack` は v5 単一ファイルに実装済みだが、Mac/MPS + thinking ON は極端に遅いので reduced-row で段階評価する。
- 以降、この文書内に古い仮説が残っている場合は **README とこの更新内容を優先**する。

まず、外部一次ソースを確認して、
1) 採点実コードと公開説明の差分
2) Nemotron-3-Nano-30B の推論/テンプレ/LoRA互換条件
3) vLLM/PEFT/TRL/Transformers の現行ベストプラクティス
4) Apple Silicon/Mac Studio 側の実運用制約
を整理します。 その前提に基づいて「即実装レベル」の戦略一覧に落とします。了解。
「Mac Studio 512GB は official BF16 + Transformers + PEFT の多並列実験の主戦場」「必要なら Kaggle CUDA は有望レシピの再現・検証に使う」 という制約で、top10 / 0.9+ を最も堅く狙うための、試すべき戦略を全部入りで、即実装レベルまで落として整理する。

結論だけ先に言う。

結論: 勝ち筋はこれ

このコンペで一番堅いのは、solver/distillation 主導の template-aware LoRA です。

具体的には:

1. README 契約に一致したローカル評価・提出基盤を作る
   - 特に `max_lora_rank=32`, `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, `max_model_len=8192` を正とする
   - `\boxed{}` 優先抽出と `submission.zip` 互換性を前提にする
   - 公開 metric notebook の既定値差分は補助情報として扱い、最終判断は README を優先する

2. 6テンプレートを family ごとに分解して、
   - exact solver / parser を作る
   - real data を family 別に解析
   - family 近傍 synthetic を作る
   - 最終答えの canonical form を family ごとに固定する

3. SFT を2段階以上でやる
   - Stage A: real + core synth で reasoning 能力を壊さず generalist を作る
   - Stage B: hard synth + format sharpening で出力を安定化
   - 余力で Stage C: RFT / GRPO / RLVR

4. 最終出力は extraction-aware に最適化する
   - \boxed{} は万能ではない
   - 特に 答えに } が含まれるケースは boxed が危険
   - safe case / unsafe case で出力方針を分ける

5. Mac では Transformers + PEFT + MPS を主軸に、単一ファイル pipeline を多並列で回す
   - SFT sweep
   - smoke / validate / submission packaging
   - reduced-row official-style eval
   - hard case mining
   - memory monitoring
   - 有望 recipe だけを追加 submit / 必要時 CUDA 再現へ回す

以下、優先度順に全部書く。

0. まず固定する前提

これは全戦略の土台。

0-1. 正とする評価条件
`README.md` の Evaluation / Submitting を絶対基準にする。

- temperature=0.0
- top_p=1.0
- max_tokens=7680
- max_num_seqs=64
- max_model_len=8192
- rank<=32 の LoRA adapter を `submission.zip` にまとめる
- `\boxed{}` 優先抽出に寄せる
- ローカル近似では Nemotron chat template と thinking-on 挙動も保持して本番に寄せる

公開 metric notebook の既定値ではなく、README に書かれた本番評価条件で判断する。

0-2. visible test.csv は評価に使わない
あなたの分析どおり、train と一致している。
使い道は:

- submission フロー確認
- extraction 確認
- zip 構造確認
- adapter load 確認

だけ。

0-3. 推論時 prompt は変えられない
このコンペの本質は prompt engineering contest ではなく adapter contest。

つまり本番で変えられないもの:

- system prompt
- few-shot 追加
- custom preprocessor
- 外部 solver 呼び出し
- ensembling

なので、本番で使えない推論ハックに時間を使わない。

0-4. 目標スコア設定
6 family がほぼ均衡なら、0.90 を安定で超えるには family ごとの最低ラインを持つべき。

最低KPI
- Roman: 0.995+
- Unit: 0.99+
- Gravity: 0.985+
- Bit: 0.93+
- Text decrypt: 0.90+
- Symbol/equation: 0.88+

これで全体 0.94 近辺まで見える。
top10狙いなら local OOF で 0.95 以上、hard split で 0.90 前後を目標にしたい。

1. 最優先でやるべき基盤戦略

1-1. metric 完全複製 evaluator をローカルに持つ
実装
ローカルに以下をそのまま作る:

- extract_final_answer()
- verify()
- prompt 組み立て
- README 契約の generation params
- thinking-on の near-production eval
- type別集計
- raw generations 保存

必須ログ
各サンプルごとに:

- family
- raw_output
- extracted_answer
- gold_answer
- is_correct
- format_fail
- has_boxed
- output_len
- contains_extra_numbers
- risk_flag

成功条件
- どの実験でも family別精度 / extraction fail率 / 出力長が見える
- “なぜ落ちたか” が answer level で追える

1-2. extraction 危険ケースのユニットテストを最初に作る
これはかなり重要。

テスト対象
- \boxed{42} → 42
- Final answer: 42 → 42
- 複数の \boxed{} がある
- 最後に別の数字がある
- 答えが } を含む
- 答えが \ を含む
- 答えが space を含む
- 答えが text phrase
- 答えが Roman
- boxed が空
- boxed 未閉じ

特に重要
答えが } を含む場合、\boxed{} は壊れる。
metric の regex は ` なので、中に }` が来た時点で終了*する。

つまり、symbolic family の一部では
“boxed 強制” はむしろ事故要因。

ここから導く方針
出力フォーマットは family / answer-risk に応じて変える実験を必ずやる。

1-3. 3系統 validation を作る
visible test を捨て、train から3種類の validation を作る。

Split A: stratified random
- family 比率維持
- ベースライン比較用

Split B: family-hard split
- family ごとに harder cases を holdout
- 例:
  - bit: op composition が複雑
  - gravity/unit: rounding が厳しい
  - roman: 4/9/40/90/99 周辺
  - text/symbol: rare chars / longer outputs / risky chars

Split C: template-generator shift split
- 可能なら family 内の generator signature 単位で分ける
- 例:
  - bit: inferred operation family
  - text: inferred cipher family
  - symbol: inferred transduction family
  - unit: ratio bin
  - gravity: g bin

採用基準
モデル採用は A/B/C の加重平均で判断。
A だけ良くて B/C が死ぬモデルは却下。

1-4. family classifier / parser をルールベースで作る
LLM で判定しない。regex / parser で十分。

返すもの
- family
- answer_type
- query
- examples
- format_risk_flag
- difficulty_tags

用途
- stratified split
- synthetic generation
- hard mining
- family 別 sampling
- family 別 format target

1-5. ローカル評価を “1回生成” と “多回生成” の2軸で持つ
本番は1回生成だが、学習判断では多回生成も有効。

Eval 1
- 本番相当: 1 sample @ README params（temperature=0.0）

Eval 2
- robustness: 8-view の補助比較（checkpoint / adapter / reduced-row pack）
- 指標:
  - pass@1
  - pass@8
  - majority exact-match
  - answer entropy
  - shortest-correct rate

これで何が分かるか
- 出力分布がブレているか
- correct answer を知っているのに sampling で外しているか
- SFT で足りないのか、format 崩れなのか

2. データ戦略: ここが勝負

このコンペでは、モデルアーキよりデータの質のほうが効く可能性が高い。

2-1. real データの canonicalization
やること
train.csv を family ごとに canonical 形式へ正規化したメタデータを付ける。

付与すべき列:
- family
- subfamily
- answer_type
- answer_canonical
- format_risk_flag
- difficulty
- query_len
- num_examples
- special_chars
- estimated_rule_signature
- source=real

目的
- family sampling
- validation stratification
- format 制御
- synthetic との混合管理

2-2. “real の兄弟問題” を最優先 synthetic にする
雑な synth より、これが一番勝ちやすい。

実装
各 real 問題について:

1. prompt を parser で分解
2. underlying rule / parameter を推定
3. 同じ family / 同じ subfamily / 同じ answer format を保ったまま
   - example 値だけ変える
   - query だけ変える
   - 境界ケース化する
   - 丸めだけ難しくする
4. sibling prompt を 3〜20 件生成
5. solver で answer を再計算
6. near-dup filter を通す

これが効く理由
- hidden test が train 近傍なら、最も分布が近い
- freeform synthetic より分布崩壊しにくい
- family 固有の書式・口調・例示数・長さを保てる
- LoRA が “タスク理解” より “タスク分布適応” に集中できる

family 別 sibling 生成ルール
bit
- 同じ op family のまま input examples を差し替え
- query を Hamming weight 極端ケースに変更
- 00000000, 11111111, alternating bits を増やす
- examples 7〜10 個を維持

gravity
- 同じ g で観測例だけ差し替え
- query t を 1.0〜5.0 の端に寄せる
- 1桁小数 / 2桁小数の両方を維持

unit
- 同じ ratio で例示値だけ変更
- 丸め境界に近い query を追加
- answer は必ず 2 decimal

text decrypt
- 同じ cipher/mapping で phrase だけ差し替え
- 語数 3〜5 を維持
- answer vocab を閉じた語彙に寄せる

roman
- 同じテンプレで query 数だけ変更
- 4, 9, 14, 19, 40, 49, 90, 99, 100 を厚くする

symbol/equation
- 同じ transduction class のまま query 文字だけ変更
- risky chars (}, \, `  ``) を意図的に増やす
- numeric / symbolic を別管理

受け入れ基準
- exact solver で全 examples / query が整合
- prompt 長が family 分布から逸脱しない
- near-dup similarity が閾値以下
- real validation を悪化させない

初期の量
最初は欲張らない。
real 9500 に対し sibling synth 3000〜8000 で十分。

2-3. synth は 4 プールに分ける
全部一緒に混ぜない。

Pool A: Core-ID synth
目的: real 近傍の汎化強化

- family 比率は real 近似
- sibling 中心
- prompt 長・例示数も real 近似
- 最初のベース学習用

Pool B: Hard synth
目的: 境界ケース・丸め・曖昧系の攻略

- bit 境界
- gravity/unit 丸め
- roman subtractive
- text rare mapping
- symbol risky chars

Pool C: Format synth
目的: extraction 崩れ対策

- boxed あり / なし
- final answer line only
- extra numbers を出さない
- } を含む answer の safe format
- 複数 boxed を避ける
- 最後の行だけ答えにする

Pool D: Distilled reasoning synth
目的: “どう考えるか” より “どう正答に収束するか” を学ばせる

- teacher から複数解答生成
- solver / label で検証
- shortest correct / cleanest correct を採用
- reasoning 長の異なる版を混ぜる

2-4. family ごとの generator を最初から作る
このコンペは “モデル学習” の前に “問題生成器” を持った側が強い。

2-4-1. Bit manipulation generator
ルール空間
まず op library を固定する。

- bitwise NOT
- XOR with mask
- AND with mask
- OR with mask
- left shift
- right shift
- left rotate
- right rotate
- bit reverse
- nibble swap
- parity-conditioned op
- index permutation
- conditional mask apply

生成方針
- 1〜3個の op を compose
- 8bit 固定
- examples 7〜10
- query は example と重複禁止
- answer は 8 chars exact

難度タグ
- single_op
- two_op
- three_op
- rotation_vs_shift
- mask_ambiguous
- boundary_zero
- boundary_all_ones

実装メモ
- op 列を rule_spec に保存
- examples だけ見て rule が複数候補になる場合は reject
- ambiguity check は brute force で候補 op 空間から count する

即試すべき強化
- sibling synth
- ambiguity-minimized synth
- ambiguity-maximized hard synth
- shortest-correct distillation
- answer-only sharpening

2-4-2. Gravity generator
ルール
d = 0.5 * g * t^2

サンプリング
- g: 4.91〜19.58
- example 数: 3〜5
- t: 1.0〜5.0
- output decimal: 1 or 2 digits, real 比率維持

難化
- t が接近
- 丸め境界
- 1桁/2桁混在
- g 極端値

実装ポイント
- answer canonical form を family で統一
- commas を使わない
- unnecessary trailing zero の扱いを固定
- final output は短く

即試すべき強化
- unit との混同を防ぐため文面 variation 少なめ
- “計算過程を短くして最後だけ出す” 蒸留
- numeric-only format sharpening

2-4-3. Unit conversion generator
ルール
- fixed ratio conversion
- ratio は問題内一定

サンプリング
- ratio: 0.50〜2.00
- query value: 5.0〜49.89 近傍
- examples: 3〜5
- answer: 2 decimals fixed

難化
- ratio が 0.5 近傍 / 2.0 近傍
- query が丸め閾値に近い
- examples が見た目に似る

即試すべき強化
- 2 decimal fixed-format teacher data
- “答えの前後に数値を出さない” format set
- wrong rounding correction data

2-4-4. Text decryption generator
ここは大事。
最も LLM 的で、最もノイズを入れやすい。

まず閉じた phrase generator を作る
- vocab 50〜200 語
- 3〜5 語 phrase
- 語数分布は real 準拠
- answer length 分布も real に寄せる

cipher 候補
- substitution
- Caesar/shift
- word-level permutation
- position-based char mapping
- vowel/consonant swap
- fixed affine-ish char mapping
- bigram substitution
- word-preserving letter mapping

絶対条件
- query/answer 語数一致
- reversible
- solver で復号可能
- freeform long text 禁止

hard 化
- 似た語形
- 同じ語の再利用
- rare character
- phrase length 5
- mapping collision が起きそうで起きないケース

即試すべき強化
- teacher に reasoning trace を作らせる
- solver で正誤判定
- shortest clean correct を採用
- phrase-level canonical spacing を固定

2-4-5. Roman numeral generator
これは簡単に取り切るべき family。

ルール
- 1〜100
- subtractive notation 標準
- uppercase only

hard 集中
- 4, 9, 14, 19, 40, 44, 49, 90, 94, 99, 100
- 39 / 40 / 41 の近接
- 89 / 90 / 91

即試すべき強化
- answer-only 蒸留
- boxed 1行固定
- uppercase consistency
- final-line-only

2-4-6. Symbol / equation generator
ここが最難所候補。

最初に 2 系統へ分ける
- symbol_equation_numeric
- symbol_equation_symbolic

alphabet を固定
- real で出てくる文字集合近傍に制限
- 危険文字:
  - }
  - {
  - \
  - `  ``
  - :
  - space

query/answer 長
- query 長 5 近辺
- answer 長 1〜4 を中心に維持

ルール候補
- char permutation
- position select/drop
- symbol mapping
- count-based output
- local rewrite
- digit-symbol hybrid transform
- parity/position-conditioned rewrite

hard 化
- visually similar symbols
- brace/backslash answers
- numeric / symbolic 境界
- shortest answer collisions

重要方針
この family だけは boxed 例外戦略を必ず試す。
答えに } が入るケースがあるため。

2-5. teacher-distilled high-quality traces を作る
real answer だけではなく、良い reasoning target を作る。

teacher 候補
Mac 512GB を活かして、ローカル teacher を複数走らせる。

- Qwen 系 reasoning model
- DeepSeek distill 系
- Nemotron base 自身
- 必要なら 70B 級量子化モデル

1 問あたり生成するもの
各 prompt について teacher に:

- long reasoning × 2
- concise reasoning × 2
- answer-only × 2
- format-safe variant × 1

合計 5〜7 本生成させる。

採用ルール
- solver / gold label で correct 判定
- extraction で安全か確認
- その中から
  - shortest correct
  - cleanest format
  - most stable across resampling
を採用

データ化
各問題について複数 target を持たせる:

- target_long
- target_short
- target_answer_only
- target_format_safe

学習時の混合比
最初の推奨:

- long: 20%
- short: 45%
- answer-only: 20%
- format-safe: 15%

理由:
- reasoning 能力は残す
- でも README の temperature=0.0 でも長い出力は format drift や latency の事故源なので、短い答えに寄せたい

2-6. self-consistency を “学習データ化” する
本番では multi-sample できない。
だから学習時に多数決を吸収させる。

実装
1. teacher / current student から N=8〜32 生成
2. extracted answer を集計
3. correct なものだけ残す
4. 最頻 correct を採用
5. その答えに収束する最短 trace を選ぶ

特に効く family
- bit
- text decrypt
- symbol

保存するメタ
- num_generations
- num_correct
- consensus_rate
- trace_len
- format_pass

使い道
- high-consensus examples は early stage に入れる
- low-consensus examples は hard pool に回す
- wrong-heavy examples は DPO/RL 用へ送る

2-7. “誤答→修正” データを作る
単純な正解 SFT だけだと、もっともらしい誤答が残る。

実装
1. current student で全 train/valid に生成
2. incorrect answer を回収
3. incorrect patterns を family ごとに分類
4. correction target を作る

データ形式
形式A: 直接修正版
- user: 元 prompt
- assistant: 正しい concise reasoning + final answer

形式B: 誤答比較 preference
- chosen: correct output
- rejected: model の誤答出力

誤答分類例
- bit: rotate と shift を混同
- gravity: 丸めミス
- unit: ratio 逆適用
- roman: subtractive miss
- text: partially decoded
- symbol: 位置ずれ / brace事故

これが効く理由
モデルの実際の失敗分布に合わせられるから。

2-8. format sharpening 専用データを別で作る
これは本当に重要。
Accuracy コンペだが、format failure はそのまま誤答になる。

入れるべき target 形式
safe answers 用
...短い推論...
\boxed{ANSWER}

unsafe symbolic answers 用
Final answer: ANSWER

あるいは
The final answer is: ANSWER

何を unsafe とみなすか
- } を含む
- 複数行に割れる
- backslash を含む
- boxed だと regex が誤切断しやすい

sharpening set の中身
- 同じ問題に対し
  - bad format
  - good format
を paired にする

学習法
- SFT で good だけ学習
- DPO で good > bad を学習
- last-line tokens の loss weight を上げる

2-9. near-dup / leakage 管理は厳密にやる
exact reject
- prompt 一致
- prompt+answer 一致
- same rule_spec + same query

near-dup reject
family ごとに正規化して similarity を計算。

正規化例
- 数値を `` 化
- binary を `` 化
- roman を `` 化
- phrase を token skeleton 化
- symbol を char class 化

閾値
- sibling synth では 0.92 以上の高類似は削る
- hard synth では 0.88 以上でも削る候補

2-10. “実データのうち学習価値が高いもの” を選別する
real 9500 全件を均等に使うより、価値の高い real を厚く使う。

スコアリング
各 real に対し:
- current model の正答率
- generation entropy
- extraction fail 率
- family rarity
- risk chars
- boundary-ness
- teacher disagreement

から importance_score を付ける。

使い方
- importance 高: 反復学習
- importance 低: replay 少なめ
- いつも簡単に解ける roman は薄くできる

2-11. curriculum を固定する
いきなり全部混ぜない。

推奨カリキュラム
Phase 1
- real easy/normal
- core synth
- high-consensus distilled

Phase 2
- real 全件
- core synth
- hard synth 少量

Phase 3
- hard synth 増量
- correction data
- format sharpening
- risky family over-sample

Phase 4
- DPO / ORPO / GRPO / RFT
- もしくは hard-only short finetune

family 別 oversampling 初期案
- bit: 1.3x
- gravity: 0.9x
- unit: 0.8x
- text: 1.4x
- roman: 0.6x
- symbol: 1.6x

2-12. 外部データを使うなら “task-near” のみ
使うにしても、汎用数学コーパス大量投入は危険。

使ってよい候補
- rule induction
- symbol rewriting
- short algorithmic puzzles
- exact-answer transform tasks
- deterministic cipher/decode
- small arithmetic formatting

避けるもの
- 長文数学証明
- 一般チャット
- コーディング大量
- broad instruction tuning data
- 雑多な CoT コーパス

2-13. 一番安全なデータ比率の初期値
最初の大外ししにくい配合:

- real: 50%
- sibling synth: 25%
- distilled correct traces: 15%
- hard synth: 5%
- format sharpening: 5%

次に試す配合:

- real: 40%
- sibling synth: 25%
- distilled: 15%
- hard synth: 10%
- correction/DPO pairs 起源: 10%

3. 学習戦略: SFT / DPO / RFT / RL の打ち分け

3-1. 最初の本命は all-linear rank 32 LoRA
baseline 本命
- r=32
- lora_alpha=32 or 64
- target_modules = [q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj]
- use_rslora=True
- lora_dropout=0.0 or 0.05

最初に切る比較
- A: r32 alpha32 dropout0.0
- B: r32 alpha64 dropout0.0
- C: r32 alpha32 dropout0.05
- D: r16 alpha32 dropout0.05

優先度
まず A/B/C を回す。
r16 は圧縮比較用。

3-2. target modules の探索は少数精鋭で
全部試す必要はない。順番はこれ。

優先順
1. all-linear
2. attention-only (qkv o)
3. mlp-only (gate up down)
4. qv-only

予想
このタスクは
- pattern induction
- formatting
- exact output
が重要なので、all-linear が一番勝ちやすい。

3-3. full reasoning SFT だけでなく “短答化 SFT” を混ぜる
Nemotron の thinking prior は壊したくない。
でも本番近似でも、長すぎる trace は latency と format drift の事故源にもなる。

target の混合
- long rationale
- short rationale
- answer-only
- format-safe only

を混ぜる。

具体比率
まずは:
- long 20
- short 45
- answer-only 20
- format-safe 15

さらに試すべき比率
- 30/40/20/10
- 10/50/25/15
- 0/60/25/15

3-4. completion-only loss を基本にする
user prompt には loss をかけない。
assistant 出力だけに loss。

さらにやる
assistant 内でも token weighting を分ける。

重み案
- rationale tokens: 1.0
- “Final answer” prefix: 2.0
- boxed 内 answer tokens: 4.0
- last line 全体: 3.0

狙い
- reasoning も学ぶ
- でも 最後の答え をより強く最適化する

これはかなり効く可能性が高い。

3-5. “最後の行” 重み付け学習
このコンペの本質にかなり合う。

実装
各 target から final answer span を抽出し、
その span と直前 prefix の loss weight を上げる。

例
if token in final_span:
    weight = 5.0
elif token in final_line:
    weight = 3.0
else:
    weight = 1.0

family 別重み
- symbol: final span 6.0
- bit: final span 5.0
- unit/gravity: 4.0
- roman: 4.0
- text: 3.0

3-6. 2段階 SFT が本命、3段階目で preference/RL
Stage A: Generalist SFT
- real + core sibling synth + distilled clean traces
- 目的: family 全体を底上げ

Stage B: Hardening SFT
- hard synth
- correction data
- format sharpening
- risky family oversample

Stage C: Preference/RFT/RL
- chosen/rejected pairs
- exact-answer reward
- brevity/format reward
- 小さく上積み

重要
いきなり RL から入らない。
まず強い SFT を作る。

3-7. preference 学習は DPO/ORPO を優先
GRPO は強いが、工数が上がる。
この規模ならまず DPO/ORPO/RPO 的な軽量 preference がやりやすい。

chosen / rejected の作り方
chosen
- correct
- short
- extraction safe
- final answer clean

rejected
- incorrect
- correct だが extraction unsafe
- correct だが最後に余計な数字
- wrong rounding
- wrong format

効きやすい領域
- text
- symbol
- bit
- format failure 全般

3-8. true RL より RFT がコスパ良い可能性が高い
このコンペでは、Rejection Sampling Fine-Tuning がかなり強いはず。

実装
1. current model で多サンプル生成
2. reward = exact correctness + format safety
3. 正しい出力だけ採用
4. SFT し直す

メリット
- RL より安定
- Mac でも回しやすい
- solver 付き family との相性が良い

初期おすすめ
Stage C はまず RFT。
その後に小さく DPO。
GRPO はさらに余力があれば。

3-9. GRPO / RLVR をやるなら reward を最小限に絞る
reward を盛りすぎると壊れる。

reward 初期案
+1.0 exact correct
+0.3 numeric close / canonical close
+0.2 extraction safe
+0.1 short final answer
-0.3 extra trailing numbers after final answer
-0.5 malformed boxed

family 別補助 reward
- bit: 8bit exact length
- roman: uppercase roman valid
- unit: 2 decimal
- gravity: numeric parseable
- text: word count match
- symbol: no unwanted spaces

重要
reward の中心はあくまで correctness。

3-10. specialist adapter を作ってから merge する
最終提出は1 adapterでも、途中は複数でよい。

やること
- family 別 specialist LoRA を作る
- generalist LoRA も作る
- checkpoint / adapter merge を試す
- SVD で rank32 に圧縮

候補
- G = generalist
- B = bit specialist
- T = text specialist
- S = symbol specialist
- F = format specialist

merge 例
- 0.55G + 0.15B + 0.15T + 0.10S + 0.05F
- merge 後 rank32 再圧縮
- その後 short hardening 再学習

これが効く理由
hidden test の family 比率が微妙にズレても、specialist 能力を一つにまとめられる。

3-11. checkpoint averaging / adapter soup は必須で試す
提出は1つだが、複数 seed の良い部分を吸える。

試すべきもの
- 同一 run の last 3 checkpoint average
- 異 seed 2〜4 本の linear soup
- 異 curriculum run の weighted soup

その後
- validation で比較
- 必要なら SVD rank32 化
- hardening 数百〜数千 step で馴染ませる

3-12. family 別ミニバッチ制御
データが均衡でも、学習が均衡である必要はない。

sampler 案
sampler A: static weighted
- symbol, text, bit を厚め

sampler B: dynamic hard-mining
- 直近評価で落ちた family を増やす

sampler C: uncertainty-based
- student entropy 高い例を増やす

おすすめ
Phase A は static
Phase B/C は dynamic

3-13. 短い max_seq_len を基本にする
prompt が短いので、学習は長尺不要。

初期設定
- max_seq_len=1024
- 長 rationale を混ぜるなら 1536
- pack を使う

packing
短データだから packing は効く。
ただし final span weighting と相性確認は必要。

3-14. 学習率・step の現実的初期値
Stage A
- lr: 1e-4 or 8e-5
- warmup: 3%
- epochs: 1.5〜3
- wd: 0.0〜0.1

Stage B
- lr: 5e-5
- epochs: 0.5〜1.5
- hard data over-sample

Stage C (DPO/RFT)
- lr: 2e-5〜5e-5
- short run

比較候補
- 1e-4
- 8e-5
- 5e-5

3-15. まず試すべき学習設定ベスト5
1. all-linear / r32 / alpha32 / rsLoRA / dropout0 / StageA only
2. 同上 + final-span weighted loss
3. 2 に StageB hardening 追加
4. 3 に format sharpening 追加
5. 4 に RFT 追加

まずこれで十分戦える。

4. 出力フォーマット戦略: ここで落とさない

4-1. “必ず boxed” は危険。safe/unsafe を分ける
safe answers
- 数値
- 8bit binary
- Roman
- 普通の text phrase
- brace を含まない symbolic

→ \boxed{ANSWER} を最終行に出す

unsafe answers
- } を含む
- boxed regex が壊れやすい
- backslash が絡みやすい
- 複数記号で boxed が崩れやすい

→ Final answer: ANSWER を最終行に出す方針を学習で教える

理由
metric は boxed 優先だが、fallback もある。
壊れた boxed より、綺麗な final answer line のほうが強い。

4-2. 最終 answer は必ず “最後の行だけ”
悪い例
\boxed{42}
So the answer is 42.

良い例
\boxed{42}

学習ルール
- final answer の後は EOS
- 追加の数字禁止
- 追加の説明禁止

4-3. 複数 boxed を絶対に避ける
metric は最後の非空 boxed を拾う。
途中 reasoning に boxed を使うと事故る。

対策
- reasoning 内に boxed 不使用
- boxed は 1回だけ
- しかも最後

4-4. family ごとの canonical answer ルールを固定
bit
- 8 chars only
- spaces なし
- prefix 0b なし

gravity
- numeric only
- commas なし
- unnecessary unit なし

unit
- 2 decimals exact
- commas なし
- unit suffix なし

roman
- uppercase
- spaces なし

text
- single spaces only
- 前後空白なし
- punctuation 追加なし

symbol
- 原答え以外の空白なし
- dangerous chars のとき boxed 回避

4-5. extraction-aware teacher filtering
teacher 生成は correct でも、そのまま使わない。

採用条件
- extract_final_answer(output) == gold
- raw output 内に余計な boxed なし
- trailing numbers なし
- unsafe answer で malformed boxed なし

これを通ったものだけ蒸留用に使う。

4-6. format 専用 loss / preference を別で回す
精度だけでなく format を直接学習。

chosen
- same answer, clean format

rejected
- same answer, dirty format

これで DPO/ORPO するとかなり効くはず。

5. family 別の勝ち筋

5-1. Roman は “完全回収” を狙う
ここを落とすのはもったいない。

戦略
- generator 大量
- edge cases 厚め
- answer-only 比率高め
- uppercase 固定
- 1行 boxed 固定

目標
local 0.995〜1.000

5-2. Unit もほぼ完全回収
戦略
- 2 decimal canonical
- ratio hard cases
- wrong rounding correction
- final answer only

目標
0.99+

5-3. Gravity は丸めと書式で落とさない
戦略
- 1桁/2桁混在に慣らす
- round-half 系 hard case
- numeric parsing safe
- answer-only を多めに混ぜる

目標
0.985+

5-4. Bit は solver-aligned synth で押す
戦略
- sibling synth 大量
- op family ごとの hard case
- ambiguity low/high 両方作る
- shortest-correct distillation
- incorrect-op correction pairs

目標
0.93〜0.96

5-5. Text decrypt は teacher + solver で磨く
戦略
- closed vocab
- reversible ciphers
- phrase-length control
- concise reasoning 蒸留
- chosen/rejected で部分復号を潰す

目標
0.90〜0.94

5-6. Symbol は format-aware に分離攻略
戦略
- numeric / symbolic を別学習プール
- risky chars hardening
- boxed 例外学習
- shortest-answer stabilization
- character-level canonicalization

目標
0.88〜0.93

6. Mac Studio 512GB の使い倒し方

6-1. Mac は “大量生成工場” にする
Kaggle GPU を本番再現 lane に回すなら、Mac の価値はここ。

Mac でやるべきこと
- teacher inference
- self-consistency sampling
- synthetic generation
- parser / solver 実行
- family analysis
- hard mining
- ablation 自動化
- adapter merge / soup
- long-running eval

6-2. 役割分担を明確にする
Mac 側
- Transformers / PEFT / MPS
- official BF16 base 直学習
- synth / trace / preference data 作成
- LoRA sweep / ablation / smoke / packaging
- family-aware eval / ablation / hard mining
- 勝ち recipe の manifest 化

Kaggle CUDA 側
- A6000 Pro 48GB/96GB 級 GPU
- 必要時の BF16 + Transformers + PEFT 再学習
- Mac で勝った data ratio / weighting / style policy の忠実再現
- adapter_config.json / adapter_model.safetensors / submission.zip 生成
- vLLM / PeftModel.from_pretrained() / smoke / 提出互換の最終検証
- submit 上限を見ながら有望候補のみ本番投入

6-3. Mac 上の並列パイプライン
512GB あるなら、プロセス並列で回す。

例
- process 1: bit synth generator
- process 2: text decrypt teacher generation
- process 3: symbol hard pool generation
- process 4: current student eval
- process 5: merge candidate scoring

ストレージ
- raw generations: parquet
- normalized datasets: parquet / jsonl
- metadata index: sqlite / duckdb

6-4. 大規模 teacher を複数持つ
512GB なら、量子化モデルをかなり自由に回せる。

役割別 teacher
- Teacher A: reasoning 強い
- Teacher B: concise / instruction 強い
- Teacher C: base Nemotron 近縁のスタイル

使い分け
- A: long traces
- B: short clean outputs
- C: style alignment

6-5. Mac/MPS 学習アダプタも正式な提出候補として扱う
現行の正ルートは、Mac/MPS 上で official BF16 + Transformers + PEFT を直接学習し、同じ run から `adapter_config.json` 検証と `submission.zip` 生成まで完結させること。
必要なら、その有望 run を CUDA で再現して再現性確認を追加する。

必須
- Mac run ごとに data manifest / hyperparameter / seed / target_modules / weighting / style ratio を保存
- 有望 candidate は smoke / validate / submission まで同じ系で通す
- 必要に応じて Kaggle CUDA で BF16 再学習し、再現性を比較する
- adapter_config.json / adapter_model.safetensors / submission.zip を candidate ごとに検証する
- Kaggle 本番受理と score を run 単位で記録する

6-6. 24時間回しっぱなしの自動ループを作る
ループ
1. current model 評価
2. hard examples 収集
3. teacher 多サンプル生成
4. solver で correct filtering
5. distilled set 更新
6. 新 LoRA 学習
7. merge 候補生成
8. 再評価

重要
人手で毎回回さない。
夜間バッチ前提にする。

7. Kaggle GPU 30h/週・1日5提出 の使い方

7-1. Kaggle は “有望レシピの BF16 再現と提出”
それで正しい。

Kaggle でやること
- Mac で勝った recipe の CUDA / BF16 再学習
- submission zip 互換確認
- vLLM 実挙動確認
- small hidden-like smoke eval
- leaderboard submit

7-2. 提出ポリシーを固定する
1日5回使えるので、厳しすぎる温存は不要。
無駄打ちは避けるが、提出価値がある候補は積極的に出す。

推奨
- local best 更新候補は原則 submit queue に入れる
- 改善幅が小さくても family 改善や format 改善が見えるなら出す
- exploratory submit と confirmatory submit を混ぜる
- 1日 3〜5 提出を許容する

7-3. Kaggle に上げる候補条件
以下のいずれかを満たし、かつ packaging / load smoke が通れば提出候補:

- local overall best 更新
- hard split または難 family で明確改善
- extraction fail / format fail の改善
- weighting / style policy / mix 比率の仮説として leaderboard で見たい価値がある

7-4. 週30hの配分
週の使い方
- 4h: smoke & packaging
- 8h: top3 candidate verification
- 8h: merge / compressed adapter verification
- 5h: midpoint / weekly best submit
- 5h: buffer

7-5. 提出は “価値がある候補なら出す”
以下のいずれかなら出してよい:

- local overall best を更新した
- hard split / symbol / text など難所で改善した
- format fail が下がった
- 新しい recipe の当たり外れを hidden leaderboard で早く知る価値がある

8. 実験計画: まず何から試すか

8-1. P0: 絶対やる 10 実験
1. real-only all-linear r32 baseline
2. + final-span weighted loss
3. + sibling synth
4. + distilled short traces
5. + hard synth
6. + format sharpening
7. + correction data
8. DPO on clean-vs-dirty format
9. DPO on correct-vs-incorrect outputs
10. checkpoint soup + short hardening

8-2. P1: 高期待値 10 実験
1. alpha32 vs alpha64
2. dropout0 vs 0.05
3. all-linear vs attention-only
4. StageB only family oversample tuning
5. safe/unsafe boxed policy 学習
6. answer-only 比率 sweep
7. long/short trace 比率 sweep
8. hard synth 比率 sweep
9. RFT 追加
10. specialist merge

8-3. P2: 余力があれば
1. GRPO exact reward
2. ORPO vs DPO
3. layer subset LoRA
4. seed soup 4本
5. dynamic sampler
6. layerwise rank allocation
7. adapter merge 後の再蒸留
8. family-specific reward shaping

9. 具体的ハイパラ探索表

9-1. LoRA config sweep
- r: [16, 32]
- alpha: [32, 64]
- dropout: [0.0, 0.05]
- rsLoRA: [True]
- target: [all-linear, attn-only]

まず 8 通り以内に抑える。

9-2. data mix sweep
- Mix A: real50 / sibling25 / distilled15 / hard5 / format5
- Mix B: real40 / sibling25 / distilled15 / hard10 / correction10
- Mix C: real55 / sibling20 / distilled10 / hard10 / format5
- Mix D: real45 / sibling20 / distilled20 / hard10 / format5

9-3. target style sweep
- Style A: long20 short45 answer20 format15
- Style B: long10 short50 answer25 format15
- Style C: long30 short40 answer20 format10
- Style D: long0 short60 answer25 format15

10. 失敗しやすい罠

10-1. README の評価条件で合わせる
正しい。README の Evaluation / Submitting が本番条件の基準。公開 metric notebook の既定値を優先してズラすのはダメ。

10-2. visible test.csv を検証に使う
ダメ。train 重複。

10-3. boxed を絶対視する
ダメ。} を含む答えで壊れる。

10-4. synth を大量投入しすぎる
ダメ。real-only valid が悪化したら即止める。

10-5. 汎用 reasoning データを盛りすぎる
ダメ。分布が壊れる。

10-6. 長い reasoning を増やしすぎる
thinking-on / 長出力で latency と format drift の事故源になる。

10-7. family 別集計を見ない
overall だけ見ると、roman/unit が良くて難 family が死んでいても気づけない。

10-8. 6bit/旧 MLX 系を本番主ルートに戻す
ダメ。現行本線は official BF16 + Transformers 単一ファイル pipeline で、その run から提出まで繋ぐ。

11. 直ちに実装すべき ToDo

11-1. 今日やること
1. `official_bf16_run256_r16_ep2_run1` / `official_bf16_run256_r24_ep2_run1` / `official_bf16_run256_r24_ep2_len1024_run1` を完走まで監視
2. 完走した候補を smoke / validate / submission まで通す
3. best 候補に対して reduced-row official-style eval を再開する
4. memory monitor を維持し、RAM 圧迫時は枝を止める
5. run ごとの manifest / metrics / Kaggle score を記録する
6. 次の分岐（row 数増加、rank、length、データ改善）の優先度を更新する
7. 0.5 を超える提出候補だけ本番投入する

11-2. 今週やること
1. run256 勝ち筋の再現確認
2. row 数 256→512 か、family-aware data mix のどちらが先か判断
3. sibling synth / hard mining / format sharpening の優先順位を再整理
4. family 別 canonical metadata と risk 管理を v5 実験系へ接続
5. best candidate を複数回 Kaggle 提出して分散を見る
6. 必要なら CUDA 側で強い recipe の再現 run を行う
7. local eval と Kaggle score の相関を更新する
8. 0.7 を越えたら official-first best を単一ファイルとして再実装・再現確認する

11-3. 来週やること
1. text decrypt / symbol generator 強化
2. correction dataset 作成
3. DPO/ORPO format 実験
4. checkpoint soup
5. safe/unsafe boxed policy 実験
6. top3 candidate Kaggle submit

12. 最終的な“本命レシピ”

現時点で、最も堅い一本はこれ。

Base recipe
- all-linear LoRA
- r=32
- alpha=32 or 64
- rsLoRA=True
- dropout=0.0

Data
- real canonical
- sibling synth
- distilled short traces
- format sharpening
- hard synth 少量

Training
- Stage A generalist SFT
- Stage B hardening SFT
- final-span weighted loss
- answer style mix: long10 short50 answer25 format15

Optional Stage C
- RFT
- DPO on format + correction

Final
- adapter soup
- rank32 維持 / 再圧縮
- Mac で勝った recipe を CUDA BF16 + PEFT で再学習
- PEFT load test
- Kaggle smoke
- submit

13. top10 / 0.9+ を現実的に狙う優先順位

最重要
1. metric 実コード一致
2. family-aware validation
3. sibling synth
4. distilled short clean traces
5. final answer weighting
6. format-safe policy
7. hard family over-sampling

次点
8. correction data
9. DPO / ORPO
10. adapter soup

余力
11. RFT
12. GRPO
