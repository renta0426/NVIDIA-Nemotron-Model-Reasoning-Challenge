# v20 corrective corpus v8 reassessment

## Status

- Created: 2026-04-22 UTC
- Evidence sources:
  - `A-Open-ProgressPrizePublication/result/results-8/results.csv`
  - `A-Open-ProgressPrizePublication/result/results-8/validation.csv`
  - `A-Open-ProgressPrizePublication/result/leaderboard_proxy_eval-v8/reports/leaderboard_proxy_eval_summary.md`
  - `A-Open-ProgressPrizePublication/result/leaderboard_proxy_eval-v8/artifacts/leaderboard_proxy_eval_row_level.csv`
  - `A-Open-ProgressPrizePublication/README.md`
  - `versions/v20_corrective_corpus_v4_mainline/v20_corrective_corpus_v4_mainline-results.md`
  - `versions/v20_corrective_corpus_v6_mainline/v20_corrective_corpus_v6_mainline-results.md`
  - `versions/v20_corrective_corpus_v7_mainline/v20_corrective_corpus_v7_mainline-results.md`
- Measured score summary:
  - validation: `839 / 950 = 0.8832`
  - leaderboard proxy: `178 / 200 = 0.8900`
  - official leaderboard: user-reported `0.84`

## Executive summary

`v8` は **promote 不可** です。

ローカルでは `validation 839 / 950` と見栄えが良い一方で、README が主戦場と定義している `bit_manipulation` の frontier を押し上げておらず、公式スコアは `0.84` へ悪化しました。挙動としては `v2` の再発に近く、**easy-family / boxed-surface の局所回復で validation を稼ぎ、binary content を前進させないまま public で負けた run** と読むのが妥当です。

したがって、`v8` を次の本命 branch の土台にしてはいけません。次に進む前に、**public blind spot を埋める追加の重大な検証**が残っています。

## README-grounded interpretation

`A-Open-ProgressPrizePublication/README.md` の主張は一貫しています。

- 最大の差分源は `bit_manipulation`
- 評価契約は deterministic decoding 下の boxed-first extraction
- easy-family の boxed / terminal surface を壊すと無駄落ちする
- ただし 0.87 以上へ行く主レバーは easy repair ではなく binary frontier

`v8` はこの契約に対して、次のような位置づけです。

1. boxed-first extraction の最低限は守れている
2. numeral の no-box 系を一部戻して validation を押し上げた
3. しかし binary frontier は `v6` より弱く、`v4` よりもわずかに弱い
4. 結果として public は `v4` に届かず、`0.84` に落ちた

つまり `v8` は「README 契約を満たす本命」ではなく、**README 契約のうち easy-family surface 側だけを局所的に直した run** です。

## Scorecard

| version | validation | proxy | proxy binary | public leaderboard | read |
| --- | ---: | ---: | ---: | ---: | --- |
| `v4_mainline` | `813/950 = 0.8558` | `179/200 = 0.8950` | `79/92 = 0.8587` | `0.85-0.86` | best public mainline in this family |
| `v6_mainline` | `829/950 = 0.8726` | `180/200 = 0.9000` | `80/92 = 0.8696` | `0.83-0.85` | proxy-strong, public blind spot exposed |
| `v8` | `839/950 = 0.8832` | `178/200 = 0.8900` | `78/92 = 0.8478` | `0.84` | local recovery, public regression |

この比較で重要なのは次の 3 点です。

1. `v8` は validation だけ見ると最良だが、public は最良ではない
2. `v8` は proxy でも `v6` を下回り、`v4` すら超えていない
3. public best は依然として `v4` 系であり、local best と public best が一致していない

## What v8 actually changed

### Validation movement vs v6

- net: `+10`
- improved by category:
  - `numeral`: `+10`
  - `bit_manipulation`: `+4`
  - `cipher`: `+1`
  - `gravity`: `+1`
- regressed by category:
  - `bit_manipulation`: `-4`
  - `cryptarithm_deduce`: `-1`
  - `gravity`: `-1`

つまり `v8` の validation gain の主因は **numeral recovery** です。bit は net で大きく伸びていません。

### Proxy movement vs v6

- net: `-2`
- improved: `0`
- regressed IDs:
  - `c30a782a`
  - `13009e35`

どちらも binary で、しかも `verified_trace_ready` 側を含みます。これは重要です。`v8` は manual / answer-only の不安定 row だけでなく、**verified binary の一部でも後退**しています。

### Proxy movement vs v4

- net: `-1`
- improved IDs:
  - `59c78e51`
- regressed IDs:
  - `069dbaab`
  - `13009e35`

したがって `v8` は `v4` の public-safe balance を超えたとは言えません。

## Failure shape

`v8` proxy wrong rows は `22` 件です。

- binary: `14`
- symbol: `8`

selection tier 別 wrong counts は次の通りです。

- `manual_audit_priority`: `10`
- `verified_trace_ready`: `7`
- `answer_only_keep`: `5`

ここで見るべきは、**wrong が manual tier だけに閉じていない**ことです。`verified_trace_ready` にも `7` 件残っており、binary core 自体が未解決です。

### v8 proxy binary wrong IDs

- `c30a782a`
- `a6192d29`
- `01e09228`
- `12fd5b6c`
- `1532c0d1`
- `012fb81b`
- `13009e35`
- `2d790c98`
- `069dbaab`
- `101410e4`
- `12154247`
- `2230fad0`
- `257e7158`
- `31966698`

