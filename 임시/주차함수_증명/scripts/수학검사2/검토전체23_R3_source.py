# R3 검산: 5.2.1–5.2.2절의 항등식을 작은 n에서 전수(순열 열거)로 확인한다.
import itertools, sys
from fractions import Fraction as Fr
from math import comb, factorial
import sympy as sp
y = sp.symbols('y')
def p(n): return (n+1)**(n-1) if n >= 1 else 1
def caps(sig):
    n = len(sig); h = []
    for i in range(n):
        z = -1
        for j in range(i-1, -1, -1):
            if sig[j] > sig[i]: z = j; break
        h.append(i - z)
    return h
def Kpoly(n, k):
    tot = 0
    for sig in itertools.permutations(range(n)):
        t = 1
        for hi in caps(sig):
            t = t*(hi if hi <= k else y)
        tot += t
    return sp.expand(tot)
def A(n, l):
    if l < 0: return 0
    tot = 0
    for sig in itertools.permutations(range(n)):
        t = 1
        for hi in caps(sig): t *= min(hi, l+1)
        tot += t
    return tot
def Gam(d, n):
    g = [sp.Integer(1)]
    for dd in range(1, d+1):
        g.append(sp.expand(comb(n, dd)*p(dd) + y*sum(comb(n-dd+j, j)*p(j)*g[dd-1-j] for j in range(dd))))
    return g
# forests with all trees <= k : egf exp(T^{<=k})
x = sp.symbols('x')
def phi(k, M):
    T = sum(sp.Rational(t**(t-1), factorial(t))*x**t for t in range(1, k+1))
    ser = sp.series(sp.exp(T), x, 0, M+1).removeO()
    return [sp.factorial(m)*ser.coeff(x, m) for m in range(M+1)]
ok = True
for n in range(1, 8):
    for k in range(1, n+1):
        if n > 2*k+1: continue
        K = Kpoly(n, k); ph = phi(k, n); g = Gam(n, n) if n <= 1 else Gam(n-1, n)
        rhs = ph[n] + y*sum(ph[m]*g[n-m-1] for m in range(k, n))
        if sp.expand(K - rhs) != 0: ok = False; print("source-rep (ga) FAIL", n, k)
        # (da) of green-connection
        if k+1 <= n <= 2*k+1 and n >= 2:
            K1 = Kpoly(n, k+1)
            if sp.expand(K - K1 - (y-k-1)*p(k)*g[n-k-1]) != 0: ok = False; print("green (da) FAIL", n, k)
        if k <= n <= 2*k-1:
            Gm = p(k-1)*g[n-k].subs(y, k-1)
            if Gm != K.subs(y, k-1) - A(n, k-2): ok = False; print("Gamma- FAIL", n, k)
        if k+2 <= n <= 2*k-1:
            r = n-k
            Gp = p(k)*g[r-1].subs(y, k+2); Gm = p(k-1)*g[r].subs(y, k-1)
            b = lambda l: A(n, l)-A(n, l-1)
            d1 = b(k)-b(k-1); d2 = b(k+1)-b(k)
            S = Gp*d1 - Gm*d2
            hg = lambda d: sp.expand(y*g[d])
            sd = lambda d, v: hg(d).subs(y, v+1)-2*hg(d).subs(y, v)+hg(d).subs(y, v-1)
            S2 = sum(ph[n-d-1]*(Gp*sd(d, k)-Gm*sd(d, k+1)) for d in range(1, r))
            if S != S2: ok = False; print("S formula FAIL", n, k)
            print("n,k,r=", n, k, r, " S=", S, " d_{n,k}=", d1, " d_{n,k+1}=", d2,
                  " (G)_d strict:", [bool(sp.Rational(p(k), p(k-1))*g[r-1].subs(y, k+2)*sd(d, k) > g[r].subs(y, k-1)*sd(d, k+1)) for d in range(1, r)])
print("all identities ok:", ok)
