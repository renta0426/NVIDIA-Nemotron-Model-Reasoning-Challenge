# MLX 学習済み LoRA を PEFT/vLLM 提出形式へ高忠実度変換するための実行計画

この文書は、**既存の MLX 学習済み LoRA アダプタを、意味を変えずに、README.md の提出契約に合う PEFT/vLLM 形式へ変換する**ための計画に限定する。  
探索、再学習、精度改善、候補選定の一般論は対象外とし、**変換の正確性・互換性・安全性**だけを扱う。

---

## 1. README.md から固定すべき提出契約

`README.md:31-49` から、この変換タスクで絶対に満たすべき契約は次のとおり。

- 提出物は **NVIDIA Nemotron-3-Nano-30B** 向けの **LoRA adapter**
- 評価時は **vLLM inference engine** で LoRA をロードする
- adapter には **`adapter_config.json`** が必要
- 提出形式は **`submission.zip`**
- LoRA の **rank は 32 以下**
- 実評価パラメータは README 記載値を優先する  
  - `max_lora_rank = 32`
  - `max_tokens = 7680`
  - `top_p = 1.0`
  - `temperature = 0.0`
  - `max_num_seqs = 64`
  - `gpu_memory_utilization = 0.85`
  - `max_model_len = 8192`

したがって、変換の完了条件は **「PEFT として読めること」ではなく、「README 契約どおり vLLM evaluator に刺さる提出物になること」**である。

---

## 2. 現在の主対象アダプタ

現時点で exporter の主対象にすべきアダプタは、以下の **80/20 merge**。

- 候補 ID: `v5_merge_run3_run6_80_20`
- adapter path:  
  `versions/v4/outputs/train/merge_run3_run6_80_20/adapter_v5_merge_run3_run6_80_20`

根拠:

- `versions/v4/v4-results.md:196-212`
  - `hard_shadow_256 overall_accuracy = 0.5859375`
  - 現在の **best local hard-gate candidate**
- `versions/v4/data/processed/merge_candidate_registry_v4.csv:5`
  - `status=scored`
  - `quick_score=0.5390625`
  - `serious_score=0.5859375`

このため、**MLX→PEFT/vLLM exporter の最初の正式ターゲットは上記 adapter で固定**する。  
別候補へ話を広げると、変換ロジックの問題と候補選定の問題が混ざるため、当面は避ける。

---

## 3. 現在アーティファクトと README 提出契約の互換ギャップ

既存の smoke/packaging 結果  
`versions/v4/outputs/handoff/peft_smoke_v5_merge_run3_run6_80_20/peft_smoke_result.json`  
から、現物はまだ submission-compatible ではない。

### 確認済みギャップ

- `adapter_config.json` は存在する
- **`adapter_model.safetensors` が存在しない**
- top-level の **`r` が無い**
- `rank_ok = false`
- `base_model_ok = false`
- `submission_zip_ok = false`
- `all_required_files_present = false`
- `peft_load_status = "skipped_no_local_base_model"`

### つまり何が足りないか

README 契約と照らすと、現状の MLX artifact は少なくとも以下が不足または未整合。

1. **PEFT が期待する重みファイル名と構成**
   - MLX 側は `adapters.safetensors`
   - 提出互換側では少なくとも `adapter_model.safetensors` が必要
2. **PEFT/vLLM が直接参照する config フィールド**
   - top-level `r`
   - `lora_alpha`
   - `lora_dropout`
   - `bias`
   - `peft_type`
   - `target_modules`
   - `modules_to_save`
   - `use_dora`
   - `use_rslora`
   - `inference_mode`
3. **ベースモデル識別子の整合**
   - 現在の `base_model_name_or_path` はローカル MLX 6bit パス
   - README 契約上の提出対象は **Nemotron-3-Nano-30B** 向け LoRA
   - evaluator/vLLM で前提となるベース識別子と一致している保証がない
4. **submission.zip として成立する包装**
   - valid zip として最終提出に使える状態ではない

---

## 4. 意味を変えずに変換するために必要な情報

高忠実度変換には、単にファイル名を変えるだけでは不十分。  
**「MLX 側で何を意味していた重みか」を、PEFT/vLLM 側で同じ意味に再現するための情報**が必要。

### 4.1 モジュール対応情報

最低限、各 LoRA 重みについて以下を確定する必要がある。

