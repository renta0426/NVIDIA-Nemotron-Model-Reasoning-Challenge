# v20 corrective corpus v7 mainline bundle-to-bundle audit (2026-04-21)

## Scope

- README basis: `README.md`
- Reference bundles:
  - `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v4_mainline_bundle.jsonl`
  - `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_mainline_bundle.jsonl`
- Audited target bundle:
  - `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v7_mainline_tokenreuse_bundle.jsonl`
- Related generator:
  - `versions/v20_corrective_corpus_v7_mainline/reproduce_v20_corrective_corpus_v7_mainline.py`

## Why this audit was needed

The earlier v7 audit established that the current tokenreuse bundle is source-aware and no longer overwrites donor rows with base synthetic tokens.

After restoring the historical v4 and v6 single-file training bundles, the remaining question was stricter:

1. Does the `v7` base partition still match the restored v4/v6 bundles exactly?
2. Is the `v4_public_base` lane in `v7` truly the same supervision as the restored `v4` bundle?
3. Are the `v6_binary_donor` and `v6_numeral_surface_donor` rows in `v7` truly a subset of the restored `v6` bundle?
4. Is the only non-v4/non-v6 row still the explicit `1542039b` synthetic backfill?

## Manifest-level observations

- Restored `v4` bundle:
  - `base_examples = 7828`
  - `overlay_examples = 808`
  - no `overlay_token_strategy` field
- Restored `v6` bundle:
  - `base_examples = 7828`
  - `overlay_examples = 673`
  - no `overlay_token_strategy` field
- Current strict `v7` bundle:
  - `base_examples = 7828`
  - `overlay_examples = 846`
  - `overlay_token_strategy = reuse_base_synthetic`
  - `overlay_reuse_scope = v4_public_base_only`
  - `pinned_binary_donor_ids = 9`
  - `pinned_numeral_surface_ids = 11`
  - `explicit_synthetic_numeral_ids = [1542039b]`

So at the manifest level, the restored bundles are consistent with the current strict v7 interpretation:

- v7 overlay = `808` inherited v4 rows + `37` v6 donor rows + `1` explicit synth row.

## Base partition comparison

Using a multiset keyed by:

- `source_problem_id`
- `segment`
- `category`
- `num_loss_tokens`
- token digest
- mask digest

the base partitions were compared directly.

### Result

- `v4 base` vs `v7 base`: `0 missing`, `0 extra`
- `v6 base` vs `v7 base`: `0 missing`, `0 extra`

Conclusion: the restored `v4`, restored `v6`, and current strict `v7` all share the exact same `7828` base snapshot examples.

## v4 overlay vs v7 v4_public_base lane

### Token-level comparison

Using a multiset keyed by:

- `source_problem_id`
- `num_loss_tokens`
- token digest
- mask digest

the restored `v4` overlay was compared against the `v7` rows with `source_mix = v4_public_base`.

### Result

- restored `v4` overlay count: `808`
- `v7 v4_public_base` count: `808`
- token-level missing: `0`
- token-level extra: `0`

Conclusion: the `v4_public_base` lane in the current strict `v7` bundle preserves the restored `v4` overlay token streams exactly.

### Metadata differences

The two bundles are not metadata-identical, but the differences are expected and non-semantic.

- restored `v4` bundle rows have empty `assistant_style` / `supervision_role`
- current `v7 v4_public_base` rows populate those fields via the canonical v4 bucket mapping
- sample restored `v4` source tags contain `v1_selected`
- corresponding `v7` rows replace that terminal provenance tag with `v4_public_base`

These are audit/provenance enrichment differences, not training-token differences.

## v6 donor subset vs v7 donor rows

The restored `v6` overlay was filtered down to the pinned donor reference set:

- binary donor IDs: `9`
- numeral boxed-surface IDs present in restored v6: `10`
- total reference rows: `37`

The current strict `v7` donor rows were then collected from:

- `source_mix = v6_binary_donor`: `27` rows
- `source_mix = v6_numeral_surface_donor`: `10` rows

### Semantic comparison

Using a multiset keyed by:

- `source_problem_id`
- `category`
- `assistant_style`
- `supervision_role`
- `selection_tier`
- `template_subtype`
- `teacher_solver_candidate`
- `proxy_failed`
- `validation_failed`
- `num_loss_tokens`
- token digest
- mask digest

the restored `v6` donor reference subset was compared against the `v7` donor rows.

### Result

- restored `v6` donor reference rows: `37`
- `v7` donor rows: `37`
- semantic missing: `0`
- semantic extra: `0`

Conclusion: all `37` donor rows in the current strict `v7` bundle are semantically identical to rows that already exist in the restored `v6` bundle.

### Metadata delta

As with `v4_public_base`, the `v7` donor rows enrich provenance tags.

- restored `v6` donor rows keep their original `source_tags`
- corresponding `v7` donor rows append lane provenance such as `v6_binary_donor`

Again, this is expected provenance enrichment rather than a token-level change.

## Explicit synth row check

The current strict `v7` bundle contains:

- `v7_numeral_surface_synth = 1`

That row is the explicit `1542039b` synthetic numeral backfill.

### Result

- synth row count in `v7`: `1`
- semantic presence of that row in restored `v6` overlay: `0`

Conclusion: the only row in strict `v7` that does not come directly from restored `v4` or restored `v6` is the pinned explicit synthetic backfill `1542039b`.

## Final judgment

Using the restored single-file bundles as the reference source:

1. The base partition of current strict `v7` matches restored `v4` and restored `v6` exactly.
2. The `v4_public_base` lane in current strict `v7` matches restored `v4` exactly at the token-stream level.
3. The `v6_binary_donor` and `v6_numeral_surface_donor` rows in current strict `v7` are an exact semantic subset of restored `v6`.
4. The only non-v4/non-v6 row in current strict `v7` is the explicitly pinned synthetic row `1542039b`.

Therefore, after adding restored `v4` / `v6` bundles as references, the current strict `v7` bundle remains faithful to the intended experiment definition.

The only differences relative to restored `v4` / `v6` are:

- expected provenance enrichment (`source_mix`, enriched `source_tags`)
- canonical metadata filling for `v4_public_base`
- the single explicit synthetic numeral backfill `1542039b`