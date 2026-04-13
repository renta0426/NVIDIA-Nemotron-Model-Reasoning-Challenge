v2-plam.md
Version: 0.1  
Owner: me  
Prerequisite: `versions/v0/v0-plan.md` 完了済み / `versions/v1/v1-plam.md` 完了済み  
Scope: `versions/plan-overview.md` のうち、今後の全実験で共通利用する **データ生成・蒸留・学習・包装・採用判定** の基盤を、Mac 固定実行環境前提で v2 に固定する  
Purpose: v1 の evaluator / metadata / splits / eval packs を土台に、**solver-verified data factory + Mac-first training substrate + packaging gate** を作る

Historical plan note: this file preserves the original planning context, but the current authoritative competition contract is the top-level `README.md` Evaluation / Submitting section (`max_lora_rank = 32`, `max_tokens = 7680`, `top_p = 1.0`, `temperature = 0.0`, `max_num_seqs = 64`, `gpu_memory_utilization = 0.85`, `max_model_len = 8192`, final artifact `submission.zip`). If later sections in this historical plan mention older notebook/metric defaults, read them as historical notes rather than as the active contract.

## 0. この v2 の位置づけ

v0 で固定したのは、以後の全実験でぶらしてはいけない前提だった。

- Source of Truth の優先順位
- official evaluation 条件
- visible `test.csv` の扱い
- competition prompt の不変条件
- 採用基準の骨格

v1 で作ったのは、以後の全実験で毎日回す評価基盤だった。

- metric-faithful local evaluator
- extraction risk suite
- deterministic metadata / family parser
- deterministic validation splits / eval packs
- official deterministic eval と stochastic probe eval

v2 では、その上に **「実際に改善を作るためのデータ・学習基盤」** を作る。

この v2 の責務は、次の 7 点に限定する。

1. real data を学習用 canonical 形式へ固定する  
2. family ごとの exact / conservative solver・generator・validator を作る  
3. synthetic / distilled / correction / format data を strict gate 付きで作る  
4. Stage A / Stage B の学習 pack を deterministic に作る  
5. LoRA / QLoRA の基準学習 recipe を固定する  
6. PEFT 互換 packaging gate を固定する  
7. v1 evaluator を使った promotion rule を固定する  

重要なのは、v2 が **「全部の強化手法を実装する版」ではない** こと。

v2 は、以後の

- baseline LoRA
- sibling synthetic
- distilled short traces
- format sharpening
- correction / preference
- RFT
- specialist merge

のすべてが同じ土台で比較できるようにする **基盤版** である。

したがって v2 では、広げすぎることよりも

- v0 / v1 と矛盾しないこと
- ラベルと評価が壊れないこと
- 将来の ablation が一貫して比較できること

を優先する。

## 1. v2 で絶対に継承する前提

### 1-1. official evaluation の正は v0 / v1 を継承する

`versions/plan-overview.md` には metric notebook 既定値を強く扱う記述があるが、これは v0 で再整理済みである。  
v2 ではこの議論を reopen しない。

本番相当の採用判定は、以後も `README.md` + Kaggle staff clarification を継承した `official_lb` を正とする。

- `temperature = 0.0`
- `top_p = 1.0`
- `max_tokens = 7680`
- `max_num_seqs = 64`
- `max_model_len = 8192`
- `gpu_memory_utilization = 0.85`
- `enable_thinking = True`
- `add_generation_prompt = True`

`notebook_default` と `sc_probe@K` は、以後も

- 補助観察
- stochastic robustness 診断
- teacher sampling の参考

にのみ使う。

### 1-2. visible `test.csv` は今後も validation に使わない

`README.md` と既存分析どおり、visible `test.csv` は sample-only であり、`train.csv` と重複する。  
v2 でも用途は次に限定する。

- submission zip の smoke
- packaging の整合確認
- extractor / formatter の smoke

学習採用や split 評価には使わない。

### 1-3. v1 evaluator / extractor / verify は不変

v2 は学習データや出力 style を工夫してよいが、採点ロジックを勝手に変えてはならない。  
以後の評価は v1 の metric-faithful 実装を使う。

特に固定するもの:

- boxed 優先 / fallback 付き extraction 順序
- `verify()` の exact / numeric tolerance
- `}` を含む answer に対する boxed risk の扱い
- competition prompt builder の形

### 1-4. 合成ラベルは solver / validator ベースでしか採用しない

`SYNTHETIC_DATA_AUGMENTATION_POLICY.md` を継承し、v2 では次を必須にする。

- programmatic generator + exact solver
- または teacher proposal + independent validator

禁止:

- LLM が answer を直接決め、そのまま採用
- validator なし freeform synthetic を本学習へ投入
- real-only validation を悪化させても継続投入

### 1-5. リポジトリ規約として code は 1 ファイルに集約する

v1 で確定したとおり、version ごとのコア実装は `versions/vN/code/` 配下の単一ファイルに置く。  
したがって v2 でも code の中心は次で固定する。

