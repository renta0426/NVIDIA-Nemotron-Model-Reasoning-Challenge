v3-plam.md
Version: 0.1
Owner: me
Prerequisite: `versions/v0/v0-plan.md` 完了済み / `versions/v1/v1-plam.md` 完了済み / `versions/v2/v2-plam.md` 完了済み
Scope: `versions/plan-overview.md` のうち、v2 で固定したデータ・学習基盤を使って **実際に勝ち筋のある SFT 実験列と Mac-to-CUDA の再現ループ** を完成させる
Purpose: v2 の基盤版を、**real teacher trace / format-aware weighted SFT / Mac-to-CUDA handoff / candidate promotion** まで含む実戦版へ引き上げる

Historical plan note: this file preserves the original planning context, but the current authoritative competition contract is the top-level `README.md` Evaluation / Submitting section (`max_lora_rank = 32`, `max_tokens = 7680`, `top_p = 1.0`, `temperature = 0.0`, `max_num_seqs = 64`, `gpu_memory_utilization = 0.85`, `max_model_len = 8192`, final artifact `submission.zip`). If later sections in this historical plan mention older notebook/metric defaults, read them as historical notes rather than as the active contract.

## 0. この v3 の位置づけ

v0 で固定したのは、以後の全 version でぶらしてはいけない前提だった。

- Source of Truth の優先順位
- official evaluation 条件
- visible `test.csv` の扱い
- competition prompt の不変条件

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
- packaging gate と submit queue rule

ただし、v2 完了時点で分かったこともある。

- actual MLX LoRA の極小 pilot 自体は通った
- しかし tiny pilot では quick eval が改善しなかった
- format fail がまだ高い
- distilled trace は bootstrap render が中心で、real teacher trace に置き換わっていない
- weighted loss は方針として固定済みだが、実行経路が未完成
- MLX 学習成果物をそのまま最終提出アダプタに流す前提は置けない

したがって v3 は、**これ以上基盤を広げる版ではなく、v2 を使って本当に候補 adapter を作る最初の実戦版** とする。

この v3 の責務は、次の 8 点に限定する。

1. v2 の bootstrap distilled trace を、fixed MLX teacher の実出力へ置き換える
2. safe / unsafe format policy を学習 target と filtering policy の両方で固定する
3. final-span / final-line weighted loss を Mac 上で実行可能にする
4. Stage A / Stage B を meaningful な規模で回す
5. correction / format / preference-ready pool / RFT accept pool を実 row から作る
6. Mac で勝った recipe を Kaggle CUDA BF16 + PEFT run として再実装する
7. v1 evaluator で local best 更新または提出価値ありと判断した candidate を submit queue に載せる loop を固定する
8. v4 以降の DPO / RFT / merge に接続できる registry と runbook を残す

重要なのは、v3 が **「true RL を実装する版」でも「specialist merge を最適化する版」でもない** こと。

v3 は、`versions/plan-overview.md` で示された

- 2-11 curriculum
- 2-13 data ratio
- 3-1〜3-6 の強い SFT
- 4-1〜4-6 の format strategy
- 6-2 / 6-5 の Mac-to-CUDA 役割分担

を、最初に本気で実働させる版である。

## 1. v3 で絶対に継承する前提

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

teacher 生成や self-consistency では別 config を使ってよいが、採用判定は reopen しない。

### 1-2. visible `test.csv` は今後も validation に使わない

`README.md` と既存分析どおり、visible `test.csv` は sample-only であり `train.csv` と重複する。
v3 でも用途は次に限定する。

- submission zip の smoke
- packaging load の整合確認
- final formatter の最終確認

学習採用や split 評価には使わない。

### 1-3. v1 evaluator / extractor / verify は不変

v3 は出力 style や学習 recipe を強化するが、採点ロジックを勝手に変えてはならない。
以後の評価は v1 の metric-faithful 実装を使う。

特に固定するもの:

- boxed 優先 / fallback 付き extraction 順序
- `verify()` の exact / numeric tolerance
- `}` を含む answer に対する boxed risk の扱い
- competition prompt builder の形

### 1-4. 合成ラベルは solver / validator ベースでしか採用しない

`SYNTHETIC_DATA_AUGMENTATION_POLICY.md` を継承し、v3 でも次を必須にする。

- programmatic generator + exact solver
- または teacher proposal + independent validator

