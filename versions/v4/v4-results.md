# v4 Results

## Summary

- `versions/v4/code/train.py` was converted from the copied v3 baseline into a v4-specific Stage C CLI.
- `versions/v4/tests/` was added and the new v4 surface is covered by unit tests.
- Repository validation is green after the v4 implementation.
- Real v4 data generation has started on Mac/MLX.
- Current best local hard-gate candidate is `v5_merge_run3_run6_80_20` with `hard_shadow_256 = 0.5859375`.
- Current best local shadow-side serious candidate remains `v5_merge_run3_run6_85_15` with `shadow_256 = 0.5625`.
- Fine-grained merge-ratio sweeps now look diagnostic rather than transformative: `82/18` regressed on quick, so future gains need structural changes on weak families rather than more merge interpolation.
- `README.md` official evaluation parameters remain fixed during all local scoring:
  - `max_tokens = 7680`
  - `top_p = 1.0`
  - `temperature = 0.0`
  - `max_num_seqs = 64`
  - `max_model_len = 8192`

## Code / Validation

- `uv run pytest -q versions/v1/tests/test_evaluator_core.py versions/v1/tests/test_eval_determinism.py versions/v4/tests/test_v4_builders.py versions/v4/tests/test_v4_stagec.py`
  - Result: `12 passed`
- `uv run pytest -q -k 'not test_download_model_to_repo_model_dir'`
  - Result: `125 passed, 1 deselected, 2 warnings`
- `uv run python -m py_compile versions/v1/code/train.py versions/v4/code/train.py versions/v2/tests/test_model_download_bootstrap.py`
  - Result: passed

## 2026-03-24 Follow-up Status

- Shared MLX evaluator acceleration is now in place in `versions/v1/code/train.py`:
  - persistent in-process model+adapter loading
  - deterministic batched `mlx_lm.batch_generate`
  - dataset shard parallelism for local gates
  - chunk / heartbeat logging for long-running official-parameter evaluation
- RFT accept-pool sanitization was added in `versions/v4/code/train.py`:
  - strip known MLX warning prefixes from completions
  - estimate trace token length before acceptance
  - materialize cleaned `chosen_output` / `target_text` into the rebuilt Stage C mix
- After rebuilding the accept pool:
  - accepted rows dropped from `24` to `4`
  - all accepted rows are `bit_manipulation`
  - rebuilt Stage C mix now has `3940` rows and no missing `chosen_output`
- Current scored reruns:
  - `v4_rft_stage_c_cleanaccept_run2`
    - quick `shadow_128 overall_accuracy = 0.0078125`
    - rejected as a near-empty collapse candidate
  - `v4_rft_stage_c_cleanaccept_lowlr_run3`
    - quick `shadow_128 overall_accuracy = 0.515625`
    - `format_fail_rate = 0.9609375`
    - `boxed_rate = 0.59375`
    - `avg_output_len_chars = 10519.59375`
    - serious `shadow_256 overall_accuracy = 0.5234375`
    - serious `hard_shadow_256 overall_accuracy = 0.5703125`
    - `shadow_256 format_fail_rate = 0.984375`
    - `hard_shadow_256 format_fail_rate = 0.96875`
    - `shadow_256 avg_output_len_chars = 10825.73828125`
    - `hard_shadow_256 avg_output_len_chars = 10024.578125`
    - this is the current best local v4/v5 candidate so far, but it is still clearly format-fragile
    - family behavior is highly uneven:
      - `gravity_constant = 1.0`
      - `roman_numeral = 1.0`
      - `unit_conversion ≈ 0.62-0.67`
      - `text_decryption ≈ 0.29-0.48`
      - `bit_manipulation ≈ 0.12`
      - `symbol_equation ≈ 0.12-0.16`
  - `v4_rft_stage_c_cleanaccept_halfepoch_run5`
    - quick `shadow_128 overall_accuracy = 0.5078125`
    - `format_fail_rate = 0.984375`
    - `boxed_rate = 0.59375`
    - `avg_output_len_chars = 10436.6796875`
    - slightly worse than `run3 quick` and not materially cleaner, so it is not promoted to serious scoring
