# E1: (1) first n where row b is not log-concave (n<=85); (2) fibers at n<=7: any non-unimodal fiber row?
from math import comb
from itertools import permutations
def A_all(n):
    out=[]
    for l in range(n):
        f=[1]+[0]*n
        for m in range(1,n+1):
            f[m]=sum(comb(m-1,p-1)*f[p-1]*f[m-p]*min(p,l+1) for p in range(1,m+1))
        out.append(f[n])
    return out
first=None
for n in range(1,86):
    A=A_all(n); b=[A[0]]+[A[l]-A[l-1] for l in range(1,n)]
    bad=[l for l in range(1,n-1) if b[l]**2 < b[l-1]*b[l+1]]
    if bad:
        print("row b not log-concave at n=",n,"levels",bad); 
        if first is None: first=n
    if n in (79,80,81): print(n, "lc fails:", bad)
print("first non-log-concave row:", first)
def caps(sigma):
    # sigma[j] = label of car at position j (0-based); cap_j = 1 + run of smaller labels immediately left
    c=[]
    for j in range(len(sigma)):
        m=0
        while j-1-m>=0 and sigma[j-1-m]<sigma[j]: m+=1
        c.append(m+1)
    return c
for n in range(2,8):
    nonuni=0; total=0; examples=[]
    for s in permutations(range(1,n+1)):
        c=caps(s)
        row=[]
        prev=0
        for l in range(n):
            P=1
            for cj in c: P*=min(cj,l+1)
            row.append(P-prev); prev=P
        assert prev==1 or True
        total+=1
        # unimodal?
        ok=any(all(row[j]<=row[j+1] for j in range(i)) and all(row[j]>=row[j+1] for j in range(i,n-1)) for i in range(n))
        if not ok:
            nonuni+=1
            if len(examples)<3: examples.append((s,c,row))
    print(f"n={n}: fibers={total}, non-unimodal fiber rows={nonuni}, examples={examples}")
