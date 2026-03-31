結論だけ先に言うと、**この binary / bit_manipulation 問題に GRPO を入れるなら、最重要なのは「GRPO そのもの」よりも、**  
**(1) verifiable reward に最適化した binary 専用カリキュラム、(2) short-output 化、(3) warm-start** です。  
参考文献・実装としては、**理論は DeepSeekMath → DeepSeek-R1 → Minimal-RL / R1-Zero critique / DAPO / L1**、**実装は TRL と NVIDIA NeMo RL を軸**に見るのが効率的です。Nemotron 側も公式に **Nemotron 3 Nano の RLVR with GRPO** と **NeMo RL / NeMo Gym** を公開しているので、コンペ対象モデルとの整合性はかなり高いです。 

---

## まず、あなたのケースで最も参考になる論文ランキング

### 1) **DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models**
GRPO の**出発点**として最重要です。DeepSeekMath は GRPO を「PPO よりメモリ効率よく数理推論を伸ばす方法」として提示した元論文で、さらに公式 repo では `\boxed{}` を含む math-style prompting も明示されています。  
あなたの binary 問題は math ではないですが、**「正解が自動検証できる」「最終回答が strict format を持つ」**という点でかなり近いです。まずここで **GRPO の基本設計思想**を押さえるべきです。 

### 2) **DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning**
GRPO を**実戦 pipeline にどう埋め込むか**を見るならこれです。R1 系は、RL だけでなく、cold start・rejection sampling・再SFT などを含む多段構成が重要でした。Nature の要約でも、**信頼できる reward が取れるタスクでは RL を強く使い、信頼できないタスクでは人手 supervision を使う**設計が示されています。  
binary 問題は verifier を作りやすいので、**R1 的には RLVR 向き**です。ただし、R1 的発想でも **いきなり純RLに飛ばず、warm-start を入れる**のが筋です。 

### 3) **A Minimalist Approach to LLM Reasoning: from Rejection Sampling to Reinforce**
これはあなたの計画と非常に相性が良いです。公式 repo の README では、  
- **RAFT++/rejection sampling が序盤でかなり強い**  
- **負例が探索維持に重要**  
- **all-correct / all-incorrect な prompt group が harmful**  
- **GRPO の利得の一部は reward 正規化より「悪い group を暗黙に弾くこと」にある**  
と整理されています。  
binary のように **正解軌跡密度が低いタスク**では、これはかなり本質的です。つまり、**answer-only / rejection sampling / reinforce-rej 的 warm-start を先に作ってから GRPO**が合理的です。 

### 4) **Understanding R1-Zero-Like Training: A Critical Perspective**
binary に特に重要なのは、この論文が指摘する **GRPO の length bias** です。要約では、GRPO に**誤答側の出力���を不自然に伸ばす最適化バイアス**がありうると述べています。  
あなたの binary 問題では、長文化・最後の数字崩壊・boxed 崩れがすでにボトルネックなので、この論文はかなり直接的に効きます。**「binary では max completion を短く」「length reward / penalty を入れる」「長い CoT を褒めない」**という設計の根拠になります。 

### 5) **DAPO: An Open-Source LLM Reinforcement Learning System at Scale**
これは「GRPO をまずやるべきか？」への答えを少し更新していて、**GRPO が不安定なら DAPO 系へ寄せる**価値があります。DAPO は GRPO を拡張して、**dynamic sampling、token-level policy gradient、overlong reward shaping** などを入れています。NVIDIA の NeMo RL 公式 repo でも、DAPO を **GRPO 拡張の安定化版**として説明しています。  
binary は sparse reward かつ長文化が harmful なので、**GRPO の first baseline を取ったあと、DAPO を最有力 ablation**に置くのが良いです。 

### 6) **L1: Controlling How Long A Reasoning Model Thinks With Reinforcement Learning**
binary のような exact-answer 問題では、**「より賢くする」だけでなく「短く終わらせる」**ことが重要です。L1 は RL によって reasoning 長を制御する方向を明示的に扱っています。  
あなたの設定では、推論の質そのものより、**不要に長い reasoning が exact 8-bit 出力契約を壊す**危険が高いので、L1 はかなり参考になります。 

### 7) **Concise Reasoning via Reinforcement Learning**
これも同じく、**正答率を落とさず推論を短くする**方向の論文で、binary には相性が良いです。  
特にあなたのケースでは、長い reasoning よりも **最終 `\boxed{00110100}` を壊さず出すこと**が重要なので、conciseness 系の報酬設計はそのまま応用できます。 

