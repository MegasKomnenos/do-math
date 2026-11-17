# R7a: (7.7) 1 - s_{k+q-1}(k) <= q^{3/2}/(2k) 를 k=10000, 15000에서 고정밀 부동소수(mpmath 30자리)로 확인
from mpmath import mp, mpf, exp, loggamma, log
import sys
mp.dps = 30
def run(k, Q=101):
    M = k+Q-1
    # ahat_n = A_{n,k-1} e^{-n}/n!;  n<=k: p_n e^{-n}/n!
    ah = [mpf(1)]
    for n in range(1, k+1):
        ah.append(exp((n-1)*log(mpf(n+1)) - n - loggamma(n+1)))
    einv = exp(-1)
    for n in range(k+1, M+1):
        s = mpf(0)
        for j in range(1, n+1):
            s += min(j, k)*ah[j-1]*ah[n-j]
        ah.append(einv*s/n)
    worst = 0
    for q in range(1, Q+1):
        m = k+q-1
        pm = exp((m-1)*log(mpf(m+1)) - m - loggamma(m+1))
        tail = 1 - ah[m]/pm
        bound = mpf(q)**mpf(1.5)/(2*k)
        r = tail/bound
        if r > worst: worst = r; wq = q
        if q in (1, 2, 3, 10, 50, 101): print(k, q, float(tail), float(bound), float(r))
    print("k =", k, "max ratio tail/bound =", float(worst), "at q =", wq)
run(int(sys.argv[1]) if len(sys.argv) > 1 else 10000)
