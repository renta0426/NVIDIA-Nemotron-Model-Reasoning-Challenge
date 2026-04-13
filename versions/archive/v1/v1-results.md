# archive/v1 Results

## Current snapshot

- snapshot kind: historical archive copy under `versions/archive/v1/`
- script: `versions/archive/v1/code/train.py`
- current repo snapshot has no archive-local `outputs/` tree under `versions/archive/v1/`
- current repo snapshot also has no archive-local Git-managed measured-score artifact under `versions/archive/v1/`
- canonical active ledger for the non-archive v1 line lives at `versions/v1/v1-results.md`
- README-first note: the authoritative evaluation contract remains the tab-separated `README.md` Evaluation table (`max_lora_rank = 32`, `max_tokens = 7680`, `top_p = 1.0`, `temperature = 0.0`, `max_num_seqs = 64`, `gpu_memory_utilization = 0.85`, `max_model_len = 8192`)
- snapshot-local note: archive code still points at `/kaggle/working/submission_v1.zip`, which should be read as a historical archive artifact name rather than the active README submission archive contract
- measured score: **not recorded in this archive snapshot's Git-visible files**

## Recording rule

- if this archive snapshot is ever rerun as its own line, archive-local measured scores should be appended here instead of being left implicit in ad hoc artifacts
