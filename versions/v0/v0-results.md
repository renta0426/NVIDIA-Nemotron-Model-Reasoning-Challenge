# V0 Results

## Source of truth

この v0 系列のローカル判定は **`README.md` の Evaluation 節**を唯一の基準にする。

- `max_lora_rank = 32`
- `max_tokens = 7680`
- `top_p = 1.0`
- `temperature = 0.0`
- `max_num_seqs = 64`
- `max_model_len = 8192`

加えて、metric は **`\boxed{}` 優先抽出 → heuristic fallback → last numeric fallback** を使うため、binary は official score と exact string match がズレることがある。

## Current best stable single-adapter

| version | full320 | binary | gravity | roman | symbol | text | unit | status |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `v40` | **205/320 = 0.6406** | `9/60` | `47/50` | `48/50` | `12/60` | `41/50` | `48/50` | 現在の best stable single-adapter |

`v40` の主改善は `text` / `numeric_2x2` / `bit_other` の一部で、**`bit_structured_byte_formula exact = 0/14`** は未解決のまま。

## Current best local pipeline

single-adapter は `v40` が best のままだが、**single-file multi-adapter pipeline** は actual README full320 実測でさらに大きく上回った。

| pipeline | local320 | binary | gravity | roman | symbol | text | unit | note |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `prompt-router-v4` | **267/320 = 0.8344** | `31/60` | `50/50` | `50/50` | `36/60` | `50/50` | `50/50` | `prompt-router-v3` + prompt-local safe `numeric_2x2` solver fallback |
| `prompt-router-v3` | **260/320 = 0.8125** | `31/60` | `50/50` | `50/50` | `29/60` | `50/50` | `50/50` | deterministic solver for `gravity/roman/text/unit` + `focus_v1_full` for `binary/symbol` |
| `prompt-router-v2` | `252/320 = 0.7875` | `31/60` | `50/50` | `50/50` | `29/60` | `42/50` | `50/50` | `prompt-router-v1` + output-aware base fallback on suspicious `text/roman` outputs |
| `prompt-router-v1` | `245/320 = 0.7656` | `31/60` | `50/50` | `49/50` | `29/60` | `36/50` | `50/50` | actual live router run |
| `prompt-router-v1` static join ceiling | `250/320 = 0.7812` | `30/60` | `50/50` | `50/50` | `29/60` | `41/50` | `50/50` | prior full320 row-level join; live rerun前の ceiling |

補足:

- benchmark prompt は keyword だけで **family 100% 分離**できた
- single-file `eval-phase0-router` を実装済み
- `prompt-router-v1` gate24 は **`22/24 = 0.9167`**
  - `binary 4/4`, `gravity 4/4`, `roman 4/4`, `symbol 4/4`, `text 2/4`, `unit 4/4`
- `prompt-router-v2` gate24 は **`24/24 = 1.0000`**
  - `binary 4/4`, `gravity 4/4`, `roman 4/4`, `symbol 4/4`, `text 4/4`, `unit 4/4`
- `prompt-router-v3` gate24 も **`24/24 = 1.0000`**
  - slot は `solver 16`, `specialist 8`
- `prompt-router-v4` gate24 も **`24/24 = 1.0000`**
  - initial slot は `solver 16`, `specialist 8`
  - safe `numeric_2x2` fallback は gate24 では追加発火なし
- `prompt-router-v4` full320 は **`267/320 = 0.8344`**
  - `v3` 比 **gain 7 / loss 0**
  - fallback は **7 行すべて `symbol -> solver`**
  - recovered `numeric_2x2` rows: `e8de8b47`, `379d18b7`, `5f5a73ff`, `4b70414e`, `9f2fae58`, `3acfa7a4`, `68b9b9a8`
  - `numeric_2x2` は **`29/40 -> 36/40`**
- `prompt-router-v3` full320 は **`260/320 = 0.8125`**
  - `v2` 比 **gain 8 / loss 0**
  - recovered text rows: `1ab7444c`, `a3efb940`, `b3772621`, `b3af6a44`, `d300a576`, `dc10ca9b`, `dd24b691`, `e05908dd`
  - deterministic solver slot は **`gravity/roman/text/unit = 200/200`**
- `prompt-router-v2` は actual full320 で **fallback 10 行**（`text 9`, `roman 1`）を base へ再実行し、`v1` に対して **gain 7 / loss 0**
  - recovered rows: `08bc3a02`, `3daf5caa`, `487528d5`, `b9e045e8`, `e45a4109`, `f66415c0`, `f7f9ba17`
- current `v2` miss のうち、**base が既に救える text 3 行**（`dc10ca9b`, `dd24b691`, `e05908dd`）が残っている
- old 4-model family-wise oracle **`259/320 = 0.8094`** は、`prompt-router-v4` actual により **+8** 上回った
- actual `prompt-router-v2` は external strong baseline reference **`249/320 = 0.7781`** も上回った
- actual `prompt-router-v3` は external strong baseline reference **`249/320 = 0.7781`** を **+11** 上回った
- actual `prompt-router-v4` は external strong baseline reference **`249/320 = 0.7781`** を **+18** 上回った
- 残差は **binary / symbol のみ**
  - `bit_structured_byte_formula = 6/14` official
  - `numeric_2x2 = 36/40`
  - `glyph_len5 = 0/20`
- したがって、現段階の最有力改善方向は **single-adapter 追加学習ではなく deterministic solver + hard-family specialist pipeline** である

## v110 closure と integrated follow-up