禁止:

- LLM が answer を直接決め、そのまま採用
- validator なし freeform synthetic を本学習へ投入
- real-only validation を悪化させても投入継続

### 1-5. リポジトリ規約として code は 1 ファイルに集約する

version ごとのコア実装は `versions/vN/code/` 配下の単一ファイルに置く。
したがって v3 でも code の中心は次で固定する。

- `versions/v3/code/train.py`

config / data / reports / tests は複数ファイルでよいが、主実装は 1 ファイルにまとめる。

### 1-6. 実行環境は Mac 固定だが、役割は探索用と明確に分ける

以後の daily experimentation loop は **macOS 上で完結できること** を前提にする。
固定 local model は次を継続利用する。

- `lmstudio-community/NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-6bit`

ローカル primary workload は次に固定する。

- MLX / Apple Silicon 上の teacher inference
- self-consistency sampling
- synthetic / distilled / correction / format / preference pool build
- weighted SFT の pilot / ablation
- v1 evaluator によるローカル比較
- candidate manifest / CUDA reproduction spec 出力

ただし、Mac 上の学習成果物は提出候補そのものではなく、勝ち筋の仮説検証用とみなす。
v3 では、Mac で昇格した recipe を Kaggle CUDA GPU (`A6000 Pro` 48GB / 96GB 級) 上で **BF16 + PEFT** により必ず再学習し、その CUDA artifact だけを提出候補として扱う。

RAM 512GB を前提に、v3 では次を遠慮なく使う。

- hard family の candidate sampling `N=8〜32`
- trace cache と registry のメモリ常駐
- family 別並列 generation / filtering
- nightly long eval

### 1-7. submission target schema は引き続き PEFT で、rank は 32 以下

`README.md` の提出条件を継承する。

- NVIDIA Nemotron-3-Nano-30B base model 向け LoRA
- rank は高々 `32`
- `adapter_config.json` を含む
- `submission.zip` に packaging する

v3 は **Mac で recipe を探索し、提出物は CUDA / BF16 再学習から PEFT 互換で出す**。

## 2. v3 の最終成果物

v3 完了時点で、少なくとも以下が揃っていることを完了条件とする。

### 2-1. 必須成果物

1. `teacher_trace_candidates_v3.jsonl`
2. `teacher_trace_registry_v3.parquet`
3. `distilled_traces_real_v3.parquet`
4. `format_pairs_strict_v3.parquet`
5. `correction_pairs_strict_v3.parquet`
6. `preference_pairs_v3.parquet`
7. `rft_accept_pool_v3.parquet`
8. `stage_a_strong_v3.parquet`
9. `stage_b_strong_v3.parquet`
10. `weighted_train_registry_v3.parquet`
11. `weighted_ablation_v3.csv`
12. `format_audit_v3.csv`
13. `candidate_registry_v3.csv`
14. `cuda_reproduction_spec_v3.yaml`
15. `cuda_reproduction_registry_v3.csv`
16. `submission_manifest_v3.json`
17. `submission.zip`
18. `training_command_book_v3.txt`
19. `promotion_rules_v3.txt`
20. v3 tests
21. `versions/v3/code/train.py`

### 2-2. v3 が提供すべき運用価値

v3 完了後は、以後の version が少なくとも次を再利用できる状態にする。

- real teacher trace に基づく distill pipeline
- safe / unsafe format policy の deterministic rendering
- executable weighted SFT
- Mac-discovered recipe を CUDA / BF16 PEFT run へ handoff する共通 schema
- correction / format / preference / RFT accept pool の共通 schema
- submit-worthy candidate promotion の台帳

## 3. 追加ディレクトリ構成

v3 は次の構成で作る。
ここでも **code は 1 ファイル**、その周辺の config / data / tests / reports を version 配下に持つ。

