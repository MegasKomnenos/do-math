# 검토전체23 R5: 정확 정수·유리수로 장6의 항등식·부등식 표본 점검
from fractions import Fraction as Fr
from math import comb, factorial
from functools import lru_cache
import sys
sys.setrecursionlimit(10000)

def Atable(nmax, ell):
    A = [1]
    for n in range(1, nmax+1):
        A.append(sum(comb(n-1, j)*min(j+1, ell+1)*A[j]*A[n-1-j] for j in range(n)))
    return A
def p(n): return (n+1)**(n-1) if n >= 1 else 1

# --- 6.2: restricted growth ratio, k=43 (and k=42, 44 for comparison)
for k in (42, 43, 44):
    N = 3*k+40
    A = Atable(N+1, k-1)
    bound = Fr(k+1, k)**(k-1)
    eq = []; viol = []
    for n in range(0, N+1):
        r = Fr(A[n+1], (n+1)*A[n])
        if r == bound: eq.append(n)
        if r > bound: viol.append(n)
    print("k", k, "equality at N=", eq, "violations", viol[:5])
    # hazard (다): N+1>=2k -> hz >= 1/(2k)
    bad = []
    for n in range(2*k-1, N):
        s_n = Fr(A[n], p(n)); s_n1 = Fr(A[n+1], p(n+1))
        hz = 1 - s_n1/s_n
        if hz < Fr(1, 2*k): bad.append(n)
    print("   hazard (다) violations", bad[:5])

# --- small exact tables
NM = 26
Aall = {}
for ell in range(-1, NM+2):
    Aall[ell] = [1] + [0]*NM if ell == -1 else Atable(NM, ell)
def A(n, l):
    if l < 0: return 1 if n == 0 else 0
    if l >= n: return p(n)
    return Aall[l][n]
def b(n, l): return A(n, l) - A(n, l-1)
def s(m, y): return Fr(A(m, y-1), p(m))
def c(m, Y): return Fr(b(m, Y), p(m))
def sd(d, y): return s(y+d-1, y)
# check A table against p
assert all(A(n, n-1) == p(n) for n in range(1, NM+1))

# --- 6.3: identities (6.22),(6.23),(6.24) and stay law for small y (theorem only claims y>=50)
def bor_ratio_pi(N, m):  # pi_N(m) = C(N,m) m^{m-1} p_{N-m}/p_N
    return Fr(comb(N, m)*m**(m-1)*p(N-m), p(N))
def tt(y): return Fr(comb(2*y+2, y+1)*(y+1)**(2*y), 2*p(2*y+2))
def vs(m, l): return s(m+1, l+1) - s(m, l)
cnt = 0
for y in range(2, 11):
    for d in range(1, y+3):
        if y+d+1 > NM: continue
        # (6.21) incl. d=y+3
        for dd in (d, ) + ((y+3,) if d == y+2 and 2*y+3 <= NM else ()):
            rhs = 1 - sum(bor_ratio_pi(y+dd-1, y+q) for q in range(1, dd)) + sum(bor_ratio_pi(y+dd-1, y+q)*Fr(y, y+q)*sd(q, y) for q in range(1, dd))
            if dd == y+3: rhs += tt(y)/(y+1)**2
            assert rhs == sd(dd, y), ("6.21", y, dd)
        # (6.22)
        rhs = bor_ratio_pi(y+d, y+1)/(y+1) + sum(bor_ratio_pi(y+d, y+1+q)*((y+1)*c(y+q, y)+sd(q+1, y))/(y+1+q) for q in range(1, d))
        if d == y+2: rhs -= tt(y)/(y+1)**2
        assert rhs == c(y+d, y), ("6.22", y, d)
        # (6.23)
        Er = lambda q: bor_ratio_pi(y+d-1, y+q) - bor_ratio_pi(y+d, y+1+q)
        T = sum(Er(q)*(1-Fr(y, y+q)*sd(q, y)) for q in range(1, d))
        rhs = T + sum(bor_ratio_pi(y+d, y+1+q)*(Fr(y, y+q)*vs(y+q-1, y) + Fr(q, (y+q)*(y+1+q))*sd(q, y+1)) for q in range(1, d))
        assert rhs == vs(y+d-1, y), ("6.23", y, d)
        # (6.24)
        J = lambda dd: (dd-1)*c(y+dd, y) - (y+1)*vs(y+dd-1, y)
        if d >= 2:
            Cv = lambda q: (d-1)*(y+1) - Fr((q-1)*y*(y+1+q), y+q) - Fr((y+1)*q, y+q)
            Cs = lambda q: (d-1) - Fr((y+1)*q, y+q)
            rhs = Fr(d-1, y+1)*bor_ratio_pi(y+d, y+1) - (y+1)*T + sum(bor_ratio_pi(y+d, y+1+q)/(y+1+q)*(Cv(q)*c(y+q, y)+Cs(q)*sd(q+1, y)+Fr(y*(y+1+q), y+q)*J(q)) for q in range(1, d))
            if d == y+2: rhs -= tt(y)/(y+1)
            assert rhs == J(d), ("6.24", y, d)
            cnt += 1
