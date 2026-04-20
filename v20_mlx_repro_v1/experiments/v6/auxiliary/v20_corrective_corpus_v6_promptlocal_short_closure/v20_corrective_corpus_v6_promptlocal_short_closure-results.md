# v20 corrective corpus v6 promptlocal-short-closure results

## Status

- Created: 2026-04-18 UTC
- Generator: `v20_mlx_repro_v1/experiments/v6/auxiliary/v20_corrective_corpus_v6_promptlocal_short_closure/reproduce_v20_corrective_corpus_v6_promptlocal_short_closure.py`
- Run name: `v6_promptlocal_short_closure_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_closure_mb1_nobc`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_closure_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python v20_mlx_repro_v1/experiments/v6/auxiliary/v20_corrective_corpus_v6_promptlocal_short_closure/reproduce_v20_corrective_corpus_v6_promptlocal_short_closure.py --run-name v6_promptlocal_short_closure_default --write-training-bundle` を current branch で実行し、README 契約と canonical checks を通した上で bundle 再生成に成功
- Branch purpose: `bit_other` / prompt-local exact rows を厚くしたまま、short-closure rewrite lane も同時投入する bit-other short 対照線
- Execution note: `v20_mlx_v6_promptlocal_default1_heavy_mb1_nobc` の `training_result.json` 出現後にこの full pipeline が自動起動する detached queue を設定済み
- Post-run automation: `v6-promptlocal-short-train-watch` / `v6-promptlocal-short-eval-watch` に加えて、validation summary 出現後の measured diff-pack chain も armed

## Generated artifacts

- `v20_mlx_repro_v1/experiments/v6/auxiliary/v20_corrective_corpus_v6_promptlocal_short_closure/outputs/v6_promptlocal_short_closure_default/artifacts/corrective_selection.csv`
- `v20_mlx_repro_v1/experiments/v6/auxiliary/v20_corrective_corpus_v6_promptlocal_short_closure/outputs/v6_promptlocal_short_closure_default/artifacts/corrective_overlay_unique.jsonl`
- `v20_mlx_repro_v1/experiments/v6/auxiliary/v20_corrective_corpus_v6_promptlocal_short_closure/outputs/v6_promptlocal_short_closure_default/artifacts/corrective_overlay_repeated.jsonl`
- `v20_mlx_repro_v1/experiments/v6/auxiliary/v20_corrective_corpus_v6_promptlocal_short_closure/outputs/v6_promptlocal_short_closure_default/artifacts/corrective_overlay_summary.json`
- `v20_mlx_repro_v1/experiments/v6/auxiliary/v20_corrective_corpus_v6_promptlocal_short_closure/outputs/v6_promptlocal_short_closure_default/reports/corrective_overlay_report.md`

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
- easy_gravity_fragile: 6
- total unique overlay problems: 399

### Repeated training rows

- binary_structured_exact_core: 466
- binary_logic_exact: 172
- binary_permutation_exact: 124
- binary_prompt_local_exact: 285
- surface_numeral_boxed: 68
- surface_cipher_boxed: 12
- surface_unit_tail: 12
- surface_symbol_prefix: 4
- easy_gravity_fragile: 12
- total repeated overlay rows: 1155

### Bundle footprint

- base examples: 7828
- overlay examples: 1155
- total examples: 8983
- total steps: 282
- total tokens: 28206156
- max sequence length: 7971

### Overlay supervision styles

- exact_rule_commit: 343
- exact_closure_commit: 343
- short_closure_commit: 343
- anti_default1_commit: 9
- anti_default1_contrast_commit: 9
- surface_boxed_tail: 56
- surface_short_closure: 52

## Canonical validation

- passed: True
- binary max think lines: 4
- surface max think lines: 3
- mandatory anchor missing: 0
- binary non-verified contamination: 0
- surface unexpected categories: 0

## Reassessment alignment check

### 1. `prompt-local exact rowsの再活用 + short closure` requirements

- prompt-local exact rows の再活用: 満たす。`binary_prompt_local_exact` は `95`、overlay token share は `0.2531`。
- short-closure rewrite lane: 満たす。`short_closure_commit 343` と `surface_short_closure 52` を追加した。
- heavier anti-`default 1` counterexample lane: 満たす。`anti_default1_commit 9` に加えて `anti_default1_contrast_commit 9` を維持した。
- boxed-first surface stabilizer lane: 満たす。surface 側は minimal set のまま。

### 2. 今回あえて入れていないもの

- token-skill auxiliary modernization
- risky な binary token representation change
- broad symbol / cryptarithm answer-only expansion

### 3. README 契約との整合

- `README.md` の deterministic / boxed-first 契約を崩さず、bit-other 側の prompt-local exact rows と short rewrite だけを強めた。
- broad symbol expansion や answer-only teacher 化は入れていない。
- Kaggle へそのまま持ち込める single-file training bundle を生成した。

## Observed tradeoff before training

- overlay examples は `1155`、総 token は `28206156`。`promptlocal-default1-heavy` より重いが、still v20 近傍に収まる。
- prompt-local share `0.2531` を保ったまま `short_closure_commit` を binary 全体へ追加しているため、`bit_other` 側でも short rewrite が効くかを直接見に行ける。
- 逆にこの branch が悪化するなら、bit-other 系では short closure より exact closure / counterexample の方が重要という切り分けになる。

## Next evaluation gate

- `promptlocal-default1-heavy` と直接比較し、`bit_other` hard rows と prompt-local exact rows の改善量を measured diff-pack で確認する。
- proxy/public 方向で no-regression を保ちつつ `bit_other` hard core が改善するなら、bit-other 系本命 branch に昇格する。