```text
versions/v3/
├── v3-plam.md
├── code/
│   └── train.py
├── conf/
│   ├── data/
│   │   ├── teacher_trace_real.yaml
│   │   ├── format_policy_v3.yaml
│   │   ├── preference_pairs.yaml
│   │   ├── rft_accept_pool.yaml
│   │   ├── mix_stage_a_strong.yaml
│   │   └── mix_stage_b_strong.yaml
│   ├── train/
│   │   ├── sft_stage_a_weighted_mlx.yaml
│   │   ├── sft_stage_a_weighted_alpha64_mlx.yaml
│   │   ├── sft_stage_b_weighted_mlx.yaml
│   │   ├── sft_stage_b_answer_bias_mlx.yaml
│   │   ├── sft_stage_a_cuda_bf16.yaml
│   │   └── sft_stage_b_cuda_bf16.yaml
│   ├── preference/
│   │   ├── dpo_format_pairs.yaml
│   │   └── dpo_correction_pairs.yaml
│   └── package/
│       └── cuda_submission_smoke.yaml
├── data/
│   ├── processed/
│   │   ├── teacher_trace_registry_v3.parquet
│   │   ├── weighted_train_registry_v3.parquet
│   │   ├── candidate_registry_v3.csv
│   │   └── cuda_reproduction_registry_v3.csv
│   ├── synth/
│   │   ├── distilled_traces_real_v3.parquet
│   │   ├── format_pairs_strict_v3.parquet
│   │   └── correction_pairs_strict_v3.parquet
│   ├── preference/
│   │   ├── preference_pairs_v3.parquet
│   │   └── rft_accept_pool_v3.parquet
│   └── train_packs/
│       ├── stage_a_strong_v3.parquet
│       └── stage_b_strong_v3.parquet
├── outputs/
│   ├── audits/
│   ├── datasets/
│   ├── handoff/
│   ├── models/
│   ├── runtime/
│   ├── train/
│   ├── eval/
│   ├── packaging/
│   └── reports/
└── tests/
    ├── test_teacher_trace_filter.py
    ├── test_format_policy_v3.py
    ├── test_weighted_runtime.py
    ├── test_preference_pair_builder.py
    ├── test_cuda_reproduction_packaging.py
    └── test_candidate_promotion.py
```

## 4. `versions/v3/code/train.py` の責務

### 4-1. コア責務

v3 の single-file core は、少なくとも次を担当する。

1. v2 artifact の読込と v3 schema への昇格
2. real teacher trace candidate 生成
3. trace filtering / selection / registry 記録
4. strict format / correction / preference / RFT pool builder
5. Stage A / Stage B strong mix builder
6. weighted SFT 実行
7. Mac candidate の CUDA / BF16 reproduction spec と handoff manifest 作成
8. CUDA artifact を前提にした packaging smoke / runbook / promotion rule 出力

### 4-2. 想定 subcommand

少なくとも以下を持つことを前提にする。

- `build-teacher-trace-candidates`
- `generate-teacher-traces`
- `filter-teacher-traces`
- `build-format-pairs`
- `build-correction-pairs`
- `build-preference-pairs`
- `build-rft-accept-pool`
- `build-train-mix`
- `train-sft`
- `run-ablation`
- `render-cuda-repro-spec`
- `package-peft`
- `write-runbook`
- `show-active-model`

重要なのは、v2 の `train-sft` を **manifest-only で終わらせず、weighted 実行まで含める** ことである。

## 5. format policy を v3 で実戦レベルに固定する

v2 の tiny pilot では format fail が高く、ここを放置したまま学習量だけ増やしても危険である。
したがって v3 では、format を副作用ではなく主対象にする。

### 5-1. safe / unsafe answer を明示的に分ける

safe answer:

- numeric
- 8bit binary
- Roman numeral
- 通常の text phrase
- `}` を含まない symbolic

unsafe answer:

- `}` を含む
- backslash が絡む
- boxed regex を壊しやすい
- 複数記号で boxed 崩壊リスクが高い

### 5-2. rendering 規則

safe answer は次で固定する。

- 最終行だけに `\boxed{ANSWER}`
- その直後に EOS
- 後続説明禁止
- 追加の数字禁止

unsafe answer は次で固定する。

- 最終行だけに `Final answer: ANSWER`
- その直後に EOS
- reasoning 中に boxed を出さない

### 5-3. family ごとの canonical answer 規則

bit:

- 8 chars only
- spaces なし
- prefix `0b` なし

gravity:

- numeric only
- commas なし
- unnecessary unit なし

unit:

- `2 decimal` exact
- commas なし
- unit suffix なし

roman:

- uppercase
- spaces なし

text:

- single spaces only
- 前後空白なし
- punctuation 追加なし

symbol:

- 原答え以外の空白なし
- dangerous chars のとき boxed 回避

### 5-4. extraction-aware teacher filtering

