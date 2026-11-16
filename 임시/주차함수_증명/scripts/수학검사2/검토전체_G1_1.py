# 검토전체 G1: 1장·2장 수치·항등식 검산 (python -I)
from fractions import Fraction
from itertools import permutations, product
from math import comb, factorial
import mpmath as mp

mp.mp.dps = 60


def p(n):
    return (n + 1) ** (n - 1) if n >= 1 else 1


# ---------- A: 마지막 차 재귀로 A_{n,l}, b_{n,l} ----------
def A_table(N):
    A = {}
    for l in range(-1, N + 1):
        A[(0, l)] = 1 if l >= 0 else 0
    for n in range(1, N + 1):
        A[(n, -1)] = 0
        for l in range(0, N + 1):
            s = 0
            for j in range(n):
                s += comb(n - 1, j) * min(j + 1, l + 1) * A[(j, l)] * A[(n - 1 - j, l)]
            A[(n, l)] = s
    return A


def b(A, n, l):
    return A[(n, l)] - A[(n, l - 1)]


# ---------- B: 직접 열거 (n<=7) ----------
def park(alpha):
    n = len(alpha)
    occ = [0] * (n + 1)
    pos = [0] * n
    for i, a in enumerate(alpha):
        j = a
        while j <= n and occ[j]:
            j += 1
        if j > n:
            return None
        occ[j] = i + 1
        pos[i] = j
    return pos, occ


def enumerate_pf(n):
    out = []
    for alpha in product(range(1, n + 1), repeat=n):
        r = park(alpha)
        if r is not None:
            pos, occ = r
            disp = [pos[i] - alpha[i] for i in range(n)]
            out.append((alpha, pos, occ[1:], disp))
    return out


def h_of(sigma):
    n = len(sigma)
    h = []
    for i in range(1, n + 1):
        z = 0
        for j in range(1, i):
            if sigma[j - 1] > sigma[i - 1]:
                z = j
        h.append(i - z)
    return h


def unimodal(seq):
    i = 0
    while i + 1 < len(seq) and seq[i] <= seq[i + 1]:
        i += 1
    while i + 1 < len(seq) and seq[i] >= seq[i + 1]:
        i += 1
    return i + 1 == len(seq)


