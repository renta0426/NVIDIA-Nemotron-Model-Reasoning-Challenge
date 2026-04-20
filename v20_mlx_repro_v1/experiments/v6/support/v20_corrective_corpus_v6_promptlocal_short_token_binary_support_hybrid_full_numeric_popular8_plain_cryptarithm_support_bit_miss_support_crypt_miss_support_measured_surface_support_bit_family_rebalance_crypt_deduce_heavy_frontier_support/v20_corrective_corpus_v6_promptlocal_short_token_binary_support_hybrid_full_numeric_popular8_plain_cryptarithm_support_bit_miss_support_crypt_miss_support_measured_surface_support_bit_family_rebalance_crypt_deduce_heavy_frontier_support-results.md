# v20 corrective corpus v6 promptlocal-short-token-binary-support-hybrid-full-numeric-popular8-plain-cryptarithm-support-bit-miss-support-crypt-miss-support-measured-surface-support-bit-family-rebalance-crypt-deduce-heavy-frontier-support results

## Status

- Created: 2026-04-19 UTC
- Generator: `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_deduce_heavy_frontier_support/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_deduce_heavy_frontier_support.py`
- Run name: `v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_deduce_heavy_frontier_support_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_deduce_heavy_frontier_support_mb1_nobc`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_deduce_heavy_frontier_support_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python ...bit_family_rebalance_crypt_deduce_heavy_frontier_support.py --write-training-bundle` で canonical checks を通して bundle 再生成に成功
- Queue note (2026-04-20): OOM を避けつつ full-budget 比較を維持するため、この full frontier-support run は expanded frontier-support run の `training_result.json` 出現と train process 終了を待ってから、`v20_mlx_repro_v1/outputs/v6/support` 配下で fresh relaunch する detached queue に設定した
- Eval automation note (2026-04-20): grouped support root 向けに `training_result.json` 出現後の adapter-validation watcher と `postprocess-run --postprocess-eval-kind adapter-validation` watcher を追加し、train 完了後に README 契約の validation を自動起動する
- Queue refresh note (2026-04-20): old frontier queue process が見えなかったため、`outputs/v6/support/.../train_watch.log` に skip-aware full-run queue を再配置し、expanded frontier-support の `training_result.json` 完了後だけ full train を launch するよう更新した

## README-grounded motivation

- Competition README が許容する **data filtering / curation** を、full budget 側で unrecommended frontier まで広げて試す branch
- `A-Open-ProgressPrizePublication/README.md` が hardest slice として置いている **bit_manipulation / equation** に合わせ、current miss に現れている target-table 外の `0ec17d2e` と `00d8b3db` を mandatory にした raw answer-only support を full structured support 予算の上へ足す

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
- surface_binary_structured_answer_only: 101
- surface_numeric_answer_only: 68
- surface_cryptarithm_answer_only: 48
- easy_gravity_fragile: 6
- total unique overlay problems: 712

### Repeated training rows

- binary_structured_exact_core: 768
- binary_logic_exact: 228
- binary_permutation_exact: 164
- binary_prompt_local_exact: 475
- surface_numeral_boxed: 102
- surface_cipher_boxed: 19
- surface_unit_tail: 21
- surface_symbol_prefix: 8
- surface_binary_prompt_local_answer_only: 291
- surface_binary_structured_answer_only: 324
- surface_numeric_answer_only: 217
- surface_cryptarithm_answer_only: 260
- easy_gravity_fragile: 22
- total repeated overlay rows: 2899

### Bundle footprint

- base examples: 7828
- overlay examples: 2899
- total examples: 10727
- total steps: 336
- total tokens: 28668072
- max sequence length: 7971

## Frontier raw-support mix

- `surface_binary_structured_answer_only` に **`+5 unique slots`**、`surface_numeric_answer_only` に **`+4 unique slots`** を追加
- selected frontier raw support は **9 unique rows** で、内訳は `problem_status_rule_unknown 7` と `problem_status_hypothesis_formed 2`
- current partial unrecommended misses **`0ec17d2e`** と **`00d8b3db`** は `current_frontier_miss_support` として mandatory で含める
- repeat は `FRONTIER_RAW_SUPPORT_BONUS_REPEAT = 1`、current miss 2 件には `FRONTIER_RAW_CURRENT_MISS_EXTRA_REPEAT = 2` を追加
- `surface_binary_structured_answer_only` repeats は `302 -> 324`、`surface_numeric_answer_only` repeats は `199 -> 217`

## Support budget

- prompt-local support: **96 unique / 291 repeated**
- structured support: **101 unique / 324 repeated**
- numeric support: **68 unique / 217 repeated**
- cryptarithm support: **48 unique / 260 repeated**
- cipher / unit / gravity support repeats は `19 / 21 / 22`
- combined measured-support share は **`0.3212`**
- cryptarithm share は **`0.0406`**
- exact binary share (`binary_structured_exact_core + binary_prompt_local_exact`) は **`0.5000`**

## Delta vs full crypt-deduce-heavy base

- `...crypt_deduce_heavy` 比で unique rows は `703 -> 712`
- overlay rows は `2859 -> 2899`
- total tokens は `28658260 -> 28668072` で **`+9812`**
- 増分は unrecommended frontier raw-support 9 rows の追加と extra repeat に対応する

## Interpretation before training

- `crypt_deduce_heavy` の crypt deduce push を保ったまま、**recommended target table の外にある residual frontier** を full budget 側で直接支える ablation
- full では structured support が already 厚いので、この枝はそこへ raw frontier support を重ねることで、frontier outlier 回収が本当に効くかを試す

## Next evaluation gate

- `...crypt_deduce_heavy_frontier_support` を `...crypt_deduce_heavy` と measured diff-pack で比較し、**full budget でも unrecommended frontier support が clean gain になるか** を見る
