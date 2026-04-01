# GPRO Step1 Notebook Run `result/2` 回帰分析レポート

## 対象

- 学習 Script: `baseline/GPRO/step1_binary_answer_only/train_gpro_step1_binary_answer_only.py`（修正後版）
- 評価結果: `baseline/GPRO/phase0_offline_eval/result/2/artifacts/*`
- 前回結果: `baseline/GPRO/phase0_offline_eval/result/1/artifacts/*`
- 比較基準: `baseline/cot/phase0_offline_eval/result/{0,1,2}`

## 先に結論

**`result/2` は `result/1` に対して明確な改善を示しており、Step1 の修正は有効でした。**

ただし結論は「Step1 の目的を完全に達成した」とまでは言えません。  
改善は実在するが、binary specialist の readiness としてはまだ partial success です。

主要な改善点:
1. overall accuracy `0.6125 → 0.7000` (+0.0875)
2. binary accuracy `0.1667 → 0.2333` (+0.0667, 10→14問)
3. gravity accuracy `0.7200 → 0.9800` (+0.2600) ← `\text{ m}` formatting 事故の大幅解消
4. text accuracy `0.7800 → 0.9000` (+0.1200)
5. unit accuracy `0.7600 → 0.8600` (+0.1000)
6. binary `boxed_extraction_success_rate` `0.1167 → 0.2333` (2倍)
7. binary boxed 出現数 `7/60 → 14/60` (2倍)

主要な残課題:
1. binary の `format_failure_rate` はまだ `0.7667`（46/60 がboxedなし）
2. `bit_structured_byte_formula` は依然 `0/14`
3. 一部 unit 問題で新たな repetition loop 崩壊が発生
4. symbol は `0.3833` で変化なし

## コード修正の要約

`result/1` → `result/2` 間で `train_gpro_step1_binary_answer_only.py` に加えられた主要修正は以下の通りです。

### 修正 1: tokenization における loss 境界の修正（核心的修正）

旧実装：
```python
# assistant_message の文字列開始位置から labels を張る
assistant_char_start = full_text.find(assistant_message)
```

新実装：
```python
# generation prompt の token prefix 境界から labels を切る
def shared_token_prefix_length(prefix_ids, full_ids):
    limit = min(len(prefix_ids), len(full_ids))
    index = 0
    while index < limit and prefix_ids[index] == full_ids[index]:
        index += 1
    return index

assistant_token_start = shared_token_prefix_length(prefix_ids, input_ids)
```

**影響**: boxed_only 行で chat template が `<think></think>\boxed{...}` を生成する一方、generation prompt は `<think>` で終わる。旧実装は `\boxed{...}` からしか loss を張れず、`</think>` の生成を学習できなかった。修正後は `</think>\boxed{...}` 全体が supervised span に入る。

### 修正 2: dataset CSV に `user_message` / `assistant_message` をプリコンピュート

- `enrich_output_row()` 追加により、build-dataset 時点で `user_message` と `assistant_message` を CSV に書き出す
- `render_training_pair()` がプリコンピュート値を優先参照
- notebook 側との一貫性を保証

### 修正 3: `load_dataset_rows()` のバリデーション強化

- `REQUIRED_DATASET_COLUMNS` と `OUTPUT_COLUMNS` を分離
- validate_output に `user_message` / `assistant_message` の整合性チェック追加

## Stage1 判定

**現時点の判定は conditional pass（条件付き合格）です。**

`result/1` の regression analysis で定義した暫定 success gate を再検証します。

### Success Gate チェック

| gate | 条件 | result/2 | 判定 |
| --- | --- | --- | --- |
| 1 | `Binary Hard Set` exact ≥ `12/60` (`COT/result/1`) | `14/60 = 0.2333` | **PASS** |
| 2 | binary `boxed_extraction_success_rate` > `0.2167` | `0.2333` | **PASS** |
| 3 | binary `last_number` fallback < `47/60` | `46/60` | **PASS**（ギリギリ） |
| 4 | binary 平均 output length < `result/1` の `17077` | `16166` | **PASS** |

4 つの暫定 gate をすべてクリアしています。

ただし gate 3 は `47→46` で margin が薄く、本質的な改善というより確率的な揺らぎの可能性があります。

## 比較サマリ

