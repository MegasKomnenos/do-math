# J12: D.fiber-nonunimodal-bound 재검산 (정확 유리수, n=17,100; 1000, 1e4는 mpmath 50자리)
from fractions import Fraction as F
from math import factorial, comb
import mpmath as mp
mp.mp.dps=50
def allowed(n,b):
    # all 3<=i<=b, all integers n/2<k<=n: (k+1)^(i-1)*k + (k-1)^i - 2k^i < 0
    for i in range(3,b+1):
        for k in range(n//2+1, n+1):
            if (k+1)**(i-1)*k+(k-1)**i-2*k**i>=0: return False
    return True
def bound_exact(n,b):
    tot=F(0); tot2=F(0)
    for c in range(n//2+1, n+1):
        kap=n-c-b+1
        if kap<0: continue
        pref=F(factorial(n),factorial(c))*c**(c-1)/F((n+1)**(n-1))/factorial(kap)
        if kap==0:
            t1=pref*F(1); t2=pref*F(1)   # b*(n-c+1)^{-1} -> 1 ; 2*(n-c-b+3)^{-1} -> 1 when exponents kap-1=-1: b/(n-c+1)=b/b=1 ; 2/(n-c-b+3)=2/2=1
        else:
            t1=pref*b*F(n-c+1)**(n-c-b); t2=pref*2*F(n-c-b+3)**(n-c-b)
        tot+=t1; tot2+=t2
    return 1-tot+tot2
def bound_mp(n,b):
    tot=mp.mpf(0); tot2=mp.mpf(0)
    lnorm=mp.loggamma(n+1)-(n-1)*mp.log(n+1)
    for c in range(n//2+1, n+1):
        kap=n-c-b+1
        if kap<0: continue
        lp=lnorm-mp.loggamma(c+1)+(c-1)*mp.log(c)-mp.loggamma(kap+1)
        if kap==0:
            t1=mp.e**lp; t2=t1
        else:
            t1=mp.e**(lp+mp.log(b)+(n-c-b)*mp.log(n-c+1)); t2=mp.e**(lp+mp.log(2)+(n-c-b)*mp.log(n-c-b+3))
        tot+=t1; tot2+=t2
    return 1-tot+tot2
for n in [17,100,1000,10000]:
    best=None; firstfail=None
    b=3
    while b-1<=n/2:
        if not allowed(n,b): firstfail=b; break
        v=bound_exact(n,b) if n<=100 else bound_mp(n,b)
        if best is None or v<best[0]: best=(v,b)
        b+=1
    print(n, "best b",best[1], mp.nstr(mp.mpf(best[0].numerator)/best[0].denominator if n<=100 else best[0],12), "first fail b",firstfail)
