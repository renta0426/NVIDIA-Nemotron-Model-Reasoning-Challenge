# v20 corrective corpus v6 structured-short-token-skill results

## Status

- Created: 2026-04-18 UTC
- Generator: `v20_mlx_repro_v1/v20_corrective_corpus_v6_structured_short_token_skill/reproduce_v20_corrective_corpus_v6_structured_short_token_skill.py`
- Run name: `v6_structured_short_token_skill_default`
- Active MLX full-run: `v20_mlx_v6_structured_short_token_skill_mb1_nobc`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_structured_short_token_skill_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python v20_mlx_repro_v1/v20_corrective_corpus_v6_structured_short_token_skill/reproduce_v20_corrective_corpus_v6_structured_short_token_skill.py --run-name v6_structured_short_token_skill_default --write-training-bundle` を current branch で実行し、README 契約と canonical checks を通した上で bundle 再生成に成功
- Branch purpose: structured-byte persistent hard core に対して、`short-closure` と `token-skill` の両補助 lane を同時に重ねる triple-hybrid 比較線
- Execution note: `v20_mlx_v6_structured_token_skill_mb1_nobc` の `training_result.json` 出現後にこの full pipeline が自動起動する detached queue を設定済み
- Post-run automation: `v6-structured-short-token-train-watch` / `v6-structured-short-token-eval-watch` に加えて、validation summary 出現後の measured diff-pack chain も armed

## Generated artifacts

- `v20_mlx_repro_v1/v20_corrective_corpus_v6_structured_short_token_skill/outputs/v6_structured_short_token_skill_default/artifacts/corrective_selection.csv`
- `v20_mlx_repro_v1/v20_corrective_corpus_v6_structured_short_token_skill/outputs/v6_structured_short_token_skill_default/artifacts/corrective_overlay_unique.jsonl`
- `v20_mlx_repro_v1/v20_corrective_corpus_v6_structured_short_token_skill/outputs/v6_structured_short_token_skill_default/artifacts/corrective_overlay_repeated.jsonl`
- `v20_mlx_repro_v1/v20_corrective_corpus_v6_structured_short_token_skill/outputs/v6_structured_short_token_skill_default/artifacts/corrective_overlay_summary.json`
- `v20_mlx_repro_v1/v20_corrective_corpus_v6_structured_short_token_skill/outputs/v6_structured_short_token_skill_default/reports/corrective_overlay_report.md`

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

- binary_structured_exact_core: 901
- binary_logic_exact: 226
- binary_permutation_exact: 130
- binary_prompt_local_exact: 96
- surface_numeral_boxed: 102
- surface_cipher_boxed: 18
- surface_unit_tail: 18
- surface_symbol_prefix: 8
- easy_gravity_fragile: 18
- total repeated overlay rows: 1517

### Bundle footprint

- base examples: 7828
- overlay examples: 1517
- total examples: 9345
- total steps: 293
- total tokens: 28312834
- max sequence length: 7971

### Overlay supervision styles

- exact_rule_commit: 344
- exact_closure_commit: 312
- short_closure_commit: 344
- binary_zero_skill: 344
- anti_default1_commit: 9
- surface_boxed_tail: 56
- surface_short_closure: 52
- surface_token_skill: 56

## Canonical validation

- passed: True
- binary max think lines: 4
- surface max think lines: 3
- mandatory anchor missing: 0
- binary non-verified contamination: 0
- surface unexpected categories: 0

## Reassessment alignment check

### 1. hybrid requirements

- structured-byte heavy: 満たす。`binary_structured_exact_core` は `224`、overlay token share は `0.6239`。
- short-closure rewrite lane: 満たす。`short_closure_commit 344` と `surface_short_closure 52` を追加した。
- token-skill auxiliary lane: 満たす。`binary_zero_skill 344` と `surface_token_skill 56` を追加した。
- anti-`default 1` lane: 満たす。hard binary IDs に `anti_default1_commit` を残した。
- boxed-first surface stabilizer lane: 満たす。surface は minimal set のまま。

### 2. 今回あえて入れていないもの

- risky な binary token representation change
- broad symbol / cryptarithm answer-only expansion
- answer-only heavy promotion

### 3. README 契約との整合

- `README.md` / `A-Open-ProgressPrizePublication/README.md` の deterministic・boxed-first 契約を崩さず、teacher architecture だけを二重化した。
- Kaggle へそのまま持ち込める single-file training bundle を生成した。

## Observed tradeoff before training

- overlay examples は `1517` まで増え、現時点の v6 系では最も重い。ただし総 token は `28312834` で、README v20 の token 規模からまだ大きく外れてはいない。
- structured share を `0.6239` に保ちながら `short_closure` と `token_skill` を両方入れているため、「structured-heavy が勝つ条件はどちらか一方の補助で十分か、それとも二重化が必要か」を直接切り分けられる。
- もしこの branch が悪化するなら、teacher architecture の複合化はやり過ぎで、以後は `structured-short` か `structured-token` の片側本命に絞る判断材料になる。

## Next evaluation gate

- `structured-short` / `structured-token` / 本 branch を横並びで比較し、structured hard rows の改善と surface no-regression を同時に取れるかを見る。
- proxy/public 方向で strongest なら、以後の本命 hybrid を `short+token` 二重化へ寄せる。
