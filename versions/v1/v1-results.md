# V1 Results

## Source of truth

この `v1` 系列のローカル判定も **`README.md` の Evaluation 節**を唯一の基準にする。

- `max_lora_rank = 32`
- `max_tokens = 7680`
- `top_p = 1.0`
- `temperature = 0.0`
- `max_num_seqs = 64`
- `max_model_len = 8192`

metric は **`\boxed{}` 優先抽出 → heuristic fallback → last numeric fallback** を使う。

## Reproduced prompt-router-v6 bundle

- single-file main: `mac_workspace/v1/phase2_binary_dsl_mlx_v1.py`
- local reference bundle: `mac_workspace/v1/reference/`
  - `baseline/cot/phase2_binary_dsl/artifacts/phase2_binary_hybrid_training_data.csv`
  - `baseline/nemotron-sft-lora-with-cot-v2/artifacts/train_split_with_cot.csv`
  - `baseline/cot/phase0_offline_eval/artifacts/*`
  - `baseline/cot/phase2_1_2_merge_lora/artifacts/phase2_1_2_binary_specialist_training_data.csv`
  - `baseline/cot/phase2_2_merge_lora/artifacts/phase2_2_symbol_specialist_training_data.csv`
  - `cuda-train-data-analysis-v1/artifacts/` の prompt-local / symbol solver / benchmark build に必要な CSV 群
- reproduced eval outputs: `mac_workspace/v1/outputs/eval_prompt_router_v6_repro/`

## Submission compatibility

> 重要: `prompt-router-v6-repro` は **single-file multi-adapter local pipeline** の再現であり、README の Submitting 節が要求する **「1 つの rank<=32 LoRA adapter を `submission.zip` に入れて提出する形」** をそのまま満たすものではない。  
> `v1` で再現したのは **local best pipeline** であって、**submission-compatible single adapter** ではない。

## Current best local pipeline

| pipeline | local320 | gate24 | binary | gravity | roman | symbol | text | unit | note |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `prompt-router-v6-repro` | **293/320 = 0.9156** | **24/24 = 1.0000** | `54/60` | `50/50` | `50/50` | `39/60` | `50/50` | `50/50` | `v1` single-file + local reference bundle から actual rerun で `v0` score を再現 |

補足:

- `v1` rerun は `v0` の 3 adapter を入力として使い、**`v0` actual と完全一致**した。
  - general: `mac_workspace/v0/outputs/phase2_binary_hybrid_mlx_v0_resume_v10_to_full_fusion_v40_lr1p25e6_ep0125/adapter`
  - reasoning: `mac_workspace/v0/outputs/phase2_binary_hybrid_mlx_v0_text_run3_lr2e5_top8_bs16ga1/adapter`
  - specialist: `mac_workspace/v0/outputs/phase2_binary_hybrid_mlx_v0_focus_v1_text_full_bs16ga1/adapter`
- full320 fallback は **47 行すべて solver**
  - `binary_formula_consensus_solver = 35`
  - `symbol_numeric_zero_error_solver = 12`
- binary は **`54/60`**、内訳は `bit_other = 40/46`, `bit_structured_byte_formula = 14/14`
- symbol は `numeric_2x2 = 39/40`, `glyph_len5 = 0/20`
- artifact source of truth:
  - `mac_workspace/v1/outputs/eval_prompt_router_v6_repro/gate24/phase0_offline_eval/artifacts/phase0_eval_summary.json`
  - `mac_workspace/v1/outputs/eval_prompt_router_v6_repro/full320_shard2/phase0_offline_eval/artifacts/phase0_eval_summary.json`

## Submission-compatible single-adapter track

README の提出要件を満たす本命は、**single adapter 1 本**で local score を上げること。  
`v1` ではまず、`v0` の `v110` general-support mix を土台にしつつ、`prompt-router-v6` の gain 源に近い **`bit_other` prompt-local consensus** を teacher row として追加する枝から再開した。

重要な切り分け:

