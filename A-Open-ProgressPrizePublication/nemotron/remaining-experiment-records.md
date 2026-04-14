# Remaining experiment records in `nemotron`

この整理は **`A-Open-ProgressPrizePublication/README.md`** を一次ソースにしつつ、`nemotron/training/sft/` に残っている run artifact を突き合わせて作成した。

## 結論

- `nemotron/training/sft/logpaths.txt` には **24 run** の logpath が並んでいる。
- ただし、現時点で **config / metrics / loss / logprobs / tokens まで残っている実体 run は 6 本**だけ。
- **`v20` と確実に対応づくのは `04-08-16-14`**。
- `v21` 〜 `v27` については、現 repo には version 番号付き CSV / adapter / validation 出力が残っておらず、**厳密な対応表は復元不能**。
- その不在の根拠として、`nemotron/investigators/calc_accuracy.py` には `v20.csv v26.csv` の例が残っている一方、当該 CSV 本体は commit されていない。

## 残っている SFT run 一覧

| logpath | 実験内容の要約 | データ規模 | カテゴリ | 設定の特徴 | 残っているスコア/指標 |
| --- | --- | ---: | --- | --- | --- |
| `03-23-00-47` | 初期の **easy task 6カテゴリ中心** run。cryptarithm と equation guess がまだ入っていない。 | 7,599例 / 6.53M unmasked tokens / 119 steps | `bit_manipulation`, `cipher`, `equation_numeric_deduce`, `gravity`, `numeral`, `unit_conversion` | Tinker / batch 64 / rank 32 / len 8192 | 明示 score は未保存。final `_loss_per_token=0.008000` |
| `04-06-00-22` | README で「**finetuning script end-to-end 実装**」と説明されている Modal run。 | 8,542例 / 27.79M unmasked / 267 steps | ベンチ本体 9カテゴリ | Modal / batch 32 / micro 16 / rank 32 | README 記載 **0.81**。final `_loss_per_token=0.001554` |
| `04-07-02-00` | Modal 系の別 run。9カテゴリだがデータ配分が変わっており、結果は明確に悪化。 | 7,489例 / 25.59M unmasked / 235 steps | ベンチ本体 9カテゴリ | Modal / batch 32 / micro 16 / rank 32 | 明示 score は未保存。final `_loss_per_token=0.521485`、cipher `_min_logprob=-16.5463` |
| `04-08-16-14` | README の **勝ち run = v20**。 | 7,830例 / 26.57M unmasked + 1.28M masked / 245 steps | ベンチ本体 9カテゴリ | Tinker / batch 32 / micro 16 / rank 32 | README 記載: **Leaderboard 0.85×3, 0.84×5**。training set solve rate **87.8% (8340/9500)** |
| `04-10-04-15` | **auxiliary task を小さく試す run**。matching / spelling / splitting / concatenation / lstrip を追加。 | 1,789例 / 4.71M unmasked / 28 steps | 14カテゴリ | Tinker / batch 64 / micro 16 / rank 32 | 明示 score は未保存。final `_loss_per_token=0.068420` |
| `04-10-04-33` | **auxiliary task を大規模混合**した post-v20 run。README で spelling / splitting / concatenation の弱さを見る参照先になっている。 | 15,679例 / 41.77M unmasked + 9.52M masked / 245 steps | 13カテゴリ | Tinker / batch 64 / micro 16 / rank 32 | 明示 score は未保存。final `_loss_per_token=0.004436` |

## `v20` と score の確定記録

README に明示されている、version/score の確定情報は次の 3 つ。

| 版/系統 | 対応物 | README に残る score | 補足 |
| --- | --- | --- | --- |
| `v20` | `training/sft/04-08-16-14` | **0.85 three times, 0.84 five times** | README の Performance 表に明示。勝ち run。 |
| rank16 → rank32 zero-pad 系 | `tinker-submission-notebook-v77-082.ipynb` | **0.82** | README では training-serving misalignment の対策案の 1 つとして言及。 |
| end-to-end local finetune 系 | `training/sft/04-06-00-22` | **0.81** | README では Tinker を使わない end-to-end 実装として言及。 |

## `v21`〜`v27` について現 repo から言えること

### 言えること

- `calc_accuracy.py` の usage 例に `v20.csv v26.csv` があり、**version 番号付き CSV を比較する運用自体は存在した**。
- したがって `v20` 以降に複数の versioned submission/eval artifact があったこと自体は自然。

### しかし復元できないこと

- `v21.csv`〜`v27.csv`
- それぞれの adapter bundle
- それぞれの validation / leaderboard 結果
- 各 version と `training/sft/<timestamp>` の厳密対応

現 commit に残っていないため、**`v21`〜`v27` のローカル score を version ごとに確定表として再現することはできない**。

## 実験の流れとして読めること

README と残存 run を時系列に並べると、大まかにこう読める。

1. `03-23-00-47`  
   まず easy task 6カテゴリ中心で LoRA SFT の土台を作る段階。

2. `04-06-00-22`  
   Tinker 非依存の **end-to-end local / Modal 学習**を成立させ、README 記載で **0.81**。

3. `04-07-02-00`  
   別のデータ配分/構成を試すが、残存 metrics 上は明らかに悪化。

4. `04-08-16-14`  
   7,830例の 9カテゴリ構成に整理され、**v20 の勝ち run**に到達。

5. `04-10-04-15` → `04-10-04-33`  
   README の反省点どおり、**spelling / splitting / concatenation / matching** のような auxiliary subtask を追加して post-v20 改良を試し始めている。

## 今後この記録を使うときの注意

- **「score」** と **「training loss / min logprob」** は別物。  
  特に `04-10-*` run は auxiliary task が混ざっているので、`_loss_per_token` だけで leaderboard の優劣は決められない。
- **確定スコアが残っているのは README 明記分だけ**。  
  それ以外は「残存 metrics から見た良し悪し」のレベルで扱うべき。
- `v21`〜`v27` を本気で復元するには、**当時の CSV / Kaggle notebook output / adapter export** が別途必要。