| version | design | measured result | decision |
| --- | --- | --- | --- |
| `v110` | finer-threshold `v97-lite`: `unit 64 + gravity 24 + roman 32 + symbol 24` | `gate24 21/24`, `general200 178/200`, `binary60 3/60`, `symbol60 11/60` | general 回復は real だが hard family が壊滅で mainline 不採用 |
| `v111` | finer-threshold `v97-lite`: `unit 48 + gravity 32 + roman 32 + symbol 24` | `gate24 19/24` | 不採用 |
| `v112` | finer-threshold `v97-lite`: `unit 48 + gravity 24 + roman 32 + symbol 24` | `gate24 19/24` | 不採用 |
| `v97 -> v40 (low)` | reverse continuation: symbol 寄り seed から general を戻す | `train 0.352`, `gate24 19/24` | branch closure |
| `v97 -> v40 (std)` | reverse continuation: 同上 | `train 0.361`, `gate24 18/24` | branch closure |
| `v97 -> v110 (low)` | reverse continuation: 同上 | `train 0.311`, `gate24 19/24` | branch closure |
| `v110 -> v79` | post-hoc binary repair: prompt-local current strict boxed-only-done delta | `train 0.361`, `gate24 19/24` | branch closure |
| `v110 -> v67` | post-hoc binary repair: abstract-safe + high-support verified structured delta | `train 0.360`, `gate24 19/24` | branch closure |
| `v110 -> v69` | post-hoc binary repair: answer-only-focused structured delta | `train 0.360`, `gate24 14/24` | branch closure |
| `v113` | integrated `v110 + v79` | `2160 rows`, `33 iters`, `train 0.311 -> 0.309`, `gate24 19/24` | 不採用 |
| `v114` | integrated `v110 + v67` | `2159 rows`, `33 iters`, `train 0.311 -> 0.311`, `gate24 17/24` | 不採用 |
| `v115` | integrated `v110 + (v79 + v67)` | `2175 rows`, `33 iters`, `train 0.311 -> 0.309`, `gate24 19/24` | 不採用 |

`v113-v115` は **`v110` に対して gate24 gain が 0** だった。  
row-level では `v113` が `bcdf9198(bit_other)` と `e952f61f(numeric_2x2)`、`v115` が `bcdf9198(bit_other)` と `cfa59b38(numeric_2x2)` を落とし、**binary / symbol を同時に守れなかった**。

## Strict bare-boxed prompt pivot

`v97` の `general200` regress は row-level で **`gravity 25 / unit 17 / text 14`** に偏っており、特に gravity 25 件は **`38.9 \text{m}` 型の unit suffix / latex-text 汚染**だった。  
そのため、row mix をいじる前に **boxed の中を bare final answer のみに強制する strict prompt** を sampled-new strong rows 側へ入れた。

| version | design | measured result | status |
| --- | --- | --- | --- |
| `v116` | `v97` mix + strict bare-boxed prompt on `unit + gravity` | `2114 rows`, `33 iters`, `train 0.324 -> 0.318`, `gate24 17/24` | 不採用 |
| `v117` | `v97` mix + strict bare-boxed prompt on `unit + gravity + symbol` | `2114 rows`, `33 iters`, `train 0.324 -> 0.319`, `gate24 18/24` | 不採用 |
| `v118` | `v97` mix + strict bare-boxed prompt on `unit + gravity + roman + symbol` | `2114 rows`, `33 iters`, `train 0.366 -> 0.323`, `gate24 18/24` | 不採用 |

strict bare-boxed prompt は **gravity / unit の latex-text 汚染仮説**を切る目的には沿っていたが、`v40 = 20/24` / `v97 = 21/24` を超えられなかった。  
best の `v118` でも `binary 1/4`, `symbol 2/4`, `unit 3/4` に留まり、**prompt strict 化だけで sampled-new mixed branch を mainline へ戻すのは難しい**。

## External strong baseline reference

`baseline/nemotron-sft-lora-with-cot-v2` は、**verified-correct CoT 6,558 rows** から notebook 内 sampling で **2,907 rows** を使い、README 基準 local **`249/320 = 0.7781`** を出している。

> 重要: この `249/320` は **baseline notebook/report 側の参照値**であり、**この repository の MLX run ではまだ未再現**。

| reference | local320 | binary | structured | symbol | text | unit | note |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `nemotron-sft-lora-with-cot-v2` | `249/320 = 0.7781` | `29/60` | `5/14` official | `22/60` | `49/50` | `49/50` | broad verified CoT baseline |

## Binary follow-up ledger

| version | design | measured result | decision |
| --- | --- | --- | --- |
| `v64` | solver-backed source swap: `binary_hybrid_consensus 8 + structured_recommended 16` | `binary60 official 5/60`, `exact 2/60`, `structured official/exact 1/14, 0/14` | 不採用 |
| `v65` | solver-backed source swap: `binary_hybrid_consensus 8 + structured_recommended 24` | `binary60 official 4/60`, `exact 3/60`, `structured official/exact 0/14, 0/14` | 不採用 |
| `v66` | solver-backed source swap: `binary_hybrid_consensus 16 + structured_recommended 16` | `binary60 official 5/60`, `exact 4/60`, `structured official/exact 0/14, 0/14` | 不採用 |
| `v67` | format-safe structured answer-only + high-support verified (`gap>=5`, `safe_support>=10`) | `final val 0.353`; `binary60 official 6/60`, `exact 5/60`, `structured official/exact 2/14, 1/14` | 参考保持 |
| `v68` | format-safe structured answer-only + broader high-support verified (`gap>=5`, `safe_support>=4`) | `final val 0.354`; `binary60 official 5/60`, `exact 2/60`, `structured official/exact 0/14, 0/14` | 不採用 |
| `v69` | format-safe structured answer-only only | `final val 0.357`; `binary60 official 8/60`, `exact 5/60`, `structured official/exact 1/14, 0/14` | 不採用 |

