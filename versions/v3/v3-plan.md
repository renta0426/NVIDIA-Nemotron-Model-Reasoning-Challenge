# v3 plan

## Goal

`README.md` の prompting / fine-tuning の余地と、`DATA_ANALYSIS_REPORT.md` の template-aware 学習示唆を使って、direct answer だけでなく template-aware trace supervision まで与える高精度候補を作る。

## Main changes

- repository rule に合わせて implementation を single-file に再構成する
- `trl.SFTTrainer` + `target_modules="all-linear"`
- metric と同じ user prompt を保ったまま、assistant 側だけ `direct -> mixed trace` の 2 段 SFT にする
- trace には `Task type` / `Answer format` / `Reasoning plan` を入れて、短テンプレ benchmark に latent task decomposition を教える
- trace で completion が長くなるため、この版だけ `MAX_LENGTH=640` に上げる
- デフォルトは 4bit all-linear LoRA で実行可能性を残す

## Why this is valuable

- 既存 baseline 群はほぼ final answer だけを教師にしている
- metric 側は `enable_thinking=True` を使うので、構造化された assistant completion を学ばせる価値がある
- 6 テンプレ + 複数 answer 型に対して、テンプレ判定と format 安定化を同時に学ばせられる

## Code layout

- `code/train.py`: trace-supervision training / packaging entrypoint with all helpers inlined for standalone execution
