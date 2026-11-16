# 검토전체9 O3: brute-force checks of 5.2.1 identities for small n
from itertools import permutations, product
from fractions import Fraction
from math import comb, factorial

def p(m): return (m + 1) ** (m - 1) if m >= 1 else 1

def Gamma_list(dmax, y, n):
    G = [Fraction(1)]
    for d in range(1, dmax + 1):
        s = Fraction(comb(n, d) * p(d))
        for j in range(d):
            s += y * comb(n - d + j, j) * p(j) * G[d - 1 - j]
        G.append(s)
    return G

def caps(sigma):
    # h_i = i - z_i, z_i = position of nearest larger element to the left (0 if none)
    n = len(sigma); h = []
    for i in range(n):
        z = 0
        for j in range(i - 1, -1, -1):
            if sigma[j] > sigma[i]:
                z = j + 1; break
        h.append((i + 1) - z)
    return h

def park(a):
    n = len(a); spots = [0] * n; disp = [0] * n
    for car, pref in enumerate(a, 1):
        s = pref - 1
        while s < n and spots[s]: s += 1
        if s >= n: return None
        spots[s] = car; disp[car - 1] = s - (pref - 1)
    return spots, disp

def brute(n):
    # returns dict: b[l], E[k], E2[k], B[m]
    b = {}; E = {}; E2 = {}; B = {}
    for a in product(range(1, n + 1), repeat=n):
        res = park(a)
        if res is None: continue
        spots, disp = res
        M = max(disp); cnt = disp.count(M)
        b[M] = b.get(M, 0) + 1
        if cnt % 2 == 0: E[M] = E.get(M, 0) + 1
        if cnt == 2: E2[M] = E2.get(M, 0) + 1
        h = caps(spots)
        # blocked: every car with disp M stands at spot i with h_i = M+1
        blocked = all(h[i] == M + 1 for i in range(n) if disp[spots[i] - 1] == M)
        if blocked: B[M] = B.get(M, 0) + 1
    return b, E, E2, B

def K(n, k, y):
    tot = Fraction(0)
    for sigma in permutations(range(1, n + 1)):
        h = caps(sigma); pr = Fraction(1)
        for hi in h: pr *= hi if hi <= k else y
        tot += pr
    return tot

def A(n, l):
    if n == 0: return 1
    tot = 0
    for sigma in permutations(range(1, n + 1)):
        pr = 1
        for hi in caps(sigma): pr *= min(hi, l + 1)
        tot += pr
    return tot

def phi(m, k):
    # forests on m labels all trees size <= k  == K_{m,k}(0)
    return K(m, k, Fraction(0)) if m >= 1 else Fraction(1)

ok = True
for n in range(1, 8):
    b, E, E2, B = brute(n)
    for k in range(1, n + 1):
        d = b.get(k, 0) - b.get(k - 1, 0)
        if d != 2 * E.get(k, 0) - B.get(k - 1, 0):
            ok = False; print("2-28 fail", n, k)
        # K(k+1)-2K(k)+K(k-1) = 2E
        if K(n, k, k + 1) - 2 * K(n, k, k) + K(n, k, k - 1) != 2 * E.get(k, 0):
            ok = False; print("2nd diff fail", n, k)
        if K(n, k, k - 1) - A(n, k - 2) != B.get(k - 1, 0) and k >= 1:
            # A(n,-1)=0
            pass
    # green-connection (다): K_{n,k}(y)-K_{n,k+1}(y) = (y-k-1) p_k Gamma_{n-k-1}(y;n), k+1<=n<=2k+1
    for k in range(1, n):
        if not (k + 1 <= n <= 2 * k + 1): continue
        for y in [Fraction(2), Fraction(7, 3), Fraction(-1)]:
            lhs = K(n, k, y) - K(n, k + 1, y)
            G = Gamma_list(n - k - 1, y, n)
            rhs = (y - k - 1) * p(k) * G[n - k - 1]
            if lhs != rhs: ok = False; print("(다) fail", n, k, y)
        # B_{n,k} = p_k Gamma_{n-k-1}(k;n)
        G = Gamma_list(n - k - 1, Fraction(k), n)
        if B.get(k, 0) != p(k) * G[n - k - 1]: ok = False; print("B fail", n, k)
        # (라) b_{n,k} = sum_{m=k}^{n-1} A_{m,k} Gamma_{n-m-1}(k;n)
        s = sum(A(m, k) * G[n - m - 1] for m in range(k, n))
        if b.get(k, 0) != s: ok = False; print("(라) fail", n, k)
    # source-rep (가): K_{n,k}(y) = phi_n + y sum_{m=k}^{n-1} phi_m Gamma_{n-m-1}(y;n), n<=2k+1
    for k in range(1, n + 1):
        if n > 2 * k + 1: continue
        for y in [Fraction(3), Fraction(5, 2)]:
            G = Gamma_list(n - k - 1 if n - k - 1 >= 0 else 0, y, n)
            rhs = phi(n, k) + y * sum(phi(m, k) * G[n - m - 1] for m in range(k, n))
            if K(n, k, y) != rhs: ok = False; print("(가) fail", n, k, y)
    # source-rep (다): S = sum phi [Gamma+ sd(k) - Gamma- sd(k+1)], k+2<=n<=2k-1
    for k in range(1, n + 1):
        if not (k + 2 <= n <= 2 * k - 1): continue
        r = n - k
        Gp = p(k) * Gamma_list(r - 1, Fraction(k + 2), n)[r - 1]
        Gm = p(k - 1) * Gamma_list(r, Fraction(k - 1), n)[r]
        d1 = b.get(k, 0) - b.get(k - 1, 0); d2 = b.get(k + 1, 0) - b.get(k, 0)
        S = Gp * d1 - Gm * d2
        def hg(dd, y): return y * Gamma_list(dd, y, n)[dd]
        def sd(dd, y): return hg(dd, y + 1) - 2 * hg(dd, y) + hg(dd, y - 1)
        S2 = sum(phi(n - dd - 1, k) * (Gp * sd(dd, Fraction(k)) - Gm * sd(dd, Fraction(k + 1))) for dd in range(1, r))
        if S != S2: ok = False; print("(다)S fail", n, k, S, S2)
        if Gm != B.get(k - 1, 0): ok = False; print("Gamma- != B", n, k)
        if d1 != 2 * E.get(k, 0) - Gm: ok = False; print("d=2E-Gm fail", n, k)
    print("n", n, "done; b=", [b.get(l, 0) for l in range(n)])
print("ALL OK" if ok else "FAILURES")

# suff-cond (가) numeric: V_r(k-1) <= (1+1/r)^r V_{r-1}(k)
def tw(j): return Fraction(1) if j == 1 else Fraction((j - 1) ** (j - 1), factorial(j))
def Vd(cos):
    V = [Fraction(1)]
    for dd in range(1, len(cos) + 1):
        s = (1 + cos[dd - 1]) * V[dd - 1]
        for j in range(2, dd + 1): s += tw(j) * V[dd - j]
        V.append(s)
    return V[-1]
for (r, k) in [(2, 3), (3, 5), (5, 8), (8, 20), (12, 40)]:
    n = k + r
    lhs = Vd([Fraction(k - 1, n - i + 1) for i in range(1, r + 1)])
    rhs = Fraction(r + 1, r) ** r * Vd([Fraction(k, n - i + 1) for i in range(1, r)])
    print("suff(가)", r, k, float(lhs), float(rhs), lhs <= rhs)