- Recent sweep outcomes:
  - completed training plus local-gate results:
    - `v4_rft_stage_c_cleanaccept_ultralowlr_run4`
      - `final_val_loss = 0.8187304735`
      - quick `shadow_128 overall_accuracy = 0.515625`
      - `format_fail_rate = 0.9609375`
      - `boxed_rate = 0.578125`
      - `avg_output_len_chars = 11198.671875`
      - tied on quick accuracy, but was clearly weaker than `run6` on formatting and output length, so it was not promoted
    - `v4_rft_stage_c_cleanaccept_answerbias_run6`
      - `final_val_loss = 0.7242920995`
      - quick `shadow_128 overall_accuracy = 0.515625`
      - `format_fail_rate = 0.9453125`
      - `boxed_rate = 0.609375`
      - `avg_output_len_chars = 10411.8984375`
      - quick matched `run3` accuracy while modestly improving format failure, so it was promoted immediately to serious scoring
      - serious `shadow_256 overall_accuracy = 0.53515625`
      - serious `shadow_256 format_fail_rate = 0.9375`
      - serious `shadow_256 boxed_rate = 0.65625`
      - serious `shadow_256 avg_output_len_chars = 10174.84765625`
      - serious `hard_shadow_256 overall_accuracy = 0.51953125`
      - serious `hard_shadow_256 format_fail_rate = 0.91796875`
      - serious `hard_shadow_256 boxed_rate = 0.6484375`
      - serious `hard_shadow_256 avg_output_len_chars = 9780.27734375`
      - overall interpretation: `run6` beat `run3` on `shadow_256` and was much cleaner, but underperformed `run3 hard_shadow_256 = 0.5703125`, so `run3` remains the best overall serious local candidate
    - `v4_rft_stage_c_cleanaccept_answerbias_halfepoch_run7`
      - `final_val_loss = 0.7548022866`
      - quick `shadow_128 overall_accuracy = 0.4765625`
      - `format_fail_rate = 1.0`
      - `boxed_rate = 0.5078125`
      - `avg_output_len_chars = 9978.3125`
      - clearly below the current quick bar, so it was not promoted
    - `v4_rft_stage_c_cleanaccept_answerbias_ultralowlr_run8`
      - training later completed with `final_val_loss = 0.7397576571`
      - among the current fallback quick candidates, this is now the best completed unscored one
      - quick `shadow_128 overall_accuracy = 0.515625`
      - `format_fail_rate = 0.9921875`
      - `boxed_rate = 0.578125`
      - `avg_output_len_chars = 11490.8203125`
      - tied on quick accuracy, but was too format-fragile to justify serious promotion
- Current answer-biased / low-update sweep status:
  - the main `run4` / `run6` / `run7` / `run8` quick sweep has now completed
  - `run3` remains the best overall serious local checkpoint
  - `run6` remains the most informative alternate because it improved `shadow_256` and formatting, but it did not hold on `hard_shadow_256`
- `v5_format_sft_anchor_run1` quick scoring was resumed after the serious gate, but paused again because `format-SFT quick + 5 train sweeps` pushed memory too close to the OOM boundary.
- Current automation:
  - a watcher waits for `run6 quick` to finish
  - if `run6 quick` is promising, it auto-launches `candidate_score_serious.yaml` for `run6`
  - otherwise it auto-selects the best completed unscored fallback candidate among `run7`, `run8`, and `run4` by `final_val_loss` and launches the next quick gate
  - the next single-scorer stage is configured for `10` shards because `run6 quick` + remaining train jobs still left about `~189 GB` of free pages
  - this watcher already triggered once: `run6 quick` met the promotion rule and `run6 serious` is now live on `10` shards
  - a second watcher is queued behind `run6 serious` so that, once `hard_shadow_256` finishes, the best completed unscored fallback candidate among `run7`, `run8`, and `run4` automatically enters quick scoring
  - after `run8` training completed, the fallback order became `run8 -> run7 -> run4` by final validation loss
  - after `run6 serious` finished, that second watcher auto-launched `run8 quick`
  - `run8 quick` was then reviewed manually and rejected for serious promotion because its formatting was materially worse than `run6` / `run3`; `run7 quick` was launched next
