# Nemotron-Cascade 2 論文精読メモ

`Nemotron-Cascade-2/Nemotron-Cascade-2.md` を全63ページ分、1ページずつ読み、`README.md` に記載された **NVIDIA Nemotron Model Reasoning Challenge** へ最大限つなげるための実用メモとして整理した。

本メモは、論文の内容をそのまま礼賛するのではなく、**README.md にある競技制約の下で何が直接使え、何が使えず、何をどう LoRA 学習計画へ落とすべきか**を明示することを目的にしている。

---

## 1. まず `README.md` から固定すべき競技条件

論文活用の前に、競技で絶対にずらしてはいけない前提を固定する。

- **提出物**: `Nemotron-3-Nano-30B` ベースモデルに適用可能な **LoRA adapter**。
- **LoRA 制約**: `adapter_config.json` を含み、**rank は 32 以下**。
- **推論エンジン**: `vLLM`。
- **推論パラメータ**: `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, `gpu_memory_utilization=0.85`, `max_model_len=8192`。
- **採点**: 最終回答は **`\boxed{}`** を優先的に抽出。boxed がなければ他のヒューリスティックや最後の数値にもフォールバックする。
- **タスク**: 論理推論パズル。ビット操作や代数方程式を含む「変換ルールの発見・適用」が中心。
- **評価指標**: 正答率。文字列一致または相対誤差許容内の数値一致。
- **自由度**: 学習フレームワークや手法は自由。NVIDIA 公式レシピは任意。
- **賞の条件**: 公開ノートブックと solution write-up が必要。

### この競技条件から導かれる重要な含意

- 論文の **128K〜256K トークン級の推論や test-time scaling** は、そのまま本番推論に持ち込めない。
- 本番は **temperature 0.0 の単発 deterministic 推論** なので、論文の多サンプル生成・自己改善・多数決は **オフラインのデータ生成工程へ蒸留** する必要がある。
- メトリクスが `\boxed{}` を強く優先するため、**回答フォーマット学習は精度に直結**する。
- データセットは知識問題ではなく **変換規則推論**。よって論文中でも特に価値が高いのは、
  - 正答検証付きデータ生成
  - 形式制約の厳守
  - hard example mining
  - 段階的 post-training
  - 長い思考を短い単発推論へ蒸留する発想
  である。

---

## 2. この論文から競技へ直接移植すべき最重要原則

### 2.1 直接移植すべきもの

1. **正答検証でフィルタした学習データ**
   - 論文では code/math の teacher trace を correctness filtering している。
   - この競技でも、train 問題や solver 生成 synthetic 問題に対して、**答えが確定的に検証できるものだけを強く採用**するべき。

2. **出力形式そのものを学習対象にする**
   - 論文の HLE 評価では `\boxed{}` 指定で 6–7 点上がった。
   - README の metric も boxed を優先するため、**最終回答の boxed 化、単一回答化、余計な数値を後ろに書かない訓練**は必須。

3. **難問中心の再配分**
   - 論文は GPT-OSS-120B が 8/8 正解するような easy code 問題を落として、難問だけ残している。
   - この競技でも、ベースモデルが既に解ける easy train を大量に回すより、**誤答しやすい問題・規則発見が難しい問題・出力形式を崩しやすい問題**を重視すべき。

4. **段階分けした post-training**
   - 論文の肝は「全部を同時に混ぜる」ではなく、「干渉しにくい順序で鍛える」こと。
   - この競技なら、
     - Stage A: boxed 出力と短い答えの形式統一
     - Stage B: 推論パズル本体の hard-example SFT
     - Stage C: shorter / cleaner / more deterministic な正答出力への軽い選好学習または蒸留
     の順が合理的。

5. **test-time scaling を offline distillation に変換する**
   - 論文は generate-verify-refine や tool use で強い。
   - しかし本番は単発推論なので、**offline で多数生成→検証→最良 trace を選抜→それを LoRA に蒸留**するのが正しい使い方。

### 2.2 部分移植に留めるべきもの

- **Tool calling / Python executor**
  - 論文では強いが、本競技の本番推論には出せない前提で考えるべき。
  - 使うなら **teacher data 作成専用**。

- **RLHF / agentic SWE RL**
  - 論文では重要だが、競技ドメインからはやや遠い。
  - ただし、
    - shorter but still correct
    - format-compliant
    - no trailing junk
    のような性質を学ばせる軽い preference/distillation は有効。

- **1M context / 256K proof generation**
  - 本競技の `max_model_len=8192` とは完全に別世界。
  - 参考にするなら「長い推論を短く圧縮しても正答を維持する設計思想」のみ。

### 2.3 真似しない方がよいもの

- 本番での多ラウンド自己改善を前提にした設計。
- 超長文 reasoning をそのまま吐く学習。
- コード・SWE・terminal agent に学習容量を割きすぎること。
- 知識集約型 benchmark 向けの最適化。

---

## 3. 論文を競技向けに読み替えた実験ロードマップ

### 推奨ロードマップ

- **Phase 1: 出力整形 SFT**
  - `\boxed{}` を必ず使う。
  - 1 回だけ最終回答を書く。
  - 最終回答の後に追加の数値や候補を置かない。
  - 「答えだけ短く書く」サンプルも混ぜる。

- **Phase 2: 推論パズル hard-example SFT**
  - train.csv を difficulty 別に再編。
  - ベースモデルで既に安定正答する easy 群を薄くし、誤答群・形式崩れ群を厚くする。
  - synthetic は solver-verified 前提。

- **Phase 3: teacher-trace distillation**
  - 強い teacher / 多数生成 / 自己検証で最良解を作る。
  - ただし最終的には **単発 deterministic 推論**で再現できるように、短く整理した teacher trace を採用。

- **Phase 4: concise correctness tuning**
  - 論文の conciseness bonus に相当する思想。
  - 「長いが正しい」より **「短く、答えが明確で、boxed が崩れない」** を優先。

- **Phase 5: metric-aware validation**
  - `README.md` の metric 想定そのままでローカル採点。
  - boxed 抽出・数値 tolerance・文字列一致の挙動を確認し、回答表現を揃える。

### GPU 98GB / 48GB 向けの計画メモ

#### 98GB RTX PRO 6000 を主ターゲットにする場合

- rank 32 LoRA を第一候補にする。
- 学習長は `max_model_len=8192` に近い 6k〜8k を主軸に検討する。
- 4bit QLoRA + bf16 compute + gradient checkpointing を前提に、**データ品質最優先**で回す。
- attention 系だけでなく MLP 系も含めた広めの target module を検討する価値がある。
- ただし論文のような 49K / 98K / 118K 出力長は追わず、**競技の 7680 token 制約内に入る短い reasoning へ圧縮**する。

#### 48GB RTX A6000 を縮退案にする場合

- まず 4k〜6k context で回る設定から始める。
- micro-batch を 1 にし、gradient accumulation で実効 batch を作る。
- rank 32 が厳しければ実験段階では rank 16/24 の比較もあり得るが、最終提出候補は rank 32 まで含めて再検討する。
- 長文 reasoning より、**短く正しい boxed answer を出す学習**へより強く寄せる。
- 48GB では multi-stage を無闇に増やすより、**hard-example 選別と synthetic 品質管理**に時間を使う方が得。

---

## 4. ページ別精読メモ（全63ページ）

### Page 1
- **記載内容**: タイトル、アブストラクト、主要ベンチ結果、公開アセット。Nemotron-Cascade 2 は 30B MoE / 3B active で、SFT の後に広範な Cascade RL と multi-domain on-policy distillation を行い、数学・コード推論で非常に高い性能を出すと主張している。
- **競技転用**: この競技でも、性能差は pretraining より **post-training の設計**で詰めるべきだと読める。特に「慎重な SFT → 段階的強化 → 退化回復」が重要。
- **実験案**: Nemotron-3-Nano-30B ベースに対して、1 回で全部を入れるのではなく、boxed 出力 / hard reasoning / concise correction の段階設計にする。
- **注意**: 論文の結果は多領域・大規模計算込み。本競技へ持ち込めるのは発想であり、手順を丸写ししてもそのままは再現できない。

### Page 2
- **記載内容**: 目次。導入、主結果、SFT、Cascade RL、IMO、競技プログラミング、謝辞、Appendix の構成が示される。
- **競技転用**: 競技で直接重要なのは Section 3, 4, Appendix A/B/C。特にデータ設計、段階順序、評価設定、prompt template が価値の高い部分。
- **実験案**: 論文利用の優先順位を `SFT data curation > RL ordering > output format/judge prompt > benchmark setup` と置く。
- **注意**: IMO / IOI の華やかな結果だけ追うと、本競技の単発 deterministic eval から離れる。

### Page 3
- **記載内容**: Appendix 側の目次が続く。ベンチ詳細、訓練ハイパラ、prompt templates、ELO 分析、IMO 模範解答が含まれる。
- **競技転用**: Appendix は飾りではなく再現・転用の中核。特に **boxed answer の judge prompt** と **各段階のハイパラ思想**が重要。
- **実験案**: 競技メモを作る際は本文だけでなく Appendix の評価条件まで必ず吸収する。
- **注意**: 参考文献と謝辞ページは直接的な recipe は少ないが、追跡すべき手法の出典を教えてくれる。

### Page 4
- **記載内容**: 導入。Cascade RL の利点として、 catastrophic forgetting を抑え、段階ごとに最適ハイパラを使え、計算効率も良いことを説明する。Nemotron-Cascade 2 では MOPD と multi-domain RL を追加している。
- **競技転用**: LoRA 学習でも **順序設計**が重要。形式制約と推論本体を同時に詰め込まず、干渉の少ない順に学習するのが良い。
- **実験案**: Stage A を output discipline、Stage B を reasoning hard cases、Stage C を concise correction に分ける。
- **注意**: 本競技では agentic domain を広く扱う必要はなく、論理推論パズルへ強く絞るべき。

### Page 5
- **記載内容**: Table 1。本モデルは math / code / alignment / instruction following に強く、knowledge-heavy や一部 agentic ではより大きいモデルに劣る。
- **競技転用**: 競技データは知識暗記ではなく推論変換なので、この表から学ぶべきは **math/code 型 reasoning の後学習が効く**という点。
- **実験案**: 学習データと評価設計は、知識問題ではなく「規則発見」「厳密出力」「正答検証」に寄せる。
- **注意**: broad benchmark で強い設定が、そのまま Kaggle の単一指標で最適とは限らない。

### Page 6
- **記載内容**: Table 2 の金メダル級結果と、SFT セクション導入。SFT は math, coding, science, tool use, agentic, SWE, dialogue など広い。256K packing、約 1.5 epoch で最適。chat template から `/think` タグを除去し、空の `<think></think>` を非思考モード起動に使う。
- **競技転用**: 本競技でも **chat template / thinking mode の扱い**は無視できない。出力フォーマットと reasoning mode を明示した SFT が効く。
- **実験案**: boxed final answer を入れた専用 template、思考あり/なしの両方の教師データ、ただし本番は単発推論向けに安定化した回答を重視する。
- **注意**: 256K packing は本競技の 8K 制約と無関係。sequence length をそのまま真似しない。

### Page 7
- **記載内容**: chat template の詳細。続いて math SFT と code reasoning SFT。math は python tool-use と non-tool を大量収集、proof generation と proof verification も分けて用意。code 側は 165K unique prompts を strict dedup し、約 24.2% の重複を除去。
- **競技転用**: 最重要なのは **(a) toolあり/なしの二系統データ、(b) proof generation と proof verification の分離、(c) dedup の厳格化**。
- **実験案**: train/synthetic データを「直接解答」と「自己検証つき解答」に分ける。重複は prompt fingerprint と文字列類似度で落とす。
- **注意**: 本番では tool use できない前提で、tool trace は teacher data 用に限定する。

### Page 8
- **記載内容**: code SFT は GPT-OSS-120B teacher を correctness filtering。テストで検証できない場合は長い trace を優先。加えて science, long context, general chat, multi-turn chat, instruction following, safety データが並ぶ。
- **競技転用**: **正答検証できるものは correctness filtering、できないものは長さだけではなく後で別途審査**という発想が重要。reasoning-on データが非常に多い点も参考になる。
- **実験案**: パズル用 synthetic data は solver で答えを確定し、その上で teacher trace を選ぶ。短い answer-only サンプルも少量混ぜて deterministic 化を促す。
- **注意**: chat や long-context の比率を高くすると、本競技の本質から外れる。

### Page 9
- **記載内容**: conversational tool use、SWE data、terminal agent data、そして Cascade RL + MOPD 導入。SWE では agentic data と agentless data の併用が agentic 評価を改善したと述べる。
- **競技転用**: 「**直接解くデータ**」と「**中間工程を明示するデータ**」を混ぜると generalization が上がる、という読み替えができる。
- **実験案**: パズルでも、answer-only だけでなく、規則抽出・候補列挙・検算・誤答修正のような中間工程データを混ぜる。
- **注意**: terminal / SWE はそのままのドメイン価値は低い。学ぶのはデータ設計思想だけ。

### Page 10
- **記載内容**: Figure 2 の訓練パイプライン。SFT → IF-RL → multi-domain RL → MOPD → RLHF → long-context RL → code RL → SWE RL。順序はモデル挙動に応じて決めるべきで、干渉の最小化、互換ドメイン統合、MOPD による再平衡が鍵と説明。
- **競技転用**: 競技でも **一発学習ではなく順序設計**が重要。最初に boxed 形式と制約遵守を固め、その後に reasoning を上積みする方が良い。
- **実験案**: 版管理を切るなら、`format-first -> hard-puzzle -> concise-distill` の順で v1, v2, v3 と積むのが自然。
- **注意**: NeMo-RL / GRPO をそのまま回す必要はない。思想を SFT/DPO/蒸留に落とし込めばよい。

### Page 11
- **記載内容**: on-policy GRPO の式、KL なし、importance ratio 1 で安定化。IF-RL は verifiable instruction data を使い、dynamic filtering と overlong penalty を採用。IF-RL を最初に置く理由として、後段で alignment を回復できること、MOPD teacher として優秀になることを挙げる。thinking mode only。
- **競技転用**: **dynamic filtering** と **overlong penalty** は本競技に極めて相性が良い。学習信号のない easy / impossible バッチを減らし、長すぎる解答を罰する設計がそのまま効く。
- **実験案**: 既に全正解・全不正解のサンプルを除く近傍 difficulty を厚くする。`max_tokens=7680` を超えやすい長文 trace には負例または低重みを与える。
- **注意**: 論文の学習は temperature 1.0 だが、本番評価は temperature 0.0。安定な単発出力へ別途寄せる必要がある。

### Page 12
- **記載内容**: IF-RL の具体ハイパラの続き。Multi-domain RL は STEM MCQA、agentic tool calling、structured output を 55/30/15 で混ぜる。応答長と検証コストが似ているから同居できると説明。MOPD は capability drift の再平衡策として導入される。
- **競技転用**: structured output を独立に扱っている点が重要。本競技なら `\boxed{}`、数値正規化、単一回答などを **独立サブタスク**として持たせる価値が高い。
- **実験案**: reasoning データと同じ比率でなくてよいので、format-only / short-answer-only サンプルを混ぜる。
- **注意**: response length や verifier cost が大きく違うデータを無理に混ぜると学習効率が落ちる。

### Page 13
- **記載内容**: MOPD の数式。domain teacher の token-level reverse-KL advantage を使い、truncated importance weighting で train/inference mismatch を扱う。warmup が重要で、40–50 steps で収束。teacher は math / RLHF / multi-domain の複数 checkpoint。
- **競技転用**: **複数段階で得た最良 checkpoint / teacher responses を 1 本の student に蒸留する**発想がそのまま使える。RL より蒸留の方が低予算で現実的。
- **実験案**: `best format model`, `best hard-puzzle model`, `best concise model` を teacher と見なし、正答 trace を集めて最終 LoRA に distill する。
- **注意**: sparse reward より dense token supervision が効く、という点を忘れず、競技では outcome-only より SFT/distillation を主軸に置く。

### Page 14
- **記載内容**: Table 3 で MOPD は RLHF より少ない step で ArenaHard を回復。RLHF は HelpSteer3 などの preference data と GenRM を使い、pairwise comparisons、length-normalized reward、quality-gated conciseness bonus を採用。thinking mode only。
- **競技転用**: 「**正しさを保ったまま短くする**」という conciseness bonus の思想が重要。boxed 抽出に強い短い回答は metric と相性が良い。
- **実験案**: 同じ正答の候補が複数あるなら、より短く、boxed が明確で、余計な数字が少ない方を優先して teacher に採用する。
- **注意**: 人間好みの creative writing は本競技では不要。conciseness と deterministicness だけ借りる。

### Page 15
- **記載内容**: long-context RL は long-context のみで実施し、他ドメイン混合は悪化。Code RL は GPT-OSS-120B が 8/8 正解する easy 問題を削り、3.5K の hard set に圧縮。118K response、16 rollouts、binary reward、384 CPU cores の async verifier。SWE agentless RL では no-positive-rollout の難しすぎる prompt を mask。
- **競技転用**: このページの要点は **easy を削る・hard に集中・binary correctness・難しすぎる例は扱いを変える** の 4 つ。
- **実験案**: train を base-model difficulty で分割し、easy を薄くする。synthetic も solver が簡単に解く trivials は減らす。答えが曖昧なサンプルは除外。
- **注意**: 超長 response や大規模 verifier infra は競技本番と無関係。

### Page 16
- **記載内容**: agentless RL が agentic 評価も改善。Execution-based agentic SWE RL は build/test ベースの deterministic reward を使い、16 prompts × 64 rollouts、256K context、200 turns。100% 正解の easy 問題は削除し、0% 正解の極難問は 90% を捨てる。
- **競技転用**: **100% easy を減らし、0% impossible を間引く** difficulty shaping は本競技でも非常に重要。exact answer match で reward が取れるので相性がよい。
- **実験案**: ベースモデルの pass rate で train を 3 分割し、中間 difficulty を主学習帯にする。
- **注意**: scaffold 自体ではなく、difficulty rebalancing の考え方だけを持ち込む。

### Page 17
- **記載内容**: IMO 2025 は generate-verify-refine の self-improving test-time scaling で 5 問解けた。expert review では「冗長」「不要な中間定義」「思考痕跡露出」「typo」などが指摘される。続いて IMO-ProofBench 72.9、round を増やすと Advanced が 40.7 → 53.4。IOI では generate-select-submit を多ラウンドで回し、履歴と高得点 subtask の知見を共有する。
- **競技転用**: 論文の test-time scaling は **offline data generation の黄金手順**として使うべき。つまり、多数生成→自己検証→修正→最良版選抜→短縮→LoRA 蒸留。
- **実験案**: puzzle synthetic でも、1 問から複数 reasoning trace を作り、正答かつ最も短く安定したものを teacher にする。
- **注意**: 本番評価では多ラウンド自己改善は使えない。ここを勘違いすると設計を誤る。

### Page 18
- **記載内容**: Figure 4 で generate-verify-refine rounds の増加が ProofBench を押し上げる。Table 6 では coding benchmark と TIR の性能比較。TIR は hard 問題で特に効く。ICPC では最大 1000 解答まで提出して 10/12 を解く。
- **競技転用**: hard case で tool-integrated reasoning が効く事実は、「難問用 teacher 生成を tool-assisted にする」根拠になる。
- **実験案**: offline では solver や Python を使って候補解を検証し、その正答 trace を **no-tool 単発出力**へ蒸留する。
- **注意**: avg@8 や大量 submission は leaderboard 単発推論より有利なので、数字をそのまま競技期待値に変換してはいけない。

### Page 19
- **記載内容**: Table 6 の総括。TIR ありだとより巨大な open model 群に食い込む。hard split で 0% を超えるのも強調される。その後は謝辞。
- **競技転用**: **hard split での改善こそ価値が高い**。本競技でも public LB を少し押し上げる easy 問題より、hidden hard case を拾える設計が重要。
- **実験案**: validation を easy / medium / hard に分けて追跡し、hard の改善を重視する。
- **注意**: 謝辞自体に recipe はないが、どのチーム知見が入っているかは背景理解になる。

### Page 20
- **記載内容**: Appendix A.1。AIME, HMMT, IMO-AnswerBench, IMO-ProofBench の評価設定。AIME/HMMT は 131K thinking budget、with-tool では Python executor 100 回まで。ProofBench は generate-verify-refine を NeMo-Skills で回し、128 proof generations, 64 verifications, top 32 refine, 8 rounds など非常に重い設定。
- **競技転用**: ここで重要なのは **重い inference-time compute が効く**ことではなく、**その compute を offline label quality 向上へ使う**べき、という点。
- **実験案**: public/private 用の提出モデル自体は単発だが、データ生成時は多数候補＋検証＋選抜で高品質 teacher を作る。
- **注意**: 256K 予算を前提にした trace をそのまま学習すると、本競技の 7680 token 制約下で再現不能になる。

### Page 21
- **記載内容**: ProofBench judge aggregation。どれか 1 つでも judge が 0 を出せば最終 0、それ以外は mean。これで過大評価を抑える。続いて code benchmarks の定義と eval setting。
- **競技転用**: synthetic データ品質管理にそのまま使える。**複数 verifier のうち 1 つでも強く否定するなら捨てる**、という conservative rule は非常に有用。
- **実験案**: solver, symbolic checker, regex extractor など複数検証器を用意できるなら AND 寄りに採用する。
- **注意**: 128K thinking budget や Python 100 calls は本番 inference の想定ではない。

### Page 22
- **記載内容**: HLE では question に `Please place your final answer inside \boxed{}` を追加すると 6–7 点改善。これは math SFT の answer format と揃うため。続いて ArenaHard, IFBench, Scale AI Multi-Challenge の説明。
- **競技転用**: 63ページ中でも **最重要ページの一つ**。boxed 指示は cosmetic ではなく、**測定可能な精度差**を生む。README の metric と完全に整合する。
- **実験案**: train / synthetic / validation の全プロンプトで最終回答形式を統一し、answer extraction-aware にチューニングする。
- **注意**: boxed の後に別の数字を書くと heuristic fallback が誤爆する可能性がある。最終 answer token は一つに固定する。

### Page 23
- **記載内容**: long-context benchmark の説明と、agentic tasks の評価設定。SWE-bench Verified は non-thinking、OpenHands、256K context、200 turns。`tau^2` では latest-turn thought retention が no-thought carry-over より 3–5 点高いと述べる。
- **競技転用**: train-test alignment が重要。競技でも **本番 prompt に近い形式**、**最近の重要な推論だけ残す短い文脈**が有効。
- **実験案**: synthetic trace から冗長な earlier thoughts を削り、最後の有効 reasoning と boxed answer を残す短文化データを作る。
- **注意**: full interaction retention は本競技では不要で、8K context の圧迫要因になる。

### Page 24
- **記載内容**: latest-turn thought retention の続き。多言語 benchmark。続いて Table 7 の SFT hyperparameters: global batch 64, packed 256K, max lr 5e-5, cosine, 33k steps, AdamW, weight decay 0.1。
- **競技転用**: SFT を最初の太い柱に置き、scheduler と regularization をきちんと使う、という意味で有益。
- **実験案**: LoRA では step 数は縮めるとしても、cosine / warmup / weight decay を適切に組む。多言語は優先度低。
- **注意**: sequence length や total steps をそのまま移植しない。競技条件と VRAM に合わせて再設計が必要。

### Page 25
- **記載内容**: Table 8 と Table 9。IF-RL / multi-domain RL / MOPD、RLHF / long-context RL / code RL の max response length, batch, rollout, lr, steps, overlong filtering が並ぶ。
- **競技転用**: 段階ごとに **出力長の budget を変えている**点が示唆的。本競技ではこの budget を 7680 以下前提で設計し直す必要がある。
- **実験案**: format SFT は非常に短く、hard reasoning SFT は中程度、final distill は再び短く、という length curriculum を組む。
- **注意**: 論文の 49K / 98K / 118K 出力長を真似ると、本番で truncation と format 崩れを招きやすい。

### Page 26
- **記載内容**: Table 10 の execution-based SWE RL ハイパラ。続いて Appendix C.1 の IOI test-time scaling prompt。accepted code, different constraints, incorrect code と official verdict を与えて改善させる設計。
- **競技転用**: **誤答履歴と確定的フィードバックを使って次の解を作る**という template は、offline synthetic 生成で有効。
- **実験案**: パズルでも「前回の誤答」「なぜ不一致か」「正しい答え」の差分から修正 trace を作り、error-correction SFT を構成する。
- **注意**: これは teacher generation 用。提出時の単発推論にこの multi-round 構造は持ち込めない。

### Page 27
- **記載内容**: HLE judge prompt。`extracted_final_answer`, `reasoning`, `correct`, `confidence` を明示抽出する。続いて ELO rating analysis では Codeforces 40 コンテスト、8 attempts、temp 1.0, top_p 0.95, 128K budget、弱点は constructive / interactive / hypothesis-driven tasks と分析。
- **競技転用**: answer extraction と correctness 判定を分離する evaluator 設計は本競技でも重要。弱点分析のうち **hypothesis-driven / constructive** は変換ルール系 puzzle と近い。
- **実験案**: ローカル検証でも、生成文から final answer を明示抽出し、その後に exact/tolerance 判定する二段構成にする。
- **注意**: confidence は leaderboard に不要。必要なのは final answer の一意性だけ。

### Page 28
- **記載内容**: Table 11。Python tool なしでの 40 回分 Codeforces 詳細。Div2 でかなり安定し、一部 Div1 でも高 ELO を示す。
- **競技転用**: no-tool でも十分戦えることを示す。つまり本競技も **最終 adapter 自体は tool 非依存**で十分伸ばせる。
- **実験案**: tool-assisted teacher を使うとしても、最終モデルは no-tool の plain-text boxed answer を出す前提で訓練する。
- **注意**: avg@8 的な多試行評価は、temperature 0.0 の Kaggle 評価より高めに出る点を補正して読む。

### Page 29
- **記載内容**: Table 12。Python tool ありの Codeforces 詳細。多くの contest で hard 問題寄りに改善が見える。
- **競技転用**: tool で得た改善は **teacher quality 向上のために使う**のが正解。hard synthetic puzzle の正答 trace 生成に転用できる。
- **実験案**: 難しい train/synthetic 問題だけ tool-assisted でラベルを作り、正答 short-trace へ蒸留する。
- **注意**: tool 利得は一様ではない。hard subset に限定して使った方が効率的。

### Page 30
- **記載内容**: Appendix E の IMO 2025 Model Solutions 開始。Problem 1 を定義し、short answer として `k = 0, 1, 3` を先に提示。その後に constructive proof を始める。
- **競技転用**: **最終結論を先に isolated してから推論を展開する**構成が、metric-aware training に極めて相性が良い。
- **実験案**: synthetic teacher trace でも「結論の型」を明確化し、最後は boxed で一意に閉じる。
- **注意**: 本競技では proof quality そのものではなく正答率が指標。結論の明確さを優先。

### Page 31
- **記載内容**: Problem 1 の構成法の続きと、boundary set による counting argument。special sides の概念を導入し、covering の制約を絞る。
- **競技転用**: rule-discovery 型パズルでも、**境界条件・不変量・カウント制約**を explicit に書く trace は強い教師になる。
- **実験案**: synthetic trace 生成時に「まず境界や例外を列挙する」型を増やす。
- **注意**: 冗長な詳細まで学ばせるとトークンが増えるため、要点化した trace を採用したい。

### Page 32
- **記載内容**: Problem 1 の reduction to `n-1`、base case `n=3`、induction step。構造的な帰納で impossibility を閉じる。
- **競技転用**: 複雑な puzzle でも、**縮約して既知形に落とす**思考は重要。train/synthetic に reduction-style 解説を入れる価値が高い。
- **実験案**: transformation puzzle の teacher trace に「小さいケースへ落とす」「対称性で簡約する」テンプレートを持ち込む。
- **注意**: 帰納法そのものを長く学ばせるより、縮約・場合分け・結論分離の骨格を学ばせる。

### Page 33
- **記載内容**: Problem 1 の締め。人間 expert comment と full-score 評価が入る。
- **競技転用**: ここで重要なのは、**結論が正しく、論理が閉じていれば full score**という点。スタイルより correctness が本質。
- **実験案**: synthetic data 選抜では「美しい解」より「検証できる正しい解」を優先する。
- **注意**: 競技では full proof は不要なので、style overfitting は避ける。

### Page 34
- **記載内容**: Problem 2。幾何問題を座標・円の中心・交点などで置き換える analytic な解法の導入。
- **競技転用**: 規則発見タスクでも、抽象的対象を **座標化・変数化して扱いやすい表現へ落とす** trace は有効。
- **実験案**: puzzle をそのまま解かせるだけでなく、内部表現へ変換する reasoning exemplars を作る。
- **注意**: elegant さより、後で verifier が追える explicitness を優先する。

### Page 35
- **記載内容**: unit vectors, orthocenter, beta/gamma など補助量を定義し、幾何を線形代数へ翻訳していく。
- **競技転用**: **補助変数を導入して複雑さを局所化する**書き方は、変換ルールの説明にも使える。
- **実験案**: teacher trace に「記号化」「補助量」「チェックポイント」を入れる。
- **注意**: 補助記号が多すぎると 8K 制約下では不利。最終学習用には圧縮版を使う。

### Page 36
- **記載内容**: Problem 2 の計算が継続。多数の代数操作で中間量の関係を詰める。
- **競技転用**: analytic heavy な解法でも、**一歩ずつ検証可能なら成立する**ことが示唆される。正答 trace の explicitness を恐れなくてよい。
- **実験案**: solver-verified な中間計算を含む trace を用意し、最終的には短縮蒸留する。
- **注意**: 生の長大計算 trace をそのまま LoRA に大量投入すると冗長化しやすい。

### Page 37
- **記載内容**: Problem 2 の tangency condition とその verification。幾何条件を式に落として閉じる。
- **競技転用**: 規則問題でも、最後に **条件を満たすことを明示的に確認する concluding step** があると強い。
- **実験案**: teacher trace の終盤に「最終チェック」を必ず置くテンプレートを設ける。
- **注意**: 最終チェックの後に余分な候補値や別案を書かない。

### Page 38
- **記載内容**: Problem 2 に対する LLM judge comment 用の入力仕様が現れる。proof を採点するための構造化された指示が見える。
- **競技転用**: judge prompt を使った **自己評価データ生成**が有効であることを示す。生成した trace に対して critique を作ることで repair data を作れる。
- **実験案**: train/synthetic 解答に対し、「どこが不足か」「最終答えは一致しているか」を判定する judge データを追加する。
- **注意**: judge の文章そのものを学ばせすぎると回答がメタ化するので、主役は最終解答側。

### Page 39
- **記載内容**: GPT-5.4 による厳格な採点コメント。coordinate proof だが完全であると評価している。
- **競技転用**: **elegance より completeness**。本競技でも、綺麗さより answer correctness と形式安定性を優先すべき。
- **実験案**: teacher 選抜時に「簡潔だが穴がある解」より「やや重いが正しく閉じる解」を採用し、その後に別段階で短縮する。
- **注意**: critique trace は教師品質判定に使い、最終回答モデルには過度に流し込まない。

### Page 40
- **記載内容**: 採点コメントの続き。各中間ステップが成立しているかを逐一確認している。
- **競技転用**: **ステップ単位の局所検証**が効く。パズル解法でも、途中推論を小さな確認単位へ分ける trace は学習価値が高い。
- **実験案**: synthetic trace に「checkpoint assertions」を埋め込む。
- **注意**: ただし提出時は checkpoint 全部を出す必要はない。蒸留で短くする。

### Page 41
- **記載内容**: 採点コメントの続き。最後の tangency 条件の等価変形と結論部分を確認している。
- **競技転用**: 結論直前の **同値変形ミス防止**が重要。数値パズルでも最後の変換ミスを減らすデータが効く。
- **実験案**: 「ほぼ正しいが最後の変換だけ違う」誤答修正データを作る。
- **注意**: metric は最後の boxed answer しか見ないので、終盤のミスは致命傷になる。

### Page 42
- **記載内容**: deductions なし、7/7、brief assessment。valid full-score coordinate solution と結論。
- **競技転用**: **完全性が確保されれば analytical / coordinate style でも問題ない**。変換パズルでも形式が変でも正しければよい。
- **実験案**: 多少無骨でも verifier を通る解答を優先して学習する。
- **注意**: 人間向け美文より metric-aware correctness を優先する。

### Page 43
- **記載内容**: Problem 3。bonza function を定義し、最小定数 `c=4` を求める。basic properties と primes の振る舞いから入る。
- **競技転用**: 問題を **定義→基本性質→特殊ケース** と積み上げる型は transformation rule 推論にもそのまま効く。
- **実験案**: synthetic teacher では「定義の言い換え」と「まず基本性質を列挙する」テンプレートを増やす。
- **注意**: 問題の言い換えだけで終わる trace は弱い。必ず結論へつながる中間事実を置く。

### Page 44
- **記載内容**: `S` が無限のとき、奇素数が入るとき、`S = ∅`, `S = {2}` など exhaustive case split を進める。
- **競技転用**: **場合分けの完全性**が重要。パズルでも例外ケースの取りこぼしが誤答原因になりやすい。
- **実験案**: teacher trace で case labels を明示し、「残るケースはこれだけ」と締める。
- **注意**: cases を増やしすぎると長文化するので、最終学習用には不要ケースを削る。

### Page 45
- **記載内容**: sharpness。2-adic valuation や LTE 的な議論で上界の鋭さを示す。
- **競技転用**: 上界・最適性・端点の sharpness を確認する習慣は、変換ルールの特定にも有効。
- **実験案**: 予測値が得られた後に「その値以外がダメな理由」を短く確認する trace を用意する。
- **注意**: 本競技では full proof は不要なので、sharpness は短く要約してよい。

### Page 46
- **記載内容**: Problem 3 の結論。構成例で `4` が達成され、これ未満は不可能と閉じる。
- **競技転用**: **上界証明 + 達成例** の組み合わせは、パズルの規則確定にも通じる。候補規則を出したら検証例で閉じるのが良い。
- **実験案**: answer-only データと別に、最終検算付き短い解答データを作る。
- **注意**: 結論直後に別候補値を書かない。metric 的に危険。

### Page 47
- **記載内容**: Problem 4。約数列問題。short answer は `a = 2^x 3^y m` 型の特徴付け。odd / even-not-divisible-by-3 の補題から始まる。
- **競技転用**: **不変量を見つけて全体構造を絞る**タイプの reasoning が、競技の transformation-rule 問題に非常に近い。
- **実験案**: 「最初に invariant を見つける」訓練データを増やす。
- **注意**: 補題の数を増やしすぎると推論が長くなりがち。必要最小限に整理する。

### Page 48
- **記載内容**: 全ての項が 6 の倍数であることを示し、`6M` への reduction を行う。
- **競技転用**: 複雑な入力を **正規形へ落とす**のは puzzle 解法の王道。例えば行列/ビット/文字列の規則を canonical form へ変換する発想に対応する。
- **実験案**: teacher trace に normalization step を明示的に入れる。
- **注意**: reduction の正当化なしに結果だけ言う trace は弱い。

### Page 49
- **記載内容**: `M1 = a1 / 6` の admissible 条件を、4 番目の約数ケースで分類して特徴付ける。
- **競技転用**: **局所分岐条件で全体ルールを決める**という型は、コンペの規則推定に直接有効。
- **実験案**: synthetic trace に「この条件なら branch A, そうでなければ B」といった decision tree 型説明を入れる。
- **注意**: branch 条件は相互排他的・網羅的に書く。

### Page 50
- **記載内容**: sufficiency / necessity。`M1 = 12^k d` として `d` の偶奇や 5 の可除性で可能性を分け、必要十分条件へ詰める。
- **競技転用**: **必要条件と十分条件を分ける**構成は、変換ルールの確証度を上げるのに有効。
- **実験案**: 「候補規則が十分条件なのか、必要条件まで言えるのか」を区別する訓練データを入れる。
- **注意**: 本競技は final answer 精度が全てなので、途中で不確かな仮説を複数並べない。

### Page 51
- **記載内容**: Problem 4 の final answer を統合。どの `a1` が可能かを最終形で提示する。
- **競技転用**: 長い場合分けの後でも、最後は **一行で答えをまとめる**必要がある。boxed と非常に相性が良い。
- **実験案**: train/synthetic の final line は常に canonical answer form に揃える。
- **注意**: 長い説明の後でも最終行は短く、唯一の答えだけを書く。

### Page 52
- **記載内容**: Problem 5。ゲーム問題を定義し、Bazza の key strategy を導入する。
- **競技転用**: ゲーム・逐次制約系でも、**最適戦略を一つ固定して解析する**手法が効く。規則推定問題でも支配的方策を先に仮定するのは有効。
- **実験案**: puzzle synthetic に「まず支配的仮説を置き、そこから検証する」型の trace を増やす。
- **注意**: 仮説を置いたら、その合法性・最適性確認まで行う必要がある。

### Page 53
- **記載内容**: maximal strategy の slack 解析と three regimes。`lambda` の値域別に勝敗を分ける土台を作る。
- **競技転用**: parameter regime の分割は、しきい値を持つ transformation rule の推定に有効。
- **実験案**: 入力の大きさや parity や modulo で regime を分ける teacher trace を作る。
- **注意**: regime 間の境界条件を曖昧にしない。

### Page 54
- **記載内容**: `lambda = sqrt(2)/2` などの境界ケースの解析。引き分けケースを示す。
- **競技転用**: **境界ケースを明示的に処理する**癖が重要。パズルでも off-by-one, tie case, zero case で落としやすい。
- **実験案**: zero / minimum / tie / equality case を別カテゴリとして synthetic に増やす。
- **注意**: 境界ケースは少数でも score を大きく落とすので軽視しない。

### Page 55
- **記載内容**: final answer と、その戦略が合法で勝ちにつながることの確認。
- **競技転用**: **答え + 合法性確認**という締め方は、ルール推定問題でも「この答えでサンプルを全て説明できる」確認に対応する。
- **実験案**: final answer の直前に 1 行の self-check を入れる teacher trace を検討する。
- **注意**: self-check の後に別候補を並べないこと。

### Page 56
- **記載内容**: human expert comment。proof に「thinking process 的な痕跡」が残っているが、内容は完成しており 7/7 と評価される。
- **競技転用**: exploratory trace が多少残っても correctness は成立し得るが、本競技では **max_tokens=7680** と boxed metric のため、最終的にはもっと整理された trace が望ましい。
- **実験案**: 初回 synthetic では自然な探索を許し、最終 teacher では冗長な自己修正を削る二段階生成にする。
- **注意**: thinking 痕跡が長すぎると truncation や format 崩れを招く。

### Page 57
- **記載内容**: References 開始。safety dataset、on-policy distillation、OpenAI 系モデルなど、SFT / RL / distillation に関わる主要出典が並ぶ。
- **競技転用**: 参照すべきキーワードは **on-policy distillation** と **safety/alignment データ設計**。特に distillation 論文群は競技向け low-budget 高効率化に直結する。
- **実験案**: RL より distillation を優先する設計の根拠文献として追跡する。
- **注意**: 参考文献ページ自体から直接 recipe は得にくい。深掘りの入口として使う。

### Page 58
- **記載内容**: WMT24++, CL-Bench など long-context / multilingual / context learning 系の出典が続く。
- **競技転用**: 本競技では直接価値は低め。ただし **context learning** の観点は、few-shot 的な rule induction の理解にヒントを与える。
- **実験案**: 必要なら context-heavy synthetic の少量追加は検討できるが、優先度は低い。
- **注意**: ここに寄りすぎると puzzle reasoning の主戦場から外れる。

### Page 59
- **記載内容**: HardTests, safety, benchmark 群の出典。コード難問化や保護手法の参照先が含まれる。
- **競技転用**: 特に **HardTests 的な「難しいが検証可能な問題を作る」思想**が有用。変換ルール問題でも hard synthetic 生成へ応用できる。
- **実験案**: synthetic 問題を難化させる際に、単なるノイズ増加ではなく「検証可能な難化」を意識する。
- **注意**: 難化しすぎて verifier 不安定になると逆効果。

### Page 60
- **記載内容**: AceReason-Nemotron 1.1、LM-Provers など、math/code reasoning と proof 系の出典が見える。
- **競技転用**: **math と code を横断して reasoning を鍛える**、**proof 能力を小型モデルへ教える**という方向性は本競技にも参考になる。
- **実験案**: puzzle 用 synthetic でも、answer-only ではなく「推論規則の説明」教師を併用する。
- **注意**: proof タスクそのものを増やす必要はない。必要なのは structured reasoning の骨格だけ。

### Page 61
- **記載内容**: RLHF の古典、SWE-Gym など、alignment と agentic SWE の基礎文献が並ぶ。
- **競技転用**: RLHF を全面採用する必要はないが、**人間好みではなく出力の安定化・簡潔化**のために軽い preference 学習を使う根拠になる。
- **実験案**: 正答同士の pairwise preference で、より短く boxed が明確なものを優先する。
- **注意**: 人間評価最適化をやりすぎると、本競技の exact answer 指標からズレる。

### Page 62
- **記載内容**: OpenHands など agentic coding scaffold の文献が続く。
- **競技転用**: 直接の競技価値は低いが、**環境フィードバックを使った学習**という発想は exact-answer verifier へ読み替えられる。
- **実験案**: ローカルで answer checker を環境化し、誤答修正データ生成に使う。
- **注意**: scaffold 実装そのものへ時間を使うより、データ品質へ工数を回すべき。

### Page 63
- **記載内容**: DAPO や GLM-5 など RL/agentic engineering 系の文献で参考文献が終わる。
- **競技転用**: 大規模 RL システムの存在は確認できるが、本競技への現実的転用は **SFT + distillation + metric-aware validation** が中心になる。
- **実験案**: RL システムを新規導入するより、まず high-quality verified data pipeline を整える。
- **注意**: 参考文献の豊富さに引っ張られてスコープを広げすぎない。

---

## 5. 競技に本当に効く論文由来のアクション項目

### 最優先

- `\boxed{}` を前提にした SFT データへ統一する。
- final answer の一意性を強く学習させる。
- hard-example mining を行う。
- solver / verifier で正答確認した synthetic data だけを主力にする。
- 多数生成・自己修正・tool-assisted 解法は **offline teacher 生成専用**にする。

### 中優先

- shorter-but-correct な pairwise preference を入れる。
- 最近の有効 reasoning だけを残した短縮 trace を作る。
- error-correction データ（誤答→修正版）を入れる。

### 低優先

- long-context 強化
- multilingual 強化
- terminal / SWE / conversational agent 能力の直接強化
- 人間好みの creative alignment

---

## 6. この論文を競技に使うときの危険な誤読

1. **「論文は長い推論で強い」→ なら自分も長く出せばよい**
   - 誤り。競技は `max_tokens=7680`、`temperature=0.0`。
   - 必要なのは長い推論そのものではなく、**長い探索から短い単発正答を蒸留すること**。

2. **「tool use が強い」→ 本番でも tool が使えるはず**
   - 誤り。README 上、本番は LoRA + vLLM 推論であり、外部ツールを期待しない方が安全。

3. **「IMO/IOI で勝っている」→ 何でも混ぜれば上がる**
   - 誤り。論文自身が domain interference を強く意識している。競技は puzzle reasoning に絞るべき。

4. **「RL をやれば最強」**
   - 誤り。低予算・LoRA 制約下では、まず **verified SFT + distillation + format alignment** の方が現実的で強い可能性が高い。

---

## 7. 最終結論

この論文を `README.md` の競技に最大活用するうえでの本質は、**Cascade RL そのものを再現することではない**。

本当に持ち帰るべきなのは、次の 5 点である。

- **正答検証付きデータしか信じない**
- **出力形式を学習対象として明示的に鍛える**
- **easy を薄く、hard を厚くする**
- **段階を分けて干渉を減らす**
- **test-time scaling の利益は offline distillation へ変換する**

この競技は knowledge benchmark ではなく、**変換規則を見抜き、boxed で一意に答え切る単発 deterministic 推論**の勝負である。

したがって、Nemotron-Cascade 2 から最も価値があるのは、豪華な benchmark の数字そのものではなく、**高品質な reasoning teacher をどう作り、どう短く正確な単発出力へ圧縮するか**という設計思想である。
