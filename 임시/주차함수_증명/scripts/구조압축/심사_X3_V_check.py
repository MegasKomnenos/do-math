# -*- coding: utf-8 -*-
"""심사 X3 — S12 보조 검산. (배정밀도 관찰; 증명 아님)
(1) k∈{2001,2500,3130}에서 판정 V의 양 𝒱_k(m)=Σ_{m'=m}^{2k}[(k+1)c_{m'}(k)−(k−1)c_{m'}(k−1)] (k≤m≤2k)를
    볼츠만 척도 열 ã^{(c)}_n=e^{−n}A_{n,c−1}/n! (c=k+1,k,k−1)의 양수항 재귀 n ã_n = e^{−1} Σ_{j<n} min(j+1,c) ã_j ã_{n−1−j}
    로 구해(7.5절 (7.2)의 볼츠만판) 최솟값과 𝒱_k(k)를 적는다. c_m(y)=b_{m,y}/p_m, e^{−m}p_m/m! = e·Bor(m+1).
(2) F3 §3.2의 하계식 (k−1)/(R+1)·[1−s_R(k−1)] − (k−1)c_{2k}(k−1), R=⌊3(k−1)/2⌋ 의 참값(같은 열에서)과 F3의 0.0041을 견준다.
(3) P9 보조: (7.10)의 k→∞ 극한 L_q = Σ_{s=0}^{q−2} Bor(s+1)[(q−1−s)+L_{q−1−s}] 에서 L_q/q^{3/2} (q≤101)의 최댓값.
"""
import os, math
import numpy as np
from mpmath import mp, mpf, log, exp, factorial
ROOT = r"C:\math\임시\주차함수_증명"
out = []
def bor(m):  # e^{-m} m^{m-1}/m!
    return float(exp(-m + (m-1)*log(m) - log(factorial(m))))
def cols(k):
    N = 2*k
    res = {}
    for c in (k+1, k, k-1):
        a = np.zeros(N+1); a[0] = 1.0
        w = np.minimum(np.arange(0, N+1)+1, c).astype(float)  # weight min(j+1,c) for j index
        for n in range(1, N+1):
            j = np.arange(0, n)
            a[n] = math.exp(-1)*np.dot(w[:n]*a[:n], a[n-1::-1][:n]) / n
        res[c] = a
    return res
for k in (2001, 2500, 3130):
    A = cols(k)
    eb = np.array([math.e*bor(m+1) for m in range(0, 2*k+1)])
    cK = (A[k+1]-A[k])/eb        # c_m(k)
    cKm = (A[k]-A[k-1])/eb       # c_m(k-1)
    p = (k+1)*cK - (k-1)*cKm     # 𝔭_m
    V = np.cumsum(p[k:2*k+1][::-1])[::-1]  # V_k(m), m=k..2k
    mmin = int(np.argmin(V)) + k
    R = (3*(k-1))//2
    sR = A[k-1][R]/eb[R]        # s_R(k-1) = A_{R,k-2}/p_R
    f3 = (k-1)/(R+1)*(1-sR) - (k-1)*cKm[2*k]
    out.append(f"k={k}: 𝒱_k(k)={V[0]:.4f}; min_m 𝒱_k(m)={V.min():.4e} (m={mmin}); 𝒱_k(2k)={V[-1]:.3e}; "
               f"F3 하계식 참값 (k−1)/(R+1)[1−s_R(k−1)]−(k−1)c_{{2k}}(k−1) = {f3:.4f} (R={R}, 1−s_R={1-sR:.4f}, (k−1)c_2k(k−1)={(k-1)*cKm[2*k]:.4f}); "
               f"상쇄 점검: 최소 상대차 (ã^(k+1)−ã^(k))/ã^(k) at m=k+1: {(A[k+1][k+1]-A[k][k+1])/A[k][k+1]:.3e}")
# (3)
mp.dps = 30
Lq = {1: mpf(0)}
B = {s: exp(-(s+1) + s*log(s+1) - log(factorial(s+1))) for s in range(0, 101)}  # Bor(s+1)
for q in range(2, 102):
    Lq[q] = sum(B[s]*((q-1-s) + Lq[q-1-s]) for s in range(0, q-1))
ratio = max((float(Lq[q]/mpf(q)**mpf(1.5)), q) for q in range(2, 102))
out.append(f"(7.10)의 k→∞ 극한 L_q/q^(3/2) 최댓값(q≤101): {ratio[0]:.4f} (q={ratio[1]}); L_101={float(Lq[101]):.3f}, 101^(3/2)/2={101**1.5/2:.1f}")
txt = "\n".join(out); print(txt)
open(os.path.join(ROOT, "scripts", "구조압축", "심사_X3_V_check_out.txt"), "w", encoding="utf-8").write(txt+"\n")
