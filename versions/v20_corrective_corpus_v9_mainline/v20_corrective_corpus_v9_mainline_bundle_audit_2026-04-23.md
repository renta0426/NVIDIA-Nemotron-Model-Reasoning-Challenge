# v20 corrective corpus v9 mainline bundle audit

## Status

- Created: 2026-04-23 UTC
- Audit target:
  - A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v9_mainline_bundle.jsonl
- Strategy basis:
  - A-Open-ProgressPrizePublication/README.md
  - A-Open-ProgressPrizePublication/データ戦略を理解する.md
  - cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md
  - versions/v20_corrective_corpus_v8_mainline/v20_corrective_corpus_v8_mainline_reassessment_2026-04-23.md
  - versions/v20_corrective_corpus_v9_mainline/v20_corrective_corpus_v9_mainline_strategy_2026-04-23.md
  - versions/v20_corrective_corpus_v9_mainline/v20_corrective_corpus_v9_mainline-results.md
- Evidence checked directly:
  - versions/v20_corrective_corpus_v9_mainline/reproduce_v20_corrective_corpus_v9_mainline.py
  - versions/v20_corrective_corpus_v9_mainline/outputs/v9_mainline_default/artifacts/corrective_overlay_repeated.jsonl
  - versions/v20_corrective_corpus_v9_mainline/outputs/v9_mainline_default/artifacts/corrective_overlay_unique.jsonl
  - versions/v20_corrective_corpus_v9_mainline/outputs/v9_mainline_default/artifacts/corrective_overlay_summary.json
  - versions/v20_corrective_corpus_v9_mainline/outputs/v9_mainline_default/artifacts/corrective_selection.csv
  - versions/v20_corrective_corpus_v9_mainline/outputs/v9_mainline_default/reports/corrective_overlay_report.md
  - versions/v20_corrective_corpus_v7_mainline/outputs/v7_mainline_default/artifacts/corrective_overlay_repeated.jsonl
  - A-Open-ProgressPrizePublication/nemotron/training/sft/04-08-16-14/logprobs/index.jsonl
  - A-Open-ProgressPrizePublication/nemotron/augmenters/matching.py

## Executive summary

v9 bundle is strategy-consistent.

The generated bundle really does what the v9 strategy claimed:

1. keep the v7 donor backbone,
2. stop broad v8-style BIT and symbol exact expansion,
3. add only A-Open-style matching auxiliaries on top of that backbone.

The direct recount from the bundle and overlay artifacts matches the documented counts exactly. The only drift from the historical v7 repeated overlay is metadata normalization: v9 writes `prompt_suffix_mode = boxed_final_answer` explicitly on the inherited non-matching rows, but prompt text, completion text, bucketing, teacher metadata, and repeat counts are unchanged.

This makes the branch internally coherent.

What it does **not** prove is score gain. v9 is a better-justified BIT experiment than v8, but it is still an indirect BIT intervention. It restores missing token-local curriculum rather than solving the unresolved binary frontier programmatically.

## Strategy adherence check

### 1. Base snapshot really lacks A-Open auxiliary curriculum

Direct recount of `04-08-16-14/logprobs/index.jsonl` shows only competition categories:

- bit_manipulation: 1754
- cipher: 1656
- cryptarithm_deduce: 627
- cryptarithm_guess: 154
- equation_numeric_deduce: 658
- equation_numeric_guess: 126
- gravity: 1055
- numeral: 730
- unit_conversion: 1070

Absent categories:

- matching
- spelling
- concatenation
- splitting
- lstrip

So the main v9 premise is correct: inheriting `04-08-16-14` does not restore the auxiliary curriculum used in A-Open.

### 2. Bundle footprint matches the documented v9 counts

Direct recount from the bundle gives:

- examples: 9217
- total tokens: 33305836
- total loss tokens: 31426997
- max seq len: 7971
- total steps: 289

Source split inside the bundle:

- base_snapshot: 7828
- corrective_overlay: 1389

