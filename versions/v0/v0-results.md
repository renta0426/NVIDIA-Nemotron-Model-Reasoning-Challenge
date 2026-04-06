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
- `v85` train は進行中だが、**README 基準の full320 / binary60 / symbol60 score はまだ未回収**。したがって、現時点では **MLX reproduced score なし**。

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
