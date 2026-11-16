# I12: D.fiber-nonunimodal-bound 재계산 (mpmath 50자리; n=17은 Fraction 대조)
from fractions import Fraction
import mpmath as mp
mp.mp.dps=50
def allowed(n,b):
    # all 3<=i<=b, all integers n/2<k<=n : (k+1)^{i-1} k + (k-1)^i - 2k^i < 0
    for i in range(3,b+1):
        for k in range(n//2+1, n+1):
            if (k+1)**(i-1)*k + (k-1)**i - 2*k**i >= 0: return False
    return True
def bound_mp(n,b):
    lf=[mp.mpf(0)]*(n+2)
    for i in range(1,n+2): lf[i]=lf[i-1]+mp.log(i)
    logn=lf[n]-(n-1)*mp.log(n+1)
    s1=mp.mpf(0); s2=mp.mpf(0)
    for c in range(n//2+1, n+1):
        kap=n-c-b+1
        if kap<0: continue
        base=mp.e**(logn-lf[c]+(c-1)*mp.log(c)-lf[kap])
        e=n-c-b
        t1 = b*mp.mpf(n-c+1)**e if kap>0 else mp.mpf(1)
        t2 = 2*mp.mpf(n-c-b+3)**e if kap>0 else mp.mpf(1)
        s1+=base*t1; s2+=base*t2
    return 1-s1+s2
def bound_fr(n,b):
    from math import factorial
    s1=Fraction(0); s2=Fraction(0)
    for c in range(n//2+1,n+1):
        kap=n-c-b+1
        if kap<0: continue
        base=Fraction(factorial(n)*c**(c-1), factorial(c)*factorial(kap)*(n+1)**(n-1))
        e=n-c-b
        t1=Fraction(b*(n-c+1)**e) if kap>0 else Fraction(1)
        t2=Fraction(2*(n-c-b+3)**e) if kap>0 else Fraction(1)
        s1+=base*t1; s2+=base*t2
    return 1-s1+s2
for n in [17,100,1000,10000]:
    best=None; firstfail=None
    b=3
    while b-1<=n/2:
        if not allowed(n,b): firstfail=b; break
        v=bound_mp(n,b)
        if best is None or v<best[1]: best=(b,v)
        b+=1
    print(n, "best b", best[0], mp.nstr(best[1],12), "first fail b", firstfail)
    if n<=100:
        fb=bound_fr(n,best[0]); print("   exact", mp.nstr(mp.mpf(fb.numerator)/fb.denominator,12))
