# v4 plan

## Goal

データ分析で見えた hard templates / 出力形式の揺れ / 長め prompt をまとめて難例として扱い、QLoRA のまま重点学習する実戦版を作る。

## Main changes

- repository rule に合わせて implementation を single-file に再構成する
- 4bit QLoRA + explicit target modules で現実的なメモリ帯を維持する
- template / answer_type / prompt 長 / brace をもとに `difficulty_score` を作る
- stage1 は full train を難例・format 難例で増幅、stage2 は難例 subset だけで polish する
- validation も hard subset を別で持ち、難所でモデル選択しやすくする
- `MAX_LENGTH=384` を維持して短コンテキスト性を活かす

## Why this is valuable

- レポート上のボトルネックは bit / text / symbol と output formatting
- ベースラインの一様学習では、hidden test の harder slice に弱い可能性が高い
- メモリ帯を大きく増やさずに精度改善を狙える

## Code layout

- `code/train.py`: hard-example-mining training / packaging entrypoint with all helpers inlined for standalone execution
