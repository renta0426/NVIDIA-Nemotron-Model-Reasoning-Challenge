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

補完狙いの merge (`official-ultra` + `short-ultra`) も試したが、`85/15` merge は quick で上回っても hard serious で負けたため、現時点の corrected verified best は維持。

一方で、README-faithful な `official_lb` (`enable_thinking=true`) を主指標にした **official-first の暫定 best** は別 candidate になった。

- candidate:
  - `v5_merge_officiallowlr_officialultra_97_03_bf16`
- recipe:
  - generalist:
    - `v4_baseline_notebook_sft_bf16_full_text_lowlr_clip_official_run1`
  - specialist:
    - `v4_baseline_notebook_sft_bf16_full_text_ultralowlr_clip_official_run1`
  - linear merge:
    - `97/3`
- verified local README-faithful scores:
  - `official quick shadow_128 = 0.6640625`
  - `official serious shadow_256 = 0.65625`
  - `official serious hard_shadow_256 = 0.6328125`

つまり、

- corrected proxy で最も強いのは `official-ultra` 単体 SFT
- README-faithful official-first で最もバランスが良いのは `official-lowlr` を親にした `97/3` shallow merge

という二層構造になっている。

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

## 8. 2026-03-27 official gate 方針への pivot

README の本番条件は `official_lb` (`enable_thinking=true`) なので、corrected no-think proxy だけを最適化しても十分ではない。  
このため、repo 側へ official-aligned lightweight gate を追加した。

- added:
  - `versions/v1/conf/eval/official_lb_nothink_shortboxed.yaml`
  - `versions/v4/conf/eval/candidate_score_quick_nothink_shortboxed.yaml`
  - `versions/v4/conf/eval/candidate_score_serious_nothink_shortboxed.yaml`
  - `versions/v4/conf/eval/candidate_score_official_mini.yaml`
  - `versions/v1/data/eval_packs/shadow_48_balanced.csv`

新しい ladder:

1. corrected no-think proxy で broad sweep
2. `official_mini` (`shadow_48_balanced`, `official_lb`) で official alignment 確認
3. full `official quick` (`shadow_128`, `official_lb`) に昇格
4. さらに良い候補だけ `official serious`

### 8.1 official mini 結果

`official_mini` を主要 full-SFT 候補へ当てた結果、corrected proxy の ranking がそのまま official ranking にはならないと確認できた。

- current corrected verified best
  - candidate:
    - `v4_baseline_notebook_sft_bf16_full_text_ultralowlr_clip_official_run1`
  - `official_mini = 0.5208333333`
  - `format_fail_rate = 0.2708333333`
  - `avg_output_len_chars = 60.9167`

- official-lowLR branch
  - candidate:
    - `v4_baseline_notebook_sft_bf16_full_text_lowlr_clip_official_run1`
  - `official_mini = 0.7083333333`
  - `format_fail_rate = 0.0`
  - `avg_output_len_chars = 30.0417`

family 差も大きく、`official_lowlr` は mini 上で

- `roman_numeral = 1.0`
- `text_decryption = 1.0`
- `unit_conversion = 1.0`

まで伸びた。  
一方 `official_ultra` は `unit_conversion = 0.0`、`text_decryption format_fail_rate = 0.5` で明確に不利だった。

### 8.2 full official quick 結果

`official_mini` 勝者の `v4_baseline_notebook_sft_bf16_full_text_lowlr_clip_official_run1` を full `official quick` へ昇格。

- `shadow_128 = 0.640625`
- `format_fail_rate = 0.0078125`
- `boxed_rate = 1.0`
- `avg_output_len_chars = 31.125`

主な family:

- `unit_conversion = 1.0`
- `roman_numeral = 1.0`
- `text_decryption = 0.8571`
- `gravity_constant = 0.4091`
- `bit_manipulation = 0.3636`
- `symbol_equation = 0.2381`

これは、従来 verified best の `official quick = 0.484375` を大きく上回る。  
つまり **本番寄せでは current best candidate が入れ替わった**。

### 8.3 full official serious 結果

同 candidate をさらに full `official serious` へ昇格した。

- `shadow_256 = 0.64453125`
- `hard_shadow_256 = 0.63671875`
- `format_fail_rate = 0.0078125 / 0.01171875`
- `boxed_rate = 1.0 / 1.0`
- `avg_output_len_chars = 30.2383 / 31.0352`

