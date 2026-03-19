# v2 plan

## Goal

`baseline/` の高スコア notebook の学びを取り込み、より高スコアを狙う攻めた別版を作る。

## Main changes

- `trl.SFTTrainer` を採用する
- `target_modules="all-linear"` を使う
- easy templates -> full dataset -> hard templates の 3 段 curriculum を入れる
- prompt 形式は submission metric と一致させる
- データ分析で学習テキスト長が近似 `p95=137` に収まることを確認し、`MAX_LENGTH` を 1024 -> 384 に圧縮する
- デフォルトは bf16 full-model LoRA、必要なら 4bit に切り替え可能にする

## Code layout

- `code/train.py`: v2 training / packaging entrypoint
- `code/nemotron_reasoning_common.py`: shared helpers copied for version-local execution
