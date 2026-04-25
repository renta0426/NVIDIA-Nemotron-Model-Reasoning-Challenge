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
- CPU RAM 枯渇対策として、`core_family_records` の重複 cache を外し、`core_family_output_index` / `core_reduced_group_maps` を bounded cache に変更した。
- local validation では symbolic first3 rows の可否は不変で、wallclock は `28.156s -> 24.959s`。
- ただし support 増分がそのまま solved 増分には落ちていない。
  - `02e871e4`, `0babcba2`, `1545b8f1` は current support 上は改善しているが individually unsolved のまま。
- row `012cab1f` に対して、`concat` 近傍の unlisted family 121 本を narrow probe した。
  - target operator `'`: 0 hit
  - non-target `>`: 0 hit
  - non-target `]`: 0 hit
- row `012cab1f` に対して、target `'` の full scalar `concat` 957 本も追加で probe したが 0 hit。
- row `012cab1f` に対して、narrow `mix` 近傍 158 本も追加で probe した。
  - target operator `'`: 0 hit
  - non-target `]`: 0 hit
- row `012cab1f` に対して、さらに次の narrow probe を行ったが、すべて 0 hit。
  - target `'`: scalar `copymix` 375 本, scalar `mask` 184 本
  - non-target `>`: scalar `copymix` 68 本, scalar `mask` 144 本, 仮説的 mod-10 pairwise class 32 本
  - non-target `]`: `pairconcat` 200 本
- ここでの hit 判定は「その operator の reduced map が、残り 2 operator の current survivor family 群それぞれと pairwise merge を持つか」。
- したがって `012cab1f` の dominant gap は current parser 近傍の `concat` / `mix` / `copymix` / `mask` / `pairconcat` / mod-10 pairwise 仮説ではない。
- 別 anchor として row `02e871e4` も再点検した。
  - current file では operator `+` が zero-candidate で、`*` は 8 candidate, `-` は 109 candidate。
  - `+` の example output 長は `(2,3,3)` で、target は別 operator にある。
  - row-local probe では unlisted generic 300 本, scalar `copymix` 76 本, full scalar `concat` 957 本, dual-chunk generic 仮説 392 本, scalar `mask_strip0` 1200 本がすべて 0 hit。
  - `generic copymix` 2240 本と `generic mask-strip0` 1344 本も 0 hit。
  - さらに broad `mix` 4924 本と、3 桁の independent 1-digit function strip0 仮説 5832 本も 0 hit。
  - この output-length profile `(3,(2,3,3),None)` は symbolic 全体で 27 群あり、そのうち 14 群が current zero-candidate。
- 現時点の read はよりはっきりしている。
  - `prod:*` のような未登録 generic family を足すと support は少し動く
  - しかし dominant hard rows の主因は依然として family basis の不足か global consistency failure
  - `012cab1f` に関しては current parser 近傍の主要 composite grammar をかなり強く除外できたので、次の probe は新しい 2-digit generic class か parser 外の non-concat computed chunk へ移すべき
  - `02e871e4` 型の `(2,3,3)` mixed-length cluster も zero-op 母数があるので、単発 row ではなく family class として扱う価値がある
  - ただし `02e871e4` については current parser の broad `mix` まで空振りなので、単なる whitelist 拡張ではなく parser 外の new class を仮説化する必要がある
  - completion 条件の 659 / 823 explicit 回収に向けては、generic family の取りこぼし回収だけでは全く足りない

- zero-op profile ranking を symbolic 全体で取り直した。
  - 最大母数は `(2,(4,4),None)` で `52 / 142` zero-candidate。
  - target-present では `(2,(4,4),4)` が `20 / 57` zero-candidate。
  - 次点は `(2,(3,4),None)` が `21 / 42`, `(3,(4,4,4),None)` が `16 / 42`, `(3,(2,3,3),None)` が `14 / 27`。
- `(2,(4,4),4)` の operator 分布は `*` に強く偏っている。
  - profile 全体では `* = 34 / 57`。
  - zero-candidate 側では `* = 16 / 20` で、残りは `%`, `|`, `&`, `>` が各 1。
- `(2,(4,4),4)` の `*` 行では、zero/nonzero の両方が surface repetition signature `('abcd','abcd')` に集まる。
  - nonzero 側でも zero 側でも最頻 signature が同じなので、dominant gap は formatter より arithmetic family 差分の可能性が高い。
  - 同 signature の current nonzero rows は first candidate が plain `x*y` に落ちる (`3cb3fd89`, `a52c726c`, `d0e1010b`, `dc6c0d49`, `e62b6ae9`)。
- dominant zero slice の representative row `1785b35e` (`(2,(4,4),4)` / operator `*`) で `x*y` 近傍を追加 probe した。
  - `pairconcat(prod,prod)` 512 families: example-side 0 hit, target-compatible 0。
  - custom direct check による broad basic `pairconcat` (`sum/diff/rdiff/absdiff/prod/max/min` x `ac_bd/ad_bc/ab_cd/cd_ab`, no-swap/no-strip0, 784 families) も example-side 0 hit, target-compatible 0。
  - scalar `mask|scalar|x*y|...` + `copymix|scalar|x*y|...` 1074 families: example-side 0 hit, target-compatible 0。
  - scalar `concat` with at least one `x*y` side 84 families: example-side 0 hit, target-compatible 0。
  - fixed 2-digit `pairconcat(max/min/absdiff, max/min/absdiff)` 144 families: example-side 0 hit, target-compatible 0。
  - plain 4-digit `x*y` の digit permutation 24 と 9-complement+permutation 48 も 0 hit。
- same multiplication gap は target-absent の最大 profile `(2,(4,4),None)` にも強く出ている。
  - profile 全体の operator 分布は `* = 77 / 142`, `+ = 29 / 142`。
  - current zero-candidate は `* = 38 / 77`, `+ = 2 / 29`。
  - したがって symbolic 全体の最大未解決 profile でも主因は non-target `*` 4-char support 欠落。
- unresolved `*` 4-char rows の surface signature は cluster family に向かない。
  - target-present `(2,(4,4),4)` の unresolved `*` 16 行は exact repetition signature が 16/16 で全て一意。
  - target-absent `(2,(4,4),None)` の unresolved `*` 38 行も exact repetition signature が 38/38 で全て一意。
  - したがって dominant gap は少数の repeated surface pattern ではなく、より抽象的な arithmetic family 欠落として扱うべき。
- target-present unresolved `*` 16 行に対して、plain product-digit family を slice-wide に再点検した。
  - explicit 00..99 enumeration で raw 4-digit `x*y` permutation 24 と 9-complement+permutation 24 を全 row に再適用したが、target-compatible hit row は `0 / 16`。
  - 既存の raw/c9 product-digit rearrangement family では dominant slice の subset すら剥がせない。
- ただし `1785b35e` の product-digit-derived one-digit hypothesis 自体は死んでいない。
  - 出力 digit を input digit ではなく `x*y` の 4 桁 product digits `p0..p3` から 1-digit 関数で作る仮説を position-wise に調べると、4 position 全てで多数候補が残る。
  - row-local viable count は position0 = 32, position1 = 38, position2 = 32, position3 = 28。
  - 強い surviving functions は `sum_carry:01/12/13`, `9-p3`, `9-p2`, `absdiff:02/12/13`, `max:02/12` などで、以前の input-digit shallow family failure と対照的に signal がある。
  - sub-search では position2-3 の強い pair と position1 の `sum_carry:01` / `sum_carry:13` まで小さな frontier に落ちる一方、現 library の position0 候補を足した full 4-tuple は 0 hit だった。
  - 現時点の read は「product-digit family 全体が無い」のではなく、「位置0の関数族が現 library では不足している可能性が高い」。
