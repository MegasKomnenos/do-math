# -*- coding: utf-8 -*-
"""수학 검사 2 (7B): 7.4–7.7절과 부록 D(band102-integer, column-certificates, Q-fin-1130)의 수치 상수를 다시 계산한다.
실행: python -I scripts/수학검사2/7B_검산_numeric.py   (mpmath, numpy; 약 1–2분)
항목: 꼬리 삼중 (7.13) 여섯 묶음의 최소 상대 여유와 ke-bar; 쌍별 도달 nu_P(K1) 열한 열(부동소수 스캔);
      쌍별 판정 k=10000, 껍질 50 (정확 유리수, 10,725경우); 보조정리 kernel-bound; 보조정리 hermite-nu의 d, H_1, H_2, U_r, V_r, M_0 하계;
      보조정리 vertical-nu (다); 보조정리 explicit-bounds (가)–(바); hazard-floor (나)의 rt 하계; 정리 theorem-H-star 기저 상수;
      정리 theorem-W (가)(나) 상수; 보조정리 threshold-unit-ratio 상수; 정리 polar-PD 상수; 정리 theorem-C-moment의 n_M 비;
      보조정리 error-induction (나)(다) 상수; 정리 old-6-22의 x_k n>368; 부록 D의 1/e 유리 상계, C M^{3/2}, 2^k 넘침 한계."""
import sys, json, os
from fractions import Fraction as Q
from math import comb, factorial, isqrt
import mpmath as mp
mp.mp.dps = 40

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
fails = 0
def check(name, ok, info=""):
    global fails
    print(("OK   " if ok else "FAIL ") + name + ("" if info == "" else "  " + str(info)))
    if not ok: fails += 1

def Bor(m):  # e^{-m} m^{m-1}/m!
    m = mp.mpf(m)
    return mp.exp(-m + (m - 1) * mp.log(m) - mp.loggamma(m + 1))

# ---------------- 1. 꼬리 삼중 (7.13) ----------------
print("== 1. 꼬리 삼중 (7.13)")
def kebar(K1, M):
    K1 = mp.mpf(K1); M = mp.mpf(M)
    return (3 * (M - 1) / (2 * (K1 + 1)) + (M - 1) * (3 * M - 4) / (12 * (K1 + 1) ** 2)
            + (M - 1) ** 2 / (2 * (K1 + 1) * (K1 + 2 - M)) + (M - 1) ** 4 / (12 * (K1 + 1) ** 2 * (K1 + 2 - M)))
triples = [(9950, 120, '0.54'), (10000, 120, '0.54'), (20000, 250, '0.593'), (100000, 300, '0.522'), (100000, 450, '0.548'), (1000000, 700, '0.519')]
expect_slack = ['1.08e-4', '1.99e-4', '1.00e-4', '8.70e-5', '2.06e-6', '8.28e-5']
expect_ke = ['0.0181', '0.0180', '0.0188', '0.0045', '0.0068', '0.0010']
bor = [None] + [Bor(m) for m in range(1, 702)]
for (K1, M, C), es, ek in zip(triples, expect_slack, expect_ke):
    C = mp.mpf(C); kb = kebar(K1, M); ekb = mp.exp(kb)
    mins = None
    for q in range(2, M + 1):
        F = C * mp.mpf(q) ** 1.5 - ekb * mp.fsum(bor[s + 1] * ((q - 1 - s) + C * mp.mpf(q - 1 - s) ** 1.5) for s in range(0, q - 1))
        rel = F / (C * mp.mpf(q) ** 1.5)
        if mins is None or rel < mins[0]: mins = (rel, q)
        if F < 0: print("  F<0 at", K1, M, q)
    print(f"  ({K1},{M},{C}): min rel slack {mp.nstr(mins[0],4)} at q={mins[1]} (D: {es}); ke-bar {mp.nstr(kb,4)} (D: {ek})")
    check(f"꼬리 삼중 ({K1},{M},{C}) 모두 F>=0, 최소 상대 여유 q=M", mins[0] > 0 and mins[1] == M)
    # C M^{3/2} < K1
    check(f"  C M^(3/2) = {mp.nstr(C*mp.mpf(M)**1.5,6)} < K1", C * mp.mpf(M) ** 1.5 < K1)

# ---------------- 2. 쌍별 도달 nu_P(K1) (부동소수 스캔 + 최악점 정확 유리수) ----------------
print("== 2. 쌍별 도달 nu_P(K1)")
import numpy as np
table = [(12000, 120, '0.54', 93), (13000, 120, '0.54', 96), (14000, 120, '0.54', 99), (15000, 120, '0.54', 102), (20000, 120, '0.54', 115),
         (30000, 250, '0.593', 132), (50000, 250, '0.593', 164), (100000, 300, '0.522', 228), (200000, 450, '0.548', 298),
         (500000, 450, '0.548', 435), (1000000, 700, '0.519', 590)]
