# cuda-train-data-analysis-v1 binary structured-byte manual exact curation

## Purpose

Re-read the last structured-byte residual rows whose prompts already admit a single exact structured formula, but which were still blocked because:

- the exact formula had only singleton support, or
- the broader exact / abstract family was contaminated elsewhere in train.

This is a **manual prompt-level override** pass, not a new broad family rule.

## Verified by direct prompt reading

The following rows were promoted to `verified_trace_ready` after confirming that the prompt examples themselves already specify one exact structured transform and the query answer matches it.

| id | query | answer | exact formula | why it was still manual before |
| --- | --- | --- | --- | --- |
| `1bf84ce3` | `10011001` | `00000000` | `and(nibble_swap,ror2)` | singleton exact family |
| `2aa6ce6a` | `10000011` | `11010001` | `xor(ror1,shr3)` | contaminated abstract family `xor(ror,shr)` |
| `26df9536` | `11001110` | `11101010` | `xor(ror3,shr2)` | contaminated abstract family `xor(ror,shr)` |
| `d5a28743` | `00101110` | `00000011` | `and(ror1,ror2)` | singleton exact family |
| `9bfb1cc6` | `00110110` | `10001101` | `ror2` | exact family `ror2` was globally contaminated by one mismatch row |

### Important nuance for `9bfb1cc6`

`ror2` was not auto-promoted globally because `fee5976e` is a hard mismatch inside the same exact family.

But `9bfb1cc6` itself is still safe after manual reading:

- every prompt example is an exact 2-bit right rotation
- the query follows the same transform cleanly
- the ambiguity is in the **global train family**, not in this row-local prompt

So this row is now treated as prompt-exact verified supervision.

## Newly excluded after direct prompt reading

One residual row was strong enough to move from manual to `exclude_suspect`.

| id | query | gold | exact formula prediction | exact formula |
| --- | --- | --- | --- | --- |
| `8631d7b6` | `11011101` | `00000000` | `10000000` | `xor(ror1,shr1)` |

The prompt examples cleanly separate the two output modes:

- rows where `ror1(query) == shr1(query)` map to `00000000`
- rows where they differ only on the top bit map to `10000000`

`11011101` falls in the second case, so the gold label conflicts with the exact prompt-backed rule.

## Row kept manual

One structured-byte residual still remains manual:

| id | query | gold | competing predictions | status |
| --- | --- | --- | --- | --- |
| `5a6dd286` | `10010110` | `10111100` | `10111100` / `10111101` | keep manual |

Reason:

- the examples fit both `or(rol1,rol3)` and `or(rol3,shl1)`
- the two formulas diverge on the query bitstring
- current prompt evidence does not disambiguate the final wrapped bit

So this row stays manual even after direct prompt reading.

## Counts after this pass

- overall: `6086 verified / 1147 answer_only / 2240 manual / 27 exclude`
- binary: `604 verified / 35 answer_only / 947 manual / 16 exclude`
- structured-byte residual: `1 manual + 5 exclude`
- pass1 manual pack: `497 rows`
  - `334` `symbol_numeric_same_op`
  - `117` `binary_low_gap`
  - `46` `symbol_glyph_multiset`

## Artifacts

- `artifacts/binary_structured_byte_manual_exact_verified_v1.csv`
- `artifacts/binary_structured_byte_manual_exact_excludes_v1.csv`

## Decision

This closes the structured-byte residual as a broad family problem.

What remains is no longer a repeated structured slice:

- one truly ambiguous multi-pred row (`5a6dd286`)
- five exclude rows whose prompt-backed structured rule conflicts with gold
