# v8 plan

## Goal

`SYNTHETIC_DATA_AUGMENTATION_POLICY.md` を守りつつ、visible `test.csv` をそのまま validation 扱いせず、`train_only` な合成 manifest を裏側に持つ prompt-only projection として `data/test.csv` を増強する。

## Main changes

- `data/test.csv` の元 3 行は `data/test.visible.csv` に退避する
- `data/train.csv` と突き合わせて answer を復元し、label-preserving な prompt example order augmentation を作る
- 合成行は `synthetic_id`, `template_family`, `generator_version`, `rule_spec`, `dedup_hash`, `split_policy=train_only` などの必須メタデータを持つ manifest に保存する
- `data/test.csv` は manifest から `id,prompt` だけを投影した prompt-only ビューとして再構成する
- 実装は repository rule に合わせて single-file generator として `code/train.py` にまとめる

## Why this is valuable

- visible `test.csv` は `train.csv` と重複しており、そのまま評価セットとして使うのは危険
- ただし prompt surface を少量だけ増やした test-like pool は、submission smoke test や qualitative check には使いやすい
- answer を新規生成せず label-preserving augmentation に限定するので、ポリシー上のラベルノイズを避けやすい

## Code layout

- `code/train.py`: policy-compliant test-pool generator / manifest writer / projection writer