This matches the v9 strategy and results note exactly.

### 3. Overlay source mix matches the intended v9 design

Direct recount from `corrective_overlay_repeated.jsonl` gives:

- v4_public_base: 808
- v6_binary_donor: 27
- v6_numeral_surface_donor: 10
- v7_numeral_surface_synth: 1
- v9_bit_matching_aux: 543

Repeated overlay total:

- 1389

Overlay category counts:

- bit_manipulation: 683
- matching: 543
- numeral: 83
- cipher: 24
- cryptarithm_deduce: 24
- unit_conversion: 16
- gravity: 12
- equation_numeric_deduce: 4

These counts agree with:

- strategy note
- results note
- overlay report
- overlay summary
- direct recount from the bundle rows themselves

### 4. v7 donor backbone is preserved in substance

Comparing v9 non-matching overlay rows against v7 repeated overlay rows:

- v7 repeated rows: 846
- v9 non-matching repeated rows: 846
- prompt changes: 0
- answer changes: 0
- completion_text changes: 0
- teacher / bucket / source_mix changes: 0

The only observed difference is metadata normalization:

- v7 stored `prompt_suffix_mode` as null
- v9 stores inherited rows as `boxed_final_answer`

So the claim "keep the token-safe v7 donor backbone" is correct at the level that matters for training behavior.

### 5. Matching lane is really A-Open-style auxiliary data

The implementation in `reproduce_v20_corrective_corpus_v9_mainline.py` copies the same extraction structure and downsampling logic used by `A-Open-ProgressPrizePublication/nemotron/augmenters/matching.py`:

- same section list
- same `Matching output / Left / Right` block extraction
- same deterministic hash-based keep rules for all-absent / both-none / few-match sections
- same non-boxed auxiliary completion style

Direct recount confirms the generated matching rows have exactly the intended format:

- matching examples in bundle: 543
- prompt_suffix_mode none: 543 / 543
- matching completion with boxed answer: 0 / 543
- non-matching rows with prompt_suffix_mode none: 0

So v9 did not accidentally convert matching into final-answer supervision. It stayed an auxiliary lane.

## Matching lane nuance

The strategy note says matching was extracted from the 240 binary origin IDs carried by v7. That is true at the scan stage, but there is one nuance worth recording.

Direct recount shows:

- binary origin IDs scanned: 240
- raw sections extracted: 2160
- informative sections: 739
- kept sections after deterministic downsampling: 543
- origin IDs contributing at least one kept matching row: 233
- origin IDs contributing zero kept rows after downsampling: 7

Sample zero-row IDs after downsampling:

- 100e280a
- 1c2a3c5b
- 1dba764b
- 33910360
- 3bdda816
- 574d1901
- 6ae30806

This is not a strategy violation. It is a consequence of reusing the original A-Open keep rule at section granularity. But it matters for interpretation: the matching lane is distributed across most, not all, of the 240 origins after keep filtering.

## Why this branch can plausibly improve BIT

The positive case for v9 is stronger than the case for v8.

### 1. It attacks a missing curriculum, not an ambiguous answer frontier

v8 tried to improve BIT by adding more exact final-answer teachers on competition rows. That did not move binary proxy beyond `78 / 92`, and the v8 postmortem showed that broad exact expansion was not enough.

v9 instead restores a local subskill curriculum that A-Open explicitly used: bit-column matching, left/right chain scoring, and best-path selection. This is closer to the README philosophy of decomposing reasoning into token-level stable subproblems.

### 2. It does not inject new boxed answers into the audited ambiguous tail

`FINAL_SUMMARY_REPORT.md` says the remaining binary tail is not a clean solved region. After strict audit, binary is:

- 1229 verified
- 271 answer_only
- 87 manual
- 15 exclude

That means broad answer-level expansion is dangerous. v9 respects that constraint. It adds no new boxed answer teachers for those ambiguous residual families.

### 3. It preserves the public-safe donor mix that v8 abandoned