- `versions/v2/code/train.py`

config / data / reports / tests は複数ファイルでよいが、ロジックの主実装は 1 ファイルにまとめる。

### 1-6. 実行環境は Mac 固定、かつ 512GB RAM 前提にする

以後の daily loop は **macOS 上で完結できること** を前提にする。  
Linux / CUDA / 98GB GPU は v2 の前提にしない。

ローカル primary workload は次に固定する。

- MLX / Apple Silicon 上の teacher inference
- self-consistency sampling
- synthetic / distilled / correction / format data build
- v1 evaluator によるローカル比較
- packaging 変換と smoke
- 可能なら Mac 上での adapter training

また、RAM 512GB を前提に、メモリは保守的に節約しすぎない。

- registry / candidate pool / cached generations はメモリ常駐を前提にしてよい
- hard family では `N=8〜32` の candidate sampling を許可する
- teacher 系 process は複数並列を前提にしてよい

ただし、**メモリが潤沢でも acceptance gate は緩めない**。

- dedup
- solver validation
- real-only validation 優先

は v1 / v2 を通して厳守する。

## 2. v2 の最終成果物

v2 完了時点で、少なくとも以下が揃っていることを完了条件とする。

### 2-1. 必須成果物

1. `train_real_canonical_v2.parquet`  
2. `solver_registry_v2.json`  
3. `synthetic_registry_v2.parquet`  
4. `teacher_trace_registry_v2.parquet`  
5. `synth_core_v2.parquet`  
6. `synth_hard_v2.parquet`  
7. `synth_format_v2.parquet`  
8. `distilled_traces_v2.parquet`  
9. `correction_pairs_v2.parquet`  
10. `format_pairs_v2.parquet`  
11. `stage_a_mix_v2.parquet`  
12. `stage_b_mix_v2.parquet`  
13. `train_mix_registry_v2.parquet`  
14. `sft_stage_a_*` / `sft_stage_b_*` の Mac-first training config 群  
15. `active_model.json` / `model_registry_v2.json`  
16. `peft_smoke.yaml` と packaging check 出力  
17. `candidate_registry_v2.csv`  
18. `promotion_rules_v2.txt`  
19. `training_command_book_v2.txt`  
20. v2 tests  
21. `versions/v2/code/train.py`

### 2-2. v2 が提供すべき運用価値

v2 完了後は、以後の各 version が少なくとも次を再利用できる状態にする。

- real / synth / distilled / correction の共通 schema
- family-aware な data mix
- final answer weighting を含む学習入力生成
- Mac-first LoRA recipe の比較軸
- PEFT packaging の smoke
- v1 evaluator による promotion 判定

## 3. 追加ディレクトリ構成

v2 は次の構成で作る。  
ここでは **code は 1 ファイル**、その周辺の config / data / tests / reports を version 配下に持つ。

```text
versions/v2/
├── v2-plam.md
├── code/
│   └── train.py
├── conf/
│   ├── data/
│   │   ├── real_canonical.yaml
│   │   ├── synth_core.yaml
│   │   ├── synth_hard.yaml
│   │   ├── teacher_distill.yaml
│   │   ├── format_sharpening.yaml
│   │   ├── mix_stage_a.yaml
│   │   └── mix_stage_b.yaml
│   ├── train/
│   │   ├── sft_stage_a_r32_alpha32.yaml
│   │   ├── sft_stage_a_r32_alpha32_weighted.yaml
│   │   ├── sft_stage_a_r32_alpha64.yaml
│   │   ├── sft_stage_b_hardening.yaml
│   │   └── sft_stage_b_a6000_compat.yaml
│   └── package/
│       └── peft_smoke.yaml
├── data/
│   ├── processed/
│   │   ├── train_real_canonical_v2.parquet
│   │   ├── solver_registry_v2.json
│   │   ├── synthetic_registry_v2.parquet
│   │   ├── teacher_trace_registry_v2.parquet
│   │   └── train_mix_registry_v2.parquet
│   ├── synth/
│   │   ├── synth_core_v2.parquet
│   │   ├── synth_hard_v2.parquet
│   │   ├── synth_format_v2.parquet
│   │   ├── distilled_traces_v2.parquet
│   │   ├── correction_pairs_v2.parquet
│   │   └── format_pairs_v2.parquet
│   └── train_packs/
│       ├── stage_a_mix_v2.parquet
│       ├── stage_b_mix_v2.parquet
│       └── stage_b_hard_only_v2.parquet
├── outputs/
│   ├── audits/
│   ├── datasets/
│   ├── models/
│   ├── runtime/
│   ├── train/
│   ├── eval/
│   ├── packaging/
│   └── reports/
└── tests/
    ├── test_real_canonical_builder.py
    ├── test_solver_acceptance.py
    ├── test_generators_v2.py
    ├── test_dedup_and_registry.py
    ├── test_train_mix_builder.py
    ├── test_loss_weighting.py
    └── test_peft_packaging_spec.py
```

