Update 2026-04-12T04:08Z:
- README-aligned `readme_local320` now resolves `reprobridge21_text3bit1num8raw2grav1unitedge_v1` as dead:
  - final local score is `227/320 = 0.7094`
  - so the lane cannot meet the working `0.75` gate and should be retired at the next moment shell execution is healthy enough to stop its remaining live/proxy workers
- the stronger surviving bridge lanes remain healthy:
  - `reprobridge23_text3bit1num8raw5unitedge_v1`: `216/272 = 0.7941`
  - `reprobridge24_text3bit1num8raw6nograv_v1`: `48/48 = 1.0000`
  - `reprobridge25_text3bit1num8raw6unitedge_v1`: `32/32 = 1.0000`
- the queue has been extended one more step offline:
  - `reprobridge31_text3bit1num8raw12unitedge_v1`
    - remove: `3f37b894`
    - add: `2f5959c9`
    - resulting mix: `Bit 34 / Text 18 / Gravity 9 / Unit 1 / Equation 18`
    - rationale: start from `reprobridge30`, keep only the last hard unit-edge hedge `0c26f842`, and swap the final non-edge unit stabilizer for the next highest-hard-score still-unused train_split `numeric_2x2` row
- operational blocker:
  - the current shell runtime is intermittently failing with `posix_openpt failed: Device not configured`, so `reprobridge21` retirement and the missing `reprobridge31` launcher/postprocess/0.80 waiters are prepared but not yet armed from this session

Update 2026-04-12T03:45Z:
- `reprobridge22_text3bit1num8raw5grav1_fullraw_v1` is now operationally retired:
  - README-aligned `readme_local320` finalized at `231/320 = 0.7219`, so the lane cannot cross the working `0.75` promotion gate
  - its live poller, postprocess worker, threshold waiter, and stale `reprobridge22 summary -> reprobridge21/23` waiters were explicitly stopped
- the recovered headroom was used immediately:
  - free memory recovered to about `178.12 GB`
  - `reprobridge25_text3bit1num8raw6unitedge_v1` was manual early-launched with the same single-file `resume-train-from-run` path used for `reprobridge24`
  - existing `reprobridge25` prepare/live/postprocess waiters attached automatically once `prepare_manifest.json` appeared
- current implication:
  - active bridge lanes are now `21/23/24/25`
  - after `25` joined, free memory settled near `95.04 GB`, so `reprobridge26+` remain queued behind the normal corrected handoff chain rather than being manual early-launched

Update 2026-04-12T03:34Z:
- `reprobridge24_text3bit1num8raw6nograv_v1` was manual early-launched as soon as `reprobridge20` was cut and host free memory recovered above the standing launch band:
  - launch path: single-file `resume-train-from-run`
  - source run: `o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1`
  - runtime preflight: `system_free_memory=63%`, `gpu_device_util=100%`
  - immediate state: `prepare_manifest.json` is present, the existing live/postprocess/threshold waiters have attached, and training has already reached `Iter 1: Val loss 0.397`
- operational implication:
  - the bridge wave is back to four active lanes (`21/22/23/24`) before `reprobridge23` full-suite completion
  - `reprobridge25 -> 30` remain queued behind the corrected handoff chain, so the queue can keep refilling even after this early-launch override

Update 2026-04-12T03:29Z:
- `reprobridge20_text3bit1num8raw4grav1_hedgecut_v1` is now operationally retired:
  - README-aligned `readme_local320` finished at `229/320 = 0.7156`, so it can no longer cross the working `0.75` promotion gate even with the remaining proxy pass
  - its live poller, postprocess worker, threshold waiter, and stale `reprobridge20 summary -> reprobridge22/23` handoff waiters were explicitly stopped
- immediate implication:
  - host free memory recovered to about `178.93 GB`, which is back above the standing `PhysMem unused >= 150 GB` launch band
  - the next actual blocker for `reprobridge24` is no longer host headroom; it is only the missing `reprobridge23` full-suite summary
- current visible bridge-wave state after the cut:
  - `reprobridge21`: `226/288 = 0.7847` (`14/32` still needed to hold `0.75`)
  - `reprobridge22`: `230/288 = 0.7986` (`10/32` still needed to hold `0.75`)
  - `reprobridge23`: `144/144 = 1.0000` so far, still the key handoff lane for `24 -> 30`

Update 2026-04-12T03:18Z:
- The repaired raw-heavy bridge queue has now been extended two more steps beyond `reprobridge28`:
  - `reprobridge29_text3bit1num8raw10unitedge_v1` is now materialized from `reprobridge28`
    - remove: `2af08815`
    - add: `1f445c5e`
    - resulting mix: `Bit 34 / Text 18 / Gravity 9 / Unit 3 / Equation 16`
    - rationale: keep the hard unit-edge hedge `0c26f842` and the remaining stronger unit stabilizers, but swap the weakest remaining unit row for the highest-hard-score still-unused verified `numeric_2x2` row that is already present in the baseline `train_split_with_cot.csv`
  - `reprobridge30_text3bit1num8raw11unitedge_v1` is now also materialized from `reprobridge29`
    - remove: `95e8326c`
    - add: `2f485a40`
    - resulting mix: `Bit 34 / Text 18 / Gravity 9 / Unit 2 / Equation 17`
    - rationale: continue the same bridge direction one step further by cutting the last remaining hard-2 unit stabilizer while still leaving `3f37b894` and the hard unit-edge row `0c26f842` in place
- immediate implication:
  - queue depth is now `24 -> 25 -> 26 -> 27 -> 28 -> 29 -> 30`
  - unlike `27/28`, both new additions come from `baseline/nemotron-sft-lora-with-cot-v2/artifacts/train_split_with_cot.csv`, so they stay inside the generated-COT-safe source family and do not require manual `type` backfill
- operational note:
  - the continuous proxybench best-submission poller was restarted after the old shell exited; the selected exportable candidate is still the same `235/320, 131/200` `o30best_proxybench30ao_b10_t10_g15_u15` lane, so queue extension can continue without losing submission mirroring

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1 -->
### Auto result: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1`

- recorded_at: `2026-04-12T04:12:39.403064+00:00`
- label: `o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_v1`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_binary10_text10_grav15_unit15_v1.csv`
- sampled_rows: `80`
- optimizer_steps: `8`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Scores

- readme_local320: `235/320 = 0.7344`
- local320_components: `general_stable_set 183/200 = 0.9150; binary_hard_set 29/60 = 0.4833; symbol_watch_set 23/60 = 0.3833`
- leaderboard_proxy_v1_set: `131/200 = 0.6550`

#### Submission audit

- audit_status: `potentially_exportable_2d_only`
- peft_export_ready: `True`
- tensor_count: `232`

#### Submission export

- submission_zip: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1/submission_export/submission.zip`
- zip_size_bytes: `102357401`
- validation_valid: `True`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1 -->

### Manual threshold promotion note: `local-ge-0.70 frontier`

- source_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1`
- promotion_script: `versions/baseline_mlx_threshold_submission_v1/reproduce_threshold_submission.py`
- promoted_at: `2026-04-11T19:08Z`
- threshold_label: `local-ge-0.70`
- readme_contract: `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, `max_model_len=8192`, `max_lora_rank=32`
- gate_scores: `readme_local320 235/320 = 0.7344`, `leaderboard_proxy_v1_set 131/200 = 0.6550`
- output_root: `baseline_mlx/outputs/threshold_submission_local_ge_070_frontier_v1`
- summary_md: `baseline_mlx/outputs/threshold_submission_local_ge_070_frontier_v1/threshold_submission_summary.md`
- reproduced_submission_zip: `baseline_mlx/outputs/threshold_submission_local_ge_070_frontier_v1/submission_export/submission.zip`
- reproduced_zip_size_bytes: `102357401`
- reproduced_validation_valid: `True`
- notes: `the already-achieved >0.70 frontier is now re-exported by the new single-file threshold pipeline, so future >0.75 / >0.8 promotions can reuse the same README-contract path instead of relying on the original run-root export only`

### Manual threshold waiter note: `active + queued wave 0.75 / 0.8`

