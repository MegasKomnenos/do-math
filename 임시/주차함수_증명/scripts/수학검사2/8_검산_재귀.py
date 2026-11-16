# -*- coding: utf-8 -*-
"""수학 검사 2(태그 8): 8.1절·8.2절·8.3절의 등식·부등식을 작은 k에서 정확한 유리수로 검사한다.
 - 생존 s_N(y)=Pr_N(M<=y-1)를 정리 2.13의 재귀(최대 나무 사슬)로 정확히 계산(N<=2y+1).
 - theta_{N+1}(m)=(N+1-m)pi_N(m)=Bor(m)Ren(N+1-m)/Bor(N+1), pi_n(m)의 두 꼴, Theta_n/p_n 꼴.
 - (8.2) 한 블록 재귀 등식(k+1<=m<=2k+1), (8.4) R_q 재귀, (8.8) E[A]의 셋째 식(독립 재귀와 비교)과 Jensen 하계,
   (8.9) 탈출 하계, (8.10) 가장 낮은 위반 항등식, 명제 U (8.11) B_N>=B^low와 s_N<=1/(1+B_N),
   보조정리 old-6-30 (가)(나)(다), old-6-31 (다)(라)(마), old-6-32 eps_cap>=eps_size/2,
   보조정리 explicit-bounds (가)(나)(다)(라)(마)의 수치 검사.
실행: python -I scripts/수학검사2/8_검산_재귀.py
"""
from fractions import Fraction as Fr
from math import comb, factorial
from mpmath import mp, mpf, sqrt, exp, log, pi, zeta, e as E_

mp.dps = 40
C2 = 1 / sqrt(2 * pi)
Z12, ZM12, Z32 = zeta(mpf(1) / 2), zeta(-mpf(1) / 2), zeta(mpf(3) / 2)
CPSI = -Z12 + Z32 / 12
fails = []


def rep(name, ok, detail=""):
    print(("OK   " if ok else "FAIL ") + name + ("  " + detail if detail else ""))
    if not ok:
        fails.append(name)


def p(m):            # p_m = (m+1)^(m-1)
    return (m + 1) ** (m - 1) if m >= 1 else 1


def pi_n(n, m):      # C(n,m) m^{m-1} p_{n-m}/p_n (exact)
    return Fr(comb(n, m) * m ** (m - 1) * p(n - m), p(n))


def pi0(n, y):       # Pr_n(G<=y): forests of size n with all trees <= y, / p_n.  Count via exponential formula coefficients.
    # number of rooted forests on n labelled vertices with all tree sizes <= y:  n! [x^n] exp(sum_{t<=y} t^{t-1} x^t / t!)
    # compute by recursion on the tree containing vertex 1: F(n) = sum_{t<=min(y,n)} C(n-1,t-1) t^{t-1} F(n-t)
    F = [Fr(1)]
    for nn in range(1, n + 1):
        F.append(sum(Fr(comb(nn - 1, t - 1) * t ** (t - 1)) * F[nn - t] for t in range(1, min(y, nn) + 1)))
    return F[n] / p(n)


def s_table(y, Nmax):
    """s_N(y) for 0<=N<=Nmax (<=2y+1) via Theorem 2.13: s_N = pi0_N(y) + sum_{m=y+1}^N pi_N(m) (y/m) s_{m-1}."""
    s = {}
    for N in range(0, Nmax + 1):
        if N <= y:
            s[N] = Fr(1); continue
        s[N] = pi0(N, y) + sum(pi_n(N, m) * Fr(y, m) * s[m - 1] for m in range(y + 1, N + 1))
    return s


def Bor(m): return Fr(m ** (m - 1), factorial(m)) * Fr(1)  # times e^{-m}: handled symbolically below via ratios


# e^{-m} factors cancel in every ratio used (Bor(m)Bor(n+1-m)/Bor(n+1), Ren(j)/Bor etc.), so define e-free versions
def BorE(m): return Fr(m ** (m - 1), factorial(m))       # Bor(m) e^{m}
def RenE(j): return Fr(j ** j, factorial(j)) if j >= 1 else Fr(1)   # Ren(j) e^{j}, Ren(0)=1


