# Experiment Portfolio Overview

2026-03-31 再構成版。  
この文書は `README.md` を最優先の契約とし、`baseline/binary_program_induction_and_specialist_adapter.md` とその周辺結果、および現行 `v5` の Transformers 本線を踏まえて、**有益そうな大型実験だけ**を残した全体計画である。

この文書の役割は、`baseline/binary_program_induction_and_specialist_adapter.md` の続編ではない。  
**次に試すべき大きい実験方針を複数並べ、Kaggle 実測で選別するためのポートフォリオ**である。

---

## 0. 固定前提

### 0-1. 評価契約

`README.md` の Evaluation / Submitting を絶対基準にする。

- Nemotron-3-Nano-30B に LoRA adapter をロードして評価
- `adapter_config.json` を含む `submission.zip` が必要
- 推論は `vLLM`
- `\boxed{}` 優先抽出
- `max_lora_rank = 32`
- `max_tokens = 7680`
- `top_p = 1.0`
- `temperature = 0.0`
- `max_num_seqs = 64`
- `gpu_memory_utilization = 0.85`
- `max_model_len = 8192`

### 0-2. 実行基盤

- 提出互換の本線は `versions/v5/code/train_transformers_submission_v5.py`
- `versions/v2/v2-results.md` を追加し、最後に残っていた historical version-local ledger gap を埋めた。現 snapshot では `versions/v2/outputs/` と実測 score artifact が無いことを明示している
- `versions/v5/`, `versions/v5-1/`, `versions/v6/`, `versions/v7/` には Git-visible な `*-results.md` ledger を追加済みで、現 snapshot ではまだ version-local outputs / 実測 score artifact が無いことを明示している
- `versions/archive/v1/`, `versions/archive/v4/`, `versions/archive/v7/`, `versions/archive/v8/` にも archive-local `*-results.md` ledger を追加し、historical snapshot 側で measured-score artifact が無いこと、active canonical ledger が別にあるかどうか、`archive/v4/submission.zip` のような snapshot-only artifact の扱いを Git-visible にした
- `archive/v1`, `archive/v4`, `archive/v7` の results ledger では、archive code が保持している version-suffixed packaged-archive names (`submission_v1.zip`, `submission_v4.zip`, `submission_v7.zip`) は historical snapshot-local naming であり、active README contract ではないことも注記している
- `versions/v5/code/train_transformers_submission_v5.py` とその late variants (`v5-1`, `v6`, `v7`) は、CLI entry で live `README.md` evaluation table を再読込して contract drift / missing row / malformed value を即 fail するように harden 済み
- その README runtime guard は `versions/v5/tests/test_readme_contract_sync.py` で cross-version に固定しており、happy path / missing row / empty value / malformed value / value drift を 1 本で回帰化している
- `versions/v4/code/train_official_first_best_v4_minimal.py` と `versions/v4/code/train_best_notebook_sft_v4_minimal.py` も CLI entry で live `README.md` evaluation table を再読込して contract drift / missing row / malformed value を即 fail するように harden 済み
- その v4 minimal README runtime guard は `versions/v4/tests/test_v4_minimal_readme_contract.py` で固定しており、artifact 側の `readme_eval_contract` / `readme_contract_verified_from_readme_file` surfacing も 1 本で回帰化している
- `versions/v1/code/train.py` の `official_lb` loader も live `README.md` evaluation table を再読込して、official evaluator config 自体の drift / missing row / malformed value を即 fail するように harden 済み
- その evaluator-side README runtime guard は `versions/v1/tests/test_eval_readme_contract.py` で固定しており、official-only enforcement と non-official bypass の両方を回帰化している
- `versions/v0/code/train.py` の `official_lb` loader も同じ README runtime guard を持ち、historical evaluator line 側でも drift / missing row / malformed value を即 fail するように harden 済み
- その v0 evaluator-side README runtime guard は `versions/v0/tests/test_eval_readme_contract.py` で固定しており、official-only enforcement と non-official bypass の両方を回帰化している
- ベースモデルは `models/nemotron-3-nano-30b-a3b-bf16`
- MLX は本線から外す

### 0-3. 評価運用

