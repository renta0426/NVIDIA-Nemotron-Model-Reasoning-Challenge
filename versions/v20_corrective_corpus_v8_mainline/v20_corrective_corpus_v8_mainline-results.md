# v20_corrective_corpus_v8_mainline

- created_at: 2026-04-22T10:45:58+00:00
- strategy note: versions/v20_to_088_reassessment_2026-04-18.md
- README basis: deterministic boxed-answer evaluation, bit_manipulation as primary score source, tokenization-aware supervision, and symbol exact-transduction weaknesses called out in the A-Open note.
- status: bundle generated and measured; see versions/v20_corrective_corpus_v8_mainline/v20_corrective_corpus_v8_mainline_reassessment_2026-04-23.md for score and raw-output analysis.

## Strategy

- One major run only: BIT-core mainline with targeted symbol exact lanes and minimal easy-family guardrails.
- Allocation target: roughly 75-80% BIT, 15-20% symbol, <=5% guardrail.
- Latest reference run remains v7-1; v8 here is a new data-generation branch, not a score claim.

## Selected Unique Rows

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

## Allocation Check

- bit_unique: 472 (78.93%)
- symbol_unique: 96 (16.05%)
- guardrail_unique: 30 (5.02%)
- total_unique: 598

## Hard Anchors

- binary_hard_hits: 15
- symbol_hard_hits: 8

## Bundle

- path: A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v8_mainline_bundle.jsonl
- base_examples: 7828
- overlay_examples: 1183
- total_examples: 9011
- total_tokens: 28199629
- max_seq_len: 7971

## Canonical Validation

- passed: True
- errors: []

## Measured Evaluation Update

- validation / proxy / official reassessment: versions/v20_corrective_corpus_v8_mainline/v20_corrective_corpus_v8_mainline_reassessment_2026-04-23.md
- latest measured read: validation 834 / 950, proxy 178 / 200, official user-reported 0.83-0.84

---

v8 の結果と、その原因になりうる学習データ差分を切り分けます。まず v8 の score 記録、評価の生データ、そして v8 bundle / selection artifact を読み、直前系統との差分まで落とします。

v8 の実測と raw data を精査し、score 低下の原因を training-data 変更と row-level 出力差分まで切り分けました。Git-visible には v20_corrective_corpus_v8_mainline_reassessment_2026-04-23.md を追加し、v20_corrective_corpus_v8_mainline-results.md も measured 状態に更新しました。



主要所見は 3 つです。

1. v8 は score 的に失敗です。validation は 834 / 950、proxy は 178 / 200、proxy binary は 78 / 92、official はユーザー報告で 0.83-0.84 でした。v7-1 より validation で 5 行落ち、proxy は同点止まり、official も悪化です。整理した記録は v20_corrective_corpus_v8_mainline_reassessment_2026-04-23.md に残しました。

2. 今回の学習データ変更は、v7-1 のような token-safe repair ではなく、teacher architecture の差し替えです。v7-1 は v4_public_base を強く含む donor 混合でしたが、v8 はそれを捨てて 04-08-16-14 base に synthetic overlay を直接重ねる構成へ戻しました。overlay は 846 から 1183 に増えた一方、総 token 数は 32.95M から 28.20M へ 4.75M 減っています。つまり例数は増えたが、監督信号はかなり短文化されています。中身は BIT 472 unique、symbol 96 unique、guardrail 30 unique で、symbol exact lane にかなり予算を振り、surface guardrail は v6 よりかなり薄くなりました。

3. 出力への影響は、symbol 不動、binary 横ばい、easy-family 悪化です。proxy は v7-1 と aggregate で同じ 178 / 200 ですが、中身は binary の 2 勝 2 敗の入れ替えだけでした。069dbaab と 13009e35 は直った一方、26a70ae0 と 6a333ed6 が新たに落ちています。しかも全部 boxed のままの content drift で、format 改善ではありません。symbol はもっと深刻で、v8 が hard anchor として固定投入した hard 8 行が 1 行も動いていません。validation では numeral が 148 / 149 から 143 / 149 に落ち、6 行が Roman numeral ではなく boxed 0 を返す新しい regression になっていました。これは README.md の boxed-first 契約に対してかなり悪い形です。

今回の変更を一言で言うと、v8 は public-safe な v4 系 donor 分布を削って、短い exact synthetic teacher と symbol exact lane に寄せた run でした。しかし README が主戦場とする bit_manipulation は前進せず、symbol 投資は 0 リターンで、代わりに numeral surface に新しい debt を作りました。なので official 0.83-0.84 はかなり整合的です。v7 みたいな bundle bug ではなく、純粋に data policy の読み違いです。