v9 keeps the v7 donor skeleton intact and only adds matching. So it does not repeat the main v8 mistake of replacing a token-safe donor-dominant branch with a shorter synthetic exact-heavy branch.

### 4. It is aligned with the A-Open data strategy

The A-Open reference did not rely only on competition CoT. It also pushed large auxiliary corpora that targeted low-level token weaknesses. For BIT specifically, `matching` was not side noise. It was a direct extraction of a key local step from the bit reasoner. v9 is the first branch in this workspace that explicitly restores that missing piece.

## Why BIT may still fail to improve

This audit also needs the negative case.

### 1. Matching is indirect supervision

matching improves local bit-column alignment, but it does not teach the final query-specific closure by itself. If the current binary frontier is limited mainly by:

- query-specific closure failure,
- persistent `default 1` content drift,
- or final output composition after the matching phase,

then matching alone may not move proxy enough.

### 2. v9 does not solve the unresolved binary families programmatically

The audit of train data already concluded that the remaining binary tail needs either:

- new unique trace-ready circuit families,
- or new disambiguation evidence.

v9 does neither. It is a curriculum restoration branch, not a new solver-family branch.

### 3. The restored curriculum is smaller than full A-Open auxiliary coverage

v9 adds only 543 matching rows. That is useful, but it is far smaller than the full A-Open auxiliary stack, and it does not restore spelling / splitting / concatenation / lstrip. That is intentional for a BIT-focused branch, but it limits expected upside.

## A-Open history constraint

There is one more important constraint from the original A-Open run history.

Direct recount of the training snapshots shows:

- `04-08-16-14`: 7830 examples, competition categories only, no matching / spelling / concatenation / splitting / lstrip
- `04-10-04-33`: 15679 examples, with matching 4515, spelling 648, concatenation 1500, splitting 1500
- `04-10-04-15`: 1789 examples, with matching 506, spelling 75, concatenation 168, splitting 168, lstrip 34

README still identifies `04-08-16-14` as the winning submission run. So from the A-Open chronology, auxiliary restoration is already a known method, and the existence of a larger auxiliary-rich run did not automatically supersede the competition-only winning run.

This matters for v9 interpretation.

v9 is not recovering a missing secret that A-Open never tried. It is importing one known later A-Open ingredient into the local corrective branch that descends from `04-08-16-14`.

Therefore the correct read is:

- v9 is a coherent diagnostic branch,
- v9 may still help if the local `04-08-16-14` derivative is specifically undertrained on bit-local alignment,
- but v9 does **not** have a strong historical prior of improving leaderboard score on its own.

In other words, the historical evidence weakens the promotion case for v9 as a mainline answer. If `04-08-16-14` already beat auxiliary-rich A-Open siblings, then restoring matching alone is more likely to be a local patch test than a winning redesign.

## Audit judgment

The bundle is valid and faithful to the written v9 strategy.

More precisely:

- the branch really is v7 backbone plus matching,
- it really does avoid broad v8-style exact expansion,
- it really does restore an A-Open-style BIT-local auxiliary that the inherited base snapshot lacks,
- and it does so without changing inherited donor prompts or completions.

So the design is coherent.

However, the expected benefit should be framed correctly.

The reason v9 could improve BIT is **not** that it covers more hard answers. The reason is that it may reduce token-local instability in the internal bit-matching stage that A-Open treated as worth isolating into its own curriculum. That is a plausible intervention and a better fit than v8.

But the unresolved binary frontier is still unresolved. If v9 fails to beat at least `78 / 92` proxy binary, the next conclusion should not be "need more matching" by default. The next conclusion should be that auxiliary restoration alone is insufficient and the next branch must add a new query-specific closure or anti-`default 1` mechanism without repeating v8's broad exact-answer expansion mistake.

Given the A-Open history constraint above, there is also a stronger planning implication: even before training, v9 should be treated as promote-ineligible by default unless it produces a clear binary gain without public-safe regressions. If not, the correct next move is a v9 redesign rather than a larger matching replay.
