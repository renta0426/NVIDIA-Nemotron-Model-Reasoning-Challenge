# cuda-train-data-analysis-v1 glyph answer-only hold

## Decision

- pass1 glyph rows reviewed: `0`
- rows promoted: `470`
- rows newly excluded: `0`
- decision: move remaining non-suspect glyph rows to `answer_only_keep`, while keeping them out of `verified_trace_ready`.

## Why they stay non-trace-safe

- exhaustive grouped / exact-coarse glyph scans still do not produce unique latent rules for the remaining rows.
- however, these rows are `parse_ok`, carry no `suspect_label`, and no glyph row shows a concrete rule-vs-gold contradiction strong enough for `exclude_suspect`.
- exact examples-only enumeration under the same coarse model still yields `0` unique query strings (`0` query-unseen, `0` ambiguous-multiset, `0` ambiguous-order, `0` no-multiset).
- per `README.md`, leaderboard score is direct final-answer accuracy, so these rows are safer as answer-only supervision than as trace teachers.

## Representative glyph answer-only rows

| id | hard_score | answer | query_raw |
| --- | --- | --- | --- |
| 4bb8c6cd | 9.0 | ]}\! | ]}*\! |
| 50ba5396 | 9.0 | \]]@ | }&(\" |
| 56efc838 | 9.0 | }$?( | ()*?} |
| 71d91445 | 9.0 | } | \"/@\| |
| a40497f9 | 9.0 | %]\< | <%*]\ |
| d7e5414c | 9.0 | \|%\\ | #[}@[ |
| 10a94678 | 8.0 | ""\} | ">*)\ |
| 193c21d5 | 8.0 | }>[[ | >\|*%{ |
| 2e9973b7 | 8.0 | )\?% | )\+?% |
| 3cc03e36 | 8.0 | }\|(# | #/*\|# |
| 60ed3f31 | 8.0 | @%:\ | @%*:\ |
| 65b13ba2 | 8.0 | ]/"} | #@{]" |
| 7138d71a | 8.0 | \ | ^]-'% |
| 7933172a | 8.0 | ^/&` | %#+^` |
| 7a65a8eb | 8.0 | }'#' | '(*?? |
| 82b32563 | 8.0 | ^\%\ | %\+^\ |
| 8326116b | 8.0 | {{@? | #:*#\ |
| 98eed496 | 8.0 | ^[}` | ^[>}` |
| b50cf853 | 8.0 | \|?"} | \|?*"} |
| c37e694c | 8.0 | {&\\ | /{*{\ |

## Residual glyph manual rows

_none remain after the training-label promotion pass._

Interpretation: even the best glyph candidates remain underdetermined as latent-rule teachers. They are still valid final-answer supervision, so the current pass keeps them as answer-only labels while withholding trace-ready status.
