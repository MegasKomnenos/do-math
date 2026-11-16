# I5 검산 3: 6.6 상수 (theorem-D 귀납 상수, prop-W, prop-R, critical-front, lemma-Hprime, lemma-M)
from math import sqrt, exp, log, pi, e, factorial
c=1/sqrt(2*pi)
def Bor(n): return exp(-n)*n**(n-1)/factorial(n) if n<150 else c*n**-1.5*exp(-1/(12*n)+1/(12*n+1))/2*2  # approx for large n (not used large)
def Ren(n): return n*Bor(n)
Psi=lambda d: sum(Ren(j) for j in range(1,d+1))
print("Psi(14)=",Psi(14)," Psi(14)/(2e)=",Psi(14)/(2*e))
# theorem-D (ㄱ)(ㄷ) constants at m=701
m=701; d=m**(2/3)/2
print("(2/3)(3/4)^(-1/3)=",(2/3)*(3/4)**(-1/3)," d/m at 701=",d/m," k=d^1.5/(m-d)=",d**1.5/(m-d)," es<=",0.798*d**1.5/(m-d)," N>=",exp(-1/(12*(m-d))))
kk=0.3747; es=0.2991; N=0.99987
print("bracket",N*(1-0.5-es)-0.7979*0.5*kk," lhs",exp(-1)*(N*(1-0.5-es)-0.7979*0.5*kk)," rhs 0.025 m^-2/3 =",0.025*m**(-2/3), 0.7979*0.5/(sqrt(2)*12*0.9437))
print("upper: sqrt(d) coeff",0.09*1.5*0.7979+(1+0.09/701)*1.74*0.7979," d coeff",(1+0.09/701)*3.28*1.5*0.5)
print("1.4963/(sqrt2*0.9437)=",1.4963/(sqrt(2)*0.9437)," 2.4604/(2*0.9437)=",2.4604/(2*0.9437)," at 701:",1.1212*701**(-2/3)+1.3036*701**(-1/3)," lhs 0.5/e=",0.5/e)
# prop-W
k=3131
ups=0.5+5/(2*k)+1/(4*k*k); gW=2*exp(0.0031)/e
print("ups_3131=",ups," gamma_W=",gW," ups*gW=",ups*gW)
print("(e+3/4)/k=",(e+0.75)/k," 6.03/k=",6.03/k," 3.51/k=",3.51/k)
print("max (1-D)(1+0.7183D)/(2-D):",max((1-D)*(1+0.7183*D)/(2-D) for D in [i/100000 for i in range(100001)]))
# Fr factor at k=3131: sqrt(2pi) n^1.5 Bor(n) with n=3146 via Stirling-exact: use log-gamma
from math import lgamma
def logBor(n): return -n+(n-1)*log(n)-lgamma(n+1)
n=k+15
f1=sqrt(2*pi)*n**1.5*exp(logBor(n)); f2=(k/(k+15))**1.5; f3=(k+1)/(k+14)
print("Fr factors",f1,f2,f3,f1*f2*f3,"*Psi(14)/(2e)=",f1*f2*f3*Psi(14)/(2*e))
def u(k): return 3/0.35*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5
def dd(k): return gW*(0.5+5/(2*k)+1/(4*k*k))+u(k)/(e*2**1.5)
print("d(3131)=",dd(3131)," parts",gW*ups,u(3131)/(e*2**1.5)," d(10001)=",dd(10001))
print("E3 const 0.3951/(e 2^1.5)=",0.3951/(e*2**1.5)," 0.0648 e 2^1.5=",0.0648*e*2**1.5)
# lemma-Hprime / lemma-M
zeta32=sum(j**-1.5 for j in range(1,200000))+2/sqrt(200000)
print("zeta(3/2)~",zeta32," 2+zeta/12=",2+zeta32/12)
B=2.218*3131**(-1/3); print("B=",B," R(1/2)=",3/4-2*B*0.5**1.5-2*c*sqrt(0.5)+c*B, 0.18581-0.30817*B, " 3B=",3*B," c/sqrt(.5)=",c/sqrt(.5))
print("1.4 k^(2/3) <= (k+1)/2 at k=22?",1.4*22**(2/3),(23)/2)
