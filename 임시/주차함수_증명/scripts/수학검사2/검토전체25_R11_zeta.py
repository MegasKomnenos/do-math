# R11 검산: D.zeta-constants 항목의 수치
from mpmath import iv, mp, zeta
mp.dps = 40
for dps in (25, 30):
    iv.dps = dps
    N = 2000; s = iv.mpf(0)
    for n in range(1, N): s += iv.mpf(n) ** iv.mpf('-1.5')
    lo = (s + 2 * iv.mpf(N) ** iv.mpf('-0.5') + iv.mpf(N) ** iv.mpf('-1.5') / 2).a
    hi = (s + 2 * (iv.mpf(N) - iv.mpf('0.5')) ** iv.mpf('-0.5')).b
    print("dps", dps, "zeta32 C=2000:", mp.nstr(lo, 15), mp.nstr(hi, 15))
    # coarse: sum_{j<=C} + 2(C+1)^{-1/2} .. 2(C+1/2)^{-1/2}
    s2 = s + iv.mpf(N) ** iv.mpf('-1.5')
    print("  coarse lower:", mp.nstr((s2 + 2 * (iv.mpf(N) + 1) ** iv.mpf('-0.5')).a, 12), "coarse upper:", mp.nstr((s2 + 2 * (iv.mpf(N) + iv.mpf('0.5')) ** iv.mpf('-0.5')).b, 12))
print(zeta(mp.mpf('1.5')), zeta(mp.mpf('0.5')), zeta(mp.mpf('-0.5')))
# c_Psi
print("c_Psi upper from intervals:", 1.46036 + 2.61238/12, " lower:", 1.46035 + 2.61237/12)
