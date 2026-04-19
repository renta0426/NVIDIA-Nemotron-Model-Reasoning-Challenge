# v20 corrective corpus v6 promptlocal-short-token-binary-support-hybrid-full-numeric-popular8-plain-cryptarithm-support results

## Status

- Created: 2026-04-19 UTC
- Generator: `v20_mlx_repro_v1/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support.py`
- Run name: `v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_mb1_nobc`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python v20_mlx_repro_v1/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support.py --run-name v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_default --write-training-bundle` を current branch で実行し、`README.md` と `A-Open-ProgressPrizePublication/README.md` の deterministic / boxed-first 契約を保ったまま canonical checks を通して bundle 再生成に成功
- Branch purpose: `hybrid_full_numeric_popular8_plain` の full dual bit support を維持しつつ、README の cryptarithm split / concat weakness に合わせて `glyph_len5` answer-only support lane を追加し、upper-bound 側でも numeric boost ではなく cryptarithm glyph stabilization へ予算を振り直す branch

## README-grounded motivation

- `A-Open-ProgressPrizePublication/README.md` では cryptarithm は chain-of-thought 自体が難しい一方、**symbols の split / concatenation が弱い**ことが明示されている
- 同 README は、easy task での `\boxed{}` surface failure や symbol conversion failure が leaderboard を削ることも強く示している
- そこで full dual bit support を維持したまま、hard reasoning ではなく **glyph surface exactness** の support lane を追加する

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

- binary_structured_exact_core: 618
- binary_logic_exact: 228
- binary_permutation_exact: 164
- binary_prompt_local_exact: 380
- surface_numeral_boxed: 102
- surface_cipher_boxed: 18
- surface_unit_tail: 18
- surface_symbol_prefix: 8
- surface_binary_prompt_local_answer_only: 288
- surface_binary_structured_answer_only: 288
- surface_numeric_answer_only: 192
- surface_cryptarithm_answer_only: 144
- easy_gravity_fragile: 18
- total repeated overlay rows: 2466

### Bundle footprint

- base examples: 7828
- overlay examples: 2466
- total examples: 10294
- total steps: 323
- total tokens: 28551534
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
- selected notes は `symbol_glyph_grouped_exact_answer_only 36` と `symbol_glyph_training_answer_only 12`
- overlay tokens は `19281`、overlay token share は **`0.0270`**
- surface styles は plain 3-style only で、glyph mapping / ordering / grouping exactness を明示する

## Full support budget rebalance

- prompt-local support: **96 unique / 288 repeated**
- structured support: **96 unique / 288 repeated**
- numeric support: **64 unique / 192 repeated**
- cryptarithm support: **48 unique / 144 repeated**
- overlay token share は prompt-local `0.1213`、structured `0.1265`、numeric `0.0397`、cryptarithm `0.0270`
- combined answer-only support share は **`0.3145`**

## Delta vs full plain base

- `hybrid_full_numeric_popular8_plain` 比で overlay rows は `2322 -> 2466`
- total tokens は `28530722 -> 28551534` で **`+20812`**
- numeric lane は不変 (`64 unique / 192 repeated`) のまま、増分の中心は **cryptarithm support 144 rows / 19281 tokens**

## Interpretation before training

- これは full support upper-bound に **glyph_len5 cryptarithm surface lane** を追加した branch
- numeric boost は戻しておらず、popular8-first numeric coverage を維持したまま cryptarithm symbol stability を別 lane として加えている
- upper-bound 側で効くなら、README が示した split / concat weakness を support tuning だけでもある程度補える可能性がある

## Next evaluation gate

- `hybrid_full_numeric_popular8_plain_cryptarithm_support` / `hybrid_full_numeric_popular8_plain` / `hybrid_full_numeric_mixed` の diff-pack と 950 validation を比較し、upper-bound 側で cryptarithm glyph support が実利を持つかを見る
