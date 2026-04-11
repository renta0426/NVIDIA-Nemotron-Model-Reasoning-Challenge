Strategy to solve 85% of bit manipulation
This is part of my publication for the Open Progress Prize.

I read the 0.73 scoring notebook from @llkh0a / Kh0a.

The approach described in Kh0a's notebook is actually very similar to mine

Use code to write synthetic CoT traces
Train SFT on the synthetic CoT traces
Make the submission
Kh0a reports the following validation score.

Per-category:
  bit_manipulation: 35/160 = 21.88%
  gravity_physics: 160/160 = 100.00%
  numeral_system: 158/158 = 100.00%
  numeric_equation: 51/73 = 69.86%
  symbol_transform: 0/82 = 0.00%
  text_decryption: 145/158 = 91.77%
  unit_conversion: 159/159 = 100.00%
Overall: 708/950 = 74.53%
Weighted CV score: 74.76%
Kh0a's algorithm solves only 35/160 of bit manipulation problems.

I have an algorithm that solves 1364 of 1602 bit manipulation problems (85.1%).

85.1% of 160 is around 136. The additional 136 - 35 = 101 correct solutions will bring the overall score from 708/950 to 809/950 which is approximately 85%, which is the same as my winning submission score.

If Kh0a is actually able to perfectly train the model to generate exactly the chain of thought, Kh0a would have won the progress prize.

I describe my algorithm for bit manipulation here in a separate post. I do not want my main post to have 50% of the content to be on bit manipulation even though it accounts for more than half of the difference with Kh0a's notebook. This also allows me to elaborate more on the bit manipulation problem here.

This task asks to discover a per-bit transformation rule from input-output examples of 8-bit binary numbers.

I consider three possible transformations, each with seven possible values

ROT (rotation)
SHR (shift right)
SHL (shift left)
There are 7 + 7 + 7 = 21 possible transformations.

I consider six possible operations

AND and AND-NOT
OR and OR-NOT
XOR and XOR-NOT
I consider up to three transformations per expression

One-transformation: ROT(4)
Two-transformation: SHL(3) XOR NOT SHL(6)
Three-transformation: (ROT(5) AND NOT SHR(4)) XOR NOT SHL(4)
In the training data alone, there are 622 expressions

One-transformation: 20
Two-transformation: 318
Three-transformation: 284
However, the 622 expressions do not cover all possible expressions.

Consider the following template (ROT(X) AND NOT SHR(Y)) XOR NOT SHL(Z)

There are already 10,584 possible expressions for this template

7 possible values for ROT(X)
6 possible operations for ROT and SHR
7 possible values for SHR(Y)
6 possible operations for ROT+SHR and SHL
7 possible values for SHL(Z)
You are only allowed 7680 tokens for your completion. Even if you spend only one token testing one expression, you will run out of tokens.

Insight
I am still able to solve most of the three-transformation expressions.

This is my key insight — instead of iterating over the possible expressions, I iterate over the possible pairs of input bits that produce the output bit.

For example, (SHL(5) XOR SHR(5)) AND ROT(7) can be read like this

SHL(5)                                      0     1     2  
SHR(5)        5     6     7               
ROT(7)        1     2     3     4     5     6     7     0

Relevant     51    62    73    x4    x5    06    17    20
Operation AND51 AND62 AND73    C0    C0 AND06 AND17 AND20
(Note: it is C0 for constant 0 because the left-hand side of the AND operation is zero)

My algorithm only works if the number of relevant bits for each output is at most 2. I am not able to solve three-transformation expressions involving SHL(x) and SHR(y) where x + y < 8.

One example is (SHL(3) XOR SHR(3)) AND ROT(7)

SHL(3)                          0     1     2     3     4
SHR(3)        3     4     5     6     7              
ROT(7)        1     2     3     4     5     6     7     0

Relevant     31    42    53   064   175    26    37    40
Operation AND31 AND42 AND53   ???   ??? AND26 AND37 AND40
You see that there are output bits that depend on three input bits. My solution does not cover these problems.

Algorithm
I described that the number of expressions is too large to enumerate directly.

I need to test 18 possible unary combinations

8 possible positions
8 possible negated positions
2 possible constants
I need to test 336 possible binary combinations

8 possible positions for the first input
7 possible positions for the second input
6 possible operations
In total, I need to test 354 possible combinations.

I spend around 15 tokens to test each combination

2 tokens to denote the input bit positions
10 tokens for up to 10 possible example test cases
1 bitsum to make matching easier
2 spaces for formatting
more if there is a match
The section looks like this

AND-NOT
01 0100000000 1
12 1001000101 4
23 0100101000 3
34 1000000010 2 match 0
45 0010010000 2 match 1
56 1001000111 5
67 0000000000 a
70 0001010011 4

...

07 0000000000 a
10 1001001111 6
21 0100000000 1
32 1000010001 3
43 0001000100 2
54 1000000010 2 match 0
65 0010010000 2 match 1
76 0101100011 5 match 2

Matching output
0 34 54
1 45 35 65
2 76
3 05
4 absent
5 absent
6 absent
7 absent
The total budget here is 354 * 15 = 5130 tokens.

You notice that in the sequence

Operation AND51 AND62 AND73    I4    I5 AND06 AND17 AND20
The transition between each element is +1/+1.

AND51 -> AND62
So I match from the left and and from the right.

For each binary combination matching the first bit of the output, I add one (modulo 8) to each input index and check if it appears in the second bit of the output, continuing until it does not match.

The matching part of the chain of thought looks like this.

Left
34 45 56x
54 65 76 07x
Best: AND-NOT54 65 76: 3

Right
none
Best: none
The best match is the longest sequence. For tie-breaking, I simply choose the sequence that appears earlier.

After iterating over all the combinations, I choose the operations.

Left longest: 3
Right longest: 5

Right winner: Identity yes, NOT no, Constant no, AND no, OR no, XOR no, AND-NOT no, OR-NOT no, XOR-NOT no
Left winner: Identity no, NOT no, Constant no, AND no, OR no, XOR no, AND-NOT yes, OR-NOT no, XOR-NOT no

Best right: I4 3 2 1 0: 5
Best left: AND-NOT54 65 76: 3

Truncated right: I4 3 2 1 0: 5
Truncated left: AND-NOT54 65 76: 3
Then I submit the result.

Selected
0 AND-NOT54
1 AND-NOT65
2 AND-NOT76
3 I0
4 I1
5 I2
6 I3
7 I4

Applying to 00010010
Input
0 0
1 0
2 0
3 1
4 0
5 0
6 1
7 0
Output
0 AND-NOT54 = AND(0,NOT(0)) = 0
1 AND-NOT65 = AND(1,NOT(0)) = 1
2 AND-NOT76 = AND(0,NOT(1)) = 0
3 I0 = 0
4 I1 = 0
5 I2 = 0
6 I3 = 1
7 I4 = 0

I will now return the answer in \boxed{}
The answer in \boxed{–} is \boxed{01000010}
The full chain of thought is available here baseline/nemotron-unsloth-sft-training/c4a6d52b.txt

I hope this is useful!