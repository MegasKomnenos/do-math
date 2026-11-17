# 검토전체24 R5: 장6 의 k>=2001 진술을 k=2001 (및 y=2000, y=4000) 에서 배정밀도로 직접 확인
# 방법: 마지막 차 재귀 (6.11) 을 z=1/e 로 기울여 U_N = A_{N,cap-1} e^{-N}/N! 을 구하고
#       s_N(cap) = U_N / (p_N e^{-N}/N!) 로 나눈다. 모든 항이 양수라 상대 오차는 N*eps 수준.
import numpy as np
import math
import sys


def tilted(cap, nmax):
    U = np.zeros(nmax + 1)
    U[0] = 1.0
    K = np.minimum(np.arange(nmax + 1) + 1, cap).astype(float)
    z = math.exp(-1.0)
    KU = np.zeros(nmax + 1)
    KU[0] = K[0] * U[0]
    for N in range(nmax):
        U[N + 1] = z * np.dot(KU[:N + 1], U[N::-1][:N + 1]) / (N + 1)
        KU[N + 1] = K[N + 1] * U[N + 1]
    return U


def free(nmax):
    # p_N e^{-N}/N! = e*Bor(N+1)
    out = np.zeros(nmax + 1)
    out[0] = 1.0
    for N in range(1, nmax + 1):
        out[N] = math.exp((N - 1) * math.log(N + 1) - N - math.lgamma(N + 1))
    return out


def Bor(n):
    return math.exp((n - 1) * math.log(n) - n - math.lgamma(n + 1))


def g(x):
    return (x - 1) * math.log1p(1 / x)


c2p = (2 * math.pi) ** -0.5
k = 2001
NM = 2 * k + 6
F = free(NM)
S = {}
for cap in (k - 1, k, k + 1, k + 2):
    S[cap] = tilted(cap, NM) / F
    assert abs(S[cap][cap] - 1) < 1e-11, (cap, S[cap][cap])


def s(m, y):
    return S[y][m]


def c(m, Y):
    return S[Y + 1][m] - S[Y][m]


# --- 정리 6:old-8-25 at y=2000, 2001 ; 따름정리 6:old-7-13
for y in (k - 1, k):
    worst = 0
    for d in range(1, y + 3):
        up = min(1.0, 1.15 * (y + d) / d ** 1.5)
        worst = max(worst, s(y + d - 1, y) / up)
    w3 = max(s(y + q, y) / min(1.0, 3 * y * q ** -1.5) for q in range(1, y + 1))
    print("y", y, "max s_d/s^up", worst, "max s/min(1,3y q^-1.5)", w3)

# --- 따름정리 6:old-8-11
def uu(k):
    return 3 / 0.35 * (1.35 + 1 / k) * (0.65 - 1 / k) ** -1.5 / math.sqrt(k)


def ub(k):
    return 1.15 / 0.35 * (2 + 1 / k) * (0.65 - 1 / k) ** -1.5 / math.sqrt(k)


print("k c_{2k}(k-1)", k * c(2 * k, k - 1), "(k-1)c_{2k}(k)", (k - 1) * c(2 * k, k), "u", uu(k), "uflat", ub(k))

# --- V 핵심, 모든 절단점
pm = np.array([(k + 1) * c(m, k) - (k - 1) * c(m, k - 1) for m in range(k, 2 * k + 1)])
V = np.cumsum(pm[::-1])[::-1]
bm = np.array([math.e * Bor(m + 1) for m in range(k, 2 * k + 1)]) * pm
Ub = np.cumsum(bm[::-1])[::-1]


def DDLn(k):
    return 14 * (math.log(3 * k) - 1) / (5 * math.sqrt(math.pi * k)) + 37.6 / (5 * math.sqrt(math.pi) * k)


v = 2 - 4.6 / math.sqrt(k + 1) - 2 * ub(k) - DDLn(k) / 2
print("V_k(k)", V[0], "v(k)", v, "min V_k(m)", V.min(), "argmin m-k", int(V.argmin()), "min U_k(m)", Ub.min(), "argmin", int(Ub.argmin()))
near = [V[m - k] for m in range(k, 2 * k + 1) if m - k <= m ** (2 / 3) / 2]
print("핵심 근처 절단점 수", len(near), "min V", min(near), ">= 1/6?", min(near) >= 1 / 6)

# --- (6.40), DD 와 H_d
def DD(m, y):
    return (y + 2) * s(m + 2, y + 2) - 2 * (y + 1) * s(m + 1, y + 1) + y * s(m, y)


