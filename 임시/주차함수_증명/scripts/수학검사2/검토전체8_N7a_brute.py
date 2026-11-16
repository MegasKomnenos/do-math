# 검토전체8 N7a: 7.4절·7.5절 항등식·부등식의 작은 크기 전수 검산(정확 유리수)과 수치 검산(mpmath)
import itertools, math, sys
from fractions import Fraction as Fr
from math import comb, factorial
import sympy as sp
from mpmath import mp, mpf, exp, factorial as mpfact, log

mp.dps = 50
def section(t):
    print("\n==== " + t)

def capacities(sig):
    n = len(sig); h = [0] * n
    for i in range(n):
        j = i - 1
        while j >= 0 and sig[j] < sig[i]:
            j -= 1
        h[i] = i - j
    return h

def p(m):
    return (m + 1) ** (m - 1) if m >= 1 else 1

# 정확한 A_{m,l} (마지막 차 재귀)
from functools import lru_cache
@lru_cache(maxsize=None)
def A(m, l):
    if l < 0: return 0
    if m == 0: return 1
    return sum(comb(m - 1, j - 1) * min(j, l + 1) * A(j - 1, l) * A(m - j, l) for j in range(1, m + 1))

# ---------- A. 순열 전수 ----------
section("A. 순열 전수: 모멘트 재귀 (7.2)(7.3), (7.4), mom_k, (7.5), Green 원자")
def brute_stats(n, k):
    """returns A_{n,k-1}, Zflat, ZH, Z (moments under weighted law), K poly dict {Z: coeff}, J poly dict {Z: coeff}, B_{n,k-1}"""
    tot = 0; sZ = 0; sH = 0; sZZ = 0
    K = {}; J = {}; B = 0
    for sig in itertools.permutations(range(1, n + 1)):
        h = capacities(sig)
        w = 1
        for x in h: w *= min(x, k)
        Z = sum(1 for x in h if x > k); H = sum(1 for x in h if x == k)
        tot += w; sZ += w * Z; sH += w * H; sZZ += w * Z * (Z - 1)
        wl = 1
        for x in h:
            if x <= k: wl *= x
        K[Z] = K.get(Z, 0) + wl
        wlt = 1
        for x in h:
            if x < k: wlt *= x
        if H >= 1:
            J[Z] = J.get(Z, 0) + H * k ** (H - 1) * wlt
        # B_{n,k-1}: 최대 변위 k-1, 변위 k-1인 모든 차가 h_i=k 인 자리에 있음 (2:old-2-30 첫 식)
        B += wlt * (k - 1) ** Z * (k ** H - (k - 1) ** H)
    return tot, Fr(sZ, tot), Fr(sH, tot), Fr(sZZ, tot), K, J, B

def B_direct(n, k):
    # 변위 벡터 전수: 최대 변위 m=k-1, 변위 m인 모든 차의 자리가 h_i=m+1=k
    B = 0
    for sig in itertools.permutations(range(1, n + 1)):
        h = capacities(sig)
        for d in itertools.product(*[range(x) for x in h]):
            M = max(d)
            if M != k - 1: continue
            if all(h[i] == k for i in range(n) if d[i] == M):
                B += 1
    return B

def root_law(m, k):
    Am = A(m, k - 1)
    return [Fr(min(j, k) * comb(m - 1, j - 1) * A(j - 1, k - 1) * A(m - j, k - 1), Am) for j in range(1, m + 1)]