## 4. `versions/v2/code/train.py` の責務

v2 の主実装は 1 ファイルに集約し、責務を次に固定する。

### 4-1. コア責務

1. v1 metadata / splits を読み込み、real canonical table を作る  
2. 固定 MLX モデルをダウンロードし、active model manifest を保存する  
3. family ごとの rule spec / generator readiness を判定する  
4. synth / distill / correction / format pair を構築する  
5. Stage A / Stage B の train pack を作る  
6. training manifest を出力する  
7. Mac-first adapter training run を実行、または packaging-target manifest を render する  
8. adapter packaging / PEFT smoke を行う  
9. v1 evaluator で candidate を評価するための runbook を出す  

### 4-2. 想定 subcommand

実装時点で最低限必要な CLI は次。

- `download-model`
- `show-active-model`
- `smoke-model`
- `build-real-canonical`
- `build-solver-registry`
- `build-synth-core`
- `build-synth-hard`
- `build-format-pairs`
- `build-distill-candidates`
- `filter-distilled-traces`
- `build-correction-pairs`
- `build-train-mix`
- `train-sft`
- `package-peft`
- `write-runbook`

この順序自体が、そのまま実装順になる。

## 5. real canonical data layer を固定する

v2 の最初の中心成果物は `train_real_canonical_v2.parquet` である。  
これは `versions/v1/data/processed/train_metadata_v1.parquet` と `train_splits_v1.parquet` を継承し、**学習用 canonical schema** を追加したものにする。

### 5-1. 入力

- `versions/v1/data/processed/train_metadata_v1.parquet`
- `versions/v1/data/processed/train_splits_v1.parquet`
- `data/train.csv`

### 5-2. 出力行スキーマ

既存の v1 列を残したうえで、少なくとも以下を追加する。

- `source_kind`: 常に `real`
- `answer_canonical`: family-aware に正規化した answer
- `format_policy`: `boxed_final_line` or `final_answer_colon`
- `rule_spec_json`: generator / validator が使う最小 rule spec
- `rule_spec_hash`: rule spec の stable hash
- `template_signature`: near-dup / curriculum 用の coarse signature
- `difficulty_tags`: family ごとの hard tag 群
- `format_risk_flags`: `contains_right_brace`, `contains_backslash`, `contains_backtick`, `boxed_safe` を集約した列
- `generator_ready`: exact / conservative generator の seed に使ってよいか
- `eligible_pools`: `core`, `hard`, `distill`, `format`, `correction` など
- `importance_prior`: v1 hard_score + risk + family prior から作る初期重要度
- `train_sample_weight`: family over-sampling の前段となる基本重み

### 5-3. canonicalization 規則

#### bit_manipulation

- 常に 8 文字の `0/1`
- `0b` prefix 禁止
- 空白禁止
- `answer_canonical` は original gold を trim した 8bit 文字列

#### gravity_constant

- 数値のみ
- comma 禁止
- unit suffix 禁止
- decimal style は v1 の `answer_decimal_style` を継承
- `answer_canonical` は original gold の桁数を保った正規形

#### unit_conversion

- 数値のみ
- 常に小数第 2 位
- comma / suffix 禁止

#### roman_numeral

- uppercase only
- 前後空白なし
- 空白区切り禁止

#### text_decryption

- 単語間は single space
- 前後空白なし
- punctuation の勝手な追加禁止

#### symbol_equation

