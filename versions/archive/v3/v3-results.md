# V3 Results

## Update 2026-04-12

- `versions/v3/code/train.py` `package-peft` now live-reloads the authoritative `README.md` submission wording and hard-fails if local packaging config drifts from the README-overlapping contract.
- The v3 CUDA packaging default archive name is now `submission.zip` instead of the older version-suffixed local name, matching README Submitting.
- v3 packaging artifacts now surface `readme_submission_contract` plus `readme_submission_contract_verified_from_readme_file = true`, while keeping the local packaging contract explicit in the emitted JSON.
- Regression coverage was extended in:
  - `versions/v3/tests/test_v3_packaging_spec.py`
  - `versions/v3/tests/test_cuda_reproduction_packaging.py`
  - `versions/v3/tests/test_v3_bootstrap.py`
- Runtime execution remains blocked in this session by the host PTY failure (`posix_openpt failed: Device not configured`), so this update is static hardening only.

## Executive summary

`v3` で得られた主な成果は、**Mac/MLX 上で v3 の実験基盤を最後まで実働化し、strict logging 付きで Stage A / Stage B の weighted SFT pilot を完走させたこと**です。

一方で、**この時点では「ローカルスコアが良かった」とは言えません**。理由は、`v3` ではまだ shadow split / holdout / Kaggle metric 相当のローカル評価を回しておらず、確認できているのは teacher trace の品質、train/val loss、mix 生成の整合性、CUDA handoff までです。

したがって、以前の「task complete」は **Mac 側での v3 実装・実行・記録タスクが完了した**という意味であり、**ローカルスコア改善が証明された**という意味ではありません。

## What was completed

- `versions/v3/code/train.py`
  - v3 CLI
  - teacher trace pipeline
  - strict format / correction / preference / RFT pool builders
  - weighted train mix builder
  - custom weighted MLX SFT runtime
  - CUDA reproduction spec renderer
  - runbook / registry outputs

- `versions/v3/tests/test_v3_*.py`
  - v3 用テストを追加
  - `uv run pytest -q` は `109 passed`

## Actual experiment results

### 1. Teacher trace pipeline

#### First attempt

- command family:
  - `bootstrap-v3`
  - `build-teacher-trace-candidates --max-rows 3`
  - `generate-teacher-traces --limit 8`
  - `filter-teacher-traces`
  - `audit-format`

- result:
  - sampled 8 candidates
  - 8/8 failed at generation time
  - error: `generate_step() got an unexpected keyword argument 'temp'`

- action taken:
  - generation code was fixed to use `mlx_lm.sample_utils.make_sampler(...)`
  - the failure is preserved in logs

#### Second attempt after runtime fix

- sampled 8 candidates again
- generation itself succeeded
- strict accepted traces: `0 / 8`
- all sampled rows ended in strict reject
- observed failure mode:
  - `selection_reason = wrong_answer`
  - `format_bucket = last_number_fallback`

This means the model did not reliably produce the required final answer line under the sampled bit-manipulation prompts. So, **teacher-trace distillation was operationally verified, but it did not yet yield usable strict traces in this sampled run**.

### 2. Strict pair pools

Artifacts generated:

- `versions/v3/data/synth/format_pairs_strict_v3.parquet`
  - `19000` rows
- `versions/v3/data/synth/correction_pairs_strict_v3.parquet`
  - `2375` rows
- `versions/v3/data/preference/preference_pairs_v3.parquet`
  - `21375` rows
- `versions/v3/data/preference/rft_accept_pool_v3.parquet`
  - `0` rows

`rft_accept_pool_v3.parquet` が `0` 行なのは、teacher strict pass が sampled run で `0` 件だったためです。これは仕様通りです。

### 3. Train mix builder

#### Initial mix-builder failure

最初の `build-train-mix` 実行では、`v2` 由来 row の `format_policy` が `v3` 形式へ正規化されていなかったため、weighted final span 検出に失敗しました。

その結果、いったん次のような異常状態になりました。

- Stage A rows: `0`
- Stage B rows: `500`
- accepted rows were almost entirely correction-only

#### After fix

`v2` の `format_policy` を `v3` の `boxed` / `final_answer` に正規化する修正を入れ、再生成しました。

最終的な train pack は以下です。

- `versions/v3/data/train_packs/stage_a_strong_v3.parquet`
  - `12000` rows
- `versions/v3/data/train_packs/stage_b_strong_v3.parquet`
  - `9000` rows

### 4. Weighted SFT pilot

#### Stage A pilot

