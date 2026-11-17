# R11 검산: D.exact-n20000 · D.c50의 개수
from math import ceil
B = lambda k: (k*k+3)//4
print("k2..120 direct:", sum((10000-12+1) if k <= 5 else (10000-2*k) for k in range(2, 121)))
for lo, hi in ((161, 500), (121, 160)):
    print(lo, hi, "direct:", sum(2*B(k)-2*k for k in range(lo, hi+1)), "ratio:", sum(B(k)+1 for k in range(lo, hi+1)))
print("row cert:", sum(10000-2*k for k in range(501, 5000)))
kn = lambda n: (n+1)//2
print("(L) 10001..20000:", sum(kn(n)-1 for n in range(10001, 20001)))
pos = lambda n: n-2-ceil((n-1)/2)
print("(R) 5..20000 positions:", sum(pos(n) for n in range(5, 20001)), "pairs:", sum(pos(n)+1 for n in range(5, 20001)))
print("c50 positions:", sum(pos(n) for n in range(20001, 50001)), "pairs:", sum(pos(n)+1 for n in range(20001, 50001)))
# m(n) = max{m: m^{3/2}+9m <= n}; integer test m^3 <= (n-9m)^2 (n>=9m)
def mm(n):
    m = 0
    while (m+1)*9 <= n and (m+1)**3 <= (n-9*(m+1))**2: m += 1
    return m
print("m(20001), m(50000):", mm(20001), mm(50000), " min n with m>=171:", next(n for n in range(1, 10**5) if mm(n) >= 171))
