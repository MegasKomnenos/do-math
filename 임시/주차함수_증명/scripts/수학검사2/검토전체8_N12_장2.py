# N12: appendix D chapter-2 items recheck
import sys,io,itertools,math
from fractions import Fraction
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
def caps(s):
    n=len(s); h=[]
    for i in range(1,n+1):
        z=max([j for j in range(1,i) if s[j-1]>s[i-1]]+[0]); h.append(i-z)
    return h
def row(h):
    n=len(h); A=[math.prod(min(x,l+1) for x in h) for l in range(n)]
    return [A[0]]+[A[l]-A[l-1] for l in range(1,n)]
def unimodal(b):
    i=0
    while i+1<len(b) and b[i+1]>=b[i]: i+=1
    while i+1<len(b) and b[i+1]<=b[i]: i+=1
    return i==len(b)-1
for n in range(1,8):
    ms=set(); bad=[]; 
    for s in itertools.permutations(range(1,n+1)):
        h=caps(s); ms.add(tuple(sorted(h)))
        if not unimodal(row(h)): bad.append((s,h,row(h)))
    print(n,len(ms),len(bad), bad[0] if bad else None)
# bound
def bound(n,b,F):
    tot1=F(0); tot2=F(0)
    for c in range(n//2+1,n+1):
        kap=n-c-b+1
        if kap<0: continue
        pref=F(math.factorial(n),math.factorial(c))*F(c)**(c-1)/F(n+1)**(n-1)/math.factorial(kap)
        t1=pref*b*F(n-c+1)**(n-c-b)
        t2=pref*2*F(n-c-b+3)**(n-c-b)
        tot1+=t1; tot2+=t2
    return 1-tot1+tot2
def admissible(n,b):
    for i in range(3,b+1):
        for k in range(n//2+1,n+1):
            if not ((k+1)**(i-1)*k+(k-1)**i-2*k**i<0): return False
    return True
import mpmath
mpmath.mp.dps=40
for n in [17,100,1000,10000]:
    res=[]; firstbad=None
    b=3
    while b-1<=n/2:
        if not admissible(n,b): firstbad=b; break
        F=Fraction if n<=100 else mpmath.mpf
        v=bound(n,b,F)
        res.append((b,float(v)))
        b+=1
        if n>=1000 and b>12: break
    best=min(res,key=lambda t:t[1])
    print(n,'first inadmissible b=',firstbad,'best',best, [ (bb,round(v,6)) for bb,v in res][:10])
