# v7 plan

## Goal

データセットの 6 系列という構造を正面から使い、generalist adapter と hard-template specialist adapter を作って最後に merge する最上位候補を作る。

## Main changes

- repository rule に合わせて implementation を single-file に再構成する
- まず全データで general adapter を学習する
- その general adapter から bit / text / symbol の specialist adapter を継続学習する
- final submission は general + specialists を重み付き平均した 1 本の LoRA adapter
- notebook 系 baseline の `all-linear` を使うが、4bit を許して計算量を抑える
- `MAX_LENGTH=384` を維持する

## Why this is valuable

- レポート上、この benchmark は事実上 6 つの合成タスクの混合データ
- ただし提出は 1 adapter に限られるため、merge が task-aware 最適化と提出要件の両立策になる
- hard templates に追加容量を割きつつ、general side の安定性も残せる

## Code layout

- `code/train.py`: specialist-merge training / packaging entrypoint with all helpers inlined for standalone execution