## Exact-trace-safe pivot

analysis docs を再現コードどおりに再集計すると、binary の **exact-trace-safe base は `817` rows**、現行 900-row `phase2_binary_hybrid_training_data.csv` と **非重複は `659` rows**。

non-overlap breakdown:

- `binary_structured_byte_formula = 392`
- `binary_structured_byte_formula_abstract = 152`
- `binary_structured_byte_not_formula = 25`
- `binary_affine_xor = 54`
- `binary_bit_permutation_bijection = 22`
- `binary_byte_transform = 9`
- `binary_bit_permutation_independent = 5`

この base から、single-file `mac_workspace/v0/phase2_binary_dsl_mlx_v0.py` に **exact binary program trace renderer** を追加した。trace は docs の canonical style に寄せ、`Check examples -> exact rule -> query execution -> Final answer` の固定順で `trace_boxed` teacher を出す。

## Exact-trace / boxed-twin result ledger

> 2026-04-06 修正: `v73-v81` の初回 launch では、`train --run-name ...` が既存 `prepare-train` artifact を読まず、**baseline / chat / default train args** で `prepare_manifest.json` と `mlx_lora_config.yaml` を上書きしていた。  
> そのため、下記 `v73-v75` の初回 score は **intended profile の測定値ではなく無効**。`train` subcommand は修正済みで、closure 系の corrected rerun は `v78 / v79 / v81` まで回収済み。

| version | design | prepare stats | status |
| --- | --- | --- | --- |
| `v70` | exact-trace-safe structured hard+leading-zero: `formula 16 + abstract 8` | `1970 rows`, `123 iters` | train `0.353 -> 0.339`, `binary60 official/exact 3/60, 2/60`, `structured official/exact 1/14, 0/14` |
| `v71` | exact-trace-safe structured hard broad: `formula 16 + abstract 8` | `1970 rows`, `123 iters` | train `0.353 -> 0.338`, `binary60 official/exact 7/60, 5/60`, `structured official/exact 1/14, 0/14` |
| `v72` | mixed trace pivot: `binary_candidates 8 + formula 12 + abstract 8 + not_formula 4` | `1978 rows`, `123 iters` | train `0.353 -> 0.328`, `binary60 official/exact 5/60, 5/60`, `structured official/exact 0/14, 0/14` |
| `v73` | exact-trace formula/abstract + same-prompt boxed-only twin | `1994 rows`, `124 iters` | **無効化**: 初回 train は baseline/chat default へ上書き。正しい rerun 未回収 |
| `v74` | mixed trace pivot + same-prompt boxed-only twin (`formula + abstract + not_formula`) | `2002 rows`, `125 iters` | **無効化**: 初回 train は baseline/chat default へ上書き。正しい rerun 未回収 |
| `v75` | leading-zero exact-trace + same-prompt boxed-only twin | `1994 rows`, `124 iters` | **無効化**: 初回 train は baseline/chat default へ上書き。正しい rerun 未回収 |
| `v78` | strict 8-bit prompt + closure trace + boxed-only-done twin + leading-zero focus | `1978 rows`, `123 iters` | corrected rerun train `0.353 -> 0.329`, `binary60 official/exact 3/60, 3/60`, `structured official/exact 0/14, 0/14` |
| `v79` | strict 8-bit prompt + boxed-only-done only | `1962 rows`, `122 iters` | corrected rerun train `0.353 -> 0.346`, `binary60 official/exact 6/60, 6/60`, `structured official/exact 2/14, 2/14`, `leading-zero official/exact 2/6, 2/6` |
| `v80` | leading-zero filtered `boxed_only_done` | `1962 rows`, `122 iters` | corrected rerun train `0.353 -> 0.347`, `binary60 official/exact 7/60, 4/60`, `structured official/exact 2/14, 0/14`; hits は tolerance / leading-zero collapse のみ |
| `v81` | strict 8-bit prompt + pure boxed-only | `1962 rows`, `122 iters` | corrected rerun train `0.353 -> 0.346`, `binary60 official/exact 6/60, 3/60`, `structured official/exact 1/14, 0/14`; `55f5e590` は `10001111 -> 10101111` の numeric-tolerance hit |
| `v82` | `v79` + same-row `boxed_only` twin | `1978 rows`, `123 iters` | train `0.353 -> 0.329`, `binary60 official/exact 7/60, 4/60`, `structured official/exact 0/14, 0/14` |

## Strong baseline MLX reproduction pivot

- `v85` prepare 完了:
  - source: `baseline/nemotron-sft-lora-with-cot-v2/artifacts/train_split_with_cot.csv`
  - normalized rows: `6558`
  - notebooklike sampled rows: `2907`
  - family mix: `roman 300`, `gravity 400`, `unit 700`, `text 700`, `binary 607`, `symbol 200`
  - dataset format: `chat`
  - teacher shape: `generated_cot` から既存 `\boxed{}` を除去し、`</think>\n\boxed{answer}` で閉じる
  - train config: `full-layer`, `bs=1`, `ga=8`, `lr=1e-4`, `epochs=2`, `max_seq_length=4096`
- `v85` train は完走:
  - `Iter 1 Val loss 0.679`
  - `Iter 5814 Val loss 3.683`
  - `Iter 5814 Train loss 4.873`
  - peak mem `82.705 GB`
