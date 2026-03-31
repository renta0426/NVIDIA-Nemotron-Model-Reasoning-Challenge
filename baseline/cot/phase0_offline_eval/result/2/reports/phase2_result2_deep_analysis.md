# Phase 2 Result 2 詳細分析

## 前提

- 対象は `baseline/cot/phase0_offline_eval/result/2` 配下の Phase 0 offline eval 結果。
- 評価基準は `README.md` の Accuracy / `\boxed{}` 優先抽出 / fallback 抽出 / numeric tolerance に合わせたもの。(`README.md:31-46`, `baseline/cot/phase0_offline_eval/result/2/reports/phase0_eval_manifest.md`)
- 今回は `result/2` 単体の要約に加え、既存の `result/0`・`result/1` と比較して「どこが伸びて、どこが崩れたか」を row-level / raw outputs まで掘っている。(`baseline/cot/phase0_offline_eval/result/0/reports/train_rule_based_cot_baseline_result0_deep_analysis.md`, `baseline/cot/phase0_offline_eval/result/1/reports/phase1_result1_deep_analysis.md`, `baseline/cot/phase0_offline_eval/result/2/artifacts/phase0_eval_row_level.csv`, `baseline/cot/phase0_offline_eval/result/2/artifacts/phase0_eval_raw_outputs.csv`)

## 結論

`result/2` の Phase 0 スコアは `227/320 = 0.7094` で、`result/1` の `225/320 = 0.7031` から **+2 correct / +0.0063**、`result/0` の `216/320 = 0.6750` からは **+11 correct / +0.0344** 改善した。(`baseline/cot/phase0_offline_eval/result/0/reports/phase0_eval_summary.md`, `baseline/cot/phase0_offline_eval/result/1/reports/phase0_eval_summary.md`, `baseline/cot/phase0_offline_eval/result/2/reports/phase0_eval_summary.md`)

ただし中身はかなり偏っている。

- `general_stable_set`: `0.9400 → 0.9500`
- `binary_hard_set`: `0.2000 → 0.2167`
- `symbol_watch_set`: `0.4167 → 0.4000`
- family では `gravity`, `roman`, `unit`, `binary` が改善
- 逆に `text`, `symbol` は悪化

つまり今回の +2 は「全面的な底上げ」ではなく、**general stable の回復と binary のわずかな前進で、text / symbol の退行をかろうじて相殺した** 形である。

さらに誤答の型も変わっている。

- `last_number`: `73 → 62`
- `boxed_non_empty`: `17 → 29`
- `boxed_empty`: `5 → 2`

これは、前回より boxed へ着地するケースは増えた一方、**boxed の中身そのものが wrong exact output になるケースが増えた** ことを意味する。とくに symbol がその典型で、unboxed 崩壊から「boxed はするが string exactness で負ける」失敗へ移っている。

## 1. 全体差分

### スコア比較

| metric | result/0 | result/1 | result/2 | delta vs result/1 |
| --- | ---: | ---: | ---: | ---: |
| overall | 0.6750 | 0.7031 | 0.7094 | +0.0063 |
| `general_stable_set` | 0.8950 | 0.9400 | 0.9500 | +0.0100 |
| `binary_hard_set` | 0.1833 | 0.2000 | 0.2167 | +0.0167 |
| `symbol_watch_set` | 0.4333 | 0.4167 | 0.4000 | -0.0167 |

(`baseline/cot/phase0_offline_eval/result/0/reports/general_stable_set_summary.md`, `baseline/cot/phase0_offline_eval/result/1/reports/general_stable_set_summary.md`, `baseline/cot/phase0_offline_eval/result/2/reports/general_stable_set_summary.md`, `baseline/cot/phase0_offline_eval/result/0/reports/binary_hard_set_summary.md`, `baseline/cot/phase0_offline_eval/result/1/reports/binary_hard_set_summary.md`, `baseline/cot/phase0_offline_eval/result/2/reports/binary_hard_set_summary.md`, `baseline/cot/phase0_offline_eval/result/0/reports/symbol_watch_set_summary.md`, `baseline/cot/phase0_offline_eval/result/1/reports/symbol_watch_set_summary.md`, `baseline/cot/phase0_offline_eval/result/2/reports/symbol_watch_set_summary.md`)

### family 別差分

| family | result/1 | result/2 | delta |
| --- | ---: | ---: | ---: |
| `gravity` | 0.9200 | 0.9400 | +0.0200 |
| `roman` | 0.9800 | 1.0000 | +0.0200 |
| `unit` | 0.9600 | 1.0000 | +0.0400 |
| `binary` | 0.2000 | 0.2167 | +0.0167 |
| `text` | 0.9000 | 0.8600 | -0.0400 |
| `symbol` | 0.4167 | 0.4000 | -0.0167 |

