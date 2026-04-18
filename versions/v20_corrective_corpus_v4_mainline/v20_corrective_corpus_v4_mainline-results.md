# v20_corrective_corpus_v4_mainline results

> Repository note: canonical challenge contract lives in `A-Open-ProgressPrizePublication/README.md`.
> This version keeps the direct-training single-file path, preserves the `submission.zip` target, and records measured scores and artifact-backed analysis.

## Executive summary

v4 is the first run in this corrective family that clearly improved the **official public leaderboard distribution** over the README v20 baseline while keeping most of the v3 binary gain.

- Official leaderboard, user-reported over 5 submissions:
  - `0.86 x 2`
  - `0.85 x 3`
  - mean: `0.8540`
  - min / max: `0.85 / 0.86`
- README v20 leaderboard distribution:
  - `0.85 x 3`
  - `0.84 x 5`
  - mean: `0.8438`
  - min / max: `0.84 / 0.85`

So v4 did three things that matter:

1. It removed the `0.84` floor seen in README v20.
2. It pushed the best observed public score from `0.85` to `0.86`.
3. It achieved that **without** collapsing the binary proxy slice back to v20.

At the same time, local validation remains far below public readiness:

- validation: `813 / 950 = 0.8558`
- leaderboard proxy: `179 / 200 = 0.8950`

This means v4 is **not** a solved mainline. It is a better public run than v20, but it still carries a large local numeral / boxed-surface debt.

## Active MLX reproduction status

