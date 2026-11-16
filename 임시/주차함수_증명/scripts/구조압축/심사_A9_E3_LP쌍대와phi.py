# A9 E3 검산: (1) 상자 제약+총질량 제약 선형 최소화의 쌍대식 검증(무작위), (2) k=6668, nu=103에서 9.36의 LP 값 재현(Y^LP ≈ -0.0436),
# (3) F2 §9가 제안한 공통 문제(phi를 변수로; 상한 (phi+P^theta)/k, 총질량 v-(k+1)phi/k)의 값과 비교해 실익을 센다.
from math import log, exp, sqrt
import random
def greedy(c,u,v):
    idx=sorted(range(len(c)),key=lambda i:c[i]); tot=0.0; val=0.0
    for i in idx:
        take=min(u[i],max(0.0,v-tot)); tot+=take; val+=c[i]*take
        if tot>=v-1e-15: break
    return val if tot>=v-1e-9 else float('inf')
def dual(c,u,v,lam): return lam*v-sum(u[i]*max(0.0,lam-c[i]) for i in range(len(c)))
random.seed(1); worst=0
for _ in range(2000):
    n=random.randint(2,12); c=[random.random() for _ in range(n)]; u=[random.random() for _ in range(n)]
    v=random.random()*sum(u); g=greedy(c,u,v)
    best=max(dual(c,u,v,lam) for lam in [0.0]+c+[max(c)+1])
    worst=max(worst,abs(g-best))
print("(1) 쌍대식 max_lambda[lambda v - sum u(lambda-c)_+] = 탐욕 최솟값 : 최대 오차",worst)

k=6668; nu=103; n=2*k+nu
g=lambda s: (s-1)*log(1+1/s)
u_k=3/0.35*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5
Ups=(k-1)*u_k/(2*k+1)
v=0.7654
theta={k+1:(k/(k+1))**(k-1)}
for t in range(k+1,2*k+2):
    j=t-k; theta[t+1]=theta[t]*(1+1/j)**j*(1+1/t)**(-(t-1))
Ptheta={}; s=0.0
for t in range(k+2,2*k+2):
    s+=theta[t-1]; Ptheta[t]=s
def rho_lb(t):
    Nn=n-t
    if Nn<=k-1: return exp(g(t-1)-g(n-t+1))-1
    h=1.5-47/(24*k)+(1-3/(2*k))*0.307*k/(Nn+1)
    return max(0.0,exp((h-k*(1-g(t-1)))/k)-1)
T=list(range(k+2,2*k+2)); c=[rho_lb(t) for t in T]; u=[Ptheta[t]/k for t in T]
LP=greedy(c,u,v); YLP=k*LP-Ups
print("(2) k=6668, nu=103: hatUps=%.6f, k*LP=%.6f, Y^LP=%.6f (부록 D: Y^LP>=-0.0436255), F^LP=Y^LP+(1/20)(1-1/k)^nu=%.6f"%(Ups,k*LP,YLP,YLP+0.05*(1-1/k)**nu))
def phiLP(phi):
    uu=[max(0.0,(phi+Ptheta[t])/k) for t in T]; vv=v-(k+1)*phi/k
    return phi/k+greedy(c,uu,vv)
vals=[(phiLP(-Ups*i/40),-Ups*i/40) for i in range(0,41)]
best=min(vals)
print("(3) phi-LP: k*min = %.6f at phi=%.4f ; k*phiLP(-Ups)=%.6f  (비교: 9.36의 k*LP-Ups = %.6f)"%(k*best[0],best[1],k*phiLP(-Ups),YLP))
print("    phi-LP가 9.36보다 좋아지는 양(k배) =",round(k*best[0]-YLP,5),"; 필요한 여유(1/20)(1-1/k)^103 =",round(0.05*(1-1/k)**nu,5))
rhoH=(1/k)*((1-3/(2*k))*0.307*k/(k+nu-1)-47/(24*k)); rhoL=1.5*nu/(k*(k+nu))*(1-1.2/k); rmin=max(0,min(rhoH,rhoL))
print("    9.29의 Y_k(2k+103) =",round(k*rmin*v-Ups*(1-(k+1)*rmin),5))
# 같은 계산을 몇 (k,nu)에서: phi-LP가 1/20 여유 없이도 닫히는 자리가 있는가
for (kk,nn) in ((6668,200),(9466,103),(9466,150),(20000,103),(38886,103)):
    k=kk; nu=nn; n=2*k+nu
    u_k=3/0.35*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5; Ups=(k-1)*u_k/(2*k+1)
    theta={k+1:(k/(k+1))**(k-1)}
    for t in range(k+1,2*k+2):
        j=t-k; theta[t+1]=theta[t]*(1+1/j)**j*(1+1/t)**(-(t-1))
    Ptheta={}; s=0.0
    for t in range(k+2,2*k+2):
        s+=theta[t-1]; Ptheta[t]=s
    T=list(range(k+2,2*k+2)); c=[rho_lb(t) for t in T]; u=[Ptheta[t]/k for t in T]
    YLP=k*greedy(c,u,v)-Ups
    yphi=k*min(phiLP(-Ups*i/20) for i in range(0,21))
    print("   (k,nu)=(%d,%d): Y^LP=%.5f, phi-LP=%.5f, 여유 1/20(1-1/k)^nu=%.5f"%(k,nu,YLP,yphi,0.05*(1-1/k)**nu))
