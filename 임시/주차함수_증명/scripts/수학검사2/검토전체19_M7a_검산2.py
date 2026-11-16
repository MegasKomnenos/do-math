# M7a 검산 2: (7.6) 지수 공식과 (7.7) 초과 항등식을 k=3,4에서 z=k, k+1 (정확 유리수)로 확인한다.
from fractions import Fraction as Fr
from math import comb, factorial
from functools import lru_cache
import sys
out = []
def P(*a): out.append(" ".join(str(x) for x in a))

@lru_cache(None)
def A(n, l):
    if l < 0: return 0
    if n == 0: return 1
    return sum(comb(n-1, j-1)*min(j, l+1)*A(j-1, l)*A(n-j, l) for j in range(1, n+1))
def p(n): return (n+1)**(n-1) if n > 0 else 1

# 얼린 용량 다항식 K_{n,k}(z): 최대 원소(왼쪽에서 본) 분해 재귀 — (7.6)의 오른쪽-최댓값 조각 분해와 다른 길
def Kpoly(N, k, z):
    K = [Fr(1)]
    for n in range(1, N+1):
        K.append(sum(comb(n-1, pp-1)*(Fr(pp) if pp <= k else z)*K[pp-1]*K[n-pp] for pp in range(1, n+1)))
    return K

def mul(a, b, N):
    c = [Fr(0)]*(N+1)
    for i, x in enumerate(a):
        if x == 0: continue
        for j, y in enumerate(b):
            if i+j > N: break
            c[i+j] += x*y
    return c
def integ(a, N): return [Fr(0)]+[a[i]/(i+1) for i in range(N)]
def deriv(a, N): return [a[i+1]*(i+1) for i in range(N)]+[Fr(0)]
def expser(f, N):  # f[0]=0
    g = [Fr(0)]*(N+1); g[0] = Fr(1)
    fp = deriv(f, N)
    for n in range(1, N+1):
        g[n] = sum(fp[i]*g[n-1-i] for i in range(n))/n
    return g
def add(a, b): return [x+y for x, y in zip(a, b)]
def sub(a, b): return [x-y for x, y in zip(a, b)]
def scal(c, a): return [c*x for x in a]

bad = 0
for k in [3, 4]:
    N = 3*k+2
    for z in [Fr(k), Fr(k+1), Fr(k)-Fr(1, 3)]:
        K = Kpoly(N, k, z)
        D = [K[n]/factorial(n) for n in range(N+1)]
        if z == k:
            assert all(K[n] == A(n, k-1) for n in range(N+1))
        if z == k+1:
            assert all(K[n] == A(n, k) for n in range(N+1))
        E_lt = [Fr(p(n), factorial(n)) if n < k else Fr(0) for n in range(N+1)]
        Dge = sub(D, E_lt)
        Tle = [Fr(t**(t-1), factorial(t)) if 1 <= t <= k else Fr(0) for t in range(N+1)]
        T = [Fr(t**(t-1), factorial(t)) if t >= 1 else Fr(0) for t in range(N+1)]
        Tgt = sub(T, Tle)
        # (7.6)
        F = add(Tle, scal(z, integ(Dge, N)))
        D76 = expser(F, N)
        if D76 != D: bad += 1; P("  FAIL (7.6)", k, z)
        # G_* : S' = Q_k + z e^T S, S(0)=0
        eT = [Fr(p(n), factorial(n)) for n in range(N+1)]
        one = [Fr(1)]+[Fr(0)]*N
        Qk = mul(sub(one, T), sub(eT, E_lt), N)
        S = [Fr(0)]*(N+1)
        for n in range(0, N):
            # S'[n] = Qk[n] + z*(eT*S)[n]  -> S[n+1] = S'[n]/(n+1); (eT*S)[n] uses S[0..n]
            conv = sum(eT[i]*S[n-i] for i in range(n+1))
            S[n+1] = (Qk[n]+z*conv)/(n+1)
        Gst = add(add(E_lt, Qk), scal(z, mul(eT, S, N)))
        # 확인: G_* = e^T(1 - T_{>k} + z∫(G_*-E_{<k}))
        chk = mul(eT, add(sub(one, Tgt), scal(z, integ(sub(Gst, E_lt), N))), N)
        if chk != Gst: bad += 1; P("  FAIL G_* identity", k, z)
        X = sub(D, Gst)
        low = next((i for i, v in enumerate(X) if v != 0), None)
        if low != 2*k+2: bad += 1; P("  FAIL lowest degree", k, z, low)
        bd = sub(scal(z, integ(Dge, N)), Tgt)
        rhs = mul(expser(Tle, N), add(scal(z, integ(X, N)), scal(Fr(1, 2), mul(bd, bd, N))), N)
        if X != rhs: bad += 1; P("  FAIL (7.7)", k, z, [float(a-b) for a, b in zip(X, rhs)])
        # bd_t(z) = z K_{t-1}(z) - t^{t-1} for t>k
        for t in range(k+1, N+1):
            if bd[t]*factorial(t) != z*K[t-1]-t**(t-1): bad += 1; P("  FAIL bd_t", k, z, t)
P("(7.6)/(7.7) failures:", bad)
open(sys.argv[1], "w", encoding="utf-8").write("\n".join(out))
