# CUDA train data analysis v1 - kickoff

- Source grounding: `README.md`, `try-cuda-train-data-analyst-plan.md`, `try-cuda-train-result.md`
- Scope: analyze `data/train.csv` only; do not run training.
- Goal: explain low teacher coverage and produce row-level audit signals for later curation.
- Workspace: `/home/renta0426/.copilot/session-state/833e73c6-310a-4ba9-89a3-7e4373bac223/files/cuda-train-data-analysis-v1/`

## Immediate observations

- `README.md` confirms score is plain accuracy, so bad labels and weak verified traces directly hurt leaderboard performance.
- `try-cuda-train-result.md` shows only 36.6% teacher coverage overall, with `gravity/text/symbol` at 0 and `binary` at 19.1%.
- Existing `versions/v1` code already has family parsers and metadata builders; `versions/v4` adds conservative generator-ready logic and a bit-op identifier.

## Next step

Build one analysis script that reuses those helpers, emits row-level metadata/artifacts, and writes follow-up reports.
