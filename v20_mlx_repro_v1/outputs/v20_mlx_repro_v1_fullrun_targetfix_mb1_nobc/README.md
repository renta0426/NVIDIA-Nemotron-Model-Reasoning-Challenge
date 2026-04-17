# v20_mlx_repro_v1_fullrun_targetfix_mb1_nobc

> Repository note: canonical challenge contract lives in `README.md`.
> この run は `A-Open-ProgressPrizePublication/nemotron/training/sft/04-08-16-14` を MLX 単一ファイル実装 `v20_mlx_repro_v1/reproduce_v20_mlx_repro.py` で再現した **best local300 run** です。

## この run の要点

- run_root: `v20_mlx_repro_v1/outputs/v20_mlx_repro_v1_fullrun_targetfix_mb1_nobc`
- 役割: 現在の MLX baseline best
- 学習データ: `A-Open-ProgressPrizePublication/nemotron/training/sft/04-08-16-14`
- ベースモデル: `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16`
- backend: `mlx`
- optimizer: `Adam`
- Adam bias_correction: `False`
- learning_rate: `0.0002`
- micro_batch_size: `1`
- effective_batch_size: `32`
- optimizer_steps: `245`
- microsteps: `7830`
- max_seq_length: `8192`
- lora_rank: `32`
- smoke8 記録スコア: **`6/8 = 0.75`**
- local300 記録スコア: **`254/300 = 0.846667`**
- baseline 差分: **`246/300 -> 254/300`**

## baseline との差分

この run は `v20_mlx_repro_v1_fullrun_targetfix_mb1` と同じ snapshot replay / batch 設計 / LoRA 設定を使い、**Adam bias_correction だけを `False` にした run** です。

## 学習再現手順

1. リポジトリ root に移動します。
2. UV 環境が未同期なら `uv sync` を実行します。
3. 次のコマンドで学習を起動します。

```bash
cd "/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge"
uv sync
uv run python v20_mlx_repro_v1/reproduce_v20_mlx_repro.py train \
  --output-root v20_mlx_repro_v1/outputs \
  --run-name v20_mlx_repro_v1_fullrun_targetfix_mb1_nobc
```

## 実行後に確認するファイル

- `training_result.json`: 学習完了結果
- `run_manifest.json`: 学習設定の正本
- `adapter/`: 学習済み LoRA adapter
- `shadow_model/`: 評価用 shadow model
- `train_cmd.sh`: この run で記録された実コマンド
- `adapter_validation_smoke8_snapshot/`: smoke 6/8 の退避結果

## local300 再評価手順

この run の `0.846667` は、300 行 stratified subset を 4 shard で回して merge した結果です。

```bash
cd "/Users/mac-studio/work/NVIDIA Nemotron Model Reasoning Challenge"

for i in 0 1 2 3; do
  uv run python v20_mlx_repro_v1/reproduce_v20_mlx_repro.py eval-adapter-validation \
    --run-name v20_mlx_repro_v1_fullrun_targetfix_mb1_nobc \
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
  --run-name v20_mlx_repro_v1_fullrun_targetfix_mb1_nobc \
  --validation-subset-size 300 \
  --validation-subset-mode stratified-category-proportional \
  --max-num-seqs 4 \
  --prompt-chunk-size 4 \
  --prefill-batch-size 4 \
  --completion-batch-size 4

uv run python v20_mlx_repro_v1/reproduce_v20_mlx_repro.py postprocess-run \
  --run-name v20_mlx_repro_v1_fullrun_targetfix_mb1_nobc \
  --postprocess-eval-kind adapter-validation
```

再評価結果は以下に出ます。

- `adapter_validation/validation_summary.json`
- `adapter_validation/validation_summary.md`
- `adapter_validation/validation.csv`

## 補足

- 学習入力は現在の `corpus.jsonl` ではなく、`04-08-16-14/tokens` と `logprobs/index.jsonl` を replay します。
- 公開 snapshot 側の `backend=tinker` / `micro_batch_size=16` とは異なり、この run は **MLX / micro_batch_size=1** の再現です。
- local300 の改善は **`equation_numeric_deduce 7/15 -> 15/15`** が主因で、他カテゴリは baseline と同一でした。