- armed_at: `2026-04-11T19:10Z`
- wait_script: `versions/baseline_mlx_threshold_submission_v1/reproduce_threshold_submission.py`
- wait_condition: `each waiter blocks on eval_suite_readme_proxy_specialized/benchmark_eval_suite_summary.json for its target run, then conditionally emits threshold artifacts only when both README-contract gates are satisfied`
- gate_contract: `readme_local320 >= target threshold`, `leaderboard_proxy_v1_set >= 0.65`, `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, `max_model_len=8192`
- active_waiters: `reprobridge20 -> {0.75, 0.80}`, `reprobridge22 -> {0.75, 0.80}`, `reprobridge21 -> {0.75, 0.80}`, `reprobridge23 -> {0.75, 0.80}`
- retired_waiters: `numreal8` retired after local320 finished at `226/320 = 0.7063`, which ruled out both `local-ge-0.75` and `local-ge-0.80`; `reprogap5` retired after stalling at `225/304 = 0.7401` with one chunk left, which made `local-ge-0.75` improbable enough to cut for memory; `reprogap4` retired after local320 finished at `229/320 = 0.7156`, which ruled out both the tracked frontier and `local-ge-0.75`; `reprobridge9` retired after local320 finished at `230/320 = 0.7188`, which ruled out both the tracked frontier and `local-ge-0.75`; `reprobridge10` retired after local320 finished at `228/320 = 0.7125`, which ruled out both the tracked frontier and `local-ge-0.75`; `reprobridge12` retired after local320 finished at `228/320 = 0.7125`, which ruled out both the tracked frontier and `local-ge-0.75`; `reprobridge13` retired after local320 finished at `235/320 = 0.7344`, which matched the tracked frontier but still missed the `0.75` gate and therefore did not justify further proxy continuation; `reprobridge15` retired after local320 finished at `228/320 = 0.7125`, which ruled out both the tracked frontier and `local-ge-0.75` and made further proxy continuation lower EV than the stronger raw-heavy siblings; `reprobridge16` retired after local320 finished at `232/320 = 0.7250`, which cleared the previous bridge-family siblings but still missed both the tracked frontier and the `0.75` gate; `reprobridge17` retired after local320 finished at `227/320 = 0.7094`, which matched the older bridge-family collapse pattern rather than the surviving raw+gravity line; `reprobridge18` retired after local320 finished at `227/320 = 0.7094`, which failed in almost the same way as reprobridge17 and removed the last live value from the hybrid restore branch; `reprobridge19` retired after local320 finished at `231/320 = 0.7219`, which ruled out both the tracked frontier and the `0.75` gate before proxy continuation justified another heavy eval worker`
- queued_waiters: `reprobridge24 -> {0.75, 0.80}`, `reprobridge25 -> {0.75, 0.80}`, `reprobridge26 -> {0.75, 0.80}`, `reprobridge27 -> {0.75, 0.80}`, `reprobridge28 -> {0.75, 0.80}`
- output_roots: `baseline_mlx/outputs/threshold_submission_numreal8_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprogap4_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprogap5_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprobridge9_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprobridge10_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprobridge12_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprobridge13_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprobridge15_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprobridge16_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprobridge17_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprobridge18_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprobridge19_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprobridge20_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprobridge21_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprobridge22_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprobridge23_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprobridge24_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprobridge25_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprobridge26_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprobridge27_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprobridge28_local_ge_075_v1`, `..._080_v1`
- notes: `this keeps the threshold packaging path live across the currently running bridge wave, so any qualifying >0.75 or >0.8 result can materialize a submission artifact immediately instead of waiting for another manual pass; numreal8, reprogap5, reprogap4, reprobridge9, reprobridge10, reprobridge12, reprobridge13, reprobridge15, reprobridge16, reprobridge17, reprobridge18, and now reprobridge19 were all retired from the active threshold set after finishing below the necessary local gates, while reprobridge20, reprobridge22, reprobridge21, and manually early-launched reprobridge23 remain the active threshold-tracked lanes; a later artifact audit found that reprobridge23 actually trained with sampled_rows=79 because 0c26f842 landed in the queued CSV with blank generated_cot/type, so queued descendants reprobridge24/25/26 were repaired in place before launch and the queue now extends further through corrected reprobridge27 to reprobridge28`

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_verifiedswap22_bit33eq2_lr1e6_len1024_from_proxybench_v2 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_verifiedswap22_bit33eq2_lr1e6_len1024_from_proxybench_v2`

- status: `paused_memory_cut`
- label: `o30best-verifiedswap22-bit33eq2-v2-eval-live`
- observed_at: `2026-04-11T18:00:40+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_verifiedswap22_bit33eq2_lr1e6_len1024_from_proxybench_v2`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_verifiedswap22_bit33eq2_v1.csv`
- sampled_rows: `80`
- optimizer_progress: `0/8 = 0.00%`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_verifiedswap22_bit33eq2_lr1e6_len1024_from_proxybench_v2/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_verifiedswap22_bit33eq2_lr1e6_len1024_from_proxybench_v2/eval_suite_readme_proxy_specialized`
- suite_evaluations: `1/2 = 50.00%`
- current_evaluation: `leaderboard_proxy_v1_set`
- current_rows_progress: `0/200 = 0.00%`
- current_chunks_progress: `0/13 = 0.00%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_verifiedswap22_bit33eq2_lr1e6_len1024_from_proxybench_v2/eval_suite_readme_proxy_specialized/leaderboard_proxy_v1_set/benchmark_eval_progress.json`
- accuracy_so_far: `0.0000`
- correct_so_far: `0`
- completed_evaluations: `['readme_local320']`
- completed_evaluation_scores: `readme_local320 230/320 = 0.7188`
- manual_cut_note: `bit33eq2 finished local320 at 230/320, below the tracked 235/320 frontier; after reprogap4 launch pushed host headroom down to roughly PhysMem unused 49 GB, proxy continuation was intentionally cut to protect the wave and keep resources for reprogap4 plus the numreal bridge lanes`
- post_cut_memory_note: `after killing the bit33 postprocess + live poller workers, host headroom recovered to roughly PhysMem unused 206 GB`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `74387`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_verifiedswap22_bit33eq2_lr1e6_len1024_from_proxybench_v2 -->

### Manual queue note: `reprogap4_text3bit1_anchortrim_v1`

- status: `launched_after_sym9_cut`
- queued_at: `2026-04-11T17:42Z`
- launched_at: `2026-04-11T17:57Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprogap4_text3bit1_anchortrim_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprogap4_text3bit1_anchortrim_v1.csv`
- trigger: `launched early once sym9 was cut and free memory recovered to ~145 GB; the original wait-on-bit33 launcher was then terminated to avoid duplicate start paths`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: tracked `131/200` frontier beats clean repro `128/200` on six proxy rows; two numeric_2x2 rows are already covered by the current bridge family, so this queue targets the remaining four absent rows (`text_monoalphabetic x3 + bit_structured_byte_formula x1`) while trimming the easiest gravity/unit stabilizers from `verifiedswap22_bit33eq2`

### Manual queue note: `reprogap5_text3bit1num1_anchortrim_v1`

- status: `launched_after_bit33_cut`
- queued_at: `2026-04-11T17:50Z`
- launched_at: `2026-04-11T18:02Z`
- training_completed_at: `2026-04-11T18:05Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprogap5_text3bit1num1_anchortrim_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprogap5_text3bit1num1_anchortrim_v1.csv`
- trigger: `launched early once bit33 proxy was cut and free memory recovered to ~206 GB; the original wait-on-numreal8 launcher was then terminated to avoid duplicate start paths`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: `reprogap4` covers the four absent frontier-over-repro rows with verified text + structured-byte rows; this hedge adds the only remaining absent reverse-gap row (`8158a14c`, `answer_only_keep numeric_2x2`) as a boxed answer-only example while trimming the next easiest gravity stabilizer, keeping answer-only exposure at `1/80`
- cut_note: `this lane was later retired at readme_local320 225/304 = 0.7401 with one chunk left because it needed 15/16 in the final chunk to recover the 0.75 gate; proxy continuation was intentionally terminated to free memory for reprogap4, reprobridge9, and the queued sibling wave`

### Manual queue note: `reprobridge9_text3bit1num5_anchortrim_v1`

- status: `cut_after_local320`
- queued_at: `2026-04-11T18:10Z`
- launched_at: `2026-04-11T18:36Z`
- training_completed_at: `2026-04-11T18:38Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge9_text3bit1num5_anchortrim_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge9_text3bit1num5_anchortrim_v1.csv`
- triggers: `it was launched early while reprogap4 / reprogap5 / numreal8 were still active because host headroom was about PhysMem unused 143-144 GB, which was enough to reopen a fourth active lane; the original summary-trigger launch waiters are no longer the primary path`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: this hybrid combines the exact four absent frontier-over-repro rows from `reprogap4` with the five quality-focused numeric anchors from `verifiedmix`, while trimming the easiest five gravity and four unit stabilizers from `verifiedswap22_bit33eq2`
- resulting_mix: `Bit 34 / Text 18 / Gravity 10 / Unit 11 / Equation 7`
- notes: `the goal was to test whether the narrow text+structured-byte reproducibility fix and the verified numeric bridge stack could combine constructively without introducing answer_only numeric rows; the early launch opened with Iter 1 val_loss ≈ 0.398, closed short train at train_loss ≈ 0.3614 / val_loss ≈ 0.3980, handed off to README-contract eval, and was then retired once local320 finalized at 230/320 = 0.7188`

### Manual queue note: `reprobridge10_text3bit1num5num1_anchortrim_v1`

- status: `cut_after_local320`
- queued_at: `2026-04-11T18:20Z`
- launched_at: `2026-04-11T20:34Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge10_text3bit1num5num1_anchortrim_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge10_text3bit1num5num1_anchortrim_v1.csv`
- trigger: `launched early once the numreal8 and reprogap5 cuts recovered roughly PhysMem unused 202 GB; this intentionally overrode the previous wait-for-reprobridge9-summary chain so the sibling matrix could keep expanding in parallel`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: this sibling stacks the exact four `reprogap4` frontier-over-repro rows, the five verifiedmix numeric anchors, and the single raw-only reverse-gap answer_only row from `reprogap5`, while trimming the easiest five gravity and five unit stabilizers from `verifiedswap22_bit33eq2`
- resulting_mix: `Bit 34 / Text 18 / Gravity 10 / Unit 10 / Equation 8`
- notes: `this is the first queued sibling that carries all currently known repro-gap fixes in one 80-row set while keeping answer_only exposure capped at 1/80; the original launch waiter was accidentally killed during stale summary cleanup, but a fresh duplicate-safe wait-resume launcher was re-armed and confirmed live; once memory recovered, the run was started directly and opened with Iter 1 val_loss ≈ 0.368 while the existing live/postprocess waiters remained in place to pick up the new run; it was later retired once local320 finalized at 228/320 = 0.7125`

### Manual queue note: `reprobridge12_text3bit1num8_anchortrim_v1`

- status: `cut_after_local320`
- queued_at: `2026-04-11T18:24Z`
- launched_at: `2026-04-11T20:41Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge12_text3bit1num8_anchortrim_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge12_text3bit1num8_anchortrim_v1.csv`
- trigger: `launched early once the reprogap4 cut recovered roughly PhysMem unused 192 GB; this intentionally overrode the previous wait-for-reprobridge10-summary chain so the broad sibling could join the live wave immediately`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: this broader sibling combines the exact four `reprogap4` frontier-over-repro rows with the full eight-row `numreal8` numeric block, while trimming the easiest six gravity and six unit stabilizers from `verifiedswap22_bit33eq2`
- resulting_mix: `Bit 34 / Text 18 / Gravity 9 / Unit 9 / Equation 10`
- notes: `this is the broad-numeric counterpart to reprobridge9 and was originally chained after reprobridge10, but after the reprogap4 cut freed enough memory it was started directly; the short train closed with train_loss ≈ 0.3630 / val_loss ≈ 0.4518 / optimizer_step 8 / peak_memory ≈ 65.46 GB and then handed off to the existing live/postprocess waiters; it was later retired once local320 finalized at 228/320 = 0.7125`

### Manual queue note: `reprobridge13_text3bit1num8num1_anchortrim_v1`

- status: `cut_after_local320`
- queued_at: `2026-04-11T18:29Z`
- launched_at: `2026-04-11T20:58Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge13_text3bit1num8num1_anchortrim_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge13_text3bit1num8num1_anchortrim_v1.csv`
- trigger: `launched early once host headroom returned to roughly PhysMem unused 192 GB, intentionally overriding the original wait-for-reprobridge12-summary chain so the final answer_only sibling could join the active wave immediately`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: this factor sibling adds the single `reprogap5` reverse-gap answer_only hedge on top of `reprobridge12`, closing the narrow/broad numeric bridge × answer_only off/on 2x2 queue matrix
- resulting_mix: `Bit 34 / Text 18 / Gravity 9 / Unit 8 / Equation 11`
- notes: `reprobridge13 differs from reprobridge12 by exactly one row: answer_only hedge row 8158a14c replaces the next easiest remaining unit stabilizer a127eb72; runtime preflight captured current_pid 77590 with PhysMem unused about 192 GB, GPU device util 100%, and in-use system memory about 193.37 GB at launch; the short train then closed with train_loss ≈ 0.3629 / val_loss ≈ 0.4594 / optimizer_step 8 / peak_memory ≈ 65.46 GB and handed off to README-contract eval; it later finalized at readme_local320 235/320 = 0.7344 with binary 29/60, symbol 23/60, and text 33/50, then was intentionally retired because it still missed the 0.75 gate and early proxy rows were only 14/32 = 0.4375`

### Manual queue note: `reprobridge15_text3bit1num8num1swap_anchorrestore_v1`

- status: `cut_after_local320_below_threshold`
- queued_at: `2026-04-11T22:04Z`
- launched_at: `2026-04-11T22:31Z`
- local320_completed_at: `2026-04-12T00:40Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge15_text3bit1num8num1swap_anchorrestore_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge15_text3bit1num8num1swap_anchorrestore_v1.csv`
- trigger: `launched early once reprobridge10 and reprobridge12 were cut and host headroom returned to roughly PhysMem unused 313 GB, intentionally overriding the original wait-for-reprobridge13-summary queue while keeping the duplicate-safe waiters alive as no-op backups`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: `the selected numeric_2x2 pool is already exhausted by reprobridge13, so this follow-up no longer tries to widen numeric coverage; instead it keeps the 8158a14c hedge row from reprobridge13, restores one unit stabilizer, and drops one high-audit answer_only numeric row to test whether the broad+hedge branch works better with slightly less answer_only burden`
- resulting_mix: `Bit 34 / Text 18 / Gravity 9 / Unit 9 / Equation 10`
- notes: `reprobridge15 is a hedge-swap / anchor-restore branch built by replacing answer_only numeric row 6e60b0c5 from reprobridge13 with restored unit stabilizer a127eb72 from reprobridge12; the run stayed within the currently selected train pool and was started immediately once the reprobridge10 and reprobridge12 cuts reopened enough headroom; runtime preflight captured current_pid 4499 with PhysMem unused about 313 GB, GPU device util 99%, and in-use system memory about 65.03 GB at launch; the short train then closed with train_loss ≈ 0.3678 / val_loss ≈ 0.4383 / optimizer_step 8 / peak_memory ≈ 65.46 GB, but local320 then collapsed in the final chunk and finished at 228/320 = 0.7125 (general 177/200, binary 30/60, symbol 21/60, text 28/50), so the lane was cut before any meaningful proxy continuation rather than spending further memory on a now-clearly losing hedge-heavy branch`

### Manual queue note: `reprobridge16_text3bit1num8num1raw4_answertrim_v1`

- status: `cut_after_local320_below_threshold`
- queued_at: `2026-04-11T22:41Z`
- launched_at: `2026-04-11T22:42Z`
- local320_completed_at: `2026-04-12T01:08Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge16_text3bit1num8num1raw4_answertrim_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge16_text3bit1num8num1raw4_answertrim_v1.csv`
- trigger: `launched immediately once reprobridge10 / reprobridge12 cuts and the light 2-lane eval wave left roughly PhysMem unused 251 GB, so the raw-numeric sibling did not wait for a further parent summary`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: `start from reprobridge15, keep the restored unit stabilizer a127eb72 and the low-hard-score hedge 8158a14c, trim two harder answer_only numeric rows plus two easy unit stabilizers, and replace them with four unused verified_trace_ready raw numeric_2x2 rows with generated CoT to test whether raw verified numeric depth beats selected-pool answer_only saturation`
- resulting_mix: `Bit 34 / Text 18 / Gravity 9 / Unit 7 / Equation 12`
- notes: `reprobridge16 is the first bridge sibling that explicitly steps outside the currently exhausted selected numeric pool while preserving the reprogap4 text/bit corrective skeleton; it removes answer_only numeric rows 9cb03277 and a19a75ba plus easy unit stabilizers 7291f716 and c1775d35, then adds raw verified numeric rows 118f8c86, 7195cb7b, 9b820b4e, and a8e033fe sourced from generated-CoT train splits; runtime preflight captured current_pid 8818 with PhysMem unused about 251 GB, GPU device util 100%, and in-use system memory about 130.65 GB at launch; the short train then closed with train_loss ≈ 0.3599 / val_loss ≈ 0.3957 / optimizer_step 8 / peak_memory ≈ 65.46 GB, but local320 finished at only 232/320 = 0.7250 (general 182/200, binary 30/60, symbol 20/60, text 32/50), so the lane was cut after only the first proxy chunk (10/16 = 0.625) instead of spending more memory on a below-threshold continuation`

### Manual queue note: `reprobridge17_text3bit1num8num1gravrestore_v1`

- status: `cut_after_local320_below_threshold`
- queued_at: `2026-04-11T22:47Z`
- launched_at: `2026-04-11T22:55Z`
- local320_completed_at: `2026-04-12T01:20Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge17_text3bit1num8num1gravrestore_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge17_text3bit1num8num1gravrestore_v1.csv`
- trigger: `launched immediately once reprobridge15 and reprobridge16 both opened strongly and host headroom returned to roughly PhysMem unused 252 GB, intentionally overriding the surviving wait-for-reprobridge15/16-summary queue while keeping the duplicate-safe waiters attached as no-op backups`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: `start from reprobridge15, remove one harder answer_only numeric row plus the low-hard-score hedge row, and restore two zero-hard-score gravity stabilizers to test whether the bridge wave benefits more from broader stabilizer recovery than from carrying the extra answer_only numeric burden`
- resulting_mix: `Bit 34 / Text 18 / Gravity 11 / Unit 9 / Equation 8`
- notes: `reprobridge17 is the stabilizer-restore sibling to reprobridge16's raw-numeric expansion; it removes numeric rows 9cb03277 and 8158a14c, restores gravity rows 853a0e3b and 66ae2b46, and serves as the low-risk fallback if the raw-verified numeric jump over-corrects toward equation-heavy behavior; runtime preflight captured current_pid 13023 with PhysMem unused about 252 GB, GPU device util 100%, and in-use system memory about 129.23 GB at launch; the short train then closed with train_loss ≈ 0.3504 / val_loss ≈ 0.3976 / optimizer_step 8 / peak_memory ≈ 65.46 GB, but local320 finished at only 227/320 = 0.7094 (general 175/200, binary 30/60, symbol 22/60, text 26/50), so the lane was cut before the first proxy chunk rather than spending more memory on another below-threshold continuation`

