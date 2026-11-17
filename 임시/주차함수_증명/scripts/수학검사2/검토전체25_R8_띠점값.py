# 검토전체25 R8: 장8.md의 (8.23) LB^low(k,nu)와 (8.21)을 본문 식 그대로 점에서 평가 (배정밀도; 증명이 아니라 대조)
# 입력 표: 원고_자료/세션_재계산/r030ffae_window/work/{wKrig,qenv_fix_v}.npy (읽기만 한다)
import numpy as np, sys
from math import lgamma, log, exp, pi, sqrt, ceil, floor

W = "원고_자료/세션_재계산/r030ffae_window/work/"
wK = np.load(W + "wKrig.npy"); zT = np.load(W + "qenv_fix_v.npy")
KK = 1e5; hK = KK ** (-2.0 / 3.0)
xK = np.arange(len(wK)) * hK

def ramp(s):
    return np.where(s <= -0.1, 0.0, np.where(s < 0.1, (s + 0.1) ** 2 / 0.4, s))
g = np.minimum(1.0, 0.04 + 0.12 * ramp(xK - 1.0))
nodes = (1 - g) * wK
assert np.array_equal(np.minimum.accumulate(nodes), nodes), "누적 최솟값이 표를 바꿈"
sec = np.diff(nodes) / hK
assert np.all(sec < 0)
sl = np.empty_like(nodes)
sl[1:-1] = 2 * sec[:-1] * sec[1:] / (sec[:-1] + sec[1:])       # 이웃한 두 할선 기울기의 조화평균
e0 = 1.5 * sec[0] - 0.5 * sec[1]; e1 = 1.5 * sec[-1] - 0.5 * sec[-2]
sl[0] = e0 if e0 < 0 else 0.0; sl[-1] = e1 if e1 < 0 else 0.0
def Omega(x):
    x = np.asarray(x, dtype=float)
    i = np.clip(np.floor(x / hK).astype(int), 0, len(nodes) - 2)
    t = (x - xK[i]) / hK
    h00 = 2 * t ** 3 - 3 * t ** 2 + 1; h10 = t ** 3 - 2 * t ** 2 + t; h01 = -2 * t ** 3 + 3 * t ** 2; h11 = t ** 3 - t ** 2
    return h00 * nodes[i] + h10 * hK * sl[i] + h01 * nodes[i + 1] + h11 * hK * sl[i + 1]
def That(x):
    return np.interp(np.asarray(x, dtype=float), 0.0005 * np.arange(len(zT)), zT)
print("Omega(0,0.5,1,2,3,4,6) =", np.round(Omega([0, 0.5, 1, 2, 3, 4, 6]), 4), " (부록 D: 0.96, 0.731, 0.455, 0.123, 0.038, 0.014, 0.002)")
print("max|Omega'| at nodes =", round(float(np.max(np.abs(sl))), 4), "(본문: <=0.5851)")
xs = np.linspace(0, 6, 600001); om = Omega(xs)
print("int_0^6 Omega sqrt(2x/pi) dx ~", round(float(np.sum(om * np.sqrt(2 * xs / pi)) * (xs[1] - xs[0])), 4), "(본문: 약 0.744)")

MAXM = 1_100_000
lB = np.array([-m + (m - 1) * log(m) - lgamma(m + 1) for m in range(1, MAXM + 1)])
Bor = np.exp(lB)                     # Bor[m-1]
BorLe = np.concatenate([[0.0], np.cumsum(Bor)])                     # BorLe[q] = sum_{m<=q}
Psi = np.concatenate([[0.0], np.cumsum(np.arange(1, MAXM + 1) * Bor)])  # Psi[q]

def qmax_of(k):
    q = int(round(6 * k ** (2 / 3)))
    while (q + 1) ** 3 <= 216 * k * k: q += 1
    while q ** 3 > 216 * k * k: q -= 1
    return q
def hfun(k, nu): return k / (k + nu) - k / (2 * k - 1)

