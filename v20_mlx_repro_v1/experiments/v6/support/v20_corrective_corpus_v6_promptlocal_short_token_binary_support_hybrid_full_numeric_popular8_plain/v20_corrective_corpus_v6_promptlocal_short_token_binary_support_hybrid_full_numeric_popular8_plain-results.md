# v20 corrective corpus v6 promptlocal-short-token-binary-support-hybrid-full-numeric-popular8-plain results

## Status

- Created: 2026-04-19 UTC
- Generator: `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain.py`
- Run name: `v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_mb1_nobc`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain.py --run-name v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_default --write-training-bundle` を current branch で実行し、`README.md` と `A-Open-ProgressPrizePublication/README.md` の deterministic / boxed-first 契約を保ったまま canonical checks を通して bundle 再生成に成功
- Branch purpose: `hybrid_full_numeric_popular8` の full dual bit support を維持したまま、numeric lane の extra boost repeat をすべて外し、upper-bound 側でも coverage と repeat emphasis の寄与を切り分ける plain branch
- Execution note: `v20_mlx_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_mb1_nobc` の `training_result.json` 出現後にこの full pipeline が自動起動する detached queue を設定
- Post-run automation: `v6-promptlocal-short-token-binary-support-hybrid-full-numeric-popular8-plain-train-watch` / `v6-promptlocal-short-token-binary-support-hybrid-full-numeric-popular8-plain-eval-watch` に加えて、validation summary 出現後の measured diff-pack chain も armed

## Generated artifacts

- `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain/outputs/v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_default/artifacts/corrective_selection.csv`
- `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain/outputs/v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_default/artifacts/corrective_overlay_unique.jsonl`
- `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain/outputs/v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_default/artifacts/corrective_overlay_repeated.jsonl`
- `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain/outputs/v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_default/artifacts/corrective_overlay_summary.json`
- `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain/outputs/v6_promptlocal_short_token_binary_support_hybrid_full_numeric_popular8_plain_default/reports/corrective_overlay_report.md`

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
- surface_binary_prompt_local_answer_only: 96
- surface_binary_structured_answer_only: 96
- surface_numeric_answer_only: 64
- easy_gravity_fragile: 6
- total unique overlay problems: 655

### Repeated training rows

- binary_structured_exact_core: 618
- binary_logic_exact: 228
- binary_permutation_exact: 164
- binary_prompt_local_exact: 380
- surface_numeral_boxed: 102
- surface_cipher_boxed: 18
- surface_unit_tail: 18
- surface_symbol_prefix: 8
- surface_binary_prompt_local_answer_only: 288
- surface_binary_structured_answer_only: 288
- surface_numeric_answer_only: 192
- easy_gravity_fragile: 18
- total repeated overlay rows: 2322

### Bundle footprint

- base examples: 7828
- overlay examples: 2322
- total examples: 10150
- total steps: 318
- total tokens: 28530722
- max sequence length: 7971

### Overlay supervision styles

- exact_rule_commit: 343
- exact_closure_commit: 343
- short_closure_commit: 343
- binary_zero_skill: 343
- anti_default1_commit: 9
- anti_default1_contrast_commit: 9
- surface_boxed_tail: 312
- surface_short_closure: 308
- surface_token_skill: 312

## Canonical validation

- passed: True
- binary max think lines: 4
- surface max think lines: 3
- mandatory anchor missing: 0
- binary non-verified contamination: 0
- surface unexpected categories: 0

## Full dual bit support + plain numeric popular8 slice

- prompt-local support lane は `surface_binary_prompt_local_answer_only` として **96 unique / 288 repeated**
- structured support lane は `surface_binary_structured_answer_only` として **96 unique / 288 repeated**
- numeric support lane は `surface_numeric_answer_only` として **64 unique / 192 repeated**
- overlay token は prompt-local support `86787`、structured support `90471`、numeric support `28423`
- overlay token share は prompt-local `0.1247`、structured `0.1300`、numeric `0.0408` で、combined bit+numeric support share は `0.2955`
- `hybrid_full_numeric_popular8` 比で overlay は `2430 -> 2322`、total tokens は `28549228 -> 28530722` と減り、差分はほぼ **numeric boost repeat 108 rows の削除**に一致する

## Plain numeric popular8 slice

- `surface_numeric_answer_only` の 64 unique rows は **すべて** `equation_numeric_guess`
- answer-only 候補に存在した 26 operator を **26/26 で全カバー**
- popular8/fallback unique selection は boost 版と同一で、guess unique mix は `+ 4`, `- 4`, `* 3`, `/ 3`, `: 3`, `@ 3`, `[ 3`, `\\ 3`, fallback `%` / backtick operator `2`
- numeric lane は **plain 3-style only** に固定し、`surface_boxed_tail_boost` / `surface_short_closure_boost` / `surface_token_skill_boost` を完全に外した
- numeric repeated rows は `300 -> 192`、overlay tokens は `45398 -> 28423`、numeric token share は `0.0637 -> 0.0408` に下がった

## Reassessment alignment check

### 1. `hybrid full + numeric popular8 plain` requirements

- prompt-local exact rows の再活用: 満たす。verified exact は `95` を維持した
- structured exact rows の再活用: 満たす。structured core `152` を維持した
- short-closure rewrite lane: 満たす。`short_closure_commit 343` と `surface_short_closure 308` を維持した
- token-skill auxiliary lane: 満たす。`binary_zero_skill 343` と `surface_token_skill 312` を維持した
- answer-only separate lanes: 満たす。prompt-local / structured / numeric の answer-only rows を verified exact lane に混ぜず support lane のみに隔離した
- popular-8-first numeric allocation: 満たす。popular8 を主枠にしつつ fallback2 unique rows も確保した
- boxed-first / deterministic contract: 満たす。`README.md` と `A-Open-ProgressPrizePublication/README.md` の boxed-first / deterministic 契約を崩していない

### 2. 今回あえて入れていないもの

- numeric boost repeat
- numeric deduce reserve
- risky な binary token representation change

### 3. README / reassessment に対する位置づけ

- `A-Open-ProgressPrizePublication/README.md` の popular8-first 方針を保ちながら、upper-bound 側でも coverage だけでどこまで効くかを見る pure coverage branch である
- `versions/v20_to_088_reassessment_2026-04-18.md` の separate-lane 方針を保ったまま、numeric lane の repeat emphasis を切り落とした upper-bound ablation である

## Observed tradeoff before training

- upper-bound numeric grid の中では最も lightweight で、boost 版や mixed 版より token budget が明確に軽い
- その代わり numeric lane の emphasis は unique coverage と 3-style surface teacher に限られ、popular operators への explicit over-sampling は消えている

## Next evaluation gate

- `hybrid_full_numeric_popular8_plain` / `hybrid_full_numeric_popular8` / `hybrid_full_numeric_mixed` を直接比較し、upper-bound 側での numeric lane の improvement が coverage・boost・deduce reserve のどれに主に由来するかを measured diff-pack で判定する
