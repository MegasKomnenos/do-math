# M1: 정리 chain-expansion(라), moving-tail (가)-(사), chain-normalization (가)(다) 수치 대조
from math import comb, factorial, exp, sqrt, pi
from fractions import Fraction as Fr
from functools import lru_cache
from itertools import product

@lru_cache(None)
def A(n, l):
    if l < 0: return 0
    if n == 0: return 1
    return sum(comb(n-1, j)*min(j+1, l+1)*A(j, l)*A(n-1-j, l) for j in range(n))
def b(n, l): return A(n, l)-A(n, l-1)
def p(n): return (n+1)**(n-1) if n >= 1 else 1
def Ren(j): return Fr(1) if j == 0 else Fr(j**j, factorial(j))*Fr(1)  # times e^{-j} handled separately
ok = True

def W(n, gam):
    j = len(gam); t = [n+1-sum(gam[:i+1]) for i in range(j)]
    if t[-1] < 1: return 0
    num = factorial(n)*t[-1]**(t[-1]-1)*gam[0]**(gam[0]-1)
    for g in gam[1:]: num *= g**g
    den = factorial(t[-1])*factorial(gam[0]-1)
    for g in gam[1:]: den *= factorial(g)
    return Fr(num, den), t

def comps(total_max, j):
    # all gamma tuples of length j with each >=1 and sum <= total_max
    def rec(j, rem):
        if j == 0: yield (); return
        for g in range(1, rem-(j-1)+1):
            for rest in rec(j-1, rem-g): yield (g,)+rest
    return rec(j, total_max)

for n in range(3, 16):
    for r in range(1, (n-1)//2+1):
        lhs = b(n, n-r-1)-b(n, n-r)
        Qs = []
        for j in range(1, r+2):
            Q = Fr(0)
            for gam in comps(r+1, j):
                Wv, t = W(n, gam)
                def f(d):
                    pr = Fr(1)
                    for ti in t: pr *= Fr(max(d-(n+1-ti), 0), ti)
                    return pr
                Q += Wv*(f(r+2)-2*f(r+1)+f(r))
            Qs.append(Q)
            if Q < 0: ok = False; print("Q negative", n, r, j)
        rhs = sum((-1)**(j)*Qs[j-1]*(-1) for j in range(1, r+2))  # (-1)^{j+1}
        rhs = sum(((-1)**(j+1))*Qs[j-1] for j in range(1, r+2))
        if rhs != lhs: ok = False; print("chain-expansion (라) FAIL", n, r, lhs, rhs)
        # moving-tail (가)
        Q1 = Fr(comb(n, r)*(n-r)**(n-r-2)*(r+1)**r)
        if Qs[0] != Q1: ok = False; print("Q1 closed FAIL", n, r)
        if not (Qs[0]-(Qs[1] if r >= 1 and len(Qs) > 1 else 0) <= lhs <= Qs[0]): ok = False; print("moving-tail (가) FAIL", n, r)
        for m in range(1, r+2):
            partial = sum(((-1)**(j+1))*Qs[j-1] for j in range(1, m+1))
            if not ((-1)**m*(lhs-partial) >= 0): ok = False; print("moving-tail (가) general FAIL", n, r, m)
        # (나)
        if len(Qs) > 1:
            Q2 = Fr(0)
            for g1 in range(1, r+1):
                for g2 in range(1, r+1):
                    t1 = n+1-g1; t2 = t1-g2
                    if t2 < 1: continue
                    Wv, _ = W(n, (g1, g2))
                    if g1+g2 <= r: Q2 += 2*Wv/(t1*t2)
                    elif g1+g2 == r+1: Q2 += (g2+1)*Wv/(t1*t2)
            if Q2 != Qs[1]: ok = False; print("moving-tail (나) FAIL", n, r)
        # (사) and (마) with floats
        nf = exp(r)*factorial(n)/factorial(n-r)*(n-r)**(n-r-2)/n**(n-2)
        eRen = exp(1)*(r+1)**(r+1)*exp(-(r+1))/factorial(r+1)
        val = nf*eRen + float(Fr(b(n, n-r)-b(n, n-r-1), n**(n-2)))
        if not (-1e-12 <= val <= exp(1)*(5*r-1)/(4*n*(1-r/n)**4)+1e-12): ok = False; print("moving-tail (마) FAIL", n, r, val)
        if not (abs(float(Fr(b(n, n-r-1)-b(n, n-r), n**(n-2))) - eRen) <= 60*(r+1)/n): ok = False; print("moving-tail (사) FAIL", n, r)
        if not ((n/(n-r))**2 <= nf <= (n/(n-r))**3): ok = False; print("moving-tail (다) FAIL", n, r)
print("chain-expansion/moving-tail ok =", ok)
# (바)
from math import lgamma, log
for r in range(0, 2000):
    leRen = 1+(r+1)*log(r+1)-(r+1)-lgamma(r+2)
    if not (leRen <= 1e-12): ok = False; print("(바) upper FAIL", r)
    if r >= 1 and not (leRen >= -0.5-0.5*log(r)-1e-12 and exp(-0.5)*r**-0.5 > 1/(2*sqrt(r+1))): ok = False; print("(바) lower FAIL", r)
# (라) sums
def RenF(j): return j**j*exp(-j)/factorial(j)
for eta in range(2, 120):
    s = sum(RenF(g)*RenF(eta-g) for g in range(1, eta)); s2 = sum((eta-g)*RenF(g)*RenF(eta-g) for g in range(1, eta))
    if not (s <= 0.5 and s2 <= eta/4): ok = False; print("(라) sums FAIL", eta, s, s2)
# (아): D>=2, n>=20 D^{3/2}: check small D with recursion where feasible (n up to ~60)
for D in range(2, 4):
    import math
    n0 = math.ceil(20*D**1.5)
    for n in range(n0, n0+3):
        row = [b(n, l) for l in range(n)]
        if not all(row[n-D+i] > row[n-D+i+1] for i in range(0, D-1)): ok = False; print("(아) FAIL", D, n)
print("(바)(라)(아) ok =", ok)
# chain-normalization (가),(다) for iota=0..3
for n in range(5, 14):
    for r in range(1, (n-1)//2+1):
        for iota in range(0, 4):
            if n < max(2*r+1, 2*r+2*iota-3): continue
            lhs = sum((-1)**(iota-i)*comb(iota, i)*(p(n)-A(n, n-(r+i))) for i in range(iota+1))
            lhs = Fr(lhs, n**(n-2))
            tot = Fr(0)
            for j in range(1, r+iota+1):
                for gam in comps(r+iota-1, j):
                    Wv, t = W(n, gam)
                    def g(d):
                        pr = Fr(1)
                        for ti in t: pr *= max(d-(n+1-ti), 0)
                        return pr
                    diff = sum((-1)**(iota-i)*comb(iota, i)*g(r+i) for i in range(iota+1))
                    prodt = 1
                    for ti in t: prodt *= ti
                    tot += ((-1)**(j+1))*Wv*diff/(prodt*n**(n-2))
            if tot != lhs: ok = False; print("chain-normalization (다) FAIL", n, r, iota, lhs, tot)
print("chain-normalization ok =", ok)
