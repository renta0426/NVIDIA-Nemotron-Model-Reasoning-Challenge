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

---

## 補足メモ（日本語）: この戦略で「すべての BIT 問題を安全に CoT 化できる」とは限らない理由

この補足は、この戦略そのものを否定するためではなく、**README.md の評価前提**と、repo 内で進めてきた学習データ分析の観点から、何が強みで、どこに限界があるかを明確にするための整理である。

### 1. README.md 前提で重要なのは「もっともそれっぽい reasoning」ではなく最終 answer の Accuracy

README.md では、このコンペの評価は最終的な **Accuracy** で決まり、モデルは最終 answer を `\boxed{}` に入れて出力することが期待される。したがって、学習時に CoT を付ける目的は、単に長い reasoning を見せることではなく、

- examples から hidden rule を安定して同定させること
- query に同じ rule を適用させること
- 最後の answer を 8-bit binary string として壊さずに出させること

である。

特に binary は `00110100` のような **8 桁固定・leading zero あり・文字列 exact match** のため、数値問題と違って extraction fallback が効きにくい。よって、CoT は長ければ良いわけではなく、**正しい procedure を壊れにくい形で教えること**が重要になる。

### 2. この戦略は強いが、文書の主張自体が「全 BIT 問題を解ける」ではない

この文書自身が述べている通り、この戦略で解けるのは **1602 問中 1364 問、85.1%** である。裏返すと **238 問はこの方法では解けない**。

さらに本文では、自分のアルゴリズムが動く条件として、各出力 bit が高々 2 個までの relevant input bits に依存する場合を想定しており、3 つ以上の input bits に依存する出力 bit がある式、特に `SHL(x)` と `SHR(y)` の組み合わせによって 3-bit dependence が出るケースはカバーできないと明記している。

したがって、この戦略は bit manipulation の大きな部分に効く有力な solver ではあるが、**すべての BIT 問題に対して完全に適用可能な universal solver ではない**。

### 3. 「答えを出せる」と「安全な CoT teacher を作れる」は別問題である

ここが学習設計では非常に重要である。

train.csv には gold answer はあるが、元から gold reasoning text が入っているわけではない。したがって CoT を学習に使うには、あとから synthetic に CoT を作る必要がある。

このとき安全な CoT teacher とは、単に final answer が合っているだけでは足りず、

- prompt の examples 全体と整合すること
- query answer だけでなく **途中の procedure も忠実であること**
- competing rule が残らず、少なくとも teacher として採用するには十分に一意であること

が必要になる。

逆に unsafe な CoT teacher とは、例えば次のようなものである。

- final answer は正しいが、途中で採用した rule が唯一とは言えない
- tie-break や heuristic で選んだ rule を、唯一の正しい推論として書いている
- examples に整合する別の手続きが残っているのに、その競合を無視して一つの探索ログだけを正解として教える

このような CoT は、answer-only より強い supervision であるぶん、間違っていると harmful になりやすい。モデルは「この family ではこの探索をすればよい」と学んでしまうため、実際には underdetermined な row に偽の確信を植え込みやすい。

### 4. この戦略の CoT は「探索ログ型」であり、それ自体が長所でもあり、同時に safety 上の注意点でもある

この文書の戦略で自然に生成される CoT は、候補列挙、matching、left/right の比較、best の選択、selected operations の並び、query への適用、という **探索過程に近い CoT** である。

これは長所でもある。なぜなら、モデルに単なる rule 名だけでなく、**どう候補を絞っていくか**まで学ばせられる可能性があるからである。

一方で、学習用 teacher として見ると、次の注意が必要になる。

- その探索過程は本当に唯一の正解手順なのか
- longest match や earliest tie-break が、学習教師として十分に正当化できるのか
- 同じ answer に到達する別手順が残っていないか

つまり、この strategy の CoT は **solver の内部探索をかなりそのまま見せる**タイプであり、teacher として使うには、その探索自体の faithful 性を別途チェックする必要がある。