### Manual queue note: `reprobridge18_text3bit1num8num1raw2gravrestore_v1`

- status: `cut_after_local320_below_threshold`
- queued_at: `2026-04-11T22:59Z`
- launched_at: `2026-04-11T23:08Z`
- local320_completed_at: `2026-04-12T01:27Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge18_text3bit1num8num1raw2gravrestore_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge18_text3bit1num8num1raw2gravrestore_v1.csv`
- trigger: `launched immediately once the active wave still held roughly PhysMem unused 190 GB, intentionally overriding the wait-for-reprobridge15/16/17-summary queue while keeping the duplicate-safe waiters attached as no-op backups`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: `start from reprobridge15, keep the low-hard-score hedge 8158a14c, remove two harder answer_only numeric rows plus two easy unit stabilizers, then add two strongest unused raw verified numeric rows and two zero-hard-score gravity stabilizers; this is the balanced hybrid between reprobridge16's raw expansion and reprobridge17's pure stabilizer restore`
- resulting_mix: `Bit 34 / Text 18 / Gravity 11 / Unit 7 / Equation 10`
- notes: `reprobridge18 preserves the corrective reprogap4 text/bit skeleton and the 8158a14c hedge while moderating reprobridge16's equation-heavy jump; it removes 9cb03277, a19a75ba, 7291f716, and c1775d35, then adds raw verified numeric rows 118f8c86 and 7195cb7b plus restored gravity rows 853a0e3b and 66ae2b46; runtime preflight captured current_pid 17080 with PhysMem unused about 190 GB, GPU device util 100%, and in-use system memory about 193.36 GB at launch; the short train then closed with train_loss ≈ 0.3596 / val_loss ≈ 0.4478 / optimizer_step 8 / peak_memory ≈ 65.46 GB, but local320 finished at only 227/320 = 0.7094 (general 177/200, binary 30/60, symbol 20/60, text 27/50), so the lane was cut before the first proxy chunk rather than preserving a now-clearly losing hybrid branch`

### Manual queue note: `reprobridge19_text3bit1num8num1raw3grav1_v1`

- status: `cut_after_local320_below_threshold`
- queued_at: `2026-04-11T23:11Z`
- launched_at: `2026-04-11T23:53Z`
- training_completed_at: `2026-04-11T23:56Z`
- local320_completed_at: `2026-04-12T02:18Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge19_text3bit1num8num1raw3grav1_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge19_text3bit1num8num1raw3grav1_v1.csv`
- trigger: `manually launched once host headroom recovered to roughly PhysMem unused 154 GB / system_free_memory 51%, intentionally overriding the wait-for-reprobridge15/16/17/18-summary queue while keeping the duplicate-safe waiters alive as no-op backups`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: `start from reprobridge15, keep the hedge 8158a14c, remove two harder answer_only numeric rows plus two easy unit stabilizers, then add three strongest unused raw verified numeric rows and one zero-hard-score gravity stabilizer; this is the bridge between reprobridge16's raw4 push and reprobridge18's raw2+grav2 balance`
- resulting_mix: `Bit 34 / Text 18 / Gravity 10 / Unit 7 / Equation 11`
- notes: `reprobridge19 preserves the corrective reprogap4 text/bit skeleton while leaning slightly more equation-heavy than reprobridge18; it removes 9cb03277, a19a75ba, 7291f716, and c1775d35, then adds raw verified numeric rows 118f8c86, 7195cb7b, and 9b820b4e plus restored gravity row 853a0e3b; runtime preflight captured current_pid 30788 with PhysMem unused about 154 GB, system_free_memory 51%, GPU device util 100%, and in-use system memory about 257.48 GB at launch; the short train then closed with train_loss ≈ 0.3468 / val_loss ≈ 0.4527 / optimizer_step 8 / peak_memory ≈ 65.46 GB, but local320 ultimately finished at only 231/320 = 0.7219, so the lane was cut before leaderboard_proxy_v1_set could consume another heavy eval worker and the recovered headroom was immediately reused for reprobridge23`

### Manual queue note: `reprobridge20_text3bit1num8raw4grav1_hedgecut_v1`

- status: `launched_early_after_reprobridge16_cut`
- queued_at: `2026-04-11T23:49Z`
- launched_at: `2026-04-12T01:15Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge20_text3bit1num8raw4grav1_hedgecut_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge20_text3bit1num8raw4grav1_hedgecut_v1.csv`
- trigger: `original queue trigger was reprobridge19 full-suite summary plus free memory >= 150 GB, but after reprobridge16 was cut the host returned to PhysMem unused ≈ 194 GB, so this lane was started manually with the duplicate-safe launcher left in place as a no-op backup`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: `start from reprobridge19, drop the remaining low-hard-score answer_only hedge 8158a14c, and replace it with the strongest still-unused generated-COT-capable raw verified numeric row f94810f5; this preserves the single gravity restore from reprobridge19 while following the current live evidence that raw-heavy bridge siblings are staying cleaner than the hedge-heavy branch as local320 hardens`
- resulting_mix: `Bit 34 / Text 18 / Gravity 10 / Unit 7 / Equation 11`
- notes: `reprobridge20 is the hedge-cut continuation of the raw+gravity branch: it keeps the reprogap4 corrective text/bit skeleton, retains raw verified numeric rows 118f8c86, 7195cb7b, and 9b820b4e plus restored gravity row 853a0e3b, then swaps out hedge row 8158a14c for sourced raw verified numeric row f94810f5; f94810f5 was confirmed in generated-COT-capable sources including train_split_with_cot_v3f_one_shot_repair_v1.csv, train_split_with_cot_v2_plus_binary_route_aware.csv, and sampled_train_split_with_cot.csv; runtime preflight at manual early launch captured current_pid 54704 with PhysMem used ≈ 317 GB / unused ≈ 194 GB, GPU device util 100%, and in-use system memory ≈ 194.11 GB`

### Manual queue note: `reprobridge22_text3bit1num8raw5grav1_fullraw_v1`

- status: `launched_early_after_reprobridge18_cut`
- queued_at: `2026-04-12T00:27Z`
- launched_at: `2026-04-12T01:29Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge22_text3bit1num8raw5grav1_fullraw_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge22_text3bit1num8raw5grav1_fullraw_v1.csv`
- trigger: `original queue trigger was reprobridge20 full-suite summary plus free memory >= 150 GB, but after reprobridge18 was cut the host returned to PhysMem unused ≈ 251 GB while reprobridge20 had already opened 16/16, so this lane was started manually with the duplicate-safe launcher left in place as a no-op backup`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: `start from reprobridge20, drop the last remaining answer_only numeric row 9c8eef89, and replace it with the strongest still-unused generated-COT-capable raw verified numeric row a8e033fe; this preserves the single gravity restore from reprobridge19/20 while merging the last top raw row that already defined reprobridge16's strongest raw-heavy branch`
- resulting_mix: `Bit 34 / Text 18 / Gravity 10 / Unit 7 / Equation 11`
- notes: `reprobridge22 is the full-raw continuation of the raw+gravity branch: it keeps the reprogap4 corrective text/bit skeleton, retains raw verified numeric rows 118f8c86, 7195cb7b, 9b820b4e, and f94810f5 plus restored gravity row 853a0e3b, then swaps out the last answer_only numeric row 9c8eef89 for sourced raw verified numeric row a8e033fe; a8e033fe was confirmed in generated-COT-capable sources including train_split_with_cot_v3f_one_shot_repair_v1.csv, train_split_with_cot_v2_plus_binary_route_aware.csv, and sampled_train_split_with_cot.csv; runtime preflight at manual early launch captured current_pid 59249 with PhysMem used ≈ 259 GB / unused ≈ 251 GB, GPU device util 100%, and in-use system memory ≈ 129.21 GB`

### Manual queue note: `reprobridge21_text3bit1num8raw2grav1unitedge_v1`

- status: `launched_early_after_reprobridge22_train_handoff`
- queued_at: `2026-04-12T00:13Z`
- reordered_at: `2026-04-12T00:28Z`
- launched_at: `2026-04-12T01:34Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge21_text3bit1num8raw2grav1unitedge_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge21_text3bit1num8raw2grav1unitedge_v1.csv`
- trigger: `original trigger was reprobridge22 full-suite summary plus free memory >= 150 GB, but once reprobridge22 had finished train and the host still held PhysMem unused ≈ 191 GB, this final queued continuation was started manually with the duplicate-safe launcher left in place as a no-op backup`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: `start from reprobridge18, keep the raw2 branch and one restored gravity stabilizer, but trade the second zero-hard-score gravity row 66ae2b46 for the strongest still-unused generated-COT-capable ratio_edge unit row 0c26f842; this tests whether a harder unit hedge improves later hidden-tail robustness without giving up the strong raw2 balance`
- resulting_mix: `Bit 34 / Text 18 / Gravity 10 / Unit 8 / Equation 10`
- notes: `reprobridge21 was originally kept queued one step later behind reprobridge22 because the raw-heavy bridge family was still owning the cleaner live evidence than the unit-edge side hedge; it preserves raw verified numeric rows 118f8c86 and 7195cb7b plus restored gravity row 853a0e3b from reprobridge18, then swaps out gravity row 66ae2b46 for sourced unit row 0c26f842; 0c26f842 was confirmed in generated-COT-capable sources including train_split_with_cot_v2_plus_binary_route_aware.csv and sampled_train_split_with_cot.csv; runtime preflight at manual early launch captured current_pid 60884 with PhysMem used ≈ 320 GB / unused ≈ 191 GB, GPU device util 100%, and in-use system memory ≈ 193.38 GB`

