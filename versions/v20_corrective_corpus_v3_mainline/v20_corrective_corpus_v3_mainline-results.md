# v20_corrective_corpus_v3_mainline results

> Repository note: canonical challenge contract lives in `README.md`.
> This version prepares a **single-file corrective training bundle** for the Kaggle direct-training path and preserves the submission target as `submission.zip`.
> Measured validation / proxy / leaderboard scores for this version must be recorded here after each run.

## Purpose

- Base strategy source: `A-Open-ProgressPrizePublication/v20_to_088_strategy.md`
- README grounding:
  - `bit_manipulation` remains the main upside slice (`README.md`)
  - higher score requires new programmatic insight, so we should improve binary signal without damaging easy families
- Correction vs prior v3 ablation:
  - do **not** blacklist every `default 1` trace
  - remove only **actual metric-wrong teacher rows** from the v20 snapshot
  - allow only **teacher-correct** overlay examples into the binary corrective pack

## Implementation

- Script: `versions/v20_corrective_corpus_v3_mainline/reproduce_v20_corrective_corpus_v3_mainline.py`
- Style: single-file monolith
- Bundle:
  - `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v3_mainline_bundle.jsonl`
- Kaggle notebook path:
  - `A-Open-ProgressPrizePublication/kaggle-v20-sft-repro.ipynb`

## Current status

- Implementation: **ready**
- Bundle generation: **done**
- Teacher-correct overlay audit: **done**
- Kaggle training run: **done**
- Validation / proxy evaluation: **done**
- `submission.zip` export: **pending**

## 2026-04-16 corpus generation: `v3_mainline_default`

### Core fixes

1. Base snapshot exclusion:
   - removed metric-wrong base problem ID: `ef2fe526`
   - removed base rows: `ef2fe526`, `ef2fe526-p0`
2. Overlay correctness gate:
   - filtered out `130` teacher-incorrect binary candidates before selection
   - selected overlay rows with teacher mismatch: `0`
3. Binary emphasis:
   - `binary_structured_core = 192` unique / `768` repeated
   - `binary_other_light = 80` unique / `160` repeated
4. Guardrails kept light:
   - numeral / gravity / unit / cryptarithm symbolic at `12` unique each
   - symbol prefix at `2` unique

### Bundle summary

| Metric | Value |
| --- | ---: |
| Base examples kept | `7828` |
| Overlay examples | `990` |
| Total examples | `8818` |
| Total steps | `276` |
| Total tokens | `34,703,186` |
| Max seq len | `7971` |
| Retokenized overlay problem count | `2` |

### Selected buckets

| Bucket | Unique | Repeated |
| --- | ---: | ---: |
| binary_structured_core | `192` | `768` |
| binary_other_light | `80` | `160` |
| guardrail_numeral_subtractive | `12` | `24` |
| guardrail_gravity_fragile | `12` | `12` |
| guardrail_unit_fragile | `12` | `12` |
| guardrail_cryptarithm_symbolic | `12` | `12` |
| guardrail_symbol_prefix | `2` | `2` |

### Diagnostics

- `proxy_failed_selected = 1`
- `validation_failed_selected = 0`
- binary mandatory rows forced in:
  - structured: `0520a6ec`, `0a50c4a8`, `59c78e51`, `fa67da07`
  - other: `8e5d6fe6`, `b9500f41`, `c30a782a`

## Score ledger

| run | data change | validation | proxy | public leaderboard | notes |
| --- | --- | ---: | ---: | ---: | --- |
| v3_mainline_default (`results-v3`) | v20 minus `ef2fe526*` + teacher-correct-only binary overlay + heavier binary repeats / lighter guardrails | `801/950 = 84.3%` | `180/200 = 0.9000` | user-reported `0.84-0.85` | proxy improved, but validation collapsed from answer-surface regressions; not promotable |

## Recording

All scores are recorded from measured outputs only. Update this file after each Kaggle run.

## 2026-04-16 measured run analysis: `results-v3` / `leaderboard_proxy_eval-v3`

README.md の評価契約では、提出は **`\boxed{}` を優先して抽出**され、A-Open README でも Nemotron の弱点として **`\\boxed` 終端の崩れ**、**記号 split / concat の弱さ**、**template 末尾破損** が明示されている。今回の v3 はまさにその弱点を踏み抜いた。

### v2 からの学習データ変更

1. **binary teacher 品質を強くした**
   - base snapshot から metric-wrong row `ef2fe526*` だけを除外。
   - overlay 候補から **teacher-incorrect binary 130 行**を除外。
   - その結果、binary corrective line は **teacher-correct-only** になった。
2. **repeat 予算を binary に再配分した**
   - `binary_structured_core`: `480 -> 768`
   - `binary_other_light`: `64 -> 160`
   - `guardrail_numeral_subtractive`: `48 -> 24`
   - `guardrail_gravity_fragile`: `24 -> 12`
   - `guardrail_unit_fragile`: `24 -> 12`
   - `guardrail_cryptarithm_symbolic`: `48 -> 12`
   - `guardrail_symbol_prefix`: `2 -> 2`
