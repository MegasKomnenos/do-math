# S12 검산: 기록 cemaj_iv.py의 zeta32 (C=2000) 구간과 부록 D.zeta-constants 「결과」의 값 대조,
# 그리고 사다리꼴 보정 없는 성긴 방법의 하단(2.6123698) 재현.
from mpmath import iv, mp
mp.dps = 30; iv.dps = 30
N = 2000
s = iv.mpf(0)
for j in range(1, N):
    s += iv.mpf(j) ** iv.mpf('-1.5')
lo = (s + 2 * iv.mpf(N) ** iv.mpf('-0.5') + iv.mpf(N) ** iv.mpf('-1.5') / 2).a
hi = (s + 2 * (iv.mpf(N) - iv.mpf('0.5')) ** iv.mpf('-0.5')).b
print("zeta32 C=2000:", mp.nstr(lo, 12), mp.nstr(hi, 12))
# 성긴 방법: sum_{j<=C} j^{-3/2} + 2(C+1)^{-1/2} (하단), + 2(C+1/2)^{-1/2} (상단)
s2 = s + iv.mpf(N) ** iv.mpf('-1.5')
lo2 = (s2 + 2 * iv.mpf(N + 1) ** iv.mpf('-0.5')).a
hi2 = (s2 + 2 * (iv.mpf(N) + iv.mpf('0.5')) ** iv.mpf('-0.5')).b
print("coarse C=2000:", mp.nstr(lo2, 10), mp.nstr(hi2, 10))
# |zeta(-1/2)| 참값 대조
print("zeta(-1/2) =", mp.nstr(mp.zeta(-0.5), 20), " diff const-true =", mp.nstr(mp.mpf('0.2078862250607') - abs(mp.zeta(-0.5)), 5))
print("zeta(1/2) =", mp.nstr(mp.zeta(0.5), 20), " zeta(3/2) =", mp.nstr(mp.zeta(1.5), 20))
