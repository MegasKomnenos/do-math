# 첫 조각(Bor^tail_k(1)) 재검산: 꼬리는 1-부분합으로 정확히
from mpmath import mp, mpf, exp, sqrt, pi, log, loggamma, zeta
mp.dps=40
def Bor(j):
    j=mpf(j); return exp(-j+(j-1)*log(j)-loggamma(j+1))
c=1/sqrt(2*pi)
for k in (1,2,5,10,100,1000,10000,100000):
    S=mpf(0); S2=mpf(0)
    for j in range(1,k+1):
        b=Bor(j); S+=b; S2+=j*b
    tail=1-S
    d=2*c/sqrt(k)-tail
    print('k=%7d first: diff=%s bound=%s ok=%s | second: resid=%s bound=%s ok=%s'%(k,mp.nstr(d,8),mp.nstr(mpf(5)/9*c*k**mpf(-1.5),8),0<=d<=mpf(5)/9*c*k**mpf(-1.5),
          mp.nstr(S2-(2*c*sqrt(k)-mpf(2)/3),8),mp.nstr(mpf(2)/3*c/sqrt(k),8),0<=S2-(2*c*sqrt(k)-mpf(2)/3)<=mpf(2)/3*c/sqrt(k)))
# y_k bound
G2=mpf(1)/64
for k in (2,10,10000):
    yk=(2*k-1)*log(1+G2)/2-k*G2/2
    print('k',k,'y_k',yk,'>= 63k/8192-127/16384 =',mpf(63)*k/8192-mpf(127)/16384, yk>=mpf(63)*k/8192-mpf(127)/16384)
