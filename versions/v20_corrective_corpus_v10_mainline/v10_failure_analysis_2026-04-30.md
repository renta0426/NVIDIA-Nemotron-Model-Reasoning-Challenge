# v10 failure analysis 2026-04-30

> Canonical basis: `README.md` and `A-Open-ProgressPrizePublication/README.md`.
> Goal checked here: whether v10 could stably reach official `0.87` by keeping the v4 public-safe distribution while adding v6 BIT donor and new BIT frontier lanes.

## 1. Conclusion

v10 is **not promoteable**. The official result was `0.84 x3`, and the local evidence says this is not noise.

The short version is:

1. v10 fixed local easy-family surface debt, especially numeral.
2. v10 did **not** improve the README-defined main lever, `bit_manipulation`.
3. v10 regressed two important binary rows relative to v4/v6: `0520a6ec` and `069dbaab`.
4. The new manual/frontier lanes did not suppress the `default 1` failure mode.
5. The run did not actually preserve the full v4 public-safe overlay distribution; it kept only a subset and replaced large mass with new binary frontier rows.

Therefore the official `0.84` result is consistent with the measured data. v10 looks good only if one over-weights local validation total, where the main gain is numeral repair rather than hidden/public BIT correctness.

## 2. Attachment / Evidence Checklist

Checked materials:

- Root `README.md`: official metric contract, deterministic evaluation, `\boxed{}` extraction, `max_tokens=7680`, `temperature=0.0`, `max_model_len=8192`.
- `A-Open-ProgressPrizePublication/README.md`: A-Open winning thesis: SFT only, deterministic CoT, min-logprob objective, bit manipulation as main differentiator, tokenization awareness, Nemotron weakness on spelling/splitting/symbol conversion.
- `A-Open-ProgressPrizePublication/v20_to_088_strategy.md`: v1-v3/v4/v6 interpretation, `default 1` as failure signature, v4/v6 donor logic, v3/v4/v6 public/proxy mismatch.
- `A-Open-ProgressPrizePublication/v20_snapshot_final_summary_replacement_report.md`: do not wholesale replace v20; use narrow audited BIT replacement/overlay; treat `default 1` as monitor, not automatic blacklist.
- `versions/v20_to_088_reassessment_2026-04-18.md`: row-level corrective limit, need separation of exact teacher / surface teacher / token-skill lanes.
- `versions/v10_bit_mainline_strategy_2026-04-23.md`: intended v10 architecture and promotion gates.
- `versions/v20_corrective_corpus_v10_mainline/reproduce_v20_corrective_corpus_v10_mainline.py`: actual data generation logic.
- `A-Open-ProgressPrizePublication/result/leaderboard_proxy_eval-v10`: proxy summary, row-level CSV, raw outputs.
- `A-Open-ProgressPrizePublication/result/results-v10`: validation CSV, results CSV, mistakes.

## 3. Scorecard

| version |         validation |              proxy |     proxy binary |           official | read                                       |
| ------- | -----------------: | -----------------: | ---------------: | -----------------: | ------------------------------------------ |
| v20     | `837/950 = 0.8811` | `176/200 = 0.8800` | `76/92 = 0.8261` |        `0.84-0.85` | original A-Open reproduction baseline      |
| v4      | `813/950 = 0.8558` | `179/200 = 0.8950` | `79/92 = 0.8587` | `0.85 x3, 0.86 x2` | best public distribution in this family    |
| v6      | `829/950 = 0.8726` | `180/200 = 0.9000` | `80/92 = 0.8696` |        `0.83-0.85` | strong BIT donor, public blind spot        |
| v7-1    | `839/950 = 0.8832` | `178/200 = 0.8900` | `78/92 = 0.8478` |             `0.84` | token-safe/easy recovery, no frontier gain |
| v8      | `834/950 = 0.8779` | `178/200 = 0.8900` | `78/92 = 0.8478` |        `0.83-0.84` | symbol/short exact did not help            |
| v9      | `823/950 = 0.8663` | `176/200 = 0.8800` | `76/92 = 0.8261` |       not promoted | matching auxiliary negative                |
| v10     | `839/950 = 0.8832` | `178/200 = 0.8900` | `78/92 = 0.8478` |          `0.84 x3` | local numeral repair, no BIT/public gain   |