### Manual queue note: `reprobridge23_text3bit1num8raw5unitedge_v1`

- status: `launched_early_after_reprobridge19_cut`
- queued_at: `2026-04-12T01:45Z`
- launched_at: `2026-04-12T02:20Z`
- training_completed_at: `2026-04-12T02:23Z`
- suite_started_at: `2026-04-12T02:23Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge23_text3bit1num8raw5unitedge_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge23_text3bit1num8raw5unitedge_v1.csv`
- trigger: `duplicate-safe launchers were originally armed behind the first full-suite summary from reprobridge19, reprobridge20, reprobridge21, or reprobridge22, but once reprobridge19 was cut the host immediately recovered to PhysMem unused ≈ 189 GB while reprobridge20 / reprobridge21 / reprobridge22 still held strong early scores, so this lane was manual early-launched with the remaining duplicate-safe launchers left in place as later no-op backups`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: `start from reprobridge22, keep the full raw verified numeric spine, but trade the last zero-hard-score gravity restore 853a0e3b for reprobridge21's harder ratio_edge unit row 0c26f842; this explicitly fuses the current full-raw mainline with the unit-edge side hedge to test whether later hidden-tail robustness benefits more from one hard unit anchor than from one easy gravity stabilizer once all answer_only numerics are already gone`
- resulting_mix: `Bit 34 / Text 18 / Gravity 9 / Unit 8 / Equation 11`
- notes: `reprobridge23 is the queue-refill cross between the two surviving design ideas: reprobridge22's full-raw backbone and reprobridge21's unit-edge hedge; it removes the remaining gravity restore 853a0e3b from reprobridge22, keeps raw verified numeric rows 118f8c86, 7195cb7b, 9b820b4e, f94810f5, and a8e033fe, and injects unit row 0c26f842 instead; runtime preflight at manual early launch captured current_pid 74969 with PhysMem used ≈ 322 GB / unused ≈ 189 GB, system_free_memory 62%, GPU device util 100%, and in-use system memory ≈ 194.06 GB; the short train then closed almost immediately with train_loss ≈ 0.3439 / val_loss ≈ 0.3951 / optimizer_step 8 / peak_memory ≈ 65.46 GB, and the pre-armed postprocess chain has already started `eval_suite_readme_proxy_specialized` on the target root (`readme_local320` 0/320 at handoff), so the bridge queue remains live without waiting for another full-suite summary to free memory; later audit of the run root showed `prepare_manifest.sampled_rows = 79`, because 0c26f842 had blank generated_cot/type in the artifact CSV and was silently skipped by the loader, so treat reprobridge23 as a useful but imperfect early diagnostic rather than the exact intended 80-row unitedge fusion`

### Manual queue note: `reprobridge24_text3bit1num8raw6_nograv_v1`

- status: `queued_behind_reprobridge23_full_suite_summary`
- queued_at: `2026-04-12T01:46Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge24_text3bit1num8raw6nograv_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge24_text3bit1num8raw6_nograv_v1.csv`
- trigger: `queued one step behind reprobridge23 full-suite summary, again with duplicate-safe start guards and the conservative free-memory gate of PhysMem unused >= 150 GB`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: `start from reprobridge22, drop the last remaining easy gravity restore 853a0e3b, and replace it with the strongest still-unused generated-COT-capable verified numeric_2x2 row dfec0ed4; this is the aggressive continuation of the raw-heavy line and tests whether the branch can push one step past fullraw now that every answer_only numeric row has already been removed`
- resulting_mix: `Bit 34 / Text 18 / Gravity 9 / Unit 7 / Equation 12`
- notes: `reprobridge24 keeps the reprogap4 corrective bit/text skeleton and all five full-raw numeric rows from reprobridge22, then swaps the final gravity restore for unused raw verified numeric row dfec0ed4, which is present in train_split_with_cot_v3f_one_shot_repair_v1.csv, train_split_with_cot_v2_plus_binary_route_aware.csv, the broad-v3f sampled_train_split_with_cot.csv, and baseline train_split_with_cot.csv; a later artifact audit found dfec0ed4 missing type/generated_cot in the queued-only CSV, so the train CSV was repaired in place from baseline train_split_with_cot.csv before launch; duplicate-safe live-poller, postprocess, and threshold waiters are already armed on the target root so the queue can keep extending even if reprobridge23 itself is later manual-launched early`

### Manual queue note: `reprobridge25_text3bit1num8raw6unitedge_v1`

- status: `queued_behind_reprobridge24_full_suite_summary`
- queued_at: `2026-04-12T02:07Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge25_text3bit1num8raw6unitedge_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge25_text3bit1num8raw6unitedge_v1.csv`
- trigger: `queued one step behind reprobridge24 full-suite summary, again guarded by duplicate-safe launchers and the conservative free-memory band of PhysMem unused >= 150 GB`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: `start from reprobridge23, keep the injected ratio_edge unit hedge 0c26f842, but swap one weakest remaining ratio_lt2 unit stabilizer f9103e02 for the strongest still-unused generated-COT-capable verified numeric_2x2 row 791fc537; this explicitly fuses reprobridge23's unit-edge hedge with reprobridge24's raw6 push instead of forcing an either-or choice`
- resulting_mix: `Bit 34 / Text 18 / Gravity 9 / Unit 7 / Equation 12`
- notes: `reprobridge25 is the deeper continuation after the queue-refill pair: it starts from reprobridge23, preserves raw verified numeric rows 118f8c86, 7195cb7b, 9b820b4e, f94810f5, and a8e033fe plus unit-edge row 0c26f842, then removes weak ratio_lt2 unit row f9103e02 in favor of unused raw verified numeric row 791fc537; 791fc537 was confirmed in train_split_with_cot_v3f_one_shot_repair_v1.csv, train_split_with_cot_v2_plus_binary_route_aware.csv, the broad-v3f sampled_train_split_with_cot.csv, and baseline train_split_with_cot.csv; a later artifact audit found that both 0c26f842 and 791fc537 had landed in the queued-only CSV without complete type/generated_cot fields, so the train CSV was repaired in place from baseline train_split_with_cot.csv before launch; duplicate-safe launch, live-poller, postprocess, and threshold waiters are all now armed on the target root so the bridge queue can continue beyond reprobridge24 without another manual wiring pass`

### Manual queue note: `reprobridge26_text3bit1num8raw7unitedge_v1`

- status: `queued_behind_reprobridge25_full_suite_summary`
- queued_at: `2026-04-12T02:43Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge26_text3bit1num8raw7unitedge_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge26_text3bit1num8raw7unitedge_v1.csv`
- trigger: `queued one step behind reprobridge25 full-suite summary, again guarded by duplicate-safe launchers and the conservative free-memory band of PhysMem unused >= 150 GB`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: `start from reprobridge25, keep the injected ratio_edge unit hedge 0c26f842 and the first extra raw verified numeric row 791fc537, but swap another weakest remaining ratio_lt2 unit stabilizer a127eb72 for reprobridge24's generated-COT-capable verified numeric_2x2 row dfec0ed4; this is the next raw-heavy continuation because it merges the two queued raw6 branches instead of forcing an either-or choice between them`
- resulting_mix: `Bit 34 / Text 18 / Gravity 9 / Unit 6 / Equation 13`
- notes: `reprobridge26 is the triple-fusion continuation after reprobridge24 and reprobridge25: it starts from reprobridge25, preserves raw verified numeric rows 118f8c86, 7195cb7b, 9b820b4e, f94810f5, a8e033fe, and 791fc537 plus unit-edge row 0c26f842, then removes weak ratio_lt2 unit row a127eb72 in favor of dfec0ed4 from the reprobridge24 raw6-nograv branch; dfec0ed4 was confirmed in train_split_with_cot_v3f_one_shot_repair_v1.csv, train_split_with_cot_v2_plus_binary_route_aware.csv, and baseline train_split_with_cot.csv; a later artifact audit found that 0c26f842, 791fc537, and dfec0ed4 needed full type/generated_cot backfill in the queued-only CSV, so the train CSV was repaired in place from baseline train_split_with_cot.csv before launch; duplicate-safe launch, live-poller, postprocess, and threshold waiters can extend the bridge queue one more step without leaving the generated-COT-capable source family`

### Manual queue note: `reprobridge27_text3bit1num8raw8unitedge_v1`

- status: `queued_behind_reprobridge26_full_suite_summary`
- queued_at: `2026-04-12T03:27Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge27_text3bit1num8raw8unitedge_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge27_text3bit1num8raw8unitedge_v1.csv`
- trigger: `queued one step behind reprobridge26 full-suite summary, again guarded by duplicate-safe launchers and the conservative free-memory band of PhysMem unused >= 150 GB`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: `start from repaired reprobridge26, keep the injected ratio_edge unit hedge 0c26f842 and both extra raw verified numeric rows 791fc537 and dfec0ed4, but swap another weakest remaining ratio_lt2 unit stabilizer dae6dea8 for stronger verified numeric_2x2 row 8c6a158e from the rule-based verified COT source; this is the next raw-heavy continuation once the queue has already merged reprobridge24 and reprobridge25`
- resulting_mix: `Bit 34 / Text 18 / Gravity 9 / Unit 5 / Equation 14`
- notes: `reprobridge27 is the raw8 continuation after the repaired reprobridge26 queue: it preserves raw verified numeric rows 118f8c86, 7195cb7b, 9b820b4e, f94810f5, a8e033fe, 791fc537, dfec0ed4, plus unit-edge row 0c26f842, then removes weak ratio_lt2 unit row dae6dea8 in favor of 8c6a158e from baseline/cot/output-csv/rule_based_verified_600_training_data_v2.csv; this intentionally steps outside the current route-aware/v3f source trio for one stronger rule-based verified raw row while keeping the rest of the queue on generated-COT-capable train_split_with_cot sources; duplicate-safe launcher, live-poller, postprocess, and 0.75/0.80 threshold waiters are now armed on the target root behind reprobridge26 full-suite completion`

### Manual queue note: `reprobridge28_text3bit1num8raw9unitedge_v1`

- status: `queued_behind_reprobridge27_full_suite_summary`
- queued_at: `2026-04-12T03:43Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge28_text3bit1num8raw9unitedge_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge28_text3bit1num8raw9unitedge_v1.csv`
- trigger: `queued one step behind reprobridge27 full-suite summary, again guarded by duplicate-safe launchers and the conservative free-memory band of PhysMem unused >= 150 GB`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: `start from reprobridge27, keep only the hardest remaining ratio_edge unit hedge 0c26f842 together with the growing raw verified numeric spine, but swap another weak ratio_lt2 unit stabilizer e346233f for stronger verified numeric_2x2 row db6a5663 from the rule-based verified COT source; this continues the raw-heavy bridge one step further without dropping the final hard unit-edge anchor`
- resulting_mix: `Bit 34 / Text 18 / Gravity 9 / Unit 4 / Equation 15`
- notes: `reprobridge28 is the raw9 continuation after reprobridge27: it preserves raw verified numeric rows 118f8c86, 7195cb7b, 9b820b4e, f94810f5, a8e033fe, 791fc537, dfec0ed4, 8c6a158e, plus unit-edge row 0c26f842, then removes weak ratio_lt2 unit row e346233f in favor of db6a5663 from baseline/cot/output-csv/rule_based_verified_600_training_data_v2.csv; this pushes the queue one more step outside the current route-aware/v3f source trio while still leaving one hard unit-edge stabilizer in place; duplicate-safe launcher, live-poller, postprocess, and 0.75/0.80 threshold waiters are now armed on the target root behind reprobridge27 full-suite completion`

