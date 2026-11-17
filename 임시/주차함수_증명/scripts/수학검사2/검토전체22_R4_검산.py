# 검토전체22 R4: 장5B 진술의 수치 검산(binary64; 항등식·부등식의 형태 확인용)
#  (1) 보조정리 5:old-5-19 (열 재귀), Abel 재배열 식
#  (2) 명제 5:old-5-22 와 (5.1) (작은 n; IH는 수치로 확인)
#  (3) 정리 5:old-5-33 (Y=300,400; 범위 조건만 맞춘 작은 Y)
#  (4) 보조정리 5:landing-mass 의 착지 질량 (Y=25000, 30000)
import sys, io, math
import numpy as np
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

NMAX = 70000
m_arr = np.arange(0, NMAX + 2, dtype=np.float64)
lgam = np.array([math.lgamma(i + 1.0) for i in range(NMAX + 2)])
logBor = np.full(NMAX + 2, -np.inf)
logBor[1:] = -m_arr[1:] + (m_arr[1:] - 1.0) * np.log(m_arr[1:]) - lgam[1:]


def pi_n(n, t):
    # 가장 큰 나무 핵 pi_n(t) = Bor(t)Bor(n+1-t)/Bor(n+1), t 는 배열 가능
    t = np.asarray(t)
    return np.exp(logBor[t] + logBor[n + 1 - t] - logBor[n + 1])


def survival(y, N):
    # s_n(y), n=0..N (N<=2y+1): 정리 2:old-2-13(나)
    assert N <= 2 * y + 1
    s = np.ones(N + 1)
    for n in range(y + 1, N + 1):
        t = np.arange(y + 1, n + 1)
        p = pi_n(n, t)
        s[n] = (1.0 - p.sum()) + np.dot(p, (y / t) * s[t - 1])
    return s


def mfrak(n):
    # 꼬리 칸 수 m(n) = max({170} U {m>=171: m^1.5+9m<=n})
    best = 170
    m = 171
    while m ** 1.5 + 9 * m <= n:
        best = m
        m += 1
    return best


def t0(y):
    m = y + 1
    while not (m - y >= mfrak(m) + 1):
        m += 1
    return 1 + m


print("== (1)(2) 열 재귀, Abel 환원, (5.1)")
for (n, ys) in [(600, [301, 320, 360, 400, 420]), (900, [451, 500, 600, 700])]:
    for y in ys:
        sm = survival(y - 1, n)   # s_m(y-1)
        s0 = survival(y, n)       # s_m(y)
        sp = survival(y + 1, n)   # s_m(y+1)
        c_y = sp - s0             # c_m(y)
        c_y1 = s0 - sm            # c_m(y-1)
        lhs = c_y[n] - c_y1[n]
        # 나무 곡률 x_t(y), t=y..n
        x = np.zeros(n + 1)
        x[y] = -1.0 / y
        for t in range(y + 1, n + 1):
            x[t] = ((y + 1) * c_y[t - 1] - (y - 1) * c_y1[t - 1]) / t
        ts = np.arange(y, n + 1)
        pis = np.zeros(n + 1)
        pis[y:] = pi_n(n, ts)
        col = float(np.dot(pis[y:], x[y:]))
        P = x[y:].sum()
        tail = np.zeros(n + 1)   # tail_s = sum_{t=s+1}^n x_t
        for s in range(n - 1, y - 1, -1):
            tail[s] = tail[s + 1] + x[s + 1]
        abel = pis[y] * P + sum((pis[s + 1] - pis[s]) * tail[s] for s in range(y, n))
        T0 = t0(y)
        ok_range = (y + 2 <= T0 <= n)
        ih = all(c_y[m] >= c_y1[m] for m in range(T0 - 1, n)) if ok_range else None
        msg = "n=%d y=%d: 차분=%.6e 열재귀=%.6e Abel=%.6e t0=%d" % (n, y, lhs, col, abel, T0)
        if ok_range:
            WIN0 = sum((pis[t] - pis[y]) * max(-x[t], 0.0) for t in range(y + 1, T0))
            POS0 = sum((pis[m + 1] - pis[T0 - 1]) * (c_y[m] + c_y1[m]) / (m + 1) for m in range(T0 - 1, n))
            rhs22 = pis[y] * P - WIN0 + POS0
            top = y * (y - 1) * c_y1[n - 1] / n
            rhs51 = POS0 - WIN0 - pis[y] / y * (1 + top)
            corL = (P >= -(1 + top) / y)
            # 보조정리 5:old-5-25
            theta = [math.exp(math.log(t - y) + logBor[t - y] + logBor[y] - logBor[t]) for t in range(y + 1, T0)]
            WINV = sum((pis[t] - pis[y]) * th for t, th in zip(range(y + 1, T0), theta)) / y
            msg += " IH=%s 명제22우변=%.6e(%s) (5.1)우변=%.6e(%s) corL=%s WIN0=%.3e<=WINV=%.3e(%s)" % (
                ih, rhs22, lhs >= rhs22 - 1e-18, rhs51, lhs >= rhs51 - 1e-18, corL, WIN0, WINV, WIN0 <= WINV * (1 + 1e-12))
        print(msg)


