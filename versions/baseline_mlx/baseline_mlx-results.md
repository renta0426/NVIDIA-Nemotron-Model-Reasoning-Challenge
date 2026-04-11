<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1 -->
### Auto result: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1`

- recorded_at: `2026-04-11T21:31:34.038045+00:00`
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
- active_waiters: `reprobridge10 -> {0.75, 0.80}`, `reprobridge12 -> {0.75, 0.80}`, `reprobridge13 -> {0.75, 0.80}`
- retired_waiters: `numreal8` retired after local320 finished at `226/320 = 0.7063`, which ruled out both `local-ge-0.75` and `local-ge-0.80`; `reprogap5` retired after stalling at `225/304 = 0.7401` with one chunk left, which made `local-ge-0.75` improbable enough to cut for memory; `reprogap4` retired after local320 finished at `229/320 = 0.7156`, which ruled out both the tracked frontier and `local-ge-0.75`; `reprobridge9` retired after local320 finished at `230/320 = 0.7188`, which ruled out both the tracked frontier and `local-ge-0.75``
- queued_waiters: `none`
- output_roots: `baseline_mlx/outputs/threshold_submission_numreal8_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprogap4_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprogap5_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprobridge9_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprobridge10_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprobridge12_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprobridge13_local_ge_075_v1`, `..._080_v1`
- notes: `this keeps the threshold packaging path live across the currently running bridge wave, so any qualifying >0.75 or >0.8 result can materialize a submission artifact immediately instead of waiting for another manual pass; numreal8, reprogap5, reprogap4, and reprobridge9 were all retired from the active threshold set after finishing below the necessary local gates, while reprobridge10, reprobridge12, and reprobridge13 were all launched early once memory recovered enough to reopen parallel lanes`

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

- status: `launched_early_after_memory_recovery`
- queued_at: `2026-04-11T18:20Z`
- launched_at: `2026-04-11T20:34Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge10_text3bit1num5num1_anchortrim_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge10_text3bit1num5num1_anchortrim_v1.csv`
- trigger: `launched early once the numreal8 and reprogap5 cuts recovered roughly PhysMem unused 202 GB; this intentionally overrode the previous wait-for-reprobridge9-summary chain so the sibling matrix could keep expanding in parallel`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: this sibling stacks the exact four `reprogap4` frontier-over-repro rows, the five verifiedmix numeric anchors, and the single raw-only reverse-gap answer_only row from `reprogap5`, while trimming the easiest five gravity and five unit stabilizers from `verifiedswap22_bit33eq2`
- resulting_mix: `Bit 34 / Text 18 / Gravity 10 / Unit 10 / Equation 8`
- notes: `this is the first queued sibling that carries all currently known repro-gap fixes in one 80-row set while keeping answer_only exposure capped at 1/80; the original launch waiter was accidentally killed during stale summary cleanup, but a fresh duplicate-safe wait-resume launcher was re-armed and confirmed live; once memory recovered, the run was started directly and opened with Iter 1 val_loss ≈ 0.368 while the existing live/postprocess waiters remained in place to pick up the new run`

### Manual queue note: `reprobridge12_text3bit1num8_anchortrim_v1`

- status: `launched_early_after_memory_recovery`
- queued_at: `2026-04-11T18:24Z`
- launched_at: `2026-04-11T20:41Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge12_text3bit1num8_anchortrim_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge12_text3bit1num8_anchortrim_v1.csv`
- trigger: `launched early once the reprogap4 cut recovered roughly PhysMem unused 192 GB; this intentionally overrode the previous wait-for-reprobridge10-summary chain so the broad sibling could join the live wave immediately`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: this broader sibling combines the exact four `reprogap4` frontier-over-repro rows with the full eight-row `numreal8` numeric block, while trimming the easiest six gravity and six unit stabilizers from `verifiedswap22_bit33eq2`
- resulting_mix: `Bit 34 / Text 18 / Gravity 9 / Unit 9 / Equation 10`
- notes: `this is the broad-numeric counterpart to reprobridge9 and was originally chained after reprobridge10, but after the reprogap4 cut freed enough memory it was started directly; the short train closed with train_loss ≈ 0.3630 / val_loss ≈ 0.4518 / optimizer_step 8 / peak_memory ≈ 65.46 GB and then handed off to the existing live/postprocess waiters`

### Manual queue note: `reprobridge13_text3bit1num8num1_anchortrim_v1`

- status: `launched_early_after_memory_recovery`
- queued_at: `2026-04-11T18:29Z`
- launched_at: `2026-04-11T20:58Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge13_text3bit1num8num1_anchortrim_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge13_text3bit1num8num1_anchortrim_v1.csv`
- trigger: `launched early once host headroom returned to roughly PhysMem unused 192 GB, intentionally overriding the original wait-for-reprobridge12-summary chain so the final answer_only sibling could join the active wave immediately`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: this factor sibling adds the single `reprogap5` reverse-gap answer_only hedge on top of `reprobridge12`, closing the narrow/broad numeric bridge × answer_only off/on 2x2 queue matrix
- resulting_mix: `Bit 34 / Text 18 / Gravity 9 / Unit 8 / Equation 11`
- notes: `reprobridge13 differs from reprobridge12 by exactly one row: answer_only hedge row 8158a14c replaces the next easiest remaining unit stabilizer a127eb72; runtime preflight captured current_pid 77590 with PhysMem unused about 192 GB, GPU device util 100%, and in-use system memory about 193.37 GB at launch; the short train then closed with train_loss ≈ 0.3629 / val_loss ≈ 0.4594 / optimizer_step 8 / peak_memory ≈ 65.46 GB and has already handed off to README-contract eval`

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxymiss40_text20_grav15_unit15_sym8_lr2e6_len1536_v1 -->
### Auto result: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxymiss40_text20_grav15_unit15_sym8_lr2e6_len1536_v1`

