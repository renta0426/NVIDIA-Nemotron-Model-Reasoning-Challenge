# v20_corrective_corpus_v3 results

> 競技契約の正本は `README.md`。  
> 戦略根拠は `README.md` と `A-Open-ProgressPrizePublication/README.md`。  
> この v3 は **旧 d1 除外アブレーションを mainline に昇格するものではなく**、**現行 MLX 再現 run の失敗行に直接合わせた corrective corpus generator** を同フォルダへ追加した記録。

## 目的

- 現行 MLX 再現 run  
  `v20_mlx_repro_v1/outputs/v20_mlx_repro_v1_fullrun_targetfix_mb1/adapter_validation/validation_summary.json`
  の **`246 / 300 = 0.82`** を起点に、今この run が落としている行へ直接オーバーレイを張る。
- `README.md` の deterministic / boxed-answer 契約を守りつつ、`A-Open-ProgressPrizePublication/README.md` が明示する
  - bit の長期 main lever
  - equation_numeric の deterministic trace 有効性
  - cryptarithm の splitting / concatenation 弱さ
  を、**現行失敗分布**で再配分する。
- v2 は旧 Kaggle 系差分寄りで、現行 54 wrong のうち **5 行しか拾えていなかった**。v3 はここを修正する。

## 現行失敗プロファイル（MLX reproduced run）

- source run: `v20_mlx_repro_v1/v20_mlx_repro_v1-results.md`
- local eval: **`246 / 300 = 0.82`**
- 同じ 300 行に対する publication deterministic reasoners: **`257 / 300 = 0.856667`**
- wrong total: `54`
- category 別:
  - `cryptarithm_deduce = 23`
  - `cryptarithm_guess = 4`
  - `equation_numeric_deduce = 8`
  - `equation_numeric_guess = 2`
  - `bit_manipulation = 16`
  - `cipher = 1`

train metadata に突き合わせると、現行 wrong は主に次へ写像された。

- `glyph_len5 = 27`（cryptarithm 系）
- `numeric_2x2 = 10`（equation_numeric 系）
- `bit_structured_byte_formula / bit_prompt_local_exact_formula / bit_other = 16`
- `text_monoalphabetic = 1`

つまり v2 の binary 寄り補正だけでは足りず、**現行 MLX では symbolic equation / cryptarithm 補正を前面へ出す必要がある**。

## 実装

- Script: `versions/v20_corrective_corpus_v3/reproduce_v20_corrective_corpus_v3.py`
- 形式: **single-file monolith**
- 既定入力:
  - `cuda-train-data-analysis-v1/artifacts/train_recommended_learning_target_v1.csv`
  - `data/train.csv`
  - `A-Open-ProgressPrizePublication/nemotron/problems.jsonl`
  - `A-Open-ProgressPrizePublication/nemotron/reasoning/*.txt`
  - `A-Open-ProgressPrizePublication/nemotron/training/sft/04-08-16-14/logprobs/index.jsonl`
  - `v20_mlx_repro_v1/outputs/v20_mlx_repro_v1_fullrun_targetfix_mb1/adapter_validation/validation.csv`
  - `v20_mlx_repro_v1/outputs/v20_mlx_repro_v1_fullrun_targetfix_mb1/adapter_validation/validation_summary.json`
- 既定出力:
  - `corrective_selection.csv`
  - `current_mlx_failure_profile.csv`
  - `corrective_overlay_unique.jsonl`
  - `corrective_overlay_repeated.jsonl`
  - `anchor_watchlist.csv`
  - `corrective_overlay_summary.json`
  - `reports/corrective_overlay_report.md`
- optional:
  - `--write-training-bundle`
  - `A-Open-ProgressPrizePublication/nemotron/training/sft/v20_corrective_corpus_v3_bundle.jsonl`

### v2 からの設計差分

- **旧 signal 中心** → **現行 MLX wrong row 中心**
- **binary + easy guardrail** → **exact current failures + typed support**
- 新 bucket:
  - `current_symbol_glyph_failures`
  - `current_symbol_numeric_failures`
  - `current_bit_failures`
  - `current_cipher_failures`
  - `symbol_numeric_support`
  - `symbol_glyph_support`
  - `bit_formula_support`
