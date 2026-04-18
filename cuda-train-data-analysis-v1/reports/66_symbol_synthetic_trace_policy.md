# cuda-train-data-analysis-v1 symbol synthetic trace policy

README.md の契約では評価は final boxed answer accuracy だが、repo 内の trace 教師は `verified_trace_ready` とそれ以外を分けて扱う。ここでは `symbol_equation` について、prompt-only verified と synthetic / pseudo trace を明示的に分離する。

- `prompt_verified_trace`: `110`
- `synthetic_trace_hypothesis`: `1368`
- `no_trace_teacher`: `77`
- rows requiring gold-based candidate selection: `1254`

## Policy summary

| symbol_trace_teacher_tier | symbol_trace_policy | symbol_trace_gold_role | symbol_trace_contract | symbol_problem_category | rows |
| --- | --- | --- | --- | --- | --- |
| synthetic_trace_hypothesis | answer_conditioned_latent_hypothesis | candidate_selection_required | answer_conditioned | cryptarithm_deduce | 353 |
| synthetic_trace_hypothesis | answer_conditioned_operator_semantics | candidate_selection_required | answer_conditioned | cryptarithm_deduce | 306 |
| synthetic_trace_hypothesis | answer_conditioned_family_choice | candidate_selection_required | answer_conditioned | equation_numeric_deduce | 275 |
| synthetic_trace_hypothesis | answer_conditioned_operator_semantics | candidate_selection_required | answer_conditioned | cryptarithm_guess | 164 |
| synthetic_trace_hypothesis | unique_rule_below_verified_support | final_check_only | non_prompt_evidence_needed | equation_numeric_deduce | 114 |
| prompt_verified_trace | strict_prompt_safe | final_check_only | prompt_only | equation_numeric_deduce | 110 |
| synthetic_trace_hypothesis | answer_conditioned_operator_semantics | candidate_selection_required | answer_conditioned | equation_numeric_guess | 108 |
| synthetic_trace_hypothesis | answer_conditioned_rule_choice | candidate_selection_required | answer_conditioned | equation_numeric_deduce | 47 |
| no_trace_teacher | not_answer_only | not_applicable | none | equation_numeric_deduce | 35 |
| no_trace_teacher | prompt_conflict_requires_external_semantics | insufficient_even_with_gold | none | equation_numeric_guess | 27 |
| no_trace_teacher | prompt_conflict_requires_external_semantics | insufficient_even_with_gold | none | equation_numeric_deduce | 15 |
| synthetic_trace_hypothesis | answer_conditioned_rule_choice | candidate_selection_required | answer_conditioned | equation_numeric_guess | 1 |

## Synthetic trace candidates

