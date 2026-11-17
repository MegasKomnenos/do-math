# -*- coding: utf-8 -*-
# R11 검산: D.critical-window-rig 「독립 재계산」의 "e_n/B_{n,k-1} >= 1.54" — 창 1.4<=xhat<=10 의 모든 정수 위치에서의 최솟값
import math, sys, glob
REC = glob.glob(r"C:/math/.skill-workspace/do-math/parking-unimodality-fresh-20261105-150803/knowledge/records/ra4c01fc*/evidence/peer")[0]
sys.path.insert(0, REC)
from exact_en_B import recursions
for c in [10001, 10500, 11036, 11037, 12220, 16970, 19093, 32257, 37356]:
    u = c ** (-1.0 / 3)
    Ymax = int(10 * c ** (2.0 / 3)) + 2
    nmax = min(2 * c, c + Ymax)
    r, a, d, e, j = recursions(c, nmax=nmax)
    best = None; samp = None
    for n in range(c + 1, nmax + 1):
        Y = n - c; xh = (Y + 1) * u * u
        if xh < 1.4 or xh > 10: continue
        q = e[n] / j[n]
        if best is None or q < best[0]: best = (q, n, Y, xh)
        if Y % 200 == 0 and (samp is None or q < samp[0]): samp = (q, n, Y, xh)
    print("c=%d  min e/B over window = %.4f at Y=%d (xhat=%.4f);  min over Y%%200==0 = %.4f at Y=%d (xhat=%.3f)" % (c, best[0], best[2], best[3], samp[0], samp[2], samp[3]))

# 독립 재구현(부록 D.central-gap-integer 의 네 재귀; 순열 전수와 대조한 _icert.py 의 식을 numpy 로)
import numpy as np
def myrec(k, nmax):
    s = math.e
    r = np.zeros(nmax + 2); r[0] = 1.0
    for i in range(1, nmax + 2):
        # r_i = p_i/(i! s^i), p_i=(i+1)^(i-1):  r_i/r_{i-1} = ((i+1)/i)^(i-1) * ... 
        r[i] = math.exp((i - 1) * math.log(i + 1) - math.lgamma(i + 1) - i)
    A = np.zeros(nmax + 1); D = np.zeros(nmax + 1); Z = np.zeros(nmax + 1); J = np.zeros(nmax + 1)
    A[:k + 1] = r[:k + 1]; J[k] = r[k - 1] / (s * k)
    for n in range(k + 1, nmax + 1):
        rr = n - k
        i1 = np.arange(0, rr - 1); i2 = np.arange(rr - 1, k + 1); i3 = np.arange(0, rr)
        A[n] = (np.dot((k + i1 + 1) * r[i1], A[n - 1 - i1]) + np.dot(np.minimum(i2 + 1, k) * r[i2], r[n - 1 - i2])) / (s * n)
        D[n] = (np.dot((k + i1 + 1) * r[i1], D[n - 1 - i1]) + np.dot(r[i3], A[n - 1 - i3])) / (s * n)
        Z[n] = (np.dot((k + i1 + 1) * r[i1], Z[n - 1 - i1]) + 2 * np.dot(r[i1], D[n - 1 - i1])) / (s * n)
        J[n] = (np.dot((k + i3) * r[i3], J[n - 1 - i3]) + r[k - 1] * r[n - k]) / (s * n)
    return Z, J
k = 10001
Z, J = myrec(k, k + 4660)
u2 = k ** (-2.0 / 3)
best = min(((Z[n] / J[n], n - k, (n - k + 1) * u2) for n in range(k + 1, k + 4661) if 1.4 <= (n - k + 1) * u2 <= 10))
print("own implementation, k=10001: min e_n/J_n(k-1) over the window = %.5f at r=%d (xhat=%.4f)" % best)