- `1785b35e` に対して position0 を second-order combiner まで広げると、row-local では初めて full 4-tuple が立つ。
  - verified tuple class は `pos0 = 9-absdiff(p0, max:12)` と `pos1 in {sum_carry:01, sum_carry:13}`, `pos2 = sum_mod:23`, `pos3 in {max:02, p2}` の 4 variant。
  - explicit 00..99 enumeration では `!^*?] -> !>"?`, `:&*?? -> ]>/!`, `(!*?! -> :^:/` に対して final survivor 1 map を再現した。
  - したがって dominant row の local gap は、input-digit family ではなく `x*y` product digits 上の second-order computed-digit class で説明できる。
  - さらに non-`*` side の joined maps 17 本を seed にして generic tuple search を掛けると、row-consistent full solve も見つかった。verified tuple は `pos0 = 9 - prod_mod(p2, prod_mod:12)`, `pos1 = absdiff(p3, prod_tens:13)`, `pos2 = sum_mod(absdiff:12, max:12)`, `pos3 = prod_mod(9-p1, max:02)`。
  - explicit merge では final solution 1 件を再現し、digit map は `!->3, "->1, &->8, (->0, /->4, :->5, >->2, ?->6, ]->7, ^->9` になった。non-`*` families は `+ = prod:ac_bd:swap`, `- = x-y` で join する。
  - この tuple は `prod_tuple|expr0|expr1|expr2|expr3` family として実装済みで、default solver でも `1785b35e` を solve する。
- ただしこの second-order class の slice-wide reuse は薄い。
  - unresolved `*` 4-char groups 全体 58 件に対して、上の 4 tuple variant を example-side / target-sideで再点検すると、example-side hit row は `5 / 58`、full hit row は `0 / 58`。
  - example-side hit row は `1785b35e`, `2fc5ef5b`, `563bf8f9`, `64d775e5`, `a4e4ec1d` のみ。
  - 内訳は `(2,(4,4),4)` が 2 行、`(2,(4,4),None)` が 3 行で、dominant target-present slice 全体を剥がす class ではない。
- hit rows 5 件の surface を比較しても、narrow repeated subcluster は見えない。
  - canonical pair signatures は 5 / 5 で相互に異なり、target-present / target-absent, `cryptarithm_deduce` / `cryptarithm_guess` が混在する。
  - したがってこの second-order class は reusable family 候補というより thin-support sibling とみなすべき。
- 次点の unresolved zero-op profile でも、surface cluster 側の突破口は見えていない。
  - `(2,(3,4),None)` は zero rows 21 件のうち `* = 15` が支配的で、上位 unresolved signatures は全て singleton。
  - `(3,(4,4,4),None)` も zero rows 16 件のうち `* = 13` が支配的で、こちらも上位 unresolved signatures は全て singleton。
  - したがって次の pivot も repeated surface ではなく、row-local arithmetic family 探索として扱うべき。
- `(3,(4,4,4),None)` の representative row `30ac5c8e` は、`*` 側だけなら first-order product-digit family が row-local に立つ。
  - `:/*/} -> #/&?`, `}&*#" -> #&\}`, `\}*)@ -> &&#?` に対し、`pos0 = sum_mod:03`, `pos1 = max:03`, `pos2 = p2`, `pos3 = absdiff:01` で final merged map 1 件を再現した。
  - これは `98*87 = 8526`, `72*41 = 2952`, `57*06 = 0342` から `4823`, `4257`, `2243` を作る row-local first-order computed-digit hit で、`1785b35e` のような second-order まで要らない。
- ただし `30ac5c8e` は clean `*` anchor ではなく multi-gap 行だった。
  - 上の `*` map を固定して row 全体を join すると、既存 `-` family 52 本の reduced maps とは `0` 件、`+` side でも example maps / target maps ともに `0` 件しか join しない。
  - したがってこの row は「`*` family を足せば解ける行」ではなく、少なくとも `*` 以外にも missing family が残っている証拠である。
- したがって current parser-neighbor の multiplication-side extension (`x*y` concat/mask/copymix/permutation と narrow pairconcat) では、dominant `*` 4-char zero slice の representative row は説明できない。
  - 次の multiplication-side仮説は、`x*y` 近傍ではなく parser 外の新 computed-digit transform class として立てるべき。
- clean な non-target `*` anchor として `99b7018f` も追加で点検した。
  - この row は `*` examples 3 本、target は unseen `+` で、既存 family 候補数は `* = 0`。`*` 側だけを独立に見られるため、OOM を避けた lightweight probe の代表に向く。
  - まず plain multiplication cryptarithm として解けるかを直に再点検したが、distinct digits 前提の標準形でも、leading zero を許した緩い形でも example-side exact solution は `0` 件だった。
  - したがって `99b7018f` の missing `*` は「普通の掛け算を既存 parser が取り逃がしただけ」の型ではなく、やはり computed-digit family 側の gap とみるべき。
- `99b7018f` の first-order product-digit probe では、inner positions にだけ強い signal が出た。
  - position-wise top counts は `pos1: 03_min -> 6`, `pos2: 03_prod_mod -> 78`, `pos3: p3 -> 192` で、少なくとも middle digits には product-digit-derived family が掛かる余地がある。
  - ただし strongest singles 同士をそのまま join すると `pos1 = 03_min`, `pos2 = 03_prod_mod` は `0` 件で、individual best を並べるだけでは row を説明できない。
  - pos1 top5 x pos2 top5 の小さい直積を調べると、唯一 surviving した pair は `pos1 = prod_mod:13`, `pos2 = min:03` で、reduced map は `1` 件だった。
  - その partial map は `"->8, $->6, '->5, )->0, :->4, >->2, \\->7, {->1, |->3` を固定し、example-side decoded products は `3876`, `1584`, `5146` になる。
- しかし `99b7018f` は full first-order row には伸びなかった。
  - 上の unique partial map を固定したうえで current first-order library 全体を再点検すると、outer positions `pos0` と `pos3` を延長できる候補はどちらも `0` 件だった。
  - したがってこの row は「first-order product-digit family が全体を説明する clean hit」ではなく、「inner pair には本物の product-digit signal があるが、outer positions には richer class が要る」thin-support sibling とみなすべき。
- `99b7018f` は outer positions だけを second-order combiner に広げると、`*` side の full local tuple まで届く。
  - verified tuple の一例は `pos0 = 9 - sum_mod(9-p2, prod_mod:01)`, `pos1 = prod_mod:13`, `pos2 = min:03`, `pos3 = absdiff(absdiff:01, prod_tens:01)`。
  - explicit 00..99 enumeration では `'{*\\$ -> |"||`, `||*:" -> |){:`, `"|*$> -> ^$':` に対して final survivor 1 map を再現し、`"->8, $->6, '->5, )->0, :->4, >->2, \\->7, ^->9, {->1, |->3` を得た。
  - したがってこの row の `*` gap は、`1785b35e` より軽い「inner は first-order product-digit、outer だけ second-order」の hybrid computed-digit class で説明できる。
  - ただし target は unseen `+` のままなので、これは row 全体の solve ではなく non-target `*` family support の新証拠として扱うべきである。
  - さらに same-profile (`3 examples`, all `*`, 4-char outputs) 6 行にこの exact tuple を example-side で当て直すと hit は `1 / 6` で、`99b7018f` 自身しか再現しなかった。
  - よってこの hybrid tuple も reusable family というより、`30ac5c8e` と同様に row-local thin-support sibling とみるのが妥当である。