teacher 生成は correct でも、そのまま採用しない。
採用条件は次を全部満たすこと。

- `extract_final_answer(output) == gold`
- raw output 内に余計な boxed がない
- trailing numbers がない
- unsafe answer で malformed boxed がない
- final answer が最後の行だけにある

この条件を通ったものだけ蒸留・preference・RFT の材料に使う。

## 6. bootstrap distill を real teacher trace へ置き換える

### 6-1. teacher は fixed MLX model を使う

v3 の primary teacher は次で固定する。

- `lmstudio-community/NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-6bit`

v2 で確認した active model manifest をそのまま再利用し、teacher identity を registry に必ず残す。

### 6-2. target style は 4 系統を継承する

v3 でも target style は次で固定する。

- `long`
- `short`
- `answer_only`
- `format_safe`

ただし本命は v2 同様 `short` と `format_safe` であり、`long` は薄く保つ。

### 6-3. teacher 生成数

初回 full pass では v2 の上限を継承しつつ、hard family だけ厚くする。

- long: 1〜2
- short: 1〜2
- answer-only: 1〜2
- format-safe: 1

`bit`, `text`, `symbol` の hard row だけは別枠で次を許可する。

- self-consistency buffer: `N=8〜32`
- raw candidate cache は一時的に保存してよい
- registry には selection 用要約と accepted trace を残す

### 6-4. `teacher_trace_registry_v3.parquet` の必須列

- `trace_id`
- `source_id`
- `source_kind`
- `family`
- `answer_type`
- `target_style`
- `teacher_name`
- `teacher_seed`
- `sampling_profile`
- `raw_output`
- `extracted_answer`
- `is_correct`
- `format_bucket`
- `format_pass`
- `boxed_policy`
- `trace_len_chars`
- `trace_len_tokens_est`
- `consensus_rate`
- `selected_for_training`
- `selected_for_preference`
- `selected_for_rft`
- `selection_reason`

### 6-5. distill row の選定方針

distill に入れるのは、次のいずれかに限る。

- shortest correct
- cleanest correct
- format-safe correct
- family 難所で consensus が高い short trace

逆に入れないもの:

- correct だが trailing number がある
- correct だが multiple boxed がある
- correct だが unsafe answer を boxed に入れている
- unnecessarily long で final answer が汚い

## 7. correction / format / preference / RFT pool を固定する

### 7-1. correction pair

`correction_pairs_strict_v3.parquet` は current student の誤答を材料に作る。
v2 より strict にし、chosen 側は extraction-aware pass を必須にする。

必須列:

- `pair_id`
- `prompt`
- `family`
- `rejected_output`
- `chosen_output`
- `chosen_extracted_answer`
- `rejected_extracted_answer`
- `error_family_tag`
- `error_subtype`
- `source_eval_run`

### 7-2. format pair

`format_pairs_strict_v3.parquet` は **同じ answer で bad format vs good format** を持つ。

chosen:

- clean boxed
- clean `Final answer: ...`

rejected:

- multiple boxed
- trailing numbers
- malformed boxed
- unsafe answer を boxed に入れたもの
- final answer の後に説明を続けたもの

### 7-3. preference pair

`preference_pairs_v3.parquet` は v4 の DPO / ORPO / RFT に直結する共通 pair schema とする。
pair kind は最低でも次を持つ。

- `format`
- `correction`
- `brevity`
- `consensus`

必須列:

- `pair_id`
- `source_id`
- `family`
- `pair_kind`
- `prompt`
- `chosen_output`
- `rejected_output`
- `chosen_is_correct`
- `rejected_is_correct`
- `chosen_format_bucket`
- `rejected_format_bucket`
- `preference_reason`

### 7-4. RFT accept pool

`rft_accept_pool_v3.parquet` は true RL ではなく **rejection-sampling fine-tuning 用** の accepted output pool とする。

採用条件:

- correct
- extraction-safe
- concise
- final answer が最後の行だけ

これは v3 で builder まで作り、実際の本格 RFT は v4 以降でもよい。

## 8. Stage A / Stage B の strong mix を固定する

v2 は基盤版だったが、v3 では実際に強い配合を回す。

### 8-1. Stage A: Generalist strong SFT

最初の安全側配合は次で固定する。

- real: 50%
- sibling synth: 25%
- distilled correct traces: 15%
- hard synth: 5%
- format sharpening: 5%

