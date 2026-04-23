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
  - wider scan で `2e9973b7` も example-side では `prod_digits|1785|carry01|max02` に hit したが、これは new coverage ではない。row 自体は既存 solver でも `{'*': 'x*y', '-': 'y-x', '+': 'drop_op'}` で既に solve 済みだった。
  - したがってこの wave の immediate value は「example-side hit row を増やすこと」ではなく、既存 solver が未解決だった `*`-heavy rows を実際に回収した点にある。現時点で confirmed new current coverage は `1785b35e`, `2fc5ef5b`, `64d775e5` の 3 行になった。
  - current symbolic rows のうち「`*` examples が 2 本で両方 4-char」の slice を再走査すると、この family の example-side hit row は `6` 件だった: `1785b35e`, `2e9973b7`, `2fc5ef5b`, `563bf8f9`, `64d775e5`, `a4e4ec1d`。
  - ただし row-level で見ると、`2e9973b7` は既存 solver で既に解ける redundant hit、`563bf8f9` / `a4e4ec1d` は依然 unsolved のままで、new current coverage として確認できたのは `1785b35e`, `2fc5ef5b`, `64d775e5` の 3 行だった。