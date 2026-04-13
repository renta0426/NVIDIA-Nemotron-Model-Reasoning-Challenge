# v3f_submission_line_v1

- script: `versions/v3f_submission_line_v1/reproduce_v3f_submission_line.py`
- purpose: README 契約準拠の single-file wrapper として、`v3f` の監査済み知見を submission-compatible な stage-freeze line へ移す

## Verified source anchors

| metric | score | source |
| --- | ---: | --- |
| stored Phase0 local320 | `249/320 = 0.7781` | `baseline/nemotron-sft-lora-with-cot-v2/result/v3f/phase0_offline_eval/artifacts/phase0_eval_summary.json` |
| corrected local320 | `240/320 = 0.7500` | `cuda-train-data-analysis-v1/proof_first_solver_factory_routing/result/LEADERBOARD_GAP_INVESTIGATION_2026-04-09.md` |
| actual proxy rerun | `133/200 = 0.6650` | `baseline/nemotron-sft-lora-with-cot-v2/result/v3f/leaderboard_proxy_eval/artifacts/leaderboard_proxy_eval_summary.json` |
| specialized563 | `238/563 = 0.4227` | `baseline/nemotron-sft-lora-with-cot-v2/result/v3f/phase0_offline_eval_binary_bias_specialized/artifacts/binary_bias_specialized_eval_summary.json` |
| supported_not_structured | `1/55 = 0.0182` | `baseline/nemotron-sft-lora-with-cot-v2/result/v3f/phase0_offline_eval_binary_bias_specialized/artifacts/binary_bias_specialized_eval_summary.json` |
| binary_structured_byte_not_formula | `1/25 = 0.0400` | `baseline/nemotron-sft-lora-with-cot-v2/result/v3f/phase0_offline_eval_binary_bias_specialized/artifacts/binary_bias_specialized_eval_summary.json` |

## Wrapped pipeline

