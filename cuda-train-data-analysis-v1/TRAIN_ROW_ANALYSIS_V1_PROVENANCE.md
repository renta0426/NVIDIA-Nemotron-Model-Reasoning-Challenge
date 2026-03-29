# `train_row_analysis_v1.csv` 作成経緯・根拠まとめ

## 1. 結論

`cuda-train-data-analysis-v1/artifacts/train_row_analysis_v1.csv` は、`data/train.csv` の **9,500 行すべて**を対象に、行単位で

- family / subtype の再分類
- solver による厳密復元可否
- answer-only なら安全に残せるか
- 人手監査を優先すべきか
- gold label が怪しく除外すべきか

を記録した **最終台帳** です。

この CSV は `cuda-train-data-analysis-v1/code/train_data_analysis_v1.py` という **単一スクリプト**で生成され、最終時点では

- `9500` rows
- `97` columns
- `verified_trace_ready = 6086`
- `answer_only_keep = 1151`
- `manual_audit_priority = 2236`
## 6. family / tier の詳細はどこを見るべきか

family ごとの solved / unsolved の意味、selection tier の解釈、Kaggle 側 family 名との対応、学習へどう流し込むかは、重複を避けるため **FINAL_SUMMARY_REPORT.md を正本** とします。

とくに次の内容は provenance 本文で再説明せず、最終サマリを参照してください。

- `verified_trace_ready` / `answer_only_keep` / `manual_audit_priority` / `exclude_suspect` の実務的な意味
- `roman_numeral` / `gravity_constant` / `unit_conversion` / `text_decryption` / `bit_manipulation` / `symbol_equation` の最終解釈
- `symbol_equation` 内部の `numeric_2x2` / `glyph_len5` と Kaggle 側 `Equation (Numeric)` / `Equation (Symbolic)` の対応
- 今後の学習ハンドオフでどの artifact をどう使うか

この provenance 文書では以降、**どのコードと pass によって台帳が生成されたか** に焦点を当てます。

- 例から ratio を推定し、query に適用
- format / decimal places も確認
- 最終的に `1594 / 1594` verified

overview では template bucket は `unit_fixed_ratio` です。

### 6.4 `text_decryption`

`analyze_text_row(...)` は 3 段構えです。

1. character substitution がそのまま閉じるか
2. word dictionary で閉じるか
3. query で足りない文字を、**gold answer が矛盾なく埋める**か

この 3 番目が今回の最大収穫で、`reports/06_text_unknown_notes.md` にある通り、

- 未解決 `971` 行は mapping conflict ではなく
- query に必要な文字が examples に `1〜6` 文字足りないだけ

だったため、**全 971 行を clean `answer_only_keep`** に昇格できました。

結果:

- `605 verified`
- `971 answer_only`
- `manual 0`

### 6.5 `bit_manipulation`

`analyze_bit_row(...)` は binary を最も重く解析しています。

base pass で見ている family は:

- bit permutation / inversion
- bitwise independent copy/invert
- bijection
- 2-bit boolean
- 3-bit boolean
- GF(2) affine XOR
- byte transform (`not`, `xor_mask`, `and_mask`, `or_mask`, `lshift`, `rshift`, `lrot`, `rrot`, `reverse`, `nibble_swap`)
- structured byte formula 候補
- hybrid consensus 候補

ここで `bit_*` 系の多数の列が埋まり、後段 pass の材料になります。

とくに重要だったのは後段の structured-byte 系で、

- `reports/43` で `+189 verified`
- `reports/45` で singleton tail から `+29 verified`
- `reports/47` で same-pred multi-formula から `+2 answer_only`
- `reports/51` で thin abstract family から `+11 answer_only`
- `reports/54` で support3 narrow family から `+2 answer_only`
- `reports/56` で prompt reread により `+5 verified`, `+1 exclude`

が追加され、最終的に

- `604 verified`
- `35 answer_only`
- `947 manual`
- `16 exclude`

になりました。

### 6.6 `symbol_equation`

`analyze_symbol_row(...)` はまず `symbol` を

- `numeric_2x2`
- `glyph_len5`

に分けます。

