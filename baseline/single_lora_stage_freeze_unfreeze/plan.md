# 単一LoRA内の段階 Freeze/Unfreeze 実験計画

## 1. 文書の目的

この文書は、`baseline/nemotron-sft-lora-with-cot-v2` 系の broad generalist 学習を土台にしつつ、**単一の LoRA adapter の中で段階的に trainable 層を切り替える**ことで hard family を補修する実験計画をまとめたものである。

本計画の主題は次の 1 点である。

- `in_proj/out_proj/up_proj/down_proj` を使う broad generalist 学習を維持しながら、後段で `q_proj/k_proj/v_proj/o_proj` の attention 系だけを追加で適応させ、binary と symbol の content error を狙って削る

この計画は、**LoRA を 2 本作る案ではなく、1 本の LoRA の中で freeze / unfreeze を切り替える案**を扱う。

## 2. 背景

### 2.1 競技 README 前提

`README.md` の Evaluation は Accuracy であり、最終回答は `\boxed{}` 優先抽出で評価される。提出物は `submission.zip` に格納された Nemotron 互換 LoRA adapter であり、`max_lora_rank` は 32 である。

このため、今回の設計では次を守る。

1. 最終成果物は単一 adapter とする
2. broad family を壊して局所改善だけ取る設計は避ける
3. binary では boxed close を維持した上で content error を減らすことを優先する

### 2.2 現在の broad generalist の位置づけ

`baseline/nemotron-sft-lora-with-cot-v2/result/origin/reports/phase0_eval_summary.md` では、origin broad generalist は local320 で `249/320 = 0.7781` を出している。family 別では次である。

- `binary = 29/60 = 0.4833`
- `gravity = 50/50 = 1.0000`
- `roman = 50/50 = 1.0000`
- `symbol = 22/60 = 0.3667`
- `text = 49/50 = 0.9800`
- `unit = 49/50 = 0.9800`

特に binary metrics では、次が強い資産である。

- `boxed_extraction_success_rate = 0.8333`
- `regex_exact_rate = 0.8333`
- `leading_zero_retention_rate = 0.8333`
- `format_failure_rate = 0.1667`

この broad generalist は、hard family の抜けはあるが、**easy family の維持と binary の boxed close の習慣**をすでに持っている。

### 2.3 v3f が示した改善方向

`baseline/nemotron-sft-lora-with-cot-v2/result/v3f/phase0_offline_eval/reports/phase0_eval_summary.md` と `baseline/nemotron-sft-lora-with-cot-v2/result/v3f/v3f_effects_risks_and_next_strategy.md` から見えるのは次である。

1. overall は origin と同じ `249/320 = 0.7781`
2. symbol watch は `22/60 -> 24/60` に改善
3. binary hard watch は `29/60 -> 27/60` に微退行
4. ただし binary の boxed path は強化され、`boxed_extraction_success_rate = 1.0`、`format_failure_rate = 0.0` になった
5. binary の真の弱点は boxed 崩れではなく `format_ok_content_wrong_rate = 0.55` という **content miss の増加**だった

さらに `baseline/nemotron-sft-lora-with-cot-v2/result/v3f/phase0_offline_eval_binary_bias_specialized/reports/binary_bias_specialized_eval_summary.md` では、specialized 563 問で v3f は `0.3375 -> 0.4227` へ改善している。特に次が大きく伸びた。

- `dominant_structured_safe = 0.2917 -> 0.4417`
- `dominant_structured_abstract = 0.2111 -> 0.3111`

一方で次は弱いままである。

- `supported_not_structured = 0.0545 -> 0.0182`

したがって、v3f の教訓は次の 2 つである。

1. boxed 強化だけでは binary broad robustness は改善しない
2. structured / abstract だけに強く寄せると non-structured 側の content miss が残る

### 2.4 specialist 系失敗が示した禁止事項

`baseline/cot/phase0_offline_eval/result/2_1_merge_lora/reports/phase2_binary_specialist_result2_1_merge_lora_deep_analysis.md` は、binary-only specialist が壊れ方の具体例を示している。