v10 ties v7-1 on validation and proxy. It does not beat v4 or v6 on proxy binary, and it is below v4 on official score.

## 4. What Training Data Changed

### 4.1 v10 overlay composition

v10 selected:

- `568` selected unique rows
- `811` repeated overlay rows
- historical bundle footprint recorded before training:
  - base examples: `7828`
  - overlay examples: `811`
  - total examples: `8639`
  - total tokens: `29,885,798`
  - max sequence length: `7971`
  - reused base synthetic problem count: `298`
  - retokenized overlay problem count: `254`

Note: during the 2026-04-30 audit, the actual `v20_corrective_corpus_v10_mainline_bundle.jsonl` file was not present in the current working tree, so the footprint above is taken from the preserved v10 results record. Selection artifacts were regenerated without rewriting the training bundle.

Repeated rows by source mix:

| source mix                   | repeated rows |
| ---------------------------- | ------------: |
| `v10_verified_frontier`      |         `385` |
| `v4_public_base`             |         `318` |
| `v10_manual_frontier`        |          `48` |
| `v6_binary_donor`            |          `27` |
| `v6_numeral_surface_donor`   |          `10` |
| `v6_cipher_guardrail_donor`  |           `6` |
| `v6_unit_guardrail_donor`    |           `6` |
| `v6_gravity_guardrail_donor` |           `6` |
| `v6_symbol_prefix_donor`     |           `4` |
| `v10_numeral_surface_synth`  |           `1` |

Repeated rows by major bucket:

| bucket                         | repeated rows |
| ------------------------------ | ------------: |
| `binary_structured_exact_core` |         `204` |
| `binary_structured_core`       |         `176` |
| `binary_logic_exact`           |          `82` |
| `binary_other_light`           |          `64` |
| `binary_prompt_local_exact`    |          `51` |
| `binary_permutation_exact`     |          `48` |
| `binary_manual_frontier`       |          `48` |
| `surface_numeral_boxed*`       |          `47` |
| `surface_cipher_boxed*`        |          `14` |
| `surface_unit_tail*`           |          `14` |
| `easy_gravity_fragile*`        |          `18` |
| `surface_symbol_prefix*`       |           `6` |
| `surface_cryptarithm_boxed`    |          `12` |

Category mass:

- `bit_manipulation`: `700 / 811 = 86.3%`
- non-BIT guardrail/surface: `111 / 811 = 13.7%`

### 4.2 Comparison to v4

v4 repeated overlay rows: `808`.

v10 did **not** keep all of them. It kept `318` v4 unique IDs, added `121` new unique IDs, and removed/reduced `198` IDs relative to v4 repeat counts.

Important deltas vs v4:

| slice                             | v4 repeated |                               v10 repeated | read                                            |
| --------------------------------- | ----------: | -----------------------------------------: | ----------------------------------------------- |
| v4-style `binary_structured_core` |       `528` |                                      `176` | v4 long-trace structured mass cut by two thirds |
| v4-style `binary_other_light`     |       `128` |                                       `64` | v4 bit-other mass halved                        |
| v4-style surface rows             |       `152` | `78` from `v4_public_base` plus donor rows | not full v4 surface distribution                |
| new v10 verified frontier         |         `0` |                                      `385` | main replacement mass                           |
| new v10 manual frontier           |         `0` |                                       `48` | risky manual lane introduced                    |

This is the first major diagnosis: v10 was intended to keep the v4 public-safe backbone, but the actual overlay mix is closer to **v4 subset + large new BIT replacement**. If v4's public edge came from the exact v4 overlay distribution, v10 had already moved away from it.

### 4.3 Comparison to v6

v6 repeated overlay rows: `673`.

v10 added mass over v6 but did not simply import v6:

- shared unique IDs with v6: `232`
- v10-only unique IDs: `207`
- v6-only unique IDs: `160`

v10 imported only `27` rows as explicit `v6_binary_donor`, plus `32` v6 surface/guardrail rows. The rest of BIT mass was regenerated as v10 verified/manual frontier. This means v10 was not a faithful v6 BIT transplant either.

## 5. Local Validation Behavior

v10 validation:

