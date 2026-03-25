# CUDA train data analysis v1 - mid results

- generated_at_utc: `2026-03-25T12:40Z` 前後
- source: `README.md`, `try-cuda-train-data-analyst-plan.md`, `try-cuda-train-result.md`, `try-cuda-train.md`
- scope: `data/train.csv` 9,500 件の全件解析。学習は未実行。

## 1. 現時点の全件カテゴリ分け

- `verified_trace_ready`: 5,816
- `manual_audit_priority`: 3,602
- `answer_only_keep`: 65
- `exclude_suspect`: 17

これはかなり保守的な判定で、**規則と答えの整合を programmatic に確認できたものだけ**を `verified_trace_ready` に入れている。

## 2. family ごとの進捗

- `roman`: 1,576 / 1,576 を厳密復元
- `gravity`: 1,597 / 1,597 を厳密復元
- `unit`: 1,594 / 1,594 を厳密復元
- `text`: 605 / 1,576 を厳密復元
- `binary`: 370 / 1,602 を厳密復元
- `symbol`: 74 / 1,555 を厳密復元

## 3. 重要な発見

### text family

- 未解決 971 件は **mapping conflict 0 件**
- つまり「規則が壊れている」より **query で必要な暗号文字が例に 1〜6 文字足りない** ケースが支配的
- よって text は、solver 自体より **例カバレッジ不足** がボトルネック

### symbol family

- 少なくとも 2 つの大サブタイプに割れる
  - `glyph_len5`: 823
  - `numeric_2x2`: 732
- `numeric_2x2` は row-local operator-aware formula search で
  - `verified_trace_ready`: 74
  - `answer_only_keep`: 65
  まで回収できた
- `glyph_len5` は未解決で、単純な deletion+substitution transducer 仮説でも 0 / 823
- したがって symbol は、1 family として雑に扱うのではなく **最低でも 2 つに分けて別々に監査** すべき

### binary family

- `bit permutation / inversion` に加えて、
  - 2bit boolean
  - 3bit (`majority / choice / parity3`)
  - affine XOR (GF(2))
  を入れると strict verified は `370 / 1602`
- これは `try-cuda-train-result.md` の 306 solved を上回る
- つまり binary は「以前の teacher が過大」だけではなく、**rule family の取り方が浅かった** 側面もある
- 残り 1,224 件は、現在の strict rule family では説明できず、追加の circuit / non-local transform 分析が必要

## 4. 現時点のデータ方針

- 直ちに trace 蒸留へ回してよいコアは `train_verified_trace_ready_v1.csv`
- answer-only 補助候補を含む現時点の推奨学習対象は `train_recommended_learning_target_v1.csv`
- `text` 未解決 971 件は「未知文字不足」なので、目視または外部 hypothesis generation の優先候補
- `symbol` 残り 1,416 件と `binary` 残り 1,224 件は、**誤 teacher を混ぜる危険が高いので、今のまま trace 化しない**
- `train_exclude_suspect_v1.csv` の 17 件は、現時点では学習対象から外す

## 5. 次の掘り順

1. `symbol` の `glyph_len5` を数十件目視して規則クラスを特定
2. `manual_pass1_priority_pack_v1.csv` を起点に人手監査を開始
3. `binary` の残り 1,224 件を circuit / non-local transform 観点で再クラスタ
4. `text` の未解決 971 件を unknown-char 数順に処理
