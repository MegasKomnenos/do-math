# 검토전체23 R5: 사슬 재귀 (6.21)로 생존 확률을 부동소수로 재계산해 장6 진술을 표본 점검
import math, sys
from math import lgamma, exp, log, sqrt, pi, e
def lbor(m): return -m + (m-1)*log(m) - lgamma(m+1)
LB = [0.0] + [lbor(m) for m in range(1, 30000)]
def surv(y, dmax):
    """s_d(y)=s_{y+d-1}(y), d=1..dmax (dmax<=y+3), via (6.21) and the t(y) correction at d=y+3"""
    s = [None, 1.0]
    for d in range(2, dmax+1):
        tot = 0.0; acc = 0.0
        base = LB[y+d]
        for q in range(1, d):
            p = exp(LB[d-q] + LB[y+q] - base)
            tot += p
            acc += p * (y/(y+q)) * s[q]
        val = (1.0 - tot) + acc
        if d == y+3:
            t = exp(-1 + 2*LB[y+1] - LB[2*y+3]) / 2
            val += t/(y+1)**2
        s.append(val)
    return s
def s_of(tab, y, m):
    return 1.0 if m <= y else tab[m-y+1]

def check_k(k):
    Sm = surv(k-1, k+2)   # s_m(k-1), m up to 2k
    S0 = surv(k, k+2)     # s_m(k), m up to 2k+1
    Sp = surv(k+1, k+1)   # s_m(k+1), m up to 2k+1
    sm = lambda m: s_of(Sm, k-1, m)
    s0 = lambda m: s_of(S0, k, m)
    sp = lambda m: s_of(Sp, k+1, m)
    c_k = lambda m: sp(m) - s0(m)       # c_m(k)
    c_k1 = lambda m: s0(m) - sm(m)      # c_m(k-1)
    # theorem 6:old-8-25 for y=k
    worst = max(S0[d] / min(1, 1.15*(k+d)/d**1.5) for d in range(1, k+3))
    print("k", k, "max s_d(k)/s^up_d(k)", worst)
    # V_k(m)
    p = {m: (k+1)*c_k(m) - (k-1)*c_k1(m) for m in range(k, 2*k+1)}
    V = {}; acc = 0.0
    for m in range(2*k, k-1, -1):
        acc += p[m]; V[m] = acc
    mn = min(V, key=lambda m: V[m])
    print("  V_k(k)", V[k], "min V_k(m)", V[mn], "at m", mn, "(m-k)", mn-k, "m^(2/3)/2 at k", k**(2/3)/2)
    near = [m for m in range(k, 2*k+1) if m-k <= m**(2/3)/2]
    print("  min V on near-core", min(V[m] for m in near))
    # Boltzmann tails
    b = {m: e*exp(LB[m+1])*p[m] for m in range(k, 2*k+1)}
    U = {}; acc = 0.0
    for m in range(2*k, k-1, -1):
        acc += b[m]; U[m] = acc
    neg = [m for m in range(k, 2*k+1) if U[m] <= 0]
    print("  U_k(m)<=0 for m-k in", (min(neg)-k, max(neg)-k) if neg else None, "; first m with all U>0 beyond: ", (max(neg)+1-k) if neg else 0)
    # central row masses
    print("  k c_2k(k-1)", k*c_k1(2*k), "(k-1) c_2k(k)", (k-1)*c_k(2*k))
    # stay law (6.20) with y=k-1: s_m(k)-s_{m-1}(k-1) <= (m-k)/k c_m(k-1), m=k+1..2k
    bad = [m for m in range(k+1, 2*k+1) if s0(m)-sm(m-1) > (m-k)/k*c_k1(m)*(1+1e-9)+1e-15]
    print("  stay law violations", len(bad))
    # diag (6.26) with w=k-1: (k+1)(m+1)c_{m+1}(k) > (k-1)(m+2)c_m(k-1), m=k..2k-1
    bad = [m for m in range(k, 2*k) if (k+1)*(m+1)*c_k(m+1) <= (k-1)*(m+2)*c_k1(m)]
    print("  diag violations", len(bad))
    # DD sum and Bd
    DD = lambda m: (k+1)*sp(m+2) - 2*k*s0(m+1) + (k-1)*sm(m)
    sdd = sum(DD(m) for m in range(k, 2*k))
    neg = sum(-min(DD(m),0) for m in range(k, 2*k))
    Bd = 2 - 2*sp(2*k+1) - (k-1)*(sp(2*k+1)-s0(2*k)) - (k-1)*c_k1(2*k)
    print("  sum DD", sdd, "neg part", neg, "Bd", Bd, "Bd+sumDD", Bd+sdd)
    # W0 and losses
    W0 = sum(exp(LB[n])*c_k1(n-1) for n in range(k+1, 2*k+1))
    print("  W0*k^1.5/(2 s2pi)", W0*k**1.5/(2*(2*pi)**-0.5))
    return V, U, c_k, c_k1
for k in (60, 300, 2001):
    check_k(k)
