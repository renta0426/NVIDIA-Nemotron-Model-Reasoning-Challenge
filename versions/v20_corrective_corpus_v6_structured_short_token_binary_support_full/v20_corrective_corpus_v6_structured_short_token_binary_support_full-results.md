# v20 corrective corpus v6 structured-short-token-binary-support-full results

## Status

- Created: 2026-04-19 UTC
- Generator: `versions/v20_corrective_corpus_v6_structured_short_token_binary_support_full/reproduce_v20_corrective_corpus_v6_structured_short_token_binary_support_full.py`
- Run name: `v6_structured_short_token_binary_support_full_default`
- Active MLX full-run: `v20_mlx_v6_structured_short_token_binary_support_full_mb1_nobc`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_structured_short_token_binary_support_full_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python versions/v20_corrective_corpus_v6_structured_short_token_binary_support_full/reproduce_v20_corrective_corpus_v6_structured_short_token_binary_support_full.py --run-name v6_structured_short_token_binary_support_full_default --write-training-bundle` を current branch で実行し、`README.md` と `A-Open-ProgressPrizePublication/README.md` の deterministic / boxed-first 契約を保ったまま canonical checks を通して bundle 再生成に成功
- Branch purpose: structured answer-only support を `96` まで広げ、`149` 行 pool の大半を separate support lane に落とした full 比較線として、narrow / expanded / full の勾配を直接見るための branch
- Execution note: `v20_mlx_v6_structured_short_token_binary_support_expanded_mb1_nobc` の `training_result.json` 出現後にこの full pipeline が自動起動する detached queue を設定
- Post-run automation: `v6-structured-short-token-binary-support-full-train-watch` / `v6-structured-short-token-binary-support-full-eval-watch` に加えて、validation summary 出現後の measured diff-pack chain も armed

## Generated artifacts

- `versions/v20_corrective_corpus_v6_structured_short_token_binary_support_full/outputs/v6_structured_short_token_binary_support_full_default/artifacts/corrective_selection.csv`
- `versions/v20_corrective_corpus_v6_structured_short_token_binary_support_full/outputs/v6_structured_short_token_binary_support_full_default/artifacts/corrective_overlay_unique.jsonl`
- `versions/v20_corrective_corpus_v6_structured_short_token_binary_support_full/outputs/v6_structured_short_token_binary_support_full_default/artifacts/corrective_overlay_repeated.jsonl`
- `versions/v20_corrective_corpus_v6_structured_short_token_binary_support_full/outputs/v6_structured_short_token_binary_support_full_default/artifacts/corrective_overlay_summary.json`
- `versions/v20_corrective_corpus_v6_structured_short_token_binary_support_full/outputs/v6_structured_short_token_binary_support_full_default/reports/corrective_overlay_report.md`

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
- surface_binary_structured_answer_only: 96
- easy_gravity_fragile: 6
- total unique overlay problems: 496

### Repeated training rows

- binary_structured_exact_core: 901
- binary_logic_exact: 226
- binary_permutation_exact: 130
- binary_prompt_local_exact: 96
- surface_numeral_boxed: 102
- surface_cipher_boxed: 18
- surface_unit_tail: 18
- surface_symbol_prefix: 8
- surface_binary_structured_answer_only: 288
- easy_gravity_fragile: 18
- total repeated overlay rows: 1805

### Bundle footprint

- base examples: 7828
- overlay examples: 1805
- total examples: 9633
- total steps: 302
- total tokens: 28403593
- max sequence length: 7971

### Overlay supervision styles

- exact_rule_commit: 344
- exact_closure_commit: 312
- short_closure_commit: 344
- binary_zero_skill: 344
- anti_default1_commit: 9
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

## Bit structured-byte answer-only support slice

- support lane は `surface_binary_structured_answer_only` として **96 unique / 288 repeated**
- selected 96 行はすべて `bit_structured_byte_formula` + `answer_only_keep` で、source tag は `bit_structured_answer_only_support`
- `cuda-train-data-analysis-v1/reports/02_hard_family_findings.md` 上の structured answer-only pool `149` 行に対し、今回は `96` 行まで使う full 比較線で、未使用は `53` 行まで圧縮された
- support style は `surface_boxed_tail 96`, `surface_short_closure 96`, `surface_token_skill 96`
- overlay token は `90759`、overlay token share は `0.16`
- expanded 比で overlay は `1709 -> 1805`、total tokens は `28375145 -> 28403593`

## Reassessment alignment check

### 1. `structured short/token + near-full binary answer-only support` requirements

- structured-byte heavy exact rows の維持: 満たす。`binary_structured_exact_core 224` をそのまま保持した
- short-closure rewrite lane: 満たす。`short_closure_commit 344` と `surface_short_closure 148` を維持した
- token-skill auxiliary lane: 満たす。`binary_zero_skill 344` と `surface_token_skill 152` を維持した
- answer_only separate lane: 満たす。`bit_structured_byte_formula` の `answer_only_keep` を verified exact lane へ混ぜず support lane のみに隔離した
- boxed-first / deterministic contract: 満たす。`README.md` と `A-Open-ProgressPrizePublication/README.md` の boxed-first / deterministic 契約を崩していない

### 2. 今回あえて入れていないもの

- structured answer-only rows の full CoT teacher 化
- prompt-local answer-only support との同時合成
- risky な binary token representation change

### 3. README / reassessment に対する位置づけ

- `A-Open-ProgressPrizePublication/README.md` の bit gap に対し、structured-byte answer-only headroom をほぼ full に使ったときの挙動を見る branch である
- `versions/v20_to_088_reassessment_2026-04-18.md` の separate-lane 方針を維持したまま、support lane を強く積んだときに public/proxy で伸びるか、それとも過剰 teacher 化で鈍るかを測る

## Observed tradeoff before training

- exact binary mainline は narrow / expanded と同一なので、差分は **support lane 32 / 64 / 96** の量だけになる
- full でも selected source はまだ `bit_prompt_local_current_consensus_answer_only` 系だけで、nested/abstract の別 source を混ぜていない
- token share `0.16` は narrow `0.063` よりかなり重く、もし悪化するなら structured answer-only support は `96` まで積むと過剰と判断できる

## Next evaluation gate

- `structured_short_token_binary_support` / `expanded` / `full` を横並びで比較し、structured answer-only support の最適量を measured diff-pack で特定する
- full が strongest なら、次は prompt-local support と structured support の併用 branch を検討する
