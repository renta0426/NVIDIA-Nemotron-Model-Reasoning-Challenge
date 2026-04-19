# v20 corrective corpus v6 promptlocal-short-token-binary-support-hybrid results

## Status

- Created: 2026-04-19 UTC
- Generator: `v20_mlx_repro_v1/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid.py`
- Run name: `v6_promptlocal_short_token_binary_support_hybrid_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_binary_support_hybrid_mb1_nobc`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python v20_mlx_repro_v1/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid.py --run-name v6_promptlocal_short_token_binary_support_hybrid_default --write-training-bundle` を current branch で実行し、`README.md` と `A-Open-ProgressPrizePublication/README.md` の deterministic / boxed-first 契約を保ったまま canonical checks を通して bundle 再生成に成功
- Branch purpose: `promptlocal_short_token_binary_support_full` の full prompt-local support lane を維持したまま、さらに `bit_structured_byte_formula` の answer-only support lane を narrow に追加し、bit support の separate lanes が **stack するか**を見る hybrid branch
- Execution note: `v20_mlx_v6_structured_short_token_binary_support_full_mb1_nobc` の `training_result.json` 出現後にこの full pipeline が自動起動する detached queue を設定
- Post-run automation: `v6-promptlocal-short-token-binary-support-hybrid-train-watch` / `v6-promptlocal-short-token-binary-support-hybrid-eval-watch` に加えて、validation summary 出現後の measured diff-pack chain も armed

## Generated artifacts

- `v20_mlx_repro_v1/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid/outputs/v6_promptlocal_short_token_binary_support_hybrid_default/artifacts/corrective_selection.csv`
- `v20_mlx_repro_v1/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid/outputs/v6_promptlocal_short_token_binary_support_hybrid_default/artifacts/corrective_overlay_unique.jsonl`
- `v20_mlx_repro_v1/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid/outputs/v6_promptlocal_short_token_binary_support_hybrid_default/artifacts/corrective_overlay_repeated.jsonl`
- `v20_mlx_repro_v1/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid/outputs/v6_promptlocal_short_token_binary_support_hybrid_default/artifacts/corrective_overlay_summary.json`
- `v20_mlx_repro_v1/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid/outputs/v6_promptlocal_short_token_binary_support_hybrid_default/reports/corrective_overlay_report.md`

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
- surface_binary_structured_answer_only: 32
- easy_gravity_fragile: 6
- total unique overlay problems: 527

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
- surface_binary_structured_answer_only: 96
- easy_gravity_fragile: 18
- total repeated overlay rows: 1938

### Bundle footprint

- base examples: 7828
- overlay examples: 1938
- total examples: 9766
- total steps: 306
- total tokens: 28445302
- max sequence length: 7971

### Overlay supervision styles

- exact_rule_commit: 343
- exact_closure_commit: 343
- short_closure_commit: 343
- binary_zero_skill: 343
- anti_default1_commit: 9
- anti_default1_contrast_commit: 9
- surface_boxed_tail: 184
- surface_short_closure: 180
- surface_token_skill: 184

## Canonical validation

- passed: True
- binary max think lines: 4
- surface max think lines: 3
- mandatory anchor missing: 0
- binary non-verified contamination: 0
- stage-b-like exact contamination: 0

## Dual bit answer-only support slices

- prompt-local support lane は `surface_binary_prompt_local_answer_only` として **96 unique / 288 repeated**
- structured support lane は `surface_binary_structured_answer_only` として **32 unique / 96 repeated**
- prompt-local support source は `bit_prompt_local_current_consensus_answer_only 74` と `bit_prompt_local_nested_support3_or_abstract_answer_only 22`
- structured support source は `bit_structured_byte_formula` + `answer_only_keep` の narrow head `32`
- overlay token は prompt-local support `86787`、structured support `31943`
- overlay token share は prompt-local `0.1425`、structured `0.0525` で、combined bit support share は `0.1950`
- `promptlocal_short_token_binary_support_full` 比で overlay は `1842 -> 1938`、total tokens は `28413359 -> 28445302`

## Reassessment alignment check

### 1. `prompt-local + structured dual support` requirements

- prompt-local exact rows の再活用: 満たす。verified exact は `95` を維持した
- short-closure rewrite lane: 満たす。`short_closure_commit 343` と `surface_short_closure 180` を維持した
- token-skill auxiliary lane: 満たす。`binary_zero_skill 343` と `surface_token_skill 184` を維持した
- answer_only separate lanes: 満たす。prompt-local と structured-byte の answer_only をどちらも verified exact lane へ混ぜず support lane のみに隔離した
- boxed-first / deterministic contract: 満たす。`README.md` と `A-Open-ProgressPrizePublication/README.md` の boxed-first / deterministic 契約を崩していない

### 2. 今回あえて入れていないもの

- answer-only rows の full CoT teacher 化
- structured support の expanded/full 併用
- risky な binary token representation change

### 3. README / reassessment に対する位置づけ

- `A-Open-ProgressPrizePublication/README.md` が強調する `bit_manipulation` の headroomに対して、prompt-local と structured-byte の **別々の support lane** を同時に当てる branch である
- `versions/v20_to_088_reassessment_2026-04-18.md` の「answer_only は exact lane に混ぜず separate lane にするべき」を、bit の主要 2 source に同時適用した比較線である

## Observed tradeoff before training

- exact binary mainline は `promptlocal_short_token_binary_support_full` と同一なので、差分は **structured narrow support 32 行の上積み**にかなり近い
- combined bit support share が `0.1950` まで上がっており、もし改善が出るなら separate lane 同士の stacking が有効と判断できる
- 逆に悪化するなら、prompt-local support full だけで既に飽和しており、structured support は独立 branch として扱うべきと分かる

## Next evaluation gate

- `promptlocal_short_token_binary_support_full` と本 branch を直接比較し、structured narrow support を追加した差分が bit/public 方向で効くかを measured diff-pack で確認する
- もし stacking が有効なら、次は `promptlocal full + structured expanded` まで広げる
