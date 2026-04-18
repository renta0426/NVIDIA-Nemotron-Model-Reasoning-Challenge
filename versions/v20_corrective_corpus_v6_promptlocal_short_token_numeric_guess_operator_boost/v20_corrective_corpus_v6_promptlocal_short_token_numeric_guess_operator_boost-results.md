# v20 corrective corpus v6 promptlocal-short-token-numeric-guess-operator-boost results

## Status

- Created: 2026-04-18 UTC
- Generator: `versions/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_operator_boost/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_operator_boost.py`
- Run name: `v6_promptlocal_short_token_numeric_guess_operator_boost_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_numeric_guess_operator_boost_mb1_nobc`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_operator_boost_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python versions/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_operator_boost/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_operator_boost.py --run-name v6_promptlocal_short_token_numeric_guess_operator_boost_default --write-training-bundle` を current branch で実行し、README 契約と canonical checks を通した上で bundle 再生成に成功
- Branch purpose: bit-other triple-hybrid と 26-operator coverage を維持したまま、low-frequency `equation_numeric_guess` operator にだけ追加 overlay を載せる rare-repeat branch
- Execution note: `v20_mlx_v6_promptlocal_short_token_numeric_guess_operator_cover_mb1_nobc` の `training_result.json` 出現後にこの full pipeline が自動起動する detached queue を設定済み
- Post-run automation: `v6-promptlocal-short-token-guess-boost-train-watch` / `v6-promptlocal-short-token-guess-boost-eval-watch` に加えて、validation summary 出現後の measured diff-pack chain も armed

## Generated artifacts

- `versions/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_operator_boost/outputs/v6_promptlocal_short_token_numeric_guess_operator_boost_default/artifacts/corrective_selection.csv`
- `versions/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_operator_boost/outputs/v6_promptlocal_short_token_numeric_guess_operator_boost_default/artifacts/corrective_overlay_unique.jsonl`
- `versions/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_operator_boost/outputs/v6_promptlocal_short_token_numeric_guess_operator_boost_default/artifacts/corrective_overlay_repeated.jsonl`
- `versions/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_operator_boost/outputs/v6_promptlocal_short_token_numeric_guess_operator_boost_default/artifacts/corrective_overlay_summary.json`
- `versions/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_operator_boost/outputs/v6_promptlocal_short_token_numeric_guess_operator_boost_default/reports/corrective_overlay_report.md`

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
- surface_numeric_answer_only: 288
- easy_gravity_fragile: 18
- total repeated overlay rows: 1842

### Bundle footprint

- base examples: 7828
- overlay examples: 1842
- total examples: 9670
- total steps: 303
- total tokens: 28370761
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
- surface_short_closure_boost: 21
- surface_token_skill: 120
- surface_token_skill_boost: 11

## Canonical validation

- passed: True
- binary max think lines: 4
- surface max think lines: 3
- mandatory anchor missing: 0
- binary non-verified contamination: 0
- surface unexpected categories: 0

## Numeric guess operator boost

- `surface_numeric_answer_only` の 64 unique rows は **すべて** `equation_numeric_guess`
- answer-only 候補に存在した 26 operator を **26/26 で全カバー**
- repeated numeric rows は `192 -> 288` へ増加し、増分 `96` は low-frequency operator 向け `_boost` overlay
- rare operator (`pool <= 2`) は +2 overlay、mid operator (`pool == 3`) は +1 overlay を追加
- repeated operator mix: `+ 24`, `- 40`, `* 36`, `/ 12`, `: 12`, `@ 8`, `\\ 20`, `[ 8`, `% 4`, `` ` 8``, `| 5`, `! 5`, `] 10`, `} 15`, `^ 10`, `) 5`, `{ 12`, `& 6`, `' 6`, `# 6`, `( 6`, `? 6`, `" 6`, `< 6`, `> 6`, `$ 6`

## Reassessment alignment check

### 1. `prompt-local short/token + numeric guess operator boost` requirements

- prompt-local exact rows の再活用: 満たす。`binary_prompt_local_exact` は `95` を維持した。
- short-closure rewrite lane: 満たす。`short_closure_commit 343` と `surface_short_closure 116 + boost 21` を維持した。
- token-skill auxiliary lane: 満たす。`binary_zero_skill 343` と `surface_token_skill 120 + boost 11` を維持した。
- numeric guess operator coverage lane: 満たす。`surface_numeric_answer_only 64` を全件 `equation_numeric_guess` に振り切り、26 operator 全カバーを維持した。
- rare-operator repeat boost: 満たす。`surface_boxed_tail_boost 64`, `surface_short_closure_boost 21`, `surface_token_skill_boost 11` を low-frequency operator にだけ追加した。
- heavier anti-`default 1` counterexample lane: 満たす。`anti_default1_commit 9` と `anti_default1_contrast_commit 9` を維持した。

### 2. 今回あえて入れていないもの

- broad `glyph_len5` / cryptarithm answer-only expansion
- risky な binary token representation change
- raw `manual_audit_priority` の直接投入

### 3. README 契約との整合

- `README.md` と `A-Open-ProgressPrizePublication/README.md` の deterministic / boxed-first 契約を崩さず、rare operator だけに追加 overlay を積んだ。
- `FINAL_SUMMARY_REPORT.md` の handoff に従い、`answer_only_keep` は full trace teacher ではなく final-answer support lane として扱った。
- README の `Coverage` 原則に合わせ、少数回しか現れない guess operator のトークン列を追加 repetition で補強した。

## Observed tradeoff before training

- overlay examples は `1842`、総 token は `28370761`。`operator-cover` 比で `+96` overlay examples、`+15208` tokens と増分はまだ小さい。
- unique rows は変えず repeated rows だけ増やしたので、`guess-heavy` や `operator-cover` と比較したときの差分要因が明確である。
- もしこの branch が悪化するなら、coverage 自体は有効でも rare-operator repeat boost が過学習寄りだったと切り分けられる。

## Next evaluation gate

- `promptlocal-short-token-numeric-guess-operator-cover` と本 branch を直接比較し、rare-operator repeat boost が `equation_numeric_guess` をさらに押し上げるか measured diff-pack で確認する。
- proxy/public 方向で改善するなら、以後の corrective ladder では numeric guess lane を `count -> coverage -> rare-repeat` の順で段階的に積む。
