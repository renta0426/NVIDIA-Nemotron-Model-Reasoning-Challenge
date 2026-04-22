# v20 corrective corpus v7-1 bundle and raw-output audit

## Status

- Created: 2026-04-22 UTC
- Naming note: historical `v8` references in this workspace correspond to the corrected `v7` rerun, now normalized as `v7-1`
- README basis:
  - `README.md`
  - `A-Open-ProgressPrizePublication/README.md`
- Evidence sources:
  - `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v7_mainline_bundle.jsonl`
  - `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v7_mainline_tokenreuse_bundle.jsonl`
  - `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v4_mainline_bundle.jsonl`
  - `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v6_mainline_bundle.jsonl`
  - `A-Open-ProgressPrizePublication/result/results-v7/results.csv`
  - `A-Open-ProgressPrizePublication/result/results-v7/validation.csv`
  - `A-Open-ProgressPrizePublication/result/results-v7-1/results.csv`
  - `A-Open-ProgressPrizePublication/result/results-v7-1/validation.csv`
  - `A-Open-ProgressPrizePublication/result/leaderboard_proxy_eval-v7/reports/leaderboard_proxy_eval_summary.md`
  - `A-Open-ProgressPrizePublication/result/leaderboard_proxy_eval-v7/artifacts/leaderboard_proxy_eval_row_level.csv`
  - `A-Open-ProgressPrizePublication/result/leaderboard_proxy_eval-v7-1/reports/leaderboard_proxy_eval_summary.md`
  - `A-Open-ProgressPrizePublication/result/leaderboard_proxy_eval-v7-1/artifacts/leaderboard_proxy_eval_row_level.csv`
  - `versions/v20_corrective_corpus_v7_mainline/v20_corrective_corpus_v7_mainline-results.md`
  - `versions/v20_corrective_corpus_v7_mainline/v20_corrective_corpus_v7_mainline-tokenstream-audit-2026-04-21.md`
  - `versions/v20_corrective_corpus_v7_mainline/v20_corrective_corpus_v7_mainline-bundle-to-bundle-audit-2026-04-21.md`

## Executive summary

`v7-1` の学習データ変更は、まず **text corpus の入れ替えではありません**。

- `v7` と `v7-1` は overlay mix 自体は同じです
  - `v4_public_base = 808`
  - `v6_binary_donor = 27`
  - `v6_numeral_surface_donor = 10`
  - `v7_numeral_surface_synth = 1`
- prompt / completion text も実質同一です
- 実際に変わったのは **token / mask の構成**で、差分は `298` 行、`298` problem IDs、しかも全件 `v4_public_base` に閉じています
- donor rows 自体の tokenization は `v7` と `v7-1` で同じです

この変更は README が繰り返し強調している

- deterministic CoT
- tokenization awareness
- work with tokens instead of text

の 3 点に完全に一致しています。`v7-1` は「新しい teacher text を足した run」ではなく、**壊していた teacher token stream を戻した run** と理解するのが正確です。

raw output 側では、変更の効果は狙い通りに出ています。

- validation: `784 -> 839` で `+55`
- proxy: `154 -> 178` で `+24`
- 改善の大半は binary で、failure mode が `no_box` / 桁崩れ / 非 binary から `boxed_binary` へ戻っています

したがって、`v7-1` は public winner ではないものの、**v7 の大きなバグが token-safe 継承の破壊だった**こと自体は強く裏づけられました。

## README-grounded expectation

`README.md` の評価契約は deterministic decoding と boxed-first extraction です。`A-Open-ProgressPrizePublication/README.md` はさらに、勝ち筋を

- `bit_manipulation` が主戦場
- token-aware な deterministic trace を保つこと
- text ではなく tokens を基準に扱うこと

と整理しています。

この観点から見ると、`v7 -> v7-1` の修正で最初に確認すべきことは正答率そのものではなく、**binary raw output が malformed / no-box から boxed 8-bit answer に戻ったか** でした。

## Bundle delta: what actually changed

## Same overlay definition

`v7` と `v7-1` の bundle 構成は同じです。

- total examples: `8674`
- base examples: `7828`
- overlay examples: `846`
- overlay mix:
  - `v4_public_base = 808`
  - `v6_binary_donor = 27`
  - `v6_numeral_surface_donor = 10`
  - `v7_numeral_surface_synth = 1`

つまり `v7-1` は donor set の入れ替えでも、overlay size の変更でもありません。

## Same text, different token stream

bundle 比較では、prompt / completion text の差分は検出されませんでした。差分は token / mask のみです。

- changed token rows: `298`
- changed problem IDs: `298`
- changed source mix: `v4_public_base` のみ
- changed categories:
  - `bit_manipulation = 239`
  - `numeral = 20`
  - `cryptarithm_deduce = 12`
  - `gravity = 11`
  - `cipher = 8`
  - `unit_conversion = 6`
  - `equation_numeric_deduce = 2`

この `298` は tokenstream audit に記録されている `reused_base_synthetic_problem_count = 298` と整合しています。つまり `v7-1` の修正本体は、`v4_public_base` lane のうち base snapshot の synthetic token stream を再利用できる問題を **text 再 token 化から source-aware token reuse に戻した**ことです。

