# archive/v4 Results

## Current snapshot

- snapshot kind: historical archive copy under `versions/archive/v4/`
- script: `versions/archive/v4/code/train.py`
- archive-local artifact inventory currently includes `versions/archive/v4/submission.zip`
- however, the current repo snapshot has no archive-local Git-managed measured-score artifact or provenance manifest alongside that packaged archive under `versions/archive/v4/`
- canonical active ledger for the non-archive v4 line lives at `versions/v4/v4-results.md`
- README-first note: the authoritative evaluation contract remains the tab-separated `README.md` Evaluation table (`max_lora_rank = 32`, `max_tokens = 7680`, `top_p = 1.0`, `temperature = 0.0`, `max_num_seqs = 64`, `gpu_memory_utilization = 0.85`, `max_model_len = 8192`)
- snapshot-local note: archive code still carries `/kaggle/working/submission_v4.zip` as its historical packaged-archive name; the active non-archive README contract now uses `submission.zip`
- measured score: **not recorded in this archive snapshot's Git-visible files**

## Recording rule

- if this archive snapshot is ever rerun or its packaged artifact is revalidated as a distinct line, the first archive-local measured score and provenance note should be appended here
