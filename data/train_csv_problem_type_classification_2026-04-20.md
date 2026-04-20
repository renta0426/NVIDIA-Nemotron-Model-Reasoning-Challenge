# Train CSV Problem Type Classification (2026-04-20)

## Input Scope

- Source data: data/train.csv
- Reference counts: README.md tail section and discussion/Are problem types the same for train and test?.md
- Original data file was not modified

## Major Categories

- bit_manipulation: 1602
- cipher: 1576
- gravity: 1597
- unit_conversion: 1594
- numeral: 1576
- equation: 1555

## Equation Split Rules

- equation_numeric_deduce: numeric equation prompts where the target operator appears in the example equations.
- equation_numeric_guess: numeric equation prompts where the target operator does not appear in the example equations.
- cryptarithm_guess: symbolic equation prompts with at least 4 examples, exactly 1 target symbol unseen anywhere in the example equations, and at most 1 target symbol that appeared only on example right-hand sides.
- cryptarithm_deduce: remaining symbolic equation prompts.

## Final Label Counts

- cryptarithm_guess: 164
- cryptarithm_deduce: 659
- equation_numeric_guess: 136
- equation_numeric_deduce: 596
- bit_manipulation: 1602
- cipher: 1576
- gravity: 1597
- unit_conversion: 1594
- numeral: 1576

## Generated Artifacts

- Classification CSV: /home/renta0426/kaggle/NVIDIA-Nemotron-Model-Reasoning-Challenge/data/train_with_classification.csv