def moments_rec(nmax, k):
    Zf = [Fr(0)] * (nmax + 1); ZH = [Fr(0)] * (nmax + 1); ZZ = [Fr(0)] * (nmax + 1)
    for n in range(1, nmax + 1):
        P = root_law(n, k)
        Zf[n] = sum(P[p_ - 1] * ((1 if p_ > k else 0) + Zf[p_ - 1] + Zf[n - p_]) for p_ in range(1, n + 1))
        ZH[n] = sum(P[p_ - 1] * ((1 if p_ == k else 0) + ZH[p_ - 1] + ZH[n - p_]) for p_ in range(1, n + 1))
        ZZ[n] = sum(P[p_ - 1] * (ZZ[p_ - 1] + ZZ[n - p_] + 2 * Zf[p_ - 1] * Zf[n - p_] + 2 * (1 if p_ > k else 0) * (Zf[p_ - 1] + Zf[n - p_])) for p_ in range(1, n + 1))
    return Zf, ZH, ZZ

ok_all = True
for k in (2, 3, 4):
    nmax = 7
    Zf, ZH, ZZ = moments_rec(nmax, k)
    for n in range(1, nmax + 1):
        tot, zf, zh, zz, K, J, B = brute_stats(n, k)
        # (7.2)
        afn = Fr(A(n, k - 1), factorial(n))
        rhs = sum(min(p_, k) * Fr(A(p_ - 1, k - 1), factorial(p_ - 1)) * Fr(A(n - p_, k - 1), factorial(n - p_)) for p_ in range(1, n + 1))
        c1 = (tot == A(n, k - 1)) and (n * afn == rhs)
        c2 = (zf == Zf[n] and zh == ZH[n] and zz == ZZ[n])
        # (7.5): d >= K''(k) - B >= K''(k) - J(k-1)
        Kpp = sum(c * Z * (Z - 1) * k ** (Z - 2) for Z, c in K.items() if Z >= 2)
        Jk1 = sum(c * (k - 1) ** Z for Z, c in J.items())
        d = A(n, k) - 2 * A(n, k - 1) + A(n, k - 2)
        c3 = (d >= Kpp - B) and (Kpp - B >= Kpp - Jk1)
        if n <= 6:
            c3b = (B == B_direct(n, k))
        else:
            c3b = True
        # K(k)=A_{n,k-1}, K(k+1)=A_{n,k}
        c4 = (sum(c * k ** Z for Z, c in K.items()) == A(n, k - 1)) and (sum(c * (k + 1) ** Z for Z, c in K.items()) == A(n, k))
        if not (c1 and c2 and c3 and c3b and c4):
            ok_all = False
            print("FAIL", k, n, c1, c2, c3, c3b, c4)
print("A: (7.2),(7.3) 전수 일치, (7.5) 성립, B 두 셈 일치, K(k)=A:", ok_all)

# (7.4): cnt, y(m), mom
def check_74(k, nmax):
    Zf, ZH, ZZ = moments_rec(nmax, k)
    # cnt_n(m)
    cnt = [[Fr(0)] * (nmax + 1) for _ in range(nmax + 1)]
    for n in range(1, nmax + 1):
        P = root_law(n, k)
        cnt[n][n] = Fr(1)
        for m in range(1, n):
            cnt[n][m] = sum(P[p_ - 1] * (cnt[p_ - 1][m] + cnt[n - p_][m]) for p_ in range(1, n + 1))
    def g(m, p_):
        return (1 if p_ > k else 0) + Zf[p_ - 1] + Zf[m - p_]
    def yv(m):
        P = root_law(m, k)
        return sum(P[p_ - 1] * g(m, p_) ** 2 for p_ in range(1, m + 1)) - Zf[m] ** 2
    def Pmk(m):
        return root_law(m, k)[k - 1] if m >= k else Fr(0)
    def mom(m):
        P = root_law(m, k)
        return 2 * sum(P[p_ - 1] * Zf[p_ - 1] * Zf[m - p_] for p_ in range(1, m + 1)) + 2 * sum(P[p_ - 1] * (Zf[p_ - 1] + Zf[m - p_]) for p_ in range(k + 1, m + 1)) - k * Pmk(m)
    ok = True
    for n in range(1, nmax + 1):
        Var = ZZ[n] + Zf[n] - Zf[n] ** 2
        e1 = (Var == sum(cnt[n][m] * yv(m) for m in range(1, n + 1)))
        e2 = (k * ZH[n] == sum(cnt[n][m] * k * Pmk(m) for m in range(k, n + 1)))
        ET = ZZ[n] - k * ZH[n]
        e3 = (ET == Zf[n] * (Zf[n] - 1) + sum(cnt[n][m] * (yv(m) - k * Pmk(m)) for m in range(k, n + 1)))
        e4 = (ET == sum(cnt[n][m] * mom(m) for m in range(k, n + 1)))
        ok = ok and e1 and e2 and e3 and e4
    xk = Fr(k ** (k - 1), (k + 1) ** (k - 1))
    ok = ok and (mom(k) == -k * xk)
    # old-6-6: Zflat_n >= (n-k)/(k+1)
    ok6 = all(Zf[n] >= Fr(n - k, k + 1) for n in range(1, nmax + 1))
    return ok, ok6
