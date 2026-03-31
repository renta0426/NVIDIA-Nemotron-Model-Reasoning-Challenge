# Phase 2 Hybrid Result 2-1 詳細分析

## 前提

- 対象は `baseline/cot/phase0_offline_eval/result/2-1` 配下の Phase 0 offline eval 結果。
- 評価基準は `README.md` の Accuracy / `\boxed{}` 優先抽出 / fallback 抽出 / numeric relative tolerance `0.01` に合わせる。(`README.md:31-46`, `baseline/cot/phase0_offline_eval/result/2-1/reports/phase0_eval_manifest.md`)
- 今回の学習データは `baseline/cot/phase2_binary_dsl/build_phase2_binary_dsl_dataset.py` が出力する **hybrid narrative** 版で、manifest は `baseline/cot/phase2_binary_dsl/artifacts/phase2_binary_hybrid_manifest.json`。binary の verified rows は `hybrid_narrative`、answer-only binary rows は boxed-only のまま、`<think>` 内で最終 8-bit 答えを再掲しない。(`baseline/cot/phase2_binary_dsl/build_phase2_binary_dsl_dataset.py:670-685,706-721,777-821`, `baseline/cot/phase2_binary_dsl/artifacts/phase2_binary_hybrid_manifest.json`)
- 実験の比較対象は前回の DSL scratchpad 版 `result/2` と、その前の `result/0`, `result/1`。(`baseline/cot/phase0_offline_eval/result/0/reports/phase0_eval_summary.md`, `baseline/cot/phase0_offline_eval/result/1/reports/phase0_eval_summary.md`, `baseline/cot/phase0_offline_eval/result/2/reports/phase2_result2_deep_analysis.md`, `baseline/cot/phase0_offline_eval/result/2-1/reports/phase0_eval_summary.md`)

## 実験内容の事実整理

今回の hybrid 実験は、Phase 1 / Phase 2 で固定している 900-row mixture 自体は変えていない。

- 総行数: `900`
- family counts: `bit=280`, `gravity=120`, `roman=120`, `symbol=140`, `text=120`, `unit=120`
- `assistant_style`: `trace_boxed=680`, `boxed_only=220`
- binary design: `verified_binary_trace_rows=160`, `answer_only_binary_boxed_rows=120`
- binary trace categories: `hybrid_exact_formula=133`, `hybrid_byte_transform=14`, `generic_solver_family=13`

(`baseline/cot/phase2_binary_dsl/artifacts/phase2_binary_hybrid_manifest.json`)

さらに、前回の DSL 版 `phase2_binary_dsl_training_data.csv` と今回の `phase2_binary_hybrid_training_data.csv` を row-by-row で比較すると、**900 行の ID 集合は完全一致**し、変わっているのは **160 行の `binary + trace_boxed` row の `generated_cot` だけ**だった。非 binary row と binary boxed-only row は同一である。

実際、binary trace の平均 `generated_cot` 長は

- DSL: `180.6 chars`
- Hybrid: `363.8 chars`

まで伸びており、hybrid は「DSL を自然言語で言い換えた短い説明」ではなく、**binary trace の文体と長さをかなり変える介入**になっている。

## 結論

この実験は失敗だった。

`result/2-1` の Phase 0 スコアは `216/320 = 0.6750` で、前回の DSL 版 `result/2` の `227/320 = 0.7094` から **-11 correct / -0.0344**。しかも overall は `result/0` と同点まで後退した。(`baseline/cot/phase0_offline_eval/result/0/reports/phase0_eval_summary.md`, `baseline/cot/phase0_offline_eval/result/2/reports/phase2_result2_deep_analysis.md`, `baseline/cot/phase0_offline_eval/result/2-1/reports/phase0_eval_summary.md`)

ベンチマーク別でも全面的に悪い。

| metric | result/0 | result/1 | result/2 | result/2-1 |
| --- | ---: | ---: | ---: | ---: |
| overall | 0.6750 | 0.7031 | 0.7094 | 0.6750 |
| `general_stable_set` | 0.8950 | 0.9400 | 0.9500 | 0.9200 |
| `binary_hard_set` | 0.1833 | 0.2000 | 0.2167 | 0.1333 |
| `symbol_watch_set` | 0.4333 | 0.4167 | 0.4000 | 0.4000 |