dd = np.array([DD(m, k - 1) for m in range(k, 2 * k)])
stay2k = s(2 * k + 1, k + 1) - s(2 * k, k)
Bd = 2 - 2 * s(2 * k + 1, k + 1) - (k - 1) * stay2k - (k - 1) * c(2 * k, k - 1)
print("(6.40) 잔차", V[0] - (Bd + dd.sum()), "Bd", Bd, "Bd 하계", 2 - 4.6 / math.sqrt(k + 1) - 2 * ub(k), "sum DD", dd.sum(), "sum DD_-", np.minimum(dd, 0).sum())

# H_d (6.37) : y0 = k
gv = np.array([0.0] + [g(x) for x in range(1, 2 * k + 5)])
lB = np.array([0.0] + [(n - 1) * math.log(n) - n - math.lgamma(n + 1) for n in range(1, 2 * k + 5)])
H = np.zeros(k + 2)
viol = 0
for q in range(1, k + 1):
    ds = np.arange(q + 1, k + 2)
    incm = gv[k - 1 + ds] - gv[k - 1 + q]
    incp = gv[k + ds] - gv[k + q]
    kk = np.expm1(incm) + np.expm1(-incp)
    acrit = (k - 1) * kk / (2 * (-np.expm1(-incp)))
    stp = acrit * (k + 1 + q) / q
    tilt = np.exp(lB[k + q] - lB[k + ds])
    borj = np.exp(lB[ds - q])
    rho = (k - 1) / (k - 1 + q)
    Jmax = int(math.ceil(stp.max())) + 1
    js = np.arange(0, Jmax + 1, dtype=float)
    P1 = np.cumsum(js * rho ** js)
    P2 = np.cumsum(js * js * rho ** js)
    Jd = np.ceil(stp).astype(int) - 1  # 1<=j<stp
    Jd = np.maximum(Jd, 0)
    inner = P1[Jd] - P2[Jd] / stp
    term = q * kk * tilt * borj * np.minimum(ds - q, inner)
    H[ds] += term
    if acrit.max() > 1.3778:
        viol += 1
DDL2 = 2 * H[2:].sum()
neg = np.maximum(-dd, 0)
print("DDL_2(k)", DDL2, "DDLnat(k)", DDLn(k), "A^crit>1.3778 위반 q 수", viol)
print("max over d of (DD_- - H_d)", max(neg[d - 2] - H[d] for d in range(2, k + 2)), "sum DD_-", neg.sum(), "<= DDL2/2", DDL2 / 2)

# --- 명제 6:prop-R 와 보조정리 6:lemma-Hprime
sB = math.e * c2p
dk = 1 / math.e + uu(k) / (math.e * 2 ** 1.5)
worst = min(Ub[m - k] / math.e - ((k + 1) * Bor(m + 1) * c(m, k) - dk * sB * k ** -1.5) for m in range(k, 2 * k + 1))
print("prop-R 여유 최소", worst)


def Low(k, rho):
    eps = k ** (-1 / 3)
    br = c2p * (2 * math.sqrt(rho) - 1.6781 * eps)
    return k ** (1 / 3) * br / (1 + rho * eps) * math.exp(-1 / (12 * (k + 1))) * math.exp(-rho ** 2 * (1 + rho * eps) ** 1.5 * math.exp(1 / (4 * (k + 1))) / br)


worst = min((k + 1) * c(k + d, k) / Low(k, d / k ** (2 / 3)) for d in range(1, k + 1))
print("Hprime: min (k+1)c_m(k)/Low", worst)
W0 = sum(Bor(n) * c(n - 1, k - 1) for n in range(k + 1, 2 * k + 1))
print("W0", W0, "상계", 2 * c2p * k ** -1.5)

# --- 정리 6:old-8-12 at y=4000 (인자로 'bulk' 를 주면)
if len(sys.argv) > 1 and sys.argv[1] == 'bulk':
    y = 4000
    NM2 = 2 * y + 2
    F2 = free(NM2)
    Sa = tilted(y - 1, NM2) / F2
    Sb = tilted(y, NM2) / F2
    q0 = math.ceil(1.5 * (2 * y + 1) ** (2 / 3))
    worst = max((Sb[y + q] - Sa[y + q]) / (16.54 * (y + q / 3) * q ** -2.5) for q in range(q0, y + 1))
    print("old-8-12: q0", q0, "max c/(16.54(y+q/3)q^-2.5)", worst)