### Family accuracy 一覧

| run | overall | binary | gravity | symbol | text | unit | roman |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **GPRO/result/2** | **0.7000** | **0.2333** | **0.9800** | 0.3833 | **0.9000** | **0.8600** | **1.0000** |
| GPRO/result/1 | 0.6125 | 0.1667 | 0.7200 | 0.3833 | 0.7800 | 0.7600 | 1.0000 |
| COT/result/0 | 0.6750 | 0.1833 | 0.8600 | 0.4333 | 0.7400 | 0.9800 | 1.0000 |
| COT/result/1 | 0.7031 | 0.2000 | 0.9200 | 0.4167 | 0.9000 | 0.9600 | 0.9800 |
| COT/result/2 | 0.7094 | 0.2167 | 0.9400 | 0.4000 | 0.8600 | 1.0000 | 1.0000 |

### result/1 → result/2 差分

| family | result/1 | result/2 | delta |
| --- | ---: | ---: | ---: |
| overall | 0.6125 | 0.7000 | **+0.0875** |
| binary | 0.1667 | 0.2333 | **+0.0667** |
| gravity | 0.7200 | 0.9800 | **+0.2600** |
| symbol | 0.3833 | 0.3833 | +0.0000 |
| text | 0.7800 | 0.9000 | **+0.1200** |
| unit | 0.7600 | 0.8600 | **+0.1000** |
| roman | 1.0000 | 1.0000 | +0.0000 |

### COT Best (result/2) との差分

| family | COT/result/2 | GPRO/result/2 | delta |
| --- | ---: | ---: | ---: |
| overall | 0.7094 | 0.7000 | -0.0094 |
| binary | 0.2167 | 0.2333 | **+0.0167** |
| gravity | 0.9400 | 0.9800 | **+0.0400** |
| symbol | 0.4000 | 0.3833 | -0.0167 |
| text | 0.8600 | 0.9000 | **+0.0400** |
| unit | 1.0000 | 0.8600 | **-0.1400** |
| roman | 1.0000 | 1.0000 | +0.0000 |

**注目点**: GPRO/result/2 は COT ベストに対して overall で -0.0094 とほぼ同等。binary, gravity, text では上回っている。unit の -0.14 が唯一の明確な劣化で、これは repetition loop 崩壊（後述）に起因する。

## 主要所見

### 1. 核心修正（loss 境界）は有効だった

binary の boxed 出現が `7/60 → 14/60` と 2 倍になっています。

| metric | result/1 | result/2 | delta |
| --- | ---: | ---: | ---: |
| boxed_extraction_success_rate | 0.1167 | 0.2333 | **+0.1167** |
| regex_exact_rate | 0.1667 | 0.3500 | **+0.1833** |
| format_failure_rate | 0.8833 | 0.7667 | **-0.1167** |
| leading_zero_retention_rate | 0.2000 | 0.3000 | +0.1000 |
| 8-bit boxed 出現 | 7/60 | 14/60 | +7 |
| gold in raw_output | 22/60 | 27/60 | +5 |
| no-box 率 | 53/60 | 46/60 | -7 |

`</think>` を supervised span に含めた修正により、モデルが「thinking を閉じて boxed に入る」パターンを学習できるようになったことが、この改善の直接原因です。

### 2. gravity の大幅回復は formatting 事故の解消

result/1 では gravity が `36/50` に落ちており、その原因は `\boxed{94.72\text{ m}}` のような box 内単位混入でした。

result/2 では gravity が `49/50` に回復。唯一の失敗は `565bc498`（gold=94.71, pred=94.72\text{ m}）で、まだ `\text{ m}` が混入しています。

ただし result/2 でも gravity の多くの問題で最初の boxed に `\text{ m}` が入る傾向は残っており、最後の boxed で数値だけに修正する self-correction パターン（`\boxed{94.72\text{ m}}` → `\boxed{94.72}`）が頻繁に観察されます。`565bc498` だけこの self-correction が成功しなかったケースです。

### 3. text / unit の改善と残存問題

#### text (39/50 → 45/50, +6)

flip 分析:
- **gained 10問**: `last_number` fallback → 正しい boxed 回答（例: `dragon draws in valley`, `the dark knight sees`）
- **lost 4問**: 正しかった回答が `last_number` fallback や空 boxed に退行

