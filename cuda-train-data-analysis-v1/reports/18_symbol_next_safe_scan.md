# cuda-train-data-analysis-v1 next safe symbol scan

## 目的

`reports/17_symbol_query_only_rejection.md` で query-only mimic 32 行を全却下した後、残る `symbol_numeric_same_op` から **次の safe family があるか**を再探索する。

`README.md` の accuracy 評価を守るため、このパスでも条件は同じにした。

- same-op examples だけで規則が決まること
- query gold answer を tie-break に使わないこと
- sign / prefix / suffix format が examples から一意に決まること

## 今回見た残差

query-only mimic 32 行を除いた残りは `341` 行。

### answer 長さ分布

- 長さ `1`: `20`
- 長さ `2`: `92`
- 長さ `3`: `129`
- 長さ `4`: `100`

### 目立つクラスタ

- `*` で answer 長さ `4`: `43` 行
- `+` で answer 長さ `3`: `39` 行
- `-` で answer 長さ `3`: `24` 行
- operator を answer に埋め込む行: `54` 行（うち same-op examples が 2 以上あるものは `20` 行）

## 実施した探索

### 1. `+` 3桁 / `*` 4桁への digit-feature exact template 総当たり

非 query-only 残差のうち、件数が多い次の 2 群を直接探索した。

- `+` / answer 長さ `3` (`39` 行)
- `*` / answer 長さ `4` (`43` 行)

template token には単純 digit だけでなく、次も入れた。

- `x1`, `x2`, `y1`, `y2`
- `sum_h`, `sum_t`, `sum_o`
- `prod_th`, `prod_h`, `prod_t`, `prod_o`
- `diff_t`, `diff_o`
- 桁ごとの和 / 積 / cross 積の 2 桁表現

結果:

- `+` 3桁: **0 recovered**
- `*` 4桁: **0 recovered**

つまり、単純な digit rearrangement や、sum/product/diff 由来の局所 feature 合成では説明できない。

### 2. operator 埋め込み answer への派生 template 探索

answer 内に query operator 自体を含む `54` 行を見直した。

- same-op examples が 2 以上ある行: `20`
- `op` token を含む派生 template を総当たり
- `diff_t/diff_o`, `sum_*`, `prod_*` も併用

結果:

- **0 recovered**

代表的には `-55`, `-92`, `14>`, `*4`, `&42` のような行があるが、どれも簡単な signed/prefix/suffix arithmetic では説明できない。

## 代表クラスタの印象

### `*` 4桁

代表例:

- `40c53743` (`79*63`)
- `68b9b9a8` (`47*34`)
- `850dc715` (`33*95`)
- `a9deb8b5` (`01*31`)

同一 operator の examples を見ると、既知の `concat_xy / concat_yx` でもなく、単純 product の桁操作でもない。

### `+` 3桁

代表例:

- `2bc2a65a` (`70+85`)
- `691f2f76` (`33+98`)
- `0819520a` (`40+19`)
- `163db2d8` (`85+66`)

3 桁 output だが、carry・sum・difference の素朴な組み合わせでは再現できなかった。

### operator 埋め込み output

代表例:

- `7688e06e` (`63-19 -> -55`)
- `936b3ae5` (`95>81 -> 14>`)
- `e667f2d7` (`73*33 -> *4`)
- `4d1ae327` (`22&64 -> &42`)

prefix / suffix だけを見ると拾えそうに見えるが、examples 側が普通の signed arithmetic と一致しない。

## 結論

**このパスでは新しい safe family は見つからなかった。**

- query-only mimic: `32` 行すべて却下済み
- `+` 3桁 / `*` 4桁: digit-feature exact template でも **0**
- operator 埋め込み output: derived template でも **0**

したがって、残る `symbol_numeric_same_op` の中心は

- より operator-specific な非線形規則
- multi-step の桁変換
- row-local ではあるが単純 token 合成では表せない format

のどれかである可能性が高い。

## 影響

- global counts は **変化なし**
- `symbol_numeric_same_op` は引き続き `373` 行
- 今回は「安全に増やせる行」を見つけるより、「まだ増やせない」ことを確認した価値が大きい

## 次の優先候補

現時点の優先順位は次のまま。

1. `*` / answer 長さ `4`
2. `+` / answer 長さ `3`
3. `-` / answer 長さ `3`
4. operator 埋め込み output 群

ただし次は brute-force よりも、**operator ごとの prompt 実例を読んで family を手で束ねる manual curation** の比重が高くなる。