def bt_cdf(z, chi):
    # Pr(R_z <= chi-1), R_z = Borel 변수 z개의 합; Bor^{*z}(D) = (z/D) e^{-D} D^{D-z}/(D-z)!
    if z == 0:
        return 1.0
    tot = 0.0
    for Dd in range(z, chi):
        tot += math.exp(math.log(z / Dd) - Dd + (Dd - z) * math.log(Dd) - math.lgamma(Dd - z + 1))
    return tot


def hov(rho, chi):
    return sum(rho ** z * bt_cdf(z, chi) for z in range(0, chi))


def qmax(Y):
    q = int(6 * Y ** (2.0 / 3.0))
    while (q + 1) ** 3 <= 216 * Y * Y:
        q += 1
    while q ** 3 > 216 * Y * Y:
        q -= 1
    return q


print("== (3) 정리 5:old-5-33 (작은 Y에서 부등식 꼴 확인)")
for Y in [300, 400]:
    N = 2 * Y + 1
    sY = survival(Y, N)
    sY1 = survival(Y + 1, N)
    c = sY1 - sY
    Q = qmax(Y)
    Lam = sum(Y / (Y + q + 1.0) * c[Y + q] for q in range(1, Q + 1))
    for chi in [2, 5, 20]:
        worst = None
        for m in range(Y + Q + chi + 1, 2 * Y + 2):
            V = (2 * math.pi) ** -0.5 * ((m + 1.0) / ((Y + 1.0) * (m - Y))) ** 1.5 * math.exp(
                -1.0 / (12 * (m - chi - Y - Q + 1)) - 1.0 / (12 * (Y + 1)))
            bound = hov(Y / (m + 1.0), chi) * V * Lam
            ratio = c[m] / bound
            if worst is None or ratio < worst[0]:
                worst = (ratio, m)
        print("Y=%d qmax=%d Lam=%.5f chi_w=%d: min c_m(Y)/(hov*V*Lam)=%s" % (Y, Q, Lam, chi, worst))

print("== (4) 착지 질량 (보조정리 5:landing-mass)")
for Y in [25000, 30000]:
    Q = qmax(Y)
    N = Y + Q
    # s_n(Y), s_n(Y+1) for n in (Y, Y+Q]
    def surv_window(y):
        s = np.ones(N + 1)
        for n in range(y + 1, N + 1):
            t = np.arange(y + 1, n + 1)
            p = np.exp(logBor[t] + logBor[n + 1 - t] - logBor[n + 1])
            s[n] = (1.0 - p.sum()) + np.dot(p, (y / t) * s[t - 1])
        return s
    sY = surv_window(Y)
    sY1 = surv_window(Y + 1)
    c = sY1 - sY
    Lam = sum(Y / (Y + q + 1.0) * c[Y + q] for q in range(1, Q + 1))
    first = 1 - 2.0 / Y - (1 - (Q + 1.0) / Y) * 1.15 * (Y + Q + 1) / (Q + 1) ** 1.5 - sum(
        min(1.0, 1.15 * (Y + q + 1) / (q + 1) ** 1.5) for q in range(1, Q)) / Y
    viol = max(sY[Y + q] - min(1.0, 1.15 * (Y + q + 1) / (q + 1) ** 1.5) for q in range(1, Q + 1))
    print("Y=%d Q=%d: Lam=%.6f, 첫째 하계=%.6f, 4/5; max(s_{Y+q}(Y)-상계)=%.3e" % (Y, Q, Lam, first, viol))
