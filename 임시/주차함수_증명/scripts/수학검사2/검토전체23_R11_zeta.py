from mpmath import mp, iv, zeta, mpf, sqrt
mp.dps = 30; iv.dps = 30
print("zeta(-1/2)", zeta(mpf(-1)/2)); print("zeta(1/2)", zeta(mpf(1)/2)); print("zeta(3/2)", zeta(mpf(3)/2))
for C in (2000, 4000):
    s = iv.mpf(0)
    for j in range(1, C): s += iv.mpf(1)/iv.sqrt(iv.mpf(j))**3
    Cn = iv.mpf(C)
    lo = s + 2/iv.sqrt(Cn) + 1/(2*iv.sqrt(Cn)**3)
    hi = s + 2/iv.sqrt(Cn - iv.mpf(1)/2)
    print(C, "trap/mid:", lo.a, hi.b)
    # coarser: partial sum through C plus integral bounds 2(C+1)^(-1/2), 2(C+1/2)^(-1/2)
    s2 = s + 1/iv.sqrt(Cn)**3
    print(C, "coarse:", (s2 + 2/iv.sqrt(Cn+1)).a, (s2 + 2/iv.sqrt(Cn+iv.mpf(1)/2)).b)