`result/2` から `result/2_1_merge_lora` への変化は次だった。

- overall: `0.7094 -> 0.6250`
- binary: `13/60 -> 10/60`
- gravity: `0.9400 -> 0.7800`
- unit: `1.0000 -> 0.7800`

binary metrics も悪化している。

- `boxed_extraction_success_rate = 0.2 -> 0.1333`
- `leading_zero_retention_rate = 0.4 -> 0.2`
- `format_failure_rate = 0.8 -> 0.8667`

この実験は次の禁止事項を示す。

1. binary-only specialist を broad generalist の代わりに本体へ据えない
2. all-linear で specialist を強く当てない
3. easy family を再学習で巻き込んで壊す設計を避ける
4. 長文化と fallback 増加を招く後段学習を避ける

## 3. なぜ「単一LoRA内の段階 freeze/unfreeze」なのか

LoRA を 2 本に分ける案では、提出形式、adapter merge、rank 管理、推論時整合性の問題が増える。競技 README の提出前提と、`baseline/nemotron-sft-lora-with-cot-v2` の現在の notebook 保存フローを考えると、最終成果物は単一 adapter の方が自然である。

このため、本計画では最初から 1 本の LoRA を **8 層 union** で作り、その中で段階的に trainable パラメータを切り替える。

対象 union は次である。

- attention: `q_proj`, `k_proj`, `v_proj`, `o_proj`
- MLP/MoE: `up_proj`, `down_proj`
- Mamba: `in_proj`, `out_proj`

`how-to-get-started-transformers.md` でも Nemotron 実装に合わせる target_modules としてこの 8 層が整理されている。

## 4. 本計画の基本戦略

### 4.1 概要

単一 LoRA adapter を最初から 8 層で作る。ただし、学習は 2 段階から 3 段階で行う。

- Stage 1: `in_proj/out_proj/up_proj/down_proj` のみ trainable にして broad generalist を作る
- Stage 2: Stage 1 の 4 層を凍結し、`q_proj/k_proj/v_proj/o_proj` のみ trainable にして route-sensitive 補修を行う
- Stage 2.5: 必要時のみ、Stage 2 後に broad drift を戻す短い re-anchor を行う

### 4.2 戦略の狙い

この順序にする狙いは次の通りである。

1. Stage 1 で broad family の boxed close と easy family の高精度を先に固定する
2. Stage 2 では attention 系だけを動かし、参照・対応付け・変換判断の補修に集中する
3. Stage 2 で Mamba / MoE 系まで再更新すると broad behavior ごと崩れるため、それを避ける

### 4.3 なぜ Stage 2 を narrow にするか

既存結果では、壊れる run は次の特徴を持つ。

1. specialist 化しすぎる
2. binary-only へ寄りすぎる
3. 長文化する
4. boxed close よりも content miss を増やす
5. gravity / unit / text を巻き添えにする

したがって Stage 2 は、**small, narrow, verified, low-LR, short-sequence** でなければならない。

## 5. LoRA の器

### 5.1 target_modules

LoRA の器は最初から次の 8 層 union とする。

```python
target_modules=[
    "q_proj",
    "k_proj",
    "v_proj",
    "o_proj",
    "up_proj",
    "down_proj",
    "in_proj",
    "out_proj",
]
```

正規表現で実装してもよいが、freeze / unfreeze 時の判定を単純にするため、ここでは suffix list の方が扱いやすい。

### 5.2 rank / alpha / dropout

初期案は現行 broad notebook と合わせる。

- `r = 32`
- `lora_alpha = 32`
- `lora_dropout = 0.05`
- `bias = "none"`

理由は、現行 broad run との比較軸を target_modules と学習段階設計に集中させるためである。ここで同時に rank や alpha を触ると、freeze/unfreeze の効果を切り分けにくくなる。

## 6. Stage 1 設計

### 6.1 役割

Stage 1 の役割は broad generalist 形成である。ここでは次の 4 層のみ trainable にする。

