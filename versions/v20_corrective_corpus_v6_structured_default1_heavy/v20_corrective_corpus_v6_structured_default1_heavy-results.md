# v20 corrective corpus v6 structured-default1-heavy results

## Status

- Created: 2026-04-18 UTC
- Generator: `versions/v20_corrective_corpus_v6_structured_default1_heavy/reproduce_v20_corrective_corpus_v6_structured_default1_heavy.py`
- Run name: `v6_structured_default1_heavy_default`
- Active MLX full-run: `v20_mlx_v6_structured_default1_heavy_mb1_nobc`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_structured_default1_heavy_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python versions/v20_corrective_corpus_v6_structured_default1_heavy/reproduce_v20_corrective_corpus_v6_structured_default1_heavy.py --run-name v6_structured_default1_heavy_default --write-training-bundle` を current branch で実行し、README 契約と canonical checks を通した上で bundle 再生成に成功
- Branch purpose: `structured-heavy` の骨格は維持しつつ、anti-`default 1` lane を heavier counterexample supervision に拡張した hard-core 比較線
- Execution note: `v20_mlx_v6_structured_short_token_skill_mb1_nobc` の `training_result.json` 出現後にこの full pipeline が自動起動する detached queue を設定済み
- Post-run automation: `v6-structured-default1-train-watch` / `v6-structured-default1-eval-watch` に加えて、validation summary 出現後の measured diff-pack chain も armed

## Generated artifacts

- `versions/v20_corrective_corpus_v6_structured_default1_heavy/outputs/v6_structured_default1_heavy_default/artifacts/corrective_selection.csv`
- `versions/v20_corrective_corpus_v6_structured_default1_heavy/outputs/v6_structured_default1_heavy_default/artifacts/corrective_overlay_unique.jsonl`
- `versions/v20_corrective_corpus_v6_structured_default1_heavy/outputs/v6_structured_default1_heavy_default/artifacts/corrective_overlay_repeated.jsonl`
- `versions/v20_corrective_corpus_v6_structured_default1_heavy/outputs/v6_structured_default1_heavy_default/artifacts/corrective_overlay_summary.json`
- `versions/v20_corrective_corpus_v6_structured_default1_heavy/outputs/v6_structured_default1_heavy_default/reports/corrective_overlay_report.md`

## Dataset composition

### Unique rows

- binary_structured_exact_core: 224
- binary_logic_exact: 56
- binary_permutation_exact: 32
- binary_prompt_local_exact: 32
- surface_numeral_boxed: 34
- surface_cipher_boxed: 6
- surface_unit_tail: 6
- surface_symbol_prefix: 4
- easy_gravity_fragile: 6
- total unique overlay problems: 400

### Repeated training rows

- binary_structured_exact_core: 458
- binary_logic_exact: 116
- binary_permutation_exact: 68
- binary_prompt_local_exact: 32
- surface_numeral_boxed: 34
- surface_cipher_boxed: 6
- surface_unit_tail: 6
- surface_symbol_prefix: 4
- easy_gravity_fragile: 6
- total repeated overlay rows: 730

### Bundle footprint

- base examples: 7828
- overlay examples: 730
- total examples: 8558
- total steps: 268
- total tokens: 28075622
- max sequence length: 7971

### Overlay supervision styles

- exact_rule_commit: 344
- exact_closure_commit: 312
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

### 1. `v6-core + structured-heavy + heavier anti-default1` requirements

- structured-byte exact closure heavy: 満たす。`binary_structured_exact_core` を `224` に維持し、overlay token share も `0.6464` を保った。
- heavier anti-`default 1` counterexample lane: 満たす。`anti_default1_commit 9` に加えて `anti_default1_contrast_commit 9` を追加した。
- logic / permutation / prompt-local の lane は維持: 満たす。`56 / 32 / 32` を残し、mainline 骨格は崩していない。
- boxed-first surface stabilizer lane: 満たす。surface 側は v6-core の minimal set を維持した。

### 2. 今回あえて入れていないもの

- short-closure rewrite lane
- token-skill auxiliary modernization
- risky な binary token representation change

### 3. README 契約との整合

- `README.md` の deterministic / boxed-first 契約を崩さず、binary hard-core の counterexample supervision だけを増やした。
- public edge を壊しやすい broad symbol expansion や token representation 変更は入れていない。
- Kaggle へそのまま持ち込める single-file training bundle を生成した。

## Observed tradeoff before training

- `structured-heavy` と比べて overlay examples は `721 -> 730` の微増に留まり、総 token も `28072297 -> 28075622` とほぼ同水準のまま。
- 追加差分は hard binary IDs のみに集中しているため、`default 1` 再発を抑える explicit counterexample supervision の純効果を見やすい。
- 逆にこの branch で改善しないなら、anti-`default 1` lane は量より short/token 系 architecture 変更の方が重要という切り分けになる。

## Next evaluation gate

- `structured-heavy` と直接比較し、`default 1` rows と structured-byte hard IDs の改善量を measured diff-pack で確認する。
- proxy/public 方向で no-regression かつ hard-core 改善が出るなら、structured 系本命を本 branch に置き換える。