- `v85` README eval:
  - `binary60 = 0/60`
    - `bit_other = 0/46`
    - `bit_structured_byte_formula = 0/14`
    - `boxed_extraction_success_rate = 0.0`
    - `format_failure_rate = 1.0`
  - `symbol60 = 0/60`
    - `numeric_2x2 = 0/40`
    - `glyph_len5 = 0/20`
  - binary/symbol ともに **全 60 行が `line_fallback`**, **`has_boxed = False`**, raw output prefix は **`\box the the the ...`** の同一 collapse
  - `full320 = 0/320`
    - `binary = 0/60`
    - `gravity = 0/50`
    - `roman = 0/50`
    - `symbol = 0/60`
    - `text = 0/50`
    - `unit = 0/50`
  - したがって **broad verified CoT full-layer reproduction は README 基準 local320 でも完全 collapse**
- `v86` prepare 完了:
  - profile: `strong-baseline-cot-v2-structured-anchor-v1`
  - base sampled rows: `2907`
  - augmentation: `597`
    - `binary boxed_only = 562` (`bit_structured_byte_formula verified 416 + answer_only 146`)
    - `symbol boxed_only = 35` (`numeric_2x2 verified`)
  - total train rows: `3504`
  - total iters: `7008`
- `v86` early train signal:
  - `Iter 1 Val loss 0.691`
  - `Iter 35 Train loss 0.483` までは安定
  - `Iter 45 Train loss 11.536` まで急騰
  - ただし **parallel `v85 + v86` で PhysMem `450 GB`** まで上がり、ユーザー指定 RAM cap を超えたため **手動停止 (`exit 143`)**
- `v87` prepare 完了:
  - profile: `strong-baseline-cot-v2-structured-anchor-v2`
  - `v86` の augmentation に加え `symbol numeric_2x2 answer_only = 479` を追加
  - augmentation total: `1076`
  - total train rows: `3983`
  - total iters: `7966`
  - まだ未 train
- `v85 full320 = 0/320` を受けて、queued `v86 / v87` full-layer branch は **起動前に打ち切り**。以後の strong-baseline 利用は full-layer chat 再現ではなく、`v40` seed continuation 側の data-only injection を優先する。
- strong sampled-new pivot:
  - sampled 2907 rows のうち、現行 900-row phase2 CSV に未投入の **new rows = 2560**
  - hard-family buckets:
    - `bit_structured_byte_formula verified = 189`
    - `bit_structured_byte_formula answer_only = 60`
    - `bit_other verified = 171`
    - `bit_other answer_only = 33`
    - `numeric_2x2 verified = 36`
    - `numeric_2x2 answer_only = 75`
    - `glyph_len5 answer_only = 14`
- `v88` prepare / train 完了:
  - profile: `single-adapter-fusion-v88`
  - design: `v40` core + strong baseline sampled-new hard-family rows (`binary 434`, `symbol 121`)
  - total train rows: `2517`
  - total iters: `39`
  - train `0.554 -> 0.458`
  - peak mem `121.316 GB`
  - note: longest sentence `2495 > 2048` の truncate warning が 1 回出た
  - `binary60 official/exact = 6/60, 5/60`
    - `bit_other official/exact = 6/46, 5/46`
    - `bit_structured_byte_formula official/exact = 0/14, 0/14`
    - `verified/manual/answer_only = 5/1/0`
    - `boxed_extraction_success_rate = 0.15`
    - `format_failure_rate = 0.9333`
    - structured 14 行は **`numeric_fallback 13 + boxed 1`**
  - したがって **hard-family sampled-new notebook CoT append は `v40` binary branch を超えられず不採用**
- `v89` prepare 完了:
  - profile: `single-adapter-fusion-v89`
  - design: `v88 + text anchor 64 verified + 64 answer_only`
  - total train rows: `2645`
  - total iters: `41`
  - まだ未 train
- `v90` prepare 完了:
  - profile: `single-adapter-fusion-v90`
  - design: same sampled-new hard-family rows を **conservative quota 168 rows** に絞り、teacher を **`boxed_only_done`** へ短文化
  - total train rows: `2130`
  - total iters: `33`
  - augmentation: `binary 128`, `symbol 40`
  - train `0.331 -> 0.330`
  - peak mem `74.475 GB`
  - `binary60 official/exact = 7/60, 5/60`
    - `bit_other official/exact = 7/46, 5/46`
    - `bit_structured_byte_formula official/exact = 0/14, 0/14`
    - `verified/manual/answer_only = 5/0/2`
    - `boxed_extraction_success_rate = 0.15`
    - `format_failure_rate = 0.9`
    - structured 14 行は **`numeric_fallback 14`**
  - `v88 (6/60, exact 5/60)` より official は +1 だが、**`v40` binary branch は超えられず不採用**
- `v91` prepare 完了:
  - profile: `single-adapter-fusion-v91`
  - design: `v90` と同一 quota / same rows で、teacher だけ **pure `boxed_only`** に切り替えた clean ablation
  - total train rows: `2130`
  - total iters: `33`
  - augmentation: `binary 128`, `symbol 40`
  - train `0.327 -> 0.329`
  - peak mem `74.475 GB`
  - `binary60` 初回並列は RAM cap 超過回避のため停止し、**1-shard rerun** で回収
  - `binary60 official/exact = 5/60, 5/60`
    - `bit_other official/exact = 5/46, 5/46`
    - `bit_structured_byte_formula official/exact = 0/14, 0/14`
    - `verified/manual/answer_only = 5/0/0`
    - `boxed_extraction_success_rate = 0.1333`
    - `format_failure_rate = 0.9167`
    - structured 14 行は **`numeric_fallback 14`**
  - **pure `boxed_only` は `boxed_only_done` の `v90` を下回り不採用**
