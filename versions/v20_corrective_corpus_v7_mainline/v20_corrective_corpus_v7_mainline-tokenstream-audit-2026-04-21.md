# v20 corrective corpus v7 mainline token-stream audit (2026-04-21)

## Scope

- README basis: `README.md`
- Strategy docs: `versions/v20_to_088_reassessment_2026-04-18.md`, `versions/v20_corrective_corpus_v7_mainline/v20_corrective_corpus_v7_mainline-results.md`, `A-Open-ProgressPrizePublication/v20_to_088_strategy.md`
- Generator audited: `versions/v20_corrective_corpus_v7_mainline/reproduce_v20_corrective_corpus_v7_mainline.py`
- Audited bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v7_mainline_tokenreuse_bundle.jsonl`
- Audited overlay artifacts: `versions/v20_corrective_corpus_v7_mainline/outputs/v7_mainline_tokenreuse_repro/artifacts/`

## Intended v7 strategy

From the README contract and the v7 reassessment notes, the intended v7 idea is narrow and specific:

1. Keep the `v4` public-safe overlay as the base supervision manifold.
2. Add only the measured `v6` binary donor rows that were supposed to repair binary regressions.
3. Add boxed-surface reinforcement for the `v6` numeral no-box failures.
4. Avoid broad new symbol or cryptarithm expansion.

This means v7 is not supposed to be a broad new corpus. It is supposed to preserve `v4` behavior and inject only a small donor lane.

## Pinned overlay definition

The current generator no longer discovers donor rows dynamically.

- The binary donor set is pinned to the `9` audited IDs recorded in the v7 results note.
- The numeral boxed-surface set is pinned to the `11` audited IDs recorded in the v7 results note.
- The only allowed synthetic row is the explicit `1542039b` numeral backfill.
- Any other missing donor row now causes a hard failure instead of silent backfill.
- `v4_public_base` keeps a canonical metadata mapping for `assistant_style` / `supervision_role` because the upstream repeated v4 artifact omits those per-row fields.

This removes the remaining experiment drift from general fallback behavior.

## Two invalid v7 states

### 1. Historical measured v7

The historical `0.80` run is not a clean measurement of the intended idea.

- The generator path effectively behaved like `retokenize_all`.
- The overlay diverged from the `v4` public-safe token stream from the first overlay batch.
- The measured collapse therefore mixed the intended donor hypothesis with a token-stream reconstruction bug.

### 2. First tokenreuse rerun

The first `v7_mainline_tokenreuse_repro` bundle was also invalid.

- `reuse_base_synthetic` reused the base synthetic segment for any overlay row whose `(problem_id, "synthetic.jsonl")` existed in the base snapshot.
- Because many donor rows shared problem IDs with `v4_public_base`, the intended donor traces were silently replaced by legacy base synthetic token streams.
- The donor metadata survived, but the actual training tokens were wrong.

That state did not satisfy the intended v7 strategy either. It mostly duplicated old base traces instead of injecting the measured donor supervision.

## Source-aware fix applied

The current generator was patched so that under `--overlay-token-strategy reuse_base_synthetic`:

- `v4_public_base` rows may reuse base synthetic tokens when the base snapshot has a backing segment.
- `v6_binary_donor` rows always use their own prompt/completion tokenization.
- `v6_numeral_surface_donor` rows always use their own prompt/completion tokenization.
- `v7_numeral_surface_synth` rows always use their own prompt/completion tokenization.
- donor row selection is pinned rather than recomputed from mutable proxy CSVs.
- general synthetic backfill is disabled; only the explicit `1542039b` row is allowed.

This makes reuse source-aware instead of problem-ID-only.

## Regenerated source-aware bundle

### Command

`uv run python versions/v20_corrective_corpus_v7_mainline/reproduce_v20_corrective_corpus_v7_mainline.py --run-name v7_mainline_tokenreuse_repro --write-training-bundle --bundle-path A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v7_mainline_tokenreuse_bundle.jsonl --overlay-token-strategy reuse_base_synthetic`

### Overlay mix

- `v4_public_base`: `808` repeated rows
- `v6_binary_donor`: `27` repeated rows
- `v6_numeral_surface_donor`: `10` repeated rows
- `v7_numeral_surface_synth`: `1` repeated row
- total repeated rows: `846`

### Bundle token construction stats

- `overlay_token_strategy = reuse_base_synthetic`
- `overlay_reuse_scope = v4_public_base_only`
- `reused_base_synthetic_example_count = 768`
- `retokenized_overlay_example_count = 78`
- `retokenized_overlay_by_source_mix`:
  - `v4_public_base = 40`
  - `v6_binary_donor = 27`
  - `v6_numeral_surface_donor = 10`
  - `v7_numeral_surface_synth = 1`
- `retokenized_overlay_problem_count = 36`

The `reused_base_synthetic_problem_count = 298` still contains donor problem IDs when those IDs also appear in the `v4_public_base` lane. That count is correct but should be interpreted as "problem IDs with at least one reused v4 example", not as "donor rows reused base tokens".

## Token-level verification

The regenerated bundle was compared against:

1. the exact tokenization of each overlay row's own prompt/completion text
2. the base snapshot synthetic token stream for the same `problem_id`

### Result summary

- `matches_expected_by_source_mix`
  - `v4_public_base = 40`
  - `v6_binary_donor = 27`
  - `v6_numeral_surface_donor = 10`
  - `v7_numeral_surface_synth = 1`
- `matches_base_by_source_mix`
  - `v4_public_base = 768`
- `differs_base_by_source_mix`
  - `v4_public_base = 40`
  - `v6_binary_donor = 27`
  - `v6_numeral_surface_donor = 10`
  - `v7_numeral_surface_synth = 1`

Interpretation:

- All `27 / 27` binary donor examples now match their intended donor tokenization.
- All `10 / 10` numeral donor examples now match their intended donor tokenization.
- The single synthetic numeral backfill row also matches its intended tokenization.
- No non-`v4_public_base` overlay row matches the base synthetic token stream anymore.
- The only reused base tokens are the intended `v4_public_base` examples.

### Donor collapse check

For the binary donor problem IDs, the non-v4 rows were checked for distinct token streams per assistant style.

- `0520a6ec`, `0a50c4a8`, `0dd5caf4`, `17fd9612`, `59c78e51`, `8e5d6fe6`, `b9500f41`, `c30a782a` now each have `3` non-v4 rows with `3` distinct token sequences.
- `fa67da07` has `3` non-v4 rows with `2` distinct token sequences, which is consistent with two donor styles sharing the same concrete text rather than with base-token collapse.

This directly resolves the earlier donor-collapse failure mode.

## Current judgment

### Historical measured v7

- still invalid as a clean read of the intended hypothesis
- it measured a retokenized-overlay failure mode

### First tokenreuse rerun

- also invalid
- it measured source-mix-unaware donor overwrite

### Current regenerated bundle

- now satisfies the intended v7 token-construction and row-selection strategy
- no longer exhibits the same donor-overwrite bug
- no longer contains general fallback behavior that can broaden the overlay definition
- still has no new train / validation / proxy / public score attached to it

So the correct status is:

- historical `v7 = invalid measurement`
- first tokenreuse rerun `= invalid bundle`
- current source-aware tokenreuse bundle `= structurally valid and ready for re-train / re-eval`

## Practical implication

Any future v7 or v8-like branch that mixes inherited public-safe rows with donor rows must treat token reuse as source-aware.

Problem-ID-only reuse is unsafe whenever donor rows intentionally change the teacher trace for an already base-backed problem.

For direct bundle references against the restored `v4` / `v6` single-file bundles, see `versions/v20_corrective_corpus_v7_mainline/v20_corrective_corpus_v7_mainline-bundle-to-bundle-audit-2026-04-21.md`.
