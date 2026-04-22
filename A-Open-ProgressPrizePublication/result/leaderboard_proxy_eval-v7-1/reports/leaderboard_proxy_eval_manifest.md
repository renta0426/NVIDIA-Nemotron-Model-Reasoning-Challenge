# Leaderboard Proxy V1 Report

## Purpose

This benchmark is a local leaderboard proxy aligned to README.md inference conditions. It is engineered to reproduce the observed rank gap between v3f and the current proof-first route-aware run, not to claim recovery of the hidden leaderboard set.

## Proxy scores

- v3f: `143 / 200 = 0.7150`
- current: `112 / 200 = 0.5600`

## Selected role counts

| role | rows |
| --- | ---: |
| `v3f_only` | 31 |
| `both_correct` | 112 |
| `both_wrong` | 57 |

## Selected source splits

| source_split | rows |
| --- | ---: |
| `phase0` | 110 |
| `specialized` | 90 |