- gold 以外の空白は追加しない
- `}`, `\`, backtick を含む場合は `format_policy = final_answer_colon`
- safe であれば boxed 可

### 5-4. `format_policy` の決め方

原則:

- `boxed_safe == true` かつ answer が単一行なら `boxed_final_line`
- `boxed_safe == false` なら `final_answer_colon`

ただし symbol family では、`boxed_safe == true` でも高 risk な記号集合なら `final_answer_colon` を許容する。  
この判定は conservative に寄せる。

### 5-5. `importance_prior` の初期式

v2 初期時点では model-based hardness をまだ持たないので、次の prior を作る。

```text
importance_prior
= normalized(hard_score within family)
+ family_bonus(bit/text/symbol)
+ risk_bonus(risk_bin high, boxed unsafe, risky chars)
+ ambiguity_bonus(generator_ready false but parse_ok true)
```

目的は:

- teacher 生成の優先順
- correction の優先順
- curriculum の並び順

であり、これ自体を評価指標にはしない。

## 6. solver / generator / validator を family ごとに固定する

v2 のデータ工場は、family ごとの rule space を明示的に持たなければならない。  
ただし **全 row に無理やり rule spec を付けるのは禁止**。  
exact に説明できない row は `generator_ready = false` として残し、real-only で使う。

### 6-1. 共通原則

Rule 1: solver / validator が説明できない synthetic は reject  
Rule 2: ambiguous fit を guess しない  
Rule 3: `text` / `symbol` は teacher-only に逃げない  
Rule 4: generator 可能 row と real-only row を分離管理する  

### 6-2. Roman generator

最優先で full support にする。

- rule: standard subtractive Roman, range `1-100`
- `rule_spec_json`: `{"family":"roman_numeral","range":"1_100","subtractive":true}`
- hard knobs:
  - `4, 9, 14, 19, 40, 44, 49, 90, 94, 99, 100`
  - decade edge

受け入れ条件:

- examples と query が同一 rule で再現
- answer uppercase Roman
- query range が `1-100`

### 6-3. Gravity generator

full support にする。

- rule: `d = 0.5 * g * t^2`
- `rule_spec_json` に `g`, `decimal_style`, `num_examples`
- hard knobs:
  - `g` edge
  - query `t` edge
  - rounding boundary
  - 1 decimal vs 2 decimal

受け入れ条件:

- 全 example / query が同一 `g` で一致
- answer decimal style が rule spec と整合
- query `t` が train 近傍レンジ

### 6-4. Unit conversion generator

full support にする。

- rule: fixed conversion ratio
- `rule_spec_json` に `ratio`, `decimal_style=2`, `num_examples`
- hard knobs:
  - ratio edge
  - rounding boundary
  - query range edge

受け入れ条件:

- 全 example / query が同一 ratio で一致
- answer は常に小数第 2 位
- unit 名の surface form は元テンプレ近傍

### 6-5. Bit manipulation generator

v2 の難所だが、programmatic support を入れる。  
ただし曖昧な fit を無理に採用しない。

op library:

- NOT
- XOR mask
- AND mask
- OR mask
- left shift
- right shift
- left rotate
- right rotate
- bit reverse
- nibble swap
- parity-conditioned op
- position permutation

生成方針:

- 8bit 固定
- 1〜3 op compose
- examples 7〜10
- query 重複禁止

判定方針:

- examples から rule candidate を探索
- single-fit なら `generator_ready = true`
- multi-fit / unknown は `generator_ready = false`

受け入れ条件:

- candidate rule が 1 つに定まる
- examples と query の両方を exact 再現
- 8bit 長が壊れない

### 6-6. Text decryption generator

ここは **full freeform generator にしない**。  
v2 では closed-vocab + reversible mapping + exact validator に限定する。

対象 rule class:

- substitution
- Caesar / shift
- word permutation
- position-based char mapping
- vowel / consonant swap
- fixed affine-ish mapping

方針:

- answer phrase は real answer vocab 近傍の closed vocab から作る
- 3〜5 語固定
- query / answer 語数一致必須
- reversible でない rule は reject

`generator_ready = true` 条件:

- examples から single reversible mapping が導ける
- query まで同一 mapping で整合
- answer spacing canonical

それ以外の row は real-only に残す。

### 6-7. Symbol / equation generator

最も危険なので、numeric と symbolic を最初から分離する。

- `symbol_equation_numeric`
- `symbol_equation_symbolic`

対象 rule class:

- char permutation
- position select / drop
- symbol mapping
- local rewrite
- digit-symbol hybrid transform
- parity / position-conditioned rewrite

方針:

- query 長 5、answer 長 1〜4 を原則維持
- alphabet は real 近傍へ制限
- risky chars は flag 付きで管理

`generator_ready = true` 条件:

- rule class が 1 つに定まり再現可能
- numeric / symbolic が曖昧でない
- escape-sensitive chars を含む場合も answer を safe に保持可能

それ以外は real-only とする。

## 7. synthetic pool を 4 系統で作る

v2 では synthetic を 1 塊にしない。  
`versions/plan-overview.md` の意図を継承し、次の 4 pool で固定する。

### 7-1. Pool A: Core sibling synth

目的:

- real 近傍の汎化
- 分布崩壊を起こさない補強

作り方:

- `generator_ready = true` の real row を親にする
- family / subfamily / answer type / format policy を保持
- query / examples / boundary conditions だけを近傍変更

初期量:

- まず real の `20〜30%` 相当
- full でも real の `35〜60%` まで

### 7-2. Pool B: Hard synth

目的:

- rounding
- boundary
- risky chars
- ambiguity 近傍

family 別重点:

- bit
- text
- symbol

軽く足す family:

- gravity
- unit
- roman

初期量:

- total mix の `5〜10%` まで
- v2 初回は `real_val` を見ながら後段注入

### 7-3. Pool C: Format synth

目的:

- extraction fail を学習で減らす
- same answer / cleaner format を教える

内容:

- boxed safe case の clean boxed
- unsafe case の clean `Final answer: ...`
- extra trailing numbers を出さない版
- boxed multiple を避ける版

重要:

ここで作るのは **新ラベル** ではなく、既知 answer に対する output style data である。

### 7-4. Pool D: Distilled traces

目的:

- base model の reasoning prior を壊さず、短く clean な target を与える

teacher 生成候補:

- long reasoning
- short reasoning
- answer-only
- format-safe

採用基準:

- v1 extractor で gold と一致
- format bucket が clean
- trailing numbers なし
- unsafe answer で malformed boxed なし

### 7-5. v2 での初期 volume cap

最初から大量投入しない。  
v2 では以下を上限の初期値にする。

- Core sibling: real の `0.25x`
- Hard synth: real の `0.05x`
- Format synth: real の `0.03x`
- Distilled traces: real の `0.20x` 相当の採用 target

pilot で real-only validation を悪化させなければ、次段で次へ進む。

- Core sibling: `0.40x`
- Hard synth: `0.10x`
- Distilled traces: `0.30x`

## 8. dedup / acceptance gate を厳密に固定する

v2 では synthetic の質保証を row 単位で持つ。

### 8-1. exact reject

最低限、次は reject。

- `prompt` 完全一致
- `prompt + answer` 完全一致
- 同一 `rule_spec_hash` + 同一 query
- visible `test.csv` と完全一致

### 8-2. near-dup reject

family ごとに normalized form を作り、閾値を固定する。

- Core sibling: `similarity >= 0.92` は reject
- Hard synth: `similarity >= 0.88` は reject 候補

### 8-3. row acceptance gates

全 synthetic / distilled row について、少なくとも次を持つ。

- `rule_consistency_pass`
- `format_validity_pass`
- `length_validity_pass`
- `template_validity_pass`
- `exact_dedup_pass`
- `near_dedup_pass`
- `accepted_by`
- `rejected_reason`

### 8-4. `synthetic_registry_v2.parquet` の必須列

- `synthetic_id`
- `parent_real_id`
- `template_family`
- `template_subfamily`
- `prompt`
- `answer`
- `answer_type`
- `format_policy`
- `generator_type`
- `generator_version`
- `rule_spec_json`
- `rule_spec_hash`
- `difficulty_tags`
- `format_risk_flags`
- `seed`
- `dedup_hash`
- `split_policy`
- `accepted_by`
- `rejected_reason`

`split_policy` は v2 では常に `train_only` に固定する。

## 9. teacher-distilled / correction / format pair を固定する

### 9-1. distilled trace の target style

v2 では target style を次で固定する。

- `long`
- `short`
- `answer_only`
- `format_safe`

ただし v2 の本命は `short` と `format_safe` であり、`long` は薄く保つ。

### 9-2. teacher 生成数

初回 full pass では欲張りすぎない。  
prompt ごとに次を上限にする。

- long: 1〜2
- short: 1〜2
- answer-only: 1〜2
- format-safe: 1

全採用ではなく、filter 後の accepted rows だけを残す。

ただし `bit`, `text`, `symbol` の hard row だけは別枠で、candidate generation を厚くしてよい。

- self-consistency buffer: `N=8〜32`
- 全保存ではなく registry には selection 用要約と accepted trace だけを残す
- 一時的な raw candidate cache はメモリ 512GB を前提にしてよい

### 9-3. `teacher_trace_registry_v2.parquet` の必須列

- `trace_id`
- `source_id`
- `source_kind`
- `family`
- `answer_type`
- `target_style`
- `teacher_name`
- `teacher_seed`
- `raw_output`
- `extracted_answer`
- `is_correct`
- `format_bucket`
- `format_pass`
- `trace_len_chars`
- `trace_len_tokens_est`
- `consensus_rate`
- `selected_for_training`
- `selection_reason`

### 9-4. correction pair

`correction_pairs_v2.parquet` は current student の誤答を材料に作る。

形式:

- `prompt`
- `rejected_output`
- `chosen_output`
- `error_family_tag`
- `error_subtype`
- `source_eval_run`

error subtype 例:

- bit: shift / rotate confusion
- gravity: rounding miss
- unit: inverse ratio
- roman: subtractive miss
- text: partial decode
- symbol: brace / position shift / mixed-char confusion

### 9-5. format pair

`format_pairs_v2.parquet` は **同じ answer で bad format vs good format** を持つ。

chosen:

- clean boxed
- clean `Final answer: ...`

rejected:

- multiple boxed
- trailing numbers
- malformed boxed
- unsafe answer を boxed に入れたもの

この pair builder は v2 に入れる。  
実際の DPO 実験は v3 以降でもよいが、pair の生成は v2 で固定する。

## 10. Stage A / Stage B の train mix を固定する

v2 では **学習 pack の構成比** を deterministic に固定する。  
これがないと、後続の「何が効いたか」が崩れる。

### 10-1. Stage A: Generalist SFT

目的:

- family 全体の底上げ
- 分布を壊さない強化

初期 mix:

- real: `50%`
- sibling synth: `25%`
- distilled traces: `15%`
- hard synth: `5%`
- format synth: `5%`

style mix:

- long: `20%`
- short: `45%`
- answer-only: `20%`
- format-safe: `15%`

### 10-2. Stage B: Hardening SFT

目的:

- hard case
- format fail
- risky family

初期 mix:

- real: `40%`
- sibling synth: `20%`
- distilled traces: `15%`
- hard synth: `10%`
- format synth: `5%`
- correction pairs 起源 chosen outputs: `10%`

style mix:

- long: `10%`
- short: `50%`
- answer-only: `25%`
- format-safe: `15%`

### 10-3. family over-sampling 初期値

Stage A / B の両方で、初期重みを次で始める。

- bit: `1.3x`
- gravity: `0.9x`
- unit: `0.8x`
- text: `1.4x`
- roman: `0.6x`
- symbol: `1.6x`

これは固定ではなく、v1 evaluator の family metrics を見て更新可能にする。  
ただし更新履歴は必ず registry に残す。

### 10-4. `train_mix_registry_v2.parquet` の必須列

- `mix_name`
- `stage`
- `source_dataset`
- `row_id`
- `family`
- `answer_type`
- `target_style`
- `sample_weight`
- `family_weight`
- `format_policy`
- `included_by`

## 11. 学習 recipe は Mac-first に固定する

v2 の primary execution stack は、**Mac 固定・512GB RAM 前提の Mac-first stack** に固定する。  
submission target は引き続き PEFT 互換 LoRA だが、daily iteration の主戦場は Mac である。

したがって v2 では、学習基盤を次の 2 層で管理する。

1. local execution layer  
   - Mac 上で実行する data build / teacher generation / candidate sampling / evaluation / adapter training
2. submission packaging layer  
   - 最終的に必要な `adapter_config.json` / `adapter_model.safetensors` / rank 制約 / load smoke

理由:

- 実行環境が Mac 固定である
- `versions/plan-overview.md` も Mac Studio を主戦場に置いている
- 512GB RAM があるので、生成・蒸留・比較の反復を大量に回せる
- CUDA 依存を前提にすると、日常運用と最終採用判断が乖離する

### 11-1. local primary workload

ローカルで毎日回す対象は次に固定する。

- 既定モデル `lmstudio-community/NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-6bit` の利用
- teacher inference
- `N=8〜32` self-consistency sampling
- synthetic / distilled / correction / format data build
- adapter merge / compression
- v1 evaluator による quick / serious gate
- packaging smoke
- 可能なら Mac 上での adapter training

### 11-1-1. 固定モデル ID

今後のローカル MLX 実験の既定モデルは、次で固定する。

- `lmstudio-community/NVIDIA-Nemotron-3-Nano-30B-A3B-MLX-6bit`

このモデルは `versions/v2/outputs/models/` 配下へ保存し、active pointer は `versions/v2/outputs/runtime/active_model.json` に保持する。

### 11-2. submission target schema は引き続き PEFT

ローカル runtime が Mac-first でも、提出物の target schema は変えない。

- `adapter_config.json`
- `adapter_model.safetensors`
- `base_model_name_or_path`
- rank `<= 32`
- target modules 一致

つまり v2 の設計思想は、

- **実行は Mac-first**
- **提出形式は PEFT-first**

の二層管理である。

### 11-3. baseline target modules

最初に固定する target modules:

- `q_proj`
- `k_proj`
- `v_proj`
- `o_proj`
- `gate_proj`
- `up_proj`
- `down_proj`

### 11-4. 最初に切る LoRA 比較

v2 の P0 でまず比較するのは次。

- A: `r=32`, `alpha=32`, `dropout=0.0`
- B: `r=32`, `alpha=64`, `dropout=0.0`
- C: `r=32`, `alpha=32`, `dropout=0.05`
- D: `r=16`, `alpha=32`, `dropout=0.05`

優先順は A → B → C → D。

### 11-5. local training objective / loss

初期固定:

- completion-only loss
- final-span weighted / unweighted の両比較
- rank target `32`
- `alpha = 32 or 64`
- `dropout = 0.0 or 0.05`
- Stage A / Stage B の 2 段

quantization や optimizer の詳細は、**Mac で実際に採る runtime に合わせて manifest 化**する。  
v2 では BitsAndBytes 固定にはしない。

### 11-6. sequence length

初期値:

- default: `max_seq_len = 1024`
- long trace sweep のみ `1536`

prompt 自体は短いので、長尺を常用しない。

### 11-7. Mac 512GB を使う場所

RAM 512GB を活かして、v2 では次を積極的に回す。

- hard family の large candidate buffer
- 複数 teacher process の並列
- raw generation cache の一時メモリ保持
- registry のメモリ常駐 join / filter / scoring
- quantized teacher 複数本の併走比較

ただし、増やす優先順は **model size より candidate quality / validation throughput** とする。

### 11-8. 初期学習率と段数

初期値:

- Stage A lr: `1e-4` or `8e-5`
- Stage B lr: `5e-5`
- warmup: `3%`
- epochs:
  - Stage A: `1.5〜3`
  - Stage B: `0.5〜1.5`

packing は有効化候補だが、final-span weighting との整合 test を通ってから使う。

## 12. final-span / final-line weighting を v2 で入れる

このコンペでは、assistant 全体を均等 loss にすると最後の答えが弱くなりやすい。  
v2 では weighted loss を **比較可能な形** で入れる。

### 12-1. 重みの基本形

- rationale tokens: `1.0`
- final answer prefix: `2.0`
- final line tokens: `3.0`
- final answer span:
  - gravity / unit / roman: `4.0`
  - bit: `5.0`
  - symbol risky: `6.0`
  - text: `3.0`

### 12-2. 実装方針

1. user prompt 部分には loss をかけない  
2. assistant 出力だけに base loss をかける  
3. assistant 内で final line と final answer span に追加 weight をかける  

### 12-3. v2 で必ず比較する 2 系統

- unweighted baseline
- weighted final-span baseline

ここを曖昧にせず、`sft_stage_a_r32_alpha32.yaml` と `sft_stage_a_r32_alpha32_weighted.yaml` を別 manifest にする。

## 13. format policy を学習対象として固定する

### 13-1. safe / unsafe を分ける

safe:

- numeric
- binary8
- Roman
- clean text phrase
- brace を含まない symbolic

unsafe:

- `}` を含む
- `\` を含む
- multiple line になりうる
- boxed regex が壊れやすい symbolic

### 13-2. target rendering 規則

safe answer:

```text
\boxed{ANSWER}
```

unsafe answer:

```text
Final answer: ANSWER
```

重要:

- final answer の後は EOS
- 追加の数字禁止
- 追加説明禁止
- boxed は 1 回だけ

### 13-3. v2 で作る target style

real row の fallback target:

- `answer_only` + family-aware `format_policy`

teacher row の target:

- `long`
- `short`
- `format_safe`

format synth row:

- same answer で cleaner output だけを学習

## 14. PEFT packaging gate を v2 で固定する

v2 の baseline は、学習が通っても packaging が壊れていたら不合格にする。

### 14-1. 必須確認

- `adapter_config.json` がある
- `adapter_model.safetensors` がある
- `base_model_name_or_path` が Nemotron base と一致
- target modules 名が model と一致
- `PeftModel.from_pretrained()` で load 可能
- zip 化後の submission structure が正しい

### 14-2. `peft_smoke.yaml` に入れる内容

- base model path
- expected target modules
- expected rank cap (`<= 32`)
- required files list
- smoke prompt path

### 14-3. packaging outputs

- `outputs/packaging/peft_smoke_result.json`
- `outputs/packaging/submission_manifest.json`
- `outputs/reports/training_command_book_v2.txt`

## 15. v1 evaluator を使った promotion rule を固定する

v2 の候補採用は、すべて v1 evaluator で判定する。  
training loss だけで昇格させない。

### 15-1. quick daily gate

毎日比較する最小セット:

- `shadow_128` + `official_lb`
- `shadow_128` + `sc_probe_k8`

### 15-2. serious gate

昇格候補で必ず回す:

- `shadow_256` + `official_lb`
- `hard_shadow_256` + `official_lb`

### 15-3. weekly / pre-submit gate

週次または submit 前に回す:

- `holdout_hard` + `official_lb`
- `group_shift_split0/1/2` + `official_lb`

### 15-4. 採用指標

必須で見るもの:

- overall accuracy
- family accuracy
- extraction fail rate
- format fail rate
- probe majority / pass@k

### 15-5. weighted offline score

daily score:

```text
0.50 * shadow_256_acc
+ 0.30 * hard_shadow_256_acc
+ 0.20 * probe_shadow128_k8_majority_acc
```

weekly score:

```text
0.35 * shadow_256_acc
+ 0.25 * holdout_hard_acc
+ 0.20 * mean(group_shift_acc)
+ 0.10 * hard_shadow_256_acc
+ 0.10 * probe_shadow128_k8_majority_acc
```

### 15-6. promotion gate

candidate 昇格条件:

1. daily score が current best 以上  
2. `hard_shadow_256` が non-negative  
3. extraction fail rate が悪化しない  
4. family のいずれか 1 つで大崩れしない  

submit 候補条件:

1. weekly score が `+0.003` 以上改善、または hard split が `+0.005` 以上改善  
2. `text` / `symbol` / `bit` のいずれかで改善が明確  
3. packaging smoke pass  
4. raw output audit が clean  

## 16. 実装順序を固定する

v2 は広いので、実装順を固定する。  
この順番を崩さない。

### Step 1. v2 bootstrap

やること:

- `versions/v2/` の土台作成
- `train.py` の CLI 骨格
- config / output path 定数

完了条件:

- `python versions/v2/code/train.py --help` が動く
- v2 ディレクトリ群が作れる

### Step 2. real canonical builder

やること:

- v1 metadata / splits 読み込み
- canonical columns 追加
- `train_real_canonical_v2.parquet` 出力

完了条件:

- 9500 行維持
- family counts 不変
- required canonical columns あり
- public overlap flag 維持

### Step 3. solver registry

やること:

- Roman / gravity / unit full support
- bit exact-fit solver
- text / symbol conservative validator
- `solver_registry_v2.json` 出力

完了条件:

- family ごとの rule class が registry 化
- unsupported row が silent fallback されない
- `generator_ready` 列が埋まる

### Step 4. synth core / hard builders

やること:

- sibling synth
- hard synth
- synthetic registry
- near-dup / exact-dedup gate

完了条件:

- exact dup 0
- near-dup threshold 守る
- accepted / rejected reason が残る

### Step 5. distilled / format / correction builders

やること:

- teacher candidate 受け入れ
- distilled trace filter
- format pair builder
- correction pair builder

完了条件:

- accepted trace は全件 gold と一致
- clean format のみ selected
- unsafe answer が boxed に残らない

### Step 6. Stage A / B mix builder

やること:

- mix ratios 固定
- style mix 固定
- family weights 固定
- train packs 出力

完了条件:

- pack composition が config 通り
- source provenance が追える
- `train_mix_registry_v2.parquet` 出力

### Step 7. training manifests と weighted loss

やること:

- Mac-first training config
- weighted / unweighted 比較
- packaging-target manifest

完了条件:

- Stage A / Stage B manifest 出力
- weighted loss spec test pass

### Step 8. packaging gate / promotion rule / runbook

やること:

- PEFT smoke
- candidate registry
- promotion rule text
- command book

完了条件:

- packaging smoke spec が固定
- evaluation handoff が定義される

## 17. 最初に回すべき P0 実験を固定する

v2 は基盤版だが、基盤が機能するか確認するための P0 実験列を同時に持つ。

### P0

1. real-only Mac-first adapter baseline `r32 alpha32 dropout0.0`
2. 1 + final-span weighted loss
3. 2 + core sibling synth
4. 3 + distilled short traces
5. 4 + hard synth
6. 5 + format synth
7. 6 + correction chosen outputs
8. 7 の packaging smoke
9. 8 の `shadow_256` / `hard_shadow_256` 比較
10. best two の weekly gate 比較

### P1

1. `alpha32` vs `alpha64`
2. `dropout0.0` vs `0.05`
3. weighted loss on/off
4. Stage B correction 量 sweep
5. safe / unsafe format policy 強化

### P2

v2 の範囲外に近いが、将来接続のため metadata だけ準備する。

- DPO on format pairs
- DPO on correction pairs
- RFT from accepted trace pool
- specialist merge

## 18. v2 でやらないこと

範囲を守るため、次は v2 の primary deliverable から外す。

- true RL / GRPO 本体
- multi-adapter merge の最適化本体
- external broad reasoning corpus の大量投入
- v1 evaluator の再設計
- visible `test.csv` の validation 利用
- unsupported family に対する guess-based synthetic

## 19. v2 のテストと検証

### 19-1. 必須 test

- real canonical schema regression
- solver / generator acceptance
- dedup / registry integrity
- mix builder composition
- weighted loss span detection
- packaging spec

### 19-2. 実行コマンド

```bash
python -m py_compile versions/v2/code/train.py
pytest -q versions/v2/tests
pytest -q
```

### 19-3. CLI smoke

```bash
python versions/v2/code/train.py build-real-canonical \
  --metadata versions/v1/data/processed/train_metadata_v1.parquet \
  --splits versions/v1/data/processed/train_splits_v1.parquet \
  --output versions/v2/data/processed/train_real_canonical_v2.parquet