| category                  | correct / total | accuracy |
| ------------------------- | --------------: | -------: |
| `bit_manipulation`        |     `149 / 169` | `0.8817` |
| `cipher`                  |     `161 / 162` | `0.9938` |
| `cryptarithm_deduce`      |        `5 / 71` | `0.0704` |
| `cryptarithm_guess`       |        `3 / 14` | `0.2143` |
| `equation_numeric_deduce` |       `42 / 48` | `0.8750` |
| `equation_numeric_guess`  |         `0 / 7` | `0.0000` |
| `gravity`                 |     `159 / 159` | `1.0000` |
| `numeral`                 |     `149 / 149` | `1.0000` |
| `unit_conversion`         |     `171 / 171` | `1.0000` |
| total                     |     `839 / 950` | `0.8832` |

Validation deltas show the real source of the local gain:

- vs v6: `+18 / -8`, net `+10`
  - gains: `11` numeral, `5` bit, `1` cipher, `1` gravity
  - losses: `6` bit, `1` cryptarithm, `1` cipher
- vs v7-1: `+4 / -4`, net `0`
  - gains: `2` bit, `1` numeral, `1` gravity
  - losses: `3` bit, `1` cipher
- vs v4: `+33 / -7`, net `+26`
  - gains dominated by `25` numeral rows
  - losses include `0520a6ec`, `069dbaab`, `065abaf6`, `0c2243ff`

Interpretation:

- The v10 validation score is high because numeral and unit/gravity are repaired.
- The validation BIT score is not improved: v10 is `149/169`, below v4/v6/v7-1/v9 (`150/169`).
- This local score is therefore not evidence that v10 is closer to official `0.87`.

## 6. Proxy Behavior

v10 proxy:

| slice   | correct / total | accuracy |
| ------- | --------------: | -------: |
| overall |     `178 / 200` | `0.8900` |
| binary  |       `78 / 92` | `0.8478` |
| symbol  |       `24 / 32` | `0.7500` |
| roman   |       `19 / 19` | `1.0000` |
| gravity |       `19 / 19` | `1.0000` |
| text    |       `20 / 20` | `1.0000` |
| unit    |       `18 / 18` | `1.0000` |

Template detail:

- `bit_other`: `27/35`, worse than v4/v6.
- `bit_structured_byte_formula`: `25/31`, tied with v4/v7-1/v8/v9 and below v6.
- `bit_permutation_inversion`: `26/26`, recovered from v9.
- `numeric_2x2`: `23/27`, unchanged.
- `glyph_len5`: `1/5`, unchanged.

Proxy flips vs prior runs:

| comparison | v10 gains | v10 losses |  net | meaning                                           |
| ---------- | --------: | ---------: | ---: | ------------------------------------------------- |
| vs v4      |       `1` |        `2` | `-1` | below best public run                             |
| vs v6      |       `0` |        `2` | `-2` | failed to transplant strongest BIT donor behavior |
| vs v7-1    |       `1` |        `1` |  `0` | effectively same as v7-1                          |
| vs v8      |       `2` |        `2` |  `0` | effectively same as v8                            |
| vs v9      |       `3` |        `1` | `+2` | recovers some v9 matching damage only             |

Concrete proxy changes:

- vs v4:
  - gain: `59c78e51`
  - losses: `0520a6ec`, `069dbaab`
- vs v6:
  - no gains
  - losses: `0520a6ec`, `c30a782a`
- vs v9:
  - gains: `14a72508`, `59c78e51`, `b9500f41`
  - loss: `0520a6ec`

This is the second major diagnosis: v10 mostly recovered from v9's matching-auxiliary damage, but it did not exceed v4/v6 on the proxy rows that matter.

## 7. Raw Output Changes

### 7.1 `default 1` was not suppressed

Binary proxy raw-output metrics:

| version | binary wrong | `default 1` rows | wrong rows with `default 1` | bad binary format |
| ------- | -----------: | ---------------: | --------------------------: | ----------------: |
| v4      |         `13` |             `14` |                        `12` |               `0` |
| v6      |         `12` |             `13` |                        `10` |               `1` |
| v7-1    |         `14` |             `15` |                        `12` |               `0` |
| v8      |         `14` |             `14` |                        `11` |               `0` |
| v9      |         `16` |             `16` |                        `14` |               `1` |
| v10     |         `14` |             `15` |                        `12` |               `1` |

v10 is not closer to v6 here. It is basically v7-1/v8-level and worse than v6. The anti-default1 lane did not move the aggregate failure mode.

