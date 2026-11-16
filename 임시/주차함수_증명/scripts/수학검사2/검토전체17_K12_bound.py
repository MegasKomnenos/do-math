# K12: D.fiber-nonunimodal-bound 재검산 (n=17 정확 유리수; n=100,1000 mpmath 50자리)
from fractions import Fraction
from math import factorial
import mpmath as mp
mp.mp.dps=50
def admissible(n,b):
    for i in range(3,b+1):
        for k in range(n//2+1, n+1):
            if (k+1)**(i-1)*k+(k-1)**i-2*k**i >= 0: return False
    return True
def P(n,c,b,exact):
    kap=n-c-b+1
    if kap<0: return 0
    if exact:
        base=Fraction(factorial(n),factorial(c))*c**(c-1)/((n+1)**(n-1))
        t1=base*Fraction(b*(n-c+1)**kap, (n-c+1)*factorial(kap))  # b (n-c+1)^{kap-1}/kap!
        t2=base*Fraction(2*(n-c-b+3)**kap, (n-c-b+3)*factorial(kap))
        return t1,t2
    else:
        lb=mp.loggamma(n+1)-mp.loggamma(c+1)+(c-1)*mp.log(c)-(n-1)*mp.log(n+1)-mp.loggamma(kap+1)
        t1=mp.e**(lb+mp.log(b)+(kap-1)*mp.log(n-c+1))
        t2=mp.e**(lb+mp.log(2)+(kap-1)*mp.log(n-c-b+3))
        return t1,t2
def bound(n,b,exact):
    s1=s2=0
    for c in range(n//2+1,n+1):
        r=P(n,c,b,exact)
        if r==0: continue
        s1+=r[0]; s2+=r[1]
    return 1-s1+s2
for n,exact in ((17,True),(100,False),(1000,False)):
    best=None; b=3
    while True:
        if not admissible(n,b): print(n,"first non-admissible b =",b); break
        v=bound(n,b,exact)
        if best is None or v<best[1]: best=(b,v)
        b+=1
    print(n,"best b",best[0],"bound",mp.nstr(mp.mpf(best[1].numerator)/best[1].denominator if exact else best[1],12))
