# A-Open-ProgressPrizePublication 学習SFTパイプライン

> このドキュメントは **A-Open-ProgressPrizePublication/README.md** と  
> **A-Open-ProgressPrizePublication/nemotron/** 実装をもとに、A-Open 公開物の
> **学習パイプライン**を分かりやすく整理したものです。  
> 参照: [README.md](./README.md) | 提出物: submission.zip

---

## 1. 先に結論

この公開物の勝ち筋は、**Tinker 上で LoRA を SFT する**流れです。

- 学習本体: `A-Open-ProgressPrizePublication/nemotron/train_sft.py`
- 学習前の CoT 生成: `A-Open-ProgressPrizePublication/nemotron/reasoning.py`
- Kaggle 側の変換・評価: `A-Open-ProgressPrizePublication/nemotron/notebook_tinker.py`

重要なのは、**Kaggle ノートブックは学習本体ではない**ことです。  
勝ち提出の学習は README に明記されている通り **Tinker** で行われています。

また、これは **SFT only** の方針です。README では「you only need SFT」と述べられ、強化学習は不要と明言されています。

---

## 2. どのコードが何を担当しているか

| 段階 | 実コード | 役割 |
| --- | --- | --- |
| CoT 設計・生成 | `nemotron/reasoners/*.py` `nemotron/reasoning.py` | 問題ごとの completion trace を生成する |
| 学習データ統合 | `nemotron/corpus.py` | reasoning / augmentations をまとめて学習用 manifest にする |
| Tinker 学習 | `nemotron/train_sft.py` | completion traces を Tinker に送り、LoRA を学習する |
| ログ確認 | `nemotron/training/sft/<log_path>/...` | min logprob / token loss / per-step metrics を見る |
| Kaggle 変換・評価 | `nemotron/notebook_tinker.py` | Tinker adapter を提出互換形式へ変換し、評価する |
| Kaggle へ配置 | `nemotron/upload_adapter.py` | adapter を Kaggle に持ち込む |

---

## 3. 全体フロー

README の「End-to-end processes」を、そのまま学習パイプラインとして整理すると次です。

```text
CoT 実装を直す
  ↓
reasoning.py で completion traces を生成
  ↓
train_sft.py で Tinker に送って LoRA 学習
  ↓
min logprob / 大きい loss token を確認
  ↓
CoT をさらに修正
  ↓
adapter を Kaggle にアップロード
  ↓
notebook_tinker.py で提出形式へ変換・評価
  ↓
提出
```

ポイントは、**損失を見て終わりではなく、min logprob の低い箇所を見て CoT を修正する**反復になっていることです。  
README の主題は「loss を下げる」より、**submission 時にも崩れにくい token を増やす**ために **minimum logprob を最大化する**ことにあります。

---

## 4. 学習本体は `train_sft.py`

勝ち提出で実際に Tinker に送っている学習コードは `nemotron/train_sft.py` です。

このスクリプトの流れは次の通りです。

1. `load_corpus_entries()` で学習対象を読み込む
2. `included == True` の例だけを使う
3. カテゴリが偏らないよう `_stratified_batches()` でバッチを組む
4. Tinker の LoRA training client を作る
5. 各バッチについて
   - token 列と mask を読み込む
   - `forward_backward_async()` を呼ぶ
   - `optim_step_async()` を呼ぶ
   - 各 example の logprob を保存する
   - category ごとの loss / min logprob を保存する
6. 学習最後に checkpoint を保存する

つまりこれは、単なる「学習ジョブ発射」だけでなく、**各 trace の token-level logprob まで保存する監視付き SFT スクリプト**です。

---

## 5. 勝ちランの実設定

再現時は `train_sft.py` の現在のデフォルト値だけでなく、**勝ちランの保存済み設定**を見るのが重要です。  
勝ち提出 v20 に対応するログは `nemotron/training/sft/04-08-16-14/` にあります。

### 5.1 勝ちラン設定

`training/sft/04-08-16-14/config.json` から読める内容は次です。

| 項目 | 値 |
| --- | --- |
| backend | `tinker` |
| base model | `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16` |
| loss | `cross_entropy` |
| batch size | `32` |
| micro batch size | `16` |
| epochs | `1` |
| LoRA rank | `32` |
| max length | `8192` |
| train_attn | `true` |
| train_mlp | `true` |
| train_unembed | `true` |
| learning rate schedule | `StepLinearDecayLRSchedule(2e-4)` |
| Adam beta1 / beta2 | `0.9 / 0.95` |
| weight decay | `0.0` |
| total examples | `7,830` |
| total training tokens | `27,850,703` |
| total steps | `245` |

### 5.2 大事な注意

チェックインされている `train_sft.py` の `Cfg` デフォルトには `batch_size = 64` が見えますが、  
**勝ちラン実績値は 32** です。

したがって、完全再現を目指すなら

- まず `README.md`
- 次に `training/sft/04-08-16-14/config.json`
- 最後に `train_sft.py` の現在のデフォルト

の順で優先して読むのが安全です。

---

## 6. 学習は SFT のみ。強化学習は使っていない

ここは誤解しやすいので明確にしておきます。

### 6.1 コード上は複数 loss をサポートしている

`train_sft.py` の冒頭には、次のような loss のサポートが書かれています。

- `cross_entropy`
- `importance_sampling`
- `ppo`
- `cispo`
- `dro`

つまり、**実験用の余地**としては RL 系や別 loss を扱える形です。

### 6.2 しかし勝ち提出は SFT

ただし、実際の勝ちラン設定ファイルでは `loss_config` は **`cross_entropy`** です。  
さらに README では、

- 「you only need SFT」
- 「Reinforcement learning approaches are not necessary」

と書かれています。

したがって、**公開情報から高信頼で言える結論は「勝ち提出は plain cross-entropy SFT」**です。

---

## 7. なぜこの学習が普通の SFT と少し違うのか

このパイプラインの特徴は、単に SFT を回すことではなく、**SFT の監視方法**にあります。

### 7.1 目的関数の中心は min logprob

README では「minimum logprob を最大化する」と明言されています。  
`train_sft.py` でも各ステップで

- category ごとの loss
- category ごとの min logprob
- 各 example の logprob

を保存しています。

つまり学習の考え方は、

- ただ平均 loss を見るのではなく
- **一番危ない token**
- **submission 時に崩れそうな token**

を見つけて CoT を修正する、

というものです。

### 7.2 バッチもカテゴリ分散を意識

`_stratified_batches()` により、カテゴリごとの例が各 batch に散るように構成されています。  
これは単なるシャッフルより、**カテゴリ偏りの少ない学習ログ**を得る意図が強いと読めます。

---

## 8. Kaggle の役割は「学習」ではなく「変換と評価」

README の勝ち筋では、Kaggle は **Tinker 学習の置き場**ではなく、**Tinker の出力 adapter を提出互換に直す場所**です。

`notebook_tinker.py` がやっていることは主に次です。

1. Tinker で学習した adapter を読み込む
2. 提出形式の reference adapter と config を比較する
3. key prefix を `model` から `backbone` に変換する
4. fused expert weights を per-expert `up_proj` / `down_proj` に展開する
5. Mamba の `gate_proj + x_proj` を `in_proj` に **SVD で統合**する
6. 変換後 adapter で生成・評価する

つまり、Kaggle 側のノートブックは **postprocess + validation notebook** に近い役割です。

---

## 9. なぜ Tinker のまま提出できないのか

README には、Tinker 学習出力と提出形式の差が明記されています。

### 9.1 差分

- key prefix が `model` で、提出側は `backbone`
- experts が fused `w1 / w2`
- Mamba が `gate_proj` と `x_proj` に分かれている
- `lm_head` LoRA がある

### 9.2 一番重い問題

最も重要なのは、Mamba 層の

- `gate_proj`
- `x_proj`

を提出形式の単一 `in_proj` に戻すときに、**SVD 圧縮**が必要になる点です。

README では、この変換は **lossy** で、  
「only 75% of singular mass values are captured」と書かれています。

これが training-serving misalignment の核心です。

---

## 10. README が言う training-serving misalignment とは何か

著者は、学習中にはできていたのに、提出・検証時には次のような崩れが起きると述べています。

- `\boxed` を書けない
- 直前 token の反復
- テンプレートを崩す

つまり問題は「データ戦略が弱い」よりも、**Tinker 学習結果を提出形式へ変換する段階で情報が落ちる**ことです。

README でも、これを直せば 0.877 に近づける改善余地として挙げています。

---

## 11. README 上の実運用イメージ

README の説明を、そのまま運用イメージとして短く言い換えるとこうです。

### 11.1 著者が日々やっていたこと

1. CoT を直す
2. traces を再生成する
3. Tinker で 1 回学習する
4. min logprob が悪い trace を探す
5. どの token が危ないか見る
6. CoT をさらに直す
7. Kaggle で変換して評価する

### 11.2 何が速かったのか

README では、ローカル実装では

- 約 50 秒 / step

なのに対し、Tinker では

- 約 20 分で 1 学習反復

と説明されています。

そのため、著者はローカル完全実装よりも、**Tinker を使って速く反復する方を勝ち筋として選んだ**と読めます。

---

## 12. Kaggle RTX PRO 6000 Blackwell で完全再現するなら

ここは解釈を間違えやすい点です。

### 12.1 「公開された勝ち筋そのまま」は Kaggle 学習ではない

勝ち提出の実際の流れは

- 学習: **Tinker**
- 変換と評価: **Kaggle**

です。

したがって、Kaggle RTX PRO 6000 Blackwell 上で「完全再現」したい場合、

- **勝ち筋をそのまま replay する**のではなく
- **Tinker 学習部分をローカル GPU 向けに置き換える**

必要があります。

### 12.2 再現対象として優先すべきもの

Kaggle 移植の際に、まず忠実に守るべきなのは次です。

1. **データ**  
   `reasoning.py` / `corpus.py` 系で作られた学習例
2. **SFT 設定**  
   rank 32, length 8192, 1 epoch, CE loss, LR 2e-4 線形減衰
3. **LoRA の対象**  
   attn / mlp / unembed
4. **監視指標**  
   average loss だけでなく min logprob を保存
5. **提出互換性**  
   変換不要な学習形式にするか、変換時の損失を管理する

---

## 13. まとめ

この公開物の SFT パイプラインを一言で言うと、

> **「deterministic CoT を大量に作り、Tinker で LoRA SFT し、min logprob を見ながら CoT を磨き、最後に Kaggle で提出互換へ変換する」**

です。

要点は次の 4 つです。

1. **勝ち提出の学習本体は `train_sft.py` + Tinker**
2. **勝ち筋は SFT only で、強化学習は使っていない**
3. **Kaggle は学習場所ではなく、変換・評価場所**
4. **本当のボトルネックは平均 loss より min logprob と training-serving misalignment**

---

## 参照した主要ファイル

- `A-Open-ProgressPrizePublication/README.md`
- `A-Open-ProgressPrizePublication/nemotron/train_sft.py`
- `A-Open-ProgressPrizePublication/nemotron/notebook_tinker.py`
- `A-Open-ProgressPrizePublication/nemotron/training/sft/04-08-16-14/config.json`
- `A-Open-ProgressPrizePublication/nemotron/training/sft/04-08-16-14/metrics.jsonl`
