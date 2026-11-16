# 검토전체14 H5: 6장 수치 재계산
from mpmath import mp, mpf, e, sqrt, log, exp, pi, factorial, power, floor, ceil, quad, findroot
from fractions import Fraction
mp.dps = 30
def Bor(n): return exp(-n)*mpf(n)**(n-1)/factorial(n)
def Ren(n): return n*Bor(n)
def Psi(d): return sum(Ren(j) for j in range(1,d+1))
def g(x): return (x-1)*log(1+mpf(1)/x)
print("== 6.1 (6.8) numbers")
qs=ceil((3*4000)**(mpf(2)/3)); print("q*(4000)=",qs, "1-1.6/sqrt525=",1-mpf(1.6)/sqrt(525))
print("1.2(1-2/525)^-2.5=",1.2*(1-mpf(2)/525)**-2.5, " 1.2(1+2/525)^.5=",1.2*sqrt(1+mpf(2)/525)," 1.5(1-1/525)^-2.5=",1.5*(1-mpf(1)/525)**-2.5)
print("bracket terms:",0.8*sqrt(2)/3*(1+mpf(1)/1048), 3.923*mpf(3)**(-mpf(4)/3)*mpf(4000)**(-mpf(1)/3), 1.5/(3*sqrt(525)))
print("== 6.2 B2")
def B2(k): return (1-1/e)+(exp(mpf(3)/2+mpf(1)/k)-1)*2*(sqrt(k+1)-1)/(sqrt(2*pi)*(k+1))
print("B2(42),B2(43),B2(2000)=",B2(42),B2(43),B2(2000))
# tilt-sum small k exact rational
bad=[]
for k in range(2,61):
    x=Fraction(k,k+1)**(k-1)
    s=sum(Fraction(n**(n-1),factorialint:=1) for n in [])  # placeholder
    tot=Fraction(0)
    import math
    for n in range(2,k+2):
        tot+=Fraction(n**(n-1),math.factorial(n))*x**n
    if tot>=1: bad.append(k)
    if k in (2,3,10,20,42,43): print("k",k,"sum=",float(tot))
print("tilt-sum >=1 for k in", bad)
print("== 6.3 Omega constants")
Xs=(5-sqrt(7))/6; print("X*=",Xs," max=",Xs*(1-Xs)*(3-2*Xs)," (10+7sqrt7)/54=",(10+7*sqrt(7))/54)
print("u<=",exp(mpf(1)/24+mpf(1)/612)*(1/(1-mpf(3)/204))*(1+mpf(1)/51)*mpf(4)/3)
print("L/G V>=2:",1.5/53*mpf(4)/3*0.5*(1+mpf(1)/51)*(1/(1-mpf(3)/204)), " V=1:",1.5/52*2.02*0.51*(1+mpf(1)/51)*(1/(1-mpf(3)/204)))
print("== 6.4 u(k)")
def u(k): return 3/mpf(0.35)*(1.35+mpf(1)/k)*(0.65-mpf(1)/k)**(-1.5)/sqrt(k)
for k in (3131,6667,10000,10001): print("u(%d)="%k,u(k)," 2u=",2*u(k))
print("== 6.5 m*, Gamma*, v(k)")
tp=mpf('0.55'); ka=mpf('2.4978')
r=max([(ka*tp+2+sqrt((ka*tp+2)**2-4*tp*ka))/(2*tp)])
print("root=",r," m*=",(r*r-ka*r)*exp(-tp*r))
xx=mpf(3132)/3130; print("Gamma*=",xx/((1+xx)**(1-tp)-1))
print("3c(JI+cYI)=",3/sqrt(2*pi)*(8.133+10.301/sqrt(2*pi)), " second=",1.5*2.7323*0.8051/sqrt(2*pi)*(17.951+23.462/sqrt(2*pi)))
def v(k):
    vp=max(k+1,4000); io=2*k+1-vp
    return 2-2*min(1,3*vp*mpf(io)**-1.5)-2*u(k)-mpf('50.62')/sqrt(k-1)