(`baseline/cot/phase0_offline_eval/result/1/reports/phase0_eval_summary.md`, `baseline/cot/phase0_offline_eval/result/2/reports/phase0_eval_summary.md`)

今回の改善は `gravity/unit/roman` の安定化が主で、hard exact-output 側では `binary` がわずかに伸びたものの、`text` と `symbol` がそのぶん落ちている。

## 2. 変わったのは「誤答数」より「誤答の型」

誤答数は `95 → 93` と 2 件しか減っていないが、fallback の内訳はかなり動いている。

| incorrect bucket | result/1 | result/2 | delta |
| --- | ---: | ---: | ---: |
| `last_number` | 73 | 62 | -11 |
| `boxed_non_empty` | 17 | 29 | +12 |
| `boxed_empty` | 5 | 2 | -3 |

(`baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_eval_row_level.csv`, `baseline/cot/phase0_offline_eval/result/2/artifacts/phase0_eval_row_level.csv`)

解釈としてはかなり明確で、

1. 前回より boxed へ持っていく力は上がった
2. その代わり、boxed した内容が exact にはズレるケースが増えた
3. したがって score 改善幅は小さい

という状態である。

これは「emission collapse の一部は直ったが、exact-answer discipline はまだ甘い」と読むのが自然である。

## 3. `result/1` から `result/2` で実際に何件ひっくり返ったか

row-level 比較では、correctness が反転した ID は 28 件だった。

- 改善: 15 件
- 退行: 13 件

family 別の内訳は次の通り。

- 改善: `binary +5`, `gravity +4`, `text +3`, `unit +2`, `roman +1`
- 退行: `text +5`, `binary +4`, `gravity +3`, `symbol +1`

(`baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_eval_row_level.csv`, `baseline/cot/phase0_offline_eval/result/2/artifacts/phase0_eval_row_level.csv`)

したがって今回の +2 は、

- `binary` と `gravity` の改善がプラス寄与
- `text` の 5 件退行がそれをかなり食う
- `symbol` は改善ゼロで 1 件退行

という構図でできている。

## 4. 本当に改善したところ

### 4.1 gravity は「box 内の余計な単位」を減らして改善

`gravity` は `46/50 → 47/50`。大きなブレではないが、改善例の質は分かりやすい。

- `2d4c4625`: `45.84\\text{ m}` で落としていたのが、`45.84` だけを box に入れる形へ寄り、正解化。raw length も `2641 → 2078` に短縮。(`baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_eval_row_level.csv`, `baseline/cot/phase0_offline_eval/result/2/artifacts/phase0_eval_row_level.csv`)
- `6f3ba33d`: `29.28\\text{ m}` → `29.28` へ整理されて正解。(`baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_eval_row_level.csv`, `baseline/cot/phase0_offline_eval/result/2/artifacts/phase0_eval_row_level.csv`)
- `e55f610f`: `55.08\\ \\text{m}` 系の box 汚染が消え、`55.09` へ修正。(`baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_eval_row_level.csv`, `baseline/cot/phase0_offline_eval/result/2/artifacts/phase0_eval_row_level.csv`)

一方で逆方向の退行もあり、

- `565bc498`: `94.71` 正解 → `94.71\\text{ m}` で誤答
- `d50a479c`: `22.72` 正解 → `22.72\\text{ m}` で誤答

という例もある。(`baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_eval_row_level.csv`, `baseline/cot/phase0_offline_eval/result/2/artifacts/phase0_eval_row_level.csv`)

要するに gravity では、「box 内は数値だけ」の discipline は前回より良くなったが、まだ完全には固定できていない。

### 4.2 roman と unit は回復して飽和域へ

`roman` は `49/50 → 50/50`、`unit` は `48/50 → 50/50` に回復した。(`baseline/cot/phase0_offline_eval/result/1/reports/phase0_eval_summary.md`, `baseline/cot/phase0_offline_eval/result/2/reports/phase0_eval_summary.md`)

代表例として `f0c8102d` は、

- result/1: 長文ループ後に `last_number=4`
- result/2: `XLIII` を boxed で返し、raw length も `10686 → 302`

となっている。(`baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_eval_row_level.csv`, `baseline/cot/phase0_offline_eval/result/2/artifacts/phase0_eval_row_level.csv`)

この recovery は small but real で、general stable families の最終回答 discipline は前回より改善している。

