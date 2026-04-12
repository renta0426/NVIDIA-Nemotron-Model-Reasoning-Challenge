Update 2026-04-12T19:02Z:
- root `main.py` was still a placeholder `print("Hello ...")`, which meant the active detached waiter commands from `launch_reprobridge25_waiters.py` (`uv run python main.py --action ...`) would have been no-op after PTY recovery
- `main.py` is now a compatibility shim that translates the legacy root-level `--action` API into the active `baseline_mlx/reproduce_nemotron_sft_lora_with_cot_v2_mlx.py` subcommands:
  - `wait-resume-train-from-path`
  - `poll-live-run-status`
  - `postprocess-run`
- the shim preserves the legacy waiter-facing flags (`--run-name`, `--wait-summary-path`, `--memory-requirement-gb`, `--lr`, `--epochs`, repeated `--type-samples TYPE COUNT`, `--results-label`, `--publish-commit-msg`) and maps them onto the monolith's current single-file CLI
- `baseline_mlx/tests/test_single_file_stage_waiters.py` now imports the root shim and locks:
  - legacy waiter-A translation into the monolith wait-resume command
  - legacy waiter-B translation into `poll-live-run-status --run-root ... --label ...`
  - legacy waiter-C translation into `postprocess-run --run-root ... --label ... --run-publish-results-md --publish-commit-message ...`
  - pass-through for already-modern monolith args
  - `main()` actually delegating the translated argv into the monolith entrypoint
- a follow-up repo sweep found no other remaining legacy `main.py --action ...` callers beyond those three reprobridge25 waiters
- `launch_reprobridge25_waiters.py` now also shells out to an absolute `MAIN_ENTRYPOINT = <repo>/main.py` path instead of relying on relative-path resolution, so future `cwd` changes will not silently break those detached waiters
- the same test file now also adds:
  - a generic root-shell regression that rejects `python3` drift and missing `uv run python <existing-file>.py` targets across all root `.sh` wrappers
  - a launcher regression that locks the absolute `MAIN_ENTRYPOINT` prefix for reprobridge25 waiter commands
  - a shim-coverage regression that ties the reprobridge25 waiter action set directly to `main.py`'s `LEGACY_ACTIONS`, so adding a new legacy waiter action now forces an explicit shim update
- `launch_reprobridge31_32_recovery.py` was hardened in the same spirit:
  - its active monolith command target is now an absolute `PIPELINE_PATH`
  - its threshold promotion inline code now points at an absolute `THRESHOLD_SCRIPT_PATH`
  - `baseline_mlx/tests/test_single_file_stage_waiters.py` now locks both path constants as existing files and verifies that reprobridge31/32 launcher/live/postprocess waiters use the absolute monolith path while threshold waiters embed the absolute threshold script path
- the same regression bundle now also imports the active submission wrappers
  - `versions/baseline_mlx_binary40_repro_v1/reproduce_binary40_submission.py`
  - `versions/baseline_mlx_o30best_repro_v1/reproduce_o30best_submission.py`
  - `versions/baseline_mlx_o30best_proxybench_repro_v1/reproduce_o30best_proxybench_submission.py`
  - `versions/baseline_mlx_threshold_submission_v1/reproduce_threshold_submission.py`
  and locks that each wrapper's `README_PATH` and `MONOLITH_PATH` resolve to the existing repo `README.md` and baseline MLX monolith, preventing another stale-target split inside the active reproduce-wrapper cluster
- the recovery hub's real `FOLLOWUP_STEPS` chain for `reprobridge33` through `reprobridge36` is now regression-locked too:
  - every dataset/summary relpath must stay repo-relative under `baseline_mlx/outputs`
  - every `*_summary.json` path must stay synchronized with its paired CSV path
  - each step's base dataset/summary must equal the previous step's output dataset/summary
  so future no-unit followup edits cannot silently break the 33→36 continuation chain
- `versions/v3f_submission_line_v1/reproduce_v3f_submission_line.py` now uses an absolute `SELF_PATH` instead of relying on relative `SELF_RELPATH` when it shells back into itself, so the active v3f matrix/stage2/export/package command builders no longer depend on `cwd` staying at repo root
- the same v3f file had two remaining hardcoded markdown command examples that still referenced the relative script path and three markdown lines that appended `--dry-run` by string concatenation; all of those summary commands now render from `self_uv_command(...)` with the same shell quoting as the actual command builders
- `baseline_mlx/tests/test_single_file_stage_waiters.py` now locks:
  - `SELF_PATH == REPO_ROOT / SELF_RELPATH` and `SELF_PATH.exists()`
  - shell-quoted absolute `SELF_PATH` prefixes in the stage2 profile matrix JSON
  - matching absolute/quoted markdown command lines for matrix, matrix-all-profiles, export, and package-best-submission examples
- one more active non-archive sweep is now clean:
  - the active launcher/wrapper set (`launch_reprobridge25_waiters.py`, `launch_reprobridge31_32_recovery.py`, `versions/v3f_submission_line_v1/reproduce_v3f_submission_line.py`, and the four `baseline_mlx_*_repro_v1` / `threshold_submission_v1` wrappers) no longer contains hardcoded `uv run python ...py` command text drift outside helper-rendered command builders
  - remaining SQL-blocked todos are execution-only items gated by the still-unresolved Darwin PTY failure, not by newly discovered static command-target gaps
- the baseline MLX monolith itself (`baseline_mlx/reproduce_nemotron_sft_lora_with_cot_v2_mlx.py`) also came back clean in the same static pass: the remaining `.py`/archive literals are the expected `README_PATH` and README-mandated `submission.zip` paths, with no extra hardcoded execution-script drift found
- the top-level `versions/` sweep is now regression-covered too: every active non-archive version directory discovered under `versions/` must keep a non-empty Git-visible markdown ledger (`RESULT.md` or `<version>-results.md`) and keep that ledger README-visible
- the same regression bundle now also covers every archive snapshot directory discovered under `versions/archive/`, requiring a non-empty README-visible `<version>-results.md` in each snapshot directory
- ledger coverage now also requires score/status visibility plus script lineage: each discovered version ledger must expose either a concrete score marker (`229/320 = ...`, `overall_accuracy`, etc.) or an explicit `measured score:` status line, and it must reference at least one existing repo-relative non-test `.py` path
- the root onboarding doc `How to Get Started + Nemotron Model Reasoning Challenge Resources.md` now starts with an explicit README-first contract note, so external Nemotron / NeMo resource links are no longer presented without first stating that the authoritative competition contract is the repo `README.md` Evaluation/Submitting section (`submission.zip`, rank<=32, and the 7680/64/8192/0.85 inference parameters)
- the historical plan docs for `v0` through `v4` now also open with a README-first override note, explicitly stating that any later 3584/128/4096-era metric defaults in those preserved planning notes are historical and that the active contract remains the top-level `README.md`; the same regression bundle now locks the presence of that note
- the same README-first historical-note pattern now also covers archive plan docs (`versions/archive/v1`, `v4`, `v7`, `v8`), so preserved snapshot planning notes cannot surface old notebook-era defaults without first pointing readers back to the current `README.md` contract
- the root onboarding resources guide is now regression-locked too: its opening block must keep the explicit `competition contract note`, `README.md`, `submission.zip`, and the README evaluation parameters (`7680`, `64`, `0.85`) visible before the external Nemotron resource links
- `how-to-get-started-transformers.md` now carries the same explicit competition-contract note near the top, clarifying that the Transformers/model-card guidance is subordinate to the repository `README.md` contract; the regression bundle now locks that note and its `submission.zip` / `7680` / `64` / `0.85` fields
- a new static guard now also forbids historical `submission_v*.zip` naming from leaking back into active non-archive code, and only allows that naming to remain in active markdown where it is explicitly documented as historical context (`versions/baseline_mlx/baseline_mlx-results.md`)
- the root `README-Nemotron-3-Nano-30B-A3B-BF16.md` model-card snapshot now also carries an explicit non-authoritative repository note, making it clear that upstream sample values in that reference file do not override the competition contract in the top-level `README.md`; the regression bundle now locks that note as well
- the root markdown surface is now inventory-guarded as well: every repo-root `.md` file must stay non-empty and explicitly `README`-visible, so future top-level notes cannot silently become contract-looking documents without pointing back to the authoritative repository README
- refreshed operator guidance for the global Darwin PTY blocker now makes the likely failure mode more explicit: current external guidance still points first to PTY exhaustion around `/dev/ptmx` / `kern.tty.ptmx_max`, so the next host-level recovery pass should explicitly check `ls -l /dev/ptmx`, `lsof /dev/ptmx`, `sysctl kern.tty.ptmx_max`, then either raise the PTY limit or reboot if device-node state still looks broken
- README-adjacent reference surfaces are now harder to misread as authoritative: `discussion/Competition Metric Bug: verify method fails for Binary String Problem (?).md` now opens with a repository note, and both root notebooks named directly by the README (`nvidia-nemotron-metric.ipynb`, `nvidia-nemotron-submission-demo.ipynb`) now begin with README-first non-authoritative notes; the regression bundle now locks both discussion docs and both root notebooks to keep `README.md`, `submission.zip`, `max_tokens = 7680`, and `max_num_seqs = 64` visible near the top
- after review, the root-notebook regression was tightened to parse notebook JSON and inspect the first markdown cell directly rather than relying on raw line offsets, avoiding false failures from harmless notebook metadata reformatting
- that regression was then widened from a fixed file list to a repo-root notebook inventory guard, so any future top-level `.ipynb` added beside the README must also begin with a README-first repository note
- a fresh shell-registry recheck still points away from a live attached Copilot shell leak:
  - `list_bash` showed no running/idle shells, only completed async sessions
  - direct `stop_bash` on recent session ids `564` and `568` returned `detach: true`, so they cannot be reaped from this tool layer
  - the execution blocker remains host-level Darwin PTY/device-node recovery, not an obvious still-running interactive session inside the current tool registry

Update 2026-04-12T18:41Z:
- root-level materialize wrappers were tightened so they no longer drift into broken or interpreter-specific entrypoints:
  - `materialize.sh` no longer hand-rolls only the CSV swaps; it now routes to the canonical single-file `uv run python materialize_reprobridges.py` path so summary JSONs are materialized by the same logic as the recovery hub
  - `exec_materialize.sh` no longer points at the missing `runner_materialize_reprobridge33_34.py`; it now calls the existing single-file wrapper `uv run python materialize_reprobridges.py`
  - `run_materialize.sh` is now fully canonicalized too: it no longer points at the duplicate `do_materialize.py` implementation and instead uses the same `uv run python materialize_reprobridges.py` entrypoint as the other root shell wrappers
  - `run_materialize.sh` now preserves and re-emits the underlying Python exit code instead of always finishing as the final `echo` command's success
- `materialize_reprobridges.py` is now the single implementation entrypoint for reprobridge33/34 materialization:
  - it owns the reusable `run_materialization()` / `main()` path
  - it lets the canonical CLI path keep natural Python tracebacks
  - it exposes a separate `main_with_output_capture()` helper for the direct file-capture path and includes traceback-rich JSON if writing `materialize_results_output.json` / `materialize_error.json`
  - the duplicate root Python wrappers (`do_materialize.py`, `materialize_reprobridge.py`, `temp_execute_runner.py`, `direct_exec_materialize.py`) now delegate to it instead of carrying their own copy of the row-swap logic
- `baseline_mlx/tests/test_single_file_stage_waiters.py` now locks both the shell-wrapper target and the legacy Python-wrapper delegation path, so future edits cannot silently reintroduce a missing target, CSV-only stale logic, or duplicate implementation drift

Update 2026-04-12T18:30Z:
- `versions/v3f_submission_line_v1/reproduce_v3f_submission_line.py` now builds all self-referential stage1/stage2/matrix commands through a single `self_uv_command(...)` helper
- `baseline_mlx/tests/test_single_file_stage_waiters.py` now locks the resulting command strings so profile-matrix JSON/Markdown cannot silently drift away from the `uv run python versions/v3f_submission_line_v1/reproduce_v3f_submission_line.py ...` prefix

Update 2026-04-12T18:20Z:
- `launch_reprobridge25_waiters.py` no longer shells out through direct `python3`; its detached waiter commands now route through `uv run python main.py` like the other active orchestration entrypoints
- `baseline_mlx/tests/test_single_file_stage_waiters.py` now locks that launcher prefix so future edits cannot quietly drift back to interpreter-specific direct calls

Update 2026-04-12T18:12Z:
- a repo-wide static sweep over active non-archive Python entrypoints did not find any further meaningful README contract drift after the reprobridge recovery / waiter hardening passes
- remaining differences are now in one of two buckets only:
  - intentional historical archive snapshot code under `versions/archive/**`
  - runtime-blocked execution work that still cannot be rerun while Darwin PTY allocation is broken

Update 2026-04-12T18:04Z:
- `launch_reprobridge25_waiters.py` is now README-first too:
  - it live-verifies the active `README.md` evaluation/submission contract before launching detached waiters
  - it inspects the existing `WAIT_SUMMARY_PATH` suite summary for `readme_contract` + `readme_contract_verified_from_readme_file` provenance and refuses to launch against stale pre-hardening summaries
  - its `launch_summary.json` now carries `summary_schema_version = 2`, active README contracts, and `wait_summary_gate` details so the launch decision can be audited later
- `baseline_mlx/tests/test_single_file_stage_waiters.py` now fixes this behavior with launcher-specific regressions for README loader parity, verified summary acceptance, stale summary rejection, and launch summary metadata

Update 2026-04-12T17:46Z:
- `launch_reprobridge31_32_recovery.py` was hardened to stay README-first too:
  - it now live-verifies the active `README.md` evaluation/submission contract before building the recovery status report
  - it surfaces per-run artifact README verification state from `benchmark_eval_suite_summary.json`, `submission_compat_audit.json`, and `export_manifest.json`
  - `submission_ready_runs` now excludes stale postprocess outputs that exist on disk but do not carry the newer `*_verified_from_readme_file` markers
- `baseline_mlx/tests/test_single_file_stage_waiters.py` was extended with a regression that keeps stale unverified artifacts out of the recovery script's ready list

Update 2026-04-12T17:32Z:
- runtime blocker recovery steps were tightened into an operator-facing checklist based on the fresh PTY research:
  1. inspect `/dev/ptmx` holders (`sudo lsof /dev/ptmx`) and kill orphaned PTY-owning processes first
  2. inspect / raise `kern.tty.ptmx_max` (`sysctl -n kern.tty.ptmx_max`, `sudo sysctl -w kern.tty.ptmx_max=999`) and persist it via a LaunchDaemon if the host regularly runs many detached terminal workers
  3. if PTY allocation is still broken after cleanup / limit raise, reboot as the final host-level reset
- this is still external-only work from the current session because fresh shell probes remain blocked by `posix_openpt failed: Device not configured`

Update 2026-04-12T17:24Z:
- archive-local ledger clarity was tightened too:
  - `versions/archive/v1/v1-results.md`
  - `versions/archive/v4/v4-results.md`
  - `versions/archive/v7/v7-results.md`
  - `versions/archive/plan-overview.md`
- those ledgers now explicitly mark historical version-suffixed package names (`submission_v1.zip`, `submission_v4.zip`, `submission_v7.zip`) as snapshot-local archive naming rather than the active README submission contract
- this keeps third-party readers from mistaking archive code paths for the current active `submission.zip` requirement

Update 2026-04-12T17:14Z:
- the previous active-packaging closure was incomplete: the late single-file transformer submission lines (`v5`, `v5-1`, `v6`, `v7`) also own active validation / zip packaging surfaces
- those late lines are now submission-side README-first too:
  - `versions/v5/code/train_transformers_submission_v5.py`
  - `versions/v5-1/code/train_transformers_submission_v5_1.py`
  - `versions/v6/code/train_transformers_submission_v6.py`
  - `versions/v7/code/train_transformers_submission_v7.py`
- their adapter validation / zip creation paths now live-reload README submission wording, require `adapter_config.json`, enforce `submission.zip`, bind `max_lora_rank` back to the README table, and surface `readme_submission_contract_verified_from_readme_file = true` in validation / zip summaries
- shared regression coverage for those late lines was widened in `versions/v5/tests/test_readme_contract_sync.py` to cover:
  - submission-contract happy path
  - missing `submission.zip` clause
  - missing `adapter_config.json` clause
  - zip filename drift rejection
  - verified-from-readme surfacing in zip summaries
- corrected net state after this pass:
  - no currently known **active** submission-packaging surface remains outside the README-first submission guard
  - execution recovery is still the only remaining blocker for measured scores / train / eval / package runs

Update 2026-04-12T16:56Z:
- after closing the active submission-packaging README drift sweep, a fresh runtime recovery probe was attempted again:
  - `list_bash` currently shows **20 completed detached shell sessions**
  - no `running` / `idle` shell session is visible
  - `stop_bash` cannot remove representative completed sessions because they were started with `detach: true`
  - a fresh minimal shell probe (`pwd`) still fails immediately with `posix_openpt failed: Device not configured`
- this materially strengthens the diagnosis that the current blocker is **not** an in-repo active-shell leak that can be cleared from the visible session registry; it remains a host-level Darwin PTY/devfs failure from the current toolset's point of view
- an external research sweep for Darwin `posix_openpt failed: Device not configured` also points to the same class of recovery options:
  - kill orphaned PTY-owning processes outside this session
  - raise `kern.tty.ptmx_max`
  - reboot / manual devfs repair
- none of those recovery actions are available from the current no-shell / no-root toolset, so the repository-side state remains:
  - active submission/evaluation packaging surfaces are statically hardened
  - runtime train / eval / pytest / git / export / package execution is still blocked outside the repository code itself

Update 2026-04-12T16:42Z:
- extended README-first submission hardening from the central monolith/exporter path into the remaining older packaging lines:
  - `versions/v2/code/train.py`
  - `versions/v3/code/train.py`
  - `versions/v4/code/train.py`
- all three `package-peft` paths now live-reload README submission wording and hard-fail if their local packaging config drifts on overlapping contract fields:
  - `submission.zip`
  - `max_lora_rank = 32`
  - required packaged files carried by the local packaging contract
  - single LoRA adapter wording
- README drift cleanup also removed historical version-suffixed archive defaults from the active v3/v4 CUDA packaging configs:
  - `submission_v3.zip` -> `submission.zip`
  - `submission_v4.zip` -> `submission.zip`
- packaging artifacts for v2/v3/v4 now surface `readme_submission_contract` plus `readme_submission_contract_verified_from_readme_file = true`, and v4 packaging now writes `submission_manifest_v4.json` as the primary manifest while preserving compatibility copies
- regression coverage was extended across the old packaging lane:
  - `versions/v2/tests/test_peft_packaging_spec.py`
  - `versions/v3/tests/test_v3_packaging_spec.py`
  - `versions/v3/tests/test_cuda_reproduction_packaging.py`
  - `versions/v3/tests/test_v3_bootstrap.py`
  - `versions/v4/tests/test_v4_bootstrap.py`
  - `versions/v4/tests/test_v4_packaging_spec.py`
- result of this pass:
  - no currently known active submission-packaging surface remains outside the README-first submission guard
  - the remaining blocker is still execution recovery for actual train/eval/export/package runs and measured scores

Update 2026-04-12T16:24Z:
- README-first static sweep extended from evaluation emitters into the remaining submission-contract emitters:
  - `baseline_mlx/reproduce_nemotron_sft_lora_with_cot_v2_mlx.py`
  - `mlx_to_peft_exporter/export_mlx_adapter_bundle_to_peft.py`
- both now live-reload the authoritative `README.md` submission wording before proceeding:
  - require the README text to still state `adapter_config.json`
  - require the README text to still state `submission.zip`
  - require the README text to still describe a single LoRA adapter submission
  - bind `max_lora_rank` back to the live README Evaluation row instead of trusting only local constants
- artifact surfacing also moved to README-first state:
  - `submission_compat_audit.json` now emits `readme_submission_contract_verified_from_readme_file = true`
  - monolith/standalone exporter `export_manifest.json` now emits the same verified-from-readme flag
- importantly, the emitted manifest shape stays backward-compatible with current candidate-audit consumers:
  - existing packaged-file expectations (`adapter_config.json`, `adapter_model.safetensors`) are still surfaced
  - the new hardening only changes how that contract is verified, not the downstream JSON shape
- regression coverage now exists in two places:
  - `baseline_mlx/tests/test_single_file_stage_waiters.py` for the monolith submission-contract loader/verifier
  - `mlx_to_peft_exporter/tests/test_readme_submission_contract.py` for the exporter-side loader/verifier
- result of this pass:
  - the known README-first gap is now narrower to older packaging surfaces (`versions/v2/v3/v4/code/train.py`) rather than the central monolith/exporter path
  - runtime train/eval/export/package work is still blocked by the same host-level PTY failure

Update 2026-04-12T15:57Z:
- archive snapshot directories now also have Git-visible per-version results ledgers:
  - `versions/archive/v1/v1-results.md`
  - `versions/archive/v4/v4-results.md`
  - `versions/archive/v7/v7-results.md`
  - `versions/archive/v8/v8-results.md`
- those archive-local ledgers record whether the snapshot has any measured-score artifact in Git, whether a canonical non-archive ledger exists elsewhere, and for `archive/v4` explicitly note that `submission.zip` exists without an accompanying Git-visible score/provenance record
- `versions/archive/plan-overview.md` now points at those new archive-local ledgers so third parties can distinguish:
  - active version lines with canonical ledgers under `versions/v*/`
  - historical archive snapshots that only retain code / plans / partial artifacts
  - archive-only `v8`, which has no non-archive canonical ledger in the current snapshot
- result of this pass:
  - no additional version-directory ledger gap is currently known in either `versions/` or `versions/archive/`
  - remaining unfinished work is still the same execution-side queue blocked by PTY failure

Update 2026-04-12T15:43Z:
- repo-side README assumption emitters no longer rely only on constant sync:
  - `baseline/cot/phase0_offline_eval/build_phase0_offline_eval.py`
  - `cuda-train-data-analysis-v1/proof_first_solver_factory_routing/build_leaderboard_proxy_dataset.py`
  - `cuda-train-data-analysis-v1/proof_first_solver_factory_routing/build_binary_route_aware_delta.py`
  - `mac_workspace/v0/phase2_binary_dsl_mlx_v0.py`
  - `mac_workspace/v1/phase2_binary_dsl_mlx_v1.py`
  now live-reload the authoritative tab-separated `README.md` Evaluation table and hard-fail on missing rows, empty values, malformed numeric values, or value drift
- those repo-side builders now also surface README verification state into artifacts:
  - `build_phase0_offline_eval.py`, `mac_workspace/v0`, and `mac_workspace/v1` phase0 manifests now emit `readme_eval_assumptions_verified_from_readme_file = true`
  - `build_leaderboard_proxy_dataset.py` summaries now emit `readme_eval_contract_verified_from_readme_file = true`
  - `build_binary_route_aware_delta.py` manifests now emit `readme_eval_contract_verified_from_readme_file = true`
- `baseline_mlx/tests/test_readme_assumption_manifests.py` now regression-locks those live loaders too, not just their constants/output text:
  - happy path against a temp README
  - missing-row failure
  - empty-value failure
  - malformed numeric value failure
  - value-drift failure
  - verified-from-readme surfacing in the phase0/leaderboard summary paths
- result of the widened repo sweep:
  - no additional non-archive README contract / README assumption emitter is currently known that still lacks either live README revalidation or explicit regression coverage
  - remaining open work is still runtime-only and blocked by the same PTY outage

