# v20 corrective corpus v6 promptlocal-short-token-numeric-guess-operator-cover results

## Status

- Created: 2026-04-18 UTC
- Generator: `versions/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_operator_cover/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_operator_cover.py`
- Run name: `v6_promptlocal_short_token_numeric_guess_operator_cover_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_numeric_guess_operator_cover_mb1_nobc`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_operator_cover_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python versions/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_operator_cover/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_operator_cover.py --run-name v6_promptlocal_short_token_numeric_guess_operator_cover_default --write-training-bundle` を current branch で実行し、README 契約と canonical checks を通した上で bundle 再生成に成功
- Branch purpose: bit-other triple-hybrid を維持したまま、`equation_numeric_guess` の 26 operator を one-per-operator で必ず拾い、その上で numeric guess lane を 64 行まで厚くする coverage branch
- Execution note: `v20_mlx_v6_promptlocal_short_token_numeric_guess_heavy_mb1_nobc` の `training_result.json` 出現後にこの full pipeline が自動起動する detached queue を設定済み
- Post-run automation: `v6-promptlocal-short-token-guess-cover-train-watch` / `v6-promptlocal-short-token-guess-cover-eval-watch` に加えて、validation summary 出現後の measured diff-pack chain も armed

## Generated artifacts

- `versions/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_operator_cover/outputs/v6_promptlocal_short_token_numeric_guess_operator_cover_default/artifacts/corrective_selection.csv`
- `versions/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_operator_cover/outputs/v6_promptlocal_short_token_numeric_guess_operator_cover_default/artifacts/corrective_overlay_unique.jsonl`
- `versions/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_operator_cover/outputs/v6_promptlocal_short_token_numeric_guess_operator_cover_default/artifacts/corrective_overlay_repeated.jsonl`
- `versions/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_operator_cover/outputs/v6_promptlocal_short_token_numeric_guess_operator_cover_default/artifacts/corrective_overlay_summary.json`
- `versions/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_operator_cover/outputs/v6_promptlocal_short_token_numeric_guess_operator_cover_default/reports/corrective_overlay_report.md`

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
- surface_numeric_answer_only: 64
- easy_gravity_fragile: 6
- total unique overlay problems: 463

### Repeated training rows

- binary_structured_exact_core: 618
- binary_logic_exact: 228
- binary_permutation_exact: 164
- binary_prompt_local_exact: 380
- surface_numeral_boxed: 102
- surface_cipher_boxed: 18
- surface_unit_tail: 18
- surface_symbol_prefix: 8
- surface_numeric_answer_only: 192
- easy_gravity_fragile: 18
- total repeated overlay rows: 1746

### Bundle footprint

- base examples: 7828
- overlay examples: 1746
- total examples: 9574
- total steps: 300
- total tokens: 28355553
- max sequence length: 7971

### Overlay supervision styles

- exact_rule_commit: 343
- exact_closure_commit: 343
- short_closure_commit: 343
- binary_zero_skill: 343
- anti_default1_commit: 9
- anti_default1_contrast_commit: 9
- surface_boxed_tail: 120
- surface_short_closure: 116
- surface_token_skill: 120

## Canonical validation

- passed: True
- binary max think lines: 4
- surface max think lines: 3
- mandatory anchor missing: 0
- binary non-verified contamination: 0
- surface unexpected categories: 0

## Numeric guess coverage

- `surface_numeric_answer_only` の 64 unique rows は **すべて** `equation_numeric_guess`
- `equation_numeric_guess` answer-only 候補に存在した 26 operator を **26/26 で全カバー**
- 1 operator 1 行の prefill 後に、残り枠は global priority で埋めた
- selected operator mix: `+ 6`, `- 10`, `* 9`, `/ 3`, `: 3`, `@ 2`, `\\ 5`, `[ 2`, `% 1`, `` ` 2``, `| 1`, `! 1`, `] 2`, `} 3`, `^ 2`, `) 1`, `{ 2`, `& 1`, `' 1`, `# 1`, `( 1`, `? 1`, `" 1`, `< 1`, `> 1`, `$ 1`

## Reassessment alignment check

### 1. `prompt-local short/token + numeric guess operator cover` requirements

- prompt-local exact rows の再活用: 満たす。`binary_prompt_local_exact` は `95` を維持した。
- short-closure rewrite lane: 満たす。`short_closure_commit 343` と `surface_short_closure 116` を維持した。
- token-skill auxiliary lane: 満たす。`binary_zero_skill 343` と `surface_token_skill 120` を維持した。
- numeric guess operator coverage lane: 満たす。`surface_numeric_answer_only 64` を全件 `equation_numeric_guess` に振り切り、one-per-operator prefill で rare operator coverage を入れた。
- heavier anti-`default 1` counterexample lane: 満たす。`anti_default1_commit 9` と `anti_default1_contrast_commit 9` を維持した。
- boxed-first surface stabilizer lane: 満たす。surface 側は README 契約を保った boxed-first supervision のみ。

### 2. 今回あえて入れていないもの

- broad `glyph_len5` / cryptarithm answer-only expansion
- risky な binary token representation change
- raw `manual_audit_priority` の直接投入

### 3. README 契約との整合

- `README.md` と `A-Open-ProgressPrizePublication/README.md` の deterministic / boxed-first 契約を崩さず、rare operator coverage を `answer_only_keep` の support lane だけで強化した。
- `FINAL_SUMMARY_REPORT.md` の handoff に従い、`answer_only_keep` は full trace teacher ではなく final-answer support lane として扱った。
- README の `Coverage` 原則に合わせ、popular operator に寄せるのではなく low-frequency guess operator まで確実に学習 bundle に載せた。

## Observed tradeoff before training

- overlay examples は `1746`、総 token は `28355553`。`guess-heavy` より `+48` overlay examples、`+6925` tokens に留まり、RAM/step 増はほぼ無視できる。
- numeric lane を deduce 混在から切り離して guess-only に振り切ったため、`equation_numeric_guess` の undertrained operator tail を局所的に強められる。
- もしこの branch が悪化するなら、numeric support は件数不足ではなく guess-only 偏重そのものが過剰だったと切り分けられる。

## Next evaluation gate

- `promptlocal-short-token-numeric-guess-heavy` と本 branch を直接比較し、`equation_numeric_guess` の rare-operator 改善が `bit_other` no-regression 付きで取れるか measured diff-pack で確認する。
- proxy/public 方向で改善するなら、以後の corrective ladder では numeric lane を count 増より operator cover 優先で設計する。
