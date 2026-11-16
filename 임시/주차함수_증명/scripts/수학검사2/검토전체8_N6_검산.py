# -*- coding: utf-8 -*-
"""전체 독립 검토 8차 N6 — 장7A 검산.

1) 작은 n,k에서 전수 열거로 7.1–7.3의 항등식·부등식을 확인한다.
   - 정리 old-6-2 (mu_n(k) = E[v_k(Z,H)]), 따름정리 old-6-4, 명제 old-6-5(볼록–꺾임), 정리 old-6-6,
     따름정리 factorial-moment, 명제 old-6-7(결합 부등식, 엄격), 정리 old-6-10(상계, n=k 등호),
     명제 riccati의 반례 (k,z,n)=(3,1,2), 정리 old-6-11(가)의 유한 크기 공식, 보조정리 level-chain(가).
2) 수치 상수: t_k, n^sharp_k, 열 인증 상수, 자기일관 상계 표(세 층), cor-S-prime의 세 값, polar-N 상수.
"""
from fractions import Fraction as F
from itertools import permutations, product
from math import comb, factorial, log, exp, sqrt, cosh, e as E_
import sys

def caps(sigma):
    n = len(sigma); h = []
    for i in range(n):
        j = i - 1
        while j >= 0 and sigma[j] < sigma[i]:
            j -= 1
        h.append(i - j)
    return h

def A_sigma(h, ell):
    p = 1
    for x in h: p *= min(x, ell + 1)
    return p

def A(n, ell):
    if n == 0: return 1
    if ell < 0: return 0
    return sum(A_sigma(caps(s), ell) for s in permutations(range(1, n + 1)))

def d(n, k): return A(n, k) - 2 * A(n, k - 1) + A(n, k - 2)

ok = True
def check(cond, msg):
    global ok
    if not cond:
        ok = False; print("FAIL:", msg)

# ---------- 1. 전수 열거 ----------
for n in range(1, 8):
    perms = list(permutations(range(1, n + 1)))
    H = {s: caps(s) for s in perms}
    for k in range(2, n + 2):
        Ak1 = A(n, k - 1)
        w = {s: F(A_sigma(H[s], k - 1), Ak1) for s in perms}
        Z = {s: sum(1 for x in H[s] if x > k) for s in perms}
        Hk = {s: sum(1 for x in H[s] if x == k) for s in perms}
        # old-6-2
        mu = F(d(n, k), Ak1)
        v = sum(w[s] * ((1 + F(1, k)) ** Z[s] + (1 - F(1, k)) ** (Z[s] + Hk[s]) - 2) for s in perms)
        check(mu == v, f"old-6-2 n={n} k={k}")
        # old-6-4
        ET = sum(w[s] * (Z[s] * (Z[s] - 1) - k * Hk[s]) for s in perms)
        check(d(n, k) >= Ak1 * ET / k ** 2, f"old-6-4 n={n} k={k}")
        # old-6-5: Conv - Kink
        # Conv = int_{-1}^{1}(1-|s|) Abar''(k+s) ds, Abar on (k,k+1): sum (prod_{h<=k} h) y^Z ; on (k-1,k): sum(prod_{h<=k-1}h) y^{Z+H}
        def poly_int(coefs, a, b, kk):
            # coefs: dict exponent->coef ; integrate (weight) * p''(y) over [a,b] with weight (1-|y-kk|)
            tot = F(0)
            for m, c in coefs.items():
                if m < 2: continue
                # p'' term c*m*(m-1) y^{m-2}; weight: on [k,k+1]: (k+1-y); on [k-1,k]: (y-k+1)
                def prim(y, sign):
                    # integrate y^{m-2} * (sign*(y) + const) handled directly below
                    return None
                mm = m - 2
                if a == kk:  # [k,k+1], weight (k+1-y)
                    val = (kk + 1) * (F(b) ** (mm + 1) - F(a) ** (mm + 1)) / (mm + 1) - (F(b) ** (mm + 2) - F(a) ** (mm + 2)) / (mm + 2)
                else:        # [k-1,k], weight (y-k+1)
                    val = (F(b) ** (mm + 2) - F(a) ** (mm + 2)) / (mm + 2) - (kk - 1) * (F(b) ** (mm + 1) - F(a) ** (mm + 1)) / (mm + 1)
                tot += c * m * (m - 1) * val
            return tot
        right = {}; left = {}
        for s in perms:
            pr = 1
            for x in H[s]:
                if x <= k: pr *= x
            right[Z[s]] = right.get(Z[s], 0) + pr
            pl = 1
            for x in H[s]:
                if x <= k - 1: pl *= x
            left[Z[s] + Hk[s]] = left.get(Z[s] + Hk[s], 0) + pl
        conv = poly_int(right, k, k + 1, k) + poly_int(left, k - 1, k, k)
        kink = Ak1 * sum(w[s] * Hk[s] for s in perms) / k
        check(conv - kink == d(n, k), f"old-6-5 n={n} k={k}")
        check(conv >= 0, f"old-6-5 conv>=0 n={n} k={k}")
        # old-6-6 (Psi = 1{M<=k-1}, y=k) and factorial moment
        if k <= n:
            EZ = sum(w[s] * Z[s] for s in perms)
            check(EZ >= F(n - k, k + 1), f"old-6-6 n={n} k={k}")
            m = F(n - k, k + 1)
            if m >= 1:
                EZ2 = sum(w[s] * Z[s] * (Z[s] - 1) for s in perms)
                check(EZ2 >= m * (m - 1), f"factorial-moment n={n} k={k}")
        # old-6-7 (strict), using floats for the power
        R = A(n, k) / Ak1; Zr = A(n, k - 2) / Ak1
        xf = 1 - 1 / k; xs = 1 + 1 / k
        o = -2 * log(xf) / log(xs)
        check(Zr > xf * R ** (-o) + 1e-15, f"old-6-7 n={n} k={k}: Z={Zr} rhs={xf*R**(-o)}")
        # old-6-10
        if k <= n:
            EkH = k * sum(w[s] * Hk[s] for s in perms)
            xk = F(k, k + 1) ** (k - 1)
            check(EkH <= xk * n, f"old-6-10 n={n} k={k}")
            if n == k: check(EkH == xk * n, f"old-6-10 equality n=k={k}")
