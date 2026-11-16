import sys,io,math
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
import mpmath
mpmath.mp.dps=50
def lf(x): return mpmath.loggamma(x+1)
def bound(n,b):
    tot1=mpmath.mpf(0); tot2=mpmath.mpf(0)
    for c in range(n//2+1,n+1):
        kap=n-c-b+1
        if kap<0: continue
        lp=lf(n)-lf(c)+(c-1)*mpmath.log(c)-(n-1)*mpmath.log(n+1)-lf(kap)
        e=n-c-b
        tot1+=mpmath.exp(lp)*b*mpmath.mpf(n-c+1)**e
        tot2+=mpmath.exp(lp)*2*mpmath.mpf(n-c-b+3)**e
    return 1-tot1+tot2
def admissible(n,b):
    for i in range(3,b+1):
        for k in range(n//2+1,n+1):
            if not ((k+1)**(i-1)*k+(k-1)**i-2*k**i<0): return False
    return True
for n in [1000,10000]:
    res=[]
    for b in range(3,13):
        res.append((b,bound(n,b)))
    best=min(res,key=lambda t:t[1])
    fb=None
    for b in range(3,200):
        if not admissible(n,b): fb=b;break
    print(n,'first inadmissible',fb,'best',best[0],mpmath.nstr(best[1],12),[(b,mpmath.nstr(v,6)) for b,v in res])