- MLX 側 module path
- それに対応する PEFT/HF/vLLM 側 module path
- その module が線形層なのか、MoE shared expert なのか、switch expert 群なのか
- その module が README 契約下の vLLM LoRA 実装で対象化可能か

必要な観点:

- `q_proj / k_proj / v_proj / o_proj / gate_proj / up_proj / down_proj` だけでなく、
- 実際の tensor key に出てくる  
  `backbone.layers.*.mixer.shared_experts.*`
- `backbone.layers.*.mixer.switch_mlp.*`

が **どの HF/PEFT module に対応するか** を確定しなければならない。

### 4.2 テンソル意味論

各 tensor について、少なくとも以下を知る必要がある。

- `lora_a` / `lora_b` がどちらが入力側・出力側か
- forward での適用順
- 転置の必要有無
- どの軸が rank か
- どの軸が expert 軸か
- shared expert と switched experts の違い
- PEFT/vLLM 側が想定する LoRA weight layout

### 4.3 MoE / switch expert 軸の意味

今回の主 blocker は、80/20 adapter 内に **3D の expert-wise tensor** が存在すること。

確認済み shape:

- `backbone.layers.36.mixer.shared_experts.down_proj.lora_a = (3712, 32)`
- `backbone.layers.36.mixer.shared_experts.down_proj.lora_b = (32, 2688)`
- `backbone.layers.36.mixer.switch_mlp.fc1.lora_a = (128, 32, 2688)`
- `backbone.layers.36.mixer.switch_mlp.fc1.lora_b = (128, 1856, 32)`
- `backbone.layers.36.mixer.switch_mlp.fc2.lora_a = (128, 32, 1856)`
- `backbone.layers.36.mixer.switch_mlp.fc2.lora_b = (128, 2688, 32)`

ここから分かること:

- shared expert 系は 2D LoRA で見える
- switch expert 系は **expert 数 128 を含む 3D tensor**
- この 3D 軸を **そのまま PEFT 標準 LoRA に写せる保証がない**

したがって、faithful conversion には少なくとも以下の知識が必要。

- `128` が expert index 軸であることの確認
- 各 expert ごとの独立 LoRA とみなすべきか
- 1 つの grouped parameter とみなすべきか
- HF/PEFT/vLLM が Nemotron MoE のこの表現を受理するか
- 受理しない場合、等価な分解表現が存在するか

### 4.4 scaling / alpha の意味

変換時には以下の意味対応が必要。

- MLX の `scale`
- PEFT の `lora_alpha`
- vLLM の scaling 計算
- `use_rslora` の有無

ここが不一致だと、shape が合っても**実質別 adapter**になる。  
意味保存を主張するには、少なくとも

- `rank`
- `scale`
- `dropout`
- `use_rslora`
- `bias`

の意味を確定して、変換先 config に明示的に反映する必要がある。

### 4.5 metadata / packaging 情報

faithful conversion に必要なメタデータ:

- base model identity
- adapter 作成時の fine-tune type
- target module 一覧
- rank / dropout / scale
- モジュールごとの shape registry
- MoE expert 軸の表現ルール
- 元 adapter と変換後 adapter の対応 manifest

---

## 5. exporter 実装に必要な具体的構成要素

実装は 1 ファイルにまとめる前提で、最低限以下が必要。

### 5.1 入力検査

- MLX adapter directory を受け取る
- `adapter_config.json` の存在確認
- `adapters.safetensors` の存在確認
- `fine_tune_type == "lora"` の確認
- rank が 32 以下か確認
- target_modules が空でないことを確認

### 5.2 MLX config 読み取りと正規化

MLX config から少なくとも以下を抽出して正規化する。

- `base_model_name_or_path`
- `fine_tune_type`
- `lora_parameters.rank`
- `lora_parameters.scale`
- `lora_parameters.dropout`
- `target_modules`

必要なら追加で保持:

- `num_layers`
- `merge_sources`
- `merge_weights`
- 親 adapter 情報

### 5.3 state_dict 走査と module mapping

重みキーを全走査し、各 key について:

- MLX key を分解
- 対応する PEFT key を決定
- 2D LoRA か 3D expert-wise LoRA か分類
- 非対応 key を検出して停止または隔離

### 5.4 tensor layout 変換

2D tensor について必要なら:

- `lora_a` → `lora_A.weight`
- `lora_b` → `lora_B.weight`
- PEFT 側期待 layout への転置

3D expert-wise tensor について必要:

- expert 軸の意味を保持した変換ロジック
  - もしくは
- **「PEFT/vLLM 等価表現が未確認なら明示的に停止する」ロジック**

### 5.5 PEFT adapter_config.json 生成

少なくとも以下を出力:

- `peft_type = "LORA"`
- `base_model_name_or_path`
- `r`
- `lora_alpha`
- `lora_dropout`
- `target_modules`
- `bias = "none"`
- `modules_to_save = null`
- `use_dora = false`
- `use_rslora` の明示
- `inference_mode = true`

### 5.6 packaging

- `adapter_model.safetensors` を出力
- `adapter_config.json` を出力
- 必要なら manifest を同ディレクトリに出力
- `submission.zip` 用の単一 adapter ディレクトリ構造を保証

### 5.7 監査ログ / manifest

最低限記録すべき内容:

- 元 adapter path
- 元 config 抜粋
- 変換先 base model identity
- key mapping 一覧
- tensor shape 変換結果
- 未対応 key 一覧
- 3D expert-wise tensor の扱い
- 変換停止理由または注意事項

---

## 6. まだ不足しているもの

現時点では、以下が不足しているため、**まだ「意味保存で変換できる」とは言えない**。

### 6.1 Nemotron MoE 部分の確定的 module mapping

特に不足しているのは:

- `shared_experts.down_proj`
- `switch_mlp.fc1`
- `switch_mlp.fc2`

が HF/PEFT/vLLM 側でどう表現されるべきかの確証。

### 6.2 3D expert-wise LoRA の PEFT/vLLM 等価表現

最大の未解決点:

- `(128, ..., ...)` 形状の LoRA を、PEFT 標準 LoRA checkpoint としてどう表すか
- vLLM がそれをどう受理するか
- expert 軸を flatten / split / per-expert module に分解しても意味が保存されるか

この点が未確認のままでは、**変換しても別物になる危険が高い**。

### 6.3 ベースモデル識別子の正式固定

現在の MLX config はローカル MLX 6bit パスを持っているが、提出契約上は

- Nemotron-3-Nano-30B 向け
- vLLM evaluator が使う base と整合

である必要がある。  
どの文字列を `base_model_name_or_path` として最終採用するか、正式に固定が必要。

### 6.4 変換後の実機検証

必要な検証がまだ足りない。

- PEFT でロードできるか
- vLLM で legal check を通るか
- official evaluator 相当条件で smoke test を通るか
- 変換前後でローカルな出力差が破綻していないか

---

## 7. 信頼できる変換と認めるための確認事項

変換を trust するには、最低でも以下が必要。

### 7.1 静的整合チェック

- `adapter_model.safetensors` がある
- `adapter_config.json` がある
- `r <= 32`
- `target_modules` が空でない
- `bias == "none"`
- `modules_to_save == null`
- `use_dora == false`
- base model identity が固定されている

### 7.2 PEFT ロード確認

- official Nemotron base に対して adapter を attach できる
- missing/unexpected key が出ない
- adapter 適用で forward が成立する

### 7.3 vLLM smoke

- README 契約相当の設定で LoRA をロード可能
- rank 制約で落ちない
- submission.zip から認識できる
- few-shot でも generation が壊れない

### 7.4 変換 fidelity の最低検証

可能なら同一プロンプトに対して

- MLX + 元 adapter
- HF/vLLM + 変換後 adapter

を比較し、少なくとも主要 layer 出力または初期 token 挙動が極端に乖離しないことを確認する。  
これが取れない場合、**意味保存の主張は弱い**。

---

## 8. 今後 MLX adapter 作成時点で必ず仕込むべき要件

ここは特に重要。  
後から exporter で救えない情報があるため、**MLX adapter creation time に残しておくべき情報**を明示する。

### 8.1 base model identity を作成時に固定保存する

必須:

- Hugging Face / evaluator と整合する base model identifier
- 量子化済みローカルパスだけでなく、**元の公式ベース識別子**
- 可能なら model revision / commit / checksum

理由:

- 後からローカル MLX パスしか残っていないと、提出契約上の base 整合が崩れる

### 8.2 target module registry を作成時に保存する

必須:

- 学習対象 module の完全修飾名一覧
- short name だけでなく **実 tensor key に対応する完全 path**
- 各 module の種類
  - dense linear
  - shared expert
  - switch expert

理由:

- `target_modules = ["q_proj", ...]` だけでは MoE 実体との対応が足りない

### 8.3 shape / layout registry を作成時に保存する

必須:

- 各 LoRA key の shape
- どの軸が input/output/rank/expert か
- forward での適用規約
- 転置要否

理由:

- 後から shape だけ見ても、3D tensor の意味が断定できない

### 8.4 MoE expert 軸の意味を作成時に明文化する

必須:

- `128` 軸が何を表すか
- expert ごとに独立 parameter なのか
- grouped operator として扱うのか
- HF/PEFT 変換時に想定する表現

理由:

- ここが曖昧だと 3D LoRA は exporter で正しく扱えない

### 8.5 module mapping registry を作成時に保存する

必須:

- MLX module path → HF/PEFT module path の対応表
- shared expert / switched expert の対応規則
- バージョン差分がある場合はその対応条件

理由:

- 後から手作業推定すると変換の意味保存性が崩れる

### 8.6 scaling semantics を作成時に固定保存する

必須:

- rank
- scale
- dropout
- bias 使用有無
- rsLoRA / DoRA 使用有無
- 可能なら forward 式のバージョン情報

理由:

- alpha の再構成に必要

### 8.7 module coverage を作成時に保存する

必須:

- どの layer に adapter が入ったか
- どの layer には入っていないか
- merge 後 adapter の場合、由来 source と coverage 差分

理由:

- PEFT 側で key 数が減った時に、欠落か仕様かを判断できる

### 8.8 export manifest を毎回残す

推奨ではなく必須:

- 元 MLX config
- 元 tensor key 一覧
- shape registry
- module mapping registry
- base model identity
- 変換先想定フォーマット

理由:

- 今回のように後追いで exporter を作る場合の情報欠落を防ぐ

---

## 9. リスク / 変換停止条件

以下に当てはまる場合、**変換は unsafe または実質不可能**として停止すべき。

### 9.1 3D expert-wise tensor の意味対応が確定しない

- PEFT/vLLM 等価表現が確認できない
- expert 軸をどう扱うか仕様が無い
- flatten / split で意味保存を証明できない

この場合、**direct PEFT/vLLM translation は不可**とみなす。

### 9.2 base model identity が固定できない

- どの Nemotron base に対する adapter か確定できない
- evaluator base と齟齬の可能性がある

この場合、提出互換を主張できない。

### 9.3 学習時 metadata が足りない

- rank/scale/dropout はあるが module-level layout 情報が無い
- MoE expert 軸の意味が不明
- module mapping registry が無い

この場合、重みを「それっぽく」並べ替えるしかなくなり、意味保存ではない。

### 9.4 vLLM legal 条件に反する

- `r > 32`
- `bias != "none"`
- `modules_to_save != null`
- `use_dora = true`

この場合、README 契約に適合しない。

### 9.5 変換後に PEFT/vLLM smoke が通らない

- PEFT attach 不可
- key mismatch 多発
- submission.zip 不成立
- vLLM load failure

この場合、提出物として採用しない。

---

## 10. 実務上の優先順位

現時点の優先順位は以下。

1. **80/20 merge adapter を唯一の exporter ターゲットとして固定**
2. **MLX artifact と README 契約のギャップを埋める最小 PEFT packaging を定義**
3. **MoE / switch expert 3D tensor の意味対応可否を最優先で調査**
4. **等価表現が無ければ unsafe として停止**
5. **今後の MLX adapter 作成時に必要 metadata を必須化**

---

## 11. この計画の結論

現段階で分かっていることを一文で言うと:

> **2D の通常 LoRA 部分だけなら PEFT 形式への写像は見えているが、80/20 merge adapter に含まれる 3D の MoE expert-wise LoRA が、意味保存付きで PEFT/vLLM に直訳できるかは未確認であり、ここがコア blocker である。**

したがって、現時点の正しい計画は次の二段階。

1. **README 契約に照らして何が必要かを固定する**
2. **MoE 3D tensor の等価表現が確認できるまで、faithful conversion 完了とは言わない**

これにより、「とりあえず PEFT っぽいファイルを作る」ことと、  
「意味を変えずに submission-compatible にする」ことを明確に区別できる。
