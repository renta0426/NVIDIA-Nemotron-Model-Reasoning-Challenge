# v2 Results

## Update 2026-04-12

- `versions/v2/code/train.py` `package-peft` now live-reloads the authoritative `README.md` submission wording before packaging:
  - `adapter_config.json`
  - `submission.zip`
  - single LoRA adapter wording
  - `max_lora_rank = 32`
- v2 packaging smoke / submission manifest artifacts now surface `readme_submission_contract` plus `readme_submission_contract_verified_from_readme_file = true`, while retaining the local packaging contract separately.
- `versions/v2/tests/test_peft_packaging_spec.py` now regression-locks the positive README-first path and rejects a drifted local `submission_zip_name`.
- Runtime execution remains blocked in this session by the host PTY failure (`posix_openpt failed: Device not configured`), so this segment is static hardening only.

## Current snapshot

- script: `versions/v2/code/train.py`
- current repo snapshot has no `versions/v2/outputs/` tree
- current repo snapshot also has no version-local Git-managed measured-score artifact under `versions/v2/`
- README-first note: the authoritative evaluation contract remains the tab-separated `README.md` Evaluation table (`max_lora_rank = 32`, `max_tokens = 7680`, `top_p = 1.0`, `temperature = 0.0`, `max_num_seqs = 64`, `gpu_memory_utilization = 0.85`, `max_model_len = 8192`)
- measured score: **not recorded in the current Git-visible snapshot**

## Recording rule

- once runtime execution recovers, the first measured local / proxy / leaderboard-facing score for this line should be appended here instead of being left only inside transient output artifacts
