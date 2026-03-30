# Phase 1 Result 1 詳細分析

## 前提

- 対象は `baseline/cot/phase0_offline_eval/result/1` 配下の Phase 0 offline eval 結果。
- 評価基準は `README.md` の Accuracy / `\boxed{}` 優先抽出 / fallback 抽出 / numeric tolerance `1e-2` に合わせたもの。(`README.md:31-46`, `baseline/cot/phase0_offline_eval/result/1/reports/phase0_eval_manifest.md:1-30`)
- 今回は `result/1` 単体の分析に加え、直前の `result/0` と比較して「何が改善し、何が未改善か」も見た。(`baseline/cot/phase0_offline_eval/result/0/reports/phase0_eval_summary.md:3-86`, `baseline/cot/phase0_offline_eval/result/1/reports/phase0_eval_summary.md:3-86`)

## 結論

`result/1` の Phase 0 スコアは `225/320 = 0.7031` で、`result/0` の `216/320 = 0.6750` から **+9 correct / +0.0281** 改善した。(`baseline/cot/phase0_offline_eval/result/0/reports/phase0_eval_summary.md:3-86`, `baseline/cot/phase0_offline_eval/result/1/reports/phase0_eval_summary.md:3-86`)

ただし改善の中身は偏っている。

- `general_stable_set`: `0.8950 → 0.9400`
- `text`: `0.7400 → 0.9000`
- `gravity`: `0.8600 → 0.9200`
- `binary`: `0.1833 → 0.2000` の微増
- `symbol`: `0.4333 → 0.4167` の微減

(`baseline/cot/phase0_offline_eval/result/0/reports/general_stable_set_summary.md:3-68`, `baseline/cot/phase0_offline_eval/result/1/reports/general_stable_set_summary.md:3-68`, `baseline/cot/phase0_offline_eval/result/0/reports/phase0_eval_summary.md:9-18`, `baseline/cot/phase0_offline_eval/result/1/reports/phase0_eval_summary.md:9-18`)

要するに、Phase 1 で効いたのは **general stable families の answer emission 安定化** であり、`binary` / `glyph_len5` のような exact-output hard family はほぼ未解決のままである。

## 1. まず全体差分

### スコア比較

| metric | result/0 | result/1 | delta |
| --- | ---: | ---: | ---: |
| overall | 0.6750 | 0.7031 | +0.0281 |
| general_stable_set | 0.8950 | 0.9400 | +0.0450 |
| binary_hard_set | 0.1833 | 0.2000 | +0.0167 |
| symbol_watch_set | 0.4333 | 0.4167 | -0.0166 |

(`baseline/cot/phase0_offline_eval/result/0/reports/phase0_eval_summary.md:3-86`, `baseline/cot/phase0_offline_eval/result/1/reports/phase0_eval_summary.md:3-86`, `baseline/cot/phase0_offline_eval/result/0/reports/general_stable_set_summary.md:3-68`, `baseline/cot/phase0_offline_eval/result/1/reports/general_stable_set_summary.md:3-68`, `baseline/cot/phase0_offline_eval/result/0/reports/binary_hard_set_summary.md:3-66`, `baseline/cot/phase0_offline_eval/result/1/reports/binary_hard_set_summary.md:3-66`, `baseline/cot/phase0_offline_eval/result/0/reports/symbol_watch_set_summary.md:3-64`, `baseline/cot/phase0_offline_eval/result/1/reports/symbol_watch_set_summary.md:3-64`)

### family 別差分

| family | result/0 | result/1 | delta |
| --- | ---: | ---: | ---: |
| `gravity` | 0.8600 | 0.9200 | +0.0600 |
| `text` | 0.7400 | 0.9000 | +0.1600 |
| `binary` | 0.1833 | 0.2000 | +0.0167 |
| `symbol` | 0.4333 | 0.4167 | -0.0166 |
| `roman` | 1.0000 | 0.9800 | -0.0200 |
| `unit` | 0.9800 | 0.9600 | -0.0200 |

(`baseline/cot/phase0_offline_eval/result/0/reports/phase0_eval_summary.md:9-18`, `baseline/cot/phase0_offline_eval/result/1/reports/phase0_eval_summary.md:9-18`)

この表だけでも、今回の伸びは `text` と `gravity` が主で、hard exact families の改善ではないことが分かる。

## 2. 変わったのは「誤答数」より「誤答の型」

