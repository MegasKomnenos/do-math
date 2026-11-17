# R3 검산: 작은 n의 행을 정확한 정수로 계산해 5.1절의 주장과 5.2.1절의 항등식을 본다.
import sys, itertools
from fractions import Fraction
from math import comb, factorial

def perm_caps(sigma):
    # 자리 i(1-based)의 용량: 왼쪽으로 더 큰 번호의 차가 선 가장 가까운 자리까지의 거리(없으면 i)
    n=len(sigma); h=[]
    for i in range(n):
        d=i+1
        for j in range(i-1,-1,-1):
            if sigma[j]>sigma[i]:
                d=i-j; break
        h.append(d)
    return h

def A_table(N):
    # A[n][l] = #PF_n with max displacement <= l  (l=-1..n-1) via last-car recursion
    A={}
    for l in range(0,N+1):
        col=[1]
        for n in range(1,N+1):
            s=0
            for j in range(n):
                s+=comb(n-1,j)*min(j+1,l+1)*col[j]*col[n-1-j]
            col.append(s)
        A[l]=col
    return A

N=int(sys.argv[1]) if len(sys.argv)>1 else 120
A=A_table(N)
def Aval(n,l):
    if l<0: return 0
    if l>=n: l=n-1 if n>=1 else 0
    return A[l][n]
def b(n,l): return Aval(n,l)-Aval(n,l-1)
p=lambda n:(n+1)**(n-1)
# sanity
for n in range(1,8):
    assert Aval(n,n-1)==p(n)
# brute-force check with permutations for n<=6
for n in range(1,7):
    for l in range(0,n):
        tot=0
        for s in itertools.permutations(range(1,n+1)):
            h=perm_caps(s); pr=1
            for x in h: pr*=min(x,l+1)
            tot+=pr
        assert tot==Aval(n,l),(n,l)
print("A table ok")
kn=lambda n:(n+1)//2
bad=[]; nonuni=[]; midneg=[]
for n in range(1,N+1):
    row=[b(n,l) for l in range(n)]
    # unimodal?
    i=0
    while i+1<n and row[i]<=row[i+1]: i+=1
    while i+1<n and row[i]>=row[i+1]: i+=1
    if i!=n-1: nonuni.append(n)
    k=kn(n)
    if not all(row[i]<row[i+1] for i in range(0,k-1)): bad.append(n)
    if n>=2 and k<=n-1 and row[k]-row[k-1]<0: midneg.append(n)
print("non-unimodal rows:",nonuni)
print("rows where b0<...<b_{k_n-1} fails:",bad)
print("rows with d_{n,k_n}<0:",midneg)
# witness offset
import mpmath as mp
mp.mp.dps=30
lo=1e9;hi=-1e9;alo=ahi=None
for n in range(50,N+1):
    row=[b(n,l) for l in range(n)]
    m=max(row); ls=row.index(m)
    assert row.count(m)==1
    v=n+1-ls-mp.mpf('0.59963')*mp.mpf(n+1)**(mp.mpf(2)/3)-mp.mpf('1.24847')*mp.mpf(n+1)**(mp.mpf(1)/3)
    if v<lo: lo=v;alo=n
    if v>hi: hi=v;ahi=n
print("witness offset range n=50..%d:"%N,lo,alo,hi,ahi)