- clean target `*` gap として `2fc5ef5b` も追加で切った。
  - operator-level に見ると `+` side は既存 family 候補が `10` 本ある一方、target `*` は `0` 本で、row 全体の failure は実質 `*` 側に集中している。
  - 以前の `1785b35e` second-order class 4 variant を example-side に当て直すと、`pos1 = sum_carry:13`, `pos2 = sum_mod:23`, `pos3 = p2` を含む 1 variant だけが `*` examples を通し、reduced map も `1` 件だった。
  - ただしその unique example map を target に延長すると、inputs は `60 * 84` に固定される一方、class が作る target output は `8044` で、gold `0673` には全く届かない。target-compatible hit は `0` 件だった。
  - その map が誘導する numeric triples は `3569 -> 6156`, `7154 -> 7095`, `5040 -> 0673` で、ここに対して現 first-order product-digit library を再点検すると全 position `0` hit、second-order combiner を見ても `pos0 / pos1 / pos3` には候補があるのに `pos2` は `0` hit だった。
  - よって `2fc5ef5b` は `1785b35e` の近傍 sibling ではあるが、そのまま同 classを target まで延ばせる行ではない。少なくとも target `*` の core transform は、現 first/second-order product-digit vocabulary とは別物である。
  - 追加で reduced third-order grammar を切ると、target `*` 単体には compact continuation が見つかった。例として `pos0 = max(min:23, prod_mod:01)`, `pos1 = sum_mod(absdiff:02, sum_mod:01)`, `pos2 = sum_mod(9-absdiff:02, sum_mod:02)`, `pos3 = sum_mod(9-absdiff:01, sum_mod:02)` は `*` examples と target の 3 instances をすべて通し、reduced map `1` 件・target join `1` 件だった。
  - ただしその star map は `&->6, %->3, ^->1` を固定し、これは `+` side reduced maps が許す overlap triple 29 種のどれにも含まれなかった。実際、existing `+` families との join count は `0` だった。
  - この false lead の後、search を full `+` reduced maps 190 本に戻し、残りの free symbols を `\` と `'` の 2 つだけに絞って再探索した。
  - そこで `+ = x+y` と両立する row-consistent star tuple が見つかった。verified tuple は `pos0 = sum_mod(sum_mod:01, max:13)`, `pos1 = prod_mod(sum_mod:01, sum_mod:23)`, `pos2 = 9 - prod_tens(9-p0, p2)`, `pos3 = 9 - sum_mod(absdiff:03, max:03)`。
  - explicit merge では full solution 1 件を再現し、digit map は `$->2, %->1, &->6, '->3, /->0, :->7, \->5, ^->4, {->8, }->9` だった。decoded row は `71*31 -> 6496`, `51*87 -> 5089`, target `60*73 -> 0651`, plus examples は `07+87 -> 94`, `26+16 -> 42` で、`x+y` と完全に整合した。
  - よって `2fc5ef5b` は「target `*` vocabulary の外側にある unsolved row」ではなく、「second-order `1785` class では足りないが、row-consistent third-order product-digit tuple を 1 本足せば解ける row」に再分類された。
- ただし同じ `1785b35e` class でも、non-target `*` gap row では row-level solve まで届く例がある。
  - `64d775e5` では `*` side current candidates が `0`、`+` side は example/target とも `swap_halves` 1 本だけが残る clean row だった。
  - `1785` class の variant `pos0 = 9-absdiff(p0, max:12)`, `pos1 = sum_carry:13`, `pos2 = sum_mod:23`, `pos3 = p2` を `*` examples に当てると reduced map `1` 件を得て、それが `+` examples の `swap_halves` と target `+` の `swap_halves` の両方に join した。
  - explicit merge では final solution 1 件を再現し、digit map は `!->7, $->0, %->5, &->6, /->8, @->9, \`->3` になった。
  - したがって earlier の `0 / 58` は「この class 単体で target `*` まで説明する full-hit がない」という意味では保たれるが、「non-target `*` gap row を既存他operator family と組んで row-level solve できる例がない」とまでは言えない。`64d775e5` はその反例である。
- 上の `1785` class は `analyze_symbol_rules.py` に `prod_digits|1785|carry01|max02`, `prod_digits|1785|carry01|p2`, `prod_digits|1785|carry13|max02`, `prod_digits|1785|carry13|p2` の 4 family として実装した。
  - default solver (`explain_symbol_row_with_core_solver`) でも `64d775e5` は `{'+' : 'swap_halves', '*' : 'prod_digits|1785|carry01|max02'}` で solve されるようになった。
  - さらに generic `prod_tuple|expr0|expr1|expr2|expr3` interpreter を追加し、`2fc5ef5b` の row-consistent tuple を family 化したことで、default solver でも `{'*': 'prod_tuple|sum_mod(sum_mod01,max13)|prod_mod(sum_mod01,sum_mod23)|9-(prod_tens(9-p0,p2))|9-(sum_mod(absdiff03,max03))', '+': 'x+y'}` で solve されるようになった。
  - 同じ interpreter に `1785b35e` の row-consistent tuple `prod_tuple|9-(prod_mod(p2,prod_mod12))|absdiff(p3,prod_tens13)|sum_mod(absdiff12,max12)|prod_mod(9-p1,max02)` も追加し、default solver で `{'*': 'prod_tuple|9-(prod_mod(p2,prod_mod12))|absdiff(p3,prod_tens13)|sum_mod(absdiff12,max12)|prod_mod(9-p1,max02)', '+': 'prod:ac_bd:swap', '-': 'x-y'}` を再現した。
  - そのまま `563bf8f9` と `a4e4ec1d` にも target-compatible non-`*` seed search を当てると、両方とも free symbols は高々 2 個で、row-consistent tuples が見つかった。
  - `563bf8f9` の verified tuple は `pos0 = 9-absdiff:03`, `pos1 = min:02`, `pos2 = 9-p3`, `pos3 = 9-sum_mod:12` で、`+ = sum:ac_bd`, target `- = op+diff:ac_bd` と join し、final map `!->4, "->5, $->8, %->6, '->3, /->2, :->7, <->9, \`->0, {->1` を与えた。
  - `a4e4ec1d` の verified tuple は `pos0 = 9-max:12`, `pos1 = 9-p0`, `pos2 = sum_mod(9-p2, p0)`, `pos3 = absdiff(p0, sum_mod:23)` で、`- = x-y` と join し、final map `!->4, "->6, $->2, %->1, >->3, @->0, \->5, {->7, |->9, }->8` を与えた。
  - この 2 tuple も `prod_tuple|...` families として実装済みで、default solver で `563bf8f9` と `a4e4ec1d` の両方を solve する。
  - wider scan で `2e9973b7` も example-side では `prod_digits|1785|carry01|max02` に hit したが、これは new coverage ではない。row 自体は既存 solver でも `{'*': 'x*y', '-': 'y-x', '+': 'drop_op'}` で既に solve 済みだった。
  - したがってこの wave の immediate value は「example-side hit row を増やすこと」ではなく、既存 solver が未解決だった `*`-heavy rows を実際に回収した点にある。initial six-row hit slice だけでも `1785b35e`, `2fc5ef5b`, `563bf8f9`, `64d775e5`, `a4e4ec1d` の 5 行を new current coverage として回収した。
  - current symbolic rows のうち「`*` examples が 2 本で両方 4-char」の slice を再走査すると、この family の example-side hit row は `6` 件だった: `1785b35e`, `2e9973b7`, `2fc5ef5b`, `563bf8f9`, `64d775e5`, `a4e4ec1d`。
  - row-level で見ると、`2e9973b7` は既存 solver で既に解ける redundant hitだが、それ以外の 5 行はすべて current solver で回収された。つまり same six-row slice は now `6 / 6` solved で、そのうち `5 / 6` が new current coverage である。
- adjacent low-free row `0da1841f` も bounded seed search で追加回収できた。
  - この row は `*` examples が 2 本とも 4-char だが、target operator が unseen `+` で、`target = (\+#%`, `answer = (\#%` なので、target side は既存 `drop_op` family で固定できる。
  - `-` examples 側を既存 families で絞ると、`x+y` join 後の map で free symbols は `#`, `%`, `/` の 3 個だけだった。
  - その completion 全探索に `*` examples 上の product-digit grammar を当てると、verified tuple `pos0 = 9-prod_tens:01`, `pos1 = 9-min:01`, `pos2 = max(9-p0, sum_mod:02)`, `pos3 = sum_mod(max:01, p3)` が見つかった。
  - explicit merge では full solution 1 件を再現し、final map は `!->6, "->0, #->3, (->7, )->8, -->1, /->9, \->2, ]->5` だった。decoded row は `29*65 -> 9893`, `69*89 -> 9837`, `65+55 -> 120`, `75+85 -> 160`, target `72+34 -> 7234` で、default solver でも `{'*': 'prod_tuple|9-(prod_tens01)|9-(min01)|max(9-p0,sum_mod02)|sum_mod(max01,p3)', '+': 'drop_op', '-': 'x+y'}` を返す。