誤答数は `104 → 95` に減った。内訳を再集計すると以下。

| incorrect bucket | result/0 | result/1 | delta |
| --- | ---: | ---: | ---: |
| `last_number` | 85 | 73 | -12 |
| `boxed_non_empty` | 15 | 17 | +2 |
| `boxed_empty` | 4 | 5 | +1 |

(`baseline/cot/phase0_offline_eval/result/0/artifacts/phase0_eval_row_level.csv`, `baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_eval_row_level.csv`)

つまり、Phase 1 の改善は主に **`last_number` fallback 崩壊を減らした** ことで説明できる。一方で、

- boxed はより多く出るようになった
- しかし boxed した中身がずれる／空になる退行も少数残る

という状態になっている。

これは「最終解答を出す意思」は強くなったが、「exact に正しい boxed answer を閉じる」まではまだ不十分、という解釈が最もしっくりくる。

## 3. `result/0` から `result/1` で実際に何件ひっくり返ったか

row-level を比較すると、correctness が反転した ID は 39 件あった。

- 改善: 24 件
- 退行: 15 件

family 別の内訳は

- 改善: `text +10`, `gravity +7`, `binary +4`, `symbol +2`, `unit +1`
- 退行: `gravity +4`, `binary +3`, `symbol +3`, `text +2`, `unit +2`, `roman +1`

だった。(`baseline/cot/phase0_offline_eval/result/0/artifacts/phase0_eval_row_level.csv`, `baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_eval_row_level.csv`)

つまり今回は「全面的に安定化した」というより、**改善も退行もあるが、text / gravity の改善が上回ってトータルプラス** になった、という結果である。

## 4. 何が本当に改善したか

## 4.1 gravity は大きく改善

`gravity` は `0.8600 → 0.9200` に上がった。しかも平均出力長が

- result/0: `10432`
- result/1: `2035`

まで大きく短縮されている。(`baseline/cot/phase0_offline_eval/result/0/artifacts/phase0_eval_raw_outputs.csv`, `baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_eval_raw_outputs.csv`)

これはかなり重要で、Phase 1 によって gravity では「長考して最後に変な数字を残す」挙動がだいぶ減ったと見てよい。

代表例:

- `1bde7dfb`: `result/0` では prediction `3.3` で `last_number` 誤答だったが、`result/1` では `38.9` を boxed で返して正解。(`baseline/cot/phase0_offline_eval/result/0/artifacts/phase0_eval_row_level.csv:2`, `baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_eval_row_level.csv:2`)
- `76a0c79a`: `result/0` では `boxed_empty`、`result/1` では `11.15` で正解。(`baseline/cot/phase0_offline_eval/result/0/artifacts/phase0_eval_row_level.csv:11`, `baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_eval_row_level.csv:11`)

ただし完全ではない。`2d4c4625`, `6f3ba33d`, `e55f610f` などでは `45.84\\text{ m}` や `55.08\\ \\text{m}` のように **単位文字列を box 内に混ぜて string mismatch** を起こしている。(`baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_eval_row_level.csv:25`, `baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_eval_raw_outputs.csv`)

よって gravity は「ほぼ解ける」が、「box 内には数値だけ」という discipline はまだ要る。

## 4.2 text は最も良く伸びた

`text` は `0.7400 → 0.9000`。これは今回最大の改善である。(`baseline/cot/phase0_offline_eval/result/0/reports/phase0_eval_summary.md:9-18`, `baseline/cot/phase0_offline_eval/result/1/reports/phase0_eval_summary.md:9-18`)

また boxed rate も

- result/0: `0.86`
- result/1: `0.98`

へ上がっている。(`baseline/cot/phase0_offline_eval/result/0/artifacts/phase0_eval_row_level.csv`, `baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_eval_row_level.csv`)

代表改善例:

- `6de757af`: `result/0` では `boxed_empty`、`result/1` では gold そのものを boxed で返して正解。(`baseline/cot/phase0_offline_eval/result/0/artifacts/phase0_eval_row_level.csv:169`, `baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_eval_row_level.csv:169`)
- `94643472`: `result/0` では prediction `6` の `last_number` 誤答、`result/1` では `knight chases message` を正しく返した。(`baseline/cot/phase0_offline_eval/result/0/artifacts/phase0_eval_row_level.csv:198`, `baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_eval_row_level.csv:198`)

一方で退行もあり、

