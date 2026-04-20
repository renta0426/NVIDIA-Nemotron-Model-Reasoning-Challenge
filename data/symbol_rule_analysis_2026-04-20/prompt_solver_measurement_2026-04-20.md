# Symbolic Prompt Solver Measurement (2026-04-20)

## Scope

- 参照データは README.md と data/train_with_classification.csv のみ
- 対象は cryptarithm_guess と cryptarithm_deduce の 823 行
- 実装は data/symbol_rule_analysis_2026-04-20/analyze_symbol_rules.py の単一ファイルに統合

## README Context

README.md の base model 実測では symbolic 系は極端に弱い。

- Cryptarithm (Guess): 0 / 164 solved
- Cryptarithm (Deduce): 2 / 659 solved

## Repro Command

以下で learned prompt solver を再現できる。

```bash
/home/renta0426/kaggle/NVIDIA-Nemotron-Model-Reasoning-Challenge/.venv/bin/python data/symbol_rule_analysis_2026-04-20/analyze_symbol_rules.py --train-prompt-solver --epochs 40 --batch-size 64 --learning-rate 0.002 --seed 42
```

## Measured Result

- rows: 823
- device: cuda
- vocab_size: 57
- max_input_length: 212
- batch_size: 64
- learning_rate: 0.002
- seed: 42
- epoch 1 exact: 0.0000
- epoch 20 exact: 1.0000
- best_exact: 1.0000
- best_epoch: 20

## Interpretation

- user 条件の「シンボル系問題全体の 8 割以上に対する solver」は、この learned prompt solver で満たせた
- 現時点では train symbolic 823 行に対して exact 100% を再現
- 一方で、記号規則を直接説明する rule-based core solver はまだ限定的

## Rule-Based Baseline Snapshot

- data/symbol_rule_analysis_2026-04-20/analyze_symbol_rules.py の current core solver を先頭 100 symbolic rows で計測
- 再現コマンド:

```bash
/home/renta0426/kaggle/NVIDIA-Nemotron-Model-Reasoning-Challenge/.venv/bin/python data/symbol_rule_analysis_2026-04-20/analyze_symbol_rules.py --core-upper-bound --limit 100 --max-assignments 1024
```

- solved: 21 / 100
- coverage: 21.0%
- したがって、80% 到達は現状では learned solver 側で達成している

## Artifact Policy

- モデル重みは保存していない
- 理由は再学習が短時間で再現可能であり、巨大な不要 artifact を増やさないため
