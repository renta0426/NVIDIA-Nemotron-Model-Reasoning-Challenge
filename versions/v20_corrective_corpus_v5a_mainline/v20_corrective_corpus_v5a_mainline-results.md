# v20_corrective_corpus_v5a_mainline results

> Repository note: canonical challenge contract lives in `A-Open-ProgressPrizePublication/README.md`.
> This report records the measured v5a scores, the training-data differences from v4, and the observed effect on raw outputs.

## Executive summary

v5a was the first attempt to execute the `v5` idea from `A-Open-ProgressPrizePublication/v20_to_088_strategy.md` as a real run:

- Stage A: verified binary core with short family/query/closure supervision
- Stage C: short easy-family boxed-surface stabilizer
- Stage B: intentionally excluded

The measured result is clear.

- Official leaderboard, user-reported over 2 submissions:
	- `0.85 x 2`
	- mean: `0.8500`
	- min / max: `0.85 / 0.85`
- Local validation: `829 / 950 = 0.8726`
- Leaderboard proxy: `173 / 200 = 0.8650`

So v5a did **not** reproduce the v4 public improvement pattern.

What it actually did was:

1. **Recover local easy-family stability** relative to v4, especially numeral and unit.
2. **Lose the proxy binary frontier** that had explained the v4 public gain.
3. Therefore land on a public score that is roughly the **lower edge of v4**, not an improvement over it.

In one sentence: **v5a proved that the short Stage C surface stabilizer works locally, but the current Stage A implementation is too lossy to preserve v4's binary public edge.**

## README-grounded interpretation

The A-Open README still gives the correct lens for this run.

- The main upside slice is still `bit manipulation`.
- Deterministic chain-of-thought and tokenization awareness still matter.
- Easy tasks can still fail if the final `\boxed{...}` surface is unstable.
- Nemotron remains weak at spelling / splitting / symbol handling.

v5a matches that picture almost perfectly.

- On the **local side**, Stage C repaired exactly the kind of boxed-surface failures the README warns about.
- On the **public/proxy side**, the main loss came from binary content correctness, which the README identifies as the key medal-driving slice.
- Because this run is direct Kaggle-compatible SFT rather than Tinker -> submission conversion, these regressions are **not best explained by SVD misalignment**. They are better explained by the v5a data/trace design itself.

## Scorecard

| version | validation | proxy | public leaderboard | interpretation |
| --- | ---: | ---: | ---: | --- |
| v20 | `837/950 = 0.8811` | `176/200 = 0.8800` | README: `0.85 x3`, `0.84 x5` | strong easy families, weaker binary frontier |
| v4_mainline | `813/950 = 0.8558` | `179/200 = 0.8950` | user-reported `0.85 x3`, `0.86 x2` | partial surface recovery plus preserved binary gain |
| v5a_mainline | `829/950 = 0.8726` | `173/200 = 0.8650` | user-reported `0.85 x2` | local easy-family recovery, but binary proxy/public collapse |

The key asymmetry is:

- v5a beats v4 by `+16` rows on local validation.
- v5a loses to v4 by `-6` rows on the leaderboard proxy.
- public comes down with proxy, not up with validation.

That strongly suggests the hidden/public set is still paying more for binary frontier quality than for the local numeral/unit recovery that v5a achieved.

## Generated artifacts

- generator: `versions/v20_corrective_corpus_v5a_mainline/reproduce_v20_corrective_corpus_v5a_mainline.py`
- selection csv: `versions/v20_corrective_corpus_v5a_mainline/outputs/canonical_build/artifacts/corrective_selection.csv`
- summary json: `versions/v20_corrective_corpus_v5a_mainline/outputs/canonical_build/artifacts/corrective_overlay_summary.json`
- report md: `versions/v20_corrective_corpus_v5a_mainline/outputs/canonical_build/reports/corrective_overlay_report.md`
- training bundle: `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v5a_mainline_bundle.jsonl`
- measured validation: `A-Open-ProgressPrizePublication/result/results-v5/validation.csv`
- measured proxy: `A-Open-ProgressPrizePublication/result/leaderboard_proxy_eval-v5/artifacts/leaderboard_proxy_eval_row_level.csv`

## Training-data summary

### v5a canonical bundle

- selected unique rows: `244`
- selected repeated rows: `622`
- base examples: `7828`
- total examples: `8450`
- total steps: `265`
- total tokens: `28,043,350`
- max seq len: `7971`