つまり hybrid は、

- general stable を `190/200 → 184/200` に落とし
- binary hard を `13/60 → 8/60` に落とし
- symbol watch は `24/60` のまま据え置き

で、**意図した binary 改善に失敗しただけでなく、周辺 family まで巻き添えで崩した**。

## 1. `result/2` から何が落ちたか

family 別に見ると、`result/2 → result/2-1` の変化はこうなった。

| family | result/2 | result/2-1 | delta |
| --- | ---: | ---: | ---: |
| `binary` | 0.2167 | 0.1333 | -0.0834 |
| `gravity` | 0.9400 | 0.9800 | +0.0400 |
| `roman` | 1.0000 | 0.9800 | -0.0200 |
| `symbol` | 0.4000 | 0.4000 | 0.0000 |
| `text` | 0.8600 | 0.7200 | -0.1400 |
| `unit` | 1.0000 | 1.0000 | 0.0000 |

row-level の反転件数は 27 件で、

- 改善: `8`
- 退行: `19`

だった。

内訳は次の通り。

- 改善: `gravity +3`, `text +4`, `symbol +1`
- 退行: `text +11`, `binary +5`, `gravity +1`, `roman +1`, `symbol +1`

要するに、gravity の「unit を box に入れない」改善が少しあった一方で、**text が大きく崩れ、binary がさらに落ちた**ことで全体が沈んでいる。

## 2. 誤答の型は `result/0` に近いところまで戻った

incorrect fallback bucket はこう変化した。

| incorrect bucket | result/0 | result/1 | result/2 | result/2-1 |
| --- | ---: | ---: | ---: | ---: |
| `last_number` | 85 | 73 | 62 | 85 |
| `boxed_non_empty` | 15 | 17 | 29 | 17 |
| `boxed_empty` | 4 | 5 | 2 | 2 |

`result/2` では「boxed までは行くが中身が wrong」に寄っていたのに対し、`result/2-1` では `last_number` が **62 → 85** へ再悪化し、完全に `result/0` 水準へ戻っている。

これは、hybrid trace が model の最終回答 discipline を強めるどころか、**長い自然言語推論を誘発し、最後の boxed 出力を崩した**と読むのが自然である。

## 3. Binary は明確に悪化した

### 3.1 README 互換スコアでも悪化

`binary_hard_set` は

- `result/0`: `11/60 = 0.1833`
- `result/1`: `12/60 = 0.2000`
- `result/2`: `13/60 = 0.2167`
- `result/2-1`: `8/60 = 0.1333`

で、hybrid は前回 DSL より **-5 問**、baseline よりも **-3 問** 悪い。(`baseline/cot/phase0_offline_eval/result/0/reports/binary_hard_set_summary.md`, `baseline/cot/phase0_offline_eval/result/1/reports/binary_hard_set_summary.md`, `baseline/cot/phase0_offline_eval/result/2/reports/phase2_result2_deep_analysis.md`, `baseline/cot/phase0_offline_eval/result/2-1/reports/binary_hard_set_summary.md`)

### 3.2 exact 8-bit で見ると、hybrid はさらに弱い

README metric は numeric tolerance を持つため、unboxed の `01101000` と `01111111` のような **digit-only binary string** でも、「数値として近い」だけで正解扱いされることがある。そこで binary だけは、official-like score と別に **exact 8-bit string 一致**も切り分けて見た。

| result | official-like binary correct | exact 8-bit correct | tolerance-only correct |
| --- | ---: | ---: | ---: |
| `result/0` | 11 | 11 | 0 |
| `result/1` | 12 | 10 | 2 |
| `result/2` | 13 | 9 | 4 |
| `result/2-1` | 8 | 8 | 0 |

重要なのは次の 2 点である。

1. 前回 DSL の `13/60` は、実質的には **exact 9/60 + tolerance-only 4/60** だった  
2. 今回 hybrid は **official-like でも exact でも悪い**

