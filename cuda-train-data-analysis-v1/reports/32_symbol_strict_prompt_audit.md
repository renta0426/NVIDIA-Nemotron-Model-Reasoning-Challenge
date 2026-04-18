# cuda-train-data-analysis-v1 symbol strict prompt audit

README.md 基準ではコンペ評価は final boxed answer accuracy だが、この report は `verified_trace_ready` を prompt-only trace teacher として再監査した補助レイヤー。

- verified_prompt rows: `110`
- unseen_query_operator rows: `108`
- prompt_ambiguous rows: `56`
- prompt_exact_conflict rows: `55`
- support_below_verified_threshold rows: `114`

## Status summary

| selection_tier | symbol_strict_status | symbol_problem_category | rows |
| --- | --- | --- | --- |
| answer_only_keep | answer_only_keep:latent_rule_nonunique | cryptarithm_deduce | 353 |
| answer_only_keep | answer_only_keep:unseen_query_operator | cryptarithm_deduce | 306 |
| answer_only_keep | answer_only_keep:needs_cross_row_evidence | equation_numeric_deduce | 275 |
| answer_only_keep | answer_only_keep:unseen_query_operator | cryptarithm_guess | 164 |
| answer_only_keep | answer_only_keep:support_below_verified_threshold | equation_numeric_deduce | 114 |
| verified_trace_ready | verified_trace_ready:verified_prompt | equation_numeric_deduce | 110 |
| answer_only_keep | answer_only_keep:unseen_query_operator | equation_numeric_guess | 108 |
| answer_only_keep | answer_only_keep:prompt_ambiguous | equation_numeric_deduce | 47 |
| answer_only_keep | answer_only_keep:prompt_exact_conflict | equation_numeric_guess | 27 |
| answer_only_keep | answer_only_keep:prompt_exact_conflict | equation_numeric_deduce | 15 |
| manual_audit_priority | manual_audit_priority:needs_cross_row_evidence | equation_numeric_deduce | 14 |
| exclude_suspect | exclude_suspect:prompt_exact_conflict | equation_numeric_deduce | 9 |
| manual_audit_priority | manual_audit_priority:prompt_ambiguous | equation_numeric_deduce | 8 |
| manual_audit_priority | manual_audit_priority:prompt_exact_conflict | equation_numeric_deduce | 4 |
| answer_only_keep | answer_only_keep:prompt_ambiguous | equation_numeric_guess | 1 |

## Gap summary