- quick differential note (`run6` vs `run3`):
  - overall accuracy stayed tied at `0.515625`
  - `run6` improved `text_decryption` (`0.2857 -> 0.4762`) and `bit_manipulation` (`0.0455 -> 0.0909`)
  - `run6` shortened `text_decryption` outputs materially
  - the main regression was `unit_conversion` (`0.8095 -> 0.5714`), with several rows moving from correct `boxed_multiple` answers to `last_number_fallback`
  - this suggests answer-bias is helping text-style answer fidelity more than numeric final-answer precision

## 2026-03-24 Merge checkpoint

- `v5_format_sft_anchor_run1`
  - quick `shadow_128 overall_accuracy = 0.4921875`
  - `format_fail_rate = 0.984375`
  - `boxed_rate = 0.5703125`
  - `avg_output_len_chars = 10911.4140625`
  - this did not recover formatting enough and was not promoted
- `v5_merge_run3_run6_85_15`
  - quick `shadow_128 overall_accuracy = 0.5390625`
  - `format_fail_rate = 0.984375`
  - `boxed_rate = 0.6171875`
  - `avg_output_len_chars = 10822.90625`
  - serious `shadow_256 overall_accuracy = 0.5625`
  - serious `hard_shadow_256 overall_accuracy = 0.55859375`
  - `shadow_256 format_fail_rate = 0.9921875`
  - `hard_shadow_256 format_fail_rate = 0.9765625`
  - interpretation:
    - this is the current **best shadow-side serious** candidate
    - it does not beat `run3 hard_shadow_256 = 0.5703125`
    - therefore it is a strong balanced candidate, but not an outright replacement for `run3`
- `v5_merge_run3_run6_75_25`
  - quick `shadow_128 overall_accuracy = 0.515625`
  - `format_fail_rate = 0.953125`
  - `boxed_rate = 0.6328125`
  - `avg_output_len_chars = 10286.359375`
  - serious `shadow_256 overall_accuracy = 0.5390625`
  - serious `hard_shadow_256 overall_accuracy = 0.5625`
  - `shadow_256 format_fail_rate = 0.9765625`
  - `hard_shadow_256 format_fail_rate = 0.96484375`
  - `hard_shadow_256 avg_output_len_chars = 9721.1015625`
  - interpretation:
    - `75/25` is weaker than `85/15` on `shadow_256`, but stronger on `hard_shadow_256`
    - it still does not beat `run3 hard_shadow_256`, but it is cleaner than both `run3` and `85/15`
    - this is the current **best balanced merge** candidate
- overall local ranking after the merge sweep:
  - `run3` remains the best hard-robust serious checkpoint (`hard_shadow_256 = 0.5703125`)
  - `85/15` is the best shadow-side serious checkpoint (`shadow_256 = 0.5625`)
  - `75/25` is the cleanest merge and the closest balanced compromise
  - none of the merge candidates clearly dominates `run3` on both serious datasets
- next parallel continuation:
  - `v4_rft_stage_c_cleanaccept_hardrobust_run9` is training in parallel
  - config change vs `run3`:
    - `learning_rate = 3.5e-5`
    - `final_line_weight = 4.0`
    - `bit_manipulation = 6.0`
    - `symbol_equation = 7.0`
    - `text_decryption = 4.0`
  - the goal is to preserve `run3` hard robustness while strengthening final-answer supervision without reintroducing `run6`-style hard regressions

## 2026-03-25 Consolidated checkpoint