### Selected unique rows by bucket

- `binary_verified_core`: `192`
- `surface_numeral_boxed`: `34`
- `surface_cipher_boxed`: `6`
- `surface_unit_tail`: `6`
- `easy_gravity_fragile`: `6`

### Repeated rows by bucket

- `binary_verified_core`: `570`
- `surface_numeral_boxed`: `34`
- `surface_cipher_boxed`: `6`
- `surface_unit_tail`: `6`
- `easy_gravity_fragile`: `6`

### Canonical validation of the bundle itself

- canonical checks: `pass`
- mandatory anchor missing: `0`
- Stage A non-verified rows: `0`
- Stage B-like contamination in Stage A: `0`
- unexpected Stage C categories: `0`
- Stage A max think lines: `4`
- Stage C max think lines: `3`
- retokenized overlay problem count: `244`
- retokenized overlay example count: `622`

## v4 -> v5a corpus differences

The largest design shift from v4 to v5a was not just "more binary". It was **more abstract binary, much less surface, and much shorter supervision**.

| slice | v4 | v5a | delta |
| --- | ---: | ---: | ---: |
| overlay repeated rows | `808` | `622` | `-186` |
| total tokens | `32,858,695` | `28,043,350` | `-4,815,345` |
| total steps | `271` | `265` | `-6` |
| repeated binary rows | `656` | `570` | `-86` |
| repeated surface/easy rows | `152` | `52` | `-100` |
| repeated binary share | `81.2%` | `91.6%` | `+10.4pt` |
| repeated surface/easy share | `18.8%` | `8.4%` | `-10.4pt` |

Important implications:

1. v5a **reduced total binary rows** relative to v4, not just surface rows.
2. v5a **removed all symbol-prefix and cryptarithm symbolic repair lanes** that had existed in v4.
3. v5a Stage C became very small in absolute size, but much more targeted.
4. v5a Stage A became much more abstract and much less row-specific.

### What Stage A actually emphasized

Stage A family distribution:

- `xor(shl,shr)`: `99`
- `choose(shl,shr,rol)`: `18`
- `choose(shl,shr,ror)`: `16`
- `majority(ror,shl,shr)`: `16`
- `majority(rol,shl,shr)`: `16`
- `xor(ror,shl)`: `10`
- `or(rol,shr)`: `8`
- `or(ror,shr)`: `3`

Stage A subtype / solver composition:

- template subtype:
	- `bit_structured_byte_formula`: `102`
	- `bit_other`: `87`
	- `bit_permutation_inversion`: `3`
- teacher solver candidate:
	- `binary_structured_byte_formula`: `92`
	- `binary_two_bit_boolean`: `38`
	- `binary_affine_xor`: `37`
	- `binary_structured_byte_formula_abstract`: `9`
	- `binary_bit_permutation_bijection`: `2`
	- `binary_bit_permutation_independent`: `1`

This is the first hard warning sign in the data.

- v5a proxy regressions later concentrate in `bit_permutation_inversion` and `bit_structured_byte_formula`.
- Yet Stage A gives only `3` unique permutation rows and only `3` permutation-family solver rows in total (`2` bijection + `1` independent).

So the current v5a curriculum **broadens abstract binary families**, but it also **underweights exact permutation / bijection supervision**.

### What Stage C actually emphasized

Overlay token share by bucket:

- `binary_verified_core`: `0.9613`
- `surface_numeral_boxed`: `0.0222`
- `easy_gravity_fragile`: `0.0060`
- `surface_cipher_boxed`: `0.0055`
- `surface_unit_tail`: `0.0049`

So only `3.87%` of overlay tokens were spent on Stage C buckets in total.

Despite that, Stage C still produced large local gains. That means the v5a **surface repair lane is much more token-efficient than the v4 repair lane**, even though it is too small to matter for public once binary regresses.

## Local results analysis

### Category-level scores

