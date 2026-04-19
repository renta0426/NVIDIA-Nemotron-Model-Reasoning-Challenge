# v20 corrective corpus v6 short-closure results

## Status

- Created: 2026-04-18 UTC
- Generator: `v20_mlx_repro_v1/v20_corrective_corpus_v6_short_closure/reproduce_v20_corrective_corpus_v6_short_closure.py`
- Run name: `v6_short_closure_default`
- Active MLX full-run: `v20_mlx_v6_short_closure_mb1_nobc`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_short_closure_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python v20_mlx_repro_v1/v20_corrective_corpus_v6_short_closure/reproduce_v20_corrective_corpus_v6_short_closure.py --run-name v6_short_closure_default --write-training-bundle` を current branch で実行し、README 契約と canonical checks を通した上で bundle 再生成に成功
- Branch purpose: `v6-core` の exact-binary mainline を保持したまま、binary と easy family に short-closure rewrite lane を追加し、`v20_to_088_reassessment_2026-04-18.md` の Run 2 を MLX full-run 可能な単一ファイルとして固定した
- Execution note: 現在の RAM 状況を踏まえて即時 3 本目起動は避け、`v20_mlx_v6_mainline_mb1_nobc` の `training_result.json` 出現をトリガにこの full pipeline が自動起動する detached queue を設定済み
- Post-run automation: `v6-short-train-watch` / `v6-short-eval-watch` に加えて、validation summary 出現後の measured diff-pack chain も armed

## Generated artifacts

- `v20_mlx_repro_v1/v20_corrective_corpus_v6_short_closure/outputs/v6_short_closure_default/artifacts/corrective_selection.csv`
- `v20_mlx_repro_v1/v20_corrective_corpus_v6_short_closure/outputs/v6_short_closure_default/artifacts/corrective_overlay_unique.jsonl`
- `v20_mlx_repro_v1/v20_corrective_corpus_v6_short_closure/outputs/v6_short_closure_default/artifacts/corrective_overlay_repeated.jsonl`
- `v20_mlx_repro_v1/v20_corrective_corpus_v6_short_closure/outputs/v6_short_closure_default/artifacts/corrective_overlay_summary.json`
- `v20_mlx_repro_v1/v20_corrective_corpus_v6_short_closure/outputs/v6_short_closure_default/reports/corrective_overlay_report.md`

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
- surface_symbol_prefix: 4
- easy_gravity_fragile: 12
- total repeated overlay rows: 1061

### Bundle footprint

- base examples: 7828
- overlay examples: 1061
- total examples: 8889
- total steps: 279
- total tokens: 28175578
- max sequence length: 7971

### Overlay supervision styles

- exact_rule_commit: 336
- exact_closure_commit: 272
- short_closure_commit: 336
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

### 1. `v6-core + short-closure` requirements

- Fixed easy-family surface stabilizer lane: 満たす。surface base は v6-core と同じ minimal set を維持した。
- Exact binary closure lane expansion: 満たす。structured / logic / permutation / prompt-local の v6-core lane をそのまま維持した。
- anti-`default 1` counterexample lane: 満たす。hard binary IDs に `anti_default1_commit` を残した。
- short-closure rewrite lane: 満たす。binary 全 bucket と easy-family surface bucket に short closure variant を追加した。

### 2. 今回あえて入れていないもの

- token-skill auxiliary modernization
- broad cryptarithm / broad symbol answer-only expansion
- risky な binary token representation change

### 3. README 契約との整合

- `README.md` の deterministic / boxed-first 契約を崩さないよう、すべての追加 lane を短い `\boxed{}` 終端 supervision に揃えた。
- short-closure を入れても binary exact lane 自体は削らず、README 由来の binary gain を残したまま追加比較できる形にした。
- Kaggle へそのまま持ち込める single-file training bundle を生成した。

## Observed tradeoff before training

- repeated overlay は `673 -> 1061` に増えたが、総 token は `28057594 -> 28175578` と小幅増に留まる。short-closure を増やしても token budget はまだ v6-core とほぼ同水準。
- short-closure 追加分は `short_closure_commit 336` と `surface_short_closure 52`。binary/easy family を中心に再配線し、broad symbol 化は避けた。
- `surface_symbol_prefix` はあえて 1 variant のまま据え置き、token-style branch と役割を分けた。

## Next evaluation gate

- まず `v6-core` 本線の measured score を回収し、その後この branch を MLX full-run に投入して proxy binary / `format_ok_content_wrong_rate` / numeral-unit no-regression を比較する。
- README 契約下で public edge を維持しつつ binary hard core が伸びるなら、次の本命候補に昇格する。