- candidate id: `v3-stage-a-pilot-001`
- train pack: `stage_a_strong_v3.parquet`
- config: `sft_stage_a_weighted_mlx`
- pilot size:
  - train rows: `8`
  - valid rows: `2`
- result:
  - final train loss: `0.8024193644523621`
  - final val loss: `1.671875`
  - peak memory: `32.999992148 GB`

Artifacts:

- manifest:
  - `versions/v3/outputs/train/pilot_stage_a_run1/sft_a_sft_stage_a_weighted_mlx_manifest.json`
- result:
  - `versions/v3/outputs/train/pilot_stage_a_run1/sft_a_sft_stage_a_weighted_mlx_result.json`
- metrics:
  - `versions/v3/outputs/train/pilot_stage_a_run1/sft_a_sft_stage_a_weighted_mlx_metrics.jsonl`
- adapter dir:
  - `versions/v3/outputs/train/pilot_stage_a_run1/adapter_a_sft_stage_a_weighted_mlx`

#### Stage B pilot

- candidate id: `v3-stage-b-pilot-001`
- train pack: `stage_b_strong_v3.parquet`
- config: `sft_stage_b_weighted_mlx`
- pilot size:
  - train rows: `8`
  - valid rows: `2`
- result:
  - final train loss: `1.91576087474823`
  - final val loss: `2.7182202339172363`
  - peak memory: `30.719048974 GB`

Artifacts:

- manifest:
  - `versions/v3/outputs/train/pilot_stage_b_run1/sft_b_sft_stage_b_weighted_mlx_manifest.json`
- result:
  - `versions/v3/outputs/train/pilot_stage_b_run1/sft_b_sft_stage_b_weighted_mlx_result.json`
- metrics:
  - `versions/v3/outputs/train/pilot_stage_b_run1/sft_b_sft_stage_b_weighted_mlx_metrics.jsonl`
- adapter dir:
  - `versions/v3/outputs/train/pilot_stage_b_run1/adapter_b_sft_stage_b_weighted_mlx`

#### Pilot comparison

現時点の小型 pilot 比較では、**Stage A が Stage B より明確に良い**です。

- Stage A val loss: `1.671875`
- Stage B val loss: `2.7182202339172363`

ただし、これはあくまで **小型 Mac pilot の loss 比較** です。まだ shadow accuracy や competition metric による評価ではありません。

## Does v3 already have a good local score?

**No. Not yet proven.**

この時点で言えること:

- v3 pipeline is implemented and runnable
- v3 weighted training works on Mac
- Stage A pilot currently looks better than Stage B pilot on tiny train/val loss
- teacher strict trace quality is still poor in the sampled run

この時点でまだ言えないこと:

- `v3` が `v2` よりローカル精度で上回った
- `v3` が Kaggle private/public LB で有利
- sampled teacher failure を乗り越えた strong recipe が完成した

## Logs and registries

### Failure-inclusive logs

- teacher generation logs:
  - `versions/v3/outputs/datasets/teacher_trace_generations_v3.jsonl`
- teacher registry:
  - `versions/v3/data/processed/teacher_trace_registry_v3.parquet`
- format audit:
  - `versions/v3/outputs/audits/format_audit_v3.csv`

### Experiment summaries

- weighted ablations:
  - `versions/v3/outputs/reports/weighted_ablation_v3.csv`
- candidate registry:
  - `versions/v3/data/processed/candidate_registry_v3.csv`
- CUDA reproduction registry:
  - `versions/v3/data/processed/cuda_reproduction_registry_v3.csv`

## CUDA handoff artifacts

Generated:

- `versions/v3/outputs/handoff/cuda_reproduction_spec_v3.yaml`
- `versions/v3/outputs/handoff/cuda_reproduction_spec_v3.sh`
- `versions/v3/outputs/handoff/cuda_reproduction_spec_stage_b_v3.yaml`
- `versions/v3/outputs/handoff/cuda_reproduction_spec_stage_b_v3.sh`

At this moment, the best manual CUDA reproduction target is:

- **First choice:** `v3-stage-a-pilot-001`
- **Reason:** Stage A pilot beat Stage B pilot on tiny Mac validation loss, and Stage B looked correction-heavy and weaker.

## Recommendation

1. Kaggle CUDA / BF16 ではまず `v3-stage-a-pilot-001` を再現する。
2. その CUDA run で local shadow / holdout / submission candidate evaluation を取る。
3. teacher trace prompting は別途改善し、strict pass を増やしてから distillation を本格投入する。
4. Stage B は現状では優先度を下げる。
