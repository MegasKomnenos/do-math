# H2: 3장 검산 — 3.3 n<=80 로그오목성, 3.4 수치, 1.3 표 증인
from fractions import Fraction as Fr
from math import comb, isqrt
import sys
NMAX=80
LMAX=NMAX
# A[n][l] for 0<=n<=NMAX, 0<=l<=LMAX via last-car recursion
A=[[0]*(LMAX+1) for _ in range(NMAX+1)]
for l in range(LMAX+1):
    A[0][l]=1
    for n in range(1,NMAX+1):
        s=0
        for j in range(n):
            s+=comb(n-1,j)*min(j+1,l+1)*A[j][l]*A[n-1-j][l]
        A[n][l]=s
def b(n,l):
    return A[n][l]-(A[n][l-1] if l>=1 else 0)
# row sums
for n in range(1,NMAX+1):
    assert sum(b(n,l) for l in range(n))==(n+1)**(n-1)
# 1.3 table and witnesses
for n in range(1,11):
    row=[b(n,l) for l in range(n)]
    m=max(row); wit=[l for l in range(n) if row[l]==m]
    print(n,row,wit,"ceil(n/2)=",-(-n//2))
# log-concavity first failure
first=None
for n in range(1,NMAX+1):
    row=[b(n,l) for l in range(n)]
    bad=[l for l in range(1,n-1) if row[l]**2<row[l-1]*row[l+1]]
    if bad:
        print("LC fail n=",n,bad); 
        if first is None: first=n
print("first LC failure n=",first)
r80=[b(80,l) for l in range(80)]
print("b80,39..41:",r80[39],r80[40],r80[41], r80[39]<r80[40]<r80[41], r80[40]**2<r80[39]*r80[41])
print("ratios", r80[40]/r80[39], r80[41]/r80[40])
# 3.4 rational
lam=Fr(751,1000); J=8
val=lam**J+Fr(1,31)*sum(i*lam**(i-1) for i in range(1,J+1))+Fr(1,1000)*sum((i-1)*lam**(i-1) for i in range(1,J+1))
print("3.4 value",val, val==Fr(7309649993107890414228499,15500000000000000000000000), float(val))
# small n E omega_n
def p(n): return (n+1)**(n-1) if n>=1 else 1
for n in range(1,6):
    E=sum(Fr(comb(n,j)*j**j*p(n-j),p(n)) for j in range(1,n//2+1))
    print("E omega",n,E, float(E)<=n**0.5)
# check 9n^2-48n-32 at n=6
print(9*36-48*6-32)
# ratio (3/4)^{3/2} vs 2^-3/3^-1.5
print((3/4)**1.5, 2**-3/3**-1.5)
