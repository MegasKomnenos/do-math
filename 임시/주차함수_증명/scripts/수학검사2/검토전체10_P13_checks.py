# 검토전체10 P13 — 부록 D 장7A·7B·9 항목의 수치를 다시 세는 검산 스크립트.
# 실행: python -I 검토전체10_P13_checks.py   (작업 디렉토리 무관; 파일을 읽지 않는다)
# 모든 수는 본문 식에서 직접 계산하며, 기록이나 재계산 자료를 읽지 않는다.
from fractions import Fraction
from math import ceil, exp, lgamma, log

print("== D.column-certification-k500 ==")
L = 10**21 * 400**10
R = 17**21 * 123**10
print("10^21*400^10 = %.6e, 17^21*123^10 = %.6e, L>R: %s" % (L, R, L > R))
for lo, hi, name in ((121, 160, "첫째 작성자"), (161, 500, "둘째 작성자")):
    dd = rr = 0
    for k in range(lo, hi + 1):
        B = -(-k * k // 4)
        dd += 2 * B - 2 * k      # 2k+1 <= n <= 2B
        rr += B + 1              # B <= n <= 2B
    print("%s: 직접 차분 %d, 비 비교 %d" % (name, dd, rr))

print("== D.self-consistent-constants (mpmath 60자리) ==")
try:
    from mpmath import mp, mpf, e as mpe, exp as mexp, log as mlog, loggamma, ceil as mceil

    mp.dps = 60

    def ac(m):
        m = mpf(m)
        return mpf(1) if m == 0 else mexp((m - 1) * mlog(m + 1) - loggamma(m + 1))

    def run(Ls, J, k0, y):
        Lf = mpf(Fraction(Ls).numerator) / Fraction(Ls).denominator
        m = 0
        while ac(m + 1) / ac(m) < Lf:
            m += 1
        js = m - 1
        kR = max(2 * js + 2, int(mceil(Lf ** (js + 2) / ac(js + 1))))
        EJ = sum(ac(J + i) / ac(J) * mexp(-i) for i in range(1, k0 - js + 1))
        Ei = (Lf / mpe) * (1 - (Lf / mpe) ** k0) / (1 - Lf / mpe)
        RJ = max(1 / (1 + EJ), 1 / (1 + Ei))
        xk = (mpf(k0) / (k0 + 1)) ** (k0 - 1)
        Xi = Xik = mpf(0)
        for kap in range(J):
            xb = ac(kap) * Lf ** (-(kap + 1))
            q = max(mpf(0), 1 - sum(ac(j) * Lf ** (-(j + 1)) for j in range(kap)))
            Xi += max(mpf(0), xb - RJ * q)
            Xik += max(mpf(0), ac(kap) * xk * Lf ** (-kap) - RJ * q)
        A0 = xk + Xik / (Lf * (1 - Xi))
        B0 = RJ * (1 + Xik / (1 - Xi))
        xi = mpf(1) / k0
        yy = mpf(Fraction(y).numerator) / Fraction(y).denominator
        val = (yy - xi) * (yy - 2 * xi - xi**2) - (1 + xi) ** 2 * (A0 * xi + B0 * yy)
        vert = (3 * xi + xi**2) / 2 + (1 + xi) ** 2 * B0 / 2
        print(Ls, "j*", js, "k_R", kR, "R_J", mp.nstr(RJ, 10), "Xi", mp.nstr(Xi, 8),
              "Xi^(k0)", mp.nstr(Xik, 8), "A0", mp.nstr(A0, 7), "B0", mp.nstr(B0, 7),
              "값", mp.nstr(val, 5), "꼭짓점/k^2", mp.nstr(vert, 5))

    run("267/100", 25, 501, "13/100")
    run("27/10", 70, 1855, "2/25")
    run("271/100", 100, 6098, "11/200")
except ImportError:
    print("mpmath 없음: 건너뜀")

print("== D.band102-integer (ㄱ) 경우 수와 최솟값 ==")
k = 10000
def exbar(q):
    p = q * (q - 1) / (2 * (k + 1))
    return q + (k + q) * p / (1 - p)
cnt_unord = cnt_ord = 0
best = (9.0, None)
for q in range(1, 50):
    for qp in range(1, 50):
        for j in range(0, 51 - q - qp):
            cnt_ord += 1
            if q <= qp:
                cnt_unord += 1
                v = 1 - j / k * (exbar(q) + exbar(qp)) - (exbar(q) * (qp - 1) + exbar(qp) * (q - 1)) / (2 * k)
                if v < best[0]:
                    best = (v, (q, qp, j))
print("순서 없는 쌍", cnt_unord, "순서쌍", cnt_ord, "최솟값 %.5f at %s" % best)

print("== D.band102-integer (ㄴ) 꼬리 삼중 ==")
def Bor(m):
    return exp(-m + (m - 1) * log(m) - lgamma(m + 1))
def kebar(K1, M):
    return (3 * (M - 1) / (2 * (K1 + 1)) + (M - 1) * (3 * M - 4) / (12 * (K1 + 1) ** 2)
            + (M - 1) ** 2 / (2 * (K1 + 1) * (K1 + 2 - M)) + (M - 1) ** 4 / (12 * (K1 + 1) ** 2 * (K1 + 2 - M)))
for (K1, M, tf) in [(10**4, 120, 0.54), (2 * 10**4, 250, 0.593), (10**5, 300, 0.522), (10**5, 450, 0.548), (10**6, 700, 0.519)]:
    kb = kebar(K1, M)
    mn = (9.0, None)
    for q in range(2, M + 1):
        F = tf * q**1.5 - exp(kb) * sum(Bor(s + 1) * ((q - 1 - s) + tf * (q - 1 - s) ** 1.5) for s in range(0, q - 1))
        r = F / (tf * q**1.5)
        if r < mn[0]:
            mn = (r, q)
    print((K1, M, tf), "ke상한 %.4f" % kb, "최소 상대 여유 %.3e (q=%d)" % mn)

print("== D.band102-integer (ㄷ) 쌍별로 닿은 껍질 (배정밀도) ==")
rows = [(12000, 120, 0.54), (13000, 120, 0.54), (14000, 120, 0.54), (15000, 120, 0.54), (20000, 120, 0.54),
        (30000, 250, 0.593), (50000, 250, 0.593), (100000, 300, 0.522), (200000, 450, 0.548),
        (500000, 450, 0.548), (1000000, 700, 0.519)]
for (K1, M, tf) in rows:
    kk = K1
    ex = [None] + [(q + (kk + q) * (tf * q**1.5 / kk) / (1 - tf * q**1.5 / kk) if q > 1 else 1.0) for q in range(1, M + 1)]
    def lb(q, qp, j):
        return 1 - j / kk * (ex[q] + ex[qp]) - (ex[q] * (qp - 1) + ex[qp] * (q - 1)) / (2 * kk)
    nuP = worst = nxt = None
    for nu in range(2, M + 2):
        mn = (9.0, None)
        for q in range(1, nu):
            for qq in range(q, nu - q + 1):
                if qq > M:
                    continue
                v = lb(q, qq, nu - q - qq)
                if v < mn[0]:
                    mn = (v, (q, qq, nu - q - qq))
        if mn[0] <= 0:
            nuP, nxt = nu - 1, mn
            break
        worst = mn
    print("K1", K1, "nu_P", nuP, "껍질 nu_P 최악 %.4f %s" % worst, "껍질 nu_P+1 최솟값 %.4f" % nxt[0])

print("== D.band102-integer (ㄹ) 감사 횟수, (ㅁ) 비교 수 ==")
numax = [58, 79, 99, 102, 115, 132, 164, 228, 298, 435, 590]
print("감사 횟수", sum(v + 1 - 41 + 1 for v in numax))
def strip(klo, khi, nulo_fn, nuhi):
    cols = comps = 0
    for kq in range(klo, khi + 1):
        lo = nulo_fn(kq)
        if lo <= nuhi:
            cols += 1
            comps += nuhi - lo + 1
    return cols, comps
print("실행 2 (ν 1..40, n>=20001):", strip(9981, 11099, lambda kq: max(1, 20001 - 2 * kq), 40))
print("실행 3:", strip(9972, 11999, lambda kq: max(41, 20001 - 2 * kq), 58))
print("실행 4:", strip(9950, 11999, lambda kq: max(59, 20001 - 2 * kq), 102))
print("실행 5:", strip(12000, 12999, lambda kq: 59, 102), "실행 6:", strip(13000, 13999, lambda kq: 80, 102),
      "실행 7:", strip(14000, 14999, lambda kq: 96, 102))

print("== D.moment-certification 위치 수 (첫째 범위) ==")
print(sum((13 * kq * kq) // 100 - 2 * kq for kq in range(501, 841)))

print("== D.m1-column-reading 세 총수 (정확한 정수 바닥) ==")
tot = 0
for n in range(5, 20001):
    lo = -(-(n - 1) // 2)
    tot += max(0, n - 3 - lo + 1)
print("위치 수", tot)
def fl(num, den, kq):  # floor((num/den) k^(2/3)) 정확히
    q = int((num / den) * kq ** (2 / 3)) + 2
    while (den * q) ** 3 > num**3 * kq * kq:
        q -= 1
    return q
s75 = s1 = 0
for kq in range(3132, 19404):
    hi = min(2 * kq - 1, 20000)
    s75 += max(0, hi - (kq + fl(3, 4, kq)) + 1)
    s1 += max(0, hi - (kq + fl(1, 1, kq)) + 1)
print("쌍 수 0.75:", s75, " 1.0:", s1)
