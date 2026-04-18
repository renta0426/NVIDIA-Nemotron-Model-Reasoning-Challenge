# v20 corrective corpus v6 mainline results

## Status

- Created: 2026-04-18 UTC
- Generator: `versions/v20_corrective_corpus_v6_mainline/reproduce_v20_corrective_corpus_v6_mainline.py`
- Run name: `v6_mainline_default`
- Active MLX full-run: `v20_mlx_v6_mainline_mb1_nobc`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_mainline_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: current branch で `uv run python versions/v20_corrective_corpus_v6_mainline/reproduce_v20_corrective_corpus_v6_mainline.py --run-name v6_mainline_default --write-training-bundle` を再実行し、canonical checks を通した上で bundle 再生成に成功
- Execution note: initially queued behind `v20_mlx_v4_mainline_mb1_nobc`, but after confirming large RAM headroom and that the live v4 eval process used about `66 GB` RSS, the waiting chain was superseded and `v20_mlx_v6_mainline_mb1_nobc` was launched immediately in parallel
- Live MLX snapshot: train `step 48`, loss `0.000846738863832236`, trained tokens `5293788`
- Post-run automation: validation summary watcher and measured diff-pack chain are both armed for `v20_mlx_v6_mainline_mb1_nobc`

## Generated artifacts

- `versions/v20_corrective_corpus_v6_mainline/outputs/v6_mainline_default/artifacts/corrective_selection.csv`
- `versions/v20_corrective_corpus_v6_mainline/outputs/v6_mainline_default/artifacts/corrective_overlay_unique.jsonl`
- `versions/v20_corrective_corpus_v6_mainline/outputs/v6_mainline_default/artifacts/corrective_overlay_repeated.jsonl`
- `versions/v20_corrective_corpus_v6_mainline/outputs/v6_mainline_default/artifacts/corrective_overlay_summary.json`
- `versions/v20_corrective_corpus_v6_mainline/outputs/v6_mainline_default/reports/corrective_overlay_report.md`

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

- binary_structured_exact_core: 341
- binary_logic_exact: 114
- binary_permutation_exact: 98
- binary_prompt_local_exact: 64
- surface stabilizer total: 56
- total repeated overlay rows: 673

### Bundle footprint

- base examples: 7828
- overlay examples: 673
- total examples: 8501
- total steps: 267
- total tokens: 28057594
- max sequence length: 7971

### Overlay supervision styles

- exact_rule_commit: 336
- exact_closure_commit: 272
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

### 1. v6-core mainline requirements

- Fixed easy-family surface stabilizer lane: 満たす。surface lanes は numeral 34, cipher 6, unit 6, symbol-prefix 4, gravity 6 の最小構成に固定した。
- Exact binary closure lane expansion: 満たす。binary を structured 168, logic 56, permutation 48, prompt-local 64 に分割した。
- anti-`default 1` counterexample lane: 満たす。teacher-feasible な hard binary IDs に対して `anti_default1_commit` を 9 例入れた。
- minimal symbol-prefix repair lane: 満たす。`surface_symbol_prefix` を 4 行だけ入れ、broad symbol expansion は避けた。

### 2. v6-core で除外すべきもの

- short-closure rewrite lane: 入れていない
- token-skill auxiliary modernization: 入れていない
- broad cryptarithm / broad symbol answer-only expansion: 入れていない
- binary token representation change: 入れていない

### 3. README 契約との整合

- boxed-first extraction を壊さないよう surface stabilizer を別 lane で維持した。
- binary content gain を主目的にしつつ、surface を配分だけで解かず lane 分離した。
- single-file Kaggle bundle を生成し、LoRA 学習側でそのまま利用できる形式にした。

## Observed debt

- `teacher_incorrect_filtered_count = 177`。このため measured hard IDs の一部は mainline mandatory anchor に昇格させていない。
- 特に `binary_prompt_local_exact` の hard measured IDs は teacher correctness が立っておらず、mainline では lane 維持のみに留めた。
- `binary_structured_exact_core` でも persistent hard rows の一部は teacher incorrect のままで、v6-core だけでは hard-core 完治ではない。

## Next evaluation gate

- まず v6-core を学習して、`versions/v20_to_088_reassessment_2026-04-18.md` の gate 通り proxy binary `80/92` 以上を確認する。
- その後に `v6-core + short-closure` と `v6-core + token-skill` を branch run として切る。
