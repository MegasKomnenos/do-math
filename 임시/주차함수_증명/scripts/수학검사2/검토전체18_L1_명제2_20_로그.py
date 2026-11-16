# 명제 2.20 유한 n 상계값의 독립 재계산(로그 공간 배정밀도; n=17은 정확 유리수와 대조).
from math import lgamma, log, exp
from fractions import Fraction as Fr
from math import factorial
def v_neg(n,b):
    for i in range(3,b+1):
        for k in range(n//2+1,n+1):
            if (k+1)**(i-1)*k+(k-1)**i-2*k**i>=0: return False
    return True
def lp(n,c,b,second):
    kap=n-c-b+1
    if kap<0: return None
    base=lgamma(n+1)-lgamma(c+1)+(c-1)*log(c)-(n-1)*log(n+1)-lgamma(kap+1)
    if second: base+=log(2)+(n-c-b)*log(n-c-b+3)
    else: base+=log(b)+(n-c-b)*log(n-c+1)
    return base
def bound(n,b):
    s1=s2=0.0
    for c in range(n//2+1,n+1):
        a=lp(n,c,b,False); 
        if a is None: continue
        s1+=exp(a); s2+=exp(lp(n,c,b,True))
    return 1-s1+s2
def exact17(b):
    n=17; pn=(n+1)**(n-1); t1=t2=Fr(0)
    for c in range(n//2+1,n+1):
        kap=n-c-b+1
        if kap<0: continue
        base=Fr(factorial(n),factorial(c))*c**(c-1)/pn/factorial(kap)
        t1+=base*b*Fr(n-c+1)**(n-c-b); t2+=base*2*Fr(n-c-b+3)**(n-c-b)
    return 1-t1+t2
print("n=17 exact b=3:", float(exact17(3)))
for n in (17,100,1000,10000):
    best=None; first_fail=None
    for b in range(3,80):
        if not v_neg(n,b): first_fail=b; break
        r=bound(n,b)
        if best is None or r<best[1]: best=(b,r)
    print(f"n={n}: best b={best[0]} bound={best[1]:.6f} first_fail_b={first_fail}", flush=True)
