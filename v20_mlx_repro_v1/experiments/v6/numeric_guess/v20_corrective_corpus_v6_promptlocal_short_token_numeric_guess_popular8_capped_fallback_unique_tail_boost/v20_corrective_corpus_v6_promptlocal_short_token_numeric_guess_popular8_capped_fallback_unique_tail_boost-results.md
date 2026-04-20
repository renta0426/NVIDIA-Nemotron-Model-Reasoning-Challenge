# v20 corrective corpus v6 promptlocal-short-token-numeric-guess-popular8-capped-fallback-unique-tail-boost results

## Status

- Created: 2026-04-18 UTC
- Generator: `v20_mlx_repro_v1/experiments/v6/numeric_guess/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_popular8_capped_fallback_unique_tail_boost/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_popular8_capped_fallback_unique_tail_boost.py`
- Run name: `v6_promptlocal_short_token_numeric_guess_popular8_capped_fallback_unique_tail_boost_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_numeric_guess_popular8_capped_fallback_unique_tail_boost_mb1_nobc`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_popular8_capped_fallback_unique_tail_boost_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python v20_mlx_repro_v1/experiments/v6/numeric_guess/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_popular8_capped_fallback_unique_tail_boost/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_popular8_capped_fallback_unique_tail_boost.py --run-name v6_promptlocal_short_token_numeric_guess_popular8_capped_fallback_unique_tail_boost_default --write-training-bundle` を current branch で実行し、README 契約と canonical checks を通した上で bundle 再生成に成功
- Branch purpose: `popular8_capped_fallback_tail_boost` の次段として、fallback operators (`%`, `` ` ``) の **second unique row を先に確保**し、その上で popular8 extra unique を詰める branch
- Execution note: `v20_mlx_v6_promptlocal_short_token_numeric_guess_popular8_capped_fallback_tail_boost_mb1_nobc` の `training_result.json` 出現後にこの full pipeline が自動起動する detached queue を設定
- Post-run automation: `v6-promptlocal-short-token-popular8-fallback-unique-train-watch` / `v6-promptlocal-short-token-popular8-fallback-unique-eval-watch` に加えて、validation summary 出現後の measured diff-pack chain も armed

## Generated artifacts

- `v20_mlx_repro_v1/experiments/v6/numeric_guess/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_popular8_capped_fallback_unique_tail_boost/outputs/v6_promptlocal_short_token_numeric_guess_popular8_capped_fallback_unique_tail_boost_default/artifacts/corrective_selection.csv`
- `v20_mlx_repro_v1/experiments/v6/numeric_guess/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_popular8_capped_fallback_unique_tail_boost/outputs/v6_promptlocal_short_token_numeric_guess_popular8_capped_fallback_unique_tail_boost_default/artifacts/corrective_overlay_unique.jsonl`
- `v20_mlx_repro_v1/experiments/v6/numeric_guess/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_popular8_capped_fallback_unique_tail_boost/outputs/v6_promptlocal_short_token_numeric_guess_popular8_capped_fallback_unique_tail_boost_default/artifacts/corrective_overlay_repeated.jsonl`
- `v20_mlx_repro_v1/experiments/v6/numeric_guess/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_popular8_capped_fallback_unique_tail_boost/outputs/v6_promptlocal_short_token_numeric_guess_popular8_capped_fallback_unique_tail_boost_default/artifacts/corrective_overlay_summary.json`
- `v20_mlx_repro_v1/experiments/v6/numeric_guess/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_popular8_capped_fallback_unique_tail_boost/outputs/v6_promptlocal_short_token_numeric_guess_popular8_capped_fallback_unique_tail_boost_default/reports/corrective_overlay_report.md`

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
- surface_numeric_answer_only: 300
- easy_gravity_fragile: 18
- total repeated overlay rows: 1854

### Bundle footprint

- base examples: 7828
- overlay examples: 1854
- total examples: 9682
- total steps: 303
- total tokens: 28371970
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
- surface_token_skill_boost: 14

## Canonical validation

- passed: True
- binary max think lines: 4
- surface max think lines: 3
- mandatory anchor missing: 0
- binary non-verified contamination: 0
- surface unexpected categories: 0

## Numeric guess popular8-capped-fallback-unique slice

- `surface_numeric_answer_only` の 64 unique rows は **すべて** `equation_numeric_guess`
- answer-only 候補に存在した 26 operator を **26/26 で全カバー**
- popular8 unique mix は `+ 4`, `- 4`, `* 3`, `/ 3`, `: 3`, `@ 3`, `[ 3`, `\\ 3` へ少し圧縮し、そのぶん fallback operators `%` と `` ` `` を **`2 unique / 10 repeated`** まで増やした
- `popular8_capped_fallback_tail_boost` (`302 repeated`) に対して numeric repeated rows は **`300`** に下がるが、fallback 側の unique generalization を明示的に増やせた
- `surface_token_skill_boost` も `16 -> 14` にわずかに下がり、bundle 総量は fallback-repeat 版より軽くなった

## Reassessment alignment check

### 1. `prompt-local short/token + numeric guess popular8 capped fallback unique tail boost` requirements

- prompt-local exact rows の再活用: 満たす。`binary_prompt_local_exact` は `95` を維持した。
- short-closure rewrite lane: 満たす。`short_closure_commit 343` と `surface_short_closure 116 + boost 30` を維持した。
- token-skill auxiliary lane: 満たす。`binary_zero_skill 343` と `surface_token_skill 120 + boost 14` を維持した。
- numeric guess operator coverage lane: 満たす。`surface_numeric_answer_only 64` を全件 `equation_numeric_guess` に振り切り、26 operator 全カバーを維持した。
- low-frequency tail row inclusion: 満たす。`pool <= 3` の 34 rows を unique selection で全件投入した。
- popular-8-first allocation: 満たす。popular8 が依然として主枠を維持している。
- fallback second unique rows: 満たす。fallback `%` / `` ` ``` に second unique row を先に確保するループ順へ変更した。

### 2. 今回あえて入れていないもの

- broad `glyph_len5` / cryptarithm answer-only expansion
- risky な binary token representation change
- fallback operators を popular8 と同等まで膨らませる強い再配分

### 3. README 契約との整合

- `README.md` と `A-Open-ProgressPrizePublication/README.md` の deterministic / boxed-first 契約を崩していない。
- `A-Open-ProgressPrizePublication/README.md:104` の popular-first / rarer-set 構造を、**popular8 capped + fallback2 unique/repeat** の二段配分として実装した。
- `FINAL_SUMMARY_REPORT.md` の handoff に従い、`answer_only_keep` は full trace teacher ではなく final-answer support lane として扱った。

## Observed tradeoff before training

- overlay examples は `1854`、総 token は `28371970`。`popular8_capped_tail_boost` と同重量帯で、fallback-repeat 版よりも軽い。
- fallback-repeat 版が `%` / `` ` `` を `1 unique / 5 repeated` に留めたのに対し、本 branch は **`2 unique / 10 repeated`** を実現した。
- そのコストは popular8 の一部 unique を `4 -> 3` へ一段下げる程度に留まっており、README の popular-first 骨格は維持できている。

## Next evaluation gate

- `popular8_capped_tail_boost` / `popular8_capped_fallback_tail_boost` / 本 branch の 3 本で、fallback 側の repeat だけ足すのが良いか、unique まで増やすのが良いかを measured diff-pack で比較する。
- さらに改善するなら、次は fallback2 を `%` / `` ` `` 固定ではなく README popular ranking の 9-10 位で自動選定する一般化版に進む。
