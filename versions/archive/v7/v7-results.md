# v7 Results

## Source of truth

- this ledger follows the authoritative `README.md` Evaluation / Submitting contract
- `max_lora_rank = 32`
- `max_tokens = 7680`
- `top_p = 1.0`
- `temperature = 0.0`
- `max_num_seqs = 64`
- `gpu_memory_utilization = 0.85`
- `max_model_len = 8192`

## Current snapshot

- script: `versions/v7/code/train_transformers_submission_v7.py`
- static hardening: `DEFAULT_OUTPUT_ROOT` now points to `versions/v7/outputs/transformers_submission_v7` instead of the copied `transformers_submission_v6` path
- runtime contract hardening: the script now re-reads the live `README.md` evaluation table at CLI entry and fails explicitly on missing rows, empty values, malformed numeric values, or constant drift against the current README
- submission contract hardening: validation / packaging paths now also live-reload the README submission wording, require `adapter_config.json`, enforce `submission.zip`, and surface `readme_submission_contract_verified_from_readme_file = true` in validation / zip summaries
- regression coverage: `versions/v5/tests/test_readme_contract_sync.py` now locks the shared v5 / v5-1 / v6 / v7 README-table loader plus submission-contract loader / zip behavior for happy path, missing clause, and zip-name drift
- current repo snapshot has no `versions/v7/outputs/` tree
- current repo snapshot also has no version-local Git-managed measured-score artifact under `versions/v7/`
- measured score: **not recorded in the current Git-visible snapshot**

## Recording rule

- once runtime execution recovers, the first measured local / proxy / leaderboard-facing score for this line should be appended here instead of being left only inside transient output artifacts
