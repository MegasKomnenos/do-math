# D.zeta-constants: coarse method check (no trapezoid correction) at N=2000
from mpmath import mp, mpf, zeta
mp.dps = 30
N = 2000
S_full = sum(mpf(j)**mpf(-1.5) for j in range(1, N+1))   # sum_{j<=N}
lo = S_full + 2/mp.sqrt(N+1)
hi = S_full + 2/mp.sqrt(N+mpf(1)/2)
print("coarse lower", lo, "upper", hi)
S = S_full - mpf(N)**mpf(-1.5)   # sum_{j<N}
lo2 = S + 2/mp.sqrt(N) + mpf(1)/(2*mpf(N)**mpf(1.5))
hi2 = S + 2/mp.sqrt(N-mpf(1)/2)
print("trapezoid lower", lo2, "midpoint upper", hi2)
print("zeta(3/2)", zeta(mpf(3)/2), "zeta(-1/2)", zeta(mpf(-1)/2), "zeta(1/2)", zeta(mpf(1)/2))
print("ZM12 const - true", mpf('0.2078862250607') + zeta(mpf(-1)/2))
# check 8^6, 7^5
print(7**5, 8**6)