つまり hybrid は「metric の見かけ上の binary gain」すら失い、**本当に bit exactness を改善できていない**。

### 3.3 落ちたのは intended slice 以外だけではない

selection tier ごとの binary 成績は次の通り。

| selection_tier | result/2 official | result/2 exact | result/2-1 official | result/2-1 exact |
| --- | ---: | ---: | ---: | ---: |
| `verified_trace_ready` | 7/20 | 7/20 | 7/20 | 7/20 |
| `answer_only_keep` | 2/20 | 1/20 | 1/20 | 1/20 |
| `manual_audit_priority` | 4/20 | 1/20 | 0/20 | 0/20 |

hybrid が本来改善したかった `verified_trace_ready` は **7/20 のまま据え置き**で、落ちたのは主に

- `answer_only_keep`: `2 → 1`
- `manual_audit_priority`: `4 → 0`

だった。

つまり今回の変更は、「verified binary trace を強くする」効果すら見せず、むしろ周辺 slice の generation を悪化させている。

### 3.4 `bit_structured_byte_formula` は依然 `0/14`

前回 DSL でも未解決だった `bit_structured_byte_formula` は、今回も **`0/14`** のままだった。(`baseline/cot/phase0_offline_eval/result/2-1/reports/binary_hard_set_summary.md`)

この点はかなり重要で、hybrid 化は **Phase 2 が本当に触りたい structured binary 本丸を 1 問も押し上げていない**。

### 3.5 binary failure shape

`result/2-1` の binary 失敗 52 件を形で分けると、

- `binary_absent`: `31`
- `unboxed_binary_present`: `19`
- `boxed_binary_wrong`: `2`

だった。

また wrong binary だけを見ると、

- gold が raw output のどこかに現れた: `19`
- first 8-bit candidate が gold: `0`
- last 8-bit candidate が gold: `2`

で、前回同様 **extractor をいじっても大半は救えない**。そもそも正しい 8-bit を安定して固め切れていない。

### 3.6 binary の代表的な退行

`result/2 → result/2-1` で binary の改善 ID は 0 件、退行 ID は 5 件だった。

- `5356c59d` (`answer_only_keep`)
- `004ef7c7` (`manual_audit_priority`)
- `0290f51a` (`manual_audit_priority`)
- `0df8306a` (`manual_audit_priority`)
- `101410e4` (`manual_audit_priority`)

特に `0df8306a` は、DSL 版では boxed 8-bit まで到達していたのに、hybrid 版では長文化して `last_number` へ崩れた。manual slice の 4/20 → 0/20 崩壊は、こうした「最後まで boxed exact byte を固定できない」退行の集積と見てよい。

## 4. Text が大きく巻き添え退行した

text は `43/50 → 36/50` と **-7 問**。ここが overall を大きく押し下げた主因のひとつだった。

failure profile は次の通り。

| text metric | result/2 | result/2-1 |
| --- | ---: | ---: |
| correct | 43/50 | 36/50 |
| `last_number` wrong | 5 | 10 |
| `boxed_non_empty` wrong | 2 | 4 |
| mean raw length | 7837 | 10109 |
| wrong-only mean raw length | 21028 | 20663 |
| rows `>10000 chars` | 9 | 16 |
| rows `>20000 chars` | 6 | 11 |

代表例:

- 改善: `a54f901d`, `3daf5caa`, `9443e78b`, `557f9a4a`
- 退行: `5923f138`, `fbd58e38`, `a3efb940`, `d300a576`, `dc10ca9b`, `e05908dd`, `ed5a4c11`, `ccd5baec`, `f7ab60d6`, `03e2bedc`, `74da6cbe`

改善も少しあるが、数では完全に負けている。しかも悪化の質は、

- phrase 1 文字ズレ
- boxed しているが単語が壊れる
- 長文化して `last_number` に落ちる

の混合で、**自然言語 hybrid が binary 以外にも「冗長に考えて最後を壊す」癖を広げた**ように見える。

## 5. Symbol は点数横ばいだが、failure mode は悪化寄り

symbol は `24/60` のまま据え置きで、点数だけ見ると横ばいである。

しかし中身は良くない。

