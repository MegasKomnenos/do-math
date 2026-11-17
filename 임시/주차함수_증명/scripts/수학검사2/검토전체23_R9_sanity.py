# R9: small-k sanity checks of 9.4-9.6 statements against exact parking-function counts
from fractions import Fraction as F
from math import comb, exp, log, sqrt, pi, lgamma
from functools import lru_cache
import sys
sys.setrecursionlimit(10000)
@lru_cache(None)
def A(m, l):
    if l < 0: return 1 if m == 0 else 0
    if m == 0: return 1
    return sum(comb(m-1, j-1)*min(j, l+1)*A(j-1, l)*A(m-j, l) for j in range(1, m+1))
def p(m): return (m+1)**(m-1) if m >= 1 else 1
def s(m, y): return A(m, y-1)/p(m)
def sF(m, y): return F(A(m, y-1), p(m))
def c(m, l): return (A(m, l)-A(m, l-1))/p(m)
def Bor(j): return exp(-j+(j-1)*log(j)-lgamma(j+1))
def Ren(j): return j*Bor(j)
f1 = 4/(3*sqrt(2*pi)); cR = sqrt(2*pi)/2*exp(1/12)
def slow(d, y): return exp(-f1*((y+d-1)/y)**1.5*d**1.5/y)
worst = {}
def rec(name, val):
    worst[name] = min(worst.get(name, 1e9), val)
for k in range(3, 41):
    y = k+1
    # chain representation thm 9:old-8-28: F(q)=E_q[Pi_L (1-1/y)^(L+1ch)]
    sy = {1: 1.0}; Fq = {}
    for q in range(1, k+2):
        tot = 0.0; accs = 0.0; accF = 0.0
        for qp in range(1, q):
            pr = Bor(q-qp)*Bor(y+qp)/Bor(y+q)
            tot += pr; accs += pr*y/(y+qp)*sy[qp]; accF += pr*y/(y+qp)*(1-1/y)*Fq[qp]
        pch = Bor(y)*Bor(q)/Bor(y+q)
        if q > 1: sy[q] = 1-tot+accs
        Fq[q] = (1-tot-pch)+pch*(1-1/y)+accF
        assert abs(sy[q]-s(y+q-1, y)) < 1e-9, (k, q)
        cc = c(k+q, k)
        assert abs((sy[q]-Fq[q])-cc) < 1e-9, ("chainrep", k, q, sy[q]-Fq[q], cc)
    for q0 in range(2, k+2):
        cc = c(k+q0, k)
        # lemma 30 (y=k+1 and y=k)
        rec("L30", s(y+q0-1, y)-slow(q0, y))
        # lemma 31(i)
        z = 0.0
        for q in range(1, q0):
            l = q0-q
            Aup = sqrt(2*pi)/4*exp(1/(12*l))*(q0+q)*sqrt(l)
            z += (2*pi)**-0.5*l**-0.5*exp(-1/(12*l))*exp(-(q+Aup)/y)*sy[q]
        Bgt = 1-sum(Bor(j) for j in range(1, q0))
        rhs = k/(k+1)*(1-q0/(2*k))*(max(z, sy[q0]-Bgt)+Bor(q0))
        rec("L31", k*cc-rhs)
        # lemma 32(i)
        Q = k/(k+1)*(1-q0/(2*k))*2*(2*pi)**-0.5*exp(-1/12)*y/(cR*q0)*(exp(-q0/y)*slow(q0, y)*(exp(-cR*q0/y)-exp(-cR*q0*sqrt(q0/2)/y))+exp(-q0/(2*y))*slow(q0/2, y)*(exp(-cR*q0*sqrt(q0/2+1)/y)-exp(-cR*q0**1.5/y)))
        rec("L32", k/(k+1)*(1-q0/(2*k))*z-Q)
    # supersolution phi_1 and capacity shift & reduction (5) ratio bound for all nu<=k-1
    for nu in range(2, k):
        N = k+nu
        sW = 1-sum(Bor(j)*(nu-j)/(k+nu+1-j) for j in range(1, nu))
        rec("sW", sW-s(N, k+1))
        ratio = s(N-1, k+1)/s(N-1, k)
        pitwo = Bor(k)*Bor(nu-1)/(exp(1)*Bor(N))
        rec("pitwo", s(N-1, k)-pitwo)
        best = 1e9
        for j0 in range(0, nu+1):
            Pup = 1.0
            for i in range(1, j0+2): Pup *= (k+1)/(k+i)
            best = min(best, (1+1/k)**min(j0, nu-1)+(1 if j0 < nu-1 else 0)*Pup/pitwo)
        rec("rstar", best-ratio)
        # u_n/w_k <= e^{3/(2k)} r_*  and theta-part (4)
        g = lambda x: (x-1)*log(1+1/x)
        uw = exp(g(N)-g(k))*s(N, k+1)/s(N-1, k)
        rec("uw<=", exp(3/(2*k))*best-uw)
        rec("uw>=1", uw-1)
        th = 2*(1+1/k)*s(N, k)/s(N, k+1)-1
        rec("thlb", th-(2*(1+1/k)**(1-nu)-1))
        wr = exp(g(k+1)-g(N-1))*s(N-2, k)/s(N-1, k)   # w_{k+1}/w_k
        if nu >= 2: rec("wratio", (1+1/(k-1))**(nu-1)-wr)
print({a: round(b, 6) for a, b in worst.items()})
# staying law based (da): Stays<=Stays^vis, exact, k=51..53 (needs y>=50)
for k in (51, 52):
    for nu in (1, 5, 20, 40, k-1):
        N = k+nu
        st = lambda m, l: sF(m+1, l+1)-sF(m, l)
        cF = lambda m, l: F(A(m, l)-A(m, l-1), p(m))
        Stays = 2*st(N+1, k)+sum((2-F(m-N, k))*(st(m, k)+st(m-1, k-1)) for m in range(N+2, 2*k+1))
        vis = 2*F(nu+1, k+1)*cF(N+2, k)+sum((2-F(m-N, k))*(F(m-k, k+1)*cF(m+1, k)+F(m-k, k)*cF(m, k-1)) for m in range(N+2, 2*k+1))
        print("k", k, "nu", nu, "Stays", float(Stays), "vis", float(vis), Stays <= vis)
# cancellation lemma 34: pure function check on a grid
import random
random.seed(1)
bad = 0; mn = 1e9
for _ in range(4000):
    k = random.randint(104, 60000); nu = random.randint(103, k-1); nup = random.uniform(nu, k-1)
    sW = 1-sum(Bor(j)*(nu-j)/(k+nu+1-j) for j in range(1, nu)) if nu < 3000 else None
    if sW is None: continue
    lhs = 4-3*sW+(2*(1+1/k)**(1-nu)-1)*(1+1/(k-1))**(-(nu-1))
    ec = 3*nup**2/((k-1)*k)+4.8*sqrt(nup)/k+nup**2/(2*(k-1)**2)
    mn = min(mn, lhs-(2-ec))
    if lhs < 2-ec: bad += 1
print("lemma34 violations", bad, "min margin", mn)
