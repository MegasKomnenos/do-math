# G5 독립 검토: 장6의 수치 상수 검산 (python -I 로 실행)
from fractions import Fraction as Fr
from math import *
import sys
c=1/sqrt(2*pi)
def Bor(n): return exp(-n+(n-1)*log(n)-lgamma(n+1))
def Ren(n): return n*Bor(n)
def Psi(d): return sum(Ren(j) for j in range(1,d+1))
def g(x): return (x-1)*log(1+1/x)
out=[]
def P(*a): out.append(" ".join(str(x) for x in a))
# 6.1: Up max, q*, (6.8)
Up=lambda G:(1-G)**.5*(1+2*G); P("Up(1/2)=",Up(.5),"max grid",max(Up(i/1000) for i in range(1001)))
k=4000; C=3; qs=ceil((C*k)**(2/3)); P("q*=",qs, "lhs", 1-1.6/sqrt(qs), "bracket", .8*sqrt(2)/3*(1+1/(2*(qs-1))), (1.212+1.203+1.508)*3**(-4/3)*4000**(-1/3), 1.5/(3*sqrt(qs)))
P("1.2(1-2/525)^-2.5=",1.2*(1-2/525)**-2.5, "1.2(1+2/525)^.5=",1.2*(1+2/525)**.5, "1.5(1-1/525)^-2.5=",1.5*(1-1/525)**-2.5)
# 6.2: B2
def B2(k): return (1-1/e)+(exp(1.5+1/k)-1)*2*(sqrt(k+1)-1)/(sqrt(2*pi)*(k+1))
P("B2(43)=",B2(43),"B2(2000)=",B2(2000),"B2(42)=",B2(42), "1-B2(2000)=",1-B2(2000))
# exact k<=42
mx=(0,0)
for k in range(2,43):
    x=Fr(k,k+1)**(k-1)
    # sum Bor(n) q^n with q=e x  -> Bor(n) e^n x^n = n^(n-1)/n! x^n exactly rational
    s=sum(Fr(n**(n-1),factorial(n))*x**n for n in range(2,k+2))
    if s>=1: P("FAIL k",k,float(s))
    if s>mx[0]: mx=(s,k)
P("max exact sum k<=42:",mx[1],float(mx[0]), "8/9=",8/9)
# 6.4: u(3131)
def u(k): return 3/0.35*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5
P("u(3131)=",u(3131),"u(6667)=",u(6667),"u(1e4)=",u(10000),"u(10001)=",u(10001))
P("(2k)^(2/3) at 3131:",6262**(2/3),"0.65k-1=",.65*3131-1)
wp=lambda n:1.99+0.59963*(n+1)**(2/3)+1.24847*(n+1)**(1/3)
P("wp(20000)=",wp(20000))
# 6.3 lemma-omega constants
Xs=(5-sqrt(7))/6; P("X*=",Xs,"max=",Xs*(1-Xs)*(3-2*Xs),(10+7*sqrt(7))/54)
P("u-factor:",exp(1/24+1/612),1/(1-3/(4*51)),1+1/51, exp(1/24+1/612)*(1/(1-3/204))*(1+1/51)*4/3, 0.5282*1.449)
P("L/G V>=2:",1.5/53*(4/3)*.5*1.01961*1.0150,"V=1:",1.5/52*2.02*.51*1.01961*1.0150)
# d=3 case
y=50; P("d=3 ratio y=50:", 0.0441*(y-1)/(y+3)**2/(1.2*(y+1)/((y+2)**2*(y+3))))
P("c_{y+2} lower:",(2*exp(-2)+exp(-1)-1.03*exp(-2)/51)/52, 0.6/53)
# 6.5: v(k)
def v(k):
    vp=max(k+1,4000); io=2*k+1-vp
    return 2-2*min(1,3*vp*io**-1.5)-2*u(k)-50.62/sqrt(k-1)
