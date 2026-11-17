# 검토 22차 R5: (6.37) DD >= Res_d >= -H_d 를 작은 k에서, 정리 6:old-8-12를 y=4000에서 부동소수로 견줌 (배정밀도 평가)
import numpy as np
from math import lgamma, log, exp, sqrt, pi, e
M=9000
ms=np.arange(1,M+1,dtype=float)
LB=np.concatenate(([0.0],-ms+(ms-1)*np.log(ms)-np.array([lgamma(x+1) for x in ms])))
def g(x): return (x-1)*np.log1p(1/x)
def surv(y,dmax):
    sd=np.zeros(dmax+1); sd[1]=1.0
    for d in range(2,dmax+1):
        q=np.arange(1,d)
        pk=np.exp(LB[d-q]+LB[y+q]-LB[y+d])
        val=1-np.sum(pk*(1-y/(y+q)*sd[1:d]))
        if d==y+3: val+=exp(-1+2*LB[y+1]-LB[2*y+3])/2/(y+1)**2
        sd[d]=val
    return sd
def check(k):
    S={yy:surv(yy,k+2) for yy in (k-1,k,k+1)}
    worst=1e9; tot=0
    for d in range(2,k+2):
        DD=(k+1)*S[k+1][d]-2*k*S[k][d]+(k-1)*S[k-1][d]
        H=0.0
        for q in range(1,d):
            incm=g(k-1+d)-g(k-1+q); incp=g(k+d)-g(k+q)
            kk=exp(incm)+exp(-incp)-2
            Ac=(k-1)*kk/(2*(1-exp(-incp)))
            stp=Ac*(k+1+q)/q
            js=np.arange(1,int(np.ceil(stp))) if stp>1 else np.array([])
            js=js[js<stp]
            inner=np.sum(js*(1-js/stp)*((k-1)/(k-1+q))**js) if len(js) else 0.0
            tilt=exp(LB[k+q]-LB[k+d])
            H+=q*kk*tilt*exp(LB[d-q])*min(d-q,inner)
        worst=min(worst,DD+H); tot+=H
    return worst,2*tot
for k in (2,3,5,10,30,80,200):
    w,ddl=check(k)
    print("k",k,"min(DD+H_d)",w,"DDL2",ddl)
# 6:old-8-12, y=4000
y=4000
Sy=surv(y,y+2); Sy1=surv(y-1,y+2)
qmin=int(np.ceil(1.5*(2*y+1)**(2/3)))
mx=0
for q in range(qmin,y+1):
    n=y+q
    c=Sy[n-y+1]-Sy1[n-(y-1)+1]
    mx=max(mx,c/(16.54*(y+q/3)*q**-2.5))
print("8-12 y=4000 qmin",qmin,"max ratio",mx)