| id | template_subtype | symbol_problem_category | symbol_trace_policy | symbol_trace_gold_role | symbol_strict_status | answer | query_raw |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fe393711 | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 1291 | 46}03 |
| 37f04e3e | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 0092 | 85}05 |
| 6402d0ee | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | \93 | 92\86 |
| f299569f | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 7992 | 18\73 |
| 17c98340 | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 731 | 78}05 |
| 3687b4bb | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 4602 | 53`95 |
| 3acfa7a4 | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 6651 | 45%92 |
| 5e67b1a1 | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 63 | 32{31 |
| 5f5a73ff | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 0897 | 59"48 |
| 6cd73bdd | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 6895 | 37{28 |
| 76b79a0c | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 2192 | 23@19 |
| 791056ce | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 4922 | 58{72 |
| 936b3ae5 | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 14> | 95>81 |
| b3f9a15c | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 1773 | 85[56 |
| d78ce112 | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 7042 | 38\92 |
| 10ff9431 | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 0271 | 02"68 |
| 1580f498 | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 1554 | 05*19 |
| 1861c08f | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 3001 | 71:95 |
| 1cb4d524 | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 6314 | 74!88 |
| 207ab66f | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 2815 | 17{37 |
| 2d3e809c | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 9264 | 25*98 |
| 320d8d2b | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 3913 | 65>75 |
| 333d93ec | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 7 | 44-73 |
| 379d18b7 | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 2101 | 22!64 |
| 40c53743 | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 7963 | 24*88 |
| 44398869 | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 5913 | 54^17 |
| 4b70414e | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 1913 | 48#83 |
| 4d39d098 | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 7434 | 96*36 |
| 4f660f4b | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 6554 | 76[86 |
| 5aeb4ba5 | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 3985 | 17>38 |
| 5d44a0b2 | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 8035 | 78*16 |
| 61766c6f | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 2572 | 46[34 |
| 67f1bc8a | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 1321 | 77-61 |
| 68b9b9a8 | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 4734 | 45*18 |
| 6bd59a1f | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 7241 | 82$15 |
| 6c9e4485 | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 6253 | 28%34 |
| 6da9eb9a | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 2664 | 36&47 |
| 744a2570 | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 5 | 87"38 |
| 836d6c4a | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 5643 | 99>53 |
| 837af955 | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 0814 | 67*55 |
| 852d16cb | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | -7 | 09-79 |
| 88fe5a52 | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 8065 | 97*17 |
| 912c6ea5 | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 071 | 47}69 |
| 93d1c7eb | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 0154 | 28`55 |
| 98bb54f7 | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 5846 | 96*49 |
| 9ae3b78e | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 5214 | 57@55 |
| 9d7af57b | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 89 | 33`56 |
| 9f2fae58 | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 7272 | 88$13 |
| b3ae7f39 | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 801 | 08}82 |
| b643d81f | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 9 | 97-07 |
| bd4c584a | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 0491 | 02$79 |
| c2199ff2 | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 1807 | 37(79 |
| ce507d39 | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 2861 | 85%92 |
| d4483d51 | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 3752 | 33*87 |
| d9bedb64 | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | (1 | 04(14 |
| dd626fd0 | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 1671 | 08*22 |
| f66f0fe0 | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 7793 | 14{79 |
| f6db706e | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 4 | 94*54 |
| 01cd504a | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 6644 | 85/77 |
| 04171e29 | numeric_2x2 | equation_numeric_deduce | answer_conditioned_family_choice | candidate_selection_required | answer_only_keep:needs_cross_row_evidence | 32 | 97-65 |

## Policy contract

1. `prompt_verified_trace`: prompt-only で一意かつ trace-safe。既存 `verified_trace_ready` と同義。
2. `synthetic_trace_hypothesis`: 学習用の一貫した導出は作れるが、prompt semantics を証明したものではない。gold を候補選択に使う場合は必ずこの tier に留める。
3. `no_trace_teacher`: current prompt / gold / exact DSL の組み合わせだけでは、trace を書いても benchmark row の semantics を正当化できない。

Interpretation: これで `answer_only_keep` の中でも、README 準拠の accuracy 目的で保持している supervision と、strict verified としては使えない synthetic trace をコード上で切り分けられる。今後の ablation では `prompt_verified_trace` と `synthetic_trace_hypothesis` を別々に投入できる。

## SFT use guidance

- **使えるが、verified trace と同列には扱わない。**
- `prompt_verified_trace` はそのまま trace SFT の主力に使ってよい。
- `synthetic_trace_hypothesis` は補助 trace / pseudo-trace として使える。
  - `unique_rule_below_verified_support` (`114`) は比較的安全で、gold は最終照合に近い。
  - それ以外の `1254` 行は `gold` による候補選択が必要で、**answer-conditioned synthetic trace** として扱うべき。
- `no_trace_teacher` は trace SFT に使わない。

Practical recommendation:

1. `prompt_verified_trace` を core trace teacher にする。
2. `synthetic_trace_hypothesis` は別 tag / 別 sampling weight で混ぜる。
3. 特に `candidate_selection_required` 行は low-ratio で使い、`verified` と混ぜて同一品質と見なさない。
