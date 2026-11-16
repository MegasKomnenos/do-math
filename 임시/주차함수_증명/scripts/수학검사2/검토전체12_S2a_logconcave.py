# 3.3: recompute rows n<=80 via last-car recurrence; check first log-concavity failure; n=780 cumulative partial check
from math import comb
import sys, time
N=80
C=[[comb(n,j) for j in range(n+1)] for n in range(N+1)]
def column(l, N):
    A=[1]+[0]*N
    for n in range(1,N+1):
        s=0
        for j in range(n):
            s+=C[n-1][j]*min(j+1,l+1)*A[j]*A[n-1-j]
        A[n]=s
    return A
cols=[column(l,N) for l in range(N)]  # cols[l][n]=A_{n,l}
def b(n,l):
    if l<0: return 0
    if l>=n: return 0
    return cols[l][n]-(cols[l-1][n] if l>=1 else 0)
first=None; viol=[]
for n in range(1,N+1):
    assert sum(b(n,l) for l in range(n))==(n+1)**(n-1)
    for l in range(1,n-1):
        if b(n,l)**2 < b(n,l-1)*b(n,l+1):
            viol.append((n,l))
print("violations n<=80:",viol)
print(b(80,39),b(80,40),b(80,41),sep="\n")
print(b(80,39)<b(80,40)<b(80,41), b(80,40)/b(80,39), b(80,41)/b(80,40))
# witnesses n<=10
for n in range(1,11):
    row=[b(n,l) for l in range(n)]
    m=max(row); w=[l for l in range(n) if row[l]==m]
    print(n,row,w,-(-n//2))