| category | v20 | v4 | v5a |
| --- | ---: | ---: | ---: |
| bit_manipulation | `149/169 = 88.2%` | `150/169 = 88.8%` | `148/169 = 87.6%` |
| cipher | `158/162 = 97.5%` | `161/162 = 99.4%` | `161/162 = 99.4%` |
| cryptarithm_deduce | `6/71 = 8.5%` | `5/71 = 7.0%` | `5/71 = 7.0%` |
| cryptarithm_guess | `3/14 = 21.4%` | `3/14 = 21.4%` | `3/14 = 21.4%` |
| equation_numeric_deduce | `42/48 = 87.5%` | `43/48 = 89.6%` | `43/48 = 89.6%` |
| equation_numeric_guess | `0/7 = 0.0%` | `0/7 = 0.0%` | `0/7 = 0.0%` |
| gravity | `159/159 = 100.0%` | `159/159 = 100.0%` | `159/159 = 100.0%` |
| numeral | `149/149 = 100.0%` | `124/149 = 83.2%` | `139/149 = 93.3%` |
| unit_conversion | `171/171 = 100.0%` | `168/171 = 98.2%` | `171/171 = 100.0%` |
| TOTAL | `837/950 = 88.1%` | `813/950 = 85.6%` | `829/950 = 87.3%` |

### v4 -> v5a delta

- improved rows: `25`
- regressed rows: `9`

Improved by category:

- numeral: `16`
- unit_conversion: `3`
- bit_manipulation: `4`
- cryptarithm_deduce: `1`
- cipher: `1`

Regressed by category:

- bit_manipulation: `6`
- numeral: `1`
- cipher: `1`
- cryptarithm_deduce: `1`

So almost the whole local lift comes from **numeral + unit recovery**. Binary is actually net `-2` rows versus v4 on validation.

### v20 -> v5a delta

- improved rows: `9`
- regressed rows: `17`

Regressed by category:

- numeral: `10`
- bit_manipulation: `5`
- cryptarithm_deduce: `1`
- cipher: `1`

So v5a still does **not** catch back up to v20 on local validation. It recovers much of v4's easy-family damage, but it remains below the v20 baseline by `8` rows.

### What local wrong rows now look like

Wrong-row tier distribution in v5a validation:

| category | answer_only_keep | verified_trace_ready | other/blank |
| --- | ---: | ---: | ---: |
| bit_manipulation | `2` | `17` | `2` |
| cipher | `1` | `0` | `0` |
| cryptarithm_deduce | `66` | `0` | `0` |
| cryptarithm_guess | `11` | `0` | `0` |
| equation_numeric_deduce | `4` | `0` | `1` |
| equation_numeric_guess | `7` | `0` | `0` |
| numeral | `0` | `10` | `0` |

This is exactly the shape the v5 strategy expected in theory:

- easy-family debt is now much smaller and sits on `verified_trace_ready` rows,
- cryptarithm/equation wrongs remain overwhelmingly `answer_only_keep`,
- binary debt remains a `verified_trace_ready` frontier problem.

But v5a does **not** turn that cleaner local decomposition into better public performance yet.

## Raw-output impact on local validation

### 1. Stage C really did fix numeral and unit endings

This is the strongest success of v5a.

Representative numeral recoveries:

- `00d9f682`
	- v4 tail: `I will now return the answer in \box` then plain `C`
	- v5a tail: `I will now return the answer in \boxed{}` then `\boxed{C}`
	- result: wrong -> correct
- `0186fc54`
	- v4: plain `LXIV`
	- v5a: `\boxed{LXIV}`
- `07214cbb`, `076fda72`, `078e4ee7`, `0805b912`, `0aa2c5bf`
	- same pattern

Representative unit recovery:

- `033826f6`
	- v4 final numeric line: `19.144`
	- v5a final numeric line: `29.144`
	- result: wrong -> correct

Measured surface heuristics confirm the same thing.

| heuristic on wrong validation rows | v4 | v5a |
| --- | ---: | ---: |
| total `box_not_boxed` | `32` | `19` |
| numeral `box_not_boxed` | `25` | `10` |
| cipher `box_not_boxed` | `1` | `0` |

Also, of the `16` numeral rows improved from v4 to v5a, `12` were directly selected into the v5a overlay, and the remaining `4` improved by generalization. So Stage C is not only fixing anchors; it is transferring to nearby rows.

### 2. Local binary did improve in some places

v5a Stage A is not a total failure. It does repair some binary rows.

Representative local binary recoveries:

- `034fb629`
	- v4: `01111001`
	- v5a: `00111001`
- `0dd5caf4`
	- v4: `01000000`
	- v5a: `00000000`
- `1496dfeb`
	- v4: `11111100`
	- v5a: `00000000`

However, this is not enough to offset the proxy/public regressions described below.

### 3. Symbolic endings got noisier once v4 repair lanes were removed

Although v5a did not materially change cryptarithm scores, the raw outputs show that symbolic ending quality got slightly worse once v4's symbolic repair lanes were dropped.