target style 比率はまず次を本命にする。

- long: 20
- short: 45
- answer-only: 20
- format-safe: 15

### 8-2. Stage B: Hardening strong SFT

Stage B は Phase 3 に対応する hardening とする。

- real: 35%
- sibling synth: 20%
- distilled correct traces: 10%
- hard synth: 15%
- correction: 10%
- format sharpening: 10%

### 8-3. family over-sampling 初期値

plan-overview の初期案を継承する。

- bit: `1.3x`
- gravity: `0.9x`
- unit: `0.8x`
- text: `1.4x`
- roman: `0.6x`
- symbol: `1.6x`

Phase A は static、Phase B は必要なら dynamic hard-mining を入れてよい。

### 8-4. `weighted_train_registry_v3.parquet` の必須列

- `row_id`
- `source_id`
- `mix_name`
- `family`
- `target_style`
- `format_policy`
- `is_weighted`
- `final_span_start_char`
- `final_span_end_char`
- `final_line_start_char`
- `final_line_end_char`
- `weight_profile_name`
- `rationale_weight`
- `final_line_weight`
- `final_span_weight`
- `selected_for_stage`

## 9. weighted SFT を v3 で実行可能にする

`versions/plan-overview.md` の 3-4 / 3-5 は、v3 の中心課題である。
v2 では manifest を出せても、weighted runtime execute は未完だった。
v3 はここを必ず埋める。

### 9-1. 基本方針

- completion-only loss
- prompt tokens には loss をかけない
- assistant 出力のみを対象にする

token weight の初期値は次で固定する。

- rationale tokens: `1.0`
- `Final answer` prefix: `2.0`
- final line: `3.0`
- final span default: `4.0`

family 別 final span weight は次を本命にする。

- symbol: `6.0`
- bit: `5.0`
- unit / gravity / roman: `4.0`
- text: `3.0`

### 9-2. 実装原則

1. weighted が有効な config で `--execute` したら、本当に weighted runtime が走ること
2. manifest-only fallback で終わらせないこと
3. final span が一意に取れない row は reject すること
4. boxed / final-answer line のどちらでも span detection が壊れないこと

MLX 既存 CLI で token-level weight を渡せないなら、v3 では `train.py` 側で custom execution path を持つ。

### 9-3. 最初に切る LoRA 比較

plan-overview の比較を継承する。

- A: `r32 alpha32 dropout0.0`
- B: `r32 alpha64 dropout0.0`
- C: `r32 alpha32 dropout0.05`
- D: `r16 alpha32 dropout0.05`

優先度は A / B / C を先、D は圧縮比較用に留める。

### 9-4. sequence length / packing / lr

初期設定:

- `max_seq_len = 1024`
- `1536` は long trace を厚く入れる時だけ
- packing は基本 on
- ただし final span weighting と相性確認を必須にする

学習率と段数:

Stage A

- `lr = 1e-4` or `8e-5`
- warmup `3%`
- epochs `1.5〜3`

Stage B

- `lr = 5e-5`
- epochs `0.5〜1.5`

Stage C 相当の pair / RFT は v3 では data まで、長い本体実験は後続に回してよい。

## 10. Mac の勝ち筋を CUDA / BF16 submission へ橋渡しする

plan-overview の 6-2 / 6-5 を、v3 で必ず実働させる。
Mac 学習成果物そのものは提出せず、そこから得た recipe を CUDA / BF16 で再現したものだけを提出する。

### 10-1. handoff の必須確認

- `cuda_reproduction_spec_v3.yaml` が生成できる
- base model / train mix / row counts / hashes / LoRA config / weighting config / style ratio が固定される
- Kaggle CUDA / BF16 用の実行コマンドが出力される
- CUDA artifact から `adapter_config.json` / `adapter_model.safetensors` が生成される
- `PeftModel.from_pretrained()` smoke が通る
- visible `test.csv` smoke と vLLM smoke が CUDA artifact で通る

### 10-2. `candidate_registry_v3.csv` の必須列

- `candidate_id`
- `parent_candidate_id`
- `runtime_lane`
- `mac_candidate_id`
- `cuda_run_id`
- `stage`
- `mix_name`
- `train_config`
- `rank`
- `alpha`
- `dropout`
- `weighted_loss`
- `overall_acc`
- `hard_shadow_acc`
- `format_fail_rate`
- `boxed_rate`
- `cuda_repro_pass`
- `packaging_pass`
- `selected_for_submit`
- `notes`

