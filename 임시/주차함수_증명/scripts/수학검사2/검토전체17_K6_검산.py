# 검토전체17 K6 (장7A) 검산 스크립트. python -I 로 실행.
# 1) 7.1 t_k, n^sharp; 2) old-6-6/6-7/6-10/6-11/riccati 소규모 전수 확인;
# 3) column-lemma(가) 정수 부등식; 4) self-consistent-S 표 재계산; 5) cor-S-prime 값;
# 6) prime-decomposition: C_{n,n}, rho_k; 7) polar-N 상수.
from fractions import Fraction as Fr
from itertools import permutations
from math import log, exp, factorial, comb, sqrt, cosh, e as E, ceil
import sys

out = []
def P(*a):
    out.append(" ".join(str(x) for x in a))

# ---------- 기본 도구 ----------
def caps(sig):
    n = len(sig); h = []
    for i in range(n):
        z = 0
        for j in range(i - 1, -1, -1):
            if sig[j] > sig[i]:
                z = j + 1; break
        h.append(i + 1 - z)
    return h

def A_exact(n, l):
    # A_{n,l} = sum_sigma prod min(h_i, l+1); A_{0,l}=1; A_{n,-1}=0
    if l < 0: return 0
    if n == 0: return 1
    return sum_over(n, lambda h: prod(min(hi, l + 1) for hi in h))

def prod(it):
    p = 1
    for x in it: p *= x
    return p

_cache = {}
def sum_over(n, f):
    if n not in _cache:
        _cache[n] = [caps(s) for s in permutations(range(1, n + 1))]
    return sum(f(h) for h in _cache[n])

# A_{n,l} via Theorem 2-6 recursion (fast, exact)
from functools import lru_cache
@lru_cache(None)
def A(n, l):
    if l < 0: return 0
    if n == 0: return 1
    return sum(comb(n - 1, j) * min(j + 1, l + 1) * A(j, l) * A(n - 1 - j, l) for j in range(n))

def d(n, k): return A(n, k) - 2 * A(n, k - 1) + A(n, k - 2)

# ---------- 1) t_k ----------
def t_k(k):
    j = 0
    while not ((k + 1) ** j * k ** (j + 1) + (k - 1) ** (2 * j + 1) >= 2 * k ** (2 * j + 1)):
        j += 1
    return j
P("[1] t_k, n#_k:", [(k, t_k(k), k + (k + 1) * t_k(k)) for k in range(2, 13)])
P("    check 1<=t_k<=k:", all(1 <= t_k(k) <= k for k in range(2, 60)))
# 반감 경계 뒤의 d>0 소규모 확인
bad = [(n, k) for k in range(2, 7) for n in range(k + (k + 1) * t_k(k), k + (k + 1) * t_k(k) + 15) if d(n, k) <= 0]
P("    d_{n,k}>0 for n>=n#_k (k<=6, 15 rows):", "OK" if not bad else bad)

# ---------- 2) 소규모 전수 확인 (n<=8) ----------
def stats(n, k):
    # returns list of (weight, Z, H) over sigma
    res = []
    for h in (_cache.setdefault(n, [caps(s) for s in permutations(range(1, n + 1))])):
        w = prod(min(hi, k) for hi in h)
        Z = sum(1 for hi in h if hi > k); H = sum(1 for hi in h if hi == k)
        res.append((w, Z, H))
    return res

ok66 = ok_fm = ok67 = ok610 = True; eq610 = True
for n in range(1, 9):
    for k in range(2, n + 2):
        st = stats(n, k); W = sum(w for w, _, _ in st)
        EZ = Fr(sum(w * Z for w, Z, _ in st), W); EH = Fr(sum(w * H for w, _, H in st), W)
        EZZ = Fr(sum(w * Z * (Z - 1) for w, Z, _ in st), W)
        m = Fr(n - k, k + 1)
        if k <= n and EZ < m: ok66 = False; P("  6-6 FAIL", n, k, EZ, m)
        if n >= 2 * k + 1 and EZZ < m * (m - 1): ok_fm = False; P("  fm FAIL", n, k)
        Rs = Fr(A(n, k), A(n, k - 1)); Rf = Fr(A(n, k - 2), A(n, k - 1))
        ok = log(1 - 1 / k); osk = -2 * log(1 - 1 / k) / log(1 + 1 / k)
        if not (float(Rf) > (1 - 1 / k) * float(Rs) ** (-osk) + 1e-15): ok67 = False; P("  6-7 FAIL", n, k)
        if k <= n:
            xk = Fr(k, k + 1) ** (k - 1)
            if k * EH > xk * n: ok610 = False; P("  6-10 FAIL", n, k)
            if n == k and k * EH != xk * n: eq610 = False; P("  6-10 eq FAIL", n, k)
