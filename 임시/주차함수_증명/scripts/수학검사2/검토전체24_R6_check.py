# -*- coding: utf-8 -*-
# 검토 전체 24차 R6: 장7A.md 의 수치·항등식 검산 (python -I)
from fractions import Fraction as F
from itertools import permutations, product
from math import factorial, comb, log
import sys

def caps(sig):
    n = len(sig); h = []
    for i in range(n):
        j = i - 1
        while j >= 0 and sig[j] < sig[i]:
            j -= 1
        h.append(i - j)   # i-j = (i+1) - (j+1), j=-1 -> i+1
    return h

def prod(xs):
    r = 1
    for x in xs: r *= x
    return r

# ---------- 1. t_k, n^sharp_k
def tk(k):
    j = 0
    while (k+1)**j * k**(j+1) + (k-1)**(2*j+1) < 2 * k**(2*j+1):
        j += 1
    return j
mx = 0; ok = True
for k in range(2, 141):
    t = tk(k); assert 1 <= t <= k
    ns = k + (k+1)*t
    mx = max(mx, ns)
    assert ns <= k*k + 2*k
print("1. t_k in [1,k] for 2<=k<=140; max n^sharp_k (k<=140) =", mx, "; k^2+2k at 140 =", 140*140+280)
first_over = next(k for k in range(2, 400) if k + (k+1)*tk(k) > 20000)
print("   first k with n^sharp_k > 20000:", first_over, "n^sharp =", first_over + (first_over+1)*tk(first_over),
      "; n^sharp_141 =", 141 + 142*tk(141), "; t_141 =", tk(141))

# ---------- 2. integer inequality of column lemma (ga)
L = 10**21 * 400**10; R = 17**21 * 123**10
print("2. 10^21*400^10 > 17^21*123^10:", L > R, "L=%.6e R=%.6e" % (L, R))
assert 4**10 == 1048576 and 17**4 == 83521 and 123**2 == 15129
assert F(836,100)**5 < 40836 and 17*40836 < 695000
assert 17**21 < 695 * 10**23 and F(1513,1000)**5 < F(793,100) and 123**10 < 793 * 10**18
assert 695*793 < 552000
assert all(F(2*(k+1), k-1) <= F(21,10) for k in range(41, 3000)) and F(2*41, 39) > F(21,10)
assert 1 - F(21,10)*F(10,17)**3 > 0
print("   bounds 17^21<6.95e25, 123^10<7.93e20, product<5.52e46, o_k<=21/10 (k>=41; fails at k=40): ok")

# ---------- 3. brute force over permutations
def stats(n):
    out = []
    for sig in permutations(range(1, n+1)):
        out.append(caps(sig))
    return out
A = {}
for n in range(0, 9):
    hs = stats(n) if n > 0 else [[]]
    for l in range(-1, 12):
        A[(n, l)] = sum(prod(min(h, l+1) for h in hh) for hh in hs) if l >= 0 else 0
    if n >= 1:
        assert A[(n, n-1)] == (n+1)**(n-1)
    # mean lower bound, joint inequality, moment expression
    for k in range(2, n+2):
        w = [prod(min(h, k) for h in hh) for hh in hs]
        tot = sum(w)
        assert tot == A[(n, k-1)]
        if n >= 1:
            for y in range(0, n+1):
                EZ = F(sum(wi * sum(1 for h in hh if h > y) for wi, hh in zip(w, hs)), tot)
                assert EZ >= F(n-y, y+1), (n, k, y)
            Rs = F(A[(n, k)], tot); Rf = F(A[(n, k-2)], tot)
            ok_ = -2*log(1-1/k)/log(1+1/k)
            assert float(Rf) > (1-1/k) * float(Rs)**(-ok_) , (n, k)
            mu = sum(F(wi) * ((1+F(1,k))**sum(1 for h in hh if h > k) + (1-F(1,k))**sum(1 for h in hh if h >= k) - 2) for wi, hh in zip(w, hs)) / tot
            d = A[(n, k)] - 2*A[(n, k-1)] + A[(n, k-2)]
            assert mu == F(d, tot)
            T = F(sum(wi * (sum(1 for h in hh if h > k)*(sum(1 for h in hh if h > k)-1) - k*sum(1 for h in hh if h == k)) for wi, hh in zip(w, hs)), tot)
            assert F(d, tot) >= T / k**2
print("3. n<=8: p_n, E[Z_y]>=(n-y)/(y+1) (all y, Psi=1{M<=k-1}), joint inequality, mu=E[v], d>=T/k^2: ok")

# k=1 bound b_{n,1} >= (n-1) n!/2
for n in range(2, 9):
    b1 = A[(n,1)] - A[(n,0)]
    assert A[(n,0)] == factorial(n) and b1 >= (n-1)*factorial(n)//2
print("   b_{n,1} >= (n-1) n!/2 for 2<=n<=8: ok; (n-1)n!/2 > n! needs n>=4")

# supermultiplicativity
for k in range(1, 6):
    for m in range(0, 5):
        for m2 in range(0, 9-m):
            if m + m2 <= 8:
                assert A[(m+m2, k-1)] >= comb(m+m2, m) * A[(m, k-1)] * A[(m2, k-1)]
print("   supermultiplicativity m+m'<=8, k<=5: ok")

# ---------- 4. last-car recursion to larger n, finite size formula
def Atab(k, N):
    a = [1]
    for n in range(1, N+1):
        a.append(sum(comb(n-1, j) * min(j+1, k) * a[j] * a[n-1-j] for j in range(n)))
    return a
