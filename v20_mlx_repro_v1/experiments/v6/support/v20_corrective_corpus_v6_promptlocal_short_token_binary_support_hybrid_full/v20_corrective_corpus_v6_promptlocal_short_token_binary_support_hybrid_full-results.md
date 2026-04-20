# v20 corrective corpus v6 promptlocal-short-token-binary-support-hybrid-full results

## Status

- Created: 2026-04-19 UTC
- Generator: `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full.py`
- Run name: `v6_promptlocal_short_token_binary_support_hybrid_full_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_binary_support_hybrid_full_mb1_nobc`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full.py --run-name v6_promptlocal_short_token_binary_support_hybrid_full_default --write-training-bundle` を current branch で実行し、`README.md` と `A-Open-ProgressPrizePublication/README.md` の deterministic / boxed-first 契約を保ったまま canonical checks を通して bundle 再生成に成功
- Branch purpose: `promptlocal_short_token_binary_support_hybrid` の stacking を最大化し、prompt-local full support と structured full support の両方を separate lane として積んだときの upper bound を測る branch
- Execution note: `v20_mlx_v6_promptlocal_short_token_binary_support_hybrid_expanded_mb1_nobc` の `training_result.json` 出現後にこの full pipeline が自動起動する detached queue を設定
- Post-run automation: `v6-promptlocal-short-token-binary-support-hybrid-full-train-watch` / `v6-promptlocal-short-token-binary-support-hybrid-full-eval-watch` に加えて、validation summary 出現後の measured diff-pack chain も armed

## Generated artifacts

- `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full/outputs/v6_promptlocal_short_token_binary_support_hybrid_full_default/artifacts/corrective_selection.csv`
- `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full/outputs/v6_promptlocal_short_token_binary_support_hybrid_full_default/artifacts/corrective_overlay_unique.jsonl`
- `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full/outputs/v6_promptlocal_short_token_binary_support_hybrid_full_default/artifacts/corrective_overlay_repeated.jsonl`
- `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full/outputs/v6_promptlocal_short_token_binary_support_hybrid_full_default/artifacts/corrective_overlay_summary.json`
- `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full/outputs/v6_promptlocal_short_token_binary_support_hybrid_full_default/reports/corrective_overlay_report.md`

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
- easy_gravity_fragile: 6
- total unique overlay problems: 591

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
- easy_gravity_fragile: 18
- total repeated overlay rows: 2130

### Bundle footprint

- base examples: 7828
- overlay examples: 2130
- total examples: 9958
- total steps: 312
- total tokens: 28503830
- max sequence length: 7971

### Overlay supervision styles

- exact_rule_commit: 343
- exact_closure_commit: 343
- short_closure_commit: 343
- binary_zero_skill: 343
- anti_default1_commit: 9
- anti_default1_contrast_commit: 9
- surface_boxed_tail: 248
- surface_short_closure: 244
- surface_token_skill: 248

## Canonical validation

- passed: True
- binary max think lines: 4
- surface max think lines: 3
- mandatory anchor missing: 0
- binary non-verified contamination: 0
- stage-b-like exact contamination: 0

## Dual bit answer-only support slices

- prompt-local support lane は `surface_binary_prompt_local_answer_only` として **96 unique / 288 repeated**
- structured support lane は `surface_binary_structured_answer_only` として **96 unique / 288 repeated**
- prompt-local support source は `bit_prompt_local_current_consensus_answer_only 74` と `bit_prompt_local_nested_support3_or_abstract_answer_only 22`
- structured support source は `bit_structured_byte_formula` + `answer_only_keep` の head `96`
- overlay token は prompt-local support `86787`、structured support `90471`
- overlay token share は prompt-local `0.13`、structured `0.1355` で、combined bit support share は `0.2655`
- hybrid expanded 比で overlay は `2034 -> 2130`、total tokens は `28475478 -> 28503830`

## Reassessment alignment check

### 1. `prompt-local full + structured full dual support` requirements

- prompt-local exact rows の再活用: 満たす。verified exact は `95` を維持した
- short-closure rewrite lane: 満たす。`short_closure_commit 343` と `surface_short_closure 244` を維持した
- token-skill auxiliary lane: 満たす。`binary_zero_skill 343` と `surface_token_skill 248` を維持した
- answer_only separate lanes: 満たす。prompt-local と structured-byte の answer_only をどちらも verified exact lane へ混ぜず support lane のみに隔離した
- boxed-first / deterministic contract: 満たす。`README.md` と `A-Open-ProgressPrizePublication/README.md` の boxed-first / deterministic 契約を崩していない

### 2. 今回あえて入れていないもの

- answer-only rows の full CoT teacher 化
- structured support beyond current 96-row full ladder
- risky な binary token representation change

### 3. README / reassessment に対する位置づけ

- `A-Open-ProgressPrizePublication/README.md` の bit headroom に対し、prompt-local と structured-byte の support lanes を両方 full に寄せた upper-bound 比較線である
- `versions/v20_to_088_reassessment_2026-04-18.md` の separate-lane 方針を最大ボリュームで試す branch であり、stacking が過剰かどうかを見切るための線である

## Observed tradeoff before training

- exact binary mainline は hybrid / hybrid_expanded と同一なので、差分は **structured support 32 / 64 / 96** の量だけになる
- combined bit support share は `0.2655` まで上がるが、total tokens は still `28.50M` と README v20 (`27,850,703`) 近辺にとどまっている
- もしこの版が悪化するなら、dual support stacking は 96 まで積むと過剰で、expanded か narrow に戻すべきと分かる

## Next evaluation gate

- `hybrid` / `hybrid_expanded` / `hybrid_full` を横並びで比較し、dual support stacking の最適量を measured diff-pack で特定する
- strongest line が出たら、その branch を mainline 候補として submission 再現パイプラインへ昇格させる