print("전수 열거(1–7) 끝")

# riccati 반례 (k,z,n)=(3,1,2): 좌변 n![x^n]Y_z = sum_sigma A^sigma_{k-1} H_z
k, z, n = 3, 1, 2
lhs = sum(A_sigma(caps(s), k - 1) * sum(1 for x in caps(s) if x == z) for s in permutations(range(1, n + 1)))
# 우변: A_{k-1} O_z + k Ex/(Delta)^2 int O_z Ex ; 형식적 멱급수 차수 n까지
N = 6
p = [1, 1, 3, 16, 125, 1296, 16807]
def series_mul(a, b):
    c = [F(0)] * (N + 1)
    for i in range(N + 1):
        for j in range(N + 1 - i):
            c[i + j] += a[i] * b[j]
    return c
def series_exp(a):  # a[0]=0
    r = [F(0)] * (N + 1); r[0] = F(1)
    # r' = a' r
    for m in range(1, N + 1):
        r[m] = sum(j * a[j] * r[m - j] for j in range(1, m + 1)) / m
    return r
def series_int(a):
    return [F(0)] + [a[i] / (i + 1) for i in range(N)]
def series_inv(a):
    r = [F(0)] * (N + 1); r[0] = 1 / a[0]
    for m in range(1, N + 1):
        r[m] = -sum(a[j] * r[m - j] for j in range(1, m + 1)) / a[0]
    return r
Q = [F(0)] * (N + 1)
for j in range(k - 1):
    Q[j + 1] += F((k - 1 - j) * p[j], factorial(j + 1))
Ex = series_exp([-q for q in Q])
Delta = [F(1)] + [-k * x for x in series_int(Ex)[1:]]
Ak1s = series_mul(Ex, series_inv(Delta))
# 검산: A_{n,k-1}
for m in range(N + 1):
    check(Ak1s[m] * factorial(m) == A(m, k - 1) if m <= 6 else True, f"A_{k-1} series m={m}")
