# -*- coding: utf-8 -*-
# 검토전체24 R7b: (7.11) 가운데 대괄호의 앞 네 항과 합 항의 크기(중앙 행 가까이; 부동소수 관찰).
import sys
from math import log, exp, lgamma, sqrt
try:
    import numpy as np
except Exception:
    np = None

def logp(m): return (m-1)*log(m+1)
def logP(m, j):
    return log(j) + lgamma(m) - lgamma(j) - lgamma(m-j+1) + logp(j-1) + logp(m-j) - logp(m)
def lognorm(m): return logp(m) - m - lgamma(m+1)

def table(l, N):
    # a[m] = A_{m,l-1} e^{-m}/m!
    e1 = exp(-1)
    if np is None:
        a = [1.0]
        for m in range(1, N+1):
            s = 0.0
            for j in range(1, m+1): s += min(j, l)*a[j-1]*a[m-j]
            a.append(s*e1/m)
        return a
    a = np.zeros(N+1); a[0] = 1.0
    wgt = np.minimum(np.arange(1, N+1), l).astype(float)
    for m in range(1, N+1):
        a[m] = np.dot(wgt[:m]*a[:m], a[m-1::-1][:m])*e1/m
    return a

def report(k, nus, U0s):
    N = 2*k + max(nus)
    tabs = {l: table(l, N) for l in (k-1, k, k+1)}
    s = lambda m, y: float(tabs[y][m])/exp(lognorm(m)) if m > 0 else 1.0
    c = lambda m, y: s(m, y+1)-s(m, y)
    for nu in nus:
        n = 2*k+nu
        rw = lambda q: exp(log(k/(k+1+q)) + logP(n, k+1+q) - logP(n, k))
        four = c(k+nu, k-1)+s(k+nu, k+1)-s(n, k)-s(n, k+1)
        out = []
        for U0 in U0s:
            sm = sum((rw(k+nu-1-U)-1)*(s(n-1-U, k)-s(n-U, k)) for U in range(0, U0+1))
            out.append("U0=%d: 합=%.4f, 대괄호=%.4f" % (U0, sm, four+sm))
        print("k=%d nu=%d: s_n(k)=%.4f s_n(k+1)=%.4f s_{k+nu}(k+1)=%.4f c_{k+nu}(k-1)=%.4f 앞 네 항=%.4f | %s"
              % (k, nu, s(n, k), s(n, k+1), s(k+nu, k+1), c(k+nu, k-1), four, "; ".join(out)))

report(301, [1, 5, 20, 102], [0, 10, 300])
report(2001, [1, 5, 20, 102, 400], [0, 10, 300])
