# 검토전체22 R7a: (7.7) 1-s_q(k) <= q^{3/2}/(2k) 의 수치 대조 (k=10000, q<=101; 배정밀도 평가)
import numpy as np, sys
from math import sqrt, pi
k=int(sys.argv[1]) if len(sys.argv)>1 else 10000
N=k+100
beta=np.exp(-1.0)
def col(cap):
    a=np.zeros(N+1); a[0]=1.0
    w=np.minimum(np.arange(1,N+1),cap).astype(float)
    for n in range(1,N+1):
        a[n]=beta*np.dot(w[:n]*a[:n],a[n-1::-1][:n])/n
    return a
a=col(k); u=col(10**9)
worst=0
for q in [1,2,3,5,10,20,50,101]:
    n=k+q-1
    tail=1-a[n]/u[n]
    ub=(2*pi)**-0.5*((n+1)/(k+1))**1.5/(k+1)*(4/3*(q-1)**1.5+sqrt(q-1)-(q-1)-1/3) if q>=2 else 0.0
    print(q, "1-s=%.6e"%tail, "union closed=%.6e"%ub, "q^1.5/(2k)=%.6e"%(q**1.5/(2*k)), "ratio=%.4f"%(tail/(q**1.5/(2*k))))
allok=all(1-a[k+q-1]/u[k+q-1] <= q**1.5/(2*k) for q in range(1,102))
print("all q<=101 ok:", allok)
