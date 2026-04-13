Training Nemotron-3-Nano-30B-A3B-BF16 with rank 32 LoRA on length 8192 sequences
I want to understand the theoretical limitations when training Nemotron-3-Nano-30B-A3B-BF16 with rank 32 LoRA on length 8192 sequences.

I have not proven that any of the configurations listed here works in practice. I am making my own training implementation, and I want to understand whether my inefficiencies are avoidable with better implementation. Please help me check if I have missed any theoretical limits, thanks!

This table calculates how much memory is needed to train Nemotron-3-Nano-30B-A3B-BF16 with different microbatch sizes (μ). Larger microbatch sizes can improve hardware utilization and speed up training, but only if they fit in memory [1].

Component	Formula	μ=1	μ=4	μ=16	μ=64
Base model weights (BF16)	W × 2	63.6 GB	63.6 GB	63.6 GB	63.6 GB
LoRA adapter weights (FP32)	P × 4	3.5 GB	3.5 GB	3.5 GB	3.5 GB
LoRA gradients (FP32)	P × 4	3.5 GB	3.5 GB	3.5 GB	3.5 GB
Optimizer m + v (FP32)	P × 8	7.1 GB	7.1 GB	7.1 GB	7.1 GB
CUDA context & buffers	~3 GB	3.0 GB	3.0 GB	3.0 GB	3.0 GB
Checkpointed layer inputs	L × μ × S × H × 2	2.3 GB	9.2 GB	36.6 GB	146.6 GB
Peak intra-layer intermediates	μ × S × D × 2	331 MB	1.3 GB	5.3 GB	21.2 GB
Logits — unchunked	μ × S × V × 2	2.1 GB	8.6 GB	34.4 GB	137.4 GB
Logits — fused CE	≈ 0	0	0	0	0
TOTAL (unchunked logits)		85.6 GB	99.9 GB	157.1 GB	386.0 GB
TOTAL (fused CE)		83.4 GB	91.3 GB	122.8 GB	248.6 GB
LoRA parameters
Layer type	Weight name	Shape	per adapter	× count	typical	possible
Attention	q_proj	[2688, 4096]	217,088	× 6	1.30M	1.30M
k_proj	[2688, 256]	94,208	× 6	565,248	565,248
v_proj	[2688, 256]	94,208	× 6	565,248	565,248
o_proj	[4096, 2688]	217,088	× 6	1.30M	1.30M
SUBTOTAL				3.74M	3.74M
Mamba-2	in_proj	[2688, 12864]	497,664	× 23	11.45M	11.45M
out_proj	[5376, 2688]	258,048	× 23	5.94M	5.94M
conv1d	[5376, 1, 4]	—	× 23	—	—
dt_bias	[64]	—	× 23	—	—
A_log	[64]	—	× 23	—	—
D	[64]	—	× 23	—	—
SUBTOTAL				17.38M	17.38M
MoE routed	experts.{j}.fc1	[2688, 1856]	145,408	× 2944	428.08M	428.08M
experts.{j}.fc2	[1856, 2688]	145,408	× 2944	428.08M	428.08M
SUBTOTAL				856.16M	856.16M
MoE shared	shared_experts.fc1 *	[2688, 3712]	204,800	× 23	—	4.71M
shared_experts.fc2 *	[3712, 2688]	204,800	× 23	—	4.71M
SUBTOTAL				—	9.42M
MoE router	gate	[2688, 128]	90,112	× 23	—	2.07M
Output	lm_head	[2688, 131072]	4,280,320	× 1	—	4.28M
Embedding	embed_tokens	[131072, 2688]	4,280,320	× 1	—	4.28M
All layers	norm (RMSNorm)	[2688]	—	× 104	—	—
TOTAL					877.28M	897.33M
FP32 size					3.51 GB	3.59 GB
Training throughput
Training throughput
The forward pass is 3.5B active parameters × 8192 sequence length × 2 = 57 TFLOP. With gradient checkpointing, the backward pass is 3× the forward (recompute forward, compute activation gradients, compute weight gradients) = 171 TFLOP [5]. Each forward-backward pass requires 228 TFLOP per sample.

GPU	BF16 TFLOPS	HBM bandwidth	Critical arithmetic intensity (FLOPs/byte)
H200	990	4.8 TB/s	206
RTX Pro 6000	252	1.15 TB/s	219
If training achieves 100% compute efficiency, it will be able to process one sequence in 228 / 990 = 0.23 seconds on a H200 or 228 / 252 0.90 seconds on a RTX Pro 6000.