P("[2] old-6-6:", ok66, " factorial-moment(iota=2):", ok_fm, " old-6-7 strict:", ok67, " old-6-10:", ok610, " eq at n=k:", eq610)

# old-6-11 (가): E[H_k] = (n+1) a_{k-1} sum_{j=k+1}^{n+1} K_j a_{n+1-j}/a_n  with K from recursion
def pf(i): return (i + 1) ** (i - 1) if i >= 1 else 1
def a(m, k): return Fr(A(m, k - 1), factorial(m))
def Kcoef(k, J):
    # j K_j = sum_{m=1}^{k-1} (k-m) a0_{m-1} K_{j-m} + [j=k+1]
    K = [Fr(0)] * (J + 1)
    for j in range(1, J + 1):
        s = Fr(1 if j == k + 1 else 0)
        for m in range(1, k):
            if j - m >= 0: s += (k - m) * Fr(pf(m - 1), factorial(m - 1)) * K[j - m]
        K[j] = s / j
    return K
ok611 = True
for k in range(2, 6):
    K = Kcoef(k, 10)
    for n in range(1, 9):
        st = stats(n, k); W = sum(w for w, _, _ in st); EH = Fr(sum(w * H for w, _, H in st), W)
        rhs = (n + 1) * a(k - 1, k) * sum(K[j] * a(n + 1 - j, k) for j in range(k + 1, n + 2)) / a(n, k)
        if EH != rhs: ok611 = False; P("  6-11 FAIL", n, k, EH, rhs)
P("    K_{k+1}=1/(k+1):", all(Kcoef(k, k + 2)[k + 1] == Fr(1, k + 1) for k in range(2, 7)), " old-6-11(가):", ok611)

# riccati counterexample (k,z,n)=(3,1,2): LHS n! coefficient 4 vs RHS 5 — 직접 확인(위 본문 손계산 대신 급수)
def series_mul(a_, b_, N): return [sum(a_[i] * b_[n - i] for i in range(n + 1)) for n in range(N + 1)]
def series_exp_neg(Q, N):  # exp(-Q) for Q with Q[0]=0
    R = [Fr(0)] * (N + 1); R[0] = Fr(1)
    # R' = -Q' R
    for n in range(1, N + 1):
        s = Fr(0)
        for i in range(1, n + 1): s += i * Q[i] * R[n - i]
        R[n] = -s / n
    return R
def series_int(F, N): return [Fr(0)] + [F[n - 1] / n for n in range(1, N + 1)]
def series_inv(F, N):
    R = [Fr(0)] * (N + 1); R[0] = 1 / F[0]
    for n in range(1, N + 1): R[n] = -sum(F[i] * R[n - i] for i in range(1, n + 1)) / F[0]
    return R
def riccati_rhs(k, z, N):
    Q = [Fr(0)] * (N + 1)
    for j in range(0, k - 1): Q[j + 1] = Fr((k - 1 - j) * ((j + 1) ** (j - 1) if j >= 1 else 1), factorial(j + 1))
    Ex = series_exp_neg(Q, N); Dl = [Fr(1)] + [-k * x for x in series_int(Ex, N)[1:]]
    Ak = series_mul(Ex, series_inv(Dl, N), N)
    O = [Fr(0)] * (N + 1); O[z] = Fr(min(z, k) * A(z - 1, k - 1), factorial(z - 1)) / z
    t1 = series_mul(Ak, O, N)
    inner = series_int(series_mul(O, Ex, N), N)
    t2 = series_mul(series_mul([k * x for x in Ex], series_mul(series_inv(Dl, N), series_inv(Dl, N), N), N), inner, N)
    return [t1[n] + t2[n] for n in range(N + 1)]
def Yz_lhs(k, z, n):
    st = [(prod(min(hi, k) for hi in h), sum(1 for hi in h if hi == z)) for h in _cache.setdefault(n, [caps(s) for s in permutations(range(1, n + 1))])]
    return Fr(sum(w * H for w, H in st), factorial(n))
P("    riccati (3,1,2): LHS*2! =", Yz_lhs(3, 1, 2) * 2, " RHS*2! =", riccati_rhs(3, 1, 2)[2] * 2)
okR = all(Yz_lhs(k, z, n) == riccati_rhs(k, z, 7)[n] for k in range(2, 5) for z in range(k - 1, 7) for n in range(1, 8))
P("    riccati z>=k-1 (k<=4,n<=7):", okR)