- recorded_at: `2026-04-11T21:31:37.177725+00:00`
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

- recorded_at: `2026-04-11T21:31:40.689997+00:00`
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

- recorded_at: `2026-04-11T21:31:51.571914+00:00`
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

- recorded_at: `2026-04-11T21:32:10.113886+00:00`
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

- recorded_at: `2026-04-11T21:32:16.863485+00:00`
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

- recorded_at: `2026-04-11T21:32:31.548447+00:00`
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

- recorded_at: `2026-04-11T21:31:38.386062+00:00`
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

- recorded_at: `2026-04-11T21:30:48.178188+00:00`
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

- recorded_at: `2026-04-11T21:30:56.547831+00:00`
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
- observed_at: `2026-04-11T21:30:54.605921+00:00`
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
- suite_evaluations: `0/2 = 0.00%`
- current_evaluation: `readme_local320`
- current_rows_progress: `128/320 = 40.00%`
- current_chunks_progress: `8/20 = 40.00%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge10_text3bit1num5num1_anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/readme_local320/benchmark_eval_progress.json`
- accuracy_so_far: `0.9922`
- correct_so_far: `127`

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

- status: `evaluating`
- label: `reprobridge12 broad`
- observed_at: `2026-04-11T21:31:23.404598+00:00`
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
- suite_evaluations: `0/2 = 0.00%`
- current_evaluation: `readme_local320`
- current_rows_progress: `112/320 = 35.00%`
- current_chunks_progress: `7/20 = 35.00%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge12_text3bit1num8_anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/readme_local320/benchmark_eval_progress.json`
- accuracy_so_far: `1.0000`
- correct_so_far: `112`

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
- observed_at: `2026-04-11T21:32:14.943969+00:00`
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
- suite_evaluations: `0/2 = 0.00%`
- current_evaluation: `readme_local320`
- current_rows_progress: `64/320 = 20.00%`
- current_chunks_progress: `4/20 = 20.00%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge13_text3bit1num8num1_anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/readme_local320/benchmark_eval_progress.json`
- accuracy_so_far: `1.0000`
- correct_so_far: `64`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `77590`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge13_text3bit1num8num1_anchortrim_lr1e6_len1024_from_proxybench_v1 -->
