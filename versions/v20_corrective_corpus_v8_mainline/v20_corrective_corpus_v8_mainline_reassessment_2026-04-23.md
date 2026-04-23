# v20 corrective corpus v8 mainline reassessment

## Status

- Created: 2026-04-23 UTC
- README basis:
  - README.md
  - A-Open-ProgressPrizePublication/README.md
- Evidence sources:
  - A-Open-ProgressPrizePublication/result/results-v8/results.csv
  - A-Open-ProgressPrizePublication/result/results-v8/validation.csv
  - A-Open-ProgressPrizePublication/result/leaderboard_proxy_eval-v8/reports/leaderboard_proxy_eval_summary.md
  - A-Open-ProgressPrizePublication/result/leaderboard_proxy_eval-v8/artifacts/leaderboard_proxy_eval_row_level.csv
  - A-Open-ProgressPrizePublication/result/leaderboard_proxy_eval-v8/artifacts/leaderboard_proxy_eval_raw_outputs.csv
  - versions/v20_corrective_corpus_v8_mainline/v20_corrective_corpus_v8_mainline-results.md
  - versions/v20_corrective_corpus_v8_mainline/v20_corrective_corpus_v8_mainline_strategy_2026-04-22.md
  - versions/v20_corrective_corpus_v8_mainline/v20_corrective_corpus_v8_mainline_bundle_audit_2026-04-22.md
  - versions/v20_corrective_corpus_v7_mainline/v20_corrective_corpus_v7-1_reassessment_2026-04-22.md
  - versions/v20_corrective_corpus_v7_mainline/v20_corrective_corpus_v7-1_bundle_and_raw_output_audit_2026-04-22.md
  - versions/v20_corrective_corpus_v6_mainline/v20_corrective_corpus_v6_mainline-results.md
  - versions/v20_corrective_corpus_v4_mainline/v20_corrective_corpus_v4_mainline-results.md
- Official leaderboard note:
  - user-reported official score range: 0.83-0.84

## Measured score summary

- validation: 834 / 950 = 0.8779
- leaderboard proxy: 178 / 200 = 0.8900
- proxy binary: 78 / 92 = 0.8478
- proxy symbol: 24 / 32 = 0.7500
- official leaderboard: user-reported 0.83-0.84

## Executive summary

v8 is promote-ineligible.

README says the main score source is bit_manipulation and that boxed-first extraction still matters. v8 did neither side well enough. It spent a large budget on symbol exact lanes without moving the frozen symbol hard rows, failed to improve binary frontier over the best prior proxy runs, and introduced fresh easy-family debt where Roman numeral problems collapsed to boxed 0.

This is not a v7-style tokenstream bug. The v8 bundle audit already showed token-level integrity. The regression is therefore a training-data policy failure, not a bundle-construction failure.

## Scorecard

| version     |       validation |            proxy |   proxy binary |   proxy symbol | official leaderboard | read                                    |
| ----------- | ---------------: | ---------------: | -------------: | -------------: | -------------------: | --------------------------------------- |
| v4_mainline | 813/950 = 0.8558 | 179/200 = 0.8950 | 79/92 = 0.8587 | 24/32 = 0.7500 |            0.85-0.86 | best public mainline in this family     |
| v6_mainline | 829/950 = 0.8726 | 180/200 = 0.9000 | 80/92 = 0.8696 | 24/32 = 0.7500 |            0.83-0.85 | proxy-strong, public blind spot exposed |
| v7-1        | 839/950 = 0.8832 | 178/200 = 0.8900 | 78/92 = 0.8478 | 24/32 = 0.7500 |                 0.84 | token-safe repair run                   |
| v8          | 834/950 = 0.8779 | 178/200 = 0.8900 | 78/92 = 0.8478 | 24/32 = 0.7500 |            0.83-0.84 | data-policy miss                        |

Three points matter.

