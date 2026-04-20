# v20 corrective corpus v6 promptlocal-short-token-binary-support-hybrid-expanded-numeric-popular8-plain-cryptarithm-support results

## Status

- Created: 2026-04-19 UTC
- Generator: `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support.py`
- Run name: `v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_mb1_nobc`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support.py --run-name v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_default --write-training-bundle` を current branch で実行し、`README.md` と `A-Open-ProgressPrizePublication/README.md` の deterministic / boxed-first 契約を保ったまま canonical checks を通して bundle 再生成に成功
- Branch purpose: `hybrid_expanded_numeric_popular8_plain` の popular8-first numeric coverage を維持しつつ、README が指摘する cryptarithm の split / concat weakness に合わせて `glyph_len5` answer-only support lane を追加し、numeric boost ではなく cryptarithm glyph stabilization へ予算を振り直す branch

## README-grounded motivation

- `A-Open-ProgressPrizePublication/README.md` では cryptarithm について **split / concatenation** が Nemotron の弱点と明示されている
- 同 README では cryptarithm 自体の target solve rate は低いが、記号表面を正確に扱うこと自体は final leaderboard で重要な基礎能力だと整理されている
- `versions/v20_corrective_corpus_v4_mainline/v20_corrective_corpus_v4_mainline-results.md` の live MLX partial でも、主失点は `bit_manipulation` と `cryptarithm_deduce` に寄っていた
- したがって今回は numeric lane をこれ以上 boost せず、`glyph_len5` answer-only pool を separate support lane として切り出して cryptarithm glyph surface を補強する

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

- binary_structured_exact_core: 618
- binary_logic_exact: 228
- binary_permutation_exact: 164
- binary_prompt_local_exact: 380
- surface_numeral_boxed: 102
- surface_cipher_boxed: 18
- surface_unit_tail: 18
- surface_symbol_prefix: 8
- surface_binary_prompt_local_answer_only: 288
- surface_binary_structured_answer_only: 192
- surface_numeric_answer_only: 192
- surface_cryptarithm_answer_only: 144
- easy_gravity_fragile: 18
- total repeated overlay rows: 2370

### Bundle footprint

- base examples: 7828
- overlay examples: 2370
- total examples: 10198
- total steps: 320
- total tokens: 28523182
- max sequence length: 7971

## Canonical validation

- passed: True
- binary max think lines: 4
- surface max think lines: 3
- mandatory anchor missing: 0
- binary non-verified contamination: 0
- surface unexpected categories: 0

## Cryptarithm support lane

- `surface_cryptarithm_answer_only` は **48 unique / 144 repeated**
- unique 配分は **`cryptarithm_deduce 36` + `cryptarithm_guess 12`**
- selected notes は `symbol_glyph_grouped_exact_answer_only 36` と `symbol_glyph_training_answer_only 12` が中心
- overlay tokens は `19281`、overlay token share は **`0.0281`**
- support completion は glyph mapping / grouping / ordering exactness を明示し、surface style は `surface_boxed_tail` / `surface_short_closure` / `surface_token_skill` の plain 3-style のみ

## Support budget rebalance

- prompt-local support: **96 unique / 288 repeated**
- structured support: **64 unique / 192 repeated**
- numeric support: **64 unique / 192 repeated**
- cryptarithm support: **48 unique / 144 repeated**
- overlay token share は prompt-local `0.1263`、structured `0.0904`、numeric `0.0414`、cryptarithm `0.0281`
- combined answer-only support share は **`0.2862`**

## Delta vs expanded plain base

- `hybrid_expanded_numeric_popular8_plain` 比で overlay rows は `2226 -> 2370`
- total tokens は `28502373 -> 28523182` で **`+20809`**
- numeric lane は不変 (`64 unique / 192 repeated`) のまま、増分の中心は **cryptarithm support 144 rows / 19281 tokens**

## Interpretation before training

- これは numeric boost を戻す branch ではなく、popular8-first numeric coverage を維持したまま **glyph_len5 split/concat stabilization** を追加した再配分 branch
- cryptarithm は README 上でも難所だが、今回は hard reasoning を teach するのではなく、answer-only support として symbol surface を崩さない方向へ寄せている

## Next evaluation gate

- `hybrid_expanded_numeric_popular8_plain_cryptarithm_support` と `hybrid_expanded_numeric_popular8_plain` を measured diff-pack で比較し、numeric boost を減らした budget を cryptarithm glyph support に回す方が hidden leaderboard 寄りかを判定する
