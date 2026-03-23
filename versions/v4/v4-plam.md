v4-plam.md
Version: 0.1
Owner: me
Prerequisite: `versions/v0/v0-plan.md` 完了済み / `versions/v1/v1-plam.md` 完了済み / `versions/v2/v2-plam.md` 完了済み / `versions/v3/v3-plam.md` の stable trunk・weighted runtime・logging が揃っていること（v3 の残タスクは並行継続可）
Scope: `versions/plan-overview.md` のうち、`3-7〜3-11`, `7-2〜7-5`, `8-1〜8-3` を、v3 の best trunk と実測失敗知見を前提に **Stage C preference / RFT / specialist merge / local-score-gated promotion** として固定する
Purpose: v3 で実働化した strong SFT / weighted runtime / Mac-to-CUDA handoff を土台に、**良いローカルスコアが確認できた candidate だけを CUDA BF16 再現・提出候補へ送る v4 の実戦ループ** を作る

## 0. この v4 の位置づけ

v0 で固定したのは、以後の全 version でぶらしてはいけない前提だった。

- Source of Truth の優先順位
- official evaluation 条件
- visible `test.csv` の扱い
- competition prompt の不変条件
- 採用基準の骨格

v1 で作ったのは、毎日回す評価基盤だった。

- metric-faithful local evaluator
- extraction risk suite
- deterministic metadata / parser / splits / eval packs
- official deterministic eval と stochastic probe eval

v2 で作ったのは、データ生成・学習基盤だった。

- real canonical data
- solver / generator / validator registry
- synth / distill / correction / format pool
- Stage A / Stage B train mix
- Mac-first training substrate
- packaging gate と promotion rule

v3 で作ったのは、最初の実戦 SFT ループだった。

- real teacher trace / strict pair / preference / RFT pool builder
- weighted Stage A / Stage B strong mix
- custom weighted MLX SFT runtime
- candidate registry と CUDA reproduction handoff

ただし、v3 の実測から分かったこともある。

- teacher trace pipeline 自体は動いたが、sampled run では strict accepted が `0 / 8` だった
- tiny Mac pilot loss では Stage A が Stage B より明確に良かった
- weighted SFT runtime は動いたが、shadow / hard split での local score 改善はまだ証明していない
- したがって v3 完了時点では「提出価値のある strong candidate が確定した」とは言えない

よって v4 は、**SFT をさらに広げる版ではない**。

v4 は、`versions/plan-overview.md` にある

- 3-7 preference 学習
- 3-8 RFT
- 3-10 specialist adapter merge
- 3-11 checkpoint / adapter soup
- 7-2〜7-5 の candidate / submission policy

を、v3 の best trunk とログを前提に **実際のローカルスコア改善へ結び付ける版** とする。

この v4 の責務は、次の 8 点に限定する。

1. v3 の best trunk を起点に、local score を証明する candidate scoring loop を固定する
2. clean-vs-dirty format と correct-vs-incorrect output の chosen / rejected pair を deterministic に作る
3. multi-sample generation + exact / format reward による RFT accept pool を作る
4. Stage C として、RFT と preference 学習を小さく安全に回せる形へ固定する
5. Stage B を無理に本命化せず、まず Stage A trunk 中心で improvement を確認する
6. bit / text / symbol / format specialist を必要時のみ切り、merge / soup / rank32 compression を比較可能にする
7. failure-inclusive logging と candidate scoreboard を整え、なぜ良くなったか / 悪くなったかを追えるようにする
8. 良いローカルスコアが出た candidate だけを CUDA BF16 + PEFT 再現・提出候補へ送る

重要なのは、v4 が **「いきなり true RL を実装する版」でも「提出を量産する版」でもない** こと。

また、v4 は **まだ準備だけを続ける版でもない**。

v4 の最初の数ステップには準備がある。

- Stage A / Stage B trunk の baseline scoring
- preference pair builder
- RFT accept pool builder

