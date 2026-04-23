# v20 corrective corpus v9 mainline strategy

## Status

- Created: 2026-04-23 UTC
- Generator: versions/v20_corrective_corpus_v9_mainline/reproduce_v20_corrective_corpus_v9_mainline.py
- Strategy basis:
  - A-Open-ProgressPrizePublication/README.md
  - cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md
  - data/symbol_rule_analysis_2026-04-20/analysis_report.md
  - versions/v20_corrective_corpus_v8_mainline/v20_corrective_corpus_v8_mainline_reassessment_2026-04-23.md
- Parent overlay backbone: versions/v20_corrective_corpus_v7_mainline/outputs/v7_mainline_default/artifacts/corrective_overlay_repeated.jsonl

## Executive summary

v9 は、v8 の BIT exact expansion が frontier を動かさなかった事実を受けて、主戦略を answer-level expansion から bit-local auxiliary restoration へ切り替えた corrective branch です。

README は bit_manipulation を最大の差分源としつつ、token-level weakness を補助課題へ分解していました。ところがこの workspace で実際に使っている 04-08-16-14 base snapshot には `matching` が入っていません。v8 はその欠落を埋めず、competition rows に exact synthetic teacher を増やしただけでした。

したがって v9 は次の 3 点だけをやります。

1. v7 の token-safe donor overlay をそのまま骨格として残す
2. broad symbol exact lane と broad BIT exact laneの追加をやめる
3. v7 が保持する binary origin 240 IDs から、A-Open 方式そのままの matching auxiliary 543 行を再導入する

## Why v8 was not enough

v8 の実測は validation `834 / 950`, proxy `178 / 200`, proxy binary `78 / 92`, official `0.83-0.84` でした。これは `v7-1` と同じ proxy binary であり、v4 / v6 の binary proxy を超えていません。

同時に `cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md` では、strict audit 後の binary が `1229 verified / 271 answer_only / 87 manual / 15 exclude` に整理されています。ここで残っている `87 manual` は曖昧尾部であり、exact trace をさらに増やせば安全に進む状態ではありません。

つまり v8 の失敗は「BIT 量が足りなかった」のではなく、**曖昧尾部に対して answer-level exact teacher を増やす方向が mainline として不適切だった**ことを示しています。

## Why matching is the chosen lever

`A-Open-ProgressPrizePublication/nemotron/augmenters/matching.py` は、bit reasoning の `Matching output / Left / Right` をそのまま補助課題へ切り出しています。これは新しい boxed answer を仮定するのではなく、bit reasoning の局所技能だけを反復学習させる設計です。

今回 v7 overlay の binary origin 240 IDs から再抽出した結果は次の通りです。

- raw sections: `2160`
- informative sections: `739`
- kept after original A-Open downsampling: `543`

kept by section:

- Identity: `133`
- AND-NOT: `89`
- AND: `81`
- OR: `78`
- OR-NOT: `68`
- XOR: `40`
- XOR-NOT: `30`
- Constant: `17`
- NOT: `7`

## Concrete v9 composition

Source mix:

- v4_public_base: `808`
- v6_binary_donor: `27`
- v6_numeral_surface_donor: `10`
- v7_numeral_surface_synth: `1`
- v9_bit_matching_aux: `543`

Repeated overlay total: `1389`

Overlay category counts:

- bit_manipulation: `683`
- matching: `543`
- numeral: `83`
- cipher: `24`
- cryptarithm_deduce: `24`
- unit_conversion: `16`
- gravity: `12`
- equation_numeric_deduce: `4`

Bundle footprint:

- base examples: `7828`
- overlay examples: `1389`
- total examples: `9217`
- total tokens: `33,305,836`
- total steps: `289`
- reused base synthetic examples: `768`
- retokenized overlay examples: `621`

## Interpretation

v9 の狙いは、v8 のような broad exact expansion ではありません。狙いは

- public-safe v4/v7 donor balance を保持したまま、
- local base snapshot に欠けている A-Open の bit-local curriculum を補い、
- 曖昧な binary tail へ新しい final answer teacher を追加しないこと

です。

この branch はまだ未計測であり、score claim はありません。ここで固定したのは「何を増やすか」ではなく、**何を増やさないか**まで含めた mainline policy です。
