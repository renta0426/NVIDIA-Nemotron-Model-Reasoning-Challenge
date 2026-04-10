# Phase 0 Offline Eval Manifest

## README-aligned evaluation assumptions

- metric: `accuracy`
- temperature: `0.0`
- top_p: `1.0`
- max_tokens: `7680`
- max_num_seqs: `64`
- max_model_len: `8192`
- boxed_first_extraction: `True`
- numeric_relative_tolerance: `0.01`

## Benchmark sets

| set | rows | family_counts | selection_tier_counts | binary_focus_bucket_counts |
| --- | ---: | --- | --- | --- |
| `general_stable_set` | 200 | `{"gravity": 50, "roman": 50, "text": 50, "unit": 50}` | `{"verified_trace_ready": 200}` | `{}` |
| `binary_hard_set` | 60 | `{"binary": 60}` | `{"answer_only_keep": 24, "manual_audit_priority": 5, "verified_trace_ready": 31}` | `{"boolean_family": 6, "dominant_structured_abstract": 6, "dominant_structured_safe": 8, "no_solver_answer_only": 6, "no_solver_manual": 5, "rare_byte_transform": 1, "rare_perm_independent": 1, "supported_affine_xor": 7, "supported_bijection": 16, "supported_not_structured": 4}` |
| `symbol_watch_set` | 60 | `{"symbol": 60}` | `{"answer_only_keep": 35, "manual_audit_priority": 10, "verified_trace_ready": 15}` | `{}` |

## Binary holdout fold counts

| holdout_kind | fold_counts |
| --- | --- |
| `gap_signature` | `{"0": 321, "1": 321, "2": 320, "3": 320, "4": 320}` |
| `prompt_signature` | `{"0": 320, "1": 321, "2": 321, "3": 320, "4": 320}` |
| `solver_family` | `{"0": 176, "1": 598, "2": 171, "3": 446, "4": 211}` |
| `structured_family` | `{"0": 213, "1": 642, "2": 322, "3": 213, "4": 212}` |
