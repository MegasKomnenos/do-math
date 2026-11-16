# E1: 명제 2-20의 유한 n 상계값(0.740, 0.317, 0.0658, 0.0115) 재계산 (배정밀도; 세 자리 올림 비교용)
from math import lgamma, log, exp, floor
def lp(m): return (m-1)*log(m+1) if m>=1 else 0.0  # log p_m
def logC(n,k): return lgamma(n+1)-lgamma(k+1)-lgamma(n-k+1)
def v(k,Z,H): return (1+1/k)**Z+(1-1/k)**(Z+H)-2
for n in (17,100,1000,10000):
    best=None
    for b in range(3,40):
        # 조건: 3<=i<=b, n/2<k<=n 에서 v_k(i-1,1)<0
        if not all(v(k,i-1,1)<0 for i in range(3,b+1) for k in range(n//2+1,n+1)): continue
        s1=0.0; s2=0.0
        for c in range(n//2+1,n+1):
            base=lgamma(n+1)-lgamma(c+1)+(c-1)*log(c)-(n-1)*log(n+1)
            kap=n-c-b+1
            if kap<0: continue
            t1=base+log(b)+(n-c-b)*log(n-c+1)-lgamma(kap+1)
            t2=base+log(2)+(n-c-b)*log(n-c-b+3)-lgamma(kap+1)
            s1+=exp(t1); s2+=exp(t2)
        val=1-s1+s2
        if best is None or val<best[0]: best=(val,b)
    print(n, "min over b of bound =", round(best[0],5), "at b =", best[1])