a_zm1 = A(z - 1, k - 1) / F(factorial(z - 1))
Oz = [F(0)] * (N + 1); Oz[z] = F(min(z, k)) * a_zm1 / z
term1 = series_mul(Ak1s, Oz)
inner = series_int(series_mul(Oz, Ex))
term2 = series_mul(series_mul([k * x for x in Ex], series_mul(series_inv(Delta), series_inv(Delta))), inner)
rhs = (term1[n] + term2[n]) * factorial(n)
print(f"riccati 반례 (3,1,2): 좌변 {lhs}, 우변 {rhs}")
check(lhs == 4 and rhs == 5, "riccati counterexample values")
# riccati 성립 확인 z>=k-1: (k,z)=(3,2),(3,3),(2,1) n<=6
for (k, z) in [(3, 2), (3, 3), (2, 1), (2, 2)]:
    Q = [F(0)] * (N + 1)
    for j in range(k - 1):
        Q[j + 1] += F((k - 1 - j) * p[j], factorial(j + 1))
    Ex = series_exp([-q for q in Q])
    Delta = [F(1)] + [-k * x for x in series_int(Ex)[1:]]
    Ak1s = series_mul(Ex, series_inv(Delta))
    a_zm1 = A(z - 1, k - 1) / F(factorial(z - 1))
    Oz = [F(0)] * (N + 1); Oz[z] = F(min(z, k)) * a_zm1 / z
    term1 = series_mul(Ak1s, Oz)
    inner = series_int(series_mul(Oz, Ex))
    term2 = series_mul(series_mul([k * x for x in Ex], series_mul(series_inv(Delta), series_inv(Delta))), inner)
    for n in range(1, 7):
        lhs = sum(A_sigma(caps(s), k - 1) * sum(1 for x in caps(s) if x == z) for s in permutations(range(1, n + 1)))
        rhs = (term1[n] + term2[n]) * factorial(n)
        check(lhs == rhs, f"riccati k={k} z={z} n={n}: {lhs} vs {rhs}")
    if z == k:
        # old-6-11 (가): E[H_k] = (n+1) a_{k-1} sum_j K_j a_{n+1-j}/a_n ; K = e^{Q} int f^k e^{-Q}
        eQ = series_exp(Q)
        fk = [F(0)] * (N + 1); fk[k] = F(1)
        Kser = series_mul(eQ, series_int(series_mul(fk, Ex)))
        check(Kser[k + 1] == F(1, k + 1) and all(Kser[j] == 0 for j in range(k + 1)), f"K coefficients k={k}")
        a = [F(A(m, k - 1), factorial(m)) for m in range(N + 1)]
        for n in range(1, 6):
            EH = sum(F(A_sigma(caps(s), k - 1), A(n, k - 1)) * sum(1 for x in caps(s) if x == k) for s in permutations(range(1, n + 1)))
            rhs = (n + 1) * a[k - 1] * sum(Kser[j] * a[n + 1 - j] for j in range(k + 1, n + 2)) / a[n]
            check(EH == rhs, f"old-6-11(가) k={k} n={n}: {EH} vs {rhs}")
print("riccati / old-6-11 끝")

# level-chain (가): transition probabilities sum to one; path law check by direct enumeration for n=5,k=2
n, k = 5, 2
a = [F(A(m, k - 1), factorial(m)) for m in range(n + 1)]
def nn(z): return F(1) if z == 0 else min(z, k) * a[z - 1]
for z in range(1, n + 1):
    check(sum(a[z - 1 - zp] * nn(zp) / (z * a[z - 1]) for zp in range(0, z)) == 1, f"level-chain transition sum z={z}")
check(sum(a[n - z] * nn(z) / (n * a[n]) for z in range(1, n + 1)) == 1, "level-chain start sum")
# path law vs enumeration: P(z_1 = m)
cnt = {}
tot = F(0)
for s in permutations(range(1, n + 1)):
    h = caps(s); wgt = F(A_sigma(h, k - 1), A(n, k - 1))
    for i in range(n):  # uniform position
        # largest interval containing i: piece containing i (right-to-left maxima decomposition)
        # compute intervals (j-h_j, j] containing i (0-indexed: positions j with j-h_j < i <= j)
        lens = [h[j] for j in range(n) if j - h[j] < i <= j]
        z1 = max(lens)
        cnt[z1] = cnt.get(z1, 0) + wgt / n
for m in range(1, n + 1):
    check(cnt.get(m, 0) == min(m, k) * a[m - 1] * a[n - m] / (n * a[n]), f"P(z_1={m})")
