# v20 corrective corpus v7 mainline results

## Status

- Created: 2026-04-20 UTC
- Generator: `versions/v20_corrective_corpus_v7_mainline/reproduce_v20_corrective_corpus_v7_mainline.py`
- Strategy source: `versions/v20_to_088_reassessment_2026-04-18.md`
- Later token-stream audit: `versions/v20_corrective_corpus_v7_mainline/v20_corrective_corpus_v7_mainline-tokenstream-audit-2026-04-21.md`
- Later bundle-to-bundle audit: `versions/v20_corrective_corpus_v7_mainline/v20_corrective_corpus_v7_mainline-bundle-to-bundle-audit-2026-04-21.md`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v7_mainline_bundle.jsonl`
- Kaggle train log: `versions/v20_corrective_corpus_v7_mainline/adapter-validation-notebook.log`
- Comparison train log: `versions/v20_corrective_corpus_v4_mainline/adapter-validation-notebook (1).log`
- Training / validation / leaderboard score:
  - validation: `784 / 950 = 0.8253`
  - leaderboard proxy: `154 / 200 = 0.7700`
  - official leaderboard: `0.80`
- Comparison baselines:
  - README `v20`: validation `837 / 950 = 0.8811`, proxy `176 / 200 = 0.8800`, public `0.84-0.85`
  - `v4`: validation `813 / 950 = 0.8558`, proxy `179 / 200 = 0.8950`, public `0.85-0.86`
  - `v6`: validation `829 / 950 = 0.8726`, proxy `180 / 200 = 0.9000`, public `0.83-0.85`

## Executive summary

`v7` は、この corrective 系列で初めての明確な崩壊 run です。`official leaderboard = 0.80` は `v4` の `0.85-0.86` と比べて大幅悪化であり、ローカルでも `validation 784 / 950`、`proxy 154 / 200` と同方向に崩れました。

崩壊はほぼ全面的に `bit_manipulation` に集中しています。

- validation `bit_manipulation`: `95 / 169 = 56.2%`
- proxy `binary`: `54 / 92 = 58.7%`
- 一方で `numeral = 149 / 149`, `unit_conversion = 171 / 171`, `cipher = 161 / 162`, `symbol = 24 / 32` で、easy family と symbol は大きく崩れていません

したがって、今回の失敗は「全体の学習が壊れた」のではなく、**binary overlay が質的に壊れた** run と読むべきです。

さらに重要なのは、**学習 notebook 自体は v4 と同一**で、Kaggle train log でも target modules、optimizer、trainable params、micro batch、環境構築は同一だったことです。v4/v7 の train loss は `step 244` まではほぼ一致し、**`step 245` から突然 v7 だけが崩れます**。この `step 245` は overlay 開始点なので、原因は training runtime ではなく、**学習データ bundle の token stream と overlay 設計**にあります。

結論を先に言うと、v7 の本質的な失敗は次の 2 点です。

1. `v4` の public-safe overlay を「同じ text」として再利用したつもりでも、**同じ token stream としては継承していなかった**
2. その上で `v6` donor の short exact traces を混ぜたため、overlay 区間の teacher manifold が急に不均質になり、bit 出力が **content error から malformed output へ** 崩れた

これは `A-Open-ProgressPrizePublication/README.md` が強調していた

- deterministic CoT
- tokenization awareness
- work with tokens instead of text

の 3 点に正面から反する failure でした。

## README に照らした解釈

`A-Open-ProgressPrizePublication/README.md` の勝ち筋は一貫しています。

- 最大の差分源は `bit_manipulation`
- deterministic decoding では CoT を単純・安定に保つ必要がある
- tokenization weakness を踏まえて trace を設計する必要がある
- より高いスコアには `work with tokens instead of text` が有望

今回の `v7` は、この README 契約に対して逆方向へ動きました。

- bit だけが大きく崩れた
- wrong rows の failure mode が `format_ok_content_wrong` から `non-binary / no-box / truncated` に変質した
- `v4` の public-safe branch を text として再構成し直したため、token-safe だった supervision を壊した可能性が高い

つまり `v7` は「binary insight が間違っていた」のではなく、**token-aware な teacher の継承方法を誤った** run です。

## Scorecard

| version | validation | proxy | public leaderboard | interpretation |
| --- | ---: | ---: | ---: | --- |
| `v20` | `837/950 = 0.8811` | `176/200 = 0.8800` | `0.84-0.85` | README baseline |
| `v4` | `813/950 = 0.8558` | `179/200 = 0.8950` | `0.85-0.86` | best public run in this family |
| `v6` | `829/950 = 0.8726` | `180/200 = 0.9000` | `0.83-0.85` | proxy-strong donor branch |
| `v7` | `784/950 = 0.8253` | `154/200 = 0.7700` | `0.80` | catastrophic binary collapse |

`v7` の重要な点は、proxy と public が今回は同方向に崩れていることです。`v6` では `proxy > public` という blind spot がありましたが、`v7` はそうではありません。したがって `v7` は proxy 設計の問題ではなく、**run 自体が真に悪い**と判断してよい負例です。

## Measured results

### Category summary

| category | v20 | v4 | v6 | v7 |
| --- | ---: | ---: | ---: | ---: |
| bit_manipulation | `149/169` | `150/169` | `150/169` | `95/169` |
| numeral | `149/149` | `124/149` | `138/149` | `149/149` |
| unit_conversion | `171/171` | `168/171` | `171/171` | `171/171` |
| gravity | `159/159` | `159/159` | `158/159` | `158/159` |
| cipher | `158/162` | `161/162` | `161/162` | `161/162` |
| TOTAL | `837/950` | `813/950` | `829/950` | `784/950` |

この表から分かることは明確です。

- `numeral` は `v6` の no-box 問題を完全回収した
- `unit` も維持できた
- しかしその代償として `bit` が `-55 rows` 以上落ちた

つまり `v7` は easy-family repair 自体には成功したが、その費用として binary frontier を壊しすぎました。

### Validation flips

`v4 -> v7`

- improved: `31`
- regressed: `60`
- net: `-29`
- regressed by category:
  - `bit_manipulation`: `56`
  - `cryptarithm_deduce`: `1`
  - `cipher`: `1`
  - `gravity`: `1`
  - `equation_numeric_deduce`: `1`
- improved by category:
  - `numeral`: `25`
  - `unit_conversion`: `3`
  - `cryptarithm_deduce`: `1`
  - `cipher`: `1`
  - `bit_manipulation`: `1`

`v6 -> v7`

- improved: `15`
- regressed: `60`
- net: `-45`
- regressed by category:
  - `bit_manipulation`: `58`
  - `cryptarithm_deduce`: `1`
  - `gravity`: `1`

したがって、validation 上の `v7` は **numeral donor の成功**と**bit branch の全面回帰**を交換した run です。

### Proxy summary

| slice | v20 | v4 | v6 | v7 |
| --- | ---: | ---: | ---: | ---: |
| overall | `176/200` | `179/200` | `180/200` | `154/200` |
| binary | `76/92` | `79/92` | `80/92` | `54/92` |
| symbol | `24/32` | `24/32` | `24/32` | `24/32` |
| bit_other | `28/35` | `28/35` | `28/35` | `17/35` |
| bit_structured_byte_formula | `23/31` | `25/31` | `26/31` | `16/31` |
| bit_permutation_inversion | `25/26` | `26/26` | `26/26` | `21/26` |

重要なのは、`v7` の崩壊が structured だけでも permutation だけでもなく、**binary の 3 subtype 全部に広がっている**ことです。

### Proxy flips

`v4 -> v7`

- improved: `1`
- regressed: `26`
- regressed family: **all binary**
- improved binary ID: `59c78e51`
- regressed binary IDs:
  - `0031df9c`, `0520a6ec`, `069dbaab`, `0abfab8b`, `0d7aacfc`, `0f7ddd75`, `111296b0`, `13009e35`, `1c671acc`, `26a70ae0`, `2817d770`, `3fdc3de7`, `3feeabea`, `4ada9150`, `57b03b2b`, `5d77eff6`, `6a186446`, `783a1317`, `885c8b51`, `8ad0116e`, `8e5d6fe6`, `af5302ca`, `b80795b4`, `b9500f41`, `d50683b4`, `fa67da07`

`v6 -> v7`

- improved: `0`
- regressed: `26`
- regressed family: **all binary**

つまり `v7` は donor として期待していた `v6` binary gains を移植するどころか、**proxy 上で donor line そのものを失った** run です。

## Training log comparison: same notebook, different overlay fate

### What stayed identical

v4 と v7 の Kaggle train log では次が一致しています。

- torch / wheel setup
- target modules
- trainable params: `888,154,112`
- optimizer: `paged_adamw_8bit`
- local micro batch size: `1`
- matched target modules counts

したがって、学習 notebook や optimizer 実装の差は主因ではありません。

### What changed in bundle stats

| field | v4 | v7 | delta |
| --- | ---: | ---: | ---: |
| num_examples | `8636` | `8674` | `+38` |
| total_tokens | `32858695` | `32948771` | `+90076` |
| total_steps | `271` | `272` | `+1` |
| max_seq_len | `7971` | `7999` | `+28` |
| bit_manipulation rows | `2408` | `2435` | `+27` |
| numeral rows | `802` | `813` | `+11` |
| last batch size | `8` | `14` | `+6` |

見た目には小差ですが、崩壊はこの追加部分だけでは説明できません。

### The decisive evidence: divergence starts exactly at the overlay boundary

v4 / v7 の train loss を比較すると、`step 244` まではほぼ一致しています。

- pre-overlay mean loss
  - `v4`: `0.016921`
  - `v7`: `0.016911`

しかし `step 245` 以降、すなわち overlay 開始点からだけ v7 が急激に崩れます。

- overlay-phase mean loss
  - `v4`: `0.004818`
  - `v7`: `0.264982`
- overlay-phase max loss
  - `v4`: `0.081475`
  - `v7`: `5.556264`
- first five overlay steps
  - `v4`: `0.000141, 0.000171, 0.000084, 0.000040, 0.000301`
  - `v7`: `0.063266, 0.056079, 0.051936, 0.045561, 0.041328`

特に最後の数 step だけでなく、**最初の overlay batch から既に v7 は v4 と別物**です。

これは次のことを意味します。

1. base snapshot 部分は原因ではない
2. runtime / optimizer / hardware も主因ではない
3. **overlay token stream 全体**が v4 と違っていた

## Learning data diff

### Intended v7 mix

v7 は設計上、次の mix でした。

- `v4_public_base`: `808` repeated rows
- `v6_binary_donor`: `27` repeated rows
- `v6_numeral_surface_donor`: `10` repeated rows
- `v7_numeral_surface_synth`: `1` repeated row

追加 donor の内訳はこうです。

- binary donor IDs:
  - `0520a6ec`, `0a50c4a8`, `0dd5caf4`, `17fd9612`, `59c78e51`, `8e5d6fe6`, `b9500f41`, `c30a782a`, `fa67da07`
- numeral surface IDs:
  - `00d9f682`, `018d465c`, `0aa2c5bf`, `0b2877ce`, `0ea93e44`, `105255db`, `1112ec96`, `1542039b`, `18840879`, `188fe6d4`, `18997574`

### Why the added 38 rows are not the whole explanation

v4 overlay は `808 rows` なので、batch size `32` だと `25` full batches と `1` partial batch (`8 rows`) です。v7 はここに `38 rows` 足しているので、追加 rows は主に overlay の最後 `2` batches に乗ります。

しかし train log の崩壊は `step 245`、すなわち **overlay 最初の batch** から始まっています。したがって、

- 「最後の 38 rows が hard すぎた」

だけでは説明できません。崩れているのは donor 末尾だけではなく、**v4 public base を含む overlay 全区間**です。

### The critical generator-level difference: v4 token reuse vs v7 re-tokenization

今回もっとも重要な技術差分はここです。

`v4` の bundle generator は、overlay row に対して

- `base_examples[(problem_id, "synthetic.jsonl")]` が存在する場合は、その **base snapshot token / mask を再利用**する
- synthetic row しかない場合だけ text を token 化する

実装でした。

一方 `v7` の bundle generator は、overlay row を **すべて text から token 化し直します**。

つまり `v7` は、`v4_public_base` の `808 rows` を「同じ row text」としては継承していても、**同じ token supervision としては継承していません**。

これは README の

- tokenization awareness
- work with tokens instead of text

という改善提案に対して、明確に逆方向の変更です。

`v4` が public-safe だった理由の一部は、少なくとも overlay の一部で **既存 synthetic token stream をそのまま使っていた**ことにあります。`v7` はその安全性を壊してしまいました。

### Secondary issue: heterogeneous overlay style

v7 overlay では、次の teacher style が同居しています。

- `v4` 由来の legacy long trace
- `v6` 由来の `exact_rule_commit`
- `v6` 由来の `exact_closure_commit`
- `v6` 由来の `anti_default1_commit`
- numeral の `surface_boxed_tail`

しかもこれが overlay 区間で一気に現れるため、モデルから見ると最後の学習フェーズが

- long-form bit trace
- short exact closure
- anti-default1 imperative
- boxed-only tail

の混在になっています。v4 の public-safe line と比べて、teacher style の manifold が広すぎます。

## Raw output analysis

### Proxy binary failure shape

| version | wrong rows | default1 | repeat loop | non-binary prediction | no-box |
| --- | ---: | ---: | ---: | ---: | ---: |
| `v20` | `16` | `16` | `16` | `0` | `0` |
| `v4` | `13` | `12` | `13` | `0` | `0` |
| `v6` | `12` | `10` | `12` | `1` | `0` |
| `v7` | `38` | `13` | `22` | `20` | `10` |

`v20-v6` では wrong binary の主形は

- `default 1`
- format は保っているが内容がずれる

でした。

しかし `v7` では、新しく

- `non_binary_prediction = 20`
- `no_box = 10`

が大量発生しています。これは **format-preserved content miss** ではなく、**trace collapse / malformed decoding** です。

### Validation binary failure shape

| version | wrong rows | default1 | repeat loop | non-binary prediction | no-box |
| --- | ---: | ---: | ---: | ---: | ---: |
| `v20` | `20` | `11` | `20` | `1` | `1` |
| `v4` | `19` | `14` | `19` | `0` | `1` |
| `v6` | `19` | `14` | `19` | `1` | `1` |
| `v7` | `74` | `11` | `26` | `37` | `26` |

validation でも同じで、`v7` は bit wrong `74` のうち

- `37` が non-binary prediction
- `26` が no-box

です。したがって public `0.80` の原因は単なる rule miss ではなく、**binary answer surface そのものが壊れた**ことです。

### Representative raw-output regressions

#### 1. `0520a6ec`: donor itself regressed

- `v4 proxy`: correct `10100001`
- `v6 proxy`: correct `10100001`
- `v7 proxy`: wrong `01100001`

trace tail は v4/v6 と同じ boxed answer closureに見えるのに、**最上位 bit だけが flipped** しています。これは format 崩れではなく、token-level content drift です。

#### 2. `8e5d6fe6`: content miss から malformed fallback へ悪化

- `v4 proxy`: correct `10000111`
- `v6 proxy`: correct `10000111`
- `v7 proxy`: prediction `101`

`v7` では raw output が bit-column listing で止まり、`numeric_fallback` へ落ちています。これは v4/v6 には無かった failure mode です。

#### 3. `c30a782a`: v6 で直した row を 10-bit boxed output に退行

- `v4 proxy`: wrong `01010110`
- `v6 proxy`: correct `01000110`
- `v7 proxy`: wrong `0010001111`

`v6` の donor が効いて一度直った row が、v7 では **boxed されているのに 10-bit** という悪い形に変わっています。

#### 4. `b9500f41`: anti-default1 donor を入れたのに `default 1` 再発

- `v4 proxy`: correct `11110000`
- `v6 proxy`: correct `11110000`
- `v7 proxy`: wrong `11111000`

raw output では `4 default 1 = 1` が再発しています。つまり donor row の存在だけでは `default 1` は抑えられず、むしろ overlay 混在で再活性化しました。

#### 5. `17fd9612`: validation で truncation

- `v4 validation`: correct `00011010`
- `v6 validation`: correct `00011010`
- `v7 validation`: prediction `2`

raw output が bit-column 解釈途中で切れており、これも v7 特有の malformed failure です。

## Donor behavior

期待されていた donor IDs の実際の挙動は次の通りです。

| id | v4 | v6 | v7 | read |
| --- | --- | --- | --- | --- |
| `0520a6ec` | correct | correct | wrong | donor 自身が regression |
| `0a50c4a8` | correct | validation wrong / proxy correct | correct | 局所回収あり |
| `59c78e51` | wrong | correct | correct | v7 唯一の明確な proxy gain |
| `8e5d6fe6` | correct | correct | wrong | malformed fallback 化 |
| `b9500f41` | correct | correct | wrong | `default 1` 再発 |
| `c30a782a` | proxy wrong | proxy correct | wrong | 10-bit output に退行 |
| `fa67da07` | correct | correct | wrong | permutation row を喪失 |
| `17fd9612` | validation correct | validation correct | validation wrong | truncation |

要するに、`v7` の失敗は「donor の選定が全部悪かった」ではありません。**correct donor を混ぜても transfer が壊れた**のが実態です。

## Root-cause judgment

### Primary cause

**v7 は v4 の public-safe overlay を verbatim に継承していない。**

より正確には、v7 は v4 overlay row text を再利用したが、v4 が public-safe だったときの token stream は継承していませんでした。generator 実装上、v4 は base synthetic tokens を再利用できたのに、v7 は overlay を全 retokenize しています。

その結果、README が警告していた tokenization weakness が、bit overlay で一気に噴出しました。

### Secondary cause

**overlay style の混在が強すぎる。**

v4 long trace と v6 short exact trace を同一 final phase に混ぜたことで、overlay 冒頭から loss が急騰しています。donor 追加は最後の 38 rows だけですが、train loss 崩壊は overlay 開始点から起きているため、問題は donor rows 単体ではなく、**v4_public_base を含む overlay 設計全体**です。

### What this is not

- training notebook bug ではない
- optimizer bug ではない
- easy family 崩壊でもない
- symbol branch expansion の副作用でもない

今回の run は、**bit overlay token stream の再構成事故**として扱うのが最も正確です。

## Why this negative result is valuable

今回の `0.80` は大きく下がりましたが、貴重なデータです。

1. `v6` のような proxy/public mismatch ではなく、proxy/public が同時に崩れる「真に悪い run」の形が取れた
2. 学習ログが `step 245` からだけ壊れているため、base snapshot ではなく overlay が悪いと強く断定できた
3. v4 public-safe branch を donor 化するときに、**text reuse では足りず token reuse が必要**だと分かった
4. `anti_default1` donor を足しても、teacher mix が悪いと `default 1` は再発しうると確認できた

README の「work with tokens instead of text」が、ここで初めて実測の failure と直接つながりました。

## Practical next steps

### Must do before any v8-like branch

1. `v4` を donor に使うなら、`v4_public_base` を text から再構築せず、**v4 bundle の overlay token stream をそのまま引き継ぐ**
2. `v4` public-safe rows と `v6` donor rows の混合実験は、まず **v4 token stream fixed** 条件で行う
3. `v4_public_base retokenized only` という単独アブレーションを作り、今回の崩壊のうち何割が retokenization 単体かを切る
4. donor rows を足すなら final two batches だけでなく、**overlay whole-phase loss** を監視する

### What should not be repeated

1. `v4` public base を「同じ row text だから同じ supervision」と見なして再利用すること
2. long trace / short exact / anti-default1 / boxed-tail を無造作に同じ overlay phase に積むこと
3. proxy gain donor をそのまま mainline へ混ぜれば移植できると考えること

## Final judgment

`v7` の失敗は、単なる「追加 donor 38 行の入れすぎ」ではありません。

**`v4` の public-safe token distribution を失った状態で、`v6` の short exact donor を混ぜたことにより、binary overlay の学習位相そのものが壊れた** run です。

README ベースで言い換えると、`v7` は

- bit を主戦場にする
- deterministic CoT を保つ
- tokenization を意識する

という勝ち筋のうち、最後の 2 つを壊したために、bit の content だけでなく answer surface まで崩れました。

これは 0.80 という悪い結果ですが、次に避けるべき地雷はかなり明確になりました。