- `v4_rft_stage_c_cleanaccept_hardrobust_run9`
  - `final_train_loss = 0.5982142687`
  - `final_val_loss = 0.8202174902`
  - quick `shadow_128 overall_accuracy = 0.0390625`
  - `format_fail_rate = 0.90625`
  - `avg_output_len_chars = 257.4921875`
  - interpretation:
    - validation looked superficially acceptable, but local gate quality collapsed almost completely
    - aggressive weighted-loss / final-answer emphasis can create a “val looks okay, eval is dead” failure mode
- `v5_merge_run3_run6_80_20`
  - quick `shadow_128 overall_accuracy = 0.5390625`
  - `format_fail_rate = 0.9765625`
  - `boxed_rate = 0.6328125`
  - `avg_output_len_chars = 10822.484375`
  - serious `shadow_256 overall_accuracy = 0.5390625`
  - serious `shadow_256 format_fail_rate = 0.98046875`
  - serious `shadow_256 boxed_rate = 0.60546875`
  - serious `shadow_256 avg_output_len_chars = 10448.80859375`
  - serious `hard_shadow_256 overall_accuracy = 0.5859375`
  - serious `hard_shadow_256 format_fail_rate = 0.9765625`
  - serious `hard_shadow_256 boxed_rate = 0.6484375`
  - serious `hard_shadow_256 avg_output_len_chars = 9960.86328125`
  - interpretation:
    - this is the current **best local hard-gate candidate**
    - it clearly beats `run3 hard_shadow_256 = 0.5703125`
    - however it does not improve the shadow-side serious score over `75/25`, and it is still below `85/15 shadow_256 = 0.5625`
- `v5_merge_run3_run6_82_18`
  - quick `shadow_128 overall_accuracy = 0.4921875`
  - `format_fail_rate = 0.9765625`
  - `boxed_rate = 0.5859375`
  - `avg_output_len_chars = 11293.2421875`
  - interpretation:
    - this regressed sharply versus `80/20`
    - that makes further merge-ratio micro-sweeps look like diminishing-return diagnostics, not the main path to a step-function score gain
- `v4_rft_stage_c_cleanaccept_symbolboost_run10`
  - training completed
  - `final_train_loss = 0.3779761791`
  - `final_val_loss = 0.9210160971`
  - `peak_memory_gb = 34.24126099`
  - relative to `run3`, this changed only training/loss parameters:
    - `learning_rate: 1.0e-5 -> 5.0e-5`
    - `num_epochs: 1.0 -> 1.5`
    - `rationale_weight: 1.0 -> 0.8`
    - `final_line_weight: 3.0 -> 5.0`
    - answer-span weights shifted to `3/3/3/6/8/4`
  - interpretation:
    - this is still fundamentally a `run3`-family parameter variation, not a structural change in data or modeling
    - the final validation loss is worse than `run3` (`0.9210 > 0.8168`), so the chance of clearly updating the local best looked low
    - for that reason, inference was intentionally skipped at this checkpoint
- `v4_rft_stage_c_cleanaccept_balancedrobust_run11`
  - the first launch accidentally produced a `rendered_only` artifact because `train-stage-c-rft` was invoked without `--execute`
  - the real training rerun then completed successfully
  - `final_train_loss = 0.8444767594`
  - `final_val_loss = 0.7712868452`
  - `peak_memory_gb = 34.241110838`
  - relative to `run3`, this also changed only training/loss parameters:
    - `learning_rate: 1.0e-5 -> 1.2e-5`
    - `num_epochs: 1.0 -> 1.0` (unchanged)
    - `rationale_weight: 1.0 -> 1.0` (unchanged)
    - `final_line_weight: 3.0 -> 3.5`
    - answer-span weights shifted to `4/4/4/5.5/6.5/3.5`
  - interpretation:
    - this was a conservative `run3` refinement, not a new recipe class
    - the final validation loss improved over `run3` (`0.7713 < 0.8168`), so it looked better than `run10`
    - however the expected upside still looked incremental rather than the kind of jump needed to move meaningfully toward an official `0.9+`
    - therefore inference was also intentionally skipped at this checkpoint