### 7.2 `0520a6ec` is the most damaging unexpected regression

This row was correct in v4/v6/v7-1/v8/v9:

- gold: `10100001`
- v4-v9 prediction: `10100001`
- v10 prediction: `01100001`

The raw v10 trace reintroduced `default 1`:

```text
Selected: ... AND-NOT25, AND-NOT36, default 1, I4, I5, I6, I7, I0
Output: ... 2 default 1 = 1 ...
\boxed{01100001}
```

This was not expected. The row was included from multiple routes in v10 selection (`v4_public_base`, `v6_binary_donor`, `v10_verified_frontier`), yet the model moved away from the correct v4/v6 behavior. That means the new global distribution interfered with a previously stable row.

### 7.3 `c30a782a` failed to inherit the v6 correction

- gold: `01000110`
- v6 prediction: `01000110`
- v4/v7-1/v8/v9/v10 prediction: `01010110`

v6 had learned the missing `AND-NOT07` closure. v10 still emitted `default 1` at bit 3:

```text
Output:
0 AND-NOT54 = 0
1 AND-NOT65 = 1
2 AND-NOT76 = 0
3 default 1 = 1
...
\boxed{01010110}
```

This directly falsifies the v10 donor hypothesis. v10 included `c30a782a` as both `v6_binary_donor` and `v10_verified_frontier`, but the output stayed in the non-v6 failure basin.

### 7.4 `59c78e51` shows that some v6 donor behavior did transfer

- gold: `00000000`
- v4: `00001101`
- v6/v7-1/v8: `00000000`
- v9: `00001111`
- v10: `00000000`

This is a real positive result. v10 switched from `default 1`-style output to exact `AND01/AND12/AND23/AND34` closure. So the donor idea is not categorically wrong; it is simply too weak/inconsistent to carry the run.

### 7.5 `069dbaab` is a public-risk regression

Proxy:

- gold: `00010000`
- v4: `00010000`
- v8: `00010000`
- v10 raw final trace internally reaches `\boxed{00010001}`, then degenerates to `\boxed{0}`.

This row demonstrates a different failure mode from ordinary content drift: terminal answer corruption after an almost valid binary output.

```text
... Output ... 7 AND15 = 1
The answer in \boxed is
\boxed{00010001}
</think>
\boxed{0}
```

The metric extracts `0`, so this is both content wrong and terminal-surface unstable. It is especially bad because v4 had this row correct.

### 7.6 Manual frontier rows did not become reliable

v10 proxy wrong binary rows include many manual/no-solver rows:

- `069dbaab`: bad final format / `0`
- `101410e4`: `default 1`, gold `10001101`, pred `10011101`
- `12154247`: `default 1`, gold `10111101`, pred `11111101`
- `12fd5b6c`: `default 1`, gold `11001111`, pred `11011111`
- `2230fad0`: `default 1`, gold `01001010`, pred `01111110`
- `257e7158`: `default 1`, gold `00001001`, pred `00001111`

The proxy selection-tier accuracy confirms the issue:

- `verified_trace_ready`: `149/156 = 0.9551`
- `answer_only_keep`: `21/26 = 0.8077`
- `manual_audit_priority`: `8/18 = 0.4444`

This is the third major diagnosis: `manual_audit_priority` is not ready as a training lane unless the exact closure is substantially better verified or converted into a safer contrast/surface-only form.

### 7.7 Symbol outputs did not move, as expected

v10 did not include broad symbol training. The proxy symbol result remained:

- overall symbol: `24/32`
- `numeric_2x2`: `23/27`
- `glyph_len5`: `1/5`

Wrong examples remain the same type:

- `8158a14c`: gold `46`, pred `)46`
- `b7b1d1a8`: gold `57`, pred `"42`
- `a85864a9`: gold `(\}:`, pred `(\::`

This part is not surprising. It was an accepted tradeoff in v10 strategy, but it means v10 had no upside from symbol.

## 8. Was v10 Behavior Expected?

Partly yes, mostly no.

Expected and confirmed:

1. Broad symbol did not improve because v10 did not fund it.
2. v9 matching damage was partly undone: `14a72508` and `b9500f41` recovered.
3. Local easy surface improved: numeral reached `149/149`, unit and gravity reached `100%`.
4. Some v6 donor behavior transferred: `59c78e51` was recovered.

Unexpected and harmful:

