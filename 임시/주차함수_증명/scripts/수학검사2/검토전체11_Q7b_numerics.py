# Q7b numeric re-checks for 7.6-7.7 (chapter 7B)
from mpmath import mp, mpf, sqrt, log, exp, pi, binomial, factorial, cbrt
mp.dps = 30
def report(name, val, claim):
    print(f"{name}: {val}  | claim: {claim}")
# explicit-bounds (가): tail constant, 0.9538
report("(2pi)^-1/2 *2", 2/sqrt(2*pi), "<=0.8")
report("1-0.8/sqrt(301)", 1-mpf('0.8')/sqrt(301), ">=0.9538")
# exact Borel sum to 301
def Bor(d): return exp(-d)*mpf(d)**(d-1)/factorial(d)
S=sum(Bor(d) for d in range(1,302)); report("sum_{d<=301} Bor(d)", S, ">=0.9538 (exact)")
report("(2pi)^-1/2", 1/sqrt(2*pi), "<=0.398943")
report("0.9538/0.398943", mpf('0.9538')/mpf('0.398943'), ">=2.38")
# theorem-W (나)
k=3131; n=2*k+1
im = lambda m: m*log(mpf(m)/(m+1))+1
report("i_n at n=6263", im(n), "e^{-i_n}>=0.9999 -> i_n <= 1.00005e-4")
report("exp(-i_6263)", exp(-im(n)), ">=0.9999")
report("0.14*2.38*0.9999", mpf('0.14')*mpf('2.38')*mpf('0.9999'), ">=0.33316")
report("0.14*301", mpf('0.14')*301, "=42.14")
report("0.33316/4", mpf('0.33316')/4, "=0.08329")
Dk2 = mpf('0.08329')*sqrt(k)-2-mpf('42.14')/k
report("D_3131(2)", Dk2, ">2.647")
# right end
k16 = mpf(k)**(mpf(1)/6)
report("3131^(1/6)", k16, ">=3.8248")
rhs = mpf('0.33316')*(sqrt(k)-2*k16+1/k16)-mpf('1.0005')*cbrt(k)-mpf('1.0145')
report("right-end lower bound at k=3131", rhs, ">0.529")
deriv = mpf('0.33316')*(3*cbrt(k)-2-1/cbrt(k))-mpf('2.001')*k16
report("derivative wrt k^(1/6) at 3131", deriv, ">0")
report("(1+1/3131)^(4/3)", (1+mpf(1)/k)**(mpf(4)/3), "<=1.0005")
report("2/3131", mpf(2)/k, "<=0.001")
report("1.001+42.14/3131", mpf('1.001')+mpf('42.14')/k, "<=1.0145")
# n_PD check: n_PD(k) >= 3k+2 for k=3131, and ceil((k+1)^(4/3))
import math
nPD = math.ceil((k+1)**(4/3))+k+1
report("n_PD(3131)", nPD, "record says t_PD-1 = 4895? -> n_PD=4896?")
report("n_PD/k vs 1.0005k^(1/3)+1.001", (mpf(nPD)/k, mpf('1.0005')*cbrt(k)+mpf('1.001')), "<=")
# direct check of G_k(n) > 1 on whole range for k=3131 (sanity)
def G(k,n):
    return mpf('0.14')/n*(mpf('2.38')*mpf(k)**mpf('1.5')*(n-k+1)**2/(exp(im(n))*n*(n+1))-301)
mn = min(G(k,n) for n in range(2*k+1, nPD))
report("min G_3131(n), 2k+1<=n<=n_PD-1", mn, ">1")
# threshold-unit-ratio
k=6667
j0 = math.floor(0.3*k)
val = -(mpf('0.3')*k-1)*(mpf('0.3')*k)/(2*(mpf('1.3')*k+1))
report("-(0.3k-1)(0.3k)/(2(1.3k+1)) at 6667", val, "=-230.6")
report("1+1.5log k + val", 1+mpf(1.5)*log(k)+val, "=-216.4")
report("exact -sum_{i<=j0} i/(k+1+i)", -sum(mpf(i)/(k+1+i) for i in range(1,j0+1)), "<= -230.6 ?")
report("e^0.3", exp(mpf('0.3')), "<1.34986")
report("e^{3/(2k)} k=6667", exp(mpf(3)/(2*k)), "<=1.00023")
report("1.00023*1.34986", mpf('1.00023')*mpf('1.34986'), "<1.3502")
report("2*0.7654-1.3502", 2*mpf('0.7654')-mpf('1.3502'), ">=0.18")
# two-tree lower bound: C(2k-1,k) k^{k-1} (k-1)^{k-2} / (2k)^{2k-2} >= e^{-1} k^{-3/2}, check k=6667 via logs
lhs = log(binomial(2*k-1,k)) + (k-1)*log(k) + (k-2)*log(k-1) - (2*k-2)*log(2*k)
rhs = -1 - mpf(1.5)*log(k)
report("log two-tree LB minus log(e^-1 k^-3/2) at 6667", lhs-rhs, ">=0")
# old-6-22: x_k n > 368
k=501; n=1003
xk = (mpf(k)/(k+1))**(k-1)
report("x_501 * 1003", xk*n, ">368")
report("(m#)^2 + (m#+3)^2/2 max with m#<2", 4+ (2+3)**2/mpf(2), "<16.5")
# residue counts
report("3*3333-1", 3*3333-1, "<10001"); report("3*6666-1", 3*6666-1, "=19997"); report("3*6667-1",3*6667-1,"=20000")
# e^{-i_n}: bound i_m <= 1/(2(m+1)) + 1/(6m(m+1)) check numerically for several m
for m in [1,2,5,10,100,6263]:
    b = mpf(1)/(2*(m+1)) + mpf(1)/(6*m*(m+1))
    print("i_m bound check m=",m, im(m), "<=", b, im(m)<=b, im(m)>=0)
# Lemma root-symmetry: brute check rw(nu)=1 and ratio formula at small k,nu
from fractions import Fraction
def p(m): return Fraction((m+1)**(m-1)) if m>=1 else Fraction(1)
def P(n,j): return Fraction(j)*binomial(n-1,j-1)*p(j-1)*p(n-j)/p(n)
import sympy
for k in [2,3,5]:
    for nu in [1,2,3]:
        n=2*k+nu
        rw = lambda q: Fraction(k, k+1+q)*Fraction(int(P(n,k+1+q)*p(n)), int(P(n,k)*p(n)))
        print("k,nu",k,nu,"rw(nu)=",rw(nu), [float(rw(q))>=1 for q in range(nu,k+nu)])
