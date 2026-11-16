# M1: 2.7절 동률-막힘 항등식(2-28), 보조정리 2-30, J-egf 재귀(가)와 닫힌 꼴(나), 2-29 를 전수 셈으로 대조 (n<=7)
from math import comb, factorial
from itertools import permutations, product
from functools import lru_cache
from fractions import Fraction
import sympy as sp

@lru_cache(None)
def A(n, l):
    if l < 0: return 0
    if n == 0: return 1
    return sum(comb(n-1, j)*min(j+1, l+1)*A(j, l)*A(n-1-j, l) for j in range(n))
def b(n, l): return A(n, l)-A(n, l-1)
def p(n): return (n+1)**(n-1) if n >= 1 else 1

def h_of(sig):
    n = len(sig); hs = []
    for i in range(1, n+1):
        z = max([j for j in range(1, i) if sig[j-1] > sig[i-1]] + [0])
        hs.append(i-z)
    return hs

def park(a):
    n = len(a); occ = [False]*(n+2); pos = [0]*n
    for i, ai in enumerate(a):
        q = ai
        while q <= n and occ[q]: q += 1
        if q > n: return None
        occ[q] = True; pos[i] = q
    return pos

ok = True
for n in range(1, 8):
    pfs = []
    for a in product(range(1, n+1), repeat=n):
        pos = park(a)
        if pos is None: continue
        d = [pp-x for pp, x in zip(pos, a)]
        sig = [0]*n
        for car, pp in enumerate(pos): sig[pp-1] = car+1
        pfs.append((a, d, tuple(sig)))
    hcache = {}
    for k in range(1, n+1):
        E = E2 = B = 0
        for a, d, sig in pfs:
            M = max(d); cnt = d.count(M)
            if M == k and cnt % 2 == 0: E += 1
            if M == k and cnt == 2: E2 += 1
            if M == k-1:
                if sig not in hcache: hcache[sig] = h_of(sig)
                hs = hcache[sig]
                if all(hs[i] == k for i in range(n) if d[sig[i]-1] == k-1): B += 1
        dnk = b(n, k)-b(n, k-1)
        if dnk != 2*E-B: ok = False; print("2-28 FAIL", n, k, dnk, 2*E-B)
        if not (2*E2-B <= dnk): ok = False; print("2-29 FAIL", n, k)
        # 2-30 first formula and J_n(k-1)
        Bf = 0; J = 0; Xi = 0
        for sig in permutations(range(1, n+1)):
            hs = h_of(sig); Z = sum(1 for h in hs if h > k); H = sum(1 for h in hs if h == k)
            pr = 1
            for h in hs:
                if h < k: pr *= h
            Bf += pr*(k-1)**Z*(k**H-(k-1)**H)
            J += pr*H*k**(H-1)*(k-1)**Z if H >= 1 else 0
        if Bf != B: ok = False; print("2-30 first formula FAIL", n, k, Bf, B)
        if not (B <= J): ok = False; print("2-30 ineq FAIL", n, k)
        if n <= 2*k-1 and B != J: ok = False; print("2-30 equality FAIL", n, k, B, J)
        if n == 2*k:
            Xi = comb(2*k-1, k-1)*p(k-1)**2
            if B != J-Xi: ok = False; print("2-30 Xi FAIL", n, k, B, J, Xi)
print("brute checks 2-28/2-29/2-30 done, ok =", ok)

# J-egf (가) recursion and (나) closed form, symbolic in z, for k=1..4, n<=2k
z, x = sp.symbols('z x')
def Jpoly(n, k):
    J = 0
    for sig in permutations(range(1, n+1)):
        hs = h_of(sig); Z = sum(1 for h in hs if h > k); H = sum(1 for h in hs if h == k)
        pr = 1
        for h in hs:
            if h < k: pr *= h
        if H >= 1: J += pr*H*k**(H-1)*z**Z
    return sp.expand(J)
# tree function series
N = 10
T = sum(sp.Integer(t)**(t-1)*x**t/sp.factorial(t) for t in range(1, N+1))
Gr = sp.expand(T - T**2/2)
def series_trunc(e, N): return sp.series(e, x, 0, N+1).removeO()
eT = series_trunc(sp.exp(T), N)
for k in range(1, 5):
    Js = {n: Jpoly(n, k) for n in range(0, min(2*k, 7)+1)}
    # (가)
    for n in range(0, min(2*k-1, 6)+1):
        rhs = sum(comb(n, i)*(z+i+1)*p(i)*Js[n-i] for i in range(n+1))
        if n >= k-1: rhs += comb(n, k-1)*p(k-1)*p(n-k+1)
        if sp.expand(rhs - Js[n+1]) != 0: ok = False; print("J-egf (가) FAIL", k, n)
    # (나)
    integrand = series_trunc(sp.exp(-z*Gr)*x**(k-1)/sp.factorial(k-1), N)
    integ = sp.integrate(integrand, x)
    Y = series_trunc(sp.expand(eT*series_trunc(sp.exp(z*Gr), N)*integ), N)
    Y = sp.expand(Y)
    for n in range(0, min(2*k, 7)+1):
        coeff = sp.expand(Y.coeff(x, n)*sp.factorial(n)*p(k-1))
        if sp.expand(coeff - Js[n]) != 0: ok = False; print("J-egf (나) FAIL", k, n, coeff, Js[n])
print("J-egf checks done, ok =", ok)