- `v92` prepare / train / gate24 完了:
  - profile: `single-adapter-fusion-v92`
  - design: sampled-new general verified rowsだけを **short `boxed_only_done`** に蒸留して `v40` continuation へ追加
  - augmentation: `text 96`, `unit 64`, `gravity 32`, `roman 32`, `symbol 24` （計 `248`）
  - total train rows: `2210`
  - total iters: `34`
  - train `0.335 -> 0.325`
  - peak mem `74.475 GB`
  - `gate24 official/exact = 19/24, 16/24`
    - `general_stable = 14/16`
    - `binary_hard = 3/4`
    - `symbol_watch = 2/4`
    - `binary boxed_extraction_success_rate = 1.0`
    - `binary regex_exact_rate = 0.75`
- `v93` prepare / train / gate24 完了:
  - profile: `single-adapter-fusion-v93`
  - design: `v92` と同一 rows / quota で、teacher だけ **pure `boxed_only`**
  - augmentation: `text 96`, `unit 64`, `gravity 32`, `roman 32`, `symbol 24` （計 `248`）
  - total train rows: `2210`
  - total iters: `34`
  - train `0.331 -> 0.323`
  - peak mem `74.475 GB`
  - `gate24 official/exact = 19/24, 16/24`
    - `general_stable = 14/16`
    - `binary_hard = 3/4`
    - `symbol_watch = 2/4`
    - `binary boxed_extraction_success_rate = 0.75`
    - `binary regex_exact_rate = 0.75`
- `v96` prepare / train / gate24 完了:
  - profile: `single-adapter-fusion-v96`
  - design: `v92` の **no-text** variant。sampled-new `unit 64 / gravity 32 / roman 32 / symbol 24` を **`boxed_only_done`** で追加
  - augmentation: `unit 64`, `gravity 32`, `roman 32`, `symbol 24` （計 `152`）
  - total train rows: `2114`
  - `gate24 official/exact = 20/24, 16/24`
    - `general_stable = 14/16`
    - `binary_hard = 3/4`
    - `symbol_watch = 3/4`
    - `binary boxed_extraction_success_rate = 0.75`
    - `binary regex_exact_rate = 0.75`
  - `v40` same-slice 比では **official tie / exact +1**
    - gains: `c625ba91` (`bit_other`), `db6a5663` / `cfa59b38` (`numeric_2x2`)
    - losses: `e17e76cc`, `c0e9cf43` (`text_monoalphabetic`), `e952f61f` (`numeric_2x2 -> your answer`)
- `v97` prepare / train / gate24 完了:
  - profile: `single-adapter-fusion-v97`
  - design: `v96` と同一 no-text rows / quota で、teacher だけ **pure `boxed_only`**
  - augmentation: `unit 64`, `gravity 32`, `roman 32`, `symbol 24` （計 `152`）
  - total train rows: `2114`
  - `gate24 official/exact = 21/24, 17/24`
    - `general_stable = 16/16`
    - `binary_hard = 2/4`
    - `symbol_watch = 3/4`
    - `binary boxed_extraction_success_rate = 0.75`
    - `binary regex_exact_rate = 0.5`
  - `v40` same-slice 比では **gain 1 / loss 0 = net +1**
    - gain: `cfa59b38` (`numeric_2x2 = 233`)
  - `README.md` gate24 条件では、この no-text branch の **現 best**
  - `symbol60 official/exact = 20/60, 20/60`
    - `numeric_2x2 = 20/40`
    - `glyph_len5 = 0/20`
    - `verified/manual/answer_only = 13/0/7`
    - `numeric/symbolic = 19/36, 1/24`
  - `v40 symbol60 = 12/60` 比では **gain 10 / loss 2 = net +8**
    - gains は `numeric_2x2` verified `6`, answer_only `4`
    - losses は `numeric_2x2` answer_only `2`
  - `general200 official = 144/200`
    - `gravity 25/50`
    - `roman 50/50`
    - `text 36/50`
    - `unit 33/50`
  - same 200-row control `v40 = 184/200` 比では **gain 11 / loss 51 = net -40**
    - gains: `text 5`, `gravity 2`, `roman 2`, `unit 2`
    - losses: `gravity 24`, `unit 17`, `text 10`
  - failure mode は `gravity` の boxed numeric tolerance miss と、`unit/text` の **`last_number` numeric fallback**
  - したがって `v97` は **full320 昇格候補ではなく、symbol specialist branch** として扱う
- `v98` prepare / train / gate24 完了:
  - profile: `single-adapter-fusion-v98`
  - design: `v96` からさらに symbol も外した **numeric-only** variant。sampled-new `unit 64 / gravity 32 / roman 32` を **`boxed_only_done`** で追加
  - augmentation: `unit 64`, `gravity 32`, `roman 32` （計 `128`）
  - total train rows: `2090`
  - `gate24 official/exact = 18/24, 15/24`
    - `general_stable = 15/16`
    - `binary_hard = 1/4`
    - `symbol_watch = 2/4`
    - `binary boxed_extraction_success_rate = 0.5`
    - `binary regex_exact_rate = 0.25`
  - `v40` same-slice 比では **gain 1 / loss 3 = net -2**
    - gain: `cfa59b38` (`numeric_2x2`)
    - losses: `2bd7896f` (`unit_fixed_ratio`), `bcdf9198` (`bit_other -> your answer`), `5b06502f` (`numeric_2x2 -> your answer`)
