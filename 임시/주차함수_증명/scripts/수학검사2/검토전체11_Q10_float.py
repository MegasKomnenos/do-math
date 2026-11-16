# -*- coding: utf-8 -*-
"""Q10 float checks: chain DP for s_d(y), FLQ (ga)(na) directly at the four first columns,
DDL^natural, check-na table, check-ga table pieces, lemmas 8-25, 8-30, 8-31, 8-33 numerically."""
import numpy as np
from math import log, exp, sqrt, pi, lgamma, factorial
import mpmath as mp

# ---------- Borel ----------
def logBor(j):
    return -j + (j - 1) * log(j) - lgamma(j + 1)

def Bor(j):
    return exp(logBor(j))

LB = None
def prep_logBor(J):
    global LB
    j = np.arange(1, J + 1, dtype=float)
    LB = np.concatenate(([np.nan], -j + (j - 1) * np.log(j) - np.array([lgamma(x + 1) for x in j])))

def s_all(y, D):
    """return array S[d] = s_d(y) = s_{y+d-1}(y) for d=1..D via chain first-step recursion."""
    S = np.zeros(D + 1)
    S[1] = 1.0
    # Pr^y(q->q') = Bor(q-q')Bor(y+q')/Bor(y+q)
    for q in range(2, D + 1):
        qp = np.arange(1, q)
        lp = LB[q - qp] + LB[y + qp] - LB[y + q]
        pr = np.exp(lp)
        pi0 = 1.0 - pr.sum()
        S[q] = pi0 + np.sum(pr * (y / (y + qp)) * S[qp])
    return S

def check_dp_small():
    from fractions import Fraction as F
    from math import comb
    # exact A for y<=8
    def exactA(NMAX, LMAX):
        A = {}
        def getA(m, l):
            if l < 0: return F(0)
            return A[(m, l)]
        for l in range(0, LMAX + 1):
            A[(0, l)] = F(1)
            for m in range(1, NMAX + 1):
                A[(m, l)] = sum(F(comb(m - 1, j - 1)) * min(j, l + 1) * getA(j - 1, l) * getA(m - j, l) for j in range(1, m + 1))
        return getA
    getA = exactA(20, 9)
    prep_logBor(60)
    worst = 0
    for y in range(1, 9):
        S = s_all(y, y + 2)
        for d in range(1, y + 3):
            m = y + d - 1
            ex = float(getA(m, y - 1) / F((m + 1) ** (m - 1)))
            worst = max(worst, abs(ex - S[d]))
    print("DP vs exact (y<=8): max abs diff", worst)

# ---------- chapter-10 named functions ----------
def g(x): return (x - 1) * log(1 + 1 / x)
def u_k(k): return 3 / 0.35 * (1.35 + 1 / k) * (0.65 - 1 / k) ** -1.5 * k ** -0.5
def BdT(k, nu): return (k + nu) * u_k(k) * (1 / (k - 1) + 1 / k) + 3 * (k + 1) * (k - 1) ** -1.5
mS = 1.15
def s_up(d, y): return min(1.0, mS * (y + d) / d ** 1.5)
f1 = 4 / (3 * sqrt(2 * pi))
def s_low(d, y): return exp(-f1 * ((y + d - 1) / y) ** 1.5 * d ** 1.5 / y)
def e_c(k, nu): return 3 * nu ** 2 / ((k - 1) * k) + 4.8 * sqrt(nu) / k + nu ** 2 / (2 * (k - 1) ** 2)

# DDL^natural
qf = lambda rho: 1 + 0.7501 * rho / (1 + rho)
def j_integrals():
    mp.mp.dps = 30
    q = lambda r: 1 + mp.mpf('0.7501') * r / (1 + r)
    f2 = lambda r: mp.sqrt((1 + r) / r) * mp.mpf('0.70836') * q(r) ** 3
    f1_ = lambda r: f2(r) * (mp.mpf('2.528571') - mp.log(q(r)) + mp.mpf('1.5') * mp.log(r))
    j2 = mp.quad(f2, [0, mp.mpf('1e-6'), mp.mpf('0.01'), 1])
    j1 = mp.quad(f1_, [0, mp.mpf('1e-6'), mp.mpf('0.01'), 1])
    return float(j1), float(j2)