#### `numeric_2x2`

`ddOdd` パターンを operator-aware に解き、formula / format を総当たりします。

base pass では

- same-operator examples が 2 本以上あり
- formula / format が一意に決まり
- gold と一致

なら `verified_trace_ready`、

- low-shot だが gold と一致

なら `answer_only_keep`

になります。

その後、

- prompt-backed exact family (`concat_xy`, `concat_yx`, `abs_diff_2d`, `abs_diff_2d_op_suffix`, `comp99_abs_diff_2d`)
- operator-specific consensus
- minus prefix subfamily
- minus direct plain
- star prefix-if-negative
- thin support2
- colon direct reread
- prefix-always-abs tail

が順次上書きされ、最終的に

- `110 verified`
- `145 answer_only`
- `1289 manual`
- `11 exclude`

になりました。

#### `glyph_len5`

こちらは coarse に

- `glyph_multiset_possible`
- `glyph_order_acyclic`

を付けますが、これは **診断用** です。

`reports/10_glyph_probe_notes.md`、`10_glyph_order_probe.md`、`24_glyph_exact_coarse_scan.md`、`16_glyph_manual_hold.md` が示す通り、

- simple transducer では `0 / 823`
- multiset 仮説に整合 `70`
- さらに order DAG 整合 `46`
- ただし exact examples-only enumeration でも `0 unique_string`

なので、最終的に glyph は **昇格の材料ではなく manual clustering の材料**として扱われました。

## 7. `train_row_analysis_v1.csv` にどの report がどう反映されたか

`train_row_analysis_v1.csv` の最終版は、1 回の script 実行だけで突然できたのではなく、`reports/` の判断がコードへ織り込まれて固まっています。

### Phase A: 土台作り (`00`-`09`)

- `00_kickoff.md`: README / result / plan を grounding に固定
- `01_overview.md`: 初回全体像、family summary、高優先 manual 行
- `02_hard_family_findings.md`: binary / text / symbol の base solver で何が取れるか
- `03_curation_recommendations.md`: tier の意味を定義
- `04_mid_results.md`: 中間スナップショット (`5816 verified / 65 answer_only / 3602 manual / 17 exclude`)
- `05_symbol_split_notes.md`: `symbol` を `numeric_2x2` と `glyph_len5` に分割
- `06_text_unknown_notes.md`: text 971 行を clean answer-only と判断
- `07_binary_cluster_notes.md`: unresolved binary の cluster を定義
- `08_symbol_operator_notes.md`: operator 別の symbol queue を可視化
- `09_manual_pass1_pack.md`: `manual_pass1_priority_pack_v1.csv` の起点を定義

### Phase B: pass1 と安全性の証明 (`10`-`19`)

- `10_glyph_probe_notes.md`: glyph の simple transducer 仮説を否定
- `10_glyph_order_probe.md`: glyph の coarse multiset/order 仮説を定義
- `11_latest_snapshot.md`: 最新 counts を最短確認する snapshot
- `12_symbol_tail_probes.md`: broader linear probe / glyph consistency probe の negative evidence
- `13_manual_curation_pass1.md`: prompt-backed exact symbol rowsの昇格、binary low-gap の扱い
- `14_symbol_residual_template_scan.md`: symbol residual scan
- `15_binary_residual_affine_scan.md`: low-gap affine mismatch の exclude ルールを確定
- `16_glyph_manual_hold.md`: glyph 46 行を全件 manual hold
- `17_symbol_query_only_rejection.md`: query-only arithmetic lookalike 43 行を却下
- `18_symbol_next_safe_scan.md`: 次の derived family を探したが gain `0`
- `19_pass1_completion_and_round2.md`: pass1 を閉じて round2 優先順位を明文化

### Phase C: round2 cluster 化と hold 記録 (`20`-`41`)

この群は「新規昇格」よりも、**何を昇格させないか** を定義したフェーズです。

- `20` / `21` / `22`: symbol / glyph / binary の round2 cluster map
- `23`: known-family mimic union を分離
- `24`: glyph exact coarse enumeration でも `0 unique string`
- `25`-`40`: symbol / binary の各 top cluster を読み直したが安全昇格 `0`
- `41`: broader symbol template library でも repeated exact hit `0`