1. Stage1 broad trunk: `stage-union-exportsafe` + `broad-exportsafe`, `lr=1e-4`, `epochs=2.0`, `len=4096`
2. Stage2 corrective: `stage-union-exportsafe` + `attention`, `lr=2e-5`, `epochs=0.75`, `len=1536`, `max_answer_only_ratio=0.05`
3. Linked Stage2 option: `launch-stage2-linked` wraps `wait-train-from-run`, so Stage2 can be armed before Stage1 finishes
4. Full pipeline option: `run-full-pipeline` builds artifacts, launches Stage1, arms linked Stage2, and starts postprocess in one command
5. Postprocess: `readme_local320` + `leaderboard_proxy_v2` + `binary_bias_specialized_set`
6. Both Stage1 and Stage2 LoRA groups are now CLI-overridable, so shell-recovered experiments can compare `attention` vs `stage-union-exportsafe` without editing code
7. `write-stage2-matrix` now emits JSON/Markdown launch recipes for multiple corrective profiles, including one shared `launch-stage1` command plus per-profile `launch-stage2-linked`, `postprocess-stage2`, and `export-stage2-submission` commands
8. `export-stage2-submission` now exports a Stage2 run root directly to a README-compatible `submission.zip` by deriving `adapter/`, `shadow_model/`, and `submission_export/` paths from the run root
9. `launch-stage2-matrix` now launches the shared Stage1 once and then arms multiple Stage2 linked/postprocess lanes from one wrapper command, matching the parallel experiment workflow expected by the README-driven operating model
10. `package-stage2-matrix-best-submission` now promotes the best README-compatible `submission.zip` from selected Stage2 profiles by calling the monolith `package-best-submission` with wrapper-derived candidate run roots
11. Stage2 matrix profiles now also own per-profile `build-stage2-artifacts` commands and distinct artifact paths, so the wrapper can compare data-mix settings as well as LoRA hyperparameters
12. The matrix now includes `attention-short-noanswer`, an exact-route-first comparison lane with `max_answer_only_ratio=0.0`
13. The monolith corrective builder now supports a bounded `manual_audit_priority` helper slice (`--max-manual-audit-ratio`) scoped to `bit_other`, and the matrix includes `attention-short-manual` (`max_manual_audit_ratio=0.10`) to compare that portable prompt-router-v6 signal directly
14. `launch-stage2-matrix` and `package-stage2-matrix-best-submission` now default to the curated trio `attention-short-default`, `attention-short-noanswer`, and `attention-short-manual`; exploratory lanes remain opt-in
15. Both matrix commands now also support `--all-profiles` for the opposite explicit choice: launch/package the full Stage2 inventory without manually enumerating every exploratory lane
16. `write-stage2-matrix` and the main wrapper summary now expose both wide-sweep commands (`launch-stage2-matrix --all-profiles` and `package-stage2-matrix-best-submission --all-profiles`) so the full inventory path is Git-visible as well
17. Regression coverage now also locks the guardrail that `--profile` and `--all-profiles` are mutually exclusive across the Stage2 profile-selection surfaces, including matrix launch/package and candidate audit
18. `write-stage2-candidate-audit` now writes a static JSON/Markdown gate audit for selected Stage2 profiles by reusing the monolith submission-candidate logic, so README submission readiness can be inspected before packaging
19. The Stage2 candidate gate defaults used by `write-stage2-candidate-audit`, `postprocess-stage2`, `run-full-pipeline`, and `package-stage2-matrix-best-submission` are now single-sourced and exposed in wrapper summaries/matrix payloads to avoid drift
20. The candidate-audit artifact check now resolves `submission.zip` relative to the chosen `--export-relpath` sibling directory, so custom export roots do not silently fall back to the default path
21. Candidate audit now also tracks per-profile Stage2 artifact readiness (`stage2_dataset_csv`, summary JSON, proxy_v2 CSV, proxy summary) so it can distinguish “run root missing” from “build-stage2-artifacts still needed”
22. Candidate audit now emits a `recommended_next_step` per profile (`build-stage2-artifacts`, `launch-stage1`, `launch-stage2-linked`, `postprocess-stage2`, `export-stage2-submission`, or package/review), making the current execution frontier Git-visible
23. Candidate audit now inspects `submission.zip` itself: ZIP integrity, required files, `adapter_config.json` parseability, `base_model_name_or_path`, and LoRA rank against the README `max_lora_rank=32` contract
24. Candidate audit now also treats `submission_export/export_manifest.json` as a real contract gate: `validation.valid`, `converted_tensor_count > 0`, and `base_model_name_or_path` must all align before a profile is package-eligible
25. Candidate audit now also enforces core PEFT/LoRA compatibility fields inside `adapter_config.json` (`peft_type=LORA`, `task_type=CAUSAL_LM`, `inference_mode=true`, non-empty `target_modules`) and checks that `export_manifest.json target_modules` matches the packaged adapter config
26. Stage2 artifact readiness is no longer existence-only: candidate audit now requires non-empty Stage2/proxy CSVs plus valid summary JSONs with positive `rows` and matching `output_csv`, otherwise the profile stays on `build-stage2-artifacts`
27. Candidate audit now also surfaces `recorded_run_result.json readme_eval_assumptions` drift against the README evaluation table (plus `eval_enable_thinking=true`) as a Git-visible diagnostic without blocking packaging by itself
28. Candidate audit now also treats `submission_compat_audit.json` as a real gate: `peft_export_ready`, `unsupported_tensor_count`, base model, PEFT preview rank/target modules/inference mode, README required files/max rank, and preview-vs-package consistency must all line up before a profile is package-ready
29. Candidate audit now also treats `prepare_manifest.json` and `training_result.json` as real run-metadata gates: the prepare manifest must carry the expected Nemotron base model, non-empty `train_csv`, `training.lora_rank <= 32`, non-empty `training.lora_keys` / `training.trainable_lora_suffixes`, and a README-matching `readme_contract`, while the training result must report positive `adapter_config.json` / `adapters.safetensors` sizes plus positive `latest_train_report.iteration` / `optimizer_step`
30. Invalid or stale run metadata now pushes `recommended_next_step` back to `launch-stage2-linked` instead of letting malformed Stage2-linked runs drift forward to postprocess/export/package stages; regression coverage now includes both validator helpers and the candidate-audit wiring even though runtime pytest remains PTY-blocked
31. Candidate audit now also treats `export_manifest.json zip_path` / `zip_size_bytes` as a real consistency gate: the manifest must point to the chosen `--export-relpath` sibling `submission.zip`, and its recorded ZIP size must match the actual packaged archive before the profile is export/package-ready
32. Candidate audit now also ties Stage2 run metadata back to the selected profile artifact lineage: `prepare_manifest.json train_csv` must match that profile's `stage2_dataset_csv`, so a run cannot be compared or packaged under the wrong matrix profile when the Stage2 dataset pointer has drifted
33. Candidate audit now also enforces `submission_compat_audit.json readme_submission_contract.single_adapter_submission_zip = true`, mirroring the README requirement that the final artifact is a single packaged `submission.zip` LoRA adapter
34. The new single-adapter audit field is also populated on the missing/invalid `submission_compat_audit.json` early-return paths, preventing markdown rendering from raising `KeyError` when candidate audit inspects broken audit artifacts
35. `submission.zip` inspection now also rejects unsafe member paths, extra `.safetensors` payloads beyond `adapter_model.safetensors`, duplicate nested `adapter_config.json` entries, and exact duplicate required entries so the packaged archive itself respects the README single-adapter contract instead of only relying on `submission_compat_audit.json`
36. Wrapper-generated summaries now also stamp `summary_schema_version = 2` and `readme_contract_state`, so regenerated JSON/Markdown can self-report whether they fully match the current README evaluation table

