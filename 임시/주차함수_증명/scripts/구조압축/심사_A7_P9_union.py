# -*- coding: utf-8 -*-
"""심사 A7 — P9 보조 검산: F4 §5가 출발점으로 적은 합집합 상계
   1 - s_N(k) <= sum_{m>k} theta_{N+1}(m) (m-k)/m,  theta_{N+1}(m) = Ren(N+1-m) Bor(m)/Bor(N+1)  (R4의 사슬 통과 확률)
가 N = k+q-1 에서 q^{3/2}/(2k) 를 주는지(상수 1/2가 그 길에서 나오는지)를 k=10^4, 10^5 와 극한에서 센다.
Ren(0)은 1로 둔다(사슬의 첫 원소 m=N+1 자신; 그 항은 (N+1-k)/(N+1) = q/(k+q)).
"""
import os
from mpmath import mp, mpf, exp, log, loggamma
mp.dps = 30
ROOT = r"C:\math\임시\주차함수_증명"
def Bor(w):
    w = mpf(w); return exp(-w + (w - 1) * log(w) - loggamma(w + 1))
def Ren(j):
    if j == 0:
        return mpf(1)
    j = mpf(j); return exp((j - 1) * log(j) - j - loggamma(j))
out = []
for k in [10**4, 10**5]:
    worst = (mpf(0), 0)
    for q in range(2, 102):
        N1 = k + q
        s = sum(Ren(N1 - m) * Bor(m) / Bor(N1) * mpf(m - k) / m for m in range(k + 1, N1 + 1))
        r = k * s / mpf(q) ** mpf(1.5)
        if r > worst[0]:
            worst = (r, q)
    out.append(f"k={k}: max_q<=101 of k*UnionBound/q^1.5 = {mp.nstr(worst[0],5)} at q={worst[1]}  (needs <= 0.5 for F4's boxed claim via this route)")
# limit: (1/k) sum_{j=0}^{q-1} (q-j) Ren(j)
for q in [50, 101]:
    v = sum((q - j) * Ren(j) for j in range(0, q)) / mpf(q) ** mpf(1.5)
    out.append(f"limit k->inf, q={q}: sum_(j<q) (q-j)Ren(j)/q^1.5 = {mp.nstr(v,5)}")
txt = "\n".join(out); print(txt)
open(os.path.join(ROOT, "scripts", "구조압축", "심사_A7_P9_union_out.txt"), "w", encoding="utf-8").write(txt + "\n")