`hard_shadow_256` family snapshot:

- `unit_conversion = 1.0`
- `roman_numeral = 1.0`
- `text_decryption = 0.6190`
- `bit_manipulation = 0.6047`
- `gravity_constant = 0.3488`
- `symbol_equation = 0.2558`

解釈:

- corrected proxy の verified best (`official-ultralow`) より、README-faithful local official score はこちらの方がかなり良い
- したがって現時点の **official-first local best** は
  - `v4_baseline_notebook_sft_bf16_full_text_lowlr_clip_official_run1`
- まだ `0.8+` には届かないが、`0.484375 -> 0.640625 -> 0.64453125/0.63671875` まで改善したため、
  今後の sweep / continuation はこの candidate を親にして進める価値が高い

### 8.4 次の改善方針

parent / parentfix 系は corrected quick でも `0.16-0.23` 台と弱く、本線から外した。  
代わりに、`official quick = 0.640625` を出した

- `v4_baseline_notebook_sft_bf16_full_text_lowlr_clip_official_run1`

を parent にして、gentle な Stage-C continuation を 2 本開始した。

- `v4_rft_stage_c_fullsftparent_gentle_run1`
- `v4_rft_stage_c_fullsftparent_answerbias_gentle_run1`

狙いは、full-SFT parent の boxed stability を壊さずに `symbol_equation` / `gravity_constant` / `bit_manipulation` を少しずつ押し上げ、official `0.7-0.8` の保持線へ乗せること。

### 8.5 gentle Stage-C continuation は official-first では失敗

上記 2 本の continuation は train 自体は完走した。

- `v4_rft_stage_c_fullsftparent_gentle_run1`
  - `final_train_loss = 0.4285714328`
  - `final_val_loss = 0.6206146479`
- `v4_rft_stage_c_fullsftparent_answerbias_gentle_run1`
  - `final_train_loss = 0.4107142985`
  - `final_val_loss = 0.5231760144`

しかし `official_micro` (`shadow_12_balanced`, `official_lb`) で診断すると、どちらも実運用には不適だった。

- gentle
  - `overall_acc = 0.4166666667`
  - `format_fail_rate = 0.5`
  - `avg_output_len_chars = 726.25`
- answerbias
  - `overall_acc = 0.3333333333`
  - `format_fail_rate = 0.25`
  - `avg_output_len_chars = 668.8333`

row-level では `NOT_FOUND`, `your answer`, `boxed{XXIV}`, `<think>:}` などが出ており、training loss が改善しても official thinking-on generation はむしろ壊れた。  
したがって full-SFT parent からの gentle Stage-C continuation は、本線から外した。

### 8.6 official-first shallow merge sweep

continuation の代わりに、README-faithful local best の

- `v4_baseline_notebook_sft_bf16_full_text_lowlr_clip_official_run1`

へ corrected verified best の `official-ultra` を少量混ぜる shallow merge を試した。

試行した比率と結果:

1. `95/5`
   - quick: `0.6484375`
   - serious: `0.66796875 / 0.6171875`

2. `90/10`
   - quick: `0.640625`
   - serious: `0.63671875 / 0.609375`

3. `97/3`
   - quick: `0.6640625`
   - serious: `0.65625 / 0.6328125`

比較基準の parent は:

- quick: `0.640625`
- serious: `0.64453125 / 0.63671875`

解釈:

- `95/5` は shadow 側の伸びが最も大きいが、hard を落とし過ぎた
- `90/10` は shadow / hard の両方で parent を超えられなかった
- `97/3` は quick が現 best で、`shadow_256` も parent 超え、`hard_shadow_256` は parent とほぼ同等まで維持した

3 点平均でも:

- parent mean = `0.640625`
- `95/5` mean = `0.64453125`
- `97/3` mean = `0.6510416667`

となり、現時点では `97/3` が最もバランスの良い official-first candidate と判断できる。

### 8.7 2026-03-27 時点の official-first 暫定結論

README-faithful local screening の現状 Pareto は次の 2 本。

1. stable parent
   - `v4_baseline_notebook_sft_bf16_full_text_lowlr_clip_official_run1`
   - serious: `0.64453125 / 0.63671875`

2. balanced shallow-merge leader
   - `v5_merge_officiallowlr_officialultra_97_03_bf16`
   - quick: `0.6640625`
   - serious: `0.65625 / 0.6328125`

