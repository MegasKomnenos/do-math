# I5 검산 4: far-window / small-k-bulk / (6.49) / (6.50) 수치
from math import sqrt, exp, log, pi, e, factorial, lgamma
c=1/sqrt(2*pi)
def Low(k,rho):
    eps=k**(-1/3)
    br=2*sqrt(rho)-2.218*eps
    return c*k**(1/3)*br/(1+rho*eps)*exp(-1/(12*(k+1)))*exp(-rho**2*(1+rho*eps)**1.5*exp(1/(4*(k+1)))/(c*br))
def u(k): return 3/0.35*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5
gW=2*exp(0.0031)/e
def dd(k): return gW*(0.5+5/(2*k)+1/(4*k*k))+u(k)/(e*2**1.5)
print("Low(10001,1.4)=",Low(10001,1.4)," Obar(10001)=",dd(10001)*exp(1+1/(12*10001))*(1+1.4*10001**(-1/3)+1/10001)**1.5)
print("Low(3131,0.75)=",Low(3131,0.75)," Obar(3131,0.75)=",dd(3131)*exp(1+1/(12*3131))*(1+0.75*3131**(-1/3)+1/3131)**1.5)
# monotonic sanity: Low(k,1.4) increasing in k, decreasing in rho
print("Low(20000,1.4)",Low(20000,1.4),"Low(10001,1.0)",Low(10001,1.0),"Low(10001,0.5)",Low(10001,0.5))
# (6.49)
k=3131; U=k**(1/3)
wp=lambda n: 1.99+0.59963*(n+1)**(2/3)+1.24847*(n+1)**(1/3)
print("u=",U," quad=",0.15037*U*U-1.54829*U-1.3314," direct diff=",0.75*k**(2/3)-(wp(k+0.75*k**(2/3))-1)," 1.30212+0.39976/u+0.41616/u^2=",1.30212+0.39976/U+0.41616/U**2)
a=0.15037;b=-1.54829;cc=-1.3314; print("larger root",(-b+sqrt(b*b-4*a*cc))/(2*a))
# (6.50)
def Bor(n): return exp(-n+(n-1)*log(n)-lgamma(n+1))
def Ren(n): return n*Bor(n)
k=3131
for d in range(1,14):
    m=k+d
    L=(k-1)*(e*Ren(d+1)-60*(d+1)/m)
    R=2*(1+sum(e*Ren(r+1)+60*(r+1)/m for r in range(1,d)))
    print(d, round(L,1), round(R,2))
