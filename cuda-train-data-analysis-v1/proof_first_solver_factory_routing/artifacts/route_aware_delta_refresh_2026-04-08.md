# Route-Aware Delta Refresh 2026-04-08

## Summary

README.md の評価契約に合わせて、binary route-aware delta を再生成した。

今回の更新では、v3f 実験から得た次の制約を builder と plan に反映した。

1. boxed preservation 単独では安全判定にしない
2. primary lane は exact-route verified rows とする
3. coarse answer-only は bounded low-ratio support に落とす
4. coarse route でも family-only ではなく template-subtype 水準の route を残す

## Regenerated Artifacts

1. binary_route_aware_delta.csv
2. train_split_with_cot_v2_plus_binary_route_aware.csv
3. binary_route_aware_delta_manifest.json

## Counts

manifest の値は次の通り。

1. requested_exact_quota = 240
2. requested_answer_only_quota = 56
3. available_exact_candidates = 117
4. available_blocked_exact_clone_candidates = 621
5. available_answer_only_candidates = 310
6. accepted_delta_rows = 296
7. accepted_exact_rows = 240 (new_unique_exact 117 + blocked_exact_clone 123)
8. accepted_answer_only_rows = 56

binary-only delta 内の比率は次の通り。

1. exact = 240 / 296 = 0.8108
2. coarse = 56 / 296 = 0.1892

これは plan で固定した exact `75-85%` / coarse `15-25%` の範囲内にある。

## Distribution Highlights

route_label の主要内訳は次の通り。

1. bit_manipulation.binary_affine_xor = 54
2. bit_manipulation.binary_structured_byte_formula_abstract = 51
3. bit_manipulation.binary_structured_byte_formula = 49
4. bit_manipulation.bit_other = 34
5. bit_manipulation.binary_bit_permutation_bijection = 30
6. bit_manipulation.binary_structured_byte_not_formula = 25
7. bit_manipulation.bit_structured_byte_formula = 22
8. bit_manipulation.binary_two_bit_boolean = 20
9. bit_manipulation.binary_byte_transform = 6
10. bit_manipulation.binary_three_bit_boolean = 4
11. bit_manipulation.binary_bit_permutation_independent = 1

assistant_style の内訳は次の通り。

1. route_trace_full = 188
2. route_closure_only = 56
3. route_trace_sanitized = 52

row_reuse_mode の内訳は次の通り。

1. blocked_exact_clone = 123
2. new_unique_exact = 117
3. new_unique_answer_only = 56

## Notes

1. `uv run python` はこの Linux 環境で `uv: command not found` だったため、artifact 再生成は `python3` で実行した
2. このステップでは training / benchmark の再実行はしていない
3. したがって新しい leaderboard score や offline score はまだ記録していない