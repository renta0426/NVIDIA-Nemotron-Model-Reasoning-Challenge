# o30best proxybench repro v1

- source run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1`
- source resume run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxymiss40_text20_grav15_unit15_sym8_lr2e6_len1536_v1`
- readme_local320: `235/320 = 0.7344`
- leaderboard_proxy_v1_set: `131/200 = 0.6550`
- audit_status: `potentially_exportable_2d_only`
- regenerated_submission_zip: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1/submission_export/submission.zip`
- regenerated_submission_valid: `True`

## README contract

- `max_lora_rank = 32`
- `max_tokens = 7680`
- `top_p = 1.0`
- `temperature = 0.0`
- `max_num_seqs = 64`
- `max_model_len = 8192`

## single-file pipeline

- script: `versions/baseline_mlx_o30best_proxybench_repro_v1/reproduce_o30best_proxybench_submission.py`
- verify: `uv run python versions/baseline_mlx_o30best_proxybench_repro_v1/reproduce_o30best_proxybench_submission.py verify`
- re-export: `uv run python versions/baseline_mlx_o30best_proxybench_repro_v1/reproduce_o30best_proxybench_submission.py export-existing`
- full rerun: `uv run python versions/baseline_mlx_o30best_proxybench_repro_v1/reproduce_o30best_proxybench_submission.py full-reproduce`

## queued next action

- clean full rerun is queued behind a conservative free-memory gate: `uv run python baseline_mlx/reproduce_nemotron_sft_lora_with_cot_v2_mlx.py wait-for-free-memory --min-free-gb 190`
