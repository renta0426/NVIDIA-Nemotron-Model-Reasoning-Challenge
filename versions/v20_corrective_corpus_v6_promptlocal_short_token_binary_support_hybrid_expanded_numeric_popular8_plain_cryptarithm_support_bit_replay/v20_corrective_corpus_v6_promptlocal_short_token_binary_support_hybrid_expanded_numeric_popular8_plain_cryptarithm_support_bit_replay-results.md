# v20 corrective corpus v6 promptlocal-short-token-binary-support-hybrid-expanded-numeric-popular8-plain-cryptarithm-support-bit-replay results

## Status

- Created: 2026-04-19 UTC
- Generator: `versions/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_replay/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_replay.py`
- Run name: `v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_replay_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_replay_mb1_nobc`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_replay_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python versions/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_replay/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_replay.py --run-name v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_replay_default --write-training-bundle` を current branch で実行し、`README.md` と `A-Open-ProgressPrizePublication/README.md` の deterministic / boxed-first 契約を保ったまま canonical checks を通して bundle 再生成に成功

## README-grounded purpose

- `A-Open-ProgressPrizePublication/README.md` は `bit_manipulation` を最大の上振れ余地と位置づけている
- `versions/v20_corrective_corpus_v4_mainline/v20_corrective_corpus_v4_mainline-results.md` の live partial でも、主失点は `bit_manipulation 17 miss` と `cryptarithm_deduce 36 miss`
- cryptarithm support lane は前 branch で追加済みなので、この branch では **bit side の replay pressure** を上げる
- ただし teacher-correct を崩さないため、`v4` partial miss IDs のうち **safe replay できる selected rows のみ** に extra repeat を載せる

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
- surface_binary_structured_answer_only: 64
- surface_numeric_answer_only: 64
- surface_cryptarithm_answer_only: 48
- easy_gravity_fragile: 6
- total unique overlay problems: 671

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
- surface_binary_structured_answer_only: 196
- surface_numeric_answer_only: 192
- surface_cryptarithm_answer_only: 144
- easy_gravity_fragile: 18
- total repeated overlay rows: 2380

### Bundle footprint

- base examples: 7828
- overlay examples: 2380
- total examples: 10208
- total steps: 320
- total tokens: 28526123
- max sequence length: 7971

## Canonical validation

- passed: True
- binary max think lines: 4
- surface max think lines: 3
- mandatory anchor missing: 0
- binary non-verified contamination: 0
- surface unexpected categories: 0

## Bit measured replay lane

- replay source: `v20_mlx_v4_mainline_mb1_nobc` partial validation `544 / 950` 時点の bit misses
- current partial miss `17` 件のうち、この branch で **safe replay として実際に押せる selected rows は 5 件**
- 内訳は **structured exact 3 件** (`02a66bcb`, `053f87d3`, `0b56b953`) と **structured answer-only support 2 件** (`04d8c3e6`, `06120e47`)
- replay bonus は `+2 repeats`。binary exact 側は `exact_rule_commit_boost` / `exact_closure_commit_boost`、support 側は `surface_boxed_tail_boost` / `surface_short_closure_boost` として追加
- overlay 増分は `hybrid_expanded_numeric_popular8_plain_cryptarithm_support` 比で **`2370 -> 2380` rows**, **`28523182 -> 28526123` tokens**

## Support budget snapshot

- prompt-local support: **96 unique / 288 repeated**
- structured support: **64 unique / 196 repeated**
- numeric support: **64 unique / 192 repeated**
- cryptarithm support: **48 unique / 144 repeated**
- overlay token share は structured exact `0.3037`、prompt-local support `0.1258`、structured support `0.0919`、numeric `0.0412`、cryptarithm `0.0280`

## Interpretation before training

- これは support lane をさらに増やす branch ではなく、`v4` live partial が示した **bit exact failures の一部を extra repeat で再押し**する branch
- README の bit 主導仮説を保ちつつ、teacher-correct な replay だけに限定しているため、unsafe な exact row 再注入は避けている

## Next evaluation gate

- `hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_replay` / `hybrid_expanded_numeric_popular8_plain_cryptarithm_support` / `hybrid_expanded_numeric_popular8_plain` を比較し、bit replay bonus が public-relevant side に寄るかを measured diff-pack で判定する
