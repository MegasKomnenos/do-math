# 검토 22차 R5: k=2001(및 y=2000)에서 사슬 재귀(6.21)로 생존 확률을 부동소수로 계산해 6장 상계·하계를 견준다 (배정밀도 평가; 증명 아님)
import numpy as np
from math import lgamma, log, exp, sqrt, pi, e
def lBor(m): return -m+(m-1)*np.log(m)-np.array([lgamma(x+1) for x in np.atleast_1d(m)])
LB=None
def prep(M):
    global LB
    ms=np.arange(1,M+1,dtype=float)
    LB=np.concatenate(([0.0],-ms+(ms-1)*np.log(ms)-np.array([lgamma(x+1) for x in ms])))
prep(9000)
def surv(y,dmax):
    """sd[d]=s_{y+d-1}(y), d=1..dmax (dmax<=y+3; d=y+3은 보정 포함)"""
    sd=np.zeros(dmax+1); sd[1]=1.0
    for d in range(2,dmax+1):
        q=np.arange(1,d)
        lp=LB[d-q]+LB[y+q]-LB[y+d]
        pk=np.exp(lp)
        val=1-np.sum(pk*(1-y/(y+q)*sd[1:d]))
        if d==y+3:
            t=exp(-1+2*LB[y+1]-LB[2*y+3])/2
            val+=t/(y+1)**2
        sd[d]=val
    return sd
# 정리 6:old-8-25, y=2000
y=2000
sd=surv(y,y+2)
d=np.arange(1,y+3)
up=np.minimum(1,1.15*(y+d)/d**1.5)
print("8-25 y=2000: max sd/up =",np.max(sd[1:]/up), " 위반:",np.sum(sd[1:]>up))
q=np.arange(1,y+1); print("7-13 max ratio",np.max(sd[2:y+2]/np.minimum(1,3*y*q**-1.5)))
k=2001
S={}
for yy in (k-1,k,k+1):
    S[yy]=surv(yy,min(2*k+1-yy+1,yy+3))
def s(m,yy):
    if m<=yy: return 1.0
    return S[yy][m-yy+1]
def c(m,Y): return s(m,Y+1)-s(m,Y)
u=lambda k:3/0.35*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5
ub=lambda k:1.15/0.35*(2+1/k)*(0.65-1/k)**-1.5*k**-0.5
print("k c_2k(k-1)",k*c(2*k,k-1),"(k-1)c_2k(k)",(k-1)*c(2*k,k),"u,ub",u(k),ub(k))
pm=[(k+1)*c(m,k)-(k-1)*c(m,k-1) for m in range(k,2*k+1)]
V=np.cumsum(pm[::-1])[::-1]
print("V_k(k)",V[0],"min V_k(m)",V.min(),"argmin m-k",V.argmin())
near=[i for i in range(len(V)) if i<=((k+i)**(2/3))/2]
print("핵심 근처 최소",min(V[i] for i in near),"(>=1/6?)", "근처 끝 d=",max(near))
bm=[e*exp(LB[m+1])*pm[m-k] for m in range(k,2*k+1)]
U=np.cumsum(bm[::-1])[::-1]
far=[i for i in range(len(U)) if i>((k+i)**(2/3))/2]
print("너머 U 최소 부호",min(U[i] for i in far)>0, "U_k(k)",U[0])
DD=lambda m,yy:(yy+2)*s(m+2,yy+2)-2*(yy+1)*s(m+1,yy+1)+yy*s(m,yy)
dds=[DD(m,k-1) for m in range(k,2*k)]
print("sum DD",sum(dds),"sum DD^-",sum(-x for x in dds if x<0),"DDLnat/2",0.5*(14*(log(3*k)-1)/(5*sqrt(pi*k))+37.6/(5*sqrt(pi)*k)))
Bd=2-2*s(2*k+1,k+1)-(k-1)*(s(2*k+1,k+1)-s(2*k,k))-(k-1)*c(2*k,k-1)
print("Bd",Bd,"Bd+sumDD",Bd+sum(dds))
W0=sum(exp(LB[n])*c(n-1,k-1) for n in range(k+1,2*k+1)); print("W0",W0,"bound",2*(2*pi)**-0.5*k**-1.5)
# 명제 R
dk=1/e+u(k)/(e*2**1.5); sB=e/sqrt(2*pi)
viol=0
for m in range(k,2*k+1):
    if U[m-k]/e < (k+1)*exp(LB[m+1])*c(m,k)-dk*sB*k**-1.5-1e-15: viol+=1
print("명제 R 위반",viol)
# 머묾 법칙 k: s_m(k)-s_{m-1}(k-1) <= (m-k)/k c_m(k-1)
viol=0
for m in range(k+1,2*k+1):
    if s(m,k)-s(m-1,k-1) > (m-k)/k*c(m,k-1)+1e-14: viol+=1
print("머묾 위반",viol)
# 8-12: y=4000은 생략. cutpoint (6.41)
R=(3*(k-1))//2
viol=0
for m in range(k,R+1):
    if V[m-k] < (k-1)/(R+1)*(s(m-1,k-1)-s(R,k-1))-(k-1)*c(2*k,k-1)-1e-12: viol+=1
print("(6.41) 위반",viol)