1. v8 is lower than v7-1 on validation and worse on the official leaderboard.
2. v8 ties v7-1 on proxy only in aggregate; it does not beat v6 or v4 on binary proxy.
3. symbol proxy is frozen at 24 / 32 across v4, v6, v7-1, and v8.

## What v8 actually changed in training data

v8 is not a continuation of the v7-1 token-safe repair line. It replaces the teacher architecture.

### 1. It dropped the v4_public_base-dominant donor mix

The key effect in v7-1 was token-safe reuse for v4_public_base. Its overlay mix remained

- v4_public_base = 808
- v6_binary_donor = 27
- v6_numeral_surface_donor = 10
- v7_numeral_surface_synth = 1

with 846 overlay examples, 8674 total examples, and 32948771 total tokens.

v8 instead returned to a 04-08-16-14 base snapshot plus synthetic overlay design.

- overlay examples: 1183
- total examples: 9011
- total tokens: 28199629

So v8 added 337 overlay examples versus v7-1 while removing 4749142 total training tokens. The supervision became much shorter even as the number of overlay rows increased.

### 2. It reallocated budget toward BIT and symbol exact lanes

The unique row mix in v8 was

- binary_structured_exact_core: 224
- binary_logic_exact: 88
- binary_permutation_exact: 64
- binary_prompt_local_exact: 96
- symbol_numeric_exact: 48
- symbol_glyph_exact: 48
- surface_numeral_boxed: 18
- surface_cipher_boxed: 4
- surface_unit_tail: 4
- easy_gravity_fragile: 4

This is 598 unique rows total, allocated as

- BIT: 472 (78.93%)
- symbol: 96 (16.05%)
- guardrail: 30 (5.02%)

Artifact recount of the repeated overlay shows the actual supervision styles:

- exact_rule_commit = 472
- exact_closure_commit = 472
- anti_default1_commit = 17
- symbol_operator_commit = 48
- symbol_format_commit = 48
- symbol_glyph_copy_commit = 48
- symbol_glyph_length_commit = 48
- surface_boxed_tail = 30

That means v8's center of mass was a large short exact binary commit pack plus 192 repeated symbol exact rows, with only 30 repeated easy-family guardrail rows.

### 3. It cut surface stabilizers harder than v6

v6 kept repeated surface stabilizer rows at 56, and unique rows included

- surface_numeral_boxed = 34
- surface_cipher_boxed = 6
- surface_unit_tail = 6
- surface_symbol_prefix = 4
- easy_gravity_fragile = 6

v8 shrank this to

- surface_numeral_boxed = 18
- surface_cipher_boxed = 4
- surface_unit_tail = 4
- easy_gravity_fragile = 4
- surface_boxed_tail = 30 repeated rows

and dropped surface_symbol_prefix entirely. Given the README emphasis on boxed-first extraction and easy-family surface debt, this was a high-risk cut.

## What changed in outputs

## Validation vs v7-1

- net: -5
- improved: 6
- regressed: 11

Category movement:

- improved:
  - cryptarithm_deduce: +2
  - bit_manipulation: +2
  - gravity: +1
  - numeral: +1
- regressed:
  - numeral: -6
  - bit_manipulation: -3
  - cryptarithm_deduce: -1
  - unit_conversion: -1

So the v8 validation loss is driven mainly by numeral regression and binary content regression.

### Numeral regression shape

These numeral rows were correct in v7-1 and regressed in v8 to boxed 0:

- 0805b912: XCIX -> 0
- 0adca57b: V -> 0
- 0ea93e44: XL -> 0
- 1112ec96: IV -> 0
- 18840879: XC -> 0
- 18997574: XL -> 0

This is not the v6 no-box pattern. The answer stayed boxed but the answer space slipped from Roman output to numeric 0.

### Binary regression shape

These validation binary rows regressed from v7-1 to v8:

- 0a50c4a8: 00001101 -> 00011101
- 0dd5caf4: 00000000 -> 01000000
- 13c8ae90: 00110000 -> 10101000

