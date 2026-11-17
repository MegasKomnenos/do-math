# R11 검산: D.zeta-constants의 수치
from mpmath import iv, mp, mpf, zeta
mp.dps = 40; iv.dps = 30
def z32(N):
    s = iv.mpf(0)
    for j in range(1, N):
        s += iv.mpf(j) ** iv.mpf('-1.5')
    Nn = iv.mpf(N)
    lo = s + 2 * Nn ** iv.mpf('-0.5') + Nn ** iv.mpf('-1.5') / 2
    hi = s + 2 * (Nn - iv.mpf('0.5')) ** iv.mpf('-0.5')
    return lo.a, hi.b, s
lo, hi, s = z32(2000)
print("C=2000 trapezoid/midpoint:", lo, hi)
# coarse: S + C^{-3/2} + 2(C+1)^{-1/2}, upper + 2(C+1/2)^{-1/2}
C = iv.mpf(2000)
sC = s + C ** iv.mpf('-1.5')
print("coarse C=2000 lower:", (sC + 2 * (C + 1) ** iv.mpf('-0.5')).a, " upper:", (sC + 2 * (C + iv.mpf('0.5')) ** iv.mpf('-0.5')).b)
lo, hi, s = z32(4000)
print("C=4000:", lo, hi)
print("zeta(3/2), zeta(1/2), zeta(-1/2):", zeta(mpf(3)/2), zeta(mpf(1)/2), zeta(mpf(-1)/2))