for k in (2, 3, 4):
    print(f"(7.4) k={k}:", check_74(k, 14), "(식 넷, mom_k=-k x_k; old-6-6 하계)")

# Green 원자: J_n(z) <= J^G_n(z), 등호 n<=2k
z = sp.symbols('z')
def green_atom_check(k, nmax):
    # e^T 계수 a°_m = p_m/m!
    ac = [sp.Rational(p(m), factorial(m)) for m in range(nmax + 1)]
    # hat gr: gr' = a°_{k-1} x^{k-1} + z e^T gr ; coefficients g_m of x^m
    g = [sp.Integer(0)] * (nmax + 1)
    for m in range(1, nmax + 1):
        # m g_m = [x^{m-1}] (a°_{k-1} x^{k-1} + z e^T gr)
        s = sp.Integer(0)
        if m - 1 == k - 1: s += ac[k - 1]
        s += z * sum(ac[i] * g[m - 1 - i] for i in range(0, m))
        g[m] = sp.expand(s / m)
    ok = True
    for n in range(1, nmax + 1):
        JG = sp.expand(factorial(n) * sum(ac[i] * g[n - i] for i in range(0, n + 1)))
        tot, zf, zh, zz, K, J, B = brute_stats(n, k)
        Jpoly = sum(c * z ** Z for Z, c in J.items())
        diff = sp.expand(JG - Jpoly)
        if n <= 2 * k:
            if diff != 0: ok = False; print("  equality fails", k, n, diff)
        for zv in range(0, k + 2):
            if diff.subs(z, zv) < 0: ok = False; print("  inequality fails", k, n, zv)
        # 2:J-egf (가) 재귀도 대조 (n<=2k-1 -> J_{n+1})
    return ok
for k in (2, 3):
    print(f"Green 원자 k={k} (n<=7):", green_atom_check(k, 7))

# ---------- B. 조각의 지수 공식 (7.6), X의 시작 차수, (7.7), (7.9) — k=2, n<=8 ----------
section("B. 명제 block-exponential (k=2, 차수 <=8), 보조정리 pair-terms (7.9)")
x = sp.symbols('x')
def Kpoly_all(k, nmax):
    Ks = {0: sp.Integer(1)}
    for n in range(1, nmax + 1):
        K = {}
        for sig in itertools.permutations(range(1, n + 1)):
            h = capacities(sig)
            Z = sum(1 for v in h if v > k)
            wl = 1
            for v in h:
                if v <= k: wl *= v
            K[Z] = K.get(Z, 0) + wl
        Ks[n] = sum(c * z ** Z for Z, c in K.items())
    return Ks
k = 2; N = 8
Ks = Kpoly_all(k, N)
D = sum(Ks[n] * x ** n / factorial(n) for n in range(N + 1))
Elt = sum(sp.Rational(p(m), factorial(m)) * x ** m for m in range(k))
Dge = sp.expand(D - Elt)
Tle = sum(sp.Rational(t ** (t - 1), factorial(t)) * x ** t for t in range(1, k + 1))
T = sum(sp.Rational(t ** (t - 1), factorial(t)) * x ** t for t in range(1, N + 1))
Tgt = sp.expand(T - Tle)
def trunc(expr, deg):
    expr = sp.expand(expr)
    return sum(expr.coeff(x, i) * x ** i for i in range(deg + 1))
