# baseline_mlx Results

## Source of truth

この系列の判定基準は **`README.md` の Evaluation / Submitting 節**に固定する。

- `max_lora_rank = 32`
- `max_tokens = 7680`
- `top_p = 1.0`
- `temperature = 0.0`
- `max_num_seqs = 64`
- `max_model_len = 8192`

補足:

- baseline notebook は `baseline/nemotron-sft-lora-with-cot-v2/artifacts/train_split_with_cot.csv` を使い、type ごとに `300 / 400 / 700 / 700 / 607 / 200` を sampling している。
- `baseline_mlx` の再現は上記 sampling と CoT 整形を維持しつつ、MLX 用に `shadow_model` と `enable_thinking` patch を入れている。
- 生成される `mlx_adapter_bundle.zip` は **ローカル MLX 再利用用**であり、現時点では **PEFT/vLLM 提出互換を主張しない**。

## HF notebook reference

| pipeline | local320 | binary | gravity | roman | symbol | text | unit | source |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `baseline/nemotron-sft-lora-with-cot-v2` | `249/320 = 0.7781` | `29/60` | `50/50` | `50/50` | `22/60` | `49/50` | `49/50` | `baseline/nemotron-sft-lora-with-cot-v2/result/artifacts/phase0_eval_summary.json` |

## MLX reproduction runs

| version | run_name | scope | sampled_rows | train_rows | valid_rows | total_iters | max_seq | measured | status | artifacts |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| `baseline-mlx-smoke-v1` | `nemotron_sft_lora_with_cot_v2_mlx_smoke_v1` | smoke | `24` | `24` | `4` | `1` | `1024` | `val_loss=0.607`, `train_loss=0.565`, `peak_mem=64.835 GB` | adapter 生成まで完走 | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_smoke_v1/training_result.json` |
| `baseline-mlx-full-v1` | `nemotron_sft_lora_with_cot_v2_mlx_v1` | full notebook-equivalent | `2907` | `2907` | `32` | `5814` | `4096` | `iter1 val_loss=0.683`; `iter5600 val_loss=0.186`; `iter5800 val_loss=0.180`; `iter5814 val_loss=0.181`; `iter5814 train_loss=0.272`; `peak_mem=68.581 GB` | 完走 | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_v1/training_result.json` |
| `baseline-mlx-lora-fix-smoke-v1` | `nemotron_sft_lora_with_cot_v2_mlx_lora_fix_smoke_v1` | smoke (LoRA target fix) | `24` | `24` | `4` | `1` | `1024` | `val_loss=0.607`, `train_loss=0.565`, `peak_mem=71.683 GB`, `trainable=880.138M`, `adapter=3.52 GB` | adapter 生成まで完走 | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_lora_fix_smoke_v1/training_result.json` |
| `baseline-mlx-lora-fix-full-v2` | `nemotron_sft_lora_with_cot_v2_mlx_lora_fix_v2` | full notebook-equivalent (parity-fix rerun) | `2907` | `2907` | `32` | `5814` | `4096` | `iter1 val_loss=0.683`; `iter400 val_loss=4.807`; `iter600 val_loss=1.359`; `iter800 val_loss=0.847`; `iter5814 val_loss=0.213`; `iter5814 train_loss=0.327`; `peak_mem=82.603 GB` | adapter 生成まで完走 | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_lora_fix_v2/training_result.json` |
| `baseline-mlx-lora-fix-schedopt-v1` | `nemotron_sft_lora_with_cot_v2_mlx_lora_fix_schedopt_v1` | full notebook-equivalent (expanded LoRA rerun, optimizer-step schedule) | `2907` | `2907` | `32` | `5814` | `4096` | `iter1 val_loss=0.683`; `iter5200 val_loss=0.186`; `iter5400 val_loss=0.182`; `iter5600 val_loss=0.180`; `iter5800 val_loss=0.180`; `iter5814 val_loss=0.180`; `iter5814 train_loss=0.298`; `peak_mem=82.603 GB` | adapter 生成まで完走 | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_lora_fix_schedopt_v1/training_result.json` |
| `baseline-mlx-narrow-schedopt-v1` | `nemotron_sft_lora_with_cot_v2_mlx_narrow_schedopt_v1` | full notebook-equivalent (narrow LoRA, optimizer-step schedule) | `2907` | `2907` | `32` | `5814` | `4096` | `iter1 val_loss=0.683`; `iter2000 val_loss=0.248`; `iter3000 val_loss=0.200`; `iter3400 val_loss=0.188`; `iter3600 val_loss=0.185`; `iter3800 val_loss=0.183`; `iter4000 val_loss=0.177`; stalled after `iter4060`; `peak_mem=68.122 GB` | stalled in MLX eval wait; no adapter checkpoint because `save_every=5814` | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_narrow_schedopt_v1/mlx_lora_config.yaml` |
| `baseline-mlx-narrow-schedopt-v2` | `nemotron_sft_lora_with_cot_v2_mlx_narrow_schedopt_v2` | full notebook-equivalent (narrow LoRA, optimizer-step schedule, reduced eval cadence) | `2907` | `2907` | `32` | `5814` | `4096` | `steps_per_eval=5814`; `save_every=200`; OOM during restart before first train report | interrupted by OOM before adapter or training_result creation | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_narrow_schedopt_v2/mlx_lora_config.yaml` |
| `baseline-mlx-narrow-schedopt-v3` | `nemotron_sft_lora_with_cot_v2_mlx_narrow_schedopt_v3` | full notebook-equivalent (narrow LoRA, optimizer-step schedule, reduced eval cadence; interactive rerun) | `2907` | `2907` | `32` | `5814` | `4096` | no persisted train log; adapter dir only contains `adapter_config.json` | interactive rerun was manually stopped during abnormal slowdown before the first checkpoint | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_narrow_schedopt_v3/mlx_lora_config.yaml` |
| `baseline-mlx-narrow-schedopt-v4` | `nemotron_sft_lora_with_cot_v2_mlx_narrow_schedopt_v4` | full notebook-equivalent (narrow LoRA, optimizer-step schedule, reduced eval cadence; file-logged rerun) | `2907` | `2907` | `32` | `5814` | `4096` | `iter1 val_loss=0.683`; `iter1 val_took=329.883s`; no `iter10` report; `resource_tracker` warned about 1 leaked semaphore | file logging did not fix the slowdown; process stayed low-utilization after `iter1` and was killed with no adapter checkpoint | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_narrow_schedopt_v4/train.log` |
| `baseline-mlx-narrow-schedopt-v5` | `nemotron_sft_lora_with_cot_v2_mlx_narrow_schedopt_v5` | full notebook-equivalent (narrow LoRA, optimizer-step schedule, reduced eval cadence; `valid_shadow_rows=4`, detached rerun) | `2907` | `2907` | `4` | `5814` | `4096` | `iter1 val_loss=0.577`; `iter1 val_took=36.390s`; no `iter10` report; `resource_tracker` warned about 1 leaked semaphore | lowering shadow validation made the first eval fast, but the detached run still exited right after `iter1`; no adapter checkpoint | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_narrow_schedopt_v5/train.log` |
| `baseline-mlx-narrow-schedopt-v7` | `nemotron_sft_lora_with_cot_v2_mlx_narrow_schedopt_v7` | full notebook-equivalent (narrow LoRA, optimizer-step schedule, reduced eval cadence; `valid_shadow_rows=4`, async-attached rerun) | `2907` | `2907` | `4` | `5814` | `4096` | `iter1 val_loss=0.577`; `iter1 val_took=52.753s`; `iter10 train_loss=0.811`, `it/sec=0.026`; `iter20 train_loss=0.993`, `it/sec=0.029`; `iter30 train_loss=0.827`, `it/sec=0.031`; `peak_mem=65.675 GB` | async-attached mode stayed alive, but throughput was far below historical narrow runs, so it was stopped before first checkpoint | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_narrow_schedopt_v7/train.log` |

## README-aligned local eval

| version | eval_name | scope | local320 | binary | gravity | roman | symbol | text | unit | notes |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `baseline-mlx-eval-smoke-v1` | `baseline_mlx_eval_smoke_v1` | smoke 6 rows | `4/6 = 0.6667` | `1/1` | `1/1` | `1/1` | `0/1` | `0/1` | `1/1` | `peak_memory_gb=65.63`, `generation_tps=8.20` |
| `baseline-mlx-eval-full320-v1` | `baseline_mlx_eval_full320_shard2_v1` | README local320 | `196/320 = 0.6125` | `19/60` | `39/50` | `50/50` | `17/60` | `21/50` | `50/50` | shard parallel; chunk peak `73.69 GB`; binary boxed extraction `1.0`; leading-zero retention `0.9` |
| `baseline-mlx-eval-full320-lora-fix-v1` | `baseline_mlx_eval_full320_shard1_lora_fix_v1` | README local320 | `6/320 = 0.0187` | `5/60` | `0/50` | `0/50` | `1/60` | `0/50` | `0/50` | one-shard rerun after stopping 2-shard for memory; binary boxed extraction `0.0`; format failure `1.0`; peak_memory_gb `76.08` |
| `baseline-mlx-eval-binary60-lora-fix-v2` | `baseline_mlx_eval_binary60_lora_fix_v2` | README binary60 | `18/60 = 0.3000` | `18/60` | `0/0` | `0/0` | `0/0` | `0/0` | `0/0` | `bit_other 12/46`, `bit_structured_byte_formula 6/14`; binary boxed extraction `1.0`; regex exact `1.0`; leading-zero retention `0.8667`; format failure `0.0` |
| `baseline-mlx-eval-symbol60-lora-fix-v2` | `baseline_mlx_eval_symbol60_lora_fix_v2` | README symbol60 | `13/60 = 0.2167` | `0/0` | `0/0` | `0/0` | `13/60` | `0/0` | `0/0` | `numeric_2x2 13/40`, `glyph_len5 0/20`; isolated rerun1 も `13/60` を **60/60 row-level identical** で再現。same 60 ids の full320 内 symbol は `20/60` で、MLX eval は batch composition-sensitive |
| `baseline-mlx-eval-full320-lora-fix-v2` | `baseline_mlx_eval_full320_lora_fix_v2` | README local320 | `194/320 = 0.6062` | `18/60` | `49/50` | `50/50` | `20/60` | `9/50` | `48/50` | shard parallel。`lora-fix-v1 6/320` からは大幅回復したが、旧 MLX v1 `196/320` は未更新。gravity/symbol は改善、text が大きく regress |
| `baseline-mlx-eval-full320-lora-fix-schedopt-v1` | `baseline_mlx_eval_full320_shard1_lora_fix_schedopt_v1` | README local320 | `189/320 = 0.5906` | `15/60` | `49/50` | `50/50` | `18/60` | `10/50` | `47/50` | one-shard rerun。`lora-fix-v2` と manifest は同一だが `-5` rows。binary boxed extraction `1.0`; format failure `0.0`; peak_memory_gb `77.49` |
| `baseline-mlx-notebook-original-fullrun-v2-eval-v1` | `baseline_mlx_notebook_original_fullrun_v2` | README local320 | `215/320 = 0.6719` | `26/60` | `50/50` | `50/50` | `15/60` | `25/50` | `49/50` | 2-shard eval。旧 MLX best `196/320` を更新。binary boxed extraction `1.0`; regex exact `1.0`; leading-zero retention `0.9`; format failure `0.0` |
| `baseline-mlx-notebook-original-routeaware-fullrun-v2-eval-v1` | `baseline_mlx_notebook_original_routeaware_fullrun_v2` | README local320 | `170/320 = 0.5312` | `33/60` | `15/50` | `40/50` | `5/60` | `29/50` | `48/50` | 2-shard eval。binary/text は改善したが、gravity/roman/symbol が大きく regress。binary boxed extraction `1.0`; regex exact `1.0`; leading-zero retention `0.9`; format failure `0.0` |
| `baseline-mlx-resume-routeaware-bit1317-lr2p5e5-ep1-eval-v1` | `baseline_mlx_notebook_original_resume_routeaware_bit1317_lr2p5e5_ep1` | README local320 | `142/320 = 0.4437` | `27/60` | `17/50` | `40/50` | `7/60` | `7/50` | `44/50` | baseline adapter resume + constrained route-aware mix。baseline `0.6719` を大きく下回ったため specialized gate は通さず |

## Binary bias specialized eval

| version | eval_name | rows | accuracy | bit_other | byte_formula | permutation | boolean_family | notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `baseline-mlx-notebook-original-fullrun-v2-binary-specialized-v1` | `baseline_mlx_notebook_original_fullrun_v2/phase0_binary_bias_specialized_eval` | `563` | `286/563 = 0.5080` | `118/218` | `128/283` | `40/62` | `47/60` | `boxed=1.0`; `regex_exact=1.0`; `leading_zero=0.8494`; `supported_bijection=33/50`; `supported_not_structured=15/55`; `rare_byte_transform=9/11` |
| `baseline-mlx-notebook-original-routeaware-fullrun-v2-binary-specialized-v1` | `baseline_mlx_notebook_original_routeaware_fullrun_v2/phase0_binary_bias_specialized_eval` | `563` | `348/563 = 0.6181` | `136/218` | `152/283` | `60/62` | `47/60` | `boxed=1.0`; `regex_exact=1.0`; `leading_zero=0.8946`; `supported_bijection=50/50`; `supported_not_structured=14/55`; `rare_byte_transform=11/11` |

## Baseline vs route-aware comparison

- README local320 は baseline **`215/320 = 0.6719`** に対して route-aware **`170/320 = 0.5312`** で、**`-45 rows / -0.1407`**。binary **`26 -> 33`** と text **`25 -> 29`** は伸びたが、gravity **`50 -> 15`**、roman **`50 -> 40`**、symbol **`15 -> 5`** の崩れが大きく、総合では明確に悪化した。
- binary bias specialized は baseline **`286/563 = 0.5080`** に対して route-aware **`348/563 = 0.6181`** で、**`+62 rows / +0.1101`**。subtype では `bit_permutation_inversion` **`40 -> 60`**, `bit_other` **`118 -> 136`**, `bit_structured_byte_formula` **`128 -> 152`** と全部改善した。
- focus / exposure では `supported_bijection` **`33/50 -> 50/50`**, `rare_byte_transform` **`9/11 -> 11/11`**, `dominant_structured_safe` **`64/120 -> 74/120`**, `dominant` **`105/210 -> 127/210`**, `supported` **`126/225 -> 153/225`** が改善した。一方で `supported_not_structured` は **`15/55 -> 14/55`** と微減で、boolean_family は **`47/60`** のまま横ばいだった。
- したがって今回の route-aware retrain は **binary-specialized 強化には有効**だが、README local320 の総合ベースライン置換には不適。現時点の総合候補は依然として **`baseline_mlx_notebook_original_fullrun_v2`**。
- continuation の **bit1317 / lr2.5e-5 / ep1** も README local320 では **`142/320 = 0.4437`** に沈み、baseline **`215/320`** どころか route-aware full retrain **`170/320`** よりも下だった。family 別では `binary 27/60`, `gravity 17/50`, `roman 40/50`, `symbol 7/60`, `text 7/50`, `unit 44/50` で、local320 gate 未達のため binary-specialized は **未実行** とした。

## Wait-state diagnosis probes

| version | runner | scope | valid_rows | total_iters | measured | status | artifacts |
| --- | --- | --- | ---: | ---: | --- | --- | --- |
| `baseline-mlx-narrow-rawprobe-v1` | raw `mlx_lm.lora.run` + chat patch only | narrow schedopt probe | `4` | `14` | `iter1 val_loss=0.577`; `iter1 val_took=17.457s`; `iter10 train_loss=0.837`, `it/sec=0.048`; `iter14 val_loss=0.658`; `iter14 train_loss=0.897`, `it/sec=0.163`; `peak_mem=65.632 GB` | completed | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_narrow_rawprobe_v1/train.log` |
| `baseline-mlx-narrow-patchprobe-v1` | current single-file patched trainer | narrow schedopt probe | `4` | `14` | `iter1 val_loss=0.577`; `iter1 val_took=17.057s`; `iter10 train_loss=0.837`, `it/sec=0.057`; `iter14 val_loss=0.656`; `iter14 train_loss=0.894`, `it/sec=0.160`; `peak_mem=65.632 GB` | completed | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_narrow_patchprobe_v1/training_result.json` |
| `baseline-mlx-narrow-asyncprobe-v1` | current single-file patched trainer via async shell | narrow schedopt probe | `4` | `14` | `iter1 val_loss=0.577`; `iter1 val_took=20.217s`; `iter10 train_loss=0.837`, `it/sec=0.057`; `iter14 val_loss=0.655`; `iter14 train_loss=0.898`, `it/sec=0.165`; `peak_mem=65.632 GB` | completed | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_narrow_asyncprobe_v1/train.log` |

## In-flight follow-up batch

| version | run_name | train_csv | bit_rows | mask_prompt | lr | status |
| --- | --- | --- | ---: | --- | ---: | --- |
| `baseline-mlx-v3f-exact-v1` | `nemotron_sft_lora_with_cot_v2_mlx_v3f_exact_v1` | `train_split_with_cot_v3f_safe_plus_notformula.csv` | `1021` | `true` | `1e-4` | stopped by user before first train report |
| `baseline-mlx-v3f-nomask-v1` | `nemotron_sft_lora_with_cot_v2_mlx_v3f_nomask_v1` | `train_split_with_cot_v3f_safe_plus_notformula.csv` | `1021` | `false` | `1e-4` | stopped by user before first train report |
| `baseline-mlx-v2-exact-v1` | `nemotron_sft_lora_with_cot_v2_mlx_v2_exact_v1` | `train_split_with_cot_v2.csv` | `1021` | `true` | `1e-4` | stopped by user before first train report |
| `baseline-mlx-v3f-lr5e5-v1` | `nemotron_sft_lora_with_cot_v2_mlx_v3f_lr5e5_v1` | `train_split_with_cot_v3f_safe_plus_notformula.csv` | `1021` | `true` | `5e-5` | stopped by user before first train report |
| `baseline-mlx-v3f-exact-v2` | `nemotron_sft_lora_with_cot_v2_mlx_v3f_exact_v2` | `train_split_with_cot_v3f_safe_plus_notformula.csv` | `1021` | `true` | `1e-4` | stopped by user mid-startup; no train report recorded |
| `baseline-mlx-v3f-nomask-v2` | `nemotron_sft_lora_with_cot_v2_mlx_v3f_nomask_v2` | `train_split_with_cot_v3f_safe_plus_notformula.csv` | `1021` | `false` | `1e-4` | stopped by user mid-startup; no train report recorded |
| `baseline-mlx-v3f-nothink-v1` | `nemotron_sft_lora_with_cot_v2_mlx_v3f_nothink_v1` | `train_split_with_cot_v3f_safe_plus_notformula.csv` | `1021` | `true` | `1e-4` | `enable_thinking=false`; stopped by user mid-startup |
| `baseline-mlx-v2-exact-v2` | `nemotron_sft_lora_with_cot_v2_mlx_v2_exact_v2` | `train_split_with_cot_v2.csv` | `1021` | `true` | `1e-4` | stopped by user mid-startup; no train report recorded |
| `baseline-mlx-v3f-lr5e5-v2` | `nemotron_sft_lora_with_cot_v2_mlx_v3f_lr5e5_v2` | `train_split_with_cot_v3f_safe_plus_notformula.csv` | `1021` | `true` | `5e-5` | stopped by user mid-startup; no train report recorded |

## Origin gap analysis

`baseline/nemotron-sft-lora-with-cot-v2/result/origin/reports` をオリジナルの source of truth として、README local320 の same-320 row-level を MLX 再現と突き合わせた。

| slice | origin | MLX | delta |
| --- | ---: | ---: | ---: |
| overall | `249/320 = 0.7781` | `196/320 = 0.6125` | `-53` |
| `general_stable_set` | `198/200 = 0.9900` | `160/200 = 0.8000` | `-38` |
| `binary_hard_set` | `29/60 = 0.4833` | `19/60 = 0.3167` | `-10` |
| `symbol_watch_set` | `22/60 = 0.3667` | `17/60 = 0.2833` | `-5` |

family delta:

- `text`: `49/50 -> 21/50` (`-28`)
- `gravity`: `50/50 -> 39/50` (`-11`)
- `binary`: `29/60 -> 19/60` (`-10`)
- `symbol`: `22/60 -> 17/60` (`-5`)
- `roman`: `50/50 -> 50/50` (`±0`)
- `unit`: `49/50 -> 50/50` (`+1`)

row-level overlap:

- `HF-only 65`
- `MLX-only 12`
- `both_wrong 59`
- `both_correct 184`

主要な失敗様式:

- **gravity**: origin-only 11 問はすべて `boxed_non_empty` で、MLX 予測が正解の **ほぼ 1/2**。`g = 2d/t^2` ではなく `g = d/t^2` と解いている系統誤差。
- **text**: origin-only 29 問はすべて `boxed_non_empty`。format failure ではなく、`inside -> mirror`, `under -> door`, `mirror -> puzzle` のような **復号語彙の内容劣化**。
- **binary**: MLX は `boxed_extraction_success_rate 1.0`, `format_failure_rate 0.0` まで改善しており、差分は format ではなく **content**。特に `bit_other` が `24/46 -> 13/46` (`-11`)。
- **symbol**: `glyph_len5` は origin / MLX とも `0/20`。差分は主に `numeric_2x2` の `22/40 -> 17/40` (`-5`)。
- 差分の大半は hard/manual ではなく **`verified_trace_ready` の再現差**で、selection tier でも `226/235 -> 177/235` (`-49`) が最大の落差。

構成差から見つかった具体的な bug candidate:

- HF `NemotronHMOE` は `experts[*].up_proj/down_proj` と `shared_experts.up_proj/down_proj` を持つが、MLX v1 script の default LoRA keys は **`mixer.shared_experts.up_proj/down_proj` しか拾っていなかった**。
- MLX `nemotron_h.py` では routed experts が `mixer.switch_mlp.fc1/fc2` に畳み込まれており、`mlx_lm` の LoRA 実装は `SwitchLinear` をサポートしている。
- つまり v1 run は MoE block で **shared expert だけを学習し、routed experts 側 (`switch_mlp.fc1/fc2`) を未学習**だった可能性が高い。
- そのため `baseline_mlx/reproduce_nemotron_sft_lora_with_cot_v2_mlx.py` の default LoRA keys は、後続修正で `mixer.switch_mlp.fc1/fc2`（および generic `mixer.up_proj/down_proj`）を含む形へ拡張した。

## LoRA target fix validation

| version | run_name | status | measured | notes |
| --- | --- | --- | --- | --- |
| `baseline-mlx-lora-fix-smoke-v1` | `nemotron_sft_lora_with_cot_v2_mlx_lora_fix_smoke_v1` | 完走 | `val_loss=0.607`, `train_loss=0.565`, `peak_mem=71.683 GB` | smoke では loss は旧 v1 と同値だが、trainable params は `23.976M -> 880.138M`、adapter は `3.52 GB` に増加 |
| `baseline-mlx-lora-fix-full-v1` | `nemotron_sft_lora_with_cot_v2_mlx_lora_fix_v1` | 完走 | `iter1 val_loss=0.683`; `iter200 val_loss=0.340`; `iter400 val_loss=0.276`; `iter600 val_loss=0.259`; `iter5200 val_loss=5.089`; `iter5400 val_loss=4.772`; `iter5600 val_loss=4.716`; `iter5800 val_loss=4.676`; `iter5814 val_loss=4.705`; `iter5814 train_loss=5.676`; `peak_mem=82.603 GB` | 拡張 LoRA target 自体は HF trainable params 規模に近づいたが、README local320 は `6/320` まで崩壊。終盤でも `learning_rate≈9.863e-05` のままで、scheduler step 単位 mismatch が有力 |
| `baseline-mlx-lora-fix-full-v2` | `nemotron_sft_lora_with_cot_v2_mlx_lora_fix_v2` | 完走 | `iter1 val_loss=0.683`; `iter400 val_loss=4.807`; `iter600 val_loss=1.359`; `iter800 val_loss=0.847`; `iter5814 val_loss=0.213`; `iter5814 train_loss=0.327`; `peak_mem=82.603 GB` | optimizer-step schedule + final accumulation flush を適用した parity-fix rerun。README local320 は `194/320`、binary60 は `18/60`、isolated symbol60 は `13/60` まで回復 |

## Scheduler mismatch finding

- notebook (`baseline/nemotron-sft-lora-with-cot-v2.ipynb`) は `learning_rate=1e-4`, `lr_scheduler_type="cosine"`, `warmup_ratio=0.05`, `gradient_accumulation_steps=8`, `num_train_epochs=2`。
- 現行 MLX 再現では schedule の decay/warmup steps を **microstep (`iters=5814`) 基準**で構築していたが、`mlx_lm` trainer は optimizer update を **8 microstep ごと**にしか進めない。
- その結果、warmup と cosine decay が **約 8 倍遅く進み**、実ログでも終盤 `iter5800` 付近で `learning_rate≈9.864e-05` とほぼ初期値のままだった。
- 次 run では `lr_schedule_step_unit=optimizer` を導入し、今回の baseline 条件 (`2907 rows`, `epochs=2`, `batch=1`, `grad_accum=8`) では **effective schedule steps = 727** として notebook 相当に合わせる。

## Notes

- 初期 v1 run の LoRA target は `mixer.in_proj`, `mixer.out_proj`, `mixer.shared_experts.up_proj`, `mixer.shared_experts.down_proj` だけだったが、後続の構成照合で routed expert 側の `mixer.switch_mlp.fc1/fc2` も必要と判明した。現行 script では generic `mixer.up_proj/down_proj` を含めて target を拡張している。
- `baseline_mlx/reproduce_nemotron_sft_lora_with_cot_v2_mlx.py` は 2026-04-07 更新で `--lr-schedule-step-unit {optimizer,micro}` を追加し、default を `optimizer` に変更した。今後の notebook 再現 run は optimizer-step 基準 schedule を使う。
- 今回の full run は **`train_split_with_cot.csv` の元 baseline 再現**であり、Bit Manipulation は `607` 行 sampling のまま。IDE 上で見えていた `1021` 行設定は別 notebook 変更で、今回の完走 run には使っていない。
- full320 実測は HF notebook reference `249/320 = 0.7781` を下回り、主な失点は `symbol 17/60`, `binary 19/60`, `text 21/50`。特に `glyph_len5 0/20`, `numeric_2x2 17/40`, `bit_other 13/46` が弱い。
- 拡張 LoRA target の full run は local320 `6/320` まで崩れ、binary ですら `boxed_extraction_success_rate=0.0`, `format_failure_rate=1.0` になった。これは単なる target 拡張の問題ではなく、schedule mismatch を含む学習設定不整合の可能性が高い。
- parity-fix rerun `baseline-mlx-lora-fix-full-v2` は optimizer-step schedule + final accumulation flush で train を回復し、README local320 も **`194/320`** まで戻した。ただし旧 MLX v1 `196/320` には届かず、family 差分は概ね `binary -1`, `gravity +10`, `roman ±0`, `symbol +3`, `text -12`, `unit -2` だった。
- 同一 manifest の expanded-target rerun `baseline-mlx-lora-fix-schedopt-v1` は **`189/320`** で、`baseline-mlx-lora-fix-full-v2` より `-5` rows。`gravity 49/50` は再現した一方、`binary 15/60`, `text 10/50`, `unit 47/50` まで揺れ、expanded LoRA + optimizer schedule 系は run-to-run variance を無視できない。
- narrow-target rerun `baseline-mlx-narrow-schedopt-v1` は **`iter4000 val_loss=0.177`** まで最良の学習曲線を示したが、`iter4060` 以降で main thread が `mlx::core::eval_impl` 内の `std::condition_variable::wait` に張り付き、進捗が停止した。`save_every=5814` だったため中間 adapter を回収できず、次 run は validation 回数を減らしつつ periodic save を有効にして再実行する。
- `baseline-mlx-narrow-schedopt-v2` は `steps_per_eval=5814` と `save_every=200` を入れた safe-rerun 準備だったが、前 run 終了直後の再起動で OOM により中断した。v2 output dir には dataset/shadow/config だけが残り、学習成果物は生成されていない。
- `baseline-mlx-narrow-schedopt-v3` は同条件の interactive rerun だったが、checkpoint 前の段階で異常に遅く、永続 train log も残らなかった。少なくとも `steps_per_eval=5814` と `save_every=200` を入れるだけでは recovery できていない。
- `baseline-mlx-narrow-schedopt-v4` は stdout/stderr を `train.log` へ逃がして PTY 干渉を切り分けた rerun だったが、**初回 validation 32 row に 329.883 秒**かかり、`iter1` 後も `iter10` に到達しなかった。したがって slowdown の主因は TTY ではなく、次の単独 rerun は `--valid-shadow-rows` を `32 -> 4` に落として初回 eval 自体を軽くする。
- `baseline-mlx-narrow-schedopt-v5` では `--valid-shadow-rows 4` により初回 validation が **`329.883s -> 36.390s`** まで改善した。したがって、初回 eval の重さそのものは主要因の 1 つだった。
- ただし同じ `valid_shadow_rows=4` でも、**detached 背景 run (`v5`) は `iter1` 直後に終了**し、**async-attached run (`v7`) は `iter30` まで進行**した。今の環境では長時間 MLX train を detached で投げるより、attached な shell で監視した方が挙動が安定する。
- `v7` 実行中の process sample では main thread の大半が `mlx::core::eval_impl -> std::condition_variable::wait` に入りつつ、`steel_matmul` / `binary_op_gpu` / Metal dispatch も見えていた。つまり current slowdown は **GPU 未使用ではなく、GPU を使いながら wait が多い状態** と見るのが妥当。
- shared environment 側では別系統の MLX train (`phase2_binary_dsl_mlx_v1.py train`) が **RSS 約 63 GB**、さらに Flutter/Dart test 群が CPU を大きく消費していた。一方で system memory free は **約 80%**, swap 0 のため、現時点のボトルネックは RAM 枯渇ではなく **GPU/Metal 実行待ちと shared runtime contention** である。
- raw / patched / async の **14-step probe 3 本**はすべて近い速度 (`iter10 it/sec = 0.048 ~ 0.057`) で収束した。したがって、今回の重い wait は **final accumulation flush patch そのもの**でも **async shell そのもの**でも説明しにくい。
- 2026-04-08 の追加修正として、`baseline_mlx/reproduce_nemotron_sft_lora_with_cot_v2_mlx.py` に **runtime preflight** を入れた。train 開始前に `memory_pressure`, `IOAccelerator`, competing MLX train process を記録し、`--fail-on-runtime-contention` を付ければ **同時 MLX train がいる状態で明示的に abort** できる。
- 実測では `nemotron_sft_lora_with_cot_v2_mlx_preflightcheck_v2` が **system_free_memory=45%**, `gpu_device_util=35%`, `renderer=23%`, `tiler=19%`, **4 本の外部 MLX train** を検知して即時 abort した。今後の full rerun は、この preflight が clean なタイミングで再開する。
- さらに `nemotron_sft_lora_with_cot_v2_mlx_preflightwarnprobe_v1` では、同じ **4 本の外部 MLX train** がいる状態で warn-only の tiny train を開始したところ、**2-step probe の `iter1` validation だけで `168.147s`** を要した。`runtime_preflight.json` でも `system_free_memory=41%`, `gpu alloc system memory ≈ 317 GB`, `gpu in-use system memory ≈ 315 GB` を記録しており、wait の主因が shared MLX contention であることを補強している。
- `symbol60` の isolated score は **初回 `13/60` / rerun1 `13/60`** で完全一致し、row-level も **60/60 identical**。一方で同じ 60 symbol ids を含む `full320` では **`20/60`** となり、raw output は **54/60 rows** で変化、**9 rows** で correctness が反転した。したがって MLX 系の family slice 判定は batch composition に敏感で、mainline 採用判断は **README actual full320** を優先する。
- 一方で `roman 50/50`, `unit 50/50` は README 条件下でも完全再現できており、baseline notebook 由来の知識は family ごとに保持率が大きく異なる。
- row-level で origin reference と突き合わせると `HF-only 65`, `MLX-only 12`, `both_wrong 59`, `both_correct 184`。HF-only loss は `text 29`, `binary 16`, `gravity 11`, `symbol 9` が中心で、特に text は **HF が取れて MLX だけ落とす**再現差が支配的。
- notebook 現在版の学習セルは `train_split_with_cot_v3f_safe_plus_notformula.csv` と `Bit Manipulation = 1021` を指している。したがって、今回の `train_split_with_cot.csv` / `607` 再現は「元 CSV baseline」の記録として保持しつつ、次段では **notebook current config の MLX 再現**も別 run として切り分ける。
- 2026-04-07 の現タスクでは、ユーザー指示により **並列学習は禁止**。LoRA target fix の full retrain 1 本だけを継続し、追加の並列再学習やアブレーション起動は保留にした。

## Default BF16 base-model inference probe

| version | model | prompt | measured | status | artifacts |
| --- | --- | --- | --- | --- | --- |
| `baseline-mlx-default-model-root-infer-probe-v1` | `DEFAULT_MODEL_ROOT` BF16 base, no adapter | `data/test.csv` row `00066667`, `enable_thinking=true`, boxed instruction, `max_tokens=128` | `load=3.223s`; `prompt=259 tok`; `prompt_tps=176.74`; `gen128=12.53s`; `gen_tps=11.78`; `MLX peak=59.318 GB`; `process RSS peak=59.563 GB`; `GPU in-use peak=61.193 GB`; `GPU device util peak=97%`; `generate avg device util=42.75%` | completed | `baseline_mlx/outputs/nemotron_default_model_root_infer_probe_v1/inference_probe/summary.json` |

- system telemetry (`IOAccelerator`) では `t≈4.26s` に `gpu in-use system memory` が **`~1.09 GB -> ~52.90 GB`** へ急増し、`t≈5.35s` で **`device util 97%`, `renderer 83%`, `in-use ~60.29 GB`** を記録した。
- `generation_complete` 後の cooldown では `gpu in-use system memory` が一度 **`61.19 GB`** まで残り、その後 `t≈17.55s` で **`~1.09 GB`** へ戻った。したがって、この BF16 base の単発推論は **ロード後常駐 ~59 GB級 / 生成中 system-GPU ~55-61 GB級** を見込む。
- `load_complete` 時点で tokenizer は `eos_token_id=11`, `eos_token_ids={11}` に揃っており、shadow model 経由のロードで推論は成功した。

## Notebook-current parity foundation

| version | command | profile | train_csv | sampled_rows | total_iters | optimizer_steps | measured | status | artifacts |
| --- | --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |
| `baseline-mlx-notebook-current-audit-v1` | `audit-notebook-current` | `notebook-current` | `train_split_with_cot_v3f_safe_plus_notformula.csv` | `3321` | `n/a` | `n/a` | `score=n/a`; `clear_omissions=0`; `records=3321`; `bit=1021`; `lora generic coverage=ok` | completed | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_notebook_current_audit_v1/notebook_current_audit_summary.json` |
| `baseline-mlx-notebook-current-prepare-v1` | `prepare-train --profile notebook-current` | `notebook-current` | `train_split_with_cot_v3f_safe_plus_notformula.csv` | `3321` | `6642` | `831` | `score=n/a`; `clear_omissions=0`; `valid_rows=1`; `steps_per_eval_requested=0`; `steps_per_eval_resolved=6642`; `save_every=6642` | completed | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_notebook_current_prepare_v1/prepare_manifest.json` |

- `baseline_mlx/reproduce_nemotron_sft_lora_with_cot_v2_mlx.py` に **`--profile notebook-current`** を追加し、現行 notebook training cell の `train_csv=v3f_safe_plus_notformula`, `Bit Manipulation=1021`, `epochs=2`, `batch=1`, `grad_accum=8`, `lr=1e-4`, `max_seq=4096`, `logging_steps=10`, `save_strategy=no`, `warmup_ratio=0.05` を明示的に解決できるようにした。
- profile 監査は `notebook_current_parity_report.{json,md}` として永続化され、**`status=no_clear_omissions`** を返す。これにより、現時点の MLX 単一ファイル基板では **明確な設定漏れが残っていない**ことを機械的に確認できる。
- notebook の `target_modules=r".*\.(in_proj|out_proj|up_proj|down_proj)$"` に対して、MLX 側は `mixer.in/out/up/down_proj` を必須 generic key として監査しつつ、`switch_mlp.fc1/fc2` と `shared_experts.up/down_proj` を **Nemotron-H MoE の構造差を埋める追加 key** として保持する。
- HF notebook には validation loop が無いため、MLX profile では **`valid_shadow_rows=1` + `steps_per_eval=0`** を notebook-friendly scaffolding とした。内部では `steps_per_eval<=0 -> total_iters` に解決されるため、**中間 validation 無し / iter1 と final のみ**の最小監視になる。
- packaging については、現スクリプトは引き続き **local MLX bundle (`adapter_config.json` + `adapters.safetensors`)** を出すだけで、notebook の PEFT/vLLM 提出互換 (`adapter_model.safetensors`, `submission.zip`) は **意図的に未主張**。今回の parity 判定は training 設定面に限定している。

## Generic notebook parity hardening