### Manual queue note: `reprobridge29_text3bit1num8raw10unitedge_v1`

- status: `queued_behind_reprobridge28_full_suite_summary`
- queued_at: `2026-04-12T03:18Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge29_text3bit1num8raw10unitedge_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge29_text3bit1num8raw10unitedge_v1.csv`
- trigger: `queued one step behind reprobridge28 full-suite summary, again guarded by duplicate-safe launchers and the conservative free-memory band of PhysMem unused >= 150 GB`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: `start from reprobridge28, keep the hard unit-edge hedge 0c26f842 and the remaining stronger unit stabilizers, but swap the weakest remaining unit row 2af08815 for the highest-hard-score still-unused verified numeric_2x2 row 1f445c5e from baseline train_split_with_cot.csv; this deepens the raw-heavy bridge while stepping back inside the generated-COT-safe source family after the two rule-based additions`
- resulting_mix: `Bit 34 / Text 18 / Gravity 9 / Unit 3 / Equation 16`
- notes: `reprobridge29 is the raw10 continuation after reprobridge28: it preserves the raw verified numeric spine 118f8c86, 7195cb7b, 9b820b4e, f94810f5, a8e033fe, 791fc537, dfec0ed4, 8c6a158e, db6a5663, plus the hard unit-edge row 0c26f842 and remaining unit stabilizers 95e8326c and 3f37b894, then removes weak unit row 2af08815 in favor of 1f445c5e from baseline/nemotron-sft-lora-with-cot-v2/artifacts/train_split_with_cot.csv; duplicate-safe launcher, live-poller, postprocess, and 0.75/0.80 threshold waiters are now armed on the target root behind reprobridge28 full-suite completion`

### Manual queue note: `reprobridge30_text3bit1num8raw11unitedge_v1`

- status: `queued_behind_reprobridge29_full_suite_summary`
- queued_at: `2026-04-12T03:18Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge30_text3bit1num8raw11unitedge_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge30_text3bit1num8raw11unitedge_v1.csv`
- trigger: `queued one step behind reprobridge29 full-suite summary, again guarded by duplicate-safe launchers and the conservative free-memory band of PhysMem unused >= 150 GB`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: `start from reprobridge29, keep the hard unit-edge hedge 0c26f842 and the last stronger unit stabilizer 3f37b894, but swap the remaining hard-2 unit row 95e8326c for the next highest-hard-score still-unused verified numeric_2x2 row 2f485a40 from baseline train_split_with_cot.csv; this extends the raw-heavy bridge another step while still leaving two unit anchors in place`
- resulting_mix: `Bit 34 / Text 18 / Gravity 9 / Unit 2 / Equation 17`
- notes: `reprobridge30 is the raw11 continuation after reprobridge29: it preserves the entire raw verified numeric spine from reprobridge29 plus unit anchors 3f37b894 and 0c26f842, then removes weak unit row 95e8326c in favor of 2f485a40 from baseline/nemotron-sft-lora-with-cot-v2/artifacts/train_split_with_cot.csv; this is the deepest queued continuation so far and keeps the bridge queue populated two steps beyond reprobridge28 without leaving the generated-COT-safe source family; duplicate-safe launcher, live-poller, postprocess, and 0.75/0.80 threshold waiters are now armed on the target root behind reprobridge29 full-suite completion`

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxymiss40_text20_grav15_unit15_sym8_lr2e6_len1536_v1 -->
### Auto result: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxymiss40_text20_grav15_unit15_sym8_lr2e6_len1536_v1`

- recorded_at: `2026-04-12T04:12:42.509379+00:00`
- label: `o30best_proxymiss40_text20_grav15_unit15_sym8_lr2e6_v1`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxymiss40_text20_grav15_unit15_sym8_lr2e6_len1536_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage2_o30best_proxymiss40_text20_grav15_unit15_sym8_v1.csv`
- sampled_rows: `98`
- optimizer_steps: `16`
- lr: `2e-06`
- max_seq_length: `1536`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Scores

- readme_local320: `232/320 = 0.7250`
- local320_components: `general_stable_set 182/200 = 0.9100; binary_hard_set 29/60 = 0.4833; symbol_watch_set 21/60 = 0.3500`
- leaderboard_proxy_v1_set: `130/200 = 0.6500`

#### Submission audit

- audit_status: `potentially_exportable_2d_only`
- peft_export_ready: `True`
- tensor_count: `232`

#### Submission export

- submission_zip: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxymiss40_text20_grav15_unit15_sym8_lr2e6_len1536_v1/submission_export/submission.zip`
- zip_size_bytes: `102356734`
- validation_valid: `True`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxymiss40_text20_grav15_unit15_sym8_lr2e6_len1536_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_ep12_len1024_from_proxymiss_v1 -->
### Auto result: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_ep12_len1024_from_proxymiss_v1`

- recorded_at: `2026-04-12T04:12:46.170653+00:00`
- label: `o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_ep12_v1`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_ep12_len1024_from_proxymiss_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_binary10_text10_grav15_unit15_v1.csv`
- sampled_rows: `80`
- optimizer_steps: `12`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Scores

- readme_local320: `230/320 = 0.7188`
- local320_components: `general_stable_set 179/200 = 0.8950; binary_hard_set 29/60 = 0.4833; symbol_watch_set 22/60 = 0.3667`
- leaderboard_proxy_v1_set: `127/200 = 0.6350`

#### Submission audit

- audit_status: `potentially_exportable_2d_only`
- peft_export_ready: `True`
- tensor_count: `232`

#### Submission export

- submission_zip: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_ep12_len1024_from_proxymiss_v1/submission_export/submission.zip`
- zip_size_bytes: `102356385`
- validation_valid: `True`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_ep12_len1024_from_proxymiss_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_verifiedswap22_eq12anchortrim_lr1e6_len1024_from_proxybench_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_verifiedswap22_eq12anchortrim_lr1e6_len1024_from_proxybench_v1`

- status: `paused_memory_cut`
- label: `o30best-verifiedswap22-eq12anchortrim-v1-live`
- observed_at: `2026-04-11T17:28:21.583398+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_verifiedswap22_eq12anchortrim_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_verifiedswap22_eq12anchortrim_v1.csv`
- sampled_rows: `80`
- optimizer_progress: `0/8 = 0.00%`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_verifiedswap22_eq12anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_verifiedswap22_eq12anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized`
- suite_evaluations: `0/2 = 0.00%`
- current_evaluation: `readme_local320`
- current_rows_progress: `192/320 = 60.00%`
- current_chunks_progress: `12/20 = 60.00%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_verifiedswap22_eq12anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/readme_local320/benchmark_eval_progress.json`
- accuracy_so_far: `0.8906`
- correct_so_far: `171`
- manual_cut_note: `Heavy eq12anchortrim eval was stopped after numreal8 launch pushed host memory to about PhysMem 463G used / 48G unused. Rerun remains possible from existing artifacts.`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `84126`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_verifiedswap22_eq12anchortrim_lr1e6_len1024_from_proxybench_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b20_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1 -->
### Auto result: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b20_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1`

- recorded_at: `2026-04-12T04:12:56.907941+00:00`
- label: `o30best_proxybench30ao_b20_t10_g15_u15_lr1e6_v1`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b20_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_binary20_text10_grav15_unit15_v1.csv`
- sampled_rows: `90`
- optimizer_steps: `9`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Scores

- readme_local320: `229/320 = 0.7156`
- local320_components: `general_stable_set 177/200 = 0.8850; binary_hard_set 29/60 = 0.4833; symbol_watch_set 23/60 = 0.3833`
- leaderboard_proxy_v1_set: `125/200 = 0.6250`

#### Submission audit

- audit_status: `potentially_exportable_2d_only`
- peft_export_ready: `True`
- tensor_count: `232`

#### Submission export

- submission_zip: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b20_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1/submission_export/submission.zip`
- zip_size_bytes: `102356554`
- validation_valid: `True`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b20_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_text060_num100_grav20_unit20_recover_lr4e6_len1024_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_text060_num100_grav20_unit20_recover_lr4e6_len1024_v1`

- status: `evaluating`
- label: `o30_general_recover_t060_n100_g20_u20`
- observed_at: `2026-04-11T06:18:26.528278+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_text060_num100_grav20_unit20_recover_lr4e6_len1024_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_text060_num100_grav20_unit20_recover_v1.csv`
- sampled_rows: `200`
- optimizer_progress: `0/8 = 0.00%`
- lr: `4e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_text060_num100_grav20_unit20_recover_lr4e6_len1024_v1/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_text060_num100_grav20_unit20_recover_lr4e6_len1024_v1/eval_suite_readme_proxy_specialized`
- suite_evaluations: `1/2 = 50.00%`
- current_evaluation: `leaderboard_proxy_v1_set`
- current_rows_progress: `0/200 = 0.00%`
- current_chunks_progress: `0/13 = 0.00%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_text060_num100_grav20_unit20_recover_lr4e6_len1024_v1/eval_suite_readme_proxy_specialized/leaderboard_proxy_v1_set/benchmark_eval_progress.json`
- completed_evaluations: `['readme_local320']`
- completed_evaluation_scores: `readme_local320 228/320 = 0.7125`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `99469`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_text060_num100_grav20_unit20_recover_lr4e6_len1024_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv130_bin40proxyo30p0s10_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1 -->
### Auto result: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv130_bin40proxyo30p0s10_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1`

- recorded_at: `2026-04-12T04:13:17.799031+00:00`
- label: `binary40_o30_p0_s10_no_lz`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv130_bin40proxyo30p0s10_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_text_verified130_binary40proxyo30p0s10_grav15_unit15_rowselect_v1.csv`
- sampled_rows: `200`
- optimizer_steps: `12`
- lr: `8e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Scores

- readme_local320: `231/320 = 0.7219`
- local320_components: `general_stable_set 180/200 = 0.9000; binary_hard_set 28/60 = 0.4667; symbol_watch_set 23/60 = 0.3833`
- leaderboard_proxy_v1_set: `130/200 = 0.6500`

#### Submission audit

- audit_status: `potentially_exportable_2d_only`
- peft_export_ready: `True`
- tensor_count: `232`

#### Submission export

- submission_zip: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv130_bin40proxyo30p0s10_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1/submission_export/submission.zip`
- zip_size_bytes: `102356609`
- validation_valid: `True`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv130_bin40proxyo30p0s10_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_text040_num120_grav20_unit20_recover_lr4e6_len1024_v1 -->
### Auto result: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_text040_num120_grav20_unit20_recover_lr4e6_len1024_v1`

- recorded_at: `2026-04-12T04:13:23.370311+00:00`
- label: `o30_general_recover_t040_n120_g20_u20`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_text040_num120_grav20_unit20_recover_lr4e6_len1024_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_text040_num120_grav20_unit20_recover_v1.csv`
- sampled_rows: `200`
- optimizer_steps: `8`
- lr: `4e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Scores

- readme_local320: `231/320 = 0.7219`
- local320_components: `general_stable_set 182/200 = 0.9100; binary_hard_set 28/60 = 0.4667; symbol_watch_set 21/60 = 0.3500`
- leaderboard_proxy_v1_set: `127/200 = 0.6350`

#### Submission audit