- `in_proj`
- `out_proj`
- `up_proj`
- `down_proj`

attention 系 `q/k/v/o` の LoRA パラメータはこの時点では存在するが `requires_grad=False` にしておく。

### 6.2 データ

Stage 1 データは、現在 `cuda-train-data-analysis-v1/proof_first_solver_factory_routing/plan.md` に沿って作成している broad mix をそのまま主系とする。

この plan が固定している方針は次である。

1. broad strength を維持する
2. binary と symbol の content error を下げる
3. binary の boxed close を守る
4. exact-route verified rows を主 lane にする
5. answer-only は低比率補助 lane にする

したがって Stage 1 では、今の学習中の broad routing データを baseline に据えるのが最も自然である。

### 6.3 ハイパーパラメータ

初期案としては、現行 notebook の broad 設定をそのまま使う。

- `num_train_epochs = 2`
- `per_device_train_batch_size = 1`
- `gradient_accumulation_steps = 8`
- `learning_rate = 1e-4`
- `lr_scheduler_type = "cosine"`
- `warmup_ratio = 0.05`
- `max_length = 4096`
- `packing = False`

この段は学習全体の大半を占める本体なので、ここで broad strength を先に作る。

### 6.4 Stage 1 で守る指標

最低限次を守る。

1. easy family を壊さない
2. binary boxed habit を壊さない
3. symbol numeric_2x2 を落としすぎない

特に次を Stage 1 の資産とみなす。

- `text >= 49/50`
- `unit >= 49/50`
- `gravity >= 49/50`
- `roman = 50/50`
- binary `boxed_extraction_success_rate` を高く保つ

## 7. Stage 2 設計

### 7.1 役割

Stage 2 は specialist 本学習ではなく、**attention-only 補修**である。

ここでは次のみ trainable にする。

- `q_proj`
- `k_proj`
- `v_proj`
- `o_proj`

Stage 1 の 4 層は完全凍結する。

### 7.2 Stage 2 の狙い

狙いは次の 3 点に限定する。

1. binary60 の `format_ok_content_wrong` を下げる
2. `supported_not_structured` と `abstract` の content miss を補修する
3. symbol の `numeric_2x2` を維持または改善する

ここで重要なのは、Stage 2 は **broad family を再学習する場所ではない** という点である。

### 7.3 データ方針

Stage 2 データは broad mix をそのまま流用しない。ここでは route-sensitive 補修用の小さなデータセットを別に作る。

主 lane は次である。

1. binary exact-route verified
2. binary structured abstract cleanup
3. binary not-formula 専用 teacher
4. symbol `numeric_2x2` verified

補助 lane は次である。

1. binary answer-only keep のうち query answer が強く一意なもの
2. text verified のごく少量

原則として除外するものは次である。

1. gravity broad rows
2. unit broad rows
3. roman broad rows
4. unresolved manual rows
5. specialist 的に長文化しやすい粗い closure-only rows の大量投入

### 7.4 binary データの優先順位

binary は v3f の既存知見を踏まえ、優先順位を次で固定する。

1. `dominant_structured_safe`
2. `dominant_structured_abstract`
3. `supported_not_structured`
4. `supported_affine_xor`
5. `supported_bijection`

この順序の意味は次である。

- safe / abstract は v3f で伸びたので、attention 補修で勝ちを壊さずに content を寄せる対象
- `supported_not_structured` は v3f で特に落ちたので、Stage 2 の最重要補修対象
- affine / bijection は broad generalist が元からある程度持っているため、過剰比重を避ける

### 7.5 symbol データを混ぜる理由

symbol `numeric_2x2` は origin から v3f で `22/40 -> 24/40` に伸びている。これは、binary だけに寄せず route-sensitive 変換判断を補修すると symbol にも効く可能性があることを示している。

したがって Stage 2 は binary-only にしない。symbol の verified `numeric_2x2` を一定量混ぜることで、attention 補修を「bit family 専用」ではなく「参照・変換整合性の補修」として学習させる。

### 7.6 Stage 2 データ構成の初期案