print("level-chain 끝")

# ---------- 2. 수치 상수 ----------
def t_k(k):
    j = 0
    while not ((k + 1) ** j * k ** (j + 1) + (k - 1) ** (2 * j + 1) >= 2 * k ** (2 * j + 1)):
        j += 1
    return j
for k in [2, 3, 5, 10, 41, 100, 501, 2000]:
    t = t_k(k); ns = k + (k + 1) * t
    print(f"k={k}: t_k={t}, n#_k={ns}, n#/k^2={ns/k**2:.4f}")
    check(1 <= t <= k, f"t_k range k={k}")

# column-lemma (가) numerics
check(10 ** 21 * 400 ** 10 > 17 ** 21 * 123 ** 10, "integer inequality")
print("17^21*123^10 =", 17 ** 21 * 123 ** 10, " 10^21*400^10 =", 10 ** 21 * 400 ** 10)
print("40/41*(10/17)^2.1 =", 40 / 41 * (10 / 17) ** 2.1)
for k in [41, 100, 1000]:
    o = -2 * log(1 - 1 / k) / log(1 + 1 / k)
    check(2 < o <= 2 * (k + 1) / (k - 1) <= 2.1, f"o_k bound k={k}")
    xf = 1 - 1 / k
    phi17 = 1.7 + xf * 1.7 ** (-o) - 2
    check(phi17 > 0, f"phi(17/10)>0 k={k}")
    check(1 - o * xf * 1.7 ** (-o - 1) > 0, f"phi' >0 k={k}")