def series_exp(f, deg):
    # exp of series with zero constant term
    f = trunc(f, deg)
    res = sp.Integer(1); term = sp.Integer(1)
    for i in range(1, deg + 1):
        term = trunc(term * f / i, deg)
        res += term
    return sp.expand(res)
intD = sp.integrate(Dge, x)
rhs76 = series_exp(Tle + z * intD, N)
print("(7.6) D = exp(T_{<=k} + z∫D_{>=k}) up to x^8:", sp.expand(trunc(D, N) - rhs76) == 0)
# G_*: solve G = e^T (1 - T_{>k} + z ∫(G - E_{<k})) as series
eT = sum(sp.Rational(p(m), factorial(m)) * x ** m for m in range(N + 1))
G = sp.Integer(0)
for it in range(N + 2):
    G = trunc(eT * (1 - Tgt + z * sp.integrate(G - Elt, x)), N)
# also via S^G: S' = Q_k + z e^T S
Qk = trunc((1 - T) * (eT - Elt), N)
S = sp.Integer(0)
for it in range(N + 2):
    S = trunc(sp.integrate(Qk + z * eT * S, x), N)
G2 = trunc(Elt + Qk + z * eT * S, N)
print("G_* 두 꼴 일치:", sp.expand(G - G2) == 0)
X = sp.expand(trunc(D, N) - G)
lowest = min(i for i in range(N + 1) if sp.expand(X.coeff(x, i)) != 0)
print("X 최저 차수:", lowest, "(claim 2k+2 =", 2 * k + 2, ")")
bd = sp.expand(z * intD - Tgt)
eTle = series_exp(Tle, N)
rhs77 = trunc(eTle * (z * sp.integrate(X, x) + bd ** 2 / 2), N)
print("(7.7) mod x^{3k+3}=x^9 (차수<=8):", sp.expand(X - rhs77) == 0)
# bd_t(z) = z K_{t-1}(z) - t^{t-1}
for t in range(k + 1, N + 1):
    bdt = sp.expand(z * Ks[t - 1] - t ** (t - 1))
    assert sp.expand(bd.coeff(x, t) * factorial(t) - bdt) == 0
print("bd_t = z K_{t-1,k}(z) - t^{t-1}: ok")
# (7.9) 값 검사: bd_t(k), bd'_t(k), bd''_t(k), q_j(t,t')
Zf, ZH, ZZ = moments_rec(N, k)
def bdvals(t):
    bdt = sp.expand(z * Ks[t - 1] - t ** (t - 1))
    return [sp.Rational(sp.diff(bdt, z, i).subs(z, k)) for i in range(3)]
ok9 = True
for t in range(k + 1, N + 1):
    b0, b1, b2 = bdvals(t)
    At = A(t - 1, k - 1)
    ex = Fr(t * p(t - 1), At) - k
    ok9 = ok9 and (Fr(b0) == -At * ex) and (Fr(b1) == At * (1 + Zf[t - 1])) and (Fr(b2) == Fr(At, k) * (2 * Zf[t - 1] + ZZ[t - 1]))