- neighboring row `dac75343` も同じ bounded search で追加回収できた。
  - この row も `*` examples は 2 本とも 4-char で、non-`*` side は `+` examples / target と `-` examples から seed を作れる。actual solver assignment は `+ = drop_op`, `- = x-y` になった。
  - target-compatible seeds は `46` 件あったが、いずれも free symbols は `3` 個 (`'`, `[`, `{`) に落ちていた。
  - completion 全探索に `*` examples 上の product-digit grammar を当てると、verified tuple `pos0 = p0`, `pos1 = max(absdiff:23, p0)`, `pos2 = 9-absdiff:03`, `pos3 = 9-absdiff:23` が見つかった。
  - explicit merge では full solution 1 件を再現し、final map は `#->9, %->3, '->5, (->1, )->0, @->8, [->6, \`->4, {->7, |->2` だった。decoded row は `32*49 -> 1227`, `82*71 -> 5569`, `33+74 -> 3374`, `38-10 -> 28`, `34-83 -> -49`, target `98+84 -> 9884` で、default solver でも `{'*': 'prod_tuple|p0|max(absdiff23,p0)|9-(absdiff03)|9-(absdiff23)', '+': 'drop_op', '-': 'x-y'}` を返す。
- neighboring row `398478f6` も low-free seed pair から追加回収できた。
  - この row は `-` example が 1 本、target `+` が unseen だが、`- = x//y` と target `+ = x*y` の pair が overlap join 後に seed `1` 件・free symbols `2` 個まで落ちた。
  - その 1 seed に対する bounded completion search で、verified tuple `pos0 = prod_tens(9-p3, 9-p3)`, `pos1 = prod_tens(p1, p1)`, `pos2 = 9-max:13`, `pos3 = 9-p1` が見つかった。
  - explicit merge では full solution 1 件を再現し、final map は `!->3, )->4, -->1, :->9, @->0, [->6, \->7, ]->5, \`->8, |->2` だった。decoded row は `65-05 -> 13`, `56*76 -> 0037`, `94*80 -> 8244`, target `24*04 -> 96` で、default solver でも `{'*': 'prod_tuple|prod_tens(9-p3,9-p3)|prod_tens(p1,p1)|9-(max13)|9-p1', '+': 'x*y', '-': 'x//y'}` を返す。
- former `hypothesis_formed` row `02902eb3` も同じ low-free route で回収できた。
  - この row は `-` example が 1 本、target `+` が unseen だが、`- = x%y` と target `+ = x%y` の pair から seed `6` 件・free symbols `2` 個まで落ちた。
  - その bounded completion search で、verified tuple `pos0 = 9-p2`, `pos1 = prod_mod:12`, `pos2 = absdiff(9-p0, max:02)`, `pos3 = max(9-p2, p3)` が見つかった。
  - explicit merge では full solution 1 件を再現し、final map は `!->5, $->2, %->8, &->6, )->4, /->3, >->1, ]->0, }->7` だった。decoded row は `56*88 -> 7818`, `20*66 -> 7667`, `86%31 -> 24`, target `55%21 -> 13` で、default solver でも `{'*': 'prod_tuple|9-p2|prod_mod12|absdiff(9-p0,max02)|max(9-p2,p3)', '+': 'x%y', '-': 'x%y'}` を返す。
- external `rule_found` row `b1b10e83` も finally 回収できた。
  - この row は `+` examples / target がすべて `drop_op` なので、non-`*` side は digit map をほとんど固定しない。代わりに `*` examples 側だけに現れる 7 symbols (`"`, `#`, `$`, `)`, `\\`, `{`, `|`) に対して star-only brute force を回した。
  - 7 symbols なので search space は `10P7 = 604800` 通りで、2 本の `*` examples を current product-digit grammar に通すだけで十分だった。
  - その結果、verified tuple `pos0 = min(9-p1, p1)`, `pos1 = 9-sum_mod(9-p1, 9-p1)`, `pos2 = prod_tens(9-p2, sum_mod(9-p1, 9-p1))`, `pos3 = prod_tens(9-p1, max(9-p1, p1))` が見つかった。
  - explicit merge では full solution 1 件を再現し、star-map は `"->0, #->1, $->2, )->3, \\->4, {->5, |->6` だった。decoded star rows は `10*10 -> 1356`, `24*30 -> 2521` で、default solver でも `{'*': 'prod_tuple|min(9-p1,p1)|9-(sum_mod(9-p1,9-p1))|prod_tens(9-p2,sum_mod(9-p1,9-p1))|prod_tens(9-p1,max(9-p1,p1))', '+': 'drop_op'}` を返す。
- row `5968bf6c` も同じ regime で追加回収できた。
  - non-`*` side からは `+ = prod:ad_bc:strip0swap`, `- = diff:ac_bd` の mergeable map が 1 本だけ残り、その時点で free symbol は `!` 1 個に落ちた。
  - その merged map から 3 本の `*` rows の product digits は `1702`, `5238`, `1092` に固定されるので、position-wise signature を直接閉包して新しい tuple `pos0 = max(max:01, sum_mod:03)`, `pos1 = sum_mod(max:02, p2)`, `pos2 = prod_tens(9-prod_mod:03, 9-p2)`, `pos3 = sum_mod(min:23, prod_mod:02)` を得た。
  - explicit merge では full solution 1 件を再現し、final map は `!->9, "->8, &->5, (->3, /->0, :->2, \\->7, ^->1, |->4, }->6` だった。decoded star rows は `23*74 -> 7160`, `97*54 -> 5858`, target `39*28 -> 3801` で、default solver でも `{'*': 'prod_tuple|max(max01,sum_mod03)|sum_mod(max02,p2)|prod_tens(9-(prod_mod03),9-p2)|sum_mod(min23,prod_mod02)', '+': 'prod:ad_bc:strip0swap', '-': 'diff:ac_bd'}` を返す。
- row `60f55291` も同じ route で追加回収できた。
  - non-`*` side は `-` examples だけなので、まず current family で `-` reduced maps を列挙した。最小 survivor は `sum:ac_bd:swap` / `sum:ac_bd:strip0swap` 系で、そこで free symbols は `[` と `\\` の 2 個だけになった。
  - `sum:ac_bd:strip0swap` の one-map case から free digits 2 通りだけを completion し、3 本の `*` rows (`target` を含む) の product digits `3904`, `0248`, `3337` に対する position-wise signature closure を回すと、short tuple `pos0 = sum_mod(absdiff:13, p2)`, `pos1 = min(absdiff:03, sum_mod:03)`, `pos2 = min(9-p2, absdiff:13)`, `pos3 = 9-sum_mod:23` が見つかった。
  - default solver での actual assignment は `{'*': 'prod_tuple|sum_mod(absdiff13,p2)|min(absdiff03,sum_mod03)|min(9-p2,absdiff13)|9-(sum_mod23)', '-': 'sum:ac_bd:swap'}` で、explicit merge の final map は `!->1, "->3, /->7, :->2, ?->9, [->8, \\->0, ]->5, {->6, |->4` だった。decoded star rows は `61*64 -> 5155`, `31*08 -> 0857`, target `47*71 -> 7049` になる。
- row `11e77bf9` も default-priority route で追加回収できた。
  - `*` side は earlier tuple `9-(absdiff03) / min02 / 9-p3 / 9-(sum_mod12)` では non-`*` side と 0 join だったので、まず default priority の `+` / `-` families だけで mergeable map を列挙した。
  - `+ = abs(x-y)` / `- = abs(x-y)` から free digit count 2 の merged map が 1 本残り、実際の non-operator free symbol は `^` 1 個だけだった。
  - その `^` に残る 2 digits (`0`, `9`) を completion し、2 本の `*` rows の product digits `1900`, `2664` に対する position-wise signature closure を回すと、default-compatible short tuple `pos0 = p2`, `pos1 = prod_mod:12`, `pos2 = absdiff(p1, sum_mod:03)`, `pos3 = p3` が見つかった。
  - default solver では `{'*': 'prod_tuple|p2|prod_mod12|absdiff(p1,sum_mod03)|p3', '+': 'rdiff:ac_bd', '-': 'abs(x-y)'}` を返し、explicit merge の final map は `!->1, #->4, %->7, &->9, '->2, :->6, @->3, \\->8, ^->0` だった。decoded row は `61*89 -> 2809`, `84*39 -> 7416`, `34+76 -> 42`, `83-67 -> 16`, target `61-93 -> 32` になる。
- ここまでで、broader two-`*` / 4-char regime における confirmed new current coverage は `02902eb3`, `053b4c86`, `083ed8fe`, `0da1841f`, `11e77bf9`, `1785b35e`, `24750c4a`, `2e9b1b9d`, `2fc5ef5b`, `398478f6`, `563bf8f9`, `5968bf6c`, `60f55291`, `64d775e5`, `693432da`, `75c8715e`, `7cb3089e`, `8395d060`, `93c9b36b`, `9f1ff166`, `a4e4ec1d`, `b1b10e83`, `dac75343`, `f36fe07e`, `faf1121c`, and `ff86cd34` の 26 行になった。