### 4.3 binary は「わずかに前進」だが、中心問題は残ったまま

`binary` は `12/60 → 13/60` と 1 問伸びた。(`baseline/cot/phase0_offline_eval/result/1/reports/binary_hard_set_summary.md`, `baseline/cot/phase0_offline_eval/result/2/reports/binary_hard_set_summary.md`)

ただし中身はまだかなり厳しい。

- `bit_structured_byte_formula`: `0/14` のまま
- `verified_trace_ready`: `8/20 → 7/20` にむしろ低下
- `answer_only_keep`: `3/20 → 2/20` に低下
- `manual_audit_priority`: `1/20 → 4/20` に改善

(`baseline/cot/phase0_offline_eval/result/1/reports/binary_hard_set_summary.md`, `baseline/cot/phase0_offline_eval/result/2/reports/binary_hard_set_summary.md`)

つまり今回の +1 は、**verified binary の本丸が伸びたというより、manual hard slice の一部が取れた** ことで生まれている。

失敗類型もまだ binary らしい。

- `correct`: 13
- `unboxed_binary_present`: 44
- `boxed_binary_wrong`: 3

(`baseline/cot/phase0_offline_eval/result/2/artifacts/phase0_eval_row_level.csv`, `baseline/cot/phase0_offline_eval/result/2/artifacts/phase0_eval_raw_outputs.csv`)

さらに binary 誤答 47 件に対して、

- gold が raw output のどこかに現れた: 17 件
- first 8-bit candidate が gold: 0 件
- last 8-bit candidate が gold: 3 件

だった。つまり前回同様、**extractor だけ直しても大半は救えない**。正しい 8-bit を安定して固め切れていない。

改善例はある。

- `bcdf9198`: result/1 では `last_number=3` だったが、result/2 では `\boxed{11111111}` に改善。raw length も `17894 → 2489` へ激減。(`baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_eval_row_level.csv`, `baseline/cot/phase0_offline_eval/result/2/artifacts/phase0_eval_row_level.csv`)

しかし退行も重い。

- `567e3da4`: `\boxed{10000100}` 正解 → 長文化して `last_number=3` に崩壊。raw length `3777 → 20691`。(`baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_eval_row_level.csv`, `baseline/cot/phase0_offline_eval/result/2/artifacts/phase0_eval_row_level.csv`)
- `52a9d5e4`: `bit_structured_byte_formula` で前回正解だったのに、今回は `010` の `last_number` 誤答。raw length `12302 → 18634`。(`baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_eval_row_level.csv`, `baseline/cot/phase0_offline_eval/result/2/artifacts/phase0_eval_row_level.csv`)
- `de11a23a`: boxed は維持したが `00000001` → `00000000` の content wrong。(`baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_eval_row_level.csv`, `baseline/cot/phase0_offline_eval/result/2/artifacts/phase0_eval_row_level.csv`)

要するに binary は、

- boxed collapse は少し減った
- しかし verified DSL 的な slice はまだ伸びていない
- structured byte formula は依然 0/14

であり、**Phase 2 で触りたい本質課題はまだ未解決** である。

## 5. 悪化したところ

### 5.1 text は前回の伸びを少し吐き戻した

`text` は `45/50 → 43/50` に低下した。(`baseline/cot/phase0_offline_eval/result/1/reports/phase0_eval_summary.md`, `baseline/cot/phase0_offline_eval/result/2/reports/phase0_eval_summary.md`)

改善例もあるが、退行の質が悪い。

- 改善例 `b9e045e8`: `cat drasw inside island` → `cat draws inside island` に修正。raw length `9249 → 4634`。(`baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_eval_row_level.csv`, `baseline/cot/phase0_offline_eval/result/2/artifacts/phase0_eval_row_level.csv`)
- 退行例 `a54f901d`: 正解 phrase から `last_number=1` へ崩壊、raw length `17809 → 22466`
- 退行例 `3daf5caa`: 正解 phrase から `last_number=3`、raw length `5150 → 25283`
- 退行例 `9443e78b`: 正解 phrase から `last_number=5`、raw length `7335 → 28222`

(`baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_eval_row_level.csv`, `baseline/cot/phase0_offline_eval/result/2/artifacts/phase0_eval_row_level.csv`)

つまり text の悪化は、単語 1 文字ズレだけでなく、**再び長文化して numeric fallback に崩れるケースが戻ってきた** ことが主因である。

### 5.2 symbol は「unboxed 崩壊」から「boxed wrong exactness」へ移ったが、点は増えていない

