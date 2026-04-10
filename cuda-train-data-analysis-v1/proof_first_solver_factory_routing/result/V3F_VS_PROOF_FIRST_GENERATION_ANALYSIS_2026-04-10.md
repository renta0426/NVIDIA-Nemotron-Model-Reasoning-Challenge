# v3f vs Proof-First Solver Factory Routing 生成文分析 2026-04-10

## 1. 目的

`baseline/nemotron-sft-lora-with-cot-v2/result/v3f` と `cuda-train-data-analysis-v1/proof_first_solver_factory_routing/result` の差を、単なる score 比較ではなく、**生成された本文の構造と失敗様式**まで含めて精密に比較する。

分析の基準は `README.md` の Evaluation 契約に置く。

1. 評価対象は最終 answer の Accuracy
2. `\boxed{}` 抽出が最優先
3. `temperature=0.0`, `max_tokens=7680`, `max_model_len=8192`

したがって本分析で見るべきものは、

1. `\boxed{}` を出しているかどうか
2. その前にどのような reasoning scaffold を置いているか
3. scaffold が正答率を押し上げているのか、逆に誤答を固定しているのか

である。

## 2. スコアの整理

### 2.1 broad local と hidden-proxy は別の振る舞いをしている

既存再監査の corrected 値と、今回 raw output を伴う leaderboard proxy rerun を合わせると、差は次の通りである。

| benchmark | v3f | proof-first current | 所見 |
| --- | ---: | ---: | --- |
| corrected Phase0 local320 | `240/320 = 0.7500` | `241/320 = 0.7531` | broad local では実質同点 |
| specialized563 | `238/563 = 0.4227` | `234/563 = 0.4156` | 小差 |
| leaderboard proxy rerun 200 | `133/200 = 0.6650` | `98/200 = 0.4900` | hard slice で大差 |

この時点で、proof-first current の崩壊は「全体的に弱い」のではなく、**proxy/hard slice でだけ急激に悪化する run** と読むのが正しい。

### 2.2 proxy の負け方は明確に偏っている

proxy 200 問での row-level 実測は次の通りだった。

| role | rows |
| --- | ---: |
| `v3f_only` | `40` |
| `current_only` | `5` |
| `both_correct` | `93` |
| `both_wrong` | `62` |

`v3f_only 40` の内訳は以下だった。

| family | rows |
| --- | ---: |
| `binary` | `21` |
| `text` | `13` |
| `symbol` | `6` |

つまり今回の差は、**binary が主因、次に text、その次に symbol** で説明される。

## 3. 生成文の全体構造比較

## 3.1 Phase0 local320 では文体差はほぼ無い

Phase0 row-level の raw output を集計すると、両者は broad local ではほぼ同じ文章スタイルだった。

| metric | v3f phase0 | current phase0 |
| --- | ---: | ---: |
| mean raw chars | `3141.1` | `3114.3` |
| median raw chars | `1253.5` | `1245.5` |
| mean lines | `98.38` | `100.82` |
| route rate | `0.0` | `0.0` |
| so-rule rate | `0.1187` | `0.1062` |
| constraints rate | `0.0` | `0.0` |

重要なのは、**Phase0 では proof-first current も route 文体へはまだ全面移行していない**ことだ。したがって local320 で差が見えないのは自然である。

加えて、両者とも wrong rows は extremely long になっていた。

| split | v3f mean chars | current mean chars |
| --- | ---: | ---: |
| correct | `1662.1` | `1666.9` |
| wrong | `8328.0` | `8379.3` |

これは broad local では、両者とも主な failure mode が **長い思考の drift** 側にあったことを示す。

## 3.2 proxy では current だけが route scaffold に大きく固定される

proxy 200 問では景色が一変する。

| metric | v3f proxy | current proxy |
| --- | ---: | ---: |
| accuracy | `0.6650` | `0.4900` |
| mean raw chars | `2301.4` | `919.0` |
| median raw chars | `274.0` | `369.0` |
| mean lines | `67.18` | `34.38` |
| route rate | `0.0` | `0.8000` |
| route granularity rate | `0.0` | `0.8000` |
| check-examples rate | `0.0550` | `0.8000` |
| so-rule rate | `0.0800` | `0.5850` |
| constraints rate | `0.0` | `0.5450` |

opening も完全に別物である。

| opening | v3f proxy | current proxy |
| --- | ---: | ---: |
| `Route:` 開始 | `0/200` | `160/200` |
| その他 | `199/200` | `39/200` |

この差は単なる短文化ではない。**思考の入り口そのものが変わっている。**

v3f は proxy でも基本的に従来型の自然文 reasoning を保ち、必要な時だけ局所的に short verified-rule phrasing を使う。

proof-first current は逆に、

1. `Route:`
2. `Route granularity:`
3. `Check ex1/ex2` または `Check examples`
4. `So the rule is`
5. `Constraints:`

という **固定 scaffold** を前面に出す。

## 3.3 specialized563 では文体差がさらに極端になる

binary specialized row-level は、両 run の文章設計差を最も純粋に見せる。

