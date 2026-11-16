# 명제 2:old-2-20 의 유한 n 상계값 (n=17: 0.740, 100: 0.317, 1000: 0.0658, 1e4: 0.0115) 을 본문 식으로 재계산.
from math import lgamma, log, exp, floor, ceil
def lfact(n): return lgamma(n+1)
def v(k,Z,H): return (1+1/k)**Z+(1-1/k)**(Z+H)-2
def bound(n,b):
    # 조건: 3<=i<=b, n/2<k<=n 에서 v_k(i-1,1)<0
    for i in range(3,b+1):
        for k in range(n//2+1,n+1):
            if not v(k,i-1,1)<0: return None
    S1=0.0; S2=0.0
    for c in range(n//2+1,n+1):
        kap=n-c-b+1
        if kap<0: continue
        base=lfact(n)-lfact(c)+(c-1)*log(c)-(n-1)*log(n+1)-lfact(kap)
        S1+=exp(base+log(b)+(n-c-b)*log(n-c+1)) if (n-c+1)>0 else 0
        S2+=exp(base+log(2)+(n-c-b)*log(n-c-b+3))
    return 1-S1+S2
for n in (17,100,1000,10000):
    best=None
    for b in range(3,40):
        r=bound(n,b)
        if r is None: break
        if best is None or r<best[0]: best=(r,b)
    print(n, "최소 상계 %.5f (b=%d)"%best, "-> 유효숫자 셋 올림:", ceil(best[0]*10**(2-floor(log(best[0],10))))/10**(2-floor(log(best[0],10))))
