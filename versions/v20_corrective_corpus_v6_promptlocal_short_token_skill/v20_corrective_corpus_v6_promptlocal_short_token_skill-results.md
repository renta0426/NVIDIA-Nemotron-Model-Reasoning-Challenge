# v20 corrective corpus v6 promptlocal-short-token-skill results

## Status

- Created: 2026-04-18 UTC
- Generator: `versions/v20_corrective_corpus_v6_promptlocal_short_token_skill/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_skill.py`
- Run name: `v6_promptlocal_short_token_skill_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_skill_mb1_nobc`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_skill_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python versions/v20_corrective_corpus_v6_promptlocal_short_token_skill/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_skill.py --run-name v6_promptlocal_short_token_skill_default --write-training-bundle` を current branch で実行し、README 契約と canonical checks を通した上で bundle 再生成に成功
- Branch purpose: `bit_other` / prompt-local exact rows を厚くしたまま、`short-closure` と `token-skill` の両補助 lane を同時投入する bit-other triple-hybrid 比較線
- Execution note: `v20_mlx_v6_promptlocal_token_skill_mb1_nobc` の `training_result.json` 出現後にこの full pipeline が自動起動する detached queue を設定済み
- Post-run automation: `v6-promptlocal-short-token-train-watch` / `v6-promptlocal-short-token-eval-watch` に加えて、validation summary 出現後の measured diff-pack chain も armed

## Generated artifacts

- `versions/v20_corrective_corpus_v6_promptlocal_short_token_skill/outputs/v6_promptlocal_short_token_skill_default/artifacts/corrective_selection.csv`
- `versions/v20_corrective_corpus_v6_promptlocal_short_token_skill/outputs/v6_promptlocal_short_token_skill_default/artifacts/corrective_overlay_unique.jsonl`
- `versions/v20_corrective_corpus_v6_promptlocal_short_token_skill/outputs/v6_promptlocal_short_token_skill_default/artifacts/corrective_overlay_repeated.jsonl`
- `versions/v20_corrective_corpus_v6_promptlocal_short_token_skill/outputs/v6_promptlocal_short_token_skill_default/artifacts/corrective_overlay_summary.json`
- `versions/v20_corrective_corpus_v6_promptlocal_short_token_skill/outputs/v6_promptlocal_short_token_skill_default/reports/corrective_overlay_report.md`

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

- binary_structured_exact_core: 618
- binary_logic_exact: 228
- binary_permutation_exact: 164
- binary_prompt_local_exact: 380
- surface_numeral_boxed: 102
- surface_cipher_boxed: 18
- surface_unit_tail: 18
- surface_symbol_prefix: 8
- easy_gravity_fragile: 18
- total repeated overlay rows: 1554

### Bundle footprint

- base examples: 7828
- overlay examples: 1554
- total examples: 9382
- total steps: 294
- total tokens: 28326572
- max sequence length: 7971

### Overlay supervision styles

- exact_rule_commit: 343
- exact_closure_commit: 343
- short_closure_commit: 343
- binary_zero_skill: 343
- anti_default1_commit: 9
- anti_default1_contrast_commit: 9
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

### 1. `prompt-local exact rows + short/token hybrid` requirements

- prompt-local exact rows の再活用: 満たす。`binary_prompt_local_exact` は `95`、overlay token share は `0.2531`。
- short-closure rewrite lane: 満たす。`short_closure_commit 343` と `surface_short_closure 52` を追加した。
- token-skill auxiliary lane: 満たす。`binary_zero_skill 343` と `surface_token_skill 56` を追加した。
- heavier anti-`default 1` counterexample lane: 満たす。`anti_default1_commit 9` と `anti_default1_contrast_commit 9` を維持した。
- boxed-first surface stabilizer lane: 満たす。surface 側は minimal set のまま。

### 2. 今回あえて入れていないもの

- risky な binary token representation change
- broad symbol / cryptarithm answer-only expansion
- answer-only heavy promotion

### 3. README 契約との整合

- `README.md` と `A-Open-ProgressPrizePublication/README.md` の deterministic / boxed-first 契約を崩さず、teacher architecture だけを二重化した。
- broad symbol expansion や answer-only teacher 化は入れていない。
- Kaggle へそのまま持ち込める single-file training bundle を生成した。

## Observed tradeoff before training

- overlay examples は `1554`、総 token は `28326572`。現時点の bit-other 系では最も重いが、README v20 の token 規模からはまだ大きく外れていない。
- prompt-local share `0.2531` を保ったまま `short_closure` と `token_skill` を両方入れているため、bit-other 側でも「片側補助で十分か、二重化が必要か」を直接切り分けられる。
- もしこの branch が悪化するなら、bit-other 系の本命は `promptlocal-short` か `promptlocal-token` の片側に戻す判断材料になる。

## Next evaluation gate

- `promptlocal-short` / `promptlocal-token` / 本 branch を横並びで比較し、`bit_other` hard rows と prompt-local exact rows の改善量を measured diff-pack で確認する。
- proxy/public 方向で strongest なら、bit-other 系本命 hybrid を `short+token` 二重化へ寄せる。
