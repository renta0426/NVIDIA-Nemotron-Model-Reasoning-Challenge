# v20 snapshot FINAL_SUMMARY replacement report

> Repository note: canonical challenge contract lives in `README.md`.
> This report reviews whether parts of `A-Open-ProgressPrizePublication/nemotron/training/sft/04-08-16-14` should be rebuilt with `cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md`-aligned teacher traces while preserving the submission target as `submission.zip`.
> Measured score changes from any replacement run must be recorded in the relevant version ledger before promotion.

## Conclusion

**Yes, but only selectively.** The right move is **not** to rebuild the whole `04-08-16-14` snapshot from `FINAL_SUMMARY_REPORT.md`.

The README-grounded reason is:

1. The original A-Open win path already had strong deterministic coverage on easy families and a large slice of `bit_manipulation`.
2. The current audit shows that the earlier broad `default 1 contamination` story was wrong for the frozen v20 snapshot.
3. The remaining value of `FINAL_SUMMARY` is therefore **surgical replacement and teacher-correct overlay**, not wholesale regeneration.

## README-grounded framing

`A-Open-ProgressPrizePublication/README.md` says the winning bet was:

- deterministic code-generated chain-of-thought,
- strong `bit_manipulation`,
- Tinker SFT,
- minimum-logprob-oriented training,
- and a target `bit_manipulation` solve rate of `1364 / 1602 = 85.1%`, not 100%.

That matters because `FINAL_SUMMARY_REPORT.md` should be read as a **later audit and curation layer**, not as the original source of every trace inside `04-08-16-14`.

## What is actually aligned with FINAL_SUMMARY

There are two distinct layers:

| Layer | Relationship to `FINAL_SUMMARY_REPORT.md` | Practical reading |
| --- | --- | --- |
| Original v20 snapshot `04-08-16-14` | **Indirect / partial** | It comes from the original README-era Nemotron teacher pipeline, not from the later audit report. |
| Current corrective work (`v3_mainline`) | **Direct / strong** | It uses `FINAL_SUMMARY`-style curation: teacher-correct filtering, structured bit prioritization, and surgical base cleanup. |

So the current run is already moving in the correct direction: **keep the historical v20 base where it is proven safe, and apply `FINAL_SUMMARY` only where it adds audited value.**

## What should not be rewritten

### 1. Do not rewrite the whole snapshot

The frozen v20 snapshot is a historical training artifact. It should be treated as a base distribution, not as a file to regenerate blindly from today's repo state.

Reasons:

- current `reasoning/*.txt` and `problems.jsonl` are not guaranteed to be a perfect time match to the historical `04-08-16-14` snapshot,
- `nemotron/corpus.py` only includes `rule_found` rows for normal categories, so the mere existence of wrong reasoning files in the repo does **not** mean they all entered training,
- the snapshot contains many easy-family examples that README and later validation both show were already strong.

### 2. Do not use `default 1` as a blanket rewrite rule

This was the most important correction from the v3 audit.

- In the full binary reasoning pool, `default 1` is often dangerous.
- But in the actual v20 snapshot overlap, the `92` rows tied to `66` `default 1` base problems were teacher-correct.

Therefore:

- **`default 1` is a monitoring signal**
- **not an automatic replacement criterion**

## What should be replaced or excluded

### 1. Known metric-wrong base bit rows

This is the cleanest replacement target.

Current audited finding:

- known wrong base problem in the frozen v20 overlap: `ef2fe526`
- base rows affected: `ef2fe526`, `ef2fe526-p0`

This is why the current `v3_mainline` excludes `ef2fe526*` from the base snapshot.

### 2. Any future bit rows proven wrong by direct audit

The replacement policy should stay evidence-first:

1. verify the frozen snapshot row exists,
2. verify teacher boxed answer against `train.csv` using metric-consistent comparison,
3. only then remove or replace.

This is the safe pattern. Broad heuristics alone are not enough.

## What should be rebuilt with FINAL_SUMMARY-derived data

The high-EV use of `FINAL_SUMMARY` is **not** full snapshot reconstruction. It is:

1. **teacher-correct-only overlay**
2. **bit-heavy reallocation toward high-value families**
3. **small guardrails for easy families so binary strengthening does not regress them**

That is exactly the logic of `versions/v20_corrective_corpus_v3_mainline/`.

Current audited implementation properties:

- remove only the known wrong base problem `ef2fe526`,
- filter out `130` teacher-incorrect binary overlay candidates before selection,
- selected overlay teacher mismatches: `0`,
- concentrate overlay on:
  - `binary_structured_core`
  - `binary_other_light`
- keep easy-family guardrails light.

## Family-level recommendation

| Family / slice | Recommendation | Why |
| --- | --- | --- |
| stable easy families already strong in README (`numeral`, `gravity`, `unit`, much of `cipher`) | **Keep base as-is** | Little upside, unnecessary rewrite risk |
| `bit` rows with direct audited teacher error | **Replace / exclude** | Clear correctness win |
| `bit_structured_*` and other teacher-correct curated binary rows from `FINAL_SUMMARY` | **Add as overlay** | Best current upside per README and later proxy work |
| `default 1` snapshot rows with teacher-correct answers | **Keep unless a direct audit fails them** | Earlier blanket removal claim was false |
| answer-only / manual-review rows from `FINAL_SUMMARY` | **Do not use as automatic trace replacement** | They are not trace-safe by default |

## Answer to the main question

**Yes, some parts of `A-Open-ProgressPrizePublication/nemotron/training/sft/04-08-16-14` are worth rebuilding with `FINAL_SUMMARY`-aligned data, but only a narrow audited `bit` subset.**

The recommended policy is:

1. keep the frozen v20 snapshot as the base,
2. surgically remove known wrong base bit rows,
3. add only teacher-correct `FINAL_SUMMARY`-derived bit overlays,
4. avoid wholesale replacement of the historical snapshot,
5. record measured validation / proxy / leaderboard changes after every run.

## Operational implication for the current line

This report supports the current corrected mainline direction:

- **old v3 ablation**: too aggressive, removed many teacher-correct `default 1` rows
- **current `v3_mainline`**: correct direction, because it uses `FINAL_SUMMARY` as a curation and replacement aid rather than as a reason to discard the entire v20 base

In short: **rewrite a small audited `bit` subset, not the whole snapshot.**
