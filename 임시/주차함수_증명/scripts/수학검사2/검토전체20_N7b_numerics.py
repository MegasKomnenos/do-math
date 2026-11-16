from mpmath import mp, mpf, sqrt, log, exp, pi, e
mp.dps = 30
k = mpf(3131)
print("sqrt(2pi)^-1 =", 1/sqrt(2*pi))
print("1-0.8/sqrt(301) =", 1-mpf('0.8')/sqrt(301))
print("0.9538/0.398943 =", mpf('0.9538')/mpf('0.398943'))
print("0.14*2.38*0.9999 =", mpf('0.14')*mpf('2.38')*mpf('0.9999'))
n0 = 2*k+1
sg = n0*log(n0/(n0+1))+1
print("sg_6263 =", sg, " e^-sg =", exp(-sg))
print("D_k(2) at 3131 =", mpf('0.08329')*sqrt(k)-2-mpf('42.14')/k)
print("0.33316/4 =", mpf('0.33316')/4)
print("(1+1/k)^(4/3) =", (1+1/k)**(mpf(4)/3), " 2/k =", 2/k)
t = k**(mpf(1)/6)
print("k^(1/6) =", t, " k^(1/3) =", k**(mpf(1)/3))
val = mpf('0.33316')*(sqrt(k)-2*t+1/t) - mpf('1.0005')*k**(mpf(1)/3) - mpf('1.0145')
print("D_k(nPD/k) lower at 3131 =", val)
der = mpf('0.33316')*(3*k**(mpf(1)/3)-2-k**(-mpf(1)/3)) - mpf('2.001')*t
print("derivative at 3131 =", der)
print("42.14/3131+1.001 =", mpf('42.14')/k+mpf('1.001'))
# n_PD bound check: n_PD(k)/k <= k^{1/3}(1+1/k)^{4/3}+1+2/k ; n_PD = ceil((k+1)^{4/3})+k+1
import math
for kk in [3131, 3132, 5000, 6667, 6668, 10000, 20000]:
    nPD = math.ceil((kk+1)**(4/3)) + kk + 1
    ub = kk**(1/3)*(1+1/kk)**(4/3) + 1 + 2/kk
    lb = kk**(1/3)
    print(kk, nPD, nPD/kk, "<=", ub, nPD/kk <= ub, ">=k^(1/3)", nPD/kk >= lb, "nPD>=3k+2", nPD >= 3*kk+2)
# k=2000 check of (k+1)^(4/3) ceil vs 3k+2
for kk in [2000, 2001, 3000, 3131]:
    nPD = math.ceil((kk+1)**(4/3)) + kk + 1
    print("nPD", kk, nPD, "3k+2 =", 3*kk+2, nPD>=3*kk+2)
# threshold-unit-ratio numerics
k = mpf(6667)
j0 = mp.floor(mpf('0.3')*k)
print("j0 =", j0, " (0.3k-1)(0.3k)/(2(1.3k+1)) =", (mpf('0.3')*k-1)*(mpf('0.3')*k)/(2*(mpf('1.3')*k+1)))
print("1+1.5 log k - that =", 1+mpf(1.5)*log(k)-(mpf('0.3')*k-1)*(mpf('0.3')*k)/(2*(mpf('1.3')*k+1)))
print("exact: 1+1.5log k + j0(j0+1)/(2(k+1+j0)) neg =", 1+mpf(1.5)*log(k)-j0*(j0+1)/(2*(k+1+j0)))
print("e^0.3 =", exp(mpf('0.3')))
print("e^{3/(2k)} =", exp(3/(2*k)))
print("1.00023*1.34986 =", mpf('1.00023')*mpf('1.34986'))
print("2*0.7654-1.3502 =", 2*mpf('0.7654')-mpf('1.3502'))
print("(1+1/k)^j0 =", (1+1/k)**j0, " <= e^0.3", (1+1/k)**j0 <= exp(mpf('0.3')))
# v_k bound: a<2, c<=5 -> a^2 + c^2/2
print("4+12.5 =", 4+12.5, " 1003/e =", 1003/e)
# Robbins sanity: Bor(d) <= (2pi)^-1/2 d^-3/2
from mpmath import factorial
for d in [1,2,5,10,100]:
    bor = exp(-d)*mpf(d)**(d-1)/factorial(d)
    print("Bor",d, bor, bor <= mpf(d)**(-1.5)/sqrt(2*pi))
# sum Bor(d), d=1..301
S = sum(exp(-d)*mpf(d)**(d-1)/factorial(d) for d in range(1,302))
print("sum Bor 1..301 =", S)