# ---------- 3) column-lemma (가) ----------
P("[3] 10^21*400^10 > 17^21*123^10:", 10 ** 21 * 400 ** 10 > 17 ** 21 * 123 ** 10, 10 ** 21 * 400 ** 10, 17 ** 21 * 123 ** 10)
P("    17^21 <6.95e25:", 17 ** 21 < 6.95e25, " 123^10<7.93e20:", 123 ** 10 < 7.93e20, " 8.36^5:", 8.36 ** 5, " 1.513^5:", 1.513 ** 5)
def hf(xi, k):
    o = -2 * log(1 - 1 / k) / log(1 + 1 / k); return xi - 2 + (1 - 1 / k) * xi ** (-o)
P("    hf(1.7,k) for k=41,100,1000:", [round(hf(1.7, k), 6) for k in (41, 100, 1000)], " o_41=", -2 * log(1 - 1 / 41) / log(1 + 1 / 41))
P("    (40/41)(10/17)^2.1 =", (40 / 41) * (10 / 17) ** 2.1)

# ---------- 4) self-consistent-S 표 ----------
def a0(m): return Fr((m + 1) ** (m - 1), factorial(m)) if m >= 1 else Fr(1)
def free_ratio(m): return float(a0(m + 1) / a0(m))  # e^{g(m+1)}
def jstar(L):
    m = 0
    while free_ratio(m + 1) < L: m += 1
    return m
def kR(L):
    j = jstar(L); return max(2 * j + 2, ceil(float(Fr(L) ** (j + 2) / a0(j + 1))))
import mpmath as mp
mp.mp.dps = 40
for (L, J, k0, Rtab, Xitab, Xiktab, A0tab, B0tab) in [(Fr(267, 100), 25, 501, 0.02499107, 0.749711, 0.736245, 1.4708, 0.098505),
                                                    (Fr(27, 10), 70, 1855, 0.00880166, 0.854757, 0.849132, 2.5335, 0.060259),
                                                    (Fr(271, 100), 100, 6098, 0.00569075, 0.865504, 0.862859, 2.7354, 0.0422)]:
    js = jstar(float(L)); kr = kR(float(L))
    Lm = mp.mpf(L.numerator) / L.denominator
    a0m = lambda m: mp.mpf((m + 1) ** (m - 1)) / mp.factorial(m) if m >= 1 else mp.mpf(1)
    Elow = mp.fsum(a0m(J + i) / a0m(J) * mp.e ** (-i) for i in range(1, k0 - js + 1))
    Einf = (Lm / mp.e) * (1 - (Lm / mp.e) ** k0) / (1 - Lm / mp.e)
    RJ = max(1 / (1 + Elow), 1 / (1 + Einf))
    xk0 = (mp.mpf(k0) / (k0 + 1)) ** (k0 - 1)
    def qlow(x): return max(mp.mpf(0), 1 - mp.fsum(a0m(j) * Lm ** (-(j + 1)) for j in range(x)))
    Xi = mp.fsum(max(mp.mpf(0), a0m(x) * Lm ** (-(x + 1)) - RJ * qlow(x)) for x in range(J))
    Xik = mp.fsum(max(mp.mpf(0), a0m(x) * xk0 * Lm ** (-x) - RJ * qlow(x)) for x in range(J))
    A0 = xk0 + Xik / (Lm * (1 - Xi)); B0 = RJ * (1 + Xik / (1 - Xi))
    P(f"[4] L={L}: j*={js} (table {[82,220,490][[Fr(267,100),Fr(27,10),Fr(271,100)].index(L)]}), k_R={kr}, R_J={mp.nstr(RJ,9)} (tab {Rtab}), Xi={mp.nstr(Xi,7)} (tab {Xitab}), Xi(k0)={mp.nstr(Xik,7)} (tab {Xiktab}), A0={mp.nstr(A0,6)} (tab {A0tab}), B0={mp.nstr(B0,6)} (tab {B0tab})")
    # cor-S-prime
    y = {501: Fr(13, 100), 1855: Fr(2, 25), 6098: Fr(11, 200)}[k0]
    xi = mp.mpf(1) / k0; ym = mp.mpf(y.numerator) / y.denominator
    g_tab = (ym - xi) * (ym - 2 * xi - xi ** 2) - (1 + xi) ** 2 * (A0tab * xi + B0tab * ym)
    g_exact = (ym - xi) * (ym - 2 * xi - xi ** 2) - (1 + xi) ** 2 * (A0 * xi + B0 * ym)
    nv = ((3 * xi + xi ** 2) / 2 + (1 + xi) ** 2 * B0tab / 2)
    P(f"    cor-S': g(yk^2)/k^4 with table A0,B0 = {mp.nstr(g_tab,6)}, with computed = {mp.nstr(g_exact,6)}; n_v/k^2 = {mp.nstr(nv,5)} <= y={float(y)}; yk^2-2k-1>0: {float(y)*k0*k0-2*k0-1>0}")