この集合は、以前から見えていた persistent hard core とほぼ重なっています。つまり `v8` は新しい frontier を切り開いていません。

### v8 proxy binary regressions are content regressions

`v8` で落ちた代表 row は、いずれも boxed 自体は保っています。

- `c30a782a`: `01000110 -> 01010110`
- `13009e35`: `11111011 -> 10111011`
- `069dbaab`: `00010000 -> 00010001`

これは `v7` のような malformed collapse ではなく、**format は正しいが中身が wrong** という binary content drift です。README の観点では、こちらの方が本質的に重い失点です。

## Why public fell to 0.84

### 1. v8 is a validation-improving run, not a binary-improving run

`839 / 950` の gain の大半は numeral 回復です。一方で proxy binary は

- `v6`: `80 / 92`
- `v8`: `78 / 92`

と悪化しています。README の「bit manipulation が主戦場」という整理に従えば、public が下がる方が自然です。

### 2. v8 repeats the already-known proxy/public blind spot

`versions/v20_corrective_corpus_v6_mainline/v20_corrective_corpus_v6_mainline-results.md` で既に、

- `v4 > v6` on public despite `v6 > v4` on proxy
- current proxy has a non-trivial blind spot

が記録されていました。`v8` はこの blind spot を埋めていません。むしろ proxy 自体も `v6` より弱いので、public 0.84 は surprise ではなく **warning ignored** に近い結果です。

### 3. symbol is still weak, but symbol is not the decisive new failure here

`v8` proxy symbol は `24 / 32 = 0.7500` で、`v4` / `v6` と同水準です。

- `glyph_len5`: `1 / 5`
- `numeric_2x2`: `23 / 27`

symbol は依然弱いものの、今回 public が落ちた主因は新しい symbol collapse ではありません。**binary が進んでいないこと**が主因です。

## Major validation debt still remaining

次の実験に進む前に、少なくとも次の 3 つは重大な未完了検証です。

### 1. Public-calibrated gate is still missing

現状の gate は

- validation 950
- proxy 200

が中心ですが、`v4`, `v6`, `v8` の並びで **public best を選べていません**。このまま次の run を回しても、また local best を public loser と誤認する可能性が高いです。

必要なのは、既知の contradiction を集めた **public-risk mini gate** です。最低でも次を含めるべきです。

- `v4 > v6` だった hidden-sensitive rows
- `v6 > v8` で regression した verified binary rows
- numeral no-box / `\box` tail rows
- binary content-only regressions

### 2. Binary hard-core watchlist gate is still missing

次の run は、少なくとも次の proxy hard IDs を **守る / 直す** ことを昇格条件に入れるべきです。

- `012fb81b`
- `01e09228`
- `101410e4`
- `12154247`
- `12fd5b6c`
- `1532c0d1`
- `2230fad0`
- `257e7158`
- `2d790c98`
- `31966698`
- `a6192d29`
- `c30a782a`
- `13009e35`
- `069dbaab`

今までは aggregate score で見ていましたが、`v8` で分かったのは **aggregate が上がっても binary verified rows を落とせば public は負けうる** ということです。

### 3. Any v8-like mixed branch still needs source-aware token reuse

`v7` で確認済みですが、public-safe rows を donor と混ぜる branch では token stream 継承が source-aware でなければいけません。`v8` 自体は `v7` のような全面 collapse ではないものの、次の mixed mainline をやるならこの条件は引き続き mandatory です。

つまり、次に試す branch が

- `v4` public-safe base
- `v6` binary donor
- 新しい guardrail / short closure

を混ぜるなら、**text reuse ではなく token reuse 条件を先に固定**しないと、また別の blind spot を作ります。

## Directional judgment

### What to do now

1. `v8` は mainline 候補から外す
2. public baseline は引き続き `v4` を使う
3. binary donor branch としては `v6` を参照するが、そのまま promote しない
4. 次の本命は `v4` を土台に、`v6` の binary gain だけを慎重に移植する branch にする

### What not to do now

1. `v8` の validation `839 / 950` を理由に、そのまま次の主系列へ進めること
2. numeral / easy-family をさらに厚くして local score を積みにいくこと
3. broad symbol overlay を mainline へ戻すこと
4. current proxy だけで promote 判定すること

## Concrete next-step recommendation

次の本命 branch に進む前に、以下を先にやるべきです。

1. `v4 / v6 / v8` の contradiction rows だけで構成した small public-risk gate を作る
2. proxy hard binary watchlist を昇格条件へ追加する
3. `v4` token-safe inheritance を壊さない mixed mainline を設計する

そのうえで次の training branch は、方向としては次が最も筋が良いです。

- base: `v4` public-safe balance
- donor: `v6` binary exact closure line
- preserve: numeral / unit / cipher の minimal surface stabilizer
- reject condition: `c30a782a`, `13009e35` のような verified binary regression が 1 件でも出たら不合格

## Final judgment

`v8` から得るべき結論は、「このまま次の実験へ進む」ではありません。

正しい結論は、**public 0.84 悪化を説明できるだけの追加重大検証がまだ残っている** です。

より具体的には、未解決なのは model quality そのものというより、

- public-calibrated validation
- binary hard-core watch gating
- token-safe mixed-branch inheritance

の 3 点です。

この 3 点を埋めずに次の run を回しても、また `validation 良化 / public 悪化` の繰り返しになる可能性が高いです。