`symbol` は `25/60 → 24/60` に微減した。(`baseline/cot/phase0_offline_eval/result/1/reports/symbol_watch_set_summary.md`, `baseline/cot/phase0_offline_eval/result/2/reports/symbol_watch_set_summary.md`)

構造的にはほぼ同じで、

- `glyph_len5`: `0/20`
- `manual_audit_priority`: `0/30`
- `verified_trace_ready`: `15/15`
- `symbolic` answer type: `1/24`

のままである。(`baseline/cot/phase0_offline_eval/result/2/reports/symbol_watch_set_summary.md`)

ただし failure kind の見え方は変わった。

| symbol failure kind | result/1 | result/2 |
| --- | ---: | ---: |
| `numeric2x2_boxed_wrong` | 5 | 5 |
| `numeric2x2_unboxed_wrong` | 10 | 11 |
| `glyph_boxed_wrong` | 6 | 18 |
| `glyph_unboxed_wrong` | 14 | 2 |

(`baseline/cot/phase0_offline_eval/result/1/reports/phase1_result1_deep_analysis.md`, `baseline/cot/phase0_offline_eval/result/2/artifacts/phase0_eval_row_level.csv`)

つまり symbol は前回より「boxed はする」ようになったが、glyph exact string 自体は相変わらず外している。これは improvement ではなく、**failure mode の見た目が boxed 側へ移っただけ** と考えるべきである。

代表退行例:

- `9cb03277`: result/1 では `26` 正解だったが、result/2 では長文化して `last_number=9026`。raw length `5115 → 16728`。(`baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_eval_row_level.csv`, `baseline/cot/phase0_offline_eval/result/2/artifacts/phase0_eval_row_level.csv`)

## 6. 出力長から見えること

result/2 の correct / incorrect 平均出力長は次の通り。

| family | correct mean | incorrect mean |
| --- | ---: | ---: |
| `binary` | 8254 | 18007 |
| `gravity` | 1812 | 1496 |
| `roman` | 297 | - |
| `symbol` | 2145 | 19424 |
| `text` | 5690 | 21028 |
| `unit` | 1572 | - |

(`baseline/cot/phase0_offline_eval/result/2/artifacts/phase0_eval_raw_outputs.csv`, `baseline/cot/phase0_offline_eval/result/2/artifacts/phase0_eval_row_level.csv`)

特に重要なのは、

- `binary`: 49 件が 1 万文字超、9 件が 2 万文字超
- `symbol`: 32 件が 1 万文字超、18 件が 2 万文字超
- `text`: 9 件が 1 万文字超、6 件が 2 万文字超

で、前回より `binary` の 2 万文字超が `1 → 9` と悪化している点である。(`baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_eval_raw_outputs.csv`, `baseline/cot/phase0_offline_eval/result/2/artifacts/phase0_eval_raw_outputs.csv`)

今回の experiment は general families では出力を短くまとめられているが、hard exact families ではまだ「長く考え、最後に exact final answer を壊す」症状を抱えたままである。

## 7. binary holdout から見えること

`result/2` の binary holdout は、いくつかの fold で改善があるものの、依然として非常に不安定である。

- `gap_signature fold4`: `0.0 → 0.1`
- `prompt_signature fold1`: `0.1111 → 0.2222`
- `prompt_signature fold3`: `0.3333 → 0.5`
- `structured_family fold1`: `0.125 → 0.2`
- `solver_family fold1`: `0.1 → 0.15`

一方で、

- `structured_family fold0`: `0.5455 → 0.3636`
- `solver_family fold4`: `0.4 → 0.35`

は退行している。(`baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_binary_holdout_accuracy.csv`, `baseline/cot/phase0_offline_eval/result/2/artifacts/phase0_binary_holdout_accuracy.csv`)

しかも最大でも `0.5` で、その fold も 6 行しかない。行数が多い fold では依然 `0.15`〜`0.35` に留まるため、binary generalization が本質的に改善したとはまだ言いにくい。

## 8. まとめ

今回の `result/2` は、

- overall では前進している
- general stable families の回復は本物
- binary はわずかに伸びた
- ただし symbol と text を削って稼いだ部分がある
- binary structured byte formula と glyph exact string は依然壊滅

という結果だった。

一言で言えば、**Phase 1 の「general emission stabilizer」からは少し先へ進んだが、Phase 2 の本命である exact-output hard family の攻略にはまだ届いていない**。

次に重視すべきなのは、

1. binary verified / structured-byte-formula slice の直接改善
2. glyph exact string の boxed wrong 抑制
3. text で再発した長文化 `last_number` 崩壊の抑制

の 3 点である。
