# -*- coding: utf-8 -*-
"""Interval (directed-rounding) recomputation for appendix item D.{{D:four-families}}
(Propositions 10:check-na and 10:check-ga), written from the definitions of chapter 10.

Method.  mpmath `iv` (outward-rounded interval arithmetic), 30 decimal digits, everywhere.
  * Closed forms (o_F, Bd^T, u, s^up, e^c, bulk majorants, DDL^natural, Flat, Ab, R#, R#') are evaluated in `iv`.
  * The integrals Sub and Top of Proposition 10:old-8-33 are evaluated by exact antiderivatives in `iv`:
      Sub(k;nu) = (k-1)/k * 2 [G(sqrt 0.6) - G(sqrt xi)],  G(s) = xi/s + (1-xi) s/(1-s^2) - 2 xi atanh(s),  xi = (nu+4)/(k-1)
        (substitution rho = s^2 and partial fractions (u-xi)(1+u)/(u(1-u)^2) = -xi/u - (1+xi)/(1-u) + 2(1-xi)/(1-u)^2);
      Top(k;nu): for every family e := (nu+1)/k <= 0.6 - 2.6/k (checked in `iv`), so min(2, 2+e-rho) = 2+e-rho on the
        whole range and Top = [-2 a0 rho^(-1/2) + 2 a1 rho^(1/2) - (2/9) rho^(3/2)]_{0.6-2.6/k}^{1}, a0 = 2+e, a1 = a0/3 - 1.
  * j1, j2 inside DDL^natural are the enclosures certified by ../M_natural/j_integrals_iv.py
    (j2 in [2.717199867930190, 2.717199867930191], j1 in [0.7998716895841891, 0.7998716895841892]).
  * The first-layer survivals s_q(y) are computed by the chain first-step recursion of section 2.11 in `iv`:
      s_1 = 1,  s_q = 1 - sum_{q'<q} Bor(q-q') Bor(y+q')/Bor(y+q) * (1 - y/(y+q') s_q'),
    with log Bor(n) = (n-1) log n - n - sum_{j<=n} log j  (interval sum).  Pr(Bor >= q0) = 1 - sum_{j<q0} Bor(j).
  * (ga)(a) is evaluated for every 2 <= q0 <= eps0 (and 104 <= q0 <= eps0 for 1a, 1b); the minimum over q0 is the
    minimum of the certified lower endpoints.  (ga)(b) is a point evaluation.
  * Lemma 10:old-8-32(iii): the two analytic conditions are enclosed on 40000 interval cells covering [1.04, 2^(2/3)].
  * Monotonicity samples (same grids as the record): each consecutive pair is compared with certified intervals.
Run:  python -I families_iv.py   (output: families_iv_out.txt)
"""
import math
import time
from fractions import Fraction

import numpy as np
from mpmath import iv, mp, mpf

iv.dps = 30
mp.prec = 400                      # only for exact transfer of interval endpoints
F = iv.mpf
ONE = F(1)
ZERO = F(0)
CINV = 1 / iv.sqrt(2 * iv.pi)
SQ2PI = iv.sqrt(2 * iv.pi)
MS = F('1.15')
J2 = iv.mpf(['2.717199867930190', '2.717199867930191'])
J1 = iv.mpf(['0.7998716895841891', '0.7998716895841892'])
TWO3 = F(2) / 3


# ---------------------------------------------------------------- interval helpers
def lo(x):
    return mpf(x._mpi_[0])


def hi(x):
    return mpf(x._mpi_[1])


def mk(a, b):
    return iv.mpf([a, b])


def imin(a, b):
    return mk(min(lo(a), lo(b)), min(hi(a), hi(b)))


def imax(a, b):
    return mk(max(lo(a), lo(b)), max(hi(a), hi(b)))


def pos(x):
    return lo(x) > 0


def _frac(raw):
    sign, man, exp, bc = raw
    v = Fraction(man) * (Fraction(2) ** exp)
    return -v if sign else v


