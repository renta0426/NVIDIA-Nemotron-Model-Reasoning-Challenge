# v20 corrective corpus v6 structured-heavy results

## Status

- Created: 2026-04-18 UTC
- Generator: `versions/v20_corrective_corpus_v6_structured_heavy/reproduce_v20_corrective_corpus_v6_structured_heavy.py`
- Run name: `v6_structured_heavy_default`
- Active MLX full-run: `v20_mlx_v6_structured_heavy_mb1_nobc`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_structured_heavy_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python versions/v20_corrective_corpus_v6_structured_heavy/reproduce_v20_corrective_corpus_v6_structured_heavy.py --run-name v6_structured_heavy_default --write-training-bundle` を current branch で実行し、README 契約と canonical checks を通した上で bundle 再生成に成功
- Branch purpose: `v6-core` の exact-binary mainline を保持しつつ、再考メモの Option B に従って structured-byte exact closure へ追加予算を寄せた 4 本目候補
- Execution note: `v20_mlx_v6_token_skill_mb1_nobc` の `training_result.json` 出現後にこの full pipeline が自動起動する detached queue を設定済み
- Post-run automation: `v6-structured-train-watch` / `v6-structured-eval-watch` に加えて、validation summary 出現後の measured diff-pack chain も armed

## Generated artifacts

- `versions/v20_corrective_corpus_v6_structured_heavy/outputs/v6_structured_heavy_default/artifacts/corrective_selection.csv`
- `versions/v20_corrective_corpus_v6_structured_heavy/outputs/v6_structured_heavy_default/artifacts/corrective_overlay_unique.jsonl`
- `versions/v20_corrective_corpus_v6_structured_heavy/outputs/v6_structured_heavy_default/artifacts/corrective_overlay_repeated.jsonl`
- `versions/v20_corrective_corpus_v6_structured_heavy/outputs/v6_structured_heavy_default/artifacts/corrective_overlay_summary.json`
- `versions/v20_corrective_corpus_v6_structured_heavy/outputs/v6_structured_heavy_default/reports/corrective_overlay_report.md`

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

- binary_structured_exact_core: 453
- binary_logic_exact: 114
- binary_permutation_exact: 66
- binary_prompt_local_exact: 32
- surface_numeral_boxed: 34
- surface_cipher_boxed: 6
- surface_unit_tail: 6
- surface_symbol_prefix: 4
- easy_gravity_fragile: 6
- total repeated overlay rows: 721

### Bundle footprint

- base examples: 7828
- overlay examples: 721
- total examples: 8549
- total steps: 268
- total tokens: 28072297
- max sequence length: 7971

### Overlay supervision styles

- exact_rule_commit: 344
- exact_closure_commit: 312
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

### 1. `v6-core + structured-heavy` requirements

- structured-byte exact closure heavy: 満たす。`binary_structured_exact_core` を `168 -> 224` に拡張し、overlay token share も `0.6478` まで上げた。
- logic / permutation / prompt-local の lane は維持: 満たす。`56 / 32 / 32` を残し、mainline 骨格は消していない。
- anti-`default 1` counterexample lane: 満たす。hard binary IDs に `anti_default1_commit` を残した。
- boxed-first surface stabilizer lane: 満たす。surface 側は v6-core の minimal set を維持した。

### 2. 今回あえて入れていないもの

- short-closure rewrite lane
- token-skill auxiliary modernization
- risky な binary token representation change

### 3. README 契約との整合

- `README.md` の deterministic / boxed-first 契約を崩さず、binary 側の配分だけを structured-byte に寄せた。
- public edge を壊しやすい broad symbol expansion や token representation 変更は入れていない。
- Kaggle へそのまま持ち込める single-file training bundle を生成した。

## Observed tradeoff before training

- unique overlay は `392 -> 400` と微増だが、structured 比率が大きく上がっている。`binary_structured_exact_core` は `168 -> 224`、一方で permutation / prompt-local は `48/64 -> 32/32` に縮小した。
- repeated overlay は `721` と v6-core の `673` より少し大きい程度で、総 token は `28057594 -> 28072297`。budget 増は小さいまま structured 側へ再配分できている。
- structured family 内でも `xor(shl,shr)` を `155` まで厚くし、persistent hard core が残りやすい領域へ優先的に寄せた。

## Next evaluation gate

- `v6-core` / short-closure / token-skill の結果と並べ、`default 1` rows の残差中心が structured-byte に残るならこの branch を実投入する。
- proxy binary と measured diff-pack で structured-byte hard IDs の改善が見え、surface no-regression を維持できるなら 4 本目本命に昇格する。
