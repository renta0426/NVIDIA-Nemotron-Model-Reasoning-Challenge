# Explicit Solver Benchmark 2026-04-20 v3

## Scope

- README.md の評価文脈に合わせ、ここでは cryptarithm 系に対する explicit family / solver の拡張だけを記録する。
- learned prompt solver の 823/823 は参考値であり、この記録の達成判定には含めない。

## Code Delta

- family record の全走査を、そのまま right 文字列へ照合するのではなく、literal token 位置の signature bucket で再利用する形へ変更した。
- composite family に safe な長さ pruning を追加した。
- family assignment の探索順を reduced map 数優先へ変更した。
- target 演算子の family について、target answer と両立しない candidate を割り当て時点で落とす pruning を追加した。
- operator-group ごとの reduced map を cache し、solver 側に failed-state memoization を追加した。
- generic `prod:*` family の plain 16 variant を priority へ追加した。
- unresolved numeric 400 群の exact descriptor 採掘に基づき、次の sibling families を追加した。

## Added Families

### Current Generic Product Families

- prod:ac_bd
- prod:ac_bd:swap
- prod:ac_bd:strip0
- prod:ac_bd:strip0swap
- prod:ad_bc
- prod:ad_bc:swap
- prod:ad_bc:strip0
- prod:ad_bc:strip0swap
- prod:ab_cd
- prod:ab_cd:swap
- prod:ab_cd:strip0
- prod:ab_cd:strip0swap
- prod:cd_ab
- prod:cd_ab:swap
- prod:cd_ab:strip0
- prod:cd_ab:strip0swap

### Earlier Composite Additions

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

### Search Memoization Check

- Command: /home/renta0426/kaggle/NVIDIA-Nemotron-Model-Reasoning-Challenge/.venv/bin/python data/symbol_rule_analysis_2026-04-20/analyze_symbol_rules.py --core-upper-bound --limit 25 --max-assignments 4096
- Result: 6 / 25 = 24.0%
- Read: reduced-map cache と failed-state memoization は wallclock 改善には寄与するが、この 25 行 slice の solved count は増えなかった。

### Current First100 Benchmark

- Command: uv run python data/symbol_rule_analysis_2026-04-20/analyze_symbol_rules.py --core-upper-bound --limit 100 --max-assignments 1024
- Result: 24 / 100 = 24.0%
- by_label: cryptarithm_guess 6, cryptarithm_deduce 18
- Current zero-op support snapshot on the same first100 slice: {0: 65, 1: 35}
- Earlier zero-op support snapshot before current prod-family state: {0: 63, 1: 36, 2: 1}
- Read: current file は support 側では改善しているが、hard rows `02e871e4`, `0babcba2`, `1545b8f1` は individually unsolved のまま。

### Hard Row Ceiling Check

- row `012cab1f` は current solver で `max_assignments=65536` まで未解決のまま。
- row-level probe では、target operator `'` に example-side family survivor はあるが、現 family 空間では non-target `>` と `]` の pairwise consistent map 自体が作れない。
- したがって少なくとも `012cab1f` 系は search ceiling ではなく family basis の不足。

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
- search memoization だけでは 25 行 slice の coverage は 24.0% のまま据え置きだった。
- current file 全体では first100 benchmark が 24 / 100 まで上がったが、support 増分の一部は solved count に直結していない。
- composite 全体 slice はまだ重く、25 行 aggregate を短時間で安定計測できていない。
- 次の主作業は、composite aggregate の wallclock をさらに削る pruning と、hard rows 00457d26 / 00c032a8 / 012cab1f 系へ当たる new family の抽出。