- numeric support は **現行 failure operator と同じ operator** を優先。
- glyph support は **現行 failure answer 文字集合** に寄せる。
- bit support は **現行 failure の solver / abstract family** に寄せる。
- `0ec17d2e` は `train_recommended_learning_target_v1.csv` に不在だったため、`train.csv + reasoning + problems.jsonl` から fallback で拾う。

## Smoke generation

実行コマンド:

```bash
uv run python -m py_compile versions/v20_corrective_corpus_v3/reproduce_v20_corrective_corpus_v3.py
uv run python versions/v20_corrective_corpus_v3/reproduce_v20_corrective_corpus_v3.py --run-name smoke_current_mlx_failure_focus
```

## 2026-04-16 測定結果: `smoke_current_mlx_failure_focus`

- current failure coverage:
  - v2 overlap on current 54 wrong: **`5 / 54`**
  - v3 overlap on current 54 wrong: **`54 / 54`**
- selected unique rows: **`134`**
- selected repeated rows: **`290`**
- exact current failure rows: **`54`**
- support rows: **`80`**

bucket 別 unique:

- `current_symbol_glyph_failures = 27`
- `current_symbol_numeric_failures = 10`
- `current_bit_failures = 16`
- `current_cipher_failures = 1`
- `symbol_numeric_support = 24`
- `symbol_glyph_support = 32`
- `bit_formula_support = 24`

bucket 別 repeated:

- `current_symbol_glyph_failures = 81`
- `current_symbol_numeric_failures = 40`
- `current_bit_failures = 32`
- `current_cipher_failures = 1`
- `symbol_numeric_support = 48`
- `symbol_glyph_support = 64`
- `bit_formula_support = 24`

failure signal 要約:

- numeric failure operators:
  - `* = 2`
  - `} = 2`
  - `" = 1`
  - `' = 1`
  - `+ = 1`
  - `- = 1`
  - `: = 1`
  - `^ = 1`
- glyph failure answer chars 上位:
  - `: = 9`
  - `$ = 6`
  - `" = 5`
  - `(`, `<`, `>`, `?` が各 `4`
- bit failure solver 上位:
  - `binary_structured_byte_formula = 5`
  - `binary_structured_byte_formula_abstract = 5`
  - `binary_prompt_local_stage2_unique_exact = 2`

## 生成物

- `versions/v20_corrective_corpus_v3/outputs/smoke_current_mlx_failure_focus/artifacts/current_mlx_failure_profile.csv`
- `versions/v20_corrective_corpus_v3/outputs/smoke_current_mlx_failure_focus/artifacts/corrective_selection.csv`
- `versions/v20_corrective_corpus_v3/outputs/smoke_current_mlx_failure_focus/artifacts/corrective_overlay_unique.jsonl`
- `versions/v20_corrective_corpus_v3/outputs/smoke_current_mlx_failure_focus/artifacts/corrective_overlay_repeated.jsonl`
- `versions/v20_corrective_corpus_v3/outputs/smoke_current_mlx_failure_focus/artifacts/anchor_watchlist.csv`
- `versions/v20_corrective_corpus_v3/outputs/smoke_current_mlx_failure_focus/artifacts/corrective_overlay_summary.json`
- `versions/v20_corrective_corpus_v3/outputs/smoke_current_mlx_failure_focus/reports/corrective_overlay_report.md`

## Measured score ledger

| run | kind | measured source score | corrective coverage | notes |
| --- | --- | ---: | ---: | --- |
| smoke_current_mlx_failure_focus | corpus generation smoke | source MLX validation `246 / 300 = 0.82` | `54 / 54 = 1.0000` | no training yet; `134` unique / `290` repeated |

## 次のアクション

- この v3 overlay を使った学習・再評価はまだ未実施。
- 次は `equation_numeric_deduce` と `cryptarithm_*` の改善が本当に取れるか、`numeral / gravity / unit_conversion` 無劣化で検証する。
- public / proxy / local の 3 軸で、README 契約下の score を継続記録する。

## Historical note

同フォルダに残っている以下は **旧 v3 d1 exclusion / default-1 exposure ablation** の監査用 artifact。現時点の mainline corrective corpus 方針ではないが、履歴として保持する。

- `versions/v20_corrective_corpus_v3/d1_exclusion_list.json`
- `versions/v20_corrective_corpus_v3/v3_bundle_summary.json`