- **ローカル Mac/MPS**: family ごとの `1-2` case micro smoke のみ
- **本格評価**: ユーザーの Kaggle / Blackwell 環境で `baseline/cot/phase0_offline_eval` を使う

つまり、今後の判断は

1. local micro smoke  
2. Kaggle `phase0_offline_eval`  
3. family breakdown 分析  

の順で行う。

---

## 1. 既存結果から見える確定事項

### 1-1. いま強い family と弱い family

`baseline/cot/phase0_offline_eval/result/0` と `result/1` を見ると、改善後でも構図は大きく変わっていない。

- `roman`: `1.0000` → `0.9800`
- `unit`: `0.9800` → `0.9600`
- `gravity`: `0.8600` → `0.9200`
- `text`: `0.7400` → `0.9000`
- `binary`: `0.1833` → `0.2000`
- `symbol`: `0.4333` → `0.4167`

結論:

- **roman / unit / gravity は維持対象**
- **text は改善済みなので壊さないことが重要**
- **binary と symbol が主戦場**

### 1-2. hard slice は binary と symbol の中にも偏っている

`phase0_eval_summary.md` から、特に厳しい slice は次。

- `bit_structured_byte_formula`
  - `0.0714` → `0.1429`
- `glyph_len5`
  - `0.0000` → `0.0000`

一方で symbol 全体が悪いわけではなく、

- `numeric_2x2`: `0.6500` → `0.6250`
- `glyph_len5`: `0.0000` 継続

したがって symbol は一枚岩ではない。  
**`numeric_2x2` と `glyph_len5` を分けて扱う必要がある。**

### 1-3. verified rows は価値が高く、manual rows はそのままでは危険

`phase0_eval_summary.md` の selection tier 集計では、

- `verified_trace_ready`: `0.8553` → `0.8979`
- `answer_only_keep`: `0.4000` → `0.3714`
- `manual_audit_priority`: `0.0200` → `0.0200`

結論:

- **verified を主軸にするのは正しい**
- **answer_only は final answer / format 補強用として使う**
- **manual を raw CoT 教師として雑に入れるのは危険**

### 1-4. binary のボトルネックは reasoning だけではなく format collapse

`baseline/cot/rule_based_adapter_readme_inference_samples_rule_base-600_analysis.md` では、失点の大半が binary で、`1`, `001`, `-0`, `10` のような崩れた抽出が多い。

また `phase0_eval_summary.md` の binary metrics では、

- `boxed_extraction_success_rate`: `0.2167`
- `regex_exact_rate`: `0.25`
- `leading_zero_retention_rate`: `0.2333`
- `format_failure_rate`: `0.7833`

結論:

- binary は「解けていない」だけでなく **最後の 1 行で落としている**
- **final answer closure** は大きい改善余地

### 1-5. binary は program induction として扱うべき

`baseline/binary_bit_manipulation_difficulty_report_2026-03-29.md` と `baseline/binary_program_induction_and_specialist_adapter.md` が示す通り、binary は few-shot の rule induction / program induction に近い。

特に重要なのは次。

- curated total はあるが trace-safe teacher は限定的
- unresolved cluster は easy rule の取りこぼしではなく構造的難問群
- 8-bit exact + leading zero + boxed closure まで必要

結論:

- binary を自然文 CoT の延長で厚塗りするより、
- **DSL scratchpad / executable-style trace / boxed-only answer-only**
  が筋が良い

### 1-6. すでに有望な “前段素材” は repo にある

`baseline/cot/phase1_assistant_only/artifacts/phase1_assistant_only_manifest.json` と `baseline/cot/phase2_binary_dsl/artifacts/phase2_binary_dsl_manifest.json` から、すでに次の方向は試す価値が高い。

- assistant-only loss
- verified / answer-only の役割分離
- binary answer-only の boxed-only 化
- binary verified trace の DSL 化
- final answer を `<think>` 内で再掲しない設計

つまり、完全な白紙ではない。  
**次はこれらを Transformers 本線の大型実験として再構成する段階**である。

---

## 2. 今回残す設計原則

### 原則1: binary-first, symbol-aware