3. **bundle 全体は v2 より少し重くした**
   - total tokens: `32,083,353 -> 34,703,186`
   - total steps: `267 -> 276`

要するに、**binary trace の純度は上げたが、surface repair / easy-family preservation は薄くした** run だった。

### スコアの読み方

- validation:
  - v20: `837/950 = 88.1%`
  - v1: `838/950 = 88.2%`
  - v2: `839/950 = 88.3%`
  - **v3: `801/950 = 84.3%`**
- leaderboard proxy:
  - v20: `176/200 = 0.8800`
  - v1: `178/200 = 0.8900`
  - v2: `176/200 = 0.8800`
  - **v3: `180/200 = 0.9000`**
- public leaderboard:
  - **user-reported `0.84-0.85`**

つまり v3 は **proxy では過去最高**だが、**validation と public は悪化**した。README / strategy で置いていた promotion gate（validation 839 以上、numeral / gravity / unit / text の純減なし）を明確に失敗している。

### 生出力で実際に改善したこと

binary については、teacher-correct-only 化が **狙い通り効いた**。

- validation 改善:
  - `0520a6ec`: `01100001 -> 10100001`
  - `0dd5caf4`: `6 default 1 = 1` が消え `00000010 -> 00000000`
  - `17fd9612`: 途中の operator detail が戻り `00001010 -> 00011010`
- proxy 改善:
  - `c30a782a`: `3 default 1 = 1` が `3 AND-NOT07 = AND(0,NOT(1)) = 0` に戻り `01010110 -> 01000110`
  - `b9500f41`: `4 default 1 = 1` が消え `11111000 -> 11110000`
  - `8e5d6fe6`: `OR-NOT50` の無限反復が消え、`50 -> 10000111`
  - `0520a6ec`: `AND-NOT25` drift が消え `01100001 -> 10100001`
  - `d9bedb64`: symbol prefix が戻り `1 -> (1`

ここで見えているのは、**binary 失点の主因が format failure ではなく content drift / `default 1` 汚染だった**という点。v3 の binary corrective はこの点には確かに効いている。

### 生出力で新たに悪化したこと

一方で、guardrail を薄くした副作用は **answer surface** に集中した。

1. **numeral が 31 行まとめて `\\boxed` -> `\\box` に崩れた**
   - validation `numeral`: `147/149 -> 116/149`
   - wrong 33 行のうち **33 行が `\\box` だが `\\boxed` ではない**
   - 代表例:
     - `00d9f682`: raw output は `Result: C` まで正しいが、末尾が `I will now return the answer in \box` になり prediction は `0`
     - `02e4851e`: `XLIV` を正しく作れているのに boxed surface を失って `0`
     - `188fe6d4`: `IX` を正しく作れているのに boxed surface を失って `0`
2. **cipher も同じ surface failure を起こした**
   - `0184a864`, `018c6f61`, `13db9692`, `16642d10`
   - reasoning 自体は合っているのに、末尾が `\wizard reads in village\` のような **backslash 包み** になって metric miss
3. **cryptarithm symbolic answer でも terminal corruption が再発した**
   - `0133bcec`, `065abaf6`, `0dcfd566`
   - いずれも途中の symbol 復元はかなり正しいが、最後が `\box` や escape 崩れになり prediction が `5` などへ化ける
4. **少数だが content regression も残った**
   - `034fb629`: `00111001 -> 01111001`
   - `053f87d3`: permutation trace が反復ループし prediction `0`
   - `077cfc0b`: `40.023 -> 39.023`

つまり v3 の失点は v2 と違って、**binary の弱さではなく、answer surface の系統崩壊**が主因になった。

### なぜ proxy 0.900 と public / validation が食い違ったか

proxy 側では、この新しい failure mode がほぼ出ていない。

- proxy `roman_standard`: `19/19`, `\\box` だが `\\boxed` ではない行は `0`
- proxy `text_monoalphabetic`: `20/20`, `\\box` だが `\\boxed` ではない行は `0`
- proxy binary はむしろ改善して `76/92 -> 80/92`

したがって v3 proxy は **binary hard slice の改善だけを強く拾い、validation で爆発した boxed-surface failure をほとんど踏まなかった**。README が指摘している「held-out validation をちゃんと持つべきだった」という反省と完全に一致する。

### 結論

v3 mainline は、

- **binary corrective の純化**という仮説には成功した
- しかし **guardrail / surface repair を削りすぎた**
- その結果、README 評価契約で重要な **final answer surface** が numeral / cipher / cryptarithm で壊れた

よって今回の学びは明確で、**teacher-correct-only binary overlay 自体は残す価値があるが、v2 より削った guardrail をそのまま mainline から外してはいけない**。特に `\\boxed` を安定させる terminal pattern は、binary とは別 line で維持しないと proxy 改善がそのまま public 改善に繋がらない。
