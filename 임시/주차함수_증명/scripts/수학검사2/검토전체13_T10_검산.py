# T10 검산: 10장의 닫힌 꼴 수치 몇 개를 다시 센다(배정밀도; 자릿수 확인용).
import math
L=math.log; E=math.exp; S=math.sqrt
def u(k): return 3/0.35*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5
def BdT(k,nu): return (k+nu)*u(k)*(1/(k-1)+1/k)+3*(k+1)*(k-1)**-1.5
def sup(d,y): return min(1,1.15*(y+d)/d**1.5)
print("10.3 표:", [ (k, 20001-2*k, 0.48*k) for k in (8064,8065,9948,9949)])
print("가족 첫 열:", [(k,20001-2*k,1.3*k**(2/3),2*k**(2/3),0.48*k) for k in (9704,9705,9550,9551)])
print("eps0:", [math.floor(2**(2/3)*(k+1)**(2/3)) for k in (6668,8065,9551,9705)])
k=6668
abar=3*1.15*(1.48*k+2)/(0.48*k+1)**1.5; bbar=2*u(k)*(2*k-1)/(k-1)+3*(k+1)*(k-1)**-1.5; dbar=72.217/S(k)
s=S(5*k*L(k)); xi=(s+2)/k
ebar=E(3/(2*k))*(E(S(5*L(k)/k)+1/k)+2.40918*k**(1.5-2.5/(1+xi)))
print("벌크 6668: abar=%.5f bbar=%.5f dbar=%.5f ebar=%.5f 4-ebar=%.5f"%(abar,bbar,dbar,ebar,4-ebar))
print("132.32*bracket(0.48)=%.4f"%(132.32*(0.48**-0.5-1+(1-S(0.48))/3)))
k=8065; print("가족2: 3sup=%.5f BdT=%.5f theta0=%.5f"%(3*sup(2*k**(2/3)+1,k+1),BdT(k,0.48*k),(2*E(-0.48)-1)*E(-0.48)))
k=9551; x=2*k**(2/3)/(k-1); print("1b: 3sup=%.5f theta=%.5f BdT=%.5f"%(3*sup(1.3*k**(2/3)+1,k+1),(2*E(-x)-1)*E(-x),BdT(k,2*k**(2/3))))
k=9705; n2=1.3*k**(2/3); ec=3*n2**2/((k-1)*k)+4.8*S(n2)/k+n2**2/(2*(k-1)**2); print("1a: ec=%.5f BdT=%.5f"%(ec,BdT(k,n2)))
cR=S(2*math.pi)/2*E(1/12); print("cR=%.6f  cR*1.04^1.5/sqrt2=%.6f  cR*2^(2/3)/6669^(1/3)=%.4f"%(cR,cR*1.04**1.5/S(2),cR*2**(2/3)/6669**(1/3)))
k=6667; print("A^crit 계수 (1+1/k)(1+2/k)/(1-3/(4k))=%.7f ; 0.7501 검: 3/8*(1+e^(3/2k))=%.6f"%((1+1/k)*(1+2/k)/(1-3/(4*k)),3/8*(1+E(3/(2*k)))))
print("0.70836 검: 3*sqrt2*0.16696=%.6f ; 2.5-log2-log0.485917=%.6f ; sqrt(sqrt2*0.16696)=%.7f"%(3*S(2)*0.16696,2.5-L(2)-L(0.485917),S(S(2)*0.16696)))
dn=2*k**(2/3); rho0=math.floor(dn)/k; q=lambda r:1+0.7501*r/(1+r)
print("rho0=%.5f q(rho0)=%.5f iota0 검=%.5f sigma0=%.4f"%(rho0,q(rho0),2.528571+L(math.floor(dn)**1.5/k)-L(q(rho0)),E(-3.4964/1.5)))
# j1, j2 적분(단순 중점법, 치환 rho=t^2로 특이점 제거)
def integ(f,N=200000):
    h=1/N; return sum(f((i+0.5)*h)*h for i in range(N))
j2=integ(lambda t: S((1+t*t)/(t*t))*0.70836*q(t*t)**3*2*t)
j1=integ(lambda t: S((1+t*t)/(t*t))*0.70836*q(t*t)**3*(2.528571-L(q(t*t))+1.5*L(t*t))*2*t)
print("j2=%.7f j1=%.7f"%(j2,j1))
# 상위해 상수: F 최대 2/sqrt(pi)
print("2/sqrt(pi)=%.6f ; cAb(0.6) 검=%.4f ; 2cAb-4/sqrt0.6=%.4f ; 2*sqrt(.6)/.4=%.6f"%(2/S(math.pi), 2*S(.6)/.4+2*L((1+S(.6))/(1-S(.6))), 2*(2*S(.6)/.4+2*L((1+S(.6))/(1-S(.6))))-4/S(.6), 2*S(.6)/.4))
print("pi_two 상수: (2pi)^-1/2 e^-1 2^1.5=%.5f ; 1/0.41508=%.5f"%((2*math.pi)**-0.5/math.e*2**1.5,1/0.41508))