最大ボトルネックは binary。  
ただし `glyph_len5 = 0.0` を放置して 0.9 へ行く計画は危険。

### 原則2: plumbing before sophistication

先にやるべきは

- assistant-only loss
- template 整合
- final answer 重視
- curated mix
- binary DSL

であり、merge や RL はその後。

### 原則3: large-bet only

以後は

- `lr`
- `rank`
- `max_length`
- 小さな target module 差分

のような local micro sweep を主戦略にしない。  
大きな実験軸だけを回す。

### 原則4: Kaggle report driven

採否は local loss や local full eval ではなく、

- local family micro smoke
- Kaggle `phase0_offline_eval`
- row-level / family-level report

で決める。

### 原則5: strong family は “伸ばす” より “維持する”

roman / unit / gravity / text は、今は主投資先ではない。  
これらは **anchor family** として扱い、binary/symbol 改善の副作用監視に使う。

---

## 3. 残す大型実験ポートフォリオ

以下の 6 本だけを今後の本命として残す。

### Track A. Plumbing-Hardened Generalist

**狙い**  
現行 generalist を、binary/symbol へ入る前に「壊れにくい LoRA」に作り直す。

**中身**

- assistant-only loss
- train / infer template 整合
- verified / answer_only の役割分離
- final answer / last line を重視した学習
- boxed closure を壊しにくい短め出力設計

**根拠**

- `phase1_assistant_only_manifest.json` はこの方向の妥当性を already 示している
- binary の format collapse は plumbing 側の寄与が大きい
- manual rows を入れなくても verified rows の質が高い

**成功条件**

- strong family を壊さず
- binary format metrics が改善
- Kaggle phase0 で `overall` と `binary` の両方が上向く

**備考**

この track は今後の全 experiment の土台。  
ここで細かい hyperparameter sweep はしない。**1-2 本の強い generalist recipe に絞る。**

---

### Track B. Binary Program-Induction Redesign

**狙い**  
binary を natural-language CoT ではなく program induction task として学習させる。

**中身**

- verified binary rows を DSL scratchpad 化
- binary answer-only rows は boxed-only 維持
- `<think>` 内で final 8-bit answer を再掲しない
- affine / permutation だけでなく
  - `bit_structured_byte_formula`
  - blank `teacher_solver_candidate`
  - unresolved hard slice
  を主対象にする

**根拠**

- binary metrics の主失点は format collapse
- `bit_structured_byte_formula` が極端に弱い
- `binary_program_induction_and_specialist_adapter.md` の Phase 2 は repo 内証拠と整合
- `phase2_binary_dsl_manifest.json` に具体的な dataset 形がある

**成功条件**

- binary `regex_exact_rate`
- `leading_zero_retention_rate`
- `boxed_extraction_success_rate`
- `bit_structured_byte_formula` accuracy

が Kaggle phase0 で改善すること。

---

### Track C. Symbol Hardening, Especially `glyph_len5`

**狙い**  
symbol family を一括で扱わず、`numeric_2x2` と `glyph_len5` を分離し、特に `glyph_len5` の catastrophic failure を止める。

**中身**

- symbol data を subtype 別に再編成
- `glyph_len5` 専用の answer formatting / target design
- risky char を含む output の扱いを明示
- `numeric_2x2` は retention 寄り、`glyph_len5` は repair 寄り

**根拠**

- symbol overall は約 `0.4` だが、その内訳は非対称
- `numeric_2x2` はまだ戦える
- `glyph_len5` は `0.0`

**成功条件**

- `glyph_len5` が 0 から脱出
- `numeric_2x2` を落としすぎない
- binary 改善との干渉が小さい

**備考**

この track は binary の次点。  
binary-only で進めると 0.9 到達前に詰まる可能性が高い。

---

### Track D. Family-Preserving Synthetic Expansion

**狙い**  
256-512 row の local training 制約を超えるため、task-near な synthetic で大きく分布を広げる。

**中身**

- real の sibling synth を主軸にする
- solver / verifier がある family だけ厚く作る
- 主対象:
  - binary hard / structured byte
  - symbol `glyph_len5`
  - text monoalphabetic の hard slice
- easy bulk synth は作らない

**根拠**