| version | command | profile | sampled_rows | total_iters | optimizer_steps | measured | status | artifacts |
| --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |
| `baseline-mlx-notebook-original-audit-v1` | `audit-notebook-original` | `notebook-original` | `2907` | `n/a` | `n/a` | `score=n/a`; `clear_omissions=0`; `records=2907`; `mask_prompt=false`; `lora generic coverage=ok` | completed | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_notebook_original_audit_v1/notebook_original_audit_summary.json` |
| `baseline-mlx-notebook-original-prepare-v1` | `prepare-train --profile notebook-original` | `notebook-original` | `2907` | `5814` | `727` | `score=n/a`; `clear_omissions=0`; `valid_rows=1`; `steps_per_eval_resolved=5814`; `save_every=5814`; `final_flush_microbatches=6` | completed | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_notebook_original_prepare_v1/prepare_manifest.json` |
| `baseline-mlx-notebook-original-probe-v1` | `train --profile notebook-original` (tiny smoke) | `notebook-original` | `6` | `6` | `1` | `score=n/a`; `trainable=880.138M`; `peak_mem=77.550 GB`; `runtime_free=98%`; `bundle_zip=2.978 GB` | completed | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_notebook_original_probe_v1/training_result.json` |
| `baseline-mlx-notebook-current-audit-v2` | `audit-notebook-current` | `notebook-current` | `3321` | `n/a` | `n/a` | `score=n/a`; `clear_omissions=0`; `records=3321`; `bit=1021`; `mask_prompt=false` | completed | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_notebook_current_audit_v2/notebook_current_audit_summary.json` |
| `baseline-mlx-notebook-current-prepare-v2` | `prepare-train --profile notebook-current` | `notebook-current` | `3321` | `6642` | `831` | `score=n/a`; `clear_omissions=0`; `valid_rows=1`; `steps_per_eval_resolved=6642`; `save_every=6642`; `final_flush_microbatches=2` | completed | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_notebook_current_prepare_v2/prepare_manifest.json` |

- `baseline_mlx/reproduce_nemotron_sft_lora_with_cot_v2_mlx.py` の parity machinery を **current 専用から notebook-original / notebook-current 共通**へ組み替え、`audit-notebook-original` を追加した。これで 2 系統の notebook 設定を **同じ単一ファイル** から監査・prepare できる。
- parity の core check に **`mask_prompt`** を昇格し、original/current の両 profile を **`mask_prompt=false`** に統一した。これは original notebook が `assistant_only_loss` / `completion_only_loss` を使っておらず、**full-sequence loss 寄り**であることに合わせた修正で、以前の current foundation (`mask_prompt=true`) 仮説はここで退役させる。
- MLX train 実行経路には tokenizer parity patch を入れ、`mlx_lm.lora.load()` 直後に **`eos_token_ids` 正規化** と **`pad_token=eos_token` 補完**を適用するようにした。`notebook_original_parity_report.md` には HF 側 observed log (`eos_token_id=11`, `pad_token_id=11`) も記録した。
- original notebook parity は audit/prepare とも **`status=no_clear_omissions`**。さらに tiny smoke train では **`Trainable parameters: 2.787% (880.138M/31577.936M)`** を出し、notebook log の **`880,138,240` trainable params** と一致したため、LoRA target coverage の大きな抜けは潰せたと判断する。
- tiny smoke train は parity gate ではなく実行経路確認用なので、`type_samples`, `num_epochs`, `logging_steps` を意図的に縮めたぶん `prepare_manifest.json` 上の `notebook_parity.status` は **`mismatches_found`** になる。これは基板の不整合ではなく、probe 用 override を反映しただけである。
- 依然として出力は **local MLX bundle (`adapter_config.json` + `adapters.safetensors`)** であり、README 本番契約の **PEFT/vLLM submission 互換は未主張**。今回解消したのは **MLX LoRA 側の設定漏れ / tokenizer / mask / schedule / target coverage** であって、base model 差分までは埋めていない。

## Loss / LR parity diagnosis

| version | command | profile | sampled_rows | total_iters | optimizer_steps | measured | status | artifacts |
| --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |
| `baseline-mlx-notebook-original-audit-v3` | `audit-notebook-original` | `notebook-original` | `2907` | `n/a` | `728` | `score=n/a`; `clear_omissions=0`; `optimizer_steps=728`; `logging_unit=optimizer` | completed | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_notebook_original_audit_v3/notebook_original_audit_summary.json` |
| `baseline-mlx-notebook-original-prepare-v2` | `prepare-train --profile notebook-original` | `notebook-original` | `2907` | `5814` | `728` | `score=n/a`; `effective_schedule_steps=728`; `warmup_ratio=0.05`; `final_flush_microbatches=3`; `flush_on_epoch_boundary=true` | completed | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_notebook_original_prepare_v2/prepare_manifest.json` |
| `baseline-mlx-notebook-current-prepare-v3` | `prepare-train --profile notebook-current` | `notebook-current` | `3321` | `6642` | `832` | `score=n/a`; `effective_schedule_steps=832`; `final_flush_microbatches=1`; `flush_on_epoch_boundary=true` | completed | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_notebook_current_prepare_v3/prepare_manifest.json` |
| `baseline-mlx-notebook-original-loss-v5` | `train --profile notebook-original --steps-per-report 1 --steps-per-report-step-unit optimizer` (partial diagnostic run) | `notebook-original` | `2907` | `5814` | `728` | `score=n/a`; `Opt1 loss=1.052 lr=0`; `Opt2 loss=1.916 lr=2.778e-06`; `Opt3 loss=1.305 lr=5.556e-06`; `Opt10 single-step loss=0.599 lr=2.500e-05`; `mean Opt1-10 loss=0.9282`; `peak_mem≈80.230 GB` | partial diagnostic completed | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_notebook_original_loss_v5/console.log` |

- 根本原因は 2 つだった。1 つ目は `steps_per_report_step_unit=optimizer` が `mlx_lm.lora.train_model()` 内で `TrainingArgs` に詰め替える際に落ちており、loss/LR ログが **microstep 基準**に戻っていたこと。2 つ目は optimizer-step 数を **`ceil(total_iters / grad_accum)` = 727** と見積もっていたことで、HF notebook の **`728/728`**（epoch ごとの端数 flush）と 1 step ずれていたこと。
- これを受けて、single-file 基板に **`steps_per_report_step_unit` の runtime 伝播**と **`flush_on_epoch_boundary=true`** を追加した。notebook parity profile は now **original=`728` steps / current=`832` steps** に更新され、prepare manifest でもそのまま確認できる。
- HF / Transformers の cosine warmup を `num_training_steps=728`, `num_warmup_steps=36` で直接回すと、optimizer 側の LR は **initial `0.0` → step1 `2.778e-06` → step2 `5.556e-06` → step10 `2.500e-05`** となる。partial diagnostic run の MLX 実測も **`Opt1=0`, `Opt2=2.778e-06`, `Opt3=5.556e-06`, `Opt10=2.500e-05`** で一致し、**LR scheduler の予期しない不一致は解消**したと判断する。
- 一方で loss の絶対値は HF notebook と一致しない。HF notebook HTML table の **`Step 10 = 10.750076`** は「最初の 10 optimizer steps の平均 loss」なので、単点の `Opt 10 = 0.599` ではなく、MLX 側も **`Opt1-10 mean = 0.9282`** で揃えて比較した。それでも桁が大きく離れており、現時点では **LR parity は取れたが、loss magnitude は HF と MLX の proxy 比較指標として使えない**。この差は base model / runtime / loss reporting semantics を含む複合差として扱う。
- 旧 `prepare` 記録の **original `727` / current `831`** は、この epoch-boundary flush 修正前の値であり、loss/LR parity の観点では **`prepare-v2` / `prepare-v3` が正**である。

## Running full MLX reproduction baseline

| version | command | profile | sampled_rows | total_iters | optimizer_steps | measured | status | artifacts |
| --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |
| `baseline-mlx-notebook-original-fullrun-v1` | `train --profile notebook-original --force-prepare` | `notebook-original` | `2907` | `5814` | `728` | `score=n/a`; `trainable=880.138M`; `Iter1 val=1.220`; `Opt90 loss=0.959 lr=9.875e-05`; `it_per_sec=0.058`; `tokens_per_sec=36.385`; `peak_mem=81.271 GB`; stopped for reboot | interrupted | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_notebook_original_fullrun_v1/console.log` |
| `baseline-mlx-notebook-original-fullrun-v2` | `train --profile notebook-original --force-prepare --fail-on-runtime-contention` | `notebook-original` | `2907` | `5814` | `728` | `score=n/a`; `trainable=880.138M`; `Iter1 val=1.220`; `Iter5814 val=0.284`; `Iter5814 train_loss=0.316`; `avg_train_itps=0.740`; `peak_mem=82.603 GB`; `bundle_zip=3.245 GB`; `restart_after_reboot=true`; `preflight_competing=0` | completed | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_notebook_original_fullrun_v2/training_result.json` |
| `baseline-mlx-notebook-original-batch2-probe-v1` | `train --profile notebook-original --batch-size 2 --grad-accumulation-steps 4 --num-epochs 0.056` | `notebook-original` | `2907` | `81` | `21` | `score=n/a`; `concurrent_with_fullrun=true`; `Iter1 val=1.323`; `val_took=21.146s`; `console_log=missing (tee opened before mkdir)`; stopped before first train report | aborted | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_notebook_original_batch2_probe_v1/prepare_manifest.json` |
| `baseline-mlx-contention-probe-v1` | `train --profile notebook-original --num-epochs 0.001 --fail-on-runtime-contention` | `notebook-original` | `2907` | `2` | `1` | `score=n/a`; `preflight_competing=1`; `pid=55490`; ancestor-wrapper false positive resolved | aborted as designed | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_contention_probe_v1/runtime_preflight.json` |

- 2026-04-08 時点で、parity-hardened single-file baseline の **FULLRUN** を `nemotron_sft_lora_with_cot_v2_mlx_notebook_original_fullrun_v1` として起動した。run は detached で継続中で、`console.log` を継続追記している。
- detached 実行では runtime preflight が wrapper shell を「other MLX/Nemotron train process」として列挙するが、これは **同一 detached job の bash/uv/tee ラッパ**であり、実競合ではないことを ps で確認した。したがって fullrun 本体はそのまま継続させている。
- 最初の train report は **`Iter 80 (Opt 10)`** で、**`Train loss 0.931 / LR 2.500e-05 / It/sec 0.061 / Tokens/sec 36.667 / Peak mem 80.230 GB`**。この時点の単純見積もりでは残り **約 26.1 時間**で、run は「停止」ではなく **低速だが前進中** と判断している。
- `batch2 / accum4` の短尺 speed probe を fullrun と並走させると、combined `In use system memory` は **約 236.8 GB** まで上がった一方、clean baseline だった fullrun 側の speed は **`Opt20 it/sec 0.058` → `Opt30 it/sec 0.042`** まで落ちた。これは並列化による throughput 汚染が大きく、speed 比較として無効なので probe は停止した。
- 上の理由により、**batch-size 系の速度比較は fullrun と同時には行わない**。必要なら isolated window で再実行する。なお今回の probe は `tee` が run dir 作成前に開いたため `console.log` を残せず、shell 出力と生成 artifact のみを証跡とした。
- detached 起動で `--fail-on-runtime-contention` が wrapper bash を「other train process」と誤認していたので、single-file 基板の process scan を修正し、**current train process の ancestor PID** と **`bash/sh/zsh -c` shell wrapper** を除外するようにした。live 検証では `collect_competing_mlx_train_processes(current_pid=55490) == []` を確認し、別プロセスからの CLI probe では **実競合の fullrun 本体 `pid=55490` だけを 1 件**拾って期待どおり abort した。
- probe 停止後の fullrun は **`Iter 320 (Opt 40): It/sec 0.051, Tokens/sec 32.276, Peak mem 81.271 GB`** まで回復した。したがって `Opt30` の落ち込みは常時劣化というより **並走干渉の一過性影響** とみなす。
- その後さらに **`Iter 400 (Opt 50): It/sec 0.058, Tokens/sec 37.452, Peak mem 81.271 GB`** を観測し、throughput はほぼ `Opt20` 水準まで戻った。fullrun は low-throughput ではあるが、**probe 停止後は clean baseline に概ね復帰**して継続している。
- 現在位置は **`Iter 480 (Opt 60 / 728)`**。最新 report は **`Train loss 1.018 / LR 9.977e-05 / It/sec 0.058 / Tokens/sec 37.479 / Peak mem 81.271 GB`** で、残りは **`5334` microsteps / `668` optimizer steps**。直近 throughput をそのまま使う単純見積もりでは、終了まで **約 25.55 時間**。
- 次の節目 **`Iter 560 (Opt 70 / 728)`** では **`Train loss 1.530 / LR 9.952e-05 / It/sec 0.053 / Tokens/sec 32.838 / Peak mem 81.271 GB`**。残りは **`5254` microsteps / `658` optimizer steps** で、最新速度ベースの単純見積もりは **約 27.54 時間**。`Opt50-70` の clean 区間を見る限り、現在の sustained throughput はおおむね **`0.053-0.058 it/s`** の帯にある。
- 続く **`Iter 640 (Opt 80 / 728)`** は **`Train loss 1.526 / LR 9.918e-05 / It/sec 0.058 / Tokens/sec 37.010 / Peak mem 81.271 GB`**。残りは **`5174` microsteps / `648` optimizer steps** で、最新速度ベースの単純見積もりは **約 24.78 時間**。Opt70 の一時低下から 다시 `0.058 it/s` へ戻っており、throughput は依然レンジ内で揺れているだけとみる。
- **`Iter 720 (Opt 90 / 728)`** では **`Train loss 0.959 / LR 9.875e-05 / It/sec 0.058 / Tokens/sec 36.385 / Peak mem 81.271 GB`**。残りは **`5094` microsteps / `638` optimizer steps** で、最新速度ベースの単純見積もりは **約 24.40 時間**。Opt80-90 でも `0.058 it/s` を維持しており、現時点の clean baseline throughput は再び安定している。
- PC 再起動のため、この fullrun は **`Iter 720 (Opt 90 / 728)`** 時点で明示停止した。`save_every=0` の final-only 運用だったため、**resumable checkpoint は残っていない**。保持されるのは `console.log`・`prepare_manifest.json`・parity/report artifact・ここまでの Git ledger のみで、学習重みの進捗自体は再実行が必要。
- 再起動後、同条件で **`nemotron_sft_lora_with_cot_v2_mlx_notebook_original_fullrun_v2`** を clean restart した。修正済みの `--fail-on-runtime-contention` を有効にしたまま、runtime preflight は **`preflight_competing=0`** を通過し、初回 validation も **`Iter 1: Val loss 1.220, Val took 1.035s`** と v1 よりやや速く立ち上がった。
- v2 の最初の train report は **`Iter 80 (Opt 10): Train loss 0.927 / LR 2.500e-05 / It/sec 0.713 / Tokens/sec 429.584 / Peak mem 80.230 GB`**。v1 の同位置 **`0.061 it/s`** と比べて **約 11.7x** 速く、残り **`5734` microsteps / `718` optimizer steps** の単純見積もりは **約 2.23 時間** まで短縮した。再起動後の環境は throughput 面で明確に改善している。
- v2 はその後も **`Opt20=0.730`, `Opt30=0.709`, `Opt40=0.721`, `Opt50=0.709`, `Opt60=0.716`, `Opt70=0.733 it/s`** と高水準を維持した。`Opt30-70` の平均は **`0.718 it/s`**、`Opt70` 時点の残り **`5254` microsteps / `658` optimizer steps** に対する単純 ETA は **約 1.99 時間**。現状のボトルネックは v1 時代とは別物で、reboot 前の 24-27h 級 estimate はもはや適用しない。
- さらに **`Opt80=0.727`, `Opt90=0.732`, `Opt100=0.728`, `Opt110=0.715`, `Opt120=0.754`, `Opt130=0.712`, `Opt140=0.723`, `Opt150=0.752`, `Opt160=0.737`, `Opt170=0.796`, `Opt180=0.784`, `Opt190=0.738`, `Opt200=0.744`, `Opt210=0.746`, `Opt220=0.748`, `Opt230=0.729`, `Opt240=0.752`, `Opt250=0.726`, `Opt260=0.757`, `Opt270=0.765`, `Opt280=0.719`, `Opt290=0.733`, `Opt300=0.715`, `Opt310=0.764`, `Opt320=0.782`, `Opt330=0.732`, `Opt340=0.738`, `Opt350=0.760`, `Opt360=0.728`, `Opt370=0.738`, `Opt380=0.731 it/s`** を観測した。`Opt240-380` の平均は **`0.742 it/s`** で、reboot 後の高速化が一時的な spike ではなく sustained throughput であることが確認できた。
- 現在位置は **`Iter 3035 (Opt 380 / 728)`**。最新 report は **`Train loss 0.332 / LR 5.474e-05 / It/sec 0.731 / Tokens/sec 469.065 / Trained Tokens 1,896,983 / Peak mem 82.102 GB`**。残りは **`2779` microsteps / `348` optimizer steps** で、直近 8 report 平均 **`0.747 it/s`** に基づく単純 ETA は **約 1.03 時間**。
- fullrun v2 は **`Iter 5814 (Opt 728 / 728)`** まで完走した。最終 validation は **`Val loss 0.284 (0.555s)`**、最終 train report は **`Train loss 0.316 / LR 6.708e-07 / It/sec 0.731 / Tokens/sec 466.694 / Trained Tokens 3,630,012 / Peak mem 82.603 GB`**。`Iter80` 以降の train report 平均 throughput は **`0.740 it/s`** で、reboot 後の高速化を最後まで維持した。
- 完走後の artifact として **`adapter/adapters.safetensors`**, **`adapter/0005814_adapters.safetensors`**, **`training_result.json`**, **`mlx_adapter_bundle.zip`** を確認した。`training_result.json` には bundle zip **`3,245,381,643 bytes`** が記録されており、single-file MLX 再現 baseline の baseline benchmark 実行に進める状態になった。

## Route-aware retrain

| version | command | train_csv | sampled_rows | total_iters | optimizer_steps | measured | status | artifacts |
| --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |
| `baseline-mlx-routeaware-fullrun-v1` | `train --profile notebook-original --train-csv train_split_with_cot_v2_plus_binary_route_aware.csv --type-sample ...full counts...` | `cuda-train-data-analysis-v1/proof_first_solver_factory_routing/artifacts/train_split_with_cot_v2_plus_binary_route_aware.csv` | `7268` | `14536` | `1818` | `Iter1 val=1.340`; startup only; restarted immediately to attach persisted `console.log` before first optimizer report | aborted early for logging | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_notebook_original_routeaware_fullrun_v1/prepare_manifest.json` |
| `baseline-mlx-routeaware-fullrun-v2` | `train --profile notebook-original --train-csv train_split_with_cot_v2_plus_binary_route_aware.csv --type-sample ...full counts... --fail-on-runtime-contention` | `cuda-train-data-analysis-v1/proof_first_solver_factory_routing/artifacts/train_split_with_cot_v2_plus_binary_route_aware.csv` | `7268` | `14536` | `1818` | `Iter1 val=1.340`; `Opt10 loss=0.937 lr=1.000e-05 itps=0.701`; `Opt20=0.728`; `Opt30=0.717`; `Opt40=0.743`; `Opt50=0.692`; `Opt60=0.735`; `Opt70=0.744`; `Opt80=0.716`; `Opt90=0.749`; `Opt100=0.741`; `Opt110=0.755`; `Opt120=0.722`; `Opt130=0.733`; `Opt140=0.735`; `Opt150=0.748`; `Opt160=0.724`; `Opt170=0.746`; `Opt180=0.739`; `Opt190=0.746`; `Opt200=0.713`; `Opt210=0.719`; `Opt220=0.745`; `Opt230=0.742`; `Opt240=0.766`; `Opt250=0.696`; `Opt260=0.740`; `Opt270=0.744`; `Opt280=0.741`; `Opt290=0.764`; `Opt300=0.741`; `Opt310=0.757`; `Opt320=0.729`; `Opt330=0.764`; `Opt340=0.730`; `Opt350=0.742`; `Opt360=0.757`; `Opt370=0.783`; `Opt380=0.735`; `Opt390=0.748`; `Opt400=0.711`; `Opt410=0.751`; `Opt420=0.735`; `Opt430=0.736`; `Opt440=0.767`; `Opt780=0.757`; `Opt1120=0.747`; `Opt1460=0.752`; `Iter14536 val=0.413`; `Iter14536 train_loss=0.284`; `avg_train_itps=0.742`; `peak_mem=82.603 GB`; `bundle_zip=3.248 GB` | completed | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_notebook_original_routeaware_fullrun_v2/training_result.json` |

- route-aware retrain では **single-file MLX pipeline と notebook-original profile は据え置き**、変更点は **`train_csv` 差し替え**と、追加された binary rows を捨てないための **`type_sample` 全件数上書き**だけに限定した。
- route-aware CSV の sampling は **`Bit Manipulation=1317`, `Equation Transformation=200`, `Gravitational Constant=1511`, `Numeral Conversion=1491`, `Text Encryption=1407`, `Unit Conversion=1342`** で、`sampled_rows=7268`, `optimizer_steps=1818`。baseline fullrun (`2907 rows`, `728 steps`) より大きく、現時点の sustained throughput では **約 5.3 時間**級の run になる。
- 20 分後の定点では **`Iter 2160 (Opt 270 / 1818)`** まで到達した。最新 report は **`Train loss 0.452 / LR 9.765e-05 / It/sec 0.744 / Tokens/sec 454.688 / Trained Tokens 1,338,611 / Peak mem 82.554 GB`**。直近 10 report 平均は **`0.735 it/s`** で、残りは **`12376` microsteps / `1548` optimizer steps**、単純 ETA は **約 4.68 時間**。
- さらに 30 分後の定点では **`Iter 3520 (Opt 440 / 1818)`** に到達した。最新 report は **`Train loss 0.376 / LR 9.123e-05 / It/sec 0.767 / Tokens/sec 447.751 / Trained Tokens 2,173,112 / Peak mem 82.554 GB`**。直近 10 report 平均は **`0.746 it/s`** で、残りは **`11016` microsteps / `1378` optimizer steps**、単純 ETA は **約 4.10 時間**。
- さらに 1 時間後の定点では **`Iter 6240 (Opt 780 / 1818)`** に到達した。最新 report は **`Train loss 0.285 / LR 6.863e-05 / It/sec 0.757 / Tokens/sec 452.406 / Trained Tokens 3,852,520 / Peak mem 82.554 GB`**。直近 10 report 平均は **`0.741 it/s`** で、残りは **`8296` microsteps / `1038` optimizer steps**、単純 ETA は **約 3.11 時間**。
- さらに 1 時間後の定点では **`Iter 8956 (Opt 1120 / 1818)`** に到達した。最新 report は **`Train loss 0.286 / LR 3.979e-05 / It/sec 0.747 / Tokens/sec 453.717 / Trained Tokens 5,525,132 / Peak mem 82.554 GB`**。直近 10 report 平均は **`0.746 it/s`** で、残りは **`5580` microsteps / `698` optimizer steps**、単純 ETA は **約 2.08 時間**。
- さらに 1 時間後の定点では **`Iter 11676 (Opt 1460 / 1818)`** に到達した。最新 report は **`Train loss 0.274 / LR 1.437e-05 / It/sec 0.752 / Tokens/sec 453.946 / Trained Tokens 7,215,887 / Peak mem 82.554 GB`**。直近 10 report 平均は **`0.748 it/s`** で、残りは **`2860` microsteps / `358` optimizer steps**、単純 ETA は **約 1.06 時間**。
- route-aware fullrun v2 は **`Iter 14536 (Opt 1818 / 1818)`** まで完走した。最終 validation は **`Val loss 0.413 (0.493s)`**、最終 train report は **`Train loss 0.284 / LR 6.305e-07 / It/sec 0.749 / Tokens/sec 455.112 / Trained Tokens 8,958,288 / Peak mem 82.603 GB`**。全 train report 平均 throughput は **`0.742 it/s`** で、完走 artifact として **`adapter/adapters.safetensors`**, **`adapter/0014536_adapters.safetensors`**, **`training_result.json`**, **`mlx_adapter_bundle.zip`** を確認した。bundle zip は **`3,247,798,973 bytes`**。

## Resume-from-baseline continuation matrix

| version | run_name | bit_rows | lr | epochs | sampled_rows | total_iters | optimizer_steps | measured | status | artifacts |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| `baseline-mlx-resume-routeaware-bit800-lr5e5-ep2-v1` | `nemotron_sft_lora_with_cot_v2_mlx_notebook_original_resume_routeaware_bit800_lr5e5_ep2` | `800` | `5e-5` | `2` | `3100` | `6200` | `776` | `resume=baseline_fullrun_v2`; `Iter1 val=0.133`; `val_took=1.200s`; `Metal OOM before Opt10` | blocked | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_notebook_original_resume_routeaware_bit800_lr5e5_ep2/console.log` |
| `baseline-mlx-resume-routeaware-bit1000-lr5e5-ep2-v1` | `nemotron_sft_lora_with_cot_v2_mlx_notebook_original_resume_routeaware_bit1000_lr5e5_ep2` | `1000` | `5e-5` | `2` | `3300` | `6600` | `826` | `resume=baseline_fullrun_v2`; `Iter1 val=0.355`; `Opt40 loss=0.388`; `itps=0.027`; `peak_mem=82.554 GB`; `stopped to free memory after wait-state` | blocked | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_notebook_original_resume_routeaware_bit1000_lr5e5_ep2/console.log` |
| `baseline-mlx-resume-routeaware-bit1000-lr2p5e5-ep1-v1` | `nemotron_sft_lora_with_cot_v2_mlx_notebook_original_resume_routeaware_bit1000_lr2p5e5_ep1` | `1000` | `2.5e-5` | `1` | `3300` | `3300` | `413` | `resume=baseline_fullrun_v2`; `Iter1 val=0.355`; `Opt40 loss=0.359`; `itps=0.027`; `peak_mem=82.554 GB`; `stopped to free memory after wait-state` | blocked | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_notebook_original_resume_routeaware_bit1000_lr2p5e5_ep1/console.log` |
| `baseline-mlx-resume-routeaware-bit1317-lr2p5e5-ep1-v1` | `nemotron_sft_lora_with_cot_v2_mlx_notebook_original_resume_routeaware_bit1317_lr2p5e5_ep1` | `1317` | `2.5e-5` | `1` | `3617` | `3617` | `453` | `resume=baseline_fullrun_v2`; `Iter1 val=0.476`; `Iter3617 val=0.455`; `Iter3617 train_loss=0.329`; `avg_train_itps=0.698`; `peak_mem=82.603 GB`; `bundle_zip=3.246 GB` | completed | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_notebook_original_resume_routeaware_bit1317_lr2p5e5_ep1/training_result.json` |

- 4 本とも **`--resume-adapter-file baseline_mlx/.../fullrun_v2/adapter/adapters.safetensors`** を使い、**route-aware CSV + baseline non-binary counts (`Eq=200`, `Gravity=400`, `Numeral=300`, `Text=700`, `Unit=700`)** に固定している。可変なのは **bit rows / learning rate / epochs** だけ。
- intentional parallel train のため runtime preflight は他の 3 run を列挙したが、今回は **比較実験として並列化が意図どおり**なので `--fail-on-runtime-contention` は使っていない。
- 初期 validation だけを見ると **bit800 / lr5e-5 / ep2** が **`Val loss 0.133`** で最も良い立ち上がりを見せた。一方で **bit1317 / lr2.5e-5 / ep1** は **`Val loss 0.476`** と最も重い設定で、route-aware full retrain の general collapse を繰り返すかを今後の local320 で確認する。
- ただし **4 並列**はそのままでは安定しなかった。**bit800 / lr5e-5 / ep2** は `Iter 1` の直後に **`[METAL] ... Insufficient Memory`** で落ち、`training_result.json` を残さなかった。したがって現環境の continuation full-train は **4 本同時だと OOM リスクあり** とみなす。
- 生存した 3 本は **`Opt20`** まで進み、**bit1000 / lr5e-5 / ep2 = `0.294 it/s`**, **bit1000 / lr2.5e-5 / ep1 = `0.294 it/s`**, **bit1317 / lr2.5e-5 / ep1 = `0.298 it/s`** を観測した。単純見積もりでは残り ETA はそれぞれ **約 6.1h / 3.0h / 3.2h**。
- 20 分定点では **bit1000 / lr5e-5 / ep2** と **bit1000 / lr2.5e-5 / ep1** がともに **`Opt30 loss=0.359 / itps=0.285 / peak=81.375 GB`** まで横並びで進み、ETA は **約 6.50h / 3.13h**。一方の **bit1317 / lr2.5e-5 / ep1** は **`Opt40 loss=0.386 / itps=0.305 / peak=80.641 GB`** とわずかに速く、ETA **約 3.23h** だった。
- その後 1 時間定点では **2 本の bit1000 run がともに `Opt40` で `itps=0.027`, `peak_mem=82.554 GB`** まで失速し、明確な wait-state に入った。そこで両者を停止し、**bit1317 / lr2.5e-5 / ep1** だけを残してメモリを解放した。
- 絞り込み後 10 分で **bit1317 / lr2.5e-5 / ep1** は **`Opt90 loss=0.338 / itps=0.747 / peak=81.193 GB`** まで回復した。残りは **`2897` microsteps / `363` optimizer steps** で、単純 ETA は **約 1.72h**。現時点の continuation 本命はこの 1 本である。
- さらに 45 分後の定点では **bit1317 / lr2.5e-5 / ep1** が **`Opt360 loss=0.281 / itps=0.747 / peak=82.603 GB`** まで到達した。残りは **`737` microsteps / `93` optimizer steps** で、単純 ETA は **約 0.27h**。完走後は README local320 を即時に流す待機ジョブを別 shell で仕掛けた。
- bit1317 continuation は **`Iter 3617 (Opt 453 / 453)`** で完走した。最終 validation は **`Val loss 0.455 (0.583s)`**、最終 train report は **`Train loss 0.329 / LR 1.727e-07 / It/sec 0.727 / Tokens/sec 454.649 / Trained Tokens 2,164,850 / Peak mem 82.603 GB`**。全 train report 平均 throughput は **`0.698 it/s`**、bundle zip は **`3,246,047,318 bytes`**。
- 完走直後に README local320 の screen を自動起動した。さらに、この score が baseline **`0.6719`** を超えた場合だけ binary-specialized を続行する待機ジョブも追加した。したがって以後の continuation 分岐は **local320 score** で自動的に絞られる。
- screen 結果は **`142/320 = 0.4437`** で、baseline gate **`0.6719`** を大きく下回った。binary は **`27/60`** と baseline **`26/60`** をわずかに上回ったが、`text 7/50`, `gravity 17/50`, `symbol 7/60` が重く、general 保持には失敗した。このため conditional specialized shell は **`skip_specialized_below_baseline`** で終了した。

## Stage freeze/unfreeze v1

| version | run_name | train_csv | sampled_rows | total_iters | optimizer_steps | measured | status | artifacts |
| --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |
| `baseline-mlx-stagefreeze-v1-stage1-broad-launch` | `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_stage1_broad_v3f_union` | `baseline/nemotron-sft-lora-with-cot-v2/artifacts/train_split_with_cot_v3f_safe_plus_notformula.csv` | `3321` | `6642` | `832` | `Iter1 val=1.677`; `Opt10 loss=0.892 lr=2.195e-05 itps=0.669 peak=80.897 GB`; `Opt50 loss=0.779 lr=9.998e-05 itps=0.756 peak=81.208 GB`; `Opt100 loss=0.710 lr=9.885e-05 itps=0.742 peak=81.954 GB`; `Opt110 loss=0.701 lr=9.841e-05 itps=0.742 peak=81.954 GB`; `Opt190 loss=0.539 lr=9.249e-05 itps=0.742 peak=81.954 GB`; `Opt250 loss=0.428 lr=8.549e-05 itps=0.415 peak=82.620 GB`; `Opt260 loss=0.456 lr=8.413e-05 itps=0.420 peak=82.620 GB`; `Opt270 loss=0.447 lr=8.273e-05 itps=0.396 peak=82.620 GB`; `Opt280 loss=0.512 lr=8.128e-05 itps=0.418 peak=82.620 GB`; `Opt290 loss=0.444 lr=7.978e-05 itps=0.410 peak=82.620 GB`; `Opt300 loss=0.447 lr=7.825e-05 itps=0.407 peak=82.620 GB`; `Opt310 loss=0.485 lr=7.667e-05 itps=0.409 peak=82.620 GB`; `Opt320 loss=0.409 lr=7.505e-05 itps=0.403 peak=82.620 GB`; `Opt330 loss=0.472 lr=7.340e-05 itps=0.422 peak=82.620 GB`; `Opt340 loss=0.375 lr=7.172e-05 itps=0.410 peak=82.620 GB`; `Opt350 loss=0.433 lr=7.000e-05 itps=0.347 peak=82.620 GB`; `Opt360 loss=0.507 lr=6.826e-05 itps=0.285 peak=82.620 GB`; `Opt370 loss=0.435 lr=6.649e-05 itps=0.329 peak=82.620 GB`; `Opt380 loss=0.393 lr=6.469e-05 itps=0.414 peak=82.620 GB`; `Opt390 loss=0.480 lr=6.288e-05 itps=0.402 peak=82.620 GB`; `Opt400 loss=0.436 lr=6.105e-05 itps=0.400 peak=82.620 GB`; `Opt410 loss=0.447 lr=5.920e-05 itps=0.409 peak=82.620 GB`; `Opt420 loss=0.414 lr=5.734e-05 itps=0.410 peak=82.620 GB`; `Opt430 loss=0.389 lr=5.546e-05 itps=0.408 peak=82.620 GB`; `Opt440 loss=0.353 lr=5.358e-05 itps=0.399 peak=82.620 GB`; `Opt450 loss=0.352 lr=5.170e-05 itps=0.401 peak=82.620 GB`; `Opt460 loss=0.370 lr=4.981e-05 itps=0.413 peak=82.620 GB`; `Opt470 loss=0.379 lr=4.792e-05 itps=0.407 peak=82.620 GB`; `Opt480 loss=0.360 lr=4.604e-05 itps=0.415 peak=82.620 GB`; `Opt490 loss=0.345 lr=4.416e-05 itps=0.412 peak=82.620 GB`; `Opt500 loss=0.337 lr=4.229e-05 itps=0.390 peak=82.620 GB`; `Opt510 loss=0.274 lr=4.043e-05 itps=0.423 peak=82.620 GB` | running | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_stage1_broad_v3f_union/prepare_manifest.json` |