def LB(k, nu, verbose=False):
    n = 2 * k + nu; N = n - k
    qmax = qmax_of(k)
    qfb = (3 * (k - 1) - 4 * qmax - 12) // 32            # floor((3(k-1)/4 - qmax - 3)/8)
    assert qfb == floor((3 * (k - 1) / 4 - qmax - 3) / 8)
    if nu >= qmax + 1: case = 1; qw = qmax; qws = 6 * k ** (2 / 3)
    elif nu - 1 >= k / 4: case = 2; qw = nu - 1; qws = nu - 1
    else: case = 3; qw = qmax; qws = None
    def Rlow(kk, nn):
        q = np.arange(1, qw + 1)
        xi = (q - 1) / kk ** (2 / 3)
        assert xi[-1] <= 6.0 + 1e-12
        return float(np.sum((1 - q * nn / (kk * (kk + nn))) ** 1.5 * (kk / (kk + q)) * (That(xi) + Psi[q - 1] * Omega(xi)))) / kk
    def fb(lam): return sum((lam * BorLe[qfb]) ** i for i in range(8))
    c0 = max((1 - 1 / k) ** (N - k + 1), 1 - exp(7 / 6) * N ** 1.5 / (4 / sqrt(2 * pi) * k * (2 * k - 1 - N)))
    LOWk = LOWk1 = 0.0
    if case in (1, 2):
        inf = float("inf")
        if nu >= qfb + 2:
            La = k / (n - k) - k / (2 * k + 2) * exp(-hfun(k, nu))
            Lc = k / (k + qfb + 1) - 0.5 if qfb >= qw else inf
            Lap = (k - 1) / (k + nu + 1) - (k - 1) / (2 * k) * exp(-hfun(k - 1, nu + 2))
            Lcp = (k - 1) / (k + qfb + 1) - 0.5 if qfb >= qw else inf
        else:
            La = k / (n - k) - max(0.5, k / (n - qfb)); Lc = inf
            Lap = (k - 1) / (k + nu + 1) - max(0.5, (k - 1) / (n - qfb)); Lcp = inf
        for i in range(8):
            Li = k / (k + qws + 1) - k / (2 * k + 2 - (i + 1) * qfb)
            Lip = (k - 1) / (k + qws) - (k - 1) / (2 * k + 2 - (i + 1) * qfb)
            LOWk += (k / n * BorLe[qfb]) ** i * 0.5 * max(0.0, min(La, Lc, Li))
            LOWk1 += ((k - 1) / n * BorLe[qfb]) ** i * 0.5 * max(0.0, min(Lap, Lcp, Lip))
    Rk = Rlow(k, nu); Rk1 = Rlow(k - 1, nu + 2)
    val = BorLe[nu - 1] * exp(-1 / (12 * (n + 1))) * (k / n) * (exp(-5 / (12 * k)) * Rk * fb(k / n) + LOWk + c0 * (exp(-5 / (12 * (k - 1))) * Rk1 * fb((k - 1) / n) + LOWk1))
    if verbose:
        print(f"   k={k} nu={nu} case={case} qmax={qmax} qfb={qfb} qw={qw} Rlow_k={Rk:.5f} Rlow_k-1={Rk1:.5f} fb={fb(k/n):.4f} c0={c0:.5f} LOW_k={LOWk:.5f} LOW_k-1={LOWk1:.5f} -> LB^low={val:.5f}")
    return val, case

pts = [(6668, 103), (6668, 500), (6668, 1667), (6668, 1668), (6668, 1669), (6668, 2125), (6668, 2126), (6668, 2600), (6668, 3200),
       (6800, 3264), (6935, 3328), (6935, 3280), (9000, 2251), (9000, 2596), (9000, 2597), (9000, 4320), (13000, 3251), (13000, 3317), (13000, 3318), (13000, 6240),
       (13823, 3457), (20000, 103), (20000, 9600), (100000, 103), (100000, 12926), (100000, 48000), (1000000, 103), (1000000, 60000), (1000000, 86251), (1000000, 480000)]
print("== (8.23) 점값")
for k, nu in pts:
    LB(k, nu, verbose=True)
print("== k=6668..6935 격자에서 nu 전체 훑기(간격 1)의 최솟값")
for k in (6668, 6700, 6800, 6935):
    best = (9e9, None)
    for nu in range(103, int(floor(0.48 * k)) + 1, 1 if k == 6668 else 7):
        v, c = LB(k, nu)
        if v < best[0]: best = (v, nu, c)
    print(f"   k={k}: min LB^low = {best[0]:.5f} at nu={best[1]} (case {best[2]})")

# (8.21): R_q = k c_{k+q}(k) >= Psi(q) Omega(xi_q), 재귀 (8.4)를 배정밀도로 풀어 대조. s_{k+j-1}(k+1)는 정리 2:old-2-13(나)의 재귀.
def window_check(k):
    qm = qmax_of(k)
    y = k + 1
    # s_n(k+1) for n <= k+qm
    s = np.ones(k + qm + 1)
    for nn in range(y + 1, k + qm + 1):
        m = np.arange(y + 1, nn + 1)
        pin = np.exp(lB[m - 1] + lB[nn - m] - lB[nn])
        s[nn] = 1 - pin.sum() + (pin * (y / m) * s[m - 1]).sum()
    R = np.zeros(qm + 1)
    for q in range(1, qm + 1):
        j = np.arange(1, q + 1)
        pin = np.exp(lB[k + j - 1] + lB[q - j] - lB[k + q])      # pi_{k+q}(k+j)=Bor(k+j)Bor(q+1-j)/Bor(k+q+1)
        R[q] = float(np.sum(pin * (k / (k + j)) * (s[k + j - 1] + R[j - 1])))
    q = np.arange(1, qm + 1)
    ratio = R[1:] / (Psi[q] * Omega(q / k ** (2 / 3)))
    i = int(np.argmin(ratio))
    tmin = float(np.min(s[k + 2:k + qm + 1] - That(np.arange(2, qm + 1) / k ** (2 / 3))))
    print(f"   k={k}: min_q R_q/(Psi(q)Omega(xi_q)) = {ratio[i]:.5f} at q={i+1}; min_q [s_(k+q)(k+1) - That(xi_q)] = {tmin:.3e}; (1/k)sum Psi*Omega = {float(np.sum(Psi[q]*Omega(q/k**(2/3))))/k:.4f}; (1/k) sum R_q = {R[1:].sum()/k:.4f}")
print("== (8.21)과 보조정리 8:table-tolerance의 대조")
for k in (6600, 6668, 20000):
    window_check(k)
