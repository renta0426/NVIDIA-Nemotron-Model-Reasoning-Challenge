import sys
sys.path.insert(0, 'A-Open-ProgressPrizePublication/nemotron/investigators')
from cryptarithm_deduce import Solver, solve_problem, OPS, num_to_digits

OP_NAMES = ["add", "abs_diff", "mul", "concat", "rev_concat"]


def show_result(row_id, data):
    ans, (mapping, op_info) = solve_problem(data)
    print("\n" + "="*60)
    print("ROW: " + row_id)
    print("="*60)
    if ans is None:
        print("  NO SOLUTION FOUND")
        return

    print("Answer: " + str(ans))
    print("\nSymbol->Digit mapping:")
    for s in sorted(mapping.keys()):
        print("  " + repr(s) + " -> " + str(mapping[s]))
    print("\nOperator->Operation mapping:")
    for op in sorted(op_info.keys()):
        print("  " + repr(op) + " -> " + op_info[op])

    op_funcs = {
        "add":        lambda a, b: (a + b,     str(a)+"+"+str(b)+"="+str(a+b)),
        "abs_diff":   lambda a, b: (abs(a-b),  "|"+str(a)+"-"+str(b)+"|="+str(abs(a-b))),
        "mul":        lambda a, b: (a * b,     str(a)+"*"+str(b)+"="+str(a*b)),
        "concat":     lambda a, b: (a*100+b,   "concat("+str(a)+","+str(b)+")="+str(a*100+b)),
        "rev_concat": lambda a, b: (b*100+a,   "revcat("+str(a)+","+str(b)+")="+str(b*100+a)),
    }

    rev_map = {}
    for sym, dig in mapping.items():
        if dig not in rev_map:
            rev_map[dig] = sym

    print("\nExamples verification:")
    for ex in data["examples"]:
        inp = ex["input_value"]
        out = ex["output_value"]
        s0, s1, op_sym, s3, s4 = inp[0], inp[1], inp[2], inp[3], inp[4]
        d0 = mapping.get(s0, "?")
        d1 = mapping.get(s1, "?")
        d3 = mapping.get(s3, "?")
        d4 = mapping.get(s4, "?")
        op_name = op_info.get(op_sym, "?")
        if (isinstance(d0, int) and isinstance(d1, int)
                and isinstance(d3, int) and isinstance(d4, int)
                and op_name in op_funcs):
            lv = d0*10 + d1
            rv = d3*10 + d4
            res_val, calc_str = op_funcs[op_name](lv, rv)
            if op_name in ("concat", "rev_concat"):
                rd = (res_val//1000, (res_val//100) % 10,
                      (res_val//10) % 10, res_val % 10)
            else:
                rd = num_to_digits(res_val)
            result_syms = "".join(rev_map.get(d, "?") for d in rd)
            line = ("  " + repr(inp) + " = " + repr(out) + ":  "
                    + repr(s0) + "=" + str(d0) + " "
                    + repr(s1) + "=" + str(d1) + "  op=" + op_name + "  "
                    + repr(s3) + "=" + str(d3) + " "
                    + repr(s4) + "=" + str(d4) + "  "
                    + calc_str + "  ->" + result_syms)
            print(line)
        else:
            print("  " + repr(inp) + " = " + repr(out)
                  + "  (mapping incomplete for op=" + str(op_name) + ")")

    q = data["question"]
    qs0, qs1, qop, qs3, qs4 = q[0], q[1], q[2], q[3], q[4]
    d0 = mapping.get(qs0, "?")
    d1 = mapping.get(qs1, "?")
    d3 = mapping.get(qs3, "?")
    d4 = mapping.get(qs4, "?")
    op_name = op_info.get(qop, "?")
    print("\nQuery: " + repr(q))
    if (isinstance(d0, int) and isinstance(d1, int)
            and isinstance(d3, int) and isinstance(d4, int)
            and op_name in op_funcs):
        lv = d0*10 + d1
        rv = d3*10 + d4
        res_val, calc_str = op_funcs[op_name](lv, rv)
        if op_name in ("concat", "rev_concat"):
            rd = (res_val//1000, (res_val//100) % 10,
                  (res_val//10) % 10, res_val % 10)
        else:
            rd = num_to_digits(res_val)
        result_syms = "".join(rev_map.get(d, "?") for d in rd)
        print("  left=" + repr(qs0) + "=" + str(d0)
              + " " + repr(qs1) + "=" + str(d1)
              + "  =>  " + str(lv))
        print("  right=" + repr(qs3) + "=" + str(d3)
              + " " + repr(qs4) + "=" + str(d4)
              + "  =>  " + str(rv))
        print("  op=" + op_name + "  " + calc_str)
        print("  digit tuple: " + str(rd))
        print("  symbols: " + result_syms)
        print("  ANSWER: " + str(ans))


# ─── ROW 00457d26 ───
row1 = {
    "examples": [
        {"input_value": "`!*[{",  "output_value": "'\"[`"},
        {"input_value": "\\'*'>", "output_value": "![@"},
        {"input_value": "\\'-!`", "output_value": "\\\\"},
        {"input_value": "`!*\\&", "output_value": "'@'{"},
    ],
    "question": "[[-!'",
}

# ─── ROW 035c4c40 ───
row2 = {
    "examples": [
        {"input_value": "#>*%<", "output_value": "/(``"},
        {"input_value": "/?-`<", "output_value": "-<"},
        {"input_value": "|`->(", "output_value": "-/?"},
        {"input_value": "##*|#", "output_value": "((#"},
        {"input_value": ">`*|>", "output_value": "/<|"},
    ],
    "question": "?<-'#",
}

# ─── ROW 05bd2dab ───
BS = chr(92)
row3 = {
    "examples": [
        {"input_value": "}/{/&",         "output_value": "$}"},
        {"input_value": "}}^(!",         "output_value": "($})"},
        {"input_value": "($[)&",         "output_value": "/!"},
        {"input_value": "(}^$$",         "output_value": "(!}?"},
        {"input_value": "(" + BS + "^?}", "output_value": "(($/"},
    ],
    "question": "'&[?!",
}

show_result("00457d26", row1)
show_result("035c4c40", row2)
show_result("05bd2dab", row3)
