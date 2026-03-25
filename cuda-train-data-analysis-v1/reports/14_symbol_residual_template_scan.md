# cuda-train-data-analysis-v1 symbol residual template scan

## 目的

`README.md` の accuracy 評価を前提に、`symbol_numeric_same_op` の残差から **gold と一致する exact rule だけ** を追加回収する。

## 今回の探索

### 1. arithmetic 候補の再照合

background agent が `x_plus_y`, `x_minus_y`, `x_mod_y`, `y_mod_x` などの候補を 18 行提案したが、`train_row_analysis_v1.csv` で再照合すると **全件 `auto_solver_match=False`** だった。

つまり examples だけを見ると説明できても、query の gold answer とは一致しない。  
この 18 行は **昇格しない**。

### 2. pure string template 全探索

`x1/x2/y1/y2/op` のみで構成される長さ 1〜5 の template を manual 残差へ総当たりした。

- gold と一致する行は `2` 行だけ
- ただし両方とも `same_operator_example_count=1`
- `9fb854c3` は `y1` で説明できるが、`(x-y)/10` 系でも見えてしまうため保留
- `db4383f3` は `x2y1y2` で一致するが、support が 1 例のみで再現パターンが弱いため保留

結論: **low-shot の pure string template は今回は昇格しない**。

### 3. digit-feature template 全探索

次の token を使う exact template を `same_operator_example_count>=2` に限定して探索した。

- `x1`, `x2`, `y1`, `y2`, `op`
- `diff_t`, `diff_o` (`abs(x-y)` の 2 桁表現)

ここで安全に拾えたのは次の `2` 行。

| id | new_tier | rule | 根拠 |
| --- | --- | --- | --- |
| `824d4bcb` | `verified_trace_ready` | `abs_diff_2d_op_suffix` | `11:92 = 81:`, `68:06 = 62:` から `24:88 -> 64:` が exact |
| `9cb03277` | `answer_only_keep` | `abs_diff_2d` | `57!58 = 01` から `52!78 -> 26` が exact だが same-op は 1 例なので answer-only |

### 4. suspect 化した行

`4c6cf9d9` は `29*65` に対して gold `63` だが、same-op examples

- `58*34 = 24`
- `29*25 = 04`

は明確に `abs(x-y)` の zero-padded 2 桁へ一致し、query でも `36` が出る。  
このため **`exclude_suspect` に降格**した。

## 結果

今回の residual scan による net 変化は次のとおり。

- `verified_trace_ready`: `+1`
- `answer_only_keep`: `+1`
- `manual_audit_priority`: `-3`
- `exclude_suspect`: `+1`

pass1 queue は

- `symbol_numeric_same_op`: `376 -> 373`
- `binary_low_gap`: `150`
- `symbol_glyph_multiset`: `46`

まで圧縮された。

## 判断メモ

- exact match でも、**low-shot で別解が強く見える template は上げない**
- `README.md` の accuracy を守るため、gold mismatch が出た rule は即座に suspect 側へ寄せる
- 今回の残差では、「昇格できる行を無理に増やす」よりも「危険行を manual / exclude に残す」方が安全
