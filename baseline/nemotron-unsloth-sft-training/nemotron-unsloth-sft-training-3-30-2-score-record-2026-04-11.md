# nemotron-unsloth-sft-training-3-30-2 score record (2026-04-11)

## README contract

- Evaluation contract is taken from `README.md`.
- Base model: `NVIDIA Nemotron-3-Nano-30B-A3B-BF16`
- Submission: single LoRA adapter with `adapter_config.json`
- Inference assumptions: `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, `gpu_memory_utilization=0.85`, `max_model_len=8192`
- Final answer extraction prioritises `\boxed{}`

## Reference measured scores used for this notebook revision

### Baseline teacher dataset reference

Source:
- `baseline/nemotron-sft-lora-with-cot-v2/artifacts/train_split_with_cot.csv`
- documented in `baseline_mlx/baseline_mlx/baseline_mlx-results.md`

Measured reference:
- HF notebook reference local320: `249/320 = 0.7781`
- family breakdown: binary `29/60`, gravity `50/50`, roman `50/50`, symbol `22/60`, text `49/50`, unit `49/50`

### v3f binary-heavy reference

Source:
- `baseline/nemotron-sft-lora-with-cot-v2/artifacts/train_split_with_cot_v3f_safe_plus_notformula.csv`
- documented in `baseline/nemotron-sft-lora-with-cot-v2/result/v3f/v3f_effects_risks_and_next_strategy.md`

Measured reference:
- local320: `249/320 = 0.7781`
- binary specialized 563: `238/563 = 0.4227`
- binary hard 60: `27/60 = 0.4500`

## Current notebook revision

Target notebook:
- `baseline/nemotron-unsloth-sft-training/nemotron-unsloth-sft-training-3-30-2.ipynb`

Revision summary:
- non-bit training rows now prefer reproducible teacher data from `train_split_with_cot.csv`
- bit training rows are rebuilt from public `train.csv` instead of relying on private trace datasets
- rebuilt bit traces follow the structure of `Strategy to solve 85% of bit manipulation.md` and `c4a6d52b.txt`
- bit quota is set to `1021` rows to match the established notebook-current binary mix while keeping non-bit quotas at `300 / 400 / 700 / 700 / 200`
- validation still comes from public `train.csv` hold-out logic
- notebook training-data assembly has been moved out of the notebook runtime; the notebook now loads prebuilt CSV artifacts and trains from them

## Generated CSV artifacts

Artifact directory:
- `baseline/nemotron-unsloth-sft-training/artifacts/`

Generated files:
- `training_source_repro_public_bit_v1_2026-04-11.csv`
- `formatted_train_dataset_repro_public_bit_v1_2026-04-11.csv`

Artifact row counts:
- training source rows: `3321`
- formatted train rows: `3321`

Artifact composition:
- Bit Manipulation: `1021`
- Text Encryption: `700`
- Unit Conversion: `700`
- Gravitational Constant: `400`
- Numeral Conversion: `300`
- Equation Transformation: `200`

Source composition:
- rebuilt_bit_strategy_trace: `1021`
- teacher_csv::Text Encryption: `700`
- teacher_csv::Unit Conversion: `700`
- teacher_csv::Gravitational Constant: `400`
- teacher_csv::Numeral Conversion: `300`
- teacher_csv::Equation Transformation: `200`

## Measurement status for this revision

- target score: `0.85`
- measured score in this workspace: `pending`
- reason: this turn only updated the notebook and provenance files; no end-to-end Kaggle BF16 training/inference run was executed from this Linux workspace
- next required measurement: run the notebook in the Kaggle-compatible environment, record local validation and specialized binary scores, then append the actual measured result here

## Local preflight metrics in this Linux workspace

These are not Kaggle leaderboard-equivalent scores. They only verify that the rebuilt BIT teacher selection behaves as intended before full training.

Environment note:
- local GPU detected here: `NVIDIA GeForce RTX 3060 12GB`
- this is insufficient for the intended Nemotron BF16 training/inference flow described in `README.md`, so only data-pipeline preflight checks were performed here

Measured preflight results:
- public bit rows in `data/train.csv`: `1602`
- top selected rebuilt bit rows: `1021`
- fully supported rows across all bit rows: `1460 / 1602 = 0.9114`
- fully supported rows inside selected top-1021 pool: `1021 / 1021 = 1.0000`
- mean supported bits across all bit rows: `7.8414`
- mean supported bits inside selected top-1021 pool: `8.0000`
- mean continuity span across all bit rows: `34.2316`
- mean continuity span inside selected top-1021 pool: `40.8962`
- supported-bits histogram across all bit rows: `{2: 1, 3: 2, 4: 8, 5: 20, 6: 35, 7: 76, 8: 1460}`

Interpretation:
- the rebuilt BIT selector successfully finds a fully supported `1021`-row subset from the public bit pool
- this validates the structural intent of the notebook revision: keep the binary-heavy mix while avoiding dependence on private BIT traces
- this does **not** validate final notebook score; only Kaggle-side training plus validation/inference can do that
