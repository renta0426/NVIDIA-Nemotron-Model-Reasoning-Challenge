# v20 corrective corpus v6 promptlocal-short-token-binary-support-hybrid-expanded results

## Status

- Created: 2026-04-19 UTC
- Generator: `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded.py`
- Run name: `v6_promptlocal_short_token_binary_support_hybrid_expanded_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_binary_support_hybrid_expanded_mb1_nobc`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded.py --run-name v6_promptlocal_short_token_binary_support_hybrid_expanded_default --write-training-bundle` を current branch で実行し、`README.md` と `A-Open-ProgressPrizePublication/README.md` の deterministic / boxed-first 契約を保ったまま canonical checks を通して bundle 再生成に成功
- Branch purpose: `promptlocal_short_token_binary_support_hybrid` の stacking を保ったまま structured-byte support lane を `32 -> 64` に広げ、prompt-local full support と structured expanded support が共存するときの最適点を測る branch
- Execution note: `v20_mlx_v6_promptlocal_short_token_binary_support_hybrid_mb1_nobc` の `training_result.json` 出現後にこの full pipeline が自動起動する detached queue を設定
- Post-run automation: `v6-promptlocal-short-token-binary-support-hybrid-expanded-train-watch` / `v6-promptlocal-short-token-binary-support-hybrid-expanded-eval-watch` に加えて、validation summary 出現後の measured diff-pack chain も armed
- Watcher note (2026-04-20): `v20_mlx_repro_v1/outputs/v6/support` 配下で actual grouped-root train/eval watcher を再配置し、predecessor `training_result.json` 待ちの launch queue と train 完了後の adapter-validation / postprocess を実体として arm した

## Generated artifacts

- `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded/outputs/v6_promptlocal_short_token_binary_support_hybrid_expanded_default/artifacts/corrective_selection.csv`
- `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded/outputs/v6_promptlocal_short_token_binary_support_hybrid_expanded_default/artifacts/corrective_overlay_unique.jsonl`
- `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded/outputs/v6_promptlocal_short_token_binary_support_hybrid_expanded_default/artifacts/corrective_overlay_repeated.jsonl`
- `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded/outputs/v6_promptlocal_short_token_binary_support_hybrid_expanded_default/artifacts/corrective_overlay_summary.json`
- `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded/outputs/v6_promptlocal_short_token_binary_support_hybrid_expanded_default/reports/corrective_overlay_report.md`

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
- easy_gravity_fragile: 6
- total unique overlay problems: 559

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
- easy_gravity_fragile: 18
- total repeated overlay rows: 2034

### Bundle footprint

- base examples: 7828
- overlay examples: 2034
- total examples: 9862
- total steps: 309
- total tokens: 28475478
- max sequence length: 7971

### Overlay supervision styles

- exact_rule_commit: 343
- exact_closure_commit: 343
- short_closure_commit: 343
- binary_zero_skill: 343
- anti_default1_commit: 9
- anti_default1_contrast_commit: 9
- surface_boxed_tail: 216
- surface_short_closure: 212
- surface_token_skill: 216

## Canonical validation

- passed: True
- binary max think lines: 4
- surface max think lines: 3
- mandatory anchor missing: 0
- binary non-verified contamination: 0
- stage-b-like exact contamination: 0

## Dual bit answer-only support slices

- prompt-local support lane は `surface_binary_prompt_local_answer_only` として **96 unique / 288 repeated**
- structured support lane は `surface_binary_structured_answer_only` として **64 unique / 192 repeated**
- prompt-local support source は `bit_prompt_local_current_consensus_answer_only 74` と `bit_prompt_local_nested_support3_or_abstract_answer_only 22`
- structured support source は `bit_structured_byte_formula` + `answer_only_keep` の head `64`
- overlay token は prompt-local support `86787`、structured support `62119`
- overlay token share は prompt-local `0.1358`、structured `0.0972` で、combined bit support share は `0.2330`
- hybrid narrow 比で overlay は `1938 -> 2034`、total tokens は `28445302 -> 28475478`

## Reassessment alignment check

### 1. `prompt-local full + structured expanded dual support` requirements

- prompt-local exact rows の再活用: 満たす。verified exact は `95` を維持した
- short-closure rewrite lane: 満たす。`short_closure_commit 343` と `surface_short_closure 212` を維持した
- token-skill auxiliary lane: 満たす。`binary_zero_skill 343` と `surface_token_skill 216` を維持した
- answer_only separate lanes: 満たす。prompt-local と structured-byte の answer_only をどちらも verified exact lane へ混ぜず support lane のみに隔離した
- boxed-first / deterministic contract: 満たす。`README.md` と `A-Open-ProgressPrizePublication/README.md` の boxed-first / deterministic 契約を崩していない

### 2. 今回あえて入れていないもの

- answer-only rows の full CoT teacher 化
- structured support の full `96` 併用
- risky な binary token representation change

### 3. README / reassessment に対する位置づけ

- `A-Open-ProgressPrizePublication/README.md` の bit headroom に対し、prompt-local full support に structured expanded support を重ねた branch である
- `versions/v20_to_088_reassessment_2026-04-18.md` の separate-lane 方針を保ったまま、stacking の強さを narrow より一段重くした比較線である

## Observed tradeoff before training

- exact binary mainline は hybrid narrow と同一なので、差分は **structured support 32 -> 64** にほぼ一致する
- combined bit support share は `0.2330` まで上がるが、total tokens はまだ `28.48M` で README v20 の token 規模から大きく逸脱していない
- narrow が弱く full が重すぎる場合、この expanded 版が stacking の最適点になる可能性がある

## Next evaluation gate

- `hybrid` / `hybrid_expanded` / `hybrid_full` を横並びで比較し、dual support stacking の最適量を measured diff-pack で特定する
- stacking が効くなら、その strongest line を本命 mainline 候補へ昇格させる