- old plan の「family-preserving sibling synth」は有望
- binary manual rows をそのまま教師化するより安全
- broad generic synthetic より distribution-safe

**成功条件**

- Kaggle phase0 の hard slice が改善
- strong family retention
- side effect が小さい

**備考**

この track は Track A/B/C のどれかが効いた後に乗せる。  
**最初から synth 主体にはしない。**

---

### Track E. Specialist Adapters + Merge

**狙い**  
general family retention と binary/symbol hardening を 1 本の adapter に無理やり同居させず、役割分担して最後に統合する。

**中身**

- General adapter
- Binary specialist
- 必要なら Symbol specialist
- merge は
  - linear
  - SVD
  - TIES / DARE
  の大枠だけ比較

**根拠**

- `binary_program_induction_and_specialist_adapter.md` の Phase 3 は妥当
- binary/symbol の objective は strong family 維持と衝突しやすい
- merge は “後段の大型実験” として意味がある

**成功条件**

- binary or symbol gain
- gravity / roman / unit / text retention
- merged adapter が source adapter を上回る

**備考**

これは本命だが **Track A/B/C の standalone value が見えてから** 行う。  
merge weight の微調整自体を主戦略にしない。

---

### Track F. Error-Driven RFT / Preference

**狙い**  
Kaggle row-level failure を使って、実際の失敗分布に合わせた correction / preference 学習を行う。

**中身**

- Kaggle phase0 の raw outputs を回収
- family ごとに failure taxonomy を作る
- chosen / rejected を作る
- まずは RFT / DPO / ORPO 系
- true RL は最後

**主対象**

- binary format collapse
- binary exactness failure
- symbol risky output
- text / numeric の “almost correct but last line で落ちる” ケース

**根拠**

- local MPS では full eval ループが遅すぎる
- user の Kaggle report が今後の最重要信号
- 実際の誤答分布から correction data を作る方が効率的

**成功条件**

- format collapse 減少
- binary / symbol の row-level hard case 改善
- strong family retention

**備考**

RL はここで初めて候補に入る。  
**plumbing と data redesign より先には置かない。**

---

## 4. 今回外すもの

古い `versions/plan-overview.md` から、以下は主計画から外す。

- local full-eval を前提にした反復 loop
- `lr / rank / max_length / dropout` の細かい sweep
- target module の広い探索
- teacher model zoo を前提にした大規模 distillation
- broad generic synthetic の大量投入
- manual rows への raw CoT 付与
- RL を early phase に置く構成

これらは「完全に禁止」ではないが、**今の主ポートフォリオでは優先しない**。

---

## 5. 実験の実行順

### Priority 1

- Track A. Plumbing-Hardened Generalist
- Track B. Binary Program-Induction Redesign

### Priority 2

- Track C. Symbol Hardening

### Priority 3

- Track D. Family-Preserving Synthetic Expansion
- Track E. Specialist Adapters + Merge

### Priority 4

- Track F. Error-Driven RFT / Preference

---

## 6. 実運用ループ

1. 大きな仮説 1 本を選んで学習
2. local family micro smoke を実施
3. pass 候補だけ `submission.zip` を作る
4. ユーザーが Kaggle / Blackwell で `baseline/cot/phase0_offline_eval` を回す
5. 返却レポートを family / subtype / failure mode で分析する
6. 次の large-bet を 1 本か 2 本だけ選ぶ

このループを繰り返す。

---

## 7. 近い将来の採用基準

次候補として残すのは、Kaggle `phase0_offline_eval` で少なくとも次のどれかを満たす run のみ。

1. binary が明確に改善
2. `glyph_len5` が 0 から改善
3. strong family を維持したまま overall が改善
4. row-level で「次の correction / synthetic / merge に繋がる失敗様式」が明確

逆に、次は落とす。

- binary も symbol も改善しない
- text / gravity / unit / roman を壊す
- local だけ良くて Kaggle phase0 で再現しない

---

## 8. 一文まとめ

今後の全体戦略は、

**README 契約を守る single-file Transformers 本線の上で、binary-first / symbol-aware に large-bet を回し、Kaggle `phase0_offline_eval` の family breakdown で選別する**

という形に再構成する。
