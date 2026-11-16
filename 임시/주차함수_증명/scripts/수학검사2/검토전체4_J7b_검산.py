# J7b 검산: 7.6-7.7절의 수치 상수들을 다시 센다.
from math import log, exp, sqrt, pi, e, ceil, floor, lgamma
from fractions import Fraction

def g(x): return (x-1)*log(1+1/x)
def Bor(d): return exp(-d + (d-1)*log(d) - lgamma(d+1))
def Ren(j): return j*Bor(j)

print("== explicit-bounds (가) ==")
print("(2pi)^-1/2 =", (2*pi)**-0.5, " *e^{-1/12} =", (2*pi)**-0.5*exp(-1/12), ">=0.367")
print("0.8 vs (2pi)^-1/2*2 =", (2*pi)**-0.5*2)
# Bor lower/upper check small d
for d in [1,2,5,50]:
    print(d, 0.367*d**-1.5, "<=", Bor(d), "<=", (2*pi)**-0.5*d**-1.5)
print("sum_{d<=301} Bor(d) =", sum(Bor(d) for d in range(1,302)), " 1-0.8/sqrt(301)=", 1-0.8/sqrt(301))

print("== theorem-W (가) 상수 ==")
print("0.9538/0.398943 =", 0.9538/0.398943, ">=2.38")
print("== theorem-W (나) ==")
k=3131; n0=2*k+1
i_n = n0*log(n0/(n0+1))+1
print("i_n at n=6263:", i_n, " e^-i_n =", exp(-i_n), " bound 1/(2(n+1))+1/(6n(n+1)) =", 1/(2*(n0+1))+1/(6*n0*(n0+1)))
print("0.14*2.38*0.9999 =", 0.14*2.38*0.9999, " 0.14*301=", 0.14*301)
def D(k,z): return 0.33316*sqrt(k)*(1-1/z)**2 - z - 42.14/k
print("D_3131(2) =", D(3131,2.0), " 0.08329*sqrt(k)-2-42.14/k =", 0.08329*sqrt(3131)-2-42.14/3131)
nPD = ceil((k+1)**(4/3))+k+1
print("n_PD(3131) =", nPD, " n_PD/k =", nPD/k, " bound 1.0005k^(1/3)+1.001 =", 1.0005*k**(1/3)+1.001, " k^(1/3)(1+1/k)^(4/3)+1+2/k=", k**(1/3)*(1+1/k)**(4/3)+1+2/k)
u=k**(1/6); print("k^(1/6) =", u)
rhs = 0.33316*(u**3-2*u+1/u)-1.0005*u**2-1.0145
print("D lower bound at right end =", rhs, " actual D(n_PD/k) =", D(k,nPD/k))
print("derivative at u:", 0.33316*(3*u**2-2-u**-2)-2.001*u)
# actual G_k(n) at n = n_PD-1 and n=2k+1
def G(k,n):
    i=n*log(n/(n+1))+1
    return 0.14/n*(2.38*k**1.5*(n-k+1)**2/(exp(i)*n*(n+1))-301)
print("G_3131(2k+1) =", G(k,2*k+1), " G_3131(n_PD-1) =", G(k,nPD-1))
# min over n in [2k+1, nPD-1] (coarse)
mn=min(G(k,n) for n in range(2*k+1,nPD)); print("min G_3131 over range =", mn)
# check concavity claim numerically for D at k=3131
import itertools
zs=[2+i*0.01 for i in range(int((nPD/k-2)/0.01)+1)]
print("min D_3131 on grid =", min(D(k,z) for z in zs))
# (1+1/(n-k))^2(1-1/(n+1))>=1 spot check
for (kk,nn) in [(2,5),(3131,6263),(3131,48000)]:
    print("check", kk,nn, (1+1/(nn-kk))**2*(1-1/(nn+1)))

print("== threshold-unit-ratio ==")
k=6667; j0=floor(0.3*k)
val=-(0.3*k-1)*(0.3*k)/(2*(1.3*k+1)); print("-(0.3k-1)(0.3k)/(2(1.3k+1)) at 6667 =", val)
exact=-sum(log(1+i/(k+1)) for i in range(1,j0+1)); print("exact log Pi^up_{j0+1} =", exact, " bound -sum i/(k+1+i)=", -sum(i/(k+1+i) for i in range(1,j0+1)), " -j0(j0+1)/(2(k+1+j0))=", -j0*(j0+1)/(2*(k+1+j0)))
rhs=1+1.5*log(k)+val; print("1+1.5log k + val =", rhs)
for kk in [6667,7000,10000,10**5]:
    print(" rhs(k=%d) ="%kk, 1+1.5*log(kk)-(0.3*kk-1)*(0.3*kk)/(2*(1.3*kk+1)))
print("e^0.3 =", exp(0.3), " e^{3/(2k)} at 6667 =", exp(3/(2*k)), " product 1.00023*1.34986 =", 1.00023*1.34986)
print("2*0.7654-1.3502 =", 2*0.7654-1.3502)
# two-tree lower bound e^{-1}k^{-3/2} check: C(2k-1,k)k^{k-1}(k-1)^{k-2}/(2k)^{2k-2}
from math import comb
for kk in [5,50,500]:
    v=Fraction(comb(2*kk-1,kk)*kk**(kk-1)*(kk-1)**(kk-2), (2*kk)**(2*kk-2))
    print(" two-tree bound k=%d: %.6g  vs e^-1 k^-3/2 = %.6g"%(kk,float(v),exp(-1)*kk**-1.5))
print("== old-6-22 ==")
print("x_k n lower: 1003/e =", 1003/e, " 2^2+ (2+3)^2/2 =", 4+25/2)
print("3*3333-1 =", 3*3333-1, " 3*6666-1=", 3*6666-1, " 3*6667-1=", 3*6667-1)
print("== root-symmetry sanity (exact) ==")
def P(n,j):
    pn=lambda m: (m+1)**(m-1) if m>=1 else 1
    return Fraction(j*comb(n-1,j-1)*pn(j-1)*pn(n-j), pn(n))
for (k,nu) in [(3,1),(4,2),(5,3)]:
    n=2*k+nu
    rw=lambda q: Fraction(k,k+1+q)*P(n,k+1+q)/P(n,k)
    print(" k=%d nu=%d rw(nu)=%s"%(k,nu,rw(nu)), " ratios:", [float(rw(q+1)/rw(q)) for q in range(0,k+nu-1)], " e^{g diff}:", [exp(g(k+1+q)-g(k+nu-1-q)) for q in range(0,k+nu-1)])
print("== w_m formula check: w_m = 𝔴_n(m+1)/(n A_{n,k-1}) (symbolic ratio) ==")
for (n,m) in [(10,3),(13,5)]:
    pn=lambda t: (t+1)**(t-1) if t>=1 else 1
    lhs=Fraction(comb(n-1,m)*pn(m)); rhs=Fraction(comb(n,m+1)*(m+1)**m, n)
    print(" ", n,m, lhs==rhs)
