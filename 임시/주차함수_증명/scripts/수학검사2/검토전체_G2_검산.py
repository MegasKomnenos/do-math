# G2 검산: 3장 정리 3-6 유리수, 4장 (4.9)·M4/M0·계수, 따름정리 수치, 중앙 상쇄 항등식
from fractions import Fraction as Fr
import sympy as sp

print("== 정리 3-6 유리수 ==")
lam=Fr(751,1000); J=8
val=lam**J+Fr(1,31)*sum(i*lam**(i-1) for i in range(1,J+1))+Fr(1,1000)*sum((i-1)*lam**(i-1) for i in range(1,J+1))
print(val, float(val), val==Fr(7309649993107890414228499,15500000000000000000000000), float(val)<0.4716)

print("== 따름정리 gauss-coeff-numeric (나) ==")
w=Fr(699,100)
v=w-Fr(7,2)-(4*w+Fr(1,2))*Fr(3,2)/31-Fr(13,2)*w*1/961-12*w/30000
print(v, float(v), v==Fr(495594511,240250000), v>2)
print("== (다) ==")
w=Fr(698,100); a0=Fr(12879,10000); a1=Fr(939,1000)
k13=Fr(464159,10**7)  # 10000^{-1/3} <= 0.0464159 ?
print("10000^(-1/3)=",10000**(-1/3))
v=w-Fr(7,2)-(4*w+Fr(1,2))*a0*k13-Fr(13,2)*w*a1*k13**2-12*w/10000
print(float(v), float(v)>=1.6809)
print("조립:",5.642*1.6809*0.39893-0.0163-3.554)

print("== (4.9) 검산 ==")
n,y,th,N=sp.symbols('n y vartheta N',positive=True)
Hn,Hn1=sp.symbols('H_n H_n1')
# He_n = (n+th) He_{n-1}; N=n+y+1
Hn_e=(n+th)*Hn1
Hn2=(N*Hn1-Hn_e)/((n-1)*y)
Hn3=(N*Hn2-Hn1)/((n-2)*y)
num2=Hn_e-3*n*Hn1+3*n*(n-1)*Hn2-n*(n-1)*(n-2)*Hn3
num0=Hn_e-n*Hn1
ratio=sp.simplify((num2/num0).subs(N,n+y+1))
target=(th*((n-y)**2+n)-n*(n+1))/(y**2*th)
print("M2/M0 ok:",sp.simplify(ratio-target)==0)
# M4/M0
Hn4=(N*Hn3-Hn2)/((n-3)*y)
Hn5=(N*Hn4-Hn3)/((n-4)*y)
ff=sp.ff
num4=Hn_e-5*n*Hn1+10*n*(n-1)*Hn2-10*n*(n-1)*(n-2)*Hn3+5*ff(n,4)*Hn4-ff(n,5)*Hn5
r4=sp.simplify((num4/num0).subs(N,n+y+1))
k=sp.symbols('k',positive=True)
for nu,expr in [(0,1+16/k+18/k**2+2/k**3-(4+38/k+22/k**2+2/k**3)/th),(-1,1+12/k-6/k**2-(4+26/k-14/k**2)/th)]:
    d=sp.simplify(r4.subs({n:2*k+nu,y:k})-expr)
    print("M4/M0 nu=",nu,"ok:",d==0)
    center={0:4-26/k+506/k**2,-1:4-22/k+414/k**2}[nu]
    print("  center-> series:",sp.series(expr.subs(th,center),k,sp.oo,4))
# P의 k 계수 등
nu_,theta=sp.symbols('nu theta')
vc=4-(26+4*nu_+8*theta)/k+(506+97*nu_+5*nu_**2+(168+16*nu_)*theta+12*theta**2)/k**2
P=sp.expand(vc*((n-y)**2+n)-n*(n+1)).subs({n:2*k+nu_,y:k-theta})
P=sp.expand(P)
print("P k^2:",sp.simplify(P.coeff(k,2)),"P k^1:",sp.simplify(P.coeff(k,1)),"P k^0:",sp.factor(P.coeff(k,0)))
Q=sp.expand((k*P+5*(k-theta)**2*vc).subs({n:2*k+nu_}))
print("kP+5y^2vt k^2:",sp.simplify(Q.coeff(k,2))," k^1:",sp.factor(Q.coeff(k,1)))
Q2=sp.expand(100*k*P+499*(k-theta)**2*vc)
print("100kP+499y^2vt k^2:",sp.simplify(Q2.coeff(k,2)))
den=sp.expand(((k-theta)**2*vc))
print("denominator k^2,k^1:",den.coeff(k,2),sp.factor(den.coeff(k,1)))

print("== 중앙 상쇄 항등식 ==")
z,rho=sp.symbols('z rho',real=True)
b=sp.symbols('beta',real=True)
mu=1-rho**2; Pq=mu*z**2+mu**2*z**4/4
# Bor^ld_R(beta) e^{-beta^2/2}=2-2 beta D(beta), D=e^{-b^2/2}∫_0^b e^{u^2/2}du
Dawson=sp.exp(-b**2/2)*sp.integrate(sp.exp(sp.Symbol('u')**2/2),(sp.Symbol('u'),0,b))
BorR=(2-2*b*Dawson)*sp.exp(b**2/2)
ninf=2/sp.sqrt(sp.pi)
F0=-ninf*z**4*sp.exp(-z**2)*sp.exp(mu*z**2/2)*Pq*rho**2*BorR.subs(b,rho*z)/sp.sqrt(2*sp.pi)
F1=-ninf*z**4*sp.exp(-z**2)*sp.exp(mu*z**2/2)*Pq*rho**2*(sp.Rational(4,3)*rho**2*z**2-sp.Rational(2,3)*rho*z**4)
import mpmath as mp
f0=sp.lambdify((z,rho),F0,'mpmath'); f1=sp.lambdify((z,rho),F1,'mpmath')
I0=mp.quad(lambda zz: mp.quad(lambda r: f0(zz,r),[0,1]),[-mp.inf,0,mp.inf])
I1=mp.quad(lambda zz: mp.quad(lambda r: f1(zz,r),[0,1]),[-mp.inf,0,mp.inf])
print("int F0 =",I0,"  int F1 =",I1," 46sqrt2-12=",46*mp.sqrt(2)-12)
c=lambda r,zz:(2-r**3)/3*zz**3-r*zz
IJ=mp.quad(lambda zz: zz**3*mp.exp(-zz**2/2)*mp.quad(lambda r:r*c(r,zz),[0,1]),[-mp.inf,0,mp.inf])
print("J 선도 적분=",IJ," 3sqrt(2pi)=",3*mp.sqrt(2*mp.pi))
print("a0,a1:",mp.quad(lambda w:mp.exp(-w**3/3),[0,mp.inf]),mp.quad(lambda w:w*mp.exp(-w**3/3),[0,mp.inf]))
print("(가) 조립:",0.5*(53-5000/173-0.01)-0.01, " 1/2 없이:",53.05-5000/173-0.01-0.01)
