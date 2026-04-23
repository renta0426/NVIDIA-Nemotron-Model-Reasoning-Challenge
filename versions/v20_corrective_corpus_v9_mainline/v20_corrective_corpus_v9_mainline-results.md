# v20 corrective corpus v9 mainline results

## Status

- Created: 2026-04-23 UTC
- Generator: versions/v20_corrective_corpus_v9_mainline/reproduce_v20_corrective_corpus_v9_mainline.py
- Strategy note: versions/v20_corrective_corpus_v9_mainline/v20_corrective_corpus_v9_mainline_strategy_2026-04-23.md
- Bundle audit: versions/v20_corrective_corpus_v9_mainline/v20_corrective_corpus_v9_mainline_bundle_audit_2026-04-23.md
- Bundle: A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v9_mainline_bundle.jsonl
- Overlay report: versions/v20_corrective_corpus_v9_mainline/outputs/v9_mainline_default/reports/corrective_overlay_report.md
- Overlay summary: versions/v20_corrective_corpus_v9_mainline/outputs/v9_mainline_default/artifacts/corrective_overlay_summary.json
- Git-tracked generated artifacts: versions/v20_corrective_corpus_v9_mainline/outputs/v9_mainline_default/artifacts/corrective_selection.csv, versions/v20_corrective_corpus_v9_mainline/outputs/v9_mainline_default/artifacts/corrective_overlay_summary.json, versions/v20_corrective_corpus_v9_mainline/outputs/v9_mainline_default/reports/corrective_overlay_report.md
- Current state: bundle generated and measured on local validation plus README-contract leaderboard proxy; official leaderboard is still pending
- Training / validation / leaderboard score:
  - validation: `823 / 950 = 0.8663`
  - leaderboard proxy: `176 / 200 = 0.8800`
  - proxy binary: `76 / 92 = 0.8261`
  - official leaderboard: pending

## Executive summary

v9 は **promote-ineligible** です。

今回の実測で、A-Open-style matching auxiliary を v7 骨格へ戻しても、README が主戦場と定義する BIT frontier は前進しないことが確認されました。validation の `bit_manipulation` は `150 / 169` で `v6` / `v7-1` と同点のまま、proxy binary は `76 / 92` まで落ち、proxy total も `176 / 200` と v20 水準へ戻っています。

さらに悪いことに、v9 は numeral を `133 / 149` まで落とし、mistake rows の多くが boxed `0` へ drift しました。これは `v8` の boxed Roman drift と同系統であり、matching auxiliary が mainline の surface 安定化を置き換えないことを示しています。

結論として、v9 は v10 の本命方針を変えません。むしろ、**matching / token-skill の broad 復帰は v10 mainline に入れず、必要なら後段の diagnostic side branch に下げるべき**という判断を強めます。

## Overlay mix

- v4_public_base: `808`
- v6_binary_donor: `27`
- v6_numeral_surface_donor: `10`
- v7_numeral_surface_synth: `1`
- v9_bit_matching_aux: `543`

Repeated overlay total: `1389`

Unique rows total: `881`

## Matching auxiliary lane

- binary origin IDs: `240`
- all extracted sections: `2160`
- informative sections: `739`
- kept after A-Open downsampling: `543`
- missing reasoning files: `0`

Kept by section:

- Identity: `133`
- AND-NOT: `89`
- AND: `81`
- OR: `78`
- OR-NOT: `68`
- XOR: `40`
- XOR-NOT: `30`
- Constant: `17`
- NOT: `7`

## Bundle footprint

- base examples: `7828`
- overlay examples: `1389`
- total examples: `9217`
- total steps: `289`
- total tokens: `33,305,836`
- max seq len: `7971`
- reused base synthetic examples: `768`
- retokenized overlay examples: `621`

Overlay category counts:

- bit_manipulation: `683`
- matching: `543`
- numeral: `83`
- cipher: `24`
- cryptarithm_deduce: `24`
- unit_conversion: `16`
- gravity: `12`
- equation_numeric_deduce: `4`

## Measured results

### Validation summary

- total: `823 / 950 = 0.8663`
- bit_manipulation: `150 / 169 = 0.8876`
- numeral: `133 / 149 = 0.8926`
- unit_conversion: `171 / 171 = 1.0000`
- gravity: `158 / 159 = 0.9937`
- cipher: `162 / 162 = 1.0000`

Interpretation:

- v9 did **not** improve BIT on validation. `bit_manipulation` stayed at `150 / 169`, tying `v6` and `v7-1` and only recovering the `v8` regression.
- The main validation loss is numeral. Compared with `v7-1`, v9 loses `15` numeral rows, and even versus `v8` it loses `10` numeral rows.
- The numeral failure shape is severe and coherent: the recorded mistakes show repeated boxed `0` outputs for Roman numeral prompts.

### Proxy summary

- overall: `176 / 200 = 0.8800`
- binary: `76 / 92 = 0.8261`
- symbol: `24 / 32 = 0.7500`
- binary `boxed_extraction_success_rate`: `1.0000`
- binary `format_failure_rate`: `0.0109`
- binary `format_ok_content_wrong_rate`: `0.1648`

Interpretation:

- v9 falls back to the v20 proxy level and is clearly below `v4`, `v6`, `v7-1`, and `v8` on proxy binary.
- Format stayed mostly intact, but content quality worsened. `format_ok_content_wrong_rate = 0.1648` is materially worse than `v6 = 0.1209`.
- Measured proxy flips are negative in every comparison that matters:
  - vs `v7-1`: `+1 / -3`, net `-2`
  - vs `v8`: `+2 / -4`, net `-2`
  - vs `v6`: `+0 / -4`, net `-4`
  - vs `v4`: `+0 / -3`, net `-3`

Key regressions versus stronger prior runs include:

- `c30a782a`
- `59c78e51`
- `b9500f41`
- `14a72508`
- `069dbaab`

### Binary failure shape

v9 proxy binary wrong IDs are:

- `c30a782a`
- `a6192d29`
- `01e09228`
- `59c78e51`
- `b9500f41`
- `12fd5b6c`
- `14a72508`
- `1532c0d1`
- `012fb81b`
- `2d790c98`
- `069dbaab`
- `101410e4`
- `12154247`
- `2230fad0`
- `257e7158`
- `31966698`

This is not a new frontier. It is mostly the existing hard core plus new regressions on rows that stronger prior branches had already recovered.

### Strategy implication

v9 changes the confidence level, not the direction, of the next-step decision.

1. `matching` is **not** a v10 mainline ingredient.
2. surface guardrails remain mandatory because auxiliary restoration alone can still trigger numeral boxed-`0` drift.
3. the v10 mainline should continue to use `v4_public_base` as the backbone, `v6` only as a narrow BIT donor, and frontier hard-core / anti-`default 1` lanes as the only new main investment.

## Measurement note

v9 is now a measured score branch for local validation and README-contract leaderboard proxy. Official leaderboard calibration is still pending.

補足として、bundle 本体は約 290MB で通常の GitHub file limit を超えるため local 生成物として保持し、Git 上には再現用 generator と軽量な summary / selection / report を残しています。
