# v3f-one-shot-repair-v1

## Status

- date: `2026-04-10`
- status: `prepared`
- score_status: `pending`

## Files

1. training CSV:
   `cuda-train-data-analysis-v1/proof_first_solver_factory_routing/artifacts/train_split_with_cot_v3f_one_shot_repair_v1.csv`
2. CSV note:
   `cuda-train-data-analysis-v1/proof_first_solver_factory_routing/artifacts/train_split_with_cot_v3f_one_shot_repair_v1.md`
3. notebook:
   `cuda-train-data-analysis-v1/proof_first_solver_factory_routing/nemotron-sft-lora-with-cot-v3f-one-shot-repair-v1.ipynb`

## Strategy summary

This version is a one-shot attempt to beat `v3f` while minimizing recipe churn.

Core idea:

1. keep `v3f` broad trunk
2. add stage2 exact corrective rows for binary and numeric blind spots
3. add stage2.5 text-heavy repair rows plus a small binary proxy supplement
4. keep the original v2 full-run notebook logic except for dataset path, counts, and boxed-only fallback

## Target gates

The intended accept criteria are:

1. leaderboard proxy > `0.6650`
2. proxy binary > `0.4565`
3. binary `format_ok_content_wrong_rate` < `0.5435`
4. specialized563 >= `0.4227`

## Scores

| metric | score |
| --- | --- |
| `readme_local320` | `pending` |
| `leaderboard_proxy_v1_set` | `pending` |
| `specialized563` | `pending` |
| `kaggle_leaderboard` | `pending` |