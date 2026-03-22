Inconsistency in Evaluation metric

4
In the Evaluation section of overview page, the parameters mentioned are:

max_tokens = 7680
max_num_seqs = 64
max_model_len = 8192
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