# v1 plan

## Goal

現在の `code/Nemotron Reasoning Challenge - QLoRA Baseline.py` を土台に、メモリ使用量を大きく悪化させずに精度改善を狙う実用版を作る。

## Main changes

- metric と同一の prompt 形式を維持する
- template + answer_type ベースの validation split を使う
- 100 step 打ち切りをやめ、実質 1 epoch 学習にする
- LoRA を `r=24, alpha=48` に増やす
- Nemotron patch / packaging / local quick validation を共通化する

## Code layout

- `code/train.py`: v1 training / packaging entrypoint
- `code/nemotron_reasoning_common.py`: dataset, prompt, patch, eval helpers