net +6 は substantial な改善。completion termination の安定化が効いている。

ただし lost 4問のうち `c0e9cf43`, `a54f901d` は result/1 で正答できていた問題が崩れており、stochastic な揺らぎの範囲なのか、特定パターンでの退行なのか要注意。

#### unit (38/50 → 43/50, +5)

flip 分析:
- **gained 9問**: `last_number` fallback（多くは中間計算値）→ 正しい boxed 回答
- **lost 4問**: 新たな repetition loop 崩壊

**重要: unit で新たに発生した repetition loop 崩壊**

lost 4問のうち 3問（`2bd7896f`, `861dc9fe`, `b2e7ee08`）は同一パターンの repetition loop 崩壊:

```
maybe it's 1.279... = 1.279... maybe it's 1.279... = 1.279... maybe it's 1.279...
```

これは result/1 では見られなかった新しい failure pattern です。  
unit の一部問題で、換算係数を正しく推論できないとき、中間値を繰り返しループする崩壊を起こしています。

残り 1問（`eda92556`）は推論が途中で途切れるケースです。

### 4. symbol は変化なし (23/60 → 23/60)

gained 2、lost 2 でちょうど相殺。

- `glyph_len5` は依然 0/20（文字変換パターンの推論がまったくできていない）
- `numeric_2x2` は 23/40 で微動

symbol の `numeric_2x2` で符号反転バグ（gold=57 に対し pred=-57）が複数見られます。これは reasoning パターンの問題で、Step1 の binary-only 学習では改善されない範囲。

### 5. binary の tier 別成績

| tier | result/1 | result/2 | delta |
| --- | ---: | ---: | ---: |
| `verified_trace_ready` | 7/20 = 0.3500 | 10/20 = 0.5000 | **+0.1500** |
| `answer_only_keep` | 2/20 = 0.1000 | 1/20 = 0.0500 | -0.0500 |
| `manual_audit_priority` | 1/20 = 0.0500 | 3/20 = 0.1500 | +0.1000 |

`verified_trace_ready` が 7→10 と大きく伸び、`manual_audit_priority` も 1→3 に改善。
`answer_only_keep` の 2→1 は退行だが、1問差なので統計的揺らぎの範囲。

### 6. binary solver 別成績

| solver | result/1 | result/2 | delta |
| --- | ---: | ---: | ---: |
| `binary_affine_xor` | 7/20 | 10/20 = 0.5000 | **+3** |
| unknown (その他) | 3/40 | 4/40 = 0.1000 | +1 |

`binary_affine_xor` で 7→10 と +3 の改善。XOR 系のパターン認識が改善された証拠。

### 7. binary subtype 別成績

| subtype | result/1 | result/2 | delta |
| --- | ---: | ---: | ---: |
| `bit_other` | 10/46 | 14/46 = 0.3043 | **+4** |
| `bit_structured_byte_formula` | 0/14 | 0/14 = 0.0000 | +0 |

`bit_structured_byte_formula` は依然ゼロ。これは Step1 の SFT だけでは解けない問題群（構造化バイト公式の推論が必要）。

### 8. binary 正誤フリップの具体例

#### gained (wrong→correct): 7問

| id | gold | result/1 pred | result/2 pred | 変化 |
| --- | --- | --- | --- | --- |
| `0f7be6a8` | 01000000 | 0 (last_number) | 01000000 (boxed) | bit permutation を正しく推論し boxed |
| `08df5363` | 01011100 | 4 (last_number) | 01011100 (boxed) | bit permutation を正しく推論し boxed |
| `cb7c2230` | 10100000 | 1 (last_number) | 10100000 (boxed) | bit permutation を正しく推論し boxed |
| `71e6cae8` | 00000000 | 110 (last_number) | 00000000 (boxed) | ゼロパターンを正しく boxed |
| `ab064b6a` | 11111111 | 0 (last_number) | 11110110 (last_number) | tolerance 範囲内で近似正解 |
| `004ef7c7` | 11111111 | 1 (last_number) | 11010011 (last_number) | tolerance 範囲内で近似正解 |
| `c095f799` | 10011111 | 0 (last_number) | 10000101 (last_number) | tolerance 範囲内で近似正解 |

