# v20 corrective corpus v6 promptlocal-short-token-binary-support-hybrid-expanded-numeric-popular8-plain-cryptarithm-support-bit-miss-support-crypt-miss-support-measured-surface-support-bit-family-rebalance-crypt-deduce-heavy-frontier-support results

## Status

- Created: 2026-04-19 UTC
- Generator: `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_deduce_heavy_frontier_support/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_deduce_heavy_frontier_support.py`
- Run name: `v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_deduce_heavy_frontier_support_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_deduce_heavy_frontier_support_mb1_nobc`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_deduce_heavy_frontier_support_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python ...bit_family_rebalance_crypt_deduce_heavy_frontier_support.py --write-training-bundle` で canonical checks を通して bundle 再生成に成功
- Launch status: queued predecessor chain を待たず手動前倒し起動を試したが、`v20_mlx_v4_mainline_mb1_nobc` eval + `v20_mlx_v6_mainline_mb1_nobc` train + `v20_mlx_v6_frontier_oct_heavy_expanded_mb1_nobc` train と重なったタイミングで **Metal OOM** が発生し、`pipeline.log` には `Command buffer execution failed: Insufficient Memory` が残った。直後に heavy_count gate 付き relaunch も仕込んだが、再起動で run completion 前に中断した
- Queue note (2026-04-20): 三重起動による OOM を避けるため、この expanded frontier-support run は `v20_mlx_v6_mainline_mb1_nobc` の `training_result.json` 出現と mainline train process 終了を待ってから、`v20_mlx_repro_v1/outputs/v6/support` 配下で fresh relaunch する detached queue に切り替えた
- Eval automation note (2026-04-20): grouped support root 向けに `training_result.json` 出現後の adapter-validation watcher と `postprocess-run --postprocess-eval-kind adapter-validation` watcher を追加し、train 完了後に README 契約の validation を自動起動する
- Launch note (2026-04-20): `vm_stat` で free pages が約 `11.1M`、active MLX jobs がまだ 4 本未満に収まっていたため、queue 待ちを打ち切って `v20_mlx_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_deduce_heavy_frontier_support_mb1_nobc` を detached full-train として前倒し起動した
- Live-process note (2026-04-20): この fresh launch も `pipeline.log` がまだ空で `adapter/latest_train_report.json` 未生成のままだが、python train process の `sample` では main thread が `mlx::core::eval -> eval_impl -> std::condition_variable::wait` に入っていた。初回 OOM 後の再ハングではなく MLX eval / loader phase の継続とみなし、free pages 約 `4642`・active python `5` 本の間は kill / relaunch を行わず queue 進行だけを待つ
- Pause note (2026-04-20): その後も `latest_train_report.json` は出ず、`top` では `0% CPU`, 約 `59 GB RSS`, `state=stuck` のまま step 0 停滞が続いたため、この live train は一旦停止した。`queue-frontier-support-after-v6-mainline.log` の delayed relaunch と grouped-root eval watcher は残してあり、mainline が終わった後に再開できる

## README-grounded motivation

- Competition README が許容する **data filtering / curation** の一環として、`train_recommended_learning_target_v1.csv` から外れている raw frontier を small support lane として再導入する branch
- `A-Open-ProgressPrizePublication/README.md` が強調する **bit_manipulation** と **equation** の hard slice に合わせ、current partial で実際に落ちている unrecommended miss `0ec17d2e` (bit, `rule_unknown`) と `00d8b3db` (numeric deduce, `hypothesis_formed`) を mandatory にしつつ、同じ未推奨 pool から少量 fill する

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
- surface_binary_structured_answer_only: 69
- surface_numeric_answer_only: 68
- surface_cryptarithm_answer_only: 48
- easy_gravity_fragile: 6
- total unique overlay problems: 680

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
- surface_binary_structured_answer_only: 228
- surface_numeric_answer_only: 217
- surface_cryptarithm_answer_only: 260
- easy_gravity_fragile: 22
- total repeated overlay rows: 2803

### Bundle footprint

- base examples: 7828
- overlay examples: 2803
- total examples: 10631
- total steps: 333
- total tokens: 28639036
- max sequence length: 7971

## Frontier raw-support mix

- `surface_binary_structured_answer_only` に **`+5 unique slots`**、`surface_numeric_answer_only` に **`+4 unique slots`** を追加
- selected frontier raw support は **9 unique rows** で、内訳は `problem_status_rule_unknown 7` と `problem_status_hypothesis_formed 2`
- current partial unrecommended misses **`0ec17d2e`** と **`00d8b3db`** は `current_frontier_miss_support` として mandatory で含める
- repeat は `FRONTIER_RAW_SUPPORT_BONUS_REPEAT = 1`、current miss 2 件には `FRONTIER_RAW_CURRENT_MISS_EXTRA_REPEAT = 2` を追加
- `surface_binary_structured_answer_only` repeats は `206 -> 228`、`surface_numeric_answer_only` repeats は `199 -> 217`

## Support budget

- prompt-local support: **96 unique / 291 repeated**
- structured support: **69 unique / 228 repeated**
- numeric support: **68 unique / 217 repeated**
- cryptarithm support: **48 unique / 260 repeated**
- cipher / unit / gravity support repeats は `19 / 21 / 22`
- combined measured-support share は **`0.2966`**
- cryptarithm share は **`0.0421`**
- exact binary share (`binary_structured_exact_core + binary_prompt_local_exact`) は **`0.5181`**

## Delta vs expanded crypt-deduce-heavy base

- `...crypt_deduce_heavy` 比で unique rows は `671 -> 680`
- overlay rows は `2763 -> 2803`
- total tokens は `28629224 -> 28639036` で **`+9812`**
- 増分は unrecommended frontier raw-support 9 rows の追加と extra repeat に対応する

## Interpretation before training

- `crypt_deduce_heavy` の deduce-only crypt push を保ったまま、**curated target table の外にある residual miss frontier** を raw answer-only で薄く拾う branch
- 過度な overfit を避けるため small fill に留めており、これで `0ec17d2e` / `00d8b3db` のような frontier を cheap に回収できるかを測る

## Next evaluation gate

- `...crypt_deduce_heavy_frontier_support` を `...crypt_deduce_heavy` と measured diff-pack で比較し、**unrecommended frontier raw-support が bit/numeric frontier を拾うか、それとも単なる memorization ノイズに終わるか** を見る
