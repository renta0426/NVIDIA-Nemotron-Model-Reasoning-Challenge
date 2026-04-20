# v20 corrective corpus v6 promptlocal-short-token-binary-support-hybrid-expanded-numeric-popular8 results

## Status

- Created: 2026-04-19 UTC
- Generator: `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8.py`
- Run name: `v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_mb1_nobc`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8.py --run-name v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_default --write-training-bundle` を current branch で実行し、`README.md` と `A-Open-ProgressPrizePublication/README.md` の deterministic / boxed-first 契約を保ったまま canonical checks を通して bundle 再生成に成功
- Branch purpose: `promptlocal_short_token_binary_support_hybrid_expanded` の dual bit support を維持したまま、`equation_numeric_guess` の popular8 capped fallback-unique answer-only lane を重ね、README が指す bit と numeric の両 headroom を同時に叩く branch
- Execution note: `v20_mlx_v6_promptlocal_short_token_binary_support_hybrid_full_mb1_nobc` の `training_result.json` 出現後にこの full pipeline が自動起動する detached queue を設定
- Post-run automation: `v6-promptlocal-short-token-binary-support-hybrid-expanded-numeric-popular8-train-watch` / `v6-promptlocal-short-token-binary-support-hybrid-expanded-numeric-popular8-eval-watch` に加えて、validation summary 出現後の measured diff-pack chain も armed
- Watcher note (2026-04-20): `v20_mlx_repro_v1/outputs/v6/support` 配下で actual grouped-root train/eval watcher を再配置し、predecessor `training_result.json` 待ちの launch queue と train 完了後の adapter-validation / postprocess を実体として arm した

## Generated artifacts

- `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8/outputs/v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_default/artifacts/corrective_selection.csv`
- `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8/outputs/v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_default/artifacts/corrective_overlay_unique.jsonl`
- `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8/outputs/v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_default/artifacts/corrective_overlay_repeated.jsonl`
- `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8/outputs/v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_default/artifacts/corrective_overlay_summary.json`
- `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8/outputs/v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_default/reports/corrective_overlay_report.md`

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
- surface_binary_structured_answer_only: 64
- surface_numeric_answer_only: 64
- easy_gravity_fragile: 6
- total unique overlay problems: 623

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
- surface_binary_structured_answer_only: 192
- surface_numeric_answer_only: 300
- easy_gravity_fragile: 18
- total repeated overlay rows: 2334

### Bundle footprint

- base examples: 7828
- overlay examples: 2334
- total examples: 10162
- total steps: 318
- total tokens: 28520876
- max sequence length: 7971

### Overlay supervision styles

- exact_rule_commit: 343
- exact_closure_commit: 343
- short_closure_commit: 343
- binary_zero_skill: 343
- anti_default1_commit: 9
- anti_default1_contrast_commit: 9
- surface_boxed_tail: 280
- surface_boxed_tail_boost: 64
- surface_short_closure: 276
- surface_short_closure_boost: 30
- surface_token_skill: 280
- surface_token_skill_boost: 14

## Canonical validation

- passed: True
- binary max think lines: 4
- surface max think lines: 3
- mandatory anchor missing: 0
- binary non-verified contamination: 0
- surface unexpected categories: 0

## Dual bit support + numeric popular8 slice

- prompt-local support lane は `surface_binary_prompt_local_answer_only` として **96 unique / 288 repeated**
- structured support lane は `surface_binary_structured_answer_only` として **64 unique / 192 repeated**
- numeric support lane は `surface_numeric_answer_only` として **64 unique / 300 repeated**
- overlay token は prompt-local support `86787`、structured support `62119`、numeric support `45398`
- overlay token share は prompt-local `0.1268`、structured `0.0907`、numeric `0.0663` で、combined bit+numeric support share は `0.2838`
- `hybrid_expanded` 比で overlay は `2034 -> 2334`、total tokens は `28475478 -> 28520876` と **numeric lane 分の 45398 tokens** だけ増えた

## Numeric guess popular8-capped-fallback-unique slice

- `surface_numeric_answer_only` の 64 unique rows は **すべて** `equation_numeric_guess`
- answer-only 候補に存在した 26 operator を **26/26 で全カバー**
- popular8 unique mix は `+ 4`, `- 4`, `* 3`, `/ 3`, `: 3`, `@ 3`, `[ 3`, `\\ 3`
- fallback operators `%` と `` ` `` は **`2 unique / 10 repeated`** まで確保した
- remaining tail operators も `pool <= 3` rows を優先したので、`! ) ] ^ | }` などの rare operator がそれぞれ `3 unique`、`"` `$` `<` `>` も `1 unique` で残った
- boost style は `surface_boxed_tail_boost 64`, `surface_short_closure_boost 30`, `surface_token_skill_boost 14` で、popular operators にだけ追加 repeat を積んだ
- popular+fallback operator order は `+ - * / : @ [ \\` に fallback `%` と backtick operator を足した 10 演算子で、README の popular-first 方針をそのまま numeric lane 配分へ写している

## Reassessment alignment check

### 1. `hybrid expanded + numeric popular8 capped fallback unique` requirements

- prompt-local exact rows の再活用: 満たす。verified exact は `95` を維持した
- structured exact rows の再活用: 満たす。structured core `152` を維持した
- short-closure rewrite lane: 満たす。`short_closure_commit 343` と `surface_short_closure 276 + boost 30` を維持した
- token-skill auxiliary lane: 満たす。`binary_zero_skill 343` と `surface_token_skill 280 + boost 14` を維持した
- answer-only separate lanes: 満たす。prompt-local / structured / numeric の answer-only rows を verified exact lane に混ぜず support lane のみに隔離した
- popular-8-first numeric allocation: 満たす。popular8 を主枠にしつつ fallback2 second unique rows も確保した
- boxed-first / deterministic contract: 満たす。`README.md` と `A-Open-ProgressPrizePublication/README.md` の boxed-first / deterministic 契約を崩していない

### 2. 今回あえて入れていないもの

- structured support の full `96` 併用
- numeric deduce 側への broad answer-only expansion
- risky な binary token representation change

### 3. README / reassessment に対する位置づけ

- `A-Open-ProgressPrizePublication/README.md` が示す最大 headroom の `bit_manipulation` と、弱い slice の `equation_numeric_guess` を同時に補強する branch である
- `versions/v20_to_088_reassessment_2026-04-18.md` の separate-lane 方針を保ったまま、bit dual support の strongest middle point に numeric popular8-first lane を重ねた合成線である

## Observed tradeoff before training

- `hybrid_expanded` の dual bit support はそのままなので、差分はほぼ **numeric popular8 capped fallback-unique lane の追加**に一致する
- total tokens は `28.52M` で、`hybrid_full` より still lighter なまま numeric lane を追加できた
- numeric lane は `64 unique / 300 repeated` だが boost の内訳が `64 / 30 / 14` に割れるため、popular operators の boxed-tail を最も強く繰り返し、closure/token-skill は必要最小限に留めている

## Next evaluation gate

- `hybrid_expanded` / `hybrid_full` / 本 branch を横並びで比較し、numeric lane を重ねたときに bit gains を保ったまま numeric regressions が戻るかを measured diff-pack で確認する
- numeric lane が有効なら、次は strongest bit base に対して numeric lane の量だけを上下させる ladder へ進む
