from mpmath import mp, mpf, e, pi, sqrt, exp, log, factorial, power
mp.dps = 30
def Bor(n): return exp(-n)*mpf(n)**(n-1)/factorial(n)
def Psi(d): return sum(m*Bor(m) for m in range(1,d+1))
def u(k):
    k=mpf(k); return 3/mpf('0.35')*(mpf('1.35')+1/k)*(mpf('0.65')-1/k)**(-mpf(3)/2)/sqrt(k)
def ups(k): k=mpf(k); return mpf('0.5')+mpf('2.5')/k+1/(4*k*k)
gW = 2*exp(mpf('0.0031'))/e
def dfr(k): return gW*ups(k)+u(k)/(e*2**mpf(1.5))
print("Psi(14)=",Psi(14)," Psi(14)/(2e)=",Psi(14)/(2*e))
print("u(3131)=",u(3131)," 2u=",2*u(3131))
print("gW=",gW)
print("gW*ups(3131)=",gW*ups(3131)," u/(e 2^1.5)=",u(3131)/(e*2**mpf(1.5)))
print("d(3131)=",dfr(3131)," d(10001)=",dfr(10001))
# Fr factor at k=3131
k=3131
f1=sqrt(2*pi)*mpf(k+15)**mpf(1.5)*Bor(k+15); f2=(mpf(k)/(k+15))**mpf(1.5); f3=mpf(k+1)/(k+14)
print("Fr factors:",f1,f2,f3,f1*f2*f3, f1*f2*f3*Psi(14)/(2*e))
# max of (1-D)(1+(e-2)D)/(2-D)
import mpmath
g=lambda D:(1-D)*(1+(e-2)*D)/(2-D)
Dm=mpmath.findroot(lambda D: mpmath.diff(g,D),0.15)
print("max ratio at D=",Dm," val=",g(Dm))
# v(k)
def v(k):
    k=mpf(k); vp=max(k+1,mpf(4000)); io=2*k+1-vp
    return 2-2*min(1,3*vp*io**(-mpf(1.5)))-2*u(k)-mpf('50.62')/sqrt(k-1)
for kk in (3131,6667,10000): print("v(",kk,")=",v(kk))
# B2
def B2(k): k=mpf(k); return (1-1/e)+(exp(mpf(1.5)+1/k)-1)*2*(sqrt(k+1)-1)/(sqrt(2*pi)*(k+1))
print("B2(43)=",B2(43)," B2(2000)=",B2(2000))
# tilt sum exact for k=2..42 check <1
from fractions import Fraction
import math
def tiltsum(k):
    x=Fraction(k,k+1)**(k-1)
    # sum_{n=2}^{k+1} Bor(n) q^n with q=e x ; e^n cancels: Bor(n) e^n = n^{n-1}/n!
    return sum(Fraction(n**(n-1),math.factorial(n))*x**n for n in range(2,k+2))