しかし、これは v2 / v3 のような長い基盤整備ではなく、**local score を実際に改善するための直前準備** である。
v4 は Step 1〜3 が終わったら、すぐに Stage C candidate 実験へ入る。

v4 の最重要成功条件は、

- local overall / hard split / hard family のどこが改善したかを証明できる
- improvement が format fail / extraction fail / family collapse で相殺されていない
- その candidate を CUDA へ再実装できる

の 3 点である。

## 1. v4 で絶対に継承する前提

### 1-1. official evaluation の正は v0 / v1 を継承する

本番相当の採用判定は、以後も `README.md` と v0 / v1 の整理を継承した `official_lb` を正とする。

- `temperature = 0.0`
- `top_p = 1.0`
- `max_tokens = 7680`
- `max_num_seqs = 64`
- `max_model_len = 8192`
- `gpu_memory_utilization = 0.85`
- `enable_thinking = True`
- `add_generation_prompt = True`

teacher sampling / RFT accept mining / probe では別 config を使ってよいが、採用判定は reopen しない。

### 1-2. visible `test.csv` は今後も validation に使わない

`README.md` と既存分析どおり、visible `test.csv` は sample-only であり `train.csv` と重複する。
v4 でも用途は次に限定する。

- submission zip の smoke
- packaging load の整合確認
- final formatter の最終確認

学習採用や split 評価には使わない。

### 1-3. v1 evaluator / extractor / verify は不変

v4 は Stage C を導入するが、採点ロジックを勝手に変えてはならない。
以後の評価は v1 の metric-faithful 実装を使う。

特に固定するもの:

- boxed 優先 / fallback 付き extraction 順序
- `verify()` の exact / numeric tolerance
- `}` を含む answer に対する boxed risk の扱い
- competition prompt builder の形

### 1-4. 合成ラベルと accept pool は solver / validator ベースでしか採用しない

`SYNTHETIC_DATA_AUGMENTATION_POLICY.md` を継承し、v4 でも次を必須にする。

- programmatic generator + exact solver
- または proposal + independent validator
- または v1 evaluator で exact correct かつ format-safe と確認された accepted output

禁止:

- LLM が answer を直接決め、そのまま採用
- validator なし freeform synthetic / freeform accepted output を本学習へ投入
- real-only validation を悪化させても投入継続

### 1-5. リポジトリ規約として code は 1 ファイルに集約する

version ごとのコア実装は `versions/vN/code/` 配下の単一ファイルに置く。
したがって v4 でも code の中心は次で固定する。

- `versions/v4/code/train.py`

config / data / reports / tests は複数ファイルでよいが、主実装は 1 ファイルにまとめる。

### 1-6. 実行環境は Mac 固定だが、役割は Stage C 探索と candidate 選別である

以後の daily experimentation loop は **macOS 上で完結できること** を前提にする。
固定 local model は次を継続利用する。

- `lmstudio-community/NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-6bit`

ローカル primary workload は次に固定する。

- best candidate の shadow / hard split 評価
- multi-sample generation による chosen / rejected pair と RFT accept mining
- RFT / preference / specialist の pilot / ablation
- merge / soup / compression の候補生成
- candidate registry / score registry / CUDA reproduction spec 出力

ただし、Mac 上の学習成果物は提出候補そのものではなく、勝ち筋の仮説検証用とみなす。
v4 でも、Mac で昇格した recipe は Kaggle CUDA GPU (`A6000 Pro` 48GB / 96GB 級) 上で **BF16 + PEFT** により再学習し、その CUDA artifact だけを提出候補として扱う。

### 1-7. submission target schema は引き続き PEFT で、rank は 32 以下

`README.md` の提出条件を継承する。

- NVIDIA Nemotron-3-Nano-30B base model 向け LoRA
- rank は高々 `32`
- `adapter_config.json` を含む
- `submission.zip` に packaging する

merge / soup 後も最終的には rank32 へ圧縮または rank32 互換状態に戻す。

### 1-8. 良いローカルスコアが出ていない candidate は無理に提出しない