- active run: `v20_mlx_v4_mainline_mb1_nobc`
- source bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v4_mainline_bundle.jsonl`
- latest observed train step: `271 / 271` (train completed)
- latest observed train loss: `0.0002936268817514455`
- latest observed trained tokens: `31369667`
- latest observed total elapsed seconds: `82419.2484`
- latest observed peak memory: `221.942 GB`
- post-train state: `training_result.json` is present and `eval-adapter-validation --validation-sample-size 950` is now running
- latest observed eval checkpoint: `511 / 950` rows completed
- latest observed eval partial score: `439 / 511 = 0.8591`
- latest observed eval partial read: through `511` checked rows, `numeral 85/85`, `cipher 85/86`, `unit 91/96`, and `gravity 77/80` stay strong while the dominant misses remain concentrated in `cryptarithm_deduce` (`30` misses) and `bit_manipulation` (`17` misses)
- note: measured adapter-validation score is still pending; the completed-train snapshot above is **not** a validation result
- operational note:
  - the short-lived MLX contrast lane `v20_mlx_v3_mainline_mb1_nobc` was stopped before its first logged train step after RAM climbed to about `483.79 / 512 GB`
  - tracked heavy artifacts for the aborted v3 lane were pruned, and only the active v4 MLX lane remains

## Tooling updates

- Script: `versions/v20_corrective_corpus_v4_mainline/reproduce_v20_corrective_corpus_v4_mainline.py`
- Style: single-file monolith
- Added measured-validation diff support for immediate post-run analysis:
  - `--analysis-only --measured-validation-csv <validation.csv> --measured-tag <tag>`
  - emits row-level regression packs against `base_v20`, `binary_reference_v1`, `corrective_v2`, and `corrective_v3`
- Bundle:
  - `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v4_mainline_bundle.jsonl`
- Kaggle notebook path:
  - `A-Open-ProgressPrizePublication/kaggle-v20-sft-repro.ipynb`

## README-grounded interpretation

The A-Open README still frames this run correctly:
The A-Open README still frames this run correctly:

- `bit_manipulation` is the main upside slice.
- evaluation is boxed-first extraction under deterministic decoding.
- easy-family surface corruption can erase otherwise-correct reasoning.
- symbol split / concat remains a Nemotron weakness.

v4 matches that picture almost exactly:

- the public gain came from **binary content improvements**, not from broad symbol gains;
- the remaining local damage is dominated by **boxed-surface failures**, especially numeral;
- proxy still shows that broad symbol improvement did **not** happen.

## Scorecard

| version | validation | proxy | public leaderboard | interpretation |
| --- | ---: | ---: | ---: | --- |
| v20 | `837/950 = 0.8811` | `176/200 = 0.8800` | README: `0.85 x3`, `0.84 x5` | strong easy families, weaker binary frontier |
| v1 | `838/950 = 0.8821` | `178/200 = 0.8900` | not recorded in current Git snapshot | binary overlay worked, symbol did not |
| v2 | `839/950 = 0.8832` | `176/200 = 0.8800` | user-reported `0.83-0.84` | guardrails helped locally, binary softened |
| v3_mainline | `801/950 = 0.8432` | `180/200 = 0.9000` | user-reported `0.84-0.85` | binary strongest, boxed surface collapsed |
| v4_mainline | `813/950 = 0.8558` | `179/200 = 0.8950` | user-reported `0.85 x3`, `0.86 x2` | partial surface recovery plus preserved binary gain |

The important read is:

- v4 is **not** the best validation run.
- v4 is **not** the best proxy run.
- v4 is the best observed **public** run in this corrective-corpus family.

That suggests the v4 tradeoff moved in the right direction for the hidden leaderboard even though local validation still over-penalizes unresolved boxed-surface failures.
# v20_corrective_corpus_v4_mainline 結果レポート

> リポジトリ注記: 正式な課題契約は `A-Open-ProgressPrizePublication/README.md` にある。
> 本バージョンは direct-training の単一ファイル経路を維持し、`submission.zip` を提出物ターゲットとして保ちながら、実測スコアと成果物ベースの分析を記録する。

## エグゼクティブサマリー

v4 は、この corrective 系列の中で初めて、README に記録された v20 ベースラインより **公式 public leaderboard の分布を明確に改善**しつつ、v3 の binary 改善の大半を維持した run です。

- 公式 leaderboard 実測（ユーザー報告、5回提出）:
  - `0.86 x 2`
  - `0.85 x 3`
  - 平均: `0.8540`
  - 最小 / 最大: `0.85 / 0.86`
- README 記載の v20 leaderboard 分布:
  - `0.85 x 3`
  - `0.84 x 5`
  - 平均: `0.8438`
  - 最小 / 最大: `0.84 / 0.85`

つまり v4 は次の3点を実現しました。

1. README v20 で見えていた `0.84` の下振れ帯を消した。
2. 観測された最高 public score を `0.85` から `0.86` に押し上げた。
3. それを **binary proxy を v20 水準まで崩さずに**達成した。

一方で、ローカル validation は依然として public readiness には達していません。

- validation: `813 / 950 = 0.8558`
- leaderboard proxy: `179 / 200 = 0.8950`

したがって v4 は **完成した本命 mainline ではありません**。v20 より public では良い run ですが、ローカルには依然として numeral / boxed-surface 系の大きな負債が残っています。

## README に基づく解釈

A-Open README の整理は、今回の run にもそのまま当てはまります。

- `bit_manipulation` が最大の上振れ余地を持つ。
- 評価は deterministic decoding 下での boxed-first extraction で行われる。
- easy family の surface corruption は、reasoning が合っていても失点源になる。
- symbol の split / concat は Nemotron の弱点である。

v4 はほぼこの図式どおりです。

- public 改善の主因は **binary content の改善**であり、broad な symbol 改善ではない。
- ローカルで残っている損失の主因は **boxed-surface failure**、特に numeral である。
- proxy を見ても、broad symbol 改善は起きていない。

## スコア比較表

| version | validation | proxy | public leaderboard | 解釈 |
| --- | ---: | ---: | ---: | --- |
| v20 | `837/950 = 0.8811` | `176/200 = 0.8800` | README: `0.85 x3`, `0.84 x5` | easy family は強いが、binary frontier は弱め |
| v1 | `838/950 = 0.8821` | `178/200 = 0.8900` | 現在の Git 管理下では未記録 | binary overlay は効いたが symbol は効かなかった |
| v2 | `839/950 = 0.8832` | `176/200 = 0.8800` | ユーザー報告 `0.83-0.84` | guardrail はローカルで効いたが binary は軟化 |
| v3_mainline | `801/950 = 0.8432` | `180/200 = 0.9000` | ユーザー報告 `0.84-0.85` | binary は最強だが boxed surface が崩壊 |
| v4_mainline | `813/950 = 0.8558` | `179/200 = 0.8950` | ユーザー報告 `0.85 x3`, `0.86 x2` | surface を部分回復しつつ binary gain を概ね維持 |

ここで重要なのは次の3点です。

- v4 は **validation の最高値ではない**。
- v4 は **proxy の最高値でもない**。
- それでも v4 は、この corrective-corpus 系列で観測された **public の最高 run** である。

つまり、local validation が unresolved な boxed-surface failure を強く罰している一方で、v4 のトレードオフ自体は hidden leaderboard に対しては正しい方向に動いたと読むべきです。

## v4 コーパス差分

### run に持ち込まれた基本設計

- base snapshot は `7828` 行を維持
- base から除外したのは監査済み誤答 `ef2fe526*` のみ
- binary overlay は `teacher-correct-only` を維持
- broad symbol mainline overlay は引き続き不採用
- surface bucket は generic guardrail ではなく、explicit な terminal-repair line として昇格

### v3 -> v4 の予算再配分

| slice | v3 repeated rows | v4 repeated rows | delta |
| --- | ---: | ---: | ---: |
| binary_structured_core | `768` | `528` | `-240` |
| binary_other_light | `160` | `128` | `-32` |
| numeral repair | `24` | `72` | `+48` |
| cipher repair | `0` | `24` | `+24` |
| cryptarithm symbolic repair | `12` | `24` | `+12` |
| unit tail repair | `12` | `16` | `+4` |
| symbol prefix repair | `2` | `4` | `+2` |
| gravity fragile | `12` | `12` | `0` |

bundle 全体の差分:

- overlay examples: `990 -> 808`（`-18.4%`）
- total tokens: `34,703,186 -> 32,858,695`（`-1,844,491`, 約 `-5.3%`）
- total steps: `276 -> 271`

ここで重要なのは絶対量より比率の変化です。

- binary repeated share: v3 `928/990 = 93.7%` -> v4 `656/808 = 81.2%`
- surface/easy repeated share: v3 `62/990 = 6.3%` -> v4 `152/808 = 18.8%`

したがって v4 は次のように要約できます。

- **v3 より binary 偏重を弱めた**
- **terminal answer repair を明示的に厚くした**
- それでも **broad symbol run ではない**

この設計差が、そのまま raw output の変化に現れています。

## ローカル結果の分析

### Validation: 依然として総合では弱い

`results-v4/results.csv` のカテゴリ別集計は次のとおりです。

| category | correct | total | accuracy |
| --- | ---: | ---: | ---: |
| bit_manipulation | `150` | `169` | `88.8%` |
| cipher | `161` | `162` | `99.4%` |
| cryptarithm_deduce | `5` | `71` | `7.0%` |
| cryptarithm_guess | `3` | `14` | `21.4%` |
| equation_numeric_deduce | `43` | `48` | `89.6%` |
| equation_numeric_guess | `0` | `7` | `0.0%` |
| gravity | `159` | `159` | `100.0%` |
| numeral | `124` | `149` | `83.2%` |
| unit_conversion | `168` | `171` | `98.2%` |
| TOTAL | `813` | `950` | `85.6%` |

v3 比では validation は `+12` 行改善しています。

- improved rows: `23`
- regressed rows: `11`

v3 比の改善内訳:

- numeral: `12`
- bit_manipulation: `4`
- cipher: `3`
- cryptarithm_deduce: `2`
- unit_conversion: `1`
- equation_numeric_deduce: `1`

v3 比の悪化内訳:

- bit_manipulation: `4`
- numeral: `4`
- unit_conversion: `3`

しかし v20 比ではまだ `-24` 行の純減です。

- improved rows: `11`
- regressed rows: `35`
- 回帰の主因は numeral: `25`

ローカル validation の話を一文で言うと、**v4 は v3 の surface 崩壊を有意に戻したが、numeral の boxed-surface failure を十分には直せていない**、となります。

### Proxy: 強く、かつ public と整合的

`leaderboard_proxy_eval-v4` は次の通りです。

- overall: `179 / 200 = 0.8950`
- binary: `79 / 92 = 0.8587`
- symbol: `24 / 32 = 0.7500`
- gravity / roman / text / unit: すべて `100%`

proxy の重要 slice:

- `bit_structured_byte_formula`: `25 / 31 = 0.8065`
- `bit_other`: `28 / 35 = 0.8000`
- `bit_permutation_inversion`: `26 / 26 = 1.0000`
- `numeric_2x2`: `23 / 27 = 0.8519`
- `glyph_len5`: `1 / 5 = 0.2000`

binary metric 契約は依然としてきれいです。

- boxed extraction success: `1.0`
- regex exact: `1.0`
- leading zero retention: `1.0`
- format failure rate: `0.0`
- format-ok content-wrong rate: `0.1413`

v20 比では proxy はちょうど `+3` 行改善しており、**3行とも binary 改善**です。

- `fa67da07`
- `0520a6ec`
- `0a50c4a8`

しかも v20 比で proxy 回帰は **0 行**です。

v3 比では net `-1` です。

- improved: `1` 行（binary の `5d77eff6`）
- regressed: `2` 行（binary の `c30a782a`, `59c78e51`）

これが public 改善の最も自然な説明です。

- v4 は v3 の binary frontier を大半維持した
- proxy binary を少しだけ返した
- その代わり catastrophic な surface failure をいくらか除去できた

## 学習データ差分が raw output に与えた実際の影響

## 1. Surface repair は、当たった failure mode に対しては実際に効いた

ここが v3 -> v4 のもっとも分かりやすい回復点です。

### Numeral の boxed-surface repair は一部で明確に効いた

代表例:

- `02e4851e`
  - v3 の末尾: `I will now return the answer in \box` の後に plain `XLIV`
  - v4 の末尾: 中間文言はまだ `\box` のままだが、最終的に `\boxed{XLIV}` で閉じる
  - 結果: extraction が回復し、正答へ復帰
- `039921f2`, `03bf2ac0`, `05992f55` も同じ型

解釈:

- v4 の numeral surface line は reasoning template 自体を完全には直していない
- ただし metric に必要な **最後の extraction-critical token 列** はしばしば修復できている

### Cipher の backslash-wrap failure は大半が回復した

代表例:

- `0184a864`
  - v3 の最終出力は `\wizard reads in village\`
  - v4 では `\boxed{wizard reads in village}` に復帰
- `018c6f61`
  - v3 でも同型の backslash-wrap failure
  - v4 では通常の boxed phrase に戻る
- `16642d10` も同様に正答復帰

解釈:

- `surface_cipher_boxed` bucket は狙い通りに機能した
- v3 の text failure は深い reasoning miss ではなく terminal formatting miss だった

### Symbolic cryptarithm repair は部分的には効いたが、完治ではない

代表例:

- `065abaf6`
  - v3 は fallback `5`
  - v4 は `\boxed{&/:\}` を復元して正答へ復帰
- `02a04b59`
  - symbolic answer で正答復帰

ただし:

- `0133bcec` は依然として失敗
- `0dcfd566` も依然として失敗

解釈:

- cryptarithm repair line 自体は実在する改善線である
- ただし symbol-heavy な ending に対してはまだ狭く、脆い

### Unit repair も少なくとも1件の測定済み miss を回収した

代表例:

- `077cfc0b`
  - v3: `39.023`
  - v4: `40.023`
  - この row は保存されている numeric tolerance の下で正答扱いに戻る

解釈:

- unit tail line は measured fragile rows に対しては効いている
- ただし unit はもともと強く、主戦場ではない

## 2. 残っている local の負債は、まだ boxed-surface debt が主因

wrong validation rows の failure flag を数えると、次の傾向がはっきり見えます。

### v3 wrong-row flags

- numeral: `33` 行が `box_not_boxed`
- cipher: `4`
- cryptarithm_deduce: `3`

### v4 wrong-row flags

- numeral: `25` 行が `box_not_boxed`
- cipher: `1`
- cryptarithm_deduce: `2`

つまり v4 は v3 の surface crash を確かに修復しましたが、修復はまだ不完全です。

未解消 failure の典型は次の通りです。

- reasoning body 自体は合っている
- `I will now return the answer in \box` が出る
- 最終的な extraction-safe な boxed wrapper が無い
- metric は `0` などの fallback に落ちる

代表例:

- `1112ec96`
  - reasoning は `Result: IV` に到達
  - しかし末尾はまだ `\box` のまま
  - v4 でも失敗継続
- `18840879`
  - `XC` で同型
- `0dcfd566`
  - `</think>` 以降の symbol escape corruption が v3 から変わらず残存

validation が依然として弱い理由はここです。**v4 の last-token repair line は v3 より良いが、numeral と symbolic ending に対してはまだ十分な安定性を持っていない。**

## 3. Binary 改善は実在し、public 改善の主因として最も妥当

v20 比で v4 の proxy gains はすべて binary で、しかも **format 修正ではなく content 修正**です。

### `0520a6ec`

- v20 は `AND-NOT25 AND-NOT36` を選んで `01100001`
- v4 は `AND-NOT15 AND-NOT26 AND-NOT37` を復元して `10100001`

### `0a50c4a8`

- v20 は弱い partial rule に止まり `00011101`
- v4 は stronger な 7-rule `AND-NOT` scaffold を維持し `00001101`

### `fa67da07`

- v20 は near miss の `11101111`
- v4 は `11101011`

これは README の主張と完全に整合します。

- proxy binary の format はもともと崩れていない
- 残っていた上振れ余地は **hard binary trace の content correctness** にあった
- v4 はそこを v20 より確実に改善した

## 4. v3 から binary 予算を削ったコストも実際に出ている

v3 比では proxy binary の回帰が2件あります。

- `c30a782a`
- `59c78e51`

### `c30a782a`

- v3 の best rule: `AND-NOT54 AND-NOT65 AND-NOT76 AND-NOT07`
- v4 では末尾の項が落ちて `AND-NOT54 AND-NOT65 AND-NOT76` になる
- 出力は `01000110` から `01010110` に回帰

### `59c78e51`

- v3 は `00000000` で正答
- v4 は `00001101` に戻る

validation binary 側でも `default 1` 汚染は未解消です。

- `0dd5caf4` は correct から `01000000` に回帰し、`default 1` が再出現
- v4 の wrong validation bit rows には `14` 行の `default_1`
- v3 でも `13` 行あったため、この failure mode は総量としては改善していない

解釈:

- v4 で増やした surface budget は有用だった
- ただし repeated binary rows を `928` から `656` に落としたコストは確実に存在する

## 5. Symbol 改善は依然として起きていない

proxy の symbol family は次のままです。

- `24 / 32 = 0.7500`

subtype 内訳:

- `numeric_2x2`: `23 / 27 = 0.8519`
- `glyph_len5`: `1 / 5 = 0.2000`

つまり v4 は新しい symbol frontier を作っていません。やったことは narrow な terminal surface repair までです。

これは corpus 設計とも一致します。

- broad symbol overlay は再導入していない
- 採ったのは narrow な symbol-prefix repair と terminal boxed repair のみ

## なぜ public は改善したのに validation は低いままなのか

もっとも自然で、かつ証拠に整合する説明は次の通りです。

1. hidden/public set は local 950 validation より binary 改善を強く報酬している。
2. v4 は v3 の binary gain の大半を維持しつつ、v20 比で proxy を `+3`、しかも全部 binary で改善した。
3. v4 は v3 の catastrophic な surface failure をある程度除去し、public の下振れを `0.84` に落とさずに済んだ。
4. 一方で 950 validation は unresolved な numeral `\box` failure を大量に踏むため、そこがまだ強く罰される。

したがって、この run が矛盾して見えるのは validation を過信した場合だけです。README に沿って読むなら、むしろ構図は一貫しています。

- proxy と public はどちらも binary gain が本物だと言っている
- validation は terminal surface debt がまだ大きいと言っている
- 両方とも正しい

## Proxy slice から見た残りの伸びしろ

proxy report を見ると、残っている gap は全体ではなく、かなり局所的です。

- `teacher_solver_candidate=''`: `18 / 26 = 0.6923`
- `binary_structured_byte_formula_abstract`: `4 / 7 = 0.5714`
- `bit_structured_byte_formula`: `25 / 31 = 0.8065`
- `bit_other`: `28 / 35 = 0.8000`
- `prompt_len_bucket=500-599`: `56 / 66 = 0.8485`
- `num_examples=10`: `56 / 66 = 0.8485`

逆に、すでに飽和している binary area もあります。

- `bit_permutation_inversion`: `26 / 26`
- `binary_bit_permutation_bijection`: `24 / 24`

したがって次の binary 改善では、もう解けている permutation 系に予算を使うべきではありません。残 gap は主に次です。

- no-solver / weak-solver row
- abstract structured row
- 10-example の長い trace

## 成果物解釈上の caveat

評価成果物の読み方について、重要な注意を明示しておきます。

`results-v20`, `results-v3`, `results-v4` の validation CSV では、`predicted` 列をそのまま truth source と見なしてはいけません。

- v20 には `correct=True` なのに `predicted != answer` の行が `352`
- v3 には `347`
- v4 には `344`

これは主に次のカテゴリに集中します。

- `unit_conversion`
- `gravity`
- それより少ないが無視できない `bit_manipulation`

したがって本レポートでは:

- `correct` を authoritative な実測ラベルとして扱う
- raw output を定性的証拠として使う
- `predicted` は debugging の補助信号としてのみ使う

特に `012fb81b` のような binary row では、literal な `predicted` 文字列と保存されている correctness flag が一致しないことがあります。

## 結論

v4 は意味のある前進ですが、まだ `0.88+` の本命 mainline ではありません。

v4 が証明したこと:

- v3 型の binary frontier は、十分 public score 改善につながる形で維持できる
- explicit な surface-repair bucket は必須である
- 現時点で最良の public run は、binary を最大化するだけでも、surface を最大化するだけでもなく、そのバランスから生まれている

v4 が未解決のまま残したこと:

- numeral の boxed-surface reliability はまだ弱すぎる
- symbolic cryptarithm ending は依然として脆い
- `default 1` 汚染は local binary rows にまだ残っている
- broad symbol capability は改善していない

## v5 に向けた次の一手

v4 の結果から見ると、次の高 EV 変更は broad redesign ではなく、もっと狭い follow-up です。

1. v20 比で proxy/public を上げた v4 の binary core は維持する。
2. numeral 専用の **より外科的な last-token boxed repair lane** を足す。
3. 効いている cipher terminal-repair line は維持する。
4. `c30a782a`, `59c78e51`, `0dd5caf4` のような row を中心に、v3 側の binary repeat を少量戻す。
5. もう飽和した permutation family ではなく、no-solver / abstract structured binary row を狙う。

これは、v4 が露出させた2つの具体的負債をそのまま叩く方針です。

- unresolved な numeral `\box` ending
- v3 -> v4 の予算再配分で少し軟化した binary

## Score ledger

| run | data change | validation | proxy | public leaderboard | notes |
| --- | --- | ---: | ---: | ---: | --- |
| v4_mainline_default | v20 base minus `ef2fe526*` + teacher-correct-only binary overlay + explicit terminal-surface repair buckets | `813/950 = 0.8558` | `179/200 = 0.8950` | user-reported `0.85 x3`, `0.86 x2` | corrective 系列で観測された public 分布のベスト。ローカルでは依然として numeral boxed-surface debt がボトルネック |
