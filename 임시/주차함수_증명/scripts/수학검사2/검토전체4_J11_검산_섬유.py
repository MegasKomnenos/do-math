import sys, io, itertools
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
def caps(sig):
    n=len(sig); h=[]
    for i in range(n):
        t=0
        for j in range(i):
            if sig[j]>sig[i]: t=j+1
        h.append(i+1-t)
    return h
for n in range(1,8):
    ms=set(); nonuni=[]; 
    for sig in itertools.permutations(range(1,n+1)):
        h=caps(sig); ms.add(tuple(sorted(h)))
        A=[1]
        for l in range(n):
            p=1
            for x in h: p*=min(x,l+1)
            A.append(p)
        b=[A[l+1]-A[l] for l in range(n)]
        # unimodal?
        i=0
        while i+1<n and b[i]<=b[i+1]: i+=1
        while i+1<n and b[i]>=b[i+1]: i+=1
        if i+1<n: nonuni.append((sig,h,b))
    print(n,'distinct cap multisets',len(ms),'nonunimodal fibers',len(nonuni), nonuni[0] if nonuni else '')
