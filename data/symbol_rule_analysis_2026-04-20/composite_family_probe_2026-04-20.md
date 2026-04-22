# Composite Family Probe (2026-04-20)

## Scope

- 参照データは README.md と data/train_with_classification.csv のみ
- 対象は cryptarithm 系 explicit solver の未回収 family を増やすための composite rule probe
- 実装は data/symbol_rule_analysis_2026-04-20/analyze_symbol_rules.py の単一ファイルに追加した opt-in family 拡張で検証

## README Context

- README.md の base model 実測では Cryptarithm (Guess) 0 / 164, Cryptarithm (Deduce) 2 / 659 と極端に低い
- そのため、train 上で explicit family の辞書拡張がどこまで効くかを先に詰める必要がある

## Current Symbolic Gap Shape

現 explicit solver で未回収な symbolic operator-group の長さプロファイルは 4 桁系に強く偏る。

- (4,4): 79 groups
- (3,4): 36 groups
- (3,3): 29 groups
- (2,3,3): 24 groups
- (3,4,4): 21 groups
- (4,): 21 groups
- (2,2,3): 21 groups
- (4,4,4): 20 groups

代表 row:

- 00457d26: missing `*`, signatures include 01234->NNNN and 01234->NN30
- 00c032a8: missing `!`, two 4-char outputs
- 01b2aa67: missing `&`, two 4-char outputs
- 05bd2dab: missing `^`, three 4-char outputs with mixed copied positions

## What Was Tested

### 1. Existing Generic Family Expansion Only

- 既存 engine が parse できるが CORE_FAMILY_PRIORITY に入っていない generic family を 316 個列挙
- hard row 8 件
  - 00457d26
  - 00c032a8
  - 012cab1f
  - 01b2aa67
  - 022c4d73
  - 035c4c40
  - 053b4c86
  - 05bd2dab
- 結果: 0 hit

結論:

- priority 漏れだけではない
- family class 自体が足りていない

### 2. Scalar + Scalar Concat Mining on Numeric Unresolved Groups

- 対象: equation_numeric_deduce の既存 DSL 未回収 operator-group 906 個
- family space: 968
- 結果: 29 / 906 = 3.2%

上位 family:

- x+y:nat + y//x:nat:strip0: 3
- x:nat + y:nat: 2
- x//y:pad2 + x//y:nat: 2
- x-y:nat + x//y:nat:strip0: 2
- x*y:nat + y//x:nat:strip0: 2
- y//x:nat + y//x:pad2: 2

結論:

- 少数の複合 DSL はある
- ただし unresolved の主塊を説明するには弱い

### 3. Scalar + Pairwise Concat Mining on Numeric Unresolved Groups

- 対象: equation_numeric_deduce の既存 DSL 未回収 operator-group 906 個
- family space: 4928
- 結果: 21 / 906 = 2.3%

上位 family:

- x:nat + max:ac_bd: 2
- y//x:nat + sum:ac_bd:strip0: 2
- その他はほぼ単発

結論:

- scalar+pairwise は 4 桁 composite の一部には当たる
- ただし主力 family class とまでは言えない

### 4. Pairwise Chunk Pad2 Probe

- 仮説: 未回収 4 桁群は pairwise 各チャンクを 2 桁 zero-pad している
- 対象: equation_numeric_deduce の既存 DSL 未回収 operator-group 906 個
- family space: 56
- 結果: 0 / 906 = 0.0%

結論:

- `sum:ac_bd` などの単純な pad2 化は主因ではない

### 5. Pairwise + Pairwise Probe

- 仮説: 未回収 4 桁群は pairwise result 2 本の連結
- 対象: equation_numeric_deduce unresolved 先頭 200 group sample
- family space: 12544
- 結果: 3 / 200 = 1.5%

結論:

- pure pairwise chaining だけでも主塊は説明できない

### 6. Expr + Copied Digits Probe

- 仮説: symbolic unresolved signatures の `NN30`, `2N0N` などは「計算結果 + 入力 digit のコピー混在」
- 対象: equation_numeric_deduce の既存 DSL 未回収 operator-group 906 個
- family space: 5360
- 結果: 41 / 906 = 4.5%

上位 family:

- x+y:nat + copy:c: 3
- x+y:nat + copy:a: 2
- y//x:nat + copy:a: 2
- copy:aa + prod:ac_bd:strip0: 2
- その他は単発だが `copy + expr` / `expr + copy` の両方が出る

結論:

- 今ターンで試した composite class の中では最も強い
- unresolved symbolic signature が mixed copy/new を含むという観測とも整合する

### 7. Shallow Position-Wise 1-Digit Function Probe

