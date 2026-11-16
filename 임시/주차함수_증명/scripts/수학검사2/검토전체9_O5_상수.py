from math import *
from fractions import Fraction
def Bor(n): return exp(-n)*n**(n-1)/factorial(n)
def Ren(n): return n*Bor(n)
def Psi(d): return sum(Ren(j) for j in range(1,d+1))
def g(x): return (x-1)*log(1+1/x)
print("6.1 (6.8): q*=ceil(12000^(2/3))=",ceil(12000**(2/3)), 12000**(2/3))
print(" LHS 1-1.6/sqrt525=",1-1.6/sqrt(525))
print(" bracket:",0.8*sqrt(2)/3*(1+1/1048), 3.923*3**(-4/3)*4000**(-1/3), 1.5/(3*sqrt(525)))
print(" 1.2(1-2/525)^-2.5=",1.2*(1-2/525)**-2.5, " 1.2(1+2/525)^.5=",1.2*(1+2/525)**.5," 1.5(1-1/525)^-2.5=",1.5*(1-1/525)**-2.5)
def B2(k): return (1-1/e)+(exp(1.5+1/k)-1)*2*(sqrt(k+1)-1)/(sqrt(2*pi)*(k+1))
print("B2(42),B2(43),B2(2000)=",B2(42),B2(43),B2(2000))
# tilt-sum exact small k
mx=0
for k in range(2,43):
    xk=Fraction(k,k+1)**(k-1)
    s=sum(Fraction(n**(n-1),factorial(n))*xk**n for n in range(2,k+2))
    mx=max(mx,s)
    if s>=1: print("FAIL",k)
print("tilt-sum max over k<=42:",float(mx), mx==Fraction(8,9))
def u(k): return 3/0.35*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5
print("u(3131)=",u(3131)," u(6667)=",u(6667)," u(10^4)=",u(10000)," u(10001)=",u(10001))
print("8.5715*1.35032*1.9097*0.017872=",8.5715*1.35032*1.9097*0.017872)
def vfun(k):
    vp=max(k+1,4000); io=2*k+1-vp
    return 2-2*min(1,3*vp*io**-1.5)-2*u(k)-50.62/sqrt(k-1), 2*min(1,3*vp*io**-1.5), 2*u(k), 50.62/sqrt(k-1)
for k in (3131,3998,3999,6667,10000): print("v(%d)="%k, vfun(k))
print("24000/2263^1.5=",24000/2263**1.5)
# c*, Gamma*
tp=0.55; kap=2.4978
a=tp; b=-(kap*tp+2); c=kap
root=(-b+sqrt(b*b-4*a*c))/(2*a)
print("c* root=",root," c*=",(root**2-kap*root)*exp(-tp*root))
x=3132/3130; print("Gamma*=",x/((1+x)**(1-tp)-1))
print("varkappa min 1.498+2*3130/6261=",1.498+2*3130/6261," ex_max=",3131/6261," 2-exmax-20/(9*3130)=",2-3131/6261-20/(9*3130))
# final assembly
cc=1/sqrt(2*pi)
JI,YI,JX,YX=8.133,10.301,17.951,23.462
print("3c(JI+cYI)=",3*cc*(JI+cc*YI)," 1.5G c* c (JX+cYX)=",1.5*2.7323*0.8051*cc*(JX+cc*YX))
print("50.62/sqrt3130=",50.62/sqrt(3130))
# Psi(14)
print("Psi(14)=",Psi(14)," Psi(14)/(2e)=",Psi(14)/(2*e))
rb=lambda n: log(factorial(n))-(n+.5)*log(n)+n-.5*log(2*pi)
print("first factor k=3131:",exp(-rb(3146))*(3131/3146)**1.5*3132/3145, " *Psi/2e:",exp(-rb(3146))*(3131/3146)**1.5*3132/3145*Psi(14)/(2*e))
gW=2*exp(0.0031)/e; print("gamma_W=",gW)
ups=lambda k:0.5+5/(2*k)+1/(4*k*k)
print("ups*gW at 3131:",ups(3131)*gW)
sB=e/sqrt(2*pi)
dfun=lambda k: gW*ups(k)+u(k)/(e*2**1.5)
print("d(3131)=",dfun(3131)," u/(e2^1.5)=",u(3131)/(e*2**1.5)," d(10001)=",dfun(10001))
print("0.0648*e*2^1.5=",0.0648*e*2**1.5, " 0.3951/(e 2^1.5)=",0.3951/(e*2**1.5))
# max (1-D)(1+0.7183D)/(2-D)
print("max f(D)=",max((1-D)*(1+(e-2)*D)/(2-D) for D in [i/100000 for i in range(100001)]))
# (6.50) table
k=3131
for d in range(1,15):
    L=(k-1)*(e*Ren(d+1)-60*(d+1)/(k+d)); R=2*(1+sum(e*Ren(r+1)+60*(r+1)/(k+d) for r in range(1,d)))
    print(d, round(L,2), round(R,2))
