# 7.6-7.7절 수치 검산 (K7b)
from mpmath import mp, mpf, sqrt, log, exp, pi, e, binomial, factorial
mp.dps = 30
print("(2pi)^-1/2 =", 1/sqrt(2*pi))
print("(2pi)^-1/2 e^-1/12 =", exp(-mpf(1)/12)/sqrt(2*pi))
print("2/sqrt(2pi) =", 2/sqrt(2*pi))
print("1-0.8/sqrt(301) =", 1-mpf('0.8')/sqrt(301))
print("0.9538/0.398943 =", mpf('0.9538')/mpf('0.398943'))
print("0.14*2.38*0.9999 =", mpf('0.14')*mpf('2.38')*mpf('0.9999'))
print("0.14*301 =", mpf('0.14')*301)
k=mpf(3131)
print("n=2k+1 =", 2*k+1, " i_n bound =", 1/(2*(2*k+2))+1/(6*(2*k+1)*(2*k+2)), " exp(-) =", exp(-(1/(2*(2*k+2))+1/(6*(2*k+1)*(2*k+2)))))
print("D_k(2) at 3131 =", mpf('0.08329')*sqrt(k)-2-mpf('42.14')/k, " 0.33316/4=", mpf('0.33316')/4)
print("(1+1/k)^(4/3) =", (1+1/k)**(mpf(4)/3), " 2/k=", 2/k)
u=k**(mpf(1)/6); print("k^(1/6) =", u)
f = mpf('0.33316')*(k**mpf('0.5')-2*k**(mpf(1)/6)+k**(-mpf(1)/6)) - mpf('1.0005')*k**(mpf(1)/3) - mpf('1.0145')
print("right end value at 3131 =", f)
fp = mpf('0.33316')*(3*k**(mpf(1)/3)-2-k**(-mpf(1)/3)) - mpf('2.001')*u
print("derivative wrt u at 3131 =", fp)
# n_PD(k) and check 3k+2
import math
nPD = math.ceil((3132)**(4/3))+3131+1
print("n_PD(3131) =", nPD, " 3k+2 =", 3*3131+2)
# exact G_k(n) over the range for k=3131 (direct) using i_n exact
def G(k,n):
    k=mpf(k); n=mpf(n)
    i_n = n*log(n/(n+1))+1
    return mpf('0.14')/n*(mpf('2.38')*k**mpf('1.5')*(n-k+1)**2/(exp(i_n)*n*(n+1))-301)
mn = min(G(3131,n) for n in range(2*3131+1, nPD))
print("min G_3131(n) over [2k+1,nPD-1] =", mn)
for kk in [3131, 3200, 5000, 10000]:
    nPDk = math.ceil((kk+1)**(4/3))+kk+1
    vals=[G(kk,n) for n in range(2*kk+1, nPDk, max(1,(nPDk-2*kk)//2000))]
    print(kk, "min G sampled =", min(vals), " G(2k+1)=", G(kk,2*kk+1), " G(nPD-1)=", G(kk,nPDk-1))
# is G>1 at k=3130?
kk=3130; nPDk=math.ceil((kk+1)**(4/3))+kk+1
print("k=3130 G(2k+1)=", G(kk,2*kk+1), " G(nPD-1)=", G(kk,nPDk-1))
# 7.7 numbers
k=mpf(6667)
print("e^0.3 =", exp(mpf('0.3')))
val = (mpf('0.3')*k-1)*(mpf('0.3')*k)/(2*(mpf('1.3')*k+1))
print("(0.3k-1)(0.3k)/(2(1.3k+1)) at 6667 =", val)
print("1+1.5 log k - val =", 1+mpf('1.5')*log(k)-val)
print("e^{3/(2k)} =", exp(3/(2*k)))
print("1.00023*1.34986 =", mpf('1.00023')*mpf('1.34986'))
print("2*0.7654-1.3502 =", 2*mpf('0.7654')-mpf('1.3502'))
# exact Pi^up_{j0+1} vs bound at k=6667
j0 = int(0.3*6667)
lp = sum(log(mpf(6668)/mpf(6667+i)) for i in range(1, j0+2))
print("j0 =", j0, " log Pi^up_{j0+1} exact =", lp, " bound -j0(j0+1)/(2(k+1+j0)) =", -mpf(j0)*(j0+1)/(2*(6667+1+j0)))
# LRP: x_k n > 368
k=mpf(501); xk=(k/(k+1))**(k-1); print("x_501*1003 =", xk*1003, " 1003/e=", 1003/e)
# rw(nu)=1 and ratio check small case, exact
from fractions import Fraction
def p(m): return Fraction((m+1)**(m-1)) if m>=0 else None
def Pn(n,j): return Fraction(j)*binomial_int(n-1,j-1)*p(j-1)*p(n-j)/p(n)
def binomial_int(a,b):
    from math import comb; return Fraction(comb(a,b))
for (kk,nu) in [(3,1),(4,2),(5,3),(6,1)]:
    n=2*kk+nu
    rw=lambda q: Fraction(kk,kk+1+q)*Pn(n,kk+1+q)/Pn(n,kk)
    assert rw(nu)==1
    ok=all(rw(q)>=1 for q in range(nu,kk+nu))
    print("rw check k,nu=",kk,nu," rw(nu)=1 ok, rw>=1 for q>=nu:",ok, " min rw below nu:", float(min(rw(q) for q in range(0,nu))) if nu>0 else None)