def main(fast=False):
    N = 12
    A = A_table(N)
    if fast:
        tail_only(); return
    print("== 1.3절 표 ==")
    table = {
        1: [1], 2: [2, 1], 3: [6, 7, 3], 4: [24, 51, 34, 16], 5: [120, 421, 377, 253, 125],
        6: [720, 3963, 4594, 3688, 2546, 1296],
        7: [5040, 42253, 62145, 57398, 46142, 32359, 16807],
        8: [40320, 505515, 929856, 979430, 865970, 702292, 497442, 262144],
        9: [362880, 6724381, 15298809, 18289811, 17520519, 15455851, 12587507, 8977273, 4782969],
        10: [3628800, 98618763, 275075236, 371706836, 385131546, 359973796, 318092120, 259627152, 186093442, 100000000],
    }
    for n, row in table.items():
        comp = [b(A, n, l) for l in range(n)]
        ok = comp == row and sum(row) == p(n)
        # 가장 작은 증인
        w = max(range(n), key=lambda l: (row[l], -l))
        print(n, "OK" if ok else ("MISMATCH", comp), "sum", sum(row) == p(n), "l*=", w, "unimodal", unimodal(row))
    print("1.4절: d_{n,k_n} 부호 (2<=n<=12)")
    for n in range(2, N + 1):
        kn = (n + 1) // 2
        d = b(A, n, kn) - b(A, n, kn - 1)
        print(" n=%d k_n=%d d=%d" % (n, kn, d))

    print("== 2.1-2.2: 섬유 곱 구조와 n<=6 섬유 단봉성, 정리 2-5 ==")
    for n in range(1, 7):
        pfs = enumerate_pf(n)
        assert len(pfs) == p(n)
        fibers = {}
        for alpha, pos, sigma, disp in pfs:
            fibers.setdefault(tuple(sigma), []).append(disp)
        allok = True
        for sigma, disps in fibers.items():
            h = h_of(sigma)
            # 곱 구조
            assert len(disps) == eval("*".join(map(str, h))) if n > 0 else True
            site_disps = set()
            for alpha, pos, sg, disp in pfs:
                if tuple(sg) == sigma:
                    site_disps.add(tuple(disp[sg[i] - 1] for i in range(n)))
            assert site_disps == set(product(*[range(hi) for hi in h])), (sigma, h)
            row = []
            for l in range(n):
                row.append(sum(1 for d in disps if max(d) == l))
            if not unimodal(row):
                allok = False
        print(" n=%d: 모든 섬유 단봉 = %s (섬유 %d개)" % (n, allok, len(fibers)))
    sigma = (1, 2, 3, 5, 4, 6, 7)
    h = h_of(sigma)
    Asig = [1]
    for l in range(7):
        v = 1
        for hi in h:
            v *= min(hi, l + 1)
        Asig.append(v)
    row = [Asig[l + 1] - Asig[l] for l in range(7)]
    print(" 정리 2-5: h=", h, "A^sigma=", Asig[1:], "row=", row, "unimodal", unimodal(row))
    for n in (8, 9):
        sp = tuple(list(range(n - 6, n - 3)) + [n - 2, n - 3, n - 1, n] + list(range(n - 7, 0, -1)))
        hh = h_of(sp)
        print(" sigma' n=%d:" % n, sp, "h=", hh)

    print("== 2.7: 동률-막힘 항등식 d=2E-B, 따름 2-29, 보조정리 2-30 (n<=6 brute) ==")
    for n in range(1, 7):
        pfs = enumerate_pf(n)
        for k in range(1, n + 1):
            E = E2 = Bk1 = 0
            for alpha, pos, sigma, disp in pfs:
                M = max(disp)
                cnt = sum(1 for d in disp if d == M)
                if M == k and cnt % 2 == 0:
                    E += 1
                if M == k and cnt == 2:
                    E2 += 1
                if M == k - 1:
                    h = h_of(sigma)
                    # 변위 M인 차의 자리 i: pos[car]=i
                    blocked = all(h[pos[c] - 1] == M + 1 for c in range(n) if disp[c] == M)
                    if blocked:
                        Bk1 += 1
            d = b(A, n, k) - b(A, n, k - 1)
            assert d == 2 * E - Bk1, (n, k, d, E, Bk1)
            assert 2 * E2 - Bk1 <= d
            # 보조정리 2-30 첫 식
            s = 0
            Jn = 0
            for sigma in permutations(range(1, n + 1)):
                h = h_of(sigma)
                Z = sum(1 for x in h if x > k)
                H = sum(1 for x in h if x == k)
                pr = 1
                for x in h:
                    if x < k:
                        pr *= x
                s += pr * (k - 1) ** Z * (k ** H - (k - 1) ** H)
                Jn += H * k ** (H - 1) * (k - 1) ** Z * pr if H >= 1 else 0
            assert s == Bk1, (n, k, s, Bk1)
            if n <= 2 * k - 1:
                assert Jn == Bk1
            if n == 2 * k:
                assert Jn - Bk1 == comb(2 * k - 1, k - 1) * p(k - 1) ** 2, (n, k, Jn, Bk1)
        print(" n=%d OK" % n)

    print("== 2.7: 보조정리 J-egf (가) 재귀 vs 직접 (k=2,3,4; n<=2k) ==")
    # 다항식: dict deg->int
    def padd(a, b_):
        r = dict(a)
        for d_, c in b_.items():
            r[d_] = r.get(d_, 0) + c
        return {d_: c for d_, c in r.items() if c != 0}

    def pmul(a, b_):
        r = {}
        for d1, c1 in a.items():
            for d2, c2 in b_.items():
                r[d1 + d2] = r.get(d1 + d2, 0) + c1 * c2
        return {d_: c for d_, c in r.items() if c != 0}

    def pscale(a, s):
        return {d_: c * s for d_, c in a.items() if c * s != 0}

    for k in (2, 3, 4):
        Jdirect = {}
        for n in range(0, 2 * k + 1):
            poly = {}
            for sigma in permutations(range(1, n + 1)):
                h = h_of(sigma)
                Z = sum(1 for x in h if x > k)
                H = sum(1 for x in h if x == k)
                if H == 0:
                    continue
                pr = 1
                for x in h:
                    if x < k:
                        pr *= x
                poly = padd(poly, {Z: H * k ** (H - 1) * pr})
            Jdirect[n] = poly
        Jrec = {0: {}}
        for n in range(0, 2 * k):
            s = {}
            for i in range(0, n + 1):
                term = pmul({1: 1, 0: i + 1}, Jrec[n - i])
                s = padd(s, pscale(term, comb(n, i) * p(i)))
            if n >= k - 1:
                s = padd(s, {0: comb(n, k - 1) * p(k - 1) * p(n - k + 1)})
            Jrec[n + 1] = s
        ok = all(Jrec[n] == Jdirect[n] for n in range(0, 2 * k + 1))
        print(" k=%d: 재귀 == 직접 (n<=2k): %s" % (k, ok))

    print("== 2.5: 명제 2-20 유한 n 상계 ==")

    def v(k, Z, H):
        return (1 + mp.mpf(1) / k) ** Z + (1 - mp.mpf(1) / k) ** (Z + H) - 2

    def lg(n):
        return mp.loggamma(n + 1)

    for n in (17, 100, 1000, 10000):
        best = None
        for bb in range(3, 40):
            # 조건: 3<=i<=bb, n/2<k<=n 에서 v_k(i-1,1)<0
            cond = True
            for i in range(3, bb + 1):
                for kk in range(n // 2 + 1, n + 1):
                    if v(kk, i - 1, 1) >= 0:
                        cond = False
                        break
                if not cond:
                    break
            if not cond:
                break
            S1 = mp.mpf(0)
            S2 = mp.mpf(0)
            for c in range(n // 2 + 1, n + 1):
                kap = n - c - bb + 1
                if kap < 0:
                    continue
                base = lg(n) - lg(c) + (c - 1) * mp.log(c) - lg(kap) - (n - 1) * mp.log(n + 1)
                t1 = mp.e ** (base) * bb * mp.mpf(n - c + 1) ** (n - c - bb)
                t2 = mp.e ** (base) * 2 * mp.mpf(n - c - bb + 3) ** (n - c - bb)
                S1 += t1
                S2 += t2
            rhs = 1 - S1 + S2
            if best is None or rhs < best[0]:
                best = (rhs, bb, S1, S2)
        print(" n=%d: 최소 상계 %s (b=%d, Pr(S_b>n/2)=%s)" % (n, mp.nstr(best[0], 6), best[1], mp.nstr(best[2], 6)))

    print("== 2.12: 정리 moving-tail (아) D=2,3 sanity; (사) ==")
    A2 = A_table(104)
    for D in (2, 3):
        n = int(mp.ceil(20 * D ** 1.5))
        row = [b(A2, n, l) for l in range(n)]
        chain = all(row[n - r - 1] > row[n - r] for r in range(1, D))
        print(" D=%d n=%d chain OK: %s" % (D, n, chain))
    n = 60
    for r in (1, 2, 3, 5):
        d = b(A2, n, n - r) - b(A2, n, n - r - 1)
        Ren = mp.mpf(r + 1) ** (r + 1) * mp.e ** (-(r + 1)) / mp.factorial(r + 1)
        lhs = abs(mp.mpf(-d) / mp.mpf(n) ** (n - 2) - mp.e * Ren)
        print(" n=60 r=%d |..|=%s <= 60(r+1)/n=%s" % (r, mp.nstr(lhs, 5), mp.nstr(mp.mpf(60 * (r + 1)) / n, 5)))

    print("== 2.9: Ren/Psi, (G1) 항등식, theta 항등식 ==")
    Ren = lambda j: mp.mpf(j) ** j * mp.e ** (-j) / mp.factorial(j) if j >= 1 else mp.mpf(1)
    Bor = lambda m: mp.e ** (-m) * mp.mpf(m) ** (m - 1) / mp.factorial(m)
    Psi = lambda q: sum((Ren(j) for j in range(1, q + 1)), mp.mpf(0))
    for q in (1, 2, 5, 10):
        lhs = sum((Bor(m) * Psi(q - m) for m in range(1, q + 1)), mp.mpf(0))
        rhs = Psi(q) - sum((Bor(m) for m in range(1, q + 1)), mp.mpf(0))
        print(" q=%d G1 diff=%s  Psi<=0.7979 sqrt q: %s" % (q, mp.nstr(lhs - rhs, 5), Psi(q) <= mp.mpf('0.7979') * mp.sqrt(q)))
    for (t, k) in ((5, 3), (9, 4), (12, 5)):
        th = mp.mpf(comb(t, k)) * mp.mpf(k) ** (k - 1) * mp.mpf(t - k) ** (t - k) / mp.mpf(t) ** (t - 1)
        print(" theta_%d(%d)=%s  Ren*Bor/Bor=%s" % (t, k, mp.nstr(th, 12), mp.nstr(Ren(t - k) * Bor(k) / Bor(t), 12)))
    # 2-19 극한 확인: n=2000, b=3, (u,o1,o2)=(0,1,0)
    print("== 2.5: 보조정리 2-18 수 / p_n vs Bor 극한 (n=3000) ==")
    n = 3000
    for (u, os_) in ((0, (0, 0)), (1, (0, 1)), (2, (1, 0))):
        bb = len(os_) + 1
        c = n - u - (bb - 1) - sum(os_)
        logc = lg(n) - lg(u) - sum(lg(o) for o in os_) - lg(c) + (u - 1) * mp.log(u + 1) + sum((o - 1) * mp.log(o + 1) for o in os_) + (c - 1) * mp.log(c) - (n - 1) * mp.log(n + 1)
        lim = Bor(u + 1) * mp.fprod(Bor(o + 1) for o in os_)
        print(" (u;o)=", (u, os_), mp.nstr(mp.e ** logc, 8), "->", mp.nstr(lim, 8))


def tail_only():
    print("== 2.12: 정리 moving-tail (아) D=2,3 sanity; (사) ==")
    A2 = A_table(104)
    for D in (2, 3):
        n = int(mp.ceil(20 * D ** 1.5))
        row = [b(A2, n, l) for l in range(n)]
        chain = all(row[n - r - 1] > row[n - r] for r in range(1, D))
        print(" D=%d n=%d chain OK: %s" % (D, n, chain))
    n = 60
    for r in (1, 2, 3, 5):
        d = b(A2, n, n - r) - b(A2, n, n - r - 1)
        Ren = mp.mpf(r + 1) ** (r + 1) * mp.e ** (-(r + 1)) / mp.factorial(r + 1)
        lhs = abs(mp.mpf(-d) / mp.mpf(n) ** (n - 2) - mp.e * Ren)
        print(" n=60 r=%d |..|=%s <= 60(r+1)/n=%s" % (r, mp.nstr(lhs, 5), mp.nstr(mp.mpf(60 * (r + 1)) / n, 5)))
    print("== 2.9: Ren/Psi, (G1) 항등식, theta 항등식 ==")
    Ren = lambda j: mp.mpf(j) ** j * mp.e ** (-j) / mp.factorial(j) if j >= 1 else mp.mpf(1)
    Bor = lambda m: mp.e ** (-m) * mp.mpf(m) ** (m - 1) / mp.factorial(m)
    Psi = lambda q: sum((Ren(j) for j in range(1, q + 1)), mp.mpf(0))
    for q in (1, 2, 5, 10):
        lhs = sum((Bor(m) * Psi(q - m) for m in range(1, q + 1)), mp.mpf(0))
        rhs = Psi(q) - sum((Bor(m) for m in range(1, q + 1)), mp.mpf(0))
        print(" q=%d G1 diff=%s  Psi<=0.7979 sqrt q: %s" % (q, mp.nstr(lhs - rhs, 5), Psi(q) <= mp.mpf('0.7979') * mp.sqrt(q)))
    for (t, k) in ((5, 3), (9, 4), (12, 5)):
        th = mp.mpf(comb(t, k)) * mp.mpf(k) ** (k - 1) * mp.mpf(t - k) ** (t - k) / mp.mpf(t) ** (t - 1)
        print(" theta_%d(%d)=%s  Ren*Bor/Bor=%s" % (t, k, mp.nstr(th, 12), mp.nstr(Ren(t - k) * Bor(k) / Bor(t), 12)))
    print("== 2.5: 보조정리 2-18 수 / p_n vs Bor 극한 (n=3000) ==")
    lg = lambda n: mp.loggamma(n + 1)
    n = 3000
    for (u, os_) in ((0, (0, 0)), (1, (0, 1)), (2, (1, 0))):
        bb = len(os_) + 1
        c = n - u - (bb - 1) - sum(os_)
        logc = lg(n) - lg(u) - sum(lg(o) for o in os_) - lg(c) + (u - 1) * mp.log(u + 1) + sum((o - 1) * mp.log(o + 1) for o in os_) + (c - 1) * mp.log(c) - (n - 1) * mp.log(n + 1)
        lim = Bor(u + 1) * mp.fprod(Bor(o + 1) for o in os_)
        print(" (u;o)=", (u, os_), mp.nstr(mp.e ** logc, 8), "->", mp.nstr(lim, 8))
    # 2.9 정리 2-38 (iii)/(iv), 따름 2-39(c) 수치 확인: k=200, q<=20
    print("== 2.9: 정리 2-38 (ii)(iii)(iv), 2-39(c)(d) 수치 (k=60, q<=30) ==")
    k = 60
    A3 = A_table(2 * k + 2)
    def N(l, t):
        return min(t, l + 1) * A3[(t - 1, l)]
    def x_t(t):
        return mp.mpf(N(k, t) - 2 * N(k - 1, t) + N(k - 2, t)) / mp.mpf(t) ** (t - 1)
    def theta(t):
        return mp.mpf(comb(t, k)) * mp.mpf(k) ** (k - 1) * mp.mpf(t - k) ** (t - k) / mp.mpf(t) ** (t - 1) if t > k else mp.mpf(1)
    ok2 = ok3 = ok4 = True
    P = mp.mpf(0)
    okc = okd = True
    for q in range(0, 31):
        t = k + q
        kx = k * x_t(t)
        th = theta(t)
        if kx < -th - mp.mpf(10) ** -40: ok2 = False
        if kx > -th + (2 * q * q + q) * mp.cosh(mp.mpf(q) / k) / k + mp.mpf(10) ** -40: ok3 = False
        if not (Ren(q) - mp.mpf(10)**-40 <= th <= Ren(q) * (1 + mp.mpf(q) / k) ** mp.mpf(1.5) + mp.mpf(10)**-40): ok4 = False
        P += x_t(t)
        bc = mp.cosh(1) / k * sum(2 * qq * qq + qq for qq in range(q + 1)) + 3 * mp.mpf(q) ** 1.5 / k
        if abs(k * P + 1 + Psi(q)) > bc + mp.mpf(10)**-40: okc = False
        if k * P < -(1 + mp.mpf(q) / k) ** mp.mpf(1.5) * (1 + Psi(q)) - mp.mpf(10)**-40: okd = False
    print(" (ii) %s (iii) %s (iv) %s 2-39(c) %s 2-39(d) %s" % (ok2, ok3, ok4, okc, okd))
    print(" x_k(k) = %s (should be -1/k = %s)" % (mp.nstr(x_t(k), 10), mp.nstr(-mp.mpf(1) / k, 10)))
    kx1 = k * x_t(k + 1)
    print(" k x_{k+1}(k) = %s ; closed -(k-1)k^{k-1}/(k+1)^k = %s" % (mp.nstr(kx1, 12), mp.nstr(-mp.mpf(k - 1) * mp.mpf(k) ** (k - 1) / mp.mpf(k + 1) ** k, 12)))
    # 2.10 다섯 몫 분해 수치 확인: k=5, n in [11,14]
    print("== 2.10: 다섯 몫 분해 (k=5, 2k+1<=n<=3k-1) ==")
    k = 5
    A4 = A_table(3 * k)
    def Nl(l, t):
        return min(t, l + 1) * A4[(t - 1, l)] if t >= 1 else 0
    bT = lambda t, l: Nl(l, t) - Nl(l - 1, t)
    for n in range(2 * k + 1, 3 * k):
        d = A4[(n, k)] - 2 * A4[(n, k - 1)] + A4[(n, k - 2)]
        Theta = comb(n, k) * k ** (k - 2) * A4[(n - k, k - 1)]
        FL = sum(comb(n, t) * (bT(t, k) - bT(t, k - 1)) * A4[(n - t, k - 1)] for t in range(k + 1, 2 * k + 2))
        BV = sum(comb(n, m + 1) * p(n - 1 - m) * (b(A4, m, k) + b(A4, m, k - 1)) for m in range(2 * k + 1, n))
        KD = sum(comb(n, m + 1) * p(n - 1 - m) * k * (b(A4, m, k) - b(A4, m, k - 1)) for m in range(2 * k + 1, n))
        PAIR = Fraction(0)
        for t1 in range(1, n + 1):
            for t2 in range(1, n + 1 - t1):
                PAIR += Fraction(factorial(n), factorial(t1) * factorial(t2) * factorial(n - t1 - t2)) * (bT(t1, k) * bT(t2, k) + bT(t1, k - 1) * bT(t2, k - 1)) * p(n - t1 - t2)
        PAIR /= 2
        print(" n=%d: d=%d  -Theta+FL+BV+KD+PAIR=%s  OK=%s" % (n, d, -Theta + FL + BV + KD + PAIR, d == -Theta + FL + BV + KD + PAIR))


import sys
main(fast=("fast" in sys.argv))