v4 では submission policy を次で固定する。

- local overall best を更新していない
- hard split / hard family の改善が見えていない
- extraction fail / format fail の改善が見えていない

のいずれにも当てはまらない candidate は、**packaging smoke が通っても submit queue へは載せない**。

逆に、

- local overall best 更新
- hard split または bit / text / symbol の明確改善
- extraction fail / format fail 改善
- leaderboard で仮説価値が高い

のいずれかがあり、かつ packaging / load smoke が clean なら、1 日 5 回の枠を前提に積極的に submit queue に載せてよい。

## 2. v4 の最終成果物

v4 完了時点で、少なくとも以下が揃っていることを完了条件とする。

### 2-1. 必須成果物

1. `format_preference_pairs_v4.parquet`
2. `correctness_preference_pairs_v4.parquet`
3. `stage_c_preference_registry_v4.parquet`
4. `rft_candidate_generations_v4.jsonl`
5. `rft_accept_pool_v4.parquet`
6. `rft_registry_v4.parquet`
7. `stage_c_rft_mix_v4.parquet`
8. `stage_c_preference_mix_v4.parquet`
9. `local_scoreboard_v4.csv`
10. `family_regret_report_v4.csv`
11. `specialist_candidate_registry_v4.csv`
12. `merge_candidate_registry_v4.csv`
13. `candidate_registry_v4.csv`
14. `cuda_reproduction_spec_v4.yaml`
15. `cuda_reproduction_registry_v4.csv`
16. `submission_manifest_v4.json`
17. `training_command_book_v4.txt`
18. `promotion_rules_v4.txt`
19. v4 tests
20. `versions/v4/code/train.py`

`submission_v4.zip` は **good local score gate を通過した candidate が出た場合のみ** 必須成果物に追加する。

### 2-2. v4 が提供すべき運用価値

v4 完了後は、以後の version が少なくとも次を再利用できる状態にする。

- chosen / rejected pair の deterministic schema
- RFT accept pool の deterministic schema
- Stage C candidate を local score で比較する scoreboard
- specialist / merge / soup の比較台帳
- Mac で見つけた Stage C / merge candidate を CUDA / BF16 PEFT run へ handoff する共通 schema
- 「なぜ submit する / しないか」を説明できる promotion rule

## 3. 追加ディレクトリ構成

v4 は次の構成で作る。
ここでも **code は 1 ファイル**、その周辺の config / data / tests / reports を version 配下に持つ。

```text
versions/v4/
├── v4-plam.md
├── code/
│   └── train.py
├── conf/
│   ├── data/
│   │   ├── preference_format.yaml
│   │   ├── preference_correctness.yaml
│   │   ├── rft_accept_pool.yaml
│   │   ├── stage_c_rft_mix.yaml
│   │   ├── stage_c_preference_mix.yaml
│   │   └── specialist_sampling.yaml
│   ├── train/
│   │   ├── rft_stage_c_mlx.yaml
│   │   ├── dpo_format_mlx.yaml
│   │   ├── dpo_correctness_mlx.yaml
│   │   ├── specialist_bit_mlx.yaml
│   │   ├── specialist_text_mlx.yaml
│   │   ├── specialist_symbol_mlx.yaml
│   │   ├── specialist_format_mlx.yaml
│   │   ├── stage_c_cuda_bf16.yaml
│   │   └── merge_hardening_cuda_bf16.yaml
│   ├── eval/
│   │   ├── candidate_score_quick.yaml
│   │   ├── candidate_score_serious.yaml
│   │   └── candidate_score_weekly.yaml
│   ├── merge/
│   │   ├── generalist_specialist_merge.yaml
│   │   ├── checkpoint_soup.yaml
│   │   └── rank32_compress.yaml
│   └── package/
│       └── cuda_submission_smoke.yaml
├── data/
│   ├── processed/
│   │   ├── stage_c_preference_registry_v4.parquet
│   │   ├── rft_registry_v4.parquet
│   │   ├── score_cache_v4.parquet
│   │   └── candidate_feature_table_v4.parquet
│   ├── preference/
│   │   ├── format_preference_pairs_v4.parquet
│   │   ├── correctness_preference_pairs_v4.parquet
│   │   └── preference_pair_audit_v4.parquet
│   ├── rft/
│   │   ├── rft_candidate_generations_v4.jsonl
│   │   └── rft_accept_pool_v4.parquet
│   └── train_packs/
│       ├── stage_c_rft_mix_v4.parquet
│       └── stage_c_preference_mix_v4.parquet
├── outputs/
│   ├── eval/
│   ├── reports/
│   ├── audits/
│   ├── handoff/
│   ├── packaging/
│   └── train/
└── tests/
    ├── test_v4_bootstrap.py
    ├── test_v4_preference_builders.py
    ├── test_v4_rft_registry.py
    ├── test_v4_scoreboard.py
    ├── test_v4_merge_spec.py
    └── test_v4_promotion_gate.py
```