def DDLnat(k, j1, j2):
    dn = 2 * k ** (2 / 3)
    eps = -log(1 - sqrt(k + 1) / (0.485917 * k))
    epsp = 2.26 / k + 0.47 / (dn - 1)
    gam = 2.6047 * (2.53 + 0.5 * log(k) + eps + 1.5 / k) / k
    t1 = 0.457143 * (2 * pi) ** -0.5 * qf(dn / k) * sqrt(1 + dn / k) * (dn + 1) ** 3.5 / k ** 3
    t2 = 2 * (2 * pi) ** -0.5 * k ** -0.5 * (1 + epsp) * (j1 + (0.5 * log(k) + eps) * j2 + gam)
    t3 = 3.9 * (2 * pi) ** -0.5 / k
    return t1 + t2 + t3

# Stays^up(k; nubar) of Prop old-8-33
def cAb(rho): return 2 * sqrt(rho) / (1 - rho) + 2 * log((1 + sqrt(rho)) / (1 - sqrt(rho)))
def Sub(k, nubar):
    xi = (nubar + 4) / (k - 1)
    if xi >= 0.6: return 0.0
    f = lambda r: (r - xi) * (1 + r) * r ** -1.5 * (1 - r) ** -2
    return (k - 1) / k * float(mp.quad(f, [xi, 0.6]))
def Top(k, nubar):
    f = lambda r: min(2.0, 2 + (nubar + 1) / k - r) * (1 + r / 3) * r ** -1.5
    return float(mp.quad(f, [0.6 - 2.6 / k, 1]))
def Flat(y):
    ab = (mS * (y + 2 * y ** (2 / 3))) ** (2 / 3)
    return 2 * (ab - 1) / (y + 2 - ab)
def Ab(y, k, nubar):
    z = 0.6 + 1 / y
    return mS * (1 + 1 / y) * (4 * ((mS * y) ** (2 / 3) - 1) ** -0.5 + y ** -0.5 * (2 * cAb(z) - 4 * z ** -0.5 - Sub(k, nubar)))
def Stays_up(k, nubar):
    return sum(Flat(y) + Ab(y, k, nubar) for y in (k - 1, k)) + 2 * 16.54 * k ** -0.5 * Top(k, nubar)

# bulk majorants
def abar(k): return 3 * mS * (1.48 * k + 2) / (0.48 * k + 1) ** 1.5
def bbar(k): return 2 * u_k(k) * (2 * k - 1) / (k - 1) + 3 * (k + 1) * (k - 1) ** -1.5
def dbar(k): return 72.217 / sqrt(k)
def ebar(k):
    xip = (sqrt(5 * k * log(k)) + 2) / k
    return exp(1.5 / k) * (exp(sqrt(5 * log(k) / k) + 1 / k) + 2.40918 * k ** (1.5 - 2.5 / (1 + xip)))

def oF(fam, k, ddl):
    if fam == 'bulk': return 4 - ebar(k)
    if fam == '2':
        th0 = (2 * exp(-0.48) - 1) * exp(-0.48)
        return 4 - 3 * s_up(2 * k ** (2 / 3) + 1, k + 1) + th0 - BdT(k, 0.48 * k) - ddl
    if fam == '1b':
        xi2 = 2 * k ** (2 / 3) / (k - 1)
        return 4 - 3 * s_up(1.3 * k ** (2 / 3) + 1, k + 1) + (2 * exp(-xi2) - 1) * exp(-xi2) - BdT(k, 2 * k ** (2 / 3)) - ddl
    if fam == '1a':
        return 2 - e_c(k, 1.3 * k ** (2 / 3)) - BdT(k, 1.3 * k ** (2 / 3)) - ddl

def Rsharp(fam, k, ddl):
    if fam == 'bulk': return abar(k) + bbar(k) + ddl + dbar(k)
    if fam == '2': return 3 * s_up(2 * k ** (2 / 3) + 1, k + 1) + BdT(k, 0.48 * k) + ddl + Stays_up(k, 0.48 * k)
    if fam == '1b': return 3 * s_up(1.3 * k ** (2 / 3) + 1, k + 1) + BdT(k, 2 * k ** (2 / 3)) + ddl + Stays_up(k, 2 * k ** (2 / 3))
    if fam == '1a': return 3 + BdT(k, 1.3 * k ** (2 / 3)) + ddl + Stays_up(k, 1.3 * k ** (2 / 3))

