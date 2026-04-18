# v20 corrective corpus v6 token-skill results

## Status

- Created: 2026-04-18 UTC
- Generator: `versions/v20_corrective_corpus_v6_token_skill/reproduce_v20_corrective_corpus_v6_token_skill.py`
- Run name: `v6_token_skill_default`
- Active MLX full-run: `v20_mlx_v6_token_skill_mb1_nobc`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_token_skill_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python versions/v20_corrective_corpus_v6_token_skill/reproduce_v20_corrective_corpus_v6_token_skill.py --run-name v6_token_skill_default --write-training-bundle` を current branch で実行し、README 契約と canonical checks を通した上で bundle 再生成に成功
- Branch purpose: `v6-core` の exact-binary mainline を保持したまま、binary leading-zero exactness / boxed closure / prefix retention を補強する token-skill auxiliary lane を追加し、`v20_to_088_reassessment_2026-04-18.md` の Run 3 を MLX full-run 可能な単一ファイルとして固定した
- Execution note: `v20_mlx_v6_short_closure_mb1_nobc` の `training_result.json` 出現後にこの full pipeline が自動起動する detached queue を設定済みで、実験列が途切れないようにしている
- Post-run automation: `v6-token-train-watch` / `v6-token-eval-watch` に加えて、validation summary 出現後の measured diff-pack chain も armed

## Generated artifacts

- `versions/v20_corrective_corpus_v6_token_skill/outputs/v6_token_skill_default/artifacts/corrective_selection.csv`
- `versions/v20_corrective_corpus_v6_token_skill/outputs/v6_token_skill_default/artifacts/corrective_overlay_unique.jsonl`
- `versions/v20_corrective_corpus_v6_token_skill/outputs/v6_token_skill_default/artifacts/corrective_overlay_repeated.jsonl`
- `versions/v20_corrective_corpus_v6_token_skill/outputs/v6_token_skill_default/artifacts/corrective_overlay_summary.json`
- `versions/v20_corrective_corpus_v6_token_skill/outputs/v6_token_skill_default/reports/corrective_overlay_report.md`

## Dataset composition

### Unique rows

- binary_structured_exact_core: 168
- binary_logic_exact: 56
- binary_permutation_exact: 48
- binary_prompt_local_exact: 64
- surface_numeral_boxed: 34
- surface_cipher_boxed: 6
- surface_unit_tail: 6
- surface_symbol_prefix: 4
- easy_gravity_fragile: 6
- total unique overlay problems: 392

### Repeated training rows

- binary_structured_exact_core: 509
- binary_logic_exact: 170
- binary_permutation_exact: 146
- binary_prompt_local_exact: 128
- surface_numeral_boxed: 68
- surface_cipher_boxed: 12
- surface_unit_tail: 12
- surface_symbol_prefix: 8
- easy_gravity_fragile: 12
- total repeated overlay rows: 1065

### Bundle footprint

- base examples: 7828
- overlay examples: 1065
- total examples: 8893
- total steps: 279
- total tokens: 28176339
- max sequence length: 7971

### Overlay supervision styles

- exact_rule_commit: 336
- exact_closure_commit: 272
- binary_zero_skill: 336
- anti_default1_commit: 9
- surface_boxed_tail: 56
- surface_token_skill: 56

## Canonical validation

- passed: True
- binary max think lines: 4
- surface max think lines: 3
- mandatory anchor missing: 0
- binary non-verified contamination: 0
- surface unexpected categories: 0

## Reassessment alignment check

### 1. `v6-core + token-skill` requirements

- Fixed easy-family surface stabilizer lane: 満たす。v6-core の surface base をそのまま残した。
- Exact binary closure lane expansion: 満たす。structured / logic / permutation / prompt-local の exact lane を維持した。
- anti-`default 1` counterexample lane: 満たす。hard binary IDs に anti-default1 を残した。
- token-skill auxiliary modernization: 満たす。binary には `binary_zero_skill`、surface には `surface_token_skill` を追加し、leading-zero exactness / boxed closure / prefix retention を別 lane に分離した。

### 2. 今回あえて入れていないもの

- short-closure rewrite lane
- broad cryptarithm / broad symbol answer-only expansion
- risky な binary token representation change

### 3. README 契約との整合

- `README.md` の boxed-first / deterministic 契約を崩さないよう、すべての追加 lane を `\boxed{}` 終端 supervision のまま設計した。
- token-skill 追加後も v6-core の exact-binary lane を削らず、binary gain と surface repair を分離して比較できるようにした。
- Kaggle へそのまま持ち込める single-file training bundle を生成した。

## Observed tradeoff before training

- repeated overlay は `673 -> 1065` に増えたが、総 token は `28057594 -> 28176339` と小幅増に留まる。token-skill 補助を増やしても token budget はほぼ v6-core 水準。
- token-skill 追加分は `binary_zero_skill 336` と `surface_token_skill 56`。surface 側は broad symbol 化せず、minimal surface set の中で boxed/prefix exactness だけを強化している。
- `surface_token_skill` は empty-think boxed supervision として実装し、surface 正答文字列が think 内に再掲されて canonical check を壊すケースを回避した。

## Next evaluation gate

- まず `v6-core` 本線の measured score を回収し、その後この branch を MLX full-run に投入して symbol/text/boxed-surface failure の改善と binary collateral damage の有無を比較する。
- README 契約下で public edge を維持しながら surface 系の取りこぼしが減るなら、short-closure branch と並ぶ次候補に昇格する。
