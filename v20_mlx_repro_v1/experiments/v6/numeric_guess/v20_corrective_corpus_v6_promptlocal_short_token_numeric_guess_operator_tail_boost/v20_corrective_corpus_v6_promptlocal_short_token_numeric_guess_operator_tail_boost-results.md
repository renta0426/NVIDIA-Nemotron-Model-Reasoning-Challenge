# v20 corrective corpus v6 promptlocal-short-token-numeric-guess-operator-tail-boost results

## Status

- Created: 2026-04-18 UTC
- Generator: `v20_mlx_repro_v1/experiments/v6/numeric_guess/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_operator_tail_boost/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_operator_tail_boost.py`
- Run name: `v6_promptlocal_short_token_numeric_guess_operator_tail_boost_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_numeric_guess_operator_tail_boost_mb1_nobc`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_operator_tail_boost_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python v20_mlx_repro_v1/experiments/v6/numeric_guess/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_operator_tail_boost/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_operator_tail_boost.py --run-name v6_promptlocal_short_token_numeric_guess_operator_tail_boost_default --write-training-bundle` を current branch で実行し、README 契約と canonical checks を通した上で bundle 再生成に成功
- Branch purpose: operator-boost の rare-repeat を維持しつつ、`equation_numeric_guess` の low-frequency operator rows (`pool <= 3`) を unique selection で **全件投入**する tail branch
- Execution note: `v20_mlx_v6_promptlocal_short_token_numeric_guess_operator_boost_mb1_nobc` の `training_result.json` 出現後にこの full pipeline が自動起動する detached queue を設定済み
- Post-run automation: `v6-promptlocal-short-token-guess-tail-train-watch` / `v6-promptlocal-short-token-guess-tail-eval-watch` に加えて、validation summary 出現後の measured diff-pack chain も armed

## Generated artifacts

- `v20_mlx_repro_v1/experiments/v6/numeric_guess/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_operator_tail_boost/outputs/v6_promptlocal_short_token_numeric_guess_operator_tail_boost_default/artifacts/corrective_selection.csv`
- `v20_mlx_repro_v1/experiments/v6/numeric_guess/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_operator_tail_boost/outputs/v6_promptlocal_short_token_numeric_guess_operator_tail_boost_default/artifacts/corrective_overlay_unique.jsonl`
- `v20_mlx_repro_v1/experiments/v6/numeric_guess/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_operator_tail_boost/outputs/v6_promptlocal_short_token_numeric_guess_operator_tail_boost_default/artifacts/corrective_overlay_repeated.jsonl`
- `v20_mlx_repro_v1/experiments/v6/numeric_guess/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_operator_tail_boost/outputs/v6_promptlocal_short_token_numeric_guess_operator_tail_boost_default/artifacts/corrective_overlay_summary.json`
- `v20_mlx_repro_v1/experiments/v6/numeric_guess/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_operator_tail_boost/outputs/v6_promptlocal_short_token_numeric_guess_operator_tail_boost_default/reports/corrective_overlay_report.md`

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
- surface_numeric_answer_only: 306
- easy_gravity_fragile: 18
- total repeated overlay rows: 1860

### Bundle footprint

- base examples: 7828
- overlay examples: 1860
- total examples: 9688
- total steps: 304
- total tokens: 28372850
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
- surface_short_closure_boost: 34
- surface_token_skill: 120
- surface_token_skill_boost: 16

## Canonical validation

- passed: True
- binary max think lines: 4
- surface max think lines: 3
- mandatory anchor missing: 0
- binary non-verified contamination: 0
- surface unexpected categories: 0

## Numeric guess tail coverage

- `surface_numeric_answer_only` の 64 unique rows は **すべて** `equation_numeric_guess`
- answer-only 候補に存在した 26 operator を **26/26 で全カバー**
- `pool <= 3` の tail operators は **16 operator / 34 rows** あり、この 34 rows を unique selection で全件投入
- repeated numeric rows は `288 -> 306` へ増加し、tail rows に `surface_short_closure_boost 34` / `surface_token_skill_boost 16` を追加した
- repeated operator mix: `+ 20`, `- 24`, `* 20`, `/ 4`, `: 12`, `@ 8`, `\\ 16`, `[ 4`, `% 4`, `` ` 8``, `| 15`, `! 15`, `] 15`, `} 15`, `^ 15`, `) 15`, `{ 12`, `& 12`, `' 12`, `# 12`, `( 12`, `? 12`, `" 6`, `< 6`, `> 6`, `$ 6`

## Reassessment alignment check

### 1. `prompt-local short/token + numeric guess operator tail boost` requirements

- prompt-local exact rows の再活用: 満たす。`binary_prompt_local_exact` は `95` を維持した。
- short-closure rewrite lane: 満たす。`short_closure_commit 343` と `surface_short_closure 116 + boost 34` を維持した。
- token-skill auxiliary lane: 満たす。`binary_zero_skill 343` と `surface_token_skill 120 + boost 16` を維持した。
- numeric guess operator coverage lane: 満たす。`surface_numeric_answer_only 64` を全件 `equation_numeric_guess` に振り切り、26 operator 全カバーを維持した。
- low-frequency tail row inclusion: 満たす。`pool <= 3` の 34 rows を unique selection で全件投入した。
- heavier anti-`default 1` counterexample lane: 満たす。`anti_default1_commit 9` と `anti_default1_contrast_commit 9` を維持した。

### 2. 今回あえて入れていないもの

- broad `glyph_len5` / cryptarithm answer-only expansion
- risky な binary token representation change
- raw `manual_audit_priority` の直接投入

### 3. README 契約との整合

- `README.md` と `A-Open-ProgressPrizePublication/README.md` の deterministic / boxed-first 契約を崩さず、tail operator coverage を `answer_only_keep` の support lane だけで強化した。
- `FINAL_SUMMARY_REPORT.md` の handoff に従い、`answer_only_keep` は full trace teacher ではなく final-answer support lane として扱った。
- README の `Coverage` 原則に沿って、単に operator を 1 回ずつ載せるだけでなく、low-frequency operator rows そのものを丸ごと bundle に載せた。

## Observed tradeoff before training

- overlay examples は `1860`、総 token は `28372850`。`operator-boost` 比で `+18` overlay examples、`+2089` tokens と増分はかなり小さい。
- unique rows の差分は numeric tail selection に限定されており、`operator-boost` との比較で low-frequency tail row inclusion の効果を切り分けやすい。
- もしこの branch が悪化するなら、rare-repeat までは有効でも tail rows 全件投入は過剰だったと判断できる。

## Next evaluation gate

- `promptlocal-short-token-numeric-guess-operator-boost` と本 branch を直接比較し、tail row inclusion が `equation_numeric_guess` の rare/operator-long-tail をさらに押し上げるか measured diff-pack で確認する。
- proxy/public 方向で改善するなら、以後の corrective ladder では numeric guess lane を `coverage -> rare-repeat -> tail-row inclusion` の順で段階的に積む。