print("== 1. pi_n(m) 두 꼴, theta_{N+1}(m)=(N+1-m)pi_N(m)=Bor(m)Ren(N+1-m)/Bor(N+1), Theta_n/p_n ==")
ok = True
for n in range(2, 30):
    for m in range(1, n + 1):
        lhs = pi_n(n, m)
        rhs = BorE(m) * BorE(n + 1 - m) / BorE(n + 1)      # e^{-m-(n+1-m)+(n+1)} = 1
        ok &= (lhs == rhs)
rep("pi_n(m)=C(n,m)m^{m-1}p_{n-m}/p_n = Bor(m)Bor(n+1-m)/Bor(n+1) (n<30)", ok)
ok = True
for N in range(1, 30):
    for m in range(1, N + 1):
        a = (N + 1 - m) * pi_n(N, m)
        b = BorE(m) * RenE(N + 1 - m) / BorE(N + 1)
        # 2.9절 theta_t(k) = C(t,k) k^{k-1} (t-k)^{t-k} / t^{t-1}, t=N+1, k=m
        t, kk = N + 1, m
        c = Fr(comb(t, kk) * kk ** (kk - 1) * (t - kk) ** (t - kk), t ** (t - 1))
        ok &= (a == b == c)
rep("theta_{N+1}(m) = (N+1-m)pi_N(m) = Bor(m)Ren(N+1-m)/Bor(N+1) = 2.9절 정의 (N<30)", ok)

