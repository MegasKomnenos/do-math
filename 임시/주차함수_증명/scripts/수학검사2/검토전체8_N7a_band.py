# 검토전체8 N7a: 7.4절 중앙 띠의 수치 검산
# (1) 명제 pair-check-10000: k=10000, q+q'+j<=50 (q<=q') 경우 수와 (7.11) 우변의 최솟값
# (2) 명제 pair-reach-table (가): 다섯 꼬리 삼중에서 (7.12) F_C(q)>=0 (2<=q<=M)
# (3) 명제 pair-reach-table (나): 열한 K_1에서 nu_P(K_1)
# (4) 명제 integer-strips 비교 수, 기타 산술 상수
from fractions import Fraction as Fr
from mpmath import mp, mpf, exp, sqrt, factorial, log, pi, e as E
import numpy as np

mp.dps = 40

def section(t):
    print("\n==== " + t)

# ---------- (1) pair-check-10000 ----------
section("(1) pair-check-10000: k=10000, q+q'+j<=50")
k = 10000
def pi_sharp(q, k):
    return Fr(q * (q - 1), 2 * (k + 1))
def exbar(q, k):
    ps = pi_sharp(q, k)
    return q + (k + q) * ps / (1 - ps)
cnt = 0
mn = None; arg = None
for q in range(1, 49):
    for qp in range(q, 50 - q):
        for j in range(0, 51 - q - qp):
            cnt += 1
            r = 1 - Fr(j, k) * (exbar(q, k) + exbar(qp, k)) - (exbar(q, k) * (qp - 1) + exbar(qp, k) * (q - 1)) / (2 * k)
            if mn is None or r < mn:
                mn = r; arg = (q, qp, j)
print("count(q<=q') =", cnt, " min =", float(mn), " at", arg, " (본문: 10,725 / 0.04926 / (1,33,16))")
# 순서쌍 수
cnt2 = sum(1 for q in range(1, 49) for qp in range(1, 50 - q) for j in range(0, 51 - q - qp))
print("count ordered =", cnt2, " (부록 D: 20,825)")

# ---------- (2) 꼬리 삼중 (7.12) ----------
section("(2) 꼬리 삼중 (7.12)")
def Bor(m):
    return exp(-m) * mpf(m) ** (m - 1) / factorial(m)
def kebar(K1, M):
    K1 = mpf(K1); M = mpf(M)
    return 3 * (M - 1) / (2 * (K1 + 1)) + (M - 1) * (3 * M - 4) / (12 * (K1 + 1) ** 2) \
        + (M - 1) ** 2 / (2 * (K1 + 1) * (K1 + 2 - M)) + (M - 1) ** 4 / (12 * (K1 + 1) ** 2 * (K1 + 2 - M))
triples = [(10**4, 120, '0.54'), (2 * 10**4, 250, '0.593'), (10**5, 300, '0.522'), (10**5, 450, '0.548'), (10**6, 700, '0.519')]
for K1, M, Cs in triples:
    C = mpf(Cs)
    kb = kebar(K1, M)
    ek = exp(kb)
    bors = [Bor(s + 1) for s in range(0, M)]
    worst = None
    for q in range(2, M + 1):
        s_ = sum(bors[s] * ((q - 1 - s) + C * mpf(q - 1 - s) ** mpf('1.5')) for s in range(0, q - 1))
        F = C * mpf(q) ** mpf('1.5') - ek * s_
        rel = F / (C * mpf(q) ** mpf('1.5'))
        if worst is None or rel < worst[0]:
            worst = (rel, q)
    print(f"K1={K1} M={M} C={Cs}: kebar={float(kb):.4f}  min rel margin={float(worst[0]):.3e} at q={worst[1]}  C*M^1.5={float(C*mpf(M)**1.5):.0f}")
print("부록 D: 1.98e-4, 1.00e-4, 8.69e-5, 2.05e-6, 8.27e-5 (모두 q=M); kebar 0.0180, 0.0188, 0.0045, 0.0068, 0.0010; C M^1.5 최대 9612, 다음 5231")

# ---------- (3) nu_P(K_1) ----------
section("(3) nu_P(K_1): 껍질 nu의 최악 lb (j=nu-q-q')")
cols = [(12000, 120, 0.54), (13000, 120, 0.54), (14000, 120, 0.54), (15000, 120, 0.54), (2 * 10**4, 120, 0.54),
        (3 * 10**4, 250, 0.593), (5 * 10**4, 250, 0.593), (10**5, 300, 0.522), (2 * 10**5, 450, 0.548), (5 * 10**5, 450, 0.548), (10**6, 700, 0.519)]