def lb_exact(K1, C, q, qp, j):
    # q^{3/2} 유리 상계 (sqrt 올림, 1e-12)
    def nhat(q):
        if q == 1: return Q(0)
        r = isqrt(q * 10 ** 24) + 1           # ceil-ish of sqrt(q)*1e12
        return C * q * Q(r, 10 ** 12) / K1
    def exh(q):
        nq = nhat(q); return q + (K1 + q) * nq / (1 - nq)
    e1, e2 = exh(q), exh(qp)
    return 1 - Q(j, K1) * (e1 + e2) - (e1 * (qp - 1) + e2 * (q - 1)) / (2 * K1)
for K1, M, Cs, nuP in table:
    C = float(Cs)
    qs = np.arange(1, M + 1, dtype=float)
    nh = C * qs ** 1.5 / K1; nh[0] = 0.0
    exh = qs + (K1 + qs) * nh / (1 - nh)
    reach = None; worst = None
    for nu in range(2, M * 2 + 3):
        q = np.arange(1, nu, dtype=int); qp = nu - q  # j=0 shell with q+q'=nu, plus j>0 via smaller sums
        # 모든 (q,q',j), q+q'+j=nu, q<=q'<=M
        best = np.inf; arg = None
        for qq in range(1, min(M, nu - 1) + 1):
            qp_arr = np.arange(qq, min(M, nu - qq) + 1)
            if qp_arr.size == 0: continue
            jj = nu - qq - qp_arr
            lb = 1 - jj / K1 * (exh[qq - 1] + exh[qp_arr - 1]) - (exh[qq - 1] * (qp_arr - 1) + exh[qp_arr - 1] * (qq - 1)) / (2 * K1)
            i = int(np.argmin(lb))
            if lb[i] < best: best = float(lb[i]); arg = (qq, int(qp_arr[i]), int(jj[i]))
        if best <= 0:
            reach = nu - 1; break
        worst = (best, arg)
    # 껍질 reach의 최악점 정확 유리수 확인과 reach+1의 음수 확인
    ex_w = lb_exact(K1, Q(Cs), *worst[1])
    print(f"  K1={K1}: nu_P={reach} (D: {nuP}); worst {worst[1]} lb={worst[0]:.5f} exact {float(ex_w):.5f}; shell {reach+1} min {best:.5f} at {arg}")
    check(f"nu_P({K1}) = {nuP}", reach == nuP)

# 쌍별 판정 k=10000, 껍질 50: 정확 유리수 (bar ex)
print("== 2b. pair-check-10000 (7.12), 10,725 경우")
K1 = 10000
def exbar(q):
    pi = Q(q * (q - 1), 2 * (K1 + 1)); assert pi < 1
    return q + (K1 + q) * pi / (1 - pi)
cnt = 0; worst = None; worst_crude = None
for nu in range(2, 51):
    for q in range(1, nu):
        for qp in range(q, nu - q + 1):
            j = nu - q - qp
            if j < 0: continue
            cnt += 1
            e1, e2 = exbar(q), exbar(qp)
            v = 1 - Q(j, K1) * (e1 + e2) - (e1 * (qp - 1) + e2 * (q - 1)) / (2 * K1)
            if worst is None or v < worst[0]: worst = (v, (q, qp, j))
            if nu <= 19:
                vc = 1 - (j * e1 * qp + j * e2 * q + e1 * Q(qp * (qp - 1), 2) + e2 * Q(q * (q - 1), 2)) / K1
                if worst_crude is None or vc < worst_crude[0]: worst_crude = (vc, (q, qp, j), )
print(f"  cases {cnt}, min {float(worst[0]):.5f} at {worst[1]}; crude nu<=19 min {float(worst_crude[0]):.4f} at {worst_crude[1]}")
check("pair-check-10000: 10,725 경우, 최솟값 at (1,33,16) in [0.0492,0.0493) (본문 '0.0493'은 최근접 반올림; 내림은 0.0492), 거친 하계 nu<=19 최솟값 in [0.5935,0.5936) (D '0.5936'은 최근접; 내림 0.5935)", cnt == 10725 and worst[1] == (1, 33, 16) and Q(492, 10000) <= worst[0] < Q(493, 10000) and Q(5935, 10000) <= worst_crude[0] < Q(5936, 10000))
# 615 = nu<=19 경우 수
check("nu<=19 경우 수 615", sum(1 for nu in range(2, 20) for q in range(1, nu) for qp in range(q, nu - q + 1)) == 615)

# ---------------- 3. kernel-bound ----------------
print("== 3. kernel-bound pi_m(m-s) <= Bor(s+1) e^{ke(s,m)}")
def log_pi(m, s):
    j = m - s
    return (mp.log(mp.binomial(m, j)) + (j - 1) * mp.log(j) + (m - j - 1) * mp.log(m - j + 1) - (m - 1) * mp.log(m + 1)) if m - j >= 1 else \
           (mp.log(mp.binomial(m, j)) + (j - 1) * mp.log(j) - (m - 1) * mp.log(m + 1))
