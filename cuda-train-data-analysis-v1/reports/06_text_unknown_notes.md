# cuda-train-data-analysis-v1 text unknown-char notes

## Text answer-completion summary

| text_unknown_char_count | text_answer_completion_new_pair_count | analysis_notes | rows |
| --- | --- | --- | --- |
| 1 | 1 | text_answer_completion | 591 |
| 2 | 2 | text_answer_completion | 277 |
| 3 | 3 | text_answer_completion | 78 |
| 4 | 4 | text_answer_completion | 19 |
| 5 | 5 | text_answer_completion | 5 |
| 6 | 6 | text_answer_completion | 1 |

## Remaining text manual-audit queue

| id | text_unknown_char_count | text_unknown_chars | hard_score | answer | query_raw |
| --- | --- | --- | --- | --- | --- |

Observation: all previously unresolved text rows are conflict-free monoalphabetic ciphers. They now move to `answer_only_keep` because the gold answer cleanly closes the missing 1-6 character mappings without contradicting any in-row examples.