## 4. `versions/v4/code/train.py` の責務

### 4-1. コア責務

`versions/v4/code/train.py` は、少なくとも次の責務を持つ。

1. v1 / v2 / v3 artifact を読む bootstrap
2. candidate row-level eval をまとめて score registry 化する
3. clean-vs-dirty format pair builder
4. correct-vs-incorrect pair builder
5. multi-sample generation と RFT accept pool builder
6. Stage C mix builder
7. RFT / preference / specialist の manifest と実行 entrypoint
8. merge / soup / rank32 compression 用 manifest builder
9. candidate scoreboard / family regret report 出力
10. CUDA reproduction spec / packaging spec / runbook 出力

### 4-2. 想定 subcommand

最低限、次を持つ。

- `bootstrap-v4`
- `score-candidate`
- `score-candidate-batch`
- `build-format-preferences`
- `build-correctness-preferences`
- `build-rft-candidates`
- `filter-rft-accept-pool`
- `build-stage-c-mix`
- `train-stage-c-rft`
- `train-stage-c-preference`
- `train-specialist`
- `merge-candidates`
- `compress-merge-rank32`
- `render-cuda-repro-spec`
- `package-peft`
- `write-runbook`

重要なのは、v4 でも **builder / manifest / score registry / handoff spec が先、重い学習実行はその後** という順を守ることである。

## 5. v4 では local-score proving loop を先に固定する

### 5-1. 評価対象 candidate の起点

v4 の trunk 候補は、まず次を起点にする。

1. v3 Stage A best trunk
2. v3 Stage B trunk（比較用のみ）
3. v2 best generalist（回帰検知用のみ）

初期の本命は **v3 Stage A trunk** とする。
理由:

- tiny Mac pilot loss では Stage A が Stage B より良かった
- Stage B は correction-heavy で、現時点では over-hardening の疑いがある
- v4 は Stage C の上積みを見たいので、まずは最も clean な trunk から始めるほうがよい

### 5-2. v4 の 3 系統 score gate

v4 の candidate 採用判断は、v1 evaluator を使って次の 3 段階で固定する。

1. quick gate
   - `shadow_128`
   - family accuracy
   - extraction fail / format fail

2. serious gate
   - `shadow_256`
   - `hard_shadow_256`
   - hard family metrics (`bit`, `text`, `symbol`)

3. weekly gate
   - group-shift split
   - family-hard split
   - optional stochastic probe

overall だけで判断してはいけない。
少なくとも次を candidate registry に残す。

- `overall_accuracy`
- `hard_split_accuracy`
- family 別 accuracy
- `format_fail_rate`
- `extraction_fail_rate`
- `avg_output_len`
- `has_boxed_rate`
- `unsafe_boxed_rate`
- `candidate_status`

### 5-3. `local_scoreboard_v4.csv` の必須列

最低限、次を持つ。