- consolidated read after the current stop point:
  - best scored single-training checkpoint remains `run3`
  - best serious hard checkpoint overall is now `80/20`
  - best serious shadow checkpoint remains `85/15`
  - the biggest unresolved weak families are still `bit_manipulation`, `symbol_equation`, and `text_decryption`
  - `run10` / `run11` confirmed that simple parameter retuning around `run3` is not the main path forward
  - reaching an official score near `0.9` will require structural improvements on those weak families; merge interpolation alone is not enough

## Implemented v4 Commands

- `bootstrap-v4`
- `score-candidate`
- `score-candidate-batch`
- `build-format-preferences`
- `build-correctness-preferences`
- `build-rft-candidates`
- `filter-rft-accept-pool`
- `build-stage-c-mix`
- `train-stage-c-rft`
- `train-stage-c-preference`
- `train-specialist`
- `merge-candidates`
- `compress-merge-rank32`
- `render-cuda-repro-spec`
- `write-runbook`

## Real Runs Completed

### 1. bootstrap-v4

- Status: completed
- Output:
  - v4 scaffold/config/report directories created
  - v4 registry CSV headers created

### 2. build-format-preferences

- Status: completed
- Output path:
  - `versions/v4/data/preference/format_preference_pairs_v4.parquet`
- Rows:
  - `19000`
- Interpretation:
  - v3 preference pool already contains enough format-oriented pairs for immediate Stage C format tuning.

### 3. build-correctness-preferences

- Status: completed
- Output path:
  - `versions/v4/data/preference/correctness_preference_pairs_v4.parquet`
- Rows:
  - `1183`
- Interpretation:
  - correctness-side preference data is much smaller than format data, so early v4 preference tuning is likely to be format-heavy unless additional mining succeeds.

### 4. score-candidate (serious gate, Stage A baseline)

- Command:
  - `uv run python versions/v4/code/train.py score-candidate --config-path versions/v4/conf/eval/candidate_score_serious.yaml --candidate-id v3_stage_a_baseline`
- Candidate:
  - `v3_stage_a_baseline`
- Result:
  - `shadow_256 overall_accuracy = 0.4375`
  - `hard_shadow_256 overall_accuracy = 0.4375`
  - `shadow_256 format_fail_rate = 0.546875`
  - `hard_shadow_256 format_fail_rate = 0.5546875`
  - `extraction_fail_rate = 0.0`
  - `avg_output_len_chars ≈ 4.4k`
  - `submit_value = False`
- Interpretation:
  - current v3 Stage A trunk is not submission-worthy on the serious local gate.
  - the main visible issue is not answer extraction failure, but severe format instability / overlong responses.

## Real Runs Completed / In Progress

### 5. build-rft-candidates

- Command:
  - `uv run python versions/v4/code/train.py build-rft-candidates --config-path versions/v4/conf/data/rft_accept_pool.yaml --candidate-id v3_stage_a_baseline`
- Candidate:
  - `v3_stage_a_baseline`
- Prompt selection already written:
  - `288` prompts total
  - `96` each for `bit_manipulation`, `symbol_equation`, `text_decryption`
- Status:
  - completed
- Final output:
  - `versions/v4/data/rft/rft_candidate_generations_v4.jsonl`
- Note:
  - prompt selection and all `1152` probe generations were completed successfully on Mac/MLX.

### 6. filter-rft-accept-pool

- Input:
  - `1152` probe samples
  - `288` prompts
  - `4` samples per prompt
- Output:
  - `24` accepted rows
  - `264` rejected prompts
- Acceptance yield:
  - `24 / 288 = 8.33%`
- Accepted family distribution:
  - `bit_manipulation = 24`
