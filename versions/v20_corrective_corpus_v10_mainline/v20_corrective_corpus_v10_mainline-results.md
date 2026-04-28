# v20_corrective_corpus_v10_mainline

- created_at: 2026-04-23T14:20:36+00:00
- strategy note: versions/v10_bit_mainline_strategy_2026-04-23.md
- README basis: deterministic boxed-answer evaluation, bit_manipulation primary weighting, token-aware supervision, and token-first bundle construction.
- status: bundle generated; model score not yet measured.
- MLX launch note: this bundle is now the active queued mainline candidate behind the remaining `v8 broadbase` run. A detached single-file `queue-managed-run` plus dedicated `watch-progress-ledger` / `watch-score-publish` workers were started under `v20_mlx_repro_v1/outputs/v10/queue/`; after the manual `symbol` stop, the queue now sees `active=1` and is waiting only for a completed predecessor result (`any_ready=0`) before launch.
- eval gate note: the single-file runner now replays a `stratified_category_8_of_950` smoke validation into `adapter_validation_smoke8_snapshot/` before the README-contract local300 run, and only proceeds to full validation when prediction health is not obviously broken.
- runtime status: `queued`
- latest observed step: `not started`
- retained checkpoints: `none`
- local300 score: TBD

## Strategy

- Keep the v4 public-safe backbone token-safe.
- Reuse the pinned v6 binary donor pack narrowly, not as the mainline base.
- Add a verified/manual BIT frontier pack around persistent hard-core and anti-default1 rows.
- Restore v6-level symbol-prefix and easy-family guardrails without reviving broad symbol or matching lanes.

## Selection

- selected_unique_rows: 568
- selected_repeated_rows: 811
- overlay_token_strategy: reuse_base_synthetic

### Unique rows by bucket

- binary_logic_donor_exact: 2
- binary_logic_exact: 40
- binary_manual_frontier: 24
- binary_other_light: 64
- binary_permutation_donor_exact: 2
- binary_permutation_exact: 24
- binary_prompt_local_exact: 24
- binary_structured_core: 176
- binary_structured_donor_exact: 5
- binary_structured_exact_core: 96
- easy_gravity_fragile: 12
- easy_gravity_fragile_donor: 6
- surface_cipher_boxed: 8
- surface_cipher_boxed_donor: 6
- surface_cryptarithm_boxed: 12
- surface_numeral_boxed: 37
- surface_numeral_boxed_donor: 10
- surface_symbol_prefix: 2
- surface_symbol_prefix_donor: 4
- surface_unit_tail: 8
- surface_unit_tail_donor: 6

### Repeated rows by source mix

- v10_manual_frontier: 48
- v10_numeral_surface_synth: 1
- v10_verified_frontier: 385
- v4_public_base: 318
- v6_binary_donor: 27
- v6_cipher_guardrail_donor: 6
- v6_gravity_guardrail_donor: 6
- v6_numeral_surface_donor: 10
- v6_symbol_prefix_donor: 4
- v6_unit_guardrail_donor: 6

## Validation

- passed: True
- errors: []
- missing_watchlist_ids: []
- frontier_watchlist_hits: ['012fb81b', '01e09228', '0520a6ec', '069dbaab', '0a50c4a8', '0dd5caf4', '101410e4', '12154247', '12fd5b6c', '13009e35', '13c8ae90', '1532c0d1', '17fd9612', '2230fad0', '257e7158', '26a70ae0', '2d790c98', '59c78e51', '8e5d6fe6', 'a6192d29', 'b9500f41', 'c30a782a', 'fa67da07']

## Bundle

- path: A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v10_mainline_bundle.jsonl
- base_examples: 7828
- overlay_examples: 811
- total_examples: 8639
- total_tokens: 29885798
- max_seq_len: 7971
- reused_base_synthetic_problem_count: 298
- retokenized_overlay_problem_count: 254
