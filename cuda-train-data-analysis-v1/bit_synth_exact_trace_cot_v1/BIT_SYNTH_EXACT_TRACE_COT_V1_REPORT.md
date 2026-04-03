# bit_synth_exact_trace_cot_v1 解説レポート

## 1. 生成物

- CSV: `cuda-train-data-analysis-v1/bit_synth_exact_trace_cot_v1/bit_synth_exact_trace_cot_training_data_v1.csv`
- Manifest: `cuda-train-data-analysis-v1/bit_synth_exact_trace_cot_v1/bit_synth_exact_trace_cot_manifest_v1.json`
- Generator: `cuda-train-data-analysis-v1/bit_synth_exact_trace_cot_v1/generate_bit_synth_exact_trace_cot_v1.py`

このデータは `data/train.csv` の原本行を混ぜずに、bit manipulation の exact-trace-safe seed から新規合成した **10,000 行** の LoRA SFT 用 CSV である。

---

## 2. README.md に基づく設計前提

`README.md` の Evaluation 節では、本番採点は **最終的な `\boxed{}` 内の答え抽出を最優先** すると明記されている。したがって本データでは、推論時の出力形に寄せるために以下の形式を採用した。

1. `generated_cot` は `<think> ... </think>` のみを持つ
2. 最終 8-bit 答えは `generated_cot` 内に書かない
3. 学習時の assistant message は `generated_cot + "\n\n\\boxed{answer}"` で再構成される前提に合わせる

この方針により、CoT 部分は「規則同定と手続き」を学習させつつ、採点対象である最終 `\boxed{}` を汚さない。

README 記載の本番推論パラメータも前提にしている。

- `max_tokens = 7680`
- `top_p = 1.0`
- `temperature = 0.0`
- `max_num_seqs = 64`
- `max_model_len = 8192`

---

## 3. 10,000 行の strong group 内訳

| strong group | rows | share |
| --- | ---: | ---: |
| `binary_structured_byte_formula` | 5,472 | 54.72% |
| `binary_structured_byte_formula_abstract` | 1,868 | 18.68% |
| `binary_affine_xor` | 1,297 | 12.97% |
| `binary_bit_permutation_bijection` | 871 | 8.71% |
| `binary_structured_byte_not_formula` | 309 | 3.09% |
| `binary_byte_transform` | 120 | 1.20% |
| `binary_bit_permutation_independent` | 63 | 0.63% |
| **total** | **10,000** | **100.00%** |

要するに、この v1 データは **structured-byte 系が 7,649 行で全体の 76.49%** を占め、残りを affine / permutation / byte transform が支える構成になっている。

---

## 4. coverage

### seed coverage

- exact-trace-safe seed config 総数: `817`
- 実際に使われた distinct seed rows: `814`
- 未使用 seed rows: `3`

### exact rule coverage

- distinct exact rules used: `406`

### seed usage histogram

| per-seed usage count | number of seed rows |
| --- | ---: |
| 12 | 591 |
| 13 | 214 |
| 14 | 9 |
| 0 | 3 |

基本的には 817 seed に対して 10,000 行をほぼ均等に配りつつ、prompt 重複回避と fallback generation の結果として一部 seed が 13-14 回使われ、3 seed は未使用になった。

---

## 5. 代表的な exact rule

### 全体 top

| exact rule | rows |
| --- | ---: |
| `o1 <- i8|o2 <- i1|o3 <- i2|o4 <- i3|o5 <- i4|o6 <- i5|o7 <- i6|o8 <- i7` | 183 |
| `o1 <- i6|o2 <- i7|o3 <- i8|o4 <- i1|o5 <- i2|o6 <- i3|o7 <- i4|o8 <- i5` | 161 |
| `o1 <- i4|o2 <- i5|o3 <- i6|o4 <- i7|o5 <- i8|o6 <- i1|o7 <- i2|o8 <- i3` | 158 |
| `o1 <- i2|o2 <- i3|o3 <- i4|o4 <- i5|o5 <- i6|o6 <- i7|o7 <- i8|o8 <- i1` | 150 |
| `xor(shl1,shr5)` | 136 |
| `xor(shl1,shr4)` | 135 |
| `o1 <- i7|o2 <- i8|o3 <- i1|o4 <- i2|o5 <- i3|o6 <- i4|o7 <- i5|o8 <- i6` | 132 |
| `xor(shl3,shr1)` | 121 |
| `xor(shl1,shr3)` | 110 |
| `xor(shl2,shr1)` | 110 |

