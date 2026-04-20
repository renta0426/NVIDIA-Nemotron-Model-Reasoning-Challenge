# v20 corrective corpus v6 promptlocal-short-token-binary-support-expanded results

## Status

- Created: 2026-04-18 UTC
- Generator: `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_expanded/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_expanded.py`
- Run name: `v6_promptlocal_short_token_binary_support_expanded_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_binary_support_expanded_mb1_nobc`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_expanded_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_expanded/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_expanded.py --run-name v6_promptlocal_short_token_binary_support_expanded_default --write-training-bundle` を current branch で実行し、README 契約と canonical checks を通した上で bundle 再生成に成功
- Branch purpose: `promptlocal_short_token_binary_support` の follow-up として、bit prompt-local answer-only support lane を `32 -> 64` に広げ、README / reassessment の support-lane 仮説をより強く当てる branch
- Execution note: `v20_mlx_v6_promptlocal_short_token_binary_support_mb1_nobc` の `training_result.json` 出現後にこの full pipeline が自動起動する detached queue を設定
- Post-run automation: `v6-promptlocal-short-token-binary-support-expanded-train-watch` / `v6-promptlocal-short-token-binary-support-expanded-eval-watch` に加えて、validation summary 出現後の measured diff-pack chain も armed
- Watcher note (2026-04-20): `v20_mlx_repro_v1/outputs/v6/support` 配下で actual grouped-root train/eval watcher を再配置し、predecessor `training_result.json` 待ちの launch queue と train 完了後の adapter-validation / postprocess を実体として arm した

## Generated artifacts

- `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_expanded/outputs/v6_promptlocal_short_token_binary_support_expanded_default/artifacts/corrective_selection.csv`
- `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_expanded/outputs/v6_promptlocal_short_token_binary_support_expanded_default/artifacts/corrective_overlay_unique.jsonl`
- `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_expanded/outputs/v6_promptlocal_short_token_binary_support_expanded_default/artifacts/corrective_overlay_repeated.jsonl`
- `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_expanded/outputs/v6_promptlocal_short_token_binary_support_expanded_default/artifacts/corrective_overlay_summary.json`
- `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_expanded/outputs/v6_promptlocal_short_token_binary_support_expanded_default/reports/corrective_overlay_report.md`

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
- surface_binary_prompt_local_answer_only: 64
- easy_gravity_fragile: 6
- total unique overlay problems: 463

### Repeated training rows

- binary_structured_exact_core: 618
- binary_logic_exact: 228
- binary_permutation_exact: 164
- binary_prompt_local_exact: 380
- surface_numeral_boxed: 102
- surface_cipher_boxed: 18
- surface_unit_tail: 18
- surface_symbol_prefix: 8
- surface_binary_prompt_local_answer_only: 192
- easy_gravity_fragile: 18
- total repeated overlay rows: 1746

### Bundle footprint

- base examples: 7828
- overlay examples: 1746
- total examples: 9574
- total steps: 300
- total tokens: 28385000
- max sequence length: 7971

### Overlay supervision styles

- exact_rule_commit: 343
- exact_closure_commit: 343
- short_closure_commit: 343
- binary_zero_skill: 343
- anti_default1_commit: 9
- anti_default1_contrast_commit: 9
- surface_boxed_tail: 120
- surface_short_closure: 116
- surface_token_skill: 120

## Canonical validation

- passed: True
- binary max think lines: 4
- surface max think lines: 3
- mandatory anchor missing: 0
- binary non-verified contamination: 0
- stage-b-like exact contamination: 0

## Expanded bit prompt-local answer-only support slice

- support lane は `surface_binary_prompt_local_answer_only` として **64 unique / 192 repeated**
- 選ばれた 64 行は **すべて** `bit_prompt_local_current_consensus_answer_only`
- support style は `surface_boxed_tail 64`, `surface_short_closure 64`, `surface_token_skill 64`
- support token は `58428`。`binary_support` 版の `30867` から大きく伸びたが、bundle 全体はまだ `300 steps` に収まる
- `binary_support` 比で overlay は `1650 -> 1746`、total tokens は `28357439 -> 28385000`

## Reassessment alignment check

### 1. `prompt-local short/token + expanded binary answer-only support` requirements

- prompt-local exact rows の再活用: 満たす。verified exact は `95` を維持した。
- short-closure rewrite lane: 満たす。`short_closure_commit 343` と `surface_short_closure 116` を維持した。
- token-skill auxiliary lane: 満たす。`binary_zero_skill 343` と `surface_token_skill 120` を維持した。
- answer_only separate lane: 満たす。bit prompt-local answer-only は依然として support lane のみに隔離した。
- boxed-first / deterministic contract: 満たす。`README.md` と `A-Open-ProgressPrizePublication/README.md` の boxed-first / deterministic 契約を崩していない。

### 2. 今回あえて入れていないもの

- answer-only rows の full CoT teacher 化
- broad symbol / cryptarithm answer-only expansion
- risky な binary token representation change

### 3. README / reassessment に対する位置づけ

- `A-Open-ProgressPrizePublication/README.md` の「bit が主戦場」「token weakness repair が必要」という主張を受け、bit prompt-local answer-only support をさらに厚くした。
- `versions/v20_to_088_reassessment_2026-04-18.md` の「answer_only は別 lane にするべき」を、より大きな support volume で再検証する branch である。

## Observed tradeoff before training

- `binary_support` の純度は保ったまま support 量だけを増やした、きわめて解釈しやすい比較線になった。
- 64 行時点でもまだ `current_consensus` answer_only だけで埋まっており、nested/abstract 系は未投入である。
- これで改善するなら、bit prompt-local answer_only support は **量** そのものが効いている可能性が高い。

## Next evaluation gate

- `promptlocal_short_token_binary_support` と本 branch を直接比較し、support lane の量が bit prompt-local hard rows / proxy / public にどう効くかを measured diff-pack で確認する。
- さらに support を広げるなら、次は `nested_support3_or_abstract_answer_only` が入る閾値まで widen する。
