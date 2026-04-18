# v20 corrective corpus v6 promptlocal-short-token-numeric-guess-popular8-tail-boost results

## Status

- Created: 2026-04-18 UTC
- Generator: `versions/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_popular8_tail_boost/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_popular8_tail_boost.py`
- Run name: `v6_promptlocal_short_token_numeric_guess_popular8_tail_boost_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_numeric_guess_popular8_tail_boost_mb1_nobc`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_popular8_tail_boost_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python versions/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_popular8_tail_boost/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_popular8_tail_boost.py --run-name v6_promptlocal_short_token_numeric_guess_popular8_tail_boost_default --write-training-bundle` を current branch で実行し、README 契約と canonical checks を通した上で bundle 再生成に成功
- Branch purpose: `common_tail_boost` の **34 tail rows 全投入 + 26/26 operator coverage** を維持しつつ、A-Open `README.md` が equation で明示した **popular set of 8 operators first** をそのまま unique-slot / repeat 配分に写す concentrated branch
- Execution note: `v20_mlx_v6_promptlocal_short_token_numeric_guess_common_tail_boost_mb1_nobc` の `training_result.json` 出現後にこの full pipeline が自動起動する detached queue を設定
- Post-run automation: `v6-promptlocal-short-token-popular8-tail-boost-train-watch` / `v6-promptlocal-short-token-popular8-tail-boost-eval-watch` に加えて、validation summary 出現後の measured diff-pack chain も armed

## Generated artifacts

- `versions/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_popular8_tail_boost/outputs/v6_promptlocal_short_token_numeric_guess_popular8_tail_boost_default/artifacts/corrective_selection.csv`
- `versions/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_popular8_tail_boost/outputs/v6_promptlocal_short_token_numeric_guess_popular8_tail_boost_default/artifacts/corrective_overlay_unique.jsonl`
- `versions/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_popular8_tail_boost/outputs/v6_promptlocal_short_token_numeric_guess_popular8_tail_boost_default/artifacts/corrective_overlay_repeated.jsonl`
- `versions/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_popular8_tail_boost/outputs/v6_promptlocal_short_token_numeric_guess_popular8_tail_boost_default/artifacts/corrective_overlay_summary.json`
- `versions/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_popular8_tail_boost/outputs/v6_promptlocal_short_token_numeric_guess_popular8_tail_boost_default/reports/corrective_overlay_report.md`

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
- surface_numeric_answer_only: 308
- easy_gravity_fragile: 18
- total repeated overlay rows: 1862

### Bundle footprint

- base examples: 7828
- overlay examples: 1862
- total examples: 9690
- total steps: 304
- total tokens: 28372347
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
- surface_short_closure_boost: 28
- surface_token_skill: 120
- surface_token_skill_boost: 24

## Canonical validation

- passed: True
- binary max think lines: 4
- surface max think lines: 3
- mandatory anchor missing: 0
- binary non-verified contamination: 0
- surface unexpected categories: 0

## Numeric guess popular8-tail slice

- `surface_numeric_answer_only` の 64 unique rows は **すべて** `equation_numeric_guess`
- answer-only 候補に存在した 26 operator を **26/26 で全カバー**
- A-Open `README.md` の popular set をデータ頻度で実装した top-8 は **`+`, `-`, `*`, `/`, `:`, `@`, `[`, `\\`**
- unique numeric rows は **popular8 28 / その他 36**。ただし popular8 内の配分は `+ 21` に大きく寄り、残り 7 operator は coverage 用の 1 row ずつ
- repeated popular8 mix は `+ 126`, `- 6`, `* 6`, `/ 6`, `: 5`, `@ 5`, `[ 5`, `\\ 5`
- `common_tail_boost` と比べて numeric repeated rows は `302 -> 308` に増えたが、その大半は **`+` への集中**として現れた

## Reassessment alignment check

### 1. `prompt-local short/token + numeric guess popular8 tail boost` requirements

- prompt-local exact rows の再活用: 満たす。`binary_prompt_local_exact` は `95` を維持した。
- short-closure rewrite lane: 満たす。`short_closure_commit 343` と `surface_short_closure 116 + boost 28` を維持した。
- token-skill auxiliary lane: 満たす。`binary_zero_skill 343` と `surface_token_skill 120 + boost 24` を維持した。
- numeric guess operator coverage lane: 満たす。`surface_numeric_answer_only 64` を全件 `equation_numeric_guess` に振り切り、26 operator 全カバーを維持した。
- low-frequency tail row inclusion: 満たす。`pool <= 3` の 34 rows を unique selection で全件投入した。
- popular-8-first allocation: 満たす。A-Open `README.md` が述べる *popular set of 8 operators first* を unique-slot / repeat の両方で明示した。
- heavier anti-`default 1` counterexample lane: 満たす。`anti_default1_commit 9` と `anti_default1_contrast_commit 9` を維持した。

### 2. 今回あえて入れていないもの

- broad `glyph_len5` / cryptarithm answer-only expansion
- risky な binary token representation change
- popular8 外 common operator (`%`, `` ` ``) への extra repeat

### 3. README 契約との整合

- `README.md` と `A-Open-ProgressPrizePublication/README.md` の deterministic / boxed-first 契約を崩していない。
- `A-Open-ProgressPrizePublication/README.md:104` の *“match the more popular set of 8 operators first before matching the rarer set of 24 operators”* を、chain-of-thought order だけでなく **学習データ配分そのもの**に変換した branch である。
- `FINAL_SUMMARY_REPORT.md` の handoff に従い、`answer_only_keep` は full trace teacher ではなく final-answer support lane として扱った。

## Observed tradeoff before training

- overlay examples は `1862`、総 token は `28372347`。`common_tail_boost` より **+6 overlay / -358 tokens** のほぼ同重量比較線になった。
- ただし配分はかなり鋭く、popular8 のうち `+` に `21 unique / 126 repeated` が集中している。これは README の popular-first 仮説を最も強く押した形だが、過集中のリスクもある。
- もしこの branch が悪化するなら、README の popular-first は **推論探索順**としては有効でも、学習データの unique-slot 集中までやると過剰だと判断できる。

## Next evaluation gate

- `promptlocal-short-token-numeric-guess-common-tail-boost` と本 branch を直接比較し、popular8-first concentration が public/proxy を押し上げるかを measured diff-pack で確認する。
- `+` への集中が強すぎる場合は、次段では popular8 内に cap を入れた `popular8-capped-tail-boost` へ進む。