for k in range(1, 6):
    a = Atab(k, 8)
    assert all(a[n] == A[(n, k-1)] for n in range(9))
print("4. last-car recursion matches brute force (n<=8, k<=5)")

def p(n): return (n+1)**(n-1) if n >= 1 else 1
def finite_size(k, N):
    a = Atab(k, N+1)
    fa = [F(a[m], factorial(m)) for m in range(N+2)]
    ac = [F(p(m), factorial(m)) for m in range(N+2)]
    K = [F(0)]*(N+3)
    for j in range(1, N+2):
        s = sum((k-m)*ac[m-1]*K[j-m] for m in range(1, k) if j-m >= 0)
        if j == k+1: s += 1
        K[j] = s / j
    return fa, K
for n in range(1, 9):
    hs = stats(n)
    for k in range(2, 6):
        w = [prod(min(h, k) for h in hh) for hh in hs]
        EH = F(sum(wi * sum(1 for h in hh if h == k) for wi, hh in zip(w, hs)), sum(w))
        fa, K = finite_size(k, max(n, k))
        rhs = (n+1) * fa[k-1] * sum(K[j]*fa[n+1-j] for j in range(k+1, n+2)) / fa[n]
        assert EH == rhs, (n, k, EH, rhs)
        assert K[k+1] == F(1, k+1) and all(K[j] == 0 for j in range(0, k+1))
print("   finite-size formula 7:old-6-11(ga) E[H_k] exact for n<=8, 2<=k<=5: ok; K_{k+1}=1/(k+1)")

# ---------- 5. prime parking functions
def park(pref):
    n = len(pref); occ = [0]*(n+2); disp = []
    for a in pref:
        s = a
        while s <= n and occ[s]: s += 1
        if s > n: return None
        occ[s] = 1; disp.append(s - a)
    return disp
for n in range(1, 7):
    Cn = {}
    cntA = {}
    for pref in product(range(1, n+1), repeat=n):
        dsp = park(pref)
        if dsp is None: continue
        M = max(dsp)
        prime = all(sum(1 for a in pref if a <= b) != b for b in range(1, n))
        for k in range(1, 8):
            if M <= k-1:
                cntA[k] = cntA.get(k, 0) + 1
                if prime: Cn[k] = Cn.get(k, 0) + 1
    assert Cn.get(n, 0) == (n-1)**(n-1) if n > 1 else Cn[1] == 1
    for k in range(1, 8):
        assert cntA[k] == A[(n, k-1)]
    globals().setdefault('CC', {})[n] = Cn
    assert Cn.get(2, 0) == 1
print("5. prime PF count C_{n,n}=(n-1)^(n-1), C_{n,2}=1 (n<=6), A_{n,k-1} matches: ok")
# A = 1/(1-C_k) and C' = k - Q'(1-C)
for k in range(1, 6):
    N = 6
    c = [F(0)] + [F(CC[n].get(k, 0), factorial(n)) for n in range(1, N+1)]
    a = [F(A[(n, k-1)], factorial(n)) for n in range(N+1)]
    # (1-C)*A = 1
    for n in range(N+1):
        s = a[n] - sum(c[j]*a[n-j] for j in range(1, n+1))
        assert s == (1 if n == 0 else 0), (k, n)
    # Q'_{k-1} coefficients: sum_{t=1}^{k-1} (k-t) p_{t-1} x^{t-1}/(t-1)!
    qd = [F((k-t)*p(t-1), factorial(t-1)) for t in range(1, k)] + [F(0)]*N
    onemc = [1 - c[0]] + [-c[j] for j in range(1, N+1)]
    for n in range(0, N):
        lhs = (n+1)*c[n+1]
        rhs = (k if n == 0 else 0) - sum(qd[j]*onemc[n-j] for j in range(0, n+1))
        assert lhs == rhs, (k, n)
print("   A_{k-1}=1/(1-C_k), C_k'=k-Q'_{k-1}(1-C_k) coefficientwise (n<=6,k<=5): ok")

# ---------- 6. D.column-certification-k500 counts (범위 밖 참고)
def cnt(k0, k1):
    d = r = 0
    for k in range(k0, k1+1):
        ns = -(-k*k//4)
        d += 2*ns - (2*k+1) + 1
        r += 2*ns - ns + 1
    return d, r
print("6. D counts 121-160:", cnt(121,160), " 161-500:", cnt(161,500))
print("   2 n_* < 10000 for k up to:", max(k for k in range(121, 501) if 2*(-(-k*k//4)) < 10000))

# ---------- 7. 작은 행의 왼쪽 절반 비교 (장 머리 셋째 문단의 「행 n<=20000은 ... 덮는다」 확인)
NN = 60
AT = {k: Atab(k, NN) for k in range(0, NN+2)}     # AT[k][n] = A_{n,k-1}
def dd(n, k): return AT[k+1][n] - 2*AT[k][n] + (AT[k-1][n] if k >= 1 else 0)
bad = [(n, k) for n in range(3, NN+1) for k in range(1, n) if n >= 2*k+1 and dd(n, k) < 0]
print("7. left-half positions (n>=2k+1, n<=60) with d_{n,k}<0:", bad)
print("   d_{n,k_n}>0 first holds at n =", min(n for n in range(2, NN+1) if all(dd(m, -(-m//2)) > 0 for m in range(n, NN+1))))