**注目**: gained 7問のうち 4問は exact boxed match（新 boxed 出力が正しい）。残り 3問は `last_number` fallback だが tolerance マッチで正解扱い。

つまり、**「boxed を出せるようになった」効果が gained の過半を占めている**。

#### lost (correct→wrong): 3問

| id | gold | result/1 pred | result/2 pred | 変化 |
| --- | --- | --- | --- | --- |
| `1bf84ce3` | 00000000 | 0 (last_number) | 1 (last_number) | last_number が 0→1 に変化 |
| `18564041` | 00000000 | 0 (last_number) | 5 (last_number) | last_number が 0→5 に変化 |
| `b80795b4` | 00010000 | 00010000 (boxed) | 10100011 (last_number) | boxed→last_number に退行 |

lost 3問のうち 2問は「gold=00000000 で、旧版では偶然 last_number=0 が gold と tolerance マッチしていた」もの。これは実質的な能力退行ではなく、偶然の loss。

`b80795b4` は genuine regression で、以前 boxed 出力できていた問題が boxed を出せなくなっている。

### 9. 出力長の比較

| family | result/1 avg_len | result/2 avg_len | delta |
| --- | ---: | ---: | ---: |
| binary | 17,077 | 16,166 | **-911** |
| gravity | 2,534 | 2,406 | -128 |
| roman | 399 | 386 | -13 |
| symbol | 18,572 | 16,270 | **-2,302** |
| text | 12,698 | 10,459 | **-2,239** |
| unit | 9,828 | 7,793 | **-2,035** |

全 family で出力長が短くなっています。特に symbol, text, unit で 2,000 字前後の短縮。

binary 内の正解/不正解別:

| | result/1 | result/2 |
| --- | ---: | ---: |
| correct avg_len | 不明 | 9,566 |
| wrong avg_len | 不明 | 18,174 |
| correct median | 不明 | 6,580 |
| wrong median | 不明 | 17,800 |

正解群は平均 9,566 字、不正解群は 18,174 字。正解時は短く閉じ、不正解時は long-output collapse するパターンが明確。

### 10. no-box 率の改善

| family | result/1 no-box rate | result/2 no-box rate | delta |
| --- | ---: | ---: | ---: |
| binary | 0.8833 | 0.7667 | **-0.1167** |
| gravity | 0.0000 | 0.0000 | +0.0000 |
| roman | 0.0000 | 0.0000 | +0.0000 |
| symbol | 0.3833 | 0.3500 | -0.0333 |
| text | 0.2200 | 0.0800 | **-0.1400** |
| unit | 0.2400 | 0.1600 | **-0.0800** |

binary, text, unit で no-box 率が改善。`</think>` → box 遷移の学習が全 family に波及している。

## 代表的な failure pattern

### binary: long-output collapse（最多パターン）

`3564baf1` (gold=10101101, pred=3, len=18920)
```
START: We need to infer the bit permutation or transformation from examples...
END: ...output0 gets input3, output1 gets input4, output2 gets input5, output3 gets input6,
     output4 gets input7, output5 gets input0, output6 gets input1. That's like
```

推論が max_tokens に到達して打ち切られ、boxed を閉じられない。gold `10101101` は raw_output 内にも現れない。

### binary: near-miss boxed

`567e3da4` (gold=10000100, pred=00000100, boxed)

8-bit を boxed 出力できているが、MSB が反転。rule inference の部分的失敗。

### unit: repetition loop（新規パターン）

`2bd7896f` (gold=52.00, pred=1.279, len=13306)
```
START: We need to infer the conversion rule from examples...
END: ...maybe it's 1.279... = 1.279... maybe it's 1.279... = 1.279... maybe it's 1.279...
```

換算係数の推論に失敗し、中間値を無限ループ的に繰り返す。7 問中 3 問がこのパターン。result/1 では見られなかった新しい崩壊モード。推論が行き詰まった時の self-correction が「繰り返し」に退化。

### symbol: glyph_len5 の完全失敗

`b13d511a` (gold=`\&[[`, pred=2, len=26387)

5文字の記号変換問題。文字ごとの置換規則を推論しようとするが、記号パターンの変換を long reasoning で追いきれず max_tokens に達する。glyph_len5 は 20/20 が失敗。

### symbol: 符号反転

