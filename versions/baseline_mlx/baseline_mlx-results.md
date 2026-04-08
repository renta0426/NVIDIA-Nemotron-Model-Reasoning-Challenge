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
- `symbol60` の isolated score は **初回 `13/60` / rerun1 `13/60`** で完全一致し、row-level も **60/60 identical**。一方で同じ 60 symbol ids を含む `full320` では **`20/60`** となり、raw output は **54/60 rows** で変化、**9 rows** で correctness が反転した。したがって MLX 系の family slice 判定は batch composition に敏感で、mainline 採用判断は **README actual full320** を優先する。
- 一方で `roman 50/50`, `unit 50/50` は README 条件下でも完全再現できており、baseline notebook 由来の知識は family ごとに保持率が大きく異なる。
- row-level で origin reference と突き合わせると `HF-only 65`, `MLX-only 12`, `both_wrong 59`, `both_correct 184`。HF-only loss は `text 29`, `binary 16`, `gravity 11`, `symbol 9` が中心で、特に text は **HF が取れて MLX だけ落とす**再現差が支配的。
- notebook 現在版の学習セルは `train_split_with_cot_v3f_safe_plus_notformula.csv` と `Bit Manipulation = 1021` を指している。したがって、今回の `train_split_with_cot.csv` / `607` 再現は「元 CSV baseline」の記録として保持しつつ、次段では **notebook current config の MLX 再現**も別 run として切り分ける。
- 2026-04-07 の現タスクでは、ユーザー指示により **並列学習は禁止**。LoRA target fix の full retrain 1 本だけを継続し、追加の並列再学習やアブレーション起動は保留にした。
