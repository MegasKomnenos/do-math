# I12: D.fiber-enumeration 재계산 — 직접 주차 + 곱 공식, n<=7
import itertools, sys
from collections import Counter
def park(a):
    n=len(a); occ=[0]*(n+2); pos=[0]*n
    for i,p in enumerate(a):
        q=p
        while q<=n and occ[q]: q+=1
        if q>n: return None
        occ[q]=1; pos[i]=q
    return pos
def unimodal(z):
    m=len(z); i=0
    while i+1<m and z[i]<=z[i+1]: i+=1
    while i+1<m and z[i]>=z[i+1]: i+=1
    return i==m-1
def caps(sig):
    n=len(sig); h=[]
    for i in range(1,n+1):
        js=[j for j in range(1,i) if sig[j-1]>sig[i-1]]
        h.append(i-(max(js) if js else 0))
    return h
for n in range(1,8):
    fib=Counter(); fibA={}
    for a in itertools.product(range(1,n+1),repeat=n):
        pos=park(a)
        if pos is None: continue
        sig=[0]*n
        for car,q in enumerate(pos): sig[q-1]=car+1
        M=max(pos[i]-a[i] for i in range(n))
        fib[(tuple(sig),M)]+=1
    sigs=set(s for s,_ in fib)
    total=sum(fib.values())
    bad=[]; msets=set(); mismatch=0
    for s in sorted(sigs):
        row=[fib.get((s,l),0) for l in range(n)]
        h=caps(s); msets.add(tuple(sorted(h)))
        A=[1]*n
        for l in range(n):
            p=1
            for hi in h: p*=min(hi,l+1)
            A[l]=p
        row2=[A[0]]+[A[l]-A[l-1] for l in range(1,n)]
        if row!=row2: mismatch+=1
        if not unimodal(row): bad.append((s,h,row))
    print(n, "pf", total, (n+1)**(n-1), "perms", len(sigs), "msets", len(msets), "mismatch", mismatch, "nonuni", len(bad))
    if bad: print("  first:", bad[0])