def _dec(v, nd, up):
    if v == 0:
        return "0"
    a = abs(v)
    e = 0
    while a >= 10:
        a /= 10
        e += 1
    while a < 1:
        a *= 10
        e -= 1
    t = v * Fraction(10) ** (nd - 1 - e)
    n = math.ceil(t) if up else math.floor(t)
    s = str(abs(n)).rjust(nd, '0')
    p = e + 1
    if p <= 0:
        out = "0." + "0" * (-p) + s
    elif p >= len(s):
        out = s + "0" * (p - len(s))
    else:
        out = s[:p] + "." + s[p:]
    return ("-" if n < 0 else "") + out


def fmt(x, nd=10):
    return "[%s, %s]" % (_dec(_frac(x._mpi_[0]), nd, False), _dec(_frac(x._mpi_[1]), nd, True))


def p23(x):
    return iv.exp(iv.log(x) * TWO3)


def p15(x):
    return x * iv.sqrt(x)


# ---------------------------------------------------------------- DDL^natural (Proposition 10:old-8-23)
def qnat(r):
    return 1 + F('0.7501') * r / (1 + r)


def eps_nat(K):
    return -iv.log(1 - iv.sqrt(K + 1) / (F('0.485917') * K))


def j_record_constants():
    """j1, j2 with the record's constants 0.708345, 2.528570 in place of 0.70836, 2.528571 (comparison only):
    both integrals are linear in the constants, j2' = (c'/c) j2, j1' = (c'/c) (j1 - (K - K') j2)."""
    r = F('0.708345') / F('0.70836')
    return r * (J1 - (F('2.528571') - F('2.528570')) * J2), r * J2


def DDL(K, j1=None, j2=None):
    """DDL^natural(k) = 14 (log 3k - 1) / (5 sqrt(pi k)) + 37.6 / (5 sqrt(pi) k)   (k >= 3131; decision K4-14).
    37.6 is the upward rounding of 7(3 - log 3) + 42/sqrt(3) = 37.558..., so the value stays an upper bound.
    Every operand is an `iv` interval (outward rounding), hence the returned interval encloses the exact R(k);
    its upper end is what the (na)/(ga) margins subtract.  j1, j2 are accepted and ignored (callers unchanged)."""
    return 14 * (iv.log(3 * K) - 1) / (5 * iv.sqrt(iv.pi * K)) + F('37.6') / (5 * iv.sqrt(iv.pi) * K)


# ---------------------------------------------------------------- pieces of chapter 10
def u_(K):
    return F(3) / F('0.35') * (F('1.35') + 1 / K) / p15(F('0.65') - 1 / K) / iv.sqrt(K)


def BD(K, nu):
    return (K + nu) * u_(K) * (1 / (K - 1) + 1 / K) + 3 * (K + 1) / p15(K - 1)


def sup(d, y):
    return imin(ONE, MS * (y + d) / p15(d))


def ec(K, nu):
    return 3 * nu ** 2 / ((K - 1) * K) + F('4.8') * iv.sqrt(nu) / K + nu ** 2 / (2 * (K - 1) ** 2)


def Flat(y):
    ab = p23(MS * (y + 2 * p23(y)))
    return 2 * (ab - 1) / (y + 2 - ab)


def cAb(r):
    s = iv.sqrt(r)
    return 2 * s / (1 - r) + 2 * iv.log((1 + s) / (1 - s))


def Sub(K, nub):
    xi = (nub + 4) / (K - 1)
    if lo(xi) >= mpf('0.6'):
        return ZERO
    assert hi(xi) < mpf('0.6')

    def G(s):
        return xi / s + (1 - xi) * s / (1 - s * s) - xi * iv.log((1 + s) / (1 - s))   # 2 xi atanh s = xi log((1+s)/(1-s))
    return (K - 1) / K * 2 * (G(iv.sqrt(F('0.6'))) - G(iv.sqrt(xi)))