# ---------- 6) prime decomposition ----------
# C_{n,n} = (n-1)^{n-1} via 1 - e^{-T}
N = 8
T = [Fr(0)] + [Fr(n ** (n - 1), factorial(n)) for n in range(1, N + 1)]
Cinf = [-x for x in series_exp_neg(T, N)]; Cinf[0] = Fr(0)
P("[6] C_{n,n} from 1-e^{-T}:", [Cinf[n] * factorial(n) for n in range(1, N + 1)], " vs (n-1)^{n-1}:", [(n - 1) ** (n - 1) if n > 1 else 1 for n in range(1, N + 1)])
# C_k = 1 - 1/A_{k-1}; check C_{n,k}>=0, C_{1,k}=1, C_{n,k}=C_{n,n} for n<=k; rho_k numerics
def Ck_coeffs(k, N):
    Ak = [Fr(A(n, k - 1), factorial(n)) for n in range(N + 1)]
    inv = series_inv(Ak, N); return [-x for x in inv[1:]]  # C_{n,k}/n!, n>=1
for k in range(1, 6):
    c = Ck_coeffs(k, 9)
    P(f"    k={k}: C_{{n,k}} =", [c[n - 1] * factorial(n) for n in range(1, 10)])
# rho_k via bisection on truncated C_k (N=60 for k<=5; crude but fine for checking 1/e<rho<=1, monotone, rho_2=log2)
def rho(k, N=80):
    c = Ck_coeffs(k, N)
    f = lambda x: sum(float(c[n - 1]) * x ** n for n in range(1, N + 1)) - 1
    lo, hi = 0.3, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if f(mid) > 0: hi = mid
        else: lo = mid
    return lo
rhos = [rho(k) for k in range(1, 7)]
P("    rho_k k=1..6:", [round(r, 6) for r in rhos], " log2=", round(log(2), 6), " 1/e=", round(1 / E, 6), " decreasing:", all(rhos[i] > rhos[i + 1] for i in range(5)))
# P_k(inf) = k a_{k-1} K(rho)/rho and compare with x_k
for k in range(2, 6):
    r = rhos[k - 1]; K = Kcoef(k, 200); Kr = sum(float(K[j]) * r ** j for j in range(k + 1, 201))
    Pinf = k * float(a(k - 1, k)) * Kr / r
    P(f"    k={k}: P_k(inf)={Pinf:.5f}  x_k={(k/(k+1))**(k-1):.5f}  ratio={Pinf/((k/(k+1))**(k-1)):.4f}")

# ---------- 7) polar-N constants ----------
k = 2001
P("[7] 2/sqrt(2001)=", 2 / sqrt(k), " e^{-1+2/2002}=", exp(-1 + 2 / (k + 1)), " 0.75/sqrt(k)=", 0.75 / sqrt(k), " e^-0.0448*(1-0.0085)*0.3678=", exp(-0.0448) * (1 - 0.0085) * 0.3678)
P("    2k^1.5+1 =", 2 * k ** 1.5 + 1, " 0.3476k^2=", 0.3476 * k * k, " y^2/(12(1-y^2)) at y=.0448:", 0.0448 ** 2 / (12 * (1 - 0.0448 ** 2)))
# polar-W dagger
k = 10 ** 7
P("    polar-W: 8.344/k^1.5 *k =", 8.344 / sqrt(k), " 8(1+0.91/sqrt k)^3=", 8 * (1 + 0.91 / sqrt(k)) ** 3, " 2sqrt(k)/(k+1)=", 2 * sqrt(k) / (k + 1))

# ---------- 8) flat-threshold n^flat vs n^sharp ----------
def phi(k, n):
    m = (n - k) / (k + 1); xk = (k / (k + 1)) ** (k - 1)
    return (1 + 1 / k) ** m + (1 - 1 / k) ** (m + xk * n / k) - 2
def nflat(k):
    n = 2 * k + 1
    while phi(k, n) < 0: n += 1
    return n
P("[8] (k, n^flat, n^sharp, 0.13k^2):", [(k, nflat(k), k + (k + 1) * t_k(k), round(0.13 * k * k)) for k in (2, 5, 10, 50, 100, 501)])

open(sys.argv[1], "w", encoding="utf-8").write("\n".join(out) + "\n")