`7c5c7b73` (gold=13, pred=-13), `b7b1d1a8` (gold=57, pred=-57)

numeric_2x2 の行列式計算で符号を反転させる系統的エラー。boxed は出せているが中身の符号が逆。

## plan-base.md 基準での Phase 1（Step1）判定

### plan-base.md の Step1 責務（原文要約）

> - binary specialist の default completion を短い exact boxed byte に寄せる
> - `last_number` fallback に落ちる bad completion を減らす
> - `\boxed{[01]{8}}` に近い action space を作る
> - collapse / leading-zero drop / extra digits を減らす
> - GRPO/ORPO 前の readiness を作る

### 評価

| 責務 | 判定 | 根拠 |
| --- | --- | --- |
| boxed byte に寄せる | **部分達成** | boxed 出現 7→14 (2倍)。ただし 46/60 はまだ no-box |
| last_number fallback を減らす | **微改善** | 53→46 に減少。ただしまだ 76.7% |
| action space を boxed 8-bit 近傍へ | **改善** | regex_exact_rate 0.35 (result/1: 0.17) |
| collapse/leading-zero 改善 | **改善** | leading_zero_retention 0.20→0.30 |
| GRPO/ORPO 前 readiness | **条件付き達成** | verified_trace_ready が 10/20=0.50 に到達 |

### 総合判定: **Conditional Pass — Step 2 (ORPO) への移行を推奨**

理由：

1. **4 つの暫定 success gate をすべてクリア**している
2. **COT ベスト（result/2, overall=0.7094）とほぼ同等の overall=0.7000** を、binary-only warm start adapter でありながら達成
3. binary `verified_trace_ready` が `0.50` に到達し、XOR 系 solver で `10/20` と実用水準
4. general family（gravity/text/unit/roman）が大幅に回復し、standalone でも使えるレベル

ただし「完全な success」ではない理由：

1. binary 46/60 が依然 no-box で、`last_number` fallback 依存が残る
2. `bit_structured_byte_formula` は 0/14 で、Step1 単体では解けない
3. general の unit で新たな repetition loop 崩壊が 3 問発生
4. binary 平均出力長 16,166 はまだ長い（正解時の中央値は 6,580 なので「解ける問題は短い」が「解けない問題は長文崩壊」）

### plan-base.md に照らした Phase 配置

plan-base.md の設計は：

> Step 1: binary answer-only SFT（boxed 寄せ）  
> Step 2: ORPO（collapse を叩く）  
> Step 3: GRPO（reasoning を押す）

result/2 の状態は：
- boxed 出現率が倍増し、format discipline が改善 → **Step 1 の役割は概ね果たした**
- collapse/last_number はまだ多い → **Step 2 (ORPO) で叩くべき対象が明確**
- structured-byte が 0/14 → **Step 3 (GRPO) の領域**

したがって、**Step 1 は conditional pass とし、Step 2 (ORPO) へ移行するのが plan-base.md の設計と整合的**です。

## Step 2 に向けた具体的な注意点

### ORPO chosen / rejected の候補

**chosen 候補**:
- result/2 で boxed 正解した 14 問の short completion（avg 9,566 chars）
- `<think></think>\boxed{01010101}` パターンの exact output

**rejected 候補**:
- result/2 の 46 wrong binary（特に last_number fallback 群）
- repetition loop に入った unit 群の completion
- 長文化した binary completion（18,000 chars 超）

### 即座に対処可能な改善

1. **unit の repetition loop 対策**: 生成時の repetition_penalty を上げる、または後処理で繰り返し検出して early stop する
2. **gravity の `\text{ m}` 残存**: `565bc498` 以外は self-correction で回復しているが、最初から数値のみを box に入れる傾向を ORPO で強化可能
3. **symbol の符号反転**: ORPO で `{-57}` (wrong) vs `{57}` (correct) のペアを rejected/chosen に入れる

## 次回 rerun の暫定 success gate（Step 2 用）

Step 2 (ORPO) の success gate：

1. binary exact ≥ `16/60`（today: 14/60）
2. binary `last_number` fallback ≤ `40/60`（today: 46/60）
3. general_stable_set accuracy ≥ `0.93`（today: 0.935）← 防衛
4. unit repetition loop の新規発生 ≤ 1 問
5. overall accuracy ≥ `0.72`
