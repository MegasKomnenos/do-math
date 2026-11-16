# 9.4절 수치 검산 (H9): Υ̂_k, v(k), μ(k), ν_0 경계값, old-7-28 (3)
from math import *
def u(k): return 3/0.35*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5
def Uhat(k): return (k-1)*u(k)/(2*k+1)
def v(k):
    vp=max(k+1,4000); io=2*k+1-vp
    return 2-2*min(1,3*vp*io**-1.5)-2*u(k)-50.62/sqrt(k-1)
for k in [3131,6667,6668,10000]: print(k," u=",u(k)," Uhat=",Uhat(k)," v=",v(k))
print("u(3131)/2=",u(3131)/2)
k=6668
mu=Uhat(k)/(1.5*(1-1.2/k)*(v(k)+Uhat(k)*(k+1)/k))
print("k mu/(1-mu)=",k*mu/(1-mu)," 0.1113k=",0.1113*k," k^{1/3}mu/(1-mu)=",k**(1/3)*mu/(1-mu)," 2.094k^{2/3}+1=",2.094*k**(2/3)+1," 3.6k^{2/3}=",3.6*k**(2/3))
rhoH=lambda k,nu:(1/k)*((1-1.5/k)*0.307*k/(k+nu-1)-47/(24*k))
rhoL=lambda k,nu:1.5*nu/(k*(k+nu))*(1-1.2/k)
print("nu=0.112k: k rhoL=",k*rhoL(k,0.112*k)," k rhoH=",k*rhoH(k,0.112*k))
rh=rhoH(k,k+1); print("k rhoH(3k+1)=",k*rh, " Y(3k+1)=",k*rh*v(k)-Uhat(k)*(1-(k+1)*rh))
# Y_k 단조성 참고: 1-(k+1)rho_min >= 0.69
print("(k+1)*0.307/k=",(k+1)*0.307/k)
# dY/dnu bound
print("1.5*(1-1.2/k)*v/1.2366=",1.5*(1-1.2/k)*v(k)/1.2366, " 0.05*k/(k-1)=",0.05*k/(k-1))
for kk in [48965,48966]: print(kk," Uhat=",Uhat(kk)," (1/20)(1-1/k)^103=",(1-1/kk)**103/20, " ok" if Uhat(kk)<=(1-1/kk)**103/20 else " FAIL")
# 9.5 old-7-38
print("6668^{2/3}=",6668**(2/3)," a lower:",0.48*k-1-8*k**(2/3)," 1/(12*366)=",1/(12*366))
# ν_0(6668) 직접: 최소 ν with Y>=0
def Y(k,nu):
    rm=max(0,min(rhoH(k,nu),rhoL(k,nu))) if nu<=k else max(0,rhoH(k,nu))
    return k*rm*v(k)-Uhat(k)*(1-(k+1)*rm)
nu0=next(n for n in range(1,k+2) if Y(k,n)>=0); print("nu0(6668)=",nu0)
F=lambda k,nu:Y(k,nu)+(1-1/k)**nu/20
nu1=next(n for n in range(103,k+2) if F(k,n)>=0); print("nu1(6668)=",nu1, " F(6668,103)=",F(k,103))
for kk in [38886,38887,9467,9466]: print(kk," F(k,103)=",F(kk,103), " nu1=",next(n for n in range(103,kk+2) if F(kk,n)>=0))