- Interpretation:
  - the current Stage A parent only produces strict-accept RFT material on a narrow slice of the hard families.
  - `symbol_equation` and `text_decryption` were effectively zero-yield under the current strict filter.
  - after later warning-stripping and trace-length sanitization, the rebuilt strict accept pool shrank further to `4` rows and remained `bit_manipulation`-only.

### 7. build-stage-c-mix

- RFT mix output:
  - `versions/v4/data/train_packs/stage_c_rft_mix_v4.parquet`
  - rows: `3956`
- Preference mix output:
  - `versions/v4/data/train_packs/stage_c_preference_mix_v4.parquet`
  - rows: `3641`
- Preference mix composition:
  - `format = 2458`
  - `correction = 1183`
- RFT mix family distribution:
  - `symbol_equation = 838`
  - `bit_manipulation = 809`
  - `gravity_constant = 692`
  - `text_decryption = 675`
  - `unit_conversion = 605`
  - `roman_numeral = 337`
- Interpretation:
  - because strict RFT accepts were sparse, the Stage C RFT mix is still mostly replay-backed rather than pure accept-pool data.
  - after the sanitized rebuild, the live Stage C mix used by the latest reruns contains `3940` rows with only `4` explicit `rft_accept` rows and the rest coming from replay / real / core_synth data.

## Failures / Fixes Recorded

### A. Wrong default v3 preference source path

- Symptom:
  - `build-format-preferences` initially failed because the generated config pointed to `versions/v4/data/preference/preference_pairs_v3.parquet`.
- Cause:
  - v4 scaffold initially inherited a version-local default instead of the real v3 artifact path.
- Fix:
  - code defaults were changed to point at:
    - `versions/v3/data/preference/preference_pairs_v3.parquet`
  - config files updated:
    - `versions/v4/conf/data/preference_format.yaml`
    - `versions/v4/conf/data/preference_correctness.yaml`

### B. Wrong default Stage A replay source path

- Symptom:
  - Stage C mix config initially pointed to a nonexistent v4-local copy of `stage_a_strong_v3.parquet`.
- Fix:
  - code defaults and scaffold config were corrected to use:
    - `versions/v3/data/train_packs/stage_a_strong_v3.parquet`
  - config file updated:
    - `versions/v4/conf/data/stage_c_rft_mix.yaml`

### C. Helper name mismatch during real execution

- Symptom:
  - `build-rft-candidates` / `build-stage-c-mix` surfaced copied-name mismatches (`read_table`, `sample_with_weight`) during real execution hardening.
- Fix:
  - corrected to the actual in-file helpers:
    - `_read_table`
    - `_sample_with_weight`

### D. RFT family metadata dropped during accept-pool building

- Symptom:
  - generated probe rows contained `family_x` / `family_y`, while the accept-pool filter expected `family`, causing accepted rows to lose family metadata.
- Fix:
  - v4 code now coalesces merged metadata fields (`family`, `cv5_fold`, `difficulty_tags`) during RFT generation and filtering.
  - accept pool was regenerated after the fix.

### E. Serious-gate evaluator was too slow for iterative work

- Symptom:
  - the first `v4_format_specialist_run1` serious-gate rescoring attempt was still on `shadow_256` after roughly `5.5` hours.
- Root cause:
  - the shared MLX evaluator (`versions/v1/code/train.py`, reused by v4) launched `mlx_lm.generate` as a fresh subprocess for every prompt.
  - that meant model / adapter load overhead was paid repeatedly and `official_lb.max_num_seqs` was effectively unused.
- Action taken:
  - the slow rescoring chain was intentionally stopped.
  - the shared MLX backend was rewritten to keep model+adapter loaded in-process and use `mlx_lm.batch_generate` for deterministic (`temperature=0.0`) scoring.
  - `EvalConfig.max_num_seqs` is now passed through to the MLX backend.
- Validation:
  - targeted evaluator and v4 tests passed
  - real batched MLX smoke test (`2` prompts) passed against the local Nemotron model + specialist adapter

## Evaluator acceleration work

- Changed file:
  - `versions/v1/code/train.py`