## CLI testability

- both `reproduce_v3f_exportable_audit.py` and `reproduce_v3f_submission_line.py` now accept `parse_args(argv)`
- this makes the new `write-summary` / `run-full-pipeline` command lines regression-testable inside the existing Python test bundle
- the test bundle now also covers:
  - `--max-manual-audit-ratio` threading for the monolith and wrapper CLI surfaces
  - `attention-short-manual` as a default Stage2 matrix lane
  - the `bit_other`-only scope for the manual helper slice
  - curated default Stage2 matrix selection instead of launching every exploratory lane implicitly
  - explicit `--all-profiles` parsing for the full-inventory matrix path
  - `write-stage2-candidate-audit` output and its gate-state summary for loaded vs missing-artifact profiles
  - `prepare_manifest.json` / `training_result.json` validator helpers and the `launch-stage2-linked` fallback when those run-metadata artifacts are stale or malformed
  - `export_manifest.json zip_path` / `zip_size_bytes` consistency against the actual sibling `submission.zip`
  - selected-profile `prepare_manifest.json train_csv` lineage checks, including repo-relative path normalization
  - `submission_compat_audit.json readme_submission_contract.single_adapter_submission_zip` enforcement
  - `submission.zip` payload-shape hardening: reject extra `.safetensors`, duplicate `adapter_config.json` / required entries, and unsafe ZIP member paths
- current limitation:
  - actual pytest execution is still blocked in this environment by `posix_openpt failed: Device not configured` before pytest starts
  - `list_bash` shows only completed detached shell sessions (no running/idle session lines), and sampled `stop_bash` attempts cannot clean them because they were launched with `detach: true`; the current PTY blocker therefore does not reduce to “a live interactive shell is still holding the TTY”

## Stage2 targeting

- proxy_v2 focus buckets:
  - `dominant_structured_safe`
  - `dominant_structured_abstract`
  - `supported_not_structured`
  - `supported_affine_xor`
  - `supported_bijection`
- binary solver defaults:
  - `binary_affine_xor`
  - `binary_bit_permutation_bijection`
  - `binary_structured_byte_formula`
  - `binary_structured_byte_formula_abstract`
  - `binary_structured_byte_not_formula`

## 0.9 lineage guardrails

- README-compatible submission path remains single-adapter only, but the clearest in-repo `>0.9` accuracy blueprint is still `prompt-router-v6` at `293/320 = 0.9156` and `54/60` binary
- that lineage is **not** directly portable as a submission because it is a multi-adapter + solver local pipeline
- the wrapper summary now fixes the portable transfer priors explicitly:
  - primary binary failure mode: `format_ok_content_wrong`
  - primary lane: exact-route verified rows
  - answer-only lane stays helper-only at low ratio
  - `bit_other + answer_only_keep` overlap rows (`52`) are already present in the current phase2 train CSV, so the more portable new signal is `bit_other manual_audit_priority` + `verified_trace_ready`
  - the default lane still stays behavior-safe, but the matrix now has a dedicated small `bit_other` manual helper comparison instead of forcing that signal into every Stage2 build
  - corrective repair should explicitly include `binary_structured_byte_formula_abstract` drift cleanup as well as `binary_structured_byte_not_formula`

## README contract

