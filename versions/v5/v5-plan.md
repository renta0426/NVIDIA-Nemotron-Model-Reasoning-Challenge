# v5 plan

## Goal

小規模かつテンプレ均衡なデータで split 依存が強く出る点を利用し、複数 fold の adapter を学習して 1 本に merge する fold-soup 版を作る。

## Main changes

- repository rule に合わせて implementation を single-file に再構成する
- 3-fold の template + answer_type stratified split を作る
- 各 fold ごとに practical 4bit QLoRA adapter を順番に学習する
- fold の `eval_loss` から重みを作って adapter weight average を行う
- 最終的には competition 仕様どおり 1 本の merged LoRA zip にまとめる
- `MAX_LENGTH=384` を維持する

## Why this is valuable

- 可視 test が無意味なので、validation split の取り方でかなりぶれやすい
- hidden test への頑健性を上げるには 1 split 依存を避けたい
- final artifact は 1 adapter のままなので提出要件に合う

## Code layout

- `code/train.py`: fold-soup training / merge / packaging entrypoint with all helpers inlined for standalone execution