初期案は以下とする。

- binary verified exact-route: `55%`
- binary verified abstract cleanup: `15%`
- binary verified not-formula 専用 teacher: `10%`
- symbol verified numeric_2x2: `15%`
- answer-only keep の厳選補助: `5%`

manual は `0%` を原則とする。

### 7.7 Stage 2 ハイパーパラメータ

Stage 2 は short corrective phase として設計する。

初期案は次である。

- `learning_rate = 2e-5`
- `num_train_epochs = 1` 相当未満
- 実運用では epoch 固定より `max_steps` 管理を優先
- Stage 1 optimizer steps の `10%` から `15%` を上限とする
- `max_length = 1536` または `2048`
- `packing = False`
- `warmup_ratio = 0.03`

ここで sequence length を短くする理由は、v2 の text-shift 監査と specialist 失敗記録の両方で、長文化した行ほど崩れやすかったからである。

### 7.8 Stage 2 の trainable 制御

trainable 制御は adapter 名ではなく suffix ベースで行う。

概念的には次である。

```python
STAGE1_TRAINABLE = ("in_proj", "out_proj", "up_proj", "down_proj")
STAGE2_TRAINABLE = ("q_proj", "k_proj", "v_proj", "o_proj")

for name, param in model.named_parameters():
    if "lora_" not in name:
        param.requires_grad = False
        continue
    param.requires_grad = any(token in name for token in STAGE2_TRAINABLE)
```

Stage 1 と Stage 2 の切り替えは、optimizer を作り直し、scheduler も新しく切る。

## 8. Stage 2.5 設計

### 8.1 必要な場合だけ使う

Stage 2.5 は常設ではない。Stage 2 後に broad drift が見えた場合のみ短く入れる。

### 8.2 目的

1. `general_stable` の維持
2. gravity / unit / text の accidental drift の補修
3. binary attention 補修を消さずに easy family を戻す

### 8.3 データ

Stage 2.5 データは broad verified のみとする。answer-only は基本的に入れない。

### 8.4 trainable

Stage 2.5 でも trainable は `q/k/v/o` のままにする。Stage 1 の 4 層は再度開けない。

### 8.5 長さと学習量

- Stage 2 の `20%` 未満
- `learning_rate = 1e-5` 程度
- `max_length = 1024` から `1536`

この段は「戻し」なので、強く回してはいけない。

## 9. 並列実験の切り方

この計画は、1 本ずつ順に回すより 3 本以上の parallel 比較で切るべきである。

### 9.1 本命 run

- Stage 2 trainable: `q/k/v/o`
- Stage 2 data: binary verified + symbol verified の混合
- Stage 2 LR: `2e-5`
- Stage 2 steps: Stage 1 の `12%`

狙い:

- binary broad robustness の回復
- symbol `numeric_2x2` の維持または改善

### 9.2 保守 run

- Stage 2 trainable: `v/o` のみ
- Stage 2 data: 本命と同じ
- Stage 2 LR: `2e-5`
- Stage 2 steps: Stage 1 の `12%`

狙い:

- q/k を触らずに broad drift を抑える
- readout 側だけの attention 補修でどこまで改善できるかを確認する

### 9.3 binary 寄り run

- Stage 2 trainable: `q/k/v/o`
- Stage 2 data: binary verified 主、symbol は少量
- Stage 2 LR: `1e-5`
- Stage 2 steps: Stage 1 の `8%`

狙い:

- v3f の binary 穴埋めを優先
- easy family を壊さず binary の content miss を減らせるかを見る

### 9.4 optional run

- Stage 2.5 を追加
- trigger は Stage 2 後の broad drift

## 10. 成功判定

この計画の成否は、binary だけでなく broad stability を同時に満たすかで判断する。

### 10.1 必須ゲート

1. `general_stable` が `198/200` を下回らない
2. binary60 の `boxed_extraction_success_rate = 1.0` を維持する
3. binary60 の `format_failure_rate = 0.0` を維持する
4. binary60 の `format_ok_content_wrong_rate` を v3f の `0.55` より下げる
5. symbol watch の `numeric_2x2` を `24/40` 未満に落とさない

