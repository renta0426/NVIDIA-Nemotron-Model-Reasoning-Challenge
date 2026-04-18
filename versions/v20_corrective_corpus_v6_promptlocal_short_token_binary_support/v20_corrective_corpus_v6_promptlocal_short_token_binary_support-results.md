# v20 corrective corpus v6 promptlocal-short-token-binary-support results

## Status

- Created: 2026-04-18 UTC
- Generator: `versions/v20_corrective_corpus_v6_promptlocal_short_token_binary_support/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support.py`
- Run name: `v6_promptlocal_short_token_binary_support_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_binary_support_mb1_nobc`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python versions/v20_corrective_corpus_v6_promptlocal_short_token_binary_support/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support.py --run-name v6_promptlocal_short_token_binary_support_default --write-training-bundle` を current branch で実行し、README 契約と canonical checks を通した上で bundle 再生成に成功
- Branch purpose: `promptlocal_short_token_skill` の verified exact lane は維持したまま、`answer_only_keep` の `bit_prompt_local_current_consensus_answer_only` rows を **別 support lane** として追加し、reassessment の「answer_only は full CoT にせず short/token lane に落とす」を bit prompt-local に適用する branch
- Execution note: `v20_mlx_v6_promptlocal_short_token_numeric_guess_popular8_capped_fallback_unique_tail_boost_mb1_nobc` の `training_result.json` 出現後にこの full pipeline が自動起動する detached queue を設定
- Post-run automation: `v6-promptlocal-short-token-binary-support-train-watch` / `v6-promptlocal-short-token-binary-support-eval-watch` に加えて、validation summary 出現後の measured diff-pack chain も armed

## Generated artifacts

- `versions/v20_corrective_corpus_v6_promptlocal_short_token_binary_support/outputs/v6_promptlocal_short_token_binary_support_default/artifacts/corrective_selection.csv`
- `versions/v20_corrective_corpus_v6_promptlocal_short_token_binary_support/outputs/v6_promptlocal_short_token_binary_support_default/artifacts/corrective_overlay_unique.jsonl`
- `versions/v20_corrective_corpus_v6_promptlocal_short_token_binary_support/outputs/v6_promptlocal_short_token_binary_support_default/artifacts/corrective_overlay_repeated.jsonl`
- `versions/v20_corrective_corpus_v6_promptlocal_short_token_binary_support/outputs/v6_promptlocal_short_token_binary_support_default/artifacts/corrective_overlay_summary.json`
- `versions/v20_corrective_corpus_v6_promptlocal_short_token_binary_support/outputs/v6_promptlocal_short_token_binary_support_default/reports/corrective_overlay_report.md`

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
- surface_binary_prompt_local_answer_only: 32
- easy_gravity_fragile: 6
- total unique overlay problems: 431

### Repeated training rows

- binary_structured_exact_core: 618
- binary_logic_exact: 228
- binary_permutation_exact: 164
- binary_prompt_local_exact: 380
- surface_numeral_boxed: 102
- surface_cipher_boxed: 18
- surface_unit_tail: 18
- surface_symbol_prefix: 8
- surface_binary_prompt_local_answer_only: 96
- easy_gravity_fragile: 18
- total repeated overlay rows: 1650

### Bundle footprint

- base examples: 7828
- overlay examples: 1650
- total examples: 9478
- total steps: 297
- total tokens: 28357439
- max sequence length: 7971

### Overlay supervision styles

- exact_rule_commit: 343
- exact_closure_commit: 343
- short_closure_commit: 343
- binary_zero_skill: 343
- anti_default1_commit: 9
- anti_default1_contrast_commit: 9
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

## Bit prompt-local answer-only support slice

- support lane は `surface_binary_prompt_local_answer_only` として **32 unique / 96 repeated**
- 選ばれた 32 行は **すべて** `bit_prompt_local_current_consensus_answer_only`
- support style は `surface_boxed_tail 32`, `surface_short_closure 32`, `surface_token_skill 32`
- overlay token は `30867` で、exact binary lane を壊さずに bit prompt-local の answer surface / 8-bit closure だけを別 teacher にできた
- `promptlocal_short_token_skill` 比で overlay は `1155 -> 1650`、total tokens は `28206156 -> 28357439`。増分のほぼ全てがこの bit answer-only support lane 由来

## Reassessment alignment check

### 1. `prompt-local short/token + binary answer-only support` requirements

- prompt-local exact rows の再活用: 満たす。verified exact は `95` を維持した。
- short-closure rewrite lane: 満たす。`short_closure_commit 343` と `surface_short_closure 84` を維持した。
- token-skill auxiliary lane: 満たす。`binary_zero_skill 343` と `surface_token_skill 88` を維持した。
- answer_only separate lane: 満たす。`bit_prompt_local_current_consensus_answer_only` を verified exact lane へ混ぜず、support lane のみに隔離した。
- boxed-first / deterministic contract: 満たす。`README.md` と `A-Open-ProgressPrizePublication/README.md` の boxed-first / deterministic 契約を崩していない。

### 2. 今回あえて入れていないもの

- answer-only rows の full CoT teacher 化
- broad symbol / cryptarithm answer-only expansion
- risky な binary token representation change

### 3. README / reassessment に対する位置づけ

- `A-Open-ProgressPrizePublication/README.md` の「bit が主戦場」「token weakness repair が必要」という主張に沿い、bit prompt-local answer-only を token-aware support lane に落とした。
- `versions/v20_to_088_reassessment_2026-04-18.md` の「answer_only は full CoT ではなく short closure / token skill lane にするべき」を、そのまま bit prompt-local に適用した branch である。

## Observed tradeoff before training

- exact binary mainline はそのままなので、差分は **bit prompt-local answer-only support lane の有無**にかなり近い。
- 32 行とも `current_consensus` 系 answer_only から選ばれており、nested support3 / abstract answer_only は今回まだ使っていない。
- これで改善するなら、bit でも「verified exact + answer-only support lane」の二層 teacher が有効と判断できる。

## Next evaluation gate

- `promptlocal_short_token_skill` と本 branch を直接比較し、bit prompt-local hard rows と public/proxy のどちらで support lane が効くかを measured diff-pack で確認する。
- さらに効くなら、次は `bit_prompt_local_nested_support3_or_abstract_answer_only` まで support lane を広げる。