- `v99` prepare / train / gate24 完了:
  - profile: `single-adapter-fusion-v99`
  - design: sampled-new **symbol 24 only** の clean ablation。teacher は **pure `boxed_only`**
  - final val **`0.348`**
  - `gate24 official = 18/24`
    - `binary 2/4`, `gravity 4/4`, `roman 4/4`, `symbol 1/4`, `text 3/4`, `unit 4/4`
  - pure symbol-only にすると `numeric_2x2` が **1/4** まで落ち、`v40` を超えなかった
- `v100` prepare / train / gate24 / symbol60 完了:
  - profile: `single-adapter-fusion-v100`
  - design: `v99` と同じ **symbol 24 only** で、teacher だけ **`boxed_only_done`**
  - final val **`0.347`**
  - `gate24 official = 19/24`
    - `binary 1/4`, `gravity 4/4`, `roman 4/4`, `symbol 3/4`, `text 3/4`, `unit 4/4`
    - `v99` より `symbol/text` は戻ったが、`bit_other` が **1/4** まで崩れた
  - `symbol60 official = 9/60`
    - `numeric_2x2 = 9/40`
    - `glyph_len5 = 0/20`
    - `verified/manual/answer_only = 7/0/2`
    - `numeric/symbolic = 9/36, 0/24`
  - `v40 symbol60 = 12/60` よりも悪く、**direct symbol-only + `Done.`** は specialist としても不採用
- `v101` prepare / train / gate24 完了:
  - profile: `single-adapter-fusion-v101`
  - design: joined sampled-new symbol mix。`numeric_2x2 verified 16 + answer_only 8 + glyph_len5 8` を **`boxed_only`** で narrow append
  - final val **`0.346`**
  - `gate24 official = 18/24`
    - `binary 2/4`, `gravity 4/4`, `roman 4/4`, `symbol 2/4`, `text 2/4`, `unit 4/4`
  - failure 6 件のうち **4 件が `\boxed{your answer}`** で、glyph/numeric joined mix は format 汚染だけを増やした
- `v102` prepare / train / gate24 完了:
  - profile: `single-adapter-fusion-v102`
  - design: sampled-new **roman 32 + symbol 24** の clean ablation。teacher は **pure `boxed_only`**
  - final val **`0.349`**
  - `gate24 official = 17/24`
    - `binary 1/4`, `gravity 4/4`, `roman 4/4`, `symbol 0/4`, `text 4/4`, `unit 4/4`
  - general 16/16 は守った一方で、`bit_other` は `1/4`、`numeric_2x2` は **`0/4`** まで崩れた。`roman` 追加だけでは `v97` の specialist gain を再現できない
- `v103` prepare / train / gate24 完了:
  - profile: `single-adapter-fusion-v103`
  - design: `v102` と同じ **roman 32 + symbol 24** で、teacher だけ **`boxed_only_done`**
  - final val **`0.350`**
  - `gate24 official = 18/24`
    - `binary 1/4`, `gravity 4/4`, `roman 4/4`, `symbol 1/4`, `text 4/4`, `unit 4/4`
  - `Done.` 追加で `numeric_2x2` を **1 問だけ**戻したが、`bit_other` は依然 `1/4` のまま。roman+symbol mix 全体としては dead branch
- `v104` prepare / train / gate24 完了:
  - profile: `single-adapter-fusion-v104`
  - design: sampled-new **unit 64 + gravity 32 + symbol 24**。`v97` から **roman 32** だけを外した ablation
  - final val **`0.326`**
  - `gate24 official = 19/24`
    - `binary 1/4`, `gravity 4/4`, `roman 4/4`, `symbol 2/4`, `text 4/4`, `unit 4/4`
  - `v104` は `v104-v106` の中では best だったが、**`v97 = 21/24` には 2 問届かない**。`unit` と `gravity` の両方は効いているが、roman もまだ必要
- `v105` prepare / train / gate24 完了:
  - profile: `single-adapter-fusion-v105`
  - design: sampled-new **unit 64 + symbol 24**。gravity を落とした ablation
  - final val **`0.314`**（3 本中で最良）
  - `gate24 official = 17/24`
    - `binary 2/4`, `gravity 4/4`, `roman 4/4`, `symbol 0/4`, `text 3/4`, `unit 4/4`
  - train val は最良でも、`numeric_2x2` が **0/4** に沈み、text も 1 件落とした。**train val と README gate は相関しない**ことを再確認した
- `v106` prepare / train / gate24 完了:
  - profile: `single-adapter-fusion-v106`
  - design: sampled-new **gravity 32 + symbol 24**。unit を落とした ablation
  - final val **`0.350`**
  - `gate24 official = 18/24`
    - `binary 2/4`, `gravity 4/4`, `roman 4/4`, `symbol 1/4`, `text 3/4`, `unit 4/4`
  - gravity だけでも `v105` より `numeric_2x2` は戻るが、text が 1 件崩れる。**gravity 単独 / unit 単独のどちらでも `v97` の mixed-context には届かない**
- `v107` prepare / train / gate24 完了:
  - profile: `single-adapter-fusion-v107`
  - design: `v97-lite` その1。sampled-new **unit 64 + gravity 16 + roman 32 + symbol 24**
  - final val **`0.310`**
  - `gate24 official = 20/24`
    - `binary 1/4`, `gravity 4/4`, `roman 4/4`, `symbol 3/4`, `text 4/4`, `unit 4/4`
  - gravity quota を **32 → 16** に落とすと、general は守れても **binary が `2/4 -> 1/4`** に落ちて `v97 = 21/24` を維持できなかった
