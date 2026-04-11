# baseline_mlx_threshold_submission_v1 results

## Scope

- script: `versions/baseline_mlx_threshold_submission_v1/reproduce_threshold_submission.py`
- purpose: re-verify a completed single-adapter MLX run against the README evaluation/submission contract and regenerate a fresh `submission.zip` into a new artifact root when a threshold gate is satisfied
- README contract: `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, `max_model_len=8192`, `max_lora_rank=32`

## Measured promotion: `local-ge-0.70 frontier`

- promoted_at: `2026-04-11T19:08Z`
- source_run: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1`
- threshold_label: `local-ge-0.70`
- gate_scores: `readme_local320 235/320 = 0.7344`, `leaderboard_proxy_v1_set 131/200 = 0.6550`
- output_root: `baseline_mlx/outputs/threshold_submission_local_ge_070_frontier_v1`
- summary_md: `baseline_mlx/outputs/threshold_submission_local_ge_070_frontier_v1/threshold_submission_summary.md`
- reproduced_submission_zip: `baseline_mlx/outputs/threshold_submission_local_ge_070_frontier_v1/submission_export/submission.zip`
- reproduced_zip_size_bytes: `102357401`
- reproduced_validation_valid: `True`

## Armed follow-up promotions

- waiters: `numreal8`, `reprogap4`, `reprogap5`, `reprobridge9`, `reprobridge10`, `reprobridge12`, `reprobridge13`
- thresholds: `local-ge-0.75`, `local-ge-0.80`
- promotion rule: each waiter blocks on the run's full suite summary and only materializes a threshold artifact if `readme_local320` clears the target threshold while `leaderboard_proxy_v1_set >= 0.65`
