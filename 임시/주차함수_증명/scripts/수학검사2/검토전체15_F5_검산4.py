# F5 검산 4: Low(k,rho) 값, O-bar 상계, (6.50) 열세 부등식 (k=3131), far-window/small-k 비교
from math import e, sqrt, pi, exp, log, factorial
c=1/sqrt(2*pi)
def Low(k,rho):
    eps=k**(-1/3); A=2*sqrt(rho)-2.218*eps
    return c*k**(1/3)*A/(1+rho*eps)*exp(-1/(12*(k+1)))*exp(-rho**2*(1+rho*eps)**1.5*exp(1/(4*(k+1)))/(c*A))
print("Low(10001,1.4)=",Low(10001,1.4),"Low(3131,0.75)=",Low(3131,0.75))
gW=2*exp(0.0031)/e
def ups(k): return 0.5+2.5/k+1/(4*k*k)
def u(k): return 3/0.35*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5
def dd(k): return gW*ups(k)+u(k)/(e*2**1.5)
k=10001; print("Obar far-window:",dd(k)*exp(1+1/(12*k))*(1+1.4*k**(-1/3)+1/k)**1.5)
k=3131; print("Obar small-k:",dd(k)*exp(1+1/(12*k))*(1+0.75*k**(-1/3)+1/k)**1.5)
print("1.4*10001^(2/3)=",1.4*10001**(2/3),"10*10001^(2/3)=",10*10001**(2/3), "10/2^(2/3)=",10/2**(2/3))
print("B=",2.218*3131**(-1/3),"R(1/2) coef:",0.75-2*c/sqrt(2), 2*0.5**1.5-c)
# (6.50)
def Bor(d): return exp(-d)*d**(d-1)/factorial(d)
Ren=lambda j: j*Bor(j)
k=3131
for d in range(1,14):
    m=k+d
    lhs=(k-1)*(e*Ren(d+1)-60*(d+1)/m)
    rhs=2*(1+sum(e*Ren(r+1)+60*(r+1)/m for r in range(1,d)))
    print(d, round(lhs,2), round(rhs,3), lhs>rhs)
# (6.49) direct
uu=3131**(1/3); wp=lambda x:1.99+0.59963*(x+1)**(2/3)+1.24847*(x+1)**(1/3)
print("u=",uu,"(6.49) diff:",0.75*3131**(2/3)-(wp(3131+0.75*3131**(2/3))-1), "quad:",0.15037*uu**2-1.54829*uu-1.3314, "root:",(1.54829+sqrt(1.54829**2+4*0.15037*1.3314))/(2*0.15037))
print("wp'(1)=",2/3*0.59963*2**(-1/3)+1/3*1.24847*2**(-2/3))