- single-file MLX trainer `baseline_mlx/reproduce_nemotron_sft_lora_with_cot_v2_mlx.py` に **`--lora-key-group`**, **`--trainable-lora-suffix-group`**, **`build-corrective-stage2-csv`**, **`build-leaderboard-proxy-v2`** を追加した。これにより **1 本の union adapter の中で broad / attention を段階切替**できる状態になった。
- broad stage の abstract plan (`in/out/up/down`) は、Nemotron MLX 実機では **`mixer.in_proj`, `mixer.out_proj`, `mixer.switch_mlp.fc1`, `mixer.switch_mlp.fc2`, `mixer.shared_experts.up_proj`, `mixer.shared_experts.down_proj`** に写像した。attention stage は **`mixer.q_proj`, `mixer.k_proj`, `mixer.v_proj`, `mixer.o_proj`** を使う。
- 1-step smoke (`stage_union_broad_tiny_train_v1`) で broad filter の動作を先に確認した。`Iter1 val=1.242`, `Iter1 train_loss=1.239`, `Opt1`, `Peak mem 75.072 GB` まで通り、**base weight を開かず LoRA だけ broad suffix に絞れる**ことを確認した。
- Stage 2 corrective dataset は **`baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_artifacts/stage2_corrective_v1.csv`** として生成した。構成は **`218 rows = binary verified 209 + symbol numeric_2x2 9 + answer_only 0`**。binary solver 内訳は **`affine_xor 54`, `bit_permutation_bijection 30`, `structured_byte_formula 49`, `structured_byte_formula_abstract 51`, `structured_byte_not_formula 25`**。
- hidden-gap watch 用の `leaderboard_proxy_v2` は **`baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_artifacts/leaderboard_proxy_v2.csv`** として生成した。構成は **`84 rows = binary 73 + symbol 11`**。source 内訳は **`leaderboard_proxy_v1_focus 55`, `binary_hard_topup 18`, `symbol_numeric_watch 11`**。
- Stage1 broad trunk は **`notebook-current` broad CSV** を使い、README 契約 (`rank<=32`, single adapter) を維持したまま **union 10 keys** (`broad 6 + attention 4`) を初期化している。初期 report は **`Iter 1: Val loss 1.677 (0.953s)`**、その後 **`Opt40 loss=0.558 / It/sec 0.711`**, **`Opt50 loss=0.779 / LR 9.998e-05 / It/sec 0.756 / Peak mem 81.208 GB`**, **`Opt80 loss=0.811 / It/sec 0.745`**, **`Opt100 loss=0.710 / LR 9.885e-05 / It/sec 0.742 / Peak mem 81.954 GB`**, **`Opt110 loss=0.701 / LR 9.841e-05 / It/sec 0.742`**, **`Opt190 loss=0.539 / LR 9.249e-05 / It/sec 0.742`** まで進み、throughput は baseline fullrun v2 と同じ帯を維持している。現状は speed degradation や OOM の兆候は見えておらず、以後はこの速度帯が崩れないかと easy family drift を監視して Stage2 へ進める。
- detached waiter (`shellId 248`) を追加し、Stage1 の `training_result.json` が出たら **`nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_stage2_attention_qkvo_lr2e5_len1536`** を自動起動するようにした。Stage2 は **`resume=Stage1 adapters.safetensors`**, **`train_csv=stage2_corrective_v1.csv`**, **`type_sample=Bit209 / Eq9 / others0`**, **`lr=2e-5`**, **`max_seq_length=1536`**, **`trainable=attention(q/k/v/o)`** で実行される。
- Stage2 後の判定用に、single-file trainer へ **`eval-benchmark-csv`** と **`eval-benchmark-suite`** を追加した。`eval-benchmark-suite` は **reference `general_stable_set.csv` + `binary_hard_set.csv` + `symbol_watch_set.csv` を結合した README local320** を 1 回の MLX model load で採点し、同じ run のまま **`leaderboard_proxy_v2.csv`** と **`binary_bias_specialized_set.csv (563 rows)`** も追加評価できる。suite waiter は **`eval_suite_readme_proxy_specialized`** として detached で待機しており、Stage2 完了後に **local320 / general,binary,symbol 内訳 / proxy v2 / specialized563** を順次吐く構成に差し替えた。
- main lane の次段として、detached ablation waiters を追加した。順序は **main `q/k/v/o lr=2e-5` → eval suite → `v/o` only (`lr=2e-5`, `epochs=3.6`) → eval suite → `q/k/v/o lr=1e-5, epochs=2.4` → eval suite** で、いずれも Stage1 broad adapter を共通 resume 元に使う。これにより user 指示どおり、長時間 train の待ち時間を **次の実験へ自動連結**する形にした。
- single-file trainer へ **`audit-submission-compat`** command を追加した。既存の `baseline-mlx-notebook-original-fullrun-v2` adapter で probe した結果は **`2D tensors = 184`, `3D tensors = 92`**, status **`blocked_routed_expert_3d_tensors`** だった。block reason は **`switch_mlp` routed-expert tensor が 3D のため、現時点では PEFT/vLLM 等価 export を推測で作らず止める** というもの。main / `v/o` / low-LR-short の各 lane についても、eval suite 完了後に同 audit を自動で残す waiter を追加済みである。

## Stage freeze/unfreeze v2 export-safe

| version | run_name | train_csv | sampled_rows | total_iters | optimizer_steps | measured | status | artifacts |
| --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |
| `baseline-mlx-stagefreeze-v2-exportsafe-smoke` | `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_exportsafe_smoke` | `baseline/nemotron-sft-lora-with-cot-v2/artifacts/train_split_with_cot_v3f_safe_plus_notformula.csv` | `6` | `1` | `1` | `audit_status=potentially_exportable_2d_only`; `tensor_rank_counts=[2:184]` | completed | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_exportsafe_smoke/submission_compat_audit/submission_compat_audit.json` |
| `baseline-mlx-stagefreeze-v2-exportsafe-resume-smoke` | `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_exportsafe_resume_smoke` | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_artifacts/stage2_corrective_v1.csv` | `2` | `1` | `1` | `saved tensors=232`; `attention_tensors=48`; `audit_status=potentially_exportable_2d_only`; `submission.zip validation_valid=true` | completed | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_exportsafe_resume_smoke/submission_export/export_manifest.json` |
| `baseline-mlx-stagefreeze-v2-stage1-broad-launch` | `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage1_broad_exportsafe_v3f_union` | `baseline/nemotron-sft-lora-with-cot-v2/artifacts/train_split_with_cot_v3f_safe_plus_notformula.csv` | `3321` | `6642` | `832` | `Iter1 val=1.677`; `Opt10 loss=1.023 lr=2.195e-05 itps=0.488 peak=66.776 GB`; `Opt20 loss=0.532 lr=4.634e-05 itps=0.504 peak=67.104 GB`; `Opt30 loss=0.480 lr=7.073e-05 itps=0.512 peak=67.104 GB`; `Opt40 loss=0.486 lr=9.512e-05 itps=0.510 peak=67.104 GB`; `Opt50 loss=0.531 lr=9.998e-05 itps=0.539 peak=67.104 GB`; `Opt60 loss=0.477 lr=9.990e-05 itps=0.514 peak=67.842 GB`; `Opt70 loss=0.580 lr=9.974e-05 itps=0.503 peak=67.842 GB`; `Opt80 loss=0.793 lr=9.951e-05 itps=0.533 peak=67.842 GB`; `Opt90 loss=0.534 lr=9.921e-05 itps=0.519 peak=67.842 GB`; `Opt100 loss=0.516 lr=9.885e-05 itps=0.524 peak=67.842 GB`; `Opt110 loss=0.528 lr=9.841e-05 itps=0.527 peak=67.842 GB`; `Opt120 loss=0.461 lr=9.790e-05 itps=0.546 peak=67.842 GB`; `Opt130 loss=0.493 lr=9.733e-05 itps=0.519 peak=67.842 GB`; `Opt140 loss=0.396 lr=9.668e-05 itps=0.530 peak=67.842 GB`; `Opt150 loss=0.425 lr=9.597e-05 itps=0.524 peak=67.842 GB`; `Opt160 loss=0.478 lr=9.520e-05 itps=0.540 peak=67.842 GB`; `Opt170 loss=0.435 lr=9.436e-05 itps=0.470 peak=67.842 GB`; `Opt180 loss=0.399 lr=9.346e-05 itps=0.345 peak=67.842 GB`; `Opt190 loss=0.395 lr=9.249e-05 itps=0.346 peak=67.842 GB`; `Opt200 loss=0.446 lr=9.147e-05 itps=0.498 peak=67.842 GB`; `Opt210 loss=0.441 lr=9.038e-05 itps=0.498 peak=67.842 GB`; `Opt220 loss=0.442 lr=8.924e-05 itps=0.513 peak=68.597 GB`; `Opt230 loss=0.395 lr=8.804e-05 itps=0.529 peak=68.597 GB`; `Opt240 loss=0.375 lr=8.679e-05 itps=0.519 peak=68.597 GB`; `Opt250 loss=0.361 lr=8.549e-05 itps=0.527 peak=68.597 GB`; `Opt260 loss=0.388 lr=8.413e-05 itps=0.535 peak=68.597 GB`; `Opt270 loss=0.379 lr=8.273e-05 itps=0.508 peak=68.597 GB`; `Opt280 loss=0.453 lr=8.128e-05 itps=0.525 peak=68.597 GB`; `Opt290 loss=0.383 lr=7.978e-05 itps=0.518 peak=68.597 GB`; `Opt300 loss=0.386 lr=7.825e-05 itps=0.512 peak=68.597 GB`; `Opt310 loss=0.424 lr=7.667e-05 itps=0.524 peak=68.597 GB`; `Opt320 loss=0.355 lr=7.505e-05 itps=0.514 peak=68.597 GB`; `Opt330 loss=0.418 lr=7.340e-05 itps=0.541 peak=68.597 GB`; `Opt340 loss=0.327 lr=7.172e-05 itps=0.517 peak=68.597 GB`; `Opt350 loss=0.385 lr=7.000e-05 itps=0.512 peak=68.597 GB`; `Opt360 loss=0.452 lr=6.826e-05 itps=0.517 peak=68.597 GB`; `Opt370 loss=0.385 lr=6.649e-05 itps=0.530 peak=68.597 GB` | running | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage1_broad_exportsafe_v3f_union/console.log` |