### 5. repo の cuda-train-data-analysis-v1 側が重視していたのは、まさにこの「teacher safety」の切り分けである

repo 内の `cuda-train-data-analysis-v1` では、binary を含む train 全体を解析し、行ごとに少なくとも次を区別している。

- `verified_trace_ready`: procedure まで含めて比較的安全に trace teacher へ変換できる
- `answer_only_keep`: final answer supervision は安全だが、trace teacher としては根拠が弱い
- `manual_audit_priority`: 現時点では safe reusable rule が立たず、そのまま CoT 化しない方がよい
- `exclude_suspect`: 規則と gold が衝突する、あるいはラベルが怪しいため混ぜない

この切り分けは、binary では特に重要である。なぜなら binary では、答えが合っても procedure が一意とは限らない row が多く、しかも final formatting failure の影響が大きいからである。

さらに repo の strict な運用では、`verified_trace_ready` の中でも、**query answer だけでなく exact procedure まで一意と見なせる row** をより厳しく抽出し、それだけを exact-trace-safe な CoT seed として扱っている。ここでの考え方は、「CoT は answer-only より強いが、そのぶん fabricated だと危険」というものである。

### 6. したがって、この戦略単独では「全 BIT 問題を安全に CoT 化できる」とは言えない

まとめると、そう言えない理由は 3 つある。

1. この strategy 自体が 85.1% coverage を主張しており、全問解法ではない
2. 本文中で 3-bit dependence を含む一部 family は自分の方法で扱えないと認めている
3. たとえ answer に到達できても、その探索ログが **学習教師として faithful かどうか** は別途検証が必要である

したがって、正確に言うなら、この strategy は

- bit manipulation の大きな部分に効く有力な solver / CoT generator candidate ではある
- しかし、それだけで全 binary row を安全な CoT teacher に変換できる保証はない

という位置づけになる。

### 7. 外部戦略と cuda 側の CoT 生成思想の違い

イメージとしては、次の違いがある。

- この strategy:
  - 候補列挙と絞り込みを含む **探索ログ型 CoT**
  - 「どうやって正解にたどり着いたか」を比較的そのまま見せる
- cuda 側:
  - safety gate を通った rule だけを使う **正規化された procedural CoT**
  - 「確定した exact rule をどう query に適用するか」を短く安定して見せる

どちらが絶対に正しいという話ではない。hard binary に対する探索能力まで教えたいなら、この strategy のような探索ログ型 CoT は魅力がある。一方で、README.md 前提の本番評価では final answer の exactness と boxed formatting が非常に重要なので、unsafe な長い CoT を広く混ぜるのは危険でもある。

### 8. 実務的にはどう使うのがよいか

この strategy を学習に使うなら、単独で全面採用するより、次のように safety gate をかけるのが実務的である。

1. この strategy で候補 rule と探索型 CoT を生成する
2. その rule が examples 全体と query に対してコードで再検証できるか確認する
3. competing procedure が残らない、または teacher として十分に一意な row だけ CoT teacher に採用する
4. 一意な procedure を保証できない row は answer-only に落とす
5. conflict や suspect がある row は学習へ入れない

この運用なら、この strategy は **coverage の高い candidate generator** として非常に有用である。

### 9. Bottom line

この strategy は、bit manipulation を広く高精度に解くための非常に価値ある発想であり、特に「候補式を直接列挙する代わりに output bit を説明する input-bit pair を辿る」という insight は強い。

ただし、学習用 CoT teacher の観点では、

- 全 BIT 問題を一律に安全に CoT 化できるわけではない
- answer correctness と procedure faithfulness は分けて考える必要がある
- binary では final boxed 8-bit output の安定性まで含めて評価すべきである

という条件が付く。

したがって、この strategy は **そのまま万能な teacher generator** というより、**強力な solver / candidate-CoT generator を safety gate の前段に置くもの**として理解するのが最も正確である。