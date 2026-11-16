# T2 검산: 3장 수치
from fractions import Fraction as Fr
from math import comb, gamma, pi, sqrt
# 1) 정리 3.6 수치
lam=Fr(751,1000); a=Fr(1,31); b=Fr(1,1000); J=8
val=lam**J + a*sum(i*lam**(i-1) for i in range(1,J+1)) + b*sum((i-1)*lam**(i-1) for i in range(1,J+1))
print("3.6 rational:", val, float(val), val==Fr(7309649993107890414228499,15500000000000000000000000))
# lambda bound
print("lambda bound n=1000:", -(-3000//4)/1000, "<= 0.751?", -(-3000//4)/1000<=0.751)
# 2) E_n omega_n for n<=6
def p(m): return (m+1)**(m-1) if m>=1 else 1
for n in range(1,7):
    s=sum(Fr(comb(n,j)*j**j*p(n-j),p(n)) for j in range(1,n//2+1))
    print("E omega",n,s,float(s)<=sqrt(n))
# 3) rows b_{n,l} n<=10 witnesses
def rows(N):
    A=[[0]*(N+2) for _ in range(N+1)]
    for l in range(N+2): A[0][l]=1
    for n in range(1,N+1):
        for l in range(0,N+1):
            A[n][l]=sum(comb(n-1,j)*min(j+1,l+1)*A[j][l]*A[n-1-j][l] for j in range(n))
    return A
A=rows(10)
for n in range(1,11):
    bl=[A[n][l]-(A[n][l-1] if l>0 else 0) for l in range(n)]
    assert sum(bl)==(n+1)**(n-1)
    mx=max(bl); wit=[l for l in range(n) if bl[l]==mx]
    print(n,bl,"witness",wit,"ceil(n/2)",-(-n//2))
# 4) Mellin tail constant
c=3*sqrt(1.5)*gamma(1/3)/gamma(5/6)*gamma(2/3)/(sqrt(pi)*gamma(1/6))
print("tail const",c,3/sqrt(2*pi))
# Legendre check
print(gamma(1/3)*gamma(5/6), 2**(1/3)*sqrt(pi)*gamma(2/3))
# 5) (3/4)^{3/2}
print((2**-1.5)**2/3**-1.5, 0.75**1.5)
