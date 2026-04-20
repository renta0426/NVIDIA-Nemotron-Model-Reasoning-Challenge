# v20 corrective corpus v6 frontier sept-heavy expanded results

## Status

- Created: 2026-04-19 UTC
- Generator: `v20_mlx_repro_v1/experiments/v6/frontier/v20_corrective_corpus_v6_frontier_sept_heavy_expanded/reproduce_v20_corrective_corpus_v6_frontier_sept_heavy_expanded.py`
- Base branch: `v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_deduce_heavy_frontier_support`
- Run name: `v6_frontier_sept_heavy_expanded_default`
- Planned MLX full-run: `v20_mlx_v6_frontier_sept_heavy_expanded_mb1_nobc`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_frontier_sept_heavy_expanded_bundle.jsonl`
- Training / validation / leaderboard score: 未計測

## README-grounded motivation

- README の equation 節は、未出 operator / multiplication / division / absolute difference をどう捉えるかが残差に直結すると説明している
- sext-heavy で hard/easy tail の大半は押せたので、残る **equation deduce tail 3件** だけを薄く足す最終 additive ablation を作る

## Dataset composition

### Unique rows

- total unique overlay problems: 680
- unique bucket mix は frontier-support と同一

### Repeated training rows

- surface_binary_prompt_local_answer_only: 300
- surface_binary_structured_answer_only: 268
- surface_numeric_answer_only: 233
- surface_cryptarithm_answer_only: 358
- surface_unit_tail: 27
- easy_gravity_fragile: 30
- total repeated overlay rows: 2980

### Bundle footprint

- overlay examples: 2980
- total examples: 10808
- total steps: 339
- total tokens: 28671885
- max sequence length: 7971

## Sept-heavy mix

- sext-heavy の全成分に加えて、**3 equation deduce tail misses** に `EQUATION_DEDUCE_TAIL_CURRENT_MISS_EXTRA_REPEAT = 2`
- repeats は `surface_numeric_answer_only 227 -> 233` のみ増える

## Support budget

- combined measured-support share は **`0.3243`**
- cryptarithm share は **`0.0565`**
- exact binary share は **`0.4977`**

## Delta vs expanded frontier-support base

- unique rows は **`680 -> 680`** で不変
- overlay rows は **`2803 -> 2980`** で **`+177`**
- total tokens は **`28639036 -> 28671885`** で **`+32849`**
- 差分は sext-heavy に `equation deduce tail 3件 × repeat 2 = +6 rows` を加えたもの

## Interpretation before training

- sept-heavy は **README の equation tail だけを追加する最終薄膜 branch**
- sext-heavy に対して **+6 rows / +880 tokens** なので、ほぼノーリスクで equation deduce tail を拾えるかを見る

## Next evaluation gate

- `v20_mlx_v6_frontier_sept_heavy_expanded_mb1_nobc` を sext-heavy / quint-heavy と measured diff-pack で比較し、**equation deduce tail 追加が additive gain か** を見る
