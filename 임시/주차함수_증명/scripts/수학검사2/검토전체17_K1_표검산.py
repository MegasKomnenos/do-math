# 1.3절 표(b_{n,l}, n<=10)와 1.4절 "2<=n<=15에서 d_{n,k_n}<0, n>=16에서 >0"을 다시 센다.
# 방법 1: n<=7 주차 과정 직접 시뮬레이션. 방법 2: 결과 순열별 용량 곱(정리 2-3 꼴) n<=10.
import itertools, math, sys
def sim(n):
    b=[0]*n
    for a in itertools.product(range(1,n+1),repeat=n):
        occ=[False]*(n+2); M=0; ok=True
        for ai in a:
            p=ai
            while p<=n and occ[p]: p+=1
            if p>n: ok=False;break
            occ[p]=True; M=max(M,p-ai)
        if ok: b[M]+=1
    return b
def caps(sigma):
    n=len(sigma); c=[]
    for j in range(n):
        t=1; i=j-1
        while i>=0 and sigma[i]<sigma[j]: t+=1; i-=1
        c.append(t)
    return c
def rows_fiber(n):
    A=[0]*(n+1)  # A[k-1] = #PF with M<=k-1, k=1..n
    for sigma in itertools.permutations(range(n)):
        c=caps(sigma)
        for k in range(1,n+1):
            pr=1
            for cj in c: pr*=min(cj,k)
            A[k-1]+=pr
    b=[A[0]]+[A[l]-A[l-1] for l in range(1,n)]
    return b
out=[]
for n in range(1,8):
    s=sim(n); f=rows_fiber(n)
    out.append(f"n={n} sim={s} fiber={f} same={s==f} sum={sum(s)} p_n={(n+1)**(n-1)}")
for n in range(8,11):
    f=rows_fiber(n)
    out.append(f"n={n} fiber={f} sum={sum(f)} p_n={(n+1)**(n-1)}")
open(sys.argv[1],"w",encoding="utf-8").write("\n".join(out)+"\n")
