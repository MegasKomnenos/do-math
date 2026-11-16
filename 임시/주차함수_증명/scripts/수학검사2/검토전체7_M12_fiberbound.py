# D.fiber-nonunimodal-bound 재계산: n=17 정확 유리수, n=100,1000,10000 mpmath 50자리
from fractions import Fraction
from math import factorial
import mpmath as mp
mp.mp.dps=50
def allowed(n,b):
    # all 3<=i<=b, all integer n/2<k<=n : (k+1)^(i-1) k + (k-1)^i - 2k^i < 0
    for i in range(3,b+1):
        for k in range(n//2+1, n+1):
            if (k+1)**(i-1)*k+(k-1)**i-2*k**i >= 0: return False
    return True
def bound_exact(n,b):
    tot1=Fraction(0); tot2=Fraction(0)
    for c in range(n//2+1,n+1):
        kap=n-c-b+1
        if kap<0: continue
        base=Fraction(factorial(n),factorial(c))*c**(c-1)/Fraction(factorial(kap)*(n+1)**(n-1))
        t1=base*Fraction(b*(n-c+1)**(n-c-b)) if n-c-b>=0 else base*Fraction(b,(n-c+1))
        t2=base*Fraction(2*(n-c-b+3)**(n-c-b)) if n-c-b>=0 else base*Fraction(2,(n-c-b+3))
        tot1+=t1; tot2+=t2
    return 1-tot1+tot2
def bound_mp(n,b):
    tot1=mp.mpf(0); tot2=mp.mpf(0)
    lg=lambda x: mp.loggamma(x+1)
    for c in range(n//2+1,n+1):
        kap=n-c-b+1
        if kap<0: continue
        lbase=lg(n)-lg(c)+(c-1)*mp.log(c)-lg(kap)-(n-1)*mp.log(n+1)
        t1=mp.e**(lbase+mp.log(b)+(n-c-b)*mp.log(n-c+1))
        t2=mp.e**(lbase+mp.log(2)+(n-c-b)*mp.log(n-c-b+3))
        tot1+=t1; tot2+=t2
    return 1-tot1+tot2
for n in [17,100,1000,10000]:
    res=[]; firstbad=None
    b=3
    while b-1<=n/2:
        if not allowed(n,b):
            firstbad=b; break
        v = bound_exact(n,b) if n<=60 else bound_mp(n,b)
        res.append((b,float(v) if n<=60 else v))
        b+=1
    best=min(res,key=lambda t:t[1])
    print("n=",n,"first disallowed b=",firstbad,"best b=",best[0],"value=",mp.nstr(mp.mpf(best[1]) if n<=60 else best[1],12))
    print("   all:",[(bb,mp.nstr(mp.mpf(v),8)) for bb,v in res])
    if n==17:
        ex=bound_exact(17,best[0]); print("   exact n=17:",ex, float(ex))
