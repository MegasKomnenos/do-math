# -*- coding: utf-8 -*-
"""E12 검산 5: D.exact-n20000 (ㅁ): n<=300 전 행 단봉, 왼쪽 사슬 b_{n,0}<...<b_{n,k_n-1}이 깨지는 n."""
from math import comb
N=300
A=[[0]*(N+1) for _ in range(N)]
for l in range(N):
    col=A[l]; col[0]=1
    for n in range(1,N+1):
        if l>=n-1: col[n]=(n+1)**(n-1); continue
        col[n]=sum(comb(n-1,j)*min(j+1,l+1)*col[j]*col[n-1-j] for j in range(n))
def unimodal(b):
    i=0
    while i+1<len(b) and b[i]<=b[i+1]: i+=1
    while i+1<len(b) and b[i]>=b[i+1]: i+=1
    return i+1==len(b)
fails=[]; nonuni=[]; ties=[]
for n in range(1,N+1):
    b=[A[0][n]]+[A[l][n]-A[l-1][n] for l in range(1,n)]
    assert sum(b)==(n+1)**(n-1)
    k=(n+1)//2
    if not all(b[l]<b[l+1] for l in range(0,k-1)): fails.append(n)
    if not unimodal(b): nonuni.append(n)
    if any(b[l]==b[l+1] for l in range(n-1)): ties.append(n)
print("increase chain to k_n-1 fails at", fails); print("nonunimodal", nonuni); print("ties", ties)
