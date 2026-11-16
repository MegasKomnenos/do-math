# -*- coding: utf-8 -*-
"""E12 검산 3: 부록 D 장4 작은 n 항목. 마지막 차 재귀로 n<=200 행을 만들고
(1) d_{n,k_n} 부호(n<=80), (2) b_{n,k_n}<b_{n,k_n+1} (5<=n<=200), (3) Q_L(n) (3<=n<=15)."""
from math import comb, factorial
N=200
A=[[0]*(N+1) for _ in range(N)]
for l in range(N):
    col=A[l]; col[0]=1
    for n in range(1,N+1):
        if l>=n-1: col[n]=(n+1)**(n-1); continue
        col[n]=sum(comb(n-1,j)*min(j+1,l+1)*col[j]*col[n-1-j] for j in range(n))
def row(n): return [A[0][n]]+[A[l][n]-A[l-1][n] for l in range(1,n)]
neg=[]; 
for n in range(2,81):
    b=row(n); k=(n+1)//2
    d=b[k]-b[k-1]
    if d<0: neg.append(n)
    if d==0: print("zero at",n)
print("d_{n,k_n}<0 for n in", neg)
# right half nonincreasing for 2<=n<=15
for n in range(2,16):
    b=row(n); k=(n+1)//2
    assert all(b[j]>=b[j+1] for j in range(k,n-1)), n
print("right half nonincreasing for 2..15: ok")
bad=[]; good=[]
for n in range(5,N+1):
    b=row(n); k=(n+1)//2
    if k+1<=n-1 and b[k]<b[k+1]: good.append(n)
    else: bad.append(n)
print("b_{n,k_n}<b_{n,k_n+1} fails for n in", bad[:40], "... holds for all 20..200:", all(n in good for n in range(20,N+1)))
for n in range(3,16):
    b=row(n)
    for l in range(0,n):
        if 2*l<=n-2 and l+2<=n-1 and b[l]>b[l+1]:
            assert b[l+1]**2>=b[l]*b[l+2], (n,l)
print("Q_L(n) for 3..15: ok")