### 8) **Logic-RL: Unleashing LLM Reasoning with Rule-Based Reinforcement Learning**
binary/bit_manipulation は、数学というより **ルール発見型の symbolic reasoning** に近いので、この論文はかなり近縁です。  
特に「rule-based reward で reasoning を押す」という視点は、**binary 専用の verifier / generator を作る**というあなたの方針と合っています。 

### 9) **REASONING GYM: Reasoning Environments for Reinforcement Learning with Verifiable Rewards**
これはアルゴリズム論文というより、**無限に近い verifiable task 生成の発想源**として重要です。repo では 100 以上の task と、**algorithmically verifiable** な scoring、runtime 生成、difficulty 調整が提供されています。  
あなたの binary 問題で本当に効くのは、1,602 行の実データだけではなく、**同型の procedural binary task generator を作って success density を上げること**です。その設計思想として最も参考になります。 

---

## 実装のおすすめランキング

### 1) **Hugging Face TRL `GRPOTrainer`**
**最初の実験はこれがベスト**です。理由は明確で、公式 docs で  
- custom `reward_funcs`  
- 複数 reward の加重和  
- PEFT / LoRA  
- vLLM 連携  
- `vllm_structured_outputs_regex`  
- OpenEnv / 環境連携  
が揃っているからです。  
binary の最初の GRPO プロトタイプでは、**TRL + PEFT + vLLM** が最短距離です。特に `vllm_structured_outputs_regex` があるので、訓練時だけでも `\boxed{[01]{8}}` に近い出力規律を強制しやすいです。 

**向いている用途**
- 1〜数GPUでの高速プロトタイピング
- binary-only specialist LoRA
- reward 関数の試行錯誤
- ORPO / GRPO の比較実験

---

### 2) **NVIDIA NeMo RL + NeMo Gym**
**コンペ対象が Nemotron**なので、最終的に一番相性が良いのはこれです。Nemotron 公式 repo は Nemotron 3 Nano recipe に **multi-environment RLVR with GRPO** を含めており、NeMo RL repo には `run_grpo.py` の reference config があり、NeMo Gym docs では **custom verifier / tools / resource server** を自作する流れが整理されています。  
つまり、**Nemotron-native にやり切るなら最も本命**です。重いですが、あなたが「binary 用の custom environment / verifier」を作るなら一番自然です。 

**向いている用��**
- Nemotron に寄せた本番パイプライン
- procedural binary environment の自作
- multi-node / multi-GPU での本格 RLVR
- DAPO への移行

---

### 3) **verl**
**大規模にやるなら最強クラス**です。verl は公式 repo で PPO/GRPO/DAPO をサポートし、2025 以降は DAPO recipe や LoRA 対応も明示されています。  
ただし、最初からこれで入るとやや重いので、**TRL で reward 設計が固まってから verl へ移す**のが良いです。binary 問題で GRPO の先に DAPO, GSPO, replay 系まで見たいなら、verl は非常に有力です。 

**向いている用��**
- DAPO への upgrade
- 高スループット rollout
- 長めの RL 実験
- multi-node 本番運用

---

### 4) **OpenRLHF**
OpenRLHF も GRPO 実装を持つ実用フレームワークです。repo では PPO / GRPO / REINFORCE++ などを実装しており、vLLM や Ray ベースの高性能化も入っています。  
ただ、README のニュース欄自体が **REINFORCE++ の安定性が GRPO より高い**という最近の流れにも触れているので、**GRPO を絶対視せず、baseline/ablation 用**として見るのが良いです。 

**向いている用途**
- GRPO vs REINFORCE++ 比較
- Ray ベース RLHF/RLVR
- 実装読みでアルゴリズム差分を見る用途

---

## このコンペの binary 問題に、どう GRPO を落とし込むべきか

### 提案 1: **shared adapter ではなく binary specialist LoRA**
論文群を踏まえると、binary のような **verifiable かつ format-sensitive** な問題は、general SFT 混合より **specialist 化**が向いています。  
DeepSeek-R1 系の実務知見、Minimal-RL の warm-start 知見、R1-Zero critique の length bias を合わせると、**binary-only outcome optimization** に振るのが自然です。 

### 提案 2: **いきなり GRPO ではなく、RS/SFT warm-start → GRPO**
あなたの現状分析どおり、hard binary に sparse exact reward だけで GRPO を直打ちすると、**correct trajectory がほぼ出ない**可能性が高いです。  
そこで、まず  
1. answer-only short SFT  
2. rejection sampling で正解軌跡抽出  
3. その後に GRPO  
の順がよいです。これは DeepSeek-R1 的でもあり、Minimal-RL の結果とも整合的です。 