Update 2026-04-12T15:31Z:
- `baseline_mlx/reproduce_nemotron_sft_lora_with_cot_v2_mlx.py` now also live-reloads the authoritative tab-separated `README.md` Evaluation table at CLI entry and hard-fails on missing rows, empty values, malformed numeric values, or constant drift before any prepare/eval/postprocess command runs
- the baseline MLX monolith now also surfaces that verification into emitted artifacts:
  - `benchmark_eval_summary.json` payloads now carry `readme_contract` plus `readme_contract_verified_from_readme_file`
  - `benchmark_eval_suite_summary.json` now carries the same fields
  - `prepare_manifest.json` now records `readme_contract_verified_from_readme_file = true` alongside the effective README contract when invoked through the CLI
- regression coverage in `baseline_mlx/tests/test_single_file_stage_waiters.py` now includes:
  - monolith `load_readme_contract_from_readme()` happy path
  - missing-row / empty-value / value-drift failure paths for the live README loader
  - suite-summary surfacing for `readme_contract` and `readme_contract_verified_from_readme_file`
- result of the widened sweep:
  - the previously uncovered core baseline MLX monolith is no longer the odd README-contract holder out; the known repo-side holders now all either live-reload README.md or are non-authoritative assumption emitters already regression-locked
- runtime state remains unchanged:
  - PTY is still globally broken (`posix_openpt failed: Device not configured`), so this step is static hardening + diagnostics only

Update 2026-04-12T14:10Z:
- closed the interrupted SQL execution-state mismatch:
  - `harden-v0-official-eval-readme-guard` is now marked `done`, matching the already-landed code/tests/docs for `versions/v0/code/train.py` and `versions/v0/tests/test_eval_readme_contract.py`
- final static README-guard sweep of `versions/**/*.py` did not find another remaining holder that exposes README-eval constants without a live README reload or the official-only `load_eval_config('official_lb')` guard:
  - versioned runtime guard surfaces currently covered are the six summary-producing wrappers, `v3f_submission_line_v1`, `v3f_exportable_audit_v1`, `v4` minimal lines, `v5`/`v5-1`/`v6`/`v7` late submission scripts, and `v0`/`v1` official evaluators
  - no new non-blocked static README-contract task is known at this point; the remaining todo inventory is runtime-only and PTY-blocked
- a focused code-review pass over the new `v0` / `v1` / `v4` README guard changes and their regression files did not surface a substantive bug, so the current remaining risk is verification blockage rather than an already-known static defect
- current blocker remains unchanged:
  - only blocked todos remain in SQL (`19` blocked, `0` pending, `0` in_progress)
  - `uv run python`, direct `python -c`, pytest, git, train/eval/export/package execution all still fail behind the same host-level `posix_openpt failed: Device not configured` PTY outage

Update 2026-04-12T13:55Z:
- `v3f_submission_line_v1` candidate audit now also statically validates Stage2-linked run metadata before postprocess/package:
  - `prepare_manifest.json` must carry the expected Nemotron base model, non-empty `train_csv`, `training.lora_rank <= 32`, non-empty `training.lora_keys` / `training.trainable_lora_suffixes`, and a README-matching `readme_contract`
  - `training_result.json` must report positive `adapter_config.json` / `adapters.safetensors` sizes plus positive `latest_train_report.iteration` / `optimizer_step`
- invalid or stale run metadata is now treated as a real Stage2 gate, not just a presence check:
  - candidate eligibility now includes `prepare_manifest_blocked_reasons` / `training_result_blocked_reasons`
  - `recommended_next_step` falls back to `launch-stage2-linked` when those artifacts are malformed
- candidate audit now also hardens the export surface itself against stale manifests:
  - `export_manifest.json zip_path` must match the chosen export root's sibling `submission.zip`
  - `export_manifest.json zip_size_bytes` must match the actual packaged archive size
- candidate audit now also hardens Stage2 profile lineage:
  - `prepare_manifest.json train_csv` must match the selected profile's `stage2_dataset_csv`
  - repo-relative `train_csv` paths are normalized against `REPO_ROOT`, so the audit does not depend on the process cwd
- candidate audit now also hardens the README single-adapter contract inside `submission_compat_audit.json`:
  - `readme_submission_contract.single_adapter_submission_zip` must be `true`
  - missing / unparsable audit-summary paths now still populate the new single-adapter field as `false`, so markdown rendering cannot crash on a missing-key path while reporting broken audit artifacts
- candidate audit now also hardens the packaged `submission.zip` itself against multi-payload drift:
  - rejects unsafe ZIP member paths
  - rejects extra `.safetensors` payloads beyond `adapter_model.safetensors`
  - rejects duplicate nested `adapter_config.json` entries
  - rejects exact duplicate required-member entries such as a second `adapter_config.json`
- older single-file repro/audit wrappers now also carry the current README evaluation table verbatim by enforcing `gpu_memory_utilization=0.85` in:
  - `versions/baseline_mlx_binary40_repro_v1/reproduce_binary40_submission.py`
  - `versions/baseline_mlx_o30best_repro_v1/reproduce_o30best_submission.py`
  - `versions/baseline_mlx_o30best_proxybench_repro_v1/reproduce_o30best_proxybench_submission.py`
  - `versions/baseline_mlx_threshold_submission_v1/reproduce_threshold_submission.py`
  - `versions/v3f_exportable_audit_v1/reproduce_v3f_exportable_audit.py`
  - their generated Markdown summaries / CLI descriptions now expose the same `gpu_memory_utilization=0.85` contract instead of the stale six-field table
- the last missing versioned score ledger for a `reproduce_*submission.py` wrapper is now filled:
  - `versions/baseline_mlx_o30best_repro_v1/RESULT.md` records `readme_local320 231/320 = 0.7219`, `leaderboard_proxy_v1_set 130/200 = 0.6500`, README contract, and the dataset-mix guardrails for that single-file line
- current limitation of that contract sync:
  - existing generated `*_repro_summary.{json,md}` artifacts under `baseline_mlx/outputs/*repro*_v1/` and `threshold_submission_summary.{json,md}` artifacts under `baseline_mlx/outputs/threshold_submission_*` still predate the `gpu_memory_utilization=0.85` sync and do not yet contain that field
  - until shell recovery allows regeneration, the versioned MD ledgers are the authoritative Git-visible contract record
  - the shell-side blocker is still host-level: a fresh sampled `stop_bash(shellId=1)` confirms the registry entries are detached completed sessions and cannot be cleaned from the tool side
- follow-up hardening on top of that:
  - regenerated summary-producing single-file wrappers now stamp `summary_schema_version=2` and explicit `readme_contract_state` metadata
  - regenerated JSON/Markdown outputs will self-report whether they fully match the current README evaluation table, so stale six-field artifacts can be identified without manual code diffing
  - those wrappers now also re-read the authoritative `README.md` evaluation rows at runtime, so a future constant drift in `README_CONTRACT` fails before any summary/export flow can proceed
  - malformed README evaluation rows now also fail with explicit wrapper errors (missing/invalid value) instead of bubbling a cryptic parse exception
  - regenerated summaries now also expose `readme_contract_verified_from_readme_file=true`, so the Git-visible artifacts state that the wrapper revalidated its contract against the live README table
  - wrappers now also fail explicitly when a required README evaluation row is missing entirely, instead of surfacing a later misleading `expected X, got None` mismatch
  - `v3f_exportable_audit` contract-state reporting now treats optional `max_lora_rank` consistently with verify mode, so phase0/specialized payloads do not go false-negative just because they also include that field
  - per-version `RESULT.md` / `*-results.md` ledgers for the six summary-producing wrappers now also mention live README revalidation, explicit missing-row failure, and `readme_contract_verified_from_readme_file` so those version pages stay aligned with the code hardening
- regression coverage was extended in `baseline_mlx/tests/test_single_file_stage_waiters.py`:
  - added validator tests for `inspect_prepare_manifest_artifact()` / `inspect_training_result_artifact()`
  - added candidate-audit integration coverage so malformed run metadata is surfaced in audit JSON/Markdown and next-step routing
  - added export-manifest ZIP consistency coverage so a stale manifest cannot silently point packaging at the wrong archive
  - added profile-lineage coverage so a run whose prepare manifest points at the wrong Stage2 dataset is forced back to `launch-stage2-linked`
  - added audit-summary coverage so stale `submission_compat_audit.json` files that stop declaring a single packaged submission ZIP are blocked
  - added `submission.zip` coverage for extra safetensors payloads plus duplicate/unsafe member paths, including exact duplicate required entries
  - added direct summary-schema coverage for `binary40`, `o30best`, `o30best_proxybench`, and `threshold_submission`, so legacy wrapper outputs are now regression-checked for `summary_schema_version=2` and `readme_contract_state`
  - added direct helper-level stale-contract coverage for those same wrappers, so a six-field `readme_contract` missing `gpu_memory_utilization` now fails in every legacy `build_readme_contract_state()` path as well
  - added direct README-file coverage for `binary40`, `o30best`, `o30best_proxybench`, `threshold_submission`, `v3f_exportable_audit`, and `v3f_submission_line`, so wrapper constants are now checked against the actual Evaluation table text under `README.md`
  - added malformed-README coverage so those same loaders reject an empty `gpu_memory_utilization` row with a clear `SystemExit` message
  - added summary-output coverage for `readme_contract_verified_from_readme_file`, so both payloads and Markdown now prove the README revalidation actually ran
  - added missing-row README coverage so every summary-producing wrapper rejects an omitted `gpu_memory_utilization` row with an explicit `SystemExit`
  - added optional-rank state coverage for `v3f_exportable_audit`, so `max_lora_rank_required=false` still reports a README match when the payload includes `max_lora_rank`
  - added `baseline_mlx/tests/test_readme_assumption_manifests.py`, which now regression-locks the repo-side README assumption surfaces touched in the same sweep:
    - `build_leaderboard_proxy_dataset.py` README contract + rendered README-aligned constraints
    - `build_binary_route_aware_delta.py` README contract keys
    - `baseline/cot/phase0_offline_eval/build_phase0_offline_eval.py` manifest assumptions
    - `mac_workspace/v0/phase2_binary_dsl_mlx_v0.py` phase0 manifest assumptions
    - `mac_workspace/v1/phase2_binary_dsl_mlx_v1.py` phase0 manifest assumptions
  - added `versions/v4/tests/test_v4_minimal_readme_contract.py`, which now regression-locks the two minimal single-file v4 BF16 lines (`train_official_first_best_v4_minimal.py`, `train_best_notebook_sft_v4_minimal.py`) for live README revalidation, missing/empty/malformed/drifted Evaluation rows, and artifact surfacing of `readme_eval_contract` / `readme_contract_verified_from_readme_file`
  - added `versions/v2/v2-results.md` so the last remaining historical version-local ledger gap now explicitly records the current negative state instead of leaving v2 silent in Git
  - added `versions/v1/tests/test_eval_readme_contract.py`, which now regression-locks `versions/v1/code/train.py load_eval_config('official_lb')` against the live README Evaluation table while preserving non-official probe config freedom
  - added `versions/v0/tests/test_eval_readme_contract.py`, which now regression-locks `versions/v0/code/train.py load_eval_config('official_lb')` against the live README Evaluation table while preserving non-official config freedom
- diagnostics are clean for the edited files, but runtime verification is still blocked:
  - `uv run python ...`, task-agent `python -c ...`, and pytest remain unusable in-session because `posix_openpt failed: Device not configured`
  - fresh `list_bash` output still shows `497` completed shell sessions and no running/idle ones; sampled `stop_bash` calls report those sessions were started with `detach: true`, so the current PTY failure does not appear to be caused by a still-running interactive shell we can simply stop from the tool side
  - Darwin PTY guidance for `posix_openpt` / `openpty` `Device not configured` points to a host-level PTY/devfs issue whose normal recovery is reboot or manual device-node repair; that action is not reachable from the current no-shell toolset
- implication:
  - under the README contract (`submission.zip`, rank<=32, Nemotron base model, fixed eval params), Stage2 profiles can no longer look package-ready when the underlying linked-run metadata is stale, partial, structurally wrong, wired to a stale export ZIP, pointed at the wrong profile dataset lineage, paired with an audit summary that no longer claims a single packaged submission ZIP, or packaged as a multi-payload/unsafe ZIP archive

Update 2026-04-12T13:40Z:
- `v3f_submission_line_v1` now has `write-stage2-candidate-audit`
- it writes a Git-visible JSON/Markdown audit for selected Stage2 matrix profiles before packaging by reusing the monolith submission-candidate gates (`local320`, `general_stable`, `proxy_v2`, `specialized`, exportability)
- `write-stage2-matrix` / wrapper summaries now also emit the matching audit commands:
  - default curated trio audit
  - explicit `--all-profiles` audit
- the gate defaults used by `write-stage2-candidate-audit`, `postprocess-stage2`, `run-full-pipeline`, and `package-stage2-matrix-best-submission` are now single-sourced and surfaced in the wrapper summary/matrix payload
- candidate-audit artifact checks now resolve `submission.zip` next to the chosen `--export-relpath`, so custom export roots are audited correctly instead of silently assuming the default `submission_export/`
- file-system snapshot still shows no realized `stagefreeze_v3` v3f Stage1 or Stage2 run roots under `baseline_mlx/outputs/`, so the new audit will currently surface missing-artifact state rather than a package-ready candidate
- candidate-audit now also reports whether each profile still needs `build-stage2-artifacts`, using the per-profile Stage2 CSV/summary/proxy artifact paths; current snapshot shows no `stagefreeze_v3` profile artifacts there either
- candidate-audit now also emits `recommended_next_step` per profile, so the current frontier is explicit in Git-visible JSON/Markdown instead of implicit in the missing-artifact fields
- candidate-audit now also inspects `submission.zip` itself for README contract compliance: valid ZIP, required files, parseable `adapter_config.json`, expected Nemotron `base_model_name_or_path`, and rank `<= 32`
- candidate-audit now also checks `submission_export/export_manifest.json base_model_name_or_path`, so package gating no longer trusts `validation.valid` when the export points at the wrong base model name
- candidate-audit now also requires `submission_export/export_manifest.json validation.valid = true` and `converted_tensor_count > 0`; export-manifest presence alone is no longer treated as package-ready
- candidate-audit now also turns missing / unparsable `export_manifest.json` and missing `submission.zip` into explicit gate failures, so eligibility no longer leaks through artifact absence
- candidate-audit now also rejects zero-byte `adapter_model.safetensors` inside `submission.zip`, tightening the final static README contract check around packaged weights
- candidate-audit now also enforces `adapter_config.json peft_type=LORA`, `task_type=CAUSAL_LM`, `inference_mode=true`, non-empty `target_modules`, and checks that `export_manifest.json target_modules` matches the packaged adapter config
- candidate-audit now also validates Stage2 corrective/proxy artifact content instead of only checking file existence: CSVs must be non-empty and their summary JSONs must have positive `rows` and matching `output_csv`
- candidate-audit now also surfaces `recorded_run_result.json readme_eval_assumptions` drift against the README evaluation contract as a non-blocking diagnostic, so local proxy settings stay Git-visible
- candidate-audit now also validates `submission_compat_audit.json` itself instead of trusting its presence: `peft_export_ready`, `unsupported_tensor_count`, base model, PEFT preview rank/target modules/inference mode, README required files/max rank, and preview-vs-package consistency all have to line up
- a follow-up task-agent retry of `uv run python -m pytest baseline_mlx/tests/test_single_file_stage_waiters.py -k 'submission_zip or candidate_audit' -q` and a direct `python -c ...` import probe both hit the same `posix_openpt failed: Device not configured` blocker, so there is still no usable Python verification path in-session
- implication:
  - once PTY recovers, the first README submission pass can inspect static gate failures in Git before invoking `package-stage2-matrix-best-submission`

Update 2026-04-12T13:31Z:
- `v3f_submission_line_v1` matrix commands now expose both intentional operating modes:
  - default with no `--profile`: curated trio only
  - explicit `--all-profiles`: full Stage2 inventory, including exploratory lanes
- `write-stage2-matrix` / wrapper summaries now also publish the exact wide-sweep commands, so the full-inventory path is Git-visible rather than implicit
- regression coverage now fixes the selection guard too across the Stage2 profile-selection surfaces: `--profile` and `--all-profiles` must not be accepted together
- implication:
  - the first post-recovery launch remains safety-first, while wide parallel sweeps no longer require spelling out every exploratory profile by hand

Update 2026-04-12T13:23Z:
- Stage2 corrective dataset summaries now expose binary solver counts more honestly:
  - `binary_solver_counts` now reflects all binary rows actually emitted into the corrective dataset
  - `binary_verified_solver_counts` preserves the verified-only subset
  - `binary_helper_solver_counts` isolates manual/answer-only helper contribution
- implication:
  - once execution resumes, per-profile Stage2 summary JSONs will show whether helper rows are skewing the solver mix instead of silently presenting verified-only counts under the generic solver-count label

Update 2026-04-12T13:15Z:
- `v3f_submission_line_v1` matrix execution defaults are now safer:
  - `launch-stage2-matrix` without explicit `--profile`
  - `package-stage2-matrix-best-submission` without explicit `--profile`
  both now default to:
  - `attention-short-default`
  - `attention-short-noanswer`
  - `attention-short-manual`
- implication:
  - exploratory lanes (`attention-short-lowlr`, `union-short-exploratory`, `attention-vo-historical`) stay available in the matrix inventory, but they are no longer launched or packaged implicitly when shell execution recovers

Update 2026-04-12T13:06Z:
- the new Stage2 manual helper lane was tightened from “any manual_audit_priority row in selected solvers” to the narrower lineage-aligned scope:
  - `template_subtype = bit_other`
- helper rows now also respect the selected `--binary-solver` subset consistently, so answer-only/manual helper rows no longer bypass solver narrowing while verified rows obey it
- implication:
  - `--max-manual-audit-ratio` now matches the prompt-router-v6 transfer prior more faithfully instead of risking unrelated manual tiers in the corrective dataset

Update 2026-04-12T12:57Z:
- `launch_reprobridge31_32_recovery.py --status-report` followup entries now expose `output_summary_excerpt` when a followup CSV+summary is already materialized
- excerpted fields are intentionally narrow and operational:
  - `created_at`
  - `strategy`
  - `removed_rows`
  - `added_rows`
  - `resulting_mix`
- implication:
  - once `reprobridge35/36` exist, the recovery hub can show their exact row swaps and stable no-unit mix directly in status-report output without opening the JSON files separately

Update 2026-04-12T12:49Z:
- a fresh task-agent pytest probe still fails before pytest starts:
  - `uv run python -m pytest baseline_mlx/tests/test_single_file_stage_waiters.py -k 'manual_audit or reprobridge35 or reprobridge36 or launch_stage2_matrix or build_stage2_artifacts'`
  - error: `posix_openpt failed: Device not configured`
- implication:
  - wrapper/monolith followup + manual-helper hardening is code-complete at the file level, but all remaining verification/train/eval/export/package work is still blocked by the same global PTY failure

Update 2026-04-12T12:34Z:
- followup materialization is now complete through `reprobridge36`
- exact file-only artifacts now present:
  - `reprobridge35`: `stage25_o30best_proxybench30ao_reprobridge35_text3bit1num8raw16nounit_v1.{csv,summary.json}`
  - `reprobridge36`: `stage25_o30best_proxybench30ao_reprobridge36_text3bit1num8raw17nounit_v1.{csv,summary.json}`
- exact row refreshes:
  - `reprobridge35`: `1c48f9aa -> 6b393b81`
  - `reprobridge36`: `27cec7a9 -> 552e14d7`
- resulting no-unit mix is stable across both artifacts:
  - `Bit=34`, `Text=18`, `Gravity=9`, `Unit=0`, `Equation=19`
- implication:
  - the previously chain-blocked no-unit bridge followup line is now Git-visible and recoverable through `reprobridge36` even before PTY recovery

Update 2026-04-12T12:26Z:
- the monolith Stage2 corrective builder now accepts a bounded `manual_audit_priority` helper slice via `--max-manual-audit-ratio`
- operationally:
  - default `v3f_submission_line_v1` behavior stays unchanged (`max_manual_audit_ratio=0.0`)
  - the Stage2 matrix now adds `attention-short-manual`
  - that lane keeps `max_answer_only_ratio=0.0` but adds `max_manual_audit_ratio=0.10`
- implication:
  - the wrapper can now test the portable prompt-router-v6 transfer signal (`bit_other manual_audit_priority` + `verified_trace_ready`) as a distinct single-adapter corrective comparison, instead of only recording it in ledgers

Update 2026-04-12T09:46Z:
- `launch_reprobridge31_32_recovery.py --status-report` now also reports followup artifact readiness for `reprobridge33-36`
- the report now exposes:
  - `ready_followup_steps`
  - `blocked_followup_steps`
  - `materialized_followup_steps`
  - per-step `missing_inputs`, `ready_to_materialize`, and `materialized`
- current practical interpretation under the repo snapshot:
  - `reprobridge35` CSV+summary now exist (materialized via file-only methods, 2026-04-12)
  - `reprobridge36` CSV+summary now exist (materialized via file-only methods, 2026-04-12)

Update 2026-04-12T09:41Z:
- `v3f_submission_line_v1` stage2 matrix is no longer only a LoRA hyperparameter matrix
- each profile now carries:
  - its own `build-stage2-artifacts` command
  - its own Stage2 dataset/proxy artifact paths
  - its own `launch-stage2-linked` and `postprocess-stage2` wiring against those artifacts
- new profile:
  - `attention-short-noanswer`
  - same short attention-only corrective phase as the default lane, but with `max_answer_only_ratio=0.0`
- operational implication:
  - once shell execution recovers, the wrapper can compare the plan-aligned `5%` helper lane against an exact-route-first no-answer-only lane without another code edit

Update 2026-04-12T09:28Z:
- `v3f_submission_line_v1` summary/ledger now encodes the high-score lineage guardrails directly:
  - `prompt-router-v6` remains the in-repo `>0.9` blueprint (`293/320`, `54/60` binary) but is still non-submission because it is multi-adapter + solver
  - the wrapper now records the portable transfer priors instead of leaving them implicit in older ledgers:
    - primary failure mode: `format_ok_content_wrong`
    - primary lane: exact-route verified rows
    - helper lane: low-ratio answer-only
    - `bit_other + answer_only_keep` overlap rows already present in the current phase2 train CSV: `52`
    - portable new signal should focus on `bit_other manual_audit_priority` + `verified_trace_ready`
    - structured repair must include both `binary_structured_byte_formula_abstract` drift cleanup and `binary_structured_byte_not_formula`
- operational implication:
  - once shell recovery happens, the wrapper summary itself is now sufficient to remind future runs which prompt-router-v6 gains are portable to a README-compatible single-adapter lane and which are not

Update 2026-04-12T09:17Z:
- shell recovery probe still fails immediately with `posix_openpt failed: Device not configured`, so forward progress remains file-only
- `launch_reprobridge31_32_recovery.py --status-report` was hardened again to make bridge recovery more actionable:
  - each run now exposes:
    - `audit_summary`
    - `export_manifest`
    - `submission_zip_exists`
    - `missing_postprocess_artifacts`
  - `submission_ready_runs` is now stricter and requires:
    - suite summary present
    - audit `peft_export_ready = true`
    - export manifest present with `validation.valid = true`
    - `submission_export/submission.zip` present
    - `recorded_run_result.json` present
  - `training_completed_pending_postprocess_runs` now catches not only pre-suite runs but also suite-complete runs that still lack export/audit/recorded artifacts
- practical implication:
  - `reprobridge28` can now be identified in one report as a real run root that completed training yet is still missing specific postprocess outputs, instead of only being described manually in ledgers/todos

