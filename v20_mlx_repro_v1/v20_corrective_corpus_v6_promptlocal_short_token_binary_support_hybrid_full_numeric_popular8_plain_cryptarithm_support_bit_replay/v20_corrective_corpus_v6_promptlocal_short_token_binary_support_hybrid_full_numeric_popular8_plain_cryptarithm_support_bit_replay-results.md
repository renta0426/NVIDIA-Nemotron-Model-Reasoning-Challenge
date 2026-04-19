# v20 corrective corpus v6 promptlocal-short-token-binary-support-hybrid-full-numeric-popular8-plain-cryptarithm-support-bit-replay results

## Status

- Created: 2026-04-19 UTC
- Generator: `v20_mlx_repro_v1/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_replay/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_replay.py`
- Run name: `v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_replay_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_replay_mb1_nobc`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_replay_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python v20_mlx_repro_v1/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_replay/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_replay.py --run-name v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_replay_default --write-training-bundle` を current branch で実行し、`README.md` と `A-Open-ProgressPrizePublication/README.md` の deterministic / boxed-first 契約を保ったまま canonical checks を通して bundle 再生成に成功

## README-grounded purpose

- `A-Open-ProgressPrizePublication/README.md` の最大 upside slice である `bit_manipulation` を upper-bound 側でも再強化する
- cryptarithm support lane は維持しつつ、`v4` live partial の bit misses に対して **safe replay できる rows だけ** に extra repeat を積む

## Dataset composition

### Unique rows

- binary_structured_exact_core: 152
- binary_logic_exact: 56
- binary_permutation_exact: 40
- binary_prompt_local_exact: 95
- surface_numeral_boxed: 34
- surface_cipher_boxed: 6
- surface_unit_tail: 6
- surface_symbol_prefix: 4
- surface_binary_prompt_local_answer_only: 96
- surface_binary_structured_answer_only: 96
- surface_numeric_answer_only: 64
- surface_cryptarithm_answer_only: 48
- easy_gravity_fragile: 6
- total unique overlay problems: 703

### Repeated training rows

- binary_structured_exact_core: 624
- binary_logic_exact: 228
- binary_permutation_exact: 164
- binary_prompt_local_exact: 380
- surface_numeral_boxed: 102
- surface_cipher_boxed: 18
- surface_unit_tail: 18
- surface_symbol_prefix: 8
- surface_binary_prompt_local_answer_only: 288
- surface_binary_structured_answer_only: 292
- surface_numeric_answer_only: 192
- surface_cryptarithm_answer_only: 144
- easy_gravity_fragile: 18
- total repeated overlay rows: 2476

### Bundle footprint

- base examples: 7828
- overlay examples: 2476
- total examples: 10304
- total steps: 323
- total tokens: 28554475
- max sequence length: 7971

## Canonical validation

- passed: True
- binary max think lines: 4
- surface max think lines: 3
- mandatory anchor missing: 0
- binary non-verified contamination: 0
- surface unexpected categories: 0

## Bit measured replay lane

- replay source: `v20_mlx_v4_mainline_mb1_nobc` partial validation `544 / 950`
- safe replay として実際に押せる selected rows は **5 件**
- 内訳は structured exact **3 件** (`02a66bcb`, `053f87d3`, `0b56b953`) と structured answer-only support **2 件** (`04d8c3e6`, `06120e47`)
- replay bonus は `+2 repeats`
- exact 側では `exact_rule_commit_boost` / `exact_closure_commit_boost`、support 側では `surface_boxed_tail_boost` / `surface_short_closure_boost` として manifest に現れる

## Full support budget snapshot

- prompt-local support: **96 unique / 288 repeated**
- structured support: **96 unique / 292 repeated**
- numeric support: **64 unique / 192 repeated**
- cryptarithm support: **48 unique / 144 repeated**
- overlay token share は structured exact `0.3007`、prompt-local support `0.1244`、structured support `0.1316`、numeric `0.0408`、cryptarithm `0.0277`

## Delta vs full cryptarithm support base

- `hybrid_full_numeric_popular8_plain_cryptarithm_support` 比で overlay rows は `2466 -> 2476`
- total tokens は `28551534 -> 28554475` で **`+2941`**
- 増分はほぼ **bit replay bonus rows** に対応している

## Interpretation before training

- upper-bound 側では support volume 自体はすでに大きいので、この branch は **volume 追加ではなく targeted replay** のテスト
- README の bit-heavy worldview を維持しつつ、unsafe teacher rows は入れずに replay だけ強めている

## Next evaluation gate

- `hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_replay` / `hybrid_full_numeric_popular8_plain_cryptarithm_support` / `hybrid_full_numeric_mixed` を比較し、upper-bound 側で replay bonus が実利を持つかを見る
