# v20 corrective corpus v6 mainline report

## Purpose

This bundle keeps the v20 base snapshot,
adds exact binary teacher lanes for structured, logic, permutation, and prompt-local failures,
adds anti-default1 supervision on measured hard binary IDs,
and keeps only a small boxed-surface stabilizer lane for README-consistent answer extraction.

## Selected unique rows

- `binary_structured_exact_core`: `168`
- `binary_logic_exact`: `56`
- `binary_permutation_exact`: `48`
- `binary_prompt_local_exact`: `64`
- `surface_numeral_boxed`: `34`
- `surface_cipher_boxed`: `6`
- `surface_unit_tail`: `6`
- `surface_symbol_prefix`: `4`
- `easy_gravity_fragile`: `6`

## Repeated training rows

- `binary_structured_exact_core`: `341`
- `binary_logic_exact`: `114`
- `binary_permutation_exact`: `98`
- `binary_prompt_local_exact`: `64`
- `surface_numeral_boxed`: `34`
- `surface_cipher_boxed`: `6`
- `surface_unit_tail`: `6`
- `surface_symbol_prefix`: `4`
- `easy_gravity_fragile`: `6`

## Canonical validation

- passed: `True`
- binary max think lines: `4`
- surface max think lines: `3`

## Kaggle single-file bundle

- structured family `xor(shl,shr)`: `127`
- structured family `choose(shl,shr,rol)`: `18`
- structured family `choose(shl,shr,ror)`: `20`
- structured family `majority(ror,shl,shr)`: `16`
- structured family `majority(rol,shl,shr)`: `16`
- structured family `xor(ror,shl)`: `10`
- structured family `or(rol,shr)`: `8`
- structured family `or(ror,shr)`: `8`

## Overlay supervision styles

- `anti_default1_commit`: `9`
- `exact_closure_commit`: `272`
- `exact_rule_commit`: `336`
- `surface_boxed_tail`: `56`

- path: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_mainline_bundle.jsonl`
- total examples: `8501`
- overlay examples: `673`
- total steps: `267`
- retokenized overlay problems: `392`
- retokenized overlay examples: `673`

## Guardrail watchlist

- `roman` / `roman_standard` -> `0b34281a`
- `gravity` / `gravity_half_g_t2` -> `14fd5550`
- `unit` / `unit_fixed_ratio` -> `0047365c`
- `text` / `text_monoalphabetic` -> `94643472`
- `binary` / `bit_permutation_inversion` -> `0031df9c`