All remain boxed. The loss is content drift, not format failure. Two of them, 0a50c4a8 and 0dd5caf4, were explicit binary hard anchors in the v8 strategy.

## Proxy vs v7-1

- net: 0
- improved: 2
- regressed: 2

Every change is binary. Symbol did not move at all.

Improved IDs:

- 069dbaab: 00010001 -> 00010000
- 13009e35: 10111011 -> 11111011

Regressed IDs:

- 26a70ae0: 10010101 -> 01010101
- 6a333ed6: 00010000 -> 00010001

All four changes are boxed -> boxed. v8 did not create any new format repair on proxy; it only rotated which boxed binary content rows were correct.

## Proxy vs v6 and v4

v8 still does not beat the best earlier proxy reads.

- vs v6: net -2
  - improved: 069dbaab
  - regressed: 26a70ae0, 6a333ed6, c30a782a
- vs v4: net -1
  - improved: 59c78e51
  - regressed: 26a70ae0, 6a333ed6

So even before looking at the official score, v8 is not a better binary proxy branch than v6 or v4.

## Symbol exact lane had zero measured return

v8 used 96 unique and 192 repeated rows for symbol exact supervision. Yet symbol proxy stayed fixed at 24 / 32 with no row-level movement.

The wrong symbol IDs are still the same hard 8:

- numeric_2x2: 8158a14c, 878c843c, b7b1d1a8, e8de8b47
- glyph_len5: a85864a9, be7101dc, d7e5414c, dc240ebd

These are exactly the hard symbol anchors that v8 explicitly fixed into the corpus. So the targeted symbol lane achieved zero measured return on the rows it was designed to move.

## End-state failure shape

The 22 wrong proxy rows break down as

- binary: 14
- symbol: 8

By template subtype:

- bit_other = 8
- bit_structured_byte_formula = 6
- numeric_2x2 = 4
- glyph_len5 = 4

By selection tier:

- manual_audit_priority = 9
- verified_trace_ready = 8
- answer_only_keep = 5

And every wrong row is still in format_bucket boxed. So v8 ends in content failure, not extraction failure.

## Why the official score got worse

The cleanest read is the combination of three effects.

### 1. More BIT budget did not buy frontier progress

BIT was increased to 472 unique rows and the repeated binary exact pack rose to 961 rows worth of supervision, but proxy binary remained 78 / 92, equal to v7-1 and below v6 and v4.

### 2. 16 percent of unique budget went to symbol with zero measured gain

README says bit_manipulation is the main upside slice. v8 spent 96 unique and 192 repeated rows on symbol exact supervision and did not move a single measured symbol hard row.

### 3. Guardrails were cut too hard and numeral answer-space drift appeared

Compared with v6, v8 trimmed the surface stabilizer pack aggressively. Validation then showed a new failure mode where Roman numeral problems returned boxed 0. This is exactly the kind of easy-family surface corruption that README warns can erase otherwise-correct reasoning.

In short, v8

- did not push binary far enough,
- did not move symbol at all,
- and created new easy-family debt.

## Final judgment

v8 failed as a frontier teacher replacement run.

What this run establishes is:

1. The failure is not a tokenstream bug.
2. Simply replacing the public-safe donor lane with shorter exact synthetic traces does not improve public score.
3. The current symbol exact implementation still cannot move the frozen hard 8.
4. Minimal guardrail is not enough; numeral rows can slide all the way to boxed 0.

The next mainline should therefore require all of the following.

1. Freeze broad symbol investment until a separate symbol gate proves row-level gain.
2. Promote numeral rows 0805b912, 0adca57b, 0ea93e44, 1112ec96, 18840879, and 18997574 into the hard guardrail watchlist.
3. Treat binary rows won by v6 or v7-1 as no-regression requirements.
4. Reintroduce some public-safe distribution from the v4_public_base family instead of replacing it wholesale with short synthetic exact commits.