## What did not change

重要なのは donor rows が変わっていないことです。

- `v6_binary_donor` rows は `v7` と `v7-1` で token digest 変化なし
- `v6_numeral_surface_donor` rows も token digest 変化なし
- `v7_numeral_surface_synth` も同じ

つまり `v7-1` の improvement は「donor row を作り直したから」ではありません。**崩れていた `v4` 継承 lane を戻した結果、donor lane が意図通り機能する地盤が復旧した**というのが正しい読みです。

## Raw output movement

## Validation

- total: `784 / 950 -> 839 / 950`
- transitions:
  - `wrong -> correct = 57`
  - `correct -> wrong = 2`
- improved by category:
  - `bit_manipulation = 56`
  - `cipher = 1`
- regressed by category:
  - `bit_manipulation = 1`
  - `numeral = 1`

output 形状の変化は次の通りです。

- `no_box -> boxed_binary = 24`
- `boxed_numeric -> boxed_binary = 12`
- `boxed_binary -> boxed_binary = 20`
- `boxed_other -> boxed_other = 1`
- `boxed_binary -> boxed_binary` のまま内容だけ修正された regressed row `= 1`
- `boxed_roman -> no_box` の numeral regression `= 1`

ここで重要なのは、`v7` の失点が content-only ではなく **format / termination の崩れ** を多く含んでいたこと、そして `v7-1` でそれが boxed 8-bit へかなり戻ったことです。

## Proxy

- total: `154 / 200 -> 178 / 200`
- transitions:
  - `wrong -> correct = 24`
  - `correct -> wrong = 0`
- changed family:
  - `binary = 24`

proxy の raw output 形状変化はさらに分かりやすいです。

- `no_box -> boxed_binary = 9`
- `boxed_numeric -> boxed_binary = 4`
- `boxed_other -> boxed_binary = 3`
- `boxed_binary -> boxed_binary = 8`

README の「bit manipulation が主戦場」「token-aware deterministic trace が重要」という主張に対して、ここはかなり強い整合です。`v7-1` は frontier の全部を解いていない一方で、**v7 の malformed binary collapse はほぼ確実に修正できています**。

## Targeted donor / numeral rows

binary donor IDs に対する変化は次の通りです。

- validation で改善した donor IDs:
  - `0520a6ec`
  - `0dd5caf4`
  - `17fd9612`
- proxy で改善した donor IDs:
  - `0520a6ec`
  - `8e5d6fe6`
  - `b9500f41`
  - `fa67da07`

一方で numeral surface donor は broad に伸びたわけではありません。

- validation numeral surface IDs: `10` は維持、`1` は regression
- regressed numeral row: `188fe6d4`

つまり `v7-1` が最もはっきり直したのは numeral ではなく、**binary trace の boxed termination と 8-bit formatting** です。

## Raw tail examples

`0520a6ec`

- `v7`: `\boxed{01100001}`
- `v7-1`: `\boxed{10100001}`
- 見た目はどちらも boxed binary ですが、終盤の operator alignment が変わり、content が正答へ寄りました

`17fd9612`

- `v7`: tail が途中で崩れ、最終的に裸の `2` で終了
- `v7-1`: `The answer in \boxed is | \boxed{00011010}` で終端
- これは `v7` の malformed collapse が `v7-1` で straight に修復された例です

`8e5d6fe6`

- `v7`: no-box の `101` で終了
- `v7-1`: `\boxed{10000111}`
- proxy donor row でも boxed binary への復帰が確認できます

`b9500f41`

- `v7`: `\boxed{11111000}`
- `v7-1`: `\boxed{11110000}`
- こちらは format は両方正しいが、終盤の copy lane が変わって content が修正された例です

`188fe6d4`

- `v7`: `\boxed{IX}`
- `v7-1`: `I will now return the answer in \box` で壊れ、最終出力は裸の `IX`
- `v7-1` にも easy-family surface regression が残ることを示す counterexample です

## Directness of the causal link

改善は changed-token IDs だけに閉じていません。

- validation improved rows のうち changed-token IDs に直接含まれるのは `23 / 57`
- proxy improved rows のうち changed-token IDs に直接含まれるのは `13 / 24`

これは大事です。`v7-1` の効果は単なる row replay ではなく、**teacher manifold の安定化によって generation 分布全体を戻した**と読む方が自然です。

つまり今回の修正は

- 局所的な memorization の修復

ではなく

- overlay phase 全体で token-safe な学習信号を回復したことによる分布補正

として観測されています。

## Interpretation

`v7` の大バグは、狭い donor pack を足したこと自体ではありませんでした。

壊していたのは

- `v4_public_base` の token-safe inheritance
- その結果としての deterministic binary termination

です。

`v7-1` ではそこが回復し、raw output は狙い通り

- no-box / broken tail / numeric garbage
- から boxed 8-bit answer

へ戻りました。

この意味で `v7-1` は **README の token-first 仮説の確認 run** としては有効です。

ただし score judgment は別です。`v7-1` は malformed collapse を直しただけで、`v4` / `v6` を超える binary frontier までは押し上げていません。したがって本命 branch としては promote 不可、しかし **v7 failure の根因切り分けとしては成功** と記録するのが正確です。