print("bd_t(k), bd'_t(k), bd''_t(k) 식:", ok9)
ok9b = True
for t in range(k + 1, 6):
    for tp in range(k + 1, 6):
        for j in range(0, 4):
            b = bdvals(t); bp = bdvals(tp)
            q = Fr(j * (j - 1), 2 * k * k) * Fr(b[0]) * Fr(bp[0]) + Fr(j, k) * (Fr(b[0]) * Fr(bp[1]) + Fr(b[1]) * Fr(bp[0])) + Fr(b[1]) * Fr(bp[1]) + Fr(1, 2) * (Fr(b[0]) * Fr(bp[2]) + Fr(b[2]) * Fr(bp[0]))
            At = A(t - 1, k - 1); Atp = A(tp - 1, k - 1)
            ex = Fr(t * p(t - 1), At) - k; exp_ = Fr(tp * p(tp - 1), Atp) - k
            rhs = (1 + Zf[t - 1]) * (1 + Zf[tp - 1]) + Fr(j * (j - 1), 2 * k * k) * ex * exp_ - Fr(j, k) * (ex * (1 + Zf[tp - 1]) + exp_ * (1 + Zf[t - 1])) - Fr(1, 2 * k) * (ex * (2 * Zf[tp - 1] + ZZ[tp - 1]) + exp_ * (2 * Zf[t - 1] + ZZ[t - 1]))
            ok9b = ok9b and (q == At * Atp * rhs)
print("(7.9):", ok9b)
# X''_n(k) 부호 (k=2, n<=8)
Xpp = [sp.diff(X.coeff(x, n), z, 2).subs(z, k) * factorial(n) for n in range(N + 1)]
print("X''_n(k), n=0..8:", Xpp)
# K''_{n,k}(k) = POS^G_n + X''_n(k) with POS^G := n![x^n] d^2/dz^2 G|_{z=k}
POS = [sp.diff(G.coeff(x, n), z, 2).subs(z, k) * factorial(n) for n in range(N + 1)]
Kpp = [sp.diff(Ks[n], z, 2).subs(z, k) for n in range(N + 1)]
print("K''=POS^G+X'':", all(Kpp[n] == POS[n] + Xpp[n] for n in range(N + 1)), " 그리고 n<=2k+1에서 X''=0:", all(Xpp[n] == 0 for n in range(2 * k + 2)))

# ---------- C. 7.5절: (7.13), heavy-block, 대각선 접기 ----------
section("C. 7.5절: 한 걸음 항등식 (7.13), heavy-block (나)(다)(라), fold-A/R/T/L1/DIP, prop-PF 안쪽 항등식")
def cl(m, k, sign):
    Am = A(m, k - 1)
    return Fr(A(m, k) - A(m, k - 1), Am) if sign > 0 else Fr(A(m, k - 1) - A(m, k - 2), Am)
def mu(m, k):
    return Fr(A(m, k) - 2 * A(m, k - 1) + A(m, k - 2), A(m, k - 1))
def chi(m, j, k):
    L = j - 1; R = m - j
    ind = 1 if j > k else 0
    v = Fr(1, k) * (-(1 if j == k else 0) * (1 - cl(m - k, k, -1) if m >= k else 0) + ind * (cl(L, k, 1) + cl(L, k, -1) + cl(R, k, 1) + cl(R, k, -1)))
    v += (1 + Fr(ind, k)) * cl(L, k, 1) * cl(R, k, 1) + (1 - Fr(ind, k)) * cl(L, k, -1) * cl(R, k, -1)
    return v
def src(m, k):
    P = root_law(m, k)
    return sum(P[j - 1] * chi(m, j, k) for j in range(1, m + 1))
ok13 = True
for k in (2, 3, 5):
    for m in range(1, 22):
        P = root_law(m, k)
        rhs = src(m, k) + sum(P[j - 1] * (mu(j - 1, k) + mu(m - j, k)) for j in range(1, m + 1))
        ok13 = ok13 and (mu(m, k) == rhs)
        if m <= k - 1: ok13 = ok13 and mu(m, k) == 0 and src(m, k) == 0
print("(7.13) 한 걸음 항등식:", ok13)
print("mu_k(k) = -p_{k-1}/p_k:", all(mu(k, k) == -Fr(p(k - 1), p(k)) for k in (2, 3, 5, 7)))

# heavy-block
def s(m, y):  # survival s_m(y)=A_{m,y-1}/p_m
    return Fr(A(m, y - 1), p(m))
