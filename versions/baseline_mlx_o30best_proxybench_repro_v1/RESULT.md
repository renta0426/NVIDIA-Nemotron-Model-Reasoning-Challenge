# o30best proxybench repro v1

- source run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1`
- source resume run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxymiss40_text20_grav15_unit15_sym8_lr2e6_len1536_v1`
- readme_local320: `235/320 = 0.7344`
- leaderboard_proxy_v1_set: `131/200 = 0.6550`
- audit_status: `potentially_exportable_2d_only`
- peft_export_ready: `True`
- regenerated_submission_zip: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1/submission_export/submission.zip`
- regenerated_zip_size_bytes: `102357401`
- regenerated_submission_valid: `True`
- exportability_note: treat `audit_status` above as a legacy compatibility label; the live README-facing exportability signal is `peft_export_ready = True` together with `regenerated_submission_valid = True`.

## README contract

- `max_lora_rank = 32`
- `max_tokens = 7680`
- `top_p = 1.0`
- `temperature = 0.0`
- `max_num_seqs = 64`
- `gpu_memory_utilization = 0.85`
- `max_model_len = 8192`

## single-file pipeline

- script: `versions/baseline_mlx_o30best_proxybench_repro_v1/reproduce_o30best_proxybench_submission.py`
- verify: `uv run python versions/baseline_mlx_o30best_proxybench_repro_v1/reproduce_o30best_proxybench_submission.py verify`
- re-export: `uv run python versions/baseline_mlx_o30best_proxybench_repro_v1/reproduce_o30best_proxybench_submission.py export-existing`
- full rerun: `uv run python versions/baseline_mlx_o30best_proxybench_repro_v1/reproduce_o30best_proxybench_submission.py full-reproduce`

## queued next action

- clean full rerun is queued behind a conservative free-memory gate: `uv run python baseline_mlx/reproduce_nemotron_sft_lora_with_cot_v2_mlx.py wait-for-free-memory --min-free-gb 190`

## artifact note

- existing generated `o30best_proxybench_repro_summary.{json,md}` artifacts under `baseline_mlx/outputs/o30best_proxybench_*_repro_*_v1/` predate the README `gpu_memory_utilization = 0.85` sync in the wrapper code, so this versioned `RESULT.md` is the authoritative Git-visible contract ledger until those summaries are regenerated after shell recovery
- once regenerated, those summary artifacts will also stamp `summary_schema_version = 2`, `readme_contract_state`, and `readme_contract_verified_from_readme_file = true` so README contract completeness and live-README revalidation are machine-visible
- the wrapper now also re-reads the authoritative `README.md` evaluation rows directly and fails explicitly if a required row is missing, empty, or malformed instead of surfacing a later mismatch against `None`