def Rsharp_p(fam, k, ddl):
    nub = 1.3 * k ** (2 / 3) if fam == '1a' else 2 * k ** (2 / 3)
    return BdT(k, nub) + ddl + Stays_up(k, nub)

# Lemma old-8-31 / 8-32 lower bounds
cR = sqrt(2 * pi) / 2 * exp(1 / 12)
def Ren_star(j): return (2 * pi) ** -0.5 * j ** -0.5 * exp(-1 / (12 * j))
def A_up(q0, q): return sqrt(2 * pi) / 4 * exp(1 / (12 * (q0 - q))) * (q0 + q) * sqrt(q0 - q)
def PrBor_ge(q, cumBor):  # Pr(Bor>=q) = 1 - sum_{j<q} Bor(j)
    return 1.0 - cumBor[q - 1]

def e_low_R(k0, q0, Sy, cumBor):
    y = k0 + 1
    qs = np.arange(1, q0)
    zR = np.sum(np.array([Ren_star(q0 - q) for q in qs]) * np.exp(-(qs + np.array([A_up(q0, q) for q in qs])) / y) * Sy[1:q0])
    return k0 / (k0 + 1) * (1 - q0 / (2 * k0)) * (max(zR, Sy[q0] - PrBor_ge(q0, cumBor)) + Bor(q0))

def Qfun(y, xi):
    k = y - 1
    q0 = xi * y ** (2 / 3)
    pre = k / (k + 1) * (1 - q0 / (2 * k)) * 2 * (2 * pi) ** -0.5 * exp(-1 / 12) * y / (cR * q0)
    t1 = exp(-q0 / y) * s_low(q0, y) * (exp(-cR * q0 / y) - exp(-cR * q0 * sqrt(q0 / 2) / y))
    t2 = exp(-q0 / (2 * y)) * s_low(q0 / 2, y) * (exp(-cR * q0 * sqrt(q0 / 2 + 1) / y) - exp(-cR * q0 ** 1.5 / y))
    return pre * (t1 + t2)

