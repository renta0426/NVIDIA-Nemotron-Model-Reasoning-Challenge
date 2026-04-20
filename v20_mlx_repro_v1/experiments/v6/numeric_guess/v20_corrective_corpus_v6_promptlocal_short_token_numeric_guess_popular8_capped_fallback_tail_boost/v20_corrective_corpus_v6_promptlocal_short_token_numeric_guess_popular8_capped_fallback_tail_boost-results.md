# v20 corrective corpus v6 promptlocal-short-token-numeric-guess-popular8-capped-fallback-tail-boost results

## Status

- Created: 2026-04-18 UTC
- Generator: `v20_mlx_repro_v1/experiments/v6/numeric_guess/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_popular8_capped_fallback_tail_boost/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_popular8_capped_fallback_tail_boost.py`
- Run name: `v6_promptlocal_short_token_numeric_guess_popular8_capped_fallback_tail_boost_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_numeric_guess_popular8_capped_fallback_tail_boost_mb1_nobc`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_popular8_capped_fallback_tail_boost_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python v20_mlx_repro_v1/experiments/v6/numeric_guess/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_popular8_capped_fallback_tail_boost/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_popular8_capped_fallback_tail_boost.py --run-name v6_promptlocal_short_token_numeric_guess_popular8_capped_fallback_tail_boost_default --write-training-bundle` を current branch で実行し、README 契約と canonical checks を通した上で bundle 再生成に成功
- Branch purpose: `popular8_capped_tail_boost` の balanced 配分を保ったまま、top-8 の外にある fallback 2 operators (`%`, `` ` ``) にだけ最小追加 repeat を戻す branch
- Execution note: `v20_mlx_v6_promptlocal_short_token_numeric_guess_popular8_capped_tail_boost_mb1_nobc` の `training_result.json` 出現後にこの full pipeline が自動起動する detached queue を設定
- Post-run automation: `v6-promptlocal-short-token-popular8-fallback-train-watch` / `v6-promptlocal-short-token-popular8-fallback-eval-watch` に加えて、validation summary 出現後の measured diff-pack chain も armed

## Generated artifacts

- `v20_mlx_repro_v1/experiments/v6/numeric_guess/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_popular8_capped_fallback_tail_boost/outputs/v6_promptlocal_short_token_numeric_guess_popular8_capped_fallback_tail_boost_default/artifacts/corrective_selection.csv`
- `v20_mlx_repro_v1/experiments/v6/numeric_guess/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_popular8_capped_fallback_tail_boost/outputs/v6_promptlocal_short_token_numeric_guess_popular8_capped_fallback_tail_boost_default/artifacts/corrective_overlay_unique.jsonl`
- `v20_mlx_repro_v1/experiments/v6/numeric_guess/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_popular8_capped_fallback_tail_boost/outputs/v6_promptlocal_short_token_numeric_guess_popular8_capped_fallback_tail_boost_default/artifacts/corrective_overlay_repeated.jsonl`
- `v20_mlx_repro_v1/experiments/v6/numeric_guess/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_popular8_capped_fallback_tail_boost/outputs/v6_promptlocal_short_token_numeric_guess_popular8_capped_fallback_tail_boost_default/artifacts/corrective_overlay_summary.json`
- `v20_mlx_repro_v1/experiments/v6/numeric_guess/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_popular8_capped_fallback_tail_boost/outputs/v6_promptlocal_short_token_numeric_guess_popular8_capped_fallback_tail_boost_default/reports/corrective_overlay_report.md`

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
- surface_numeric_answer_only: 302
- easy_gravity_fragile: 18
- total repeated overlay rows: 1856

### Bundle footprint

- base examples: 7828
- overlay examples: 1856
- total examples: 9684
- total steps: 303
- total tokens: 28372324
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
- surface_short_closure_boost: 30
- surface_token_skill: 120
- surface_token_skill_boost: 16

## Canonical validation

- passed: True
- binary max think lines: 4
- surface max think lines: 3
- mandatory anchor missing: 0
- binary non-verified contamination: 0
- surface unexpected categories: 0

## Numeric guess popular8-capped-fallback slice

- `surface_numeric_answer_only` の 64 unique rows は **すべて** `equation_numeric_guess`
- answer-only 候補に存在した 26 operator を **26/26 で全カバー**
- popular8 unique mix は capped 版を維持し、**`+ 4`, `- 4`, `* 4`, `/ 4`, `: 3`, `@ 3`, `[ 3`, `\\ 3`**
- fallback operators `%` と `` ` `` は unique では coverage の **1 行ずつ**に留まったが、repeat は **`5` / `5`** まで戻した
- `popular8_capped_tail_boost` (`300 repeated`) に対して numeric repeated rows は **`302`** と +2 だけ増え、token もほぼ同等の軽量比較線になった

## Reassessment alignment check

### 1. `prompt-local short/token + numeric guess popular8 capped fallback tail boost` requirements

- prompt-local exact rows の再活用: 満たす。`binary_prompt_local_exact` は `95` を維持した。
- short-closure rewrite lane: 満たす。`short_closure_commit 343` と `surface_short_closure 116 + boost 30` を維持した。
- token-skill auxiliary lane: 満たす。`binary_zero_skill 343` と `surface_token_skill 120 + boost 16` を維持した。
- numeric guess operator coverage lane: 満たす。`surface_numeric_answer_only 64` を全件 `equation_numeric_guess` に振り切り、26 operator 全カバーを維持した。
- low-frequency tail row inclusion: 満たす。`pool <= 3` の 34 rows を unique selection で全件投入した。
- popular-8-first allocation: 満たす。popular8 capped 配分を維持した。
- fallback-2 support: 満たす。top-8 直下の `%` / `` ` `` に小さな repeat 追加を与えた。

### 2. 今回あえて入れていないもの

- broad `glyph_len5` / cryptarithm answer-only expansion
- risky な binary token representation change
- fallback operators への大きな unique 枠

### 3. README 契約との整合

- `README.md` と `A-Open-ProgressPrizePublication/README.md` の deterministic / boxed-first 契約を崩していない。
- `A-Open-ProgressPrizePublication/README.md:104` の popular-first / rarer-set 構造を、**popular8 capped + fallback2** の二段配分として実装した。
- `FINAL_SUMMARY_REPORT.md` の handoff に従い、`answer_only_keep` は full trace teacher ではなく final-answer support lane として扱った。

## Observed tradeoff before training

- overlay examples は `1856`、総 token は `28372324`。`common_tail_boost` とほぼ同重量で、`popular8_capped_tail_boost` よりわずかに重いだけ。
- popular8 capped のバランスは保たれたまま `%` と `` ` `` の repeat だけを足せたので、**balanced + tiny fallback** の純粋比較線になった。
- もしこの branch が capped 版より良ければ、README の popular-first は正しいが、rarer side にも最小 repeat を戻した方が hidden/public に効くと判断できる。

## Next evaluation gate

- `promptlocal-short-token-numeric-guess-popular8-capped-tail-boost` と本 branch を比較し、fallback2 repeat の追加が public/proxy を押し上げるかを measured diff-pack で確認する。
- さらに改善するなら、次は fallback2 の unique も 2 行まで増やす branch に進む。
