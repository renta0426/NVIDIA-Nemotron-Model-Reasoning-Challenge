# v20 corrective corpus v6 promptlocal-default1-heavy results

## Status

- Created: 2026-04-18 UTC
- Generator: `v20_mlx_repro_v1/v20_corrective_corpus_v6_promptlocal_default1_heavy/reproduce_v20_corrective_corpus_v6_promptlocal_default1_heavy.py`
- Run name: `v6_promptlocal_default1_heavy_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_default1_heavy_mb1_nobc`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_default1_heavy_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python v20_mlx_repro_v1/v20_corrective_corpus_v6_promptlocal_default1_heavy/reproduce_v20_corrective_corpus_v6_promptlocal_default1_heavy.py --run-name v6_promptlocal_default1_heavy_default --write-training-bundle` を current branch で実行し、README 契約と canonical checks を通した上で bundle 再生成に成功
- Branch purpose: `bit_other` / prompt-local exact rows を再活用しつつ、anti-`default 1` lane も heavier にした bit-other 対照線
- Execution note: `v20_mlx_v6_structured_default1_heavy_mb1_nobc` の `training_result.json` 出現後にこの full pipeline が自動起動する detached queue を設定済み
- Post-run automation: `v6-promptlocal-default1-train-watch` / `v6-promptlocal-default1-eval-watch` に加えて、validation summary 出現後の measured diff-pack chain も armed

## Generated artifacts

- `v20_mlx_repro_v1/v20_corrective_corpus_v6_promptlocal_default1_heavy/outputs/v6_promptlocal_default1_heavy_default/artifacts/corrective_selection.csv`
- `v20_mlx_repro_v1/v20_corrective_corpus_v6_promptlocal_default1_heavy/outputs/v6_promptlocal_default1_heavy_default/artifacts/corrective_overlay_unique.jsonl`
- `v20_mlx_repro_v1/v20_corrective_corpus_v6_promptlocal_default1_heavy/outputs/v6_promptlocal_default1_heavy_default/artifacts/corrective_overlay_repeated.jsonl`
- `v20_mlx_repro_v1/v20_corrective_corpus_v6_promptlocal_default1_heavy/outputs/v6_promptlocal_default1_heavy_default/artifacts/corrective_overlay_summary.json`
- `v20_mlx_repro_v1/v20_corrective_corpus_v6_promptlocal_default1_heavy/outputs/v6_promptlocal_default1_heavy_default/reports/corrective_overlay_report.md`

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

- binary_structured_exact_core: 314
- binary_logic_exact: 116
- binary_permutation_exact: 84
- binary_prompt_local_exact: 190
- surface_numeral_boxed: 34
- surface_cipher_boxed: 6
- surface_unit_tail: 6
- surface_symbol_prefix: 4
- easy_gravity_fragile: 6
- total repeated overlay rows: 760

### Bundle footprint

- base examples: 7828
- overlay examples: 760
- total examples: 8588
- total steps: 269
- total tokens: 28086482
- max sequence length: 7971

### Overlay supervision styles

- exact_rule_commit: 343
- exact_closure_commit: 343
- anti_default1_commit: 9
- anti_default1_contrast_commit: 9
- surface_boxed_tail: 56

## Canonical validation

- passed: True
- binary max think lines: 4
- surface max think lines: 3
- mandatory anchor missing: 0
- binary non-verified contamination: 0
- surface unexpected categories: 0

## Reassessment alignment check

### 1. `prompt-local exact rowsの再活用` requirements

- prompt-local exact rows の再活用: 満たす。`binary_prompt_local_exact` を `64 -> 95` に拡張し、overlay token share も `0.2535` まで上げた。
- prompt-local closure teacher: 満たす。`binary_prompt_local_exact` にも `exact_closure_commit` を入れ、query-specific closure を 2-style 化した。
- heavier anti-`default 1` counterexample lane: 満たす。`anti_default1_commit 9` に加えて `anti_default1_contrast_commit 9` を追加した。
- boxed-first surface stabilizer lane: 満たす。surface 側は v6-core の minimal set を維持した。

### 2. 今回あえて入れていないもの

- short-closure rewrite lane
- token-skill auxiliary modernization
- risky な binary token representation change

### 3. README 契約との整合

- `README.md` の deterministic / boxed-first 契約を崩さず、bit-other 側の prompt-local exact rows と counterexample supervision だけを厚くした。
- broad symbol expansion や answer-only teacher 化は入れていない。
- Kaggle へそのまま持ち込める single-file training bundle を生成した。

## Observed tradeoff before training

- overlay examples は `760` で mainline `673` より少し重いが、総 token は `28086482` とまだ v20 近傍に留まる。
- structured share を `0.4319` まで落として prompt-local share を `0.2535` まで上げているため、`bit_other` 側の EV を明確に見やすい。
- 逆にこの branch で悪化するなら、prompt-local exact の再活用は mainline 価値よりも branch 専用の補助に留めるべきという切り分けになる。

## Next evaluation gate

- `v6-core` / `permutation-heavy` / `structured-default1-heavy` と並べ、`bit_other` hard rows と prompt-local exact rows の改善量を measured diff-pack で確認する。
- proxy/public 方向で no-regression を保ちつつ `bit_other` hard core が改善するなら、bit-other 系本命 branch に昇格する。
