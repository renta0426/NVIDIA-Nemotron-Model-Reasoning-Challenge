AcceleratorError: CUDA error: no kernel image is available for execution on the device; causal_conv1d; mamba_ssm
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