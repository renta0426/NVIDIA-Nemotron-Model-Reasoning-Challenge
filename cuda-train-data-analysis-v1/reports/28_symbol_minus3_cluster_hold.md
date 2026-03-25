# cuda-train-data-analysis-v1 symbol '-' 3-digit cluster hold

## Purpose

Re-read the main round2 `symbol_numeric_same_op` clusters with operator `-` and 3-character answers, especially the sign-embedded slice, and decide whether any prompt-evidenced reusable family is safe enough to promote under the `README.md` accuracy-first evaluation.

## Scope

- focused unresolved `-` answer length `3` **sign-embedded** slice: `19` rows
- representative review still looked across nearby `-` 3-character rows to confirm that the instability is not just a single prompt quirk
- nearby short operator-embedded outputs were also re-read: `4179c322`, `812c12cb`, `d3092ac1`, `12d4a2df`
- high-shot rows re-read:
  - `4245e455` (`4` same-operator examples)
  - `7688e06e` (`5` same-operator examples)
  - `c541eb82` (`4` same-operator examples)

Representative IDs re-read:

- top cluster: `13892a7c`, `e102a09d`, `10fdae00`, `2dd48cac`, `33093ed0`
- higher-shot rows: `7688e06e`, `4245e455`, `c541eb82`
- mixed-sign rows: `13ad7bce`, `c541eb82`

## Decision

- promoted rows: `0`
- newly excluded rows: `0`
- decision: keep the current `-` 3-character round2 slice in `manual_audit_priority`
- later follow-up note: after this initial hold pass, `13892a7c` was safely promoted to `answer_only_keep` and `9a9f6025` was moved to `exclude_suspect` via the exact `comp99_abs_diff_2d` operator-prefixed zero-padded family; the remaining sign-embedded slice still stays manual

## Why these clusters still stay manual

- low-shot rows often expose only `1-2` same-operator `-` examples, so the sign / padding rule is underdetermined from the prompt alone
- even among the representative embedded rows, several answers require **negative output at query time without any negative `-` examples in the prompt**, so the sign would be a query-only inference rather than prompt-evidenced supervision
- high-shot rows still do not align to one reusable family:
  - `7688e06e`: `06-63 = 42`, `96-32 = 64`, `87-15 = 72`, `58-64 = 93`, `87-63 = 24`
  - `4245e455`: `98-22 = -76`, `66-43 = -23`, `45-35 = -1`, `39-49 = -1`
  - `c541eb82`: `68-93 = 74`, `39-26 = 13`, `93-46 = -52`, `81-67 = -85`
- nearby short embedded outputs are unsafe for the same reason:
  - `4179c322`: query `15-75`, gold `-6` even though a naive subtraction-style rule would suggest `-60`
  - `812c12cb`: query `09-19`, gold `-1`
  - `d3092ac1`: query `92-63`, gold `-7` even though a naive subtraction-style rule would suggest `29`
  - `12d4a2df`: query `68-08`, gold `-6` even though the nearby arithmetic reading would suggest `60`
  - these rows introduce unexplained truncation / prefix behavior that is not constrained by the prompt examples
- representative divergence is strong enough to block promotion:
  - `13892a7c`: query `61-47`, gold `-85`
  - `7688e06e`: query `63-19`, gold `-55`
  - `4245e455`: query `49-56`, gold `-92`
  - these rows are not explainable by one reusable subtraction/format family that is exact and prompt-evidenced
- even rows whose query answer happens to agree with `x_minus_y` are not safe to promote, because nearby same-operator rows in the same slice still contradict that family and leave the sign/padding rule unresolved
- the reviewed prompts mix several unstable behaviors:
  - signed and unsigned outputs can both appear inside the same prompt (`13ad7bce`, `c541eb82`)
  - zero-padding is inconsistent (`-1` vs `-01`)
  - some rows look like normal subtraction, while others look closer to complement-like or digitwise transforms
- under the `README.md` metric, query-only or weakly inferred promotion would be riskier than keeping the rows manual

## Interpretation

The `-` 3-character region is not just “hard subtraction”; it appears to mix multiple sign/format conventions that do not unify into one exact prompt-evidenced family. This makes the slice a round2 manual-hold candidate rather than a safe promotion source.
