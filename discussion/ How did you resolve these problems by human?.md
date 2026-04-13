[Dataset Hallucination?] How did you resolve these problems by human?
Repository note: this discussion captures puzzle-specific reasoning questions, but it does not replace the repository competition contract. In this repo, the authoritative evaluation and submission contract remains the top-level `README.md` (`max_lora_rank = 32`, `max_tokens = 7680`, `top_p = 1.0`, `temperature = 0.0`, `max_num_seqs = 64`, `gpu_memory_utilization = 0.85`, `max_model_len = 8192`, final artifact `submission.zip`). Treat the examples below as discussion context only, not as overrides of the README evaluation or submission rules.

eeae398e

In Alice's Wonderland, a secret set of transformation rules is applied to equations. Below are a few examples:
63]67 = 4
18]81 = 9
72-22 = 95
64]48 = 16
65]15 = 5
Now, determine the result for: 65/58
When we look at the above question, slash has never appeared in the example. How can we deduce the solution? We know that ] is max(A, B) % min(A, B). No example is given for /

e7cf0394

In Alice's Wonderland, a secret set of transformation rules is applied to equations. Below are a few examples:
88\87 = 7656
30]47 = 3047
52*15 = *37
Now, determine the result for: 97]83
If the symbol works across the "Alice Wonderland", here 30] 47 should not use concat.

It seems that the training dataset has hallucination?

One more thing, 7993452d

