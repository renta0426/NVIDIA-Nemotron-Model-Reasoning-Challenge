# v20 corrective corpus v6 promptlocal-short-token-numeric-support results

## Status

- Created: 2026-04-18 UTC
- Generator: `versions/v20_corrective_corpus_v6_promptlocal_short_token_numeric_support/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_numeric_support.py`
- Run name: `v6_promptlocal_short_token_numeric_support_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_numeric_support_mb1_nobc`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_numeric_support_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python versions/v20_corrective_corpus_v6_promptlocal_short_token_numeric_support/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_numeric_support.py --run-name v6_promptlocal_short_token_numeric_support_default --write-training-bundle` を current branch で実行し、README 契約と canonical checks を通した上で bundle 再生成に成功
- Branch purpose: `bit_other` / prompt-local exact rows を厚くしたまま、`short-closure` と `token-skill` の両補助 lane を維持しつつ、`numeric_2x2 answer_only_keep` を narrow support lane として追加する branch
- Execution note: `v20_mlx_v6_promptlocal_short_token_skill_mb1_nobc` の `training_result.json` 出現後にこの full pipeline が自動起動する detached queue を設定済み
- Post-run automation: `v6-promptlocal-short-token-numeric-train-watch` / `v6-promptlocal-short-token-numeric-eval-watch` に加えて、validation summary 出現後の measured diff-pack chain も armed

## Generated artifacts

- `versions/v20_corrective_corpus_v6_promptlocal_short_token_numeric_support/outputs/v6_promptlocal_short_token_numeric_support_default/artifacts/corrective_selection.csv`
- `versions/v20_corrective_corpus_v6_promptlocal_short_token_numeric_support/outputs/v6_promptlocal_short_token_numeric_support_default/artifacts/corrective_overlay_unique.jsonl`
- `versions/v20_corrective_corpus_v6_promptlocal_short_token_numeric_support/outputs/v6_promptlocal_short_token_numeric_support_default/artifacts/corrective_overlay_repeated.jsonl`
- `versions/v20_corrective_corpus_v6_promptlocal_short_token_numeric_support/outputs/v6_promptlocal_short_token_numeric_support_default/artifacts/corrective_overlay_summary.json`
- `versions/v20_corrective_corpus_v6_promptlocal_short_token_numeric_support/outputs/v6_promptlocal_short_token_numeric_support_default/reports/corrective_overlay_report.md`

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
- surface_numeric_answer_only: 24
- easy_gravity_fragile: 6
- total unique overlay problems: 423

### Repeated training rows

- binary_structured_exact_core: 618
- binary_logic_exact: 228
- binary_permutation_exact: 164
- binary_prompt_local_exact: 380
- surface_numeral_boxed: 102
- surface_cipher_boxed: 18
- surface_unit_tail: 18
- surface_symbol_prefix: 8
- surface_numeric_answer_only: 72
- easy_gravity_fragile: 18
- total repeated overlay rows: 1626

### Bundle footprint

- base examples: 7828
- overlay examples: 1626
- total examples: 9454
- total steps: 296
- total tokens: 28337474
- max sequence length: 7971

### Overlay supervision styles

- exact_rule_commit: 343
- exact_closure_commit: 343
- short_closure_commit: 343
- binary_zero_skill: 343
- anti_default1_commit: 9
- anti_default1_contrast_commit: 9
- surface_boxed_tail: 80
- surface_short_closure: 76
- surface_token_skill: 80

## Canonical validation

- passed: True
- binary max think lines: 4
- surface max think lines: 3
- mandatory anchor missing: 0
- binary non-verified contamination: 0
- surface unexpected categories: 0

## Reassessment alignment check

### 1. `prompt-local short/token + numeric support` requirements

- prompt-local exact rows の再活用: 満たす。`binary_prompt_local_exact` は `95`、overlay token share は `0.2513` 近傍を維持した。
- short-closure rewrite lane: 満たす。`short_closure_commit 343` と `surface_short_closure 76` を維持した。
- token-skill auxiliary lane: 満たす。`binary_zero_skill 343` と `surface_token_skill 80` を維持した。
- numeric answer-only support lane: 満たす。`surface_numeric_answer_only 24` を追加し、`numeric_2x2 answer_only_keep` 587 候補から narrow に補助 supervision を選んだ。
- heavier anti-`default 1` counterexample lane: 満たす。`anti_default1_commit 9` と `anti_default1_contrast_commit 9` を維持した。
- boxed-first surface stabilizer lane: 満たす。surface 側は README 契約を保った boxed-first supervision のみ。

### 2. 今回あえて入れていないもの

- broad `glyph_len5` / cryptarithm answer-only expansion
- risky な binary token representation change
- answer-only heavy promotion

### 3. README 契約との整合

- `README.md` と `A-Open-ProgressPrizePublication/README.md` の deterministic / boxed-first 契約を崩さず、`equation_numeric` の narrow answer-only lane だけを追加した。
- `FINAL_SUMMARY_REPORT.md` の handoff に従い、`answer_only_keep` は full trace teacher ではなく final-answer support lane として扱った。
- Kaggle へそのまま持ち込める single-file training bundle を生成した。

## Observed tradeoff before training

- overlay examples は `1626`、総 token は `28337474`。`promptlocal-short-token` よりやや重いが、追加分の大半は `surface_numeric_answer_only` の `72` 例だけである。
- `equation_numeric_guess` を優先する narrow lane なので、bit-other 本体を崩さずに `numeric_2x2` の undertrained slice を拾える。
- もしこの branch が悪化するなら、`answer_only_keep` の補助 lane は even narrower に絞るべきで、bit-other 本命からは外す判断材料になる。

## Next evaluation gate

- `promptlocal-short-token` と本 branch を直接比較し、`equation_numeric_guess` / `equation_numeric_deduce` の改善が `bit_other` no-regression 付きで取れるか measured diff-pack で確認する。
- proxy/public 方向で改善するなら、以後の corrective ladder に narrow numeric support lane を標準装備する。