for k in (3131,6667,10000): P("v(%d)="%k,v(k), 2*min(1,3*max(k+1,4000)*(2*k+1-max(k+1,4000))**-1.5),2*u(k),50.62/sqrt(k-1))
P("50.62/sqrt(3130)=",50.62/sqrt(3130))
# theorem-U constants
tp=.55; ka=1.498+2*3130/6261; P("kappa_d min=",ka)
a,b,cc=tp,-(ka*tp+2),ka; r=(-b+sqrt(b*b-4*a*cc))/(2*a); P("big root",r,"c*=",(r*r-ka*r)*exp(-tp*r))
xx=3132/3130; P("Gamma*=",xx/((1+xx)**(1-tp)-1))
P("3c(J+cY)=",3*c*(8.133+c*10.301),"second=",1.5*2.7323*0.8051*c*(17.951+c*23.462))
# kI derivatives numeric check
def kI(s): L=log(s); return s**1.5*(1+3*L+1.125*L*L)
h=1e-4; P("kI'(1)~",(kI(1+h)-kI(1-h))/(2*h),"kI''(1)~",(kI(1+h)-2*kI(1)+kI(1-h))/h**2)
# lemma-N constants
P("12.15:",4.5*2+4.5*2/3+0.375*2/5,"4.908:",4.5*2/3+4.5*2/5+0.375*2/7)
# prop-W
gW=2*exp(0.0031)/e; P("gamma_W=",gW)
ups=lambda k:.5+5/(2*k)+1/(4*k*k)
P("ups*gW 3131=",ups(3131)*gW, "d(3131)=",ups(3131)*gW+u(3131)/(e*2**1.5),"d(10001)=",ups(10001)*gW+u(10001)/(e*2**1.5))
P("Psi(14)=",Psi(14),"Psi(14)/(2e)=",Psi(14)/(2*e))
k=3131; f1=sqrt(2*pi)*(k+15)**1.5*Bor(k+15) if False else None
# Bor(3146) via logs
def logBor(n): return -n+(n-1)*log(n)-lgamma(n+1)
f1=sqrt(2*pi)*exp(1.5*log(k+15)+logBor(k+15)); P("first factor",f1,"product",f1*(k/(k+15))**1.5*(k+1)/(k+14), "x Psi/(2e)=",f1*(k/(k+15))**1.5*(k+1)/(k+14)*Psi(14)/(2*e))
P("max (1-D)(1+(e-2)D)/(2-D):",max((1-D)*(1+(e-2)*D)/(2-D) for D in [i/10000 for i in range(10001)]))
P("Ren(d+1)/Psi(d) >= 1/(5d)? min ratio d=1..200:",min(Ren(d+1)/Psi(d)*5*d for d in range(1,201)))
P("E3 const:",0.3951/(e*2**1.5),"0.0648*e*2^1.5=",0.0648*e*2**1.5)
# Low
def Low(k,rho):
    eps=k**(-1/3); A=c*k**(1/3)*(2*sqrt(rho)-2.218*eps)/(1+rho*eps)
    return A*exp(-1/(12*(k+1)))*exp(-rho**2*(1+rho*eps)**1.5*exp(1/(4*(k+1)))/(c*(2*sqrt(rho)-2.218*eps)))
P("Low(10001,1.4)=",Low(10001,1.4),"Low(3131,.75)=",Low(3131,.75))
dk=lambda k:ups(k)*gW+u(k)/(e*2**1.5)
P("Obar 10001:",dk(10001)*exp(1+1/(12*10001))*(1+1.4*10001**(-1/3)+1/10001)**1.5,"Obar 3131:",dk(3131)*exp(1+1/(12*3131))*(1+.75*3131**(-1/3)+1/3131)**1.5)
# (6.49)
uu=3131**(1/3); P("u=",uu,"margin bound form:",0.15037*uu*uu-1.54829*uu-1.3314,"exact margin:",.75*3131**(2/3)-(wp(3131+.75*3131**(2/3))-1))
# (6.50)
k=3131
for d in range(1,14):
    lhs=(k-1)*(e*Ren(d+1)-60*(d+1)/(k+d)); rhs=2*(1+sum(e*Ren(r+1)+60*(r+1)/(k+d) for r in range(1,d)))
    P("d=%d lhs=%.1f rhs=%.2f"%(d,lhs,rhs))
# lemma-M R(1/2)
B=2.218*3131**(-1/3); P("B=",B,"R(1/2)=",3/4-2*B*.5**1.5-2*c*sqrt(.5)+c*B, 0.18581-0.30817*B)
# old-8-11 s bound check K>=1.35k
P("1.35*3131=",1.35*3131, "u(3131) factors",3/0.35,1.35+1/3131,(0.65-1/3131)**-1.5,3131**-0.5)
# (6.46) theorem-D numbers
P("kfrak max:",(1/2**1.5)/(1-0.0563),"es:",0.798*0.3747,"N:",exp(-1/(12*661)),"bracket:",0.99987*(1-.5-.2991)-.7979*.5*.3747,"rhs:",0.025*701**(-2/3))
P("upper rhs at 701:",1.1212*701**(-2/3)+1.3036*701**(-1/3), 0.09*1.5*0.7979+1.00013*1.74*0.7979, 1.00013*3.28*1.5/2)
# s_{2k+1}(k+1) bound at 3131
P("24000/2263^1.5=",24000/2263**1.5)
# B(q*) Bernoulli etc fine. Hz: 1-B2(2000)
print("\n".join(out))
