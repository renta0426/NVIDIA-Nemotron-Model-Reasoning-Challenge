Are problem types the same for train and test?
Repository note: this discussion is useful context, but it does not replace the repository competition contract. In this repo, the authoritative evaluation and submission contract remains the top-level `README.md` (`max_lora_rank = 32`, `max_tokens = 7680`, `top_p = 1.0`, `temperature = 0.0`, `max_num_seqs = 64`, `gpu_memory_utilization = 0.85`, `max_model_len = 8192`, final artifact `submission.zip`). Treat comments below as discussion context, not as overrides of the README or as a guarantee about the hidden evaluation set that replaces the visible sample test file.

There appear to be six different problem types in the training set:

- numbers are secretly converted into a different numeral system
- the gravitational constant has been secretly changed
- a secret set of transformation rules is applied to equations
- secret encryption rules are used on text
- a secret bit manipulation rule transforms 8-bit binary numbers
- a secret unit conversion is applied to measurements

Are these the same set of problem types that appear in the test set? The approach to this competition is completely different depending on whether we are looking at all new question types or not so it would be helpful to know the answer to this question.



Ryan Holbrook
Kaggle Staff
Posted 7 days ago

Yes, they are the same. The distribution should be roughly similar as well.


Reply

React
Yuchen20
Posted 6 days ago

· 320th in this Competition

Yes, they are the same. The distribution should be roughly similar as well.

That said, wouldn’t it be possible that we can produce some simple programmatic approach that works for a whole class of similar problems, so the model can read the answer from the function output, instead of actually requiring reasoning?

For example, for a problem like this:

In Alice's Wonderland, a secret unit conversion is applied to measurements. For example:
14.89 m becomes 21.91
9.37 m becomes 13.79
5.73 m becomes 8.43
26.82 m becomes 39.46
Now, convert the following measurement: 23.28 m
one could easily write a script like:

import re

text = """
In Alice's Wonderland, a secret unit conversion is applied to measurements. For example:
14.89 m becomes 21.91
9.37 m becomes 13.79
5.73 m becomes 8.43
26.82 m becomes 39.46
Now, convert the following measurement: 23.28 m
"""

# Extract training pairs like: 14.89 m becomes 21.91
pairs = [(float(a), float(b)) for a, b in re.findall(r'(\d+\.\d+)\s*m\s*becomes\s*(\d+\.\d+)', text)]

# Estimate conversion factor by averaging b/a
factor = sum(b / a for a, b in pairs) / len(pairs)

# Extract the final value to convert
target = float(re.search(r'convert the following measurement:\s*(\d+\.\d+)\s*m', text, re.I).group(1))

# Compute Wonderland value
result = target * factor

print("pairs:", pairs)
print("target:", target)
print("wonderland value:", round(result, 2))
which derives:

pairs: [(14.89, 21.91), (9.37, 13.79), (5.73, 8.43), (26.82, 39.46)]

target: 23.28

wonderland value: 34.25
Then the result could simply be appended to the prompt, given that prompt engineering is allowed.


Reply

React
KCLamm
Posted 6 days ago

Seems to me that there is a fixed pipeline for the model evaluation, in which the only thing kagglers are supposed to change is the LoRA part. The 'you can experiment with: prompting strategies, …' part in the rules is followed by 'Participants may use any training framework, tooling, or workflow to produce their LoRA adapter,' may be indicating the prompt engineering thing mentioned is about training LoRA only.


Reply

React
Ryan Holbrook
Kaggle Staff
Posted 6 days ago

Right, you can't actually change the inference prompt or call out to Python scripts. All you're able to do is submit a LoRA adapter.


Reply

1
Alex4138
Posted 5 days ago

what eval are people using for the leaderboard, the train.csv alice set?


Reply

React
Gerwyn
Posted 5 days ago

· 192nd in this Competition

This leaderboard is calculated with approximately 50% of the test data. The final results will be based on the other 50%, so the final standings may be different.
