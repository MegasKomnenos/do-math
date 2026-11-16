# 1.3절 표(n<=10 행)와 1.2절 n=3 보기를 독립 재계산한다.
# 방법: 결과 순열마다 자리별 용량의 곱 (정리 2.3 섬유 공식) 과, n<=7 은 완전 열거로 교차 검증.
import itertools, sys
def row_by_fiber(n):
    # A_{n,k-1} = sum over perms of prod min(cap_j, k)
    A=[0]*(n+1)  # A[k-1] for k=1..n -> index k-1... use A[k] = A_{n,k-1}
    for perm in itertools.permutations(range(1,n+1)):
        caps=[]
        for j in range(n):
            c=perm[j]; t=0
            while j-1-t>=0 and perm[j-1-t]<c: t+=1
            caps.append(t+1)
        for k in range(1,n+1):
            p=1
            for cp in caps: p*=min(cp,k)
            A[k]+=p
    # b_{n,l} = A_{n,l}-A_{n,l-1} ; A_{n,l}=A[l+1]
    b=[A[l+1]-(A[l] if l>=1 else 0) for l in range(n)]
    return b
def row_by_enum(n):
    b=[0]*n
    for a in itertools.product(range(1,n+1),repeat=n):
        occ=[False]*(n+1); M=0; ok=True
        for ai in a:
            p=ai
            while p<=n and occ[p]: p+=1
            if p>n: ok=False;break
            occ[p]=True; M=max(M,p-ai)
        if ok: b[M]+=1
    return b
for n in range(1,11):
    r=row_by_fiber(n)
    s=sum(r)
    line=f"{n}: {r} sum={s} (n+1)^(n-1)={(n+1)**(n-1)}"
    if n<=7:
        e=row_by_enum(n); line+=f" enum_match={e==r}"
    print(line)
