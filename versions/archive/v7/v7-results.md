# archive/v7 Results

## Current snapshot

- snapshot kind: historical archive copy under `versions/archive/v7/`
- script: `versions/archive/v7/code/train.py`
- current repo snapshot has no archive-local `outputs/` tree under `versions/archive/v7/`
- current repo snapshot also has no archive-local Git-managed measured-score artifact under `versions/archive/v7/`
- canonical active ledger for the non-archive v7 line lives at `versions/v7/v7-results.md`
- README-first note: the authoritative evaluation contract remains the tab-separated `README.md` Evaluation table (`max_lora_rank = 32`, `max_tokens = 7680`, `top_p = 1.0`, `temperature = 0.0`, `max_num_seqs = 64`, `gpu_memory_utilization = 0.85`, `max_model_len = 8192`)
- snapshot-local note: archive code still carries `/kaggle/working/submission_v7.zip` as its historical packaged-archive name; the active non-archive README contract now uses `submission.zip`
- measured score: **not recorded in this archive snapshot's Git-visible files**

## Recording rule

- if this archive snapshot is ever rerun as its own line, archive-local measured scores should be appended here instead of being left implicit in ad hoc artifacts
