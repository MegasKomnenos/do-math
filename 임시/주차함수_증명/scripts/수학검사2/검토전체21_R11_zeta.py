# R11 검산: 부록 D.zeta-constants의 수치 주장 재계산 (mpmath iv)
from mpmath import iv, mp, mpf, zeta
mp.dps = 30; iv.dps = 30
def z32(N):
    s = iv.mpf(0)
    for j in range(1, N): s += iv.mpf(1)/iv.sqrt(iv.mpf(j))**3
    Nn = iv.mpf(N)
    lo = s + 2/iv.sqrt(Nn) + iv.mpf(1)/(2*iv.sqrt(Nn)**3)
    hi = s + 2/iv.sqrt(Nn - iv.mpf(1)/2)
    return lo.a, hi.b, s
lo, hi, s = z32(2000)
print("zeta32 C=2000 :", mp.nstr(lo, 15), mp.nstr(hi, 15))
# 성긴 방법: S' = sum_{j<=C} j^{-3/2} = S + C^{-3/2}; 하계 S' + 2(C+1)^{-1/2}, 상계 S' + 2(C+1/2)^{-1/2}
Sp = s + iv.mpf(1)/iv.sqrt(iv.mpf(2000))**3
clo = (Sp + 2/iv.sqrt(iv.mpf(2001))).a
chi = (Sp + 2/iv.sqrt(iv.mpf(2000) + iv.mpf(1)/2)).b
print("coarse C=2000 :", mp.nstr(clo, 12), mp.nstr(chi, 12))
print("true zeta(3/2) =", zeta(mpf(3)/2))
print("true zeta(-1/2)=", zeta(mpf(-1)/2), " record cemaj_iv/emaj2 value -0.2078862250607212  diff =", zeta(mpf(-1)/2) - mpf('-0.2078862250607212'))
print("true zeta(1/2) =", zeta(mpf(1)/2))
# 재실행표 여유 주장
print("margins:", mpf('-0.2078862249784')-mpf('-0.20789'), mpf('2.61238')-mpf('2.6123753488'), mpf('-1.4603545088096')-mpf('-1.46036'))
