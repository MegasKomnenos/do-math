from mpmath import mp, gamma, sqrt, pi, mpf, quad, exp, log, beta as Beta
from fractions import Fraction
mp.dps = 30
# (1) Legendre duplication check
print("dup", gamma(mpf(1)/3)*gamma(mpf(5)/6), 2**(mpf(1)/3)*sqrt(pi)*gamma(mpf(2)/3))
# (2) E[B] from product representation vs (2/3)sqrt(2/pi)
EB = sqrt(mpf(2)/3)*gamma(mpf(4)/3)/gamma(mpf(5)/6)*Beta(1,mpf(1)/6)/Beta(mpf(1)/2,mpf(1)/6)
print("EB", EB, (mpf(2)/3)*sqrt(2/pi))
# (3) tail constant of X from product rep: Pr(X>x) ~ C x^{-3/2}
C = 2/Beta(mpf(1)/2,mpf(1)/6)*sqrt(mpf(3)/2)*gamma(mpf(1)/3)/gamma(mpf(5)/6)
print("tailC", C, sqrt(2/pi))
# (4) Mellin at sigma=1: E X = ?  compare with numerically integrating?  Check E X^sigma formula vs product for a few sigma (should be identical algebraically)
def mellin(s):
    return (mpf(3)/2)**(s/3)*gamma(1+2*s/3)*gamma(mpf(5)/6-s/3)/gamma(mpf(5)/6)*gamma(mpf(1)/2-s/3)*gamma(mpf(2)/3)/(gamma(mpf(1)/2)*gamma(mpf(2)/3-s/3))
print("mellin(0)", mellin(0))
# (5) rational bound in Thm 3-6
lam = Fraction(751,1000)
val = lam**8 + Fraction(1,31)*sum(i*lam**(i-1) for i in range(1,9)) + Fraction(1,1000)*sum((i-1)*lam**(i-1) for i in range(1,9))
print("rational", val, val == Fraction(7309649993107890414228499,15500000000000000000000000), float(val))
# (6) E_n omega_n for n=1..5
def p(n): return (n+1)**(n-1) if n>=1 else 1
from math import comb
for n in range(1,7):
    s = sum(Fraction(comb(n,j)*j**j*p(n-j), p(n)) for j in range(1, n//2+1))
    print(n, s, float(s), float(s) <= n**0.5)
# (7) 9n^2-48n-32 at n=6
print(9*36-48*6-32)
# (8) (3/4)^{3/2}
print(mpf(0.75)**1.5)
