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

## New versions in progress

| version | design | prepare stats | status |
| --- | --- | --- | --- |
| `v70` | exact-trace-safe structured hard+leading-zero: `formula 16 + abstract 8` | `1970 rows`, `123 iters` | train `0.353 -> 0.339`, `binary60 official/exact 3/60, 2/60`, `structured official/exact 1/14, 0/14` |
| `v71` | exact-trace-safe structured hard broad: `formula 16 + abstract 8` | `1970 rows`, `123 iters` | train `0.353 -> 0.338`, `binary60 official/exact 7/60, 5/60`, `structured official/exact 1/14, 0/14` |
| `v72` | mixed trace pivot: `binary_candidates 8 + formula 12 + abstract 8 + not_formula 4` | `1978 rows`, `123 iters` | train `0.353 -> 0.328`, `binary60 official/exact 5/60, 5/60`, `structured official/exact 0/14, 0/14` |

## Current interpretation

1. **broad answer-only / solver-backed source swap だけでは structured exact は動かない。**
2. 次の本命は、`README.md` の boxed extraction を維持したまま **exact executable rule を短い program trace で教える** route。
3. `v67-v69` は narrow format-safe pivot としては一定の改善を出したが、structured failure の大半は依然 **`numeric_fallback / last_number`** で、boxed retention は回復していない。
4. `v67` だけが `bdd63604` で **structured exact 1/14** を取った一方、他の structured official hit は `00000000 -> 000/0` のような leading-zero collapse だった。
5. `v70-v72` は hyperparameter sweep ではなく、**data/teacher redesign only** の follow-up だったが、**structured exact は 3 本とも `0/14`** に留まった。
6. `v71` は official `7/60` で exact-trace 3 本中ベストだが、structured official hit は `1bf84ce3: 00000000 -> 0` の collapse だけで、exact recovery ではない。
7. `v72` は train 側では `final val 0.328` と最良だったが、`binary60` では `5/60` に留まり、**train val と binary hard eval の相関が弱い**ことを再確認した。
8. v71/v72 の train dataset を確認すると、**exact-trace teacher 24 rows は全件 `\boxed{}` を含んでいた**。したがって current failure は teacher 欠落ではなく、**generation-time format retention collapse** である。
