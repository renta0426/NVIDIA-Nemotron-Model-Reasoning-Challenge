# train_split_with_cot_v2 strategy

## 1. 前提

`README.md` の評価は **Accuracy** で、最終解答は `\boxed{}` 優先で抽出される。  
binary では exact 8-bit string と leading zero の保持が重要なので、今回の学習データ更新は **binary の内容誤りを減らしつつ、既存 v2 の boxing 改善を壊しにくいこと**を最優先にした。

## 2. 現行 `nemotron-sft-lora-with-cot-v2` の見立て

### 2.1 スコア

| run | overall | binary | `bit_structured_byte_formula` | binary boxed success |
| --- | ---: | ---: | ---: | ---: |
| `result/0` rule-based baseline | `0.6750` | `11/60` | `1/14` | `0.2167` |
| `nemotron-sft-lora-with-cot-v2` | local `0.7781` / public `0.70-0.72` | `29/60` | `5/14` | `0.8333` |

### 2.2 何が残差か

- v2 binary は `50/60` が boxed で出ており、format はかなり改善済み
- 残る 31 誤答のうち、主成分は **boxed できているが中身が wrong**
- hardest slice は依然 `bit_structured_byte_formula`

したがって次の一手は、boxing 練習の追加ではなく、**structured binary の高信頼 trace を増やす**のが最も自然。

## 3. なぜ今回の v2 データは保守的な first shot なのか

過去実験から次が分かっている。

1. `bit_synth_exact_trace_cot_v1` の pure synthetic 10,000 行は binary 内容自体には効いたが、全体スコアと boxing が不安定だった
2. `answer_only_keep` や `manual_audit_priority` は final-answer supervision には使えても、**full CoT teacher としては危ない**
3. 既存 v2 の強みは non-binary 側で非常に大きいので、binary だけを大きく増やし過ぎると逆噴射リスクがある

このため今回の `train_split_with_cot_v2.csv` は、次の制約で作る。

- **元の `train_split_with_cot.csv` はそのまま残す**
- 追加は **unused binary verified only**
- しかも最優先 bottleneck の **`bit_structured_byte_formula` だけ**
- synthetic teacher は **original prompt 上で作る**
- `generated_cot` は v2 notebook 互換で **no `<think>`, no final box, no answer leak**

要するに、**distribution shift を最小化しながら hardest verified structured pool だけを足す**のが今回の戦略。

## 4. `train_split_with_cot_v2.csv` の内容

### 4.1 ベースからの差分

`baseline/nemotron-sft-lora-with-cot-v2/artifacts/train_split_with_cot_v2.csv`

- base rows: `6558`
- added synthetic rows: `414`
- total rows: `6972`

### 4.2 type 別件数

| type | base | v2 |
| --- | ---: | ---: |
| `Bit Manipulation` | `607` | `1021` |
| `Equation Transformation` | `200` | `200` |
| `Gravitational Constant` | `1511` | `1511` |
| `Numeral Conversion` | `1491` | `1491` |
| `Text Encryption` | `1407` | `1407` |
| `Unit Conversion` | `1342` | `1342` |

### 4.3 追加した synthetic rows の内訳

すべて:

- `type = Bit Manipulation`
- `selection_tier = verified_trace_ready`
- `template_subtype = bit_structured_byte_formula`
- original train prompt をそのまま使用

solver family 内訳:

| teacher solver | rows |
| --- | ---: |
| `binary_structured_byte_formula` | `281` |
| `binary_structured_byte_formula_abstract` | `110` |
| `binary_structured_byte_not_formula` | `23` |

除外した候補:

- `2` rows
- 理由: `generated_cot` 内で plain-text answer leak を避けられなかった

## 5. synthetic teacher の作り方

各追加 row は、既存 analysis ledger の solver 情報から **row-local に deterministic な short trace** を作る。

形式:

1. `Check examples:`
2. 元 prompt 中の 2 例を用いた rule support
3. `So the verified rule is ...`
4. `Query x = ...`
5. `Apply ... and keep the exact 8-bit result with leading zeros for the final box.`
6. `Constraints: exact_8bit, leading_zeros, box_only_final.`

重要なのは次の 3 点:

- final answer を `generated_cot` に書かない
- `\boxed{}` を `generated_cot` に書かない
- plain-text で answer が漏れる row は除外する

この設計により、notebook 側が既存の正しい `\\boxed{answer}` 付与ロジックをそのまま使える。

## 6. 学習時の推奨

notebook `baseline/nemotron-sft-lora-with-cot-v2/nemotron-sft-lora-with-cot-v2.ipynb` は dataset path だけでなく、`TYPE_SAMPLES` の `Bit Manipulation` を見直す必要がある。

### 推奨 first shot

```python
TYPE_SAMPLES = {
    "Numeral Conversion": 300,
    "Gravitational Constant": 400,
    "Unit Conversion": 700,
    "Text Encryption": 700,
    "Bit Manipulation": 1021,         # all rows from train_split_with_cot_v2.csv
    "Equation Transformation": 200,
}
```

これで training sample 数は `3321` になり、元の `2907` からの増加分 `414` は **すべて verified structured binary** になる。

## 7. 今後の戦略

今回の v2 は **最も保守的な勝ち筋**だけを実装した first shot。  
今後は次の順で拡張する。

### Stage A: 今回

- unused `verified_trace_ready`
- `bit_structured_byte_formula` only
- short exact-trace synthetic

### Stage B: 次点候補

- unused `verified_trace_ready`
- `bit_other` / `bit_permutation_inversion`
- direct rule があるものだけ追加

### Stage C: boxed-only 補助

- unused `answer_only_keep`
- full CoT ではなく **boxed-only** か短 rationale
- 比率は verified synthetic より低くする

### Stage D: manual はまだ入れない

- `manual_audit_priority` は raw CoT 化しない
- 新しい solver evidence が増えてから再検討

## 8. この v2 で狙っていること

今回の `train_split_with_cot_v2.csv` は、**binary 全体を激しく作り替える**のではなく、

- existing v2 の broad strength を維持
- hardest structured binary にだけ verified synthetic を足す
- boxing を壊す要因を入れない

という 3 点に絞った。

期待している改善は、

1. `bit_structured_byte_formula` の content error 圧縮
2. binary 全体の near-miss 削減
3. non-binary score の維持

である。