- New behavior:
  - persistent in-process MLX load instead of subprocess-per-prompt
  - batched greedy evaluation path for official-style serious scoring
  - in-process sequential sampled fallback to preserve stochastic semantics
- New runtime controls:
  - `MLX_EVAL_PROMPT_CHUNK_SIZE`
  - `MLX_EVAL_PREFILL_BATCH_SIZE`
  - `MLX_EVAL_COMPLETION_BATCH_SIZE`
- Current rerun settings:
  - `prompt_chunk_size = 64`
  - `prefill_batch_size = 64`
  - `completion_batch_size = 64`
- Additional observability:
  - the shared MLX backend now logs chunk-level progress including seed, chunk index, prompt range, elapsed seconds, prompt TPS, generation TPS, and peak memory.
- Relevant validation:
  - `uv run pytest -q versions/v1/tests/test_evaluator_core.py versions/v1/tests/test_eval_determinism.py versions/v4/tests`
    - Result: `13 passed`
  - `uv run python -m py_compile versions/v1/code/train.py versions/v4/code/train.py`
    - Result: passed

## Current Assessment

- v4 is no longer just a plan; the Stage C pipeline is implemented and partially running.
- Format-preference data is plentiful.
- Correctness-preference data exists but is relatively small.
- Current Stage A baseline on the serious gate is weak (`0.4375` / `0.4375`) and clearly does **not** justify submission.
- The current best Stage C rerun already beats the baseline on the serious gate (`0.5234375` / `0.5703125`), so the project is no longer blocked on pure correctness.
- The current bottleneck is format behavior and overlong generation, not extraction.
- Strict RFT mining is much weaker than hoped on the Stage A parent.
- The current active experiments are low-update and answer-biased Stage C sweeps intended to preserve the new accuracy gain while reducing `boxed_multiple` / `last_number_fallback` failures.
- The next meaningful question is no longer whether Stage C can beat the baseline at all; it already can.
- The next meaningful question is which follow-up path best preserves the `run6` formatting gains while recovering `hard_shadow_256` robustness:
  - resume the paused `v5_format_sft_anchor_run1` quick gate, or
  - design the next numeric-safe loss-weighting / data-mix variant

## Active Training Snapshot

### format specialist / DPO-style run1

- Command:
  - `uv run python versions/v4/code/train.py train-specialist --config-path versions/v4/conf/train/specialist_format_mlx.yaml --pair-data-path versions/v4/data/train_packs/stage_c_preference_mix_v4.parquet --output-dir versions/v4/outputs/train/format_specialist_run1 --candidate-id v4_format_specialist_run1 --parent-candidate-id v3_stage_a_baseline --execute`
- Status:
  - running
- Observed early metrics:
  - `iters = 2335`
  - first validation after warm start: `val_loss ≈ 0.693`
  - peak memory seen so far: `~61.35 GB`
  - train loss rapidly collapsed near zero after early iterations
- Caution:
  - this may indicate the preference objective is very easy for the current sampled mix, so the real signal will come from the later serious-gate rescoring, not the training loss itself.

### format specialist / DPO-style run1 (final)

- Status:
  - completed
- Manifest:
  - `versions/v4/outputs/train/format_specialist_run1/v4_format_specialist_run1_manifest.json`
- Result:
  - `train_records = 2335`
  - `valid_records = 123`
  - `iters = 2335`
  - `final_train_loss ≈ 8.40e-11`
  - `final_val_loss ≈ 2.55e-07`
  - `peak_memory_gb ≈ 61.35`
- Interpretation:
  - the specialist preference run fit the sampled objective extremely hard.
  - whether that is useful or just overfitting will only be known after serious-gate rescoring.

### stage-c RFT run1

- Status:
  - completed
- Manifest:
  - `versions/v4/outputs/train/rft_stage_c_run1/v4_rft_stage_c_run1_manifest.json`
- Final scale:
  - `train_records = 3758`
  - `valid_records = 198`
  - `iters = 5637`
  - `num_epochs = 1.5`