def Ab(y, K, nub):
    z = F('0.6') + 1 / y
    return MS * (1 + 1 / y) * (4 / iv.sqrt(p23(MS * y) - 1) + (2 * cAb(z) - 4 / iv.sqrt(z) - Sub(K, nub)) / iv.sqrt(y))


def Top(K, nub):
    e = (nub + 1) / K
    rlo = F('0.6') - F('2.6') / K
    assert hi(e) <= lo(rlo), "kink of min(2, 2+e-rho) inside the range"
    a0 = 2 + e
    a1 = a0 / 3 - 1

    def Fp(r):
        return -2 * a0 / iv.sqrt(r) + 2 * a1 * iv.sqrt(r) - F(2) / 9 * p15(r)
    return Fp(ONE) - Fp(rlo)


def Stays_parts(K, nub):
    fl = [Flat(K - 1), Flat(K)]
    ab = [Ab(K - 1, K, nub), Ab(K, K, nub)]
    top = 2 * F('16.54') / iv.sqrt(K) * Top(K, nub)
    return fl, ab, top


def Stays(K, nub):
    fl, ab, top = Stays_parts(K, nub)
    return fl[0] + fl[1] + ab[0] + ab[1] + top


def abar_b(K):
    return 3 * MS * (F('1.48') * K + 2) / p15(F('0.48') * K + 1)


def bbar(K):
    return 2 * u_(K) * (2 * K - 1) / (K - 1) + 3 * (K + 1) / p15(K - 1)


def dbar(K):
    return F('72.217') / iv.sqrt(K)


def ebar(K):
    L = iv.log(K)
    xp = (iv.sqrt(5 * K * L) + 2) / K
    return iv.exp(F('1.5') / K) * (iv.exp(iv.sqrt(5 * L / K) + 1 / K) + F('2.40918') * iv.exp((F('1.5') - F('2.5') / (1 + xp)) * L))


THETA0 = (2 * iv.exp(-F('0.48')) - 1) * iv.exp(-F('0.48'))


def nu1(K):
    return F('1.3') * p23(K)


def nu2(K):
    return 2 * p23(K)


def family(name, k):
    """returns dict with o_F, Stays_F, R, R' (None if not defined) and the pieces."""
    K = F(k)
    dd = DDL(K)
    out = {'DDL': dd}
    if name == 'bulk':
        a, b, d, e = abar_b(K), bbar(K), dbar(K), ebar(K)
        out.update(o=4 - e, S=a + b + dd + d, pieces=dict(abar=a, bbar=b, dbar=d, ebar=e))
        out['R'] = out['S']
        out['Rp'] = None
        return out
    if name == '2':
        nub = F('0.48') * K
        s3 = 3 * sup(nu2(K) + 1, K + 1)
        bd = BD(K, nub)
        out.update(o=4 - s3 + THETA0 - bd - dd, pieces=dict(three_sup=s3, theta=THETA0, BD=bd))
        st = Stays(K, nub)
        out.update(S=st, R=s3 + bd + dd + st, Rp=None)
        return out
    if name == '1b':
        nub = nu2(K)
        s3 = 3 * sup(nu1(K) + 1, K + 1)
        x2 = nub / (K - 1)
        th = (2 * iv.exp(-x2) - 1) * iv.exp(-x2)
        bd = BD(K, nub)
        out.update(o=4 - s3 + th - bd - dd, pieces=dict(three_sup=s3, theta=th, BD=bd))
        st = Stays(K, nub)
        out.update(S=st, R=s3 + bd + dd + st, Rp=bd + dd + st)
        return out
    if name == '1a':
        nub = nu1(K)
        e1 = ec(K, nub)
        bd = BD(K, nub)
        out.update(o=2 - e1 - bd - dd, pieces=dict(ec=e1, BD=bd))
        st = Stays(K, nub)
        fl, ab, top = Stays_parts(K, nub)
        out['pieces'].update(Flat_km1=fl[0], Flat_k=fl[1], Ab_km1=ab[0], Ab_k=ab[1], top=top)
        out.update(S=st, R=3 + bd + dd + st, Rp=bd + dd + st)
        return out
    raise ValueError(name)


