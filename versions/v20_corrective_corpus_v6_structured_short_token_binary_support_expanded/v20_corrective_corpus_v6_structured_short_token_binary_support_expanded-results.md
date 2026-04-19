# v20 corrective corpus v6 structured-short-token-binary-support-expanded results

## Status

- Created: 2026-04-19 UTC
- Generator: `versions/v20_corrective_corpus_v6_structured_short_token_binary_support_expanded/reproduce_v20_corrective_corpus_v6_structured_short_token_binary_support_expanded.py`
- Run name: `v6_structured_short_token_binary_support_expanded_default`
- Active MLX full-run: `v20_mlx_v6_structured_short_token_binary_support_expanded_mb1_nobc`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_structured_short_token_binary_support_expanded_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python versions/v20_corrective_corpus_v6_structured_short_token_binary_support_expanded/reproduce_v20_corrective_corpus_v6_structured_short_token_binary_support_expanded.py --run-name v6_structured_short_token_binary_support_expanded_default --write-training-bundle` を current branch で実行し、`README.md` と `A-Open-ProgressPrizePublication/README.md` の deterministic / boxed-first 契約を保ったまま canonical checks を通して bundle 再生成に成功
- Branch purpose: narrow structured support を `32 -> 64` に広げ、`bit_structured_byte_formula` の answer-only support 量が improvement / regression のどちらへ振れるかを measured で切り分ける expanded 比較線
- Execution note: `v20_mlx_v6_structured_short_token_binary_support_mb1_nobc` の `training_result.json` 出現後にこの full pipeline が自動起動する detached queue を設定
- Post-run automation: `v6-structured-short-token-binary-support-expanded-train-watch` / `v6-structured-short-token-binary-support-expanded-eval-watch` に加えて、validation summary 出現後の measured diff-pack chain も armed

## Generated artifacts

- `versions/v20_corrective_corpus_v6_structured_short_token_binary_support_expanded/outputs/v6_structured_short_token_binary_support_expanded_default/artifacts/corrective_selection.csv`
- `versions/v20_corrective_corpus_v6_structured_short_token_binary_support_expanded/outputs/v6_structured_short_token_binary_support_expanded_default/artifacts/corrective_overlay_unique.jsonl`
- `versions/v20_corrective_corpus_v6_structured_short_token_binary_support_expanded/outputs/v6_structured_short_token_binary_support_expanded_default/artifacts/corrective_overlay_repeated.jsonl`
- `versions/v20_corrective_corpus_v6_structured_short_token_binary_support_expanded/outputs/v6_structured_short_token_binary_support_expanded_default/artifacts/corrective_overlay_summary.json`
- `versions/v20_corrective_corpus_v6_structured_short_token_binary_support_expanded/outputs/v6_structured_short_token_binary_support_expanded_default/reports/corrective_overlay_report.md`

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
- surface_binary_structured_answer_only: 64
- easy_gravity_fragile: 6
- total unique overlay problems: 464

### Repeated training rows

- binary_structured_exact_core: 901
- binary_logic_exact: 226
- binary_permutation_exact: 130
- binary_prompt_local_exact: 96
- surface_numeral_boxed: 102
- surface_cipher_boxed: 18
- surface_unit_tail: 18
- surface_symbol_prefix: 8
- surface_binary_structured_answer_only: 192
- easy_gravity_fragile: 18
- total repeated overlay rows: 1709

### Bundle footprint

- base examples: 7828
- overlay examples: 1709
- total examples: 9537
- total steps: 299
- total tokens: 28375145
- max sequence length: 7971

### Overlay supervision styles

- exact_rule_commit: 344
- exact_closure_commit: 312
- short_closure_commit: 344
- binary_zero_skill: 344
- anti_default1_commit: 9
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

## Bit structured-byte answer-only support slice

- support lane は `surface_binary_structured_answer_only` として **64 unique / 192 repeated**
- selected 64 行はすべて `bit_structured_byte_formula` + `answer_only_keep` で、source tag は `bit_structured_answer_only_support`
- `cuda-train-data-analysis-v1/reports/02_hard_family_findings.md` 上の structured answer-only pool `149` 行に対し、今回は headroom の約 `43%` を使う expanded 版
- support style は `surface_boxed_tail 64`, `surface_short_closure 64`, `surface_token_skill 64`
- overlay token は `62311`、overlay token share は `0.1156`
- narrow structured support 比で overlay は `1613 -> 1709`、total tokens は `28344873 -> 28375145`

## Reassessment alignment check

### 1. `structured short/token + widened binary answer-only support` requirements

- structured-byte heavy exact rows の維持: 満たす。`binary_structured_exact_core 224` をそのまま保持した
- short-closure rewrite lane: 満たす。`short_closure_commit 344` と `surface_short_closure 116` を維持した
- token-skill auxiliary lane: 満たす。`binary_zero_skill 344` と `surface_token_skill 120` を維持した
- answer_only separate lane: 満たす。`bit_structured_byte_formula` の `answer_only_keep` を verified exact lane へ混ぜず support lane のみに隔離した
- boxed-first / deterministic contract: 満たす。`README.md` と `A-Open-ProgressPrizePublication/README.md` の boxed-first / deterministic 契約を崩していない

### 2. 今回あえて入れていないもの

- structured answer-only rows の full CoT teacher 化
- prompt-local answer-only support との同時合成
- risky な binary token representation change

### 3. README / reassessment に対する位置づけ

- `A-Open-ProgressPrizePublication/README.md` の v20 gap の中心である `bit_manipulation` を、verified exact lane を保ったまま support 量だけ増やして追う ablation である
- `versions/v20_to_088_reassessment_2026-04-18.md` の separate-lane 方針を維持しつつ、「structured answer-only をどこまで積むと効くか」を narrow 版より一段踏み込んで測る

## Observed tradeoff before training

- exact binary mainline は narrow 版と同一なので、差分は **support lane 32 -> 64** にほぼ一致する
- まだ selected source は `bit_prompt_local_current_consensus_answer_only` 系だけで、pool `149` 中 `85` 行が未使用
- narrow で変化が弱い場合でも、この版なら token share `0.063 -> 0.1156` の差で effect size を見にいける

## Next evaluation gate

- `structured_short_token_binary_support` と本 branch を比較し、structured answer-only support 量を増やしたときの bit/public 方向の伸びを measured diff-pack で確認する
- 改善が続くなら、次の full `96` 版が本命候補になる