- Final metrics:
  - `final_train_loss ≈ 1.091`
  - `final_val_loss ≈ 1.433`
  - `peak_memory_gb ≈ 36.40`
- Training behavior:
  - initial `val_loss ≈ 2.397`
  - early / mid train losses fluctuated widely (`~0.25` to `>10`), which is more realistic than the format-specialist run
- Interpretation:
  - the continuation run completed cleanly and looks less degenerate than the format-only specialist.
  - usefulness is still unknown until the serious-gate rescoring finishes.

### post-training rescoring / merge chain

- Status:
  - completed with accelerated MLX backend
  - used **8-way MLX shard parallelism** while keeping the README official evaluation parameters unchanged
- Previous attempt:
  - stopped intentionally because the old evaluator path was too slow for practical iteration
- Final runner:
  - `versions/v4/outputs/reports/v4_stagec_runner_sharded.log`
- Current sharded setup:
  - `MLX_EVAL_NUM_SHARDS=8`
  - `MLX_EVAL_PROMPT_CHUNK_SIZE=64`
  - `MLX_EVAL_PREFILL_BATCH_SIZE=64`
  - `MLX_EVAL_COMPLETION_BATCH_SIZE=64`
  - `shadow_256` is split into `8` shards of `32` prompts each
- Observability hardening for future reruns:
  - shard workers now start with `PYTHONUNBUFFERED=1`
  - `run-eval` writes an immediate start line
  - long `mlx_lm.batch_generate(...)` calls emit a periodic heartbeat via `MLX_EVAL_HEARTBEAT_SEC` (default `60s`)
- Runtime note:
  - worker RSS summed to roughly `207 GB`
  - user-observed machine RAM reached about `339.5 / 512 GB`
  - to avoid OOM risk, shard count is intentionally held at `8` for this run
  - `sample` on a live shard worker showed it inside `mlx::core::async_eval(...)` / GPU evaluation frames, so the run appears compute-bound rather than hung
  - sampled worker peak physical footprint was about `40.2 GB`
  - roughly `47` minutes after launch, `shadow_256` still had no merged `summary.csv`, but all `8` shard workers remained alive and actively consuming CPU / memory
  - this particular run started before the later `PYTHONUNBUFFERED + heartbeat` observability patch, so missing per-worker progress lines are expected for this run
- Pending outputs:
  - none; all three serious-gate runs completed
- Final serious-gate results:
  - `v4_format_specialist_run1`
    - `shadow_256 = 0.0`
    - `hard_shadow_256 = 0.00390625`
    - `format_fail_rate = 0.96875 / 0.90625`
    - `boxed_rate = 0.0 / 0.015625`
  - `v4_rft_stage_c_run1`
    - `shadow_256 = 0.0`
    - `hard_shadow_256 = 0.0`
    - `format_fail_rate = 1.0 / 1.0`
    - `extraction_fail_rate = 0.0078125 / 0.01953125`
  - `v4_merge_rft_format_run1`
    - `shadow_256 = 0.00390625`
    - `hard_shadow_256 = 0.015625`
    - `format_fail_rate = 1.0 / 1.0`
    - `extraction_fail_rate = 0.0234375 / 0.0234375`
    - despite these weak local scores, `submit_value` in the local scoreboard was auto-set `True` because the merge adapter improved over the two individual Stage C candidates; this is still far below the baseline and **not** a CUDA handoff / submission candidate
- Cleanup note:
  - after the canonical sharded chain finished, a redundant standalone `v4_format_specialist_run1` scorer was found still running and was stopped explicitly to free memory

## Next Recorded Steps

- Analyze why all Stage C variants collapsed on serious gate despite completing training cleanly
- Focus on the dominant failure mode: near-total format failure / almost-zero boxed answers under official long-context evaluation
- Do **not** render/package CUDA reproduction artifacts for v4, because no candidate beat the weak baseline meaningfully
