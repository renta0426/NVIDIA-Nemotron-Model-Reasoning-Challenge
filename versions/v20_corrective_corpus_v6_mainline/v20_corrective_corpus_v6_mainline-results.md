# v20 corrective corpus v6 mainline results

## Status

- Created: 2026-04-18 UTC
- Generator: `versions/v20_corrective_corpus_v6_mainline/reproduce_v20_corrective_corpus_v6_mainline.py`
- Run name: `v6_mainline_default`
- Active MLX full-run: `v20_mlx_v6_mainline_mb1_nobc`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_mainline_bundle.jsonl`
- Training / validation / leaderboard score: validation `829 / 950 = 0.8726`, leaderboard proxy `180 / 200 = 0.9000`, official leaderboard `0.83-0.85`
- Local regeneration status: current branch で `uv run python versions/v20_corrective_corpus_v6_mainline/reproduce_v20_corrective_corpus_v6_mainline.py --run-name v6_mainline_default --write-training-bundle` を再実行し、canonical checks を通した上で bundle 再生成に成功
- Execution note: initially queued behind `v20_mlx_v4_mainline_mb1_nobc`, but after confirming large RAM headroom and that the live v4 eval process used about `66 GB` RSS, the waiting chain was superseded and `v20_mlx_v6_mainline_mb1_nobc` was launched immediately in parallel
- Live MLX snapshot (pre-OOM interrupted run): train `step 112`, trained tokens `12183194`, peak memory `221.9755 GB`
- Post-run automation: grouped rerun 向けに adapter-validation watcher と postprocess watcher を re-arm 済みで、`v20_mlx_v6_mainline_mb1_nobc` の `training_result.json` 出現後に `README.md` 契約 (`max_tokens 7680`, `top_p 1.0`, `temperature 0.0`, `max_model_len 8192`) の条件で adapter validation を起動する
- Interruption note: run itself had entered stable train, but OOM-triggered restart happened before validation / postprocess could complete; current ledger therefore records the last observed train snapshot only
- Relaunch note (2026-04-20): `v20_mlx_v4_mainline_mb1_nobc` eval を継続させたまま、`v20_mlx_v6_mainline_mb1_nobc` を `v20_mlx_repro_v1/outputs/v6/auxiliary` 配下で fresh full-train として再起動した。grouped run root では `adapter_config.json` / `train_report.jsonl` / `latest_train_report.json` が再生成され、現在の fresh run は `step 6`, `trained_tokens 658356`, `train_loss 0.09877014974349398`, `peak_memory 221.9409 GB` まで進行している
- live-process note (2026-04-20): `sample` では main thread が `mlx::core::eval -> eval_impl` の下で `gpu::eval` / `metal::Device::commit_command_buffer` / AGX dispatch に入っており、fresh mainline train は idle ではなく Metal command buffer 実行待ちを含む MLX GPU 計算中と判断した
- Artifact hygiene note (2026-04-20): 現在の active roots (`v20_mlx_v4_mainline_mb1_nobc`, `v20_mlx_v6_mainline_mb1_nobc`) には触れず、inactive な targetfix / aborted frontier roots に残っていた stale `shadow_model` と `training_bundle_tokens` を prune して、次の full-run 用に local workspace を整理した
- Resource gate note (2026-04-20): `README.md` 契約の full-run 群を維持したまま live 本数を `v4 eval + 4 train = 5 python` に増やした結果、`vm_stat` の free pages は約 `4642` まで低下した。`manual_launch_watch.log` でも v6 mainline はまだ `step 6` のままなので、これ以上の即時 launch は止め、既存 root が `latest_train_report.json` を更新するか `training_result.json` を出すまで queue 自動進行を優先する

## Measured results

### Validation summary

- total: `829 / 950 = 0.8726`
- bit_manipulation: `150 / 169 = 0.8876`
- numeral: `138 / 149 = 0.9262`
- unit_conversion: `171 / 171 = 1.0000`
- gravity: `158 / 159 = 0.9937`
- cipher: `161 / 162 = 0.9938`

Interpretation:

- v6 matches v5a on total validation (`829 / 950`) while shifting the gains back toward binary.
- Compared with v4, validation improves by `+16` rows net (`26` improved, `10` regressed).
- Compared with v20, v6 is still `-8` rows on validation, and almost all of that remaining easy-family debt is numeral boxed-surface loss.

### Proxy summary

- overall: `180 / 200 = 0.9000`
- binary: `80 / 92 = 0.8696`
- symbol: `24 / 32 = 0.7500`
- gravity / roman / text / unit: all `100%`
- binary `format_ok_content_wrong_rate`: `0.1209`
- binary `format_failure_rate`: `0.0109`

Interpretation:

- v6 is the strongest measured proxy run in this corrective family so far.
- Compared with v4, proxy improves by `+1` row net: it flips `c30a782a` and `59c78e51` to correct, but regresses `069dbaab`.
- Compared with v5a, proxy improves by `+7` rows net and recovers the binary edge that v5a had lost.

### Official leaderboard summary

- user-reported official submissions: `0.83-0.85`
- measured range is below v4 mainline, which had `0.85-0.86`

Interpretation:

- v6 is a clear example that the current proxy set is directionally useful for binary progress but not yet calibrated well enough to choose the best public run.
- The simplest reading is not just "slight distribution shift". More precisely, the hidden/public set appears to weight some extraction-sensitive or under-covered surface slices more heavily than the current proxy does.
- Therefore v6 should be treated as a proxy-strong diagnostic branch, not as the new public mainline.

### Measured failure shape

- `results-v6/mistakes/numeral.csv` shows `11` numeral wrong rows, and all `11` are `surface_no_box` failures rather than wrong Roman strings. The last line already contains the right Roman answer surface, but boxed extraction is absent.
- Proxy persistent binary hard rows across `v20`, `v4`, `v5a`, and `v6` are now reduced to `11`: `012fb81b`, `01e09228`, `101410e4`, `12154247`, `12fd5b6c`, `1532c0d1`, `2230fad0`, `257e7158`, `2d790c98`, `31966698`, `a6192d29`.
- This means v6 did remove part of the previous hard-core set, but it did not eliminate the binary frontier debt.

### Directional conclusion

- v6 is strong enough to keep as a research branch because it exposes real binary gains that v4 and v5a do not fully capture.
- v6 is not strong enough to replace v4 as the public mainline, because official leaderboard evidence now shows `v4 > v6` despite `v6 > v4` on proxy.
- The next decision should therefore be: keep v4 as the public baseline, and use v6 only as a donor branch for the next mainline candidate.

## Generated artifacts

- `versions/v20_corrective_corpus_v6_mainline/outputs/v6_mainline_default/artifacts/corrective_selection.csv`
- `versions/v20_corrective_corpus_v6_mainline/outputs/v6_mainline_default/artifacts/corrective_overlay_unique.jsonl`
- `versions/v20_corrective_corpus_v6_mainline/outputs/v6_mainline_default/artifacts/corrective_overlay_repeated.jsonl`
- `versions/v20_corrective_corpus_v6_mainline/outputs/v6_mainline_default/artifacts/corrective_overlay_summary.json`
- `versions/v20_corrective_corpus_v6_mainline/outputs/v6_mainline_default/reports/corrective_overlay_report.md`

## Dataset composition

### Unique rows

- binary_structured_exact_core: 168
- binary_logic_exact: 56
- binary_permutation_exact: 48
- binary_prompt_local_exact: 64
- surface_numeral_boxed: 34
- surface_cipher_boxed: 6
- surface_unit_tail: 6
- surface_symbol_prefix: 4
- easy_gravity_fragile: 6
- total unique overlay problems: 392

### Repeated training rows

- binary_structured_exact_core: 341
- binary_logic_exact: 114
- binary_permutation_exact: 98
- binary_prompt_local_exact: 64
- surface stabilizer total: 56
- total repeated overlay rows: 673

### Bundle footprint

- base examples: 7828
- overlay examples: 673
- total examples: 8501
- total steps: 267
- total tokens: 28057594
- max sequence length: 7971

### Overlay supervision styles

- exact_rule_commit: 336
- exact_closure_commit: 272
- anti_default1_commit: 9
- surface_boxed_tail: 56

## Canonical validation

- passed: True
- binary max think lines: 4
- surface max think lines: 3
- mandatory anchor missing: 0
- binary non-verified contamination: 0
- surface unexpected categories: 0

## Reassessment alignment check

### 1. v6-core mainline requirements

- Fixed easy-family surface stabilizer lane: 満たす。surface lanes は numeral 34, cipher 6, unit 6, symbol-prefix 4, gravity 6 の最小構成に固定した。
- Exact binary closure lane expansion: 満たす。binary を structured 168, logic 56, permutation 48, prompt-local 64 に分割した。
- anti-`default 1` counterexample lane: 満たす。teacher-feasible な hard binary IDs に対して `anti_default1_commit` を 9 例入れた。
- minimal symbol-prefix repair lane: 満たす。`surface_symbol_prefix` を 4 行だけ入れ、broad symbol expansion は避けた。

### 2. v6-core で除外すべきもの

- short-closure rewrite lane: 入れていない
- token-skill auxiliary modernization: 入れていない
- broad cryptarithm / broad symbol answer-only expansion: 入れていない
- binary token representation change: 入れていない

### 3. README 契約との整合

- boxed-first extraction を壊さないよう surface stabilizer を別 lane で維持した。
- binary content gain を主目的にしつつ、surface を配分だけで解かず lane 分離した。
- single-file Kaggle bundle を生成し、LoRA 学習側でそのまま利用できる形式にした。

## Observed debt

- `teacher_incorrect_filtered_count = 177`。このため measured hard IDs の一部は mainline mandatory anchor に昇格させていない。
- 特に `binary_prompt_local_exact` の hard measured IDs は teacher correctness が立っておらず、mainline では lane 維持のみに留めた。
- `binary_structured_exact_core` でも persistent hard rows の一部は teacher incorrect のままで、v6-core だけでは hard-core 完治ではない。
- `results-v6/mistakes/numeral.csv` の `11` miss はすべて boxed-surface failure であり、v6 でも easy-family extraction debt が残っている。
- proxy は `180 / 200` に到達したが、official leaderboard は `0.83-0.85` に留まり、v4 より弱かった。したがって current proxy には public mainline を選ぶには無視できない blind spot がある。
- その blind spot は単なる binary family coverage 不足だけではなく、boxed-first extraction や easy-family terminal stability の hidden weighting 差を含んでいる可能性が高い。

## Next evaluation gate

- official calibration は完了し、v6 は public mainline gate を通過しなかった。
- 次の本命は `v4` を土台にしつつ、`v6` から binary gain のみを移植する mixed mainline に置くべきである。
- 具体的には、new branch の前に boxed-surface regression set を追加して、v6 で露呈した numeral no-box failure を先に封じる。
- その上で `v6-core + short-closure` 相当の binary closure donor を `v4` 系へ移植する branch を最優先にする。
- `v6-core + token-skill` は current proxy/public mismatch の原因切り分け用 second branch に下げる。
