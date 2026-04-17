# v20_mlx_repro_v1 results

> Repository note: canonical challenge contract lives in `README.md`.
> This version is a local MLX reproduction of A-Open v20 using `A-Open-ProgressPrizePublication/nemotron/training/sft/04-08-16-14/` as the exact training snapshot.
> It does **not** claim submission.zip parity; it measures how closely MLX reproduces the published v20 training/eval behavior.

## Source contract

- Top-level README: `README.md`
- V20 snapshot: `A-Open-ProgressPrizePublication/nemotron/training/sft/04-08-16-14`
- Publication notes: `A-Open-ProgressPrizePublication/README.md`, `A-Open-ProgressPrizePublication/データ戦略を理解する.md`, `A-Open-ProgressPrizePublication/学習SFTパイプライン.md`
- Validation reference: `A-Open-ProgressPrizePublication/adapter-validation-notebook.ipynb`

## Baseline reproduced run

- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/v20_mlx_repro_v1/outputs/v20_mlx_repro_v1_fullrun_targetfix_mb1`
- backend: `mlx`
- optimizer_steps: `245`
- final_train_loss: `0.00030877206662561054`
- last_lr: `8.163265306122547e-07`
- local300_accuracy: **`0.82` (246/300)** on `adapter_validation_stratified_category_300_of_950`

| category | correct | total | accuracy |
| --- | ---: | ---: | ---: |
| bit_manipulation | 37 | 53 | 0.698113 |
| cipher | 50 | 51 | 0.980392 |
| cryptarithm_deduce | 0 | 23 | 0.000000 |
| cryptarithm_guess | 1 | 5 | 0.200000 |
| equation_numeric_deduce | 7 | 15 | 0.466667 |
| equation_numeric_guess | 0 | 2 | 0.000000 |
| gravity | 50 | 50 | 1.000000 |
| numeral | 47 | 47 | 1.000000 |
| unit_conversion | 54 | 54 | 1.000000 |

## Gap analysis after baseline

- Publication deterministic reasoners on the same 300-row subset reached **`257/300 = 0.856667`**.
- Reasoner-over-model gains were concentrated in `equation_numeric_deduce` (`7 -> 15`), with smaller possible headroom in `bit_manipulation` (`37 -> 39`) and `cipher` (`50 -> 51`).
- Same-weights `--no-eval-enable-thinking` probes did **not** rescue the missing skill:
  - exact `equation_numeric_deduce` misses: **`0/8`** recovered
  - exact `bit_manipulation` misses: **`0/16`** recovered
  - focus slice (`bit_manipulation + equation_numeric_deduce`, `68` rows): **`44/68 -> 4/68`**
- Working diagnosis after those probes: the dominant residual was more consistent with **training / weight divergence** than with eval extraction or thinking-mode verbosity alone.
- The strongest remaining strict-reproduction hypothesis was the optimizer/backend path (`paged_adamw_8bit` / Tinker side evidence versus MLX `optim.Adam`).

## No-bias-correction retrain

- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/v20_mlx_repro_v1/outputs/v20_mlx_repro_v1_fullrun_targetfix_mb1_nobc`
- changed_condition: exact same snapshot replay and `micro_batch_size=1`, with **only** `Adam bias_correction=False`
- final_train_loss: `0.00031850469393745887`
- trained_tokens: `26568807`
- peak_memory_gb: `222.0017`
- total_elapsed_seconds: `74801.3432`
- vs_baseline_train_delta:
  - loss: `+9.732627311848335e-06`
  - peak_memory_gb: `+0.0608`
  - elapsed_seconds: `-445.7722`
- smoke8_accuracy: **`6/8 = 0.75`**
- smoke note: clean eval, so the 300-row stratified adapter-validation was manually launched despite the original smoke gate

## Final local300 result for nobc

- evaluation_name: `adapter_validation_stratified_category_300_of_950`
- overall_accuracy: **`0.846667` (254/300)**
- delta_vs_baseline: **`+8` correct / `+0.026667` accuracy**
- gap_to_reasoner_reference: **`-3` correct** versus `257/300 = 0.856667`
- source_of_gain: **`equation_numeric_deduce 7/15 -> 15/15`**

| category | baseline | nobc | delta |
| --- | ---: | ---: | ---: |
| bit_manipulation | 37 / 53 | 37 / 53 | 0 |
| cipher | 50 / 51 | 50 / 51 | 0 |
| cryptarithm_deduce | 0 / 23 | 0 / 23 | 0 |
| cryptarithm_guess | 1 / 5 | 1 / 5 | 0 |
| equation_numeric_deduce | 7 / 15 | 15 / 15 | +8 |
| equation_numeric_guess | 0 / 2 | 0 / 2 | 0 |
| gravity | 50 / 50 | 50 / 50 | 0 |
| numeral | 47 / 47 | 47 / 47 | 0 |
| unit_conversion | 54 / 54 | 54 / 54 | 0 |

## Retained output runs

- `v20_mlx_repro_v1/outputs/v20_mlx_repro_v1_fullrun_targetfix_mb1`
- `v20_mlx_repro_v1/outputs/v20_mlx_repro_v1_fullrun_targetfix_mb1_nobc`
- All other intermediate MLX output directories under `v20_mlx_repro_v1/outputs/` were pruned after the `0.846667` result was confirmed, so the workspace now keeps only the latest best run and the immediately previous `0.8+` baseline run.

## Interpretation

- `Adam bias_correction=False` was a **real high-signal MLX-side change**: it did not move the symbolic `cryptarithm_*` families, but it completely closed the observed `equation_numeric_deduce` gap on this local300 slice.
- The nobc retrain therefore beat the earlier MLX baseline (`0.82 -> 0.846667`) even though its smoke score was worse (`7/8 -> 6/8`).
- The remaining stubborn buckets are still `cryptarithm_deduce`, `cryptarithm_guess`, `equation_numeric_guess`, and the residual `bit_manipulation` misses.

## Important assumptions

- Training data uses the exact checked-in v20 snapshot `04-08-16-14/tokens` + `logprobs/index.jsonl`, not the current `corpus.jsonl`.
- Optimizer-step grouping uses the recorded `step` assignments from the snapshot, so the MLX run replays the actual v20 batch membership/order.
- MLX-specific assumptions not explicit in the public v20 config: `lora_alpha = 32` and `lora_dropout = 0.0`.
- The baseline full run used MLX `Adam bias_correction = True`; the recorded strict-reproduction variant `v20_mlx_repro_v1_fullrun_targetfix_mb1_nobc` changed only that flag to `False`.
