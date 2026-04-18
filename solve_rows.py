import sys
sys.path.insert(0, 'A-Open-ProgressPrizePublication/nemotron/investigators')

from cryptarithm_deduce import solve_problem

BT = '`'   # backtick
BS = '\\'  # backslash

# ============================================================
# Row 1: id=00457d26
# After unescaping \\->\  in user-provided text:
#  ex1: input `!*[{   output '"[`   (5 chars -> 4 chars: ', ", [, `)
#  ex2: input \'*'>   output ![@    (5 chars -> 3 chars)
#  ex3: input \'-!`   output \\     (5 chars -> 2 chars: two backslashes)
#  ex4: input `!*\&   output '@'{   (5 chars -> 4 chars)
#  query: [[-!'

row1_data = {
    "examples": [
        {"input_value": BT+"!*[{",       "output_value": "'\"["+BT},
        {"input_value": BS+"'*'>",       "output_value": "![@"},
        {"input_value": BS+"'-!"+BT,     "output_value": BS+BS},
        {"input_value": BT+"!*"+BS+"&",  "output_value": "'@'{"},
    ],
    "question": "[[-!'",
}

# ============================================================
# Row 2: id=035c4c40
# #>*%< = /(``    -> s0=#, s1=>, op=*, s3=%, s4=<  out: /, (, `, `  (4 chars)
# /?-`< = -<      -> s0=/, s1=?, op=-, s3=`, s4=<  out: -, <  (2 chars)
# |`->( = -/?     -> s0=|, s1=`, op=-, s3=>, s4=(  out: -, /, ?  (3 chars)
# ##*|# = ((#     -> s0=#, s1=#, op=*, s3=|, s4=#  out: (, (, #  (3 chars)
# >`*|> = /<|     -> s0=>, s1=`, op=*, s3=|, s4=>  out: /, <, |  (3 chars)
# query: ?<-'#

row2_data = {
    "examples": [
        {"input_value": "#>*%<",   "output_value": "/("+BT+BT},
        {"input_value": "/?-"+BT+"<", "output_value": "-<"},
        {"input_value": "|"+BT+"->(", "output_value": "-/?"},
        {"input_value": "##*|#",   "output_value": "((#"},
        {"input_value": ">"+BT+"*|>", "output_value": "/<|"},
    ],
    "question": "?<-'#",
}

# ============================================================
# Row 3: id=05bd2dab
# Original prompts (interpreting (\^?} with backslash):
# /}/{/& = $}      -> user shows "/ } / { / &" which is 6 chars - likely /}{/& = 5 chars
#                     s0=/, s1=}, op={, s3=/, s4=&  out: $, }  (2 chars)
# }}^(! = ($})     -> s0=}, s1=}, op=^, s3=(, s4=!  out: (, $, }, )  (4 chars)
# ($[)& = /!       -> s0=(, s1=$, op=[, s3=), s4=&  out: /, !  (2 chars)
# (}^$$ = (!}?     -> s0=(, s1=}, op=^, s3=$, s4=$  out: (, !, }, ?  (4 chars)
# (\^?} = (($/ or  -> if BS in input: s0=(, s1=\, op=^, s3=?, s4=}  out: (, (, $, /  (4 chars)
# '&[?!            -> query: s0=', s1=&, op=[, s3=?, s4=!

# Note: user wrote "/}/{/&" - let's interpret as "/}{/&" = 5 chars
row3_data = {
    "examples": [
        {"input_value": "/}{/&",       "output_value": "$}"},
        {"input_value": "}}^(!",       "output_value": "($})"},
        {"input_value": "($[)&",       "output_value": "/!"},
        {"input_value": "(}^$$",       "output_value": "(!}?"},
        {"input_value": "("+BS+"^?}",  "output_value": "(($/" },
    ],
    "question": "'&[?!",
}

print("=== Row 1 examples ===")
for e in row1_data["examples"]:
    print(f"  inp={repr(e['input_value'])} ({len(e['input_value'])}) out={repr(e['output_value'])} ({len(e['output_value'])})")
print(f"  query={repr(row1_data['question'])}")

print("\n=== Row 2 examples ===")
for e in row2_data["examples"]:
    print(f"  inp={repr(e['input_value'])} ({len(e['input_value'])}) out={repr(e['output_value'])} ({len(e['output_value'])})")
print(f"  query={repr(row2_data['question'])}")

print("\n=== Row 3 examples ===")
for e in row3_data["examples"]:
    print(f"  inp={repr(e['input_value'])} ({len(e['input_value'])}) out={repr(e['output_value'])} ({len(e['output_value'])})")
print(f"  query={repr(row3_data['question'])}")

print("\n=== Solving Row 1 ===")
ans1, info1 = solve_problem(row1_data)
print(f"  answer={repr(ans1)}")
print(f"  mapping={info1[0]}")
print(f"  ops={info1[1]}")

print("\n=== Solving Row 2 ===")
ans2, info2 = solve_problem(row2_data)
print(f"  answer={repr(ans2)}")
print(f"  mapping={info2[0]}")
print(f"  ops={info2[1]}")

print("\n=== Solving Row 3 ===")
ans3, info3 = solve_problem(row3_data)
print(f"  answer={repr(ans3)}")
print(f"  mapping={info3[0]}")
print(f"  ops={info3[1]}")
