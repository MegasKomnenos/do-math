# K12: D.fiber-nonunimodal-bound -- recompute bound(n,b) and the admissibility condition
from fractions import Fraction
from math import factorial
import mpmath as mp
mp.mp.dps = 50

def admissible(n, b):
    for i in range(3, b+1):
        for k in range(n//2+1, n+1):
            if not ((k+1)**(i-1)*k + (k-1)**i - 2*k**i < 0): return False
    return True

def bound_exact(n, b):
    s1 = s2 = Fraction(0)
    for c in range(n//2+1, n+1):
        kap = n-c-b+1
        if kap < 0: continue
        base = Fraction(factorial(n), factorial(c)) * Fraction(c)**(c-1) / (factorial(kap)*(n+1)**(n-1))
        s1 += base*b*Fraction(n-c+1)**(n-c-b)
        s2 += base*2*Fraction(n-c-b+3)**(n-c-b)
    return 1-s1+s2

def bound_mp(n, b):
    s1 = mp.mpf(0); s2 = mp.mpf(0)
    lg = lambda m: mp.loggamma(m+1)
    for c in range(n//2+1, n+1):
        kap = n-c-b+1
        if kap < 0: continue
        lbase = lg(n)-lg(c)+(c-1)*mp.log(c)-lg(kap)-(n-1)*mp.log(n+1)
        s1 += mp.e**(lbase+mp.log(b)+(n-c-b)*mp.log(n-c+1))
        s2 += mp.e**(lbase+mp.log(2)+(n-c-b)*mp.log(n-c-b+3))
    return 1-s1+s2

for n in (17, 100, 1000, 10000):
    best = None; firstfail = None
    for b in range(3, n//2+2):
        if not admissible(n, b): firstfail = b; break
        v = bound_exact(n, b) if n <= 60 else bound_mp(n, b)
        vf = mp.mpf(v.numerator)/v.denominator if n <= 60 else v
        if best is None or vf < best[1]: best = (b, vf)
    print(f"n={n}: best b={best[0]}, bound={mp.nstr(best[1], 12)}, first inadmissible b={firstfail}")
