# v20 corrective corpus v6 promptlocal-short-token-numeric-guess-common-only-cover results

## Status

- Created: 2026-04-18 UTC
- Generator: `versions/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_common_only_cover/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_common_only_cover.py`
- Run name: `v6_promptlocal_short_token_numeric_guess_common_only_cover_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_numeric_guess_common_only_cover_mb1_nobc`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_common_only_cover_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python versions/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_common_only_cover/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_common_only_cover.py --run-name v6_promptlocal_short_token_numeric_guess_common_only_cover_default --write-training-bundle` を current branch で実行し、README 契約と canonical checks を通した上で bundle 再生成に成功
- Branch purpose: numeric support lane を common operators (`pool >= 4`) だけに限定し、tail-only branch と正面比較できる common-only ablation branch
- Execution note: `v20_mlx_v6_promptlocal_short_token_numeric_guess_tail_only_boost_mb1_nobc` の `training_result.json` 出現後にこの full pipeline が自動起動する detached queue を設定済み
- Post-run automation: `v6-promptlocal-short-token-common-only-train-watch` / `v6-promptlocal-short-token-common-only-eval-watch` に加えて、validation summary 出現後の measured diff-pack chain も armed

## Generated artifacts

- `versions/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_common_only_cover/outputs/v6_promptlocal_short_token_numeric_guess_common_only_cover_default/artifacts/corrective_selection.csv`
- `versions/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_common_only_cover/outputs/v6_promptlocal_short_token_numeric_guess_common_only_cover_default/artifacts/corrective_overlay_unique.jsonl`
- `versions/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_common_only_cover/outputs/v6_promptlocal_short_token_numeric_guess_common_only_cover_default/artifacts/corrective_overlay_repeated.jsonl`
- `versions/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_common_only_cover/outputs/v6_promptlocal_short_token_numeric_guess_common_only_cover_default/artifacts/corrective_overlay_summary.json`
- `versions/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_common_only_cover/outputs/v6_promptlocal_short_token_numeric_guess_common_only_cover_default/reports/corrective_overlay_report.md`

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
- total tokens: 28355214
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

## Numeric guess common-only slice

- `surface_numeric_answer_only` の 64 unique rows は **すべて** `equation_numeric_guess`
- selected operators は **10 common operators** (`pool >= 4`) のみ
- repeated common mix: `` ` 9``, `% 9`, `@ 12`, `\\ 15`, `[ 12`, `: 12`, `/ 15`, `* 42`, `- 33`, `+ 33`
- tail operators は意図的に不採用で、`tail-only` branch と対照になる

## Reassessment alignment check

### 1. `prompt-local short/token + numeric guess common only cover` requirements

- prompt-local exact rows の再活用: 満たす。`binary_prompt_local_exact` は `95` を維持した。
- short-closure rewrite lane: 満たす。`short_closure_commit 343` と `surface_short_closure 116` を維持した。
- token-skill auxiliary lane: 満たす。`binary_zero_skill 343` と `surface_token_skill 120` を維持した。
- numeric common-only lane: 満たす。`surface_numeric_answer_only 64` を common operators (`pool >= 4`) の `equation_numeric_guess` rows だけに限定した。
- heavier anti-`default 1` counterexample lane: 満たす。`anti_default1_commit 9` と `anti_default1_contrast_commit 9` を維持した。

### 2. 今回あえて入れていないもの

- tail operators (`pool <= 3`)
- broad `glyph_len5` / cryptarithm answer-only expansion
- risky な binary token representation change

### 3. README 契約との整合

- `README.md` と `A-Open-ProgressPrizePublication/README.md` の deterministic / boxed-first 契約を崩さず、README の `Coverage` 原則を common operators 側だけで検証する branch にした。
- `FINAL_SUMMARY_REPORT.md` の handoff に従い、`answer_only_keep` は full trace teacher ではなく final-answer support lane として扱った。
- `tail-only` / `common-only` の両 ablation を揃え、hidden/public でどちらが有効かを切り分けやすくした。

## Observed tradeoff before training

- overlay examples は `1746`、総 token は `28355214`。`tail-only` より重いが、`operator-cover` とほぼ同重量で比較しやすい。
- 10 common operators に集約しているため、tail-only concentration が効くのか、それとも大半の gain は common operators 由来かを直接比較できる。
- もしこの branch が最良なら、tail-only よりも common operator の反復量が public/proxy を支配していると判断できる。

## Next evaluation gate

- `promptlocal-short-token-numeric-guess-tail-only-boost` と本 branch を直接比較し、tail ではなく common operator 側が効いているのかを measured diff-pack で確認する。
- 改善するなら、numeric guess lane は common-only mainline と tail-only corrective を別系統で運用する。