def pi_kernel(m, j):
    return Fr(comb(m, j) * j ** (j - 1) * p(m - j), p(m))
okhb = True
for k in (3, 5, 8):
    for q in range(1, k + 3):
        t = k + q; m = k + q - 1
        sq = s(m, k)
        ex = Fr(t * p(t - 1), A(t - 1, k - 1)) - k
        okhb = okhb and (ex == q + (k + q) * (1 - sq) / sq)
        if q == 1: okhb = okhb and ex == 1
        if q >= 2:
            rhs = sum(pi_kernel(m, j) * (Fr(j - k, j) + Fr(k, j) * (1 - s(j - 1, k))) for j in range(k + 1, k + q))
            okhb = okhb and (1 - sq == rhs)
            # Borel 꼴 핵과 일치: pi_m(j) = Bor(j)Bor(m+1-j)/Bor(m+1) -> 유리수 꼴로: comb(m+1,j) j^{j-1}(m+1-j)^{m-j}/(m+1)^m
            okhb = okhb and (pi_kernel(m, j) == Fr(comb(m + 1, j) * j ** (j - 1) * (m + 1 - j) ** (m - j), (m + 1) ** m) for j in [k + 1])
        pish = Fr(q * (q - 1), 2 * (k + 1))
        okhb = okhb and (1 - sq <= pish)
        # (가) Z_k <= q-1 : 모멘트 상계
        # (sanity) Zflat_{t-1} <= q-1
print("heavy-block (나)(다)(라):", okhb)

# 대각선 접기 (mpmath)
def Bor(m): return exp(-m) * mpf(m) ** (m - 1) / mpfact(m)
def at(m, y): return exp(-m) * mpf(A(m, y - 1)) / mpfact(m)   # tilde a^{(y)}_m
def Eu(n, k): return exp(-1) / (n * at(n, k))
def src_mp(n, k):
    return mpf(src(n, k).numerator) / src(n, k).denominator