- `candidate_id`
- `parent_candidate_id`
- `recipe_stage`
- `recipe_type`
- `base_trunk`
- `split_name`
- `overall_accuracy`
- `hard_split_accuracy`
- `bit_accuracy`
- `text_accuracy`
- `symbol_accuracy`
- `format_fail_rate`
- `extraction_fail_rate`
- `avg_output_len`
- `packaging_smoke_pass`
- `cuda_ready`
- `submit_value`
- `notes`

### 5-4. v4 の promotion / rejection rule

submit queue に載せる条件は、少なくとも次のいずれかを満たすこと。

1. serious gate の `overall_accuracy` が local best を更新
2. `hard_split_accuracy` が明確に改善
3. `bit` / `text` / `symbol` のいずれかで明確改善し、他 family が崩れていない
4. `format_fail_rate` または `extraction_fail_rate` が有意に改善

却下条件:

- overall 改善なし、hard split 改善なし、format 改善なし
- roman / unit だけ伸びて難 family が落ちる
- extra trailing numbers や unsafe boxed が増える
- packaging smoke に失敗

## 6. preference pair を v4 で実戦投入する

### 6-1. format preference の chosen / rejected

format preference は、`versions/plan-overview.md` の clean-vs-dirty format 方針を v4 で固定する。

chosen:

- exact correct
- extraction safe
- final answer line が clean
- final answer の後に余計な数字がない
- unsafe answer に boxed を使っていない

rejected:

- correct だが extraction unsafe
- correct だが最後に余計な数字がある
- boxed malformed / multiple boxed
- clean final line が崩れている

初期データ源:

- `preference_pairs_v3.parquet`
- `format_pairs_strict_v3.parquet`
- v4 で新たに current trunk から採った raw outputs

### 6-2. correctness preference の chosen / rejected

correctness preference は、特に hard family に効かせる。

chosen:

- K-sample 中で exact correct
- その中でも shortest-clean または most format-safe
- family canonical form に一致

rejected:

- wrong answer
- almost correct だが verify で落ちる
- wrong rounding
- wrong formatting で extraction を壊す

優先 family:

- `bit_manipulation`
- `text_decryption`
- `symbol_equation`

roman / unit / gravity は replay と回帰監視を主にし、pair 学習で重くしすぎない。

### 6-3. `stage_c_preference_registry_v4.parquet` の必須列

最低限、次を持つ。

- `pair_id`
- `pair_type`
- `source_candidate_id`
- `family`
- `difficulty_tags`
- `chosen_text`
- `rejected_text`
- `chosen_exact`
- `rejected_exact`
- `chosen_format_safe`
- `rejected_format_safe`
- `chosen_length`
- `rejected_length`
- `selection_reason`
- `acceptance_status`

### 6-4. oversampling と pair 構成の初期値

初期構成は次で始める。

- format preference: `50%`
- correctness preference: `50%`

family 別 oversampling 初期案:

- bit: `1.3x`
- gravity: `0.9x`
- unit: `0.8x`
- text: `1.4x`
- roman: `0.6x`
- symbol: `1.6x`

v4 では、pair 生成量を増やすことよりも **chosen / rejected の質** を優先する。

## 7. RFT accept pool を v4 の本命 Stage C とする

### 7-1. RFT は teacher-only ではなく current best candidate も proposer にする

v3 では fixed teacher trace は sampled run で strict pass が弱かった。
したがって v4 では、RFT proposer を次の 2 系統に広げる。

1. fixed teacher
2. current best Stage A trunk またはその CUDA reproduction candidate

優先順位は **current best trunk > teacher** とする。
理由は、v4 の目的が「今の candidate を local score で伸ばすこと」であり、teacher trace の理想化ではないからである。

### 7-2. accept 条件

RFT accept の最小条件:

- exact correct
- extraction safe
- final answer line clean
- extra trailing numbers なし
- family canonical form に一致

加点項目:

- short final answer
- unsafe boxed 回避
- family-specific canonical formatting

### 7-3. reward の基本形

true RL はまだやらない。
RFT では accept / reject と auxiliary score のみを使う。

初期 score:

