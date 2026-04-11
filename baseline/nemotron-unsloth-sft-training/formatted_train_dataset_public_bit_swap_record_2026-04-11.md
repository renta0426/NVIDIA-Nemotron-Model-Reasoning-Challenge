# formatted_train_dataset public-bit swap record (2026-04-11)

## README contract

- Evaluation and submission contract is taken from `README.md`.
- Base data source remains the competition `train.csv` described in `README.md`.
- Submission target remains a Nemotron-compatible LoRA adapter packaged in `submission.zip`.

## Objective

- Start from `baseline/nemotron-unsloth-sft-training/artifacts/formatted_train_dataset.csv`.
- Preserve the original reconstructed 3-30-2 row order and all non-bit rows.
- Replace only the `bit_manipulation` rows with public-strategy traces generated from:
  - `baseline/nemotron-unsloth-sft-training/Strategy to solve 85% of bit manipulation.md`
  - `baseline/nemotron-unsloth-sft-training/c4a6d52b.txt`
- Final target for this revision:
  - recover the exact original 1400 bit training IDs from the backup artifact
  - regenerate those exact rows with the public bit strategy
  - keep `formatted_train_dataset.csv` at `3910` total rows

## Files

- Current updated artifact:
  - `baseline/nemotron-unsloth-sft-training/artifacts/formatted_train_dataset.csv`
- Backup of the pre-swap artifact:
  - `baseline/nemotron-unsloth-sft-training/artifacts/formatted_train_dataset_before_public_bit_swap_2026-04-11.csv`
- Historical 1021-row public-bit source:
  - `baseline/nemotron-unsloth-sft-training/artifacts/formatted_train_dataset_repro_public_bit_v1_2026-04-11.csv`
- Current exact-1400 rich formatted artifact for the BIT notebook:
  - `baseline/nemotron-unsloth-sft-training/artifacts/formatted_train_dataset_repro_public_bit_exact_original1400_v1_2026-04-11.csv`
- Current exact-1400 rich source artifact for the BIT notebook:
  - `baseline/nemotron-unsloth-sft-training/artifacts/training_source_repro_public_bit_exact_original1400_v1_2026-04-11.csv`

## Row counts

Original reconstructed artifact:

- total rows: `3910`
- original bit rows: `1400`
- original non-bit rows: `2510`

Historical intermediate swap:

- public bit rows available in the first public artifact: `1021`
- intermediate total rows after that swap: `3531`

Current exact-1400 swap:

- recovered original bit IDs: `1400 / 1400`
- current total rows: `3910`
- current bit rows: `1400`
- current non-bit rows: `2510`

## Current category composition

- `bit_manipulation`: `1400`
- `text_decryption`: `1300`
- `unit_conversion`: `200`
- `numeral_system`: `200`
- `gravity_physics`: `200`
- `symbol_transform`: `10`
- `numeric_equation`: `600`

## Public-strategy support on the recovered exact 1400 IDs

- fully supported bit rows: `1274 / 1400 = 0.91`
- partially supported bit rows: `126 / 1400 = 0.09`

Interpretation:

- The final artifact now preserves the original 3-30-2 sample identity for all 1400 bit rows.
- Non-bit rows remain unchanged from the original reconstructed artifact.
- The earlier `1021`-row swap is now only a historical intermediate step; the current artifact is back to `3910` rows.

## Split interpretation and validation implications

- The original notebook log shows `Validation: 950 samples from DATA_SPLIT_PATH hold-out` and then `bit_manipulation: 1400`, so the recovered `1400` bit IDs are interpreted as training-side IDs after hold-out filtering, not before it.
- Therefore, when `DATA_SPLIT_PATH` matches the original run, validation should come from IDs outside this recovered `1400` set.
- The BIT notebook previously had a fallback path that sampled validation rows directly from full `train.csv` when `splited.csv` was unavailable.
- On the current exact-1400 artifact, that fallback would overlap with prebuilt training IDs on `98` validation rows.
- The BIT notebook has been updated so that it:
  - prefers the exact-1400 rich CSV artifacts
  - loads prebuilt training IDs early
  - removes validation overlaps against those IDs and replenishes from non-overlapping rows

## Measurement status

- Kaggle-compatible end-to-end training/inference score: `pending`
- Measured local data-pipeline status:
  - exact-1400 artifact generation: `completed`
  - fallback validation overlap before guard: `98`
  - notebook overlap guard: `implemented`
- Reason full score is still pending: this step updated artifacts and notebook data wiring only; no full Nemotron training/inference run was executed here.