### 10-3. packaging outputs

最低限、次を生成すること。

- `cuda_reproduction_spec_v3.yaml`
- `cuda_reproduction_registry_v3.csv`
- `submission_manifest_v3.json`
- `submission.zip`

visible `test.csv` はここで only smoke に使う。
`submission.zip` は必ず CUDA artifact から作る。

## 11. v3 で最初に回すべき実験列を固定する

### 11-1. P0: 本命 SFT 実験列

1. real-only serious baseline `r32 alpha32 dropout0.0`
2. 1 + weighted final-span loss
3. 2 + core sibling synth
4. 3 + real teacher distilled short traces
5. 4 + hard synth 少量
6. 5 + format sharpening
7. 6 + correction chosen outputs
8. 7 + Stage B hardening
9. 8 の top 1〜2 recipe を Kaggle CUDA / BF16 + PEFT で再学習
10. 9 の `shadow_256` / `hard_shadow_256` submit-worthiness check
11. 10 の通過 candidate を `submission.zip` 化して leaderboard に送る

### 11-2. P1: 比較軸

1. `alpha32` vs `alpha64`
2. `dropout0.0` vs `0.05`
3. weighted loss on / off
4. `20/45/20/15` vs `30/40/20/10` vs `0/60/25/15`
5. safe / unsafe format policy 強化 on / off
6. family over-sampling static vs hard-mining

### 11-3. P2: v4 へつなぐ metadata だけ先に整える

- DPO on format pairs
- DPO on correction pairs
- RFT from accepted trace pool
- checkpoint averaging / soup
- specialist merge

P2 は v3 の primary deliverable ではない。
builder / manifest / registry まで準備できれば十分。

### 11-4. family 別の local target

plan-overview の目安を、v3 では local target として採用する。

- roman: `0.995〜1.000`
- unit: `0.99+`
- gravity: `0.985+`
- bit: `0.93〜0.96`
- text: `0.90〜0.94`
- symbol: `0.88〜0.93`

これは public leaderboard の保証ではなく、family collapse を避けるための運用 target である。

## 12. 実装順序を固定する

### Step 1. v3 bootstrap と format audit

完了条件:

- `versions/v3/` 構成ができる
- v2 artifact を読む bootstrap ができる
- `format_policy_v3.yaml` が固定される
- tiny pilot の format 失敗要因が audit 化される

### Step 2. real teacher trace builder

完了条件:

- candidate generation が動く
- filtering と registry 化が動く
- `distilled_traces_real_v3.parquet` が出る

### Step 3. strict pair / pool builders

完了条件:

- `format_pairs_strict_v3.parquet`
- `correction_pairs_strict_v3.parquet`
- `preference_pairs_v3.parquet`
- `rft_accept_pool_v3.parquet`

が schema どおり生成される

### Step 4. Stage A / Stage B strong mix builder

完了条件:

- `stage_a_strong_v3.parquet`
- `stage_b_strong_v3.parquet`
- `weighted_train_registry_v3.parquet`

が生成される

### Step 5. weighted runtime execute

完了条件:

- weighted config で `train-sft --execute` が実際に走る
- final span / final line weighting が row-level に追跡できる

### Step 6. scaled P0 baseline runs

完了条件:

- P0-1〜P0-4 の少なくとも基礎列が走る
- `weighted_ablation_v3.csv` が出る

### Step 7. Stage B hardening / format sharpening

完了条件:

- P0-5〜P0-8 が走る
- format fail 改善が確認できる

### Step 8. CUDA / BF16 reproduction / packaging

完了条件:

- `cuda_reproduction_spec_v3.yaml` が固定される
- top 1 Mac candidate が Kaggle CUDA / BF16 で再学習される
- `submission.zip` が CUDA artifact から出る
- PEFT load smoke と visible `test.csv` smoke が通る

### Step 9. submit queue / runbook / promotion

完了条件:

- `candidate_registry_v3.csv`
- `promotion_rules_v3.txt`
- `training_command_book_v3.txt`

が揃い、local best 更新または提出価値ありの candidate をすぐ submit queue に載せられる

## 13. v3 でやらないこと

範囲を守るため、次は v3 の primary deliverable から外す。

