# v20 corrective corpus v6 structured-short-closure results

## Status

- Created: 2026-04-18 UTC
- Generator: `versions/v20_corrective_corpus_v6_structured_short_closure/reproduce_v20_corrective_corpus_v6_structured_short_closure.py`
- Run name: `v6_structured_short_closure_default`
- Active MLX full-run: `v20_mlx_v6_structured_short_closure_mb1_nobc`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_structured_short_closure_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python versions/v20_corrective_corpus_v6_structured_short_closure/reproduce_v20_corrective_corpus_v6_structured_short_closure.py --run-name v6_structured_short_closure_default --write-training-bundle` を current branch で実行し、README 契約と canonical checks を通した上で bundle 再生成に成功
- Branch purpose: structured-byte persistent hard core を厚く押す `structured-heavy` と、teacher architecture 本命である `short-closure` を合成した高EV比較線
- Execution note: `v20_mlx_v6_permutation_heavy_mb1_nobc` の `training_result.json` 出現後にこの full pipeline が自動起動する detached queue を設定済み
- Post-run automation: `v6-structured-short-train-watch` / `v6-structured-short-eval-watch` に加えて、validation summary 出現後の measured diff-pack chain も armed

## Generated artifacts

- `versions/v20_corrective_corpus_v6_structured_short_closure/outputs/v6_structured_short_closure_default/artifacts/corrective_selection.csv`
- `versions/v20_corrective_corpus_v6_structured_short_closure/outputs/v6_structured_short_closure_default/artifacts/corrective_overlay_unique.jsonl`
- `versions/v20_corrective_corpus_v6_structured_short_closure/outputs/v6_structured_short_closure_default/artifacts/corrective_overlay_repeated.jsonl`
- `versions/v20_corrective_corpus_v6_structured_short_closure/outputs/v6_structured_short_closure_default/artifacts/corrective_overlay_summary.json`
- `versions/v20_corrective_corpus_v6_structured_short_closure/outputs/v6_structured_short_closure_default/reports/corrective_overlay_report.md`

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

- binary_structured_exact_core: 677
- binary_logic_exact: 170
- binary_permutation_exact: 98
- binary_prompt_local_exact: 64
- surface_numeral_boxed: 68
- surface_cipher_boxed: 12
- surface_unit_tail: 12
- surface_symbol_prefix: 4
- easy_gravity_fragile: 12
- total repeated overlay rows: 1117

### Bundle footprint

- base examples: 7828
- overlay examples: 1117
- total examples: 8945
- total steps: 280
- total tokens: 28192125
- max sequence length: 7971

### Overlay supervision styles

- exact_rule_commit: 344
- exact_closure_commit: 312
- short_closure_commit: 344
- anti_default1_commit: 9
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

### 1. hybrid requirements

- structured-byte heavy: 満たす。`binary_structured_exact_core` は `224`、overlay token share は `0.6310`。
- short-closure rewrite lane: 満たす。`short_closure_commit 344` と `surface_short_closure 52` を追加した。
- anti-`default 1` lane: 満たす。hard binary IDs に `anti_default1_commit` を残した。
- boxed-first surface stabilizer lane: 満たす。surface は minimal set のまま。

### 2. 今回あえて入れていないもの

- token-skill auxiliary modernization
- risky な binary token representation change
- broad symbol / cryptarithm answer-only expansion

### 3. README 契約との整合

- `README.md` の deterministic / boxed-first 契約を崩さず、teacher architecture と binary 配分だけを強くした。
- Kaggle へそのまま持ち込める single-file training bundle を生成した。

## Observed tradeoff before training

- overlay examples は `1117` と現時点で最も大きいが、総 token は `28192125` とまだ v6-core 近傍に収まる。
- structured token share `0.6310` を維持しつつ、short-closure を binary/easy family 全面に追加しているため、`structured-heavy` と `short-closure` の良い側が同時に出るかを直接見に行ける。
- 逆に、もしこの branch で悪化するなら「二つの高EV仮説の同時適用は過学習寄り」という切り分けができる。

## Next evaluation gate

- `v6-core` / short-closure / structured-heavy と比較し、structured hard rows の改善と surface no-regression を同時に取れるかを見る。
- proxy/public 方向の改善が strongest なら、以後の本命ラインへ昇格する。
