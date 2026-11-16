# -*- coding: utf-8 -*-
"""E12 검산 1: 부록 D 장2 항목의 수치 재확인.
(1) n<=7 섬유 전수: 서로 다른 용량 다중집합 수, n=7 비단봉 섬유 수, 첫 비단봉 순열·행.
(2) zeta32 C=2000 구간, 성긴 방법의 하단, Euler-Maclaurin 상수 vs mpmath.zeta.
"""
from itertools import permutations
from math import prod
from mpmath import mp, mpf, zeta, iv

def caps(p):
    n=len(p); h=[]
    for i in range(1,n+1):
        j=max([jj for jj in range(1,i) if p[jj-1]>p[i-1]]+[0])
        h.append(i-j)
    return h

def unimodal(b):
    i=0
    while i+1<len(b) and b[i]<=b[i+1]: i+=1
    while i+1<len(b) and b[i]>=b[i+1]: i+=1
    return i+1==len(b)

for n in range(1,8):
    seen=set(); nonuni=[]
    for p in permutations(range(1,n+1)):
        h=caps(p); seen.add(tuple(sorted(h)))
        A=[prod(min(x,l+1) for x in h) for l in range(n)]
        b=[A[0]]+[A[l]-A[l-1] for l in range(1,n)]
        if not unimodal(b): nonuni.append((p,h,b))
    print(n, "multisets", len(seen), "nonunimodal", len(nonuni), nonuni[0] if nonuni else "")

mp.dps=30; iv.dps=30
def z32(C):
    s=iv.mpf(0)
    for j in range(1,C): s+=iv.mpf(j)**iv.mpf('-1.5')
    N=iv.mpf(C)
    return (s+2/iv.sqrt(N)+1/(2*iv.sqrt(N)**3)).a, (s+2/iv.sqrt(N-iv.mpf('0.5'))).b
print("zeta32 C=2000:", z32(2000))
C=2000
S=sum(mpf(j)**mpf(-1.5) for j in range(1,C+1))
print("crude lower (sum_{j<=C} + 2(C+1)^-1/2):", S+2*mpf(C+1)**mpf(-0.5), " crude upper:", S+2*mpf(C+0.5)**mpf(-0.5))
print("zeta(3/2)=",zeta(mpf(1.5)),"zeta(1/2)=",zeta(mpf(0.5)),"zeta(-1/2)=",zeta(mpf(-0.5)))
print("ZM12_ABS - |zeta(-1/2)| =", mpf('0.2078862250607212')-abs(zeta(mpf(-0.5))))