python versions/v2/code/train.py build-synth-core \
  --config versions/v2/conf/data/synth_core.yaml \
  --input versions/v2/data/processed/train_real_canonical_v2.parquet \
  --output versions/v2/data/synth/synth_core_v2.parquet

python versions/v2/code/train.py build-train-mix \
  --config versions/v2/conf/data/mix_stage_a.yaml \
  --real versions/v2/data/processed/train_real_canonical_v2.parquet \
  --core versions/v2/data/synth/synth_core_v2.parquet \
  --distill versions/v2/data/synth/distilled_traces_v2.parquet \
  --hard versions/v2/data/synth/synth_hard_v2.parquet \
  --format versions/v2/data/synth/synth_format_v2.parquet \
  --output versions/v2/data/train_packs/stage_a_mix_v2.parquet
```

## 20. 最終的な v2 本命レシピ

現時点で v2 の最も堅い一本は次。

### Data

- real canonical
- core sibling synth
- distilled short traces
- format synth
- hard synth 少量

### Training

- Mac-first local runtime
- PEFT-target packaging
- all-linear
- `r=32`
- `alpha=32`
- `dropout=0.0`
- Stage A generalist SFT
- Stage B hardening SFT
- weighted final-span loss

### Evaluation

- v1 `official_lb` quick / serious / weekly gate
- family metrics を必ず確認
- packaging smoke pass 必須

### 判断

最終的に v2 は、**「LoRA を 1 本作る版」ではなく、「以後の全 version が同じデータ・学習・採用基準で比較できる版」** として完成させる。

そのため、最重要な成功条件は

- synthetic が壊れていない
- training mix が追跡可能
- final answer policy が明示されている
- v1 evaluator で採用判定できる
- PEFT packaging が壊れない

の 5 点である。
