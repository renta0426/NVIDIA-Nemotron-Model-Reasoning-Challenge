# archive/v8 Results

## Current snapshot

- snapshot kind: historical archive-only line under `versions/archive/v8/`
- script: `versions/archive/v8/code/train.py`
- current repo snapshot has no archive-local `outputs/` tree under `versions/archive/v8/`
- current repo snapshot also has no archive-local Git-managed measured-score artifact under `versions/archive/v8/`
- unlike `archive/v1`, `archive/v4`, and `archive/v7`, there is no non-archive `versions/v8/` ledger in the current repository snapshot
- README-first note: the authoritative evaluation contract remains the tab-separated `README.md` Evaluation table (`max_lora_rank = 32`, `max_tokens = 7680`, `top_p = 1.0`, `temperature = 0.0`, `max_num_seqs = 64`, `gpu_memory_utilization = 0.85`, `max_model_len = 8192`)
- measured score: **not recorded in this archive snapshot's Git-visible files**

## Recording rule

- if this archive-only snapshot is ever revived as an executable line, the first measured local / proxy / leaderboard-facing score should be appended here