# Low
def Low(k,rho):
    eps=k**(-1/3); c=1/sqrt(2*pi)
    A=c*k**(1/3)*(2*sqrt(rho)-2.218*eps)/(1+rho*eps)*exp(-1/(12*(k+1)))
    E=rho**2*(1+rho*eps)**1.5*exp(1/(4*(k+1)))/(c*(2*sqrt(rho)-2.218*eps))
    return A*exp(-E)
print("Low(10001,1.4)=",Low(10001,1.4)," Low(3131,.75)=",Low(3131,.75))
print("Obar(10001)=",dfun(10001)*exp(1+1/(12*10001))*(1+1.4*10001**(-1/3)+1/10001)**1.5)
print("Obar(3131)=",dfun(3131)*exp(1+1/(12*3131))*(1+0.75*3131**(-1/3)+1/3131)**1.5)
# witness bound
wp=lambda n:1.99+0.59963*(n+1)**(2/3)+1.24847*(n+1)**(1/3)
print("wp(20000)=",wp(20000)," wp'(1)=",0.39976*2**(-1/3)+0.41616*2**(-2/3))
print("(6262)^(2/3)=",6262**(2/3)," 0.65*3131-1=",0.65*3131-1, " 1.35*3131=",1.35*3131)
uu=3131**(1/3); print("u=",uu," quad=",0.15037*uu*uu-1.54829*uu-1.3314, " direct:",0.75*3131**(2/3)-(wp(3131+0.75*3131**(2/3))-1))
print("roots quad:",(1.54829+sqrt(1.54829**2+4*0.15037*1.3314))/(2*0.15037))
# theorem-D numbers
print("701^-1/3 /2=",701**(-1/3)/2," 701^-2/3=",701**(-2/3)," 1.1212*701^-2/3+1.3036*701^-1/3=",1.1212*701**(-2/3)+1.3036*701**(-1/3))
print("kfrak max=",(1/2**1.5)/0.9437," es=",0.798*(1/2**1.5)/0.9437," N=",exp(-1/(12*661)))
print("bracket:",0.99987*(0.5-0.2991)-0.7979*0.5*0.3747, " RHS 0.025*701^-2/3=",0.025*701**(-2/3))
print("0.09*1.5*0.7979+1.74*0.7979*(1+0.09/701)=",0.09*1.5*0.7979+1.74*0.7979*(1+0.09/701)," 3.28*1.5/2*(1+.09/701)=",3.28*1.5/2*(1+.09/701))
# 10001^(2/3)
print("10*10001^(2/3)=",10*10001**(2/3))
# old-8-12 number
print("9*(1.5)^1.5=",9*1.5**1.5)
# lemma-N derivatives of kI at 1
import sympy as sp
s=sp.symbols('s',positive=True); L=sp.log(s)
kI=s**sp.Rational(3,2)*(1+3*L+sp.Rational(9,8)*L**2); kX=s**sp.Rational(3,2)*(1+sp.Rational(3,2)*L)
for name,kf in (("I",kI),("X",kX)):
    print(name,[sp.nsimplify(sp.diff(kf,s,i).subs(s,1)) for i in range(4)], sp.simplify(sp.diff(kf,s,3)*s**sp.Rational(3,2)))
