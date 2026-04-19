# v20 corrective corpus v6 structured-short-token-binary-support results

## Status

- Created: 2026-04-19 UTC
- Generator: `versions/v20_corrective_corpus_v6_structured_short_token_binary_support/reproduce_v20_corrective_corpus_v6_structured_short_token_binary_support.py`
- Run name: `v6_structured_short_token_binary_support_default`
- Active MLX full-run: `v20_mlx_v6_structured_short_token_binary_support_mb1_nobc`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_structured_short_token_binary_support_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python versions/v20_corrective_corpus_v6_structured_short_token_binary_support/reproduce_v20_corrective_corpus_v6_structured_short_token_binary_support.py --run-name v6_structured_short_token_binary_support_default --write-training-bundle` を current branch で実行し、`README.md` と `A-Open-ProgressPrizePublication/README.md` の deterministic / boxed-first 契約を保ったまま canonical checks を通して bundle 再生成に成功
- Branch purpose: `structured_short_token_skill` の verified structured exact lane を維持したまま、`bit_structured_byte_formula` の `answer_only_keep` を **別 support lane** として追加し、reassessment の「answer_only は exact binary lane に混ぜず short/token lane に落とす」を structured-byte に適用する branch
- Execution note: `v20_mlx_v6_promptlocal_short_token_binary_support_full_mb1_nobc` の `training_result.json` 出現後にこの full pipeline が自動起動する detached queue を設定
- Post-run automation: `v6-structured-short-token-binary-support-train-watch` / `v6-structured-short-token-binary-support-eval-watch` に加えて、validation summary 出現後の measured diff-pack chain も armed

## Generated artifacts

- `versions/v20_corrective_corpus_v6_structured_short_token_binary_support/outputs/v6_structured_short_token_binary_support_default/artifacts/corrective_selection.csv`
- `versions/v20_corrective_corpus_v6_structured_short_token_binary_support/outputs/v6_structured_short_token_binary_support_default/artifacts/corrective_overlay_unique.jsonl`
- `versions/v20_corrective_corpus_v6_structured_short_token_binary_support/outputs/v6_structured_short_token_binary_support_default/artifacts/corrective_overlay_repeated.jsonl`
- `versions/v20_corrective_corpus_v6_structured_short_token_binary_support/outputs/v6_structured_short_token_binary_support_default/artifacts/corrective_overlay_summary.json`
- `versions/v20_corrective_corpus_v6_structured_short_token_binary_support/outputs/v6_structured_short_token_binary_support_default/reports/corrective_overlay_report.md`

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
- surface_binary_structured_answer_only: 32
- easy_gravity_fragile: 6
- total unique overlay problems: 432

### Repeated training rows

- binary_structured_exact_core: 901
- binary_logic_exact: 226
- binary_permutation_exact: 130
- binary_prompt_local_exact: 96
- surface_numeral_boxed: 102
- surface_cipher_boxed: 18
- surface_unit_tail: 18
- surface_symbol_prefix: 8
- surface_binary_structured_answer_only: 96
- easy_gravity_fragile: 18
- total repeated overlay rows: 1613

### Bundle footprint

- base examples: 7828
- overlay examples: 1613
- total examples: 9441
- total steps: 296
- total tokens: 28344873
- max sequence length: 7971

### Overlay supervision styles

- exact_rule_commit: 344
- exact_closure_commit: 312
- short_closure_commit: 344
- binary_zero_skill: 344
- anti_default1_commit: 9
- surface_boxed_tail: 88
- surface_short_closure: 84
- surface_token_skill: 88

## Canonical validation

- passed: True
- binary max think lines: 4
- surface max think lines: 3
- mandatory anchor missing: 0
- binary non-verified contamination: 0
- stage-b-like exact contamination: 0

## Bit structured-byte answer-only support slice

- support lane は `surface_binary_structured_answer_only` として **32 unique / 96 repeated**
- selected 32 行はすべて `bit_structured_byte_formula` + `answer_only_keep` で、source tag は `bit_structured_answer_only_support`
- `cuda-train-data-analysis-v1/reports/02_hard_family_findings.md` 上の structured answer-only pool は `134 + 15 = 149` 行あるので、今回はそのうち narrow head `32` 行だけを support lane に切り出した
- support style は `surface_boxed_tail 32`, `surface_short_closure 32`, `surface_token_skill 32`
- overlay token は `32039`、overlay token share は `0.063`
- `structured_short_token_skill` 比で overlay は `1517 -> 1613`、total tokens は `28312834 -> 28344873`。増分のほぼ全てがこの structured answer-only support lane 由来

## Reassessment alignment check

### 1. `structured short/token + binary answer-only support` requirements

- structured-byte heavy exact rows の維持: 満たす。`binary_structured_exact_core 224` をそのまま保持した
- short-closure rewrite lane: 満たす。`short_closure_commit 344` と `surface_short_closure 84` を維持した
- token-skill auxiliary lane: 満たす。`binary_zero_skill 344` と `surface_token_skill 88` を維持した
- answer_only separate lane: 満たす。`bit_structured_byte_formula` の `answer_only_keep` を verified exact lane へ混ぜず support lane のみに隔離した
- boxed-first / deterministic contract: 満たす。`README.md` と `A-Open-ProgressPrizePublication/README.md` の boxed-first / deterministic 契約を崩していない

### 2. 今回あえて入れていないもの

- structured answer-only rows の full CoT teacher 化
- prompt-local answer-only support との同時合成
- risky な binary token representation change

### 3. README / reassessment に対する位置づけ

- `A-Open-ProgressPrizePublication/README.md` の v20 成績では `bit_manipulation` が最大の改善余地として残っているため、surface 側だけでなく structured-byte の answer-only headroom を teacher 分離で拾う branch にした
- `versions/v20_to_088_reassessment_2026-04-18.md` の「answer_only は full CoT ではなく short closure / token skill lane にするべき」を、prompt-local ではなく structured-byte に横展開した branch である

## Observed tradeoff before training

- exact binary mainline は `structured_short_token_skill` と同一なので、差分は **structured-byte answer-only support lane の有無**にかなり近い
- support pool 全量 `149` に対して今回は `32` 行だけなので、改善すれば expanded/full ladder を作る余地がまだ大きい
- source tag 上は `bit_prompt_local_current_consensus_answer_only` がぶら下がるが、実際の selected rows は `template_subtype = bit_structured_byte_formula` に限定しており、structured-byte answer surface repair として使っている

## Next evaluation gate

- `structured_short_token_skill` と本 branch を直接比較し、structured-byte hard rows と public/proxy のどちらで support lane が効くかを measured diff-pack で確認する
- 改善が出るなら、次は `149` 行 pool を使った expanded/full structured support ladder へ進む