- audit_status: `blocked_routed_expert_3d_tensors`
- peft_export_ready: `False`
- tensor_count: `324`
- blocked_reasons: `['MLX adapter contains non-2D LoRA tensors; PEFT/vLLM-equivalent export is not claimed without a verified mapping.', 'switch_mlp routed-expert tensors are 3D in this adapter, so the current single-file pipeline blocks submission export instead of guessing a PEFT layout.']`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_text040_num120_grav20_unit20_recover_lr4e6_len1024_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_text150_bin10p5s5_lzgrav15_unit15_binaryaware_lr4e6_len1024_v3 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_text150_bin10p5s5_lzgrav15_unit15_binaryaware_lr4e6_len1024_v3`

- status: `evaluating`
- label: `o30best_binaryaware_t150_b10p5s5_lz_g15_u15_v3`
- observed_at: `2026-04-11T07:51:10.189025+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_text150_bin10p5s5_lzgrav15_unit15_binaryaware_lr4e6_len1024_v3`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_text150_bin10p5s5_lzgrav15_unit15_binaryaware_v1.csv`
- sampled_rows: `200`
- optimizer_progress: `0/8 = 0.00%`
- lr: `4e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_text150_bin10p5s5_lzgrav15_unit15_binaryaware_lr4e6_len1024_v3/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_text150_bin10p5s5_lzgrav15_unit15_binaryaware_lr4e6_len1024_v3/eval_suite_readme_proxy_specialized`
- suite_evaluations: `1/2 = 50.00%`
- current_evaluation: `leaderboard_proxy_v1_set`
- current_rows_progress: `0/200 = 0.00%`
- current_chunks_progress: `0/13 = 0.00%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_text150_bin10p5s5_lzgrav15_unit15_binaryaware_lr4e6_len1024_v3/eval_suite_readme_proxy_specialized/leaderboard_proxy_v1_set/benchmark_eval_progress.json`
- accuracy_so_far: `0.0000`
- correct_so_far: `0`
- completed_evaluations: `['readme_local320']`
- completed_evaluation_scores: `readme_local320 220/320 = 0.6875`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `37561`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_text150_bin10p5s5_lzgrav15_unit15_binaryaware_lr4e6_len1024_v3 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_verifiedswap22_sym9_lr1e6_len1024_from_proxybench_v2 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_verifiedswap22_sym9_lr1e6_len1024_from_proxybench_v2`

- status: `paused_memory_cut`
- label: `o30best-verifiedswap22-sym9-v2-eval-live`
- observed_at: `2026-04-11T17:54:11+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_verifiedswap22_sym9_lr1e6_len1024_from_proxybench_v2`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_verifiedswap22_sym9_v1.csv`
- sampled_rows: `80`
- optimizer_progress: `0/8 = 0.00%`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_verifiedswap22_sym9_lr1e6_len1024_from_proxybench_v2/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_verifiedswap22_sym9_lr1e6_len1024_from_proxybench_v2/eval_suite_readme_proxy_specialized`
- suite_evaluations: `1/2 = 50.00%`
- current_evaluation: `leaderboard_proxy_v1_set`
- current_rows_progress: `0/200 = 0.00%`
- current_chunks_progress: `0/13 = 0.00%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_verifiedswap22_sym9_lr1e6_len1024_from_proxybench_v2/eval_suite_readme_proxy_specialized/leaderboard_proxy_v1_set/benchmark_eval_progress.json`
- accuracy_so_far: `0.0000`
- correct_so_far: `0`
- completed_evaluations: `['readme_local320']`
- completed_evaluation_scores: `readme_local320 223/320 = 0.6969`
- manual_cut_note: `sym9 reached local320 223/320, so it would need 13/16 remaining tail hits to beat the tracked 235/320 frontier; proxy continuation was intentionally cut after the local summary landed to free headroom for the queued reprogap4 lane once bit33 local summary appears`
- post_cut_memory_note: `after killing the sym9 postprocess + live poller workers, host headroom recovered to roughly PhysMem unused 145 GB`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `74384`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_verifiedswap22_sym9_lr1e6_len1024_from_proxybench_v2 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv130_bin40proxyo30p0s10_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_repro_v1 -->
### Auto result: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv130_bin40proxyo30p0s10_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_repro_v1`

- recorded_at: `2026-04-12T04:13:37.842588+00:00`
- label: `o30best_local_best_actual_repro_v1`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv130_bin40proxyo30p0s10_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_repro_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_text_verified130_binary40proxyo30p0s10_grav15_unit15_rowselect_v1_repro_v1.csv`
- sampled_rows: `200`
- optimizer_steps: `12`
- lr: `8e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Scores

- readme_local320: `227/320 = 0.7094`
- local320_components: `general_stable_set 178/200 = 0.8900; binary_hard_set 29/60 = 0.4833; symbol_watch_set 20/60 = 0.3333`
- leaderboard_proxy_v1_set: `125/200 = 0.6250`

#### Submission audit

- audit_status: `potentially_exportable_2d_only`
- peft_export_ready: `True`
- tensor_count: `232`

#### Submission export

- submission_zip: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv130_bin40proxyo30p0s10_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_repro_v1/submission_export/submission.zip`
- zip_size_bytes: `102356099`
- validation_valid: `True`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv130_bin40proxyo30p0s10_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_repro_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_repro_v1 -->
### Auto result: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_repro_v1`

- recorded_at: `2026-04-12T04:12:43.723825+00:00`
- label: `o30best-proxybench-repro-eval-live`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_repro_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_binary10_text10_grav15_unit15_v1_repro_v1.csv`
- sampled_rows: `80`
- optimizer_steps: `8`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Scores

- readme_local320: `227/320 = 0.7094`
- local320_components: `general_stable_set 176/200 = 0.8800; binary_hard_set 30/60 = 0.5000; symbol_watch_set 21/60 = 0.3500`
- leaderboard_proxy_v1_set: `128/200 = 0.6400`

#### Submission audit

- audit_status: `potentially_exportable_2d_only`
- peft_export_ready: `True`
- tensor_count: `232`

#### Submission export

- submission_zip: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_repro_v1/submission_export/submission.zip`
- zip_size_bytes: `102356933`
- validation_valid: `True`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_repro_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_bit33_numreal8_anchortrim_lr1e6_len1024_from_proxybench_v2 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_bit33_numreal8_anchortrim_lr1e6_len1024_from_proxybench_v2`

- status: `evaluating`
- label: `o30best-bit33-numreal8-anchortrim-v2-live`
- observed_at: `2026-04-11T20:04:54.160553+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_bit33_numreal8_anchortrim_lr1e6_len1024_from_proxybench_v2`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_bit33_numreal8_anchortrim_v1.csv`
- sampled_rows: `80`
- optimizer_progress: `0/8 = 0.00%`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_bit33_numreal8_anchortrim_lr1e6_len1024_from_proxybench_v2/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_bit33_numreal8_anchortrim_lr1e6_len1024_from_proxybench_v2/eval_suite_readme_proxy_specialized`
- suite_evaluations: `1/2 = 50.00%`
- current_evaluation: `leaderboard_proxy_v1_set`
- current_rows_progress: `0/200 = 0.00%`
- current_chunks_progress: `0/13 = 0.00%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_bit33_numreal8_anchortrim_lr1e6_len1024_from_proxybench_v2/eval_suite_readme_proxy_specialized/leaderboard_proxy_v1_set/benchmark_eval_progress.json`
- accuracy_so_far: `0.0000`
- correct_so_far: `0`
- completed_evaluations: `['readme_local320']`
- completed_evaluation_scores: `readme_local320 226/320 = 0.7063`
- manual_cut_note: `numreal8 completed readme_local320 at 226/320, below both the tracked 235/320 frontier and the 0.75 threshold gate, so its proxy continuation was intentionally terminated to preserve headroom for reprogap4, reprogap5, and reprobridge9`
- post_cut_memory_note: `after killing the numreal8 postprocess worker, live poller, and numreal8-specific threshold waiter, host headroom recovered to roughly PhysMem unused 141 GB`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `14351`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_bit33_numreal8_anchortrim_lr1e6_len1024_from_proxybench_v2 -->

<!-- auto-run-summary:start:best-submission-candidate -->
### Auto best submission candidate

- recorded_at: `2026-04-12T04:13:38.308054+00:00`
- status: `selected_candidate`
- candidate_count: `34`
- eligible_candidate_count: `3`
- gates: `{'min_local320_accuracy': 0.7, 'min_general_stable_accuracy': 0.9, 'min_proxy_v2_accuracy': 0.0, 'min_specialized_accuracy': 0.0, 'require_exportable': True}`

- selected_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1`
- local320: `235/320 = 0.7344`
- general_stable: `183/200 = 0.9150`
- leaderboard_proxy_v1_set: `131/200 = 0.6550`
- leaderboard_proxy_v2: `0/0 = 0.0000`
- binary_bias_specialized_set: `0/0 = 0.0000`
- audit_status: `potentially_exportable_2d_only`
- submission_zip: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/best_submission_candidate_proxybench_auto/submission.zip`

| run_name | local320 | general_stable | proxy_v1 | proxy_v2 | specialized | exportable |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1` | 0.7344 | 0.9150 | 0.6550 | 0.0000 | 0.0000 | `True` |
| `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxymiss40_text20_grav15_unit15_sym8_lr2e6_len1536_v1` | 0.7250 | 0.9100 | 0.6500 | 0.0000 | 0.0000 | `True` |
| `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_text040_num120_grav20_unit20_recover_lr4e6_len1024_v1` | 0.7219 | 0.9100 | 0.6350 | 0.0000 | 0.0000 | `False` |
| `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv130_bin40proxyo30p0s10_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1` | 0.7219 | 0.9000 | 0.6500 | 0.0000 | 0.0000 | `True` |
| `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_ep12_len1024_from_proxymiss_v1` | 0.7188 | 0.8950 | 0.6350 | 0.0000 | 0.0000 | `True` |
| `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b20_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1` | 0.7156 | 0.8850 | 0.6250 | 0.0000 | 0.0000 | `True` |
| `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv130_bin40proxyo20p5s15_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1` | 0.7156 | 0.8800 | 0.6450 | 0.0000 | 0.0000 | `True` |
| `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_text100_num60_grav20_unit20_recover_lr4e6_len1024_v1` | 0.7125 | 0.9000 | 0.6200 | 0.0000 | 0.0000 | `False` |
<!-- auto-run-summary:end:best-submission-candidate -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_bit33_numreal5_anchortrim_lr1e6_len1024_from_proxybench_v2 -->
### Auto result: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_bit33_numreal5_anchortrim_lr1e6_len1024_from_proxybench_v2`

- recorded_at: `2026-04-12T02:45:57.268143+00:00`
- label: `o30best-bit33-numreal5-anchortrim-v2-live`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_bit33_numreal5_anchortrim_lr1e6_len1024_from_proxybench_v2`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_bit33_numreal5_anchortrim_v1.csv`
- sampled_rows: `80`
- optimizer_steps: `8`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Scores

- readme_local320: `226/320 = 0.7063`
- local320_components: `general_stable_set 175/200 = 0.8750; binary_hard_set 30/60 = 0.5000; symbol_watch_set 21/60 = 0.3500`
- leaderboard_proxy_v1_set: `129/200 = 0.6450`

#### Submission audit

- audit_status: `potentially_exportable_2d_only`
- peft_export_ready: `True`
- tensor_count: `232`

#### Submission export

- submission_zip: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_bit33_numreal5_anchortrim_lr1e6_len1024_from_proxybench_v2/submission_export/submission.zip`
- zip_size_bytes: `102356798`
- validation_valid: `True`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_bit33_numreal5_anchortrim_lr1e6_len1024_from_proxybench_v2 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_bit33_numreal5_verifiedmix_lr1e6_len1024_from_proxybench_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_bit33_numreal5_verifiedmix_lr1e6_len1024_from_proxybench_v1`

- status: `paused_memory_cut`
- label: `o30best-bit33-numreal5-verifiedmix-v1-live`
- observed_at: `2026-04-11T18:05:07+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_bit33_numreal5_verifiedmix_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_bit33_numreal5_verifiedmix_v1.csv`
- sampled_rows: `80`
- optimizer_progress: `0/8 = 0.00%`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_bit33_numreal5_verifiedmix_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_bit33_numreal5_verifiedmix_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized`
- suite_evaluations: `0/2 = 0.00%`
- current_evaluation: `readme_local320`
- current_rows_progress: `32/320 = 10.00%`
- current_chunks_progress: `2/20 = 10.00%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_bit33_numreal5_verifiedmix_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/readme_local320/benchmark_eval_progress.json`
- accuracy_so_far: `1.0000`
- correct_so_far: `32`
- manual_cut_note: `verifiedmix had only reached local320 32/320 when reprogap5 training plus the rest of the active wave drove host headroom down to roughly PhysMem unused 48 GB; it was intentionally cut so the broader numreal8 lane and both reprogap targeted bridges could continue safely`
- post_cut_memory_note: `after killing the verifiedmix postprocess + live poller workers, host headroom recovered to roughly PhysMem unused 107 GB`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `8973`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_bit33_numreal5_verifiedmix_lr1e6_len1024_from_proxybench_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprogap4_text3bit1_anchortrim_lr1e6_len1024_from_proxybench_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprogap4_text3bit1_anchortrim_lr1e6_len1024_from_proxybench_v1`