# ---------------------------------------------------------------- chain recursion and (ga)
def log_bor_table(nmax):
    LB = [None] * (nmax + 1)
    lf = ZERO
    for n in range(1, nmax + 1):
        ln = iv.log(F(n))
        lf = lf + ln
        LB[n] = (n - 1) * ln - n - lf
    return LB


def chain(y, D, LB, B):
    """s_q(y) for q = 1..D by the first-step recursion (list index q)."""
    E = [None] + [iv.exp(LB[y + q]) for q in range(1, D + 1)]
    Y = F(y)
    s = [None, ONE]
    u = [None, E[1] * (1 - Y / (Y + 1))]
    for q in range(2, D + 1):
        acc = ZERO
        for j in range(1, q):
            acc = acc + B[j] * u[q - j]
        sq = 1 - acc / E[q]
        s.append(sq)
        u.append(E[q] * (1 - Y / (Y + q) * sq))
    return s


def eps0_of(k0):
    t = 4 * (k0 + 1) ** 2               # eps0 = floor((4 (k0+1)^2)^(1/3))
    e = int(round(t ** (1.0 / 3)))
    while e ** 3 > t:
        e -= 1
    while (e + 1) ** 3 <= t:
        e += 1
    return e


F1 = F(4) / 3 * CINV
CR = SQ2PI / 2 * iv.exp(F(1) / 12)


def s_low(d, y):
    return iv.exp(-F1 * p15((y + d - 1) / y) * p15(d) / y)


def Qedge(y, xi):
    k = y - 1
    q0 = xi * p23(y)
    pre = (k / (k + 1)) * (1 - q0 / (2 * k)) * 2 * CINV * iv.exp(-F(1) / 12) * y / (CR * q0)
    p1 = iv.exp(-q0 / y) * s_low(q0, y) * (iv.exp(-CR * q0 / y) - iv.exp(-CR * q0 * iv.sqrt(q0 / 2) / y))
    p2 = iv.exp(-q0 / (2 * y)) * s_low(q0 / 2, y) * (iv.exp(-CR * q0 * iv.sqrt(q0 / 2 + 1) / y) - iv.exp(-CR * p15(q0) / y))
    return pre * (p1 + p2)


def ga_check(name, k0, R, Rp):
    e0 = eps0_of(k0)
    LB = log_bor_table(k0 + e0 + 5)
    B = [None] + [iv.exp(LB[j]) for j in range(1, e0 + 3)]
    sk = chain(k0, e0 + 1, LB, B)
    y = k0 + 1
    sy = chain(y, e0, LB, B)
    K, Y = F(k0), F(y)
    Rs = [None] + [CINV / iv.sqrt(F(l)) * iv.exp(-1 / (12 * F(l))) for l in range(1, e0 + 1)]
    Al = [None] + [SQ2PI / 4 * iv.exp(1 / (12 * F(l))) * iv.sqrt(F(l)) for l in range(1, e0 + 1)]
    cum = ZERO
    ptail = [None, ONE]
    for j in range(1, e0 + 1):
        cum = cum + B[j]
        ptail.append(1 - cum)              # ptail[q] = 1 - sum_{j<q} Bor(j)
    worst = None
    worstp = None
    which_max = {'z': 0, 'F': 0, 'undecided': 0}
    for q0 in range(2, e0 + 1):
        zr = ZERO
        for q in range(1, q0):
            l = q0 - q
            zr = zr + Rs[l] * iv.exp(-(q + Al[l] * (q0 + q)) / Y) * sy[q]
        Fp = sy[q0] - ptail[q0]
        if lo(zr) > hi(Fp):
            which_max['z'] += 1
        elif lo(Fp) > hi(zr):
            which_max['F'] += 1
        else:
            which_max['undecided'] += 1
        eR = (K / (K + 1)) * (1 - F(q0) / (2 * K)) * (imax(zr, Fp) + B[q0])
        el = 4 * sk[q0 + 1] + 2 * eR
        m = el - R
        if worst is None or lo(m) < lo(worst[0]):
            worst = (m, q0, el)
        if Rp is not None and q0 >= 104:
            mp_ = eR + sk[q0 + 1] - Rp
            if worstp is None or lo(mp_) < lo(worstp[0]):
                worstp = (mp_, q0)
    return dict(e0=e0, worst=worst, worstp=worstp, which=which_max, s2=sy[2], s3k=sk[3])


