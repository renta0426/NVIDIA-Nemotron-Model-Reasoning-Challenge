# v1 plan

## Goal

現在の `code/Nemotron Reasoning Challenge - QLoRA Baseline.py` を土台に、メモリ使用量を大きく悪化させずに精度改善を狙う実用版を作る。

## Main changes

- metric と同一の prompt 形式を維持する
- template + answer_type ベースの validation split を使う
- 100 step 打ち切りをやめ、実質 1 epoch 学習にする
- データ分析で学習テキスト長が近似 `p95=137` に収まることを確認し、`MAX_LENGTH` を 1024 -> 384 に圧縮する
- bit / text / symbol の hard templates を軽く増幅して学習配分を寄せる
- LoRA を `r=24, alpha=48` に増やす
- Nemotron patch / packaging / local quick validation を共通化する

## Code layout

- `code/train.py`: v1 training / packaging entrypoint
- `code/nemotron_reasoning_common.py`: dataset, prompt, patch, eval helpers