- `v108` prepare / train / gate24 完了:
  - profile: `single-adapter-fusion-v108`
  - design: `v97-lite` その2。sampled-new **unit 32 + gravity 32 + roman 32 + symbol 24**
  - final val **`0.325`**
  - `gate24 official = 18/24`
    - `binary 1/4`, `gravity 4/4`, `roman 4/4`, `symbol 1/4`, `text 4/4`, `unit 4/4`
  - unit quota を **64 → 32** に落とすと劣化が大きく、`numeric_2x2` と `bit_other` が同時に崩れた。**unit quota の方が gravity より重要**だと読める
- `v109` prepare / train / gate24 完了:
  - profile: `single-adapter-fusion-v109`
  - design: `v97-lite` その3。sampled-new **unit 32 + gravity 16 + roman 32 + symbol 24**
  - final val **`0.309`**（3 本中で最良）
  - `gate24 official = 19/24`
    - `binary 2/4`, `gravity 4/4`, `roman 4/4`, `symbol 2/4`, `text 3/4`, `unit 4/4`
  - val は最良でも README gate では `v107` に負け、**train val と gate24 の非相関**を再確認した。両 quota を一気に軽くすると `text` まで 1 件落ちる

## Current interpretation

1. **broad answer-only / solver-backed source swap だけでは structured exact は動かない。**
2. 次の本命は、`README.md` の boxed extraction を維持したまま **exact executable rule を短い program trace で教える** route。
3. `v67-v69` は narrow format-safe pivot としては一定の改善を出したが、structured failure の大半は依然 **`numeric_fallback / last_number`** で、boxed retention は回復していない。
4. `v67` だけが `bdd63604` で **structured exact 1/14** を取った一方、他の structured official hit は `00000000 -> 000/0` のような leading-zero collapse だった。
5. `v70-v72` は hyperparameter sweep ではなく、**data/teacher redesign only** の follow-up だったが、**structured exact は 3 本とも `0/14`** に留まった。
6. `v71` は official `7/60` で exact-trace 3 本中ベストだが、structured official hit は `1bf84ce3: 00000000 -> 0` の collapse だけで、exact recovery ではない。
7. `v72` は train 側では `final val 0.328` と最良だったが、`binary60` では `5/60` に留まり、**train val と binary hard eval の相関が弱い**ことを再確認した。
8. v71/v72 の train dataset を確認すると、**exact-trace teacher 24 rows は全件 `\boxed{}` を含んでいた**。したがって current failure は teacher 欠落ではなく、**generation-time format retention collapse** である。
9. `v73-v75` の初回記録は現在 **撤回**している。2026-04-06 に、`train --run-name ...` が既存 prepared config を読まず **baseline/chat default** (`lr=1e-4`, `batch=1`, `epochs=2`, `layers=-1`) で上書きしていたことを確認した。
10. `train` subcommand は修正済みで、closure follow-up は **prepared config 再利用**に切り替えた。`v78 / v79 / v81` の corrected rerun はすべて回収済み。
11. `v78` は `final val 0.329` でも `binary60 official/exact 3/60, 3/60` と弱く、**leading-zero focus + closure trace** 単独では効かなかった。
12. `v79` は **`binary60 official/exact 6/60, 6/60`**, **`structured official/exact 2/14, 2/14`**, **`leading-zero exact 2/6`** を達成し、現時点の valid run では **structured exact の新 best**。ただし structured 14 行は依然すべて `last_number` fallback で、boxed retention 自体は回復していない。
13. `v81` は official `6/60` で `v79` に並んだが、exact は `3/60` まで落ちた。`55f5e590` の structured official hit は `10001111 -> 10101111` が **README.md の numeric tolerance** で通っただけで、exact recovery ではない。
14. `v79` vs `v81` から、prompt/teacher の `Done.` 矛盾を消すこと自体は主因ではなかった。**pure boxed-only は boxed count を増やしても structured exact を押し上げない**。
15. `v80` は official `7/60` まで上がったが、exact は `4/60` に落ち、structured 14 行は **全件 `last_number` fallback** だった。leading-zero filtered `boxed_only_done` だけでは `v79` を超えない。
16. `v82` も official `7/60`, exact `4/60` で、**same-row boxed-only twin は `v79` の structured exact 2/14 を保持できなかった**。structured 14 行は `boxed 0`, `last_number 14` のまま。
17. したがって `v79` 近傍の local boxed-twin / leading-zero tweak はここでいったん閉じ、次の本命は **`nemotron-sft-lora-with-cot-v2` の broad verified CoT baseline を MLX 単一ファイルへ移植する `v85`** に置く。
18. 次の判定軸は引き続き **README.md 基準の full320 / binary60 / symbol60** だが、今後は **修正後に再実行した run だけ**を ledger に残す。
19. `v85` は **binary60 = 0/60**, **symbol60 = 0/60** で、teacher 欠落ではなく **generation-time の broad collapse** を起こした。binary/symbol はどちらも `\box the the the ...` の無箱 line fallback に潰れている。
20. したがって、strong baseline 由来の価値は **full-layer chat reproduction そのもの**ではなく、**sampled-new verified CoT rows を stable `v40` へ注入する data-only continuation** にあると解釈を更新した。
21. `v88` は **official/exact 6/60, 5/60** でも structured exact `0/14`、answer-only `0/20` に留まり、**sampled-new hard-family rows 自体より notebooklike 長尺 CoT 注入が悪さをしている**と解釈するのが自然。
22. `v85 full320 = 0/320` まで確定したため、**strong baseline の full-layer chat reproduction 系はこの環境では dead branch** と判断した。`v86/v87` queued run も起動前に止めている。
23. そのため次枝は、**same sampled-new rows / smaller quota / short-output teacher** の clean ablation `v90/v91` に切り替えた。結果は `v90 = 7/60 (exact 5/60)`, `v91 = 5/60 (exact 5/60)` で、**`Done.` 追加の有無を変えても structured exact は 0/14 のまま**。この short-teacher strong-sampled-new branch も一旦閉じる。
24. sampled-new general verified rows の short-teacher continuation `v92/v93` は、**gate24 でどちらも `19/24`**。same slice の control `v40 = 20/24` を official では超えられなかった。
25. ただし `v92/v93` は **binary を `2/4 -> 3/4`** まで押し上げ、overall exact も `15/24 -> 16/24` に改善した一方、**text が `4/4 -> 2/4`** へ落ちて net `-1` になった。つまり sampled-new general branch の問題は broad no-text families ではなく、**text short-teacher injection の regress** にある可能性が高い。
26. `v92` と `v93` の official/exact は同点だが、binary formatting は **`boxed_only_done` の `v92` がやや良い**。もしこの general short-teacher 枝を続けるなら、次は **text を外した `v92` 系** から入るのが自然。
27. `v96-v98` により、その仮説は当たりだった。**text short-teacher rows を外すだけで** `v97 = 21/24`, `v96 = 20/24` まで戻り、`v92/v93` の net regress は text 注入が主因だったとみなせる。
28. no-text branch の内部比較では、**pure `boxed_only` の `v97` が `boxed_only_done` の `v96` を上回った**。`v97` は `v40` 比で **gain 1 / loss 0**、`v96` は official tie のまま text 2 件を落としている。
29. 一方で symbol まで外した `v98` は **18/24** まで落ち、`bit_other` と `unit_fixed_ratio` に `your answer` / numeric fallback を再発させた。したがって no-text branch を続けるなら、**symbol 24 は残す**のが自然。
30. `README.md` gate24 条件では、sampled-new general short-teacher best は **`v97 = 21/24, exact 17/24`** だったが、deeper triage の `general200` では **`144/200`** に沈んだ。
31. same 200-row control の `v40 = 184/200` に対し、`v97` は **gain 11 / loss 51 = net -40**。loss は **`gravity -22`**, **`unit -15`**, **`text -5`** に集中し、`roman` だけが **+2** だった。
32. `gravity` の regress は boxed answer 自体は出しつつ **数値丸めの微差**で落ちており、`unit/text` は **`last_number` numeric fallback** が支配的だった。つまり no-text branch の regress は symbol ではなく、**sampled-new general rows 側**にある。
33. 一方で `v97` は `symbol60` では **`20/60`** まで伸び、`v40 = 12/60` を **+8** 更新した。増分はほぼ `numeric_2x2` で、**verified 13/15, answer_only 7/15** まで回復している。
34. ただし `glyph_len5 = 0/20`, `manual_audit_priority = 0/30` は依然として不変で、symbol 側の未回収部分は **glyph/manual symbolic** に集中している。したがって次枝は、**unit/gravity/roman を切った sampled-new symbol-only short-teacher** が本命になる。
35. その clean ablation として切った `v99-v101` は、**gate24 が `18/24`, `19/24`, `18/24`** で全滅した。pure symbol-only にすると `numeric_2x2` すら落ち、glyph joined mix は `\boxed{your answer}` を増やした。
36. best の `v100` でも `symbol60 = 9/60` で、control `v40 = 12/60` より悪かった。したがって **`v97` の symbol gain は symbol rows 単体では再現せず、何らかの mixed-context が必要**とみなせる。
37. `v97 general200` の same-200 比較では `roman +2` が唯一の plus だったが、実際に切った `v102/v103` の **roman+symbol mix は `17/24`, `18/24`** で失敗した。general 16/16 は保てても、**binary/symbol は `1/4`・`0-1/4`** まで崩れる。
38. したがって **`roman` は `v97` の specialist gain を支えていた mixed context ではない**。`v97` の効きは `unit/gravity` 側の numeric context にある可能性が高い。
39. `v104-v106` により、sampled-new support は **`unit + gravity + symbol = 19/24`**, **`gravity + symbol = 18/24`**, **`unit + symbol = 17/24`** の順だった。つまり **unit と gravity の両方が寄与**しており、片方だけでは `v97` の specialist gain を再現できない。
40. 一方で `v104` でも **`v97 = 21/24` より -2** なので、`roman` も「単独では無力だが、unit/gravity がある前提では still helpful」な可能性が高い。`v102-v106` をまとめると、**必要なのは family drop ではなく `v97` の mixed context を保ったまま collateral source を軽くすること**だと読める。
41. その仮説に基づいて切った `v107-v109` は **`20/24`, `18/24`, `19/24`** で全滅した。したがって、**quota を大きく落とす `v97-lite` は specialist mixed-context を保持できない**。
42. 劣化の大きさを見ると、**gravity 32 → 16 は `21/24 -> 20/24`、unit 64 → 32 は `21/24 -> 18/24`** だった。つまり sampled-new mixed-context では **unit quota の方が gravity quota より重要**で、`v97` の効きは `unit` 側により強く依存している。
43. 一方で `v107 = 20/24` は `v109 = 19/24` より良く、**gravity を軽く削ること自体は完全には外れていない**。次の本命は、`32 → 16` / `64 → 32` のような大きい削りではなく、**`gravity 32 → 24` と `unit 64 → 48` の finer threshold sweep** に置く。
