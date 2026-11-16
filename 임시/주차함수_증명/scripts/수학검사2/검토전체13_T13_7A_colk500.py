import json, math, glob, os
L = 10**21 * 400**10; R = 17**21 * 123**10
print("L", L, "%.6e" % L); print("R", R, "%.6e" % R, L > R)
def B(k): return -(-k*k//4)
dd1 = sum(2*B(k)-2*k for k in range(121,161)); dd2 = sum(2*B(k)-2*k for k in range(161,501))
rr1 = sum(B(k)+1 for k in range(121,161)); rr2 = sum(B(k)+1 for k in range(161,501))
print("direct", dd1, dd2, "ratio", rr1, rr2)
base = r"원고_자료/세션_재계산/column_k500_iv/res"
for k in (121,161,500):
    p = os.path.join(base, f"k{k}.json")
    d = json.load(open(p, encoding="utf-8"))
    print(k, {a:b for a,b in d.items() if not isinstance(b,(list,dict))})
print(open(r"원고_자료/세션_재계산/column_k500_iv/summary_out.txt", encoding="utf-8").read()[:3000])
