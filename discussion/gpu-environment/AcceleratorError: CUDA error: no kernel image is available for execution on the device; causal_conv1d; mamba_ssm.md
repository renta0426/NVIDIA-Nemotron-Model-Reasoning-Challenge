AcceleratorError: CUDA error: no kernel image is available for execution on the device; causal_conv1d; mamba_ssm
Repository note: this discussion records GPU environment troubleshooting, but it does not replace the repository competition contract. In this repo, the authoritative evaluation and submission contract remains the top-level `README.md` (`max_lora_rank = 32`, `max_tokens = 7680`, `top_p = 1.0`, `temperature = 0.0`, `max_num_seqs = 64`, `gpu_memory_utilization = 0.85`, `max_model_len = 8192`, final artifact `submission.zip`). Treat environment guidance below as operational context rather than as overrides of the README evaluation or submission rules.

On Kaggle notebook runtime GPU RTX Pro 6000, fine-tuning metric/nemotron-3-nano-30b-a3b-bf16/transformers/default fails at trainer.train() with:

AcceleratorError: CUDA error: no kernel image is available for execution on the device

The actual failing call in the traceback is:

causal_conv1d_cuda.causal_conv1d_fwd(…)

from Kaggle’s preinstalled causal_conv1d / mamba_ssm path.

This looks like the CUDA extension was built without support for the assigned GPU architecture. Model load works; the crash starts on the first training forward pass.

I have made a public notebook documenting this: https://www.kaggle.com/code/antonkratz/nvidia-nemotron-finetune-ipynb

I already spent over 10 GPU hours on this issue.

Can you confirm whether the GPU RTX Pro 6000 runtime image is missing a compatible build of causal_conv1d / mamba_ssm for this competition?

Tricks like turning internet off/on and then trying to install did not work for me. This issue should be fixed in the base environment I think.


aemad
Posted a day ago

check this notebook> it applies a Triton ptxas fix https://www.kaggle.com/code/kienngx/nvidia-nemotron-training-copy-run-instantly


Reply

React
Ashish Kumar Jha
Posted 2 days ago

I'm also facing the same issue and the fix for this issue is inprogress refer: https://www.kaggle.com/competitions/nvidia-nemotron-model-reasoning-challenge/discussion/683067, Thanks
