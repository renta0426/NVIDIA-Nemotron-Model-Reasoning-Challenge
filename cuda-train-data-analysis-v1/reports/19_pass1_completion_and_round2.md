# cuda-train-data-analysis-v1 pass1 completion and round2 priorities

## 目的

`README.md` の accuracy 最優先方針に基づき、manual curation pass1 がどこまで進み、何が safely 片付いたか、そして次の round2 をどこから始めるべきかを 1 枚で整理する。

## pass1 の結論

pass1 では、**安全に上げられるものだけを上げ、危険な行は無理に昇格しない** 方針を最後まで維持した。

結果として、pass1 の主要な収穫は次の通り。

- `text`: 未解決 971 行を clean `answer_only_keep` に昇格
- `symbol/numeric_2x2`: `concat_xy`, `concat_yx`, `abs_diff_2d`, `abs_diff_2d_op_suffix` を安全採用
- `symbol`: residual scan で `824d4bcb` を `verified`、`9cb03277` を `answer_only`、`4c6cf9d9` を `exclude_suspect`
- `binary`: 一意 affine / low-gap / gold mismatch の 11 行を `exclude_suspect`
- `glyph_len5`: 46 行を dedicated recheck したが、safe promotion 0 / safe exclusion 0

## 現在の counts

- `verified_trace_ready`: `5862`
- `answer_only_keep`: `1075`
- `manual_audit_priority`: `2534`
- `exclude_suspect`: `29`

安全側コアは `6937 / 9500` (`73.0%`) のまま変化なし。

## symbol pass1 の締め

### 1. query-only mimic 32 行は全却下

`reports/17_symbol_query_only_rejection.md` で整理した通り、query answer だけ見ると次に見える 32 行は safe ではなかった。

- `27` 行: same-op examples と衝突
- `5` 行: sign / prefix / suffix format が examples だけでは一意化できない
- net change: `0`

### 2. 次の derived template も 0 件

`reports/18_symbol_next_safe_scan.md` で、非 query-only 残差に対して次を探索した。

- `+` / answer 長さ `3`
- `*` / answer 長さ `4`
- operator 埋め込み output 群

sum / product / diff 由来の digit-feature template や 2-chunk ルールを総当たりしたが、**追加回収 0** だった。

### 3. round2 で最優先の symbol cluster

report 17 の高shot query-only lookalike `32` 行に加え、report 23 で extra known-family / low-shot mimic を足した **mimic union `56` 行** を除くと、round2 の本丸は `317` 行になる。

この `317` 行の中で目立つのは次。

- `*` / answer 長さ `4`: `43` 行
- `+` / answer 長さ `3`: `39` 行
- `-` / answer 長さ `3`: `24` 行
- operator 埋め込み output: `54` 行

ここは row-local arithmetic ではなく、operator-specific な multi-step digit transform の可能性が高い。

## binary pass1 の締め

### 1. safe exclusion は一意 affine の 11 行まで

`reports/15_binary_residual_affine_scan.md` の 11 行は、

- affine 解が一意
- stricter solver が勝たない
- low-gap (`bit_no_candidate_positions <= 1`)
- gold と衝突

を満たしたため `exclude_suspect` に移した。

### 2. それ以上の easy suspect は無し

今回、`binary_low_gap` 139 行について **複数 solver family が同じ誤答へ収束する consensus mismatch** も探索したが、`0` 行だった。

つまり、unique affine 以外の easy exclusion はまだ見つかっていない。

## glyph pass1 の締め

`glyph_len5` 46 行は依然として coarse multiset + order 仮説止まり。

- answer 長さ 1: `2`
- answer 長さ 2: `16`
- answer 長さ 3: `13`
- answer 長さ 4: `15`

短答群も読み直したが、このパスでは safe promotion / safe exclusion に繋がる exact family は見つからなかった。

## round2 の入口

### 優先順位

1. `symbol_numeric_same_op` の `*` 4桁 cluster
2. `symbol_numeric_same_op` の `+` 3桁 cluster
3. `symbol_numeric_same_op` の `-` 3桁 cluster
4. `symbol_numeric_same_op` の operator 埋め込み output 群
5. `symbol_glyph_multiset` 46 行
6. `binary_low_gap` 139 行

### round2 で変えること

round2 では brute-force template を増やすより、**operator ごとに prompt 実例を読んで family を手で束ねる manual clustering** の比重を上げる必要がある。

pass1 で分かったのは、「query gold に後追いで合う式」はほぼ取り切ったこと、そして残差の中心は more operator-specific / non-linear だということだった。

## まとめ

pass1 は成功している。

- 上げるべき安全行はかなり上げ切った
- 危険な 32 行を新たに防げた
- 次の easy family が無いことまで確認できた

そのため round2 は、**残差を無理に一般化しない** 前提で、cluster-first の手動読解へ移るのが妥当である。