| template_subtype | symbol_problem_category | selection_tier | symbol_strict_audit_scope | symbol_strict_status | symbol_strict_gap_reason | rows |
| --- | --- | --- | --- | --- | --- | --- |
| glyph_len5 | cryptarithm_deduce | answer_only_keep | glyph_structure | answer_only_keep:unseen_query_operator | glyph_query_operator_unseen_and_no_trace_safe_rule | 306 |
| glyph_len5 | cryptarithm_deduce | answer_only_keep | glyph_structure | answer_only_keep:latent_rule_nonunique | grouped_model_keeps_answer_but_not_unique_trace | 275 |
| numeric_2x2 | equation_numeric_deduce | answer_only_keep | same_operator_only | answer_only_keep:needs_cross_row_evidence | same_operator_examples_exist_but_no_exact_row_local_rule | 275 |
| glyph_len5 | cryptarithm_guess | answer_only_keep | glyph_structure | answer_only_keep:unseen_query_operator | glyph_query_operator_unseen_and_no_trace_safe_rule | 164 |
| numeric_2x2 | equation_numeric_deduce | answer_only_keep | same_operator_only | answer_only_keep:support_below_verified_threshold | same_operator_rule_is_unique_but_support_below_verified_threshold | 114 |
| numeric_2x2 | equation_numeric_deduce | verified_trace_ready | verified_selection | verified_trace_ready:verified_prompt |  | 110 |
| numeric_2x2 | equation_numeric_guess | answer_only_keep | all_examples_global | answer_only_keep:unseen_query_operator | query_operator_unseen_no_exact_prompt_rule | 108 |
| glyph_len5 | cryptarithm_deduce | answer_only_keep | glyph_structure | answer_only_keep:latent_rule_nonunique | no_examples_only_glyph_multiset_mapping | 76 |
| numeric_2x2 | equation_numeric_deduce | answer_only_keep | same_operator_only | answer_only_keep:prompt_ambiguous | multiple_same_operator_rules_survive | 47 |
| numeric_2x2 | equation_numeric_guess | answer_only_keep | all_examples_global | answer_only_keep:prompt_exact_conflict | all_examples_exact_rule_disagrees_with_gold | 27 |
| numeric_2x2 | equation_numeric_deduce | answer_only_keep | same_operator_only | answer_only_keep:prompt_exact_conflict | same_operator_exact_rule_disagrees_with_gold | 15 |
| numeric_2x2 | equation_numeric_deduce | manual_audit_priority | same_operator_only | manual_audit_priority:needs_cross_row_evidence | same_operator_examples_exist_but_no_exact_row_local_rule | 14 |
| numeric_2x2 | equation_numeric_deduce | exclude_suspect | same_operator_only | exclude_suspect:prompt_exact_conflict | same_operator_exact_rule_disagrees_with_gold | 9 |
| numeric_2x2 | equation_numeric_deduce | manual_audit_priority | same_operator_only | manual_audit_priority:prompt_ambiguous | multiple_same_operator_rules_survive | 8 |
| numeric_2x2 | equation_numeric_deduce | manual_audit_priority | same_operator_only | manual_audit_priority:prompt_exact_conflict | same_operator_exact_rule_disagrees_with_gold | 4 |
| glyph_len5 | cryptarithm_deduce | answer_only_keep | glyph_structure | answer_only_keep:latent_rule_nonunique | glyph_output_order_not_acyclic | 1 |
| glyph_len5 | cryptarithm_deduce | answer_only_keep | glyph_structure | answer_only_keep:latent_rule_nonunique | glyph_prompt_structure_not_uniquely_identified | 1 |
| numeric_2x2 | equation_numeric_guess | answer_only_keep | all_examples_global | answer_only_keep:prompt_ambiguous | multiple_global_exact_rules_survive | 1 |

## Representative unresolved rows

