# cuda-train-data-analysis-v1 binary hybrid consensus recovery

## Purpose

Test whether a conservative hybrid family can recover some `binary_low_gap` rows that were still manual after the existing exact solvers, under the `README.md` accuracy-first metric.

## Scope

- candidate slice:
  - `bit_no_candidate_positions = 1`
  - `bit_multi_candidate_positions = 0`
  - `num_examples >= 7`
- idea:
  - treat `7` output bits as fixed copy/invert mappings from `bit_candidate_signature`
  - search simple unary / 2-bit / 3-bit boolean completions for the single missing output bit
  - accept only rows where:
    - all matching completions predict the **same full query output**
    - all matching completions use the **same 2-input varset**

## Decision

- total `bit_hybrid_consensus_ready` rows: `45`
- of those, already `verified_trace_ready` by stricter existing solvers: `25`
- **newly promoted to `answer_only_keep`: `20`**
- no new `verified_trace_ready`
- no new `exclude_suspect`

## Why this stays answer-only, not trace-ready

- the missing-bit function itself is still not uniquely identified
- what is unique is the **query output**, because every matching completion over the accepted varset agrees on the same byte
- that is strong enough for safe answer supervision, but not strong enough to claim a unique reasoning trace

## Net effect on binary counts

- before this recovery:
  - `381 verified / 0 answer_only / 1202 manual / 19 exclude`
- after this recovery:
  - `381 verified / 20 answer_only / 1186 manual / 15 exclude`
- net change:
  - `+20 answer_only`
  - `-16 manual`
  - `-4 exclude`

## Newly recovered rows

| id | varset | answer |
| --- | --- | --- |
| `084a4496` | `i1,i5` | `11000111` |
| `48db5ccf` | `i1,i8` | `01101110` |
| `4c237bf3` | `i1,i8` | `10000011` |
| `a8887238` | `i1,i8` | `00101000` |
| `07434d56` | `i1,i8` | `11011001` |
| `1c7c1246` | `i1,i8` | `00100110` |
| `368f20dd` | `i1,i8` | `10000101` |
| `41beb86c` | `i1,i8` | `01010000` |
| `5a0c141c` | `i1,i8` | `01010000` |
| `62dba403` | `i1,i8` | `10011001` |
| `6686f0de` | `i1,i8` | `10110111` |
| `7a5d00a7` | `i1,i8` | `11110011` |
| `d4e29ed7` | `i1,i8` | `11111011` |
| `d8ef1dae` | `i1,i8` | `11011011` |
| `e16e7f6d` | `i1,i8` | `01110100` |
| `934a2c55` | `i2,i8` | `00101011` |
| `1deaf759` | `i4,i8` | `10100111` |
| `a41a3626` | `i5,i8` | `10111011` |
| `eeb60061` | `i5,i8` | `00000101` |
| `3ebd80e6` | `i6,i8` | `00011010` |

## Interpretation

This recovery is different from the earlier exact binary solvers. It does **not** discover a unique full transform; instead, it finds rows where the remaining ambiguity collapses to one query output anyway. That makes it a strong conservative `answer_only_keep` source and a meaningful improvement for binary curation without relaxing the `README.md` accuracy-first standard.
