# R12 검산: D.stored-table-check의 이음새 네 값과 가장 작은 여유의 설명값,
# D.band-boxes가 쓰는 Bor_<= 관련 어림을 본문 (8.10)(8.12)(8.14)(8.16)의 식에서 직접 다시 계산한다.
# mpmath 40자리(구간 산술 아님; 값의 대조용).
from mpmath import mp, mpf, sqrt, pi, exp, zeta

mp.dps = 40
g = 1 / sqrt(2 * pi)
z12 = zeta(mpf(1) / 2)
zm12 = zeta(-mpf(1) / 2)
z32 = zeta(mpf(3) / 2)
cpsi = -z12 + z32 / 12


def psilow(x):
    return g * (2 * sqrt(x) - cpsi + 1 / (2 * sqrt(x)) - x ** mpf(-1.5) / 24)


def esc(xi, k):
    xi = mpf(xi)
    k = mpf(k)
    q = xi * k ** (mpf(2) / 3)
    p = q - 1
    n = k + q
    kk = k + 1
    eps = k ** (-mpf(1) / 3)
    E = 2 * g * exp(-1 / (12 * q)) * xi ** mpf(-0.5) * (1 + xi * eps)
    R1 = mpf(3) / 2 * g * (2 * sqrt(p) - 1) * k ** (-mpf(2) / 3)
    H = mpf(2) / 3 * p ** mpf(1.5) + sqrt(p) / 2 + zm12 + 1 / (24 * sqrt(p))
    R2 = mpf(15) / 8 * g * n ** mpf(2.5) * H / (kk ** mpf(3.5) * k ** (mpf(2) / 3))
    D1 = p / k ** (mpf(2) / 3)
    D2 = kk * sqrt(2 / pi) / sqrt(p) / k ** (mpf(2) / 3)
    D3 = mpf(3) / 2 * kk * psilow(p) / ((n + 1) * k ** (mpf(2) / 3))
    return (E - R1 - R2) / (D1 + D2 - D3)


def jinf(xi):
    return mpf(4) / 3 * g * mpf(xi) ** mpf(1.5)


print("z_{1/2}, z_{-1/2}, z_{3/2}, c_Psi =", z12, zm12, z32, cpsi)
for xi in ("2", "2.1"):
    print("xi =", xi, " Esc_6600 =", mp.nstr(esc(xi, 6600), 12), " exp(-j_inf) =", mp.nstr(exp(-jinf(xi)), 12))


# 가장 작은 여유의 설명: Cr(xi K^{2/3}, K), K = 6.6e9 근처, xi = 0.0005
def Cr(q, k):
    n = k + q
    kk = k + 1
    s = mpf(4) / 15 * q ** mpf(2.5) + mpf("0.385") * q ** mpf(1.5)
    return mpf(3) / 2 * g * n ** mpf(1.5) / kk ** mpf(3.5) * s


xi = mpf("0.0005")
Ks = max(mpf(6600), (2 / xi) ** mpf(1.5))
print("K_s(0.0005) =", mp.nstr(Ks, 8), " 10 K_s =", mp.nstr(10 * Ks, 8))
K = Ks
L = 1
target = max(mpf("6.6e9"), 10 * Ks)
while K < target:
    K *= mpf("1.02")
    L += 1
print("K_{L-1} =", mp.nstr(K, 8), " L =", L)
print("Cr at K_{L-1}:", mp.nstr(Cr(xi * K ** (mpf(2) / 3), K), 8),
      " 0.16 xi^{5/2} K^{-1/3}:", mp.nstr(mpf("0.16") * xi ** mpf(2.5) * K ** (-mpf(1) / 3), 8))
