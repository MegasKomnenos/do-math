# 11.2 표의 몇 수치를 다시 센다: 제타 상수 성긴 하단(C=2000), 섬유 전수(n<=7)의 용량 다중집합 수·비단봉 섬유 수·첫 비단봉 섬유.
from mpmath import mp, mpf, zeta, nsum, inf
from itertools import permutations
from fractions import Fraction
mp.dps = 30
C = 2000
S = sum(mpf(j)**mpf(-1.5) for j in range(1, C+1))
low = S + 2/mp.sqrt(C+1); up = S + 2/mp.sqrt(C+mpf(0.5))
print("zeta(3/2) =", zeta(1.5)); print("성긴 하단 =", low, " 상단 =", up)
print("zeta(1/2) =", zeta(0.5), " zeta(-1/2) =", zeta(-0.5))
print("c_Psi =", -zeta(0.5)+zeta(1.5)/12, " f_1 =", 4/(3*mp.sqrt(2*mp.pi)))
def row(sig):
    n=len(sig); h=[]
    for i in range(1,n+1):
        prev=[j for j in range(1,i) if sig[j-1]>sig[i-1]]
        h.append(i-(max(prev) if prev else 0))
    A=[1]
    for l in range(n):
        A.append(1)
        for hi in h: A[-1]*=min(hi,l+1)
    A=A[1:]
    b=[A[0]]+[A[l]-A[l-1] for l in range(1,n)]
    return h,b
def unimodal(b):
    i=0
    while i+1<len(b) and b[i]<=b[i+1]: i+=1
    while i+1<len(b) and b[i]>=b[i+1]: i+=1
    return i==len(b)-1
for n in range(1,8):
    ms=set(); bad=0; first=None
    for sig in permutations(range(1,n+1)):
        h,b=row(sig); ms.add(tuple(sorted(h)))
        if not unimodal(b):
            bad+=1
            if first is None: first=(sig,h,b)
    print(n, "다중집합", len(ms), "비단봉", bad, first if first else "")