- stage-freeze 実装の保存 bug を特定した。`mlx_lm.tuner.trainer.train()` が checkpoint/final save で **`model.trainable_parameters()` だけ**を書いていたため、Stage2 で broad suffix を freeze すると final `adapters.safetensors` から broad LoRA が脱落していた。single-file trainer 側を patch し、save 時は **`model.named_modules()` から全 `lora_a/lora_b` tensor を回収**する方式に切り替えた。
- この patch を export-safe resume smoke で再検証した。Stage1 broad-only adapter (`184 tensors`) を resume 元に、`stage-union-exportsafe` + `trainable=attention` で 1-step Stage2 smoke を回したところ、final adapter は **`232 tensors = mamba 92 + shared_experts 92 + attention 48`** となり、**frozen broad と新規 attention が同時に保持**された。
- さらに single-file trainer に **`export-peft-submission`** command を追加し、2D-only MLX adapter を conservative に PEFT `adapter_model.safetensors` へ変換できるようにした。検証は **meta-device Nemotron + PEFT reference state_dict** を使い、**key set / tensor shape を完全一致**で照合している。
- `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_exportsafe_resume_smoke` では `audit-submission-compat` が **`potentially_exportable_2d_only`** を返し、そのまま `export-peft-submission` で **README 提出形式の `submission.zip`** (`adapter_config.json`, `adapter_model.safetensors`) を生成できた。現時点で **single-file MLX から submission 互換 bundle を structurally 作れる 2D-only lane** は成立した。
- 一方で export-safe full Stage1 を main Stage1 と並列で起動した結果、main Stage1 broad は **`Opt210 0.694 it/s` → `Opt220 0.514` → `Opt230 0.418` → `Opt240 0.403`** まで落ちた。export-safe Stage1 自身も **`~0.49-0.51 it/s`** 帯で推移しており、**30B dual-train contention が throughput を大きく削る**ことが実測で見えた。以後の full-train 並列数は score 回収速度とのトレードオフとして扱う。
- single-file trainer に **`record-run-result`** command を追加した。これは `prepare_manifest.json`, `training_result.json`, `eval_suite_readme_proxy_specialized/benchmark_eval_suite_summary.json`, `submission_compat_audit.json`, `submission_export/export_manifest.json` を読み、**`versions/baseline_mlx/baseline_mlx-results.md` に run ごとの auto summary block を idempotent に追記/更新**する。
- detached ledger/git waiters も追加済み。対象は **main qkvo**, **`v/o` only**, **low-LR-short**, **export-safe qkvo** の 4 lane で、各 run は **suite + audit (export-safe は export まで)** が揃ったら `record-run-result` を実行し、そのまま **`results.md` を commit/push** する。これにより score 回収後の Git 可視化を manual follow-up なしで継続できる。
- single-file trainer に **`package-best-submission`** command も追加した。これは README 契約の **`submission.zip` / rank<=32 / adapter_config.json 必須**を gate として、completed run 群から **exportable かつ local320 が baseline (`215/320`) を超える候補**を自動選抜し、canonical output root に `submission.zip` を昇格させる。
- detached best-candidate waiter (`shellId 316`) も起動済み。`baseline_mlx/outputs` を巡回し、**`min_local320_accuracy=0.671875`**, **`min_general_stable_accuracy=0.96`**, **`require_exportable=true`** を満たす run が出たら `baseline_mlx/outputs/best_submission_candidate_auto/` に昇格し、同時に **`results.md` の best-submission block を commit/push** する。
- export-safe lane の ablation chain も main lane と揃えた。detached chain waiters (`shellId 320`, `321`) は **export-safe qkvo → export-safe `v/o` → export-safe qkvo low-LR-short** を順に train し、それぞれで **suite → submission audit → PEFT export → `record-run-result` → commit/push** まで自動連結する。これで exportable candidate は qkvo 1 本に固定されず、README 提出可能な比較軸を 3 本へ増やした。
- single-file trainer に **JSONL progress callback** も追加した。`mlx_lm.lora.run()` が内部で callback 引数を上書きする挙動を利用し、`get_reporting_callbacks()` を wrap して **`adapter/train_report.jsonl`**, **`adapter/val_report.jsonl`**, **`adapter/latest_train_report.json`**, **`adapter/latest_val_report.json`** を常時出す。1-step smoke `nemotron_sft_lora_with_cot_v2_mlx_progress_callback_smoke` で生成を確認した。
- この progress callback により、**これから起動する Stage2 / export-safe ablation / future runs** は final save 前でも file artifact から optimizer step と latest loss/memory を追える。なお、すでに起動済みの Stage1 broad 2 本には retroactive には効かない。
- `baseline_mlx/outputs/best_submission_candidate_auto/selection_manifest.json` は継続更新中で、現時点の status は **`no_eligible_candidate`**。つまり best-submission poller 自体は動いており、まだ **`local320 > 215/320` かつ exportable** な run が出ていないことが確認できている。
- その後の live 点検で、古い detached shell waiter 群に **`trap "rmdir "`** という lock cleanup の quoting 崩れが残っていること、および旧 best-candidate poller の inline Python 判定が壊れていることを確認した。train 本体には手を触れず、**record/push waiter を safe cleanup 版へ差し替え**、best-candidate 側は **session script 化した poller** へ移した。これにより、長時間 train 完了後の **`record-run-result` → git commit/push** と best candidate 昇格の自動連結を復旧した。
- さらに poller の内側リダイレクトが `uv run python` の stdio 初期化と衝突し、`Bad file descriptor` を出していたため、session script 側を修正して再起動した。修正後は **`selection_manifest.json` が 2026-04-09 10:11:06 に更新**され、script-based poller が **継続ポーリングできている**ことを確認した。safe waiter 群は自前 cleanup を持つため、aggressive stale-lock janitor は停止した。

## Direct corrective from baseline fullrun v2