print("== 2. 생존 재귀와 8.1절 (8.2)(8.4), 8.2절 (8.8)(8.9)(8.10)(8.11), 8.3절 ==")
for k in (6, 9, 13):
    y = k
    s_k = s_table(k, 2 * k + 1)        # s_N(k), N<=2k+1
    s_k1 = s_table(k + 1, 2 * k + 3)   # s_N(k+1), N<=2k+3
    s_km = s_table(k - 1, 2 * k - 1)   # s_N(k-1), N<=2k-1
    c = {m: s_k1[m] - s_k[m] for m in range(0, 2 * k + 2)}      # c_m(k)=Pr_m(M=k)
    cm = {m: s_k[m] - s_km[m] for m in range(0, 2 * k)}        # c_m(k-1)
    # (8.2) one-block recursion equality for k+1<=m<=2k+1
    ok = True
    for m in range(k + 1, 2 * k + 2):
        rhs = sum(pi_n(m, t) / t * (s_k1[t - 1] + k * c[t - 1]) for t in range(k + 1, m + 1))
        ok &= (c[m] == rhs)
    rep(f"(8.2) c_m(k) one-block equality k={k}, k+1<=m<=2k+1", ok)
    ok = True
    for m in range(k, 2 * k):
        rhs = sum(pi_n(m, t) / t * (s_k[t - 1] + (k - 1) * cm[t - 1]) for t in range(k, m + 1))
        ok &= (cm[m] == rhs)
    rep(f"(8.2) level k-1 equality k={k}, k<=m<=2k-1", ok)
    # (8.4) R_q recursion
    R = {0: Fr(0)}
    ok = True
    for q in range(1, k + 2):
        R[q] = sum(pi_n(k + q, k + j) * Fr(k, k + j) * (s_k1[k + j - 1] + R[j - 1]) for j in range(1, q + 1))
        ok &= (R[q] == k * c[k + q])
    rep(f"(8.4) R_q = k c_{{k+q}}(k) k={k}, 1<=q<=k+1", ok)
    # (8.5) lower bound of lemma old-6-24 (numerical, Bor needs e^{-j}: use mpmath)
    ok = True
    for q in range(1, k + 2):
        lb = mpf(k) / (k + q) * sum(mpf(j ** (j - 1)) * exp(-j) / factorial(j) * (mpf(s_k1[k + q - j].numerator) / s_k1[k + q - j].denominator + mpf(R[q - j].numerator) / R[q - j].denominator) for j in range(1, q + 1))
        ok &= (mpf(R[q].numerator) / R[q].denominator >= lb - mpf(10) ** -30)
    rep(f"(8.5) R_q >= k/(k+q) sum Bor(j)[s+R] k={k}", ok)
    # (8.8): E_N[A] = sum_{j=1}^{N-y} j theta_{N+1}(y+j)  vs independent chain recursion EA(N) = sum_{m>y} pi_N(m)[(m-y)+EA(m-1)]
    for yy in (k, k + 1):
        EA = {}
        for N in range(0, 2 * yy + 2):
            EA[N] = Fr(0) if N <= yy else sum(pi_n(N, m) * ((m - yy) + EA[m - 1]) for m in range(yy + 1, N + 1))
        ok = True
        for N in range(yy, 2 * yy + 2):
            formula = sum(j * (N + 1 - (yy + j)) * pi_n(N, yy + j) for j in range(1, N - yy + 1))
            ok &= (EA[N] == formula)
        rep(f"(8.8) E_N[A] = sum_j j theta_{{N+1}}(y+j), y={yy}, y<=N<=2y+1", ok)
        # Jensen: s_N(y) >= exp(-E[A]/y)
        st = s_k if yy == k else s_k1
        ok = all(mpf(st[N].numerator) / st[N].denominator >= exp(-mpf(EA[N].numerator) / EA[N].denominator / yy) for N in range(yy, 2 * yy + 2))
        rep(f"(8.8) Jensen s_N(y) >= exp(-E[A]/y), y={yy}", ok)
    # (8.9) escape lower bound and (8.10) identity, Prop U (8.11)
    ok9 = ok10 = okU = okUl = True
    for N in range(y + 1, 2 * y + 2):
        km = sum(pi_n(N, m) * Fr(y, m) for m in range(y + 1, N + 1))
        p0 = pi0(N, y)
        ok9 &= (s_k[N] >= p0 / (1 - km)) and (p0 / (1 - km) >= p0 / (1 - Fr(y, N) + Fr(y, N) * p0))
        rhs10 = sum((N + 1 - m) * pi_n(N, m) * Fr(m - y, m) * s_k[m - 1] for m in range(y + 1, N + 1))
        ok10 &= (1 - s_k[N] == rhs10)
        B = sum((N + 1 - m) * pi_n(N, m) * Fr(m - y, m) for m in range(y + 1, N + 1))
        okU &= (s_k[N] <= 1 / (1 + B))
        nu = N - k
        S12 = 2 * sqrt(nu) + Z12 + 1 / (2 * sqrt(nu)) - mpf(nu) ** (-mpf(3) / 2) / 24
        Sm12 = mpf(2) / 3 * mpf(nu) ** (mpf(3) / 2) + sqrt(nu) / 2 + ZM12 + 1 / (24 * sqrt(nu))
        Blow = C2 / (k + nu) * ((nu + 1) * S12 - Sm12 - ((nu + 1) * Z32 - S12) / 12)
        okUl &= (mpf(B.numerator) / B.denominator >= Blow)
    rep(f"(8.9) s_N(y) >= pi0/(1-km) >= pi0/(1-y/N+(y/N)pi0), y={y}", ok9)
    rep(f"(8.10) 1-s_N(y) = sum theta_{{N+1}}(m)(m-y)/m s_{{m-1}}(y), y={y}", ok10)
    rep(f"(8.11)(가) s_N <= 1/(1+B_N), y={y}", okU)
    rep(f"(8.11)(나) B_N >= B^low(k,nu), k={k}, 1<=nu<=k+1", okUl)
    # old-6-30: k<=N<=2k-1 (가)(나); (다) N<=2k-2
    okA = okB = okC = True
    for N in range(k, 2 * k):
        ratio = s_km[N] / s_k[N]
        okA &= (ratio >= Fr(k - 1, k) ** (N - k + 1))
        okB &= (ratio >= 1 - max(Fr(1) / (k * pi0(Np, k - 1)) for Np in range(k, N + 1)))
        if N <= 2 * k - 2:
            bound = 1 - exp(mpf(7) / 6) * mpf(N) ** (mpf(3) / 2) / (4 * C2 * k * (2 * k - 1 - N))
            okC &= (mpf(ratio.numerator) / ratio.denominator >= bound)
            # two-tree lower bound of pi0_N(k-1)
            # Bor(j)Bor(N-j)/(2e Bor(N+1)) = BorE(j)BorE(N-j)e^{-N}/(2e BorE(N+1)e^{-(N+1)}) = BorE BorE/(2 BorE(N+1)) = BorE(j)BorE(N-j)e^{-N}/(2e BorE(N+1)e^{-(N+1)}) = BorE BorE/(2 BorE(N+1))
            two = sum(BorE(j) * BorE(N - j) / (2 * BorE(N + 1)) for j in range(N - k + 1, k))
            okC &= (pi0(N, k - 1) >= two) and (mpf(two.numerator) / two.denominator >= 4 * C2 * exp(-mpf(7) / 6) * (2 * k - 1 - N) * mpf(N) ** (-mpf(3) / 2))
    rep(f"old-6-30 (가) s_N(k-1)/s_N(k) >= (1-1/k)^{{N-k+1}}, k={k}", okA)
    rep(f"old-6-30 (나) >= 1-max 1/(k pi0_N'(k-1)), k={k}", okB)
    rep(f"old-6-30 (다) >= 1-e^{{7/6}}N^{{3/2}}/(4C2 k(2k-1-N)), and two-tree bound, k={k}", okC)
    # old-6-31 (다)(라)(마) numerically exact
    ok = True
    for m in range(2, 3 * k):
        for t in range((m + 1) // 2, m):
            if 2 * t >= m:
                ok &= (pi_n(m, t + 1) >= pi_n(m, t))
        for t in range(1, m + 1):
            ok &= (pi_n(m + 1, t) <= pi_n(m, t))
    rep(f"old-6-31 (다)(라) pi_m(t) incr in t on [m/2,m], decr in m, m<{3*k}", ok)
    ok = True
    for N in range(2, 3 * k):
        for j in range(N // 2 + 1, N + 1):
            ok &= (pi0(N, j) - pi0(N + 1, j) <= pi_n(N, j))
    rep(f"old-6-31 (마) pi0_N(j)-pi0_{{N+1}}(j) <= pi_N(j), N/2<j<=N, N<{3*k}", ok)
    # old-6-32: eps_cap(t) >= eps_size(t)/2, k+1<=t<=2k+1
    def sT(t, yy, st): return min(Fr(1), Fr(yy, t)) * st[t - 1]
    ok = True
    for t in range(k + 1, 2 * k + 2):
        ecap = sT(t, k + 1, s_k1) - sT(t, k, s_k)
        esz = sT(t, k, s_k) - sT(t + 1, k, s_k) if t + 1 <= 2 * k + 1 else None
        if esz is None:
            # need s_{t}(k) with t=2k+1: s_k has up to 2k+1 -> sT(2k+2,k) needs s_{2k+1}(k) which we have
            esz = sT(t, k, s_k) - Fr(k, t + 1) * s_k[t]
        ok &= (ecap >= esz / 2)
        ok &= (ecap == Fr(1, t) * (s_k1[t - 1] + k * c[t - 1]))
    rep(f"old-6-32 eps_cap >= eps_size/2 and eps_cap=(s_{{t-1}}(k+1)+k c_{{t-1}}(k))/t, k={k}", ok)
    # (8.3): c_m(k) for m=2k+1 vs sum with s_{m-t}(k)=1 and dup=0?  For m=2k+1, m-t<=k so env survival 1 and dup=0: equality already checked.

print("== 3. 보조정리 explicit-bounds ==")
# (가)
ok = True
for m in range(1, 400):
    B = mpf(m ** (m - 1)) * exp(-m) / factorial(m); Rn = mpf(m ** m) * exp(-m) / factorial(m)
    ok &= C2 * mpf(m) ** (-mpf(3) / 2) * exp(-1 / (12 * mpf(m))) <= B <= C2 * mpf(m) ** (-mpf(3) / 2) * exp(-1 / (12 * mpf(m) + 1))
    ok &= C2 * mpf(m) ** (-mpf(1) / 2) * exp(-1 / (12 * mpf(m))) <= Rn <= C2 * mpf(m) ** (-mpf(1) / 2) * exp(-1 / (12 * mpf(m) + 1))
rep("(가) Robbins bounds on Bor, Ren (m<400)", ok)
# (나)
ok = True
s12 = mpf(0); sp12 = mpf(0); s32 = mpf(0)
for r in range(1, 3000):
    s12 += mpf(r) ** (-mpf(1) / 2); sp12 += sqrt(r); s32 += mpf(r) ** (-mpf(3) / 2)
    R = mpf(r)
    ok &= s12 <= 2 * sqrt(R) + Z12 + R ** (-mpf(1) / 2) / 2
    ok &= s12 >= 2 * sqrt(R) + Z12 + R ** (-mpf(1) / 2) / 2 - R ** (-mpf(3) / 2) / 24
    ok &= sp12 >= mpf(2) / 3 * R ** (mpf(3) / 2) + sqrt(R) / 2 + ZM12
    ok &= sp12 <= mpf(2) / 3 * R ** (mpf(3) / 2) + sqrt(R) / 2 + ZM12 + R ** (-mpf(1) / 2) / 24
    ok &= s32 <= Z32
rep("(나) Euler-Maclaurin bounds (r<3000)", ok)
# (다)(라)
ok = True
Psi = mpf(0); S0 = mpf(0)
for q in range(1, 3000):
    Q = mpf(q)
    Psi += mpf(q ** q) * exp(-q) / factorial(q); S0 += mpf(q ** (q - 1)) * exp(-q) / factorial(q)
    ok &= Psi <= C2 * (2 * sqrt(Q) - 1)
    ok &= S0 >= 1 - sqrt(2 / pi) / sqrt(Q)
    ok &= 2 * C2 * exp(-1 / (12 * (Q + 1))) / sqrt(Q + 1) <= 1 - S0 <= sqrt(2 / pi) / sqrt(Q)
    Pl = C2 * (2 * sqrt(Q) - CPSI + 1 / (2 * sqrt(Q)) - Q ** (-mpf(3) / 2) / 24)
    ok &= Psi >= Pl
    ok &= C2 * (2 * sqrt(Q) - CPSI) <= Pl < 2 * C2 * sqrt(Q)
    d = C2 / sqrt(Q) * (1 - 1 / (4 * Q) + 1 / (16 * Q * Q))
    ok &= 0 < d <= C2 / sqrt(Q)
rep("(다)(라) Psi, Bor_<=, Bor_> bounds, Psi^low, derivative (q<3000)", ok)
# (마)
g = lambda x: (x - 1) * log(1 + 1 / mpf(x))
ok = True
for i in range(1, 500):
    ok &= mpf(3) / (2 * i) - mpf(5) / (6 * i * i) <= 1 - g(i) <= mpf(3) / (2 * i)
for i1 in range(2, 40):
    for i2 in range(i1, 80):
        hs = sum(mpf(1) / i for i in range(i1, i2 + 1))
        ok &= log(mpf(i2 + 1) / i1) <= hs <= log(mpf(i2) / (i1 - 1))
for ip in range(3, 200):
    for j in range(1, ip - 1):
        ratio = mpf(BorE(ip - j).numerator) / BorE(ip - j).denominator * exp(j) / (mpf(BorE(ip).numerator) / BorE(ip).denominator)
        ok &= ratio <= (mpf(ip - 1) / (ip - 1 - j)) ** (mpf(3) / 2)
        ok &= ratio >= (mpf(ip) / (ip - j)) ** (mpf(3) / 2) * exp(-mpf(5 * j) / (6 * (ip - j) ** 2))
rep("(마) 1-g(i) bounds, harmonic bounds, Bor ratio bounds", ok)
# (8.12)-(8.14) J(q,k) <= Bp+Cr at k=6600 for q=2..400 (direct sum with mpmath)
print("== 4. (8.12) J(q,k) <= Bp(q,k)+Cr(q,k) at k=6600 ==")
k = 6600; kap = k + 1
# log Bor via loggamma
from mpmath import loggamma
def lBor(m): m = mpf(m); return (m - 1) * log(m) - m - loggamma(m + 1)
def Ren(r): r = mpf(r); return exp(r * log(r) - r - loggamma(r + 1))
ok = True; worst = mpf(1)
for q in list(range(2, 60)) + [100, 200, 400, 800, 1600, 2125]:
    J = sum((q - r) * Ren(r) * exp(lBor(kap + q - r) - lBor(kap + q)) for r in range(1, q)) / kap
    qq = mpf(q); pp = qq - 1; nn = k + qq
    Lam = qq * (2 * sqrt(pp) + Z12 + 1 / (2 * sqrt(pp))) - (mpf(2) / 3 * pp ** (mpf(3) / 2) + sqrt(pp) / 2 + ZM12)
    Bp = C2 * Lam / kap
    Cr = mpf(3) / 2 * C2 * nn ** (mpf(3) / 2) / mpf(kap) ** (mpf(7) / 2) * (mpf(4) / 15 * qq ** (mpf(5) / 2) + mpf('0.385') * qq ** (mpf(3) / 2))
    ok &= J <= Bp + Cr
    worst = min(worst, (Bp + Cr) / J)
rep("J(q,6600) <= Bp+Cr for sampled q in [2,2125]", ok, f"min (Bp+Cr)/J = {mp.nstr(worst, 8)}")

print("FAIL 수:", len(fails), fails)