- row `2e9b1b9d` も same regime で追加回収できた。
  - `+ = x+y` の 1-family hit が examples と target を通して full map を一意に固定し、`!->2, "->3, $->5, )->4, :->8, <->6, >->1, ?->0, @->7, [->9` が直ちに得られた。
  - その map で 2 本の `*` rows を decode すると product digits は `3069`, `3724` になり、position-wise closure から shortest tuple `pos0 = p0`, `pos1 = p1`, `pos2 = prod_mod:03`, `pos3 = 9-p3` が得られた。
  - default solver でも `{'*': 'prod_tuple|p0|p1|prod_mod03|9-p3', '+': 'x+y'}` を返し、decoded row は `33*93 -> 3070`, `79*52 -> 3705`, target `41+32 -> 64` になる。

- row `693432da` も same regime で追加回収できた。
  - non-`*` side は `+ = x+y` と `- = rdiff:ac_bd` の merge で full map `'$'->5, '('->8, '-'->0, '>'->7, '?'->9, '['->2, '\\'->3, '^'->4, '{'->6, '|'->1` まで落ちた。
  - その map から 2 本の `*` rows の product digits は `3627`, `6525` に固定され、position-wise closure で tuple `pos0 = absdiff(max:01, p3)`, `pos1 = absdiff(9-p2, min:12)`, `pos2 = 9-absdiff:13`, `pos3 = p3` が見つかった。
  - default solver でも `{'*': 'prod_tuple|absdiff(max01,p3)|absdiff(9-p2,min12)|9-(absdiff13)|p3', '+': 'x+y', '-': 'rdiff:ac_bd'}` を返し、decoded row は `49*29 -> 3511`, `83*57 -> 6125`, `25-29 -> 01`, target `98+74 -> 172` になる。

- row `f36fe07e` も same regime で追加回収できた。
  - mergeable non-`*` side を row-local に全列挙すると、full-map survivor は 3 本まで落ち、その中で one-step star closure が通る map は `!->7, "->0, %->2, &->4, :->6, >->8, ?->1, \\->5, ]->9, }->3` だった。
  - 2 本の `*` rows の product digits は `5915`, `8624` に固定され、そこから tuple `pos0 = 9-max:23`, `pos1 = prod_mod:12`, `pos2 = max:03`, `pos3 = p2` が shortest で閉じた。
  - default solver での compatible assignment は `{'*': 'prod_tuple|9-(max23)|prod_mod12|max03|p2', '+': 'x+y', '-': 'y%x'}` で、decoded row は `70*57 -> 0643`, `14*67 -> 1724`, target `81+22 -> 103` になる。

- row `9f1ff166` も same regime で追加回収できた。
  - target `-` を含む `- = abs(x-y)` の reduced maps 8 本を点検すると、full-map survivor は `"->3, #->8, '->2, /->9, >->1, ?->7, [->5, ]->4, }->0` だった。
  - その map から 2 本の `*` rows の product digits を固定すると、position-wise closure で tuple `pos0 = prod_mod(min:12, p1)`, `pos1 = absdiff(9-p2, min:12)`, `pos2 = sum_mod(9-p2, p1)`, `pos3 = min(9-p2, p1)` が得られた。
  - default solver では `{'*': 'prod_tuple|prod_mod(min12,p1)|absdiff(9-p2,min12)|sum_mod(9-p2,p1)|min(9-p2,p1)', '-': 'abs(x-y)'}` を返す。

- row `93c9b36b` も same regime で追加回収できた。
  - non-`*` side は `+ = sum:ad_bc:strip0swap` と `- = x-y` の join が 1 本だけ残り、free symbol `-` を `0` で completion すると full map `)->3, }->8, %->9, >->1, ^->7, [->6, &->2, (->4, /->5, -->0` まで落ちた。
  - その map で 2 本の `*` rows の product digits を decode すると、新しい tuple `pos0 = absdiff(9-p0, p0)`, `pos1 = 9-absdiff:13`, `pos2 = 9-prod_tens:02`, `pos3 = absdiff(9-p0, sum_mod:03)` が shortest で閉じた。
  - default solver では `{'*': 'prod_tuple|absdiff(9-p0,p0)|9-(absdiff13)|9-(prod_tens02)|absdiff(9-p0,sum_mod03)', '-': 'x-y', '+': 'sum:ad_bc:strip0swap'}` を返す。

- row `7cb3089e` も same regime で追加回収できた。
  - non-`*` side を row-local に列挙すると、full-map survivor は `?->0, |->8, "->4, (->7, ^->5, $->6, %->1, !->3, }->9` の 1 本だけになった。
  - そこから 2 本の `*` rows を decode して position-wise closure を回すと、tuple `pos0 = max:01`, `pos1 = prod_mod:01`, `pos2 = sum_mod(9-absdiff:12, max:01)`, `pos3 = sum_carry(p2, p2)` が見つかった。
  - default solver では `{'*': 'prod_tuple|max01|prod_mod01|sum_mod(9-(absdiff12),max01)|sum_carry(p2,p2)', '+': 'x+y', '-': 'sum:ab_cd:strip0swap'}` を返す。

- row `faf1121c` も current solver 実装と ledger の間で未同期だっただけで、実際には same regime の solved row だった。
  - default solver は `{'*': 'prod_tuple|prod_mod(9-(prod_mod02),9-p3)|prod_mod(9-(max12),9-p0)|sum_mod(9-(prod_tens12),prod_mod01)|sum_mod(p1,p1)', '+': 'sum:ac_bd:swap', '-': 'x*y'}` を返す。
  - recovered digit map は `"->0, %->1, (->2, )->3, -->4, @->5, [->6, \->7, `->8, }->9` で、decoded row は `32*51 -> 3096`, `29*16 -> 0230`, `25+23 -> 15`, target `03+56 -> 336` になる。

- row `083ed8fe` も新しい low-free anchor として追加回収できた。
  - `-` side の current survivors を row-local に絞ると、`prod:ab_cd:strip0` など複数 family で non-operator symbols が `#`, `(`, `<` の 3 個まで落ちた。
  - その 3-free completion 全探索に 3 本の `*` rows を当てると、verified tuple `pos0 = max(9-sum_mod:02, prod_mod:03)`, `pos1 = absdiff(9-p0, sum_mod:02)`, `pos2 = 9-prod_tens(9-p3, p2)`, `pos3 = prod_mod(9-prod_tens:02, 9-p3)` が見つかった。
  - default solver では `{'*': 'prod_tuple|max(9-(sum_mod02),prod_mod03)|absdiff(9-p0,sum_mod02)|9-(prod_tens(9-p3,p2))|prod_mod(9-(prod_tens02),9-p3)', '-': 'prod:ab_cd:strip0'}` を返し、digit map は `!->0, "->1, #->2, &->3, (->4, )->5, /->6, :->7, <->8, [->9` になる。decoded row は `14*48 -> 8399`, `94*08 -> 0033`, `13-67 -> 5`, target `83*75 -> 9762` になる。

- row `053b4c86` もさらに cheap な 2-free anchor として追加回収できた。
  - default-priority だけで non-`*` side を絞ると、`+ = sum:ac_bd:swap` と `- = y-x` の merge で free symbols は `#`, `(` の 2 個まで落ちた。
  - その 2-free completion 全探索に 3 本の `*` rows を当てると、verified tuple `pos0 = prod_mod(9-p0, max:01)`, `pos1 = 9-sum_mod(9-p0, 9-p3)`, `pos2 = sum_mod(p1, prod_mod:13)`, `pos3 = min(9-prod_mod:13, p1)` が見つかった。
  - default solver では `{'*': 'prod_tuple|prod_mod(9-p0,max01)|9-(sum_mod(9-p0,9-p3))|sum_mod(p1,prod_mod13)|min(9-(prod_mod13),p1)', '-': 'y-x', '+': 'sum:ac_bd:swap'}` を返す。one explicit full solution は `$->6, %->2, "->5, \\->4, ]->1, &->3, @->9, ?->0, #->7, (->8` で、decoded row は `23*76 -> 6033`, `76*71 -> 0211`, `12-51 -> 39`, `62+54 -> 611`, target `89*13 -> 8981` になる。