### 提案 3: **reward は「ほぼ exact-only」、ただし初期だけ軽い shaping**
NeMo Gym / TRL のドキュメントでも、Wordle や Sudoku では **binary reward がきれいに効く**���されています。binary 問題でも最終的にはそうです。  
ただし学習初期だけは、  
- strict exact match: `+1.0`  
- strict format match (`\boxed{[01]{8}}`): `+0.05`  
- extra digits outside box: `-0.05`  
- overlong output: 小さい負報酬  
- Hamming 類似: ごく小さく、後半で 0 に anneal  
くらいはありです。最終段階では **exact reward を主**にして、near-miss 最適化を切るべきです。 

### 提案 4: **長さ制御は必須**
R1-Zero critique、L1、Concise RL の3本を見ても、GRPO 系では**長さを放置すると harmful**になりがちです。  
このコンペの binary は特に、長い reasoning が有利というより **最後の 8-bit を壊すノイズ**になりやすいので、  
- `max_completion_length` を短めにする  
- length penalty を入れる  
- teacher を short boxed-answer 中心にする  
が重要です。 

### 提案 5: **procedural synthetic binary generator を作る**
Reasoning Gym の思想をそのまま持ち込むべきです。  
実データだけでなく、  
- permutation / inversion  
- affine XOR  
- boolean 2/3  
- structured-byte formula  
- choose / majority  
- family confusion を含む hard negatives  
を procedural に生成し、difficulty を段階化して RL に流すと、GRPO の成功率が上がります。  
これはあなたの「synthetic curriculum → real verified → real all-non-exclude」という計画と一致しています。 

---

## 実装スタックの推奨

### もっとも実務的な第一候補
**TRL + PEFT + vLLM + custom reward_func** です。  
理由は、最初の 1〜2 週間で必要なのが  
- reward 実験  
- output shortness 実験  
- exact/format penalty 実験  
- binary-only specialist LoRA  
だからです。TRL はその全部が最短で回せます。さらに PEFT と vLLM の両方が公式対応です。 

### 公式整合性を最大化する第二候補
**NeMo RL + NeMo Gym + Nemotron recipe** です。  
Nemotron repo 自体が Nano について **GRPO を含む RLVR recipe** を出しているので、最終的に Nemotron-3-Nano-30B へ寄せるならここが一番きれいです。 

### GRPO が不安定だったときの第三候補
**verl で DAPO ablation** です。  
binary は sparse reward・length sensitivity・group variance 問題を持つので、GRPO plateau が来たら DAPO へ移る価値が高いです。verl はその最有力実装です。 

---

## 私ならこう進めます

### Phase 0: SFT/RS warm-start
- binary non-exclude 全部を使う  
- 出力の大半を `\boxed{xxxxxxxx}` only にする  
- 少量だけ短い 1-line scratchpad を混ぜる  
- rejection sampling で成功軌跡を増やす 

### Phase 1: binary-only GRPO
- framework: TRL  
- `num_generations=4~8`  
- short `max_completion_length`  
- reward: exact 主 + format 補助 + small length penalty  
- 必要なら `vllm_structured_outputs_regex` を訓練時のみ使う 

### Phase 2: synthetic curriculum
- easy affine / permutation から入る  
- 次に structured-byte と ambiguity-rich を混ぜる  
- 最後に real verified / answer-only / manual を混ぜる 

### Phase 3: unstable なら DAPO
- overlong shaping  
- dynamic sampling  
- token-level policy gradient  
を持つ DAPO に切り替えて比較する 

### Phase 4: general adapter と merge
- binary specialist を独立 LoRA として育てる  
- その後 general anchor と merge / ablate する  
- 少なくとも研究段階では strict exact 8-bit を主指標にする 

---

## 最終的なおすすめセット

**論文 / 技術レポート**
1. DeepSeekMath  
2. DeepSeek-R1  
3. A Minimalist Approach to LLM Reasoning  
4. Understanding R1-Zero-Like Training  
5. DAPO  
6. L1  
7. Concise Reasoning via RL  
8. Logic-RL  
9. Reasoning Gym 

**Github / 実装**
1. TRL `GRPOTrainer`  
2. NVIDIA NeMo RL  
3. NVIDIA NeMo Gym  
4. NVIDIA Nemotron repo  
5. verl  
6. OpenRLHF  
7. Reasoning Gym  
8. RLHFlow/Minimal-RL 

---
