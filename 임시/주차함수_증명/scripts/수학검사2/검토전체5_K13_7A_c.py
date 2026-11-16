# 세 재귀(D.column-certification-k500 식) 검증: 전수 열거한 A_{n,y-1}와 비교
from fractions import Fraction as Fr
from math import factorial
from itertools import product
def park_maxdisp(pref):
    n=len(pref); occ=[False]*(n+1); md=0
    for p in pref:
        s=p
        while s<=n and occ[s]: s+=1
        if s>n: return None
        occ[s]=True; md=max(md,s-p)
    return md
def A_brute(n,y):  # 최대 변위 <= y-1
    if n==0: return 1
    return sum(1 for pref in product(range(1,n+1),repeat=n) if (m:=park_maxdisp(pref)) is not None and m<=y-1)
N=7
for y in (2,3,4):
    g=[Fr(1)]
    for n in range(1,N+1):
        g.append(sum(Fr(j*j**(j-1),factorial(j))*g[n-j] for j in range(1,min(y,n)+1))/n)
    ao=lambda m: Fr((m+1)**(m-1),factorial(m)) if m>0 else Fr(1)
    h=[Fr(0)]
    for n in range(1,N+1):
        s=sum(ao(j-1)*h[n-j] for j in range(1,min(y,n)+1))
        s=y*s+(y*g[n-1] if n>=y+1 else 0)
        h.append(s/n)
    e=[Fr(1)]
    for n in range(1,N+1):
        e.append(g[n]+sum(h[j]*e[n-j] for j in range(1,n+1)))
    rec=[int(e[n]*factorial(n)) for n in range(N+1)]
    br=[A_brute(n,y) for n in range(N+1)]
    print("y",y,"세 재귀:",rec,"전수:",br,"일치:",rec==br)
