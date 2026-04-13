Inconsistency in Evaluation metric

4
In the Evaluation section of overview page, the parameters mentioned are:

max_tokens = 7680
max_num_seqs = 64
max_model_len = 8192
Repository note: this discussion records the public metric-default discrepancy, but it does not replace the repository competition contract. In this repo, the authoritative evaluation and submission contract remains the top-level `README.md` (`max_lora_rank = 32`, `max_tokens = 7680`, `top_p = 1.0`, `temperature = 0.0`, `max_num_seqs = 64`, `gpu_memory_utilization = 0.85`, `max_model_len = 8192`, final artifact `submission.zip`). Treat the abbreviated quote below as discussion context, not as an override of the README.
But, in the evaluation metric notebook (https://www.kaggle.com/code/metric/nvidia-nemotron-metric), the score function is defined with the following default parameters:

max_tokens = 3584
max_num_seqs = 128
max_model_len = 4096
So, which one is actually being used during evaluation?

Ryan Holbrook
KAGGLE STAFF
3 days ago

3
more_vert
The parameters on the Evaluation page override the default parameters.
