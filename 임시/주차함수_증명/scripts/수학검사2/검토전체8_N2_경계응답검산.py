# 검토전체8 N2: 4.2절 경계 응답 다항식 Gamma_d 의 재귀가 5.2절이 주장하는 등식
#   Gamma^- = p_{k-1} Gamma_r(k-1;n) = B_{n,k-1}  (k<=n<=2k-1)  을 작은 n에서 만족하는지 순열 전수로 확인한다.
from itertools import permutations
from math import comb
from functools import lru_cache
p = lambda n: (n+1)**(n-1) if n>=1 else 1
def caps(sig):
    n=len(sig); h=[]
    for i in range(n):
        j=i-1
        while j>=0 and sig[j]<sig[i]: j-=1
        h.append(i-j)   # 1-based distance; j=-1 -> i+1
    return h
def B(n,k):  # B_{n,k-1} by 보조정리 2-30
    tot=0
    for sig in permutations(range(1,n+1)):
        h=caps(sig); light=1; Z=0; H=0
        for x in h:
            if x<k: light*=x
            elif x==k: H+=1
            else: Z+=1
        tot+=light*(k-1)**Z*(k**H-(k-1)**H)
    return tot
@lru_cache(None)
def Gamma(d,l,n):
    if d==0: return 1
    return comb(n,d)*p(d) + l*sum(comb(n-d+j,j)*p(j)*Gamma(d-1-j,l,n) for j in range(d))
ok=True
for n in range(2,9):
    for k in range((n+1)//2, n+1):
        r=n-k
        lhs=p(k-1)*Gamma(r,k-1,n); rhs=B(n,k)
        if n<=2*k-1:
            if lhs!=rhs: ok=False; print("불일치",n,k,lhs,rhs)
        else:  # n=2k: 보조정리 2-30의 Xi = C(2k-1,k-1) p_{k-1}^2 만큼 차이
            assert lhs-rhs==comb(2*k-1,k-1)*p(k-1)**2, (n,k)
print("Gamma^- = B_{n,k-1} (2<=n<=8, k<=n<=2k-1):", ok, " / n=2k 에서 차이 = Xi_{n,k}: 확인")
