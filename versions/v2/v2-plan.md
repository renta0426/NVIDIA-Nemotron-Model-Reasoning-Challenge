# v2 plan

## Goal

`baseline/` の高スコア notebook の学びを取り込み、より高スコアを狙う攻めた別版を作る。

## Main changes

- `trl.SFTTrainer` を採用する
- `target_modules="all-linear"` を使う
- easy templates -> full dataset の 2 段 curriculum を入れる
- prompt 形式は submission metric と一致させる
- デフォルトは bf16 full-model LoRA、必要なら 4bit に切り替え可能にする

## Code layout

- `code/train.py`: v2 training / packaging entrypoint
- `code/nemotron_reasoning_common.py`: shared helpers copied for version-local execution
