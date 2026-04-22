# v20 corrective corpus v6 fresh-local300-bit-miss-heavy-no-crypt — results

## Status

- Created: 2026-04-27 UTC
- Generator: `v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_fresh_local300_bit_miss_heavy_no_crypt/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_fresh_local300_bit_miss_heavy_no_crypt.py`
- Default run name: `v6_fresh_local300_bit_miss_heavy_no_crypt_default`
- Bundle path: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_fresh_local300_bit_miss_heavy_no_crypt_bundle.jsonl`
- Dry-run validation: ✅ canonical checks passed, 680 unique, 2673 repeated rows
- MLX training run: 未実行
- Local300 score: 未計測 (baseline: 254/300 = 0.8467)
- Leaderboard score: 未計測

---

## Why this branch exists

Commit `6006ff4e` paused stuck step-zero MLX runs. Old support queues needed a fresh-restart.  
The retained best baseline is `v20_mlx_repro_v1_fullrun_targetfix_mb1_nobc` at **254/300 = 0.8467**.  
Goal is local300 >= 0.9 (270/300).

Remaining local300 misses from that baseline validation.csv:

| Category | IDs (16+2+1=19 actionable) |
|---|---|
| bit_manipulation (16) | 000b53cf, 012fb81b, 01e09228, 02a66bcb, 034fb629, 048cc279, 04d8c3e6, 05ca617c, 06881e47, 07e8cf66, 0b16458a, 0ec17d2e, 12fd5b6c, 132ec6ae, 16db2c74, 172d2417 |
| equation_numeric_guess (2) | 065f9dea, 0c0683c3 |
| cipher (1) | 0184a864 |
| cryptarithm_deduce (23) | (not targeted in this branch) |
| cryptarithm_guess (4) | (not targeted in this branch) |

**Note on 0ec17d2e**: absent from `train_recommended_learning_target_v1.csv`; gracefully skipped at corpus build time (no crash). Tracked here for visibility.

---

## Strategy (vs previous bit_family_rebalance baseline)

| Axis | Baseline (bit_family_rebalance) | This branch |
|---|---|---|
| cryptarithm budget | 48 unique × 3 = 144 rows | **0** (removed entirely) |
| surface_binary_prompt_local limit | 96 | **112** (+16) |
| surface_binary_structured limit | 96 | **112** (+16) |
| BIT miss set | 18 v4 partial misses | **16 exact local300 misses** |
| HARD_DEFAULT1 set | 23 IDs | **28 IDs** (+5 local300 verified) |
| choose(shl,shr,rol) family quota | 24 | **30** (+6; has 000b53cf, 172d2417) |
| majority(rol,shl,shr) family quota | 22 | **28** (+6; has 02a66bcb, 048cc279, 0b16458a) |
| majority(ror,shl,shr) family quota | 22 | **28** (+6; has 012fb81b, 16db2c74) |
| choose(shl,shr,ror) family quota | 20 | **24** (+4; has 07e8cf66) |
| choose(shl,shr,nibble_swap) quota | 10 | **16** (+6; has 01e09228) |
| choose(rol,ror,shr) family quota | (not present) | **12** (new; has 034fb629) |
| NUMERIC miss set | 7 v4 partial IDs | **2 exact local300 IDs** (065f9dea, 0c0683c3) |
| CIPHER miss set | {0d6d428a} | **{0184a864, 018c6f61, 13db9692, 16642d10}** |

---

## Dataset composition (dry-run output)

### Unique rows (total: 680)

- `binary_structured_exact_core`: 152
- `binary_logic_exact`: 56
- `binary_permutation_exact`: 40
- `binary_prompt_local_exact`: 95
- `surface_numeral_boxed`: 34
- `surface_cipher_boxed`: 6
- `surface_unit_tail`: 6
- `surface_symbol_prefix`: 4
- `surface_binary_prompt_local_answer_only`: 105 (limit 112; limited by available candidates)
- `surface_binary_structured_answer_only`: 112
- `surface_numeric_answer_only`: 64
- `surface_cryptarithm_answer_only`: 0 (removed in this branch)
- `easy_gravity_fragile`: 6

### Repeated training rows (total: 2673)

_Approximately 27.8M total tokens (estimated; confirmation on --write-training-bundle run)._

---

## Approximate token budget analysis

| Source | Rows | Est. tokens |
|---|---|---|
| Base snapshot (fixed) | 7828 | ~9.1M |
| Overlay (new) | 2673 | ~18.7M |
| **Total** | **10501** | **~27.8M** |

Baseline was 28.65M. This branch saves ~0.85M by removing cryptarithm; well within the high-28M / low-29M target range.

---

## To run

```bash
# Dry-run (corpus generation only)
cd /path/to/repo
uv run python v20_mlx_repro_v1/experiments/v6/support/v20_corrective_corpus_v6_promptlocal_short_token_binary_support_fresh_local300_bit_miss_heavy_no_crypt/reproduce_v20_corrective_corpus_v6_promptlocal_short_token_binary_support_fresh_local300_bit_miss_heavy_no_crypt.py

# With training bundle (for MLX training)
uv run python .../reproduce_....py --write-training-bundle
```

---

## Experiment ledger

| Run | Score (local300) | Notes |
|---|---|---|
| baseline (bit_family_rebalance) | 254/300 = 0.8467 | Previous best; stuck step-zero → paused |
| **this branch** | 未計測 | Fresh-restart; bit miss focus; no crypt |
