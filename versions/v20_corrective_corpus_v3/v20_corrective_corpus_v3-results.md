# v20_corrective_corpus_v3 — default-1 exposure ablation (ON HOLD)

> Repository: [README.md](../../README.md) | submission.zip | max_tokens=7680, max_num_seqs=64

## Audit status

**ON HOLD**. The original v3 premise was invalidated by a direct audit of `reasoning/*.txt` vs `train.csv`.

- The removed set is still **92 snapshot rows / 66 base problem IDs / 648,074 tokens**
- But in the current repo state, those **66 base problem IDs are all teacher-correct**
- So this bundle is **not a confirmed contamination cleanup**
- It is a **default-1 exposure ablation** that removes correct teacher traces and leaves at least one known non-d1 teacher error (`ef2fe526`) in the remaining v20 binary overlap

Reference: corrected discussion in `A-Open-ProgressPrizePublication/v20_to_088_strategy.md` §v3 review.

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
| Proxy overall | ≥ 179/200 | HOLD |
| Proxy binary | ≥ 80/92 | HOLD |
| Proxy bit_structured_byte_formula | ≥ 26/31 | HOLD |
| Easy-family no-regression | No new drops | HOLD |
| Public LB | ≥ 0.86 | HOLD |

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

Always-wrong binary proxy rows with wrong d1 teacher:
`01e09228, 101410e4, 12154247, 12fd5b6c, 1532c0d1, 2230fad0, 257e7158, 2d790c98, 31966698, a6192d29`

Rows that moved across v20/v1/v2 and still need targeted treatment:
`012fb81b, 0520a6ec, 0a50c4a8, 59c78e51, 8e5d6fe6, b9500f41, c30a782a, fa67da07`

## Recording

All scores are recorded from measured outputs only. This v3 bundle is currently on hold pending a corrected mainline binary corpus.
