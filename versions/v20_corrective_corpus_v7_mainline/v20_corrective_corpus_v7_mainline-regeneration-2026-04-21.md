# v20 corrective corpus v7 mainline regeneration note (2026-04-21)

> Later update on 2026-04-21: the first tokenreuse rerun described in this note is superseded.
> `reuse_base_synthetic` was still source-mix-unaware at that point, so many intended `v6_binary_donor`
> and `v6_numeral_surface_donor` rows were silently overwritten by base synthetic token streams.
> The current source-aware audit and corrected bundle state are recorded in
> `versions/v20_corrective_corpus_v7_mainline/v20_corrective_corpus_v7_mainline-tokenstream-audit-2026-04-21.md`.

## Judgment

The historical `v7` measured run should **not** be treated as a clean confirmation or rejection of the intended v7 experiment idea.

The measured `0.80` run was produced from a generator path that retokenized the entire overlay phase, so it primarily measured a data-generation / token-stream regression rather than the intended `v4 public-safe base + narrow v6 donor` hypothesis.

## Confirmed issues

1. `versions/v20_corrective_corpus_v7_mainline/reproduce_v20_corrective_corpus_v7_mainline.py` rebuilt every overlay row from text.
2. That behavior differed from the effective `v4` / `v6` bundle construction path, where base synthetic token streams were reused when available.
3. The local workspace did not contain Git-managed `v4` / `v6` output artifacts, so those prerequisite overlays had to be regenerated first.
4. `versions/v20_corrective_corpus_v4_mainline/reproduce_v20_corrective_corpus_v4_mainline.py` also referenced a non-Git optional `v1` selection artifact and needed a resilience patch before regeneration.
5. The first tokenreuse rerun was also incomplete: token reuse was keyed only on `(problem_id, "synthetic.jsonl")`,
   so donor rows sharing a base-backed problem ID could still be replaced by the legacy base synthetic stream.

## Code changes applied

### v4 generator hardening

- File: `versions/v20_corrective_corpus_v4_mainline/reproduce_v20_corrective_corpus_v4_mainline.py`
- Change: added `read_csv_map_if_exists(...)` and downgraded missing `V1_SELECTION_PATH` from a hard failure to an empty optional input.
- Purpose: allow local regeneration of `v4_mainline_default` artifacts from repository-tracked sources plus the available `04-08-16-14` snapshot.

### v7 generator correction

- File: `versions/v20_corrective_corpus_v7_mainline/reproduce_v20_corrective_corpus_v7_mainline.py`
- Change: added explicit `--overlay-token-strategy` with supported values:
  - `reuse_base_synthetic`
  - `retokenize_all`
- Corrected behavior in the current generator is source-aware:
  - `v4_public_base` rows reuse `04-08-16-14/tokens/<problem_id>/synthetic.json` when present
  - `v6_binary_donor`, `v6_numeral_surface_donor`, and `v7_numeral_surface_synth` always use their own prompt/completion tokenization
- The overlay definition is now pinned instead of dynamically discovered:
  - binary donor IDs are fixed to the audited `9` IDs
  - numeral boxed-surface IDs are fixed to the audited `11` IDs
  - the only allowed synthetic row is the explicit `1542039b` backfill
  - any other missing donor/surface row now raises a hard failure
- `v4_public_base` metadata uses the canonical v4 bucket mapping for `assistant_style` / `supervision_role` because the upstream repeated v4 artifact omits those fields.
- Historical broken behavior is still representable explicitly as `--overlay-token-strategy retokenize_all`.

## Regenerated prerequisite artifacts

### v4

- command: `uv run python versions/v20_corrective_corpus_v4_mainline/reproduce_v20_corrective_corpus_v4_mainline.py --run-name v4_mainline_default`
- artifact root: `versions/v20_corrective_corpus_v4_mainline/outputs/v4_mainline_default/artifacts`
- regenerated rows: `318 unique`, `808 repeated`

### v6

- command: `uv run python versions/v20_corrective_corpus_v6_mainline/reproduce_v20_corrective_corpus_v6_mainline.py --run-name v6_mainline_default`
- artifact root: `versions/v20_corrective_corpus_v6_mainline/outputs/v6_mainline_default/artifacts`
- regenerated rows: `392 unique`, `673 repeated`

## Corrected v7 regeneration

### Command

`uv run python versions/v20_corrective_corpus_v7_mainline/reproduce_v20_corrective_corpus_v7_mainline.py --run-name v7_mainline_tokenreuse_repro --write-training-bundle --bundle-path A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v7_mainline_tokenreuse_bundle.jsonl --overlay-token-strategy reuse_base_synthetic`

### Output roots

- run root: `versions/v20_corrective_corpus_v7_mainline/outputs/v7_mainline_tokenreuse_repro`
- bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v7_mainline_tokenreuse_bundle.jsonl`

### Corrected mix confirmation

- `v4_public_base`: `808` repeated rows
- `v6_binary_donor`: `27` repeated rows
- `v6_numeral_surface_donor`: `10` repeated rows
- `v7_numeral_surface_synth`: `1` repeated row
- total: `338 unique`, `846 repeated`

### Token-stream construction result

- `overlay_token_strategy = reuse_base_synthetic`
- `overlay_reuse_scope = v4_public_base_only`
- `reused_base_synthetic_problem_count = 298`
- `retokenized_overlay_problem_count = 36`

Residual retokenized rows are the subset not backed by a reusable base synthetic segment in the `04-08-16-14` snapshot.

### Bundle footprint

- `base_examples = 7828`
- `overlay_examples = 846`
- `total_examples = 8674`
- `total_steps = 272`
- `total_tokens = 32869812`
- `max_seq_len = 7971`

## Current status

- The corrected v7 training bundle has been regenerated successfully.
- No new train / validation / proxy / leaderboard score is recorded yet for this corrected bundle.
- Therefore the only valid statement today is:
  - historical measured `v7` = broken retokenized-overlay run
  - corrected `v7_mainline_tokenreuse_repro` = ready for re-train / re-eval

## Recommended next action

Run the corrected bundle as a new measured branch and keep its score ledger separate from the historical broken `v7` score record.