1. v10 did not preserve v4 public-safe behavior. Proxy fell from v4 `179` to v10 `178`, and official fell from v4's `0.85-0.86` to `0.84 x3`.
2. v10 did not transplant v6 binary gain. Proxy binary fell from v6 `80/92` to v10 `78/92`, with no gains vs v6 and two losses.
3. `default 1` persisted at nearly the same rate as weaker runs.
4. `0520a6ec` regressed despite being represented in v4/v6/v10 lanes.
5. Manual frontier rows remained highly unreliable.

## 9. Why Official `0.84 x3` Is Plausible

The official score is not contradicted by local `839/950`.

The README/A-Open contract says the highest-upside slice is bit manipulation, and v10 did not improve it:

- validation BIT: `149/169`, below v4/v6/v7-1/v9
- proxy BIT: `78/92`, below v4/v6 and equal to v7-1/v8
- proxy `default 1` wrong rows: `12`, not improved
- manual/no-solver proxy remains weak

v10's local validation score is inflated by local easy-family repair:

- numeral: `149/149`
- unit: `171/171`
- gravity: `159/159`

Those are good guardrails, but they are not enough to move official score toward `0.87` when the binary frontier is flat or worse.

## 10. Root Cause

The main root cause is **data-distribution interference**.

v10 tried to combine:

1. v4 public-safe overlay subset
2. v6 donor rows
3. new v10 verified frontier
4. risky manual frontier
5. restored surface guardrails

But the resulting distribution was not strong enough to preserve known-good v4/v6 binary behaviors, and it was not strong enough to create new hard-core BIT wins.

Two concrete signs:

- `0520a6ec` was correct in every prior strong branch but became `default 1` wrong in v10.
- `c30a782a` was corrected only by v6 and v10 failed to copy that behavior despite explicit donor rows.

This suggests the model did not simply memorize selected rows by ID. It followed the dominant training style/distribution, and v10's mixture pulled some rows into older or newly unstable rule-selection basins.

## 11. What Not To Do Next

Do not treat v10 as close to success. It is not a near miss.

Avoid:

1. Increasing v10 frontier mass further without fixing interference.
2. Adding more `manual_audit_priority` as full trace training.
3. Using local validation total as the primary promotion gate.
4. Assuming v4 public-safe distribution is preserved merely because some `v4_public_base` rows are reused.
5. Repeating broad matching auxiliary restoration; v9 already measured it negative.

## 12. Recommended Next Direction

The next mainline should be a stricter ablation, not another mixed expansion.

Recommended order:

1. Re-establish v4 public baseline exactly.
   - Keep all v4 overlay mass unless an ablation proves a subset is safe.
   - Do not replace v4 surface/binary mass while testing a donor.

2. Add only the proven v6 donor rows that caused measured wins.
   - `59c78e51` positive.
   - `c30a782a` needs isolated transplant testing because v10 failed it.
   - Keep `0520a6ec` as mandatory no-regression gate.

3. Remove or quarantine manual frontier from mainline.
   - Manual rows should become diagnostic/contrast rows only after exact closure is verified.
   - `manual_audit_priority` proxy accuracy `8/18` is too low for mainline.

4. Add a public-risk mini gate before full train promotion.
   - Must include `0520a6ec`, `069dbaab`, `c30a782a`, `59c78e51`, `b9500f41`, `14a72508`, and the persistent hard core.

5. Promotion gate should require:
   - proxy overall >= v4 (`179/200`) and ideally >= v6 (`180/200`)
   - proxy binary >= `80/92`
   - no regression on `0520a6ec` / `069dbaab`
   - validation numeral remains `149/149` or near-perfect, but this is guardrail only
   - official pilot must beat v4 distribution, not merely v20

## 13. Final Read

v10 answered the question it was supposed to answer: **v4 subset + v6 donor + new frontier is not a safe route to official `0.87`**.

The data changes were mostly implemented as designed, but the design assumption was wrong. The model did not preserve v4 public behavior, did not consistently inherit v6 BIT behavior, and did not suppress `default 1`. The raw outputs show that the main failure is still binary rule selection/content drift, not boxed extraction on proxy.

v10 should be treated as a failed mixed mainline and a useful negative result. The next useful experiment is a narrow, controlled v4-plus-proven-donor ablation with manual frontier removed from the mainline.