def main():
    check_dp_small()
    j1, j2 = j_integrals()
    print("j1=", j1, "j2=", j2)
    print("3*sqrt2*0.16696=", 3 * sqrt(2) * 0.16696, " 2.5-log2-log0.485917=", 2.5 - log(2) - log(0.485917))
    for k in (6667, 6668, 8065, 9551, 9705):
        print("DDLnat(%d)=%.9f" % (k, DDLnat(k, j1, j2)))
    print("decrease cond j1+j2(log(6667)/2-1)=", j1 + j2 * (0.5 * log(6667) - 1))
    # gamma constant check and 3.9/k claim at k=6667..
    for k in (6667, 9705, 10 ** 5):
        qq = qf(1 + 1 / k)
        print("k=%d sqrt2*0.70836*q(1+1/k)^3=%.5f" % (k, sqrt(2) * 0.70836 * qq ** 3))
        dn = 2 * k ** (2 / 3)
        ds = np.arange(int(dn) + 1, k + 2)
        qd = 1 + 0.7501 * (ds - 1) / (k - 1 + ds)
        last = 2 * 0.72888 * (2 * pi) ** -0.5 * np.sum(qd ** 2 * np.sqrt(k - 1 + ds)) / k ** 2.5
        print("   last-term sum*2 = %.6g  vs 3.9(2pi)^-1/2/k = %.6g" % (last, 3.9 * (2 * pi) ** -0.5 / k))
    # ---- check-na table ----
    fams = [('bulk', 6668), ('2', 8065), ('1b', 9551), ('1a', 9705)]
    for fam, k0 in fams:
        ddl = DDLnat(k0, j1, j2)
        if fam == 'bulk':
            up = abar(k0) + bbar(k0) + ddl + dbar(k0)
            print(f"[na] bulk k0={k0}: oF={oF(fam,k0,ddl):.6f} abar={abar(k0):.6f} bbar={bbar(k0):.6f} DDL={ddl:.6f} dbar={dbar(k0):.6f} ebar={ebar(k0):.6f} up={up:.6f} margin={oF(fam,k0,ddl)-up:.6f}")
        else:
            nub = {'2': 0.48 * k0, '1b': 2 * k0 ** (2 / 3), '1a': 1.3 * k0 ** (2 / 3)}[fam]
            up = Stays_up(k0, nub)
            print(f"[na] fam {fam} k0={k0}: oF={oF(fam,k0,ddl):.6f} Stays_up={up:.6f} margin={oF(fam,k0,ddl)-up:.6f}  (Flat={Flat(k0):.5f} Ab={Ab(k0,k0,nub):.5f} Top-part={2*16.54*k0**-0.5*Top(k0,nub):.5f})")
    # ---- check-ga and direct FLQ at the first columns ----
    for fam, k0 in fams:
        ddl = DDLnat(k0, j1, j2)
        k = k0
        prep_logBor(3 * k + 10)
        D = k + 3
        S = {y: s_all(y, D) for y in (k - 1, k, k + 1)}
        for y in S: S[y][0] = 1.0  # s with deficit 0 (size y-1, capacity y) is 1
        eps0 = int(2 ** (2 / 3) * (k0 + 1) ** (2 / 3))
        cumBor = np.cumsum(np.concatenate(([0.0], np.exp(LB[1:eps0 + 5]))))
        Rs = Rsharp(fam, k0, ddl)
        Sy = S[k + 1]
        margins = []
        for q0 in range(2, eps0 + 1):
            elow = 4 * S[k][q0 + 1] + 2 * e_low_R(k0, q0, Sy, cumBor)
            margins.append(elow - Rs)
        margins = np.array(margins)
        print(f"[ga] fam {fam} k0={k0}: eps0={eps0} Rsharp={Rs:.6f} min(a)-margin={margins.min():.6f} at q0={2+int(margins.argmin())}")
        xicap = 1.3 if fam == '1a' else 2 ** (2 / 3)
        edge = 4 * s_low(xicap * (k0 + 1) ** (2 / 3) + 1, k0) + 2 * Qfun(k0 + 1, xicap)
        print(f"      (b) edge: {edge:.6f} margin={edge-Rs:.6f}")
        if fam in ('1a', '1b'):
            Rp = Rsharp_p(fam, k0, ddl)
            m2 = [e_low_R(k0, q0, Sy, cumBor) + S[k][q0 + 1] - Rp for q0 in range(104, eps0 + 1)]
            edge2 = Qfun(k0 + 1, 2 ** (2 / 3)) + s_low(2 ** (2 / 3) * (k0 + 1) ** (2 / 3) + 1, k0)
            print(f"      R'={Rp:.6f} (a) m0>N min margin={min(m2):.6f} at q0={104+int(np.argmin(m2))}; (b) m0>N margin={edge2-Rp:.6f}")
        # Lemma old-8-25 / old-8-30 numerical check at y=k+1 and y=k
        for y in (k - 1, k, k + 1):
            dd = np.arange(1, y + 3)
            sup = np.minimum(1.0, mS * (y + dd) / dd ** 1.5)
            slow = np.exp(-f1 * ((y + dd - 1) / y) ** 1.5 * dd ** 1.5 / y)
            Sv = S[y][1:y + 3]
            print(f"      y={y}: max(s-s_up)={np.max(Sv-sup):.3e} (<=0 ok), min(s-s_low)={np.min(Sv-slow):.3e} (>=0 ok)")
        # direct FLQ check at column k: (ga) T_m>=0 for all m in [k+2,2k], (na) for all nu in range
        # level masses: c_m(k) = s_m(k+1)-s_m(k) = S[k+1][m-k] - S[k][m-k+1]; c_m(k-1)= S[k][m-k+1]-S[k-1][m-k+2]
        ms = np.arange(k, 2 * k + 1)
        ck = S[k + 1][ms - k] - S[k][ms - k + 1]
        ck1 = S[k][ms - k + 1] - S[k - 1][ms - k + 2]
        # s_{2k}(k-1) is outside the chain-law range (d=k+2 > (k-1)+2); use the last-car recurrence
        # s_n(y) = sum_j P_n(j) (min(j,y)/j) s_{j-1}(y) s_{n-j}(y), P_n(j) = j C(n-1,j-1) p_{j-1} p_{n-j} / p_n
        n2 = 2 * k; yy = k - 1
        js = np.arange(1, n2 + 1, dtype=float)
        logP = (np.log(js) + lgamma(n2) - np.array([lgamma(j) for j in js]) - np.array([lgamma(n2 - j + 1) for j in js])
                + (js - 2) * np.log(js) + (n2 - js - 1) * np.log(n2 - js + 1) - (n2 - 1) * log(n2 + 1))
        Pn = np.exp(logP)
        def s_of(m, y):  # s_m(y) via S[y][m-y+1], valid for m-y+1 <= y+2
            d = m - y + 1
            return 1.0 if d <= 1 else S[y][d]
        sv = np.array([s_of(int(j) - 1, yy) * s_of(n2 - int(j), yy) for j in js])
        s2k_km1 = float(np.sum(Pn * np.minimum(js, yy) / js * sv))
        print(f"      check: sum P_n(j) = {Pn.sum():.12f}; s_2k(k-1) = {s2k_km1:.6e}; c_2k(k-1)={S[k][k+1]-s2k_km1:.6e}, u(k)/k={u_k(k)/k:.6e}")
        ck1[-1] = S[k][k + 1] - s2k_km1
        numin = max(103, 20001 - 2 * k)
        worst_na = None; worst_ga = None
        for nu in range(numin, k):  # n<3k
            n = 2 * k + nu; N = k + nu
            fm = np.where(ms <= N, 2 * ((k + 1) * ck - (k - 1) * ck1), (k + n - ms + 1) * ck - (k + n - ms - 1) * ck1)
            T = np.cumsum(fm[::-1])[::-1]  # T[m-k]
            ga_min = T[2:].min()
            # u_n / w_{k+1}
            sN_k1 = S[k + 1][N - k]      # s_N(k+1) = s_{(k+1)+ (N-k) -1}(k+1): d = N-k = nu
            sNm1_k = S[k][N - 1 - k + 1]  # s_{N-1}(k): d = N-1-k+1 = nu
            sNm2_k = S[k][nu - 1]         # s_{N-2}(k): d = nu-1
            u_over_wk = exp(g(N) - g(k)) * sN_k1 / sNm1_k
            wk1_over_wk = exp(g(k + 1) - g(N - 1)) * sNm2_k / sNm1_k
            u_over_wk1 = u_over_wk / wk1_over_wk
            if nu <= 0.48 * k:
                sN_k = S[k][nu + 1]       # s_N(k): d = N-k+1 = nu+1
                theta = 2 * (1 + 1 / k) * sN_k / sN_k1 - 1
            else:
                theta = -1.0
            na_val = T[0] + theta * u_over_wk1
            if worst_na is None or na_val < worst_na[0]: worst_na = (na_val, nu)
            if worst_ga is None or ga_min < worst_ga[0]: worst_ga = (ga_min, nu)
        print(f"      DIRECT FLQ at k={k}: min over nu of (na) value w_{{k+1}}^-1(w_{{k+1}}T_k+theta u) = {worst_na[0]:.5f} at nu={worst_na[1]}; min T_m (m>=k+2) = {worst_ga[0]:.3e} at nu={worst_ga[1]}")
        # Stays vs Stays_up at a few nu (Prop old-8-33 (i))
        def Stays(nu):
            N = k + nu
            vs = lambda m, l: S[l + 1][m + 1 - (l + 1) + 1] - S[l][m - l + 1]   # varsigma_m(l) = s_{m+1}(l+1) - s_m(l)
            tot = 2 * vs(N + 1, k)
            for m in range(N + 2, 2 * k + 1):
                tot += (2 - (m - N) / k) * (vs(m, k) + vs(m - 1, k - 1))
            return tot
        if fam != 'bulk':
            nub = {'2': 0.48 * k0, '1b': 2 * k0 ** (2 / 3), '1a': 1.3 * k0 ** (2 / 3)}[fam]
            lo = {'2': int(2 * k0 ** (2 / 3)) + 1, '1b': int(1.3 * k0 ** (2 / 3)) + 1, '1a': numin}[fam]
            vals = [(Stays(nu), nu) for nu in (lo, int(nub))]
            print(f"      Stays at nu={lo}: {vals[0][0]:.5f}, at nu={int(nub)}: {vals[1][0]:.5f}  vs Stays_up(k;nubar)={Stays_up(k0,nub):.5f}")
        else:
            print(f"      Stays at nu=ceil(0.48k)+1: {Stays(int(0.48*k)+2):.5f}, nu=k-1: {Stays(k-1):.5f} vs dbar={dbar(k):.5f}")

if __name__ == "__main__":
    main()