| metric | v3f specialized | current specialized |
| --- | ---: | ---: |
| accuracy | `0.4227` | `0.4156` |
| mean raw chars | `258.6` | `369.0` |
| mean lines | `3` | `9` |
| route rate | `0.0` | `1.0` |
| check-examples rate | `0.0` | `1.0` |
| so-rule rate | `0.0` | `1.0` |
| constraints rate | `0.0` | `1.0` |

ここで重要なのは、**short answer 自体が悪いわけではない**ということだ。

v3f specialized は 3 行・258 文字の非常に短い commit で current を僅差ながら上回っている。

したがって、proof-first current の問題は「短くなりすぎた」ことではなく、**route-aware scaffold を強く固定しすぎ、その scaffold が正答率を押し上げるより先に誤答を固定している**ことにある。

## 4. 正答と誤答で生成文がどう違うか

## 4.1 v3f proxy の失敗は主に long drift

v3f proxy では wrong rows が correct rows より大きく長い。

| split | mean chars | mean lines | so-rule rate |
| --- | ---: | ---: | ---: |
| correct | `1467.7` | `65.75` | `0.0977` |
| wrong | `3956.3` | `70.01` | `0.0448` |

つまり v3f の failure mode は、**早い commit ではなく、長い自然文推論がそのまま漂流する型**である。

## 4.2 current proxy の失敗は route saturation と一緒に増える

current proxy では逆の傾向が出た。

| split | mean chars | mean lines | route rate | so-rule rate | constraints rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| correct | `609.9` | `35.99` | `0.6020` | `0.3673` | `0.2857` |
| wrong | `1215.9` | `32.84` | `0.9902` | `0.7941` | `0.7941` |

ここで重要なのは、wrong rows が correct rows より

1. `Route:` をほぼ必ず出し
2. `So the rule is` を強く出し
3. `Constraints:` まで高率で出している

ことである。

これは、proof-first current の proxy failure が **推論が足りないからではなく、誤った route と rule を早く固定しすぎている**ことを意味する。

言い換えると、current では scaffold が reasoning の補助ではなく、**誤答の固定具**になっている。

## 5. family ごとの本文 failure mode

## 5.1 binary: 正誤で文体がほぼ同一、つまり問題は route 内容そのもの

current proxy の binary 92 問では、correct と wrong の文章形が完全に同型だった。

| split | rows | mean chars | route rate | so-rule rate | constraints rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| correct | `22` | `369.0` | `1.0` | `1.0` | `1.0` |
| wrong | `70` | `369.0` | `1.0` | `1.0` | `1.0` |

これはかなり強い signal である。binary では、proof-first current は **正解時も誤答時もまったく同じ 9 行テンプレート**を出しており、文章構造自体は正誤を全く選別していない。

したがって binary 崩壊の本体は、

1. route を出したこと
2. constraints を書いたこと

ではなく、**その route と rule の中身が間違っているのに、常に exact として commit してしまう**ことにある。

### 代表例 1: affine_xor 系を structured_byte_formula_abstract に誤ロック

`id=1e677e2c`

- gold: `10001101`
- v3f: `The verified rule is or(ror3,shr5)` と具体 rule を置いて `\boxed{10001101}`
- current: `Route: bit_manipulation.binary_structured_byte_formula_abstract` と誤 route し、`So the rule is choose(shl1,shr2,ror3)` と exact claim して `\boxed{00111101}`

### 代表例 2: bit_other でも同じ誤ロックを反復

`id=3feeabea`

- gold: `10010010`
- v3f: `xor(shl4,shr6)` と局所的 verified rule を出して正解
- current: 再び `binary_structured_byte_formula_abstract` に寄せて `choose(shl2,shr5,rol3)` を宣言し誤答

この 2 例が示すのは、proof-first current の binary 弱点が「計算が少しずれた」ではなく、**route-aware exact teacher の見た目を維持したまま、wrong solver family に lock している**ことだ。

## 5.2 text: dictionary commit が早すぎて global mapping を捨てている

proxy 20 問の text は、v3f `17/20` に対して current `5/20` と激減した。

current text の正誤別比較は次の通り。

| split | rows | mean chars | route rate | so-rule rate | constraints rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| correct | `5` | `1114.6` | `1.0` | `0.0` | `0.0` |
| wrong | `15` | `563.4` | `1.0` | `0.0667` | `0.1333` |

つまり text では、**誤答の方がむしろ短い**。これは current の text failure が「だらだら考えて崩れた」のではなく、**短い word-level commit で必要な mapping を作り切らずに確定している**ことを示す。

### 代表例 1: 単語辞書 commit が global mapping を外す

`id=03e2bedc`

- gold: `rabbit dreams in castle`
- v3f: 例から cipher-to-plain mapping を積み上げて正解
- current: `Route: word_mapping` で始め、`qjbdia -> garden` を早期確定して `rabbit dreams in garden`

### 代表例 2: 未確定語を辞書で強引に埋める

`id=46951896`

- gold: `mouse found under cave`
- v3f: character mapping を広く構築して正解
- current: `plkb` を `king` と単語パターン一致で埋め、`mouse found reads king`

