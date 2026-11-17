# R9: true Stays(k,nu) by chain recursion (float64, numpy) vs Stays^up bound, k=9705
import numpy as np, math, sys
from math import lgamma, log
def lBor(m): return -m+(m-1)*np.log(m)-np.array([lgamma(x+1) for x in np.atleast_1d(m)])
def surv(y, qmax):
    lb = np.zeros(qmax+1); lb[1:] = lBor(np.arange(1, qmax+1, dtype=float))
    lby = lBor(np.arange(y, y+qmax+1, dtype=float))   # index q -> Bor(y+q)
    s = np.zeros(qmax+1); s[1] = 1.0
    fac = y/(y+np.arange(0, qmax+1, dtype=float))
    for q in range(2, qmax+1):
        qp = np.arange(1, q)
        pr = np.exp(lb[q-qp]+lby[qp]-lby[q])
        s[q] = 1-pr.sum()+(pr*fac[qp]*s[qp]).sum()
    return s
k = 9705
S = {y: surv(y, k+3) for y in (k-1, k, k+1)}
def sm(m, y): return S[y][m-y+1] if m >= y else 1.0   # s_m(y)=frak s_{m-y+1}(y)
def stay(m, l): return sm(m+1, l+1)-sm(m, l)
for nu in (103, 300, 591, 2000, 4658, 6000, k-1):
    N = k+nu
    St = 2*stay(N+1, k)+sum((2-(m-N)/k)*(stay(m, k)+stay(m-1, k-1)) for m in range(N+2, 2*k+1))
    print("k", k, "nu", nu, "Stays", St)
