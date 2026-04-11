# nemotron-unsloth-sft-training-BIT exact-original1400 score record (2026-04-11)

## README contract

- Evaluation contract is taken from `README.md`.
- Base model: `NVIDIA Nemotron-3-Nano-30B-A3B-BF16`
- Submission: single LoRA adapter with `adapter_config.json`
- Inference assumptions: `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, `gpu_memory_utilization=0.85`, `max_model_len=8192`
- Final answer extraction prioritises `\boxed{}`

## Target notebook revision

- notebook: `baseline/nemotron-unsloth-sft-training/nemotron-unsloth-sft-training-BIT.ipynb`
- fixed training dataset:
  - `/kaggle/input/datasets/happymiik/artifacts/formatted_train_dataset.csv`
- training source sidecar CSV:
  - unused in the current notebook revision

## Revision summary

- recovered the exact original `1400` bit training IDs from the pre-swap artifact
- regenerated those exact bit rows with the public bit strategy
- preserved the full original `3910`-row composition
- added a validation overlap guard so fallback validation does not reuse prebuilt training IDs
- updated the BIT notebook so training now reads only the fixed two-column CSV at `/kaggle/input/datasets/happymiik/artifacts/formatted_train_dataset.csv`
- fixed the notebook training input to `/kaggle/input/datasets/happymiik/artifacts/formatted_train_dataset.csv`
- removed local artifact path fallbacks and rich formatted CSV fallback logic from the SFT data loader

## Measured local data-pipeline metrics

- formatted rows: `3910`
- training source rows: `3910`
- category counts:
  - `bit_manipulation`: `1400`
  - `text_decryption`: `1300`
  - `unit_conversion`: `200`
  - `numeral_system`: `200`
  - `gravity_physics`: `200`
  - `symbol_transform`: `10`
  - `numeric_equation`: `600`
- fully supported bit rows on recovered exact IDs: `1274 / 1400 = 0.91`
- fallback validation overlap before notebook guard: `98`

## Interpretation

- This revision matches the original 3-30-2 bit ID set rather than the earlier `1021` fully-supported public subset.
- It is therefore better aligned to the original training artifact identity, but structurally weaker than the top-1021 subset on raw bit-support purity.
- The notebook-side validation guard is necessary whenever `splited.csv` is missing or inconsistent, because the fallback validation path can otherwise leak prebuilt training IDs.

## Measurement status

- Kaggle-compatible end-to-end training score in this workspace: `pending`
- Reason: no full training/inference run was executed in this step
- Next required measurement:
  - run the BIT notebook against the exact-original1400 rich artifact
  - record local validation and any specialized binary score
  - append the measured score to this file
