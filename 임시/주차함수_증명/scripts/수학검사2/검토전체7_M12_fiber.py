# D.fiber-enumeration 재계산: n<=7 섬유 행, 용량 다중집합 수, 비단봉 섬유 수, 직접 주차와 곱공식 대조
import itertools, sys
def caps(sigma):
    n=len(sigma); h=[]
    for i in range(1,n+1):
        m=0
        for j in range(1,i):
            if sigma[j-1]>sigma[i-1]: m=j
        h.append(i-m)
    return h
def row_from_caps(h):
    n=len(h); A=[0]
    for l in range(n):
        p=1
        for x in h: p*=min(x,l+1)
        A.append(p)
    return [A[l+1]-A[l] for l in range(n)]
def unimodal(z):
    i=0
    while i+1<len(z) and z[i]<=z[i+1]: i+=1
    while i+1<len(z) and z[i]>=z[i+1]: i+=1
    return i+1==len(z)
def park(pref):
    n=len(pref); spots=[0]*n; disp=[]
    for car,a in enumerate(pref,1):
        p=a
        while p<=n and spots[p-1]: p+=1
        if p>n: return None
        spots[p-1]=car; disp.append(p-a)
    return tuple(spots), max(disp)
for n in range(1,8):
    perms=list(itertools.permutations(range(1,n+1)))
    capsets=set(); nonuni=[]
    for s in perms:
        h=caps(s); capsets.add(tuple(sorted(h)))
        r=row_from_caps(h)
        if not unimodal(r): nonuni.append((s,h,r))
    # direct parking
    direct={}
    cnt=0
    for pref in itertools.product(range(1,n+1),repeat=n):
        res=park(pref)
        if res is None: continue
        cnt+=1
        sig,M=res
        d=direct.setdefault(sig,[0]*n); d[M]+=1
    ok=all(direct.get(s,[0]*n)==row_from_caps(caps(s)) for s in perms)
    print(n, "pf=",cnt,(n+1)**(n-1), "capsets=",len(capsets), "allperms appear=",len(direct)==len(perms), "direct==product=",ok, "nonuni=",len(nonuni))
    if nonuni:
        nonuni.sort()
        print("  first:",nonuni[0])
