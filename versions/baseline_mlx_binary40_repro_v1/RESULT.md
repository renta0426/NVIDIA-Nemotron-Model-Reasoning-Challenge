# binary40 repro v1

- source run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv130_bin40proxyo20p5s15_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1`
- readme_local320: `229/320 = 0.7156`
- leaderboard_proxy_v1_set: `129/200 = 0.6450`
- audit_status: `potentially_exportable_2d_only`
- regenerated_submission_zip: `baseline_mlx/outputs/binary40_local_best_repro_export_v1/submission_export/submission.zip`
- regenerated_submission_valid: `True`

## README contract

- `max_lora_rank = 32`
- `max_tokens = 7680`
- `top_p = 1.0`
- `temperature = 0.0`
- `max_num_seqs = 64`
- `max_model_len = 8192`

## single-file pipeline

- script: `versions/baseline_mlx_binary40_repro_v1/reproduce_binary40_submission.py`
- verify: `uv run python versions/baseline_mlx_binary40_repro_v1/reproduce_binary40_submission.py verify`
- re-export: `uv run python versions/baseline_mlx_binary40_repro_v1/reproduce_binary40_submission.py export-existing`
- full rerun: `uv run python versions/baseline_mlx_binary40_repro_v1/reproduce_binary40_submission.py full-reproduce`
