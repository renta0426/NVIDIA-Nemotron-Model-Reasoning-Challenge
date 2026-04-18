# v20 corrective corpus v6 permutation-heavy results

## Status

- Created: 2026-04-18 UTC
- Generator: `versions/v20_corrective_corpus_v6_permutation_heavy/reproduce_v20_corrective_corpus_v6_permutation_heavy.py`
- Run name: `v6_permutation_heavy_default`
- Active MLX full-run: `v20_mlx_v6_permutation_heavy_mb1_nobc`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_permutation_heavy_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python versions/v20_corrective_corpus_v6_permutation_heavy/reproduce_v20_corrective_corpus_v6_permutation_heavy.py --run-name v6_permutation_heavy_default --write-training-bundle` を current branch で実行し、README 契約と canonical checks を通した上で bundle 再生成に成功
- Branch purpose: `v6-core` の exact-binary mainline を保持しつつ、再考メモの Option A に従って permutation / bijection へ追加予算を寄せた比較 branch
- Execution note: `v20_mlx_v6_structured_heavy_mb1_nobc` の `training_result.json` 出現後にこの full pipeline が自動起動する detached queue を設定済み
- Post-run automation: `v6-permutation-train-watch` / `v6-permutation-eval-watch` に加えて、validation summary 出現後の measured diff-pack chain も armed

## Generated artifacts

- `versions/v20_corrective_corpus_v6_permutation_heavy/outputs/v6_permutation_heavy_default/artifacts/corrective_selection.csv`
- `versions/v20_corrective_corpus_v6_permutation_heavy/outputs/v6_permutation_heavy_default/artifacts/corrective_overlay_unique.jsonl`
- `versions/v20_corrective_corpus_v6_permutation_heavy/outputs/v6_permutation_heavy_default/artifacts/corrective_overlay_repeated.jsonl`
- `versions/v20_corrective_corpus_v6_permutation_heavy/outputs/v6_permutation_heavy_default/artifacts/corrective_overlay_summary.json`
- `versions/v20_corrective_corpus_v6_permutation_heavy/outputs/v6_permutation_heavy_default/reports/corrective_overlay_report.md`

## Dataset composition

### Unique rows

- binary_structured_exact_core: 144
- binary_logic_exact: 56
- binary_permutation_exact: 87
- binary_prompt_local_exact: 48
- surface_numeral_boxed: 34
- surface_cipher_boxed: 6
- surface_unit_tail: 6
- surface_symbol_prefix: 4
- easy_gravity_fragile: 6
- total unique overlay problems: 391

### Repeated training rows

- binary_structured_exact_core: 293
- binary_logic_exact: 114
- binary_permutation_exact: 176
- binary_prompt_local_exact: 48
- surface_numeral_boxed: 34
- surface_cipher_boxed: 6
- surface_unit_tail: 6
- surface_symbol_prefix: 4
- easy_gravity_fragile: 6
- total repeated overlay rows: 687

### Bundle footprint

- base examples: 7828
- overlay examples: 687
- total examples: 8515
- total steps: 267
- total tokens: 28062024
- max sequence length: 7971

### Overlay supervision styles

- exact_rule_commit: 335
- exact_closure_commit: 287
- anti_default1_commit: 9
- surface_boxed_tail: 56

## Canonical validation

- passed: True
- binary max think lines: 4
- surface max think lines: 3
- mandatory anchor missing: 0
- binary non-verified contamination: 0
- surface unexpected categories: 0

## Reassessment alignment check

### 1. `v6-core + permutation-heavy` requirements

- permutation / bijection heavy: 満たす。`binary_permutation_exact` は候補上限のため `87` までだが、overlay token share は `0.2609` まで上昇した。
- structured-byte lane は維持しつつ縮小: 満たす。`binary_structured_exact_core` は `168 -> 144` に下げ、comparison line として分離した。
- anti-`default 1` counterexample lane: 満たす。hard binary IDs に `anti_default1_commit` を残した。
- boxed-first surface stabilizer lane: 満たす。surface 側は v6-core の minimal set を維持した。

### 2. 今回あえて入れていないもの

- short-closure rewrite lane
- token-skill auxiliary modernization
- risky な binary token representation change

### 3. README 契約との整合

- `README.md` の deterministic / boxed-first 契約はそのままに、binary 配分だけ permutation 側へ寄せた。
- broad symbol expansion や token representation 変更は入れず、README の回答抽出契約を壊さない branch に留めた。
- Kaggle へそのまま持ち込める single-file training bundle を生成した。

## Observed tradeoff before training

- repeated overlay は `687`、総 token は `28062024`。v6-core とほぼ同じ token budget で permutation 側の比率だけを持ち上げている。
- `binary_permutation_exact` は repeated `176`、overlay token share `0.2609`。一方で `binary_structured_exact_core` は token share `0.4465` まで下げ、structured-heavy と対照になる比較線を作った。
- available candidate ceiling のため permutation unique は `96` に届かず `87` で止まった。この branch は「入れられる permutation を最大化した線」として解釈すべき。

## Next evaluation gate

- `v6-core` / short-closure / token-skill / structured-heavy と並べ、permutation hard rows に改善が寄るかを measured diff-pack で確認する。
- structured-byte no-regression を大きく崩さずに permutation hard IDs を取れるなら、structured-heavy と並ぶ 4-5 本目比較線として実投入する。
