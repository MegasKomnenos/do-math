# H12 검산 1: 부록 D 2장 항목
from fractions import Fraction
from itertools import permutations
import math

def caps(sigma):
    n=len(sigma); h=[]
    for i in range(1,n+1):
        m=0
        for j in range(1,i):
            if sigma[j-1]>sigma[i-1]: m=j
        h.append(i-m)
    return h

def row(h):
    n=len(h); A=[]; 
    for l in range(n):
        p=1
        for x in h: p*=min(x,l+1)
        A.append(p)
    return [A[0]]+[A[l]-A[l-1] for l in range(1,n)]

def unimodal(z):
    i=0
    while i+1<len(z) and z[i]<=z[i+1]: i+=1
    while i+1<len(z) and z[i]>=z[i+1]: i+=1
    return i==len(z)-1

print("--- D.fiber-enumeration ---")
for n in range(1,8):
    keys=set(); nonuni=[]; 
    for s in permutations(range(1,n+1)):
        h=caps(s); keys.add(tuple(sorted(h)))
        r=row(h)
        if not unimodal(r): nonuni.append((s,h,r))
    print(n, "multisets", len(keys), "nonunimodal fibers", len(nonuni), nonuni[0] if nonuni else "")
print("7^7=",7**7, "8^6=",8**6, "7^5=",7**5)

print("--- D.fiber-nonunimodal-bound ---")
def v_int_ok(n,b):
    # all 3<=i<=b, all integer n/2<k<=n: (k+1)^(i-1) k + (k-1)^i - 2k^i < 0
    for i in range(3,b+1):
        for k in range(n//2+1, n+1):
            if (k+1)**(i-1)*k + (k-1)**i - 2*k**i >= 0: return False
    return True

def bound_exact(n,b):
    tot1=Fraction(0); tot2=Fraction(0)
    for c in range(n//2+1, n+1):
        kap=n-c-b+1
        if kap<0: continue
        base=Fraction(math.factorial(n)*c**(c-1), math.factorial(c)*(n+1)**(n-1))
        if kap==0:
            t1=base*1; t2=base*1
        else:
            t1=base*Fraction(b*(n-c+1)**(n-c-b), math.factorial(kap))
            t2=base*Fraction(2*(n-c-b+3)**(n-c-b), math.factorial(kap))
        tot1+=t1; tot2+=t2
    return 1-tot1+tot2

import mpmath as mp
mp.mp.dps=50
def bound_mp(n,b):
    tot1=mp.mpf(0); tot2=mp.mpf(0)
    lognp=(n-1)*mp.log(n+1)
    for c in range(n//2+1, n+1):
        kap=n-c-b+1
        if kap<0: continue
        lb=mp.loggamma(n+1)-mp.loggamma(c+1)+(c-1)*mp.log(c)-lognp-mp.loggamma(kap+1)
        if kap==0:
            t1=mp.e**lb; t2=t1
        else:
            t1=mp.e**(lb+mp.log(b)+(n-c-b)*mp.log(n-c+1))
            t2=mp.e**(lb+mp.log(2)+(n-c-b)*mp.log(n-c-b+3))
        tot1+=t1; tot2+=t2
    return 1-tot1+tot2

for n in (17,100,1000,10000):
    best=None; firstfail=None
    for b in range(3, n//2+2):
        if not v_int_ok(n,b): firstfail=b; break
        val=bound_mp(n,b)
        if best is None or val<best[1]: best=(b,val)
    print(n, "best b", best[0], mp.nstr(best[1],12), "first fail b", firstfail)
    if n==17:
        ex=bound_exact(17,3); print(" exact n=17 b=3:", float(ex), ex)
        print(" exact b=4:", float(bound_exact(17,4)))

print("--- zeta ---")
mp.mp.dps=30
print(mp.zeta(mp.mpf(3)/2), mp.zeta(mp.mpf(1)/2), mp.zeta(-mp.mpf(1)/2))
C=2000
S=mp.fsum(mp.mpf(j)**(-1.5) for j in range(1,C+1))
print("coarse lower C=2000:", S+2*mp.mpf(C+1)**(-0.5), "upper", S+2*mp.mpf(C+0.5)**(-0.5))
S2=mp.fsum(mp.mpf(j)**(-1.5) for j in range(1,C))
print("trapezoid lower:", S2+2*mp.mpf(C)**(-0.5)+0.5*mp.mpf(C)**(-1.5), "midpoint upper:", S2+2*mp.mpf(C-0.5)**(-0.5))
print("0.2078862250607 - true =", mp.mpf('0.2078862250607')+mp.zeta(-mp.mpf(1)/2))