print("6.21-6.24 identities exact OK, cases", cnt)
# stay law for small y: where does it hold?
fails = [(y, d) for y in range(1, 12) for d in range(2, y+3) if y+d+1 <= NM and (y+1)*vs(y+d-1, y) > (d-1)*c(y+d, y)]
print("stay law (6.20) failures for small y (theorem needs y>=50):", fails)

# --- 6.4: chain count (prop 6:chain-count) and diag theorem
@lru_cache(None)
def smallforest(N, w):  # forests on N labels with all trees <= w
    if N == 0: return 1
    return sum(comb(N-1, t-1)*t**(t-1)*smallforest(N-t, w) for t in range(1, min(w, N)+1))
def cg(g): return Fr(g**(g-1), factorial(g))
def falling(a, j):
    r = 1
    for i in range(j): r *= (a-i)
    return r
def chains(d):
    # all sequences d=q0>q1>...>qL>=0, L>=1
    out = []
    def rec(prev, seq):
        for q in range(prev-1, -1, -1):
            out.append(seq+[q]); rec(q, seq+[q])
    rec(d, [])
    return out
ok = 0
for d in range(1, 7):
    for m in range(max(2, 2*d-1), 15):
        t = m+1; w = m-d; y = w+1
        tot = Fr(0)
        for seq in chains(d):
            qs = [d]+seq; L = len(seq); j = d-seq[-1]
            pr = Fr(1)
            for i in range(1, L+1): pr *= cg(qs[i-1]-qs[i])
            Br = Fr(1); Br2 = Fr(1)
            for q in seq:
                Br *= Fr(y, y+q); Br2 *= Fr(y-1, y+q)
            tot += falling(t-1, j)*pr*smallforest(t-1-j, w)*(Br-Br2)
        assert tot == b(m, m-d), ("chain-count", m, d, tot, b(m, m-d))
        ok += 1
print("chain-count exact OK, cases", ok)
viol = []; minratio = None
for d in range(1, 13):
    for m in range(max(2, 2*d-1), NM):
        w = m-d
        lhs = (w+2)*(m+1)*c(m+1, w+1); rhs = w*(m+2)*c(m, w)
        if not lhs > rhs: viol.append((m, d))
        if w >= 1:
            # ratio >= exp(1/(4(w+1)(w+2))) > 1 + 1/(4(w+1)(w+2))
            if lhs/rhs < 1 + Fr(1, 4*(w+1)*(w+2)): viol.append(("ratio", m, d))
print("diag (6.26) violations in first layer m<=", NM-1, ":", viol)
# outside the first layer (m = 2d-2): does it fail?
out = [(m, d) for d in range(2, 13) for m in (2*d-2,) if m >= 2 and m+1 <= NM and not (m-d+2)*(m+1)*c(m+1, m-d+1) > (m-d)*(m+2)*c(m, m-d)]
print("diag fails just outside (m=2d-2):", out)
# --- cor-L (6.34)
bad = []
for y in range(2, 12):
    for n in range(y+1, min(2*y+1, NM)+1):
        def sT(t, yy): return Fr(min(t, yy), t)*s(t-1, yy)
        P = sum(sT(t, y+1)-2*sT(t, y)+sT(t, y-1) for t in range(y, n+1))
        if y*P < -1 - Fr(y*(y-1), n)*c(n-1, y-1): bad.append((y, n))
print("cor-L violations:", bad)
# --- 6.5: identity (6.40) and 6.6: identity (6.42), ladder
for k in range(2, 12):
    if 2*k+1 > NM: break
    pm = lambda m: (k+1)*c(m, k) - (k-1)*c(m, k-1)
    V = sum(pm(m) for m in range(k, 2*k+1))
    DD = lambda m: (k+1)*s(m+2, k+1) - 2*k*s(m+1, k) + (k-1)*s(m, k-1)
    Bd = 2 - 2*s(2*k+1, k+1) - (k-1)*vs(2*k, k) - (k-1)*c(2*k, k-1)
    assert V == Bd + sum(DD(m) for m in range(k, 2*k)), ("6.40", k)
    # x_{m+1}(k) relation: p_m = (m+1) x_{m+1}(k)
print("(6.40) exact OK")
# first-layer end / b_{m,k}>0 and delta formula
for k in range(2, 12):
    for m in range(k+1, min(2*k, NM)+1):
        assert b(m, k) > 0
print("b_{m,k}>0 for m>=k+1 OK")
# split mass lemma
for g in range(1, 15):
    assert sum(cg(i)*cg(g-i) for i in range(1, g)) == 2*(1-Fr(1, g))*cg(g)
print("split-mass OK")
