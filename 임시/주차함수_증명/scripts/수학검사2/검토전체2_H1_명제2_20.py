# H1 검산: 명제 2.20의 유한 n 상계값(0.740, 0.317, 0.0658, 0.0115)을 로그 척도 부동소수점으로 재계산(3자리 확인용).
from math import lgamma, log, exp
from fractions import Fraction as Fr

def v_neg(k,Z):
    return Fr(k+1,k)**Z + Fr(k-1,k)**(Z+1) - 2 < 0

def lfact(n): return lgamma(n+1)

def bound(n,b):
    lpn=(n-1)*log(n+1)
    tot=0.0; restr=0.0
    for c in range(n//2+1, n+1):
        kap=n-c-b+1
        if kap<0: continue
        lbase=lfact(n)+(c-1)*log(c)-lfact(c)-lpn
        # b*(n-c+1)^(n-c-b)/kap!  (kap=0 -> b*b^{-1}=1)
        t1=log(b)+(n-c-b)*log(n-c+1)-lfact(kap)
        t2=log(2)+(n-c-b)*log(n-c-b+3)-lfact(kap)
        tot+=exp(lbase+t1); restr+=exp(lbase+t2)
    return 1-tot+restr

for n in (17,100,1000,10000):
    best=None
    for b in range(3, 80):
        ok=all(v_neg(k, i-1) for i in range(3,b+1) for k in (n//2+1,))
        if not ok: break
        val=bound(n,b)
        if best is None or val<best[1]: best=(b,val)
    print(n, "best b", best[0], "bound %.4f"%best[1])