- status: `evaluating`
- label: `reprogap4 targeted bridge`
- observed_at: `2026-04-11T20:39:53.361972+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprogap4_text3bit1_anchortrim_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprogap4_text3bit1_anchortrim_v1.csv`
- sampled_rows: `80`
- optimizer_progress: `0/8 = 0.00%`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprogap4_text3bit1_anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprogap4_text3bit1_anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized`
- suite_evaluations: `1/2 = 50.00%`
- current_evaluation: `leaderboard_proxy_v1_set`
- current_rows_progress: `0/200 = 0.00%`
- current_chunks_progress: `0/13 = 0.00%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprogap4_text3bit1_anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/leaderboard_proxy_v1_set/benchmark_eval_progress.json`
- accuracy_so_far: `0.0000`
- correct_so_far: `0`
- completed_evaluations: `['readme_local320']`
- completed_evaluation_scores: `readme_local320 229/320 = 0.7156`
- manual_cut_note: `reprogap4 was intentionally cut immediately after local320 completed at 229/320 because the exact-gap bridge still finished below the tracked 235/320 frontier and below the 0.75 threshold gate, making further proxy evaluation lower EV than reallocating memory to reprobridge10 and reprobridge12`
- post_cut_memory_note: `after killing the reprogap4 postprocess worker, live poller, and reprogap4-specific threshold waiter, host headroom recovered to roughly PhysMem unused 192 GB`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `23801`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprogap4_text3bit1_anchortrim_lr1e6_len1024_from_proxybench_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprogap5_text3bit1num1_anchortrim_lr1e6_len1024_from_proxybench_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprogap5_text3bit1num1_anchortrim_lr1e6_len1024_from_proxybench_v1`

- status: `evaluating`
- label: `reprogap5 numeric hedge`
- observed_at: `2026-04-11T20:29:45.531706+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprogap5_text3bit1num1_anchortrim_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprogap5_text3bit1num1_anchortrim_v1.csv`
- sampled_rows: `80`
- optimizer_progress: `0/8 = 0.00%`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprogap5_text3bit1num1_anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprogap5_text3bit1num1_anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized`
- suite_evaluations: `0/2 = 0.00%`
- current_evaluation: `readme_local320`
- current_rows_progress: `304/320 = 95.00%`
- current_chunks_progress: `19/20 = 95.00%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprogap5_text3bit1num1_anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/readme_local320/benchmark_eval_progress.json`
- accuracy_so_far: `0.7401`
- correct_so_far: `225`
- manual_cut_note: `reprogap5 was intentionally cut at 225/304 with one chunk left because it needed 15/16 final answers to recover the 0.75 local gate, making the expected value worse than keeping memory on reprogap4 and reprobridge9`
- post_cut_memory_note: `after killing the reprogap5 postprocess worker, live poller, threshold waiter, and local-summary waiter, host headroom recovered to roughly PhysMem unused 202 GB`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `25616`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprogap5_text3bit1num1_anchortrim_lr1e6_len1024_from_proxybench_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge9_text3bit1num5_anchortrim_lr1e6_len1024_from_proxybench_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge9_text3bit1num5_anchortrim_lr1e6_len1024_from_proxybench_v1`

- status: `paused_memory_cut`
- label: `reprobridge9 hybrid`
- observed_at: `2026-04-11T21:13:45.000000+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge9_text3bit1num5_anchortrim_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge9_text3bit1num5_anchortrim_v1.csv`
- sampled_rows: `80`
- optimizer_progress: `0/8 = 0.00%`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge9_text3bit1num5_anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge9_text3bit1num5_anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized`
- suite_evaluations: `1/2 = 50.00%`
- current_evaluation: `leaderboard_proxy_v1_set`
- current_rows_progress: `32/200 = 16.00%`
- current_chunks_progress: `2/13 = 15.38%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge9_text3bit1num5_anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/leaderboard_proxy_v1_set/benchmark_eval_progress.json`
- accuracy_so_far: `0.4062`
- correct_so_far: `13`
- completed_evaluations: `['readme_local320']`
- completed_evaluation_scores: `readme_local320 230/320 = 0.7188`
- manual_cut_note: `reprobridge9 was intentionally cut immediately after readme_local320 finalized at 230/320 because the hybrid bridge still finished below the tracked 235/320 frontier and below the 0.75 threshold gate, making further proxy continuation lower EV than reallocating memory to reprobridge10, reprobridge12, and reprobridge13`
- post_cut_memory_note: `after killing the reprobridge9 live poller, postprocess worker, threshold waiter, and obsolete reprobridge10 chain waiter, host headroom recovered to roughly PhysMem unused 192 GB`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `36795`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge9_text3bit1num5_anchortrim_lr1e6_len1024_from_proxybench_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge10_text3bit1num5num1_anchortrim_lr1e6_len1024_from_proxybench_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge10_text3bit1num5num1_anchortrim_lr1e6_len1024_from_proxybench_v1`

- status: `evaluating`
- label: `reprobridge10 sibling`
- observed_at: `2026-04-11T22:28:46.063922+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge10_text3bit1num5num1_anchortrim_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge10_text3bit1num5num1_anchortrim_v1.csv`
- sampled_rows: `80`
- optimizer_progress: `0/8 = 0.00%`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge10_text3bit1num5num1_anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge10_text3bit1num5num1_anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized`
- suite_evaluations: `1/2 = 50.00%`
- current_evaluation: `leaderboard_proxy_v1_set`
- current_rows_progress: `0/200 = 0.00%`
- current_chunks_progress: `0/13 = 0.00%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge10_text3bit1num5num1_anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/leaderboard_proxy_v1_set/benchmark_eval_progress.json`
- accuracy_so_far: `0.0000`
- correct_so_far: `0`
- completed_evaluations: `['readme_local320']`
- completed_evaluation_scores: `readme_local320 228/320 = 0.7125`
- manual_cut_note: `reprobridge10 was intentionally cut immediately after readme_local320 finalized at 228/320 because the narrow + hedge sibling still finished below the tracked 235/320 frontier and below the 0.75 threshold gate, making proxy continuation lower EV than reallocating memory to reprobridge13 and reprobridge15`
- post_cut_memory_note: `after killing the reprobridge10 live poller, postprocess worker, threshold waiter, and obsolete reprobridge12 chain waiter, host headroom rose toward PhysMem unused 313 GB`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `70437`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge10_text3bit1num5num1_anchortrim_lr1e6_len1024_from_proxybench_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge12_text3bit1num8_anchortrim_lr1e6_len1024_from_proxybench_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge12_text3bit1num8_anchortrim_lr1e6_len1024_from_proxybench_v1`

- status: `paused_memory_cut`
- label: `reprobridge12 broad`
- observed_at: `2026-04-11T22:29:52.904543+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge12_text3bit1num8_anchortrim_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge12_text3bit1num8_anchortrim_v1.csv`
- sampled_rows: `80`
- optimizer_progress: `0/8 = 0.00%`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge12_text3bit1num8_anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge12_text3bit1num8_anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized`
- suite_evaluations: `1/2 = 50.00%`
- current_evaluation: `leaderboard_proxy_v1_set`
- current_rows_progress: `0/200 = 0.00%`
- current_chunks_progress: `0/13 = 0.00%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge12_text3bit1num8_anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/leaderboard_proxy_v1_set/benchmark_eval_progress.json`
- accuracy_so_far: `0.0000`
- correct_so_far: `0`
- completed_evaluations: `['readme_local320']`
- completed_evaluation_scores: `readme_local320 228/320 = 0.7125`
- manual_cut_note: `reprobridge12 was intentionally cut immediately after readme_local320 finalized at 228/320 because the broad no-answer_only sibling still finished below the tracked 235/320 frontier and below the 0.75 threshold gate, making proxy continuation lower EV than reallocating memory to reprobridge13 and reprobridge15`
- post_cut_memory_note: `after killing the reprobridge12 live poller, postprocess worker, threshold waiter, and obsolete reprobridge13 chain waiter, host headroom rose toward PhysMem unused 313 GB`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `72737`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge12_text3bit1num8_anchortrim_lr1e6_len1024_from_proxybench_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge13_text3bit1num8num1_anchortrim_lr1e6_len1024_from_proxybench_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge13_text3bit1num8num1_anchortrim_lr1e6_len1024_from_proxybench_v1`

- status: `evaluating`
- label: `reprobridge13 factor`
- observed_at: `2026-04-11T22:46:16.979612+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge13_text3bit1num8num1_anchortrim_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge13_text3bit1num8num1_anchortrim_v1.csv`
- sampled_rows: `80`
- optimizer_progress: `0/8 = 0.00%`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge13_text3bit1num8num1_anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge13_text3bit1num8num1_anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized`
- suite_evaluations: `1/2 = 50.00%`
- current_evaluation: `leaderboard_proxy_v1_set`
- current_rows_progress: `32/200 = 16.00%`
- current_chunks_progress: `2/13 = 15.38%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge13_text3bit1num8num1_anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/leaderboard_proxy_v1_set/benchmark_eval_progress.json`
- accuracy_so_far: `0.4375`
- correct_so_far: `14`
- completed_evaluations: `['readme_local320']`
- completed_evaluation_scores: `readme_local320 235/320 = 0.7344`
- manual_cut_note: `reprobridge13 was intentionally cut after readme_local320 finalized at 235/320 because, although it matched the tracked local frontier, it still missed the 0.75 threshold gate and early proxy continuation only reached 14/32 = 0.4375, making further proxy continuation lower EV than reallocating that budget to reprobridge15, reprobridge16, and the queued reprobridge17 fallback`
- post_cut_memory_note: `after killing the reprobridge13 live poller, postprocess worker, threshold waiter, and the reprobridge17-from-13 launcher, the surviving bridge queue now depends only on reprobridge15 and reprobridge16 full-suite summaries`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `77590`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge13_text3bit1num8num1_anchortrim_lr1e6_len1024_from_proxybench_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge15_text3bit1num8num1swap_anchorrestore_lr1e6_len1024_from_proxybench_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge15_text3bit1num8num1swap_anchorrestore_lr1e6_len1024_from_proxybench_v1`

- status: `evaluating`
- label: `reprobridge15 hedge swap`
- observed_at: `2026-04-12T00:40:12.234438+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge15_text3bit1num8num1swap_anchorrestore_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge15_text3bit1num8num1swap_anchorrestore_v1.csv`
- sampled_rows: `80`
- optimizer_progress: `0/8 = 0.00%`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge15_text3bit1num8num1swap_anchorrestore_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge15_text3bit1num8num1swap_anchorrestore_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized`
- suite_evaluations: `1/2 = 50.00%`
- current_evaluation: `leaderboard_proxy_v1_set`
- current_rows_progress: `0/200 = 0.00%`
- current_chunks_progress: `0/13 = 0.00%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge15_text3bit1num8num1swap_anchorrestore_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/leaderboard_proxy_v1_set/benchmark_eval_progress.json`
- accuracy_so_far: `0.0000`
- correct_so_far: `0`
- completed_evaluations: `['readme_local320']`
- completed_evaluation_scores: `readme_local320 228/320 = 0.7125`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `4499`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge15_text3bit1num8num1swap_anchorrestore_lr1e6_len1024_from_proxybench_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge16_text3bit1num8num1raw4_answertrim_lr1e6_len1024_from_proxybench_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge16_text3bit1num8num1raw4_answertrim_lr1e6_len1024_from_proxybench_v1`