- true RL / GRPO 本体
- specialist adapter merge の最適化本体
- external broad reasoning corpus の大量投入
- v1 evaluator の再設計
- visible `test.csv` の validation 利用
- unsupported family に対する guess-based synthetic
- MLX adapter の exact conversion を提出の主ルートにすること
- multi-file core implementation

## 14. v3 のテストと検証

### 14-1. 必須 test

- real teacher trace filtering regression
- safe / unsafe format policy regression
- weighted final-span detection
- weighted runtime execute smoke
- preference / RFT pool schema integrity
- CUDA reproduction spec / packaging
- packaging spec
- candidate registry integrity

### 14-2. 実行コマンド

```bash
uv run python -m py_compile versions/v3/code/train.py
uv run pytest -q versions/v3/tests
uv run pytest -q
```

### 14-3. CLI smoke

```bash
uv run python versions/v3/code/train.py build-teacher-trace-candidates \
  --config versions/v3/conf/data/teacher_trace_real.yaml \
  --input versions/v2/data/processed/train_real_canonical_v2.parquet \
  --output versions/v3/outputs/datasets/teacher_trace_candidates_v3.jsonl

uv run python versions/v3/code/train.py build-train-mix \
  --config versions/v3/conf/data/mix_stage_a_strong.yaml \
  --real versions/v2/data/processed/train_real_canonical_v2.parquet \
  --core versions/v2/data/synth/synth_core_v2.parquet \
  --distill versions/v3/data/synth/distilled_traces_real_v3.parquet \
  --format versions/v3/data/synth/format_pairs_strict_v3.parquet \
  --output versions/v3/data/train_packs/stage_a_strong_v3.parquet

uv run python versions/v3/code/train.py train-sft \
  --config versions/v3/conf/train/sft_stage_a_weighted_mlx.yaml \
  --train-pack versions/v3/data/train_packs/stage_a_strong_v3.parquet \
  --output-dir versions/v3/outputs/train/p0_stage_a_weighted \
  --execute

uv run python versions/v3/code/train.py render-cuda-repro-spec \
  --candidate-id p0_stage_a_weighted_best \
  --candidate-registry versions/v3/data/processed/candidate_registry_v3.csv \
  --config versions/v3/conf/train/sft_stage_a_cuda_bf16.yaml \
  --output versions/v3/outputs/handoff/p0_stage_a_weighted_cuda.yaml

uv run python versions/v3/code/train.py package-peft \
  --adapter-dir /kaggle/working/p0_stage_a_weighted_cuda/adapter \
  --config versions/v3/conf/package/cuda_submission_smoke.yaml \
  --output-dir versions/v3/outputs/packaging/p0_stage_a_weighted_cuda
```

## 15. 最終的な v3 本命レシピ

現時点で v3 の最も堅い一本は次。

### Data

- real canonical
- core sibling synth
- real teacher distilled short traces
- hard synth 少量
- format sharpening
- correction chosen outputs は Stage B にのみ入れる

### Training

- Mac-first local experimentation, then CUDA / BF16 reproduction
- all-linear
- `r = 32`
- `alpha = 32`
- `dropout = 0.0`
- Stage A generalist SFT
- Stage B hardening SFT
- weighted final-span / final-line loss
- target style 比率 `20 / 45 / 20 / 15`
- `max_seq_len = 1024`

### Format

- safe answer は final-line boxed
- unsafe answer は final-line `Final answer: ...`
- final answer の後は即 EOS
- multiple boxed 禁止

### Packaging

- Mac で勝った recipe を CUDA / BF16 + PEFT で再学習
- `adapter_config.json` を精査
- `submission.zip` を smoke

### Evaluation

- v1 `official_lb` / `shadow_256` / `hard_shadow_256`
- family metrics を必ず確認
- format fail / boxed rate も確認
- packaging smoke pass 必須

### 判断

最終的に v3 は、**「基盤を作る版」ではなく、「Mac の勝ち筋を CUDA submit queue へ継続的に流せる版」** として完成させる。

そのため、最重要な成功条件は次の 5 点である。

- distilled trace が real teacher output である
- weighted SFT が本当に実行できる
- format fail が v2 pilot より改善する
- CUDA / BF16 reproduction lane が壊れない
- v1 evaluator で local best 更新または提出価値ありを判断できる
