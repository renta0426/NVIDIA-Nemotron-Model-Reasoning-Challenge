<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv120_textao20_num30_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1 -->
### Auto result: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv120_textao20_num30_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1`

- recorded_at: `2026-04-10T07:08:26.447194+00:00`
- label: `stage25 reanchor textv120 textao20 num30 grav15 unit15 rowselect from reanchor1024 v1`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv120_textao20_num30_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_text_verified120_answeronly20_num30_grav15_unit15_rowselect_v1.csv`
- sampled_rows: `200`
- optimizer_steps: `12`
- lr: `8e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Scores

- readme_local320: `215/320 = 0.6719`
- local320_components: `general_stable_set 169/200 = 0.8450; binary_hard_set 25/60 = 0.4167; symbol_watch_set 21/60 = 0.3500`
- leaderboard_proxy_v1_set: `117/200 = 0.5850`

#### Submission audit

- audit_status: `potentially_exportable_2d_only`
- peft_export_ready: `True`
- tensor_count: `232`

#### Submission export

- submission_zip: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv120_textao20_num30_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1/submission_export/submission.zip`
- zip_size_bytes: `102356778`
- validation_valid: `True`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv120_textao20_num30_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv150_textao0_num20_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv150_textao0_num20_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1`

- status: `evaluating`
- label: `stage25 reanchor textv150 textao0 num20 grav15 unit15 rowselect from reanchor1024 v1`
- observed_at: `2026-04-10T07:26:30.509813+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv150_textao0_num20_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_text_verified150_num20_grav15_unit15_rowselect_v1.csv`
- sampled_rows: `200`
- optimizer_progress: `0/12 = 0.00%`
- lr: `8e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv150_textao0_num20_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv150_textao0_num20_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1/eval_suite_readme_proxy_specialized`
- suite_evaluations: `1/2 = 50.00%`
- current_evaluation: `leaderboard_proxy_v1_set`
- current_rows_progress: `112/200 = 56.00%`
- current_chunks_progress: `7/13 = 53.85%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv150_textao0_num20_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1/eval_suite_readme_proxy_specialized/leaderboard_proxy_v1_set/benchmark_eval_progress.json`
- completed_evaluations: `['readme_local320']`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `10996`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv150_textao0_num20_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv100_textao40_num30_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv100_textao40_num30_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1`

- status: `evaluating`
- label: `stage25 reanchor textv100 textao40 num30 grav15 unit15 rowselect from reanchor1024 v1`
- observed_at: `2026-04-10T06:26:33.777820+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv100_textao40_num30_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_text_verified100_answeronly40_num30_grav15_unit15_rowselect_v1.csv`
- sampled_rows: `200`
- optimizer_progress: `0/12 = 0.00%`
- lr: `8e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv100_textao40_num30_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv100_textao40_num30_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1/eval_suite_readme_proxy_specialized`
- suite_evaluations: `1/2 = 50.00%`
- current_evaluation: `leaderboard_proxy_v1_set`
- current_rows_progress: `16/200 = 8.00%`
- current_chunks_progress: `1/13 = 7.69%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv100_textao40_num30_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1/eval_suite_readme_proxy_specialized/leaderboard_proxy_v1_set/benchmark_eval_progress.json`
- completed_evaluations: `['readme_local320']`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `9266`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv100_textao40_num30_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv60_textao80_num30_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv60_textao80_num30_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1`

- status: `evaluating`
- label: `stage25 reanchor textv60 textao80 num30 grav15 unit15 rowselect from reanchor1024 v1`
- observed_at: `2026-04-10T06:19:14.461212+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv60_textao80_num30_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_text_verified60_answeronly80_num30_grav15_unit15_rowselect_v1.csv`
- sampled_rows: `200`
- optimizer_progress: `0/12 = 0.00%`
- lr: `8e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv60_textao80_num30_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv60_textao80_num30_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1/eval_suite_readme_proxy_specialized`
- suite_evaluations: `0/2 = 0.00%`
- current_evaluation: `readme_local320`
- current_rows_progress: `144/320 = 45.00%`
- current_chunks_progress: `9/20 = 45.00%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv60_textao80_num30_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1/eval_suite_readme_proxy_specialized/readme_local320/benchmark_eval_progress.json`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `26071`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv60_textao80_num30_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv80_textao60_num30_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv80_textao60_num30_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1`

- status: `evaluating`
- label: `stage25 reanchor textv80 textao60 num30 grav15 unit15 rowselect from reanchor1024 v1`
- observed_at: `2026-04-10T07:28:57.494099+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv80_textao60_num30_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_text_verified80_answeronly60_num30_grav15_unit15_rowselect_v1.csv`
- sampled_rows: `200`
- optimizer_progress: `0/12 = 0.00%`
- lr: `8e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv80_textao60_num30_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv80_textao60_num30_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1/eval_suite_readme_proxy_specialized`
- suite_evaluations: `1/2 = 50.00%`
- current_evaluation: `leaderboard_proxy_v1_set`
- current_rows_progress: `64/200 = 32.00%`
- current_chunks_progress: `4/13 = 30.77%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv80_textao60_num30_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1/eval_suite_readme_proxy_specialized/leaderboard_proxy_v1_set/benchmark_eval_progress.json`
- completed_evaluations: `['readme_local320']`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `18644`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv80_textao60_num30_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1 -->

## 2026-04-10 notebook adaptation note: Kaggle HF/PEFT stagefreeze curriculum

- updated notebook: `baseline/nemotron-sft-lora-with-cot-v2/nemotron-sft-lora-with-cot-v2-stagefreeze-curriculum.ipynb`
- base notebook kept as reference: `baseline/nemotron-sft-lora-with-cot-v2/nemotron-sft-lora-with-cot-v2-original.ipynb`
- curriculum CSVs were materialized under `baseline/nemotron-sft-lora-with-cot-v2/artifacts/` and are referenced directly by filename:
  - `train_split_with_cot_stagefreeze_stage1_broad_v3f_safe_plus_notformula.csv` (`3321` rows)
  - `train_split_with_cot_stagefreeze_stage2_corrective_v1.csv` (`218` rows)
  - `train_split_with_cot_stagefreeze_stage25_reanchor_nonbit_50_each.csv` (`200` rows)
- decision: **split CSV per stage**, not one CSV with notebook-side filtering. Reason: the request was to avoid data shaping inside the notebook; per-stage CSVs make the curriculum explicit and reproducible in Kaggle.
- notebook LoRA logic was changed from single-stage `target_modules=r".*\\.(in_proj|out_proj|up_proj|down_proj)$"` to a union adapter over:
  - `mixer.in_proj`
  - `mixer.out_proj`
  - `mixer.shared_experts.up_proj`
  - `mixer.shared_experts.down_proj`
  - `mixer.q_proj`
  - `mixer.k_proj`
  - `mixer.v_proj`
  - `mixer.o_proj`
- stage-specific trainability now matches the MLX stagefreeze curriculum:
  - Stage1 trains broad trunk only
  - Stage2 trains attention `q/k/v/o` only with `lr=2e-5`, `epochs=2.4`, `max_length=768`
  - Stage2.5 trains attention `q/k/v/o` only with `lr=1e-5`, `epochs=0.45`, `max_length=1024`
- final adapter handoff stays compatible with the original notebook packaging flow because the curriculum cell copies the last-stage adapter to `/kaggle/working/sft_adapter`, and the submission cell still packages from that location.
