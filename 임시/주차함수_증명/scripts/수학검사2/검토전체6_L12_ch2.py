# L12 ch2 checks: fiber enumeration, fiber non-unimodal bound, zeta constants
import itertools, math
from fractions import Fraction
import mpmath as mp
mp.mp.dps = 50

def caps(sig):
    n=len(sig); h=[]
    for i in range(1,n+1):
        z=0
        for j in range(i-1,0,-1):
            if sig[j-1]>sig[i-1]: z=j;break
        h.append(i-z)
    return h
def row(h):
    n=len(h); A=[1]
    for l in range(n):
        A.append(math.prod(min(x,l+1) for x in h))
    return [A[l+1]-A[l] for l in range(n)]
def unimodal(b):
    i=0
    while i+1<len(b) and b[i]<=b[i+1]: i+=1
    while i+1<len(b) and b[i]>=b[i+1]: i+=1
    return i==len(b)-1
for n in range(1,8):
    ms=set(); nonuni=[]
    for sig in itertools.permutations(range(1,n+1)):
        h=caps(sig); ms.add(tuple(sorted(h)))
        if not unimodal(row(h)): nonuni.append(sig)
    print(n, "multisets",len(ms),"nonuni",len(nonuni), nonuni[:1], caps(nonuni[0]) if nonuni else None, row(caps(nonuni[0])) if nonuni else None)

# fiber bound
def v_cond(n,b):
    # all 3<=i<=b, all integer n/2<k<=n: (k+1)^(i-1) k + (k-1)^i - 2k^i < 0
    for i in range(3,b+1):
        for k in range(n//2+1, n+1):
            if (k+1)**(i-1)*k+(k-1)**i-2*k**i >= 0: return False
    return True
def bound(n,b,exact=False):
    F = Fraction if exact else (lambda x: mp.mpf(x))
    tot1=F(0); tot2=F(0)
    for c in range(n//2+1, n+1):
        kap=n-c-b+1
        if kap<0: continue
        base = F(math.factorial(n))/F(math.factorial(c))*F(c)**(c-1)/F(math.factorial(kap))/F(n+1)**(n-1)
        if kap==0:
            t1=base*1; t2=base*1
        else:
            t1=base*b*F(n-c+1)**(n-c-b)
            t2=base*2*F(n-c-b+3)**(n-c-b)
        tot1+=t1; tot2+=t2
    return 1-tot1+tot2
for n in [17,100,1000,10000]:
    best=None; firstfail=None
    b=3
    while b-1<=n/2:
        if not v_cond(n,b): firstfail=b;break
        val=bound(n,b)
        if best is None or val<best[0]: best=(val,b)
        b+=1
    print("n",n,"best",mp.nstr(best[0],12),"b",best[1],"first fail b",firstfail)
    if n==17: print(" exact b=3:", float(bound(17,3,True)), bound(17,3,True))

# zeta
for N in [2000,4000]:
    S=mp.fsum(mp.mpf(j)**mp.mpf(-1.5) for j in range(1,N))
    lo=S+2*mp.mpf(N)**-0.5+mp.mpf(N)**-1.5/2; hi=S+2*(mp.mpf(N)-mp.mpf(1)/2)**-0.5
    print("N",N,"z32 in",mp.nstr(lo,14),mp.nstr(hi,14),"true",mp.nstr(mp.zeta(1.5),14))
    S2=mp.fsum(mp.sqrt(j) for j in range(1,N+1))
    zm=S2-(mp.mpf(2)/3*mp.mpf(N)**1.5+mp.mpf(N)**0.5/2+mp.mpf(N)**-0.5/24); r=mp.mpf(N)**-2.5/1920
    print("  zm12 in",mp.nstr(zm-r,16),mp.nstr(zm+r,16),"true",mp.nstr(mp.zeta(-0.5),16))
    S3=mp.fsum(mp.mpf(j)**-0.5 for j in range(1,N+1))
    zp=S3-(2*mp.sqrt(N)+mp.mpf(N)**-0.5/2-mp.mpf(N)**-1.5/24); r=mp.mpf(N)**-3.5/384
    print("  z12 in",mp.nstr(zp-r,16),mp.nstr(zp+r,16),"true",mp.nstr(mp.zeta(0.5),16))
    if N==2000:
        S4=S+mp.mpf(N)**-1.5
        print("  coarse lower",mp.nstr(S4+2*(N+1)**-0.5,10))
print("0.2078862250607 - true =", mp.nstr(mp.mpf('0.2078862250607')+mp.zeta(-0.5),5))