- row `24750c4a` も default-compatible 2-free anchor として追加回収できた。
  - non-`*` side は `+ = drop_op` と `- = rdiff:ab_cd` の merge で free symbols `@`, `|` の 2 個まで落ちた。
  - その bounded completion search に 3 本の `*` rows を当てると、verified tuple `pos0 = prod_mod(9-absdiff:01, 9-p3)`, `pos1 = prod_tens(p3, p3)`, `pos2 = sum_mod(9-prod_mod:23, p1)`, `pos3 = absdiff(9-p1, min:02)` が見つかった。
  - default solver では `{'*': 'prod_tuple|prod_mod(9-(absdiff01),9-p3)|prod_tens(p3,p3)|sum_mod(9-(prod_mod23),p1)|absdiff(9-p1,min02)', '+': 'drop_op', '-': 'rdiff:ab_cd'}` を返す。one explicit full solution は `/->3, {->1, <->7, )->2, }->4, &->9, ?->8, #->6, @->0, |->5` で、decoded row は `95*63 -> 0285`, `85*90 -> 3021`, `93-41 -> 14`, `89+87 -> 89`, target `53*98 -> 8231` になる。

- row `ff86cd34` も new low-free target-`*` anchor として追加回収できた。
  - non-`*` side は `+ = sum:ac_bd` と `- = reverse_right` の join で 9 survivor まで落ち、その各 survivor は free symbols `>`, `^` の 2 個しか残さなかった。
  - その 2-free completion と `*` examples / target の product digits を shallow + depth1 basis で閉じると、verified tuple `pos0 = min:02`, `pos1 = prod_mod(absdiff:13, max:02)`, `pos2 = p3`, `pos3 = max(p3, 9-p3)` が見つかった。
  - default solver では `{'*': 'prod_tuple|min02|prod_mod(absdiff13,max02)|p3|max(p3,9-p3)', '+': 'sum:ac_bd', '-': 'reverse_right'}` を返す。one explicit full solution は `&->7, '->2, (->9, )->1, [->8, ]->0, ^->6, |->4, }->3, >->5` で、decoded row は `32+87 -> 119`, `04+33 -> 37`, `55-93 -> 39`, `29*01 -> 0899`, `66*02 -> 0327`, target `79*61 -> 1499` になる。

