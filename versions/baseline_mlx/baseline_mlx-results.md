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
| `baseline-mlx-full-v1` | `nemotron_sft_lora_with_cot_v2_mlx_v1` | full notebook-equivalent | `2907` | `2907` | `32` | `5814` | `4096` | `iter1 val_loss=0.683`; `iter200 val_loss=0.382`; `iter400 val_loss=0.299`; `iter570 train_loss=0.200`; `peak_mem=67.133 GB` | 実行中 | `baseline_mlx/outputs/nemotron_sft_lora_with_cot_v2_mlx_v1/prepare_manifest.json` |

## Notes

- LoRA target は MLX Nemotron の module 名に合わせて `mixer.in_proj`, `mixer.out_proj`, `mixer.shared_experts.up_proj`, `mixer.shared_experts.down_proj` に固定した。これは HF notebook の `in_proj|out_proj|up_proj|down_proj` を MLX 側へ最も近く写した設定。
- warmup 中の `Learning Rate` 表示は iter 10 付近で見た目が不自然だったが、schedule 単体検証と以後の train log では non-zero で立ち上がっていることを確認済み。