- `+1.0` exact correct
- `+0.2` extraction safe
- `+0.1` short final answer
- `-0.3` extra trailing numbers
- `-0.5` malformed boxed

family 別補助:

- bit: 8bit exact / binary canonical
- roman: uppercase roman canonical
- unit / gravity: numeric parseable / canonical decimals
- text: phrase canonical
- symbol: unwanted spaces / brace risk を抑える

### 7-4. `rft_registry_v4.parquet` の必須列

最低限、次を持つ。

- `candidate_id`
- `source_candidate_id`
- `family`
- `sample_k`
- `accepted_count`
- `accepted_rate`
- `reward_mean`
- `reward_max`
- `best_completion`
- `selection_reason`
- `rejection_reason`
- `format_bucket`
- `status`

### 7-5. replay を少量混ぜる

RFT short finetune は accepted pool だけで閉じず、best Stage A trunk の replay を少量混ぜる。
初期 replay 率は `10%` とする。

理由:

- roman / unit / gravity の既存能力を壊しにくい
- RFT accept pool が hard family 偏重でも generalist trunk を維持できる

## 8. Stage C 学習戦略を v4 で固定する

### 8-1. 実行順の本命

plan-overview の方針と v3 の実測を踏まえ、v4 の本命順は次で固定する。

1. Stage C1: RFT short finetune
2. Stage C2: format preference
3. Stage C3: correctness preference
4. Stage C4: optional short hardening replay

つまり、v4 では **RFT-first, preference-second** を本命にする。

### 8-2. DPO / ORPO の扱い

preference 学習の第一候補は DPO / ORPO とする。
ただし v4 の目的は「ローカル改善を証明すること」であり、loss 名を増やすことではない。

そのため v4 の優先順位は次。

1. RFT only
2. RFT + format DPO
3. RFT + correctness DPO
4. ORPO vs DPO 比較

GRPO / RLVR は v4 の P2 にとどめる。

### 8-3. Stage C mix の初期案

RFT short finetune:

- accepted RFT outputs: `90%`
- best Stage A replay: `10%`

preference pilot:

- format preference: `60%`
- correctness preference: `40%`

ここで Stage B correction-heavy mix を trunk にする必要はない。
Stage B は comparison branch としてのみ残し、v4 本命は Stage A trunk を基準にする。

### 8-4. 学習開始点

初期の base candidate は次の順で使う。

1. `v3-stage-a-pilot-001` 相当の Stage A trunk
2. その CUDA reproduction candidate
3. Stage B trunk は比較用

v4 の最初の問いは、

- Stage A trunk に RFT を足すと local score は上がるか
- format preference を足すと format fail は下がるか
- correctness preference を足すと bit / text / symbol は伸びるか

の 3 点である。

## 9. specialist / merge / soup は v4 で比較可能にする

### 9-1. specialist を切る条件

specialist は常に作るのではなく、次の条件で切る。

- generalist Stage C 候補で hard family がまだ弱い
- その family だけ狙った replay / preference / accepted pool が十分にある
- merge 後に他 family collapse を起こさない見込みがある

初期 specialist 候補:

- bit specialist
- text specialist
- symbol specialist
- format specialist

### 9-2. merge 候補の初期セット

最初に比較する merge は少数精鋭でよい。

1. `0.70 G + 0.10 B + 0.10 T + 0.07 S + 0.03 F`
2. `0.60 G + 0.15 B + 0.10 T + 0.10 S + 0.05 F`
3. generalist checkpoint soup only

その後、

- rank32 compression
- short hardening replay
- serious gate で再評価

までを 1 セットとする。

### 9-3. `merge_candidate_registry_v4.csv` の必須列

最低限、次を持つ。

- `merge_id`
- `generalist_candidate_id`
- `bit_candidate_id`
- `text_candidate_id`
- `symbol_candidate_id`
- `format_candidate_id`
- `merge_weights`
- `compression_method`
- `rank_after_compression`
- `quick_score`
- `serious_score`
- `status`
- `notes`

