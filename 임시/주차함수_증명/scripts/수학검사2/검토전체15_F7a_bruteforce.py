# F7a 검산 1: 7.4절·7.5절의 항등식을 작은 (n,k)에서 결과 순열 전수로 확인한다.
# (7.2),(7.3),(7.4),mom_k=-k x_k,(7.5),(7.13) chi,(fold-A),(7.14),(7.10),heavy-block,(7.9)의 bd 값,
# 블록 지수 공식 (7.6)·(7.7)·K''=POS^G+X'', Green 원자 J_n(z)<=J^G_n(z).
from fractions import Fraction as Fr
from itertools import permutations
from math import comb, factorial
import sys

def caps(sigma):
    n = len(sigma); h = []
    for i in range(n):
        j = i - 1
        while j >= 0 and sigma[j] < sigma[i]:
            j -= 1
        h.append(i - j)  # i-h = j (0-based j -> 1-based j+1 ... distance i-j)
    return h

def stats(n, k):
    """return dict: A_{n,l} for l in range, moments under Pr^sigma_{n,k}, J_n(z) poly coeffs, K_{n,k}(z) poly coeffs."""
    A = {}
    Zf = Fr(0); ZH = Fr(0); ZZ = Fr(0); tot = 0
    Kpoly = {}   # z-exponent -> sum of prod_{h<=k} h
    Jpoly = {}   # z-exponent -> sum H k^{H-1} prod_{h<k} h
    Zdist = {}
    for sig in permutations(range(1, n + 1)):
        h = caps(sig)
        for l in range(0, n + 2):
            w = 1
            for hi in h: w *= min(hi, l + 1)
            A[l] = A.get(l, 0) + w
        w = 1
        for hi in h: w *= min(hi, k)
        Z = sum(1 for hi in h if hi > k); H = sum(1 for hi in h if hi == k)
        tot += w; Zf += w * Z; ZH += w * H; ZZ += w * Z * (Z - 1)
        pk = 1
        for hi in h:
            if hi <= k: pk *= hi
        Kpoly[Z] = Kpoly.get(Z, 0) + pk
        pl = 1
        for hi in h:
            if hi < k: pl *= hi
        if H >= 1:
            Jpoly[Z] = Jpoly.get(Z, 0) + H * k ** (H - 1) * pl
    return dict(A=A, tot=tot, Zf=Zf / tot, ZH=ZH / tot, ZZ=ZZ / tot, K=Kpoly, J=Jpoly)

def polyval(p, z):
    return sum(c * Fr(z) ** e for e, c in p.items())
def polyd(p):
    return {e - 1: c * e for e, c in p.items() if e >= 1}

def p_(m): return (m + 1) ** (m - 1) if m >= 1 else 1
ok = True
def check(name, cond):
    global ok
    if not cond:
        ok = False; print("FAIL:", name)

