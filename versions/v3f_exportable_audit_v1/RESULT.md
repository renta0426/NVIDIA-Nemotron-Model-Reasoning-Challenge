# v3f_exportable_audit_v1

- script: `versions/v3f_exportable_audit_v1/reproduce_v3f_exportable_audit.py`
- purpose: single-file audit hub for the historical `v3f` exportable lineage under the `README.md` contract
- README contract sync: the single-file audit script now also enforces `gpu_memory_utilization = 0.85` from the README evaluation table
- regenerated audit summaries now also stamp `summary_schema_version = 2`, per-artifact `readme_contract_state`, and `readme_contract_verified_from_readme_file = true`, so README contract completeness and live-README revalidation are self-described in JSON/Markdown
- the audit script now also re-reads the authoritative `README.md` evaluation rows directly and fails explicitly if a required row is missing, empty, or malformed
- `max_lora_rank_required = false` contract-state reporting now allows optional `max_lora_rank` to be present without turning phase0/specialized README-state summaries into false negatives

## Verified score anchors

| metric | score | source |
| --- | ---: | --- |
| stored Phase0 local320 | `249/320 = 0.7781` | `baseline/nemotron-sft-lora-with-cot-v2/result/v3f/phase0_offline_eval/artifacts/phase0_eval_summary.json` |
| corrected local320 | `240/320 = 0.7500` | `cuda-train-data-analysis-v1/proof_first_solver_factory_routing/result/LEADERBOARD_GAP_INVESTIGATION_2026-04-09.md` |
| corrected binary_hard | `18/60 = 0.3000` | `cuda-train-data-analysis-v1/proof_first_solver_factory_routing/result/LEADERBOARD_GAP_INVESTIGATION_2026-04-09.md` |
| actual proxy rerun | `133/200 = 0.6650` | `baseline/nemotron-sft-lora-with-cot-v2/result/v3f/leaderboard_proxy_eval/artifacts/leaderboard_proxy_eval_summary.json` |
| specialized563 | `238/563 = 0.4227` | `baseline/nemotron-sft-lora-with-cot-v2/result/v3f/phase0_offline_eval_binary_bias_specialized/artifacts/binary_bias_specialized_eval_summary.json` |

## Hidden-gap bottlenecks fixed in code audit

| slice | score | note |
| --- | ---: | --- |
| `supported_bijection` | `47/50 = 0.9400` | already strong |
| `supported_not_structured` | `1/55 = 0.0182` | severe hidden-gap failure |
| `binary_structured_byte_not_formula` | `1/25 = 0.0400` | severe teacher-solver failure |

## Submission compatibility

- historical MLX bundle note: `This is a local MLX adapter bundle. It is not claimed to be PEFT/vLLM submission-compatible.`
- implication: `v3f` is still the strongest audited single-adapter direction, but the historical bundle itself is **not** a ready README submission artifact

## Next step

- keep this audit hub as the source of truth while rebuilding a submission-compatible single-adapter `v3f`-style line
