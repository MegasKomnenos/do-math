from mpmath import mp, mpf, sqrt, exp, log, e, pi, cbrt
mp.dps = 30
def g(x): return (x-1)*log(1+1/x)
# theorem-W (나)
k = mpf(3131)
print("sqrt(2pi)^-1 =", 1/sqrt(2*pi))
print("1-0.8/sqrt(301) =", 1-mpf('0.8')/sqrt(301))
print("0.9538/0.398943 =", mpf('0.9538')/mpf('0.398943'))
n = 2*k+1
sg = n*log(n/(n+1))+1
print("sg_6263 =", sg, " e^-sg =", exp(-sg), " bound 1/(2(n+1))+1/(6n(n+1)) =", 1/(2*(n+1))+1/(6*n*(n+1)))
print("0.14*2.38*0.9999 =", mpf('0.14')*mpf('2.38')*mpf('0.9999'))
print("D_k(2) at 3131 =", mpf('0.08329')*sqrt(k)-2-mpf('42.14')/k, " 0.33316/4=", mpf('0.33316')/4)
print("(1+1/k)^(4/3) =", (1+1/k)**(mpf(4)/3), " 2/k=", 2/k)
u = k**(mpf(1)/6)
print("k^(1/6)=", u)
val = mpf('0.33316')*(sqrt(k)-2*u+1/u) - mpf('1.0005')*k**(mpf(1)/3) - mpf('1.0145')
print("right end bound at 3131 =", val)
der = mpf('0.33316')*(3*k**(mpf(1)/3)-2-k**(-mpf(1)/3)) - mpf('2.001')*u
print("derivative at 3131 =", der)
print("42.14/3131+1.001 =", mpf('42.14')/k+mpf('1.001'))
# exact n_PD/k at 3131
import math
nPD = math.ceil((3131+1)**(4/3))+3131+1
print("n_PD(3131)=", nPD, " n_PD/k=", mpf(nPD)/k, " bound 1.0005k^(1/3)+1.001=", mpf('1.0005')*k**(mpf(1)/3)+mpf('1.001'), " k^(1/3)=", k**(mpf(1)/3))
print("n_PD>=3k+2?", nPD >= 3*3131+2)
# direct check of G_k(n)>1 on a grid for k=3131
def G(k,n):
    k=mpf(k); n=mpf(n)
    sg = n*log(n/(n+1))+1
    return mpf('0.14')/n*(mpf('2.38')*k**mpf('1.5')*(n-k+1)**2/(exp(sg)*n*(n+1))-301)
for kk in [3131, 3200, 5000, 10000]:
    nPDk = math.ceil((kk+1)**(4/3))+kk+1
    mn = min(G(kk,nn) for nn in range(2*kk+1, nPDk, max(1,(nPDk-2*kk)//2000)))
    print("k=",kk," min G over grid =", mn, " G(2k+1)=", G(kk,2*kk+1), " G(nPD-1)=", G(kk,nPDk-1))
# threshold-unit-ratio
k = mpf(6667)
j0 = mp.floor(mpf('0.3')*k)
print("j0=", j0, " exact sum bound -j0(j0+1)/(2(k+1+j0)) =", -j0*(j0+1)/(2*(k+1+j0)), " text bound =", -(mpf('0.3')*k-1)*(mpf('0.3')*k)/(2*(mpf('1.3')*k+1)))
print("1+1.5 log k - ... =", 1+mpf('1.5')*log(k)-(mpf('0.3')*k-1)*(mpf('0.3')*k)/(2*(mpf('1.3')*k+1)))
print("e^0.3 =", exp(mpf('0.3')))
print("e^{3/(2k)} =", exp(3/(2*k)))
print("1.00023*1.34986 =", mpf('1.00023')*mpf('1.34986'))
print("g(2k)-g(k) =", g(2*k)-g(k), " 3/(2k)=", 3/(2*k))
print("2*0.7654-1.3502 =", 2*mpf('0.7654')-mpf('1.3502'))
# old-6-22 bound
print("1003/e =", 1003/e)
print("(1+1/k)^{k-1} lower bound check: 1/e vs x_k at k=501:", (mpf(501)/502)**500, 1/e)
# C(2k,k) >= 4^k/(2 sqrt k) check small
from mpmath import binomial
for kk in [2,3,10,100]:
    print(kk, binomial(2*kk,kk) >= 4**kk/(2*sqrt(kk)))
# s_{2k-1}(k) >= e^{-1} k^{-3/2} chain check at k=10 via exact formula
for kk in [5,10,50]:
    val = binomial(2*kk-1,kk)*mpf(kk)**(kk-1)*mpf(kk-1)**(kk-2)/mpf(2*kk)**(2*kk-2)
    print(kk, val, exp(-1)*mpf(kk)**(-1.5), val>=exp(-1)*mpf(kk)**(-1.5))