つまりこの phase は、`train_row_analysis_v1.csv` の `manual_audit_priority` が「取り切れていない」のではなく、**安全上 hold された manual** であることを保証する材料です。

### Phase D: 後半の追加回収 (`42`-`59`)

ここで final CSV に入る late promotion / exclusion が確定しました。

- `42`: binary hybrid consensus `+20 answer_only`
- `43`: structured byte formula `+189 verified`
- `44`: structured-byte residual を category 化
- `45`: abstract structured-byte family `+29 verified`
- `46`: threshold を緩めても gain 薄いので不採用
- `47`: same-pred multi-formula `+2 answer_only`
- `48`: symbol operator-embedded near-miss だが未採用
- `49`: operator-specific consensus `+16 answer_only`
- `50`: minus prefix subfamily `+3 answer_only`
- `51`: low-support structured-byte answer-only `+11`
- `52`: star prefix-if-negative `+3 answer_only`
- `53`: minus direct plain `+3 answer_only`
- `54`: support3 structured-byte `+2 answer_only`
- `55`: thin support2 `+2 answer_only`
- `56`: structured-byte manual reread `+5 verified`, `+1 exclude`
- `57`: colon manual reread `+2 answer_only`
- `58`: prefix-always-abs tail `+2 answer_only`
- `59`: single-example gold-hit tail 8 行を全 hold

## 8. `train_row_analysis_v1.csv` の列構成

### 8.1 全体

- `train_metadata_rebuilt_v1.csv`: `41` columns
- `train_row_analysis_v1.csv`: `97` columns
- 追加列: `56`
- metadata 側の列は **1 つも落ちていません**

### 8.2 `versions/v1` 由来の 41 metadata 列

```text
id, prompt, answer, family, subfamily, answer_type, parse_ok, parse_confidence,
num_examples, query_raw, group_signature, hard_score, risk_bin, prompt_len_chars,
prompt_len_words, answer_len, contains_right_brace, contains_backslash,
contains_backtick, is_public_test_overlap, special_chars, query_value_float,
estimated_g, estimated_ratio, roman_query_value, bit_query_binary, fit_family,
query_hamming_bin, g_bin, answer_decimal_style, ratio_bin, query_bin,
near_round_boundary, answer_word_count, token_len_signature, char_overlap_bin,
rare_token_flag, unique_char_ratio, token_length_pattern_rare,
query_charset_rarity, boxed_safe
```

このうち `is_public_test_overlap` のような項目は `data/test.csv` を使って再構築されています。

### 8.3 この script が追加した 56 列

#### 共通判断列

```text
template_main, template_main_label, template_subtype, teacher_solver_candidate,
auto_solver_predicted_answer, auto_solver_match, verified_trace_ready,
example_consistency_ok, selection_tier, audit_priority_score, audit_reasons,
analysis_notes, family_analysis_json, suspect_label, answer_only_ready
```

#### binary 追加列

```text
bit_simple_family, bit_candidate_signature, bit_independent_unique,
bit_bijection_unique, bit_bijection_solution_count, bit_boolean2_unique,
bit_boolean3_unique, bit_affine_unique, bit_byte_transform_unique,
bit_no_candidate_positions, bit_multi_candidate_positions,
bit_byte_transform_names, bit_hybrid_consensus_ready,
bit_hybrid_consensus_varset, bit_hybrid_consensus_match_count,
bit_hybrid_consensus_prediction_count, bit_structured_formula_name,
bit_structured_formula_prediction, bit_structured_formula_names,
bit_structured_formula_predictions, bit_structured_formula_matches_gold,
bit_structured_formula_match_count, bit_structured_formula_prediction_count,
bit_structured_formula_safe_support, bit_structured_formula_safe,
bit_structured_formula_abstract_family,
bit_structured_formula_abstract_support,
bit_structured_formula_abstract_error_rows,
bit_structured_formula_abstract_distinct_exact,
bit_structured_formula_abstract_safe
```

#### text 追加列

