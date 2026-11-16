# D.zeta-constants 재계산: 식의 상하계를 mpmath 구간으로 평가, 성긴 방법 대조
import mpmath as mp
from mpmath import iv
iv.dps=30; mp.mp.dps=30
def z32(N):
    S=iv.mpf(0)
    for j in range(1,N): S+=iv.mpf(j)**iv.mpf(-1.5)
    lo=S+2*iv.mpf(N)**iv.mpf(-0.5)+iv.mpf(0.5)*iv.mpf(N)**iv.mpf(-1.5)
    hi=S+2*(iv.mpf(N)-iv.mpf(0.5))**iv.mpf(-0.5)
    return lo,hi,S
def zm12(N):
    S=iv.mpf(0)
    for j in range(1,N+1): S+=iv.sqrt(iv.mpf(j))
    Nn=iv.mpf(N)
    c=S-iv.mpf(2)/3*Nn**iv.mpf(1.5)-iv.mpf(0.5)*iv.sqrt(Nn)-Nn**iv.mpf(-0.5)/24
    R=Nn**iv.mpf(-2.5)/1920
    return c-R,c+R
def z12(N):
    S=iv.mpf(0)
    for j in range(1,N+1): S+=iv.mpf(j)**iv.mpf(-0.5)
    Nn=iv.mpf(N)
    c=S-2*iv.sqrt(Nn)-iv.mpf(0.5)*Nn**iv.mpf(-0.5)+Nn**iv.mpf(-1.5)/24
    R=Nn**iv.mpf(-3.5)/384
    return c-R,c+R
for N in [2000,4000]:
    lo,hi,S=z32(N); print("z32 N=",N, lo.a, hi.b)
    lo,hi=zm12(N); print("zm12 N=",N, lo.a, hi.b)
    lo,hi=z12(N); print("z12 N=",N, lo.a, hi.b)
print("true zeta(3/2)=",mp.zeta(1.5)," zeta(-1/2)=",mp.zeta(-0.5)," zeta(1/2)=",mp.zeta(0.5))
print("ZM12_ABS - true:", mp.mpf('0.2078862250607')-(-mp.zeta(-0.5)))
# coarse method at N=2000
N=2000
S=sum(mp.mpf(j)**mp.mpf(-1.5) for j in range(1,N+1))
print("coarse lower N=2000:", S+2*mp.mpf(N+1)**mp.mpf(-0.5), " upper:", S+2*mp.mpf(N+0.5)**mp.mpf(-0.5))
