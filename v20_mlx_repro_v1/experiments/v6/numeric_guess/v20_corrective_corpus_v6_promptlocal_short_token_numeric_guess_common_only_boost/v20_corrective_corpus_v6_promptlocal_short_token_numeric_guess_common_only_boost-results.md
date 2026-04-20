# v20 corrective corpus v6 promptlocal-short-token-numeric-guess-common-only-boost results

## Status

- Created: 2026-04-18 UTC
- Generator: `v20_mlx_repro_v1/experiments/v6/numeric_guess/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_common_only_boost/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_common_only_boost.py`
- Run name: `v6_promptlocal_short_token_numeric_guess_common_only_boost_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_numeric_guess_common_only_boost_mb1_nobc`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_common_only_boost_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python v20_mlx_repro_v1/experiments/v6/numeric_guess/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_common_only_boost/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_common_only_boost.py --run-name v6_promptlocal_short_token_numeric_guess_common_only_boost_default --write-training-bundle` を current branch で実行し、README 契約と canonical checks を通した上で bundle 再生成に成功
- Branch purpose: numeric support lane を common operators (`pool >= 4`) のみに限定しつつ、common pool にだけ追加 repetition を積んで tail-only / common-only-cover の次段比較線を作る boost branch
- Execution note: `v20_mlx_v6_promptlocal_short_token_numeric_guess_common_only_cover_mb1_nobc` の `training_result.json` 出現後にこの full pipeline が自動起動する detached queue を設定
- Post-run automation: `v6-promptlocal-short-token-common-boost-train-watch` / `v6-promptlocal-short-token-common-boost-eval-watch` に加えて、validation summary 出現後の measured diff-pack chain も armed

## Generated artifacts

- `v20_mlx_repro_v1/experiments/v6/numeric_guess/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_common_only_boost/outputs/v6_promptlocal_short_token_numeric_guess_common_only_boost_default/artifacts/corrective_selection.csv`
- `v20_mlx_repro_v1/experiments/v6/numeric_guess/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_common_only_boost/outputs/v6_promptlocal_short_token_numeric_guess_common_only_boost_default/artifacts/corrective_overlay_unique.jsonl`
- `v20_mlx_repro_v1/experiments/v6/numeric_guess/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_common_only_boost/outputs/v6_promptlocal_short_token_numeric_guess_common_only_boost_default/artifacts/corrective_overlay_repeated.jsonl`
- `v20_mlx_repro_v1/experiments/v6/numeric_guess/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_common_only_boost/outputs/v6_promptlocal_short_token_numeric_guess_common_only_boost_default/artifacts/corrective_overlay_summary.json`
- `v20_mlx_repro_v1/experiments/v6/numeric_guess/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_common_only_boost/outputs/v6_promptlocal_short_token_numeric_guess_common_only_boost_default/reports/corrective_overlay_report.md`

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
- surface_numeric_answer_only: 356
- easy_gravity_fragile: 18
- total repeated overlay rows: 1910

### Bundle footprint

- base examples: 7828
- overlay examples: 1910
- total examples: 9738
- total steps: 305
- total tokens: 28380265
- max sequence length: 7971

### Overlay supervision styles

- exact_rule_commit: 343
- exact_closure_commit: 343
- short_closure_commit: 343
- binary_zero_skill: 343
- anti_default1_commit: 9
- anti_default1_contrast_commit: 9
- surface_boxed_tail: 120
- surface_boxed_tail_boost: 64
- surface_short_closure: 116
- surface_short_closure_boost: 64
- surface_token_skill: 120
- surface_token_skill_boost: 36

## Canonical validation

- passed: True
- binary max think lines: 4
- surface max think lines: 3
- mandatory anchor missing: 0
- binary non-verified contamination: 0
- surface unexpected categories: 0

## Numeric guess common-only boost slice

- `surface_numeric_answer_only` の 64 unique rows は **すべて** `equation_numeric_guess`
- selected operators は **10 common operators** (`pool >= 4`) のみ: `%`, `*`, `+`, `-`, `/`, `:`, `@`, `[`, `\\`, `` ` ``
- repeated common mix は `% 15`, `* 84`, `+ 66`, `- 66`, `/ 25`, `: 20`, `@ 20`, `[ 20`, `\\ 25`, `` ` 15``
- boost は `pool >= 10` に +2 repeat、`4 <= pool < 10` に +1 repeat を加える設計で、`surface_numeric_answer_only` repeated rows を common-only-cover の `192` から `356` へ増やした

## Reassessment alignment check

### 1. `prompt-local short/token + numeric guess common only boost` requirements

- prompt-local exact rows の再活用: 満たす。`binary_prompt_local_exact` は `95` を維持した。
- short-closure rewrite lane: 満たす。`short_closure_commit 343` と `surface_short_closure 116 + boost 64` を維持した。
- token-skill auxiliary lane: 満たす。`binary_zero_skill 343` と `surface_token_skill 120 + boost 36` を維持した。
- numeric common-only lane: 満たす。`surface_numeric_answer_only 64` を common operators (`pool >= 4`) の `equation_numeric_guess` rows だけに限定した。
- numeric common-only boost lane: 満たす。common pool repetition を明示 duplicate overlay row で追加し、surface bucket の style 上限を突破した。
- heavier anti-`default 1` counterexample lane: 満たす。`anti_default1_commit 9` と `anti_default1_contrast_commit 9` を維持した。

### 2. 今回あえて入れていないもの

- tail operators (`pool <= 3`)
- broad `glyph_len5` / cryptarithm answer-only expansion
- risky な binary token representation change

### 3. README 契約との整合

- `README.md` と `A-Open-ProgressPrizePublication/README.md` の deterministic / boxed-first 契約を崩さず、README の `Coverage` 原則を common operators 側だけで boosted repetition として検証する branch にした。
- `FINAL_SUMMARY_REPORT.md` の handoff に従い、`answer_only_keep` は full trace teacher ではなく final-answer support lane として扱った。
- `tail-only` / `common-only-cover` / `common-only-boost` の 3 本を揃え、tail concentration より common repetition の方が効くかを切り分けやすくした。

## Observed tradeoff before training

- overlay examples は `1910`、総 token は `28380265`。common-only-cover より少し重いが、still full-run 比較可能な範囲に収まっている。
- surface numeric boost は `surface_boxed_tail_boost` と `surface_short_closure_boost` が各 `64`、`surface_token_skill_boost` が `36`。`build_supervision_variants()` の surface 上限を duplicate row で破ったことが反映されている。
- もしこの branch が最良なら、numeric guess lane は common operator coverage だけでなく common repetition volume 自体が public/proxy を支配していると判断できる。

## Next evaluation gate

- `promptlocal-short-token-numeric-guess-common-only-cover` と本 branch を直接比較し、common repetition の純増分が効くかを measured diff-pack で確認する。
- 改善するなら、numeric guess lane は `common-only mainline + tail corrective` の二層構成か、`very-common boost + tail cover` の折衷 branch に進む。