### 10.2 強い成功条件

1. binary60 が `27/60` を超える
2. `supported_not_structured` が `1/55` から有意に改善する
3. `dominant_structured_safe` と `dominant_structured_abstract` の v3f gain を失わない
4. overall local320 が `249/320` を超える

## 11. 想定される失敗形

### 11.1 Stage 2 が specialist 再演になる

兆候:

- gravity / unit / text が同時に落ちる
- binary 自体も伸びない

対応:

- Stage 2 データをさらに narrow にする
- answer-only 比率を下げる
- q/k を閉じて v/o のみへ縮める

### 11.2 binary の boxed は保つが content miss が増える

兆候:

- `boxed_extraction_success_rate = 1.0` のまま
- `format_ok_content_wrong_rate` だけ上がる

対応:

- Stage 2 length をさらに短くする
- not-formula / abstract の teacher を見直す
- symbol を残しつつ binary-only 比率を下げる

### 11.3 長文化して fallback へ落ちる

兆候:

- mean raw output chars 増加
- fallback 型誤答が増える

対応:

- Stage 2 sequence length を 1536 以下へ下げる
- closure-first teacher の比率を増やす
- Stage 2 steps を削る

### 11.4 Stage 2 が効かず差が出ない

兆候:

- binary / symbol ともにほぼ不変

対応:

- Stage 2 data の route purity を上げる
- symbol verified を増やす
- q/k/v/o 全開版から q/k 抑制版へ比較する

## 12. 実装上の注意

### 12.1 単一 adapter を維持する

最終提出を単純にするため、adapter は常に 1 本のまま扱う。別 adapter を load して merge する方式は本計画では採らない。

### 12.2 optimizer は段ごとに作り直す

Stage 切り替え時は、`requires_grad` を変えた後に optimizer と scheduler を作り直す。前段の optimizer state をそのまま持ち越すと、凍結・解凍の影響が見えにくくなる。

### 12.3 checkpoint 記録

各段の終了時点で次を必ず保存する。

1. adapter weights
2. adapter config
3. stage 設定 JSON
4. 評価 summary
5. row-level artifact

### 12.4 ログに残すべき実測

各 run ごとに必須で残す。

1. Stage 1 / Stage 2 / Stage 2.5 の trainable parameter 数
2. 各段の optimizer step 数
3. wallclock
4. peak VRAM
5. local320 overall
6. general_stable
7. binary_hard
8. symbol_watch
9. binary bias specialized summary

## 13. 今回の推奨初手

最初の 1 本としては、次が最も筋がよい。

### 初手推奨

- LoRA 器: 8 層 union
- Stage 1 trainable: `in/out/up/down`
- Stage 1 data: 現在の proof-first broad routing データ
- Stage 2 trainable: `q/k/v/o`
- Stage 2 data: binary verified exact-route + abstract cleanup + not-formula + symbol verified numeric_2x2
- Stage 2 LR: `2e-5`
- Stage 2 steps: Stage 1 の `12%`
- Stage 2 max_length: `1536`
- Stage 2 answer-only 比率: `5%` まで
- Stage 2.5: broad drift が見えた場合のみ

この初手の意味は、**現行の broad generalist がすでに持っている boxed close と easy family strength を土台にし、attention を hard family の content repair 専用に使う**ことにある。

## 14. 本計画の位置づけ

この計画は、`proof_first_solver_factory_routing/plan.md` の augmentation-first 方針と整合しつつ、`baseline/nemotron-sft-lora-with-cot-v2` 系が実際に観測した次の 2 種類の知見を統合したものである。

1. v3f が示した「structured 改善はできるが content miss が残る」という知見
2. binary specialist が示した「specialist 化しすぎると broad も target も壊す」という知見

したがって、本計画の本質は specialist を強く当てることではない。**Stage 1 で broad generalist を確立し、Stage 2 で attention を narrow corrective lane にのみ使うこと**が本質である。