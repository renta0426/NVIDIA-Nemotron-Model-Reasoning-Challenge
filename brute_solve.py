"""
Brute-force cryptarithm solver with extended operations.
Tries: add, abs_diff, mul, concat, rev_concat, sub_ab, sub_ba
  with both standard and reversed operands,
  and both standard and reversed result reading,
  with leading-zero padding for arithmetic results.
Non-unique mapping allowed.
"""
import json
from collections import Counter
from itertools import product as iproduct

BS = chr(92)
BT = chr(96)


def num_to_digits_padded(n, length):
    """Convert n to a digit tuple of exactly `length` digits (with leading zeros)."""
    if n < 0:
        return None
    digits = []
    for _ in range(length):
        digits.append(n % 10)
        n //= 10
    if n != 0:
        return None  # doesn't fit in `length` digits
    return tuple(reversed(digits))


# Operations: (name, func) where func(a, b) -> int|None
ARITH_OPS = [
    ("add",        lambda a, b: a + b),
    ("abs_diff",   lambda a, b: abs(a - b)),
    ("mul",        lambda a, b: a * b),
    ("sub_ab",     lambda a, b: a - b),
    ("sub_ba",     lambda a, b: b - a),
]
# Concat ops: (name, func) where func(a, b) -> 4-digit tuple
CONCAT_OPS = [
    ("concat",     lambda a, b: (a//10, a%10, b//10, b%10)),
    ("rev_concat", lambda a, b: (b//10, b%10, a//10, a%10)),
]


def parse_examples(data):
    examples = []
    for ex in data["examples"]:
        inp = ex["input_value"]
        out = ex["output_value"]
        examples.append((inp[0], inp[1], inp[2], inp[3], inp[4], tuple(out)))
    q = data["question"]
    query = (q[0], q[1], q[2], q[3], q[4])
    return examples, query


class ExtSolver:
    def __init__(self, examples, query, answer=None):
        self.examples = examples
        self.query = query
        self.expected_answer = answer
        self.mapping = {}
        self.used = set()
        self.op_assign = {}  # op_sym -> (op_name, rev_ops, rev_res)
        self.answers = Counter()
        self.answer_info = {}

    def solve(self):
        self._process(0)
        if not self.answers:
            return None, {}
        best, _ = self.answers.most_common(1)[0]
        return best, self.answer_info.get(best, {})

    def _vals(self, sym):
        if sym in self.mapping:
            return (self.mapping[sym],)
        return range(10)

    def _assign(self, sym, dig):
        if sym in self.mapping:
            return False if self.mapping[sym] == dig else None
        self.mapping[sym] = dig
        return True

    def _undo(self, sym, was_new):
        if was_new is True:
            del self.mapping[sym]

    def _apply_op(self, op_name, rev_ops, rev_res, s0, s1, s3, s4):
        """Given symbol positions and operation spec, return expected result digit tuple."""
        d0, d1, d3, d4 = (self.mapping.get(s) for s in (s0, s1, s3, s4))
        if any(d is None for d in (d0, d1, d3, d4)):
            return None
        if rev_ops:
            lv = d1 * 10 + d0
            rv = d4 * 10 + d3
        else:
            lv = d0 * 10 + d1
            rv = d3 * 10 + d4

        if op_name in ("concat", "rev_concat"):
            if op_name == "concat":
                rd = (d0//10, d0%10, d3//10, d3%10) if rev_ops else (d0, d1, d3, d4)
                # Actually concat is: result = lv*100 + rv padded to 4 digits
                val = lv * 100 + rv
                rd = (val // 1000, (val // 100) % 10, (val // 10) % 10, val % 10)
            else:
                val = rv * 100 + lv
                rd = (val // 1000, (val // 100) % 10, (val // 10) % 10, val % 10)
            if rev_res:
                rd = rd[::-1]
            return rd
        else:
            func = dict(ARITH_OPS)[op_name]
            val = func(lv, rv)
            if val is None:
                return None
            return val  # return int for arithmetic

    def _process(self, idx):
        if len(self.answers) >= 500:
            return
        if idx == len(self.examples):
            self._compute_query()
            return

        s0, s1, op_sym, s3, s4, rsyms = self.examples[idx]
        rlen = len(rsyms)

        # Determine feasible operations for this result length
        feasible = []
        for op_name, _ in ARITH_OPS:
            feasible.append((op_name, False, False))
            feasible.append((op_name, True,  False))
            feasible.append((op_name, False, True))
            feasible.append((op_name, True,  True))
        for op_name, _ in CONCAT_OPS:
            feasible.append((op_name, False, False))
            feasible.append((op_name, False, True))

        # Filter to operations that can produce rlen-length results
        def op_feasible(op_name, rlen):
            if op_name == "add":
                return rlen <= 3
            elif op_name == "abs_diff":
                return rlen <= 2
            elif op_name == "mul":
                return rlen <= 4
            elif op_name in ("sub_ab", "sub_ba"):
                return rlen <= 2  # can be negative; we'll use padded
            elif op_name in ("concat", "rev_concat"):
                return rlen == 4
            return True

        feasible = [(n, ro, rr) for (n, ro, rr) in feasible if op_feasible(n, rlen)]

        if op_sym in self.op_assign:
            ops_to_try = [self.op_assign[op_sym]]
        else:
            ops_to_try = feasible

        for d0v in self._vals(s0):
            n0 = self._assign(s0, d0v)
            if n0 is None:
                continue
            for d1v in self._vals(s1):
                n1 = self._assign(s1, d1v)
                if n1 is None:
                    continue
                for d3v in self._vals(s3):
                    n3 = self._assign(s3, d3v)
                    if n3 is None:
                        continue
                    for d4v in self._vals(s4):
                        n4 = self._assign(s4, d4v)
                        if n4 is None:
                            continue

                        for (op_name, rev_ops, rev_res) in ops_to_try:
                            if rev_ops:
                                lv = d1v * 10 + d0v
                                rv = d4v * 10 + d3v
                            else:
                                lv = d0v * 10 + d1v
                                rv = d3v * 10 + d4v

                            if op_name in ("concat", "rev_concat"):
                                if op_name == "concat":
                                    val = lv * 100 + rv
                                else:
                                    val = rv * 100 + lv
                                rd = (val // 1000, (val // 100) % 10,
                                      (val // 10) % 10, val % 10)
                                if rev_res:
                                    rd = rd[::-1]
                            else:
                                func = dict(ARITH_OPS)[op_name]
                                val = func(lv, rv)
                                if val is None:
                                    continue
                                # Try with leading-zero padding to match rlen
                                if val < 0:
                                    continue  # skip negative for now
                                rd = num_to_digits_padded(val, rlen)
                                if rd is None:
                                    continue
                                if rev_res:
                                    rd = rd[::-1]

                            if len(rd) != rlen:
                                continue

                            # Try to assign result digits to result symbols
                            assigns = []
                            ok = True
                            for rs, rdig in zip(rsyms, rd):
                                ns = self._assign(rs, rdig)
                                if ns is None:
                                    ok = False
                                    break
                                assigns.append((rs, ns))

                            if ok:
                                op_key = (op_name, rev_ops, rev_res)
                                op_new = op_sym not in self.op_assign
                                if op_new:
                                    self.op_assign[op_sym] = op_key
                                self._process(idx + 1)
                                if op_new:
                                    del self.op_assign[op_sym]

                            for rs, ns in reversed(assigns):
                                self._undo(rs, ns)

                            if len(self.answers) >= 500:
                                break

                        self._undo(s4, n4)
                        if len(self.answers) >= 500:
                            break
                    self._undo(s3, n3)
                    if len(self.answers) >= 500:
                        break
                self._undo(s1, n1)
                if len(self.answers) >= 500:
                    break
            self._undo(s0, n0)
            if len(self.answers) >= 500:
                break

    def _compute_query(self):
        qs0, qs1, qop, qs3, qs4 = self.query
        for s in (qs0, qs1, qs3, qs4):
            if s not in self.mapping:
                return

        d0 = self.mapping[qs0]
        d1 = self.mapping[qs1]
        d3 = self.mapping[qs3]
        d4 = self.mapping[qs4]

        if qop in self.op_assign:
            op_candidates = [self.op_assign[qop]]
        else:
            op_candidates = [(n, ro, rr)
                             for (n, _, _) in ARITH_OPS
                             for ro in (False, True)
                             for rr in (False, True)]
            op_candidates += [(n, False, False) for n, _ in CONCAT_OPS]
            op_candidates += [(n, False, True)  for n, _ in CONCAT_OPS]

        rev_map = {}
        for sym, dig in self.mapping.items():
            if dig not in rev_map:
                rev_map[dig] = sym

        for (op_name, rev_ops, rev_res) in op_candidates:
            if rev_ops:
                lv = d1 * 10 + d0
                rv = d4 * 10 + d3
            else:
                lv = d0 * 10 + d1
                rv = d3 * 10 + d4

            if op_name in ("concat", "rev_concat"):
                if op_name == "concat":
                    val = lv * 100 + rv
                else:
                    val = rv * 100 + lv
                rd = (val // 1000, (val // 100) % 10, (val // 10) % 10, val % 10)
                if rev_res:
                    rd = rd[::-1]
            else:
                func = dict(ARITH_OPS)[op_name]
                val = func(lv, rv)
                if val is None or val < 0:
                    continue
                # Use 1-digit or more natural representation
                if val == 0:
                    rd = (0,)
                else:
                    digits = []
                    tmp = val
                    while tmp > 0:
                        digits.append(tmp % 10)
                        tmp //= 10
                    rd = tuple(reversed(digits))
                if rev_res:
                    rd = rd[::-1]

            parts = []
            ok = True
            for d in rd:
                if d not in rev_map:
                    ok = False
                    break
                parts.append(rev_map[d])
            if not ok:
                continue

            ans = "".join(parts)
            self.answers[ans] += 1
            if ans not in self.answer_info:
                op_info = {k: v for k, v in self.op_assign.items()}
                op_info[qop] = (op_name, rev_ops, rev_res)
                self.answer_info[ans] = (dict(self.mapping), dict(op_info))


def solve_with_answer(row_id, data, expected=None):
    print("\n" + "="*60)
    print("ROW: " + row_id + ("  (expected: " + repr(expected) + ")" if expected else ""))
    print("="*60)

    examples, query = parse_examples(data)
    solver = ExtSolver(examples, query, expected)
    solver.solve()

    print("Top answers: " + str(solver.answers.most_common(5)))
    if not solver.answers:
        print("  NO SOLUTION FOUND")
        return

    # Check if expected is in answers
    if expected and expected in solver.answers:
        print("  Expected answer FOUND: " + repr(expected) + " with count " + str(solver.answers[expected]))
        mapping, op_info = solver.answer_info[expected]
    else:
        best, _ = solver.answers.most_common(1)[0]
        print("  Best answer: " + repr(best))
        mapping, op_info = solver.answer_info.get(best, ({}, {}))

    print("\nSymbol->Digit mapping:")
    for s in sorted(mapping.keys()):
        print("  " + repr(s) + " -> " + str(mapping[s]))

    print("\nOperator assignments:")
    for op in sorted(op_info.keys()):
        v = op_info[op]
        if isinstance(v, tuple):
            op_name, rev_ops, rev_res = v
            print("  " + repr(op) + " -> " + op_name + " (rev_ops=" + str(rev_ops) + ", rev_res=" + str(rev_res) + ")")
        else:
            print("  " + repr(op) + " -> " + str(v))

    # Verify examples
    print("\nVerification:")
    rev_map = {}
    for sym, dig in mapping.items():
        if dig not in rev_map:
            rev_map[dig] = sym

    for ex in data["examples"]:
        inp = ex["input_value"]
        out = ex["output_value"]
        s0_, s1_, op_, s3_, s4_ = inp[0], inp[1], inp[2], inp[3], inp[4]
        d0_ = mapping.get(s0_); d1_ = mapping.get(s1_)
        d3_ = mapping.get(s3_); d4_ = mapping.get(s4_)
        op_spec = op_info.get(op_)
        if op_spec and d0_ is not None and d1_ is not None and d3_ is not None and d4_ is not None:
            if isinstance(op_spec, tuple):
                op_name, rev_ops, rev_res = op_spec
            else:
                op_name, rev_ops, rev_res = op_spec, False, False
            if rev_ops:
                lv_ = d1_ * 10 + d0_
                rv_ = d4_ * 10 + d3_
            else:
                lv_ = d0_ * 10 + d1_
                rv_ = d3_ * 10 + d4_

            if op_name in ("concat", "rev_concat"):
                if op_name == "concat":
                    val_ = lv_ * 100 + rv_
                else:
                    val_ = rv_ * 100 + lv_
                rd_ = (val_//1000, (val_//100)%10, (val_//10)%10, val_%10)
                if rev_res:
                    rd_ = rd_[::-1]
                result_str = "".join(rev_map.get(d, "?") for d in rd_)
                print("  " + repr(inp) + " = " + repr(out) + " : " + op_name + "(" + str(lv_) + "," + str(rv_) + ")=" + str(val_) + " -> " + result_str + ("  OK" if result_str == out else "  MISMATCH"))
            else:
                func = dict(ARITH_OPS)[op_name]
                val_ = func(lv_, rv_)
                if val_ is not None:
                    rlen_ = len(out)
                    rd_ = num_to_digits_padded(val_, rlen_) if val_ >= 0 else None
                    if rd_ and rev_res:
                        rd_ = rd_[::-1]
                    if rd_:
                        result_str = "".join(rev_map.get(d, "?") for d in rd_)
                        print("  " + repr(inp) + " = " + repr(out) + " : " + op_name + "(" + str(lv_) + "," + str(rv_) + ")=" + str(val_) + " -> " + result_str + ("  OK" if result_str == out else "  MISMATCH"))
                    else:
                        print("  " + repr(inp) + " = " + repr(out) + " : " + op_name + "(" + str(lv_) + "," + str(rv_) + ") val=" + str(val_) + " CANT_PAD")
        else:
            print("  " + repr(inp) + " = " + repr(out) + "  (incomplete)")

    # Query
    q = data["question"]
    qs0_, qs1_, qop_, qs3_, qs4_ = q[0], q[1], q[2], q[3], q[4]
    d0_ = mapping.get(qs0_); d1_ = mapping.get(qs1_)
    d3_ = mapping.get(qs3_); d4_ = mapping.get(qs4_)
    op_spec = op_info.get(qop_)
    print("\nQuery: " + repr(q))
    if op_spec and d0_ is not None and d1_ is not None and d3_ is not None and d4_ is not None:
        if isinstance(op_spec, tuple):
            op_name, rev_ops, rev_res = op_spec
        else:
            op_name, rev_ops, rev_res = op_spec, False, False
        if rev_ops:
            lv_ = d1_ * 10 + d0_
            rv_ = d4_ * 10 + d3_
        else:
            lv_ = d0_ * 10 + d1_
            rv_ = d3_ * 10 + d4_
        print("  left=" + str(lv_) + " right=" + str(rv_) + " op=" + op_name + "(rev_ops=" + str(rev_ops) + ",rev_res=" + str(rev_res) + ")")
        if op_name in ("concat", "rev_concat"):
            if op_name == "concat":
                val_ = lv_ * 100 + rv_
            else:
                val_ = rv_ * 100 + lv_
            rd_ = (val_//1000, (val_//100)%10, (val_//10)%10, val_%10)
            if rev_res:
                rd_ = rd_[::-1]
            result_str = "".join(rev_map.get(d, "?") for d in rd_)
            print("  result=" + str(val_) + " -> " + result_str)
        else:
            func = dict(ARITH_OPS)[op_name]
            val_ = func(lv_, rv_)
            if val_ is not None and val_ >= 0:
                if val_ == 0:
                    rd_ = (0,)
                else:
                    digits = []
                    tmp = val_
                    while tmp > 0:
                        digits.append(tmp % 10)
                        tmp //= 10
                    rd_ = tuple(reversed(digits))
                if rev_res:
                    rd_ = rd_[::-1]
                result_str = "".join(rev_map.get(d, "?") for d in rd_)
                print("  result=" + str(val_) + " digits=" + str(rd_) + " -> " + result_str)
            else:
                print("  val=" + str(val_) + " (negative or None)")


# Load from JSONL
for fname, rid in [
    ("A-Open-ProgressPrizePublication/nemotron/problems/00457d26.jsonl", "00457d26"),
    ("A-Open-ProgressPrizePublication/nemotron/problems/035c4c40.jsonl", "035c4c40"),
    ("A-Open-ProgressPrizePublication/nemotron/problems/05bd2dab.jsonl", "05bd2dab"),
]:
    with open(fname) as f:
        data = json.loads(f.readline())
    solve_with_answer(rid, data, expected=data.get("answer"))