上位は **rotation 型 bijection** と **shift-xor structured formula** が支配的である。

### group 別の代表 rule

| group | representative rules |
| --- | --- |
| `binary_structured_byte_formula` | `xor(shl1,shr5)`, `xor(shl1,shr4)`, `xor(shl3,shr1)`, `or(ror2,shl3)` |
| `binary_structured_byte_formula_abstract` | `choose(shl1,shr2,nibble_swap)`, `choose(shl2,shr1,ror3)`, `and(ror3,shr1)`, `majority(ror2,shl3,shr4)` |
| `binary_structured_byte_not_formula` | `xor(not(shl2),shl6)`, `choose(not(ror2),not(shl3),rol3)`, `or(not(shr1),shr3)` |
| `binary_affine_xor` | `i5|i6|i7|i8|0|0|i1|i2`, `i6|i7|i1 xor i8|i2|i3|i4|i5|i6` |
| `binary_bit_permutation_bijection` | cyclic rotation 系の `o1 <- ... | o8 <- ...` mapping |
| `binary_bit_permutation_independent` | repeated-source / optional invert を含む copy mapping |
| `binary_byte_transform` | `rshift`, `lrot`, `lshift` |

---

## 6. answer distribution

- distinct 8-bit answers observed: `256 / 256`

つまり、出力側は 8-bit 全空間を一応カバーしている。頻出 answer は以下。

| answer | rows |
| --- | ---: |
| `00000000` | 328 |
| `11111111` | 120 |
| `10000001` | 107 |
| `00000001` | 98 |
| `10000000` | 95 |
| `00000010` | 93 |
| `00100000` | 89 |
| `01000000` | 86 |
| `01000001` | 86 |
| `00000011` | 81 |

ゼロや sparse bit pattern はやや多いが、回答空間そのものは偏り切っていない。

---

## 7. 品質チェック結果

最終 CSV に対して確認済みの項目は以下。

| check | result |
| --- | --- |
| row count | `10,000` |
| columns | `id,prompt,answer,generated_cot,label,assistant_style,source_selection_tier` |
| duplicate prompts | `0` |
| duplicate ids | `0` |
| overlap with `data/train.csv` prompts | `0` |
| rows whose `generated_cot` contains final answer | `0` |
| bad `<think>` wrapper rows | `0` |
| bad `assistant_style` rows | `0` |
| bad `source_selection_tier` rows | `0` |
| reject reason during generation | `max_attempts_exceeded = 37` |

したがって、少なくとも CSV 形式・prompt 重複・answer leak・原本混入の観点では、この 10,000 行は v1 の strict gate を通過している。

---

## 8. 1 行の構造

各行は次の 7 列で構成される。

| column | meaning |
| --- | --- |
| `id` | deterministic hash-based synthetic row id |
| `prompt` | 8-bit 例題列 + query を含む問題文 |
| `answer` | final 8-bit answer |
| `generated_cot` | `<think>` 内の short program-trace teacher |
| `label` | 常に `binary` |
| `assistant_style` | 常に `trace_boxed` |
| `source_selection_tier` | 常に `synthetic_exact_trace_ready` |

`generated_cot` では、原則として次の順に短く記述している。

1. `Check examples:`
2. 例からの rule 同定
3. `So the rule is ...`
4. query に対する実行手順
5. `Constraints: exact_8bit, leading_zeros, box_only_final.`

---

## 9. 再現コマンド

生成:

```bash
uv run python cuda-train-data-analysis-v1/bit_synth_exact_trace_cot_v1/generate_bit_synth_exact_trace_cot_v1.py \
  --target-rows 10000 \
  --output-csv cuda-train-data-analysis-v1/bit_synth_exact_trace_cot_v1/bit_synth_exact_trace_cot_training_data_v1.csv \
  --manifest-json cuda-train-data-analysis-v1/bit_synth_exact_trace_cot_v1/bit_synth_exact_trace_cot_manifest_v1.json
```

このレポートの主な数字は、上記 generator と manifest / final CSV を再読して再構成したものである。

---

## 10. このデータの読み方

この v1 データは、「答えの丸暗記」ではなく、

- examples から同一 rule を同定する
- query に対して同じ操作を適用する
- 最後だけ `\boxed{}` に出す

という teacher を大量供給するためのものだと理解すればよい。

特に主成分は structured-byte formula と bijection / affine なので、**bit manipulation の中でも procedural regularity が高い領域に強く寄せた 10,000 行** になっている。