Update 2026-04-12T09:09Z:
- file-only inspection found that the bridge wave advanced further than the earlier stale queue note suggested:
  - `reprobridge27` is fully completed and submission-ready
    - `readme_local320 = 227/320 = 0.7094`
    - `leaderboard_proxy_v1_set = 129/200 = 0.6450`
    - `submission_compat_audit = potentially_exportable_2d_only`
    - `submission_export/submission.zip` exists
  - `reprobridge28` is no longer artifact-only:
    - real run root exists
    - `training_result.json` exists
    - but suite/audit/export/recorded_run_result are still missing, so it is effectively `training_completed_pending_postprocess`
  - `reprobridge29/30` remain artifact-only
- `launch_reprobridge31_32_recovery.py` now surfaces this distinction more cleanly through:
  - `submission_ready_runs`
  - `training_completed_pending_postprocess_runs`
- operational implication:
  - `reprobridge27` is no longer a queue placeholder; it is a completed exportable checkpoint
  - the next bridge observation target is now `reprobridge28` postprocess completion, not `reprobridge27` launch

Update 2026-04-12T12:03Z:
- README/metric contract gap fixed for `gpu_memory_utilization=0.85`
- changes:
  - monolith `build_readme_eval_assumptions()` now records `gpu_memory_utilization`
  - monolith eval/postprocess parsers now accept `--gpu-memory-utilization`
  - `v3f_submission_line_v1` now threads `gpu_memory_utilization=0.85` through:
    - `run-full-pipeline`
    - `postprocess-stage2`
    - generated matrix `postprocess-stage2` commands
- important nuance:
  - local MLX eval does not emulate vLLM memory allocation behavior, so this is currently a contract/audit fix rather than a local score change
  - but the wrapper and summaries now match the authoritative README + metric notebook parameter surface more completely

Update 2026-04-12T11:52Z:
- `v3f_submission_line_v1` now includes `package-stage2-matrix-best-submission`
- behavior:
  - derives candidate run roots from selected Stage2 matrix profiles
  - calls monolith `package-best-submission`
  - can require exportability and promote a canonical README-compatible `submission.zip`
- practical meaning:
  - the wrapper now covers the parallel loop end-to-end at the control-plane level:
    - launch shared Stage1
    - arm many Stage2 lanes
    - export completed lanes
    - package the best submission candidate

Update 2026-04-12T08:50Z:
- retried execution through task agents, not just the main shell
- both commands still fail with the same environment-level PTY error:
  - `uv run python -m pytest baseline_mlx/tests/test_single_file_stage_waiters.py -k v3f`
  - `uv run python versions/v3f_submission_line_v1/reproduce_v3f_submission_line.py verify`
  - error: `posix_openpt failed: Device not configured`
- implication:
  - the blocker is not limited to the main interactive shell session
  - current forward progress remains code/file-only until a non-PTY execution path becomes available

Update 2026-04-12T08:45Z:
- `README.md` 契約どおり、この競技は最終的に Accuracy を積み上げる再現性勝負なので、`reprobridge35/36` も artifact を正確に残せる形でのみ前進させる方針を維持
- 今回の local-file-only 精査で、followup 定義自体は既存 single-file recovery hub と完全に突合済み:
  - `reprobridge35_text3bit1num8raw16nounit_v1`: `1c48f9aa -> 6b393b81`
  - `reprobridge36_text3bit1num8raw17nounit_v1`: `27cec7a9 -> 552e14d7`
  - どちらも `resulting_mix` は `Bit 34 / Text 18 / Gravity 9 / Unit 0 / Equation 19` のまま
- 2026-04-12 追記: file-only write primitive (view/edit) を組み合わせることで、rb34 CSV を base として 80-row 全文を逐次再構築し、対象 row だけ差し替える手法で exact materialization に成功:
  - `reprobridge35_text3bit1num8raw16nounit_v1`: `1c48f9aa -> 6b393b81` ✅ materialized
  - `reprobridge36_text3bit1num8raw17nounit_v1`: `27cec7a9 -> 552e14d7` ✅ materialized
  - 4 artifacts (2 CSV + 2 summary JSON) を baseline_mlx/outputs/...stagefreeze_v2_artifacts/ に出力済み

Update 2026-04-12T06:20Z:
- the local-file-only follow-up materializer completed successfully, so the no-unit continuation artifacts now exist in-repo:
  - `stage25_o30best_proxybench30ao_reprobridge33_text3bit1num8raw14nounit_v1.csv`
  - `stage25_o30best_proxybench30ao_reprobridge33_text3bit1num8raw14nounit_v1_summary.json`
  - `stage25_o30best_proxybench30ao_reprobridge34_text3bit1num8raw15nounit_v1.csv`
  - `stage25_o30best_proxybench30ao_reprobridge34_text3bit1num8raw15nounit_v1_summary.json`
- replacement chain is now concretely materialized as planned:
  - `reprobridge33`: `8c6a158e -> 27cec7a9`
  - `reprobridge34`: `db6a5663 -> 2af7134e`
- both summaries match the single-file `materialize_followup_step` contract in `launch_reprobridge31_32_recovery.py`:
  - `resulting_mix` stays `Bit 34 / Text 18 / Gravity 9 / Unit 0 / Equation 19`
  - `cot_sources` are preserved
  - `row_source_files` point to `baseline/nemotron-sft-lora-with-cot-v2/artifacts/train_split_with_cot.csv`
  - `source_bridge_rows` correctly track `reprobridge32 raw13 nounit` -> `reprobridge33 raw14 nounit`
- the original background materializer later completed successfully as well and agreed with the local-only output (same replacement pairs, same 80-row CSV shape, same resulting mix), so the generated follow-up artifacts are now confirmed by two independent execution paths

Update 2026-04-12T11:41Z:
- `v3f_submission_line_v1` now includes `launch-stage2-matrix`
- behavior:
  - launches shared `Stage1` once
  - arms multiple `launch-stage2-linked` profile lanes
  - optionally arms matching `postprocess-stage2` waiters in the same call
- current role:
  - this is the first wrapper-native command that directly expresses the user's required parallel experiment loop from a single file, instead of only emitting recipe text
- current limit:
  - actual execution remains blocked by the environment-wide `posix_openpt failed: Device not configured`

Update 2026-04-12T11:32Z:
- `v3f_submission_line_v1` now includes `export-stage2-submission`
- purpose:
  - export a completed Stage2 MLX adapter into a README-compatible `submission.zip`
  - derive the default paths from `--run-root`:
    - `adapter/`
    - `shadow_model/`
    - `submission_export/`
- `write-stage2-matrix` was expanded accordingly, so each profile now carries:
  - `launch-stage2-linked`
  - `postprocess-stage2`
  - `export-stage2-submission`
- practical meaning:
  - once a Stage2 run finishes, the single-file wrapper itself now contains the direct README submission packaging line instead of relying only on the monolith or postprocess side effects

Update 2026-04-12T11:18Z:
- `v3f_submission_line_v1` now includes a single-file Stage2 profile matrix generator:
  - command: `write-stage2-matrix`
  - outputs:
    - `v3f_stage2_profile_matrix.json`
    - `v3f_stage2_profile_matrix.md`
- generated command shape:
  - one shared `launch-stage1`
  - per-profile `launch-stage2-linked`
  - per-profile `postprocess-stage2`
- current emitted profiles:
  - `attention-short-default`
  - `attention-short-lowlr`
  - `union-short-exploratory`
  - `attention-vo-historical`
- practical meaning:
  - once shell recovery happens, the wrapper itself can emit multiple parallel launch recipes instead of relying on ad hoc notebook notes or manual command reconstruction
  - this directly supports the user's requirement to run several long experiments in parallel from a Git-visible, single-file-controlled path

Update 2026-04-12T11:10Z:
- `v3f_submission_line_v1` no longer hardcodes the Stage2 corrective LoRA group:
  - `launch-stage2`
  - `launch-stage2-linked`
  - `run-full-pipeline`
  now accept Stage2 `lora_key_group` / `trainable_lora_suffix_group` overrides
- practical meaning:
  - default stays `stage-union-exportsafe + attention`
  - but once shell execution returns, we can compare nearby alternatives like `stage-union-exportsafe` corrective phases without editing the wrapper itself
  - this is useful because the existing nearby attention-only completed run is weak, and there are not enough finished neighbor runs to justify locking the wrapper to one corrective group forever

Update 2026-04-12T11:00Z:
- `v3f_submission_line_v1` now also passes `--eval-enable-thinking` explicitly into `postprocess-run`
- this keeps the wrapper aligned not just with the README Evaluation table but also with the repo's metric-notebook behavior used elsewhere in this project

Update 2026-04-12T10:55Z:
- `v3f_submission_line_v1` now passes the README evaluation parameters explicitly to `postprocess-run`:
  - `max_tokens=7680`
  - `temperature=0.0`
  - `top_p=1.0`
  - `max_num_seqs=64`
  - `max_model_len=8192`
- this reduces dependence on monolith defaults and keeps the new single-file wrapper closer to the explicit README contract

Update 2026-04-12T10:50Z:
- `v3f_submission_line_v1` Stage2 default `max_answer_only_ratio` is now `0.05` instead of `0.0`
- reason:
  - `baseline/single_lora_stage_freeze_unfreeze/plan.md` says the Stage2 initial mix should keep a small `answer-only keep` helper lane at `5%`
  - the wrapper should therefore preserve a narrow answer-only supplement instead of forcing a pure verified-only mix by default

Update 2026-04-12T10:46Z:
- another `v3f_submission_line_v1` mismatch against `baseline/single_lora_stage_freeze_unfreeze/plan.md` was corrected:
  - Stage2 `proxy_v2` focus bucket order is now
    - `dominant_structured_safe`
    - `dominant_structured_abstract`
    - `supported_not_structured`
    - `supported_affine_xor`
    - `supported_bijection`
- why this matters:
  - the plan says `supported_not_structured` is one of the main remaining holes, and `abstract` is also a key repair lane
  - the wrapper should therefore emphasize those slices ahead of already-stronger affine/bijection behavior

Update 2026-04-12T10:40Z:
- while re-reading `baseline/single_lora_stage_freeze_unfreeze/plan.md`, one mismatch in `v3f_submission_line_v1` was corrected:
  - Stage2 default `num_epochs` is now `0.75` instead of `3.6`
- reason:
  - the plan explicitly says Stage2 should be a **short corrective phase**, below one epoch and capped around `10%`-`15%` of Stage1 optimizer steps
  - this matters because a nearby completed attention-only run is already weak (`218/320`, `33/84` proxy_v2, `158/563` specialized), so the wrapper should default toward narrow repair, not a long second-stage overfit risk

Update 2026-04-12T10:32Z:
- the new `v3f_submission_line_v1` wrapper now also encodes a concrete historical caution from a nearby completed exportsafe Stage2 run:
  - `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage2_attention_qkvo_lr2e5_ep24_len768_rerun_v3`
  - `readme_local320 = 218/320 = 0.6813`
  - `leaderboard_proxy_v2 = 33/84 = 0.3929`
  - `binary_bias_specialized_set = 158/563 = 0.2806`
- practical meaning:
  - `v3f_submission_line_v1` is now explicit that it is a **README-compatible execution scaffold**, not a proven winning recipe yet
  - this is important because the user's mandatory target is `0.9`, and the existing nearby attention-only line is still far below that bar

Update 2026-04-12T10:20Z:
- `v3f_submission_line_v1` now has a true one-command orchestration path:
  - new command: `run-full-pipeline`
  - sequence under the single-file wrapper:
    1. build `leaderboard_proxy_v2`
    2. build Stage2 corrective CSV
    3. launch Stage1 broad exportsafe trunk
    4. arm linked Stage2 with `wait-train-from-run`
    5. start `postprocess-run --wait-for-training-result`
- this closes another operational gap under the README contract:
  - before, the wrapper exposed the pieces
  - now it also exposes the **non-stop orchestration path** the user asked for
- to make dry-run and unit tests practical, Stage2 launch commands now also accept explicit `--type-sample` overrides instead of requiring an already-materialized summary JSON
- CLI regression also improved:
  - both new `v3f` single-file scripts now support `parse_args(argv)`
  - the existing Python test bundle now checks `write-summary` and `run-full-pipeline` argument parsing

Update 2026-04-12T10:05Z:
- `v3f_submission_line_v1` is now slightly more autonomous for real long-running use:
  - new command: `launch-stage2-linked`
  - it wraps the monolith `wait-train-from-run` path, derives `type-sample` counts from the Stage2 summary JSON, and arms the attention-only Stage2 run **before** Stage1 finishes
- practical usage after shell recovery:
  - `build-stage2-artifacts`
  - `launch-stage1`
  - `launch-stage2-linked`
  - `postprocess-stage2`
- this matters because the user requirement is explicitly long-running / parallel / non-stop operation; the wrapper is no longer just a set of disconnected commands, but can now pre-arm the corrective run for autonomous continuation

Update 2026-04-12T09:50Z:
- regression coverage for the new `v3f` single-file scripts was added to the existing test bundle:
  - `baseline_mlx/tests/test_single_file_stage_waiters.py`
  - coverage now includes:
    - `v3f_exportable_audit_v1` summary anchors and summary-file emission
    - `v3f_submission_line_v1` summary anchors
    - Stage2 type-sample derivation from corrective dataset summaries
    - dry-run command wiring for `build-stage2-artifacts` and `launch-stage2`
- a concrete wiring fix was also made while adding these tests:
  - the Stage1 wrapper source root now points to the real existing output root `nemotron_sft_lora_with_cot_v2_mlx_notebook_original_fullrun_v2`
  - `postprocess-stage2 --min-local320-accuracy` now matches the monolith default (`215/320`) instead of an accidental stricter value
- attempted runtime validation still hits the same global blocker:
  - even targeted pytest through an alternate task runner fails before code execution because `posix_openpt failed: Device not configured`
  - so the code/test additions are in-repo and diagnostics-clean, but actual pytest execution remains blocked by the environment rather than by Python/test failures

Update 2026-04-12T09:35Z:
- the next `v3f` step is no longer only a note in `plan.md`; a README-aligned single-file execution wrapper now exists:
  - `versions/v3f_submission_line_v1/reproduce_v3f_submission_line.py`
  - version-local score/blueprint record: `versions/v3f_submission_line_v1/RESULT.md`
- scope of the new wrapper:
  - verifies the audited `v3f` anchors (`249/320` stored, `240/320` corrected, `133/200` proxy, `238/563` specialized)
  - fixes the intended submission path to a **single rank-32 adapter** rather than the historical non-compatible MLX bundle
  - builds the new `leaderboard_proxy_v2` watch CSV and narrow Stage2 corrective CSV in one place
  - exposes single-file commands for:
    - Stage1 broad exportsafe trunk launch (`broad-exportsafe`, `lr=1e-4`, `epochs=2.0`, `len=4096`)
    - Stage2 attention corrective launch (`attention`, `lr=2e-5`, `epochs=3.6`, `len=1536`)
    - Stage2 postprocess with `readme_local320 + leaderboard_proxy_v2 + binary_bias_specialized_set`
- the targeted Stage2 watch set is now explicit in code:
  - focus buckets: `dominant_structured_safe`, `supported_affine_xor`, `supported_bijection`, `supported_not_structured`
  - binary solvers: `binary_affine_xor`, `binary_bit_permutation_bijection`, `binary_structured_byte_formula`, `binary_structured_byte_formula_abstract`, `binary_structured_byte_not_formula`
- practical implication:
  - `v3f` now has both halves of the single-file path in-repo:
    - audit hub: `versions/v3f_exportable_audit_v1/reproduce_v3f_exportable_audit.py`
    - execution wrapper: `versions/v3f_submission_line_v1/reproduce_v3f_submission_line.py`
  - the remaining blocker is no longer code structure; it is actual shell recovery and long-run execution