- final artifact must stay a single `submission.zip` LoRA adapter
- rank cap: `32`
- eval params: `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, `gpu_memory_utilization=0.85`, `max_model_len=8192`
- `postprocess-stage2`, `run-full-pipeline`, and generated matrix `postprocess-stage2` commands now carry the README/metric eval contract including `gpu_memory_utilization=0.85`
- `postprocess-stage2` and `run-full-pipeline` also pass `--eval-enable-thinking`, matching the metric notebook path used in this repo
- wrapper-generated summaries now also stamp `summary_schema_version = 2`, `readme_contract_state`, and `readme_contract_verified_from_readme_file = true`, so regenerated JSON/Markdown can self-report live README revalidation
- the wrapper now also re-reads the authoritative `README.md` evaluation rows directly and fails explicitly if a required row is missing, empty, or malformed instead of surfacing a later mismatch against `None`

## Current implication

- `v3f` is strong enough to be the single-adapter blueprint, but the historical MLX bundle itself is not a ready submission artifact
- this wrapper exists to rebuild the line from the verified dataset/eval contract instead of trying to promote the non-compatible historical bundle directly
- nearby caution: completed attention-only neighbor `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr2e5_ep24_len768_rerun_v3` was still weak at `218/320`, `33/84` proxy_v2, `158/563` specialized, so this wrapper should be treated as an execution scaffold, not as a proven winning recipe yet
- default corrective length is now intentionally short (`epochs=0.75`) and keeps the answer-only helper lane at `5%`, matching `baseline/single_lora_stage_freeze_unfreeze/plan.md`
- wrapper summaries now also carry the prompt-router-v6 blueprint and single-adapter transfer priors directly, so shell recovery later does not depend on re-reading older ledgers to remember what should and should not be ported
- matrix recipes now also encode the strongest code-only comparison that follows from that transfer audit: the default `5%` helper lane versus a strict no-answer-only corrective lane
- the wrapper now also has a static pre-package checkpoint (`write-stage2-candidate-audit`) so the first post-recovery README packaging pass can inspect gate failures in Git before promoting a `submission.zip`
- current repo state still has no `stagefreeze_v3` v3f Stage1 or Stage2 run roots under `baseline_mlx/outputs/`, so the new candidate audit is expected to report missing-artifact state until the first real launch occurs
- current repo state also has no `stagefreeze_v3` profile artifact CSV/summary outputs under `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v3_artifacts/`, so the audit will currently flag `build-stage2-artifacts` as still needed for every profile
- even after export artifacts appear, the audit is now README-strict about both `export_manifest.json` and the packaged `submission.zip` itself instead of trusting only `export_manifest.validation.valid`
- candidate selection now treats either `export_manifest.json base_model_name_or_path` drift or `adapter_config.json base_model_name_or_path` drift as an export-stage blocker
- candidate selection also treats `validation.valid = false` or `converted_tensor_count <= 0` in `export_manifest.json` as an export-stage blocker, so a merely-present manifest no longer looks package-ready
- candidate selection now also treats missing / unparsable `export_manifest.json` and missing `submission.zip` as explicit gate failures instead of letting those cases surface only through `recommended_next_step`
- candidate selection now also rejects `submission.zip` when `adapter_model.safetensors` is empty, so a zero-byte packaged adapter cannot appear eligible
- candidate selection now also rejects non-LoRA / non-causal / non-inference PEFT configs and manifest-vs-zip `target_modules` drift, mirroring the monolith export contract instead of trusting packaging artifacts blindly
- candidate selection now also refuses to treat Stage2 corrective/proxy artifacts as ready when the CSV is empty or the summary JSON points at the wrong output / non-positive row count
- candidate audit now also exposes local-eval-vs-README parameter drift from `recorded_run_result.json` so current proxies do not get mistaken for full README-parity evals
- candidate selection now also refuses stale or malformed `submission_compat_audit.json`; when its PEFT preview drifts from the packaged adapter, the profile is pushed back to `postprocess-stage2` instead of leaking through to packaging
- candidate selection now also refuses stale or malformed `prepare_manifest.json` / `training_result.json`; if Stage2-linked run metadata is missing key README/export facts, the profile is pushed back to `launch-stage2-linked` before postprocess/export/package can proceed
- candidate selection now also refuses stale `export_manifest.json` records that point at a different ZIP or record the wrong ZIP size; the chosen export root's sibling `submission.zip` is now the only valid package surface
- candidate selection now also refuses Stage2 runs whose `prepare_manifest.json train_csv` points at a different profile's dataset artifact, preventing cross-profile stale lineage from leaking into matrix comparison and package selection
- candidate selection now also refuses `submission_compat_audit.json` summaries that no longer claim a single packaged submission ZIP, keeping the audit summary aligned with the README submission shape
- candidate selection now also refuses packaged `submission.zip` archives that carry multiple adapter payloads, duplicate required entries, or unsafe member paths, so a stale/manual archive cannot look single-adapter-ready just because the audit summary says so
- targeted reruns through task agents still fail at the environment layer with `posix_openpt failed: Device not configured`; both `uv run python -m pytest ...` and a direct `python -c ...` import probe from task agents hit the same blocker, so actual `pytest`, `verify`, and even plain Python imports remain blocked even though the wrapper surface has been expanded
- tool-side shell inspection now also shows `497` completed detached sessions and no running/idle shells, which lowers the odds that this blocker is caused by a still-live interactive agent shell waiting to be reaped
- Darwin PTY guidance for `posix_openpt` / `openpty` `Device not configured` points to a host-level PTY/devfs issue whose usual recovery is reboot or manual device-node repair, neither of which is reachable from the current no-shell toolset
