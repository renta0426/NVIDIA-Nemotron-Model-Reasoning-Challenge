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

## Binary bias specialized eval

| version | eval_name | rows | accuracy | bit_other | byte_formula | permutation | boolean_family | notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `baseline-mlx-notebook-original-fullrun-v2-binary-specialized-v1` | `baseline_mlx_notebook_original_fullrun_v2/phase0_binary_bias_specialized_eval` | `563` | `286/563 = 0.5080` | `118/218` | `128/283` | `40/62` | `47/60` | `boxed=1.0`; `regex_exact=1.0`; `leading_zero=0.8494`; `supported_bijection=33/50`; `supported_not_structured=15/55`; `rare_byte_transform=9/11` |

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
| `baseline-mlx-routeaware-fullrun-v2` | `train --profile notebook-original --train-csv train_split_with_cot_v2_plus_binary_route_aware.csv --type-sample ...full counts... --fail-on-runtime-contention` | `cuda-train-data-analysis-v1/proof_first_solver_factory_routing/artifacts/train_split_with_cot_v2_plus_binary_route_aware.csv` | `7268` | `14536` | `1818` | `Iter1 val=1.340`; `Opt10 loss=0.937 lr=1.000e-05 itps=0.701`; `Opt20=0.728`; `Opt30=0.717`; `Opt40=0.743`; `Opt50=0.692`; `Opt60=0.735`; `Opt70=0.744`; `Opt80=0.716`; `Opt90=0.749`; `Opt100=0.741`; `Opt110=0.755`; `Opt120=0.722`; `Opt130=0.733`; `Opt140=0.735`; `Opt150=0.748`; `Opt160=0.724`; `Opt170=0.746`; `Opt180=0.739`; `Opt190=0.746`; `Opt200=0.713`; `Opt210=0.719`; `Opt220=0.745`; `Opt230=0.742`; `Opt240=0.766`; `Opt250=0.696`; `Opt260=0.740`; `Opt270=0.744`; `Opt280=0.741`; `Opt290=0.764`; `Opt300=0.741`; `Opt310=0.757`; `Opt320=0.729`; `Opt330=0.764`; `Opt340=0.730`; `Opt350=0.742`; `Opt360=0.757`; `Opt370=0.783`; `Opt380=0.735`; `Opt390=0.748`; `Opt400=0.711`; `Opt410=0.751`; `Opt420=0.735`; `Opt430=0.736`; `Opt440=0.767`; `Opt780=0.757`; `Opt1120=0.747`; `Opt1460=0.752`; `eta≈1.06h`; `peak_mem=82.554 GB` | in_progress | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_notebook_original_routeaware_fullrun_v2/console.log` |

- route-aware retrain では **single-file MLX pipeline と notebook-original profile は据え置き**、変更点は **`train_csv` 差し替え**と、追加された binary rows を捨てないための **`type_sample` 全件数上書き**だけに限定した。
- route-aware CSV の sampling は **`Bit Manipulation=1317`, `Equation Transformation=200`, `Gravitational Constant=1511`, `Numeral Conversion=1491`, `Text Encryption=1407`, `Unit Conversion=1342`** で、`sampled_rows=7268`, `optimizer_steps=1818`。baseline fullrun (`2907 rows`, `728 steps`) より大きく、現時点の sustained throughput では **約 5.3 時間**級の run になる。
- 20 分後の定点では **`Iter 2160 (Opt 270 / 1818)`** まで到達した。最新 report は **`Train loss 0.452 / LR 9.765e-05 / It/sec 0.744 / Tokens/sec 454.688 / Trained Tokens 1,338,611 / Peak mem 82.554 GB`**。直近 10 report 平均は **`0.735 it/s`** で、残りは **`12376` microsteps / `1548` optimizer steps**、単純 ETA は **約 4.68 時間**。
- さらに 30 分後の定点では **`Iter 3520 (Opt 440 / 1818)`** に到達した。最新 report は **`Train loss 0.376 / LR 9.123e-05 / It/sec 0.767 / Tokens/sec 447.751 / Trained Tokens 2,173,112 / Peak mem 82.554 GB`**。直近 10 report 平均は **`0.746 it/s`** で、残りは **`11016` microsteps / `1378` optimizer steps**、単純 ETA は **約 4.10 時間**。
- さらに 1 時間後の定点では **`Iter 6240 (Opt 780 / 1818)`** に到達した。最新 report は **`Train loss 0.285 / LR 6.863e-05 / It/sec 0.757 / Tokens/sec 452.406 / Trained Tokens 3,852,520 / Peak mem 82.554 GB`**。直近 10 report 平均は **`0.741 it/s`** で、残りは **`8296` microsteps / `1038` optimizer steps**、単純 ETA は **約 3.11 時間**。
- さらに 1 時間後の定点では **`Iter 8956 (Opt 1120 / 1818)`** に到達した。最新 report は **`Train loss 0.286 / LR 3.979e-05 / It/sec 0.747 / Tokens/sec 453.717 / Trained Tokens 5,525,132 / Peak mem 82.554 GB`**。直近 10 report 平均は **`0.746 it/s`** で、残りは **`5580` microsteps / `698` optimizer steps**、単純 ETA は **約 2.08 時間**。
- さらに 1 時間後の定点では **`Iter 11676 (Opt 1460 / 1818)`** に到達した。最新 report は **`Train loss 0.274 / LR 1.437e-05 / It/sec 0.752 / Tokens/sec 453.946 / Trained Tokens 7,215,887 / Peak mem 82.554 GB`**。直近 10 report 平均は **`0.748 it/s`** で、残りは **`2860` microsteps / `358` optimizer steps**、単純 ETA は **約 1.06 時間**。
