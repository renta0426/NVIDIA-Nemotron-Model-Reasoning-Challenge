# v7 targeted miss-recovery results

## Why v7 exists

v6 experiments ran into paused/stuck training runs and high complexity.
v7 restarts with a clean, minimal design: **laser-focus on the exact 19 confirmed
local300 miss IDs** from the retained best baseline
(`v20_mlx_repro_v1_fullrun_targetfix_mb1_nobc`, local300 = 254/300 = 0.846667).

## Targeted miss sets

### bit_manipulation misses (16)
000b53cf, 012fb81b, 01e09228, 02a66bcb, 034fb629, 048cc279, 04d8c3e6, 05ca617c, 06881e47, 07e8cf66, 0b16458a, 0ec17d2e, 12fd5b6c, 132ec6ae, 16db2c74, 172d2417

### cipher misses (1)
0184a864

### equation_numeric_guess misses (2)
065f9dea, 0c0683c3

## No-cryptarithm rationale

Cryptarithm is a hard, low-ROI category for local300.  Budget saved here is reallocated
to more answer-only repeats on the confirmed miss IDs.

## Teacher-match diagnostic

Only IDs where the teacher reasoning file's last `\boxed` answer matches the gold answer
get reasoning-style examples.  All IDs unconditionally get answer-only examples.

Known absent from `train_recommended_learning_target_v1.csv`: `0ec17d2e`
(handled gracefully; uses `train.csv` prompt/answer only).

## Dataset composition

| Field | Value |
|-------|-------|
| Base examples | 7828 |
| Overlay examples | 638 |
| Total examples | 8466 |
| Total steps | 265 |
| Base steps | 245 |
| Overlay steps | 20 |
| Total tokens | 28174571 |
| Max sequence length | 7971 |
| Answer-only repeats / miss | 32 |
| Reasoning repeats / miss (when teacher=gold) | 10 |
| Unique miss IDs covered | 19 |

### Overlay by category

| Category | Examples |
|----------|---------|
| bit_manipulation | 532 |
| cipher | 42 |
| equation_numeric_guess | 64 |

### Overlay by style

| Style | Examples |
|-------|---------|
| answer_only | 608 |
| reasoning | 30 |

## Bundle path

`/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/A-Open-ProgressPrizePublication/nemotron/training/sft/MLX/v7_targeted_miss_recovery_bundle.jsonl`

## Current status

- Bundle generated: YES
- MLX training:
  - `v20_mlx_v7_targeted_miss_recovery_mlxdir_mb1_nobc`: stopped before completion at step 183/265; no `training_result.json`, and its stale output root has since been cleaned to save disk
  - `v20_mlx_v7_targeted_miss_recovery_mlxdir_mb1_nobc_ckpt20`: running again with detached execution, `save_every_steps=20`, `max_saved_checkpoints=3`, resume-aware supervision, and a stale-progress guard that kills only the exact train PID if `latest_train_report.json` goes stale for `>= 2400s` (**step 195 observed**, so it has already passed the earlier `183/265` failure point; retained periodic checkpoints are `140 / 160 / 180`)
- runtime status: `running`
- latest observed step: `208`
- retained checkpoints: `0000160_adapters.safetensors / 0000180_adapters.safetensors / 0000200_adapters.safetensors`
- completed-run cleanup: `postprocess-run` / `full-run` now prune periodic `*_adapters.safetensors` checkpoints and remove `training_bundle_tokens/` by default after a completed evaluation summary exists
- score ledger update: `postprocess-run` now writes the measured local300 score back into this tracked markdown ledger automatically once an `adapter_validation` 300-row summary exists
- score publish watcher: a detached single-file `watch-score-publish` worker is now armed to detect completed local300 validation, rerun `postprocess-run` defensively, and `git add/commit/push` the updated tracked score ledger while skipping publish attempts whenever `.git/index.lock` is present
- progress ledger watcher: a detached single-file `watch-progress-ledger` worker now publishes `runtime status` / `latest observed step` / `retained checkpoints` back into this ledger on status or checkpoint changes and at a 5-step cadence, while backing off whenever `.git/index.lock` is present
- local300 score after training: TBD

## Generated

2026-04-22T09:22:52Z