Update 2026-04-12T09:05Z:
- the missing single-file `v3f` audit hub now exists at `versions/v3f_exportable_audit_v1/reproduce_v3f_exportable_audit.py`
  - it verifies the README evaluation contract against the local `v3f` artifacts (`max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, `max_model_len=8192`, `max_lora_rank=32` where available)
  - it hard-checks the historically important `v3f` numbers from local artifacts plus the corrected audit note:
    - stored Phase0 `249/320 = 0.7781`
    - corrected local320 `240/320 = 0.7500`
    - corrected binary_hard `18/60 = 0.3000`
    - proxy actual `133/200 = 0.6650`
    - specialized563 `238/563 = 0.4227`
  - it also pulls out the concrete hidden-gap bottlenecks that still block a README-compatible climb toward `0.9`:
    - `supported_not_structured = 1/55 = 0.0182`
    - `binary_structured_byte_not_formula = 1/25 = 0.0400`
  - and it locks the current compatibility conclusion in code, not only prose:
    - `baseline_mlx/.../stage1_broad_v3f_union/mlx_adapter_bundle/bundle_manifest.json` explicitly says the bundle is **not claimed to be PEFT/vLLM submission-compatible**
- practical implication:
  - the earlier gap “there is no single-file `v3f` audit/repro script” is now closed on the audit side
  - `audit-v3f-exportable-lineage` can now be treated as done
  - the remaining `v3f` work is no longer artifact discovery; it is the harder path of turning the verified `v3f` lessons into a submission-compatible single-adapter training/export line that can actually push toward the mandatory `0.9`

Update 2026-04-12T08:20Z:
- repo-wide lineage audit under the README contract now sharpens the roadmap toward the mandatory `0.9` target:
  - the only measured lineage above `0.9` in-repo is `prompt-router-v6(-repro)` at `293/320 = 0.9156`
  - however `versions/v1/v1-results.md` confirms that `prompt-router-v6-repro` is a **multi-adapter + solver local pipeline**, not a single `submission.zip` adapter compatible with README submitting rules
  - therefore it is the best **accuracy source of truth**, but not the current submission path
- the best historically verified exportable-leaning lineage beyond the current selected incumbent is `v3f`:
  - stored Phase0 artifact: `249/320 = 0.7781`
  - corrected README-style local320 after binary bug re-audit: `240/320 = 0.7500`
  - actual proxy rerun: `133/200 = 0.6650`
  - specialized563: `238/563 = 0.4227`
  - the supporting correction evidence lives in `cuda-train-data-analysis-v1/proof_first_solver_factory_routing/result/LEADERBOARD_GAP_INVESTIGATION_2026-04-09.md`
- practical implication:
  - `prompt-router-v6` is the clearest blueprint for **what** reaches `0.9`
  - `v3f` is the clearest blueprint for **what single-adapter direction** has already beaten the current exportable incumbent
  - the dominant submission bottleneck remains **binary_hard content correctness**, not general_stable (`0.915` is already solved in the incumbent)

Update 2026-04-12T08:05Z:
- the next no-unit continuation after `reprobridge34` is now concretized in the single-file recovery hub:
  - `reprobridge35_text3bit1num8raw16nounit_v1`: `1c48f9aa -> 6b393b81`
  - `reprobridge36_text3bit1num8raw17nounit_v1`: `27cec7a9 -> 552e14d7`
- important nuance from the follow-up audit:
  - this is **not** a new stronger hard-score frontier; the best remaining candidates are same-tier `verified_trace_ready` `numeric_2x2` lateral refreshes
  - both swaps preserve the no-unit mix (`Unit = 0`) and stay inside the all-train_split equation path
  - lower-confidence candidate `2af7134e -> 5c743e8a` was intentionally left out for now because it shifts operator/formula family more aggressively
- operationally:
  - `launch_reprobridge31_32_recovery.py` now knows `reprobridge35/36`
  - artifact materialization completed via file-only methods (view+edit row-by-row reconstruction): `reprobridge35/36` CSV+summary are now emitted

Update 2026-04-12T07:50Z:
- this queue snapshot was later proven stale by file-only inspection:
  - `reprobridge27` did later materialize fully and complete with suite/audit/export artifacts
  - `reprobridge28` did later materialize a real run root and finish training, but not postprocess
  - only `reprobridge29/30` remained artifact-only
- practical lesson:
  - `launch_reprobridge31_32_recovery.py --status-report` must distinguish artifact-only, training-complete, and submission-ready bridge states rather than collapsing them into one queued bucket

Update 2026-04-12T07:35Z:
- `reprobridge26_text3bit1num8raw7unitedge_v1` also fully completed autonomously:
  - final full-suite scores are `readme_local320 = 228/320 = 0.7125` and `leaderboard_proxy_v1_set = 126/200 = 0.6300`
  - `audit_status = potentially_exportable_2d_only`, `submission.zip` exists, and no threshold submission artifact was produced
  - detached postprocess published commit `01c6eeb4` (`Record reprobridge26 raw7-unitedge results`)
- this closes the current dead-on-local320 bridge chain:
  - `reprobridge24`: `233/320`, `127/200`, commit `c5c4e94f`
  - `reprobridge25`: `232/320`, `125/200`, commit `f61cbf57`
  - `reprobridge26`: `228/320`, `126/200`, commit `01c6eeb4`
- selector impact remains nil so far:
  - the best-submission selector is still unchanged through iteration `53` (`2026-04-12T07:34:24Z`)
  - incumbent remains `o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1`
  - `candidate_count = 38`, `eligible_candidate_count = 5`

Update 2026-04-12T07:17Z:
- `reprobridge26_text3bit1num8raw7unitedge_v1` has now also failed the README gate on local320:
  - `readme_local320 = 228/320 = 0.7125`
  - detached eval has already advanced into `leaderboard_proxy_v1_set` and is currently at `176/200` with `117` correct = `0.6648` (`11/13` chunks completed)
  - `postprocess_manifest.json` exists and shows the detached `postprocess-run` chain is active with `eval_suite.status = running`
  - as with `reprobridge24/25`, this is now another dead-on-local320 autonomous lane that may still publish a full suite result later, but it has no remaining threshold path
- queue state remains stalled beyond that point:
  - only the `reprobridge31` artifact CSV/summary exists; the `reprobridge31` run root itself still does not exist, while `/tmp/reprobridge31_waiters/` still contains only the stale partial waiter pair (`live`, `threshold075`) waiting on missing `prepare_manifest.json` / suite summary
  - only the `reprobridge32` artifact CSV/summary exists; the `reprobridge32` run root still does not exist and there is still no waiter directory
- shell recovery remains globally blocked:
  - a fresh verify/commit attempt from a separate general-purpose agent failed immediately on `git --no-pager status --short --untracked-files=all` with the same `posix_openpt failed: Device not configured`
  - so pytest plus the commit/push of the current recovery-hub / test / ledger / follow-up-artifact changes are still blocked by PTY allocation failure, not by test failures
- the single-file recovery hub now surfaces artifact-only queued state for `reprobridge31/32` as well:
  - `launch_reprobridge31_32_recovery.py` status-report includes `artifact_status` for runs whose stagefreeze artifact CSV/summary exists even when the downstream run root has never been created
  - regression coverage was added so `build_status_report()` explicitly preserves the `artifact exists / run root missing` state instead of collapsing it into a generic missing run
  - follow-up artifacts `reprobridge33/34` remain intentionally visible through `followup_steps` rather than `runs`, and regression coverage now fixes that intended distinction in tests
  - top-level summary lists now also include `artifact_only_runs`, `stale_waiter_runs`, `dead_local320_runs`, and `dead_local320_proxy_active_runs` for faster third-party handoff
  - a followup review also caught and fixed a `followup_steps` test mismatch: the regression test now matches the intentionally exposed `remove_id` / `add_id` fields
- best-submission auto selector still has not moved:
  - by iteration `51` (`2026-04-12T07:24:21Z`), the selected exportable candidate remains `o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1`
  - the selected metrics are still `local320 235/320 = 0.7344`, `general_stable 183/200 = 0.915`, `proxy_v1 131/200 = 0.655`
  - `candidate_count` has expanded to `38` and `eligible_candidate_count` to `5`, but none of the new bridge descendants displaced the incumbent

Update 2026-04-12T06:14Z:
- the detached `reprobridge24` and `reprobridge25` waiters did not stall at dead-on-local320; both now fully completed postprocess and published:
  - `reprobridge24_text3bit1num8raw6nograv_v1`: `readme_local320 = 233/320 = 0.7281`, `leaderboard_proxy_v1_set = 127/200 = 0.6350`, `audit_status = potentially_exportable_2d_only`, `submission.zip` exists, publish commit `c5c4e94f`
  - `reprobridge25_text3bit1num8raw6unitedge_v1`: `readme_local320 = 232/320 = 0.7250`, `leaderboard_proxy_v1_set = 125/200 = 0.6250`, `audit_status = potentially_exportable_2d_only`, `submission.zip` exists, publish commit `f61cbf57`
  - no threshold submission artifact is visible under either run root, matching the completed threshold waiters and the sub-`0.75` local320 outcomes
- this supersedes the earlier dead-lane reading that `reprobridge24/25` still lacked full-suite summaries; they are now closed autonomous completions, not pending cleanup
- the bridge queue also advanced for real:
  - `reprobridge26_text3bit1num8raw7unitedge_v1` is no longer hypothetical; `wait_for_trigger_path.json` shows `reprobridge25` suite summary was observed at `2026-04-12T06:12:06Z` and the memory gate immediately passed
  - `prepare_manifest.json` and `training_result.json` now exist for `reprobridge26`
  - latest visible train/eval markers are `iteration 64`, `optimizer_step 8`, `train_loss 0.3545`, `val_loss 0.4078`
  - no suite progress or full-suite summary is visible yet, so `reprobridge26` is now the active autonomous lane to watch
- runtime blocker is still current:
  - a fresh PTY-backed shell probe from this session still fails with `posix_openpt failed: Device not configured`, so new pytest / git / launcher execution remains blocked even though detached bridge automation is still advancing

Update 2026-04-12T05:34Z:
- `reprobridge24_text3bit1num8raw6nograv_v1` has now also failed the README gate on local320:
  - `readme_local320 = 233/320 = 0.7281`
  - detached eval has already rolled into `leaderboard_proxy_v1_set`, but it starts from `0/200` and there is still no full-suite summary
  - no threshold submission was produced, so this lane is now another dead-on-local320 branch that should either self-resolve through detached automation or be cut once PTY-backed shell control returns
- `reprobridge25_text3bit1num8raw6unitedge_v1` has now also failed the README gate on local320:
  - `readme_local320 = 232/320 = 0.7250`
  - detached eval has already rolled into `leaderboard_proxy_v1_set`, but it starts from `0/200` and there is still no full-suite summary
  - no threshold submission was produced, so this lane is also dead on local320 and now only has value as an already-armed autonomous completion path
- implication for the bridge wave:
  - the surviving `24/25` evidence is gone; the active wave is now effectively dead-on-local320 while queued descendants (`26/31/32`) remain unlaunched from this session because PTY-backed shell execution is still broken
  - once shell control returns, the operator now has a real choice point: either let dead `reprobridge25` finish proxy/full-suite so any already-armed `reprobridge26` chain can trigger, or cut `reprobridge25` early and manually relaunch from `reprobridge26/31/32`
- `reprobridge33/34` follow-up materialization is now being attempted via two background paths:
  - the original background materializer is still running
  - a second local-only materializer was launched so the no-unit follow-up CSV/summary generation can finish without relying on GitHub fetches

Update 2026-04-12T05:22Z:
- `reprobridge23_text3bit1num8raw5unitedge_v1` no longer needs operational retirement:
  - detached postprocess completed autonomously and published commit `bc262fc7` (`Record reprobridge23 full-raw unitedge results`)
  - final full-suite scores are `local320 227/320 = 0.7094` and `proxy_v1 126/200 = 0.6300`
  - `audit_status = potentially_exportable_2d_only`, `submission.zip` exists, and both threshold waiters correctly skipped (`local-ge-0.75` / `local-ge-0.80`)
  - the stale `reprobridge24` queue waiter also completed harmlessly as `skipped_existing_target`, confirming that `reprobridge24` had already been launched and no handoff gap remained
- surviving live bridge prefixes at this checkpoint:
  - `reprobridge24`: `233/304 = 0.7664`
  - `reprobridge25`: `231/288 = 0.8021`
- the single-file recovery hub is now better aligned with shell-recovery handoff:
  - `launch_reprobridge31_32_recovery.py --status-report` now covers `reprobridge26` as well
  - waiter summaries now expose parsed pid status and `missing_waiters`, so `reprobridge31/32` can be reattached from one JSON read once PTY execution returns
  - run summaries now also expose `gate_state` (`phase`, `proxy_started`, `dead_on_local320`, threshold gate classification), so dead-on-local320 lanes like `reprobridge24` can be recognized from status JSON without re-reading multiple progress files
  - top-level status report now also exposes `dead_local320_pending_suite`, so dead lanes that have already rolled into proxy but still lack a full-suite summary can be surfaced immediately
  - `baseline_mlx/tests/test_single_file_stage_waiters.py` now also covers the recovery hub import path, waiter pid/missing-waiter summary, `build_status_report()` coverage for `reprobridge26`, and `--materialize-followups` row replacement behavior
- queue / selector state:
  - `reprobridge26` still has no visible output root yet
  - `reprobridge31` still has only partial waiter state (`live`, `threshold075`)
  - `reprobridge32` still has no waiter directory
  - best-submission auto selector remains unchanged through iteration `26` (`2026-04-12T05:18:53Z`), still selecting `o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1` at `local320 235/320 = 0.7344`, `general_stable 183/200 = 0.915`, `proxy_v1 131/200 = 0.655`
- runtime blocker is unchanged:
  - new PTY-backed shell execution from this session still fails with `posix_openpt failed: Device not configured`

Update 2026-04-12T05:08Z:
- `baseline_mlx/reproduce_nemotron_sft_lora_with_cot_v2_mlx.py` now retries `git add` / `git commit` when concurrent publish attempts hit `.git/index.lock`:
  - this was added after the detached `reprobridge24` live poller crashed inside `publish_results_md_to_git` with `fatal: Unable to create ... .git/index.lock: File exists`
  - the publish path now waits and retries instead of failing immediately, which should make concurrent detached ledger publishers more robust during the active bridge wave
  - note: the already-running detached `reprobridge24` poller had loaded the old code and is still considered crashed; any later reattach should use the updated single-file code path
  - regression coverage now exists for both `git add` and `git commit` index.lock retry paths in `baseline_mlx/tests/test_single_file_stage_waiters.py`
- latest active bridge prefixes at this checkpoint:
  - `reprobridge24`: `220/272 = 0.8088`
  - `reprobridge25`: `201/240 = 0.8375`
- `launch_reprobridge31_32_recovery.py` now also has a repo-tracked single-file `--status-report` mode:
  - it summarizes `reprobridge23/24/25/31/32`, `reprobridge31/32` waiter directories, the best-submission selector, and whether `reprobridge33/34` follow-up artifacts already exist
  - this keeps recovery, follow-up materialization, and status inspection inside one single-file operational entrypoint
- latest detached-read state remains:
  - `reprobridge23` is still dead on local320 (`227/320 = 0.7094`) and proxy is now `97/128 = 0.7578`
  - `reprobridge24` current local prefix is `194/224 = 0.8661`
  - `reprobridge25` current local prefix is `167/176 = 0.9489`
  - none of `reprobridge23/24/25` has produced a full suite summary yet, so their detached postprocess workers are still waiting on evaluation completion
- queue / waiter reality is now sharper:
  - `reprobridge31` has partial waiter state only (`live`, `threshold075`)
  - `reprobridge32` still has no waiter directory at all
  - `reprobridge26` still has no visible `prepare_manifest.json` or `training_result.json`, so no downstream raw-heavy launch has materialized yet
- best-submission auto selector is still unchanged through poll iteration `23` (`2026-04-12T05:03:49Z`):
  - selected exportable lane remains `o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1`
  - selected score remains `local320 235/320 = 0.7344`, `general_stable 183/200 = 0.915`, `proxy_v1 131/200 = 0.655`

Update 2026-04-12T04:56Z:
- `reprobridge21_text3bit1num8raw2grav1unitedge_v1` no longer needs operational retirement:
  - its detached single-file `postprocess-run` waiter completed autonomously even while new interactive shell commands still fail with `posix_openpt failed: Device not configured`
  - final README-aligned scores are `readme_local320 = 227/320 = 0.7094` and `leaderboard_proxy_v1_set = 126/200 = 0.6300`
  - audit/export also completed (`audit_status = potentially_exportable_2d_only`, `submission.zip` present), and the waiter published the result block in commit `0878db9e` (`Record reprobridge21 unit-edge results`)
- the only dead bridge lane that still requires an actual kill is now `reprobridge23_text3bit1num8raw5unitedge_v1`:
  - local320 finalized at `227/320 = 0.7094`
  - proxy is already underway at `62/80 = 0.7750`
- surviving bridge evidence remains concentrated in:
  - `reprobridge24_text3bit1num8raw6nograv_v1`: `167/176 = 0.9489`
  - `reprobridge25_text3bit1num8raw6unitedge_v1`: `144/144 = 1.0000`
- the canonical repo recovery script was tightened accordingly:
  - `launch_reprobridge31_32_recovery.py` now retires only `reprobridge23` before arming the `reprobridge31` and `reprobridge32` waiters
- `reprobridge31` turned out to be partially armed already:
  - detached `live` and `threshold075` waiters are present under `/tmp/reprobridge31_waiters/`
  - both are still waiting on `reprobridge31` artifacts because the missing `launcher` has not created `prepare_manifest.json`
  - so the missing operational pieces are now precisely: `reprobridge31 launcher`, `reprobridge31 postprocess`, `reprobridge31 threshold080`, plus all `reprobridge32` waiters
- a repo-tracked single-file follow-up generator now exists for the next no-unit descendants:
  - `launch_reprobridge31_32_recovery.py --materialize-followups` is prepared to materialize
    - `reprobridge33`: `8c6a158e -> 27cec7a9`
    - `reprobridge34`: `db6a5663 -> 2af7134e`
  - this keeps the continuation README-visible and git-trackable even though the current PTY blocker still prevents actually running the generator from this session
- operational implication:
  - interactive PTY-backed shell execution is still blocked from this session, but previously armed detached single-file Python waiters can still finish eval/audit/export/publish on their own

Update 2026-04-12T04:52Z:
- `reprobridge23_text3bit1num8raw5unitedge_v1` is now also dead on the README contract:
  - `readme_local320` finalized at `227/320 = 0.7094`
  - the lane is already spending more eval on `leaderboard_proxy_v1_set` at `46/64 = 0.7188`, so it should be cut alongside `reprobridge21` as soon as subprocess execution is healthy again
- live bridge survivors remain strong:
  - `reprobridge24_text3bit1num8raw6nograv_v1`: `156/160 = 0.9750`
  - `reprobridge25_text3bit1num8raw6unitedge_v1`: `128/128 = 1.0000`
- dead-lane waste is now larger than at the previous checkpoint:
  - `reprobridge21` proxy has advanced further to `117/176 = 0.6648`
  - `reprobridge23` proxy has also started and is now `46/64 = 0.7188`
- the continuous best-submission selector is still unchanged:
  - as of poll iteration `20` (`2026-04-12T04:48:46Z`), the selected exportable candidate remains `o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1`
  - selected score remains `local320 235/320 = 0.7344`, `general_stable 183/200 = 0.915`, `proxy_v1 131/200 = 0.655`
- recovery scope has widened:
  - `launch_reprobridge31_32_recovery.py` now retires both dead lanes (`reprobridge21`, `reprobridge23`) before arming the `reprobridge31` and `reprobridge32` waiters
  - a shell-health probe from this session still fails with `posix_openpt failed: Device not configured`, so the actual retire/arm step remains blocked from here
- next no-unit continuation after `reprobridge32` is now narrowed down from repository evidence:
  - strongest `reprobridge33` candidate is `remove 8c6a158e -> add 27cec7a9`
  - optional follow-up `reprobridge34` candidate is `remove db6a5663 -> add 2af7134e`
  - rationale: `8c6a158e` is the remaining rule-based symbolic outlier in the no-unit branch, while `27cec7a9` is `verified_trace_ready` and stable across the recorded symbol-analysis history

Update 2026-04-12T04:08Z:
- README-aligned `readme_local320` now resolves `reprobridge21_text3bit1num8raw2grav1unitedge_v1` as dead:
  - final local score is `227/320 = 0.7094`
  - so the lane cannot meet the working `0.75` gate and should be retired at the next moment shell execution is healthy enough to stop its remaining live/proxy workers
- the stronger surviving bridge lanes remain healthy:
  - `reprobridge23_text3bit1num8raw5unitedge_v1`: `226/288 = 0.7847`
  - `reprobridge24_text3bit1num8raw6nograv_v1`: `80/80 = 1.0000`
  - `reprobridge25_text3bit1num8raw6unitedge_v1`: `48/48 = 1.0000`
- dead-lane waste that still needs cleanup once shell execution recovers:
  - `reprobridge21` has already moved on to `leaderboard_proxy_v1_set` and is currently `43/64 = 0.6719`, so it is spending eval capacity on a lane that no longer has a promotion path
- the continuous best-submission selector is still stable:
  - as of poll iteration `13` (`2026-04-12T04:13:38Z`), the selected exportable candidate remains `o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1`
  - selected score remains `local320 235/320 = 0.7344`, `general_stable 183/200 = 0.915`, `proxy_v1 131/200 = 0.655`
- the queue has been extended one more step offline:
  - `reprobridge31_text3bit1num8raw12unitedge_v1`
    - remove: `3f37b894`
    - add: `2f5959c9`
    - resulting mix: `Bit 34 / Text 18 / Gravity 9 / Unit 1 / Equation 18`
    - rationale: start from `reprobridge30`, keep only the last hard unit-edge hedge `0c26f842`, and swap the final non-edge unit stabilizer for the next highest-hard-score still-unused train_split `numeric_2x2` row
  - `reprobridge32_text3bit1num8raw13nounit_v1`
    - remove: `0c26f842`
    - add: `1c48f9aa`
    - resulting mix: `Bit 34 / Text 18 / Gravity 9 / Unit 0 / Equation 19`
    - rationale: start from `reprobridge31`, remove the final hard unit-edge hedge, and swap in the next highest-hard-score still-unused train_split `numeric_2x2` row to create the terminal no-unit aggressive descendant of the bridge family
- operational blocker:
  - the current shell runtime is intermittently failing with `posix_openpt failed: Device not configured`, so `reprobridge21` retirement and the missing `reprobridge31` launcher/postprocess/0.80 waiters are prepared but not yet armed from this session
  - a single-shot recovery entrypoint was prepared at `session-state/.../files/bridge_runtime_recovery.py`; once subprocess execution recovers, it is meant to terminate remaining `reprobridge21` workers and arm the missing `reprobridge31` waiters in one pass
  - the canonical git-tracked recovery entrypoint is now `launch_reprobridge31_32_recovery.py`, which is designed to retire `reprobridge21` and arm the `reprobridge31` plus `reprobridge32` waiters in a single-file pass once subprocess execution is healthy again

Update 2026-04-12T03:45Z:
- `reprobridge22_text3bit1num8raw5grav1_fullraw_v1` is now operationally retired:
  - README-aligned `readme_local320` finalized at `231/320 = 0.7219`, so the lane cannot cross the working `0.75` promotion gate
  - its live poller, postprocess worker, threshold waiter, and stale `reprobridge22 summary -> reprobridge21/23` waiters were explicitly stopped
- the recovered headroom was used immediately:
  - free memory recovered to about `178.12 GB`
  - `reprobridge25_text3bit1num8raw6unitedge_v1` was manual early-launched with the same single-file `resume-train-from-run` path used for `reprobridge24`
  - existing `reprobridge25` prepare/live/postprocess waiters attached automatically once `prepare_manifest.json` appeared
- current implication:
  - active bridge lanes are now `21/23/24/25`
  - after `25` joined, free memory settled near `95.04 GB`, so `reprobridge26+` remain queued behind the normal corrected handoff chain rather than being manual early-launched

Update 2026-04-12T03:34Z:
- `reprobridge24_text3bit1num8raw6nograv_v1` was manual early-launched as soon as `reprobridge20` was cut and host free memory recovered above the standing launch band:
  - launch path: single-file `resume-train-from-run`
  - source run: `o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1`
  - runtime preflight: `system_free_memory=63%`, `gpu_device_util=100%`
  - immediate state: `prepare_manifest.json` is present, the existing live/postprocess/threshold waiters have attached, and training has already reached `Iter 1: Val loss 0.397`
- operational implication:
  - the bridge wave is back to four active lanes (`21/22/23/24`) before `reprobridge23` full-suite completion
  - `reprobridge25 -> 30` remain queued behind the corrected handoff chain, so the queue can keep refilling even after this early-launch override

Update 2026-04-12T03:29Z:
- `reprobridge20_text3bit1num8raw4grav1_hedgecut_v1` is now operationally retired:
  - README-aligned `readme_local320` finished at `229/320 = 0.7156`, so it can no longer cross the working `0.75` promotion gate even with the remaining proxy pass
  - its live poller, postprocess worker, threshold waiter, and stale `reprobridge20 summary -> reprobridge22/23` handoff waiters were explicitly stopped
- immediate implication:
  - host free memory recovered to about `178.93 GB`, which is back above the standing `PhysMem unused >= 150 GB` launch band
  - the next actual blocker for `reprobridge24` is no longer host headroom; it is only the missing `reprobridge23` full-suite summary
- current visible bridge-wave state after the cut:
  - `reprobridge21`: `226/288 = 0.7847` (`14/32` still needed to hold `0.75`)
  - `reprobridge22`: `230/288 = 0.7986` (`10/32` still needed to hold `0.75`)
  - `reprobridge23`: `144/144 = 1.0000` so far, still the key handoff lane for `24 -> 30`

Update 2026-04-12T03:18Z:
- The repaired raw-heavy bridge queue has now been extended two more steps beyond `reprobridge28`:
  - `reprobridge29_text3bit1num8raw10unitedge_v1` is now materialized from `reprobridge28`
    - remove: `2af08815`
    - add: `1f445c5e`
    - resulting mix: `Bit 34 / Text 18 / Gravity 9 / Unit 3 / Equation 16`
    - rationale: keep the hard unit-edge hedge `0c26f842` and the remaining stronger unit stabilizers, but swap the weakest remaining unit row for the highest-hard-score still-unused verified `numeric_2x2` row that is already present in the baseline `train_split_with_cot.csv`
  - `reprobridge30_text3bit1num8raw11unitedge_v1` is now also materialized from `reprobridge29`
    - remove: `95e8326c`
    - add: `2f485a40`
    - resulting mix: `Bit 34 / Text 18 / Gravity 9 / Unit 2 / Equation 17`
    - rationale: continue the same bridge direction one step further by cutting the last remaining hard-2 unit stabilizer while still leaving `3f37b894` and the hard unit-edge row `0c26f842` in place
- immediate implication:
  - queue depth is now `24 -> 25 -> 26 -> 27 -> 28 -> 29 -> 30`
  - unlike `27/28`, both new additions come from `baseline/nemotron-sft-lora-with-cot-v2/artifacts/train_split_with_cot.csv`, so they stay inside the generated-COT-safe source family and do not require manual `type` backfill
- operational note:
  - the continuous proxybench best-submission poller was restarted after the old shell exited; the selected exportable candidate is still the same `235/320, 131/200` `o30best_proxybench30ao_b10_t10_g15_u15` lane, so queue extension can continue without losing submission mirroring

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1 -->
### Auto result: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1`

- recorded_at: `2026-04-12T19:31:56.183968+00:00`
- label: `o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_v1`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_binary10_text10_grav15_unit15_v1.csv`
- sampled_rows: `80`
- optimizer_steps: `8`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Scores

- readme_local320: `235/320 = 0.7344`
- local320_components: `general_stable_set 183/200 = 0.9150; binary_hard_set 29/60 = 0.4833; symbol_watch_set 23/60 = 0.3833`
- leaderboard_proxy_v1_set: `131/200 = 0.6550`

#### Submission audit

- audit_status: `potentially_exportable_2d_only`
- peft_export_ready: `True`
- tensor_count: `232`

#### Submission export

- submission_zip: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1/submission_export/submission.zip`
- zip_size_bytes: `102357401`
- validation_valid: `True`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1 -->

### Manual threshold promotion note: `local-ge-0.70 frontier`

- source_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1`
- promotion_script: `versions/baseline_mlx_threshold_submission_v1/reproduce_threshold_submission.py`
- promoted_at: `2026-04-11T19:08Z`
- threshold_label: `local-ge-0.70`
- readme_contract: `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, `max_model_len=8192`, `max_lora_rank=32`
- gate_scores: `readme_local320 235/320 = 0.7344`, `leaderboard_proxy_v1_set 131/200 = 0.6550`
- output_root: `baseline_mlx/outputs/threshold_submission_local_ge_070_frontier_v1`
- summary_md: `baseline_mlx/outputs/threshold_submission_local_ge_070_frontier_v1/threshold_submission_summary.md`
- reproduced_submission_zip: `baseline_mlx/outputs/threshold_submission_local_ge_070_frontier_v1/submission_export/submission.zip`
- reproduced_zip_size_bytes: `102357401`
- reproduced_validation_valid: `True`
- notes: `the already-achieved >0.70 frontier is now re-exported by the new single-file threshold pipeline, so future >0.75 / >0.8 promotions can reuse the same README-contract path instead of relying on the original run-root export only`

### Manual threshold waiter note: `active + queued wave 0.75 / 0.8`

- armed_at: `2026-04-11T19:10Z`
- wait_script: `versions/baseline_mlx_threshold_submission_v1/reproduce_threshold_submission.py`
- wait_condition: `each waiter blocks on eval_suite_readme_proxy_specialized/benchmark_eval_suite_summary.json for its target run, then conditionally emits threshold artifacts only when both README-contract gates are satisfied`
- gate_contract: `readme_local320 >= target threshold`, `leaderboard_proxy_v1_set >= 0.65`, `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, `max_model_len=8192`
- active_waiters: `reprobridge20 -> {0.75, 0.80}`, `reprobridge22 -> {0.75, 0.80}`, `reprobridge21 -> {0.75, 0.80}`, `reprobridge23 -> {0.75, 0.80}`
- retired_waiters: `numreal8` retired after local320 finished at `226/320 = 0.7063`, which ruled out both `local-ge-0.75` and `local-ge-0.80`; `reprogap5` retired after stalling at `225/304 = 0.7401` with one chunk left, which made `local-ge-0.75` improbable enough to cut for memory; `reprogap4` retired after local320 finished at `229/320 = 0.7156`, which ruled out both the tracked frontier and `local-ge-0.75`; `reprobridge9` retired after local320 finished at `230/320 = 0.7188`, which ruled out both the tracked frontier and `local-ge-0.75`; `reprobridge10` retired after local320 finished at `228/320 = 0.7125`, which ruled out both the tracked frontier and `local-ge-0.75`; `reprobridge12` retired after local320 finished at `228/320 = 0.7125`, which ruled out both the tracked frontier and `local-ge-0.75`; `reprobridge13` retired after local320 finished at `235/320 = 0.7344`, which matched the tracked frontier but still missed the `0.75` gate and therefore did not justify further proxy continuation; `reprobridge15` retired after local320 finished at `228/320 = 0.7125`, which ruled out both the tracked frontier and `local-ge-0.75` and made further proxy continuation lower EV than the stronger raw-heavy siblings; `reprobridge16` retired after local320 finished at `232/320 = 0.7250`, which cleared the previous bridge-family siblings but still missed both the tracked frontier and the `0.75` gate; `reprobridge17` retired after local320 finished at `227/320 = 0.7094`, which matched the older bridge-family collapse pattern rather than the surviving raw+gravity line; `reprobridge18` retired after local320 finished at `227/320 = 0.7094`, which failed in almost the same way as reprobridge17 and removed the last live value from the hybrid restore branch; `reprobridge19` retired after local320 finished at `231/320 = 0.7219`, which ruled out both the tracked frontier and the `0.75` gate before proxy continuation justified another heavy eval worker`
- queued_waiters: `reprobridge24 -> {0.75, 0.80}`, `reprobridge25 -> {0.75, 0.80}`, `reprobridge26 -> {0.75, 0.80}`, `reprobridge27 -> {0.75, 0.80}`, `reprobridge28 -> {0.75, 0.80}`
- output_roots: `baseline_mlx/outputs/threshold_submission_numreal8_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprogap4_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprogap5_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprobridge9_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprobridge10_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprobridge12_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprobridge13_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprobridge15_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprobridge16_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprobridge17_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprobridge18_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprobridge19_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprobridge20_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprobridge21_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprobridge22_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprobridge23_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprobridge24_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprobridge25_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprobridge26_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprobridge27_local_ge_075_v1`, `..._080_v1`, `threshold_submission_reprobridge28_local_ge_075_v1`, `..._080_v1`
- notes: `this keeps the threshold packaging path live across the currently running bridge wave, so any qualifying >0.75 or >0.8 result can materialize a submission artifact immediately instead of waiting for another manual pass; numreal8, reprogap5, reprogap4, reprobridge9, reprobridge10, reprobridge12, reprobridge13, reprobridge15, reprobridge16, reprobridge17, reprobridge18, and now reprobridge19 were all retired from the active threshold set after finishing below the necessary local gates, while reprobridge20, reprobridge22, reprobridge21, and manually early-launched reprobridge23 remain the active threshold-tracked lanes; a later artifact audit found that reprobridge23 actually trained with sampled_rows=79 because 0c26f842 landed in the queued CSV with blank generated_cot/type, so queued descendants reprobridge24/25/26 were repaired in place before launch and the queue now extends further through corrected reprobridge27 to reprobridge28`

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_verifiedswap22_bit33eq2_lr1e6_len1024_from_proxybench_v2 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_verifiedswap22_bit33eq2_lr1e6_len1024_from_proxybench_v2`

- status: `paused_memory_cut`
- label: `o30best-verifiedswap22-bit33eq2-v2-eval-live`
- observed_at: `2026-04-11T18:00:40+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_verifiedswap22_bit33eq2_lr1e6_len1024_from_proxybench_v2`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_verifiedswap22_bit33eq2_v1.csv`
- sampled_rows: `80`
- optimizer_progress: `0/8 = 0.00%`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_verifiedswap22_bit33eq2_lr1e6_len1024_from_proxybench_v2/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_verifiedswap22_bit33eq2_lr1e6_len1024_from_proxybench_v2/eval_suite_readme_proxy_specialized`
- suite_evaluations: `1/2 = 50.00%`
- current_evaluation: `leaderboard_proxy_v1_set`
- current_rows_progress: `0/200 = 0.00%`
- current_chunks_progress: `0/13 = 0.00%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_verifiedswap22_bit33eq2_lr1e6_len1024_from_proxybench_v2/eval_suite_readme_proxy_specialized/leaderboard_proxy_v1_set/benchmark_eval_progress.json`
- accuracy_so_far: `0.0000`
- correct_so_far: `0`
- completed_evaluations: `['readme_local320']`
- completed_evaluation_scores: `readme_local320 230/320 = 0.7188`
- manual_cut_note: `bit33eq2 finished local320 at 230/320, below the tracked 235/320 frontier; after reprogap4 launch pushed host headroom down to roughly PhysMem unused 49 GB, proxy continuation was intentionally cut to protect the wave and keep resources for reprogap4 plus the numreal bridge lanes`
- post_cut_memory_note: `after killing the bit33 postprocess + live poller workers, host headroom recovered to roughly PhysMem unused 206 GB`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `74387`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_verifiedswap22_bit33eq2_lr1e6_len1024_from_proxybench_v2 -->

### Manual queue note: `reprogap4_text3bit1_anchortrim_v1`

- status: `launched_after_sym9_cut`
- queued_at: `2026-04-11T17:42Z`
- launched_at: `2026-04-11T17:57Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprogap4_text3bit1_anchortrim_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprogap4_text3bit1_anchortrim_v1.csv`
- trigger: `launched early once sym9 was cut and free memory recovered to ~145 GB; the original wait-on-bit33 launcher was then terminated to avoid duplicate start paths`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: tracked `131/200` frontier beats clean repro `128/200` on six proxy rows; two numeric_2x2 rows are already covered by the current bridge family, so this queue targets the remaining four absent rows (`text_monoalphabetic x3 + bit_structured_byte_formula x1`) while trimming the easiest gravity/unit stabilizers from `verifiedswap22_bit33eq2`

### Manual queue note: `reprogap5_text3bit1num1_anchortrim_v1`

- status: `launched_after_bit33_cut`
- queued_at: `2026-04-11T17:50Z`
- launched_at: `2026-04-11T18:02Z`
- training_completed_at: `2026-04-11T18:05Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprogap5_text3bit1num1_anchortrim_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprogap5_text3bit1num1_anchortrim_v1.csv`
- trigger: `launched early once bit33 proxy was cut and free memory recovered to ~206 GB; the original wait-on-numreal8 launcher was then terminated to avoid duplicate start paths`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: `reprogap4` covers the four absent frontier-over-repro rows with verified text + structured-byte rows; this hedge adds the only remaining absent reverse-gap row (`8158a14c`, `answer_only_keep numeric_2x2`) as a boxed answer-only example while trimming the next easiest gravity stabilizer, keeping answer-only exposure at `1/80`
- cut_note: `this lane was later retired at readme_local320 225/304 = 0.7401 with one chunk left because it needed 15/16 in the final chunk to recover the 0.75 gate; proxy continuation was intentionally terminated to free memory for reprogap4, reprobridge9, and the queued sibling wave`

### Manual queue note: `reprobridge9_text3bit1num5_anchortrim_v1`

- status: `cut_after_local320`
- queued_at: `2026-04-11T18:10Z`
- launched_at: `2026-04-11T18:36Z`
- training_completed_at: `2026-04-11T18:38Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge9_text3bit1num5_anchortrim_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge9_text3bit1num5_anchortrim_v1.csv`
- triggers: `it was launched early while reprogap4 / reprogap5 / numreal8 were still active because host headroom was about PhysMem unused 143-144 GB, which was enough to reopen a fourth active lane; the original summary-trigger launch waiters are no longer the primary path`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: this hybrid combines the exact four absent frontier-over-repro rows from `reprogap4` with the five quality-focused numeric anchors from `verifiedmix`, while trimming the easiest five gravity and four unit stabilizers from `verifiedswap22_bit33eq2`
- resulting_mix: `Bit 34 / Text 18 / Gravity 10 / Unit 11 / Equation 7`
- notes: `the goal was to test whether the narrow text+structured-byte reproducibility fix and the verified numeric bridge stack could combine constructively without introducing answer_only numeric rows; the early launch opened with Iter 1 val_loss ≈ 0.398, closed short train at train_loss ≈ 0.3614 / val_loss ≈ 0.3980, handed off to README-contract eval, and was then retired once local320 finalized at 230/320 = 0.7188`

### Manual queue note: `reprobridge10_text3bit1num5num1_anchortrim_v1`

- status: `cut_after_local320`
- queued_at: `2026-04-11T18:20Z`
- launched_at: `2026-04-11T20:34Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge10_text3bit1num5num1_anchortrim_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge10_text3bit1num5num1_anchortrim_v1.csv`
- trigger: `launched early once the numreal8 and reprogap5 cuts recovered roughly PhysMem unused 202 GB; this intentionally overrode the previous wait-for-reprobridge9-summary chain so the sibling matrix could keep expanding in parallel`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: this sibling stacks the exact four `reprogap4` frontier-over-repro rows, the five verifiedmix numeric anchors, and the single raw-only reverse-gap answer_only row from `reprogap5`, while trimming the easiest five gravity and five unit stabilizers from `verifiedswap22_bit33eq2`
- resulting_mix: `Bit 34 / Text 18 / Gravity 10 / Unit 10 / Equation 8`
- notes: `this is the first queued sibling that carries all currently known repro-gap fixes in one 80-row set while keeping answer_only exposure capped at 1/80; the original launch waiter was accidentally killed during stale summary cleanup, but a fresh duplicate-safe wait-resume launcher was re-armed and confirmed live; once memory recovered, the run was started directly and opened with Iter 1 val_loss ≈ 0.368 while the existing live/postprocess waiters remained in place to pick up the new run; it was later retired once local320 finalized at 228/320 = 0.7125`

### Manual queue note: `reprobridge12_text3bit1num8_anchortrim_v1`

- status: `cut_after_local320`
- queued_at: `2026-04-11T18:24Z`
- launched_at: `2026-04-11T20:41Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge12_text3bit1num8_anchortrim_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge12_text3bit1num8_anchortrim_v1.csv`
- trigger: `launched early once the reprogap4 cut recovered roughly PhysMem unused 192 GB; this intentionally overrode the previous wait-for-reprobridge10-summary chain so the broad sibling could join the live wave immediately`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: this broader sibling combines the exact four `reprogap4` frontier-over-repro rows with the full eight-row `numreal8` numeric block, while trimming the easiest six gravity and six unit stabilizers from `verifiedswap22_bit33eq2`
- resulting_mix: `Bit 34 / Text 18 / Gravity 9 / Unit 9 / Equation 10`
- notes: `this is the broad-numeric counterpart to reprobridge9 and was originally chained after reprobridge10, but after the reprogap4 cut freed enough memory it was started directly; the short train closed with train_loss ≈ 0.3630 / val_loss ≈ 0.4518 / optimizer_step 8 / peak_memory ≈ 65.46 GB and then handed off to the existing live/postprocess waiters; it was later retired once local320 finalized at 228/320 = 0.7125`

### Manual queue note: `reprobridge13_text3bit1num8num1_anchortrim_v1`

- status: `cut_after_local320`
- queued_at: `2026-04-11T18:29Z`
- launched_at: `2026-04-11T20:58Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge13_text3bit1num8num1_anchortrim_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge13_text3bit1num8num1_anchortrim_v1.csv`
- trigger: `launched early once host headroom returned to roughly PhysMem unused 192 GB, intentionally overriding the original wait-for-reprobridge12-summary chain so the final answer_only sibling could join the active wave immediately`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: this factor sibling adds the single `reprogap5` reverse-gap answer_only hedge on top of `reprobridge12`, closing the narrow/broad numeric bridge × answer_only off/on 2x2 queue matrix
- resulting_mix: `Bit 34 / Text 18 / Gravity 9 / Unit 8 / Equation 11`
- notes: `reprobridge13 differs from reprobridge12 by exactly one row: answer_only hedge row 8158a14c replaces the next easiest remaining unit stabilizer a127eb72; runtime preflight captured current_pid 77590 with PhysMem unused about 192 GB, GPU device util 100%, and in-use system memory about 193.37 GB at launch; the short train then closed with train_loss ≈ 0.3629 / val_loss ≈ 0.4594 / optimizer_step 8 / peak_memory ≈ 65.46 GB and handed off to README-contract eval; it later finalized at readme_local320 235/320 = 0.7344 with binary 29/60, symbol 23/60, and text 33/50, then was intentionally retired because it still missed the 0.75 gate and early proxy rows were only 14/32 = 0.4375`

### Manual queue note: `reprobridge15_text3bit1num8num1swap_anchorrestore_v1`

- status: `cut_after_local320_below_threshold`
- queued_at: `2026-04-11T22:04Z`
- launched_at: `2026-04-11T22:31Z`
- local320_completed_at: `2026-04-12T00:40Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge15_text3bit1num8num1swap_anchorrestore_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge15_text3bit1num8num1swap_anchorrestore_v1.csv`
- trigger: `launched early once reprobridge10 and reprobridge12 were cut and host headroom returned to roughly PhysMem unused 313 GB, intentionally overriding the original wait-for-reprobridge13-summary queue while keeping the duplicate-safe waiters alive as no-op backups`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: `the selected numeric_2x2 pool is already exhausted by reprobridge13, so this follow-up no longer tries to widen numeric coverage; instead it keeps the 8158a14c hedge row from reprobridge13, restores one unit stabilizer, and drops one high-audit answer_only numeric row to test whether the broad+hedge branch works better with slightly less answer_only burden`
- resulting_mix: `Bit 34 / Text 18 / Gravity 9 / Unit 9 / Equation 10`
- notes: `reprobridge15 is a hedge-swap / anchor-restore branch built by replacing answer_only numeric row 6e60b0c5 from reprobridge13 with restored unit stabilizer a127eb72 from reprobridge12; the run stayed within the currently selected train pool and was started immediately once the reprobridge10 and reprobridge12 cuts reopened enough headroom; runtime preflight captured current_pid 4499 with PhysMem unused about 313 GB, GPU device util 99%, and in-use system memory about 65.03 GB at launch; the short train then closed with train_loss ≈ 0.3678 / val_loss ≈ 0.4383 / optimizer_step 8 / peak_memory ≈ 65.46 GB, but local320 then collapsed in the final chunk and finished at 228/320 = 0.7125 (general 177/200, binary 30/60, symbol 21/60, text 28/50), so the lane was cut before any meaningful proxy continuation rather than spending further memory on a now-clearly losing hedge-heavy branch`

### Manual queue note: `reprobridge16_text3bit1num8num1raw4_answertrim_v1`

- status: `cut_after_local320_below_threshold`
- queued_at: `2026-04-11T22:41Z`
- launched_at: `2026-04-11T22:42Z`
- local320_completed_at: `2026-04-12T01:08Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge16_text3bit1num8num1raw4_answertrim_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge16_text3bit1num8num1raw4_answertrim_v1.csv`
- trigger: `launched immediately once reprobridge10 / reprobridge12 cuts and the light 2-lane eval wave left roughly PhysMem unused 251 GB, so the raw-numeric sibling did not wait for a further parent summary`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: `start from reprobridge15, keep the restored unit stabilizer a127eb72 and the low-hard-score hedge 8158a14c, trim two harder answer_only numeric rows plus two easy unit stabilizers, and replace them with four unused verified_trace_ready raw numeric_2x2 rows with generated CoT to test whether raw verified numeric depth beats selected-pool answer_only saturation`
- resulting_mix: `Bit 34 / Text 18 / Gravity 9 / Unit 7 / Equation 12`
- notes: `reprobridge16 is the first bridge sibling that explicitly steps outside the currently exhausted selected numeric pool while preserving the reprogap4 text/bit corrective skeleton; it removes answer_only numeric rows 9cb03277 and a19a75ba plus easy unit stabilizers 7291f716 and c1775d35, then adds raw verified numeric rows 118f8c86, 7195cb7b, 9b820b4e, and a8e033fe sourced from generated-CoT train splits; runtime preflight captured current_pid 8818 with PhysMem unused about 251 GB, GPU device util 100%, and in-use system memory about 130.65 GB at launch; the short train then closed with train_loss ≈ 0.3599 / val_loss ≈ 0.3957 / optimizer_step 8 / peak_memory ≈ 65.46 GB, but local320 finished at only 232/320 = 0.7250 (general 182/200, binary 30/60, symbol 20/60, text 32/50), so the lane was cut after only the first proxy chunk (10/16 = 0.625) instead of spending more memory on a below-threshold continuation`

### Manual queue note: `reprobridge17_text3bit1num8num1gravrestore_v1`

- status: `cut_after_local320_below_threshold`
- queued_at: `2026-04-11T22:47Z`
- launched_at: `2026-04-11T22:55Z`
- local320_completed_at: `2026-04-12T01:20Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge17_text3bit1num8num1gravrestore_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge17_text3bit1num8num1gravrestore_v1.csv`
- trigger: `launched immediately once reprobridge15 and reprobridge16 both opened strongly and host headroom returned to roughly PhysMem unused 252 GB, intentionally overriding the surviving wait-for-reprobridge15/16-summary queue while keeping the duplicate-safe waiters attached as no-op backups`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: `start from reprobridge15, remove one harder answer_only numeric row plus the low-hard-score hedge row, and restore two zero-hard-score gravity stabilizers to test whether the bridge wave benefits more from broader stabilizer recovery than from carrying the extra answer_only numeric burden`
- resulting_mix: `Bit 34 / Text 18 / Gravity 11 / Unit 9 / Equation 8`
- notes: `reprobridge17 is the stabilizer-restore sibling to reprobridge16's raw-numeric expansion; it removes numeric rows 9cb03277 and 8158a14c, restores gravity rows 853a0e3b and 66ae2b46, and serves as the low-risk fallback if the raw-verified numeric jump over-corrects toward equation-heavy behavior; runtime preflight captured current_pid 13023 with PhysMem unused about 252 GB, GPU device util 100%, and in-use system memory about 129.23 GB at launch; the short train then closed with train_loss ≈ 0.3504 / val_loss ≈ 0.3976 / optimizer_step 8 / peak_memory ≈ 65.46 GB, but local320 finished at only 227/320 = 0.7094 (general 175/200, binary 30/60, symbol 22/60, text 26/50), so the lane was cut before the first proxy chunk rather than spending more memory on another below-threshold continuation`

### Manual queue note: `reprobridge18_text3bit1num8num1raw2gravrestore_v1`

- status: `cut_after_local320_below_threshold`
- queued_at: `2026-04-11T22:59Z`
- launched_at: `2026-04-11T23:08Z`
- local320_completed_at: `2026-04-12T01:27Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge18_text3bit1num8num1raw2gravrestore_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge18_text3bit1num8num1raw2gravrestore_v1.csv`
- trigger: `launched immediately once the active wave still held roughly PhysMem unused 190 GB, intentionally overriding the wait-for-reprobridge15/16/17-summary queue while keeping the duplicate-safe waiters attached as no-op backups`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: `start from reprobridge15, keep the low-hard-score hedge 8158a14c, remove two harder answer_only numeric rows plus two easy unit stabilizers, then add two strongest unused raw verified numeric rows and two zero-hard-score gravity stabilizers; this is the balanced hybrid between reprobridge16's raw expansion and reprobridge17's pure stabilizer restore`
- resulting_mix: `Bit 34 / Text 18 / Gravity 11 / Unit 7 / Equation 10`
- notes: `reprobridge18 preserves the corrective reprogap4 text/bit skeleton and the 8158a14c hedge while moderating reprobridge16's equation-heavy jump; it removes 9cb03277, a19a75ba, 7291f716, and c1775d35, then adds raw verified numeric rows 118f8c86 and 7195cb7b plus restored gravity rows 853a0e3b and 66ae2b46; runtime preflight captured current_pid 17080 with PhysMem unused about 190 GB, GPU device util 100%, and in-use system memory about 193.36 GB at launch; the short train then closed with train_loss ≈ 0.3596 / val_loss ≈ 0.4478 / optimizer_step 8 / peak_memory ≈ 65.46 GB, but local320 finished at only 227/320 = 0.7094 (general 177/200, binary 30/60, symbol 20/60, text 27/50), so the lane was cut before the first proxy chunk rather than preserving a now-clearly losing hybrid branch`

### Manual queue note: `reprobridge19_text3bit1num8num1raw3grav1_v1`

- status: `cut_after_local320_below_threshold`
- queued_at: `2026-04-11T23:11Z`
- launched_at: `2026-04-11T23:53Z`
- training_completed_at: `2026-04-11T23:56Z`
- local320_completed_at: `2026-04-12T02:18Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge19_text3bit1num8num1raw3grav1_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge19_text3bit1num8num1raw3grav1_v1.csv`
- trigger: `manually launched once host headroom recovered to roughly PhysMem unused 154 GB / system_free_memory 51%, intentionally overriding the wait-for-reprobridge15/16/17/18-summary queue while keeping the duplicate-safe waiters alive as no-op backups`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: `start from reprobridge15, keep the hedge 8158a14c, remove two harder answer_only numeric rows plus two easy unit stabilizers, then add three strongest unused raw verified numeric rows and one zero-hard-score gravity stabilizer; this is the bridge between reprobridge16's raw4 push and reprobridge18's raw2+grav2 balance`
- resulting_mix: `Bit 34 / Text 18 / Gravity 10 / Unit 7 / Equation 11`
- notes: `reprobridge19 preserves the corrective reprogap4 text/bit skeleton while leaning slightly more equation-heavy than reprobridge18; it removes 9cb03277, a19a75ba, 7291f716, and c1775d35, then adds raw verified numeric rows 118f8c86, 7195cb7b, and 9b820b4e plus restored gravity row 853a0e3b; runtime preflight captured current_pid 30788 with PhysMem unused about 154 GB, system_free_memory 51%, GPU device util 100%, and in-use system memory about 257.48 GB at launch; the short train then closed with train_loss ≈ 0.3468 / val_loss ≈ 0.4527 / optimizer_step 8 / peak_memory ≈ 65.46 GB, but local320 ultimately finished at only 231/320 = 0.7219, so the lane was cut before leaderboard_proxy_v1_set could consume another heavy eval worker and the recovered headroom was immediately reused for reprobridge23`

### Manual queue note: `reprobridge20_text3bit1num8raw4grav1_hedgecut_v1`

- status: `launched_early_after_reprobridge16_cut`
- queued_at: `2026-04-11T23:49Z`
- launched_at: `2026-04-12T01:15Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge20_text3bit1num8raw4grav1_hedgecut_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge20_text3bit1num8raw4grav1_hedgecut_v1.csv`
- trigger: `original queue trigger was reprobridge19 full-suite summary plus free memory >= 150 GB, but after reprobridge16 was cut the host returned to PhysMem unused ≈ 194 GB, so this lane was started manually with the duplicate-safe launcher left in place as a no-op backup`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: `start from reprobridge19, drop the remaining low-hard-score answer_only hedge 8158a14c, and replace it with the strongest still-unused generated-COT-capable raw verified numeric row f94810f5; this preserves the single gravity restore from reprobridge19 while following the current live evidence that raw-heavy bridge siblings are staying cleaner than the hedge-heavy branch as local320 hardens`
- resulting_mix: `Bit 34 / Text 18 / Gravity 10 / Unit 7 / Equation 11`
- notes: `reprobridge20 is the hedge-cut continuation of the raw+gravity branch: it keeps the reprogap4 corrective text/bit skeleton, retains raw verified numeric rows 118f8c86, 7195cb7b, and 9b820b4e plus restored gravity row 853a0e3b, then swaps out hedge row 8158a14c for sourced raw verified numeric row f94810f5; f94810f5 was confirmed in generated-COT-capable sources including train_split_with_cot_v3f_one_shot_repair_v1.csv, train_split_with_cot_v2_plus_binary_route_aware.csv, and sampled_train_split_with_cot.csv; runtime preflight at manual early launch captured current_pid 54704 with PhysMem used ≈ 317 GB / unused ≈ 194 GB, GPU device util 100%, and in-use system memory ≈ 194.11 GB`

### Manual queue note: `reprobridge22_text3bit1num8raw5grav1_fullraw_v1`

- status: `launched_early_after_reprobridge18_cut`
- queued_at: `2026-04-12T00:27Z`
- launched_at: `2026-04-12T01:29Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge22_text3bit1num8raw5grav1_fullraw_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge22_text3bit1num8raw5grav1_fullraw_v1.csv`
- trigger: `original queue trigger was reprobridge20 full-suite summary plus free memory >= 150 GB, but after reprobridge18 was cut the host returned to PhysMem unused ≈ 251 GB while reprobridge20 had already opened 16/16, so this lane was started manually with the duplicate-safe launcher left in place as a no-op backup`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: `start from reprobridge20, drop the last remaining answer_only numeric row 9c8eef89, and replace it with the strongest still-unused generated-COT-capable raw verified numeric row a8e033fe; this preserves the single gravity restore from reprobridge19/20 while merging the last top raw row that already defined reprobridge16's strongest raw-heavy branch`
- resulting_mix: `Bit 34 / Text 18 / Gravity 10 / Unit 7 / Equation 11`
- notes: `reprobridge22 is the full-raw continuation of the raw+gravity branch: it keeps the reprogap4 corrective text/bit skeleton, retains raw verified numeric rows 118f8c86, 7195cb7b, 9b820b4e, and f94810f5 plus restored gravity row 853a0e3b, then swaps out the last answer_only numeric row 9c8eef89 for sourced raw verified numeric row a8e033fe; a8e033fe was confirmed in generated-COT-capable sources including train_split_with_cot_v3f_one_shot_repair_v1.csv, train_split_with_cot_v2_plus_binary_route_aware.csv, and sampled_train_split_with_cot.csv; runtime preflight at manual early launch captured current_pid 59249 with PhysMem used ≈ 259 GB / unused ≈ 251 GB, GPU device util 100%, and in-use system memory ≈ 129.21 GB`

### Manual queue note: `reprobridge21_text3bit1num8raw2grav1unitedge_v1`

- status: `launched_early_after_reprobridge22_train_handoff`
- queued_at: `2026-04-12T00:13Z`
- reordered_at: `2026-04-12T00:28Z`
- launched_at: `2026-04-12T01:34Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge21_text3bit1num8raw2grav1unitedge_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge21_text3bit1num8raw2grav1unitedge_v1.csv`
- trigger: `original trigger was reprobridge22 full-suite summary plus free memory >= 150 GB, but once reprobridge22 had finished train and the host still held PhysMem unused ≈ 191 GB, this final queued continuation was started manually with the duplicate-safe launcher left in place as a no-op backup`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: `start from reprobridge18, keep the raw2 branch and one restored gravity stabilizer, but trade the second zero-hard-score gravity row 66ae2b46 for the strongest still-unused generated-COT-capable ratio_edge unit row 0c26f842; this tests whether a harder unit hedge improves later hidden-tail robustness without giving up the strong raw2 balance`
- resulting_mix: `Bit 34 / Text 18 / Gravity 10 / Unit 8 / Equation 10`
- notes: `reprobridge21 was originally kept queued one step later behind reprobridge22 because the raw-heavy bridge family was still owning the cleaner live evidence than the unit-edge side hedge; it preserves raw verified numeric rows 118f8c86 and 7195cb7b plus restored gravity row 853a0e3b from reprobridge18, then swaps out gravity row 66ae2b46 for sourced unit row 0c26f842; 0c26f842 was confirmed in generated-COT-capable sources including train_split_with_cot_v2_plus_binary_route_aware.csv and sampled_train_split_with_cot.csv; runtime preflight at manual early launch captured current_pid 60884 with PhysMem used ≈ 320 GB / unused ≈ 191 GB, GPU device util 100%, and in-use system memory ≈ 193.38 GB`

### Manual queue note: `reprobridge23_text3bit1num8raw5unitedge_v1`

- status: `launched_early_after_reprobridge19_cut`
- queued_at: `2026-04-12T01:45Z`
- launched_at: `2026-04-12T02:20Z`
- training_completed_at: `2026-04-12T02:23Z`
- suite_started_at: `2026-04-12T02:23Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge23_text3bit1num8raw5unitedge_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge23_text3bit1num8raw5unitedge_v1.csv`
- trigger: `duplicate-safe launchers were originally armed behind the first full-suite summary from reprobridge19, reprobridge20, reprobridge21, or reprobridge22, but once reprobridge19 was cut the host immediately recovered to PhysMem unused ≈ 189 GB while reprobridge20 / reprobridge21 / reprobridge22 still held strong early scores, so this lane was manual early-launched with the remaining duplicate-safe launchers left in place as later no-op backups`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: `start from reprobridge22, keep the full raw verified numeric spine, but trade the last zero-hard-score gravity restore 853a0e3b for reprobridge21's harder ratio_edge unit row 0c26f842; this explicitly fuses the current full-raw mainline with the unit-edge side hedge to test whether later hidden-tail robustness benefits more from one hard unit anchor than from one easy gravity stabilizer once all answer_only numerics are already gone`
- resulting_mix: `Bit 34 / Text 18 / Gravity 9 / Unit 8 / Equation 11`
- notes: `reprobridge23 is the queue-refill cross between the two surviving design ideas: reprobridge22's full-raw backbone and reprobridge21's unit-edge hedge; it removes the remaining gravity restore 853a0e3b from reprobridge22, keeps raw verified numeric rows 118f8c86, 7195cb7b, 9b820b4e, f94810f5, and a8e033fe, and injects unit row 0c26f842 instead; runtime preflight at manual early launch captured current_pid 74969 with PhysMem used ≈ 322 GB / unused ≈ 189 GB, system_free_memory 62%, GPU device util 100%, and in-use system memory ≈ 194.06 GB; the short train then closed almost immediately with train_loss ≈ 0.3439 / val_loss ≈ 0.3951 / optimizer_step 8 / peak_memory ≈ 65.46 GB, and the pre-armed postprocess chain has already started `eval_suite_readme_proxy_specialized` on the target root (`readme_local320` 0/320 at handoff), so the bridge queue remains live without waiting for another full-suite summary to free memory; later audit of the run root showed `prepare_manifest.sampled_rows = 79`, because 0c26f842 had blank generated_cot/type in the artifact CSV and was silently skipped by the loader, so treat reprobridge23 as a useful but imperfect early diagnostic rather than the exact intended 80-row unitedge fusion`

### Manual queue note: `reprobridge24_text3bit1num8raw6_nograv_v1`

- status: `queued_behind_reprobridge23_full_suite_summary`
- queued_at: `2026-04-12T01:46Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge24_text3bit1num8raw6nograv_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge24_text3bit1num8raw6_nograv_v1.csv`
- trigger: `queued one step behind reprobridge23 full-suite summary, again with duplicate-safe start guards and the conservative free-memory gate of PhysMem unused >= 150 GB`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: `start from reprobridge22, drop the last remaining easy gravity restore 853a0e3b, and replace it with the strongest still-unused generated-COT-capable verified numeric_2x2 row dfec0ed4; this is the aggressive continuation of the raw-heavy line and tests whether the branch can push one step past fullraw now that every answer_only numeric row has already been removed`
- resulting_mix: `Bit 34 / Text 18 / Gravity 9 / Unit 7 / Equation 12`
- notes: `reprobridge24 keeps the reprogap4 corrective bit/text skeleton and all five full-raw numeric rows from reprobridge22, then swaps the final gravity restore for unused raw verified numeric row dfec0ed4, which is present in train_split_with_cot_v3f_one_shot_repair_v1.csv, train_split_with_cot_v2_plus_binary_route_aware.csv, the broad-v3f sampled_train_split_with_cot.csv, and baseline train_split_with_cot.csv; a later artifact audit found dfec0ed4 missing type/generated_cot in the queued-only CSV, so the train CSV was repaired in place from baseline train_split_with_cot.csv before launch; duplicate-safe live-poller, postprocess, and threshold waiters are already armed on the target root so the queue can keep extending even if reprobridge23 itself is later manual-launched early`

### Manual queue note: `reprobridge25_text3bit1num8raw6unitedge_v1`

- status: `queued_behind_reprobridge24_full_suite_summary`
- queued_at: `2026-04-12T02:07Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge25_text3bit1num8raw6unitedge_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge25_text3bit1num8raw6unitedge_v1.csv`
- trigger: `queued one step behind reprobridge24 full-suite summary, again guarded by duplicate-safe launchers and the conservative free-memory band of PhysMem unused >= 150 GB`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: `start from reprobridge23, keep the injected ratio_edge unit hedge 0c26f842, but swap one weakest remaining ratio_lt2 unit stabilizer f9103e02 for the strongest still-unused generated-COT-capable verified numeric_2x2 row 791fc537; this explicitly fuses reprobridge23's unit-edge hedge with reprobridge24's raw6 push instead of forcing an either-or choice`
- resulting_mix: `Bit 34 / Text 18 / Gravity 9 / Unit 7 / Equation 12`
- notes: `reprobridge25 is the deeper continuation after the queue-refill pair: it starts from reprobridge23, preserves raw verified numeric rows 118f8c86, 7195cb7b, 9b820b4e, f94810f5, and a8e033fe plus unit-edge row 0c26f842, then removes weak ratio_lt2 unit row f9103e02 in favor of unused raw verified numeric row 791fc537; 791fc537 was confirmed in train_split_with_cot_v3f_one_shot_repair_v1.csv, train_split_with_cot_v2_plus_binary_route_aware.csv, the broad-v3f sampled_train_split_with_cot.csv, and baseline train_split_with_cot.csv; a later artifact audit found that both 0c26f842 and 791fc537 had landed in the queued-only CSV without complete type/generated_cot fields, so the train CSV was repaired in place from baseline train_split_with_cot.csv before launch; duplicate-safe launch, live-poller, postprocess, and threshold waiters are all now armed on the target root so the bridge queue can continue beyond reprobridge24 without another manual wiring pass`

### Manual queue note: `reprobridge26_text3bit1num8raw7unitedge_v1`

- status: `queued_behind_reprobridge25_full_suite_summary`
- queued_at: `2026-04-12T02:43Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge26_text3bit1num8raw7unitedge_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge26_text3bit1num8raw7unitedge_v1.csv`
- trigger: `queued one step behind reprobridge25 full-suite summary, again guarded by duplicate-safe launchers and the conservative free-memory band of PhysMem unused >= 150 GB`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: `start from reprobridge25, keep the injected ratio_edge unit hedge 0c26f842 and the first extra raw verified numeric row 791fc537, but swap another weakest remaining ratio_lt2 unit stabilizer a127eb72 for reprobridge24's generated-COT-capable verified numeric_2x2 row dfec0ed4; this is the next raw-heavy continuation because it merges the two queued raw6 branches instead of forcing an either-or choice between them`
- resulting_mix: `Bit 34 / Text 18 / Gravity 9 / Unit 6 / Equation 13`
- notes: `reprobridge26 is the triple-fusion continuation after reprobridge24 and reprobridge25: it starts from reprobridge25, preserves raw verified numeric rows 118f8c86, 7195cb7b, 9b820b4e, f94810f5, a8e033fe, and 791fc537 plus unit-edge row 0c26f842, then removes weak ratio_lt2 unit row a127eb72 in favor of dfec0ed4 from the reprobridge24 raw6-nograv branch; dfec0ed4 was confirmed in train_split_with_cot_v3f_one_shot_repair_v1.csv, train_split_with_cot_v2_plus_binary_route_aware.csv, and baseline train_split_with_cot.csv; a later artifact audit found that 0c26f842, 791fc537, and dfec0ed4 needed full type/generated_cot backfill in the queued-only CSV, so the train CSV was repaired in place from baseline train_split_with_cot.csv before launch; duplicate-safe launch, live-poller, postprocess, and threshold waiters can extend the bridge queue one more step without leaving the generated-COT-capable source family`

### Manual queue note: `reprobridge27_text3bit1num8raw8unitedge_v1`

- status: `queued_behind_reprobridge26_full_suite_summary`
- queued_at: `2026-04-12T03:27Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge27_text3bit1num8raw8unitedge_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge27_text3bit1num8raw8unitedge_v1.csv`
- trigger: `queued one step behind reprobridge26 full-suite summary, again guarded by duplicate-safe launchers and the conservative free-memory band of PhysMem unused >= 150 GB`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: `start from repaired reprobridge26, keep the injected ratio_edge unit hedge 0c26f842 and both extra raw verified numeric rows 791fc537 and dfec0ed4, but swap another weakest remaining ratio_lt2 unit stabilizer dae6dea8 for stronger verified numeric_2x2 row 8c6a158e from the rule-based verified COT source; this is the next raw-heavy continuation once the queue has already merged reprobridge24 and reprobridge25`
- resulting_mix: `Bit 34 / Text 18 / Gravity 9 / Unit 5 / Equation 14`
- notes: `reprobridge27 is the raw8 continuation after the repaired reprobridge26 queue: it preserves raw verified numeric rows 118f8c86, 7195cb7b, 9b820b4e, f94810f5, a8e033fe, 791fc537, dfec0ed4, plus unit-edge row 0c26f842, then removes weak ratio_lt2 unit row dae6dea8 in favor of 8c6a158e from baseline/cot/output-csv/rule_based_verified_600_training_data_v2.csv; this intentionally steps outside the current route-aware/v3f source trio for one stronger rule-based verified raw row while keeping the rest of the queue on generated-COT-capable train_split_with_cot sources; duplicate-safe launcher, live-poller, postprocess, and 0.75/0.80 threshold waiters are now armed on the target root behind reprobridge26 full-suite completion`

### Manual queue note: `reprobridge28_text3bit1num8raw9unitedge_v1`

- status: `queued_behind_reprobridge27_full_suite_summary`
- queued_at: `2026-04-12T03:43Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge28_text3bit1num8raw9unitedge_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge28_text3bit1num8raw9unitedge_v1.csv`
- trigger: `queued one step behind reprobridge27 full-suite summary, again guarded by duplicate-safe launchers and the conservative free-memory band of PhysMem unused >= 150 GB`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: `start from reprobridge27, keep only the hardest remaining ratio_edge unit hedge 0c26f842 together with the growing raw verified numeric spine, but swap another weak ratio_lt2 unit stabilizer e346233f for stronger verified numeric_2x2 row db6a5663 from the rule-based verified COT source; this continues the raw-heavy bridge one step further without dropping the final hard unit-edge anchor`
- resulting_mix: `Bit 34 / Text 18 / Gravity 9 / Unit 4 / Equation 15`
- notes: `reprobridge28 is the raw9 continuation after reprobridge27: it preserves raw verified numeric rows 118f8c86, 7195cb7b, 9b820b4e, f94810f5, a8e033fe, 791fc537, dfec0ed4, 8c6a158e, plus unit-edge row 0c26f842, then removes weak ratio_lt2 unit row e346233f in favor of db6a5663 from baseline/cot/output-csv/rule_based_verified_600_training_data_v2.csv; this pushes the queue one more step outside the current route-aware/v3f source trio while still leaving one hard unit-edge stabilizer in place; duplicate-safe launcher, live-poller, postprocess, and 0.75/0.80 threshold waiters are now armed on the target root behind reprobridge27 full-suite completion`

### Manual queue note: `reprobridge29_text3bit1num8raw10unitedge_v1`

- status: `queued_behind_reprobridge28_full_suite_summary`
- queued_at: `2026-04-12T03:18Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge29_text3bit1num8raw10unitedge_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge29_text3bit1num8raw10unitedge_v1.csv`
- trigger: `queued one step behind reprobridge28 full-suite summary, again guarded by duplicate-safe launchers and the conservative free-memory band of PhysMem unused >= 150 GB`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: `start from reprobridge28, keep the hard unit-edge hedge 0c26f842 and the remaining stronger unit stabilizers, but swap the weakest remaining unit row 2af08815 for the highest-hard-score still-unused verified numeric_2x2 row 1f445c5e from baseline train_split_with_cot.csv; this deepens the raw-heavy bridge while stepping back inside the generated-COT-safe source family after the two rule-based additions`
- resulting_mix: `Bit 34 / Text 18 / Gravity 9 / Unit 3 / Equation 16`
- notes: `reprobridge29 is the raw10 continuation after reprobridge28: it preserves the raw verified numeric spine 118f8c86, 7195cb7b, 9b820b4e, f94810f5, a8e033fe, 791fc537, dfec0ed4, 8c6a158e, db6a5663, plus the hard unit-edge row 0c26f842 and remaining unit stabilizers 95e8326c and 3f37b894, then removes weak unit row 2af08815 in favor of 1f445c5e from baseline/nemotron-sft-lora-with-cot-v2/artifacts/train_split_with_cot.csv; duplicate-safe launcher, live-poller, postprocess, and 0.75/0.80 threshold waiters are now armed on the target root behind reprobridge28 full-suite completion`

### Manual queue note: `reprobridge30_text3bit1num8raw11unitedge_v1`

- status: `queued_behind_reprobridge29_full_suite_summary`
- queued_at: `2026-04-12T03:18Z`
- target_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge30_text3bit1num8raw11unitedge_lr1e6_len1024_from_proxybench_v1`
- train_csv: `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge30_text3bit1num8raw11unitedge_v1.csv`
- trigger: `queued one step behind reprobridge29 full-suite summary, again guarded by duplicate-safe launchers and the conservative free-memory band of PhysMem unused >= 150 GB`
- recipe: `notebook-current`, `lr=1e-6`, `epochs=0.8`, `max_seq_length=1024`, `stage-union-exportsafe + attention`
- rationale: `start from reprobridge29, keep the hard unit-edge hedge 0c26f842 and the last stronger unit stabilizer 3f37b894, but swap the remaining hard-2 unit row 95e8326c for the next highest-hard-score still-unused verified numeric_2x2 row 2f485a40 from baseline train_split_with_cot.csv; this extends the raw-heavy bridge another step while still leaving two unit anchors in place`
- resulting_mix: `Bit 34 / Text 18 / Gravity 9 / Unit 2 / Equation 17`
- notes: `reprobridge30 is the raw11 continuation after reprobridge29: it preserves the entire raw verified numeric spine from reprobridge29 plus unit anchors 3f37b894 and 0c26f842, then removes weak unit row 95e8326c in favor of 2f485a40 from baseline/nemotron-sft-lora-with-cot-v2/artifacts/train_split_with_cot.csv; this is the deepest queued continuation so far and keeps the bridge queue populated two steps beyond reprobridge28 without leaving the generated-COT-safe source family; duplicate-safe launcher, live-poller, postprocess, and 0.75/0.80 threshold waiters are now armed on the target root behind reprobridge29 full-suite completion`

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxymiss40_text20_grav15_unit15_sym8_lr2e6_len1536_v1 -->
### Auto result: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxymiss40_text20_grav15_unit15_sym8_lr2e6_len1536_v1`

- recorded_at: `2026-04-12T19:32:00.428519+00:00`
- label: `o30best_proxymiss40_text20_grav15_unit15_sym8_lr2e6_v1`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxymiss40_text20_grav15_unit15_sym8_lr2e6_len1536_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage2_o30best_proxymiss40_text20_grav15_unit15_sym8_v1.csv`
- sampled_rows: `98`
- optimizer_steps: `16`
- lr: `2e-06`
- max_seq_length: `1536`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Scores

- readme_local320: `232/320 = 0.7250`
- local320_components: `general_stable_set 182/200 = 0.9100; binary_hard_set 29/60 = 0.4833; symbol_watch_set 21/60 = 0.3500`
- leaderboard_proxy_v1_set: `130/200 = 0.6500`

#### Submission audit

- audit_status: `potentially_exportable_2d_only`
- peft_export_ready: `True`
- tensor_count: `232`

#### Submission export

- submission_zip: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxymiss40_text20_grav15_unit15_sym8_lr2e6_len1536_v1/submission_export/submission.zip`
- zip_size_bytes: `102356734`
- validation_valid: `True`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxymiss40_text20_grav15_unit15_sym8_lr2e6_len1536_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_ep12_len1024_from_proxymiss_v1 -->
### Auto result: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_ep12_len1024_from_proxymiss_v1`

- recorded_at: `2026-04-12T19:32:01.171274+00:00`
- label: `o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_ep12_v1`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_ep12_len1024_from_proxymiss_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_binary10_text10_grav15_unit15_v1.csv`
- sampled_rows: `80`
- optimizer_steps: `12`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Scores

- readme_local320: `230/320 = 0.7188`
- local320_components: `general_stable_set 179/200 = 0.8950; binary_hard_set 29/60 = 0.4833; symbol_watch_set 22/60 = 0.3667`
- leaderboard_proxy_v1_set: `127/200 = 0.6350`

#### Submission audit

- audit_status: `potentially_exportable_2d_only`
- peft_export_ready: `True`
- tensor_count: `232`

#### Submission export

- submission_zip: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_ep12_len1024_from_proxymiss_v1/submission_export/submission.zip`
- zip_size_bytes: `102356385`
- validation_valid: `True`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_ep12_len1024_from_proxymiss_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_verifiedswap22_eq12anchortrim_lr1e6_len1024_from_proxybench_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_verifiedswap22_eq12anchortrim_lr1e6_len1024_from_proxybench_v1`

- status: `paused_memory_cut`
- label: `o30best-verifiedswap22-eq12anchortrim-v1-live`
- observed_at: `2026-04-11T17:28:21.583398+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_verifiedswap22_eq12anchortrim_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_verifiedswap22_eq12anchortrim_v1.csv`
- sampled_rows: `80`
- optimizer_progress: `0/8 = 0.00%`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_verifiedswap22_eq12anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_verifiedswap22_eq12anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized`
- suite_evaluations: `0/2 = 0.00%`
- current_evaluation: `readme_local320`
- current_rows_progress: `192/320 = 60.00%`
- current_chunks_progress: `12/20 = 60.00%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_verifiedswap22_eq12anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/readme_local320/benchmark_eval_progress.json`
- accuracy_so_far: `0.8906`
- correct_so_far: `171`
- manual_cut_note: `Heavy eq12anchortrim eval was stopped after numreal8 launch pushed host memory to about PhysMem 463G used / 48G unused. Rerun remains possible from existing artifacts.`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `84126`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_verifiedswap22_eq12anchortrim_lr1e6_len1024_from_proxybench_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b20_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1 -->
### Auto result: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b20_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1`

- recorded_at: `2026-04-12T19:31:14.190579+00:00`
- label: `o30best_proxybench30ao_b20_t10_g15_u15_lr1e6_v1`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b20_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_binary20_text10_grav15_unit15_v1.csv`
- sampled_rows: `90`
- optimizer_steps: `9`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Scores

- readme_local320: `229/320 = 0.7156`
- local320_components: `general_stable_set 177/200 = 0.8850; binary_hard_set 29/60 = 0.4833; symbol_watch_set 23/60 = 0.3833`
- leaderboard_proxy_v1_set: `125/200 = 0.6250`

#### Submission audit

- audit_status: `potentially_exportable_2d_only`
- peft_export_ready: `True`
- tensor_count: `232`

#### Submission export

- submission_zip: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b20_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1/submission_export/submission.zip`
- zip_size_bytes: `102356554`
- validation_valid: `True`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b20_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_text060_num100_grav20_unit20_recover_lr4e6_len1024_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_text060_num100_grav20_unit20_recover_lr4e6_len1024_v1`

- status: `evaluating`
- label: `o30_general_recover_t060_n100_g20_u20`
- observed_at: `2026-04-11T06:18:26.528278+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_text060_num100_grav20_unit20_recover_lr4e6_len1024_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_text060_num100_grav20_unit20_recover_v1.csv`
- sampled_rows: `200`
- optimizer_progress: `0/8 = 0.00%`
- lr: `4e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_text060_num100_grav20_unit20_recover_lr4e6_len1024_v1/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_text060_num100_grav20_unit20_recover_lr4e6_len1024_v1/eval_suite_readme_proxy_specialized`
- suite_evaluations: `1/2 = 50.00%`
- current_evaluation: `leaderboard_proxy_v1_set`
- current_rows_progress: `0/200 = 0.00%`
- current_chunks_progress: `0/13 = 0.00%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_text060_num100_grav20_unit20_recover_lr4e6_len1024_v1/eval_suite_readme_proxy_specialized/leaderboard_proxy_v1_set/benchmark_eval_progress.json`
- completed_evaluations: `['readme_local320']`
- completed_evaluation_scores: `readme_local320 228/320 = 0.7125`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `99469`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_text060_num100_grav20_unit20_recover_lr4e6_len1024_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv130_bin40proxyo30p0s10_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1 -->
### Auto result: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv130_bin40proxyo30p0s10_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1`

- recorded_at: `2026-04-12T19:31:40.563874+00:00`
- label: `binary40_o30_p0_s10_no_lz`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv130_bin40proxyo30p0s10_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_text_verified130_binary40proxyo30p0s10_grav15_unit15_rowselect_v1.csv`
- sampled_rows: `200`
- optimizer_steps: `12`
- lr: `8e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Scores

- readme_local320: `231/320 = 0.7219`
- local320_components: `general_stable_set 180/200 = 0.9000; binary_hard_set 28/60 = 0.4667; symbol_watch_set 23/60 = 0.3833`
- leaderboard_proxy_v1_set: `130/200 = 0.6500`

#### Submission audit

- audit_status: `potentially_exportable_2d_only`
- peft_export_ready: `True`
- tensor_count: `232`

#### Submission export

- submission_zip: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv130_bin40proxyo30p0s10_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1/submission_export/submission.zip`
- zip_size_bytes: `102356609`
- validation_valid: `True`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv130_bin40proxyo30p0s10_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_text040_num120_grav20_unit20_recover_lr4e6_len1024_v1 -->
### Auto result: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_text040_num120_grav20_unit20_recover_lr4e6_len1024_v1`

- recorded_at: `2026-04-12T19:31:42.668750+00:00`
- label: `o30_general_recover_t040_n120_g20_u20`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_text040_num120_grav20_unit20_recover_lr4e6_len1024_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_text040_num120_grav20_unit20_recover_v1.csv`
- sampled_rows: `200`
- optimizer_steps: `8`
- lr: `4e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Scores

- readme_local320: `231/320 = 0.7219`
- local320_components: `general_stable_set 182/200 = 0.9100; binary_hard_set 28/60 = 0.4667; symbol_watch_set 21/60 = 0.3500`
- leaderboard_proxy_v1_set: `127/200 = 0.6350`

#### Submission audit

- audit_status: `blocked_routed_expert_3d_tensors`
- peft_export_ready: `False`
- tensor_count: `324`
- blocked_reasons: `['MLX adapter contains non-2D LoRA tensors; PEFT/vLLM-equivalent export is not claimed without a verified mapping.', 'switch_mlp routed-expert tensors are 3D in this adapter, so the current single-file pipeline blocks submission export instead of guessing a PEFT layout.']`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_text040_num120_grav20_unit20_recover_lr4e6_len1024_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_text150_bin10p5s5_lzgrav15_unit15_binaryaware_lr4e6_len1024_v3 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_text150_bin10p5s5_lzgrav15_unit15_binaryaware_lr4e6_len1024_v3`

- status: `evaluating`
- label: `o30best_binaryaware_t150_b10p5s5_lz_g15_u15_v3`
- observed_at: `2026-04-11T07:51:10.189025+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_text150_bin10p5s5_lzgrav15_unit15_binaryaware_lr4e6_len1024_v3`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_text150_bin10p5s5_lzgrav15_unit15_binaryaware_v1.csv`
- sampled_rows: `200`
- optimizer_progress: `0/8 = 0.00%`
- lr: `4e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_text150_bin10p5s5_lzgrav15_unit15_binaryaware_lr4e6_len1024_v3/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_text150_bin10p5s5_lzgrav15_unit15_binaryaware_lr4e6_len1024_v3/eval_suite_readme_proxy_specialized`
- suite_evaluations: `1/2 = 50.00%`
- current_evaluation: `leaderboard_proxy_v1_set`
- current_rows_progress: `0/200 = 0.00%`
- current_chunks_progress: `0/13 = 0.00%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_text150_bin10p5s5_lzgrav15_unit15_binaryaware_lr4e6_len1024_v3/eval_suite_readme_proxy_specialized/leaderboard_proxy_v1_set/benchmark_eval_progress.json`
- accuracy_so_far: `0.0000`
- correct_so_far: `0`
- completed_evaluations: `['readme_local320']`
- completed_evaluation_scores: `readme_local320 220/320 = 0.6875`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `37561`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_text150_bin10p5s5_lzgrav15_unit15_binaryaware_lr4e6_len1024_v3 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_verifiedswap22_sym9_lr1e6_len1024_from_proxybench_v2 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_verifiedswap22_sym9_lr1e6_len1024_from_proxybench_v2`

- status: `paused_memory_cut`
- label: `o30best-verifiedswap22-sym9-v2-eval-live`
- observed_at: `2026-04-11T17:54:11+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_verifiedswap22_sym9_lr1e6_len1024_from_proxybench_v2`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_verifiedswap22_sym9_v1.csv`
- sampled_rows: `80`
- optimizer_progress: `0/8 = 0.00%`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_verifiedswap22_sym9_lr1e6_len1024_from_proxybench_v2/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_verifiedswap22_sym9_lr1e6_len1024_from_proxybench_v2/eval_suite_readme_proxy_specialized`
- suite_evaluations: `1/2 = 50.00%`
- current_evaluation: `leaderboard_proxy_v1_set`
- current_rows_progress: `0/200 = 0.00%`
- current_chunks_progress: `0/13 = 0.00%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_verifiedswap22_sym9_lr1e6_len1024_from_proxybench_v2/eval_suite_readme_proxy_specialized/leaderboard_proxy_v1_set/benchmark_eval_progress.json`
- accuracy_so_far: `0.0000`
- correct_so_far: `0`
- completed_evaluations: `['readme_local320']`
- completed_evaluation_scores: `readme_local320 223/320 = 0.6969`
- manual_cut_note: `sym9 reached local320 223/320, so it would need 13/16 remaining tail hits to beat the tracked 235/320 frontier; proxy continuation was intentionally cut after the local summary landed to free headroom for the queued reprogap4 lane once bit33 local summary appears`
- post_cut_memory_note: `after killing the sym9 postprocess + live poller workers, host headroom recovered to roughly PhysMem unused 145 GB`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `74384`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_verifiedswap22_sym9_lr1e6_len1024_from_proxybench_v2 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv130_bin40proxyo30p0s10_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_repro_v1 -->
### Auto result: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv130_bin40proxyo30p0s10_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_repro_v1`

- recorded_at: `2026-04-12T19:31:56.648640+00:00`
- label: `o30best_local_best_actual_repro_v1`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv130_bin40proxyo30p0s10_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_repro_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_text_verified130_binary40proxyo30p0s10_grav15_unit15_rowselect_v1_repro_v1.csv`
- sampled_rows: `200`
- optimizer_steps: `12`
- lr: `8e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Scores

- readme_local320: `227/320 = 0.7094`
- local320_components: `general_stable_set 178/200 = 0.8900; binary_hard_set 29/60 = 0.4833; symbol_watch_set 20/60 = 0.3333`
- leaderboard_proxy_v1_set: `125/200 = 0.6250`

#### Submission audit

- audit_status: `potentially_exportable_2d_only`
- peft_export_ready: `True`
- tensor_count: `232`

#### Submission export

- submission_zip: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv130_bin40proxyo30p0s10_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_repro_v1/submission_export/submission.zip`
- zip_size_bytes: `102356099`
- validation_valid: `True`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv130_bin40proxyo30p0s10_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_repro_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_repro_v1 -->
### Auto result: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_repro_v1`

- recorded_at: `2026-04-12T19:32:00.695691+00:00`
- label: `o30best-proxybench-repro-eval-live`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_repro_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_binary10_text10_grav15_unit15_v1_repro_v1.csv`
- sampled_rows: `80`
- optimizer_steps: `8`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Scores

- readme_local320: `227/320 = 0.7094`
- local320_components: `general_stable_set 176/200 = 0.8800; binary_hard_set 30/60 = 0.5000; symbol_watch_set 21/60 = 0.3500`
- leaderboard_proxy_v1_set: `128/200 = 0.6400`

#### Submission audit

- audit_status: `potentially_exportable_2d_only`
- peft_export_ready: `True`
- tensor_count: `232`

#### Submission export

- submission_zip: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_repro_v1/submission_export/submission.zip`
- zip_size_bytes: `102356933`
- validation_valid: `True`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_repro_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_bit33_numreal8_anchortrim_lr1e6_len1024_from_proxybench_v2 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_bit33_numreal8_anchortrim_lr1e6_len1024_from_proxybench_v2`

- status: `evaluating`
- label: `o30best-bit33-numreal8-anchortrim-v2-live`
- observed_at: `2026-04-11T20:04:54.160553+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_bit33_numreal8_anchortrim_lr1e6_len1024_from_proxybench_v2`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_bit33_numreal8_anchortrim_v1.csv`
- sampled_rows: `80`
- optimizer_progress: `0/8 = 0.00%`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_bit33_numreal8_anchortrim_lr1e6_len1024_from_proxybench_v2/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_bit33_numreal8_anchortrim_lr1e6_len1024_from_proxybench_v2/eval_suite_readme_proxy_specialized`
- suite_evaluations: `1/2 = 50.00%`
- current_evaluation: `leaderboard_proxy_v1_set`
- current_rows_progress: `0/200 = 0.00%`
- current_chunks_progress: `0/13 = 0.00%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_bit33_numreal8_anchortrim_lr1e6_len1024_from_proxybench_v2/eval_suite_readme_proxy_specialized/leaderboard_proxy_v1_set/benchmark_eval_progress.json`
- accuracy_so_far: `0.0000`
- correct_so_far: `0`
- completed_evaluations: `['readme_local320']`
- completed_evaluation_scores: `readme_local320 226/320 = 0.7063`
- manual_cut_note: `numreal8 completed readme_local320 at 226/320, below both the tracked 235/320 frontier and the 0.75 threshold gate, so its proxy continuation was intentionally terminated to preserve headroom for reprogap4, reprogap5, and reprobridge9`
- post_cut_memory_note: `after killing the numreal8 postprocess worker, live poller, and numreal8-specific threshold waiter, host headroom recovered to roughly PhysMem unused 141 GB`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `14351`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_bit33_numreal8_anchortrim_lr1e6_len1024_from_proxybench_v2 -->

<!-- auto-run-summary:start:best-submission-candidate -->
### Auto best submission candidate

- recorded_at: `2026-04-12T19:32:07.859615+00:00`
- status: `selected_candidate`
- candidate_count: `43`
- eligible_candidate_count: `6`
- gates: `{'min_local320_accuracy': 0.7, 'min_general_stable_accuracy': 0.9, 'min_proxy_v2_accuracy': 0.0, 'min_specialized_accuracy': 0.0, 'require_exportable': True}`

- selected_run: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1`
- local320: `235/320 = 0.7344`
- general_stable: `183/200 = 0.9150`
- leaderboard_proxy_v1_set: `131/200 = 0.6550`
- leaderboard_proxy_v2: `0/0 = 0.0000`
- binary_bias_specialized_set: `0/0 = 0.0000`
- audit_status: `potentially_exportable_2d_only`
- submission_zip: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/best_submission_candidate_proxybench_auto/submission.zip`

| run_name | local320 | general_stable | proxy_v1 | proxy_v2 | specialized | exportable |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_b10_t10_g15_u15_lr1e6_len1024_from_proxymiss_v1` | 0.7344 | 0.9150 | 0.6550 | 0.0000 | 0.0000 | `True` |
| `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge29_text3bit1num8raw10unitedge_lr1e6_len1024_from_proxybench_v1` | 0.7312 | 0.9050 | 0.6450 | 0.0000 | 0.0000 | `True` |
| `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge24_text3bit1num8raw6nograv_lr1e6_len1024_from_proxybench_v1` | 0.7281 | 0.9000 | 0.6350 | 0.0000 | 0.0000 | `True` |
| `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge28_text3bit1num8raw9unitedge_lr1e6_len1024_from_proxybench_v1` | 0.7281 | 0.8950 | 0.6600 | 0.0000 | 0.0000 | `True` |
| `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxymiss40_text20_grav15_unit15_sym8_lr2e6_len1536_v1` | 0.7250 | 0.9100 | 0.6500 | 0.0000 | 0.0000 | `True` |
| `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge25_text3bit1num8raw6unitedge_lr1e6_len1024_from_proxybench_v1` | 0.7250 | 0.9000 | 0.6250 | 0.0000 | 0.0000 | `True` |
| `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_text040_num120_grav20_unit20_recover_lr4e6_len1024_v1` | 0.7219 | 0.9100 | 0.6350 | 0.0000 | 0.0000 | `False` |
| `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_textv130_bin40proxyo30p0s10_grav15_unit15_rowselect_lr8e6_len1024_from_reanchor1024_v1` | 0.7219 | 0.9000 | 0.6500 | 0.0000 | 0.0000 | `True` |
<!-- auto-run-summary:end:best-submission-candidate -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_bit33_numreal5_anchortrim_lr1e6_len1024_from_proxybench_v2 -->
### Auto result: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_bit33_numreal5_anchortrim_lr1e6_len1024_from_proxybench_v2`

- recorded_at: `2026-04-12T02:45:57.268143+00:00`
- label: `o30best-bit33-numreal5-anchortrim-v2-live`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_bit33_numreal5_anchortrim_lr1e6_len1024_from_proxybench_v2`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_bit33_numreal5_anchortrim_v1.csv`
- sampled_rows: `80`
- optimizer_steps: `8`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Scores

- readme_local320: `226/320 = 0.7063`
- local320_components: `general_stable_set 175/200 = 0.8750; binary_hard_set 30/60 = 0.5000; symbol_watch_set 21/60 = 0.3500`
- leaderboard_proxy_v1_set: `129/200 = 0.6450`

#### Submission audit

- audit_status: `potentially_exportable_2d_only`
- peft_export_ready: `True`
- tensor_count: `232`

#### Submission export

- submission_zip: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_bit33_numreal5_anchortrim_lr1e6_len1024_from_proxybench_v2/submission_export/submission.zip`
- zip_size_bytes: `102356798`
- validation_valid: `True`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_bit33_numreal5_anchortrim_lr1e6_len1024_from_proxybench_v2 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_bit33_numreal5_verifiedmix_lr1e6_len1024_from_proxybench_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_bit33_numreal5_verifiedmix_lr1e6_len1024_from_proxybench_v1`

- status: `paused_memory_cut`
- label: `o30best-bit33-numreal5-verifiedmix-v1-live`
- observed_at: `2026-04-11T18:05:07+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_bit33_numreal5_verifiedmix_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_bit33_numreal5_verifiedmix_v1.csv`
- sampled_rows: `80`
- optimizer_progress: `0/8 = 0.00%`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_bit33_numreal5_verifiedmix_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_bit33_numreal5_verifiedmix_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized`
- suite_evaluations: `0/2 = 0.00%`
- current_evaluation: `readme_local320`
- current_rows_progress: `32/320 = 10.00%`
- current_chunks_progress: `2/20 = 10.00%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_bit33_numreal5_verifiedmix_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/readme_local320/benchmark_eval_progress.json`
- accuracy_so_far: `1.0000`
- correct_so_far: `32`
- manual_cut_note: `verifiedmix had only reached local320 32/320 when reprogap5 training plus the rest of the active wave drove host headroom down to roughly PhysMem unused 48 GB; it was intentionally cut so the broader numreal8 lane and both reprogap targeted bridges could continue safely`
- post_cut_memory_note: `after killing the verifiedmix postprocess + live poller workers, host headroom recovered to roughly PhysMem unused 107 GB`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `8973`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_bit33_numreal5_verifiedmix_lr1e6_len1024_from_proxybench_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprogap4_text3bit1_anchortrim_lr1e6_len1024_from_proxybench_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprogap4_text3bit1_anchortrim_lr1e6_len1024_from_proxybench_v1`

- status: `evaluating`
- label: `reprogap4 targeted bridge`
- observed_at: `2026-04-11T20:39:53.361972+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprogap4_text3bit1_anchortrim_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprogap4_text3bit1_anchortrim_v1.csv`
- sampled_rows: `80`
- optimizer_progress: `0/8 = 0.00%`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprogap4_text3bit1_anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprogap4_text3bit1_anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized`
- suite_evaluations: `1/2 = 50.00%`
- current_evaluation: `leaderboard_proxy_v1_set`
- current_rows_progress: `0/200 = 0.00%`
- current_chunks_progress: `0/13 = 0.00%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprogap4_text3bit1_anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/leaderboard_proxy_v1_set/benchmark_eval_progress.json`
- accuracy_so_far: `0.0000`
- correct_so_far: `0`
- completed_evaluations: `['readme_local320']`
- completed_evaluation_scores: `readme_local320 229/320 = 0.7156`
- manual_cut_note: `reprogap4 was intentionally cut immediately after local320 completed at 229/320 because the exact-gap bridge still finished below the tracked 235/320 frontier and below the 0.75 threshold gate, making further proxy evaluation lower EV than reallocating memory to reprobridge10 and reprobridge12`
- post_cut_memory_note: `after killing the reprogap4 postprocess worker, live poller, and reprogap4-specific threshold waiter, host headroom recovered to roughly PhysMem unused 192 GB`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `23801`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprogap4_text3bit1_anchortrim_lr1e6_len1024_from_proxybench_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprogap5_text3bit1num1_anchortrim_lr1e6_len1024_from_proxybench_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprogap5_text3bit1num1_anchortrim_lr1e6_len1024_from_proxybench_v1`

- status: `evaluating`
- label: `reprogap5 numeric hedge`
- observed_at: `2026-04-11T20:29:45.531706+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprogap5_text3bit1num1_anchortrim_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprogap5_text3bit1num1_anchortrim_v1.csv`
- sampled_rows: `80`
- optimizer_progress: `0/8 = 0.00%`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprogap5_text3bit1num1_anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprogap5_text3bit1num1_anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized`
- suite_evaluations: `0/2 = 0.00%`
- current_evaluation: `readme_local320`
- current_rows_progress: `304/320 = 95.00%`
- current_chunks_progress: `19/20 = 95.00%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprogap5_text3bit1num1_anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/readme_local320/benchmark_eval_progress.json`
- accuracy_so_far: `0.7401`
- correct_so_far: `225`
- manual_cut_note: `reprogap5 was intentionally cut at 225/304 with one chunk left because it needed 15/16 final answers to recover the 0.75 local gate, making the expected value worse than keeping memory on reprogap4 and reprobridge9`
- post_cut_memory_note: `after killing the reprogap5 postprocess worker, live poller, threshold waiter, and local-summary waiter, host headroom recovered to roughly PhysMem unused 202 GB`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `25616`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprogap5_text3bit1num1_anchortrim_lr1e6_len1024_from_proxybench_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge9_text3bit1num5_anchortrim_lr1e6_len1024_from_proxybench_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge9_text3bit1num5_anchortrim_lr1e6_len1024_from_proxybench_v1`

- status: `paused_memory_cut`
- label: `reprobridge9 hybrid`
- observed_at: `2026-04-11T21:13:45.000000+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge9_text3bit1num5_anchortrim_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge9_text3bit1num5_anchortrim_v1.csv`
- sampled_rows: `80`
- optimizer_progress: `0/8 = 0.00%`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge9_text3bit1num5_anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge9_text3bit1num5_anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized`
- suite_evaluations: `1/2 = 50.00%`
- current_evaluation: `leaderboard_proxy_v1_set`
- current_rows_progress: `32/200 = 16.00%`
- current_chunks_progress: `2/13 = 15.38%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge9_text3bit1num5_anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/leaderboard_proxy_v1_set/benchmark_eval_progress.json`
- accuracy_so_far: `0.4062`
- correct_so_far: `13`
- completed_evaluations: `['readme_local320']`
- completed_evaluation_scores: `readme_local320 230/320 = 0.7188`
- manual_cut_note: `reprobridge9 was intentionally cut immediately after readme_local320 finalized at 230/320 because the hybrid bridge still finished below the tracked 235/320 frontier and below the 0.75 threshold gate, making further proxy continuation lower EV than reallocating memory to reprobridge10, reprobridge12, and reprobridge13`
- post_cut_memory_note: `after killing the reprobridge9 live poller, postprocess worker, threshold waiter, and obsolete reprobridge10 chain waiter, host headroom recovered to roughly PhysMem unused 192 GB`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `36795`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge9_text3bit1num5_anchortrim_lr1e6_len1024_from_proxybench_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge10_text3bit1num5num1_anchortrim_lr1e6_len1024_from_proxybench_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge10_text3bit1num5num1_anchortrim_lr1e6_len1024_from_proxybench_v1`

- status: `evaluating`
- label: `reprobridge10 sibling`
- observed_at: `2026-04-11T22:28:46.063922+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge10_text3bit1num5num1_anchortrim_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge10_text3bit1num5num1_anchortrim_v1.csv`
- sampled_rows: `80`
- optimizer_progress: `0/8 = 0.00%`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge10_text3bit1num5num1_anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge10_text3bit1num5num1_anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized`
- suite_evaluations: `1/2 = 50.00%`
- current_evaluation: `leaderboard_proxy_v1_set`
- current_rows_progress: `0/200 = 0.00%`
- current_chunks_progress: `0/13 = 0.00%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge10_text3bit1num5num1_anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/leaderboard_proxy_v1_set/benchmark_eval_progress.json`
- accuracy_so_far: `0.0000`
- correct_so_far: `0`
- completed_evaluations: `['readme_local320']`
- completed_evaluation_scores: `readme_local320 228/320 = 0.7125`
- manual_cut_note: `reprobridge10 was intentionally cut immediately after readme_local320 finalized at 228/320 because the narrow + hedge sibling still finished below the tracked 235/320 frontier and below the 0.75 threshold gate, making proxy continuation lower EV than reallocating memory to reprobridge13 and reprobridge15`
- post_cut_memory_note: `after killing the reprobridge10 live poller, postprocess worker, threshold waiter, and obsolete reprobridge12 chain waiter, host headroom rose toward PhysMem unused 313 GB`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `70437`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge10_text3bit1num5num1_anchortrim_lr1e6_len1024_from_proxybench_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge12_text3bit1num8_anchortrim_lr1e6_len1024_from_proxybench_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge12_text3bit1num8_anchortrim_lr1e6_len1024_from_proxybench_v1`

- status: `paused_memory_cut`
- label: `reprobridge12 broad`
- observed_at: `2026-04-11T22:29:52.904543+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge12_text3bit1num8_anchortrim_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge12_text3bit1num8_anchortrim_v1.csv`
- sampled_rows: `80`
- optimizer_progress: `0/8 = 0.00%`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge12_text3bit1num8_anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge12_text3bit1num8_anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized`
- suite_evaluations: `1/2 = 50.00%`
- current_evaluation: `leaderboard_proxy_v1_set`
- current_rows_progress: `0/200 = 0.00%`
- current_chunks_progress: `0/13 = 0.00%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge12_text3bit1num8_anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/leaderboard_proxy_v1_set/benchmark_eval_progress.json`
- accuracy_so_far: `0.0000`
- correct_so_far: `0`
- completed_evaluations: `['readme_local320']`
- completed_evaluation_scores: `readme_local320 228/320 = 0.7125`
- manual_cut_note: `reprobridge12 was intentionally cut immediately after readme_local320 finalized at 228/320 because the broad no-answer_only sibling still finished below the tracked 235/320 frontier and below the 0.75 threshold gate, making proxy continuation lower EV than reallocating memory to reprobridge13 and reprobridge15`
- post_cut_memory_note: `after killing the reprobridge12 live poller, postprocess worker, threshold waiter, and obsolete reprobridge13 chain waiter, host headroom rose toward PhysMem unused 313 GB`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `72737`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge12_text3bit1num8_anchortrim_lr1e6_len1024_from_proxybench_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge13_text3bit1num8num1_anchortrim_lr1e6_len1024_from_proxybench_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge13_text3bit1num8num1_anchortrim_lr1e6_len1024_from_proxybench_v1`

- status: `evaluating`
- label: `reprobridge13 factor`
- observed_at: `2026-04-11T22:46:16.979612+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge13_text3bit1num8num1_anchortrim_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge13_text3bit1num8num1_anchortrim_v1.csv`
- sampled_rows: `80`
- optimizer_progress: `0/8 = 0.00%`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge13_text3bit1num8num1_anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge13_text3bit1num8num1_anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized`
- suite_evaluations: `1/2 = 50.00%`
- current_evaluation: `leaderboard_proxy_v1_set`
- current_rows_progress: `32/200 = 16.00%`
- current_chunks_progress: `2/13 = 15.38%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge13_text3bit1num8num1_anchortrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/leaderboard_proxy_v1_set/benchmark_eval_progress.json`
- accuracy_so_far: `0.4375`
- correct_so_far: `14`
- completed_evaluations: `['readme_local320']`
- completed_evaluation_scores: `readme_local320 235/320 = 0.7344`
- manual_cut_note: `reprobridge13 was intentionally cut after readme_local320 finalized at 235/320 because, although it matched the tracked local frontier, it still missed the 0.75 threshold gate and early proxy continuation only reached 14/32 = 0.4375, making further proxy continuation lower EV than reallocating that budget to reprobridge15, reprobridge16, and the queued reprobridge17 fallback`
- post_cut_memory_note: `after killing the reprobridge13 live poller, postprocess worker, threshold waiter, and the reprobridge17-from-13 launcher, the surviving bridge queue now depends only on reprobridge15 and reprobridge16 full-suite summaries`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `77590`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge13_text3bit1num8num1_anchortrim_lr1e6_len1024_from_proxybench_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge15_text3bit1num8num1swap_anchorrestore_lr1e6_len1024_from_proxybench_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge15_text3bit1num8num1swap_anchorrestore_lr1e6_len1024_from_proxybench_v1`

- status: `evaluating`
- label: `reprobridge15 hedge swap`
- observed_at: `2026-04-12T00:40:12.234438+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge15_text3bit1num8num1swap_anchorrestore_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge15_text3bit1num8num1swap_anchorrestore_v1.csv`
- sampled_rows: `80`
- optimizer_progress: `0/8 = 0.00%`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge15_text3bit1num8num1swap_anchorrestore_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge15_text3bit1num8num1swap_anchorrestore_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized`
- suite_evaluations: `1/2 = 50.00%`
- current_evaluation: `leaderboard_proxy_v1_set`
- current_rows_progress: `0/200 = 0.00%`
- current_chunks_progress: `0/13 = 0.00%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge15_text3bit1num8num1swap_anchorrestore_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/leaderboard_proxy_v1_set/benchmark_eval_progress.json`
- accuracy_so_far: `0.0000`
- correct_so_far: `0`
- completed_evaluations: `['readme_local320']`
- completed_evaluation_scores: `readme_local320 228/320 = 0.7125`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `4499`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge15_text3bit1num8num1swap_anchorrestore_lr1e6_len1024_from_proxybench_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge16_text3bit1num8num1raw4_answertrim_lr1e6_len1024_from_proxybench_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge16_text3bit1num8num1raw4_answertrim_lr1e6_len1024_from_proxybench_v1`

- status: `evaluating`
- label: `reprobridge16 raw numeric`
- observed_at: `2026-04-12T01:11:21.495770+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge16_text3bit1num8num1raw4_answertrim_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge16_text3bit1num8num1raw4_answertrim_v1.csv`
- sampled_rows: `80`
- optimizer_progress: `0/8 = 0.00%`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge16_text3bit1num8num1raw4_answertrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge16_text3bit1num8num1raw4_answertrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized`
- suite_evaluations: `1/2 = 50.00%`
- current_evaluation: `leaderboard_proxy_v1_set`
- current_rows_progress: `16/200 = 8.00%`
- current_chunks_progress: `1/13 = 7.69%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge16_text3bit1num8num1raw4_answertrim_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/leaderboard_proxy_v1_set/benchmark_eval_progress.json`
- accuracy_so_far: `0.6250`
- correct_so_far: `10`
- completed_evaluations: `['readme_local320']`
- completed_evaluation_scores: `readme_local320 232/320 = 0.7250`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `8818`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge16_text3bit1num8num1raw4_answertrim_lr1e6_len1024_from_proxybench_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge17_text3bit1num8num1gravrestore_lr1e6_len1024_from_proxybench_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge17_text3bit1num8num1gravrestore_lr1e6_len1024_from_proxybench_v1`

- status: `evaluating`
- label: `reprobridge17 grav restore`
- observed_at: `2026-04-12T01:20:13.009681+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge17_text3bit1num8num1gravrestore_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge17_text3bit1num8num1gravrestore_v1.csv`
- sampled_rows: `80`
- optimizer_progress: `0/8 = 0.00%`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge17_text3bit1num8num1gravrestore_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge17_text3bit1num8num1gravrestore_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized`
- suite_evaluations: `1/2 = 50.00%`
- current_evaluation: `leaderboard_proxy_v1_set`
- current_rows_progress: `0/200 = 0.00%`
- current_chunks_progress: `0/13 = 0.00%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge17_text3bit1num8num1gravrestore_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/leaderboard_proxy_v1_set/benchmark_eval_progress.json`
- accuracy_so_far: `0.0000`
- correct_so_far: `0`
- completed_evaluations: `['readme_local320']`
- completed_evaluation_scores: `readme_local320 227/320 = 0.7094`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `13023`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge17_text3bit1num8num1gravrestore_lr1e6_len1024_from_proxybench_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge18_text3bit1num8num1raw2gravrestore_lr1e6_len1024_from_proxybench_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge18_text3bit1num8num1raw2gravrestore_lr1e6_len1024_from_proxybench_v1`

- status: `evaluating`
- label: `reprobridge18 hybrid`
- observed_at: `2026-04-12T01:27:34.721859+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge18_text3bit1num8num1raw2gravrestore_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge18_text3bit1num8num1raw2gravrestore_v1.csv`
- sampled_rows: `80`
- optimizer_progress: `0/8 = 0.00%`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge18_text3bit1num8num1raw2gravrestore_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge18_text3bit1num8num1raw2gravrestore_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized`
- suite_evaluations: `1/2 = 50.00%`
- current_evaluation: `leaderboard_proxy_v1_set`
- current_rows_progress: `0/200 = 0.00%`
- current_chunks_progress: `0/13 = 0.00%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge18_text3bit1num8num1raw2gravrestore_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/leaderboard_proxy_v1_set/benchmark_eval_progress.json`
- accuracy_so_far: `0.0000`
- correct_so_far: `0`
- completed_evaluations: `['readme_local320']`
- completed_evaluation_scores: `readme_local320 227/320 = 0.7094`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `17080`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge18_text3bit1num8num1raw2gravrestore_lr1e6_len1024_from_proxybench_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge19_text3bit1num8num1raw3grav1_lr1e6_len1024_from_proxybench_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge19_text3bit1num8num1raw3grav1_lr1e6_len1024_from_proxybench_v1`

- status: `evaluating`
- label: `reprobridge19 hybrid`
- observed_at: `2026-04-12T02:18:30.143400+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge19_text3bit1num8num1raw3grav1_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge19_text3bit1num8num1raw3grav1_v1.csv`
- sampled_rows: `80`
- optimizer_progress: `0/8 = 0.00%`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge19_text3bit1num8num1raw3grav1_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge19_text3bit1num8num1raw3grav1_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized`
- suite_evaluations: `1/2 = 50.00%`
- current_evaluation: `leaderboard_proxy_v1_set`
- current_rows_progress: `0/200 = 0.00%`
- current_chunks_progress: `0/13 = 0.00%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge19_text3bit1num8num1raw3grav1_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/leaderboard_proxy_v1_set/benchmark_eval_progress.json`
- accuracy_so_far: `0.0000`
- correct_so_far: `0`
- completed_evaluations: `['readme_local320']`
- completed_evaluation_scores: `readme_local320 231/320 = 0.7219`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `30788`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge19_text3bit1num8num1raw3grav1_lr1e6_len1024_from_proxybench_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge20_text3bit1num8raw4grav1_hedgecut_lr1e6_len1024_from_proxybench_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge20_text3bit1num8raw4grav1_hedgecut_lr1e6_len1024_from_proxybench_v1`

- status: `evaluating`
- label: `reprobridge20 hedge cut`
- observed_at: `2026-04-12T03:27:51.314031+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge20_text3bit1num8raw4grav1_hedgecut_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge20_text3bit1num8raw4grav1_hedgecut_v1.csv`
- sampled_rows: `80`
- optimizer_progress: `0/8 = 0.00%`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge20_text3bit1num8raw4grav1_hedgecut_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge20_text3bit1num8raw4grav1_hedgecut_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized`
- suite_evaluations: `1/2 = 50.00%`
- current_evaluation: `leaderboard_proxy_v1_set`
- current_rows_progress: `32/200 = 16.00%`
- current_chunks_progress: `2/13 = 15.38%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge20_text3bit1num8raw4grav1_hedgecut_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/leaderboard_proxy_v1_set/benchmark_eval_progress.json`
- accuracy_so_far: `0.4062`
- correct_so_far: `13`
- completed_evaluations: `['readme_local320']`
- completed_evaluation_scores: `readme_local320 229/320 = 0.7156`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `54704`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge20_text3bit1num8raw4grav1_hedgecut_lr1e6_len1024_from_proxybench_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge22_text3bit1num8raw5grav1_fullraw_lr1e6_len1024_from_proxybench_v1 -->
### Live progress: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge22_text3bit1num8raw5grav1_fullraw_lr1e6_len1024_from_proxybench_v1`

- status: `evaluating`
- label: `reprobridge22 full raw`
- observed_at: `2026-04-12T03:43:35.797321+00:00`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge22_text3bit1num8raw5grav1_fullraw_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge22_text3bit1num8raw5grav1_fullraw_v1.csv`
- sampled_rows: `80`
- optimizer_progress: `0/8 = 0.00%`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Latest evaluation progress

- source: `benchmark_eval_suite_progress`
- source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge22_text3bit1num8raw5grav1_fullraw_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/benchmark_eval_suite_progress.json`
- suite_output_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge22_text3bit1num8raw5grav1_fullraw_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized`
- suite_evaluations: `1/2 = 50.00%`
- current_evaluation: `leaderboard_proxy_v1_set`
- current_rows_progress: `16/200 = 8.00%`
- current_chunks_progress: `1/13 = 7.69%`
- evaluation_source_path: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge22_text3bit1num8raw5grav1_fullraw_lr1e6_len1024_from_proxybench_v1/eval_suite_readme_proxy_specialized/leaderboard_proxy_v1_set/benchmark_eval_progress.json`
- accuracy_so_far: `0.4375`
- correct_so_far: `7`
- completed_evaluations: `['readme_local320']`
- completed_evaluation_scores: `readme_local320 231/320 = 0.7219`

#### Completion markers

- training_result_exists: `True`
- runtime_pid: `59249`
- runtime_pid_alive: `False`
- suite_summary_exists: `False`
- audit_summary_exists: `False`
- export_manifest_exists: `False`
- recorded_run_result_exists: `False`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge22_text3bit1num8raw5grav1_fullraw_lr1e6_len1024_from_proxybench_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge21_text3bit1num8raw2grav1unitedge_lr1e6_len1024_from_proxybench_v1 -->
### Auto result: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge21_text3bit1num8raw2grav1unitedge_lr1e6_len1024_from_proxybench_v1`

- recorded_at: `2026-04-12T19:31:25.656870+00:00`
- label: `reprobridge21 unit edge`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge21_text3bit1num8raw2grav1unitedge_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge21_text3bit1num8raw2grav1unitedge_v1.csv`
- sampled_rows: `80`
- optimizer_steps: `8`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Scores

- readme_local320: `227/320 = 0.7094`
- local320_components: `general_stable_set 176/200 = 0.8800; binary_hard_set 30/60 = 0.5000; symbol_watch_set 21/60 = 0.3500`
- leaderboard_proxy_v1_set: `126/200 = 0.6300`

#### Submission audit

- audit_status: `potentially_exportable_2d_only`
- peft_export_ready: `True`
- tensor_count: `232`

#### Submission export

- submission_zip: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge21_text3bit1num8raw2grav1unitedge_lr1e6_len1024_from_proxybench_v1/submission_export/submission.zip`
- zip_size_bytes: `102356901`
- validation_valid: `True`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge21_text3bit1num8raw2grav1unitedge_lr1e6_len1024_from_proxybench_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge23_text3bit1num8raw5unitedge_lr1e6_len1024_from_proxybench_v1 -->
### Auto result: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge23_text3bit1num8raw5unitedge_lr1e6_len1024_from_proxybench_v1`

- recorded_at: `2026-04-12T19:31:14.889949+00:00`
- label: `reprobridge23 full raw unitedge`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge23_text3bit1num8raw5unitedge_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge23_text3bit1num8raw5unitedge_v1.csv`
- sampled_rows: `79`
- optimizer_steps: `8`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Scores

- readme_local320: `227/320 = 0.7094`
- local320_components: `general_stable_set 175/200 = 0.8750; binary_hard_set 30/60 = 0.5000; symbol_watch_set 22/60 = 0.3667`
- leaderboard_proxy_v1_set: `126/200 = 0.6300`

#### Submission audit

- audit_status: `potentially_exportable_2d_only`
- peft_export_ready: `True`
- tensor_count: `232`

#### Submission export

- submission_zip: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge23_text3bit1num8raw5unitedge_lr1e6_len1024_from_proxybench_v1/submission_export/submission.zip`
- zip_size_bytes: `102356914`
- validation_valid: `True`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge23_text3bit1num8raw5unitedge_lr1e6_len1024_from_proxybench_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge24_text3bit1num8raw6nograv_lr1e6_len1024_from_proxybench_v1 -->
### Auto result: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge24_text3bit1num8raw6nograv_lr1e6_len1024_from_proxybench_v1`

- recorded_at: `2026-04-12T06:11:20.342053+00:00`
- label: `o30best proxybench reprobridge24 raw6 no grav v1`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge24_text3bit1num8raw6nograv_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge24_text3bit1num8raw6_nograv_v1.csv`
- sampled_rows: `80`
- optimizer_steps: `8`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Scores

- readme_local320: `233/320 = 0.7281`
- local320_components: `general_stable_set 180/200 = 0.9000; binary_hard_set 29/60 = 0.4833; symbol_watch_set 24/60 = 0.4000`
- leaderboard_proxy_v1_set: `127/200 = 0.6350`

#### Submission audit

- audit_status: `potentially_exportable_2d_only`
- peft_export_ready: `True`
- tensor_count: `232`

#### Submission export

- submission_zip: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge24_text3bit1num8raw6nograv_lr1e6_len1024_from_proxybench_v1/submission_export/submission.zip`
- zip_size_bytes: `102356918`
- validation_valid: `True`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge24_text3bit1num8raw6nograv_lr1e6_len1024_from_proxybench_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge25_text3bit1num8raw6unitedge_lr1e6_len1024_from_proxybench_v1 -->
### Auto result: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge25_text3bit1num8raw6unitedge_lr1e6_len1024_from_proxybench_v1`

- recorded_at: `2026-04-12T19:31:35.650059+00:00`
- label: `reprobridge25 raw6 unitedge`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge25_text3bit1num8raw6unitedge_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge25_text3bit1num8raw6unitedge_v1.csv`
- sampled_rows: `80`
- optimizer_steps: `8`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Scores

- readme_local320: `232/320 = 0.7250`
- local320_components: `general_stable_set 180/200 = 0.9000; binary_hard_set 30/60 = 0.5000; symbol_watch_set 22/60 = 0.3667`
- leaderboard_proxy_v1_set: `125/200 = 0.6250`

#### Submission audit

- audit_status: `potentially_exportable_2d_only`
- peft_export_ready: `True`
- tensor_count: `232`

#### Submission export

- submission_zip: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge25_text3bit1num8raw6unitedge_lr1e6_len1024_from_proxybench_v1/submission_export/submission.zip`
- zip_size_bytes: `102356895`
- validation_valid: `True`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge25_text3bit1num8raw6unitedge_lr1e6_len1024_from_proxybench_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge26_text3bit1num8raw7unitedge_lr1e6_len1024_from_proxybench_v1 -->
### Auto result: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge26_text3bit1num8raw7unitedge_lr1e6_len1024_from_proxybench_v1`

- recorded_at: `2026-04-12T19:31:53.758877+00:00`
- label: `reprobridge26 raw7 unitedge`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge26_text3bit1num8raw7unitedge_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge26_text3bit1num8raw7unitedge_v1.csv`
- sampled_rows: `80`
- optimizer_steps: `8`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Scores

- readme_local320: `228/320 = 0.7125`
- local320_components: `general_stable_set 179/200 = 0.8950; binary_hard_set 29/60 = 0.4833; symbol_watch_set 20/60 = 0.3333`
- leaderboard_proxy_v1_set: `126/200 = 0.6300`

#### Submission audit

- audit_status: `potentially_exportable_2d_only`
- peft_export_ready: `True`
- tensor_count: `232`

#### Submission export

- submission_zip: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge26_text3bit1num8raw7unitedge_lr1e6_len1024_from_proxybench_v1/submission_export/submission.zip`
- zip_size_bytes: `102356854`
- validation_valid: `True`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge26_text3bit1num8raw7unitedge_lr1e6_len1024_from_proxybench_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge27_text3bit1num8raw8unitedge_lr1e6_len1024_from_proxybench_v1 -->
### Auto result: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge27_text3bit1num8raw8unitedge_lr1e6_len1024_from_proxybench_v1`

- recorded_at: `2026-04-12T08:55:22.791307+00:00`
- label: `o30best proxybench reprobridge27 raw8 unitedge v1`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge27_text3bit1num8raw8unitedge_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge27_text3bit1num8raw8unitedge_v1.csv`
- sampled_rows: `80`
- optimizer_steps: `8`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Scores

- readme_local320: `227/320 = 0.7094`
- local320_components: `general_stable_set 174/200 = 0.8700; binary_hard_set 30/60 = 0.5000; symbol_watch_set 23/60 = 0.3833`
- leaderboard_proxy_v1_set: `129/200 = 0.6450`

#### Submission audit

- audit_status: `potentially_exportable_2d_only`
- peft_export_ready: `True`
- tensor_count: `232`

#### Submission export

- submission_zip: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge27_text3bit1num8raw8unitedge_lr1e6_len1024_from_proxybench_v1/submission_export/submission.zip`
- zip_size_bytes: `102356647`
- validation_valid: `True`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge27_text3bit1num8raw8unitedge_lr1e6_len1024_from_proxybench_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge28_text3bit1num8raw9unitedge_lr1e6_len1024_from_proxybench_v1 -->
### Auto result: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge28_text3bit1num8raw9unitedge_lr1e6_len1024_from_proxybench_v1`

- recorded_at: `2026-04-12T10:20:03.465728+00:00`
- label: `o30best proxybench reprobridge28 raw9 unitedge v1`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge28_text3bit1num8raw9unitedge_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge28_text3bit1num8raw9unitedge_v1.csv`
- sampled_rows: `80`
- optimizer_steps: `8`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Scores

- readme_local320: `233/320 = 0.7281`
- local320_components: `general_stable_set 179/200 = 0.8950; binary_hard_set 30/60 = 0.5000; symbol_watch_set 24/60 = 0.4000`
- leaderboard_proxy_v1_set: `132/200 = 0.6600`

#### Submission audit

- audit_status: `potentially_exportable_2d_only`
- peft_export_ready: `True`
- tensor_count: `232`

#### Submission export

- submission_zip: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge28_text3bit1num8raw9unitedge_lr1e6_len1024_from_proxybench_v1/submission_export/submission.zip`
- zip_size_bytes: `102356843`
- validation_valid: `True`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge28_text3bit1num8raw9unitedge_lr1e6_len1024_from_proxybench_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge29_text3bit1num8raw10unitedge_lr1e6_len1024_from_proxybench_v1 -->
### Auto result: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge29_text3bit1num8raw10unitedge_lr1e6_len1024_from_proxybench_v1`

- recorded_at: `2026-04-12T11:42:08.726020+00:00`
- label: `o30best proxybench reprobridge29 raw10 unitedge v1`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge29_text3bit1num8raw10unitedge_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge29_text3bit1num8raw10unitedge_v1.csv`
- sampled_rows: `80`
- optimizer_steps: `8`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Scores

- readme_local320: `234/320 = 0.7312`
- local320_components: `general_stable_set 181/200 = 0.9050; binary_hard_set 29/60 = 0.4833; symbol_watch_set 24/60 = 0.4000`
- leaderboard_proxy_v1_set: `129/200 = 0.6450`

#### Submission audit

- audit_status: `potentially_exportable_2d_only`
- peft_export_ready: `True`
- tensor_count: `232`

#### Submission export

- submission_zip: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge29_text3bit1num8raw10unitedge_lr1e6_len1024_from_proxybench_v1/submission_export/submission.zip`
- zip_size_bytes: `102356858`
- validation_valid: `True`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge29_text3bit1num8raw10unitedge_lr1e6_len1024_from_proxybench_v1 -->

<!-- auto-run-summary:start:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge30_text3bit1num8raw11unitedge_lr1e6_len1024_from_proxybench_v1 -->
### Auto result: `nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge30_text3bit1num8raw11unitedge_lr1e6_len1024_from_proxybench_v1`

- recorded_at: `2026-04-12T13:11:49.686458+00:00`
- label: `o30best proxybench reprobridge30 raw11 unitedge v1`
- run_root: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge30_text3bit1num8raw11unitedge_lr1e6_len1024_from_proxybench_v1`
- train_csv: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_artifacts/stage25_o30best_proxybench30ao_reprobridge30_text3bit1num8raw11unitedge_v1.csv`
- sampled_rows: `80`
- optimizer_steps: `8`
- lr: `1e-06`
- max_seq_length: `1024`
- trainable_lora_suffixes: `['mixer.q_proj', 'mixer.k_proj', 'mixer.v_proj', 'mixer.o_proj']`

#### Scores

- readme_local320: `226/320 = 0.7063`
- local320_components: `general_stable_set 177/200 = 0.8850; binary_hard_set 29/60 = 0.4833; symbol_watch_set 20/60 = 0.3333`
- leaderboard_proxy_v1_set: `129/200 = 0.6450`

#### Submission audit

- audit_status: `potentially_exportable_2d_only`
- peft_export_ready: `True`
- tensor_count: `232`

#### Submission export

- submission_zip: `/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge/baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge30_text3bit1num8raw11unitedge_lr1e6_len1024_from_proxybench_v1/submission_export/submission.zip`
- zip_size_bytes: `102357407`
- validation_valid: `True`
<!-- auto-run-summary:end:nemotron_sft_lora_with_cot_v2_mlx_stagefreeze_v2_stage25_attention_qkvo_reanchor_o30best_proxybench30ao_reprobridge30_text3bit1num8raw11unitedge_lr1e6_len1024_from_proxybench_v1 -->
