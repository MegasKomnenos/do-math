# 7.6-7.7절 수치 재확인 (H7b)
from math import *
from fractions import Fraction
def sg(m): return m*log(m/(m+1))+1
print("e^{-sg_6263} =", exp(-sg(6263)), ">=0.9999?", exp(-sg(6263))>=0.9999)
print("sg bound check m=6263:", sg(6263), 1/(2*6264)+1/(6*6263*6264))
print("1-0.8/sqrt301 =", 1-0.8/sqrt(301), ">=0.9538?", 1-0.8/sqrt(301)>=0.9538)
print("(2pi)^-1/2 =", (2*pi)**-0.5)
print("0.9538/0.398943 =", 0.9538/0.398943)
print("0.14*2.38*0.9999 =", 0.14*2.38*0.9999, "0.14*301=",0.14*301)
k=3131
print("D_k(2) at 3131:", 0.08329*sqrt(k)-2-42.14/k, " 0.33316/4=",0.33316/4)
u=k**(1/6); print("k^(1/6)=",u)
print("f'(u)=",0.33316*(3*k**(1/3)-2-k**(-1/3))-2.001*u)
print("f(u)=",0.33316*(sqrt(k)-2*k**(1/6)+k**(-1/6))-1.0005*k**(1/3)-1.0145)
print("(1+1/k)^(4/3)=",(1+1/k)**(4/3), " 2/k=",2/k)
nPD=ceil((k+1)**(4/3))+k+1; print("n_PD(3131)=",nPD, ">=3k+2?", nPD>=3*k+2, " n_PD/k=",nPD/k, " bound 1.0005k^1/3+1.001=",1.0005*k**(1/3)+1.001)
# direct G_k(n) scan
def G(k,n): return 0.14/n*(2.38*k**1.5*(n-k+1)**2/(exp(sg(n))*n*(n+1))-301)
for k in [3131,3500,5000,10000,10**5]:
    nPD=ceil((k+1)**(4/3))+k+1
    mn=min(G(k,n) for n in range(2*k+1,nPD))
    print("k=",k," min G over [2k+1,nPD-1] =",mn)
# D_k concavity sanity: min over rho grid
for k in [3131]:
    nPD=ceil((k+1)**(4/3))+k+1
    D=lambda r:0.33316*sqrt(k)*(1-1/r)**2-r-42.14/k
    print("D_k(2)=",D(2)," D_k(nPD/k)=",D(nPD/k))
# threshold-unit-ratio numerics
k=6667
j0=floor(0.3*k)
val=(0.3*k-1)*(0.3*k)/(2*(1.3*k+1)); print("(0.3k-1)(0.3k)/(2(1.3k+1)) at 6667 =",val)
exact=j0*(j0+1)/(2*(k+1+j0)); print("j0(j0+1)/(2(k+1+j0)) =",exact)
print("1+1.5 ln k - val =",1+1.5*log(k)-val)
print("e^0.3=",exp(0.3)," e^{3/(2k)}=",exp(3/(2*k))," product 1.00023*1.34986=",1.00023*1.34986)
print("2*0.7654-1.3502=",2*0.7654-1.3502)
# (1+1/k)^{j0} <= e^{0.3}?
print("(1+1/k)^j0=",(1+1/k)**j0)
# Sum log Pi^up exactly
s=sum(log(1+i/(k+1)) for i in range(1,j0+1)); print("exact -log Pi^up_{j0+1} =",s)
# s_{2k-1}(k) lower bound check: C(2k-1,k)k^{k-1}(k-1)^{k-2}/(2k)^{2k-2} vs e^-1 k^-1.5
from math import lgamma
lb=lgamma(2*k)-lgamma(k+1)-lgamma(k)+(k-1)*log(k)+(k-2)*log(k-1)-(2*k-2)*log(2*k)
print("log lower bound =",lb," log(e^-1 k^-1.5)=",-1-1.5*log(k))
# rw symmetry check small k
def P(n,j):
    p=lambda m:(m+1)**(m-1)
    return Fraction(j*comb(n-1,j-1)*p(j-1)*p(n-j),p(n))
k,nu=5,3; n=2*k+nu
rw=lambda q:Fraction(k,k+1+q)*P(n,k+1+q)/P(n,k)
print("rw(nu)=",rw(nu))
g=lambda x:(x-1)*log(1+1/x)
q=2; print("ratio",float(rw(q+1)/rw(q)),"exp",exp(g(k+1+q)-g(k+nu-1-q)))
# explicit-bounds check numerically
for m in [10,50,200]:
    for U in [0,3,m-1]:
        lhs=float(P(m,m-U)); Bor=lambda d:exp(-d)*d**(d-1)/factorial(d)
        print("m",m,"U",U,"P<=bound?",lhs<=Bor(U+1)*exp(sg(m))*(m+1)/(m-U), lhs, Bor(U+1)*exp(sg(m))*(m+1)/(m-U))
    for j in [1,5,m]:
        Ren=lambda j:j**j*exp(-j)/factorial(j)
        lhs=float(P(m,j)); print("m",m,"j",j,"P<=bound2?",lhs<=Ren(j)*exp(sg(m))*(m+1)/(m+1-j)**2)