Heuristic counts on wrong validation rows:

| heuristic | v4 | v5a |
| --- | ---: | ---: |
| cryptarithm_deduce `box_not_boxed` | `2` | `5` |
| cryptarithm_deduce `backslash_wrap_like` | `4` | `5` |
| cryptarithm_guess `backslash_wrap_like` | `0` | `1` |

So removing symbolic repair lanes did not move topline, but it did make some raw outputs uglier again.

## Proxy analysis

### Overall and family slices

| slice | v20 | v4 | v5a |
| --- | ---: | ---: | ---: |
| overall | `176/200 = 0.8800` | `179/200 = 0.8950` | `173/200 = 0.8650` |
| binary | `76/92 = 0.8261` | `79/92 = 0.8587` | `74/92 = 0.8043` |
| symbol | `24/32 = 0.7500` | `24/32 = 0.7500` | `23/32 = 0.7188` |
| gravity | `19/19 = 1.0000` | `19/19 = 1.0000` | `19/19 = 1.0000` |
| roman | `19/19 = 1.0000` | `19/19 = 1.0000` | `19/19 = 1.0000` |
| text | `20/20 = 1.0000` | `20/20 = 1.0000` | `20/20 = 1.0000` |
| unit | `18/18 = 1.0000` | `18/18 = 1.0000` | `18/18 = 1.0000` |

This is the central fact of the run.

- v5a gains nothing over v4 on proxy.
- v5a regresses by `6` rows versus v4.
- `5` of those `6` regressions are binary.

### v4 -> v5a proxy row-level delta

- improved rows: `0`
- regressed rows: `6`

Regressed IDs:

- binary: `04183bf9`, `fa67da07`, `26a70ae0`, `0520a6ec`, `e20d3f48`
- symbol: `d9bedb64`

There are **no** offsetting proxy wins.

### v20 -> v5a proxy row-level delta

- improved rows: `1` -> `0a50c4a8`
- regressed rows: `4` -> `04183bf9`, `d9bedb64`, `26a70ae0`, `e20d3f48`

So v5a does not even hold the v20 baseline on proxy. It keeps only one of the v4 binary wins and gives back several others.

### Key subtype movement

| proxy subtype | v20 | v4 | v5a |
| --- | ---: | ---: | ---: |
| `bit_structured_byte_formula` | `23/31` | `25/31` | `23/31` |
| `bit_other` | `28/35` | `28/35` | `28/35` |
| `bit_permutation_inversion` | `25/26` | `26/26` | `23/26` |
| `numeric_2x2` | `23/27` | `23/27` | `22/27` |
| `glyph_len5` | `1/5` | `1/5` | `1/5` |

This lines up exactly with the v5a data design.

- `bit_other` stays flat.
- `bit_structured_byte_formula` falls back from v4's gain to the v20 level.
- `bit_permutation_inversion` is hit hardest, dropping below both v4 and v20.
- `numeric_2x2` loses one row after v5a removed symbol-prefix repair.

## Raw-output impact on proxy/public slices

### 1. Binary format stayed perfect, but content got worse

The problem in v5a is **not** output formatting.

Binary proxy metrics:

| metric | v4 | v5a |
| --- | ---: | ---: |
| boxed extraction success | `1.0` | `1.0` |
| regex exact | `1.0` | `1.0` |
| leading zero retention | `1.0` | `1.0` |
| format failure rate | `0.0` | `0.0` |
| format-ok content-wrong rate | `0.1413` | `0.1957` |

That is exactly the wrong direction for a binary-focused v5.

The proxy says: **v5a did not break the 8-bit wrapper; it broke the binary content line inside the wrapper.**

### 2. `default 1` rose again on proxy binary wrong rows

Count of proxy binary wrong rows containing `default 1` in raw output:

- v20: `16 / 16`
- v4: `12 / 13`
- v5a: `14 / 18`

So v5a partially reintroduced the exact failure mode that v4 had reduced.

### 3. Representative binary regressions show loss of concrete rule fidelity

#### `0520a6ec` — selected in v5a overlay, but regressed anyway

- v4 output:
	- exact scaffold includes `AND-NOT15`, `AND-NOT26`, `AND-NOT37`
	- final answer: `10100001`
- v5a output:
	- scaffold shrinks to `AND-NOT25`, `AND-NOT36`, then `default 1`
	- final answer: `01100001`

Interpretation:

- v5a did include this row as a mandatory Stage A example,
- but the shorter family/query supervision was not enough to preserve the concrete 3-rule closure that v4 had learned.

#### `fa67da07` — selected in v5a overlay, permutation row regresses

- v4 output:
	- exact permutation mapping reaches `11101011`
- v5a output:
	- one position falls back to `default 1`
	- final answer: `11101111`

Interpretation:

- this is a canonical sign that the current short binary curriculum is too weak for hard permutation rows,
- even when the row is explicitly included in Stage A.

#### `26a70ae0` — selected in v5a overlay, structured row loses the first bit

- v4 final answer: `10010101`
- v5a final answer: `01010101`

Interpretation:

- most of the rule is still there,
- but the query-specific closure of the leading bit is lost.
- This is exactly the kind of row where family-level abstraction alone is not enough.

#### `04183bf9` and `e20d3f48` — not selected in v5a overlay

- both are `bit_permutation_inversion`
- both regress from exact index copying in v4 to simplified wrong mappings in v5a

Interpretation:

- the dedicated permutation lane in v5a is too thin,
- and the rows that were not explicitly selected were not protected by the new curriculum.

### 4. Symbol regression matches the removed v4 repair lane

`d9bedb64` is the cleanest symbol example.

- v4 output restores the operator prefix and returns `\boxed{(1}`
- v5a output returns `\boxed{1}`

This is exactly what should happen if v4's narrow symbol-prefix repair is removed and nothing replaces it.

## What the data difference actually caused

The causal picture is now fairly clear.

### What worked

1. **Short tail-only Stage C worked**.
	 - numeral `124 -> 139`
	 - unit `168 -> 171`
	 - total `box_not_boxed` `32 -> 19`
2. **The repair was efficient**.
	 - only `52` repeated Stage C rows,
	 - only `3.87%` of overlay tokens,
	 - yet large local recovery.

### What failed

1. **Stage A got too abstract and too thin**.
	 - binary repeated rows `656 -> 570`
	 - unique binary overlay `240 -> 192`
	 - permutation supervision only `3` unique rows
2. **Measured v4 binary wins were not preserved**.
	 - v20 -> v4 proxy gains had been `fa67da07`, `0520a6ec`, `0a50c4a8`
	 - v5a keeps only `0a50c4a8`
	 - `fa67da07` and `0520a6ec` both regress
3. **Removing symbol/cryptarithm repairs had predictable side effects**.
	 - symbol proxy `24/32 -> 23/32`
	 - cryptarithm raw endings get noisier even without topline movement

### Net interpretation

v5a validated only **half** of the v5 hypothesis.

- Correct half: easy-family boxed-surface alignment should be separated and shortened.
- Incorrect half in its current implementation: verified binary can be pushed far enough using the current short family/query/closure curriculum alone.

The current v5a Stage A supervision is too compressed to carry the exact row-level binary content that v4 had preserved on the public-driving proxy slices.

## Artifact caveat

As with earlier runs, `validation.csv` must not be read by trusting the `predicted` column as an authoritative score source.

Rows with `correct=True` but `predicted != answer`:

- v20: `352`
- v4: `344`
- v5a: `348`

These mismatches concentrate mainly in:

- `gravity`
- `unit_conversion`
- to a smaller but still relevant extent `bit_manipulation`

Therefore this report treats:

- `correct` as the authoritative measured label,
- raw output as qualitative evidence,
- `predicted` only as a debugging aid.

## Conclusion

v5a is **not** a promotion over v4.

What v5a proved:

1. the short Stage C boxed-surface stabilizer is real and should be kept,
2. local numeral/unit debt can be reduced with far fewer tokens than v4 used,
3. Stage-separated objectives are the right framing.

What v5a disproved:

1. the current short Stage A curriculum is not enough to preserve v4's binary public edge,
2. permutation / bijection rows cannot be left as a tiny side case,
3. removing all symbol-prefix and cryptarithm repair lines has a measurable downside.

The most defensible next-step judgment is:

- **keep v5a Stage C almost as-is**, because it worked;
- **rebuild Stage A**, because that is where the public/proxy loss came from;
- **restore a small dedicated permutation/bijection exact lane**;
- **reintroduce a minimal symbol-prefix repair lane** if cheap;
- do **not** assume that family-level short traces can replace concrete rule-level supervision on the hardest binary rows.

## Score record

- local validation: `829 / 950 = 0.8726`
- proxy: `173 / 200 = 0.8650`
- public leaderboard: `0.85 x 2`