- `557f9a4a`: `teacher writes mirror` → `teacher writings mirror`

のように、**意味は近いが phrase exactness で落ちる** ケースは残っている。(`baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_eval_raw_outputs.csv`)

## 4.3 binary は「少し良くなった」ではなく「まだ全然足りない」

`binary` は `11/60 → 12/60` と 1 問増えただけで、本質的にはまだ弱い。(`baseline/cot/phase0_offline_eval/result/0/reports/binary_hard_set_summary.md:3-66`, `baseline/cot/phase0_offline_eval/result/1/reports/binary_hard_set_summary.md:3-66`)

さらに見ると、

- boxed rate: `0.2167 → 0.2167` で不変
- `verified_trace_ready`: `0.35 → 0.40`
- `manual_audit_priority`: `0.05 → 0.05`
- `answer_only_keep`: `0.15 → 0.15`

で、改善は極めて限定的。(`baseline/cot/phase0_offline_eval/result/0/reports/binary_hard_set_summary.md:44-66`, `baseline/cot/phase0_offline_eval/result/1/reports/binary_hard_set_summary.md:44-66`)

再集計した failure kind でも

- `correct`: 12
- `unboxed_binary_present`: 46
- `boxed_binary_wrong`: 2

で、主 failure は前回とほぼ同じだった。(`baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_eval_row_level.csv`)

しかも binary 誤答 48 件に対し、gold が raw output のどこかに現れていたのは 15 件しかない。8-bit candidate の

- first candidate gold: 1
- last candidate gold: 1

しかなく、**extractor を変えるだけでは救えない**。(`baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_eval_raw_outputs.csv`)

改善例はある。

- `de11a23a`: `00000000 → 00000001` へ修正されて正解。(`baseline/cot/phase0_offline_eval/result/0/artifacts/phase0_eval_row_level.csv:220`, `baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_eval_row_level.csv:220`)
- `52a9d5e4`: `0` の `last_number` 誤答から `11011111` の正解へ改善。(`baseline/cot/phase0_offline_eval/result/0/artifacts/phase0_eval_row_level.csv:228`, `baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_eval_row_level.csv:228`)

ただし退行もある。

- `55f5e590`, `846176af`, `bcdf9198` は以前 boxed で取れていたのに、`result/1` では `last_number` に崩れている。(`baseline/cot/phase0_offline_eval/result/0/artifacts/phase0_eval_row_level.csv`, `baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_eval_row_level.csv`)

結論として、Phase 1 は binary の本質問題をまだ解いていない。

## 4.4 symbol はむしろ少し悪化

`symbol` は `0.4333 → 0.4167` に微減した。(`baseline/cot/phase0_offline_eval/result/0/reports/symbol_watch_set_summary.md:3-64`, `baseline/cot/phase0_offline_eval/result/1/reports/symbol_watch_set_summary.md:3-64`)

そして構造はほぼ不変。

- `glyph_len5`: `0/20`
- `manual_audit_priority`: `0/30`
- `verified_trace_ready`: `15/15`

(`baseline/cot/phase0_offline_eval/result/1/reports/symbol_watch_set_summary.md:15-49`)

つまり Phase 1 後も、

- easy / verified な numeric-like symbol は解ける
- glyph exact string と manual hard slice は解けない

という二極構造のままである。

failure kind も

- `numeric2x2_boxed_wrong`: 5
- `numeric2x2_unboxed_wrong`: 10
- `glyph_boxed_wrong`: 6
- `glyph_unboxed_wrong`: 14

で、やはり hard symbol は exact-output 崩壊が中心。(`baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_eval_row_level.csv`)

改善例:

- `9cb03277`: `7 → 26` に改善。(`baseline/cot/phase0_offline_eval/result/0/artifacts/phase0_eval_row_level.csv:278`, `baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_eval_row_level.csv:278`)

未改善 / 退行例:

- `2c8e2e06`: 前回と同じく `&52` に対して `52` のまま。leading symbol を落とす exactness failure。(`baseline/cot/phase0_offline_eval/result/0/artifacts/phase0_eval_row_level.csv:284`, `baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_eval_row_level.csv:284`)
- `b13d511a`: `\&[[` に対し `&[[` ではなく今回は `[[[` へ崩れ、むしろ悪化。(`baseline/cot/phase0_offline_eval/result/0/artifacts/phase0_eval_row_level.csv:302`, `baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_eval_row_level.csv:302`)
- `7c5c7b73` など、numeric symbol でも `13 → -13` のように符号を誤る退行が出ている。(`baseline/cot/phase0_offline_eval/result/0/artifacts/phase0_eval_row_level.csv:277`, `baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_eval_row_level.csv:277`)