mx=max((tiltsum(k),k) for k in range(2,43))
print("max tiltsum k=2..42:",float(mx[0]),"at k=",mx[1]," k=2 value:",tiltsum(2))
# m(0.55,2.4978), Gamma
tp=mpf('0.55'); ka=mpf('2.4978')
root=( (ka*tp+2)+sqrt((ka*tp+2)**2-4*tp*ka) )/(2*tp)
print("root=",root," m=",(root**2-ka*root)*exp(-tp*root))
x=mpf(3132)/3130; print("Gamma=",x/((1+x)**(1-tp)-1))
# theorem-U constants
c=1/sqrt(2*pi)
print("3c(J_I+cY_I)=",3*c*(mpf('8.133')+c*mpf('10.301')))
print("1.5 G m c (J_X+cY_X)=",mpf('1.5')*mpf('2.7323')*mpf('0.8051')*c*(mpf('17.951')+c*mpf('23.462')))
print("50.62/sqrt(3130)=",mpf('50.62')/sqrt(3130))
# old-7-13 (6.8) numbers
print("12000^(2/3)=",mpf(12000)**(mpf(2)/3))
print("0.8*sqrt2/3*(1+1/1048)=",mpf('0.8')*sqrt(2)/3*(1+mpf(1)/1048), " 3.923*3^(-4/3)*4000^(-1/3)=",mpf('3.923')*mpf(3)**(-mpf(4)/3)*mpf(4000)**(-mpf(1)/3), " 1.5/(3 sqrt525)=",mpf(1.5)/(3*sqrt(525)))
# t(y) two forms check y=5
y=5
t1=Fraction(math.comb(2*y+2,y+1)*(y+1)**(2*y),2*(2*y+3)**(2*y+1))
t2=exp(-1)*Bor(y+1)**2/(2*Bor(2*y+3))
print("t(5):",float(t1),t2)
print("=== 6.6 extra ===")
def Low(k,rho):
    k=mpf(k); rho=mpf(rho); eps=k**(-mpf(1)/3); c=1/sqrt(2*pi)
    A=c*k**(mpf(1)/3)*(2*sqrt(rho)-mpf('2.218')*eps)/(1+rho*eps)*exp(-1/(12*(k+1)))
    ex=rho**2*(1+rho*eps)**mpf(1.5)*exp(1/(4*(k+1)))/(c*(2*sqrt(rho)-mpf('2.218')*eps))
    return A*exp(-ex)
print("Low(10001,1.4)=",Low(10001,mpf('1.4')))
print("Low(3131,0.75)=",Low(3131,mpf('0.75')))
def Obar(k,coef):
    k=mpf(k); return dfr(k)*exp(1+1/(12*k))*(1+coef*k**(-mpf(1)/3)+1/k)**mpf(1.5)
print("Obar(10001,1.4)=",Obar(10001,mpf('1.4')), " Obar(3131,0.75)=",Obar(3131,mpf('0.75')))
# (6.49)
k=mpf(3131); uu=k**(mpf(1)/3)
wp=lambda m: mpf('1.99')+mpf('0.59963')*(m+1)**(mpf(2)/3)+mpf('1.24847')*(m+1)**(mpf(1)/3)
print("u=",uu," quad=",mpf('0.15037')*uu**2-mpf('1.54829')*uu-mpf('1.3314'))
print("(6.49) diff=",mpf('0.75')*k**(mpf(2)/3)-(wp(k+mpf('0.75')*k**(mpf(2)/3))-1))
print("wp(20000)=",wp(mpf(20000)))
# (6.50) table at k=3131
def Ren(j): return j*Bor(j)
k=3131
for d in range(1,14):
    m=k+d
    lhs=(k-1)*(e*Ren(d+1)-mpf(60)*(d+1)/m)
    rhs=2*(1+sum(e*Ren(r+1)+mpf(60)*(r+1)/m for r in range(1,d)))
    print(d, mp.nstr(lhs,7), mp.nstr(rhs,6))
# check e*Ren(14) vs 60*14/3144
print("eRen(14)=",e*Ren(14)," 60*14/3144=",mpf(60)*14/3144)
# witness bound numbers
print("wp(20000)<478:",wp(mpf(20000)), " 10*10001^(2/3)=",10*mpf(10001)**(mpf(2)/3))
# Fr ratio check for d>=14: Ren(d+1)/Psi(d) >= 1/(5d)?
print("min Ren(d+1)/Psi(d)*5d for d=1..60:", min(Ren(d+1)/Psi(d)*5*d for d in range(1,61)))
# lemma-B constant: 2-exmax-20/(9T)
T=mpf(3130); exm=(T+1)/(2*T+1); print("exmax=",exm," 2-exmax-20/(9T)=",2-exm-20/(9*T))
# (6.8) left
print("1-1.6/sqrt525=",1-mpf('1.6')/sqrt(525))