| version | run_name | resume_from | train_csv | total_iters | optimizer_steps | measured | status | artifacts |
| --- | --- | --- | --- | ---: | ---: | --- | --- | --- |
| `baseline-mlx-direct-fullrun-v2-qkvo-launch` | `nemotron_sft_lora_with_cot_v2_mlx_direct_from_fullrun_v2_stage2_attention_qkvo_lr2e5_len1536` | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_notebook_original_fullrun_v2/adapter/adapters.safetensors` | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_artifacts/stage2_corrective_v1.csv` | `784` | `98` | `Iter1 val=1.606`; `Opt10 loss=0.998 lr=1.996e-05 itps=0.335 peak=68.315 GB`; `Opt20 loss=0.426 lr=1.919e-05 itps=0.336 peak=69.297 GB`; `trainable=3.736M`; `attention=q/k/v/o only` | stopped for RAM pressure | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_direct_from_fullrun_v2_stage2_attention_qkvo_lr2e5_len1536/console.log` |

- この lane は **Stage1 broad の完走待ちをバイパス**して、現時点の MLX best **`baseline_mlx_notebook_original_fullrun_v2 = 215/320 = 0.6719`** を trunk とし、その上に **attention-only corrective** を直差しする即応実験として追加した。
- 設定は **`stage-union`**, **`resume=fullrun_v2 adapters.safetensors`**, **`trainable=attention(q/k/v/o)`**, **`lr=2e-5`**, **`max_seq_length=1536`**, **`train_csv=stage2_corrective_v1.csv (218 rows)`**。起動時点では **`LoRA suffix filter = 24 modules`**, **`Trainable parameters = 3.736M`**, **`Iter1 val_loss = 1.606`** を確認した。
- この resume 元は `switch_mlp` routed-expert の **3D tensor** を含むため、**この direct lane 自体は submission 互換 lane ではない**。役割はまず **「attention corrective が baseline trunk を上積みできるか」**を stagefreeze 本線より早く読むことにある。
- 完走後は detached waiter で **`eval-benchmark-suite` → `audit-submission-compat` → `record-run-result` → `results.md` commit/push** まで自動連結してある。
- direct lane も 1 本で止めず、**`qkvo lr=2e-5` → `v/o lr=2e-5` → `qkvo lr=1e-5, epochs=2.4`** の順に ablation を回す detached waiters を追加した。いずれも **resume 元は同じ `baseline_mlx_notebook_original_fullrun_v2` adapter** に固定し、各 run ごとに **suite → audit → record-run-result → commit/push** まで自動連結する。
- Stagefreeze 側を **`v/o lr2e-5` + `qkvo lr1e-5 short`** の 2 本へ切り替えた時点でも **`PhysMem 381-382G used / 129-130G unused`** を維持できたので、direct family も waiter 解放を待たず **`nemotron_sft_lora_with_cot_v2_mlx_direct_from_fullrun_v2_stage2_attention_vo_lr2e5_len1536`** を手動前倒し起動した。新 run は `prepare_manifest.json` / `runtime_preflight.json` を生成し、**`current_pid=90194`**, `system_free_memory=62%`, `gpu_device_util=100%`, trainable suffix は **`mixer.v_proj/o_proj`**, trainable params は **`1.868M`**, 初回 validation は **`Iter 1: Val loss 1.606`**。これで current search は **3 lane (`stagefreeze vo`, `stagefreeze short`, `direct fullrun_v2 vo`)** になった。
- ただし direct family は manual prelaunch のぶん auto chain が未接続だったため、**`direct vo` 向け `postprocess-run`** と **`direct vo suite -> direct short` の `wait-resume-train-from-path`**, さらに **`direct short` 向け `postprocess-run`** を single-file CLI で reattach した。これで direct 側も **train -> suite/audit/record -> (short launch) -> suite/audit/record** の流れが復旧した。
- ただし 3 本同時 train による RAM 圧迫が強く、ユーザー指示で **direct lane 一式（train 本体 + direct waiters）を停止**した。停止直前の最終観測は **`Opt20 loss=0.426 / itps=0.336 / peak=69.297 GB`**。`training_result.json` は未生成のため、この lane は **launch probe まで**として扱う。
- prune 後の定点では、repo 配下の live 実体は **main broad train 1 本 + export-safe broad train 1 本 + 各 resource_tracker** に整理された。`top` snapshot では **`PhysMem: 414G used, 97G unused`** まで戻っており、background count が大きく見えても **重い実プロセスは 2 本だけ**であることを確認した。
- safe cleanup 版へ差し替えた waiter は現在 **8 本 live**、best-candidate 側も session script `best_submission_poller.sh` で稼働中で、`selection_manifest.json` は **2026-04-09 10:19:10** 更新を確認した。したがって現状は **train 2 本 + safe waiter/poller** の構成で、Stage1 完走後に Stage2 / suite / audit / export / ledger 更新まで自動で流せる状態に戻っている。
- RAM 圧迫下でも train 本体に手を入れず次の自動化を進めるため、single-file trainer に **`wait-for-path`**, **`resume-train-from-run`**, **`wait-train-from-run`**, **`postprocess-run`** を追加した。これにより、**Stage1 完走待ち → Stage2 起動** と **run 完了後の suite / audit / export / record / candidate packaging** を、quoting に弱い detached bash one-liner ではなく **Git 管理下の 1 ファイル Python CLI** で再現できるようになった。現行の live waiter はそのまま維持しつつ、次回以降の lane はより安全に single-file 側へ寄せられる。
- その後、同 automation を **completed run (`baseline_mlx_notebook_original_fullrun_v2`) に対する dry-run** で検証し、`resume-train-from-run` / `wait-train-from-run` / `postprocess-run` が **モデル非ロード**のまま source shadow_model / adapter 解決、artifact 相対 path 解決、postprocess manifest 生成まで通ることを確認した。合わせて **`skip-if-target-started`** を追加し、dry-run manifest 自体を marker として扱うことで **同一 target run の二重起動を抑止**できるようにした。
- さらに `baseline_mlx/tests/test_single_file_stage_waiters.py` を追加し、single-file waiter automation について **`resolve_source_run_resume_paths`**, **dry-run の wait/resume manifest 生成**, **duplicate-skip**, **`postprocess-run --dry-run` summary** を unit test 化した。`uv run pytest baseline_mlx/tests/test_single_file_stage_waiters.py -q` は **4 passed** で、今回追加した lightweight automation がモデル非ロードの範囲で回帰していないことを確認した。
- 続けて同 test file に **`package-best-submission`** の synthetic candidate 選抜ケースを追加し、**best exportable candidate の選択 / canonical `submission.zip` copy / no-eligible fallback** を README gate 相当で検証した。`uv run pytest baseline_mlx/tests/test_single_file_stage_waiters.py -q` は **6 passed** となり、single-file automation だけでなく **best single adapter 選抜**の軽量回帰も押さえられた。
- 直近の定点では main broad は **Opt510**, export-safe broad は **Opt370** まで前進し、2 本とも throughput の大崩れなく継続している。一方で system snapshot は **`PhysMem: 465G used, 46G unused`** まで上がっており、今後も **新しい heavy train/eval を増やさず** 現行 2 本の完走を優先する運用が妥当と判断した。
- single-file automation をさらに前進させ、**`wait-resume-train-from-path`** command を追加した。これは **任意の trigger path（例: `.../eval_suite_readme_proxy_specialized/benchmark_eval_suite_summary.json`）を待ってから、source run の `shadow_model` / `adapters.safetensors` を解決して resumed train を起動する**ためのもので、従来の **main qkvo suite 完了→`v/o` 起動** / **`v/o` suite 完了→short 起動** のような shell waiter を single-file CLI で表現できる。
- 同 test file に **`wait-resume-train-from-path` の dry-run / duplicate-skip** を追加し、`uv run pytest baseline_mlx/tests/test_single_file_stage_waiters.py -q` は **8 passed** へ拡張した。合わせて `uv run python baseline_mlx/reproduce_nemotron_sft_lora_with_cot_v2_mlx.py wait-resume-train-from-path --help` も通し、parser wiring まで確認した。
- 最新の live progress は main broad **Opt540** (`loss=0.377`, `lr=3.494e-05`, `it/sec=0.401`, `peak=82.620 GB`) 、export-safe broad **Opt410** (`loss=0.404`, `lr=5.920e-05`, `it/sec=0.518`, `peak=68.597 GB`)。同時点の system snapshot は **`PhysMem: 472G used, 39G unused`** で、依然として **新しい heavy train/eval は増やさず**、live waiter の本番 cutover も **現行 2 本完走を優先して保留**とした。
- 続けて single-file automation の postprocess 側も harden した。`postprocess-run` に **`--skip-existing-steps/--no-skip-existing-steps`** を追加し、既存の `benchmark_eval_suite_summary.json` / `submission_compat_audit.json` / `export_manifest.json` / `recorded_run_result.json` が揃っている completed run では、**eval / audit / export / ledger record を再実行せず `skipped_existing` として処理を完了**できるようにした。重い completed run に対する replay や live waiter cutover 時の duplicate work を避けるため、default も safe 側 (`skip_existing_steps=true`) に寄せている。
- `baseline_mlx/tests/test_single_file_stage_waiters.py` にはこの **postprocess skip-existing** 回帰も追加し、completed synthetic run 上で **既存 artifact があると pipeline helper を再呼び出さない**ことを検証した。`uv run pytest baseline_mlx/tests/test_single_file_stage_waiters.py -q` は **9 passed**、`uv run python -m py_compile baseline_mlx/reproduce_nemotron_sft_lora_with_cot_v2_mlx.py` も通過、`postprocess-run --help` には `--skip-existing-steps` が露出していることを確認した。
- 最新の live progress は main broad **Opt550** (`loss=0.381`, `lr=3.316e-05`, `it/sec=0.415`, `peak=82.620 GB`) 、export-safe broad **Opt430** (`loss=0.355`, `lr=5.546e-05`, `it/sec=0.524`, `peak=68.597 GB`)。best candidate poller の `selection_manifest.json` は **2026-04-09T01:55:26Z** 時点で依然 **`no_eligible_candidate`**、system snapshot は引き続き **`PhysMem: 472G used, 39G unused`** だった。
- さらに single-file trainer に **`publish-results-md`** command を追加し、`results.md` の **git add → shared lock 取得 → commit → push** を Python 側で完結できるようにした。`postprocess-run` にも **`--run-publish-results-md`** と publish 関連 option を追加してあるため、将来は **wait / eval / audit / export / record / package / git publish** を 1 ファイル CLI だけで連結できる。
- この publish helper は temp git repo test で回帰を押さえた。`baseline_mlx/tests/test_single_file_stage_waiters.py` には **modified `results.md` を local commit できるケース** と **差分ゼロで `no_changes` を返すケース** を追加し、targeted pytest は **11 passed** へ拡張した。`publish-results-md --help` と `postprocess-run --help` の publish option も smoke で通過している。
- 最新の live progress は main broad **Opt570** (`loss=0.362`, `lr=2.965e-05`, `it/sec=0.398`, `peak=82.620 GB`) 、export-safe broad **Opt450** (`loss=0.324`, `lr=5.170e-05`, `it/sec=0.500`, `peak=68.597 GB`)。best candidate poller の `selection_manifest.json` は **2026-04-09T02:00:28Z** 時点でも **`no_eligible_candidate`** 継続、system snapshot は **`PhysMem: 474G used, 36G unused`** まで上がっているため、引き続き **新しい heavy train/eval は増やさない**。
- この時点で live stage1 completion waiters も一部 cutover した。従来の shell-based safe waiter **`85169` / `85170`** を停止し、代わりに detached single-file CLI **`postprocess-run --wait-for-training-result --no-run-eval-suite --no-run-audit-submission --no-run-export-submission --run-record-run-result --run-publish-results-md`** を **main stage1 / export-safe stage1** に対して起動した。これにより少なくとも Stage1 完了時の **record + git publish** は、long-lived shell loop ではなく single-file Python waiter で処理できる状態に入った。
- best candidate 側にも single-file 化を進め、**`poll-best-submission`** command を追加した。これは **`package-best-submission` を loop 実行し、eligible candidate 発見時だけ `publish-results-md` を呼ぶ** poller で、従来の `best_submission_poller.sh` が担っていた **selection_manifest 更新 → best-submission block 更新 → git publish** の責務を 1 ファイル CLI に寄せるためのもの。
- `baseline_mlx/tests/test_single_file_stage_waiters.py` には **temp git repo + synthetic candidate run** での poller 回帰も追加し、**candidate 選抜 → results.md commit** までを end-to-end に検証した。targeted pytest は **12 passed**、`poll-best-submission --help` も smoke で通過している。
- live best-candidate poller も shell script から cutover した。旧 `best_submission_poller.sh` (`88012` / `88013`) を停止し、代わりに detached single-file CLI **`poll-best-submission --output-root baseline_mlx/outputs/best_submission_candidate_auto --min-local320-accuracy 0.671875 --min-general-stable-accuracy 0.96 --publish-commit-message "Promote best submission candidate"`** を起動した（proc tree: `16515-16517`）。cutover 直後の `selection_manifest.json` は **2026-04-09T02:07:46Z / `no_eligible_candidate`**、`poll_best_submission_summary.json` は **`status=running`** を示しており、single-file poller への置換後も監視が継続している。
- 続けて live Stage2 chain も main / export-safe の両 lane で shell waiter から切り替えた。main 側では **`wait-train-from-run` + `postprocess-run` + `wait-resume-train-from-path`** の detached single-file waiters 6 本へ置換し、export-safe 側も同型の detached single-file waiters 6 本へ置換した。これにより、**Stage1 完了待ち → qkvo train → suite/audit(/export) → record/publish → vo train → short train** の連結は、現時点の live process でもほぼ single-file Python CLI へ寄った。
- cutover 後の各 Stage2 run root にはすでに **`postprocess_manifest.json`** が生成されており、旧 shell waiters (`57936`, `61865`, `64320`, `64307`, `64319`, `64308`, `64926`, `64928`, `64927`, `85171-85176`, `67581`, `67573`, `67519`, `70849`) は終了済みであることを確認した。最新 snapshot は **`PhysMem: 476G used, 35G unused`** で、依然として **新しい heavy train/eval は追加せず**、既存 broad 2 本の完走待ちを優先する。
- その後の live progress では、main broad `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_stage1_broad_v3f_union` が **Opt620** (`loss=0.329`, `lr=2.144e-05`, `it/sec=0.404`, `peak=82.620 GB`) まで前進し、export-safe broad `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage1_broad_exportsafe_v3f_union` も **Opt510** (`loss=0.252`, `lr=4.043e-05`, `it/sec=0.538`, `peak=68.597 GB`) まで進んだ。両 run とも `prepare_manifest.json` が示す **total_optimizer_steps=832** に対してまだ Stage1 継続中で、`training_result.json` と Stage2 qkvo の `prepare_manifest.json` は未生成だった。
- README 契約ベースの best-submission 自動昇格も継続監視中だが、`baseline_mlx/outputs/best_submission_candidate_auto/selection_manifest.json` は **2026-04-09T02:43:46Z** 時点でも依然 **`candidate_count=0` / `eligible_candidate_count=0` / `status=no_eligible_candidate`**。つまり、現時点では **README 提出互換かつ local320 / general_stable gate を満たす scored run がまだ 1 本も揃っていない**。初期の最新 system snapshot は **`PhysMem: 475G used, 35G unused`** で、方針は引き続き **新しい heavy train/eval を足さず broad run の完走を待つ**。
- broad 2 本の完走待ち時間を遊ばせないため、single-file trainer に **`record-live-run-status`** と **`poll-live-run-status`** を追加した。`adapter/latest_train_report.json` がある run はそれを一次ソースに、無ければ **`console.log` の末尾 train progress 行**を parse して、**Git 管理下の `versions/baseline_mlx/baseline_mlx-results.md` に live progress block を upsert** できる。`poll-live-run-status` は progress signature が変わったときだけ `publish-results-md` を呼ぶため、in-flight run の進捗を **single-file CLI だけで commit/push** できる。
- `baseline_mlx/tests/test_single_file_stage_waiters.py` には **latest JSON 優先**, **console.log fallback**, **poll + git commit**, さらに **dead PID を stale `training` と誤認しない stopped 判定** の回帰を追加した。qkvo suite stall の修正では、`evaluate_benchmark_rows()` の benchmark fallback で未定義変数を踏まない regression も足し、targeted pytest は **17 passed**、`record-live-run-status --help` / `poll-live-run-status --help` / `py_compile` も通過。注意点として、**main broad は既存 shell session (`shellId 240`) 側の stdout に progress があり run root には `console.log` / `latest_train_report.json` が無いため、現時点の live progress 自動記録は export-safe broad と今後の stage2/future runs で特に有効**である。
- ただし RAM 圧迫が強すぎたため、ユーザー判断に従って **export-safe broad lane は後ろ倒し**にした。最長 ETA 側だった `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage1_broad_exportsafe_v3f_union` を **最終観測 Opt580 / Iter4633** で停止し、関連する **stage1 completion waiter / stage2 train waiters / stage2 postprocess waiters / live progress poller** も停止した。system snapshot は停止前が **`PhysMem: 475G used, 35G unused`**、停止後が **`PhysMem: 280G used, 230G unused`**、その後ユーザー観測でも **266.63 / 512.0 GB** まで低下しており、**2 本目の 30B MLX 学習 lane の増分コストは概ね 190-200GB 級の unified memory** だったと見てよい。これは trainer の `Peak mem 68.597 GB` 行とは別物で、モデル複製・optimizer/state・Metal の wired/unified memory pool まで含んだ **システム全体差分**である。
- lane 停止後は main broad が即座に加速した。`shellId 240` の live stdout では **Opt680 で `it/sec=0.664`、Opt690 で `it/sec=0.746`** まで回復しており、dual-train contention が main broad の後半 throughput を強く削っていたことも確認できた。一方、止めた export-safe run root には **`prepare_manifest.json` / `runtime_preflight.json` / `adapter/adapter_config.json` しか残っておらず、`training_result.json` や `adapters.safetensors` は未生成**だったため、後日再開する場合は **途中再開ではなく full rerun** が前提になる。
- そのまま main broad を単騎で継続監視すると、**Opt700 / Opt710 / Opt720** でそれぞれ `it/sec=0.769 / 0.736 / 0.758`、`loss=0.344 / 0.354 / 0.293` まで進み、学習末尾の throughput はほぼ初期 single-lane 水準へ戻った。最新 snapshot でも **`PhysMem: 286G used, 225G unused`** と headroom は維持されており、同時点では `training_result.json` も main Stage2 qkvo の `prepare_manifest.json` もまだ無いため、**main は依然 Stage1 継続中**である。
- その後 main broad は完走し、`nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_stage2_attention_qkvo_lr2e5_len1536` が自動起動して **Opt101 / Iter784 / loss=0.187084 / lr=2.361e-07 / it/sec=0.858648 / peak=70.926 GB** で train 完了した。ただし最初の detached `postprocess-run` は **`NameError: name 'benchmark_csv' is not defined`** で suite 前に落ちており、症状としては **`training_result.json` だけあるのに suite/audit/result file が増えず、RAM も低いまま**に見えた。
- root cause は single-file evaluator `evaluate_benchmark_rows()` が `benchmark_name` の fallback に **存在しない `benchmark_csv.stem`** を参照していたことだった。これを **`evaluation_name` fallback** へ直し、regression test を追加したうえで qkvo postprocess を再投入したので、現在は **README scoring semantics (`accuracy`, `\boxed{}` 優先抽出, `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_model_len=8192`) に寄せた local proxy suite** が再実行されている。
- qkvo rerun はもう「止まって見えるだけ」ではない。per-benchmark artifact が途中まで出ており、`readme_local320` は **`113/320 = 0.3531`**（`general_stable 88/200`, `binary_hard 19/60`, `symbol_watch 6/60`）、`leaderboard_proxy_v2` は **`30/84 = 0.3571`**（`binary 27/73`, `symbol 3/11`）で完了済みだった。これは tracked MLX baseline **`215/320 = 0.6719`** を大きく下回るため、main **`attention_qkvo lr2e-5`** lane は trailing `binary_bias_specialized_set` がまだ回っていても **submission candidate としては dead** と判断してよい。
- なお、この local suite は **README 本番そのものではなく proxy** である点を明示しておく。採点ロジックと decoding 条件の主軸は README に合わせているが、現在の MLX runner は **`max_num_seqs=8`** で回しており、README Evaluation page / vLLM 本番の **`max_num_seqs=64`** とは一致していない。したがってこの数値は leaderboard の代替ではなく、**lane の生死判定用 proxy** として扱う。
- suite 完了待ちで GPU を遊ばせないため、memory headroom が戻った時点で **`nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_stage2_attention_vo_lr2e5_len1536`** を broad Stage1 完走 root から手動前倒し起動した。新 run は直ちに `prepare_manifest.json` / `runtime_preflight.json` を生成し、**`current_pid=86512`**, `system_free_memory=85%`, `gpu_device_util=100%` を記録、LoRA trainable suffix は **`mixer.v_proj` / `mixer.o_proj` のみ**、trainable params は **`1.868M`**、初回 validation は **`Iter 1: Val loss 1.191`** で通っている。既存の `wait-resume-train-from-path` waiter は target-started marker を見て duplicate skip する想定で、そのまま残してある。
- qkvo main lane は dead が確定したので、rerun postprocess `PID 50695` はここで停止して specialized tail を打ち切った。停止直後の snapshot は **`PhysMem: 217G used, 293G unused`** まで戻っており、これで dead lane の eval に GPU/RAM を使い続ける状態は解消した。
- 空いた headroom をそのまま次の corrective ablation へ回し、**`nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_stage2_attention_qkvo_lr1e5_ep24_len1536`** も broad Stage1 完走 root から手動前倒し起動した。新 run は `prepare_manifest.json` / `runtime_preflight.json` を生成し、**`current_pid=88859`**, `system_free_memory=78%`, `gpu_device_util=99%`、trainable suffix は **`mixer.q_proj/k_proj/v_proj/o_proj`**, trainable params は **`3.736M`**, 初回 validation は **`Iter 1: Val loss 1.191`**。これで現在線は **`v/o lr2e-5` + `qkvo lr1e-5 short`** の 2 本に切り替わった。
- その後 `stagefreeze v1 vo` の old waiter log を読むと、ここでも crash は **現行コードの再発ではなく、fix 前に起動して生き残っていた stale `postprocess-run`** が古い `evaluate_benchmark_rows()` を保持していたことが原因だった。実際、`copilot-detached-489-1775700669391.log` には **`NameError: name 'benchmark_csv' is not defined`** が残っていたが、現行 source にはその参照は残っていない。`stagefreeze short` も同型 stale waiter だったため旧 process を止め、**`vo` / `short` の postprocess を current single-file code で fresh rerun** し直した。
- あわせて、手動前倒しで既に起動済みの lane に対して残っていた **`wait-resume-train-from-path` chain waiter** も整理した。`stagefreeze qkvo->vo`, `stagefreeze vo->short`, `direct vo->short` の古い leaf process は、このまま suite summary 生成後まで残すと **同じ output root へ duplicate resume を試みる** 余地があったため、ここで明示停止して manual prelaunch 側を正系に固定した。
- fresh rerun / direct family の postprocess についても「無出力のまま固まっている」のではなく、**実体は MLX/Metal の generate loop 上で active** だと確認した。`sample` を `direct vo` postprocess `PID 92814` と `stagefreeze vo` postprocess `PID 99167` に当てると、どちらも main thread が **`mlx::core::async_eval` → `mlx::core::gpu::eval` → `Matmul::eval_gpu` → AGX Metal compute** に張り付いており、`lsof` でも `mlx.metallib`, `libmlx.dylib`, `AGXMetalG15X_M2`, adapter/tokenizer/safetensors を開いたままになっていた。つまり現段階は **score recovery / proxy suite 実行中** であり、`eval_suite_readme_proxy_specialized` 以下にまだ file が無いのは「最初の benchmark 完了前」だからだと見るのが妥当。
- 参考までに、すでに dead 判定済みの **main qkvo lane** でこの proxy suite の所要時間を逆算すると、`training_result.json` から **`readme_local320` summary 出現まで `4546.1s ≒ 75.8 min`**、`leaderboard_proxy_v2` summary 出現まで **`5256.5s ≒ 87.6 min`** かかっていた。したがって、現行 `vo/short/direct` lane で **training 完了後 20-40 分程度 artifact 無し**は異常値ではなく、むしろ通常レンジの途中とみなすべき。
- 無出力時間が長いと status 判定が難しいため、single-file evaluator 側にも **suite progress 可視化**を追加した。`run_eval_benchmark_suite()` は以後 `benchmark_eval_suite_progress.json` と各 benchmark root の `benchmark_eval_progress.json` を更新し、`run_postprocess_run()` は `eval_suite` 実行前から **`postprocess_manifest.json` に `steps.eval_suite.status=running` と `progress_relpath`** を残す。回帰は `uv run pytest baseline_mlx/tests/test_single_file_stage_waiters.py -q` で **19 passed**、`py_compile` も通過。
- ただし 4 本同時 postprocess のままでは、`stagefreeze vo/short` が training 完了後 **~74 分** に達してもなお first `readme_local320` summary が出ておらず、GPU share の食い合いが単純な無出力待ち以上に効いていると判断した。ここで最も弱い **`direct fullrun_v2 short qkvo lr1e-5 ep2.4`** の postprocess (`PID 92813`, wrapper `92810/92811`) をいったん停止し、`training_result.json` / final adapter / `postprocess_manifest.json` は残したまま **後順位 lane** へ回した。停止後の snapshot は **`PhysMem: 342G used, 169G unused`**。以後は **`stagefreeze vo` / `stagefreeze short` / `direct vo`** の 3 lane へ GPU を寄せる。
- それでも 3 lane 同時では、`stagefreeze vo/short` が training 完了後 **~92 分**、`direct vo` も **~81 分** に達してなお first `readme_local320` summary が出なかった。ここでさらに **`stagefreeze short qkvo lr1e-5 ep2.4`** の postprocess (`PID 99168`, wrapper `99164/99166`) を停止し、やはり `training_result.json` / final adapter / `postprocess_manifest.json` を保持したまま **later rerun候補**へ移した。停止後は **`PhysMem: 259G used, 252G unused`** まで戻り、残った **`stagefreeze vo` / `direct vo`** の 2 worker はどちらも **~46% CPU** に上昇した。以後は最有力の **vo-only 2 lane** に score recovery を集中させる。
- さらに 2 lane でも、`stagefreeze vo` が training 完了後 **~108 分**、`direct vo` も **~97 分** で still no first summary だった。`stagefreeze` trunk は同じ broad root 由来の **main qkvo lane が 113/320 で dead** になっている一方、`direct vo` は **tracked MLX baseline 215/320 trunk** 由来なので、ここで `stagefreeze vo` postprocess (`PID 99167`, wrapper `99163/99165`) も停止し、**`direct fullrun_v2 -> attention-vo lr2e-5` 1 本**へ最終集中した。停止後 snapshot は **`PhysMem: 195G used, 316G unused`**、残りの `direct vo` worker (`PID 92814`) は **~62% CPU** まで上昇。`stagefreeze vo` も `training_result.json` / final adapter / `postprocess_manifest.json` は温存してあり、必要なら later rerun できる。
- ただし、この **old blind `direct vo` postprocess** も training 完了後 **109.2 分** まで `readme_local320` / `leaderboard_proxy_v2` / suite summary のいずれも出さず、進捗の可視化がないままでは lane quality と decode 長文化を切り分けられなかった。そこで旧 worker を停止し、同じ run root に対して **current single-file code の `postprocess-run`** を `direct-fullrun-v2-vo-rerun-progress` として再投入した。
- current-code rerun では、起動直後から **`postprocess_manifest.json`** に `steps.eval_suite.status=running` が記録され、suite root に **`benchmark_eval_suite_progress.json`**、`readme_local320` root に **`benchmark_eval_progress.json`** が生成された。初回観測 (`2026-04-09T08:37:51Z`) は **`readme_local320 0/320 rows, 0/40 chunks`**、約 4 分後 (`2026-04-09T08:41:51Z`) には **`16/320 rows, 2/40 chunks`** まで進んでいた。worker 本体 (`PID 31948`) は **`%CPU 52.5`**, snapshot は **`PhysMem: 210G used, 300G unused`**。これで少なくとも **progress manifest 自体は実運用で機能し、現 lane は blind hang ではなく chunk 単位で前進している**ことが確認できた。
- さらに `2026-04-09T08:58:08Z` 時点では、同 rerun の progress は **`80/320 rows, 10/40 chunks`** まで伸びていた。少なくとも `readme_local320` は **約 2.0 分 / chunk** の速度で前進しており、今度の `direct vo` rerun は「極端に遅いが停止している」状態ではなく、**full local320 summary 到達待ち**だと判断できる。
- 一方で、score 回収待ちの間に **4 本の current Stage2 candidate adapter** (`direct vo`, `stagefreeze vo`, `stagefreeze short`, `direct short`) に対して `audit-submission-compat` を実行したところ、すべて **`blocked_routed_expert_3d_tensors`** だった。いずれも adapter 全体は **`324 tensors = 232x 2D + 92x 3D`** で、blocker は `mixer.switch_mlp.fc1/fc2` の routed-expert LoRA tensor。したがって、**現行 union-adapter Stage2 family は README 提出用 `submission.zip` を直接 export できず、score が良くてもそのまま best-submission 候補には昇格できない**。submission-ready lane は引き続き export-safe 系で確保する必要がある。
- そこで submission-ready 側を止めないため、**export-safe Stage1 broad** を新 run root **`nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage1_broad_exportsafe_v3f_union_rerun_v1`** として再始動し、同時に single-file waiter chain（Stage1 completion record、Stage2 qkvo launch、各 Stage2 postprocess、qkvo->vo->short launch waiters）も **`*_rerun_v1`** 名で再接続した。`poll-live-run-status` も付け直してあり、start block は **`11c059e`** として `results.md` に自動 commit/push 済み。
- export-safe rerun 起動後も `direct vo` score recovery は継続している。`2026-04-09T09:43:34Z` 時点で **`readme_local320 168/320 rows, 21/40 chunks`** まで進み、first summary は未到達だが **still moving**。同時点の export-safe Stage1 rerun は **`Iter1600 / Opt200 / train_loss=0.454646 / itps=0.703 / peak=67.842 GB`**、system snapshot は **`PhysMem: 375G used, 136G unused`**。つまり **1 本の export-safe broad train + 1 本の direct vo proxy eval** は slowdown こそあるものの、OOM なしで並走できている。
- その後 `direct fullrun_v2 -> attention-vo lr2e-5` current-code rerun は `readme_local320` を完走し、**`206/320 = 0.6438`** で着地した。内訳は **`general_stable 165/200 = 0.825`**, **`binary_hard 24/60 = 0.400`**, **`symbol_watch 17/60 = 0.2833`**、family 別でも **`text 19/50 = 0.380`**, **`unit 48/50 = 0.960`**, **`gravity 48/50 = 0.960`**, **`roman 50/50 = 1.000`** だった。tracked MLX baseline **`215/320 = 0.6719`** を下回り、しかも current union-adapter family 自体が `blocked_routed_expert_3d_tensors` で non-exportable なので、この lane は **local320 summary 到達をもって打ち切り**、残りの proxy/specialized tail は停止して export-safe corrective に headroom を返した。停止直後 snapshot は **`PhysMem: 151G used, 360G unused`**。
- 一方で export-safe Stage2 qkvo の最初の `*_rerun_v1` 起動は、source run 解決自体は成功したものの、`notebook-current` の broad default sampling を narrow corrective CSV にそのまま当てたため **`ValueError: No rows found for puzzle type 'Numeral Conversion'.`** で落ちた。その失敗 run root には `shadow_model` と `resume_from_run_manifest.json` が残ったため、後続の手動 restart は `--skip-if-target-started` で **`skipped_existing_target`** になった。successful Stage2 manifests を突き合わせると、正しい corrective sampling は **`Bit Manipulation=209`**, **`Equation Transformation=9`**, その他 4 family は **`0`** で固定する必要がある。
- そこで export-safe chain は **`*_rerun_v2`** 名へ張り直した。旧 `qkvo/vo/short` waiters を止めたうえで、completed Stage1 rerun root **`nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage1_broad_exportsafe_v3f_union_rerun_v1`** から **explicit `--type-sample` override 付き**で qkvo Stage2 を手動 resume し、fresh な qkvo postprocess / qkvo->vo / vo postprocess / vo->short / short postprocess waiters も再接続した。新 qkvo root **`nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr2e5_len1536_rerun_v2`** には既に **`prepare_manifest.json`**, **`runtime_preflight.json`**, **`latest_val_report.json`** が出ており、`runtime_preflight` は **`current_pid=71469`**, **`system_free_percent=97`**, first validation は **`val_loss=1.2338`**。snapshot も **`PhysMem: 215G used, 296G unused`** まで戻っているので、以後の submission-ready lane はこの export-safe v2 corrective chain を正系として追う。
- `README.md` の提出契約（**single adapter**, **rank<=32**, **`submission.zip`**, 評価時 **`max_tokens=7680` / `top_p=1.0` / `temperature=0.0` / `max_num_seqs=64` / `max_model_len=8192`**）に合わせ、以後の heavy compute は **export-safe single-adapter lane** に寄せた。現時点の current trio は **qkvo lr2e-5 len1536**, **vo lr2e-5 len1536**, **qkvo lr1e-5 ep2.4 len1536** の 3 本で、`2026-04-09T12:02Z` 前後の latest train reports は **qkvo = `Opt70 / loss=0.2141 / itps=0.359 / peak=67.399 GB`**, **vo = `Opt30 / loss=0.2627 / itps=0.356 / peak=68.048 GB`**, **short = `Opt20 / loss=0.3781 / itps=0.358 / peak=65.861 GB`**。同時点 snapshot でも **`PhysMem: 414G used, 96G unused`** を維持しており、3 並列の training 自体はまだ OOM 域に入っていない。
- 同時に、current trio の suite summary 到達後に GPU を遊ばせないため、**次線 3 本**の single-file waiters も先に張った。queued candidates は **`qkvo lr5e-6 ep2.4 len1536`**, **`vo lr5e-5 len1536`**, **`qkvo lr2e-5 ep2.4 len768`** で、いずれも source は completed Stage1 export-safe rerun root、sampling は **`Bit Manipulation=209` / `Equation Transformation=9` / others=0** に固定してある。各 candidate には **launch waiter**, **postprocess waiter**, **live progress poller** を追加済みで、trigger はそれぞれ **current qkvo suite summary**, **current vo suite summary**, **current short suite summary**。これで current trio が score 回収まで終わり次第、次の export-safe ablation へ **headroom を保ったまま自動で切り替えられる**。
- さらに `2026-04-09T12:12Z` には current **qkvo lr2e-5 len1536** が train を完走し、**`Opt101 / Iter784 / loss=0.18247 / val_loss=0.28794 / peak=67.399 GB`** で `training_result.json` を生成した。その直後から single-file `postprocess-run` が **`eval_suite_readme_proxy_specialized`** を起動しており、`benchmark_eval_suite_progress.json` と `readme_local320/benchmark_eval_progress.json` は **`status=running`**, **`0/320 rows, 0/40 chunks`** で初期化済み。つまり qkvo current は今 **score 回収フェーズ**へ入っている。
- current **short qkvo lr1e-5 ep2.4 len1536** もその後 train 完了に到達し、**`Opt67 / Iter523 / loss=0.22727 / peak=67.399 GB`** を残したうえで、同じく `readme_local320` progress manifest を **`running, 0/320`** で立ち上げた。`vo lr2e-5 len1536` だけは引き続き train 中で、`2026-04-09T12:16Z` の latest report は **`Opt70 / loss=0.22024 / itps=0.3927 / peak=68.048 GB`**。
- qkvo current が train を抜けて headroom が少し戻ったため、queued next line のうち **`qkvo lr5e-6 ep2.4 len1536`** を suite summary 待ちより前に **手動前倒し起動**した。新 run root **`nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr5e6_ep24_len1536_rerun_v2`** は **`runtime_preflight current_pid=79008`**, first validation **`val_loss=1.2338`**, first train report **`Opt10 / Iter80 / loss=0.76289 / itps=0.3577 / peak=64.841 GB`** を出している。これにより現行の heavy set は **vo train + short eval + qkvo eval + qkvo low-LR train** となり、snapshot は一時 **`PhysMem 457G used / 54G unused`** まで上がったが、その後は **`442G used / 69G unused`** に戻っている。したがって **4 heavy 同時はかなりタイトだが、まだ即 OOM 域ではない** と判断し、追加の manual prelaunch（`vo lr5e-5`, `len768`）はここでは見送って queued waiter のまま維持する。
- その後 `2026-04-09T12:25Z` には current **vo lr2e-5 len1536** も **`Opt101 / Iter784 / loss=0.18862 / itps=0.4471 / peak=68.048 GB`** で train を完了した。これで current export-safe trio は **train フェーズを全て抜け**、以後は **qkvo current / vo current / short current の 3 本が score 回収**, その横で **qkvo low-LR** が次線 train を継続する構成に移行した。
- `2026-04-09T12:33Z` 時点では、progress manifest 上 **qkvo current** の `readme_local320` が **`8/320 rows, 1/40 chunks`** まで前進しており、少なくとも current-code rerun と同様に **blind stall ではなく chunk 単位で進んでいる**。一方で **vo current** と **short current** はまだ **`0/320, 0/40`** の初期段階。次線 **qkvo low-LR** は **`Opt40 / Iter314 / loss=0.28268 / itps=0.47995 / peak=67.399 GB`** まで伸びており、system snapshot も **`PhysMem 388G used / 123G unused`** に戻った。したがって現時点の運用判断は **「current trio の score 回収は継続、manual 前倒しは qkvo low-LR 1 本で止める」** が妥当である。
- その後 **qkvo low-LR (`lr5e-6`)** も **`Opt67 / Iter523 / loss=0.25174 / itps=0.5983 / peak=67.399 GB`** で train を完了し、こちらも `readme_local320` progress manifest を立ち上げた。headroom が **`PhysMem 359G used / 152G unused`** まで戻ったタイミングで、queued 次線から **`vo lr5e-5 len1536`** をさらに **manual prelaunch**した。
- `2026-04-09T12:50Z` 時点の heavy set は **current qkvo eval + current vo eval + current short eval + qkvo low-LR eval + vo high-LR train**。local320 progress は **current qkvo = 24/320 (3/40)**、**current vo = 24/320 (3/40)**、**current short = 24/320 (3/40)**、**qkvo low-LR = 16/320 (2/40)** まで揃っており、少なくとも 4 本とも **chunk 単位で前進中**だと確認できた。一方、new **vo high-LR** は **`Opt40 / Iter314 / loss=0.22633 / itps=0.4233 / peak=68.048 GB`**。snapshot は **`PhysMem 449G used / 62G unused`** とかなりタイトなため、残る **`qkvo len768`** は queued waiter のままにして **manual prelaunch を見送る**。
- さらに `2026-04-09T13:09Z` には **vo high-LR (`lr5e-5`)** も **`Opt101 / Iter784 / loss=0.18651 / itps=0.3881 / peak=68.048 GB`** で train 完了し、そのまま `readme_local320` progress manifest を立ち上げた。ここで 5 lane（current trio + qkvo low-LR + vo high-LR）がすべて local320 回収フェーズへ入ったため、headroom は **`PhysMem 420G used / 91G unused`** に戻った。
- この headroom を使って最後の queued candidate **`qkvo len768`** も一度 manual prelaunch したが、**prepare/runtime + initial validation だけで `PhysMem 493G used / 18G unused`** まで逼迫し、train report 生成前の段階でも **OOM 直前域**だと判断した。そこで **runtime `PID 91674`**, 同 run の **live poller `91864`**, **postprocess waiter `91866`**, 旧 launch waiter `76800` を明示停止し、snapshot を **`420G used / 91G unused`** まで戻した。つまり **len768 は有望候補ではあるが、現在の multi-eval 負荷下では manual prelaunch 不可**。
- ただし len768 自体を捨てたわけではなく、stale marker を避けるため **新 run 名 `...qkvo_lr2e5_ep24_len768_rerun_v3`** で **launch waiter / postprocess waiter / live poller** を再キューした。trigger は引き続き **current short suite summary** で、これにより current heavy set のスコア回収を優先しつつ、headroom が戻ったタイミングで len768 lane を再投入できる状態は維持した。
- その後も active export-safe local320 回収は **5 lane** で継続している。`2026-04-09T13:29Z` 時点の chunk progress は **current qkvo = `72/320, 9/40`**, **current vo = `64/320, 8/40`**, **current short = `72/320, 9/40`**, **qkvo low-LR = `56/320, 7/40`**, **vo high-LR = `16/320, 2/40`** で、**5 本とも blind stall ではなく local320 を前進中**。まだ summary は 0 本だが、system snapshot は **`PhysMem 420G used / 91G unused`** を維持しているので、現時点では **lane 削減より score 回収継続**を優先する。
- `2026-04-09T13:50Z` 時点でも summary はまだ 0 本だが、progress 自体は維持されている。chunk progress は **current qkvo = `96/320, 12/40`**, **current vo = `88/320, 11/40`**, **current short = `112/320, 14/40`**, **qkvo low-LR = `88/320, 11/40`**, **vo high-LR = `48/320, 6/40`**。現時点では **current short** が最も前に出ており、5 本とも引き続き blind stall ではない。snapshot も **`PhysMem 420G used / 90G unused`** とほぼ横ばいで、依然として **OOM を踏まずに 5 lane の local320 回収を継続できている**。
- `2026-04-09T14:10Z` 時点でも summary はまだ 0 本だが、進捗はさらに積み上がった。chunk progress は **current qkvo = `144/320, 18/40`**, **current vo = `144/320, 18/40`**, **current short = `160/320, 20/40`**, **qkvo low-LR = `136/320, 17/40`**, **vo high-LR = `88/320, 11/40`**。つまり **current short が local320 のちょうど半分（20/40 chunks）を通過**し、current qkvo / current vo / qkvo low-LR もほぼ同一ペースで追っている。snapshot は引き続き **`PhysMem 420G used / 91G unused`** で横ばいなので、現方針は変えず **5 lane の score 回収を継続**する。

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage1_broad_exportsafe_v3f_union -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage1_broad_exportsafe_v3f_union`