したがって、README-faithful 条件で次に提出寄りへ進めるなら本命は `97/3`。  
ただし hard 側単独の safest choice は依然として parent なので、両方を保持したままさらに浅い merge も確認した。

- `98/2`
  - quick: `0.6328125`
  - `format_fail_rate = 0.0`
  - `boxed_rate = 1.0`

これは parent (`0.640625`) と `97/3` (`0.6640625`) の両方を下回ったため、浅い merge の best は `97/3` で頭打ちと判断した。

### 8.8 official-first best 専用の minimal single-file

corrected verified best だけでなく、README-faithful official-first best も CUDA / vLLM へ移植しやすいよう、1 ファイルの minimal pipeline に切り出した。

- file:
  - `versions/v4/code/train_official_first_best_v4_minimal.py`

この file が再現するのは次の current official-first best pipeline:

1. `data/train.csv` から official-long notebook pack を作る
2. full-data generalist SFT (`lr=1e-4`)
3. full-data specialist SFT (`lr=5e-5`)
4. 2 本の LoRA adapter を `97/3` で線形 merge する

README 契約も manifest に明示している。

- `max_lora_rank <= 32`
- `max_tokens = 7680`
- `top_p = 1.0`
- `temperature = 0.0`
- `max_num_seqs = 64`
- `max_model_len = 8192`
- `vLLM`
- `\boxed{}` 優先抽出

validation:

- `uv run python -m py_compile versions/v4/code/train_official_first_best_v4_minimal.py`
- render-only smoke:
  - `uv run python versions/v4/code/train_official_first_best_v4_minimal.py --output-dir versions/v4/outputs/train/_official_first_best_minimal_smoke --candidate-id v5_official_first_best_97_03_minimal_smoke --subsample-size 8`
- execute smoke:
  - `uv run python versions/v4/code/train_official_first_best_v4_minimal.py --output-dir versions/v4/outputs/train/_official_first_best_minimal_execute_smoke --candidate-id v5_official_first_best_97_03_minimal_execute_smoke --subsample-size 8 --execute`
- `uv run pytest -q versions/v4/tests`
- result:
  - render-only smoke pass
  - execute smoke pass
  - two-stage SFT -> merge completed end-to-end
  - tests: `5 passed`

full-data execute repro も起動済みで、`official_mini` により current official-first reference と照合する。

### 8.9 official-long full-data SFT sweep v2 は失敗

`97/3` shallow merge の次に、本線として official-long full-data SFT を 3 本並列で追加検証した。

1. `midlr`
   - candidate:
     - `v4_baseline_notebook_sft_bf16_full_text_midlr_clip_official_run1`
   - train:
     - `lr = 7.5e-5`
     - `final_train_loss = 0.4564516246`
   - `official_mini = 0.0208333333`
   - `format_fail_rate = 0.3125`
   - `boxed_rate = 0.6875`

2. `highlr`
   - candidate:
     - `v4_baseline_notebook_sft_bf16_full_text_highlr_clip_official_run1`
   - train:
     - `lr = 1.25e-4`
     - `final_train_loss = 0.3270089328`
   - `official_mini = 0.1666666667`
   - `format_fail_rate = 0.5625`
   - `boxed_rate = 0.9791666667`
   - `avg_output_len_chars = 79.8125`

3. `epoch075`
   - candidate:
     - `v4_baseline_notebook_sft_bf16_full_text_lowlr_clip_official_epoch075_run1`
   - train:
     - `lr = 1e-4`
     - `epochs = 0.75`
     - `final_train_loss = 0.5615384579`
   - `official_mini = 0.0`
   - `format_fail_rate = 0.0`
   - `boxed_rate = 1.0`

解釈:

- 3 本とも README-faithful local best (`official_lowlr` parent や `97/3`) をまったく超えられなかった
- `midlr` は `gravity_constant` / `unit_conversion` で extraction fail が多く、短すぎる壊れ方をした
- `highlr` は boxed 自体は多いが、`roman_numeral`, `symbol_equation`, `gravity_constant` で format fail が激増し、出力長も大きく伸びた
- `epoch075` は形式は保つが全 family で不正解になり、短縮ではなく reasoning quality 側が落ちた

つまり、この帯域の LR / epoch sweep は **train loss が下がっても official-first score を改善しない**。  
この結果により、current README-faithful 本線は依然として `97/3` shallow merge である。