def lemma_iii_margins(ncell=40000):
    kap = CR
    xa, xb = F('1.04'), iv.exp(iv.log(F(2)) * TWO3)
    g = lambda a: iv.exp(-a) * (1 + F('1.5') * a)
    c6669 = iv.exp(iv.log(F(6669)) / 3)
    m1 = None
    m2 = None
    for i in range(ncell):
        a_ = xa + (xb - xa) * i / ncell
        b_ = xa + (xb - xa) * (i + 1) / ncell
        x = mk(lo(a_), hi(b_))            # cell (slightly widened, covers [1.04, 2^(2/3)])
        a = kap * p15(x) / iv.sqrt(F(2))
        cd = kap * x / c6669
        v1 = iv.exp(-cd) * (1 + cd) - g(a)
        a2 = kap * p15(x)
        a1 = a2 * iv.sqrt(F('0.5') + F(1) / 562)
        v2 = g(a1) - g(a2) - a1 * iv.exp(-a1) / 564
        m1 = v1 if m1 is None else mk(min(lo(m1), lo(v1)), min(hi(m1), hi(v1)))
        m2 = v2 if m2 is None else mk(min(lo(m2), lo(v2)), min(hi(m2), hi(v2)))
    return m1, m2


def strictly(vals, inc):
    for a, b in zip(vals[:-1], vals[1:]):
        if inc and not lo(b) > hi(a):
            return False
        if not inc and not lo(a) > hi(b):
            return False
    return True