- status: `stopped`
- label: `stagefreeze-v2-exportsafe-stage1-live`
- observed_at: `2026-04-09T02:34:57.692304+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage1_broad_exportsafe_v3f_union`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline/nemotron-sft-lora-with-cot-v2/artifacts/train_split_with_cot_v3f_safe_plus_notformula.csv`
- sampled_rows: `3321`
- optimizer_progress: `580/832 = 69.71%`
- lr: `0.0001`
- max_seq_length: `4096`
- trainable_lora_suffixes: `['mixer.in_proj', 'mixer.out_proj', 'mixer.shared_experts.up_proj', 'mixer.shared_experts.down_proj']`

#### Latest train progress

- source: `console_log`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage1_broad_exportsafe_v3f_union/console.log`
- iteration: `4633`
- optimizer_step: `580`
- train_loss: `0.331`
- learning_rate: `2.794e-05`
- it_per_sec: `0.531`
- tokens_per_sec: `303.224`
- trained_tokens: `2746223`
- peak_memory_gb: `68.597`

#### Completion markers

- training_result_exists: `False`
- runtime_pid: `67528`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage1_broad_exportsafe_v3f_union -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_stage1_broad_v3f_union -->
### Auto result: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_stage1_broad_v3f_union`

- recorded_at: `2026-04-09T03:05:32.689368+00:00`
- label: `stagefreeze-v1-stage1`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_stage1_broad_v3f_union`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline/nemotron-sft-lora-with-cot-v2/artifacts/train_split_with_cot_v3f_safe_plus_notformula.csv`
- sampled_rows: `3321`
- optimizer_steps: `832`
- lr: `0.0001`
- max_seq_length: `4096`
- trainable_lora_suffixes: `['mixer.in_proj', 'mixer.out_proj', 'mixer.switch_mlp.fc1', 'mixer.switch_mlp.fc2', 'mixer.shared_experts.up_proj', 'mixer.shared_experts.down_proj']`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_stage1_broad_v3f_union -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_stage2_attention_qkvo_lr2e5_len1536 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_stage2_attention_qkvo_lr2e5_len1536`

- status: `training_completed`
- label: `stagefreeze-v1-main-qkvo-live`
- observed_at: `2026-04-09T03:21:53.429955+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_stage2_attention_qkvo_lr2e5_len1536`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_artifacts/stage2_corrective_v1.csv`
- sampled_rows: `218`
- optimizer_progress: `101/101 = 100.00%`
- lr: `2e-05`
- max_seq_length: `1536`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest train progress

- source: `latest_train_report`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_stage2_attention_qkvo_lr2e5_len1536/adapter/latest_train_report.json`
- iteration: `784`
- optimizer_step: `101`
- train_loss: `0.187084`
- learning_rate: `2.36105e-07`
- it_per_sec: `0.858648`
- tokens_per_sec: `398.413`
- trained_tokens: `418695`
- peak_memory_gb: `70.9263`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `17833`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_stage2_attention_qkvo_lr2e5_len1536 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_stage2_attention_vo_lr2e5_len1536 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_stage2_attention_vo_lr2e5_len1536`

- status: `training`
- label: `stagefreeze-v1-vo-live`
- observed_at: `2026-04-09T06:19:37.999442+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_stage2_attention_vo_lr2e5_len1536`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_artifacts/stage2_corrective_v1.csv`
- sampled_rows: `218`
- optimizer_progress: `60/101 = 59.41%`
- lr: `2e-05`
- max_seq_length: `1536`
- trainable_lora_suffixes: `['mixer.v_proj', 'mixer.o_proj']`

#### Latest train progress

- source: `latest_train_report`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_stage2_attention_vo_lr2e5_len1536/adapter/latest_train_report.json`
- iteration: `468`
- optimizer_step: `60`
- train_loss: `0.219455`
- learning_rate: `9.22316e-06`
- it_per_sec: `0.350486`
- tokens_per_sec: `181.026`
- trained_tokens: `249117`
- peak_memory_gb: `71.4728`

#### Completion markers

- training_result_exists: `False`
- runtime_pid: `86512`
- runtime_pid_alive: `True`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_stage2_attention_vo_lr2e5_len1536 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_stage2_attention_qkvo_lr1e5_ep24_len1536 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_stage2_attention_qkvo_lr1e5_ep24_len1536`

- status: `training_completed`
- label: `stagefreeze-v1-short-live`
- observed_at: `2026-04-09T06:35:13.977708+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_stage2_attention_qkvo_lr1e5_ep24_len1536`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_artifacts/stage2_corrective_v1.csv`
- sampled_rows: `218`
- optimizer_progress: `67/67 = 100.00%`
- lr: `1e-05`
- max_seq_length: `1536`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest train progress

- source: `latest_train_report`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_stage2_attention_qkvo_lr1e5_ep24_len1536/adapter/latest_train_report.json`
- iteration: `523`
- optimizer_step: `67`
- train_loss: `0.235834`
- learning_rate: `1.36786e-07`
- it_per_sec: `0.357081`
- tokens_per_sec: `187.37`
- trained_tokens: `277977`
- peak_memory_gb: `70.9263`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `88859`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_stage2_attention_qkvo_lr1e5_ep24_len1536 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_direct_from_fullrun_v2_stage2_attention_vo_lr2e5_len1536 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_direct_from_fullrun_v2_stage2_attention_vo_lr2e5_len1536`

- status: `training`
- label: `direct-fullrun-v2-vo-live`
- observed_at: `2026-04-09T06:39:58.322158+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_direct_from_fullrun_v2_stage2_attention_vo_lr2e5_len1536`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_artifacts/stage2_corrective_v1.csv`
- sampled_rows: `218`
- optimizer_progress: `80/101 = 79.21%`
- lr: `2e-05`
- max_seq_length: `1536`
- trainable_lora_suffixes: `['mixer.v_proj', 'mixer.o_proj']`

#### Latest train progress

- source: `latest_train_report`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_direct_from_fullrun_v2_stage2_attention_vo_lr2e5_len1536/adapter/latest_train_report.json`
- iteration: `628`
- optimizer_step: `80`
- train_loss: `0.237658`
- learning_rate: `3.5589e-06`
- it_per_sec: `0.627675`
- tokens_per_sec: `346.32`
- trained_tokens: `335724`
- peak_memory_gb: `71.4728`

#### Completion markers

- training_result_exists: `False`
- runtime_pid: `90194`
- runtime_pid_alive: `True`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_direct_from_fullrun_v2_stage2_attention_vo_lr2e5_len1536 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_direct_from_fullrun_v2_stage2_attention_qkvo_lr1e5_ep24_len1536 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_direct_from_fullrun_v2_stage2_attention_qkvo_lr1e5_ep24_len1536`

- status: `training_completed`
- label: `direct-fullrun-v2-short-live`
- observed_at: `2026-04-09T06:57:56.343946+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_direct_from_fullrun_v2_stage2_attention_qkvo_lr1e5_ep24_len1536`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_artifacts/stage2_corrective_v1.csv`
- sampled_rows: `218`
- optimizer_progress: `67/67 = 100.00%`
- lr: `1e-05`
- max_seq_length: `1536`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest train progress

- source: `latest_train_report`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_direct_from_fullrun_v2_stage2_attention_qkvo_lr1e5_ep24_len1536/adapter/latest_train_report.json`
- iteration: `523`
- optimizer_step: `67`
- train_loss: `0.270551`
- learning_rate: `1.36786e-07`
- it_per_sec: `0.533786`
- tokens_per_sec: `280.092`
- trained_tokens: `277977`
- peak_memory_gb: `70.9262`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `98124`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_direct_from_fullrun_v2_stage2_attention_qkvo_lr1e5_ep24_len1536 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage1_broad_exportsafe_v3f_union_rerun_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage1_broad_exportsafe_v3f_union_rerun_v1`

- status: `recorded`
- label: `export-safe-stage1-rerun-live`
- observed_at: `2026-04-09T11:41:48.519598+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage1_broad_exportsafe_v3f_union_rerun_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline/nemotron-sft-lora-with-cot-v2/artifacts/train_split_with_cot_v3f_safe_plus_notformula.csv`
- sampled_rows: `3321`
- optimizer_progress: `832/832 = 100.00%`
- lr: `0.0001`
- max_seq_length: `4096`
- trainable_lora_suffixes: `['mixer.in_proj', 'mixer.out_proj', 'mixer.shared_experts.up_proj', 'mixer.shared_experts.down_proj']`

#### Latest train progress

- source: `latest_train_report`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage1_broad_exportsafe_v3f_union_rerun_v1/adapter/latest_train_report.json`
- iteration: `6642`
- optimizer_step: `832`
- train_loss: `0.396673`
- learning_rate: `6.57615e-07`
- it_per_sec: `0.817017`
- tokens_per_sec: `386.812`
- trained_tokens: `3943876`
- peak_memory_gb: `68.5965`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `38710`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `True`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage1_broad_exportsafe_v3f_union_rerun_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr2e5_len1536_rerun_v2 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr2e5_len1536_rerun_v2`

- status: `training_completed`
- label: `export-safe-qkvo-rerun-v2-live`
- observed_at: `2026-04-09T12:12:30.827771+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr2e5_len1536_rerun_v2`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_artifacts/stage2_corrective_v1.csv`
- sampled_rows: `218`
- optimizer_progress: `101/101 = 100.00%`
- lr: `2e-05`
- max_seq_length: `1536`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest train progress

- source: `latest_train_report`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr2e5_len1536_rerun_v2/adapter/latest_train_report.json`
- iteration: `784`
- optimizer_step: `101`
- train_loss: `0.182466`
- learning_rate: `2.36105e-07`
- it_per_sec: `0.387012`
- tokens_per_sec: `179.574`
- trained_tokens: `418695`
- peak_memory_gb: `67.3986`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `71469`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr2e5_len1536_rerun_v2 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_vo_lr2e5_len1536_rerun_v2 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_vo_lr2e5_len1536_rerun_v2`

- status: `training_completed`
- label: `export-safe-vo-rerun-v2-live`
- observed_at: `2026-04-09T12:25:30.325515+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_vo_lr2e5_len1536_rerun_v2`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_artifacts/stage2_corrective_v1.csv`
- sampled_rows: `218`
- optimizer_progress: `101/101 = 100.00%`
- lr: `2e-05`
- max_seq_length: `1536`
- trainable_lora_suffixes: `['mixer.v_proj', 'mixer.o_proj']`

#### Latest train progress

- source: `latest_train_report`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_vo_lr2e5_len1536_rerun_v2/adapter/latest_train_report.json`
- iteration: `784`
- optimizer_step: `101`
- train_loss: `0.188623`
- learning_rate: `2.36105e-07`
- it_per_sec: `0.447069`
- tokens_per_sec: `207.44`
- trained_tokens: `418695`
- peak_memory_gb: `68.0482`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `73135`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_vo_lr2e5_len1536_rerun_v2 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr1e5_ep24_len1536_rerun_v2 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr1e5_ep24_len1536_rerun_v2`

- status: `training_completed`
- label: `export-safe-short-rerun-v2-live`
- observed_at: `2026-04-09T12:16:22.106309+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr1e5_ep24_len1536_rerun_v2`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_artifacts/stage2_corrective_v1.csv`
- sampled_rows: `218`
- optimizer_progress: `67/67 = 100.00%`
- lr: `1e-05`
- max_seq_length: `1536`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest train progress

- source: `latest_train_report`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr1e5_ep24_len1536_rerun_v2/adapter/latest_train_report.json`
- iteration: `523`
- optimizer_step: `67`
- train_loss: `0.227268`
- learning_rate: `1.36786e-07`
- it_per_sec: `0.355856`
- tokens_per_sec: `186.728`
- trained_tokens: `277977`
- peak_memory_gb: `67.3986`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `73434`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr1e5_ep24_len1536_rerun_v2 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr5e6_ep24_len1536_rerun_v2 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr5e6_ep24_len1536_rerun_v2`

- status: `training_completed`
- label: `export-safe-qkvo-lr5e6-rerun-v2-live`
- observed_at: `2026-04-09T12:33:20.132328+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr5e6_ep24_len1536_rerun_v2`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_artifacts/stage2_corrective_v1.csv`
- sampled_rows: `218`
- optimizer_progress: `67/67 = 100.00%`
- lr: `5e-06`
- max_seq_length: `1536`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest train progress

- source: `latest_train_report`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr5e6_ep24_len1536_rerun_v2/adapter/latest_train_report.json`
- iteration: `523`
- optimizer_step: `67`
- train_loss: `0.251744`
- learning_rate: `6.83929e-08`
- it_per_sec: `0.598294`
- tokens_per_sec: `313.941`
- trained_tokens: `277977`
- peak_memory_gb: `67.3986`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `79008`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr5e6_ep24_len1536_rerun_v2 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_vo_lr5e5_len1536_rerun_v2 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_vo_lr5e5_len1536_rerun_v2`

- status: `training_completed`
- label: `export-safe-vo-lr5e5-rerun-v2-live`
- observed_at: `2026-04-09T13:09:21.493620+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_vo_lr5e5_len1536_rerun_v2`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_artifacts/stage2_corrective_v1.csv`
- sampled_rows: `218`
- optimizer_progress: `101/101 = 100.00%`
- lr: `5e-05`
- max_seq_length: `1536`
- trainable_lora_suffixes: `['mixer.v_proj', 'mixer.o_proj']`

#### Latest train progress

- source: `latest_train_report`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_vo_lr5e5_len1536_rerun_v2/adapter/latest_train_report.json`
- iteration: `784`
- optimizer_step: `101`
- train_loss: `0.18651`
- learning_rate: `5.90262e-07`
- it_per_sec: `0.388106`
- tokens_per_sec: `180.081`
- trained_tokens: `418695`
- peak_memory_gb: `68.0482`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `84409`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_vo_lr5e5_len1536_rerun_v2 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr2e5_ep24_len768_rerun_v2 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr2e5_ep24_len768_rerun_v2`

- status: `running_untracked`
- label: `export-safe-qkvo-len768-rerun-v2-live`
- observed_at: `2026-04-09T13:13:32.380139+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr2e5_ep24_len768_rerun_v2`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_artifacts/stage2_corrective_v1.csv`
- sampled_rows: `218`
- optimizer_progress: `0/67 = 0.00%`
- lr: `2e-05`
- max_seq_length: `768`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Completion markers

- training_result_exists: `False`
- runtime_pid: `91674`
- runtime_pid_alive: `True`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr2e5_ep24_len768_rerun_v2 -->

