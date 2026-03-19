# v6 plan

## Goal

`README.md` が許す synthetic data generation を、データ特性に合う安全な形で使い、prompt 内 example order augmentation による頑健化を狙う。

## Main changes

- repository rule に合わせて implementation を single-file に再構成する
- 各 template の prompt から example block を抽出し、例示順だけを並べ替えた augment prompt を追加する
- answer はそのままなのでラベルノイズを増やさずに data augmentation できる
- stage1 は augmented train、stage2 は original train に戻して分布ずれを抑える
- `trl.SFTTrainer` + `all-linear` を使って notebook 系 baseline の強みを流用する
- `MAX_LENGTH=384` を維持する

## Why this is valuable

- この benchmark は few-shot 的な例示から規則を読むタスクで、例示順への過適合は避けたい
- 短コンテキストなので augmentation で token 長が膨れない
- synthetic augmentation の中でも、答えを壊しにくい高安全度の実験

## Code layout

- `code/train.py`: prompt-augmentation training / packaging entrypoint with all helpers inlined for standalone execution
