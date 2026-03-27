# BF16 single-file repro and experiment summary

## 1. README.md を基準にした前提

この整理は `README.md` の Evaluation / Submitting を基準にしている。

- ベースモデルは `NVIDIA Nemotron-3-Nano-30B`
- 提出物は `adapter_config.json` を含む LoRA adapter
- `max_lora_rank <= 32`
- 本番推論は `vLLM`
- 本番評価パラメータは `max_tokens=7680`, `top_p=1.0`, `temperature=0.0`, `max_num_seqs=64`, `max_model_len=8192`
- 回答は `\boxed{}` 抽出が最優先

本リポジトリ内のローカル実験は、最終的にこの契約へ寄せることを目的に進めた。

## 2. 結論サマリ

2026-03-27 時点で、ローカル corrected proxy 上の **verified best** は次の BF16 full-data notebook SFT。

- candidate:
  - `v4_baseline_notebook_sft_bf16_full_text_ultralowlr_clip_official_run1`
- recipe:
  - full `data/train.csv` 9500 rows
  - notebook-faithful chat text pack
  - official-long boxed instruction
  - `lr=5e-5`
  - `lora_r=32`
  - `batch=1`
  - `gradient_accumulation_steps=4`
  - `optimizer=adamw`
  - `warmup_ratio=0.1`
  - `valid_fraction=0.0`

verified local scores:

- `shadow_128 = 0.7265625`
- `shadow_256 = 0.76171875`
- `hard_shadow_256 = 0.78515625`

補完狙いの merge (`official-ultra` + `short-ultra`) も試したが、`85/15` merge は quick で上回っても hard serious で負けたため、現時点の verified best は維持。

## 3. ここまでの主要な実験経緯

### 3.1 BF16 のローカル評価が壊れて見えていた時期

初期の BF16 評価では、no-think local eval が極端に悪く、direct generate と shard eval が噛み合っていなかった。

観測された主症状:

- 極短の garbled output
- `overall_acc=0.0`
- `format_fail_rate=1.0`
- direct `mlx_lm.batch_generate` では clean boxed なのに、row-level parquet では壊れている

この時点では prompt wording や `enable_thinking` 側を疑っていたが、後で evaluator の tokenizer drift が主因だと判明した。

### 3.2 root cause: evaluator tokenizer drift

`versions/v1/code/train.py` を調査した結果、`get_tokenizer()` が tokenizer path 未指定時に `BuiltinCompetitionTokenizer()` へ落ちることを確認した。

さらに MLX shard worker 起動時も tokenizer path を渡していなかったため、shard 側でも fake template を踏んでいた。

この修正により:

- local eval の既定 tokenizer を real model tokenizer へ自動解決
- shard worker にも `COMPETITION_TOKENIZER_PATH` を伝搬
- stale no-think 評価結果を破棄し、tokfix 後の corrected local eval に切り替え

### 3.3 corrected no-think proxy の再較正

tokenizer drift 修正後、`enable_thinking=false` + short boxed instruction の corrected proxy で BF16 候補を再評価した。

この段階で分かったこと:

- base より良い BF16 candidate は存在する
- 形式崩れではなく reasoning quality の差で負ける family が多い
- 特に `text_decryption`, `symbol_equation`, `gravity_constant` がボトルネック

ただし absolute score はユーザー共有の official base `0.5` とはずれており、candidate 間の相対比較用 gate として扱うのが妥当だった。

### 3.4 official thinking-on local gate は cheap gate として不適

README 本番寄せの `official_lb` (`enable_thinking=true`) も real tokenizer 下で試したが、4-row head4 ですら 9 分超かかって終わらなかった。

この結果から:

- tokenizer drift 修正後も official thinking-on は local cheap gate として重すぎる
- candidate selection は corrected no-think proxy 主体で回す
- official thinking-on は最終確認向けの高コスト診断に限定

という方針に切り替えた。

ただし、その後に README 寄せ quick gate (`shadow_128` + `official_lb`) 自体は完走できることも確認した。