- row `24b2d8eb` も low-free target-`*` anchor として current coverage に昇格できた。
  - row-local に見ると、`+` side は composite family `concat|x+y|nat|y//x|nat|keep` の 3 survivor だけが残り、各 survivor は free symbols `(`, `|` の 2 個しか残さなかった。
  - その 2-free completion と `*` example / target の product digits を shallow + depth1 basis で閉じると、verified tuple `pos0 = absdiff:01`, `pos1 = prod_mod(9-p0, absdiff:03)`, `pos2 = 9-prod_tens:13`, `pos3 = sum_carry:01` が見つかった。
  - ただし tuple 追加だけでは default solver に乗らず、原因は non-`*` seed family が composite-only list にいたことだった。`concat|x+y|nat|y//x|nat|keep` を default priority に昇格すると、default solver は `{'+': 'concat|x+y|nat|y//x|nat|keep', '*': 'prod_tuple|absdiff01|prod_mod(9-p0,absdiff03)|9-(prod_tens13)|sum_carry01'}` を返す。
  - one explicit full solution は `!->9, "->8, '->4, (->1, /->5, :->7, [->6, `->0, |->3` で、decoded row は `46+44 -> 900`, `77+08 -> 850`, `36*31 -> 0090`, target `09*56 -> 5670` になる。

- row `0d4b2baa` は cheap low-free frontier 候補ではなく、current default solver の既解行だと確認できた。
  - default solver は `{'*': 'drop_op', '-': 'prod:ac_bd:strip0swap'}` を返し、追加の tuple search は不要だった。
  - したがってこの row も frontier から外し、以後は新規 anchor 候補として再訪しない。

- row `39a1f5e9` も cheap probe では未解決候補に見えたが、実際には current default solver の既解行だった。
  - default solver は `{'*': 'swap_halves', '+': 'prod:ad_bc'}` を返し、`*` side に追加 family は要らなかった。
  - したがってこの row も frontier script の stale candidate として扱い、再訪対象から外す。

- row `19968602` も single non-`*` operator slice の new current coverage として追加回収できた。
  - `+` side を default priority だけで絞ると、`sum:ab_cd:strip0swap` の survivors から free symbols `!`, `&`, `)` の 3 個まで落ちる。
  - その 3-free completion と `*` example / target の product digits を shallow + depth1 basis で閉じると、verified tuple `pos0 = sum_carry:13`, `pos1 = 9-p0`, `pos2 = sum_mod(p0, absdiff:13)`, `pos3 = 9-sum_mod:02` が見つかった。
  - default solver では `{'+': 'sum:ab_cd:strip0swap', '*': 'prod_tuple|sum_carry13|9-p0|sum_mod(p0,absdiff13)|9-(sum_mod02)'}` を返す。one explicit full solution は `[->2, `->0, ?->6, ^->5, "->1, |->4, /->3, !->7, &->9, )->8` で、decoded `*` rows は `34*58 -> 1881`, target `93*23 -> 1704` になる。

- row `02a04b59` も cheap anchor ではなく current default solver の既解行だった。
  - default solver は `{'*': 'drop_op', '+': 'sum:ac_bd:strip0swap'}` を返し、追加 family 探索は不要だった。
  - したがってこの row も stale frontier candidate として扱い、再訪対象から外す。

- row `1342687b` も current coverage に追加回収できた。
  - `+` side を default priority だけで絞ると、`x+y` の survivors から free symbols `#`, `)`, `/`, `:` の 4 個まで落ちる。
  - その 4-free completion と `*` example / target の product digits を shallow + depth1 basis で閉じると、verified tuple `pos0 = 9-sum_mod:03`, `pos1 = 9-min:13`, `pos2 = sum_mod(prod_mod:01, absdiff:23)`, `pos3 = prod_tens:23` が見つかった。
  - default solver では `{'+': 'x+y', '*': 'prod_tuple|9-(sum_mod03)|9-(min13)|sum_mod(prod_mod01,absdiff23)|prod_tens23'}` を返す。one explicit full solution は `@->1, (->2, <->3, ]->4, !->5, %->8, #->0, )->6, /->7, :->9` で、decoded `*` rows は `32*46 -> 6791`, target `83*02 -> 3803` になる。

- row `75c8715e` も low-free target-`*` anchor として current coverage に追加回収できた。
  - non-`*` side は `- = sum:ac_bd:strip0swap` の seed だけで free symbols `)`, `` ` `` の 2 個まで落ち、direct `-`/`*` join は 0 だったので bounded continuation を掛けた。
  - その 2-free completion と `*` example / target の product digits `1020`, `2838` を shallow + depth1 basis で閉じると、verified tuple `pos0 = sum_mod(p1, sum_mod:12)`, `pos1 = sum_mod(sum_mod:01, sum_mod:02)`, `pos2 = 9-absdiff:02`, `pos3 = sum_carry:02` が見つかった。
  - default solver では `{'-': 'sum:ac_bd:strip0swap', '*': 'prod_tuple|sum_mod(p1,sum_mod12)|sum_mod(sum_mod01,sum_mod02)|9-(absdiff02)|sum_carry02'}` を返す。one explicit full solution は `[->2, >->4, $->8, #->3, -->7, /->1, \\->6, ^->5, )->0, `->9` で、decoded `*` rows は `20*51 -> 2480`, target `66*43 -> 9580` になる。

- row `8395d060` も low-free target-`*` anchor として current coverage に追加回収できた。
  - non-`*` side は composite family `concat|x-y|nat|x//y|nat|strip0` の survivors で free symbols `&`, `:`, `?` の 3 個まで落ち、既存 `*` tuple との direct target join は無かったので row-local continuation を掛けた。
  - その 3-free completion と `*` example / target の product digits `4644`, `4524` を shallow + depth1 basis で閉じると、verified tuple `pos0 = sum_mod:03`, `pos1 = sum_mod(p0, sum_mod:01)`, `pos2 = sum_mod(p1, sum_mod:01)`, `pos3 = sum_mod(sum_mod:12, prod_tens:01)` が見つかった。
  - ただし tuple 追加だけでは default solver に乗らず、原因は non-`*` seed family が composite-only list にいたことだった。`concat|x-y|nat|x//y|nat|strip0` を default priority に昇格すると、default solver は `{'*': 'prod_tuple|sum_mod03|sum_mod(p0,sum_mod01)|sum_mod(p1,sum_mod01)|sum_mod(sum_mod12,prod_tens01)', '-': 'concat|x-y|nat|x//y|nat|strip0'}` を返す。
  - one explicit full solution は `$->0, (->1, |->2, @->4, '->3, /->5, !->9, &->6, :->7, ?->8` で、decoded `*` rows は `54*86 -> 8462`, target `87*52 -> 8349` に一致する。

- row `7137d73a` は low-free に見えたが、current family set では open negative だった。
  - `+ = x*y` の one-map seed を取ると free symbol は `]` 1 個まで縮み、`]=3` の completionで `*` rows は `0064 -> 0977`, `4600 -> 348`, target `2496 -> 872` に落ちる。
  - そこから mixed-length fixed-drop continuation を掛けると drop index `2` の family `prod_tuple_drop2|absdiff(prod_mod01,sum_carry01)|max(9-p1,absdiff02)|9-(absdiff23)|sum_mod(9-(sum_carry23),9-(sum_mod23))` が row を閉じる。
  - default solver でも `{'*': 'prod_tuple_drop2|absdiff(prod_mod01,sum_carry01)|max(9-p1,absdiff02)|9-(absdiff23)|sum_mod(9-(sum_carry23),9-(sum_mod23))', '+': 'x*y'}` を返すことを確認した。

- row `97d6db7a` も stale frontier candidate で、現 default solver では既解だった。
  - default solver は `{'*': 'drop_op', '+': 'sum:ad_bc:strip0'}` を返す。
  - したがってこの row も再訪対象から外す。

- row `23b0eb54` も stale frontier candidate で、現 default solver では既解だった。
  - default solver は `{'*': 'drop_op', '-': 'sum:ac_bd:strip0'}` を返す。
  - したがってこの row も frontier script の取りこぼし補正として再訪対象から外す。

- row `9fc69c17` も stale frontier candidate で、現 default solver では既解だった。
  - default solver は `{'*': 'drop_op', '-': 'y-x'}` を返す。
  - したがってこの row も frontier script の取りこぼし補正として再訪対象から外す。

- row `65add53a` は open note から fixed-drop positive に反転した。
  - non-`*` side は `+ = sum:ac_bd` の 1-map seed で free count `4` まで落ち、未確定 completion は `! = 0`, `\\ = 4`, `^ = 5` の 1 通りが current target answer と両立した。
  - verified transform は `prod_tuple_drop0|9-p2|sum_mod(min23,p3)|prod_tens13|sum_mod(9-p2,9-p3)` で、decoded `*` row `3192 -> 0407` と target `0425 -> 721` を同時に閉じる。
  - default solver でも `{'+': 'sum:ac_bd', '*': 'prod_tuple_drop0|9-p2|sum_mod(min23,p3)|prod_tens13|sum_mod(9-p2,9-p3)'}` を返すことを確認した。

- row `ae3d84e7` は open note から positive に反転した。
  - `*` side は plain `x*y` で unique map に落ち、target `*` も同じ family で join すると full map `@=7, >=4, <=8, &=6, ?=3, \`=1, %=5, ^=0, ]=2` まで確定する。
  - numeric / generic / scalar-concat では `+` family は見つからなかったが、parser-supported `copymix` を 1 hop 広げると `copymix|generic|absdiff:ac_bd|plain|a|expr_first` が `65+72 -> 136` を与え、full map とも矛盾しない。
  - default solver でも `{'*': 'x*y', '+': 'copymix|generic|absdiff:ac_bd|plain|a|expr_first'}` を返すことを確認した。

- row `06083e68` は 3-char target-`*` branch の mixed open note に回した。
  - `+ = x//y` と target-`*` family `prod_tuple_drop3|prod_mod(p2,min02)|sum_mod(sum_mod13,absdiff01)|absdiff01|sum_mod12` を合わせると partial map `48+03 -> 16`, `87*14 -> 111`, `30-43 -> -<` まで固定される。
  - plain numeric `op_prefix/op_suffix` を広げても `-` side は閉じなかったが、parser-supported `mask` を狭く再探索すると `mask|generic|prod:ad_bc:strip0|plain|oN` が minus example `30-43 -> -9` を与え、そのまま partial map と join した。
  - default solver でも `{'*': 'prod_tuple_drop3|prod_mod(p2,min02)|sum_mod(sum_mod13,absdiff01)|absdiff01|sum_mod12', '-': 'mask|generic|prod:ad_bc:strip0|plain|oN', '+': 'x//y'}` を返すことを確認した。

- row `7a17137f` は shallow continuation では一度 open note に回ったが、その後の second-order fixed-drop continuation で回収できた。
  - non-`*` side は `+ = sum:ac_bd`, `- = diff:ac_bd:strip0` で free count `2` まで落ち、未確定 digit completion は `& = 6`, `' = 8` の 1 通りだけが `*`/target 両方と整合した。
  - verified transform は `prod_tuple_drop0|sum_mod(prod_mod23,prod_mod23)|9-(prod_mod23)|prod_mod(sum_mod23,9-p0)|sum_mod23` で、decoded `*` row `08*79 -> 4631` と target `03*17 -> 446` を同時に閉じる。
  - default solver でも `{'+': 'sum:ac_bd', '-': 'diff:ac_bd:strip0', '*': 'prod_tuple_drop0|sum_mod(prod_mod23,prod_mod23)|9-(prod_mod23)|prod_mod(sum_mod23,9-p0)|sum_mod23'}` を返すことを確認した。

- row `1a28140b` は 3-char target-`*` frontier の positive として回収できた。
  - non-`*` side を merge すると `+ = x+y`, `- = x//y` が free symbols `['/', '?']` の clean seed を与え、`*` example `21*96 -> 8061` と target `30*40 -> 592` に対して bounded continuation が通った。
  - verified transform は target-only fixed drop を持つ `prod_tuple_drop3|9-p2|9-p1|9-(sum_mod02)|p2` で、4-char tuple `5924` から index `3` を落とすと target answer `592` になる。
  - これを一般 family class として `analyze_symbol_rules.py` に実装し、default solver でも `{'*': 'prod_tuple_drop3|9-p2|9-p1|9-(sum_mod02)|p2', '+': 'x+y', '-': 'x//y'}` を返すことを確認した。

- row `a692ec38` も同じ `prod_tuple_drop3` class の positive として回収できた。
  - non-`*` side は `+ = sum:ac_bd:strip0swap` だけで free count `4` まで落ち、star-side mixed-length rows `(4,3,3)` に対して full 4-char tuple と target/example drop の両立を探索した。
  - verified transform は `prod_tuple_drop3|prod_mod(p2,min02)|sum_mod(sum_mod13,absdiff01)|absdiff01|sum_mod12` で、decoded outputs は `0212`, `1238`, `6435` になり、drop index `3` により second `*` example と target がそれぞれ `123`, `643` に落ちる。
  - default solver でも `{'*': 'prod_tuple_drop3|prod_mod(p2,min02)|sum_mod(sum_mod13,absdiff01)|absdiff01|sum_mod12', '+': 'sum:ac_bd:strip0swap'}` を返すことを確認した。

- row `c7aae192` は fixed-drop class の別 variantとして回収できた。
  - non-`*` side は `+` と `-` を merge すると free count `2` まで落ち、actual default assignment は `+ = diff:ac_bd`, `- = x-y` になった。
  - bounded continuation では target-only drop ではなく `drop1` が効き、verified transform `prod_tuple_drop1|absdiff01|sum_mod(9-p0,p1)|sum_mod(sum_mod01,sum_mod03)|prod_tens(9-p1,9-p2)` が `*` example `2126` と target `530` を同時に閉じた。
  - default solver でも `{'*': 'prod_tuple_drop1|absdiff01|sum_mod(9-p0,p1)|sum_mod(sum_mod01,sum_mod03)|prod_tens(9-p1,9-p2)', '-': 'x-y', '+': 'diff:ac_bd'}` を返すことを確認した。

- row `edf364da` も same frontier の fixed-drop positive だった。
  - non-`*` side は `+ = x+y` で free count `2` まで落ち、single `*` example `1235` と target `840` に対して target-only fixed-drop continuation を掛けると row-consistent tuple が見つかった。
  - verified transform は `prod_tuple_drop0|sum_carry03|sum_mod(p2,prod_tens03)|sum_mod(9-p2,9-p3)|p0` で、target full tuple `0840` から先頭桁を落とすと answer `840` になる。
  - default solver でも `{'*': 'prod_tuple_drop0|sum_carry03|sum_mod(p2,prod_tens03)|sum_mod(9-p2,9-p3)|p0', '+': 'x+y'}` を返すことを確認した。

- row `b0206bb7` も fixed-drop class で回収できた。
  - 最初の `drop0` hit は `*` example を 1 本しか満たしておらず false positive だった。row には `*` example が 2 本あるため、valid family は `1775 -> 1459` と `4361 -> 2646` を同時に閉じる必要があった。
  - non-`*` side は `- = x-y` と `+ = x-y / abs(x-y) / x%y` の同一 merged map で free count `1` まで落ち、残り digit は target-only symbol `$` に自動で割り当たる。
  - verified transform は `prod_tuple_drop0|sum_mod(p2,sum_mod02)|prod_mod(9-p2,prod_tens02)|p3|sum_mod(prod_mod12,prod_tens12)` で、decoded `*` rows `1775 -> 1459`, `4361 -> 2646`, target `1632 -> 029` を同時に満たす。
  - default solver でも `{'*': 'prod_tuple_drop0|sum_mod(p2,sum_mod02)|prod_mod(9-p2,prod_tens02)|p3|sum_mod(prod_mod12,prod_tens12)', '-': 'x-y', '+': 'x%y'}` を返すことを確認した。

- ここまでで target-`*` 3-char fixed-drop family は `drop0`, `drop1`, `drop2`, `drop3` の全 4 index で positive が出た。さらに `drop0` には `edf364da` の target-only/single-example 型、`b0206bb7` の two-`*`-example 型、`7a17137f` の second-order single-`*`-example 型、`65add53a` の one-`+`-seed 型が揃った。したがってこれは単発 row trick ではなく、current frontier の実 family class とみなしてよい。

- row `7db0f3ee` は fixed-drop ではなく plain 3-digit product family の first positive だった。
  - non-`*` side は `+ = x+y` だけで free count `1` まで落ち、残り 1 digit completionに対して star rows `399` と target `459` を同時に通す 3-position product-digit tuple を探索した。
  - verified transform は `prod_triplet|sum_mod(9-p1,prod_mod03)|9-p0|9-(sum_carry01)` で、decoded `*` rows は `0608 -> 399` と `4332 -> 459` に一致した。
  - これに合わせて `prod_triplet|expr0|expr1|expr2` class を solver に実装し、default solver でも `{'+' : 'x+y', '*' : 'prod_triplet|sum_mod(9-p1,prod_mod03)|9-p0|9-(sum_carry01)'}` を返すことを確認した。

- row `b06625c4` も same-length `prod_triplet` class で回収できた。
  - non-`*` side は `+` / `-` merge で free count `1` に落ち、actual default assignment は `+ = x-y`, `- = abs(x-y)` になった。
  - verified transform は `prod_triplet|sum_mod(p0,max12)|sum_mod(9-p3,absdiff02)|sum_mod(9-p0,9-p0)` で、decoded rows `3344 -> 762` と `2905 -> 164` に一致した。
  - default solver でも `{'*': 'prod_triplet|sum_mod(p0,max12)|sum_mod(9-p3,absdiff02)|sum_mod(9-p0,9-p0)', '-': 'abs(x-y)', '+': 'x-y'}` を返すことを確認した。

- したがって same-length 3-char target-`*` には fixed-drop と別に `prod_triplet` という second family class がある。現時点で `7db0f3ee` と `b06625c4` の 2 行で positive を確認した。

- row `de036bbf` も same-length `prod_triplet` class で回収できた。
  - non-`*` side は `+` / `-` merge で free count `1` に落ち、actual default assignment は `+ = x+y`, `- = y-x` になった。
  - verified transform は `prod_triplet|sum_mod(p3,sum_mod13)|sum_mod02|sum_mod(9-p3,sum_mod01)` で、decoded rows `1134 -> 947` と `0220 -> 221` に一致した。
  - default solver でも `{'-': 'y-x', '+': 'x+y', '*': 'prod_triplet|sum_mod(p3,sum_mod13)|sum_mod02|sum_mod(9-p3,sum_mod01)'}` を返すことを確認した。

- これで `(3,) -> 3` の target-`*` slice には `7db0f3ee`, `b06625c4`, `de036bbf` の 3 positive が出た。same-length 3-digit product family は単発ではなく、現在の frontier で再利用可能な class になった。

- row `194695e8` は stronger negative / open branch として固定した。
  - `*` side は current plain family `x*y` だけで 1-map に落ちるが、その star-map と両立する target-compatible `-` family は現 library に 1 件も無かった。
  - 実際には `-` side の examples と target answer から複数の full survivor map を作れても、star-map との join count は常に `0` だった。
  - したがってこの row は「`*` family を増やせば足りる」型ではなく、少なくとも current `-` family basis の外に missing class が残っている。

- row `208d7838` も current family set では negative 側に倒れた。
  - `*` side には row-local tuple `prod_tuple|absdiff(max01,p3)|absdiff(9-p2,min12)|9-(absdiff13)|p3` の 1-hit map がある。
  - しかし non-`*` side を default priority で詰めると、`-` 側で target-compatible に残るのは `concat|x*y|nat|y//x|nat|strip0` の 1 family だけで、`+` side survivors と join した時点で merged maps は `0` 件になった。
  - よってこの row も「star tuple は見えているが current non-`*` library に end-to-end の接続が無い」open negative と扱う。

- row `3424f037` も cheap positive ではなく verified negative に回した。
  - `*` examples は plain `x*y` で 1-map に落ちる一方、`+` / `-` side は join 後でも 7 survivor まで縮む。
  - ただしその 7 survivor を star-map に照合すると join hit は `0 / 7` で、non-`*` side の最小 2-free seeds もすべて `* = x*y` と矛盾した。
  - したがってこの row も bounded completion を足す段階ではなく、current family basis の不一致として一旦閉じる。

- row `564916b5` は現時点では positive frontier ではなく、verified negative / open branch として固定した。
  - `*` side 自体は current `b1b10e83` 系 tuple `min(9-p1,p1) / 9-(sum_mod(9-p1,9-p1)) / prod_tens(9-p2,sum_mod(9-p1,9-p1)) / prod_tens(9-p1,max(9-p1,p1))` で 1-map に落ち、`{"->2, {->3, <->5, !->4, $->1, `->0}` まで固定される。
  - しかし `-` side の current survivor families `abs(x-y)`, `x%y`, `y%x`, `y//x` を examples と target の両方で検査しても、star-map との join は examples 側でも target 側でも 0 件だった。
  - したがって、この row は「star-only structure は既知 family に乗るが、current non-`*` family library とは end-to-end に接続しない」ケースとして扱い、次の low-cost anchor を優先する。

- row `042f1e53` は cheap frontier 再点検の結果、未解決候補ではなく current default solver の既解行だと確認できた。
  - default solver は `{'*': 'drop_op', '+': 'sum:ac_bd', '-': 'x-y'}` を返し、composite を広げなくても行全体が閉じる。
  - したがって、この row は新規 family 探索の対象から外し、「frontier script の取りこぼし補正」扱いにする。

- row `0d90736f` は現 family library では open negative 寄りだった。
  - non-`*` side は `+` target を通しても `prod:ab_cd:strip0` / `prod:cd_ab:strip0swap` までしか残らず、そこから `-` side を join すると merged non-`*` maps は 0 件になった。
  - さらに `*` examples 側には current small-hit family が 0 件で、row-local bounded search を始める前段の足場がまだない。