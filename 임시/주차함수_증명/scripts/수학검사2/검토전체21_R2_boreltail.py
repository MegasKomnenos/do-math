# 검토전체21 R2: 보조정리 borel-tail-arc (가) 둘째 조각의 상수 -2/3과 구간, 셋째 조각의 전변동 상계 검산
from mpmath import mp, mpf, exp, sqrt, pi, log, loggamma, zeta, quad, mpc, fabs, nsum, inf
mp.dps=30
def Bor(j):
    j=mpf(j); return exp(-j+(j-1)*log(j)-loggamma(j+1))
c=1/sqrt(2*pi)
# constant check: -2/3 == c*zeta(1/2) + sum_j (j Bor(j) - c j^{-1/2})
s=nsum(lambda j: j*Bor(j)-c/sqrt(j),[1,inf])
print('c*zeta(1/2)+sum =',c*zeta(mpf(1)/2)+s,' vs -2/3 =',-mpf(2)/3)
# interval check for several k
for k in (1,2,5,10,100,1000,10000):
    S=sum(j*Bor(j) for j in range(1,k+1))
    r=S-(2*c*sqrt(k)-mpf(2)/3)
    print('k=%6d  resid=%s  bound=%s  ok=%s'%(k,mp.nstr(r,10),mp.nstr(mpf(2)/3*c/sqrt(k),10),0<=r<=mpf(2)/3*c/sqrt(k)))
# first piece check
for k in (1,2,5,10,100,1000):
    tail=nsum(lambda j: Bor(j),[k+1,inf])
    d=2*c/sqrt(k)-tail
    print('k=%5d first piece diff=%s bound=%s ok=%s'%(k,mp.nstr(d,8),mp.nstr(mpf(5)/9*c*k**mpf(-1.5),8),0<=d<=mpf(5)/9*c*k**mpf(-1.5)))
# TV of h(w)=w^{-3/2}(e^{-phi w}-1+phi w) on (0,1) vs |phi|^2 e^{-Re phi}, for |phi|<=2(-Re phi)
def h(phi,w):
    return w**mpf(-1.5)*(exp(-phi*w)-1+phi*w)
def TV(phi):
    f=lambda w: fabs(mp.diff(lambda t: h(phi,t), w))
    return quad(f,[0,0.001,0.01,0.1,0.5,1])
import itertools
worst=0
for a in (0.1,0.5,1,2,5,10,20,40,80):
    for ang in (0,30,45,59.9):
        th=ang*pi/180
        phi=-mpf(a)*(mp.cos(th)-1j*mp.sin(th))  # Re = -a cos, |phi| = a
        phi=mpc(-a*mp.cos(th), a*mp.sin(th))
        if abs(phi)>2*(-phi.real)+1e-12: continue
        tv=TV(phi); bd=abs(phi)**2*exp(-phi.real)
        worst=max(worst,tv/bd)
        print('a=%5.1f ang=%5.1f TV/bound=%s'%(a,ang,mp.nstr(tv/bd,6)))
print('worst ratio',worst)