okA = True; okR = True; okT = True; okL1 = True; okPF = True
for k in (3, 4, 6):
    for n in range(2 * k + 1, 3 * k + 6):
        nu = n - 2 * k
        thr = -exp(1) * Bor(k) * at(n - k, k - 1)
        heavy = sum(at(n - 1 - m, k) * (at(m, k + 1) - at(m, k - 1)) * (1 + (1 if n - 1 - m >= k else 0)) for m in range(k, n))
        quad = sum(min(j, k + 1) * (at(j - 1, k + 1) - at(j - 1, k)) * (at(n - j, k + 1) - at(n - j, k)) + min(j, k - 1) * (at(j - 1, k) - at(j - 1, k - 1)) * (at(n - j, k) - at(n - j, k - 1)) for j in range(1, n + 1))
        lhsA = src_mp(n, k); rhsA = Eu(n, k) * (thr + heavy + quad)
        if abs(lhsA - rhsA) > mpf(10) ** (-35) * (abs(lhsA) + abs(rhsA) + 1): okA = False; print("  fold-A fail", k, n, lhsA, rhsA)
        # fold-R: for all B in [nu+1, n-1-k]
        def sib(q): return exp(1) * Bor(n - k - q)
        for Bv in range(nu + 1, n - k):
            l = n - 1 - k - Bv
            lhs = sum(sib(q) * (at(k + q, k + 1) - at(k + q, k - 1)) for q in range(nu - 1, Bv + 1))
            ed1 = exp(1) * Bor(k + 1) * at(n - 1 - k, k + 1); ed2 = exp(1) * Bor(k) * at(n - k, k + 1)
            up = exp(1) * Bor(l + 2) * at(n - 2 - l, k - 1) + exp(1) * Bor(l + 1) * at(n - 1 - l, k - 1)
            inn = sum(sib(q + 1) * at(k + q + 1, k + 1) - sib(q - 1) * at(k + q - 1, k - 1) for q in range(nu, Bv))
            rhs = ed1 + ed2 + inn - up
            if abs(lhs - rhs) > mpf(10) ** (-35) * (abs(lhs) + 1): okR = False; print("  fold-R fail", k, n, Bv)
        # (7.15) for all l in [0,k-2]
        for l in range(0, k - 1):
            rhs15 = exp(1) * Bor(k + 1) * at(n - 1 - k, k + 1) + exp(1) * Bor(k) * (at(n - k, k + 1) - at(n - k, k - 1)) - exp(1) * Bor(l + 2) * at(n - 2 - l, k - 1) - exp(1) * Bor(l + 1) * at(n - 1 - l, k - 1)
            if exp(1) * n * at(n, k) * src_mp(n, k) < rhs15 - mpf(10) ** (-35): okL1 = False; print("  (7.15) fail", k, n, l)
        # prop-PF 안쪽 항등식 (n>=3k+1)
        if n >= 3 * k + 1:
            P = root_law(n, k)
            inh = sum(mpf(P[j - 1].numerator) / P[j - 1].denominator * ((mpf(mu(j - 1, k).numerator) / mu(j - 1, k).denominator if k <= j - 1 <= 2 * k else 0) + (mpf(mu(n - j, k).numerator) / mu(n - j, k).denominator if k <= n - j <= 2 * k else 0)) for j in range(1, n + 1))
            rhsPF = 2 * k * Eu(n, k) * sum(at(n - 1 - L, k) * exp(-L) * mpf(A(L, k) - 2 * A(L, k - 1) + A(L, k - 2)) / mpfact(L) for L in range(k, 2 * k + 1))
            if abs(inh - rhsPF) > mpf(10) ** (-35) * (abs(inh) + 1): okPF = False; print("  PF fail", k, n)
    # fold-T: k>=2, n>=3, 1<=q<=n-2, 2q>=n-1
    for n in range(3, 40):
        for q in range(1, n - 1):
            if 2 * q < n - 1: continue
            if at(n - 2 - q, k) * at(q + 1, k + 1) < at(n - q, k) * at(q - 1, k - 1) - mpf(10) ** (-40):
                okT = False; print("  fold-T fail", k, n, q)
print("fold-A 항등식:", okA, " fold-R (7.14):", okR, " fold-T:", okT, " (7.15):", okL1, " prop-PF 안쪽 항등식:", okPF)

# borel-monotone, kernel-bound 수치
okbm = True
for m in range(1, 3000):
    if not (Bor(m + 1) < Bor(m)): okbm = False
    if not (mpf(m + 1) ** 1.5 * Bor(m + 2) > mpf(m) ** 1.5 * Bor(m + 1)): okbm = False
    if not (Bor(m + 2) / Bor(m + 1) >= exp(-mpf(3) / (2 * (m + 1)))): okbm = False
print("borel-monotone (가)(나)(다) m<3000:", okbm)
def ke(s_, m):
    s_ = mpf(s_); m = mpf(m)
    return 3 * (s_ + 1) / (2 * (m + 1)) + (s_ + 1) * (3 * s_ + 2) / (12 * (m + 1) ** 2) + (s_ + 1) ** 2 / (2 * (m + 1) * (m - s_)) + (s_ + 1) ** 4 / (12 * (m + 1) ** 2 * (m - s_))
okke = True; worst = mpf(0)
for m in range(1, 150):
    for s_ in range(0, m):
        pim = mpf(comb(m, s_)) * mpf(m - s_) ** (m - s_ - 1) * mpf(s_ + 1) ** (s_ - 1) / mpf(m + 1) ** (m - 1)
        bnd = Bor(s_ + 1) * exp(ke(s_, m))
        if pim > bnd: okke = False; print("  kernel-bound fail", m, s_)
        worst = max(worst, pim / bnd)
print("kernel-bound m<150:", okke, " max ratio pi/bound =", float(worst))