- 仮説: 4 桁出力は各桁が浅い 1-digit 関数で書ける
- 対象: unresolved numeric 4-digit, 2-example group 53 個 sample
- family space: 単純な 44 関数の位置別組み合わせ
- 結果: 1 / 53 = 1.9%

結論:

- 浅い per-position digit formula だけで説明するのは難しい

## Code Change

- analyze_symbol_rules.py に opt-in の composite family 拡張を追加した
- 現時点では `--include-composite-families` でのみ有効
- 既定の solver family priority は維持

追加済みの opt-in composite family は、numeric mining で拾えた少数の scalar+scalar / scalar+pairwise family を benchmark 用に入れている

## Symbolic Benchmark Status

- 現コードでの baseline explicit coverage 再計測
  - command: `--core-upper-bound --limit 100 --max-assignments 512`
  - result: 20 / 100 = 20.0%
  - by_label: cryptarithm_guess 5, cryptarithm_deduce 15
- 同じ現コードで `--max-assignments 1024` にすると baseline は 21 / 100 = 21.0%
- したがって 20 / 100 と 21 / 100 の差は solver regression ではなく探索上限差
- 旧 composite family 集合での途中 benchmark では 50 行時点で 11 / 50、baseline は 10 / 50 だった
- 現行 composite family 集合でも少なくとも 1 行の明示的な増分を確認した
  - row: `08f6216d`
  - baseline: unsolved at both 512 and 1024 assignments
  - composite: solved at both 512 and 1024 assignments
  - family assignment: `* -> concat|x-y|nat|x//y|nat|strip0`, `+ -> swap_halves`, `- -> y%x`
- hard row spot check では 00457d26, 00c032a8, 012cab1f, 01b2aa67, 022c4d73, 035c4c40, 053b4c86, 05bd2dab で新規 hit なし

## Practical Takeaway

- このターンの結果だけでは 80% へ届く方向性はまだ見えていない
- ただし search space の切り捨ては進んだ
  - generic family priority 漏れではない
  - simple scalar concat 主体でもない
  - simple pairwise pad2 でもない
  - simple pairwise+pairwise でも主塊ではない
- 相対的に最も有望なのは `expr + copied positions` を許す mixed-output family

## Next Step

- 次の explicit grammar 候補は `computed chunk + copied digit positions` を first-class に持つ family class
- 具体的には `expr + copy:c`, `expr + copy:a`, `copy:aa + expr`, `expr + copy:ca` などを symbolic solver へ直接入れて、hard row と first 100 coverage の差分を測る

## 2026-04-21 Follow-up

- README.md の cryptarithm 文脈に合わせ、search 側の冗長探索を減らすため `reduced group map cache` と `failed-state memoization` を solver に追加した。
- ただし baseline 25 行 benchmark は `6 / 25` のままで、`max_assignments=1024` と `4096` の両方で増分なし。
- row `012cab1f` は `max_assignments=65536` でも未解決で、さらに `>` と `]` の current family 候補どうしに pairwise consistent map が 1 つも無いことを確認した。
- したがって hard symbolic の主因は search ceiling ではなく family basis の欠落。
- `expr + copy:ca` / `NNca` 近傍の curated symbolic probe も追加で実施した。
  - scalar copymix + scalar mask: 792 candidates, hard `*` rows `00457d26`, `01ef1e3e`, `035c4c40`, `053b4c86` に対して 0 hit
  - generic copymix + generic mask: 680 candidates, 同 4 row に対して 0 hit
- 現時点の read は次の通り。
  - 既存 parser class の近傍拡張だけでは dominant hard rows を動かせていない
  - `expr + copied positions` 方向は numeric unresolved では signal があるが、symbolic hard rows ではさらに別の computed chunk class が必要そう
  - 次ターンの family mining は search tweak ではなく、新しい computed-chunk family を明示的に仮説化して当てる段階

## 2026-04-22 Follow-up

- current file には generic `prod:*` family の plain 16 variant が入っている。
- first100 zero-op support は `63 / 36 / 1` から `65 / 35 / 0` へ改善した。
- current benchmark は `uv run python data/symbol_rule_analysis_2026-04-20/analyze_symbol_rules.py --core-upper-bound --limit 100 --max-assignments 1024` で `24 / 100`。
- ただし support 増分がそのまま solved 増分には落ちていない。
  - `02e871e4`, `0babcba2`, `1545b8f1` は current support 上は改善しているが individually unsolved のまま。
- 現時点の read はよりはっきりしている。
  - `prod:*` のような未登録 generic family を足すと support は少し動く
  - しかし dominant hard rows の主因は依然として family basis の不足か global consistency failure
  - completion 条件の 659 / 823 explicit 回収に向けては、generic family の取りこぼし回収だけでは全く足りない