| symbol failure kind | result/2 | result/2-1 |
| --- | ---: | ---: |
| `glyph_len5_boxed_wrong` | 18 | 7 |
| `glyph_len5_unboxed_wrong` | 2 | 13 |
| `numeric_2x2_boxed_wrong` | 5 | 5 |
| `numeric_2x2_unboxed_wrong` | 11 | 11 |

つまり `result/2` で見えていた「boxed まではするが glyph exactness が壊れる」失敗が、hybrid では再び **unboxed 崩壊寄り**へ戻っている。

出力長も悪化しており、

- symbol mean raw length: `12513 → 14059`
- symbol wrong-only mean raw length: `19424 → 21836`
- `>20000 chars`: `18 → 21`

となった。

symbol は 1 件だけ改善 (`9cb03277`) したが、1 件退行 (`52c62a3e`) しており、family としての前進は無い。

## 6. General families では gravity だけが素直に良くなった

hybrid で明確に良くなった family は gravity だった。

| family | result/2 | result/2-1 |
| --- | ---: | ---: |
| `gravity` | 47/50 | 49/50 |
| `roman` | 50/50 | 49/50 |
| `unit` | 50/50 | 50/50 |

gravity の改善は主に「box 内に `\\text{ m}` を入れない」方向の整理で、

- `565bc498`
- `5e6ee1d9`
- `d50a479c`

などが正解化した。

ただし、その代わり roman では `f0c8102d` が `XLIII` から長いループ出力へ崩れて `last_number=4` になっており、**general stable 全体では `190/200 → 184/200` とちゃんと悪化している**。

## 7. Binary holdout でもほぼ全面悪化

`phase0_binary_holdout_accuracy.csv` の `result/2 → result/2-1` 比較では、改善した fold は 0、同点 5、悪化 11 だった。

特に悪いのは次のあたり。

- `gap_signature fold0`: `0.25 → 0.125`
- `prompt_signature fold0`: `0.1875 → 0.0625`
- `solver_family fold1`: `0.15 → 0.025`
- `structured_family fold1`: `0.2 → 0.1`

つまり hybrid は、hard benchmark 60 行だけでなく、**binary generalization の見え方でも前回 DSL より悪い**。

## 8. どう解釈すべきか

今回の結果から言えることはかなり明確である。

1. **変更点は実質的に binary trace の文体だけだった**  
   900 行の ID 集合は前回 DSL と同一で、変わったのは 160 行の binary trace `generated_cot` だけだった。

2. **その変更は短い DSL を「少し自然化」した程度ではなく、binary teacher を長文化する介入だった**  
   平均 trace 長が `180.6 → 363.8` に倍増している。

3. **意図した verified binary slice は全く改善しなかった**  
   `verified_trace_ready` は `7/20` で不変、`bit_structured_byte_formula` は `0/14` のまま。

4. **その一方で text / roman / symbol の boxed discipline まで悪化させた**  
   `last_number` が `62 → 85` へ再上昇し、text の長文化も再発している。

要するに hybrid narrative は、このモデルに対しては

- binary の exact byte reasoning を強くする

よりも、

- 「自然言語で長く説明する」モードを強める
- 最後の boxed exact answer を崩しやすくする

方向に働いたと見るのが妥当である。

## 9. 実務上の含意

この experiment から得るべき実務的な結論は次の通り。

- **Phase 2 の binary teacher は、少なくとも今回の hybrid narrative 方向では戻すべきではない**
- verified binary の improvement が無い以上、自然言語 hybrid を次の本線にする根拠は弱い
- 今後の binary teacher 改善は、`structured byte formula` と `verified_trace_ready` に対する exactness 改善へ直接効くものに限定すべき
- また、README metric の tolerance により binary digits-only answer が数値近似で通るケースがあるため、binary は **official-like score と exact 8-bit score の両方**で追う必要がある

今回の `result/2-1` は、**「hybrid にしたら reasoning が豊かになって binary が伸びる」仮説を否定した失敗実験**として価値がある。少なくともこのモデルでは、Phase 2 binary teacher に必要なのは自然言語化ではなく、**短く、構造的で、box discipline を壊しにくい supervision** だと読める。
