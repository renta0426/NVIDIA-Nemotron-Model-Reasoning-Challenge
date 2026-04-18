import sys
sys.path.insert(0, 'A-Open-ProgressPrizePublication/nemotron/investigators')

from cryptarithm_deduce import Solver, solve_problem, is_concat, OPS, num_to_digits

BT = chr(96)   # backtick
BS = chr(92)   # backslash

# Row 1 data
row1_data = {
    "examples": [
        {"input_value": BT+"!*[{",       "output_value": "'" + chr(34) + "[" + BT},
        {"input_value": BS+"'*'>",       "output_value": "![@"},
        {"input_value": BS+"'-!"+BT,     "output_value": BS+BS},
        {"input_value": BT+"!*"+BS+"&",  "output_value": "'@'{"},
    ],
    "question": "[[-!'",
}

# Parse examples for row 1
print("=== ROW 1 PARSE ===")
for ex in row1_data["examples"]:
    inp = ex["input_value"]
    out = ex["output_value"]
    ex_tuple = (inp[0], inp[1], inp[2], inp[3], inp[4], tuple(out))
    s0,s1,op,s3,s4,rsyms = ex_tuple
    print(f"  s0={repr(s0)} s1={repr(s1)} op={repr(op)} s3={repr(s3)} s4={repr(s4)} -> result={rsyms}")
    # Check feasibility
    rlen = len(rsyms)
    feasible = []
    if rlen <= 3: feasible.append("add")
    if rlen <= 2: feasible.append("abs_diff")
    if rlen <= 4: feasible.append("mul")
    if rlen == 4: feasible.append("concat"); feasible.append("rev_concat")
    print(f"    rlen={rlen} feasible_ops={feasible}")
    print(f"    is_concat={is_concat(ex_tuple)}")

