# K2: 장3 수치 검산
from fractions import Fraction as F
from math import comb, sqrt, pi, gamma
import math

# 1) 정리 3.6 J=8 상계
lam=F(751,1000); a=F(1,31); b=F(1,1000); J=8
val=lam**J + a*sum(i*lam**(i-1) for i in range(1,J+1)) + b*sum((i-1)*lam**(i-1) for i in range(1,J+1))
print("J=8 bound:", val, float(val))
print("claimed  :", F(7309649993107890414228499,15500000000000000000000000), val==F(7309649993107890414228499,15500000000000000000000000))
# lambda bound
print("lam<=751/1000 for n>=1000?", all(F(-(-3*n//4),n)<=lam for n in range(1000,5000)))
# 2) E_n omega_n for n=1..5 exact
def p(n): return (n+1)**(n-1) if n>=1 else 1
def Eomega(n):
    return sum(F(comb(n,j)*j**j*p(n-j),p(n)) for j in range(1,n//2+1))
print("E omega_n n=1..5:", [Eomega(n) for n in range(1,6)])
print("<= sqrt n:", [float(Eomega(n))<=sqrt(n) for n in range(1,6)])
# 9n^2-48n-32 at n=6
print("9n^2-48n-32 at 6:", 9*36-48*6-32)
# bound check vs direct for n=6..60: E omega_n <= sqrt(2/pi) sqrt((n+1)(n+2)/n) <= sqrt n
for n in range(6,61):
    assert float(Eomega(n)) <= sqrt(2/pi)*sqrt((n+1)*(n+2)/n) <= sqrt(n)
print("bound ok n=6..60")
# 3) Legendre: Gamma(1/3)Gamma(5/6) = 2^{1/3} sqrt(pi) Gamma(2/3)
print("Legendre:", gamma(1/3)*gamma(5/6), 2**(1/3)*sqrt(pi)*gamma(2/3))
# 4) E A = (2/3) sqrt(2/pi) from Mellin formula at sigma=-3/2 ... check E X^sigma = Gamma(1+2s/3) E A^{-2s/3}; with s=-3/2 gives Gamma(0) pole; use s=-3/4 -> E A^{1/2}
# Direct: check EX^s formula vs product representation moments numerically at s=0.7
s=0.7
mell=(1.5)**(s/3)*gamma(1+2*s/3)*gamma(5/6-s/3)/gamma(5/6)*gamma(0.5-s/3)*gamma(2/3)/(gamma(0.5)*gamma(2/3-s/3))
print("Mellin(0.7):",mell)
# residue check: tail const sqrt(2/pi)
print("(3/4)^{3/2}=",0.75**1.5, " 2^{-3}3^{3/2}=",3**1.5/8)
# 5) 1.3절 rows n<=10: witnesses
def rows(N):
    A={}
    for l in range(0,N):
        A[(0,l)]=1
        for n in range(1,N+1):
            if l>=n-1: A[(n,l)]=p(n)
            else: A[(n,l)]=sum(comb(n-1,j)*min(j+1,l+1)*A[(j,l)]*A[(n-1-j,l)] for j in range(n))
    return A
A=rows(12)
for n in range(1,11):
    row=[A[(n,l)]-(A[(n,l-1)] if l>=1 else 0) for l in range(n)]
    m=max(row); wit=[l for l,v in enumerate(row) if v==m]
    print(n,row,"witness",wit,"ceil(n/2)=",-(-n//2), "all < ceil:", all(w< -(-n//2) for w in wit))