## 10. v4 で最初に回すべき実験列を固定する

### 10-1. P0: 絶対やる本命実験列

1. v3 Stage A trunk を `shadow_128` / `shadow_256` / `hard_shadow_256` で baseline scoring
2. v3 Stage B trunk を同条件で scoring し、Stage A trunk を本命継続するか確認
3. current best trunk から format preference pair を構築
4. current best trunk から correctness preference pair を構築
5. current best trunk から RFT accept pool を構築
6. `RFT only` Stage C candidate を作る
7. `RFT + format DPO` candidate を作る
8. P0-6 / P0-7 を serious gate で比較
9. top 1〜2 candidate の CUDA BF16 reproduction spec を出す
10. good local score gate を通ったものだけ submit queue に載せる

### 10-2. P1: 高期待値比較

1. format DPO vs correctness DPO
2. DPO vs ORPO
3. `K=4` vs `K=8` vs `K=16` accept mining
4. strict accept vs slightly relaxed accept
5. bit specialist
6. text specialist
7. symbol specialist
8. format specialist
9. checkpoint soup
10. generalist + specialists merge

### 10-3. P2: 余力があれば

1. GRPO exact reward 小規模比較
2. dynamic sampler
3. merge 後の再蒸留
4. family-specific reward shaping

### 10-4. family 別の local target

v3 と同じ local target を継続しつつ、v4 では hard family 改善を強く見る。

- roman: `0.995〜1.000`
- unit: `0.99+`
- gravity: `0.985+`
- bit: `0.93〜0.96`
- text: `0.90〜0.94`
- symbol: `0.88〜0.93`

特に v4 では、

- bit の exact answer 安定化
- text の exact phrase 安定化
- symbol の format-safe exactness

を primary target とする。

## 11. 実装順序を固定する

### Step 1. v4 bootstrap と baseline scoring

完了条件:

- `versions/v4/` 構成ができる
- v1 / v2 / v3 artifact を読む bootstrap ができる
- Stage A trunk / Stage B trunk の baseline score が `local_scoreboard_v4.csv` に残る

### Step 2. preference pair builders

完了条件:

- `format_preference_pairs_v4.parquet`
- `correctness_preference_pairs_v4.parquet`
- `stage_c_preference_registry_v4.parquet`

が schema どおり生成される

### Step 3. RFT accept pool builder

完了条件:

- `rft_candidate_generations_v4.jsonl`
- `rft_accept_pool_v4.parquet`
- `rft_registry_v4.parquet`

が生成され、accept / reject reason が追える

### Step 4. Stage C mix / manifest builder

完了条件:

- `stage_c_rft_mix_v4.parquet`
- `stage_c_preference_mix_v4.parquet`
- Stage C training manifest 群

が生成される

### Step 5. Stage C runtime execute

完了条件:

- RFT または preference の少なくとも 1 系統が pilot 実行できる
- candidate manifest / result / metrics が揃う

### Step 6. candidate scoreboard と regret report

完了条件:

- `local_scoreboard_v4.csv`
- `family_regret_report_v4.csv`
- `candidate_registry_v4.csv`

が更新され、採用理由 / 却下理由が説明できる

### Step 7. specialist / merge / compression

完了条件:

- `specialist_candidate_registry_v4.csv`
- `merge_candidate_registry_v4.csv`

が生成され、少なくとも 1 本は merge candidate を serious gate で比較できる

### Step 8. CUDA / BF16 reproduction / packaging

完了条件:

- `cuda_reproduction_spec_v4.yaml`
- `cuda_reproduction_registry_v4.csv`
- `submission_manifest_v4.json`

が揃う

`submission_v4.zip` は good local score gate を通ったときにのみ作る。

### Step 9. submit queue / runbook / promotion

完了条件:

- `promotion_rules_v4.txt`
- `training_command_book_v4.txt`

が揃い、local score 改善がある candidate をすぐ submit queue に載せられる

## 12. v4 でやらないこと