- status: `evaluating`
- label: `reprobridge16 raw numeric`
- observed_at: `2026-04-12T01:11:21.495770+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge16_text3bit1num8num1raw4_answertrim_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge16_text3bit1num8num1raw4_answertrim_v1.csv`
- sampled_rows: `80`
- optimizer_progress: `0/8 = 0.00%`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge16_text3bit1num8num1raw4_answertrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge16_text3bit1num8num1raw4_answertrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized`
- suite_evaluations: `1/2 = 50.00%`
- current_evaluation: `leaderboard_proxy_v1_set`
- current_rows_progress: `16/200 = 8.00%`
- current_chunks_progress: `1/13 = 7.69%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge16_text3bit1num8num1raw4_answertrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/leaderboard_proxy_v1_set/benchmark_eval_progress.json`
- accuracy_so_far: `0.6250`
- correct_so_far: `10`
- completed_evaluations: `['readme_local320']`
- completed_evaluation_scores: `readme_local320 232/320 = 0.7250`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `8818`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge16_text3bit1num8num1raw4_answertrim_lr1e6_len1024_from_proxybench_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge17_text3bit1num8num1gravrestore_lr1e6_len1024_from_proxybench_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge17_text3bit1num8num1gravrestore_lr1e6_len1024_from_proxybench_v1`

- status: `evaluating`
- label: `reprobridge17 grav restore`
- observed_at: `2026-04-12T01:20:13.009681+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge17_text3bit1num8num1gravrestore_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge17_text3bit1num8num1gravrestore_v1.csv`
- sampled_rows: `80`
- optimizer_progress: `0/8 = 0.00%`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge17_text3bit1num8num1gravrestore_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge17_text3bit1num8num1gravrestore_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized`
- suite_evaluations: `1/2 = 50.00%`
- current_evaluation: `leaderboard_proxy_v1_set`
- current_rows_progress: `0/200 = 0.00%`
- current_chunks_progress: `0/13 = 0.00%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge17_text3bit1num8num1gravrestore_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/leaderboard_proxy_v1_set/benchmark_eval_progress.json`
- accuracy_so_far: `0.0000`
- correct_so_far: `0`
- completed_evaluations: `['readme_local320']`
- completed_evaluation_scores: `readme_local320 227/320 = 0.7094`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `13023`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge17_text3bit1num8num1gravrestore_lr1e6_len1024_from_proxybench_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge18_text3bit1num8num1raw2gravrestore_lr1e6_len1024_from_proxybench_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge18_text3bit1num8num1raw2gravrestore_lr1e6_len1024_from_proxybench_v1`

- status: `evaluating`
- label: `reprobridge18 hybrid`
- observed_at: `2026-04-12T01:27:34.721859+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge18_text3bit1num8num1raw2gravrestore_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge18_text3bit1num8num1raw2gravrestore_v1.csv`
- sampled_rows: `80`
- optimizer_progress: `0/8 = 0.00%`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge18_text3bit1num8num1raw2gravrestore_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge18_text3bit1num8num1raw2gravrestore_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized`
- suite_evaluations: `1/2 = 50.00%`
- current_evaluation: `leaderboard_proxy_v1_set`
- current_rows_progress: `0/200 = 0.00%`
- current_chunks_progress: `0/13 = 0.00%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge18_text3bit1num8num1raw2gravrestore_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/leaderboard_proxy_v1_set/benchmark_eval_progress.json`
- accuracy_so_far: `0.0000`
- correct_so_far: `0`
- completed_evaluations: `['readme_local320']`
- completed_evaluation_scores: `readme_local320 227/320 = 0.7094`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `17080`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge18_text3bit1num8num1raw2gravrestore_lr1e6_len1024_from_proxybench_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge19_text3bit1num8num1raw3grav1_lr1e6_len1024_from_proxybench_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge19_text3bit1num8num1raw3grav1_lr1e6_len1024_from_proxybench_v1`

- status: `evaluating`
- label: `reprobridge19 hybrid`
- observed_at: `2026-04-12T02:18:30.143400+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge19_text3bit1num8num1raw3grav1_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge19_text3bit1num8num1raw3grav1_v1.csv`
- sampled_rows: `80`
- optimizer_progress: `0/8 = 0.00%`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge19_text3bit1num8num1raw3grav1_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge19_text3bit1num8num1raw3grav1_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized`
- suite_evaluations: `1/2 = 50.00%`
- current_evaluation: `leaderboard_proxy_v1_set`
- current_rows_progress: `0/200 = 0.00%`
- current_chunks_progress: `0/13 = 0.00%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge19_text3bit1num8num1raw3grav1_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/leaderboard_proxy_v1_set/benchmark_eval_progress.json`
- accuracy_so_far: `0.0000`
- correct_so_far: `0`
- completed_evaluations: `['readme_local320']`
- completed_evaluation_scores: `readme_local320 231/320 = 0.7219`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `30788`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge19_text3bit1num8num1raw3grav1_lr1e6_len1024_from_proxybench_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge20_text3bit1num8raw4grav1_hedgecut_lr1e6_len1024_from_proxybench_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge20_text3bit1num8raw4grav1_hedgecut_lr1e6_len1024_from_proxybench_v1`

- status: `evaluating`
- label: `reprobridge20 hedge cut`
- observed_at: `2026-04-12T03:27:51.314031+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge20_text3bit1num8raw4grav1_hedgecut_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge20_text3bit1num8raw4grav1_hedgecut_v1.csv`
- sampled_rows: `80`
- optimizer_progress: `0/8 = 0.00%`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge20_text3bit1num8raw4grav1_hedgecut_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge20_text3bit1num8raw4grav1_hedgecut_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized`
- suite_evaluations: `1/2 = 50.00%`
- current_evaluation: `leaderboard_proxy_v1_set`
- current_rows_progress: `32/200 = 16.00%`
- current_chunks_progress: `2/13 = 15.38%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge20_text3bit1num8raw4grav1_hedgecut_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/leaderboard_proxy_v1_set/benchmark_eval_progress.json`
- accuracy_so_far: `0.4062`
- correct_so_far: `13`
- completed_evaluations: `['readme_local320']`
- completed_evaluation_scores: `readme_local320 229/320 = 0.7156`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `54704`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge20_text3bit1num8raw4grav1_hedgecut_lr1e6_len1024_from_proxybench_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge22_text3bit1num8raw5grav1_fullraw_lr1e6_len1024_from_proxybench_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge22_text3bit1num8raw5grav1_fullraw_lr1e6_len1024_from_proxybench_v1`

- status: `evaluating`
- label: `reprobridge22 full raw`
- observed_at: `2026-04-12T03:43:35.797321+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge22_text3bit1num8raw5grav1_fullraw_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge22_text3bit1num8raw5grav1_fullraw_v1.csv`
- sampled_rows: `80`
- optimizer_progress: `0/8 = 0.00%`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge22_text3bit1num8raw5grav1_fullraw_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge22_text3bit1num8raw5grav1_fullraw_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized`
- suite_evaluations: `1/2 = 50.00%`
- current_evaluation: `leaderboard_proxy_v1_set`
- current_rows_progress: `16/200 = 8.00%`
- current_chunks_progress: `1/13 = 7.69%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge22_text3bit1num8raw5grav1_fullraw_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/leaderboard_proxy_v1_set/benchmark_eval_progress.json`
- accuracy_so_far: `0.4375`
- correct_so_far: `7`
- completed_evaluations: `['readme_local320']`
- completed_evaluation_scores: `readme_local320 231/320 = 0.7219`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `59249`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge22_text3bit1num8raw5grav1_fullraw_lr1e6_len1024_from_proxybench_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge21_text3bit1num8raw2grav1unitedge_lr1e6_len1024_from_proxybench_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge21_text3bit1num8raw2grav1unitedge_lr1e6_len1024_from_proxybench_v1`

- status: `evaluating`
- label: `reprobridge21 unit edge`
- observed_at: `2026-04-12T04:11:34.586288+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge21_text3bit1num8raw2grav1unitedge_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge21_text3bit1num8raw2grav1unitedge_v1.csv`
- sampled_rows: `80`
- optimizer_progress: `0/8 = 0.00%`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge21_text3bit1num8raw2grav1unitedge_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge21_text3bit1num8raw2grav1unitedge_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized`
- suite_evaluations: `1/2 = 50.00%`
- current_evaluation: `leaderboard_proxy_v1_set`
- current_rows_progress: `48/200 = 24.00%`
- current_chunks_progress: `3/13 = 23.08%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge21_text3bit1num8raw2grav1unitedge_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/leaderboard_proxy_v1_set/benchmark_eval_progress.json`
- accuracy_so_far: `0.5625`
- correct_so_far: `27`
- completed_evaluations: `['readme_local320']`
- completed_evaluation_scores: `readme_local320 227/320 = 0.7094`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `60884`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge21_text3bit1num8raw2grav1unitedge_lr1e6_len1024_from_proxybench_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge23_text3bit1num8raw5unitedge_lr1e6_len1024_from_proxybench_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge23_text3bit1num8raw5unitedge_lr1e6_len1024_from_proxybench_v1`

- status: `evaluating`
- label: `reprobridge23 full raw unitedge`
- observed_at: `2026-04-12T04:11:39.874931+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge23_text3bit1num8raw5unitedge_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge23_text3bit1num8raw5unitedge_v1.csv`
- sampled_rows: `79`
- optimizer_progress: `0/8 = 0.00%`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge23_text3bit1num8raw5unitedge_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge23_text3bit1num8raw5unitedge_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized`
- suite_evaluations: `0/2 = 0.00%`
- current_evaluation: `readme_local320`
- current_rows_progress: `288/320 = 90.00%`
- current_chunks_progress: `18/20 = 90.00%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge23_text3bit1num8raw5unitedge_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/readme_local320/benchmark_eval_progress.json`
- accuracy_so_far: `0.7847`
- correct_so_far: `226`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `74969`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge23_text3bit1num8raw5unitedge_lr1e6_len1024_from_proxybench_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge24_text3bit1num8raw6nograv_lr1e6_len1024_from_proxybench_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge24_text3bit1num8raw6nograv_lr1e6_len1024_from_proxybench_v1`

- status: `evaluating`
- label: `reprobridge24 raw6 no grav`
- observed_at: `2026-04-12T04:12:13.039708+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge24_text3bit1num8raw6nograv_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge24_text3bit1num8raw6_nograv_v1.csv`
- sampled_rows: `80`
- optimizer_progress: `0/8 = 0.00%`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge24_text3bit1num8raw6nograv_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge24_text3bit1num8raw6nograv_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized`
- suite_evaluations: `0/2 = 0.00%`
- current_evaluation: `readme_local320`
- current_rows_progress: `64/320 = 20.00%`
- current_chunks_progress: `4/20 = 20.00%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge24_text3bit1num8raw6nograv_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/readme_local320/benchmark_eval_progress.json`
- accuracy_so_far: `1.0000`
- correct_so_far: `64`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `98884`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge24_text3bit1num8raw6nograv_lr1e6_len1024_from_proxybench_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge25_text3bit1num8raw6unitedge_lr1e6_len1024_from_proxybench_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge25_text3bit1num8raw6unitedge_lr1e6_len1024_from_proxybench_v1`

- status: `evaluating`
- label: `reprobridge25 raw6 unitedge`
- observed_at: `2026-04-12T04:07:55.464656+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge25_text3bit1num8raw6unitedge_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge25_text3bit1num8raw6unitedge_v1.csv`
- sampled_rows: `80`
- optimizer_progress: `0/8 = 0.00%`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge25_text3bit1num8raw6unitedge_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge25_text3bit1num8raw6unitedge_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized`
- suite_evaluations: `0/2 = 0.00%`
- current_evaluation: `readme_local320`
- current_rows_progress: `32/320 = 10.00%`
- current_chunks_progress: `2/20 = 10.00%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge25_text3bit1num8raw6unitedge_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/readme_local320/benchmark_eval_progress.json`
- accuracy_so_far: `1.0000`
- correct_so_far: `32`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `3105`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge25_text3bit1num8raw6unitedge_lr1e6_len1024_from_proxybench_v1 -->
