# v20 corrective corpus v6 promptlocal-short-token-binary-support-full results

## Status

- Created: 2026-04-19 UTC
- Generator: `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_full/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_full.py`
- Run name: `v6_promptlocal_short_token_binary_support_full_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_binary_support_full_mb1_nobc`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_full_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_full/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_full.py --run-name v6_promptlocal_short_token_binary_support_full_default --write-training-bundle` を current branch で実行し、README 契約と canonical checks を通した上で bundle 再生成に成功
- Branch purpose: `promptlocal_short_token_binary_support_expanded` の follow-up として、bit prompt-local answer-only support lane を `96` まで広げて `nested_support3_or_abstract` rows も取り込み、support-lane 仮説の上限比較を作る branch
- Execution note: `v20_mlx_v6_promptlocal_short_token_binary_support_expanded_mb1_nobc` の `training_result.json` 出現後にこの full pipeline が自動起動する detached queue を設定
- Post-run automation: `v6-promptlocal-short-token-binary-support-full-train-watch` / `v6-promptlocal-short-token-binary-support-full-eval-watch` に加えて、validation summary 出現後の measured diff-pack chain も armed

## Generated artifacts

- `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_full/outputs/v6_promptlocal_short_token_binary_support_full_default/artifacts/corrective_selection.csv`
- `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_full/outputs/v6_promptlocal_short_token_binary_support_full_default/artifacts/corrective_overlay_unique.jsonl`
- `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_full/outputs/v6_promptlocal_short_token_binary_support_full_default/artifacts/corrective_overlay_repeated.jsonl`
- `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_full/outputs/v6_promptlocal_short_token_binary_support_full_default/artifacts/corrective_overlay_summary.json`
- `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_full/outputs/v6_promptlocal_short_token_binary_support_full_default/reports/corrective_overlay_report.md`

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
- surface_binary_prompt_local_answer_only: 96
- easy_gravity_fragile: 6
- total unique overlay problems: 495

### Repeated training rows

- binary_structured_exact_core: 618
- binary_logic_exact: 228
- binary_permutation_exact: 164
- binary_prompt_local_exact: 380
- surface_numeral_boxed: 102
- surface_cipher_boxed: 18
- surface_unit_tail: 18
- surface_symbol_prefix: 8
- surface_binary_prompt_local_answer_only: 288
- easy_gravity_fragile: 18
- total repeated overlay rows: 1842

### Bundle footprint

- base examples: 7828
- overlay examples: 1842
- total examples: 9670
- total steps: 303
- total tokens: 28413359
- max sequence length: 7971

### Overlay supervision styles

- exact_rule_commit: 343
- exact_closure_commit: 343
- short_closure_commit: 343
- binary_zero_skill: 343
- anti_default1_commit: 9
- anti_default1_contrast_commit: 9
- surface_boxed_tail: 152
- surface_short_closure: 148
- surface_token_skill: 152

## Canonical validation

- passed: True
- binary max think lines: 4
- surface max think lines: 3
- mandatory anchor missing: 0
- binary non-verified contamination: 0
- stage-b-like exact contamination: 0

## Full bit prompt-local answer-only support slice

- support lane は `surface_binary_prompt_local_answer_only` として **96 unique / 288 repeated**
- 内訳は `bit_prompt_local_current_consensus_answer_only 74`、`bit_prompt_local_nested_support3_or_abstract_answer_only 22`
- support style は `surface_boxed_tail 96`, `surface_short_closure 96`, `surface_token_skill 96`
- support token は `86787`。32行版 / 64行版 / 96行版の 3 点比較で、ついに nested/abstract 系の投入有無まで見られる

## Reassessment alignment check

### 1. `prompt-local short/token + full binary answer-only support` requirements

- prompt-local exact rows の再活用: 満たす。verified exact は `95` を維持した。
- short-closure rewrite lane: 満たす。`short_closure_commit 343` と `surface_short_closure 148` を維持した。
- token-skill auxiliary lane: 満たす。`binary_zero_skill 343` と `surface_token_skill 152` を維持した。
- answer_only separate lane: 満たす。bit prompt-local answer-only は依然として support lane のみに隔離した。
- boxed-first / deterministic contract: 満たす。`README.md` と `A-Open-ProgressPrizePublication/README.md` の boxed-first / deterministic 契約を崩していない。

### 2. 今回あえて入れていないもの

- answer-only rows の full CoT teacher 化
- broad symbol / cryptarithm answer-only expansion
- risky な binary token representation change

### 3. README / reassessment に対する位置づけ

- `A-Open-ProgressPrizePublication/README.md` の「bit が主戦場」「token weakness repair が必要」という主張に対し、bit prompt-local answer-only support を最大ボリュームで当てた。
- `versions/v20_to_088_reassessment_2026-04-18.md` の「answer_only は別 lane にするべき」を、current-consensus だけでなく nested/abstract support にも広げて検証する branch である。

## Observed tradeoff before training

- support lane は `32 -> 64 -> 96` と広がるにつれ token が `30867 -> 58428 -> 86787` まで増えたが、bundle 全体はまだ `303 steps` に収まっている。
- この版だけが `nested_support3_or_abstract` を含むため、support の **量**だけでなく **質の違い**まで比較できる。
- もしこの版が悪化するなら、bit prompt-local support は `current_consensus` に限定した方がよいと判断できる。

## Next evaluation gate

- `binary_support` / `binary_support_expanded` / 本 branch の 3 本を直接比較し、bit prompt-local support lane の最適量と nested/abstract 混入の可否を measured diff-pack で確認する。
- これでも足りなければ、次は bit structured answer_only support を別 lane として切る。