expected = [93, 96, 99, 102, 115, 132, 164, 228, 298, 435, 590]
for (K1, M, C), ex in zip(cols, expected):
    qs = np.arange(1, M + 1, dtype=np.float64)
    nhat = C * qs ** 1.5 / K1
    nhat[0] = 0.0
    exhat = qs + (K1 + qs) * nhat / (1 - nhat)
    nuP = None; last_ok = None; first_bad = None
    for nu in range(2, M + 2):
        # q,q' >= 1, q+q' <= nu, q,q' <= M
        qmax = min(M, nu - 1)
        Q = np.arange(1, qmax + 1)
        A, B = np.meshgrid(Q, Q, indexing='ij')
        mask = (A + B) <= nu
        J = nu - A - B
        lb = 1 - J / K1 * (exhat[A - 1] + exhat[B - 1]) - (exhat[A - 1] * (B - 1) + exhat[B - 1] * (A - 1)) / (2 * K1)
        lbm = lb[mask]
        mnv = lbm.min()
        if mnv > 0:
            last_ok = (nu, mnv, (A[mask][lbm.argmin()], B[mask][lbm.argmin()], J[mask][lbm.argmin()]))
        else:
            first_bad = (nu, mnv)
            break
    print(f"K1={K1} (M={M},C={C}): nu_P={last_ok[0]} (본문 {ex}), worst lb={last_ok[1]:.4f} at {last_ok[2]}, next shell min={first_bad[1]:.4f}")

# ---------- (4) 기타 ----------
section("(4) integer-strips 비교 수")
cnt_a = sum(2 * k + 40 - max(20001, 2 * k + 1) + 1 for k in range(9981, 11100))
cnt_b = sum(2 * k + 102 - max(2 * k + 41, 20001) + 1 for k in range(9950, 12000))
cnt_c = 1000 * (102 - 59 + 1) + 1000 * (102 - 80 + 1) + 1000 * (102 - 96 + 1)
print("(가)", cnt_a, "(본문 44,380); (나)+(다)", cnt_b + cnt_c, "(본문 200,170)")

section("(5) 기타 상수")
print("2002^(4/3) =", float(mpf(2002) ** (mpf(4) / 3)), " ceil -> 25233?")
print("0.3^1.5/2 =", float(mpf('0.3') ** 1.5 / 2))
print("0.7*2001/2002 =", float(mpf('0.7') * 2001 / 2002))
print("2 e^{-5.3146*0.6996} =", float(2 * exp(-mpf('5.3146') * mpf('0.6996'))))
print("0.0821 e^{-3/25233} =", float(mpf('0.0821') * exp(-mpf(3) / 25233)))
print("needed varsigma: -ln(0.0820/2)/0.6996 =", float(-log(mpf('0.0820') / 2) / mpf('0.6996')))
print("2e7*3.07/9^4 =", float(2e7 * 3.07 / 9**4), " (<9400?)")
print("1/(9*10^4) =", 1 / 90000, " (<=1.12e-5?)")
print("(1.5+1/(2e4))^1.5 * e^{1/(24e4)} =", float((mpf(1.5) + mpf(1) / 20000) ** 1.5 * exp(mpf(1) / 240000)), " (<1.84)")
print("1.84*2/sqrt(pi) =", float(mpf('1.84') * 2 / sqrt(pi)), " (<2.08)")
print("2.08/sqrt(2pi) =", float(mpf('2.08') / sqrt(2 * pi)), " (<0.83)")
print("(n+1)/(2k)/128 at k=1e4, nu=600 =", (2e4 + 601) / 2e4 / 128)
print("841^1.5 =", float(mpf(841) ** 1.5), " 20507/841^1.5 =", float(20507 / mpf(841) ** 1.5), " 73032/2000^1.5 =", float(73032 / mpf(2000) ** 1.5))
print("x_k lower: e^{-1} =", float(exp(-1)))
# analytic-transfer (가) 값의 차분
vals = [0.2048, 0.1938, 0.1827, 0.1717, 0.1607, 0.1496, 0.1386, 0.1275, 0.1165, 0.1054, 0.0944, 0.0833, 0.0723, 0.0613, 0.0502, 0.0392, 0.0281, 0.0170, 0.0060]
print("analytic-transfer (가) 이웃 차:", [round(vals[i] - vals[i + 1], 4) for i in range(18)])
# hermite-nu (다) 계수 모음
nu = 0
print("23.75+2.5nu 분해: (nu+4)/2 + (3+nu) + 3/4 + 1.5 + 10 + (26+4nu)/4 =", (nu + 4) / 2 + (3 + nu) + 0.75 + 1.5 + 10 + (26 + 4 * nu) / 4, "at nu=0 (본문 23.75); nu 계수 1/2+1+1 =", 0.5 + 1 + 1)
