# v20 corrective corpus v6 promptlocal-short-token-numeric-guess-heavy results

## Status

- Created: 2026-04-18 UTC
- Generator: `v20_mlx_repro_v1/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_heavy/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_heavy.py`
- Run name: `v6_promptlocal_short_token_numeric_guess_heavy_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_numeric_guess_heavy_mb1_nobc`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_heavy_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python v20_mlx_repro_v1/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_heavy/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_heavy.py --run-name v6_promptlocal_short_token_numeric_guess_heavy_default --write-training-bundle` を current branch で実行し、README 契約と canonical checks を通した上で bundle 再生成に成功
- Branch purpose: bit-other triple-hybrid を維持したまま、`equation_numeric_guess` を優先して `numeric_2x2 answer_only_keep` support lane を heavier 化する branch
- Execution note: `v20_mlx_v6_promptlocal_short_token_numeric_support_mb1_nobc` の `training_result.json` 出現後にこの full pipeline が自動起動する detached queue を設定済み
- Post-run automation: `v6-promptlocal-short-token-guess-train-watch` / `v6-promptlocal-short-token-guess-eval-watch` に加えて、validation summary 出現後の measured diff-pack chain も armed

## Generated artifacts

- `v20_mlx_repro_v1/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_heavy/outputs/v6_promptlocal_short_token_numeric_guess_heavy_default/artifacts/corrective_selection.csv`
- `v20_mlx_repro_v1/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_heavy/outputs/v6_promptlocal_short_token_numeric_guess_heavy_default/artifacts/corrective_overlay_unique.jsonl`
- `v20_mlx_repro_v1/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_heavy/outputs/v6_promptlocal_short_token_numeric_guess_heavy_default/artifacts/corrective_overlay_repeated.jsonl`
- `v20_mlx_repro_v1/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_heavy/outputs/v6_promptlocal_short_token_numeric_guess_heavy_default/artifacts/corrective_overlay_summary.json`
- `v20_mlx_repro_v1/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_heavy/outputs/v6_promptlocal_short_token_numeric_guess_heavy_default/reports/corrective_overlay_report.md`

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
- surface_numeric_answer_only: 48
- easy_gravity_fragile: 6
- total unique overlay problems: 447

### Repeated training rows

- binary_structured_exact_core: 618
- binary_logic_exact: 228
- binary_permutation_exact: 164
- binary_prompt_local_exact: 380
- surface_numeral_boxed: 102
- surface_cipher_boxed: 18
- surface_unit_tail: 18
- surface_symbol_prefix: 8
- surface_numeric_answer_only: 144
- easy_gravity_fragile: 18
- total repeated overlay rows: 1698

### Bundle footprint

- base examples: 7828
- overlay examples: 1698
- total examples: 9526
- total steps: 299
- total tokens: 28348628
- max sequence length: 7971

### Overlay supervision styles

- exact_rule_commit: 343
- exact_closure_commit: 343
- short_closure_commit: 343
- binary_zero_skill: 343
- anti_default1_commit: 9
- anti_default1_contrast_commit: 9
- surface_boxed_tail: 104
- surface_short_closure: 100
- surface_token_skill: 104

## Canonical validation

- passed: True
- binary max think lines: 4
- surface max think lines: 3
- mandatory anchor missing: 0
- binary non-verified contamination: 0
- surface unexpected categories: 0

## Reassessment alignment check

### 1. `prompt-local short/token + numeric guess heavy` requirements

- prompt-local exact rows の再活用: 満たす。`binary_prompt_local_exact` は `95` を維持した。
- short-closure rewrite lane: 満たす。`short_closure_commit 343` と `surface_short_closure 100` を維持した。
- token-skill auxiliary lane: 満たす。`binary_zero_skill 343` と `surface_token_skill 104` を維持した。
- heavier numeric answer-only support lane: 満たす。`surface_numeric_answer_only 48` を追加し、`equation_numeric_guess` を優先して `numeric_2x2 answer_only_keep` 587 候補から heavier に補助 supervision を選んだ。
- heavier anti-`default 1` counterexample lane: 満たす。`anti_default1_commit 9` と `anti_default1_contrast_commit 9` を維持した。
- boxed-first surface stabilizer lane: 満たす。surface 側は README 契約を保った boxed-first supervision のみ。

### 2. 今回あえて入れていないもの

- broad `glyph_len5` / cryptarithm answer-only expansion
- risky な binary token representation change
- answer-only heavy promotion beyond `numeric_2x2`

### 3. README 契約との整合

- `README.md` と `A-Open-ProgressPrizePublication/README.md` の deterministic / boxed-first 契約を崩さず、`equation_numeric` の support lane だけをさらに厚くした。
- `FINAL_SUMMARY_REPORT.md` の handoff に従い、`answer_only_keep` は full trace teacher ではなく final-answer support lane として扱った。
- Kaggle へそのまま持ち込める single-file training bundle を生成した。

## Observed tradeoff before training

- overlay examples は `1698`、総 token は `28348628`。`numeric_support` より少し重いが、増分は主に `surface_numeric_answer_only` の `+72` 例である。
- overlay token share で `surface_numeric_answer_only` は `0.0431` まで増え、`equation_numeric_guess` の undertrained slice を局所的に強められる。
- もしこの branch が悪化するなら、numeric support lane は `24` 行規模が上限で、guess-heavy は過剰だったと切り分けられる。

## Next evaluation gate

- `promptlocal-short-token-numeric-support` と本 branch を直接比較し、`equation_numeric_guess` / `equation_numeric_deduce` の改善が `bit_other` no-regression 付きで取れるか measured diff-pack で確認する。
- proxy/public 方向で改善するなら、以後の corrective ladder に `guess-heavy` numeric support lane を採用する。