# self-consistent-S table (mpmath if available)
try:
    import mpmath as mp
    mp.mp.dps = 60
    def ao(m):  # a°_m = (m+1)^{m-1}/m!
        return mp.mpf(m + 1) ** (m - 1) / mp.factorial(m)
    def jstar(L):
        m = 0
        while ao(m + 2) / ao(m + 1) < L:  # e^{g(m+2)} = a°_{m+2}/a°_{m+1}; need max m with a°_{m+1}/a°_m < L
            m += 1
        # now a°_{m+2}/a°_{m+1} >= L ; check a°_{m+1}/a°_m < L
        assert ao(m + 1) / ao(m) < L
        return m
    layers = [(mp.mpf(267) / 100, 25, 501, 0.13, (82, 429, 0.024992, 0.749711, 0.736245, 1.4708, 0.098505)),
              (mp.mpf(27) / 10, 70, 1855, 0.08, (220, 1855, 0.008802, 0.854757, 0.849132, 2.5335, 0.060259)),
              (mp.mpf(271) / 100, 100, 6098, 0.055, (490, 6098, 0.005691, 0.865504, 0.862859, 2.7354, 0.0422))]
    for L, J, k0, y, tab in layers:
        js = jstar(L)
        kR = max(2 * js + 2, int(mp.ceil(L ** (js + 2) / ao(js + 1))))
        xk0 = (mp.mpf(k0) / (k0 + 1)) ** (k0 - 1)
        xbar = [ao(v) * L ** (-(v + 1)) for v in range(J)]
        qlow = [max(mp.mpf(0), 1 - sum(ao(j) * L ** (-(j + 1)) for j in range(v))) for v in range(J)]
        Elow = sum(ao(J + i) / ao(J) * mp.e ** (-i) for i in range(1, k0 - js + 1))
        Einf = (L / mp.e) * (1 - (L / mp.e) ** k0) / (1 - L / mp.e)
        Rj = max(1 / (1 + Elow), 1 / (1 + Einf))
        Rtab = mp.mpf(tab[2])
        # (i) 정의값 R_J(구간 위끝)에서 계산 — 표의 여섯 자리 값이 재현되어야 한다
        Xi = sum(max(mp.mpf(0), xbar[v] - Rj * qlow[v]) for v in range(J))
        Xik = sum(max(mp.mpf(0), ao(v) * xk0 * L ** (-v) - Rj * qlow[v]) for v in range(J))
        A0 = xk0 + Xik / (L * (1 - Xi)); B0 = Rj * (1 + Xik / (1 - Xi))
        # (ii) 표에 적힌 상계 R_J<=…를 그대로 넣어 계산 — 표의 B0 상계가 깨진다(보고 2-3)
        Xi2 = sum(max(mp.mpf(0), xbar[v] - Rtab * qlow[v]) for v in range(J))
        Xik2 = sum(max(mp.mpf(0), ao(v) * xk0 * L ** (-v) - Rtab * qlow[v]) for v in range(J))
        A02 = xk0 + Xik2 / (L * (1 - Xi2)); B02 = Rtab * (1 + Xik2 / (1 - Xi2))
        print(f"층 L={L}: j*={js} (표 {tab[0]}), k_R={kR} (표 {tab[1]}), R_J 정의값={mp.nstr(Rj,8)} (표 <= {tab[2]})")
        print(f"   정의값 R_J에서: Xi={mp.nstr(Xi,7)} (표 {tab[3]}), Xi^(k0)={mp.nstr(Xik,7)} (표 {tab[4]}), A0={mp.nstr(A0,7)} (표 <= {tab[5]}), B0={mp.nstr(B0,7)} (표 <= {tab[6]})")
        print(f"   표의 상계 {tab[2]}에서: Xi={mp.nstr(Xi2,7)}, Xi^(k0)={mp.nstr(Xik2,7)}, A0={mp.nstr(A02,7)}, B0={mp.nstr(B02,7)}  -> B0<=표? {B02 <= tab[6]}")
        check(js == tab[0] and kR == tab[1], f"j*,k_R layer {L}")
        check(Rj <= Rtab, f"R_J layer {L}")
        check(abs(Xi - tab[3]) < 1e-6 and abs(Xik - tab[4]) < 1e-6, f"Xi layer {L} (정의값 R_J)")
        check(A0 <= tab[5] and B0 <= tab[6], f"A0,B0 layer {L} (정의값 R_J)")
        check(k0 >= kR and J <= js and Xi < 1, f"layer conditions {L}")
        # cor-S-prime
        xi = mp.mpf(1) / k0
        val = (y - xi) * (y - 2 * xi - xi ** 2) - (1 + xi) ** 2 * (A0 * xi + B0 * y)
        valtab = (y - xi) * (y - 2 * xi - xi ** 2) - (1 + xi) ** 2 * (tab[5] * xi + tab[6] * y)
        vert = (3 * xi + xi ** 2) / 2 + (1 + xi) ** 2 * B0 / 2
        print(f"   cor-S-prime: g(y k^2)/k^4 = {mp.nstr(val,5)} (표값 대입 {mp.nstr(valtab,5)}), 꼭짓점/k^2={mp.nstr(vert,5)} <= y={y}: {vert <= y}, y k0^2-2k0-1>0: {y*k0**2-2*k0-1>0}")
        check(val > 0 and valtab > 0 and vert <= y, f"cor-S-prime layer {L}")
    # polar-N constants
    k = 2001
    print("2/sqrt(2001)=", mp.nstr(2 / mp.sqrt(2001), 6), " e^{-1+2/2002}=", mp.nstr(mp.e ** (-1 + mp.mpf(2) / 2002), 6),
          " 0.75/sqrt(2001)=", mp.nstr(0.75 / mp.sqrt(2001), 6), " e^{-0.0448}=", mp.nstr(mp.e ** (-0.0448), 6),
          " 0.955*0.991*0.3678=", 0.955 * 0.991 * 0.3678, " 2k^{3/2}+1=", mp.nstr(2 * mp.mpf(k) ** 1.5 + 1, 8), " 0.3476k^2=", 0.3476 * k ** 2)
    yv = mp.mpf('0.0448')
    check(2 * (mp.cosh(yv) - 1) <= 1.001 * yv ** 2, "cosh bound")
    # polar-W k>=1e7 chain numbers
    k = mp.mpf(10) ** 7
    print("8.344/sqrt(1e7)=", mp.nstr(8.344 / mp.sqrt(k), 6), " (1+0.91/sqrt k)^3*8=", mp.nstr(8 * (1 + 0.91 / mp.sqrt(k)) ** 3, 8))
    # j*: free ratio values near 82
    for m in [81, 82, 83]:
        print(f"  e^g({m+1}) = a°_{m+1}/a°_{m} =", mp.nstr(ao(m + 1) / ao(m), 8))
except ImportError:
    print("mpmath 없음 — 표 검산 생략")

print("모두 통과" if ok else "실패 있음")
