# R11 검산: n<=80 행 로그오목성 — 마지막 차 재귀의 독립 구현 (b를 직접 열별로 계산)
from math import comb, factorial
N=80
A={}  # A[(n,l)]
for l in range(N):
    A[(0,l)]=1
    for n in range(1,N+1):
        A[(n,l)]=sum(comb(n-1,j)*min(j+1,l+1)*A[(j,l)]*A[(n-1-j,l)] for j in range(n))
fails=[]
for n in range(1,N+1):
    b=[A[(n,l)]-(A[(n,l-1)] if l>0 else 0) for l in range(n)]
    assert sum(b)==(n+1)**(n-1) and b[0]==factorial(n) and all(x>=1 for x in b)
    for l in range(1,n-1):
        if b[l]**2<b[l-1]*b[l+1]: fails.append((n,l))
print("fails:",fails)
b=[A[(80,l)]-A[(80,l-1)] for l in (39,40,41)]
print(b[0]); print(b[1]); print(b[2])
print("diff>0:",b[0]*b[2]-b[1]**2>0, "incr:",b[0]<b[1]<b[2])
print("sep:",25000*b[1]<25928*b[0], 25928*b[1]<25000*b[2])
from fractions import Fraction
print("ratios: %.11f %.11f"%(b[1]/b[0], b[2]/b[1]))