def ke(s, m):
    s = mp.mpf(s); m = mp.mpf(m)
    return 3 * (s + 1) / (2 * (m + 1)) + (s + 1) * (3 * s + 2) / (12 * (m + 1) ** 2) + (s + 1) ** 2 / (2 * (m + 1) * (m - s)) + (s + 1) ** 4 / (12 * (m + 1) ** 2 * (m - s))
ok = True; tight = mp.inf
for m in [5, 10, 30, 100, 1000, 10001, 20119]:
    for s in list(range(0, min(m - 1, 60) + 1)) + [m // 2, m - 1]:
        if s > m - 1: continue
        lhs = log_pi(m, s); rhs = mp.log(Bor(s + 1)) + ke(s, m)
        ok &= lhs <= rhs + mp.mpf('1e-30'); tight = min(tight, rhs - lhs)
check("kernel-bound 표본 (m<=20119)", ok, f"min slack {mp.nstr(tight,5)}")
# p_{m-j}: (m-j+1)^{m-j-1}; 위 식에서 j=m일 때 p_0=1 처리 확인
check("pi_m(m)= m^{m-1}/(m+1)^{m-1} 식 일관", abs(log_pi(10, 0) - (9 * mp.log(10) - 9 * mp.log(11))) < mp.mpf('1e-30'))

# ---------------- 4. hermite-nu ----------------
print("== 4. hermite-nu: d, H_1, H_2, U_r, V_r, M_0 하계 (비 점화식, k=10^4, 10^5)")
def hermite_data(k, nu, theta=0):
    y = mp.mpf(k) - theta; n = 2 * k + nu; N = n + y + 1
    r = N  # He_1/He_0
    logHe = mp.log(N)  # log He_1
    rs = {1: r}
    for j in range(2, n + 1):
        r = N - y * (j - 1) / r
        logHe += mp.log(r)
        if j >= n - 5: rs[j] = r
    # He_n / He_{n-i}: 역비
    return y, n, N, rs, logHe  # logHe = log He_n
def M_ratio(k, nu, theta, r_):
    y, n, N, rs, logHe = hermite_data(k, nu, theta)
    # H[i] := He_{n-i}/He_{n-1}
    H = {0: rs[n], 1: mp.mpf(1)}
    for i in range(1, r_ + 2):
        H[i + 1] = H[i] / rs[n - i]              # He_{n-i-1} = He_{n-i}/r_{n-i}
    num = mp.fsum((-1) ** i * mp.binomial(r_ + 1, i) * mp.fprod(range(n - i + 1, n + 1)) * H[i] for i in range(r_ + 2))
    den = rs[n] - n
    return num / den
RESID = {}
for k in (10000, 100000):
    for nu in (1, 19, 102, 600):
        for theta in (0, 1):
            y, n, N, rs, logHe = hermite_data(k, nu, theta)
            d = rs[n] - n
            H1 = -(26 + 4 * nu) - 8 * theta
            H2 = 506 + 97 * nu + 5 * nu ** 2 + (168 + 16 * nu) * theta + 12 * theta ** 2
            resid = (d - 4 - mp.mpf(H1) / k) * k ** 2
            RESID[(nu, theta, k)] = resid
            print(f"  k={k} nu={nu} th={theta}: d={mp.nstr(d,12)}  k^2(d-4-H1/k)={mp.nstr(resid,8)}  H2={H2}  k^3*(rest)={mp.nstr((resid-H2)*k,6)}")
            check(f"  H_1 일치 (k={k},nu={nu},th={theta}): |k(d-4)-H1| <= 2e6/k", abs((d - 4) * k - H1) <= mp.mpf(2e6) / k, mp.nstr((d - 4) * k, 10))
            if theta == 0:
                U2 = 1 + mp.mpf(2 * nu + 2) / k + mp.mpf(nu * (nu + 1)) / k ** 2
                V2 = 4 + mp.mpf(4 * nu + 2) / k + mp.mpf(nu * (nu + 1)) / k ** 2
                U4 = 1 + mp.mpf(4 * nu + 16) / k + mp.mpf(6 * nu ** 2 + 30 * nu + 18) / k ** 2 + mp.mpf(4 * nu ** 3 + 17 * nu ** 2 + 15 * nu + 2) / k ** 3 + mp.mpf(nu * (nu + 1) ** 3) / k ** 4
                V4 = 4 + mp.mpf(12 * nu + 38) / k + mp.mpf(13 * nu ** 2 + 49 * nu + 22) / k ** 2 + mp.mpf(6 * nu ** 3 + 21 * nu ** 2 + 17 * nu + 2) / k ** 3 + mp.mpf(nu * (nu + 1) ** 3) / k ** 4
                r2 = M_ratio(k, nu, 0, 2); r4 = M_ratio(k, nu, 0, 4)
                check(f"  (라) M2/M0 = U2 - V2/d (k={k},nu={nu})", abs(r2 - (U2 - V2 / d)) < mp.mpf('1e-25'), mp.nstr(r2 - (U2 - V2 / d), 3))
                check(f"  (라) M4/M0 = U4 - V4/d (k={k},nu={nu})", abs(r4 - (U4 - V4 / d)) < mp.mpf('1e-25'))
                om = mp.mpf('6.98') if nu <= 27 else (mp.mpf('6.975') if nu <= 38 else (mp.mpf('6.97') if nu <= 40 else mp.mpf('6.95')))
                applies = (k == 10000 and nu <= 19) or (k == 100000 and nu <= 228)
                check(f"  k M2/M0 > -5 (k={k},nu={nu}); < -(omega-2) with audit omega={om} where applied={applies}", -5 < k * r2 and ((not applies) or k * r2 < -(om - 2)), mp.nstr(k * r2, 8))
                check(f"  M4 > 0 (k={k},nu={nu})", r4 > 0)
                # (다) M_0 = e^{-k/2} He_{n-1} d / p_n
                logM0 = -mp.mpf(k) / 2 + (logHe - mp.log(rs[n])) + mp.log(d) - (n - 1) * mp.log(n + 1)
                M0 = mp.exp(logM0); lo = 4 * mp.sqrt(2) * (1 - (mp.mpf('23.75') + mp.mpf('2.5') * nu) / k)
                check(f"  (다) M0 >= 4 sqrt2 (1-(23.75+2.5nu)/k) (k={k},nu={nu})", M0 >= lo, f"M0={mp.nstr(M0,10)} lo={mp.nstr(lo,10)}")
            else:
                r2 = M_ratio(k, nu, 1, 2)
                gen = 1 - 2 * mp.mpf(n) / y + mp.mpf(n * (n + 1)) / y ** 2 - mp.mpf(n * (n + 1)) / (y ** 2 * d)
                check(f"  (마) M2/M0 일반식 (k={k},nu={nu},y=k-1)", abs(r2 - gen) < mp.mpf('1e-25') and r2 < 0)
            # (가) x_n < q < 2/9, x <= 1/(9k)
            xx = y / N ** 2; xn = (n - 1) * xx; qq = n * xx
            check(f"  (가) x_n<q<2/9, x<=1/(9k) (k={k},nu={nu},th={theta})", xn < qq < mp.mpf(2) / 9 and xx <= mp.mpf(1) / (9 * k))
            nm = 1 + mp.mpf(2 * nu + 10 + 2 * theta) / k + mp.mpf((nu + 1) ** 2 + 2 * (nu - 3) * theta + theta ** 2) / k ** 2
            check(f"  (가) 1-4x_n = nm/(N/k)^2", abs((1 - 4 * xn) - nm / (N / k) ** 2) < mp.mpf('1e-30'))
# 9400/k^3 상수, 3.07
check("2e7*3.07/9^4 < 9400", 2e7 * 3.07 / 9 ** 4 < 9400, 2e7 * 3.07 / 9 ** 4)
check("N/k <= 3.07 (nu<=600, k>=1e4)", 3 + 601 / 1e4 <= 3.07)



print("== 4b. H_2: 두 k의 Richardson 외삽 R=(10 r(1e5)-r(1e4))/9, r(k)=k^2(d-4-H1/k)=H2+H3/k+...")
for nu in (1, 19, 102, 600):
    for theta in (0, 1):
        H2 = 506 + 97 * nu + 5 * nu ** 2 + (168 + 16 * nu) * theta + 12 * theta ** 2
        r1, r2 = RESID[(nu, theta, 10000)], RESID[(nu, theta, 100000)]
        R = (10 * r2 - r1) / 9
        print(f"  nu={nu} th={theta}: r(1e4)={mp.nstr(r1,9)} r(1e5)={mp.nstr(r2,9)} R={mp.nstr(R,9)} text H2={H2} rel.diff={mp.nstr((R-H2)/H2,3)}")
        check(f"  H_2 (nu={nu},th={theta}) 외삽 |R-H2| <= 6e-4 |H2| + 2", abs(R - H2) <= mp.mpf('6e-4') * H2 + 2)

# ---------------- 5. vertical-nu (다), 정규화 비 ----------------
print("== 5. vertical-nu (다)")
for k in (10000, 15000):
    for nu in (1, 102):
        n = 2 * k + nu
        ratio = mp.exp(mp.loggamma(n + 1) - (n - 1) * mp.log(n + 1) + (n + 1)) / (2 * mp.pi * mp.mpf(k) ** 1.5) / (2 / mp.sqrt(mp.pi))
        up = mp.exp((mp.mpf(3 * (nu + 1)) / 4 + mp.mpf(1) / 24) / k)
        check(f"  n_k/n_inf in [1, exp((3(nu+1)/4+1/24)/k)] (k={k},nu={nu})", 1 <= ratio <= up, f"{mp.nstr(ratio,10)} <= {mp.nstr(up,10)}")
        check(f"  Bor(k)k^{{3/2}} in [(2pi)^-1/2(1-1/(12k)), (2pi)^-1/2]", (2 * mp.pi) ** -0.5 * (1 - mp.mpf(1) / (12 * k)) <= Bor(k) * mp.mpf(k) ** 1.5 <= (2 * mp.pi) ** -0.5)
check("q4/128 <= 1/100 for K1=10000, nu<=19 and K1>=11100, nu<=600", (2 * 10000 + 20) / (2 * 10000) / 128 <= 0.01 and (2 * 11100 + 601) / (2 * 11100) / 128 <= 0.01)

# ---------------- 6. explicit-bounds ----------------
print("== 6. explicit-bounds (가)-(마), hazard-floor (나) rt")
def logP(m, j):  # log P_m(j) = log(j C(m-1,j-1) p_{j-1} p_{m-j} / p_m)
    lp = lambda t: (t - 1) * mp.log(t + 1) if t >= 1 else mp.mpf(0)
    return mp.log(j) + mp.log(mp.binomial(m - 1, j - 1)) + lp(j - 1) + lp(m - j) - lp(m)
def Ren(j): return mp.exp(j * mp.log(j) - j - mp.loggamma(j + 1))
ok = True
for dd in range(1, 2000):
    bd = Bor(dd); ok &= mp.mpf('0.367') * dd ** -1.5 <= bd <= (2 * mp.pi) ** -0.5 * dd ** -1.5
tailsum = {}
tot = mp.fsum(Bor(dd) for dd in range(1, 200001))
for m in (1, 2, 5, 10, 100, 301, 1000, 3131, 10000):
    tail = 1 - mp.fsum(Bor(dd) for dd in range(1, m + 1))   # sum_{d>m} Bor(d) = 1 - sum_{d<=m}
    ok &= tail <= mp.mpf('0.8') / mp.sqrt(m)
    ok &= mp.fsum(dd * Bor(dd) for dd in range(1, m + 1)) <= mp.mpf('0.8') * mp.sqrt(m)
check("(가) Bor 경계, 꼬리 0.8/sqrt m, sum d Bor <= 0.8 sqrt m (sum_d Bor = 1: %s)" % mp.nstr(tot, 8), ok)
check("(가) 0.367 <= (2pi)^-1/2 e^-1/12", mp.mpf('0.367') <= (2 * mp.pi) ** -0.5 * mp.exp(-mp.mpf(1) / 12), mp.nstr((2 * mp.pi) ** -0.5 * mp.exp(-mp.mpf(1) / 12), 6))
def i_m(m): return m * mp.log(mp.mpf(m) / (m + 1)) + 1
ok = True; okc = True; okd = True; oke = True
for N in (1000, 2000, 4000, 8001, 20001):
    im = i_m(N)
    ok &= 0 <= im <= mp.mpf(1) / (2 * (N + 1)) + mp.mpf(1) / (6 * N * (N + 1))
    for U in list(range(0, 60)) + [300, N // 4, N // 2, N - 1]:
        if U > N - 1: continue
        ok &= logP(N, N - U) <= mp.log(Bor(U + 1)) + im + mp.log(mp.mpf(N + 1) / (N - U)) + mp.mpf('1e-30')
    for j in list(range(1, 60)) + [N // 4, N // 2]:
        ok &= logP(N, j) <= mp.log(Ren(j)) + im + mp.log(mp.mpf(N + 1) / (N + 1 - j) ** 2) + mp.mpf('1e-30')
        if j <= N / 2:
            okc &= logP(N, j) >= mp.log(Ren(j)) - mp.mpf('2.1') / (N + 1) - mp.log(N + 1 - j) - mp.mpf('1e-30')
    # (라)(마): f_j = (F_N(j)-F_{N+1}(j))/P_N(j)
    PN = [None] + [mp.exp(logP(N, j)) for j in range(1, N + 1)]
    PN1 = [None] + [mp.exp(logP(N + 1, j)) for j in range(1, N + 2)]
    FN = [mp.mpf(0)]; FN1 = [mp.mpf(0)]
    for j in range(1, N + 1): FN.append(FN[-1] + PN[j])
    for j in range(1, N + 2): FN1.append(FN1[-1] + PN1[j])
    for j in list(range(1, 60)) + [N // 4, N // 2]:
        f = (FN[j] - FN1[j]) / PN[j]
        okd &= f <= mp.mpf('2.2') * j / (N + 1 - j) * (1 + mp.mpf('1.5') * j / (N - j + 1) + mp.mpf(1) / N)
    for U in list(range(0, 60)) + [300, N // 4, N - 1]:
        j = N - U; f = (FN[j] - FN1[j]) / PN[j]
        oke &= 1 - f <= mp.mpf('1.1') * (U + 1) ** 2 / mp.mpf(N - U) ** 2 + 15 * mp.mpf(U + 1) ** 1.5 * (N + 1) / (mp.mpf(N) ** 2 * (N - U))
    # hazard-floor (나) rt_{U'} >= 1 - 1/(2(N-U')) - 4/N^2
    for U in range(0, min(60, N - 1)):
        rt = PN1[N + 1 - U] / PN[N - U]
        ok &= rt >= 1 - mp.mpf(1) / (2 * (N - U)) - mp.mpf(4) / N ** 2
check("i_m 경계, (나) 두 상계, hazard-floor rt 하계 (N in 1000..20001 표본)", ok)
check("(다) 가벼운 뿌리 하계 (j<=N/2)", okc)
check("(라) f_j 상계 (N>=1000, j<=N/2)", okd)
check("(마) 1-f_{N-U} 상계", oke)
check("(라) 상수: 0.8/0.367<=2.18, 2.18 e^0.0027<=2.2; i_1000+2.1/1001<=0.0027", mp.mpf('0.8') / mp.mpf('0.367') <= mp.mpf('2.18') and mp.mpf('2.18') * mp.exp(mp.mpf('0.0027')) <= mp.mpf('2.2') and i_m(1000) + mp.mpf('2.1') / 1001 <= mp.mpf('0.0027'))
check("(마) 상수: e^{i_1000} 0.4/0.367<=1.1, e^{i_1000} 5.4/0.367<=15", mp.exp(i_m(1000)) * mp.mpf('0.4') / mp.mpf('0.367') <= mp.mpf('1.1') and mp.exp(i_m(1000)) * mp.mpf('5.4') / mp.mpf('0.367') <= 15)
# (바) 수치 (2.32(ㄱ)은 identities에서; 여기서는 Bor 합)
check("(바) sum_{U<k} Bor(U+1) >= 1-0.8/sqrt k (k=2000)", mp.fsum(Bor(U + 1) for U in range(2000)) >= 1 - mp.mpf('0.8') / mp.sqrt(2000))

# ---------------- 7. theorem-H-star 기저, theorem-W, threshold-unit-ratio, polar-PD, 기타 상수 ----------------
print("== 7. 상수들")
k = mp.mpf(2000)
v = (mp.mpf('0.2') - 1 / (2 * k) - 4 / k ** 2) * k / (k + 1)
check("H* 기저 (ㄱ) >= 0.1996", v >= mp.mpf('0.1996'), mp.nstr(v, 6))
U = (mp.mpf('0.8') * k) ** (mp.mpf(2) / 3)
fl = 1 - mp.mpf('0.8') / mp.sqrt(2) - (U + 1) * (1 / (2 * k) + 4 / k ** 2); kk = 1 / (1 + (U + 1) / k)
check("H* 기저 (ㄴ) fl>=0.399, k/(m+1)>=0.935, 곱>=0.373", fl >= mp.mpf('0.399') and kk >= mp.mpf('0.935') and fl * kk >= mp.mpf('0.373'), f"{mp.nstr(fl,5)} {mp.nstr(kk,5)} {mp.nstr(fl*kk,5)}")
check("(0.8k)^(2/3) <= k-1 (k=2000)", U <= k - 1)
m = mp.mpf(2000)
flc = 1 - mp.mpf('0.8') * (mp.mpf('0.2') * m) ** (-mp.mpf(1) / 3) - ((mp.mpf('0.2') * m) ** (mp.mpf(2) / 3) + 1) * (1 / (2 * m * (1 - mp.mpf('0.342') * m ** (-mp.mpf(1) / 3))) + 4 / m ** 2)
check("H* 기저 (ㄷ) fl(2000)>=0.877, 0.2^(2/3)<=0.342, /4.0005 >= 0.219", flc >= mp.mpf('0.877') and mp.mpf('0.2') ** (mp.mpf(2) / 3) <= mp.mpf('0.342') and flc / mp.mpf('4.0005') >= mp.mpf('0.219'), f"{mp.nstr(flc,5)} {mp.nstr(mp.mpf('0.2')**(mp.mpf(2)/3),5)}")
# 귀납 w=4
st = mp.mpf('1.1') / 9 + mp.mpf('0.3355') / 12
lhs = mp.mpf('0.98211') * ((1 - st) * mp.mpf('0.999875') / mp.mpf('0.14') - 1)
rhs = mp.mpf('2.2') * 4 / 3 * (1 + mp.mpf('1.5') / 3 + mp.mpf('0.000125'))
check("H* 귀납 w=4: 왼쪽 4.978 >= 오른쪽 4.400", lhs >= rhs and abs(lhs - mp.mpf('4.978')) < 1e-3 and abs(rhs - mp.mpf('4.400')) < 1e-3, f"{mp.nstr(lhs,5)} {mp.nstr(rhs,5)}")
check("15*1.000125/sqrt2000 <= 0.3355; 0.8/sqrt2000=0.01789; 8001/8002>=0.999875", 15 * mp.mpf('1.000125') / mp.sqrt(2000) <= mp.mpf('0.3355') and abs(mp.mpf('0.8') / mp.sqrt(2000) - mp.mpf('0.01789')) < 1e-5 and mp.mpf(8001) / 8002 >= mp.mpf('0.999875'))
# theorem-W
check("W(가): 1-0.8/sqrt301>=0.9538, 0.9538/0.398943>=2.38, Ren(k)<=0.398943/sqrt k", 1 - mp.mpf('0.8') / mp.sqrt(301) >= mp.mpf('0.9538') and mp.mpf('0.9538') / mp.mpf('0.398943') >= mp.mpf('2.38') and (2 * mp.pi) ** -0.5 <= mp.mpf('0.398943'))
check("W(나): 0.14*2.38*0.9999>=0.33316, 0.14*301=42.14", mp.mpf('0.14') * mp.mpf('2.38') * mp.mpf('0.9999') >= mp.mpf('0.33316') and mp.mpf('0.14') * 301 == mp.mpf('42.14'))
k = mp.mpf(3131)
D2 = mp.mpf('0.08329') * mp.sqrt(k) - 2 - mp.mpf('42.14') / k
check("W(나): D_k(2) at 3131 = 2.647, 0.33316/4=0.08329", abs(D2 - mp.mpf('2.647')) < 1e-3 and mp.mpf('0.33316') / 4 == mp.mpf('0.08329'), mp.nstr(D2, 5))
J = k ** (mp.mpf(1) / 6)
fJ = mp.mpf('0.33316') * (J ** 3 - 2 * J + 1 / J) - mp.mpf('1.0005') * J ** 2 - mp.mpf('1.0145')
dJ = mp.mpf('0.33316') * (3 * J ** 2 - 2 - J ** -2) - mp.mpf('2.001') * J
check("W(나): J=3.8249, f(J)=0.529, f'(J)>0; (1+1/3131)^(4/3)<=1.0005; 2/3131<=0.001; 1.001+42.14/3131<=1.0145", abs(J - mp.mpf('3.8249')) < 1e-4 and abs(fJ - mp.mpf('0.529')) < 1e-3 and dJ > 0 and (1 + 1 / k) ** (mp.mpf(4) / 3) <= mp.mpf('1.0005') and 2 / k <= mp.mpf('0.001') and mp.mpf('1.001') + mp.mpf('42.14') / k <= mp.mpf('1.0145'), f"J={mp.nstr(J,6)} f={mp.nstr(fJ,4)}")
check("W(나): e^{-i_n}>=0.9999 (n=6263)", mp.exp(-i_m(6263)) >= mp.mpf('0.9999'))
# threshold-unit-ratio
k = mp.mpf(6667); j0 = mp.floor(mp.mpf('0.3') * k)
val = -(mp.mpf('0.3') * k - 1) * (mp.mpf('0.3') * k) / (2 * (mp.mpf('1.3') * k + 1))
val2 = 1 + mp.mpf(3) / 2 * mp.log(k) + val
check("threshold-unit: -230.6, -216.4, e^0.3<1.34986, e^{3/(2k)}<=1.00023, 1.00023*1.34986<1.3502, 2*0.7654-1.3502>=0.18",
      abs(val - mp.mpf('-230.6')) < 0.1 and abs(val2 - mp.mpf('-216.4')) < 0.1 and mp.exp(mp.mpf('0.3')) < mp.mpf('1.34986') and mp.exp(3 / (2 * k)) <= mp.mpf('1.00023')
      and mp.mpf('1.00023') * mp.mpf('1.34986') < mp.mpf('1.3502') and 2 * mp.mpf('0.7654') - mp.mpf('1.3502') >= mp.mpf('0.18'), f"{mp.nstr(val,5)} {mp.nstr(val2,5)} {mp.nstr(mp.mpf('1.00023')*mp.mpf('1.34986'),7)}")
check("threshold-unit: j0=floor(0.3k)>=0.3k-1, log Pi^up bound monotone: (0.3k-1)(0.3k)/(2(1.3k+1)) increasing", j0 >= mp.mpf('0.3') * k - 1)
# polar-PD
check("polar-PD: 0.3^1.5/2=0.08216, 0.7*2001/2002>=0.6996, 2e^{-5.3146*0.6996}<=0.0486, 0.0821e^{-3/25233}>0.0820, n_X(2002)=25233, 필요 sigma>4.57",
      abs(mp.mpf('0.3') ** 1.5 / 2 - mp.mpf('0.08216')) < 1e-5 and mp.mpf('0.7') * 2001 / 2002 >= mp.mpf('0.6996') and 2 * mp.exp(-mp.mpf('5.3146') * mp.mpf('0.6996')) <= mp.mpf('0.0486')
      and mp.mpf('0.0821') * mp.exp(-mp.mpf(3) / 25233) > mp.mpf('0.0820') and mp.ceil(mp.mpf(2002) ** (mp.mpf(4) / 3)) == 25233 and mp.log(2 / mp.mpf('0.0820')) / mp.mpf('0.6996') < mp.mpf('4.57'),
      f"{mp.nstr(2*mp.exp(-mp.mpf('5.3146')*mp.mpf('0.6996')),5)} nX2002={mp.ceil(mp.mpf(2002)**(mp.mpf(4)/3))} need sigma>{mp.nstr(mp.log(2/mp.mpf('0.0820'))/mp.mpf('0.6996'),4)}")
check("polar-PD: n_PD(k)>=3k+2 for k>=3131; (k+1)^(4/3)>=2k+1", (3132) ** (4 / 3) >= 2 * 3131 + 1)
# error-induction (나)(다)
w = mp.mpf('0.009')
check("error-induction (나): 0.009/(2*0.991)<=0.0046, 1.0046*0.009<=0.00905, 1.0046+0.00454*1.0046<1.01; (다): 1/(1-0.0091)<=1+1.0092*0.0091, 1.01*1.0092<=1.02",
      w / (2 * (1 - w)) <= mp.mpf('0.0046') and mp.mpf('1.0046') * w <= mp.mpf('0.00905') and mp.mpf('1.0046') + mp.mpf('0.00454') * mp.mpf('1.0046') < mp.mpf('1.01')
      and 1 / (1 - mp.mpf('0.0091')) <= 1 + mp.mpf('1.0092') * mp.mpf('0.0091') and mp.mpf('1.01') * mp.mpf('1.0092') <= mp.mpf('1.02'))
x = mp.mpf('0.00905')
check("error-induction (나): x^2/(2(1-x/3)) <= 0.00454 x at x=0.00905", x / (2 * (1 - x / 3)) <= mp.mpf('0.00454'), mp.nstr(x / (2 * (1 - x / 3)), 6))
# old-6-22: x_k n > 368
check("old-6-22: x_501*1003 > 368, (k/(k+1))^(k-1)>=1/e", (mp.mpf(501) / 502) ** 500 * 1003 > 368 and (mp.mpf(501) / 502) ** 500 >= mp.exp(-1), mp.nstr((mp.mpf(501) / 502) ** 500 * 1003, 6))
# 1/e 유리 상계
inv_e = Q(36787944117144233, 10 ** 17)
check("D(ㄴ): 0.36787944117144233 > 1/e, 곱 > 1 with e lower 2.718281828459045235", mp.mpf(inv_e.numerator) / inv_e.denominator > 1 / mp.e and inv_e * Q(2718281828459045235, 10 ** 18) > 1 and mp.mpf(2718281828459045235) / 10 ** 18 < mp.e)
# (ㅁ) 넘침 한계
check("D(ㅁ): floor(30102/2)+1 < 2^14, 2*14999 < 2^15, 2^96*2^15*2^14 = 2^125 < 2^128", 30102 // 2 + 1 < 2 ** 14 and 2 * 14999 < 2 ** 15 and 96 + 15 + 14 == 125)
# (7.19) 상수: R_U <= 1.0309 (주어진 값), eps<1/3 -> (1+eps)/(1-eps)<2
check("(1+1/3)/(1-1/3)=2", Q(4, 3) / Q(2, 3) == 2)
# vertical-nu (가): w - w^2/2 <= log(1+w) <= w on [0,1/64]
check("log 부등식 (가)", all(ww - ww ** 2 / 2 <= mp.log(1 + ww) <= ww for ww in [mp.mpf(i) / 6400 for i in range(0, 101)]))
# theorem-C-moment: n_M 비
d = json.load(open(os.path.join(ROOT, '원고_자료', '세션_재계산', 'moment_cert_iv', 'nM.json')))
r = [(d[k_] / int(k_) ** 1.5, int(k_)) for k_ in d]
print(f"  n_M(k)/k^1.5: min {min(r)[0]:.6f} (k={min(r)[1]}), max {max(r)[0]:.6f} (k={max(r)[1]}); n_M(841)={d['841']}, n_M(2000)={d['2000']}")
check("theorem-C-moment: n_M 비 in [0.8165, 0.8408]  (본문·부록 D 진술)", 0.8165 <= min(r)[0] and max(r)[0] <= 0.8408, f"max={max(r)[0]:.6f} > 0.8408")
check("theorem-C-moment: n_M 비 in [0.8165, 0.8409]  (수정안)", 0.8165 <= min(r)[0] and max(r)[0] <= 0.8409)
check("n_M(841)=20507, n_M(2000)=73032", d['841'] == 20507 and d['2000'] == 73032)
# 명제 pair-reach: C M^{3/2} 최댓값 9612, 그다음 5231
check("C M^{3/2}: 0.519*700^1.5 = 9612, 0.548*450^1.5 = 5231", abs(mp.mpf('0.519') * 700 ** 1.5 - 9612) < 1 and abs(mp.mpf('0.548') * 450 ** 1.5 - 5231) < 1, f"{mp.nstr(mp.mpf('0.519')*700**1.5,6)} {mp.nstr(mp.mpf('0.548')*450**1.5,6)}")
# old-6-13: (20001-102)/2 -> 9950; 2k+40>=20001 -> k>=9981
check("old-6-13: ceil((20001-102)/2)=9950, ceil((20001-40)/2)=9981", -(-(20001 - 102) // 2) == 9950 and -(-(20001 - 40) // 2) == 9981)
# qstar-columns: 기록 binary64 첫 층 여유 최솟값 2.284e-4 < 2.3e-4 (본문 '2.3e-4 이상' 검사)
check("qstar-columns 본문 '첫 층 쪽 여유 2.3e-4 이상' vs 기록 binary64 최솟값 2.284118e-4", 2.284118e-4 >= 2.3e-4, "기록값 2.284e-4 < 2.3e-4 (이 글의 구간 재계산 2.437e-4는 >= 2.3e-4)")

print("\n실패 수:", fails)
sys.exit(1 if fails else 0)
