# v20 corrective corpus v9 mainline results

## Status

- Created: 2026-04-23 UTC
- Generator: versions/v20_corrective_corpus_v9_mainline/reproduce_v20_corrective_corpus_v9_mainline.py
- Strategy note: versions/v20_corrective_corpus_v9_mainline/v20_corrective_corpus_v9_mainline_strategy_2026-04-23.md
- Bundle: A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v9_mainline_bundle.jsonl
- Overlay report: versions/v20_corrective_corpus_v9_mainline/outputs/v9_mainline_default/reports/corrective_overlay_report.md
- Overlay summary: versions/v20_corrective_corpus_v9_mainline/outputs/v9_mainline_default/artifacts/corrective_overlay_summary.json
- Git-tracked generated artifacts: versions/v20_corrective_corpus_v9_mainline/outputs/v9_mainline_default/artifacts/corrective_selection.csv, versions/v20_corrective_corpus_v9_mainline/outputs/v9_mainline_default/artifacts/corrective_overlay_summary.json, versions/v20_corrective_corpus_v9_mainline/outputs/v9_mainline_default/reports/corrective_overlay_report.md
- Current state: bundle generated, score not measured yet
- Training / validation / leaderboard score:
  - validation: pending
  - leaderboard proxy: pending
  - official leaderboard: pending

## Executive summary

v9 は、v8 の broad BIT exact expansion をやめ、token-safe な v7 donor 骨格に A-Open-style matching auxiliary を追加した corrective branch です。

この branch で新たに増やしたのは final-answer exact teacher ではなく、bit reasoning の局所技能を教える `matching` だけです。狙いは、strict audit 後に曖昧性が残る binary tail に新しい boxed answer を押し込まず、README の本筋である token-level 補助課題をローカル base snapshot 上に復元することです。

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

## Measurement note

現時点では v9 は **データ生成まで完了** であり、学習・validation・proxy・official の計測はまだです。ここにスコアを追記するまでは、v9 は design branch であって score branch ではありません。

補足として、bundle 本体は約 290MB で通常の GitHub file limit を超えるため local 生成物として保持し、Git 上には再現用 generator と軽量な summary / selection / report を残しています。
