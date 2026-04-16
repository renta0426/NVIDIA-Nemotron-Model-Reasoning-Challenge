# v20_corrective_corpus_v3 — default-1 signal cleaning

> Repository: [README.md](../../README.md) | submission.zip | max_tokens=7680, max_num_seqs=64

## Strategy

**SUBTRACTIVE**: Remove 92 contaminated training examples containing `default 1` teacher-solver fallback.
These 92 token snapshots (66 base problem IDs + 26 -p0 continuations) carry wrong gold answers
and teach the model a harmful `default 1 → bit = 1` shortcut.

Root cause analysis: `A-Open-ProgressPrizePublication/v20_to_088_strategy.md` §v3 review.

## Bundle

| Metric | v20 baseline | v3 (this) | Delta |
|--------|-------------|-----------|-------|
| Examples | 7830 | 7738 | −92 |
| Steps (bs=32) | ~245 | 245 | −0 |
| Total tokens | 27,850,703 | 27,202,629 | −648,074 |
| Loss tokens | 26,568,807 | 25,945,530 | −623,277 |
| Categories | 9 | 9 | — |
| bit_manipulation | 1754 | 1662 | −92 |

File: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v3_bundle.jsonl` (236.6 MB)

## Promotion Gates

| Gate | Threshold | Status |
|------|-----------|--------|
| Proxy overall | ≥ 179/200 | ⏳ |
| Proxy binary | ≥ 80/92 | ⏳ |
| Proxy bit_structured_byte_formula | ≥ 26/31 | ⏳ |
| Easy-family no-regression | No new drops | ⏳ |
| Public LB | ≥ 0.86 | ⏳ |

## Measured Results

### Local Validation (train.csv head 950)

| Category | v20 | v3 | Delta |
|----------|-----|-----|-------|
| **Overall** | 837/950 | — | — |

### Leaderboard Proxy (200 rows)

| Category | v20 | v3 | Delta |
|----------|-----|-----|-------|
| **Overall** | 176/200 | — | — |
| Binary | 76/92 | — | — |
| bit_structured_byte_formula | 23/31 | — | — |

### Public Leaderboard

| Run | Score |
|-----|-------|
| v20 baseline | 0.84–0.85 |
| v1 corrective | (not submitted) |
| v2 corrective | 0.83–0.84 |
| **v3 (this)** | ⏳ |

## Key Watchlist Rows

Always-wrong proxy rows with wrong d1 teacher (unreachable without solver fix):
`0bfdba12, 3bfb9f72, 46685dd9, 49db3133, 51dc24a2, 729f5d30, 72ba7a3a, 79c42e3f, c1c18e68, ce065d18`

v1-only-win rows (should flip back to correct if d1 signal is removed):
`46cc4f06, 0e9e62a3, 8ce0e3bd`

## Recording

All scores are recorded from measured outputs only. Placeholders marked ⏳.
