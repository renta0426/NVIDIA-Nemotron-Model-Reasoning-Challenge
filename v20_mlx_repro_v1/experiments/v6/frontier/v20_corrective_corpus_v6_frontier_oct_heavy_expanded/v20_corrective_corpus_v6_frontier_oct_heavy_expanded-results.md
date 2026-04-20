# v20 corrective corpus v6 frontier oct-heavy expanded results

## Status

- Created: 2026-04-19 UTC
- Generator: `v20_mlx_repro_v1/experiments/v6/frontier/v20_corrective_corpus_v6_frontier_oct_heavy_expanded/reproduce_v20_corrective_corpus_v6_frontier_oct_heavy_expanded.py`
- Base branch: `v20_corrective_corpus_v6_promptlocal_short_token_binary_support_hybrid_expanded_numeric_popular8_plain_cryptarithm_support_bit_miss_support_crypt_miss_support_measured_surface_support_bit_family_rebalance_crypt_deduce_heavy_frontier_support`
- Run name: `v6_frontier_oct_heavy_expanded_default`
- Planned MLX full-run: `v20_mlx_v6_frontier_oct_heavy_expanded_mb1_nobc`
- Bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_frontier_oct_heavy_expanded_bundle.jsonl`
- Training / validation / leaderboard score: 未計測
- Launch status: queue 待ちを外して detached 手動起動し、実際に MLX train process まで到達したことを `ps` で確認した。ただし同時に frontier-support 側を重ねたタイミングで環境全体が OOM 再起動に入ったため、本 branch も score 取得前に中断した

## README-grounded motivation

- README は `cipher` を **100.0%** solve 可能帯として記録している
- `sept-heavy` までで current `v4` partial miss の specialized coverage を確認すると、未特化 ID は **cipher / rule_found の 1件 (`0d6d428a`)** だけだった
- そのため最後に **cipher 1件だけ** を足した最終極薄 branch を作る

## Dataset composition

### Unique rows

- total unique overlay problems: 680
- unique bucket mix は frontier-support と同一

### Repeated training rows

- surface_binary_prompt_local_answer_only: 300
- surface_binary_structured_answer_only: 268
- surface_numeric_answer_only: 233
- surface_cryptarithm_answer_only: 358
- surface_cipher_boxed: 21
- surface_unit_tail: 27
- easy_gravity_fragile: 30
- total repeated overlay rows: 2982

### Bundle footprint

- overlay examples: 2982
- total examples: 10810
- total steps: 339
- total tokens: 28672200
- max sequence length: 7971

## Oct-heavy mix

- sept-heavy の全成分に加えて、**1 cipher miss** に `CIPHER_CURRENT_MISS_EXTRA_REPEAT = 2`
- repeats は `surface_cipher_boxed 19 -> 21` のみ増える

## Support budget

- combined measured-support share は **`0.3245`**

## Delta vs expanded frontier-support base

- unique rows は **`680 -> 680`** で不変
- overlay rows は **`2803 -> 2982`** で **`+179`**
- total tokens は **`28639036 -> 28672200`** で **`+33164`**
- 差分は sept-heavy に `cipher 1件 × repeat 2 = +2 rows` を加えたもの

## Interpretation before training

- oct-heavy は **current partial miss の最後の 1件だけ** を足した最終 branch
- sept-heavy に対して **+2 rows / +315 tokens** なので、ほぼ distribution shift なしで cipher tail を拾えるかを見る

## Next evaluation gate

- `v20_mlx_v6_frontier_oct_heavy_expanded_mb1_nobc` を sept-heavy / sext-heavy と measured diff-pack で比較し、**cipher 1件追加が additive gain か** を見る
