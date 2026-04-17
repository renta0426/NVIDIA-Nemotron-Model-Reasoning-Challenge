# v20_mlx_repro_v1_fullrun_targetfix_mb1

> Repository note: canonical challenge contract lives in `README.md`.
> この run は `A-Open-ProgressPrizePublication/nemotron/training/sft/04-08-16-14` を MLX 単一ファイル実装 `v20_mlx_repro_v1/reproduce_v20_mlx_repro.py` で再現した **MLX baseline run** です。

## この run の要点

- run_root: `v20_mlx_repro_v1/outputs/v20_mlx_repro_v1_fullrun_targetfix_mb1`
- 役割: MLX baseline
- 学習データ: `A-Open-ProgressPrizePublication/nemotron/training/sft/04-08-16-14`
- ベースモデル: `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16`
- backend: `mlx`
- optimizer: `Adam`
- Adam bias_correction: `True`
- learning_rate: `0.0002`
- micro_batch_size: `1`
- effective_batch_size: `32`
- optimizer_steps: `245`
- microsteps: `7830`
- max_seq_length: `8192`
- lora_rank: `32`
- local300 記録スコア: **`246/300 = 0.82`**

## 学習再現手順

1. リポジトリ root に移動します。
2. UV 環境が未同期なら `uv sync` を実行します。
3. 次のコマンドで学習を起動します。

```bash
cd "/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge"
uv sync
uv run python v20_mlx_repro_v1/reproduce_v20_mlx_repro.py train \
  --output-root v20_mlx_repro_v1/outputs \
  --run-name v20_mlx_repro_v1_fullrun_targetfix_mb1
```

## 実行後に確認するファイル

- `training_result.json`: 学習完了結果
- `run_manifest.json`: 学習設定の正本
- `adapter/`: 学習済み LoRA adapter
- `shadow_model/`: 評価用 shadow model
- `train_cmd.sh`: この run で記録された実コマンド

## local300 再評価手順

README 契約ベースの local 再評価は、300 行 stratified subset を 4 shard で回します。

```bash
cd "/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge"

for i in 0 1 2 3; do
  uv run python v20_mlx_repro_v1/reproduce_v20_mlx_repro.py eval-adapter-validation \
    --run-name v20_mlx_repro_v1_fullrun_targetfix_mb1 \
    --validation-subset-size 300 \
    --validation-subset-mode stratified-category-proportional \
    --max-num-seqs 4 \
    --prompt-chunk-size 4 \
    --prefill-batch-size 4 \
    --completion-batch-size 4 \
    --eval-shards 4 \
    --eval-shard-index "$i"
done

uv run python v20_mlx_repro_v1/reproduce_v20_mlx_repro.py merge-adapter-validation \
  --run-name v20_mlx_repro_v1_fullrun_targetfix_mb1 \
  --validation-subset-size 300 \
  --validation-subset-mode stratified-category-proportional \
  --max-num-seqs 4 \
  --prompt-chunk-size 4 \
  --prefill-batch-size 4 \
  --completion-batch-size 4

uv run python v20_mlx_repro_v1/reproduce_v20_mlx_repro.py postprocess-run \
  --run-name v20_mlx_repro_v1_fullrun_targetfix_mb1 \
  --postprocess-eval-kind adapter-validation
```

再評価結果は以下に出ます。

- `adapter_validation/validation_summary.json`
- `adapter_validation/validation_summary.md`
- `adapter_validation/validation.csv`

## 補足

- 学習入力は現在の `corpus.jsonl` ではなく、`04-08-16-14/tokens` と `logprobs/index.jsonl` を replay します。
- この baseline は MLX 再現の比較基準で、後続の `v20_mlx_repro_v1_fullrun_targetfix_mb1_nobc` は **Adam bias_correction を False にした差分 run** です。