```text
text_wordmap_predicted_answer, text_unknown_char_count, text_unknown_chars,
text_answer_completion_new_pair_count, text_answer_completion_pairs
```

#### symbol / glyph 追加列

```text
symbol_query_operator, symbol_same_operator_example_count,
symbol_numeric_formula_name, symbol_numeric_candidate_prediction_count,
glyph_multiset_possible, glyph_order_acyclic
```

## 9. 派生 CSV は何を切り出したものか

`train_row_analysis_v1.csv` は master ledger で、他の主要 CSV はその切り出しです。

| ファイル | 行数 | 内容 |
| --- | ---: | --- |
| `train_row_analysis_v1.csv` | `9500` | 全件台帳 |
| `train_recommended_learning_target_v1.csv` | `7237` | `verified + answer_only` |
| `train_verified_trace_ready_v1.csv` | `6086` | 最も強い教師 |
| `train_answer_only_keep_v1.csv` | `1151` | conservative answer-only |
| `train_manual_audit_priority_v1.csv` | `2236` | 未解決・要人手確認 |
| `train_exclude_suspect_v1.csv` | `27` | gold / rule conflict 等で除外 |

補助的には、`FINAL_SUMMARY_REPORT.md` 5.1 / 5.2 節の一覧がそのまま artifact 索引になっています。

## 10. `analysis_manifest_v1.json` が保証していること

`artifacts/analysis_manifest_v1.json` には

- `script_version`
- `generated_at_utc`
- `repo_root`
- `out_root`
- `row_count = 9500`
- `selection_tier_counts`
- 生成ファイル一覧

が入っています。

つまり provenance の観点では、

- **どの script が**
- **いつ**
- **どの root で**
- **何ファイル生成したか**

を manifest で追跡できます。

## 11. これが「学習データそのもの」ではない理由

`train_row_analysis_v1.csv` は completion 済みの学習 JSONL や SFT corpus ではなく、**学習データを作るための row-level ledger** です。

どの tier を trace 化し、どの tier を answer-only に留め、どの tier を保留 / 除外するかの意味付けは、学習者向けの正本である `FINAL_SUMMARY_REPORT.md` に集約しています。ここでは provenance の観点から、`train_row_analysis_v1.csv` が

- metadata 再構築
- row 解析
- promotion / exclusion pass
- artifact 切り出し

を経て生成された **中間管理台帳** であることだけ押さえれば十分です。

## 12. 再生成コマンド

最終サマリに記載されている再実行例は以下です。

```bash
cd /home/renta0426/kaggle/NVIDIA-Nemotron-Model-Reasoning-Challenge
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=.venv/lib/python3.12/site-packages \
.venv/bin/python cuda-train-data-analysis-v1/code/train_data_analysis_v1.py \
  --repo-root /home/renta0426/kaggle/NVIDIA-Nemotron-Model-Reasoning-Challenge \
  --out-root /home/renta0426/kaggle/NVIDIA-Nemotron-Model-Reasoning-Challenge/cuda-train-data-analysis-v1
```

この実行で

- metadata 再構築
- row ledger 作成
- tier 別 CSV 切り出し
- support / candidate / cluster artifact 生成
- `reports/` 生成
- `analysis_manifest_v1.json`

まで一括で出ます。

## 13. 最短の参照順

重複を避けるため、用途ごとに参照先を分けます。

1. 学習へどう流すか知りたいとき
  - `cuda-train-data-analysis-v1/FINAL_SUMMARY_REPORT.md`
2. 行台帳がどう生成されたか知りたいとき
  - この provenance 文書
3. 実データを見たいとき
  - `cuda-train-data-analysis-v1/artifacts/train_row_analysis_v1.csv`
4. 実装を確認したいとき
  - `cuda-train-data-analysis-v1/code/train_data_analysis_v1.py`

## 14. 一言で言うと

`train_row_analysis_v1.csv` は、`README.md` の accuracy-first 制約と、`reports/00` から `reports/59` までの安全側判断を、単一スクリプトで再現可能な形に束ねた **row-level audit ledger** です。

本質は family 名の説明そのものではなく、**どの pass が、どの row を、どの tier へ移したかを追跡可能にしていること** にあります。