範囲を守るため、次は v4 の primary deliverable から外す。

- true RL / GRPO を primary path にすること
- 良いローカルスコアなしでの blind submit
- MLX adapter の exact conversion を提出の主ルートにすること
- external broad reasoning corpus の大量投入
- v1 evaluator の再設計
- visible `test.csv` の validation 利用
- multi-file core implementation
- Stage B が弱いままなのに trunk を強制的に差し替えること

## 13. v4 のテストと検証

### 13-1. 必須 test

- preference pair schema integrity
- RFT accept / reject regression
- candidate scoreboard aggregation
- promotion gate regression
- merge spec / rank32 compression spec
- CUDA reproduction spec / packaging

### 13-2. 実行コマンド

```bash
uv run python -m py_compile versions/v4/code/train.py
uv run pytest -q versions/v4/tests
uv run pytest -q
```

### 13-3. CLI smoke

```bash
uv run python versions/v4/code/train.py bootstrap-v4

uv run python versions/v4/code/train.py build-format-preferences \
  --input versions/v3/data/preference/preference_pairs_v3.parquet \
  --output versions/v4/data/preference/format_preference_pairs_v4.parquet

uv run python versions/v4/code/train.py build-rft-candidates \
  --candidate-id v3-stage-a-best \
  --config versions/v4/conf/data/rft_accept_pool.yaml \
  --output versions/v4/data/rft/rft_candidate_generations_v4.jsonl

uv run python versions/v4/code/train.py filter-rft-accept-pool \
  --input versions/v4/data/rft/rft_candidate_generations_v4.jsonl \
  --output versions/v4/data/rft/rft_accept_pool_v4.parquet

uv run python versions/v4/code/train.py train-stage-c-rft \
  --config versions/v4/conf/train/rft_stage_c_mlx.yaml \
  --train-pack versions/v4/data/train_packs/stage_c_rft_mix_v4.parquet \
  --output-dir versions/v4/outputs/train/p0_rft_stage_c \
  --execute

uv run python versions/v4/code/train.py score-candidate \
  --candidate-id p0_rft_stage_c \
  --config versions/v4/conf/eval/candidate_score_serious.yaml \
  --output versions/v4/outputs/eval/p0_rft_stage_c_serious

uv run python versions/v4/code/train.py render-cuda-repro-spec \
  --candidate-id p0_rft_stage_c \
  --candidate-registry versions/v4/data/processed/candidate_feature_table_v4.parquet \
  --config versions/v4/conf/train/stage_c_cuda_bf16.yaml \
  --output versions/v4/outputs/handoff/p0_rft_stage_c_cuda.yaml
```

## 14. 最終的な v4 本命レシピ

現時点で v4 の最も堅い一本は次。

### Data

- v3 Stage A trunk を起点にする
- RFT accepted outputs を hard family 中心に追加する
- format preference pair を追加する
- correctness preference pair を hard family 中心に追加する
- replay を少量混ぜて generalist 能力を維持する

### Training

- Stage C1: RFT short finetune
- Stage C2: format DPO または ORPO の小規模 pass
- Stage C3: correctness preference は効果が見えたら追加
- specialist / merge は generalist Stage C が頭打ちになってから試す
- 最終候補は CUDA / BF16 + PEFT で再学習する

### Evaluation

- v1 `official_lb` 相当の quick / serious / weekly gate
- `shadow_256` / `hard_shadow_256`
- family metrics を必ず確認
- format fail / extraction fail を必ず確認
- packaging smoke pass 必須

### 判断

最終的に v4 は、**「Stage C / merge を試した版」ではなく、「ローカルで改善が証明された candidate だけを提出候補へ送れる版」** として完成させる。

そのため、最重要な成功条件は次の 5 点である。

- Stage A trunk を基準に local score が改善する
- bit / text / symbol の hard family が少なくとも 1 つは改善する
- format fail / extraction fail が悪化しない
- CUDA / BF16 reproduction lane が壊れない
- 改善がない candidate は無理に submit しない
