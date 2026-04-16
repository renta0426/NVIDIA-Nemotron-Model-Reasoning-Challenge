# v20 snapshot FINAL_SUMMARY 置換レポート

> Repository note: challenge の canonical contract は `README.md` を参照してください。
> このレポートは `A-Open-ProgressPrizePublication/nemotron/training/sft/04-08-16-14` の一部を `cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md` に沿った teacher trace で作り直すべきかを整理したものです。提出目標は引き続き `submission.zip` です。
> 置換や overlay を伴う run を実施した場合、計測済みスコアは対応する version ledger に必ず追記してください。

## 先に結論

**はい。ただし一部だけです。**  
`04-08-16-14` 全体を `FINAL_SUMMARY_REPORT.md` ベースで作り直すべきではありません。

README を根拠にすると、判断は次の 3 点に集約されます。

1. 元の A-Open 勝ち筋は、すでに easy family と `bit_manipulation` の大きな部分で強い deterministic teacher を持っていた。
2. その後の監査で、以前の「`default 1` 汚染をまとめて除去すべき」という理解は、凍結済み v20 snapshot に対しては誤りだと分かった。
3. したがって `FINAL_SUMMARY` の使い道は、**全面再生成**ではなく、**監査済み誤答の外科的置換と teacher-correct overlay** である。

## README を基準にした位置づけ

`A-Open-ProgressPrizePublication/README.md` では、勝ち筋は次のように説明されている。

- code で生成した deterministic chain-of-thought
- `bit_manipulation` を主戦場にすること
- Tinker による SFT
- min logprob を意識した学習
- `bit_manipulation` の目標 solve rate は `1364 / 1602 = 85.1%`

重要なのは、README 自体が **bit を 100% 解けるとは書いていない** ことです。  
したがって `FINAL_SUMMARY_REPORT.md` は、元の v20 snapshot の直接の生成元というより、**あとから teacher 品質と活用可能領域を精査した監査・整理レイヤ** と読むのが正確です。

## FINAL_SUMMARY と直接つながっている部分

実際には 2 つの層があります。

| 層 | `FINAL_SUMMARY_REPORT.md` との関係 | 実務上の読み方 |
| --- | --- | --- |
| 元の v20 snapshot `04-08-16-14` | **間接的 / 部分的** | README 時代の Nemotron teacher pipeline から来た base。`FINAL_SUMMARY` から直接生成されたものではない。 |
| 現在の corrective work (`v3_mainline`) | **直接的 / 強い** | teacher-correct filtering、structured bit 優先、base の外科的 cleanup という `FINAL_SUMMARY` 的な使い方をしている。 |

つまり現在の方針として正しいのは、**安全性が確認できている v20 base は残し、`FINAL_SUMMARY` は価値が監査で確認できた箇所だけに適用する** ことです。

## 作り直してはいけない部分

### 1. snapshot 全体の再生成はしない

`04-08-16-14` は歴史的な training artifact です。  
いまの repo 状態から無条件に再生成する対象ではなく、**base distribution として扱うべき**です。

理由は次のとおりです。

- 現在の `reasoning/*.txt` と `problems.jsonl` は、当時の `04-08-16-14` snapshot と完全な時点一致を保証しない。
- `nemotron/corpus.py` は通常カテゴリでは `rule_found` の行だけを学習に入れるので、repo 内に誤答 reasoning file が存在することと、実際に training に入ったことは同義ではない。
- snapshot には README 上でも後続 validation 上でも強いことが確認されている easy family の例が多数含まれる。

### 2. `default 1` を一括置換ルールにしない

ここが v3 監査で最も大きく修正された点です。

- binary reasoning 全体で見ると、`default 1` はたしかに危険信号である。
- しかし、実際の v20 snapshot overlap に入っていた `default 1` 関連の `92` rows / `66` base IDs は teacher-correct だった。

したがって、

- **`default 1` は監視対象**
- **自動置換条件ではない**

という扱いに下げるべきです。

## 置換・除外すべき部分

### 1. 監査で誤答確定した base bit rows

ここは最もきれいな置換対象です。

現時点で確認済みのものは次です。

- 凍結済み v20 overlap に存在する既知の metric-wrong base problem: `ef2fe526`
- 影響 row: `ef2fe526`, `ef2fe526-p0`

このため、現在の `v3_mainline` では `ef2fe526*` を base snapshot から除外しています。

### 2. 今後、直接監査で誤答と確定した bit rows

今後の置換ルールも evidence-first にすべきです。

1. まず凍結 snapshot に当該 row が実在するか確認する
2. `train.csv` と teacher の boxed answer を metric 整合的に照合する
3. そのうえで除外または置換する

この順序でないと、広すぎるヒューリスティックで正答 trace まで削る危険があります。

## FINAL_SUMMARY 由来データで作り直すべき部分

`FINAL_SUMMARY` の高 EV な使い方は、snapshot 全体の再構築ではありません。狙うべきは次です。

1. **teacher-correct-only overlay**
2. **bit の中でも高価値 family への再配分**
3. **binary 強化で easy family を壊さないための軽い guardrail**

これはそのまま `versions/v20_corrective_corpus_v3_mainline/` の設計思想です。

現時点の監査済み実装特性は次のとおりです。

- 既知の誤答 base problem `ef2fe526` だけを除外
- binary overlay 候補から teacher-incorrect を `130` 件除外してから選抜
- 実際に採用した overlay の teacher mismatch は `0`
- overlay は主に
  - `binary_structured_core`
  - `binary_other_light`
 へ集中
- easy family の guardrail は軽く維持

## family ごとの推奨方針

| family / slice | 推奨 | 理由 |
| --- | --- | --- |
| README 上ですでに強い stable easy family (`numeral`, `gravity`, `unit`, `cipher` の多く) | **base を維持** | 上振れ余地が小さく、置換リスクの方が高い |
| 直接監査で teacher 誤答が確定した `bit` rows | **置換 / 除外** | correctness の改善が明確 |
| `FINAL_SUMMARY` 由来の teacher-correct curated binary rows | **overlay として追加** | README 以降の分析でも最も期待値が高い改善軸 |
| teacher-correct と確認済みの `default 1` snapshot rows | **監査で落ちない限り維持** | 以前の一括除去仮説が誤りだったため |
| `FINAL_SUMMARY` の answer-only / manual-review 行 | **自動 trace 置換には使わない** | trace-safe と確定していない |

## 主質問への回答

**はい。`A-Open-ProgressPrizePublication/nemotron/training/sft/04-08-16-14` の一部は `FINAL_SUMMARY` に沿って作り直す価値があります。**  
ただし対象は **監査済みの狭い `bit` subset** に限るべきです。

推奨ポリシーは次です。

1. 凍結済み v20 snapshot は base として維持する
2. 既知の誤答 base bit rows だけを外科的に除外する
3. `FINAL_SUMMARY` 由来でも **teacher-correct-only** の binary overlay だけを追加する
4. 歴史的 snapshot 全体の wholesale replacement はしない
5. 各 run 後に validation / proxy / leaderboard の実測結果を必ず記録する

## 現在の mainline への含意

このレポートは、現在の corrected mainline 方針を支持します。

- **old v3 ablation**: 攻めすぎで、teacher-correct な `default 1` rows まで削っていた
- **current `v3_mainline`**: 正しい方向。`FINAL_SUMMARY` を「v20 base 全否定の根拠」ではなく、「置換と overlay の監査基盤」として使っている

要するに、**作り直すのは snapshot 全体ではなく、監査済みの狭い `bit` subset だけ**です。
