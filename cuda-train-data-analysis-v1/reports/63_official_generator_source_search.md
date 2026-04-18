# cuda-train-data-analysis-v1 official generator source search

## Purpose

Check whether the missing evidence for `cryptarithm_guess` / `equation_numeric_guess` can be closed by an official or benchmark-adjacent public source, rather than by another local heuristic pass.

## Search targets

Looked for public references to:

- `cryptarithm_guess`
- `equation_numeric_guess`
- the official equation wrapper text
  - `"In Alice's Wonderland, a secret set of transformation rules is applied to equations."`

Search surfaces used:

- GitHub code search on public repos
- `NVIDIA-NeMo/Nemotron`
- benchmark-adjacent public repos already referenced in this workspace
- web search for an official NVIDIA / benchmark generator source

## Result

No official public generator source was found for:

- `cryptarithm_guess`
- `equation_numeric_guess`
- row-level query-operator semantics for the `Alice's Wonderland` equation family

Additional observations:

- `NVIDIA-NeMo/Nemotron` code search returned no hits for the exact equation wrapper text and no hits for the `*_guess` category names.
- external public repos mostly expose:
  - prompt wrappers
  - training / evaluation utilities
  - solver heuristics
- but not the authoritative benchmark generator needed to certify unseen query operators.
- a broader public-repo sweep likewise surfaced competitor heuristics and fallback factories, not an authoritative row-level generator or semantics table for `cryptarithm_guess`.
- broader web results also failed to close the gap:
  - the Kaggle competition overview and Luma announcement describe the benchmark only at a high level
  - a public competitor repo (`Hardik-Sankhla/nvidia-nemotron-reasoning`) exposes pipeline / evaluation structure, but not row-level generator semantics
  - generic web answers about cryptarithms or equation guessing were non-authoritative puzzle descriptions, not benchmark-specific source material

## Interpretation

This does **not** prove that the benchmark generator never existed internally.

It does show something narrower and operationally important:

- there is no currently found official public source in scope that can be cited to turn `cryptarithm_guess` rows into strict `verified_trace_ready` promotions
- and the public competitor implementations found in scope also remain heuristic / answer-level rather than generator-backed

So the remaining evidence gap is real, not just overlooked in the local repo.

## Decision

Treat the 90% verified target as blocked by missing public evidence unless a new official source is obtained.

Until such a source appears, further local work can still improve:

- answer-only recovery
- ambiguity documentation
- counterexample curation

but not a defensible jump to `symbol_equation >= 90% verified` under the current strict standard.
