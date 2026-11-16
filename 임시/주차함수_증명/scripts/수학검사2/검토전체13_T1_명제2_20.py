# T1: 명제 2-20 유한 n 상계값 검산 (n<=1000 정확 유리수, n=10^4 로그 부동소수)
from fractions import Fraction as Fr
from math import factorial, lgamma, log, exp
def v(k,Z,H):
    return (1+Fr(1,k))**Z + (1-Fr(1,k))**(Z+H) - 2
def cond(n,b):
    for i in range(3,b+1):
        for k in range(n//2+1, n+1):
            if v(k,i-1,1) >= 0: return False
    return True
def coef(upsilon,kap):  # [x^kap] e^{upsilon T}
    if kap==0: return Fr(1)
    return Fr(upsilon*(upsilon+kap)**(kap-1), factorial(kap))
def bound_exact(n,b):
    tot1=Fr(0); tot2=Fr(0); pn=(n+1)**(n-1)
    for c in range(n//2+1, n+1):
        kap=n-c-b+1
        if kap<0: continue
        base=Fr(factorial(n)*c**(c-1), factorial(c)*pn)
        tot1+= base*coef(b,kap); tot2+= base*coef(2,kap)
    return 1-tot1+tot2
def lcoef(u,kap):
    if kap==0: return 0.0
    return log(u)+(kap-1)*log(u+kap)-lgamma(kap+1)
def bound_float(n,b):
    tot1=0.0; tot2=0.0
    lpn=(n-1)*log(n+1)
    for c in range(n//2+1, n+1):
        kap=n-c-b+1
        if kap<0: continue
        lbase=lgamma(n+1)+(c-1)*log(c)-lgamma(c+1)-lpn
        tot1+=exp(lbase+lcoef(b,kap)); tot2+=exp(lbase+lcoef(2,kap))
    return 1-tot1+tot2
for n in (17,100,1000,10000):
    best=None
    for b in range(3, 30):
        if not cond(n,b): continue
        r = bound_exact(n,b) if n<=1000 else bound_float(n,b)
        if best is None or r<best[1]: best=(b,r)
    print(n, "b*=",best[0], float(best[1]))
