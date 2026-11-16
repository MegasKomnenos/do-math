# J12: D.fiber-enumeration 재검산 — 용량 다중집합 수, n<=6 단봉, n=7 비단봉 섬유 수와 사전식 첫째
import itertools
def caps(sig):
    n=len(sig); h=[]
    for i in range(1,n+1):
        z=0
        for j in range(i-1,0,-1):
            if sig[j-1]>sig[i-1]:
                z=j;break
        h.append(i-z)
    return h
def row(h):
    n=len(h); A=[0]
    for l in range(n):
        p=1
        for x in h: p*=min(x,l+1)
        A.append(p)
    return [A[i+1]-A[i] for i in range(n)]
def unimodal(z):
    i=0
    while i+1<len(z) and z[i]<=z[i+1]: i+=1
    while i+1<len(z) and z[i]>=z[i+1]: i+=1
    return i==len(z)-1
for n in range(1,8):
    ms=set(); bad=[]
    for sig in itertools.permutations(range(1,n+1)):
        h=caps(sig); ms.add(tuple(sorted(h)))
        if not unimodal(row(h)): bad.append((sig,h,row(h)))
    print(n,len(ms),len(bad), bad[0] if bad else None)
# direct parking n<=7 count
def park(a):
    n=len(a); spots=[0]*n; sig=[0]*n; disp=[]
    for car,pref in enumerate(a,1):
        p=pref-1
        while p<n and spots[p]: p+=1
        if p>=n: return None
        spots[p]=car; disp.append(p-(pref-1))
    return tuple(spots), max(disp)
for n in range(1,8):
    cnt=0; fib={}
    for a in itertools.product(range(1,n+1),repeat=n):
        r=park(a)
        if r is None: continue
        cnt+=1; sig,M=r
        fib.setdefault(sig,[0]*n)[M]+=1
    ok=all(fib[s]==row(caps(s)) for s in fib)
    print("n",n,"pf",cnt,(n+1)**(n-1),"all perms",len(fib)==__import__('math').factorial(n),"rows match",ok)
