# -*- coding: utf-8 -*-
"""검토전체6 L1: 명제 old-2-20의 유한 n 상계 네 값을 mpmath 50자리로 재계산한다 (허용 조건은 정확 정수). python -I."""
from mpmath import mp, mpf, loggamma, exp, log
mp.dps = 50

def allowed(n, b):
    # 3<=i<=b, n/2<k<=n 에서 k^i v_k(i-1,1) = (k+1)^{i-1} k + (k-1)^i - 2k^i < 0
    for i in range(3, b+1):
        for k in range(n//2+1, n+1):
            if (k+1)**(i-1)*k + (k-1)**i - 2*k**i >= 0:
                return False
    return True

def lf(x): return loggamma(mpf(x)+1)

def bound(n, b):
    tot1 = mpf(0); tot2 = mpf(0)
    for c in range(n//2+1, n+1):
        kap = n-c-b+1
        if kap < 0: continue
        lbase = lf(n) - lf(c) + (c-1)*log(c) - (n-1)*log(n+1) - lf(kap)
        if kap == 0:
            t1 = exp(lbase)        # b * (n-c+1)^{-1} = b/b = 1
            t2 = exp(lbase)        # 2 * (n-c-b+3)^{-1} = 2/2 = 1
        else:
            t1 = exp(lbase + log(b) + (n-c-b)*log(n-c+1))
            t2 = exp(lbase + log(2) + (n-c-b)*log(n-c-b+3))
        tot1 += t1; tot2 += t2
    return 1 - tot1 + tot2

for n in (17, 100, 1000, 10000):
    best = None; first_bad = None
    for b in range(3, n//2+2):
        if not allowed(n, b):
            first_bad = b; break
        v = bound(n, b)
        if best is None or v < best[1]: best = (b, v)
    print(n, "최적 b =", best[0], "상계 =", mp.nstr(best[1], 12), " 허용 조건 첫 실패 b =", first_bad)