for k in (3131,6667,10000): print("v(%d)="%k,v(k), " pieces:",2*min(1,3*max(k+1,4000)*mpf(2*k+1-max(k+1,4000))**-1.5), 50.62/sqrt(k-1))
print("== 6.6 Psi(14), Fr ratio, d(k), Low, Obar, (6.49), (6.50)")
print("Psi(14)/(2e)=",Psi(14)/(2*e), " first factor k=3131:", sqrt(2*pi)*mpf(3146)**1.5*Bor(3146)*(mpf(3131)/3146)**1.5*mpf(3132)/3145)
gW=2*exp(mpf('0.0031'))/e; print("gamma_W=",gW)
def ups(k): return mpf(1)/2+mpf(5)/(2*k)+mpf(1)/(4*k*k)
def dk(k): return gW*ups(k)+u(k)/(e*2**1.5)
print("gW*ups(3131)=",gW*ups(3131)," u/(e2^1.5)=",u(3131)/(e*2**1.5)," d(3131)=",dk(3131)," d(10001)=",dk(10001))
def Low(k,rho):
    eps=mpf(k)**(-mpf(1)/3); c=1/sqrt(2*pi)
    A=c*mpf(k)**(mpf(1)/3)*(2*sqrt(rho)-2.218*eps)/(1+rho*eps)*exp(-mpf(1)/(12*(k+1)))
    return A*exp(-rho**2*(1+rho*eps)**1.5*exp(mpf(1)/(4*(k+1)))/(c*(2*sqrt(rho)-2.218*eps)))
print("Low(10001,1.4)=",Low(10001,mpf('1.4'))," Low(3131,0.75)=",Low(3131,mpf('0.75')))
def Obar(k,x): return dk(k)*exp(1+mpf(1)/(12*k))*(1+x)**1.5
print("Obar(10001,1.4k^-1/3+1/k)=",Obar(10001,1.4*mpf(10001)**(-mpf(1)/3)+mpf(1)/10001)," Obar(3131,0.75k^-1/3+1/k)=",Obar(3131,0.75*mpf(3131)**(-mpf(1)/3)+mpf(1)/3131))
uu=mpf(3131)**(mpf(1)/3); print("u=k^(1/3)=",uu," quad value=",0.15037*uu**2-1.54829*uu-1.3314)
def wp(m): return 1.99+0.59963*(m+1)**(mpf(2)/3)+1.24847*(m+1)**(mpf(1)/3)
k=3131; print("(6.49) lhs-rhs=",0.75*mpf(k)**(mpf(2)/3)-(wp(k+0.75*mpf(k)**(mpf(2)/3))-1))
print("wp(20000)=",wp(20000), " wp'(1)=",mpf(2)/3*0.59963*2**(-mpf(1)/3)+mpf(1)/3*1.24847*2**(-mpf(2)/3))
k=3131
for d in range(1,14):
    lhs=(k-1)*(e*Ren(d+1)-mpf(60)*(d+1)/(k+d))
    rhs=2*(1+sum(e*Ren(r+1)+mpf(60)*(r+1)/(k+d) for r in range(1,d)))
    print("d=%d lhs=%.1f rhs=%.2f"%(d,lhs,rhs))
print("== old-8-11 witness bound at n=20000:",wp(20000))
print("== far-window 1.4k^{2/3} <= (k+1)/2 at k=10001:",1.4*mpf(10001)**(mpf(2)/3),(10002)/2)
print("== 6.6 first-factor monotone check n=3..50:", all(sqrt(2*pi)*mpf(n)**1.5*Bor(n) < sqrt(2*pi)*mpf(n+1)**1.5*Bor(n+1) for n in range(3,50)))
print("== (6.44)-> crit front 0.0648*e*2^1.5=",0.0648*e*2**1.5)
print("== lemma H' 2+2.61238/12=",2+2.61238/12)