| id | template_subtype | symbol_problem_category | selection_tier | symbol_same_operator_example_count | symbol_strict_status | symbol_strict_gap_reason | answer | query_raw |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 065abaf6 | glyph_len5 | cryptarithm_deduce | answer_only_keep | 0 | answer_only_keep:latent_rule_nonunique | grouped_model_keeps_answer_but_not_unique_trace | &/:\ | :\+&/ |
| 3f67321d | glyph_len5 | cryptarithm_deduce | answer_only_keep | 0 | answer_only_keep:latent_rule_nonunique | grouped_model_keeps_answer_but_not_unique_trace | }"[} | ^`/:[ |
| 5a3eaf6f | glyph_len5 | cryptarithm_deduce | answer_only_keep | 0 | answer_only_keep:latent_rule_nonunique | grouped_model_keeps_answer_but_not_unique_trace | \{}" | (?<\" |
| 9d20c8a7 | glyph_len5 | cryptarithm_deduce | answer_only_keep | 0 | answer_only_keep:latent_rule_nonunique | grouped_model_keeps_answer_but_not_unique_trace | ]]]} | [}\!) |
| a85864a9 | glyph_len5 | cryptarithm_deduce | answer_only_keep | 0 | answer_only_keep:latent_rule_nonunique | grouped_model_keeps_answer_but_not_unique_trace | (\}: | (\*}: |
| b13d511a | glyph_len5 | cryptarithm_deduce | answer_only_keep | 0 | answer_only_keep:latent_rule_nonunique | grouped_model_keeps_answer_but_not_unique_trace | \&[[ | \&+[[ |
| be7101dc | glyph_len5 | cryptarithm_deduce | answer_only_keep | 0 | answer_only_keep:latent_rule_nonunique | grouped_model_keeps_answer_but_not_unique_trace | \:%# | %/+^# |
| dc240ebd | glyph_len5 | cryptarithm_deduce | answer_only_keep | 0 | answer_only_keep:latent_rule_nonunique | grouped_model_keeps_answer_but_not_unique_trace | `}:} | >\|-}\| |
| ec2099f5 | glyph_len5 | cryptarithm_deduce | answer_only_keep | 0 | answer_only_keep:latent_rule_nonunique | grouped_model_keeps_answer_but_not_unique_trace | :]'\ | }[*][ |
| 0a3ee7c7 | glyph_len5 | cryptarithm_deduce | answer_only_keep | 0 | answer_only_keep:latent_rule_nonunique | grouped_model_keeps_answer_but_not_unique_trace | \@)] | }\*%] |
| 2fc5ef5b | glyph_len5 | cryptarithm_deduce | answer_only_keep | 0 | answer_only_keep:latent_rule_nonunique | grouped_model_keeps_answer_but_not_unique_trace | /&\% | &/*:' |
| 31028506 | glyph_len5 | cryptarithm_deduce | answer_only_keep | 0 | answer_only_keep:latent_rule_nonunique | grouped_model_keeps_answer_but_not_unique_trace | !\ | ?)+`` |
| 36557a2e | glyph_len5 | cryptarithm_deduce | answer_only_keep | 0 | answer_only_keep:latent_rule_nonunique | grouped_model_keeps_answer_but_not_unique_trace | !{}? | ]%*)? |
| 5186f2d7 | glyph_len5 | cryptarithm_deduce | answer_only_keep | 0 | answer_only_keep:latent_rule_nonunique | grouped_model_keeps_answer_but_not_unique_trace | \?!$ | }>)\? |
| 52395e9a | glyph_len5 | cryptarithm_deduce | answer_only_keep | 0 | answer_only_keep:latent_rule_nonunique | grouped_model_keeps_answer_but_not_unique_trace | #!%\ | '#\|</ |
| 5f9f0ed7 | glyph_len5 | cryptarithm_deduce | answer_only_keep | 0 | answer_only_keep:latent_rule_nonunique | grouped_model_keeps_answer_but_not_unique_trace | }/!} | \|!*@[ |
| 811f5f56 | glyph_len5 | cryptarithm_deduce | answer_only_keep | 0 | answer_only_keep:latent_rule_nonunique | grouped_model_keeps_answer_but_not_unique_trace | \^^@ | (!:!@ |
| 85dc976c | glyph_len5 | cryptarithm_deduce | answer_only_keep | 0 | answer_only_keep:latent_rule_nonunique | grouped_model_keeps_answer_but_not_unique_trace | }: | \|\+\} |
| 97d6db7a | glyph_len5 | cryptarithm_deduce | answer_only_keep | 0 | answer_only_keep:latent_rule_nonunique | grouped_model_keeps_answer_but_not_unique_trace | \[%^ | \[*%^ |
| 982c0b42 | glyph_len5 | cryptarithm_deduce | answer_only_keep | 0 | answer_only_keep:latent_rule_nonunique | grouped_model_keeps_answer_but_not_unique_trace | ^}\|% | ^&*"& |
| a08fbb68 | glyph_len5 | cryptarithm_deduce | answer_only_keep | 0 | answer_only_keep:latent_rule_nonunique | grouped_model_keeps_answer_but_not_unique_trace | \$'< | \$+'< |
| af018681 | glyph_len5 | cryptarithm_deduce | answer_only_keep | 0 | answer_only_keep:latent_rule_nonunique | grouped_model_keeps_answer_but_not_unique_trace | \${" | \$!{" |
| d350828e | glyph_len5 | cryptarithm_deduce | answer_only_keep | 0 | answer_only_keep:latent_rule_nonunique | grouped_model_keeps_answer_but_not_unique_trace | }!\|\| | /{:"\| |
| d9575f79 | glyph_len5 | cryptarithm_deduce | answer_only_keep | 0 | answer_only_keep:latent_rule_nonunique | grouped_model_keeps_answer_but_not_unique_trace | \|`/} | \|`{/} |
| dc0f5e5e | glyph_len5 | cryptarithm_deduce | answer_only_keep | 0 | answer_only_keep:latent_rule_nonunique | grouped_model_keeps_answer_but_not_unique_trace | %%}# | %%+}# |
| e3bf0c2c | glyph_len5 | cryptarithm_deduce | answer_only_keep | 0 | answer_only_keep:latent_rule_nonunique | grouped_model_keeps_answer_but_not_unique_trace | "` | @`}'' |
| eb354353 | glyph_len5 | cryptarithm_deduce | answer_only_keep | 0 | answer_only_keep:latent_rule_nonunique | grouped_model_keeps_answer_but_not_unique_trace | \%<% | %%}\|\| |
| efa7edc3 | glyph_len5 | cryptarithm_deduce | answer_only_keep | 0 | answer_only_keep:latent_rule_nonunique | grouped_model_keeps_answer_but_not_unique_trace | //:} | []\|/) |
| f9a33aa1 | glyph_len5 | cryptarithm_deduce | answer_only_keep | 0 | answer_only_keep:latent_rule_nonunique | grouped_model_keeps_answer_but_not_unique_trace | /((` | @(\$/ |
| 16cf827a | glyph_len5 | cryptarithm_deduce | answer_only_keep | 0 | answer_only_keep:latent_rule_nonunique | grouped_model_keeps_answer_but_not_unique_trace | "[`` | [\|-/` |
| 24750c4a | glyph_len5 | cryptarithm_deduce | answer_only_keep | 0 | answer_only_keep:latent_rule_nonunique | grouped_model_keeps_answer_but_not_unique_trace | ?)/{ | \|/*\|\| |
| 3d2cb38a | glyph_len5 | cryptarithm_deduce | answer_only_keep | 0 | answer_only_keep:latent_rule_nonunique | no_examples_only_glyph_multiset_mapping | }{ | <}+#) |
| 3d40a271 | glyph_len5 | cryptarithm_deduce | answer_only_keep | 0 | answer_only_keep:latent_rule_nonunique | grouped_model_keeps_answer_but_not_unique_trace | :/>{ | /:*[{ |
| 41a8a9f0 | glyph_len5 | cryptarithm_deduce | answer_only_keep | 0 | answer_only_keep:latent_rule_nonunique | grouped_model_keeps_answer_but_not_unique_trace | \|"`> | #>*`" |
| 48ae115d | glyph_len5 | cryptarithm_deduce | answer_only_keep | 0 | answer_only_keep:latent_rule_nonunique | grouped_model_keeps_answer_but_not_unique_trace | \[@` | ]>']\| |
| 4dcd1b40 | glyph_len5 | cryptarithm_deduce | answer_only_keep | 0 | answer_only_keep:latent_rule_nonunique | grouped_model_keeps_answer_but_not_unique_trace | `:{ | }:`]" |
| 5968bf6c | glyph_len5 | cryptarithm_deduce | answer_only_keep | 0 | answer_only_keep:latent_rule_nonunique | grouped_model_keeps_answer_but_not_unique_trace | ("/^ | (!*:" |
| 5a35e698 | glyph_len5 | cryptarithm_deduce | answer_only_keep | 0 | answer_only_keep:latent_rule_nonunique | grouped_model_keeps_answer_but_not_unique_trace | [\) | \\+%\| |
| 8a1bdd48 | glyph_len5 | cryptarithm_deduce | answer_only_keep | 0 | answer_only_keep:latent_rule_nonunique | grouped_model_keeps_answer_but_not_unique_trace | `\&[ | \@*#[ |
| 9afe43b4 | glyph_len5 | cryptarithm_deduce | answer_only_keep | 0 | answer_only_keep:latent_rule_nonunique | grouped_model_keeps_answer_but_not_unique_trace | //(} | %}!#< |

Interpretation: `symbol_equation` の残差は主に 1) query operator 未出、2) prompt-consistent exact rule の多義性、3) unique local rule はあるが support が薄い low-shot slice、4) glyph の latent rule 非一意、に分かれる。これで 90% ceiling の主因を row-level / machine-readable に固定した。

