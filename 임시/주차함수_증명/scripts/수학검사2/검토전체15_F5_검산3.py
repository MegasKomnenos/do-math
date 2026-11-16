# F5 검산 3: 6.6 상수들 — Psi(14)/(2e), gamma_W, upsilon, d(k), Fr_k(14) 비, prop-W (나) 계수 검사
from math import e, sqrt, pi, exp, log, factorial
def Bor(d): return exp(-d)*d**(d-1)/factorial(d)
Psi=lambda d: sum(m*Bor(m) for m in range(1,d+1))
print("Psi(14)=",Psi(14),"Psi(14)/(2e)=",Psi(14)/(2*e))
gW=2*exp(0.0031)/e; print("gamma_W=",gW)
def ups(k): return 0.5+2.5/k+1/(4*k*k)
def u(k): return 3/0.35*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5
for k in (3131,10001):
    print(k,"gW*ups=",gW*ups(k),"u/(e 2^1.5)=",u(k)/(e*2**1.5),"d(k)=",gW*ups(k)+u(k)/(e*2**1.5))
k=3131
f1=sqrt(2*pi)*(k+15)**1.5*Bor(k+15) if False else exp(-1/(12*(k+15)))  # Bor(3146) overflow 회피: e^{-rb}, rb<1/(12n) → 하계
print("first factor >=",f1,"(k/(k+15))^1.5=",(k/(k+15))**1.5,"(k+1)/(k+14)=",(k+1)/(k+14),"prod>=",f1*(k/(k+15))**1.5*(k+1)/(k+14))
print("0.98872*0.43946=",0.98872*0.43946, "0.4345-0.3697=",0.4345-0.3697)
# prop-W (나) 두 분수 부등식 검사 (k=3131, 모든 d)
ok1=all((2*k-2-d)/(2*k-4)<=(1-d/(2*k))*(1+2.0013/k) for d in range(2,k))
ok2=all((2*k-1-d)/(2*k-2)<=(1-d/(2*k))*(1+1.0003/k) for d in range(2,k))
print("fraction bounds ok:",ok1,ok2)
mx=max((1-D)*(1+(e-2)*D)/(2-D) for D in [i/10000 for i in range(10001)]); print("max (1-D)(1+0.7183D)/(2-D)=",mx, "*(1+7/k)=",mx*(1+7/k))
# 2.5 log(1-D/2) <= -1.25 D ; 3.51/k
print("3.51/3131=",3.51/3131, "(e+0.75)/3131=",(e+0.75)/3131, "6.03/3131=",6.03/3131)
# theorem-D (ㄱ)(ㄷ) numbers
m=701; print("0.734 check:",2/3*(3/4)**(-1/3), "d/m max:",m**(2/3)/2/m, "m-d>=",m-m**(2/3)/2)
d=m**(2/3)/2; print("k frac:",d**1.5/(m-d),"es<=",0.798*d**1.5/(m-d),"N>=",exp(-1/(12*(m-d))))
print("bracket:",exp(-1/(12*661))*(0.5-0.2991)-0.7979*0.5*0.3747, "lhs>=",exp(-1)*0.0513, "rhs<=",0.7979*0.5*sqrt(d)/(12*(m-d)), 0.025*m**(-2/3))
print("upper: ",1.1212*m**(-2/3)+1.3036*m**(-1/3), 0.5*exp(-1))
print("(4/3)^1.5=",(4/3)**1.5)
