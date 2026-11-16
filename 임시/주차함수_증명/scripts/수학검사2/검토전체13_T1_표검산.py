# T1: 1.3절 표, 증인, 가운데 비교 부호, 2.2절 섬유, n<=6 섬유 단봉 검산
from math import comb, factorial
from itertools import permutations
NMAX=30
A={}
def Acum(n,l):
    if l<0: return 0
    if n==0: return 1
    key=(n,l)
    if key in A: return A[key]
    s=sum(comb(n-1,j)*min(j+1,l+1)*Acum(j,l)*Acum(n-1-j,l) for j in range(n))
    A[key]=s; return s
def row(n): return [Acum(n,l)-Acum(n,l-1) for l in range(n)]
for n in range(1,11):
    r=row(n); print(n, r, sum(r), (n+1)**(n-1), sum(r)==(n+1)**(n-1))
print("증인(최소):")
for n in range(1,21):
    r=row(n)
    # 단봉 확인 및 최소 증인
    peak=None
    for i in range(n):
        if all(r[j]<=r[j+1] for j in range(0,i)) and all(r[j]>=r[j+1] for j in range(i,n-1)):
            peak=i; break
    kn=-(-n//2)
    d = (r[kn]-r[kn-1]) if 1<=kn<=n-1 else None
    print(n, "peak", peak, "k_n", kn, "d_{n,k_n}", d)
# 2.2 섬유 행
def hcap(sig):
    n=len(sig); h=[]
    for i in range(1,n+1):
        z=max([j for j in range(1,i) if sig[j-1]>sig[i-1]]+[0]); h.append(i-z)
    return h
def fib_row(sig):
    n=len(sig); h=hcap(sig)
    Al=[1]
    for l in range(n):
        p=1
        for x in h: p*=min(x,l+1)
        Al.append(p)
    return [Al[i+1]-Al[i] for i in range(n)], Al[1:]
print(hcap((1,2,3,5,4,6,7)), fib_row((1,2,3,5,4,6,7)))
for n in (7,8,9):
    sp=tuple([n-6,n-5,n-4,n-2,n-3,n-1,n]+list(range(n-7,0,-1)))
    print(n, sp, fib_row(sp)[0])
def unimodal(r):
    m=len(r)
    return any(all(r[j]<=r[j+1] for j in range(0,i)) and all(r[j]>=r[j+1] for j in range(i,m-1)) for i in range(m))
for n in range(1,8):
    bad=[s for s in permutations(range(1,n+1)) if not unimodal(fib_row(s)[0])]
    print("n=",n,"비단봉 섬유 수",len(bad), bad[:3])
# 2.7 보기: 합 확인
n=10
print(sum(comb(n-1,j)*(j+1)*(j+1)**(j-1 if j>0 else 0)*((n-j)**(n-2-j) if n-1-j>0 else 1) for j in range(n)), (n+1)**(n-1))
