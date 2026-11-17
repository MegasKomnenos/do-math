# -*- coding: utf-8 -*-
# 검토전체25 R7b: (7.11)·(7.12)의 크기 감각을 k=301에서 배정밀도로 본다(검산용; 증명 아님)
from math import exp, log, sqrt, lgamma, pi
import sys

def atil(nmax, cap):
    # ã_n = A_{n,cap-1} e^{-n}/n! ; n ã_n = e^{-1} sum_j min(j,cap) ã_{j-1} ã_{n-j}
    a = [0.0] * (nmax + 1); a[0] = 1.0
    e1 = exp(-1.0)
    for n in range(1, nmax + 1):
        s = 0.0
        for j in range(1, n + 1):
            s += min(j, cap) * a[j - 1] * a[n - j]
        a[n] = e1 * s / n
    return a

def ptil(m):  # p_m e^{-m}/m!
    return exp((m - 1) * log(m + 1) - m - lgamma(m + 1)) if m > 0 else 1.0

def main(k, nmax):
    am = atil(nmax, k - 1); a0 = atil(nmax, k); ap = atil(nmax, k + 1)
    pt = [ptil(m) for m in range(nmax + 1)]
    s = lambda m, y: {k - 1: am, k: a0, k + 1: ap}[y][m] / pt[m]
    c = lambda m, Y: s(m, Y + 1) - s(m, Y)
    def logP(n, j):  # log P_n(j)
        return (log(j) + lgamma(n) - lgamma(j) - lgamma(n - j + 1) + ((j - 2) * log(j) if j > 1 else 0.0)
                + ((n - j - 1) * log(n - j + 1) if n - j > 0 else 0.0) - (n - 1) * log(n + 1))
    g = lambda x: (x - 1) * log(1 + 1 / x)
    for n in [2 * k + 1, 2 * k + 5, 2 * k + 50, 2 * k + k // 2, 3 * k, 3 * k + 1, 4 * k, 6 * k, nmax]:
        nu = n - 2 * k
        rw = lambda q: exp(log(k) - log(k + 1 + q) + logP(n, k + 1 + q) - logP(n, k))
        tot = sum(rw(q) * (c(k + q, k - 1) + c(k + q, k)) for q in range(nu, k + nu)) - s(k + nu, k - 1)
        four = c(k + nu, k - 1) + s(k + nu, k + 1) - s(n, k) - s(n, k + 1)
        U0 = 300
        hzsum = sum((rw(k + nu - 1 - U) - 1) * (1 - s(n - U, k) / s(n - 1 - U, k)) for U in range(0, U0 + 1)) - 1
        hzmin = min((1 - s(n - U, k) / s(n - 1 - U, k)) for U in range(0, U0 + 1))
        print("k=%d n=%d nu=%d: k*apex/P_n(k)=%.4f  four-term=%.4f  [hz-sum bracket]=%.4f  bound(7.12)=%.4f  s_{k+nu}(k+1)=%.4f s_n(k)=%.5f s_n(k+1)=%.5f  min hz*2k=%.4f"
              % (k, n, nu, tot / s(n, k), four, hzsum, 0.528 * sqrt(k) - 151 / k - 1, s(k + nu, k + 1), s(n, k), s(n, k + 1), hzmin * 2 * k))
    print("rw(nu)-1 at n=3k+1:", exp(log(k) - log(k + 1 + (k + 1)) + logP(3 * k + 1, 2 * k + 2) - logP(3 * k + 1, k)) - 1)
    print("0.528*sqrt(301)-151/301-1 =", 0.528 * sqrt(301) - 151 / 301 - 1)
    print("1-sqrt(2/pi)/sqrt(301) =", 1 - sqrt(2 / pi) / sqrt(301), " 0.9538/0.398943 =", 0.9538 / 0.398943, " (2pi)^-1/2 =", 1 / sqrt(2 * pi))
    print("2.38*0.9994*4/9/2 =", 2.38 * 0.9994 * 4 / 9 / 2, " sg_904 bound =", 1 / (2 * 905) + 1 / (6 * 904 * 905), " exp(-0.0006) =", exp(-0.0006))
    print("sg_904 exact =", 904 * log(904 / 905) + 1)
    # Borel sum
    bor = lambda d: exp(-d + (d - 1) * log(d) - lgamma(d + 1))
    print("sum_{d<=301} Bor(d) =", sum(bor(d) for d in range(1, 302)))
    print("2*1.549-e =", 2 * 1.549 - exp(1))

main(301, 1900)