## Export-safe five-lane local320 late progress

- `2026-04-09T14:24Z` 時点では **current qkvo = `176/320, 22/40`**, **current vo = `168/320, 21/40`**, **current short = `192/320, 24/40`**, **qkvo low-LR = `168/320, 21/40`**, **vo high-LR = `144/320, 18/40`**。first summary はまだ 0 本だが、5 lane 全てが引き続き chunk 単位で前進した。
- `2026-04-09T14:34Z` 時点では **current qkvo = `192/320, 24/40`**, **current vo = `176/320, 22/40`**, **current short = `224/320, 28/40`**, **qkvo low-LR = `184/320, 23/40`**, **vo high-LR = `160/320, 20/40`**。先頭は引き続き **current short** で、first local320 summary の最有力になっている。
- memory snapshot は `14:24Z` / `14:34Z` ともに **`PhysMem 420-421G used / 90G unused`** 帯で横ばい。したがって現時点の 5-lane local320 並列は **stall でも OOM 前兆でもなく、単純に wall-clock が重い状態** とみなして継続する。
- `2026-04-09T15:06Z` 時点では **current qkvo = `248/320, 31/40`**, **current vo = `208/320, 26/40`**, **current short = `256/320, 32/40`**, **qkvo low-LR = `192/320, 24/40`**, **vo high-LR = `176/320, 22/40`**。この時点でも first summary は未生成で、依然として **current short** が先頭を維持した。
- `2026-04-09T15:26Z` 時点の progress manifest では **current short = `312/320, 39/40`**, **current qkvo = `288/320, 36/40`**, **current vo = `280/320, 35/40`**, **qkvo low-LR = `272/320, 34/40`**, **vo high-LR = `208/320, 26/40`**。first summary はまだ 0 本だが、5 lane 全てで `benchmark_eval_suite_progress.json` の mtime が引き続き更新されている。
- `ps` 上でも local320 実行中の postprocess Python は生存しており、特に **current short postprocess (`PID 71464`) は `CPU≈29%`, `MEM≈11.7%`** を維持したまま最後の 1 chunk を処理中だった。したがって **39/40 停滞は deadlock ではなく、長い最終 chunk の実行待ち** と判断して watcher を継続する。
- `2026-04-09T15:39Z` 時点では **current qkvo = `304/320, 38/40`**, **current vo = `288/320, 36/40`**, **current short = `312/320, 39/40`**, **qkvo low-LR = `272/320, 34/40`**, **vo high-LR = `232/320, 29/40`**。first summary は依然 0 本だが、current qkvo が current short の背後まで追い上げ、watcher (`shellId 956`) 上でも全 lane が引き続き live だった。
- README 契約（**single adapter / rank<=32 / submission.zip**）と現行 CLI を再照合した上で、次段の export-safe queue を 2 本追加した。新規 queued lanes は **`qkvo lr3e-5 len1536 rerun_v1`** と **`vo lr2e-5 len1024 rerun_v1`** で、いずれも **`wait-resume-train-from-path` + `prepare_manifest` 待ち postprocess + `prepare_manifest` 待ち live poller** を detached で起動済み。
- trigger は **`qkvo lr5e-6 ep2.4 len1536 rerun_v2` の suite summary** と **`vo lr5e-5 len1536 rerun_v2` の suite summary**。したがって今の 5-lane local320 / full-suite を邪魔せず、後続 single-file pipeline を切らさずに繋げられる。
- `2026-04-09T15:44Z` に **first local320 summary** が出て、最初に完了した lane は **current short (`qkvo lr1e-5 ep2.4 len1536 rerun_v2`)** だった。score は **`212/320 = 0.6625`** で、既知の export-safe baseline **`215/320 = 0.6719`** を下回ったため、submission-ready 本線としては弱い。
- breakdown は **binary `18/60`**, **symbol `19/60`**, **text `27/50`**, **unit `48/50`**, **gravity `50/50`**, **roman `50/50`**。特に **`glyph_len5 0/20`**, **`bit_structured_byte_formula 3/14`**, **`manual_audit_priority 7/50`** が重く、逆に gravity / roman は完全維持だった。
- `benchmark_eval_suite_progress.json` 上では current short は local320 完了直後に **`leaderboard_proxy_v2` (84 rows)** へ遷移しており、suite 自体はまだ継続中。残る local320 は **current qkvo `312/320, 39/40`**, **current vo `296/320, 37/40`**, **qkvo low-LR `280/320, 35/40`**, **vo high-LR `240/320, 30/40`** を追跡中で、次の summary 回収へ watcher を切り替える。
- `2026-04-09T15:49Z` に 2 本目の local320 summary として **current qkvo (`qkvo lr2e-5 len1536 rerun_v2`) = `209/320 = 0.6531`** が確定した。family は **binary `19/60`**, **symbol `20/60`**, **text `22/50`**, **unit `49/50`**, **gravity `50/50`**, **roman `49/50`** で、こちらも baseline `215/320` 未満。`glyph_len5` はやはり **`0/20`** のままだった。
- current qkvo は後続 queue をもう支えていないため、local320 summary 確定後に **postprocess tree (`PID 71465/71462/71458`) を停止**し、同 run の suite summary を待っていた stale waiters **`71474/71472/71470`**（current vo duplicate launch）と **`76802/76799/76792`**（qkvo low-LR duplicate launch）も明示停止した。memory snapshot は **`PhysMem 421G used / 90G unused -> 361G used / 150G unused`** まで回復した。
- この headroom を使って、queued candidate のうち **`vo lr2e-5 len1024 rerun_v1`** を **manual prelaunch**した。新 run は **`current_pid=27744`**, `runtime_preflight` で **`system_free_percent=50`**, **`gpu_device_util=100%`**, **`in_use_system_memory≈259.1 GB`**, competing MLX train なしを確認。first validation も **`val_loss=1.2338`** で通り、prelaunch 後の snapshot は **`PhysMem 423G used / 88G unused`**。既存の len1024 live/postprocess waiters は prepare manifest を見て引き継ぐ。
- `2026-04-09T16:00Z` には **current vo (`vo lr2e-5 len1536 rerun_v2`)** も local320 summary を出し、**`209/320 = 0.6531`** で current qkvo と同点の dead lane になった。内訳は **binary `17/60`**, **symbol `18/60`**, **text `24/50`**, **unit `50/50`**, **gravity `50/50`**, **roman `50/50`**、`glyph_len5` は **`0/20`** のまま。
- current vo も baseline `215/320` 未満で本線維持価値が無いため、**postprocess tree (`71466/71461/71459`)** を停止し、同 run の suite summary 依存だった duplicate waiters **`76791/76797/76804`**（vo high-LR duplicate launch）と **`71471/71473/71475`**（short duplicate launch）も掃除した。kill 後 snapshot は **`PhysMem 382G used / 129G unused`** まで戻り、active heavy set は **qkvo low-LR local320**, **vo high-LR local320**, **current short proxy**, **vo len1024 train** に再圧縮された。
- 戻した headroom を idle にせず、queued candidate のもう 1 本だった **`qkvo lr3e-5 len1536 rerun_v1`** も **manual prelaunch**した。新 run は **`current_pid=32475`**, `runtime_preflight` で **`system_free_percent=46`**, **`gpu_device_util=100%`**, **`in_use_system_memory≈282.8 GB`**、first validation **`val_loss=1.2338`** を確認。prelaunch 後の snapshot も **`PhysMem 448G used / 63G unused`** に収まり、qkvo lr3e5 の live/postprocess waiters は prepare manifest を見て引き継いだ。
- `2026-04-09T16:22Z` には **`vo len1024 rerun_v1` training** が完了し、**`optimizer_step=101`**, final train loss **`0.18937`**, final val loss **`0.30195`**, peak memory **`65.52 GB`** を記録した。`postprocess-run` は直ちに **`eval_suite_readme_proxy_specialized/readme_local320`** へ遷移し、suite progress は **`0/320, 0/40`** から開始している。
- 同時点で active heavy set は **qkvo low-LR local320**, **vo high-LR local320**, **current short proxy**, **vo len1024 local320**, **qkvo lr3e5 train** の 5 本となり、snapshot は **`PhysMem 449G used / 62G unused`**。この headroom では **current short suite summary 完了をトリガーにした `len768 rerun_v3` auto-launch が OOM 寄り** と判断し、queued の len768 waiters **`92543/92544/92545`**, **`92549/92551/92554`**, **`92550/92552/92553`** を明示停止した。len768 は **pause** に切り替え、次の local320 summary / lane cut で headroom が戻ってから再投入する。
- その後 current short は **`leaderboard_proxy_v2 80/84`** を完了して **`binary_bias_specialized_set 0/563`** に入ったが、lane 自体は既に local320 **`212/320`** の dead 判定で、本線には不要だった。そこで specialized eval の postprocess tree **`71464/71463/71460`** を停止し、snapshot を **`PhysMem 388G used / 123G unused`** まで戻した。
- 回復した headroom をそのまま search に戻し、pause していた **`qkvo lr2e5 ep2.4 len768 rerun_v3`** を **manual prelaunch** した。新 run は **`current_pid=37687`**, `runtime_preflight` で **`system_free_percent=45`**, **`gpu_device_util=100%`**, **`in_use_system_memory≈289.1 GB`**、first validation **`val_loss=1.2338`** を確認。manual prelaunch に合わせて **live poller** と **postprocess-run** も新規 detached で再接続済み。
- `2026-04-09T16:45Z` には **`qkvo lr3e5 len1536 rerun_v1` training** も完了し、**`optimizer_step=101`**, final train loss **`0.18247`**, final val loss **`0.27802`**, peak memory **`67.40 GB`** を記録した。`postprocess-run` はすぐに **`eval_suite_readme_proxy_specialized/readme_local320`** を開始しており、これで active heavy set は **qkvo low-LR local320**, **vo high-LR local320**, **vo len1024 local320**, **qkvo lr3e5 local320**, **len768 train** に入れ替わった。
- `2026-04-09T16:54Z` には **`qkvo lr2e5 ep2.4 len768 rerun_v3` training** も完了し、**`optimizer_step=67`**, final train loss **`0.21928`**, final val loss **`0.30148`**, peak memory **`65.03 GB`** を記録した。len768 側も `postprocess-run` が **`eval_suite_readme_proxy_specialized/readme_local320`** を開始し、snapshot は **`PhysMem 361G used / 150G unused`** まで回復。これで active set は **4 本の local320 tail回収 + len768 local320 着手** になった。
- `2026-04-09T17:07Z` には **`vo lr5e5 len1536 rerun_v2`** の local320 summary が出て、**`204/320 = 0.6375`** と確定した。内訳は **binary `10/60`**, **symbol `19/60`**, **text `26/50`**, **gravity `49/50`**, **roman `50/50`**, **unit `50/50`**。`glyph_len5 0/20` は変わらず、baseline `215/320` からさらに遠い dead lane だった。
- high-LR vo は summary 確定後に **postprocess tree (`84623/84622/76786`)** を停止し、snapshot は **`PhysMem 360G used / 151G unused`** まで回復した。この回復枠を使い、explore で保留していた **full `stage-union-exportsafe` len1024** を **manual prelaunch**。新 run **`nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_union_exportsafe_lr2e5_len1024_rerun_v1`** は **`current_pid=47215`**, `runtime_preflight` で **`system_free_percent=50`**, **`gpu_device_util=100%`**, **`in_use_system_memory≈258.8 GB`**, first validation **`val_loss=1.2338`** を確認済みで、live poller / postprocess も detached で接続した。
- `2026-04-09T17:22Z` には **`qkvo lr5e-6 ep2.4 len1536 rerun_v2`** の local320 summary が出て、**`210/320 = 0.6562`** と確定した。内訳は **binary `17/60`**, **symbol `18/60`**, **text `25/50`**, **gravity `50/50`**, **roman `50/50`**, **unit `50/50`**。`bit_structured_byte_formula` は **`2/14`**, `glyph_len5` は **`0/20`** のままで、baseline `215/320` を超えられなかった。
- low-LR qkvo は summary 確定後に **postprocess tree (`76790/79296/79297`)** を停止し、snapshot は **`PhysMem 384G used / 127G unused`** まで回復した。この headroom を使って、追加の full corrective ablation として **`stage-union-exportsafe len1536`** を **manual prelaunch**。新 run **`nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_union_exportsafe_lr2e5_len1536_rerun_v1`** は **`current_pid=50566`**, `runtime_preflight` で **`system_free_percent=46`**, **`gpu_device_util=100%`**, **`in_use_system_memory≈284.1 GB`**, first validation **`val_loss=1.2338`** を確認済みで、live poller / postprocess も detached で接続した。
- ただし dual union train + 3 local320 の同時並走では snapshot が **`PhysMem 476G used / 35G unused`** まで逼迫し、vo len1024 / qkvo lr3e5 / len768 の chunk 更新も鈍化した。`stage-union-exportsafe len1536` は **`Opt20 / train_loss=0.24355 / peak_memory=65.20 GB`** まで確認した時点で、**OOM 回避と score 回収優先**のため **`50564/50565/50566`** と related waiters **`50745-50750`** を停止した。停止後 snapshot は **`PhysMem 384G used / 127G unused`** へ回復。
- `2026-04-09T17:44Z` には、先に回していた **`stage-union-exportsafe len1024 rerun_v1` training** が完了した。最終 train report は **`optimizer_step=101`**, train loss **`0.17967`**, final val loss **`0.27409`**, peak memory **`65.90 GB`**。`postprocess-run` は直後に **`readme_local320`** を開始し、初回 progress は **`8/320 rows, 1/40 chunks`**。train 完了後の snapshot は **`PhysMem 360G used / 151G unused`** まで戻った。
- `2026-04-09T18:55Z` には **`stage-union-exportsafe len1024 rerun_v1`** の local320 summary が出て、**`100/320 = 0.3125`** と確定した。内訳は **binary `14/60`**, **general_stable `74/200`**, **symbol `12/60`**、family では **gravity `2/50`**, **text `1/50`**, **unit `22/50`** まで崩れ、full union corrective が broad trunk を完全に壊すことが露呈した。`readme_local320` summary 確定後に **postprocess tree (`47391/47392/47393`)** を停止し、snapshot は **`PhysMem 300G used / 211G unused`** まで回復した。
- full union corrective が dead と判明したため、空いた headroom は **attention-only qkvo len1024** へ回した。新 run **`nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr2e5_len1024_rerun_v1`** を manual prelaunch し、`runtime_preflight` で **`current_pid=69145`**, **`system_free_percent=62`**, **`gpu_device_util=100%`**, **`in_use_system_memory≈194.8 GB`** を確認済み。live poller / postprocess も detached で接続した。

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_vo_lr2e5_len1024_rerun_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_vo_lr2e5_len1024_rerun_v1`

- status: `training_completed`
- label: `export-safe-vo-len1024-rerun-v1-live`
- observed_at: `2026-04-09T16:22:02.430384+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_vo_lr2e5_len1024_rerun_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_artifacts/stage2_corrective_v1.csv`
- sampled_rows: `218`
- optimizer_progress: `101/101 = 100.00%`
- lr: `2e-05`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.v_proj', 'mixer.o_proj']`

#### Latest train progress

- source: `latest_train_report`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_vo_lr2e5_len1024_rerun_v1/adapter/latest_train_report.json`
- iteration: `784`
- optimizer_step: `101`
- train_loss: `0.189373`
- learning_rate: `2.36105e-07`
- it_per_sec: `0.399519`
- tokens_per_sec: `185.377`
- trained_tokens: `417059`
- peak_memory_gb: `65.5183`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `27744`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_vo_lr2e5_len1024_rerun_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr3e5_len1536_rerun_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr3e5_len1536_rerun_v1`

- status: `training_completed`
- label: `export-safe-qkvo-lr3e5-rerun-v1-live`
- observed_at: `2026-04-09T16:45:31.725837+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr3e5_len1536_rerun_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_artifacts/stage2_corrective_v1.csv`
- sampled_rows: `218`
- optimizer_progress: `101/101 = 100.00%`
- lr: `3e-05`
- max_seq_length: `1536`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest train progress

- source: `latest_train_report`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr3e5_len1536_rerun_v1/adapter/latest_train_report.json`
- iteration: `784`
- optimizer_step: `101`
- train_loss: `0.182473`
- learning_rate: `3.54157e-07`
- it_per_sec: `0.410704`
- tokens_per_sec: `190.567`
- trained_tokens: `418695`
- peak_memory_gb: `67.3986`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `32475`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr3e5_len1536_rerun_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr2e5_ep24_len768_rerun_v3 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr2e5_ep24_len768_rerun_v3`

- status: `training_completed`
- label: `export-safe-qkvo-len768-rerun-v3-live`
- observed_at: `2026-04-09T16:54:28.757331+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr2e5_ep24_len768_rerun_v3`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_artifacts/stage2_corrective_v1.csv`
- sampled_rows: `218`
- optimizer_progress: `67/67 = 100.00%`
- lr: `2e-05`
- max_seq_length: `768`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest train progress

- source: `latest_train_report`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr2e5_ep24_len768_rerun_v3/adapter/latest_train_report.json`
- iteration: `523`
- optimizer_step: `67`
- train_loss: `0.219285`
- learning_rate: `2.73572e-07`
- it_per_sec: `0.418385`
- tokens_per_sec: `219.538`
- trained_tokens: `275879`
- peak_memory_gb: `65.0323`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `37687`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr2e5_ep24_len768_rerun_v3 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_union_exportsafe_lr2e5_len1024_rerun_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_union_exportsafe_lr2e5_len1024_rerun_v1`

- status: `training_completed`
- label: `export-safe-union-len1024-rerun-v1-live`
- observed_at: `2026-04-09T17:44:15.575516+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_union_exportsafe_lr2e5_len1024_rerun_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_artifacts/stage2_corrective_v1.csv`
- sampled_rows: `218`
- optimizer_progress: `101/101 = 100.00%`
- lr: `2e-05`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.in_proj', 'mixer.out_proj', 'mixer.shared_experts.up_proj', 'mixer.shared_experts.down_proj', 'mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest train progress

- source: `latest_train_report`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_union_exportsafe_lr2e5_len1024_rerun_v1/adapter/latest_train_report.json`
- iteration: `784`
- optimizer_step: `101`
- train_loss: `0.179665`
- learning_rate: `2.36105e-07`
- it_per_sec: `0.510072`
- tokens_per_sec: `236.673`
- trained_tokens: `417059`
- peak_memory_gb: `65.8962`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `47215`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_union_exportsafe_lr2e5_len1024_rerun_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_union_exportsafe_lr2e5_len1536_rerun_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_union_exportsafe_lr2e5_len1536_rerun_v1`

- status: `training`
- label: `export-safe-union-len1536-rerun-v1-live`
- observed_at: `2026-04-09T17:33:15.378042+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_union_exportsafe_lr2e5_len1536_rerun_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_artifacts/stage2_corrective_v1.csv`
- sampled_rows: `218`
- optimizer_progress: `20/101 = 19.80%`
- lr: `2e-05`
- max_seq_length: `1536`
- trainable_lora_suffixes: `['mixer.in_proj', 'mixer.out_proj', 'mixer.shared_experts.up_proj', 'mixer.shared_experts.down_proj', 'mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest train progress

- source: `latest_train_report`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_union_exportsafe_lr2e5_len1536_rerun_v1/adapter/latest_train_report.json`
- iteration: `160`
- optimizer_step: `20`
- train_loss: `0.24355`
- learning_rate: `1.91935e-05`
- it_per_sec: `0.351834`
- tokens_per_sec: `187.039`
- trained_tokens: `84805`
- peak_memory_gb: `65.8004`

#### Completion markers

- training_result_exists: `False`
- runtime_pid: `50566`
- runtime_pid_alive: `True`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_union_exportsafe_lr2e5_len1536_rerun_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr2e5_len1024_rerun_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr2e5_len1024_rerun_v1`

- status: `training`
- label: `export-safe-qkvo-len1024-rerun-v1-live`
- observed_at: `2026-04-09T19:13:25.811685+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr2e5_len1024_rerun_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v1_artifacts/stage2_corrective_v1.csv`
- sampled_rows: `218`
- optimizer_progress: `70/101 = 69.31%`
- lr: `2e-05`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest train progress

- source: `latest_train_report`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr2e5_len1024_rerun_v1/adapter/latest_train_report.json`
- iteration: `548`
- optimizer_step: `70`
- train_loss: `0.236552`
- learning_rate: `6.20912e-06`
- it_per_sec: `0.592012`
- tokens_per_sec: `314.262`
- trained_tokens: `290510`
- peak_memory_gb: `65.85`

#### Completion markers

- training_result_exists: `False`
- runtime_pid: `69145`
- runtime_pid_alive: `True`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr2e5_len1024_rerun_v1 -->