## 5. easy family でも退行はある

今回のスコア改善だけを見ると楽観しやすいが、easy family にも危険な退行がある。

- `f0c8102d` (`roman`): `XLIII` 正解 → 長文ループ後の `last_number=4` で誤答。(`baseline/cot/phase0_offline_eval/result/0/artifacts/phase0_eval_row_level.csv:126`, `baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_eval_row_level.csv:126`, `baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_eval_raw_outputs.csv`)
- `0fd8b43e` (`unit`): `30.23` 正解 → `boxed_empty` へ退行。(`baseline/cot/phase0_offline_eval/result/0/artifacts/phase0_eval_row_level.csv:70`, `baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_eval_row_level.csv:70`, `baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_eval_raw_outputs.csv`)

この 2 件は、「Phase 1 は万能な安定化ではない」ことを示している。

## 6. 出力長から見えること

family ごとの平均出力長を result/0 と比べると、

| family | result/0 mean len | result/1 mean len | comment |
| --- | ---: | ---: | --- |
| `gravity` | 10432 | 2035 | 大幅短縮、改善と整合 |
| `text` | 10970 | 7157 | 短縮、改善と整合 |
| `binary` | 15784 | 15256 | ほぼ変わらず、依然長すぎる |
| `symbol` | 13906 | 13469 | ほぼ変わらず、依然長い |

(`baseline/cot/phase0_offline_eval/result/0/artifacts/phase0_eval_raw_outputs.csv`, `baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_eval_raw_outputs.csv`)

ここが今回の一番分かりやすいポイントで、Phase 1 の効果は

- gravity / text の runaway reasoning を抑える
- final answer を boxed に着地させやすくする

ところでは効いている。

しかし

- binary の 8-bit exact answer
- symbol glyph の exact string

のような hard exact-output 領域には、まだ十分な inductive bias が入っていない。

## 7. holdout から見ても binary はまだ広く弱い

binary holdout は small-sample なので過信は禁物だが、`result/1` でも

- `gap_signature` fold 4: `0/10`
- `structured_family` fold 1: `5/40 = 0.125`
- 良い slice でも `structured_family` fold 0 の `6/11 = 0.5455`

程度で、広い slice を安定攻略しているとは言い難い。(`baseline/cot/phase0_offline_eval/result/1/artifacts/phase0_binary_holdout_accuracy.csv:1-17`)

`solver_family=4` の `8/20 = 0.4` は多少良いが、これでも十分ではない。hard binary の本線改善はまだ必要。

## 8. 今回の Phase 1 をどう評価するか

### 良い点

- overall は確実に改善
- `general_stable_set` が `0.94` まで上がった
- `text` と `gravity` で `last_number` 崩壊が大きく減った
- いくつかの binary / symbol 行も救えている

### 悪い点

- `binary` は依然 `0.20`
- `glyph_len5` は依然 `0/20`
- `symbol manual_audit_priority` は依然 `0/30`
- easy family にも退行が残る

### 実務判断

Phase 1 は **general emission stabilizer** としては有効だった。しかし **binary-first / symbol-aware hard slice 攻略法** としてはまだ不足である。

したがって次の優先順位は変わらない。

1. `binary_hard_set` を主ゲートとして binary exact-answer を鍛える
2. `glyph_len5` / manual symbol を別タスクとして明示的に鍛える
3. gravity / text で得た emission 改善を壊さないように進める

## 9. 最終まとめ

今回の `result/1` は、`result/0` に対して「少し良くなった」のではなく、より具体的には

- **text / gravity をかなり良くした**
- **last-number 崩壊をかなり減らした**
- **しかし binary / glyph exactness はほぼ据え置き**
- **その代わり easy family に小さな退行も出た**

という結果だった。

したがって、この Phase 1 は捨てるべきではない。general stability を押し上げる部品として価値がある。

ただし leaderboard 目標に対しては、これ単体では足りない。次に必要なのは、overall 改善の継続ではなく、`binary` と `symbolic exact string` へ明示的に圧をかける次段の学習・評価ループである。
