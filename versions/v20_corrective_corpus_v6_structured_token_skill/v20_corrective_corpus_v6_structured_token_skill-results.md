# v20 corrective corpus v6 structured-token-skill results

## Status

- Created: 2026-04-18 UTC
- Generator: `versions/v20_corrective_corpus_v6_structured_token_skill/reproduce_v20_corrective_corpus_v6_structured_token_skill.py`
- Run name: `v6_structured_token_skill_default`
- Active MLX full-run: `v20_mlx_v6_structured_token_skill_mb1_nobc`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_structured_token_skill_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python versions/v20_corrective_corpus_v6_structured_token_skill/reproduce_v20_corrective_corpus_v6_structured_token_skill.py --run-name v6_structured_token_skill_default --write-training-bundle` を current branch で実行し、README 契約と canonical checks を通した上で bundle 再生成に成功
- Branch purpose: structured-byte persistent hard core を厚く押す `structured-heavy` と、README 由来の token-skill auxiliary を合成した比較線
- Execution note: `v20_mlx_v6_structured_short_closure_mb1_nobc` の `training_result.json` 出現後にこの full pipeline が自動起動する detached queue を設定する方針

## Generated artifacts

- `versions/v20_corrective_corpus_v6_structured_token_skill/outputs/v6_structured_token_skill_default/artifacts/corrective_selection.csv`
- `versions/v20_corrective_corpus_v6_structured_token_skill/outputs/v6_structured_token_skill_default/artifacts/corrective_overlay_unique.jsonl`
- `versions/v20_corrective_corpus_v6_structured_token_skill/outputs/v6_structured_token_skill_default/artifacts/corrective_overlay_repeated.jsonl`
- `versions/v20_corrective_corpus_v6_structured_token_skill/outputs/v6_structured_token_skill_default/artifacts/corrective_overlay_summary.json`
- `versions/v20_corrective_corpus_v6_structured_token_skill/outputs/v6_structured_token_skill_default/reports/corrective_overlay_report.md`

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
- surface_symbol_prefix: 8
- easy_gravity_fragile: 12
- total repeated overlay rows: 1121

### Bundle footprint

- base examples: 7828
- overlay examples: 1121
- total examples: 8949
- total steps: 281
- total tokens: 28193006
- max sequence length: 7971

### Overlay supervision styles

- exact_rule_commit: 344
- exact_closure_commit: 312
- binary_zero_skill: 344
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

### 1. hybrid requirements

- structured-byte heavy: 満たす。`binary_structured_exact_core` は `224`、overlay token share は `0.6326`。
- token-skill auxiliary lane: 満たす。`binary_zero_skill 344` と `surface_token_skill 56` を追加した。
- anti-`default 1` lane: 満たす。hard binary IDs に `anti_default1_commit` を残した。
- boxed-first surface stabilizer lane: 満たす。surface は minimal set のまま。

### 2. 今回あえて入れていないもの

- short-closure rewrite lane
- risky な binary token representation change
- broad symbol / cryptarithm answer-only expansion

### 3. README 契約との整合

- `README.md` の deterministic / boxed-first 契約を崩さず、binary 配分と token-skill 補助だけを強くした。
- Kaggle へそのまま持ち込める single-file training bundle を生成した。

## Observed tradeoff before training

- overlay examples は `1121`、総 token は `28193006`。`structured-short` とほぼ同規模だが、teacher architecture の追加が short closure ではなく token-skill になっている。
- structured token share `0.6326` を保ったまま、`binary_zero_skill` / `surface_token_skill` を全面追加しているため、surface/prefix/leading-zero failure の補修を structured hard core と同時に見に行ける。
- これで `structured-short` と `structured-token` を直接比較すれば、「teacher architecture 変更の本命が short closure か token-skill か」を切り分けやすい。

## Next evaluation gate

- `structured-heavy` / `structured-short` と並べ、structured hard rows の改善と surface no-regression を同時に取れるかを見る。
- proxy/public 方向で `structured-short` より安定するなら、token-skill 系 hybrid の本命に昇格する。
