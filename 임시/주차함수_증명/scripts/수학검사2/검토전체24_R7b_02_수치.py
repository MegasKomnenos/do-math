# -*- coding: utf-8 -*-
# 검토전체24 R7b: 7.6절의 수치 상수와 정리 apex-positive의 실제 크기(부동소수 검산).
import sys
from math import log, exp, sqrt, pi, lgamma, comb

def g(x): return (x-1)*log(1+1/x)
def logBor(m): return -m + (m-1)*log(m) - lgamma(m+1)
def logRen(j): return -j + j*log(j) - lgamma(j+1)
def logp(m): return (m-1)*log(m+1)
def logP(m, j):  # 마지막 차 자리 법칙
    return log(j) + lgamma(m) - lgamma(j) - lgamma(m-j+1) + logp(j-1) + logp(m-j) - logp(m)

print("== 상수 ==")
print("1-sqrt(2/pi)/sqrt(301) =", 1-sqrt(2/pi)/sqrt(301))
print("sum_{d<=301} Bor(d) =", sum(exp(logBor(d)) for d in range(1, 302)))
print("(2pi)^(-1/2) =", (2*pi)**-0.5)
print("0.9538/0.398943 =", 0.9538/0.398943)
n = 904
sgb = 1/(2*(n+1)) + 1/(6*n*(n+1))
print("sg bound at 904 =", sgb, " exp(-0.0006) =", exp(-0.0006))
print("2.38*0.9994*(4/9)/2 =", 2.38*0.9994*4/9/2)
print("0.528*sqrt(301)-151/301-1 =", 0.528*sqrt(301)-151/301-1)
print("2*1.549-e =", 2*1.549-exp(1))

print("== sg_m 상하계와 명시 상계(보조정리 explicit-bounds) ==")
bad = 0
for m in range(1, 400):
    sg = m*log(m/(m+1)) + 1
    ub = 1/(2*(m+1)) + 1/(6*m*(m+1))
    if not (-1e-15 <= sg <= ub*(1+1e-12)): bad += 1; print("sg fail", m, sg, ub)
    for U in range(0, m):
        lhs = logP(m, m-U); rhs = logBor(U+1) + sg + log((m+1)/(m-U))
        if lhs > rhs + 1e-9: bad += 1; print("first fail", m, U, lhs, rhs)
    for j in range(1, m+1):
        lhs = logP(m, j); rhs = logRen(j) + sg + log((m+1)/(m+1-j)**2)
        if lhs > rhs + 1e-9: bad += 1; print("second fail", m, j, lhs, rhs)
print("violations:", bad)

def survival(k, N):
    # ah[l][m] = A_{m,l-1} e^{-m}/m! (용량 l), 재귀 m*a_m = sum min(j,l) a_{j-1} a_{m-j}
    out = {}
    for l in (k-1, k, k+1):
        a = [1.0]
        e1 = exp(-1)
        for m in range(1, N+1):
            s = 0.0
            for j in range(1, m+1):
                s += min(j, l)*a[j-1]*a[m-j]
            a.append(s*e1/m)
        out[l] = a
    return out

def lognorm(m):  # log(p_m e^{-m}/m!)
    return logp(m) - m - lgamma(m+1)

def report(k, ns):
    N = max(ns)
    a = survival(k, N)
    s = lambda m, y: a[y][m]/exp(lognorm(m)) if m > 0 else 1.0
    c = lambda m, y: s(m, y+1)-s(m, y)
    for n in ns:
        nu = n-2*k
        rw = lambda q: exp(log(k/(k+1+q)) + logP(n, k+1+q) - logP(n, k))
        Pk = lambda j: min(j, k)/j*exp(logP(n, j))*s(j-1, k)*s(n-j, k)/s(n, k)
        clp = lambda m: c(m, k)/s(m, k); clm = lambda m: c(m, k-1)/s(m, k)
        apex = (sum(Pk(j)*(clp(j-1)+clm(j-1)) for j in range(n-k+1, n+1)) - Pk(k)*(1-clm(n-k)))/k
        Pn = exp(logP(n, k))
        ratio = apex*k/Pn
        mid0 = c(k+nu, k-1)+s(k+nu, k+1)-s(n, k)-s(n, k+1)
        hz = lambda Nn: 1-s(Nn+1, k)/s(Nn, k)
        U0 = min(300, k-1)
        last = sum((rw(k+nu-1-U)-1)*hz(n-1-U) for U in range(0, U0+1)) - 1
        mid = mid0 + sum((rw(k+nu-1-U)-1)*(s(n-1-U, k)-s(n-U, k)) for U in range(0, U0+1))
        print("k=%d n=%d nu=%d: s_n(k)=%.4f s_n(k+1)=%.4f s_{k+nu}(k+1)=%.4f | mid-bracket(no sum)=%.4f mid(U0=%d)=%.4f last=%.4f | k*apex/P_n(k)=%.4f bound=%.4f | hz(n-1)*2k=%.4f"
              % (k, n, nu, s(n, k), s(n, k+1), s(k+nu, k+1), mid0, U0, mid/ s(n,k) if False else mid, last, ratio, 0.528*sqrt(k)-151/k-1, hz(n-1)*2*k))

report(301, [603, 610, 650, 700, 800, 903, 904, 905, 1000, 1500])
