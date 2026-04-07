# baseline_mlx Results

## Source of truth

この系列の判定基準は **`README.md` の Evaluation / Submitting 節**に固定する。

- `max_lora_rank = 32`
- `max_tokens = 7680`
- `top_p = 1.0`
- `temperature = 0.0`
- `max_num_seqs = 64`
- `max_model_len = 8192`

補足:

- baseline notebook は `baseline/nemotron-sft-lora-with-cot-v2/artifacts/train_split_with_cot.csv` を使い、type ごとに `300 / 400 / 700 / 700 / 607 / 200` を sampling している。
- `baseline_mlx` の再現は上記 sampling と CoT 整形を維持しつつ、MLX 用に `shadow_model` と `enable_thinking` patch を入れている。
- 生成される `mlx_adapter_bundle.zip` は **ローカル MLX 再利用用**であり、現時点では **PEFT/vLLM 提出互換を主張しない**。

## HF notebook reference

| pipeline | local320 | binary | gravity | roman | symbol | text | unit | source |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `baseline/nemotron-sft-lora-with-cot-v2` | `249/320 = 0.7781` | `29/60` | `50/50` | `50/50` | `22/60` | `49/50` | `49/50` | `baseline/nemotron-sft-lora-with-cot-v2/result/artifacts/phase0_eval_summary.json` |

## MLX reproduction runs

| version | run_name | scope | sampled_rows | train_rows | valid_rows | total_iters | max_seq | measured | status | artifacts |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| `baseline-mlx-smoke-v1` | `nemotron_sft_lora_with_cot_v2_mlx_smoke_v1` | smoke | `24` | `24` | `4` | `1` | `1024` | `val_loss=0.607`, `train_loss=0.565`, `peak_mem=64.835 GB` | adapter 生成まで完走 | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_smoke_v1/training_result.json` |
| `baseline-mlx-full-v1` | `nemotron_sft_lora_with_cot_v2_mlx_v1` | full notebook-equivalent | `2907` | `2907` | `32` | `5814` | `4096` | `iter1 val_loss=0.683`; `iter5600 val_loss=0.186`; `iter5800 val_loss=0.180`; `iter5814 val_loss=0.181`; `iter5814 train_loss=0.272`; `peak_mem=68.581 GB` | 完走 | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_v1/training_result.json` |

## README-aligned local eval

| version | eval_name | scope | local320 | binary | gravity | roman | symbol | text | unit | notes |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `baseline-mlx-eval-smoke-v1` | `baseline_mlx_eval_smoke_v1` | smoke 6 rows | `4/6 = 0.6667` | `1/1` | `1/1` | `1/1` | `0/1` | `0/1` | `1/1` | `peak_memory_gb=65.63`, `generation_tps=8.20` |
| `baseline-mlx-eval-full320-v1` | `baseline_mlx_eval_full320_shard2_v1` | README local320 | `196/320 = 0.6125` | `19/60` | `39/50` | `50/50` | `17/60` | `21/50` | `50/50` | shard parallel; chunk peak `73.69 GB`; binary boxed extraction `1.0`; leading-zero retention `0.9` |

## In-flight follow-up batch

| version | run_name | train_csv | bit_rows | mask_prompt | lr | status |
| --- | --- | --- | ---: | --- | ---: | --- |
| `baseline-mlx-v3f-exact-v1` | `nemotron_sft_lora_with_cot_v2_mlx_v3f_exact_v1` | `train_split_with_cot_v3f_safe_plus_notformula.csv` | `1021` | `true` | `1e-4` | stopped by user before first train report |
| `baseline-mlx-v3f-nomask-v1` | `nemotron_sft_lora_with_cot_v2_mlx_v3f_nomask_v1` | `train_split_with_cot_v3f_safe_plus_notformula.csv` | `1021` | `false` | `1e-4` | stopped by user before first train report |
| `baseline-mlx-v2-exact-v1` | `nemotron_sft_lora_with_cot_v2_mlx_v2_exact_v1` | `train_split_with_cot_v2.csv` | `1021` | `true` | `1e-4` | stopped by user before first train report |
| `baseline-mlx-v3f-lr5e5-v1` | `nemotron_sft_lora_with_cot_v2_mlx_v3f_lr5e5_v1` | `train_split_with_cot_v3f_safe_plus_notformula.csv` | `1021` | `true` | `5e-5` | stopped by user before first train report |

## Notes

- LoRA target は MLX Nemotron の module 名に合わせて `mixer.in_proj`, `mixer.out_proj`, `mixer.shared_experts.up_proj`, `mixer.shared_experts.down_proj` に固定した。これは HF notebook の `in_proj|out_proj|up_proj|down_proj` を MLX 側へ最も近く写した設定。
- warmup 中の `Learning Rate` 表示は iter 10 付近で見た目が不自然だったが、schedule 単体検証と以後の train log では non-zero で立ち上がっていることを確認済み。
- 今回の full run は **`train_split_with_cot.csv` の元 baseline 再現**であり、Bit Manipulation は `607` 行 sampling のまま。IDE 上で見えていた `1021` 行設定は別 notebook 変更で、今回の完走 run には使っていない。
- full320 実測は HF notebook reference `249/320 = 0.7781` を下回り、主な失点は `symbol 17/60`, `binary 19/60`, `text 21/50`。特に `glyph_len5 0/20`, `numeric_2x2 17/40`, `bit_other 13/46` が弱い。
- 一方で `roman 50/50`, `unit 50/50` は README 条件下でも完全再現できており、baseline notebook 由来の知識は family ごとに保持率が大きく異なる。
- row-level で origin reference と突き合わせると `HF-only 65`, `MLX-only 12`, `both_wrong 59`, `both_correct 184`。HF-only loss は `text 29`, `binary 16`, `gravity 11`, `symbol 9` が中心で、特に text は **HF が取れて MLX だけ落とす**再現差が支配的。
- notebook 現在版の学習セルは `train_split_with_cot_v3f_safe_plus_notformula.csv` と `Bit Manipulation = 1021` を指している。したがって、今回の `train_split_with_cot.csv` / `607` 再現は「元 CSV baseline」の記録として保持しつつ、次段では **notebook current config の MLX 再現**も別 run として切り分ける。