def main():
    t0 = time.time()
    print("mpmath iv, dps = %d" % iv.dps)
    print("theta0 = (2e^-0.48 - 1)e^-0.48 in", fmt(THETA0))
    print("first rows: 20001-2k <= phi k^(2/3): 1a k=9705:", 20001 - 2 * 9705, "<=", fmt(nu1(F(9705))), " k=9704:", 20001 - 2 * 9704, "vs", fmt(nu1(F(9704))))
    print("            1b k=9551:", 20001 - 2 * 9551, "<=", fmt(nu2(F(9551))), " k=9550:", 20001 - 2 * 9550, "vs", fmt(nu2(F(9550))))
    print("            2  k=8065:", 20001 - 2 * 8065, "<=", fmt(F('0.48') * 8065, 8), "(nu<=0.48k side) / 2k^(2/3) =", fmt(nu2(F(8065))))
    fams = (('bulk', 6668), ('2', 8065), ('1b', 9551), ('1a', 9705))
    res = {}
    print("\n(na)  o_F(k0) - Stays^up_F(k0)")
    for name, k0 in fams:
        r = family(name, k0)
        res[name] = r
        m = r['o'] - r['S']
        print("family %-4s k0=%d: o_F in %s  Stays^up_F in %s  margin in %s  >0: %s"
              % (name, k0, fmt(r['o']), fmt(r['S']), fmt(m), pos(m)))
        print("      DDL in %s;  " % fmt(r['DDL']) + ";  ".join("%s in %s" % (kk, fmt(v)) for kk, v in r['pieces'].items()))
    print("bulk: abar+bbar+DDL+dbar+ebar in", fmt(res['bulk']['S'] + res['bulk']['pieces']['ebar']))
    print("\nR#_F(k0), R#'_F(k0):")
    for name, k0 in fams:
        r = res[name]
        print("family %-4s R# in %s" % (name, fmt(r['R'])) + ("   R#' in %s" % fmt(r['Rp']) if r['Rp'] is not None else ""))

    print("\n(ga)(a)  min over 2 <= q0 <= eps0 of e_low(k0,q0) - R#_F(k0);  1a,1b: min over 104 <= q0 <= eps0 of e_low_R + s_{q0+1}(k0) - R#'")
    gares = {}
    for name, k0 in fams:
        t1 = time.time()
        g = ga_check(name, k0, res[name]['R'], res[name]['Rp'])
        gares[name] = g
        w = g['worst']
        line = "family %-4s k0=%d eps0=%d: min at q0=%d, margin in %s (e_low in %s)  >0: %s" % (name, k0, g['e0'], w[1], fmt(w[0]), fmt(w[2]), pos(w[0]))
        if g['worstp'] is not None:
            line += " | m0>N: min at q0=%d, margin in %s  >0: %s" % (g['worstp'][1], fmt(g['worstp'][0]), pos(g['worstp'][0]))
        print(line)
        print("      max(z_R, s - Pr) decided by z_R at %d, by s - Pr at %d, undecided %d q0's;  s_2(k0+1) in %s, s_3(k0) in %s  (%.0f s)"
              % (g['which']['z'], g['which']['F'], g['which']['undecided'], fmt(g['s2'], 12), fmt(g['s3k'], 12), time.time() - t1))

    print("\n(ga)(b)  edge points")
    XE = iv.exp(iv.log(F(2)) * TWO3)
    caps = {'bulk': XE, '2': XE, '1b': XE, '1a': F('1.3')}
    edge = {}
    for name, k0 in fams:
        K = F(k0)
        xa = caps[name]
        La = 4 * s_low(xa * p23(K + 1) + 1, K) + 2 * Qedge(K + 1, xa)
        m = La - res[name]['R']
        edge[name] = [m, None]
        line = "family %-4s k0=%d: m0<=N, xi_cap=%s: 4 s_low + 2 Q in %s, margin in %s  >0: %s" % (name, k0, '1.3' if name == '1a' else '2^(2/3)', fmt(La), fmt(m), pos(m))
        if res[name]['Rp'] is not None:
            Lb = Qedge(K + 1, XE) + s_low(XE * p23(K + 1) + 1, K)
            mb = Lb - res[name]['Rp']
            edge[name][1] = mb
            line += " | m0>N: Q + s_low in %s, margin in %s  >0: %s" % (fmt(Lb), fmt(mb), pos(mb))
        print(line)

    m1, m2 = lemma_iii_margins()
    print("\nLemma 10:old-8-32(iii) conditions on xi in [1.04, 2^(2/3)] (40000 interval cells; y = 6669 in (h1), q0 = 562 in (h2)):")
    print("  (h1) min_xi [e^{-c d}(1+c d) - g(a)] in", fmt(m1, 6), " >0:", pos(m1))
    print("  (h2) min_xi [g(a1) - g(a2) - a1 e^{-a1}/564] in", fmt(m2, 6), " >0:", pos(m2))

    print("\n1a cross-check with the record's 30-digit recheck_1a.py (record constants 0.708345, 2.528570 in DDL):")
    r = res['1a']
    for lab, x, lit in (("Stays^up(9705;1.3k^(2/3))", r['S'], '1.1507402'), ("o_F(9705)", r['o'], '1.3554526'),
                        ("(na) margin", r['o'] - r['S'], '0.204712'), ("R#", r['R'], '4.770257'), ("R#'", r['Rp'], '1.770257'),
                        ("DDL^natural(9705)", r['DDL'], '0.11328183'),
                        ("(ga)(a) q0=2 margin", gares['1a']['worst'][0], '0.235475')):
        print("  %-28s interval %s   recheck %s   recheck within 5e-8 of the interval: %s"
              % (lab, fmt(x), lit, lo(x) - mpf('5e-8') <= mpf(lit) <= hi(x) + mpf('5e-8')))
    j1r, j2r = j_record_constants()
    dr = DDL(F(9705), j1r, j2r)
    shift = dr - r['DDL']                      # DDL enters o_F with sign -1 and R#, R#' with sign +1
    print("  with the record's constants: j1' in %s, j2' in %s, DDL'(9705) in %s (shift %s)" % (fmt(j1r), fmt(j2r), fmt(dr), fmt(shift, 4)))
    for lab, x, lit, half in (("o_F(9705)", r['o'] - shift, '1.3554526', '5e-8'), ("(na) margin", r['o'] - shift - r['S'], '0.204712', '5e-7'),
                              ("R#", r['R'] + shift, '4.770257', '5e-7'), ("R#'", r['Rp'] + shift, '1.770257', '5e-7'),
                              ("DDL'(9705)", dr, '0.11328183', '5e-9'), ("(ga)(a) q0=2 margin", gares['1a']['worst'][0] - shift, '0.235475', '5e-7'),
                              ("(ga)(b) edge m0<=N margin", edge['1a'][0] - shift, '2.87702', '5e-6'),
                              ("(ga)(b) edge m0>N margin", edge['1a'][1] - shift, '0.394753', '5e-7')):
        print("  %-28s interval %s   recheck %s   recheck rounds the interval (half unit %s): %s"
              % (lab, fmt(x), lit, half, lo(x) - mpf(half) <= mpf(lit) <= hi(x) + mpf(half)))

    print("\nmonotonicity samples (record grids; consecutive values compared with certified intervals):")
    for name, k0 in fams:
        ks = np.unique(np.concatenate([np.arange(k0, k0 + 3000, 7), np.geomspace(k0, 1e7, 300).astype(int)]))
        rows = [family(name, int(k)) for k in ks]
        flags = ["o_F increasing: %s" % strictly([x['o'] for x in rows], True),
                 "Stays^up_F decreasing: %s" % strictly([x['S'] for x in rows], False),
                 "R# decreasing: %s" % strictly([x['R'] for x in rows], False)]
        if rows[0]['Rp'] is not None:
            flags.append("R#' decreasing: %s" % strictly([x['Rp'] for x in rows], False))
        print("  family %-4s (%d points): " % (name, len(ks)) + ", ".join(flags))
    ok = True
    for xc in (F('1.3'), XE):
        xcf = float(mpf(xc._mpi_[0]))
        for yv in np.geomspace(6669, 1e9, 60):
            k = int(yv) - 1
            K = F(k)
            xs = [F(float(v)) for v in np.linspace(0.8 * xcf, xcf, 120)]
            a = [4 * s_low(x * p23(K + 1) + 1, K) + 2 * Qedge(K + 1, x) for x in xs]
            b = [Qedge(K + 1, x) + s_low(x * p23(K + 1) + 1, K) for x in xs]
            if not (strictly(a, False) and strictly(b, False)):
                ok = False
    print("  edge bounds decreasing in xi on [0.8 xi_cap, xi_cap] (2 x 60 values of y in [6669, 1e9], 120 xi each):", ok)
    ok = True
    for name, k0 in fams:
        for xc in set([float(mpf(caps[name]._mpi_[0])), float(mpf(XE._mpi_[0]))]):
            X = F(xc)
            ys = np.geomspace(k0 + 1, 1e8, 400)
            q = [Qedge(F(float(yv)), X) for yv in ys]
            s = [s_low(X * p23(F(int(yv))) + 1, F(int(yv) - 1)) for yv in ys]
            if not strictly(q, True):
                ok = False
            for a_, b_ in zip(s[:-1], s[1:]):
                if hi(b_) < lo(a_):
                    ok = False
    print("  Q(y, xi) increasing and s_low nondecreasing in y on 400 points of [k0+1, 1e8] (each family, each cap):", ok)
    print("\ntotal time %.0f s" % (time.time() - t0))


if __name__ == '__main__':
    main()
