# R2 검산: 4.3절의 정확 항등식 (4.1), 명제 4:old-4-6의 치환식, 2.7절 환원(작은 n 전수)
import itertools, sys
import sympy as sp
from math import comb, factorial
from fractions import Fraction as Fr

def park(a):
    n = len(a); occ = [0]*(n+2); pos = [0]*n
    for i, ai in enumerate(a):
        p = ai
        while p <= n and occ[p]: p += 1
        if p > n: return None
        occ[p] = i+1; pos[i] = p
    return pos, occ

def brute(n):
    # returns dict: for each parking function: (M, M#, blocked?), outcome perm
    res = []
    for a in itertools.product(range(1, n+1), repeat=n):
        r = park(a)
        if r is None: continue
        pos, occ = r
        d = [pos[i]-a[i] for i in range(n)]
        M = max(d); cnt = d.count(M)
        sigma = occ[1:n+1]  # car at spot i
        h = []
        for i in range(1, n+1):
            js = [j for j in range(1, i) if sigma[j-1] > sigma[i-1]]
            h.append(i - (max(js) if js else 0))
        blocked = all(h[pos[i]-1] == M+1 for i in range(n) if d[i] == M)
        res.append((M, cnt, blocked, tuple(sigma), tuple(h)))
    return res

y = sp.symbols('y')
def Kpoly(N, k):
    K = [sp.Integer(1)]
    for n in range(1, N+1):
        s = 0
        for j in range(n):
            wg = (j+1) if j+1 <= k else y
            s += comb(n-1, j)*wg*K[j]*K[n-1-j]
        K.append(sp.expand(s))
    return K

def Jpoly_brute(n, k, z):
    tot = 0
    for sigma in itertools.permutations(range(1, n+1)):
        h = []
        for i in range(1, n+1):
            js = [j for j in range(1, i) if sigma[j-1] > sigma[i-1]]
            h.append(i - (max(js) if js else 0))
        H = sum(1 for v in h if v == k); Z = sum(1 for v in h if v > k)
        if H == 0: continue
        pr = 1
        for v in h:
            if v < k: pr *= v
        tot += H*k**(H-1)*z**Z*pr
    return tot

ok = True
for n in range(2, 8):
    res = brute(n)
    assert len(res) == (n+1)**(n-1)
    b = [sum(1 for r in res if r[0] == l) for l in range(n+1)]
    for k in range(1, n+1):
        E = sum(1 for r in res if r[0] == k and r[1] % 2 == 0)
        E2 = sum(1 for r in res if r[0] == k and r[1] == 2)
        B = sum(1 for r in res if r[0] == k-1 and r[2])
        d = b[k] - b[k-1]
        K = Kpoly(n, k)
        e_n = sp.diff(K[n], y, 2).subs(y, k)
        J = Jpoly_brute(n, k, k-1)
        c1 = (d == 2*E - B); c2 = (e_n == 2*E2); c3 = (B <= J); c4 = (n > 2*k-1 or B == J)
        c5 = (n != 2*k or B == J - comb(2*k-1, k-1)*(k**(k-2))**2) if k >= 2 else True
        if not (c1 and c2 and c3 and c4 and c5):
            ok = False; print("FAIL", n, k, c1, c2, c3, c4, c5)
print("brute identities n<=7 ok:", ok)

# (4.1)과 명제 4.6의 치환식: Lagrange 계수 [x^n] g(T) = [Y^n] g(Y)(1-Y)e^{nY}
Y, Z = sp.symbols('Y Z')
def trunc(expr, deg):
    p = sp.Poly(sp.expand(expr), Y, Z)
    return sum(c*Y**i*Z**j for (i, j), c in p.terms() if i+j <= deg)
def ser1(f, var, deg):
    return sp.series(f, var, 0, deg+1).removeO()
def check_k(k):
    N = 2*k+2   # n<=2k+1 은 성립해야 하고 n=2k+2 는 일반적으로 어긋남
    Bt = 1 - sum(sp.exp(-j*Z)*(j*Z)**(j-1)/factorial(j) for j in range(1, k+1))
    Bt = ser1(Bt, Z, N+1)
    V = lambda t: (1-t)**2/2
    Jv = sp.expand(V(Z) - V(Y))
    eJ = sum((k*Jv)**m/sp.factorial(m) for m in range(N+2))
    integrand = trunc(sp.expand((1-Z)**2*Bt)*trunc(eJ, N+1)*(2*Jv + k*Jv**2), N+1)
    inner = sp.integrate(integrand, (Z, 0, Y))
    Phi = sp.expand(ser1(sp.exp(Y), Y, N+1)*inner)
    K = Kpoly(N, k)
    out = []
    for n in range(1, N+1):
        g = sp.expand(Phi*(1-Y)*ser1(sp.exp(n*Y), Y, N+1))
        coeff = sp.Poly(g, Y).coeff_monomial(Y**n)
        e_n = sp.diff(K[n], y, 2).subs(y, k)
        out.append((n, sp.nsimplify(coeff - sp.Rational(e_n, factorial(n))) == 0))
    return out
for k in (2, 3):
    print("(4.1) k=%d:" % k, check_k(k))

def check_J(k):
    N = 2*k+1
    Bork = sp.exp(-k)*sp.Integer(k)**(k-1)/factorial(k)
    integrand = (1-Z)*Z**(k-1)*sp.exp(k*(1-Z) + (k-1)*(1-Z)**2/2)
    integrand = ser1(integrand, Z, N+1)
    inner = sp.integrate(integrand, (Z, 0, Y))
    G = sp.expand(ser1(sp.exp(Y)*sp.exp(-(k-1)*(1-Y)**2/2), Y, N+1)*inner)
    out = []
    for n in range(1, N+1):
        g = sp.expand(G*(1-Y)*ser1(sp.exp(n*Y), Y, N+1))
        coeff = sp.simplify(Bork*sp.Poly(g, Y).coeff_monomial(Y**n))
        if n <= 7:
            Jn = Jpoly_brute(n, k, k-1)
            out.append((n, sp.simplify(coeff - sp.Rational(Jn, factorial(n))) == 0))
    return out
for k in (2, 3):
    print("prop 4.6 치환식 k=%d:" % k, check_J(k))