これらは、proof-first current の text branch が **global substitution problem を local dictionary lookup に圧縮しすぎている**ことを示す。

## 5.3 symbol: 一部には効くが、悪い時は route の後に長い誤推論へ入る

proxy 32 問の symbol は、v3f `19/32` に対して current `15/32`。

current symbol の正誤別比較は次の通り。

| split | rows | mean chars | route rate | so-rule rate | constraints rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| correct | `15` | `960.8` | `0.9333` | `0.3333` | `0.2667` |
| wrong | `17` | `5278.5` | `0.9412` | `0.5882` | `0.5294` |

ここは binary と逆で、wrong rows がかなり長い。つまり symbol では、proof-first current は

1. route を宣言する
2. 部分的なパターンを掴む
3. しかし確信が持てないと、その後に長い誤推論へ流れる

という失敗形を持つ。

### 代表例 1: operator ごとの差を潰して concatenate に誤還元

`id=18268687`

- gold: `0`
- v3f: `*` と `'` の差を分離して、`75'75` を正しく `0` へ持っていく
- current: `the result is formed by concatenating the two numbers` に lock し `7575`

### 代表例 2: 途中で rule が破綻しているのに commit を続ける

`id=79f29eb5`

- gold: `2370`
- v3f: operator ごとの違いを粘って追い、正解
- current: `15$96 = 112` など一部例からルール候補を列挙するが、`55<61 = 3355` で破綻しても、そのまま route scaffold を維持して誤答へ進む

つまり symbol では、proof-first scaffold が短い exact lock として働くのではなく、**誤った provisional rule を長く正当化する枠**として働いている。

## 6. current に利点がある場面はどこか

proof-first current の長所が全く無いわけではない。proxy では `current_only = 5` 行あり、その内訳は

1. `binary 1`
2. `symbol 2`
3. `text 1`
4. `unit 1`

である。

代表例として `id=10dfe5c5` では、v3f が `01000000` を出した一方、current は route-aware binary templateで `10100000` を正しく返している。

しかし、この gain は局所的で、proxy 全体では `v3f_only 40` に対して `current_only 5` に留まる。したがって proof-first current の route-aware scaffolding は、**効く場所では効くが、効かない場所での過失の方が圧倒的に大きい**。

## 7. 最も重要な解釈

## 7.1 問題は「route 文体を出した」ことではなく「wrong route を exact として固定した」こと

この分析で一番重要なのはここである。

proof-first current の崩壊を、単純に

1. 長い文章が悪い
2. 短い文章が悪い
3. `Route:` 文字列が悪い

と読むのは間違いである。

正しい読みは次の通り。

1. Phase0 では両者の文体差はほぼ無い
2. specialized と proxy の hard slice でのみ current が route scaffold に固定される
3. binary ではその scaffold が正誤に関わらず同型で、**solver family の誤ロック**が直接誤答になる
4. text では global mapping を作る前に **word-level の局所 commit** をしてしまう
5. symbol では partial pattern を掴んだ後に **長い誤正当化**へ流れる

要するに proof-first current の失敗は、**reasoning scaffold が evidence accumulation の器ではなく premature commitment の器になっている**ことにある。

## 7.2 v3f の勝ち筋は「route-aware でないこと」ではなく「commit を必要な場所にだけ絞っていること」

v3f は specialized では非常に短く、それでも current より強い。したがって勝ち筋は long CoT でも no-route 主義でもない。

むしろ v3f の強みは、

1. binary では verified rule を具体関数名で局所的に置く
2. text では mapping を十分に構築する
3. symbol では operator 差を捨てずに追う
4. それでいて boxed close は守る

という **必要な場所でだけ commit を行う非一様性**にある。

proof-first current は逆に、その commit skeleton を family 横断で広く適用しすぎた結果、**hard slice で mislock を増幅した**と読むのが最も整合的である。

## 8. 最終結論

proof-first_solver_factory_routing の精度低下は、スコアだけでなく生成文を見ても、かなり一貫した failure mode を持っている。

1. broad local320 では v3f と current の生成文スタイル差はほぼ無く、スコアも実質同点
2. しかし proxy と specialized では current だけが `Route -> Check examples -> So the rule is -> Constraints -> boxed` の固定 scaffold へ強く寄る
3. proxy では current の wrong rows ほど route / so-rule / constraints が高率で、**誤答時にこそ route-aware scaffold が強く出ている**
4. binary では正誤で文章テンプレートが同一なので、問題は format ではなく **wrong solver family を exact として確定すること**
5. text では global char mapping を作る代わりに **短い辞書 commit** をし、castle/cave のような unseen 側を落とす
6. symbol では partial pattern を掴んだ後、route scaffold の上で **長い誤正当化**へ入りやすい
7. current に利点がある局所例はあるが、proxy では `current_only 5` に対して `v3f_only 40` であり、利得より誤ロックの損失が大きい

したがって今回の崩壊は、単なる data quality 低下や wording の違いではない。**proof-first の表面形式を強く学習した結果、route-aware scaffold が evidence を集める前に answer を固定する方向へ働き、hidden/proxy の hard slice で mislock を増幅した**と結論づけるのが最も妥当である。