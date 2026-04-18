import sys
sys.path.insert(0, 'A-Open-ProgressPrizePublication/nemotron/investigators')
from cryptarithm_deduce import num_to_digits

OPS = [
    lambda a, b: a + b,
    lambda a, b: abs(a - b),
    lambda a, b: a * b,
]

# Row 1 symbols:
# a=BT(backtick), b=!, c=[, d={, e=', f=", g=\, h=>, i=@, j=&
# Example 1: (a,b)*(c,d) -> (e,f,c,a) 4-char
# Example 2: (g,e)*(e,h) -> (b,c,i) 3-char
# Example 3: (g,e) op- (b,a) -> (g,g) 2-char
# Example 4: (a,b)*(g,j) -> (e,i,e,d) 4-char
# Query: (c,c) op- (b,e) -> ?

results = []
for g in range(10):
  for e in range(10):
    for b in range(10):
      for a in range(10):
        # ex3
        for op_minus in range(3):
          if op_minus == 0: res3 = (g*10+e) + (b*10+a)
          elif op_minus == 1: res3 = abs((g*10+e) - (b*10+a))
          else: res3 = (g*10+e) * (b*10+a)
          target3 = g*11
          if res3 != target3 or not (10 <= target3 <= 99):
            continue
          
          for h in range(10):
            # ex2: (g*10+e)*(e*10+h) = b*100+c*10+i
            product2 = (g*10+e) * (e*10+h)
            if not (100 <= product2 <= 999):
              continue
            first2 = product2 // 100
            c_val = (product2 // 10) % 10
            i_val = product2 % 10
            if first2 != b:
              continue
            
            lv1 = a*10 + b
            for d_val in range(10):
              rv1 = c_val*10 + d_val
              product1 = lv1 * rv1
              if not (1000 <= product1 <= 9999):
                continue
              dig1 = [product1//1000, (product1//100)%10, (product1//10)%10, product1%10]
              if dig1[0] != e or dig1[2] != c_val or dig1[3] != a:
                continue
              f_val = dig1[1]
              
              for j_val in range(10):
                rv4 = g*10 + j_val
                product4 = lv1 * rv4
                if not (1000 <= product4 <= 9999):
                  continue
                dig4 = [product4//1000, (product4//100)%10, (product4//10)%10, product4%10]
                if dig4[0] != e or dig4[1] != i_val or dig4[2] != e or dig4[3] != d_val:
                  continue
                
                # Valid assignment found
                # Build digit->symbol map (first occurrence wins for unique)
                sym_chars = ['`', '!', '[', '{', "'", '"', '\\', '>', '@', '&']
                sym_vals  = [a,    b,  c_val, d_val, e, f_val, g, h, i_val, j_val]
                d2s2 = {}
                for sv, sc in zip(sym_vals, sym_chars):
                  if sv not in d2s2:
                    d2s2[sv] = sc
                
                lq = c_val*10 + c_val
                rq = b*10 + e
                if op_minus == 0: resq = lq + rq
                elif op_minus == 1: resq = abs(lq - rq)
                else: resq = lq * rq
                
                rd = num_to_digits(resq)
                ans_parts = []
                ok = True
                for dv in rd:
                  if dv not in d2s2:
                    ok = False; break
                  ans_parts.append(d2s2[dv])
                
                if ok:
                  ans = ''.join(ans_parts)
                  op_name = ['add','abs_diff','mul'][op_minus]
                  results.append((a,b,c_val,d_val,e,f_val,g,h,i_val,j_val,op_name,ans))

print(f"Total valid assignments: {len(results)}")
for r in results[:20]:
  a,b,c,dd,e,f,g,h,i,j,op,ans = r
  print(f"  BT={a} !={b} [={c} {{={dd} '={e} \"={f} \\={g} >={h} @={i} &={j} op-={op} query_ans={repr(ans)}")