- candidate:
  - `v4_baseline_notebook_sft_bf16_full_text_ultralowlr_clip_official_run1`
- result:
  - `overall_acc = 0.484375`
  - `format_fail_rate = 0.2890625`
  - `boxed_rate = 1.0`
  - `avg_output_len_chars = 66.34375`
- observed behavior:
  - clean boxed answer自体は多い
  - ただし `text_decryption` や `unit_conversion` で長めの出力や prompt echo が混じる
  - row-level preview では `<think></think>` を含む boxed output と、instruction の echo による `boxed_multiple` failure の両方が見えた

したがって official thinking-on gate は **実行不能ではない** が、corrected no-think proxy よりかなり重く、かつ format / reasoning の両面でより厳しい診断として使うのが妥当。

### 3.5 full-data notebook SFT 2x2 matrix

次の大きな分岐として、full `data/train.csv` 9500 rows の notebook-style BF16 SFT を 2x2 で比較した。

軸:

- instruction
  - short: `Put your final answer inside \boxed{}`
  - official-long: `Please put your final answer inside \boxed{}` の README 寄せ wording
- learning rate
  - `1e-4`
  - `5e-5`

結果:

1. `official-long + 5e-5`
   - `shadow_128 = 0.7265625`
   - `shadow_256 = 0.76171875`
   - `hard_shadow_256 = 0.78515625`

2. `short + 5e-5`
   - `shadow_128 = 0.6953125`
   - `shadow_256 = 0.76171875`
   - `hard_shadow_256 = 0.71875`

3. `official-long + 1e-4`
   - `shadow_128 = 0.625`

4. `short + 1e-4`
   - `shadow_128 = 0.0078125`

重要な解釈:

- instruction wording は単なる format 差ではなく、精度差を生む
- 同じ `5e-5` でも official-long が short を上回る
- `1e-4` では short branch がほぼ collapse

### 3.6 adapter merge probe

verified best (`official-long + 5e-5`) と、`symbol_equation` が少しだけ強い `short + 5e-5` を線形 merge した。

試した merge:

- `80/20`
- `85/15`

quick (`shadow_128`) では:

- `85/15 = 0.75`
- verified best = `0.7265625`

と改善したが、serious では:

- merge `85/15`
  - `shadow_256 = 0.76171875`
  - `hard_shadow_256 = 0.75390625`
- verified best
  - `shadow_256 = 0.76171875`
  - `hard_shadow_256 = 0.78515625`

となり、hard 側で悪化した。よって merge は採用しない。

## 4. verified best の弱点

family 別に見ると、verified best の残る弱点は主に次の 2 つ。

- `symbol_equation`
  - `hard_shadow_256 acc = 0.3488`
- `gravity_constant`
  - `hard_shadow_256 acc = 0.7442`

一方で以下はかなり強い。

- `roman_numeral = 1.0`
- `unit_conversion = 1.0`
- `text_decryption = 0.9286`
- `bit_manipulation = 0.6977`

つまり、現時点の BF16 notebook SFT は「長い reasoning を垂れ流さず極短 boxed answer に落とす」点で大きく改善したが、`symbol_equation` と一部 `gravity_constant` の reasoning 精度にはまだ伸び代がある。

## 5. 単一ファイル実装

ユーザー要望に合わせ、best recipe を ad-hoc YAML 群ではなく **1 ファイル** に畳み込んだ。

対象ファイル:

- `versions/v4/code/train.py`

追加した command:

- `train-best-notebook-sft-v4`

この command は 1 コマンドで以下を実行する。

1. `data/train.csv` から full notebook-faithful train pack を作る
2. README 寄せ official-long boxed instruction を使う
3. 現 verified best と同じ BF16 SFT recipe で train する

実行例:

```bash
uv run python versions/v4/code/train.py train-best-notebook-sft-v4 --execute
```

主要固定値:

- `lora_r=32`
- `learning_rate=5e-5`
- `num_epochs=1.0`
- `per_device_train_batch_size=1`
- `gradient_accumulation_steps=4`
- `optimizer=adamw`
- `mask_prompt=false`
- `warmup_ratio=0.1`
- `valid_fraction=0.0`

## 5.1 verified-best 専用 minimal standalone file

その後、CUDA / vLLM への移植時に experimental code が邪魔にならないよう、verified best のみを再現する **最小単体ファイル** も新規に切り出した。

対象ファイル:

- `versions/v4/code/train_best_notebook_sft_v4_minimal.py`

この file に残したのは次だけ:

1. BF16 base model 解決
2. `data/train.csv` から notebook-faithful pack を作る処理
3. official boxed instruction を使う verified-best BF16 LoRA training loop
4. manifest / config / adapter / metrics の出力

逆に、Stage-C / preference / merge / score-candidate などは入れていない。

validation:

- `uv run python -m py_compile versions/v4/code/train_best_notebook_sft_v4_minimal.py versions/v4/code/train.py`
- render-only smoke:
  - `uv run python versions/v4/code/train_best_notebook_sft_v4_minimal.py --output-dir versions/v4/outputs/train/_minimal_smoke --candidate-id v4_best_notebook_sft_bf16_official_ultralowlr_minimal_smoke --subsample-size 8`
- `uv run pytest -q versions/v4/tests`
- result:
  - `5 passed`

initial full execute launch は `CacheDataset` 契約違反 (`TextDataset.process()` 未実装) で失敗したが、`__getitem__` が raw datum を返し `process()` が tokenization を担当する形へ修正後、8-row execute probe は成功した。

restarted minimal repro command:

```bash
uv run python versions/v4/code/train_best_notebook_sft_v4_minimal.py \
  --output-dir versions/v4/outputs/train/best_notebook_sft_minimal_repro_run1 \
  --candidate-id v4_best_notebook_sft_bf16_official_ultralowlr_minimal_repro_run1 \
  --execute
```

この minimal repro も、完了後に pack / adapter / adapter_config hash を元 verified best と比較する。

minimal repro run は完了した。

- original pack sha256:
  - `cbc408e902d4adccfd20dc716f8cd9c8338654fdfadf2caac78a54da03df0836`
- minimal repro pack sha256:
  - `cbc408e902d4adccfd20dc716f8cd9c8338654fdfadf2caac78a54da03df0836`
- 判定:
  - **一致**

したがって minimal standalone file でも、少なくとも `data/train.csv -> notebook-faithful full official pack` までは元 verified best と同じ。

- repro status:
  - `completed`
- final_train_loss:
  - `0.34916338324546814`
- peak_memory_gb:
  - `82.635142934`

adapter 側は exact hash では一致しなかった。

- original adapter sha256:
  - `5ba26f60cbcd14381cdfbfa8c285ea88af8d7aa6c853d357f30567625cb0b558`
- minimal repro adapter sha256:
  - `bed1a50a80d4c0565a997440ba4fa36930e8f654d1f2f007c9c0d6e1ea3d3dd7`
- adapter match:
  - **不一致**
- original adapter_config sha256:
  - `0c7ac6ce03ee7eac917b55cfdb545e19bce068e663cb8541010959cd2f634efb`
- minimal repro adapter_config sha256:
  - `46613c6cf3b7dd76ab9fbed05fb6319cd28ec019831c3389ddb6f30dbe85638e`
- adapter_config match:
  - **不一致**

そのため corrected proxy で再採点した。

- original verified best
  - `shadow_128 = 0.7265625`
  - `shadow_256 = 0.76171875`
  - `hard_shadow_256 = 0.78515625`
- minimal repro
  - `shadow_128 = 0.75`
  - `shadow_256 = 0.7421875`
  - `hard_shadow_256 = 0.75390625`

解釈:

- minimal standalone file も **exact deterministic reproduction** には未到達
- ただし recipe-level では十分近く、quick は元 best を上回った
- 一方で serious / hard serious は元 best より少し低い
- よって minimal file は **移植用の最小核として有効** だが、提出用の current verified best そのものと完全同一ではない

## 6. single-file 再現性確認

### 6.1 比較対象

元の verified best:

- candidate:
  - `v4_baseline_notebook_sft_bf16_full_text_ultralowlr_clip_official_run1`
- original pack sha256:
  - `cbc408e902d4adccfd20dc716f8cd9c8338654fdfadf2caac78a54da03df0836`
- original adapter sha256:
  - `5ba26f60cbcd14381cdfbfa8c285ea88af8d7aa6c853d357f30567625cb0b558`
- original adapter_config sha256:
  - `0c7ac6ce03ee7eac917b55cfdb545e19bce068e663cb8541010959cd2f634efb`

repro command:

```bash
uv run python versions/v4/code/train.py train-best-notebook-sft-v4 \
  --output-dir versions/v4/outputs/train/best_notebook_sft_singlefile_repro_run1 \
  --candidate-id v4_best_notebook_sft_bf16_official_ultralowlr_singlefile_repro_run1 \
  --execute
```

### 6.2 再現 run の結果

single-file repro run は完了した。

- original pack sha256:
  - `cbc408e902d4adccfd20dc716f8cd9c8338654fdfadf2caac78a54da03df0836`
- repro pack sha256:
  - `cbc408e902d4adccfd20dc716f8cd9c8338654fdfadf2caac78a54da03df0836`
- 判定:
  - **一致**

つまり、single-file command による `data/train.csv -> notebook-faithful full official pack` の生成は、元の verified best run と一致している。

- repro status:
  - `completed`
- final_train_loss:
  - `0.37027615308761597`
- peak_memory_gb:
  - `82.634914498`

adapter 側は exact hash では一致しなかった。

- original adapter sha256:
  - `5ba26f60cbcd14381cdfbfa8c285ea88af8d7aa6c853d357f30567625cb0b558`
- repro adapter sha256:
  - `9e42d58b177426081b66a17995380d94955ed61ce10cfe56e0dfa61fc70fa659`
- adapter match:
  - **不一致**
- original adapter_config sha256:
  - `0c7ac6ce03ee7eac917b55cfdb545e19bce068e663cb8541010959cd2f634efb`
- repro adapter_config sha256:
  - `46613c6cf3b7dd76ab9fbed05fb6319cd28ec019831c3389ddb6f30dbe85638e`
- adapter_config match:
  - **不一致**

そのため corrected proxy で再採点した。

確認したい項目:

1. 生成された train pack が元 pack と一致するか
   - **確認済み: 一致**
2. `adapters.safetensors` hash が一致するか
   - **不一致**
3. 一致しない場合でも local corrected score が同等水準か
   - **確認済み**

rescored corrected proxy:

- original verified best
  - `shadow_128 = 0.7265625`
  - `shadow_256 = 0.76171875`
  - `hard_shadow_256 = 0.78515625`
- single-file repro
  - `shadow_128 = 0.6953125`
  - `shadow_256 = 0.79296875`
  - `hard_shadow_256 = 0.76171875`

解釈:

- exact deterministic reproduction ではない
- ただし score profile は近く、`shadow_256` ではむしろ上振れ
- 一方で `shadow_128` と `hard_shadow_256` は元 verified best より少し低い
- よって single-file command は **recipe-level reproduction** には成功しているが、**bitwise / hash-level exact reproduction** には未到達

## 7. 2026-03-27 時点の判断

現時点で「更なる改善」ではなく「一旦止める」前提で固定するなら、採用候補は次。

- code path:
  - `versions/v4/code/train.py`
- command:
  - `train-best-notebook-sft-v4`
- verified best local candidate:
  - `v4_baseline_notebook_sft_bf16_full_text_ultralowlr_clip_official_run1`

次回再開時の主論点は、`symbol_equation` と `gravity_constant` をどう押し上げるかに絞られる。