In Alice's Wonderland, a secret set of transformation rules is applied to equations. Below are a few examples:
`!-`/ = -[]
[/-:( = -](
^`*<! = :%[!
%/-<< = -/(
!<+^^ = %((
Now, determine the result for: :<-]!
Would anyone share how to reason this kind of problem? I have asked some LLM, they spent many tokens but unable to find the solution. I have also tried to deduce it but in vain.

It seems the data is unbalanced and there are some hallucinations (I think it is severe) in the dataset. 


2
11 Comments
Hotness
 
Comment here. Be patient, be friendly, and focus on ideas. We're all here to learn and improve!
This comment will be made public once posted.


Post Comment
Navneet
Posted a day ago

Cool Dataset @dennisfong


Reply

React
Yuchen20
Posted 2 days ago

· 561st in this Competition

This one is not even solvable, id : 4e840a1a

In Alice's Wonderland, a secret set of transformation rules is applied to equations. Below are a few examples:
58*93 = 152
26*21 = 48
56*65 = 122
Now, determine the result for: 15+53
the + is not even in the multi-shot example


Reply

4
Asadullah Baig
Posted a day ago

· 1022nd in this Competition

In short training on this dataset is not recommended. Either correct it and then train on a different set?


Reply

React
ImperfectKitto
Posted 3 hours ago

· 276th in this Competition

What about the hidden testing dataset?


Reply

React
George
Posted 4 days ago

Who can solve this puzzle? * not present in the examples at all

In Alice's Wonderland, a secret set of transformation rules is applied to equations. Below are a few examples:
81+79 = 511
19-41 = 7
58-87 = 7
Now, determine the result for: 07*79

Reply

React
zoey
Posted 2 days ago

Impossible, my opus-4.6 failed


Reply

React
Đăng Nguyễn Hồng
Posted 5 days ago

· 1186th in this Competition

I found the provided dataset is quite consistent in rule, but some questions indeed unsolvable in mathematical term (such as a query operator is unseen in example equations-there are many cases, but not sure if there are hidden rules to find it out, but until now it seems random to me). By this nature, think about it as a puzzle intead of mathematic :D


Reply

React
Dennis
Topic Author
Posted 4 days ago

· 161st in this Competition

@dangnh0611 , can you give some hints on solving this?

In Alice's Wonderland, a secret set of transformation rules is applied to equations. Below are a few examples:
`!-`/ = -[]
[/-:( = -](
^`*<! = :%[!
%/-<< = -/(
!<+^^ = %((
Now, determine the result for: :<-]!

Reply

React
Đăng Nguyễn Hồng
Posted 4 days ago

· 1186th in this Competition

This result obtained from a LLM by provide a detailed prompt/instructions about how to solve this kind of puzzle. Share you my obtained response, with long-CoT-thinking prunned, strip to the final result:

Digits mapping:

[ = 0, ( = 1
< = 2
/ = 3
] = 4
% = 5
: = 6
! = 7
^ = 8
` = 9
Operators:

+ = standard addition
* = multiplication
- = negative absolute difference (neg_abs_diff)
We can substitute the assigned digits into the equations to verify:

Eq 1: 97 - 93 = -04 → -|79 - 39| = -40 → reverses to -04. (Matches -[])
Eq 2: 03 - 61 = -41 → -|30 - 16| = -14 → reverses to -41. (Matches -]()
Eq 3: 89 * 27 = 6507 → 98 * 72 = 7056 → reverses to 6507. (Matches :%[!)
Eq 4: 53 - 22 = -31 → -|35 - 22| = -13 → reverses to -31. (Matches -/()
Eq 5: 72 + 88 = 511 → 27 + 88 = 115 → reverses to 511. (Matches %(()
PHASE 3: COMPUTE ANSWER We need to determine the result for the query: :< - ]!

Translate the operands: : = 6, < = 2 → 62 ] = 4, ! = 7 → 47
Apply reverse mode (reverse operands): A' = 26 B' = 74
Apply the operator - (neg_abs_diff): -|26 - 74| = -|-48| = -48
Reverse the magnitude for the final result: 48 reversed is 84. Sign is preserved as -84.
Re-encode into symbols: 8 = ^ 4 = ] Result = -^]

Reply

React
This comment has been deleted.

Dennis
Topic Author
Posted 4 days ago

· 161st in this Competition

@dangnh0611 . Thanks for sharing. It inspired me how to teach my model to fine tune.


Reply

React
yash bhaskar
Posted 3 days ago

· 2nd in this Competition

@dangnh0611 Whats the logic here?

In Alice's Wonderland, a secret set of transformation rules is applied to equations. Below are a few examples:
#[!}} = >#
]]-?< = >"]
]](>> = <<
>#-<} = <#>}
Now, determine the result for: >}-<"

Reply

React
Kh0a
Posted 2 days ago

· 269th in this Competition

I asked gemini

Wonderland Math Puzzle Solution
Digits mapping: " = 0, < = 1 ] = 2 # = 3 ? = 4 } = 5 [ = 8 > = 9

Operators: ! = standard addition - = multiplication ( = Greatest Common Divisor (GCD)

We can substitute the assigned digits into the equations to verify:

Eq 1: 38 + 55 = 93 (Matches >#)
Eq 2: 22 * 41 = 902 (Matches >"])
Eq 3: GCD(22, 99) = 11 (Matches <<)
Eq 4: 93 * 15 = 1395 (Matches <#>})
PHASE 3: COMPUTE ANSWER
We need to determine the result for the query: >}-<"

Translate the operands: > = 9, } = 5 → 95 | < = 1, " = 0 → 10
Apply the operator - (multiplication): 95 * 10 = 950
Re-encode into symbols: 9 = >, 5 = }, 0 = " → Result = >}"

Reply

1
MD Mushfirat Mohaimin
Posted 5 days ago

· 348th in this Competition

I found another example.

026106f5

In Alice's Wonderland, a secret set of transformation rules is applied to equations. Below are a few examples:
52{43 = 9
31*15 = 46
37{26 = 11
17{92 = 24
Now, determine the result for: 75*97
Here, we can observe that { acts like a minus for two examples, but for the last example the mapping is NOT a minus.
We can also observe that * seems to act like a plus from the only one example where this operator is used.
So, the answer to 75*97 would be the sum of 75 and 97, which is 172, right?

But, in the dataset, the answer to this prompt is 631

What's the logic behind it?


Reply

React
Dennis
Topic Author
Posted 5 days ago

· 161st in this Competition

I tried to solve it by hand.

31*15=46 seems like 3+1 =4 , 1+5 = 6 , and then concat = 46

@ryanholbrook , could you please provide some insights ? Thanks in advance.


Reply

React
Đăng Nguyễn Hồng
Posted 5 days ago

· 1186th in this Competition

About this example:

{ means digit-reverse then take abs(B-A) -> reverse: 9=34-25; 11=abs(62-73), 42=abs(29-71)
* means reverse -> add -> reverse: 64=51+13; 136=79+57