for k in (2, 3, 4):
    NMAX = 8 if k <= 3 else 8
    S = {n: stats(n, k) for n in range(1, NMAX + 1)}
    S[0] = dict(A={l: 1 for l in range(0, 20)}, tot=1, Zf=Fr(0), ZH=Fr(0), ZZ=Fr(0), K={0: 1}, J={})
    def Ank(n, l):
        if l < 0: return 0
        if n == 0: return 1
        if l >= n: return p_(n)
        return S[n]['A'][l]
    a = lambda m: Fr(Ank(m, k - 1), factorial(m))
    def P(n, j):  # root position law
        return Fr(min(j, k) * comb(n - 1, j - 1) * Ank(j - 1, k - 1) * Ank(n - j, k - 1), Ank(n, k - 1))
    for n in range(1, NMAX + 1):
        # (7.2)
        check(f"(7.2) k={k} n={n}", n * a(n) == sum(min(p, k) * a(p - 1) * a(n - p) for p in range(1, n + 1)))
        check(f"P sums to 1 k={k} n={n}", sum(P(n, p) for p in range(1, n + 1)) == 1)
        # Pr(pos_n=j | M<=k-1) check: P^{(k)}_n(j) = min(j,k)/j * P_n(j) * s_{j-1}s_{n-j}/s_n
        for j in range(1, n + 1):
            Pm = Fr(j * comb(n - 1, j - 1) * p_(j - 1) * p_(n - j), p_(n))
            s = lambda m: Fr(Ank(m, k - 1), p_(m))
            check(f"P rel k={k} n={n} j={j}", P(n, j) == Fr(min(j, k), j) * Pm * s(j - 1) * s(n - j) / s(n))
        # (7.3)
        Zf = lambda m: S[m]['Zf']; ZH = lambda m: S[m]['ZH']; ZZ = lambda m: S[m]['ZZ']
        check(f"(7.3a) k={k} n={n}", Zf(n) == sum(P(n, p) * ((1 if p > k else 0) + Zf(p - 1) + Zf(n - p)) for p in range(1, n + 1)))
        check(f"(7.3b) k={k} n={n}", ZH(n) == sum(P(n, p) * ((1 if p == k else 0) + ZH(p - 1) + ZH(n - p)) for p in range(1, n + 1)))
        check(f"(7.3c) k={k} n={n}", ZZ(n) == sum(P(n, p) * (ZZ(p - 1) + ZZ(n - p) + 2 * Zf(p - 1) * Zf(n - p) + 2 * (1 if p > k else 0) * (Zf(p - 1) + Zf(n - p))) for p in range(1, n + 1)))
        # initial values
        if n <= k: check(f"Zf0 k={k} n={n}", Zf(n) == 0)
        if n < k: check(f"ZH0 k={k} n={n}", ZH(n) == 0)
        if n <= k + 1: check(f"ZZ0 k={k} n={n}", ZZ(n) == 0)
    # cnt_n(m)
    cnt = {}
    def CNT(n, m):
        if (n, m) in cnt: return cnt[(n, m)]
        if n < m: v = Fr(0)
        elif n == m: v = Fr(1)
        else: v = sum(P(n, p) * (CNT(p - 1, m) + CNT(n - p, m)) for p in range(1, n + 1))
        cnt[(n, m)] = v; return v
    def g(m, p): return (1 if p > k else 0) + Zf(p - 1) + Zf(m - p)
    def yv(m): return sum(P(m, p) * g(m, p) ** 2 for p in range(1, m + 1)) - Zf(m) ** 2
    def mom(m):
        return 2 * sum(P(m, p) * Zf(p - 1) * Zf(m - p) for p in range(1, m + 1)) + 2 * sum(P(m, p) * (Zf(p - 1) + Zf(m - p)) for p in range(k + 1, m + 1)) - k * (P(m, k) if m >= k else 0)
    xk = Fr(k ** (k - 1), (k + 1) ** (k - 1))
    for n in range(1, NMAX + 1):
        Var = ZZ(n) + Zf(n) - Zf(n) ** 2
        check(f"(7.4) Var k={k} n={n}", Var == sum(CNT(n, m) * yv(m) for m in range(1, n + 1)))
        check(f"(7.4) kZH k={k} n={n}", k * ZH(n) == sum(CNT(n, m) * k * P(m, k) for m in range(k, n + 1)))
        ET = ZZ(n) - k * ZH(n)
        check(f"(7.4) ET k={k} n={n}", ET == Zf(n) * (Zf(n) - 1) + sum(CNT(n, m) * (yv(m) - k * P(m, k)) for m in range(k, n + 1)))
        check(f"(7.4) mom k={k} n={n}", ET == sum(CNT(n, m) * mom(m) for m in range(k, n + 1)))
    check(f"mom_k=-k x_k k={k}", mom(k) == -k * xk)
    # (7.5): d_{n,k} >= K''(k) - B >= K''(k) - J_n(k-1); check K''(k)=2E2 via polys and inequality
    for n in range(1, NMAX + 1):
        Kp = S[n]['K']; Jp = S[n]['J']
        check(f"K(k)=A k={k} n={n}", polyval(Kp, k) == Ank(n, k - 1))
        check(f"K(k+1)=A k={k} n={n}", polyval(Kp, k + 1) == Ank(n, k))
        d = Ank(n, k) - 2 * Ank(n, k - 1) + Ank(n, k - 2)
        K2 = polyval(polyd(polyd(Kp)), k)
        check(f"(7.5) k={k} n={n}", d >= K2 - polyval(Jp, k - 1))
        # K'(k) = A Zf/k, K''(k)=A ZZ/k^2
        check(f"K'(k) k={k} n={n}", polyval(polyd(Kp), k) == Ank(n, k - 1) * Zf(n) / k)
        check(f"K''(k) k={k} n={n}", K2 == Ank(n, k - 1) * ZZ(n) / k ** 2)
    # (7.13) one-step identity with chi
    def cl_plus(m): return Fr(Ank(m, k) - Ank(m, k - 1), Ank(m, k - 1))
    def cl_minus(m): return Fr(Ank(m, k - 1) - Ank(m, k - 2), Ank(m, k - 1))
    def mu(m): return cl_plus(m) - cl_minus(m)
    def chi(m, j):
        I = 1 if j > k else 0; E = 1 if j == k else 0
        return Fr(1, k) * (-E * (1 - cl_minus(m - k)) + I * (cl_plus(j - 1) + cl_minus(j - 1) + cl_plus(m - j) + cl_minus(m - j))) if m >= k else Fr(0)
    def chi_full(m, j):
        I = 1 if j > k else 0
        base = chi(m, j)
        return base + (1 + Fr(I, k)) * cl_plus(j - 1) * cl_plus(m - j) + (1 - Fr(I, k)) * cl_minus(j - 1) * cl_minus(m - j)
    def src(m): return sum(P(m, j) * chi_full(m, j) for j in range(1, m + 1))
    for m in range(1, NMAX + 1):
        check(f"(7.13) k={k} m={m}", mu(m) == src(m) + sum(P(m, j) * (mu(j - 1) + mu(m - j)) for j in range(1, m + 1)))
        if m <= k - 1: check(f"(7.13) zero k={k} m={m}", mu(m) == 0 and src(m) == 0)
    check(f"mu_k=-p_{{k-1}}/p_k k={k}", mu(k) == -Fr(p_(k - 1), p_(k)))
    # fold-A: src = Eu (thr+heavy+quad)
    import math
    # use exact rationals by factoring e: define at_m = e^{-m} a_m; e cancels if we track powers: thr,heavy,quad each carry e^{-(n-1)} * e-powers... we check with floats instead.
    E = math.e
    at = lambda m: E ** (-m) * float(a(m))
    atp = lambda m: E ** (-m) * Ank(m, k) / factorial(m)
    atm = lambda m: E ** (-m) * Ank(m, k - 2) / factorial(m)
    Bor = lambda m: E ** (-m) * m ** (m - 1) / factorial(m)
    for n in range(k, NMAX + 1):
        Eu = E ** (-1) / (n * at(n))
        thr = -E * Bor(k) * atm(n - k)
        heavy = sum(at(n - 1 - m) * (atp(m) - atm(m)) * (1 + (1 if n - 1 - m >= k else 0)) for m in range(k, n))
        quad = sum(min(j, k + 1) * (atp(j - 1) - at(j - 1)) * (atp(n - j) - at(n - j)) + min(j, k - 1) * (at(j - 1) - atm(j - 1)) * (at(n - j) - atm(n - j)) for j in range(1, n + 1))
        lhs = float(src(n)); rhs = Eu * (thr + heavy + quad)
        check(f"fold-A k={k} n={n} {lhs} vs {rhs}", abs(lhs - rhs) <= 1e-12 * max(1, abs(lhs)))
        # P = Eu min(j,k) at at
        for j in range(1, n + 1):
            check(f"P Boltzmann k={k} n={n} j={j}", abs(float(P(n, j)) - Eu * min(j, k) * at(j - 1) * at(n - j)) < 1e-12)
        # fold-R (7.14) for nu>=1
        nu = n - 2 * k
        if nu >= 1:
            sib = lambda q: at(n - 1 - k - q)
            for B in range(nu + 1, n - 1 - k + 1):
                l = n - 1 - k - B
                L = sum(sib(q) * (atp(k + q) - atm(k + q)) for q in range(nu - 1, B + 1))
                ed1 = E * Bor(k + 1) * atp(n - 1 - k); ed2 = E * Bor(k) * atp(n - k)
                up = E * Bor(l + 2) * atm(n - 2 - l) + E * Bor(l + 1) * atm(n - 1 - l)
                inn = sum(sib(q + 1) * atp(k + q + 1) - sib(q - 1) * atm(k + q - 1) for q in range(nu, B))
                R = ed1 + ed2 + inn - up
                check(f"(7.14) k={k} n={n} B={B}", abs(L - R) < 1e-12 * max(1, abs(L)))
                check(f"sib_q=eBor k={k} n={n} B={B}", all(abs(sib(q) - E * Bor(n - k - q)) < 1e-12 for q in range(nu - 1, B + 1)))
    # (7.10) and heavy-block for q in 1..min(k+2, NMAX-k+1)
    def s_(m): return Fr(Ank(m, k - 1), p_(m))
    def pi(m, j): return Fr(comb(m, j) * j ** (j - 1) * p_(m - j), p_(m))
    for q in range(1, k + 3):
        m = k + q - 1
        if m > NMAX: break
        sq = s_(m)
        if q == 1: check(f"s_1=1 k={k}", sq == 1)
        else:
            rhs = sum(pi(m, j) * (Fr(j - k, j) + Fr(k, j) * (1 - s_(j - k + k - 1 + 0))) for j in range(k + 1, k + q))
            # careful: s_{j-k}(k) in deficit coords = s_{k+(j-k)-1}(k) = s_{j-1}(k)
            rhs = sum(pi(m, j) * (Fr(j - k, j) + Fr(k, j) * (1 - s_(j - 1))) for j in range(k + 1, k + q))
            check(f"(7.10) k={k} q={q}", 1 - sq == rhs)
        pis = Fr(q * (q - 1), 2 * (k + 1))
        check(f"(라) tail<=pi# k={k} q={q}", 1 - sq <= pis)
        t = k + q
        if t - 1 <= NMAX:
            ex = Fr(t * p_(t - 1), Ank(t - 1, k - 1)) - k
            check(f"(나) ex k={k} q={q}", ex == q + (k + q) * (1 - sq) / sq and ex >= q)
            check(f"(가) Zf<=q-1 k={k} q={q}", 0 <= Zf(t - 1) <= q - 1 and 0 <= ZZ(t - 1) <= (q - 1) * (q - 2))
            # bd values
            Kp = S[t - 1]['K']
            bd = lambda z: z * polyval(Kp, z) - t ** (t - 1)
            A1 = Ank(t - 1, k - 1)
            check(f"bd_t(k) k={k} q={q}", bd(k) == -A1 * ex)
            bdp = polyval(Kp, k) + k * polyval(polyd(Kp), k)
            check(f"bd'_t(k) k={k} q={q}", bdp == A1 * (1 + Zf(t - 1)))
            bdpp = 2 * polyval(polyd(Kp), k) + k * polyval(polyd(polyd(Kp)), k)
            check(f"bd''_t(k) k={k} q={q}", bdpp == Fr(A1, k) * (2 * Zf(t - 1) + ZZ(t - 1)))
    # Block exponential formula (7.6), X'' identity, Green atom: power series with Fraction coefficients in x, polynomial in z (use sympy)
    import sympy as sp
    z, x = sp.symbols('z x')
    N = NMAX + 1
    # K_{n,k}(z) by the 4.3 recursion (verified against brute force for n<=NMAX)
    def W(g): return sp.Integer(g) if g <= k else z
    Kz = {0: sp.Integer(1)}
    for n in range(1, N + 1):
        Kz[n] = sp.expand(sum(sp.binomial(n - 1, j) * W(j + 1) * Kz[j] * Kz[n - 1 - j] for j in range(0, n)))
    for n in range(1, NMAX + 1):
        check(f"K recursion=brute k={k} n={n}", sp.expand(Kz[n] - sum(sp.Integer(c) * z ** e for e, c in S[n]['K'].items())) == 0)
    Dser = sum(Kz[n] * x ** n / sp.factorial(n) for n in range(0, N + 1))
    T = sum(sp.Integer(t ** (t - 1)) * x ** t / sp.factorial(t) for t in range(1, N + 2))
    Tle = sum(sp.Integer(t ** (t - 1)) * x ** t / sp.factorial(t) for t in range(1, k + 1))
    Elt = sum(sp.Integer(p_(j)) * x ** j / sp.factorial(j) for j in range(0, k))
    Dge = sp.expand(Dser - Elt)
    rhs76 = sp.series(sp.exp(Tle + z * sp.integrate(Dge, (x, 0, x))), x, 0, N + 1).removeO()
    check(f"(7.6) k={k}", sp.expand(sp.series(Dser - rhs76, x, 0, N + 1).removeO()) == 0)
    eT = sp.series(sp.exp(T), x, 0, N + 1).removeO()
    Qk = sp.expand(sp.series((1 - T) * (eT - Elt), x, 0, N + 1).removeO())
    Sc = [sp.Integer(0)] * (N + 1)
    Qc = [Qk.coeff(x, i) for i in range(N + 1)]
    eTc = [eT.coeff(x, i) for i in range(N + 1)]
    for i in range(0, N):
        Sc[i + 1] = sp.expand((Qc[i] + z * sum(eTc[a] * Sc[i - a] for a in range(0, i + 1))) / (i + 1))
    Sser = sum(Sc[i] * x ** i for i in range(N + 1))
    Gstar = sp.expand(sp.series(Elt + Qk + z * eT * Sser, x, 0, N + 1).removeO())
    check(f"G* form k={k}", sp.expand(sp.series(Gstar - eT * (1 - (T - Tle) + z * sp.integrate(Gstar - Elt, (x, 0, x))), x, 0, N + 1).removeO()) == 0)
    for n in range(1, N + 1):
        POS = sp.factorial(n) * sp.diff(Gstar.coeff(x, n), z, 2).subs(z, k)
        K2 = sp.diff(Kz[n], z, 2).subs(z, k)
        if n <= 2 * k + 1:
            check(f"POS^G=K'' k={k} n={n}", sp.expand(K2 - POS) == 0)
        else:
            Xn2 = sp.factorial(n) * sp.diff(sp.expand(Dser - Gstar).coeff(x, n), z, 2).subs(z, k)
            check(f"K''=POS+X'' k={k} n={n}", sp.expand(K2 - POS - Xn2) == 0)
    Xser = sp.expand(Dser - Gstar)
    low = min([i for i in range(N + 1) if sp.expand(Xser.coeff(x, i)) != 0] or [N + 1])
    check(f"X starts at 2k+2 k={k} (low={low})", low >= 2 * k + 2)
    bd = sp.expand(z * sp.integrate(Dge, (x, 0, x)) - (T - Tle))
    rhs77 = sp.expand(sp.series(sp.exp(Tle) * (z * sp.integrate(Xser, (x, 0, x)) + bd ** 2 / 2), x, 0, N + 1).removeO())
    for i in range(0, min(N - 1, 3 * k + 2) + 1):
        check(f"(7.7) coeff x^{i} k={k}", sp.expand(Xser.coeff(x, i) - rhs77.coeff(x, i)) == 0)
    if 3 * k + 3 <= N - 1:
        check(f"(7.7) fails at 3k+3 as expected k={k}", sp.expand(Xser.coeff(x, 3 * k + 3) - rhs77.coeff(x, 3 * k + 3)) != 0)
    # bd_t(z) = z K_{t-1}(z) - t^{t-1}
    for t in range(k + 1, N + 2):
        check(f"bd_t coefficient k={k} t={t}", sp.expand(sp.factorial(t) * bd.coeff(x, t) - (z * Kz[t - 1] - t ** (t - 1))) == 0)
    # Green atom
    gc = [sp.Integer(0)] * (N + 1)
    for i in range(0, N):
        src_i = sp.Rational(p_(k - 1), sp.factorial(k - 1)) if i == k - 1 else 0
        gc[i + 1] = sp.expand((src_i + z * sum(eTc[a] * gc[i - a] for a in range(0, i + 1))) / (i + 1))
    gser = sum(gc[i] * x ** i for i in range(N + 1))
    JG = sp.expand(sp.series(eT * gser, x, 0, N + 1).removeO())
    for n in range(0, NMAX + 1):
        JGn = sp.expand(sp.factorial(n) * JG.coeff(x, n))
        Jn = sum(sp.Integer(c) * z ** e for e, c in S[n]['J'].items()) if n >= 1 else 0
        if n <= 2 * k:
            check(f"J=J^G n<=2k k={k} n={n}", sp.expand(JGn - Jn) == 0)
        for zz in [sp.Rational(i, 2) for i in range(0, 2 * k + 3)]:
            check(f"J<=J^G k={k} n={n} z={zz}", (JGn - Jn).subs(z, zz) >= 0)
        # (7.8) d >= K''(k) - J^G(k-1)
        if n >= 1:
            d = Ank(n, k) - 2 * Ank(n, k - 1) + Ank(n, k - 2)
            check(f"(7.8) k={k} n={n}", sp.Rational(d) >= sp.diff(Kz[n], z, 2).subs(z, k) - JGn.subs(z, k - 1))
    print(f"k={k} done")
print("ALL OK" if ok else "SOME FAIL")
