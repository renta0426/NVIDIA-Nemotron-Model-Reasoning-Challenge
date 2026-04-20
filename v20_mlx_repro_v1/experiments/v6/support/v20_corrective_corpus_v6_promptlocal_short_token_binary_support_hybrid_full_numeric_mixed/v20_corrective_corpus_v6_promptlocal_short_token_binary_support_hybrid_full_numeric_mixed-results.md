# v20 corrective corpus v6 promptlocal-short-token-binary-support-hybrid-full-numeric-mixed results

## Status

- Created: 2026-04-19 UTC
- Generator: `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_mixed/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_mixed.py`
- Run name: `v6_promptlocal_short_token_binary_support_hybrid_full_numeric_mixed_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_mixed_mb1_nobc`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_mixed_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_mixed/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_mixed.py --run-name v6_promptlocal_short_token_binary_support_hybrid_full_numeric_mixed_default --write-training-bundle` を current branch で実行し、`README.md` と `A-Open-ProgressPrizePublication/README.md` の deterministic / boxed-first 契約を保ったまま canonical checks を通して bundle 再生成に成功
- Branch purpose: `hybrid_full_numeric_popular8` の full dual bit support を維持したまま、numeric lane を **guess 48 + deduce 16** の mixed support へ差し替え、2x2 grid の upper-bound mixed 比較線を作る branch
- Execution note: `v20_mlx_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_mixed_mb1_nobc` の `training_result.json` 出現後にこの full pipeline が自動起動する detached queue を設定
- Post-run automation: `v6-promptlocal-short-token-binary-support-hybrid-full-numeric-mixed-train-watch` / `v6-promptlocal-short-token-binary-support-hybrid-full-numeric-mixed-eval-watch` に加えて、validation summary 出現後の measured diff-pack chain も armed

## Generated artifacts

- `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_mixed/outputs/v6_promptlocal_short_token_binary_support_hybrid_full_numeric_mixed_default/artifacts/corrective_selection.csv`
- `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_mixed/outputs/v6_promptlocal_short_token_binary_support_hybrid_full_numeric_mixed_default/artifacts/corrective_overlay_unique.jsonl`
- `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_mixed/outputs/v6_promptlocal_short_token_binary_support_hybrid_full_numeric_mixed_default/artifacts/corrective_overlay_repeated.jsonl`
- `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_mixed/outputs/v6_promptlocal_short_token_binary_support_hybrid_full_numeric_mixed_default/artifacts/corrective_overlay_summary.json`
- `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_full_numeric_mixed/outputs/v6_promptlocal_short_token_binary_support_hybrid_full_numeric_mixed_default/reports/corrective_overlay_report.md`

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
- surface_numeric_answer_only: 288
- easy_gravity_fragile: 18
- total repeated overlay rows: 2418

### Bundle footprint

- base examples: 7828
- overlay examples: 2418
- total examples: 10246
- total steps: 321
- total tokens: 28547725
- max sequence length: 7971

### Overlay supervision styles

- exact_rule_commit: 343
- exact_closure_commit: 343
- short_closure_commit: 343
- binary_zero_skill: 343
- anti_default1_commit: 9
- anti_default1_contrast_commit: 9
- surface_boxed_tail: 312
- surface_boxed_tail_boost: 48
- surface_short_closure: 308
- surface_short_closure_boost: 32
- surface_token_skill: 312
- surface_token_skill_boost: 16

## Canonical validation

- passed: True
- binary max think lines: 4
- surface max think lines: 3
- mandatory anchor missing: 0
- binary non-verified contamination: 0
- surface unexpected categories: 0

## Full dual bit support + mixed numeric slice

- prompt-local support lane は `surface_binary_prompt_local_answer_only` として **96 unique / 288 repeated**
- structured support lane は `surface_binary_structured_answer_only` として **96 unique / 288 repeated**
- numeric support lane は `surface_numeric_answer_only` として **64 unique / 288 repeated**
- numeric unique mix は **`equation_numeric_guess 48` + `equation_numeric_deduce 16`**
- overlay token は prompt-local support `86787`、structured support `90471`、numeric support `43895`
- overlay token share は prompt-local `0.1220`、structured `0.1272`、numeric `0.0617` で、combined bit+numeric support share は `0.3109`
- `hybrid_full_numeric_popular8` 比で overlay は `2430 -> 2418`、total tokens は `28549228 -> 28547725` と **slightly lighter** で、guess-only 64 を mixed lane へ振り直しても token budget は増えていない
- `hybrid_expanded_numeric_mixed` 比では structured support だけが `64 / 192 -> 96 / 288` に増え、overlay は `2322 -> 2418`、total tokens は `28519373 -> 28547725` と **structured lane 追加分の 28352 tokens** だけ増えた

## Mixed numeric support slice

- `surface_numeric_answer_only` は deduce mandatory anchor と衝突する `surface_symbol_prefix` mandatory ID を避けた上で構成した
- `equation_numeric_deduce` 側は **16 unique / 48 repeated** の軽量 lane とし、boxed-tail / short-closure / token-skill の 3-style のみで surface undertraining を補う
- `equation_numeric_guess` 側は **48 unique / 240 repeated** を popular-first で選抜し、boost は guess rows にだけ残した
- popular8 unique mix は `* 4`, `+ 4`, `- 4`, `/ 4`, `: 3`, `@ 3`, `[ 3`, `\\ 3`
- fallback operators `%` と `` ` `` は **`2 unique`** を維持し、rare tail operator も one-per-operator で薄く残した
- numeric boost style は `surface_boxed_tail_boost 48`, `surface_short_closure_boost 32`, `surface_token_skill_boost 16`

## Reassessment alignment check

### 1. `hybrid full + mixed numeric support` requirements

- prompt-local exact rows の再活用: 満たす。verified exact は `95` を維持した
- structured exact rows の再活用: 満たす。structured core `152` を維持した
- short-closure rewrite lane: 満たす。`short_closure_commit 343` と `surface_short_closure 308 + boost 32` を維持した
- token-skill auxiliary lane: 満たす。`binary_zero_skill 343` と `surface_token_skill 312 + boost 16` を維持した
- answer-only separate lanes: 満たす。prompt-local / structured / numeric の answer-only rows を verified exact lane に混ぜず support lane のみに隔離した
- popular-first numeric allocation: 満たす。guess 側は popular8 を主枠にしつつ、deduce reserve を 16 行だけ確保した
- boxed-first / deterministic contract: 満たす。`README.md` と `A-Open-ProgressPrizePublication/README.md` の boxed-first / deterministic 契約を崩していない

### 2. 今回あえて入れていないもの

- numeric guess 26/26 full coverage の維持
- answer-only rows の full CoT teacher 化
- risky な binary token representation change

### 3. README / reassessment に対する位置づけ

- `A-Open-ProgressPrizePublication/README.md` の popular8-first 方針を保ちながら、live v4 partial で弱く見える `equation_numeric_deduce` を small reserve で拾う upper-bound branch である
- `versions/v20_to_088_reassessment_2026-04-18.md` の separate-lane 方針を保ったまま、bit full support と mixed numeric lane を同時に載せた 2x2 grid の右上比較線である

## Observed tradeoff before training

- `hybrid_full_numeric_popular8` の差分はほぼ **guess 64-only -> guess 48 + deduce 16** の振り直しに一致する
- total tokens はわずかに軽く、numeric token share も `0.0637 -> 0.0617` へ少し下がった
- その代わり guess unique coverage は 26/26 を維持しつつ、popular operators の unique massをやや圧縮して deduce reserve を作っている

## Next evaluation gate

- `hybrid_full_numeric_popular8` と本 branch を直接比較し、deduce reserve の small lane が full dual bit support 下でも `equation_numeric_guess` popular-first gainを壊さずに効くかを measured diff-pack で判定する
- もし本 branch が悪化するなら、numeric lane は upper-bound 側でも guess-only popular-first に寄せるべきで、deduce は別 lane として切り出す
