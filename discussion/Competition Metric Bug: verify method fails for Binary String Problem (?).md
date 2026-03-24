Competition Metric Bug: verify method fails for Binary String Problem (?)
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