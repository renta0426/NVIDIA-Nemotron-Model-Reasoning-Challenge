# v20 corrective corpus v6 promptlocal-short-token-numeric-guess-tail-only-boost results

## Status

- Created: 2026-04-18 UTC
- Generator: `v20_mlx_repro_v1/experiments/v6/numeric_guess/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_tail_only_boost/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_tail_only_boost.py`
- Run name: `v6_promptlocal_short_token_numeric_guess_tail_only_boost_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_numeric_guess_tail_only_boost_mb1_nobc`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_tail_only_boost_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python v20_mlx_repro_v1/experiments/v6/numeric_guess/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_tail_only_boost/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_tail_only_boost.py --run-name v6_promptlocal_short_token_numeric_guess_tail_only_boost_default --write-training-bundle` を current branch で実行し、README 契約と canonical checks を通した上で bundle 再生成に成功
- Branch purpose: numeric support lane を `pool <= 3` の tail operators のみに絞り、common operator を完全に落として tail-only で比較する ablation branch
- Execution note: `v20_mlx_v6_promptlocal_short_token_numeric_guess_operator_tail_boost_mb1_nobc` の `training_result.json` 出現後にこの full pipeline が自動起動する detached queue を設定済み
- Post-run automation: `v6-promptlocal-short-token-tail-only-train-watch` / `v6-promptlocal-short-token-tail-only-eval-watch` に加えて、validation summary 出現後の measured diff-pack chain も armed

## Generated artifacts

- `v20_mlx_repro_v1/experiments/v6/numeric_guess/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_tail_only_boost/outputs/v6_promptlocal_short_token_numeric_guess_tail_only_boost_default/artifacts/corrective_selection.csv`
- `v20_mlx_repro_v1/experiments/v6/numeric_guess/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_tail_only_boost/outputs/v6_promptlocal_short_token_numeric_guess_tail_only_boost_default/artifacts/corrective_overlay_unique.jsonl`
- `v20_mlx_repro_v1/experiments/v6/numeric_guess/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_tail_only_boost/outputs/v6_promptlocal_short_token_numeric_guess_tail_only_boost_default/artifacts/corrective_overlay_repeated.jsonl`
- `v20_mlx_repro_v1/experiments/v6/numeric_guess/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_tail_only_boost/outputs/v6_promptlocal_short_token_numeric_guess_tail_only_boost_default/artifacts/corrective_overlay_summary.json`
- `v20_mlx_repro_v1/experiments/v6/numeric_guess/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_tail_only_boost/outputs/v6_promptlocal_short_token_numeric_guess_tail_only_boost_default/reports/corrective_overlay_report.md`

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
- surface_numeric_answer_only: 34
- easy_gravity_fragile: 6
- total unique overlay problems: 433

### Repeated training rows

- binary_structured_exact_core: 618
- binary_logic_exact: 228
- binary_permutation_exact: 164
- binary_prompt_local_exact: 380
- surface_numeral_boxed: 102
- surface_cipher_boxed: 18
- surface_unit_tail: 18
- surface_symbol_prefix: 8
- surface_numeric_answer_only: 186
- easy_gravity_fragile: 18
- total repeated overlay rows: 1740

### Bundle footprint

- base examples: 7828
- overlay examples: 1740
- total examples: 9568
- total steps: 300
- total tokens: 28353958
- max sequence length: 7971

### Overlay supervision styles

- exact_rule_commit: 343
- exact_closure_commit: 343
- short_closure_commit: 343
- binary_zero_skill: 343
- anti_default1_commit: 9
- anti_default1_contrast_commit: 9
- surface_boxed_tail: 90
- surface_boxed_tail_boost: 34
- surface_short_closure: 86
- surface_short_closure_boost: 34
- surface_token_skill: 90
- surface_token_skill_boost: 16

## Canonical validation

- passed: True
- binary max think lines: 4
- surface max think lines: 3
- mandatory anchor missing: 0
- binary non-verified contamination: 0
- surface unexpected categories: 0

## Numeric guess tail-only slice

- `surface_numeric_answer_only` の 34 unique rows は **すべて** `equation_numeric_guess`
- selected operators は **16 tail operators** のみで、すべて `pool <= 3`
- common operators (`+`, `-`, `*`, `/`, `:`, `@`, `\\`, `[`, `%`, `` ` ``) は意図的に不採用
- repeated tail mix: `" 6`, `$ 6`, `> 6`, `< 6`, `{ 12`, `# 12`, `? 12`, `( 12`, `' 12`, `& 12`, `} 15`, `) 15`, `] 15`, `^ 15`, `! 15`, `| 15`

## Reassessment alignment check

### 1. `prompt-local short/token + numeric guess tail only boost` requirements

- prompt-local exact rows の再活用: 満たす。`binary_prompt_local_exact` は `95` を維持した。
- short-closure rewrite lane: 満たす。`short_closure_commit 343` と `surface_short_closure 86 + boost 34` を維持した。
- token-skill auxiliary lane: 満たす。`binary_zero_skill 343` と `surface_token_skill 90 + boost 16` を維持した。
- numeric tail-only lane: 満たす。`surface_numeric_answer_only 34` を low-frequency `equation_numeric_guess` rows だけに限定した。
- tail repeat boost: 満たす。`surface_boxed_tail_boost 34`, `surface_short_closure_boost 34`, `surface_token_skill_boost 16` を tail rows に上乗せした。
- heavier anti-`default 1` counterexample lane: 満たす。`anti_default1_commit 9` と `anti_default1_contrast_commit 9` を維持した。

### 2. 今回あえて入れていないもの

- common operator guess rows
- broad `glyph_len5` / cryptarithm answer-only expansion
- risky な binary token representation change

### 3. README 契約との整合

- `README.md` と `A-Open-ProgressPrizePublication/README.md` の deterministic / boxed-first 契約を崩さず、README の `Coverage` 原則を **tail operator だけに集中**させた。
- `FINAL_SUMMARY_REPORT.md` の handoff に従い、`answer_only_keep` は full trace teacher ではなく final-answer support lane として扱った。
- operator-tail のみで hidden/public に効くかを切り分けるための ablation branch として明確に独立させた。

## Observed tradeoff before training

- overlay examples は `1740`、総 token は `28353958`。`operator-tail-boost` より軽く、common operator noise を削った対照線になる。
- 16 tail operators だけに絞ったので、numeric guess の難所集中が本当に有効かを `operator-cover` / `operator-boost` / `operator-tail-boost` と直接比較できる。
- もしこの branch が改善するなら、common operator rows はむしろ容量ノイズで、tail-only concentration が正しかったと判断できる。

## Next evaluation gate

- `promptlocal-short-token-numeric-guess-operator-tail-boost` と本 branch を直接比較し、common operator を落とした方が `equation_numeric_guess` の public/proxy に効くか measured diff-pack で確認する。
- 改善するなら、numeric lane は coverage を維持する mainline と tail-only corrective を分離して運用する。
