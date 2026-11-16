# 9.3절 정리 old-7-16 (1)-(3) 수치 검산 (H9)
from math import *
def quad(f,a,b,limit=0,points=()):
    # 합성 심프슨; 꺾이는 점에서 나눔
    pts=[a]+sorted(x for x in points if a<x<b)+[b]; tot=0.0
    for lo,hi in zip(pts,pts[1:]):
        n=200000; h=(hi-lo)/n
        tot+=h/3*(f(lo)+f(hi)+4*sum(f(lo+(2*i-1)*h) for i in range(1,n//2+1))+2*sum(f(lo+2*i*h) for i in range(1,n//2)))
    return (tot,)
k=6668
def J1(k):
    f=lambda t: 2.5*(1+t+2/k)**-3.5*(max(0.0,1-3*k**-0.5*(t-1/k)**-1.5) if t>1/k else 0.0)
    return quad(f,1/k,1,limit=400,points=[ (3/sqrt(k))**(2/3)+1/k ])[0]
def J2(k):
    f=lambda t: 2.5*(1+t+1/k)**-3.5*(max(0.0,1-3*(k-1)*k**-1.5*(t-1/k)**-1.5) if t>1/k else 0.0)
    return quad(f,1/k,(k-1)/k,limit=400,points=[(3*(k-1)*k**-1.5)**(2/3)+1/k])[0]
J3=(k/(2*k+1))**2.5*(1-3/sqrt(k)); J4=(k/(2*k+1))**2.5*(1-3/sqrt(k-1))
print("J1..J4:",J1(k),J2(k),J3,J4," L*=",J1(k)+J2(k)+J3+J4)
# 직접 합으로도 (ω 차분·f) H_k + H'_k
om=lambda t:(k/t)**2.5
f=lambda E: max(0.0,1-3*k*(E-k)**-1.5)
H=sum((om(E+1)-om(E+2))*f(E) for E in range(k+1,2*k))+om(2*k+1)*f(2*k)
fp=lambda E: max(0.0,1-3*(k-1)*min(E-k+1,k-1)**-1.5)
Hp=sum((om(E+1)-om(E+2))*fp(E) for E in range(k,2*k))+om(2*k+1)*fp(2*k)
print("H_k+H'_k (직접 합) =",H+Hp)
# (2)
print("0.3826 check:", (2*pi)**-0.5*exp(-1/24)*exp(-1/(12*3334)))
js=ceil((3*k)**(2/3)); print("j*=",js, " 4.85[...]=",4.85*(sqrt(k)/sqrt((3*k)**(2/3)+2)-sqrt(2)))
print("6.1224*0.95^-1.5=",6.1224*0.95**-1.5, " 6/0.98=",6/0.98)
print("12/0.734=",12/0.734)
print("endpoint 0.05k:",16.35*((k+1)/(0.95*k))**1.5/(0.05*k)*k, " endpoint j*:",5.45*(1+1/k)**1.5*k/(k-js-1), " vs 6.62")
print("353.3/k vs 6.62/sqrt k:",353.3/k, 6.62/sqrt(k))
# (3)
d=6.62/sqrt(k); print("dbar=",d," band req=",(1+d/2)/(1-d/2))
cover=103*(2*pi)**-0.5*exp(1/(12*(1.48*k+1)))*(2/(0.48*k-102))**1.5; print("41.2 const:",103*(2*pi)**-0.5*exp(1/(12*6670)), " cover=",cover)
term=(2*pi)**-0.5*exp(1/(12*6670))*(2/0.48)**1.5; print("3.394 const:",term)
pi0=(0.26*k+0.5)*3.394*k**-1.5+0.676/k; print("pi0 bound:",pi0, " vs 0.8825/sqrt k+0.72/k:",0.8825/sqrt(k)+0.72/k)
req=1+(1+1/1.48)*d/(2-d)+(1/1.48)*(0.8825/sqrt(k)+0.72/k+41.2*(2/(0.48*k-102))**1.5); print("bulk req=",req)
print("limit L*(inf)=", 2*(1-2**-2.5)+2*2**-2.5)