- `binary_prompt_local_current_consensus_candidates_v1.csv` の **`bit_other + answer_only_keep` 52 行は、すべて現行 900-row phase2 train CSV と重複**していた
- したがって今回の新規 signal は **`bit_other + manual_audit_priority`** が中心
- first batch は `v110` adapter からの top8 continuation (`lr=1.25e-6`, `epoch=0.25`, `dataset_format=text`) で揃える

### v119-v122 prepare batch

| version | design | prepare result | status |
| --- | --- | --- | --- |
| `v119` | `v110 + bit_other prompt-local manual` conservative | `2114 rows`, `33 iters`, augmentation `8` (`boxed_only_done 8`) | gate24 実測済み |
| `v120` | `v110 + bit_other prompt-local manual` broad | `2118 rows`, `33 iters`, augmentation `12` (`boxed_only_done 12`) | gate24 実測済み |
| `v121` | `v110 + bit_other prompt-local manual` + same-row boxed twin | `2122 rows`, `33 iters`, augmentation `16` (`boxed_only_done 8 + boxed_only 8`) | prepare only |
| `v122` | `v110 + bit_other prompt-local manual` + hybrid-consensus verified | `2122 rows`, `33 iters`, augmentation `16` (`manual boxed_only_done 8 + hybrid boxed_only 8`) | prepare only |

artifact source of truth:

- `mac_workspace/v1/outputs/phase2_binary_hybrid_mlx_v1_resume_v110_to_top8_fusion_v119_lr1p25e6_ep025/prepare_manifest.json`
- `mac_workspace/v1/outputs/phase2_binary_hybrid_mlx_v1_resume_v110_to_top8_fusion_v120_lr1p25e6_ep025/prepare_manifest.json`
- `mac_workspace/v1/outputs/phase2_binary_hybrid_mlx_v1_resume_v110_to_top8_fusion_v121_lr1p25e6_ep025/prepare_manifest.json`
- `mac_workspace/v1/outputs/phase2_binary_hybrid_mlx_v1_resume_v110_to_top8_fusion_v122_lr1p25e6_ep025/prepare_manifest.json`

### v119-v122 gate24 follow-up

`v119` / `v120` を `v110` adapter から top8 continuation で学習し、OOM 回避のため **single-shard gate24** で先に評価した。  
結果は **どちらも `v110` の `21/24` を下回り、この枝は branch closure**。

| version | train | gate24 | family breakdown | decision |
| --- | --- | ---: | --- | --- |
| `v119` | `final val 0.311 -> 0.312` | `16/24` | `binary 0/4`, `gravity 4/4`, `roman 4/4`, `symbol 0/4`, `text 4/4`, `unit 4/4` | 不採用 |
| `v120` | `final val 0.311 -> 0.310` | `17/24` | `binary 1/4`, `gravity 4/4`, `roman 4/4`, `symbol 2/4`, `text 2/4`, `unit 4/4` | 不採用 |
| `v121` | prepare only | OOM 対応で train 停止 | twin 追加枝 | 打ち切り |
| `v122` | prepare only | OOM 対応で train 停止 | hybrid 混合枝 | 打ち切り |

観察:

- `bit_other` manual を足すと **binary hard prompt の boxed formatting が崩れた**。
  - `v119` binary metrics: `boxed_extraction_success_rate 0.0`, `format_failure_rate 1.0`
  - `v120` binary metrics: `boxed_extraction_success_rate 0.5`, `format_failure_rate 0.75`
- `v120` は `v119` より広い manual quota で **symbol 2/4** までは戻したが、`binary 1/4` / `text 2/4` に留まり、`v110` 改善には繋がらなかった。
- row-level では `your answer` placeholder と `last_number` fallback が再発しており、**current prompt-local manual teacher は single-adapter continuation だと出力形式安定性を壊す**。

artifact source of truth:

- `mac_workspace/v1/outputs/phase2_binary_hybrid_mlx_v1_resume_v110_to_top8_fusion_v119_lr1p25e6_ep025/training_result.json`
- `mac_workspace/v1/outputs/phase2_binary_hybrid_mlx_v1_resume_v110_to_top8_fusion_v119_lr1p25e6_ep025/phase0_offline_eval/artifacts/phase0_eval_summary.json`
- `mac_workspace/v1/outputs/phase2_binary_hybrid_mlx_v1_resume_v110_to_top8_fusion_v120_lr1p25e6_ep025/training_result.json`
- `mac_workspace/v1/outputs/phase2_binary_hybrid_mlx_v1_resume_v110_to_top8_fusion_v120_lr1p25e6_ep025/phase0_offline_eval/artifacts/phase0_eval_summary.json`

### v123-v124 verified-only follow-up

manual prompt-local branch が formatting を壊したため、次は **verified-only strong-sample** を `v110` continuation に narrow append する safer branch を切った。

| version | design | prepare result | train | gate24 | follow-up |
| --- | --- | --- | --- | ---: | --- |
| `v123` | `v110 + bit_other verified 24 + numeric_2x2 verified 8` | `2138 rows`, `33 iters`, augmentation `32` | `final val 0.311 -> 0.309` | `16/24` | branch closure |
| `v124` | `v110 + bit_other verified 48 + numeric_2x2 verified 16` | `2170 rows`, `33 iters`, augmentation `64` | `final val 0.311 -> 0.309` | `21/24` | slice triage 実施 → full320 昇格 |

`v124` は gate24 では **`v110` と同点 `21/24`** だったが、中身は単純な tie ではなかった。

- gain: `c625ba91` (`bit_other`) を `your answer` から **`11111111`** に回収
- loss: `0fdc689e` (`unit_fixed_ratio`) を **`29.56 -> 795`** の numeric fallback に悪化
- 未回収: `12e947ca` (`bit_other`), `db6a5663` (`numeric_2x2`)

そのため full320 の前に README 条件の slice を切った。

| version | slice | result | comparison vs `v110` | note |
| --- | --- | ---: | --- | --- |
| `v124` | `unit50` | `44/50 = 0.88` | `v110 unit = 42/50` より **+2** | gate24 の unit 1-loss は全体では regress ではなかった |
| `v124` | `binary60` | `4/60 = 0.0667` | `v110 binary60 = 3/60` より **+1** | `bit_other 4/46`, `bit_structured_byte_formula 0/14`, `format_failure_rate 0.9333` |

判断:

- `v123` は `16/24` で dead branch
- `v124` は **binary +1 / unit +2** と `v110` を上回る slice signal が見えたため、**separate eval root で README actual full320** へ進める

運用メモ:

- `mac_workspace/v1/phase2_binary_dsl_mlx_v1.py eval-phase0` は、`--adapter-path` 指定時に **既定では adapter run dir の `phase0_offline_eval` を上書き**する
- slice / full320 を並行管理するには **`--eval-output-root` を明示**する必要がある

### v124 full320 actual

`v124` を separate root (`eval_single_adapter_v124_full320_shard2`) で README 条件 actual full320 に流した。

| version | local320 | binary | gravity | roman | symbol | text | unit | note |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `v124` | `194/320 = 0.6062` | `5/60` | `49/50` | `47/50` | `13/60` | `35/50` | `45/50` | `v110` slice-equivalent `192/320` より **+2**、ただし `v40 = 205/320` には未達 |

`v110` 比の family delta:

- `binary +2` (`3 -> 5`)
- `gravity +1` (`48 -> 49`)
- `roman ±0` (`47 -> 47`)
- `symbol +2` (`11 -> 13`)
- `text -6` (`41 -> 35`)
- `unit +3` (`42 -> 45`)

結論:

- `v124` は **`v110` からは改善**した
- ただし single-adapter の best known `v40 = 205/320` を **11 点下回る**
- したがってこのまま mainline にはせず、ユーザー懸念どおり **`0.25 epoch` undertraining 仮説**を潰すため、次は同 profile / 同条件で **epoch 比較 (`0.25 / 0.5 / 1.0 / 2.0`)** を 1 回だけ実施して、以後の実験で使う epoch を決める

artifact source of truth:

- `mac_workspace/v1/outputs/eval_single_adapter_v124_full320_shard2/phase0_offline_eval/artifacts/phase0_eval_summary.json`
