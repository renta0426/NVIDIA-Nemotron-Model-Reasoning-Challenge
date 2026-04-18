# v20 corrective corpus v6 promptlocal-short-token-numeric-guess-common-tail-boost results

## Status

- Created: 2026-04-18 UTC
- Generator: `versions/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_common_tail_boost/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_common_tail_boost.py`
- Run name: `v6_promptlocal_short_token_numeric_guess_common_tail_boost_default`
- Active MLX full-run: `v20_mlx_v6_promptlocal_short_token_numeric_guess_common_tail_boost_mb1_nobc`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_common_tail_boost_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Local regeneration status: `uv run python versions/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_common_tail_boost/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_common_tail_boost.py --run-name v6_promptlocal_short_token_numeric_guess_common_tail_boost_default --write-training-bundle` を current branch で実行し、README 契約と canonical checks を通した上で bundle 再生成に成功
- Branch purpose: `operator_tail_boost` の **34 tail rows 全投入 + 26/26 operator coverage** を維持したまま、追加 repetition の重心だけを common operators (`pool >= 4`) 側へ戻す hybrid branch
- Execution note: `v20_mlx_v6_promptlocal_short_token_numeric_guess_common_only_boost_mb1_nobc` の `training_result.json` 出現後にこの full pipeline が自動起動する detached queue を設定
- Post-run automation: `v6-promptlocal-short-token-common-tail-boost-train-watch` / `v6-promptlocal-short-token-common-tail-boost-eval-watch` に加えて、validation summary 出現後の measured diff-pack chain も armed

## Generated artifacts

- `versions/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_common_tail_boost/outputs/v6_promptlocal_short_token_numeric_guess_common_tail_boost_default/artifacts/corrective_selection.csv`
- `versions/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_common_tail_boost/outputs/v6_promptlocal_short_token_numeric_guess_common_tail_boost_default/artifacts/corrective_overlay_unique.jsonl`
- `versions/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_common_tail_boost/outputs/v6_promptlocal_short_token_numeric_guess_common_tail_boost_default/artifacts/corrective_overlay_repeated.jsonl`
- `versions/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_common_tail_boost/outputs/v6_promptlocal_short_token_numeric_guess_common_tail_boost_default/artifacts/corrective_overlay_summary.json`
- `versions/v20_corrective_corpus_v6_promptlocal_short_token_numeric_guess_common_tail_boost/outputs/v6_promptlocal_short_token_numeric_guess_common_tail_boost_default/reports/corrective_overlay_report.md`

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
- surface_numeric_answer_only: 64
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
- surface_numeric_answer_only: 302
- easy_gravity_fragile: 18
- total repeated overlay rows: 1856

### Bundle footprint

- base examples: 7828
- overlay examples: 1856
- total examples: 9684
- total steps: 303
- total tokens: 28372705
- max sequence length: 7971

### Overlay supervision styles

- exact_rule_commit: 343
- exact_closure_commit: 343
- short_closure_commit: 343
- binary_zero_skill: 343
- anti_default1_commit: 9
- anti_default1_contrast_commit: 9
- surface_boxed_tail: 120
- surface_boxed_tail_boost: 64
- surface_short_closure: 116
- surface_short_closure_boost: 30
- surface_token_skill: 120
- surface_token_skill_boost: 16

## Canonical validation

- passed: True
- binary max think lines: 4
- surface max think lines: 3
- mandatory anchor missing: 0
- binary non-verified contamination: 0
- surface unexpected categories: 0

## Numeric guess common-tail slice

- `surface_numeric_answer_only` の 64 unique rows は **すべて** `equation_numeric_guess`
- answer-only 候補に存在した 26 operator を **26/26 で全カバー**
- unique mix は **tail 34 rows + common 30 rows**
- repeated operator mix は `* 30`, `+ 30`, `- 36`, `\\ 20`, `: 15`, `@ 10`, `` ` 10``, `% 5`, `/ 5`, `[ 5` を common 側の主軸にしつつ、tail operators も `! 12`, `) 12`, `] 12`, `^ 12`, `| 12`, `} 12` などで残した
- bonus schedule は `pool >= 10` に +2 repeat、`4 <= pool < 10` に +1 repeat。これにより `operator_tail_boost` の rare bonus を外しても tail coverage を壊さず、common repetition を残せる形にした

## Reassessment alignment check

### 1. `prompt-local short/token + numeric guess common tail boost` requirements

- prompt-local exact rows の再活用: 満たす。`binary_prompt_local_exact` は `95` を維持した。
- short-closure rewrite lane: 満たす。`short_closure_commit 343` と `surface_short_closure 116 + boost 30` を維持した。
- token-skill auxiliary lane: 満たす。`binary_zero_skill 343` と `surface_token_skill 120 + boost 16` を維持した。
- numeric guess operator coverage lane: 満たす。`surface_numeric_answer_only 64` を全件 `equation_numeric_guess` に振り切り、26 operator 全カバーを維持した。
- low-frequency tail row inclusion: 満たす。`pool <= 3` の 34 rows を unique selection で全件投入した。
- common repetition boost: 満たす。common operators だけに explicit duplicate overlay を追加し、surface bucket の style 上限を超えて repeat を積んだ。
- heavier anti-`default 1` counterexample lane: 満たす。`anti_default1_commit 9` と `anti_default1_contrast_commit 9` を維持した。

### 2. 今回あえて入れていないもの

- broad `glyph_len5` / cryptarithm answer-only expansion
- risky な binary token representation change
- tail-only concentration

### 3. README 契約との整合

- `README.md` と `A-Open-ProgressPrizePublication/README.md` の deterministic / boxed-first 契約を崩さず、README の `Coverage` 原則に従って **tail operator を落とさず** common repetition の再配分を試す branch にした。
- `A-Open-ProgressPrizePublication/README.md` が equation で示した「popular set と rarer set を分けて扱う」発想に沿って、popular/common operators に repeat を寄せつつ rarer set も coverage から外さない設計にした。
- `FINAL_SUMMARY_REPORT.md` の handoff に従い、`answer_only_keep` は full trace teacher ではなく final-answer support lane として扱った。

## Observed tradeoff before training

- overlay examples は `1856`、総 token は `28372705`。`operator_tail_boost` (`1860`, `28372850`) よりわずかに軽く、`common_only_boost` (`1910`, `28380265`) よりもかなり軽い。
- numeric repeated rows は `302` で、`operator_tail_boost` の `306` より少し減るが、repeat の重心は rare tail から common operators へ移った。
- つまりこの branch は `tail coverage は保持したいが、追加 repetition は common 側に置きたい` という仮説を最短距離で検証する比較線になっている。

## Next evaluation gate

- `promptlocal-short-token-numeric-guess-common-only-boost` と本 branch を直接比較し、tail 34 rows の保持が public/proxy を押し上げるかを measured diff-pack で確認する。
- `promptlocal-short-token-numeric-guess-operator-tail-boost` とも比較し、rare-repeat を common-repeat に振り直した方が効くのかを切り分ける。
