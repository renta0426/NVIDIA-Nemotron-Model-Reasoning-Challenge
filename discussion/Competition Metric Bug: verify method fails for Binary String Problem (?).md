Competition Metric Bug: verify method fails for Binary String Problem (?)
Repository note: this discussion records a possible public metric implementation bug, but it does not replace the repository competition contract. In this repo, the authoritative evaluation and submission contract remains the top-level `README.md` (`max_lora_rank = 32`, `max_tokens = 7680`, `top_p = 1.0`, `temperature = 0.0`, `max_num_seqs = 64`, `gpu_memory_utilization = 0.85`, `max_model_len = 8192`, final artifact `submission.zip`).

Binary string answers (e.g. "11111011") are parsed as decimal integers by float(), so verify() uses numeric 1% tolerance instead of exact string matching; meaning "11111011" and "11111000" are scored as equal.

I made a notebook with minimal reproducible examples: https://www.kaggle.com/code/gerwynng/competition-metric-verify-method-bug?scriptVersionId=305629662


Ryan Holbrook
Kaggle Staff
Posted 16 hours ago

Thanks for the heads up. I will investigate and update the metric as needed.


Reply

React
Tong Hui Kang
Posted a day ago

· 10th in this Competition

It also classifies 00000001 and 0001 to be the same


Reply

React