However, you do not get 100% compute efficiency. I am still understanding why. Papers usually report a MFU of 30% - 40%.

Glossary
Symbol	Meaning	Value
μ	microbatch size	samples per forward/backward; B = μ × grad accumulation steps
S	sequence length	8,192 tokens per sample
V	vocabulary size	131,072 possible output tokens
H	hidden dimension	2,688
L	number of layers	52 (23 Mamba-2 + 23 MoE + 6 GQA attention)
R	LoRA rank	32
B	global batch size	64
W	base model params	31.8B
P	LoRA trainable params	886.7M
D	MoE intra-layer width	20,224 = 6 (active experts per token) × 1856 (expert FFN intermediate) + 3712 (shared expert intermediate) + 2×2688
Observations
Notebooks on Kaggle has access to GPU RTX Pro 6000, which has 96GB VRAM. Apparently it can barely fit a microbatch size of 1 or 4 [2].
unsloth uses fused cross entropy to avoid the memory requirement for storing the logits for the microbatch [3].
Adapter weights are FP32 (3GB), even as the model is in BF16
Nemotron supports Flash Attention, which means it does not require quadratic memory for the attention mechanism [4].
References
[1] https://unsloth.ai/docs/get-started/fine-tuning-llms-guide/lora-hyperparameters-guide#effective-batch-size
[2] https://unsloth.ai/docs/models/nemotron-3#fine-tuning-nemotron-3-and-rl
[3] https://unsloth.ai/docs/blog/500k-context-length-fine-tuning#unsloth-loss-refactoring-chunk-and-fuse
[4] https://github.com/huggingface/transformers/pull/44390/changes
[5] https://jax-ml.github.io/scaling-book/transformers/ — training FLOPs: 6N without checkpointing, 8N with; arithmetic intensity and roofline model
[6] Gu & Dao, "Mamba: Linear-Time Sequence Modeling with Selective State Spaces" (2023), https://arxiv.org/abs/2312.00752 — "most operations (except matrix multiplication) are bounded by memory bandwidth"; hardware-aware scan fuses in SRAM
[7] Gale et al., "MegaBlocks: Efficient Sparse Training with Mixture-of-Experts" (2022), https://arxiv.org/abs/2211.15841 — Megatron-LM sustains 21–48% of peak; MoE padding overhead forces 2×–8× smaller microbatches
[8] https://github.com/stas00/ml-engineering/blob/master/training/performance/README.md — individual matmul kernels achieve 72–77% of peak; end-to-end single-GPU training achieves 8–20% MFU due to non-matmul overhead between kernels

---
Nguyen
Posted 9 days ago

· 506th in this Competition

I can only train with a μ=1 and a length of 16384 in 1XH200, each step taking ~22s with a gradient cumulative with B=16. Are you using packing?

cc: @huikang


Reply

React
Tong Hui Kang
Topic Author
Posted 9 days ago

· 6th in this Competition

There is no point training with a length of 16384 since the limit is 8192.

If you limit to 8192, you should be able to train with μ=2 I guess?


Reply

React
Nguyen
Posted 9 days ago

· 506th in this Competition

Ah, I mean is packing with a length of 16k, it equivalent to a mini-batch of 2 x 8192 if your data only contains data with a max length of 8192. What I want to mention is that the mini batch size you mentioned in Training throughput, for example 4x or 16x8192, seems to result in OOM (no offload weight or activation), as far as I understand.


Reply

React
Tong Hui Kang
Topic Author
Posted 9 days ago

· 6th in this Competition

Thanks for sharing your experience. I have not proven that any of the configuration works, if it OOMs I think it is good to understand whether is it an implementation issue or is there a theoretical limitation. If there is a theoretical limitation I want to write it down.


Reply

React
Nguyen
Posted 9 days ago

· 506th in this Competition

GPU	Max length	peak vram(GB)
H100	1x3000	78
H200	1x8192	104
H200	1x16384	138
Above is my exp when train nemotron use megatron, maybe it can help.


Reply

React
Tong Hui Kang
Topic Author
Posted 9 days ago

· 6th in this Competition

Probably you can ask Claude Code to break down what is making up the 104GB, and which components is an implementation inefficiency, or is there a theoretical limitation.