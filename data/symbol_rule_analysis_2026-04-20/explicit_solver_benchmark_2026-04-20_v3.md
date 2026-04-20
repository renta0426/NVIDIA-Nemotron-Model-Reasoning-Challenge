# Explicit Solver Benchmark 2026-04-20 v3

## Scope

- README.md の評価文脈に合わせ、ここでは cryptarithm 系に対する explicit family / solver の拡張だけを記録する。
- learned prompt solver の 823/823 は参考値であり、この記録の達成判定には含めない。

## Code Delta

- family record の全走査を、そのまま right 文字列へ照合するのではなく、literal token 位置の signature bucket で再利用する形へ変更した。
- composite family に safe な長さ pruning を追加した。
- family assignment の探索順を reduced map 数優先へ変更した。
- target 演算子の family について、target answer と両立しない candidate を割り当て時点で落とす pruning を追加した。
- unresolved numeric 400 群の exact descriptor 採掘に基づき、次の sibling families を追加した。

## Added Families

- copymix|scalar|x+y|pad2|c|expr_first
- copymix|scalar|x+y|pad2|a|expr_first
- mask|scalar|x+y|pad2|NNc
- mask|scalar|x+y|pad2|NNa
- concat|x+y|nat|y//x|pad2|strip0
- concat|x+y|pad2|y//x|nat|strip0
- concat|x+y|pad2|y//x|pad2|strip0
- mix|y//x|nat|sum:ac_bd:strip0swap|scalar_first

## Measurements

### Baseline Slice

- Command: /home/renta0426/kaggle/NVIDIA-Nemotron-Model-Reasoning-Challenge/.venv/bin/python data/symbol_rule_analysis_2026-04-20/analyze_symbol_rules.py --core-upper-bound --limit 25 --max-assignments 1024
- Result: 6 / 25 = 24.0%
- by_label: cryptarithm_guess 2, cryptarithm_deduce 4
- Same-session earlier snapshot before search-order/pruning update: 5 / 25 = 20.0%

### Baseline-Solved IDs In First 25 Symbolic Rows

- 0133bcec
- 02a04b59
- 02b8d816
- 03a3437f
- 042f1e53
- 0454705a

### Composite Regression Check

- Known composite-only row 08f6216d remains solvable.
- Assignment: {'*': 'concat|x-y|nat|x//y|nat|strip0', '+': 'swap_halves', '-': 'y%x'}

## Numeric Unresolved Mining Snapshot

- Sample: unresolved equation_numeric_deduce operator groups, first 400 groups.
- Top new concat siblings: concat|x+y|nat|y//x|pad2|strip0, concat|x+y|pad2|y//x|nat|strip0, concat|x+y|pad2|y//x|pad2|strip0 with 3 hits each.
- Top new copymix siblings: copymix|scalar|x+y|pad2|c|expr_first, copymix|scalar|x+y|pad2|a|expr_first with 2 hits each.
- Top new mask siblings: mask|scalar|x+y|pad2|NNc, mask|scalar|x+y|pad2|NNa with 2 hits each.
- Top new mix sibling: mix|y//x|nat|sum:ac_bd:strip0swap|scalar_first with 2 hits.

## Current Read

- baseline 側の 25 行 slice は 20.0% から 24.0% へ改善した。
- composite 全体 slice はまだ重く、25 行 aggregate を短時間で安定計測できていない。
- 次の主作業は、composite aggregate の wallclock をさらに削る pruning と、hard rows 00457d26 / 00c032a8 / 012cab1f 系へ当たる new family の抽出。