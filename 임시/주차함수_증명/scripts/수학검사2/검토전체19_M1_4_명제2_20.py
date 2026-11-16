# M1: 명제 2-20 유한 n 상계값(0.740, 0.317, 0.0658, 0.0115) 재계산 (유리수 정확 계산 -> 소수)
from fractions import Fraction
from math import comb, factorial, log
import sys
sys.setrecursionlimit(10000)

def v(k, Z, H):
    return Fraction(k+1, k)**Z + Fraction(k-1, k)**(Z+H) - 2

def lgfact(n): return sum(log(i) for i in range(1, n+1))

def bound(n, b):
    # condition: v_k(i-1,1)<0 for all 3<=i<=b and n/2<k<=n
    for i in range(3, b+1):
        for k in range(n//2+1, n+1):
            if not (v(k, i-1, 1) < 0): return None
    # use logs (floats) for n large; use Fraction for n<=100 to be exact-ish
    import mpmath as mp
    mp.mp.dps = 40
    def P1(c):
        kap = n-c-b+1
        if kap < 0: return mp.mpf(0)
        return mp.mpf(mp.factorial(n))/mp.factorial(c)*mp.mpf(c)**(c-1)*b*mp.mpf(n-c+1)**(n-c-b)/(mp.factorial(kap)*mp.mpf(n+1)**(n-1))
    def P2(c):
        kap = n-c-b+1
        if kap < 0: return mp.mpf(0)
        return mp.mpf(mp.factorial(n))/mp.factorial(c)*mp.mpf(c)**(c-1)*2*mp.mpf(n-c-b+3)**(n-c-b)/(mp.factorial(kap)*mp.mpf(n+1)**(n-1))
    s1 = sum(P1(c) for c in range(n//2+1, n+1))
    s2 = sum(P2(c) for c in range(n//2+1, n+1))
    return 1 - s1 + s2

for n in [17, 100, 1000, 10000]:
    best = None
    for b in range(3, 40):
        r = bound(n, b)
        if r is None: break
        if best is None or r < best[1]: best = (b, r)
    print(n, "best b", best[0], "bound", mp_str := str(best[1])[:12])
