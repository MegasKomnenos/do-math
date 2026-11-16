# Peer s637d3ec: interval-arithmetic upper sums for C_I and C_II of Theorem E (exposition 4.5), replacing the
# binary64 sums of emaj_upper.py.  Same majorant (13 kappa-pieces, monomials of emaj2.py).  Differences:
#  * every cell bound uses only the monotonicity of separate factors (no grid check of monotonicity):
#    sup_{[zeta,zeta+h]} Pibar <= exp(-sq2l((2/3) zs(z_c)^{3/2} + (1/2) zs(z_c)^{1/2} h0) + A + (ln2/3) h0 (z_{c+1}+h0)^2),
#    exp(-cE(zeta) kappa) <= exp(-cE(z_c) k_j)  (cE increasing in zeta), and the power factors
#    (zeta+h0)^{1+beta}, (kappa+delta)^{alpha-1/2} are integrated exactly over each cell;
#  * the tail zeta > ZMAX is bounded explicitly.
import sys, math, time
from multiprocessing import Pool
from mpmath import iv, mp, mpf

iv.dps = 25
NZ = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
NK = int(sys.argv[2]) if len(sys.argv) > 2 else 200
NPROC = int(sys.argv[3]) if len(sys.argv) > 3 else 4
ZMAX = 40
H0g = iv.mpf('0.0342')          # >= 25000^{-1/3}
EPS = iv.mpf('0.05'); B = iv.mpf('1.3'); LN2 = iv.log(2)
PIECES = ['0', '0.0625', '0.125', '0.25', '0.375', '0.5', '0.75', '1', '1.5', '2', '3', '4', '5', '6']


def lo(x): return mpf(x.a)
def hi(x): return mpf(x.b)


def zeta32():
    N = 2000; s = iv.mpf(0)
    for n in range(1, N): s += iv.mpf(n) ** iv.mpf('-1.5')
    return iv.mpf([lo(s + 2 * iv.mpf(N) ** iv.mpf('-0.5') + iv.mpf(N) ** iv.mpf('-1.5') / 2), hi(s + 2 * (iv.mpf(N) - iv.mpf('0.5')) ** iv.mpf('-0.5'))])


ZETA32 = zeta32()
ZM12_ABS = iv.mpf(['0.2078862250607212', '0.2078862250607213'])   # |zeta(-1/2)| = 0.20788622506072...
S1b = iv.sqrt(2 / iv.pi)


def piece(idx):
    kl = iv.mpf(PIECES[idx]); kr = iv.mpf(PIECES[idx + 1])
    h0 = H0g          # h_eff = min(H0, 1/kappa_l) = H0 for every piece since 1/kappa_l >= 1/5 > H0
    C0 = iv.sqrt(2 / iv.pi) * iv.exp(h0 ** 3 / 12)
    S2b = (1 / iv.sqrt(2 * iv.pi)) * (iv.mpf(2) / 3) * (1 + h0 ** 3) ** iv.mpf('1.5')
    xr = kr * h0 + h0 ** 3
    if lo(xr) >= 1: xr = iv.mpf(1)
    lam = LN2 / (1 + xr)
    ui = kr * h0
    if lo(ui) >= 1: ui = iv.mpf(1)
    rho = iv.log(1 + ui) / ui
    sq2l = iv.sqrt(2 * lam)
    A = ZM12_ABS * iv.sqrt(2 * LN2) * h0 ** iv.mpf('1.5')
    k1 = 2 / sq2l; k1lin = 1 / (3 * (1 - EPS)); k2 = (2 * lam) ** iv.mpf('-1.5') * ZETA32; k2log = iv.mpf('1.2') / (2 * lam)
    L0 = 1 + iv.log(1 / h0)
    # negative part of c1*kappa1: c1 >= 1.5h^3/(1+h^3), (2theta)^{-1/2} >= (2 ln2)^{-1/2} h^{-3/2} (theta = ln2/V <= ln2 h^3);
    # merged into the (0,0) monomial; A00 >= 0 keeps h^{1/2}A00 increasing in h.  (emaj2/emaj_upper used (2 lam_i)^{-1/2}: too large.)
    A00 = iv.mpf('1.5') * S1b + B * S2b + B * k2 - iv.mpf('1.5') / iv.sqrt(2 * LN2) / (1 + h0 ** 3)
    assert lo(A00) >= 0
    mon = [(iv.mpf('1.5'), 1, 0), (iv.sqrt(h0) * A00, 0, 0), (B * h0, 2, 0), (2 * B * S1b * h0 ** iv.mpf('1.5'), 1, 0),
           (iv.mpf('1.5') * k1, 0, iv.mpf('0.5')), (iv.mpf('1.5') * k1lin * h0, 0, 1),
           (2 * B * h0 * k1, 1, iv.mpf('0.5')), (2 * B * h0 * k1lin * h0, 1, 1),
           (2 * B * S1b * h0 ** iv.mpf('1.5') * k1, 0, iv.mpf('0.5')), (2 * B * S1b * h0 ** iv.mpf('1.5') * k1lin * h0, 0, 1),
           (B * h0 * k1 * k1, 0, 1), (B * h0 * 2 * k1 * k1lin * h0, 0, iv.mpf('1.5')), (B * h0 * (k1lin * h0) ** 2, 0, 2),
           (B * k2log * h0 ** 2 * L0, 0, 0), (B * k2log * h0 ** 2, 0, 'log')]
    a = kl - h0 * h0
    a = iv.mpf(0) if hi(a) <= 0 else iv.mpf(max(mpf(0), lo(a)))
    # kappa grid on [a, kr]; weights W_al[j] = int_{k_j}^{k_{j+1}} (kappa+delta)^{al-1/2} dkappa (delta = 0 for al=0, h0^2 otherwise)
    kg = [a + (kr - a) * j / NK for j in range(NK + 1)]
    d2 = h0 * h0
    W = {0: [2 * (iv.sqrt(kg[j + 1]) - iv.sqrt(kg[j])) for j in range(NK)],
         1: [((kg[j + 1] + d2) ** iv.mpf('1.5') - (kg[j] + d2) ** iv.mpf('1.5')) / iv.mpf('1.5') for j in range(NK)],
         2: [((kg[j + 1] + d2) ** iv.mpf('2.5') - (kg[j] + d2) ** iv.mpf('2.5')) / iv.mpf('2.5') for j in range(NK)]}
    dk = (kr - a) / NK
    zg = [iv.mpf(ZMAX) * c / NZ for c in range(NZ + 1)]
    total = iv.mpf(0)
    for c in range(NZ):
        za, zb = zg[c], zg[c + 1]
        zsa = za - h0
        zsa = iv.mpf(0) if hi(zsa) <= 0 else iv.mpf(max(mpf(0), lo(zsa)))
        Pc = iv.exp(-sq2l * ((iv.mpf(2) / 3) * zsa ** iv.mpf('1.5') + zsa ** iv.mpf('0.5') * h0 / 2) + A + (LN2 / 3) * h0 * (zb + h0) * (zb + h0))   # sup over [zeta, zeta+h] (Riemann shift): increasing part at zb+h0
        cE = rho * zsa / (1 + h0 ** 3)          # at left end (smallest)
        e0 = iv.exp(-cE * a); r = iv.exp(-cE * dk)
        J = {0: iv.mpf(0), 1: iv.mpf(0), 2: iv.mpf(0)}
        e = e0
        for j in range(NK):
            J[0] += e * W[0][j]; J[1] += e * W[1][j]; J[2] += e * W[2][j]
            e = e * r
        cellsum = iv.mpf(0)
        for (coef, al, be) in mon:
            if be == 'log':
                zint = (zb - za) * (zb + h0) * iv.mpf(max(mpf(0), hi(iv.log(zb + h0))))
            else:
                p = 1 + be
                zint = ((zb + h0) ** (p + 1) - (za + h0) ** (p + 1)) / (p + 1)
            cellsum += coef * J[al] * zint
        total += Pc * cellsum
    # tail zeta > ZMAX.  Inside the region theta(z-1) <= s_eps one has (theta/3)N(N+1) <= (1/2)(2/3)sqrt(2theta)N^{3/2}
    # (since sqrt(theta N) <= sqrt(s_eps) <= sqrt2 N/(N+1)), so Pi_z <= e^{0.21 sqrt(2theta)} exp(-(1/3) sqrt(2 lam)(zeta-h0)^{3/2})
    # <= e * exp(-(1/3) sq2l (zeta-h0)^{3/2}).  For zeta >= 40: (1/3) sq2l (zeta-h0)^{3/2} >= c zeta^{3/2} >= 2 zeta (checked),
    # and (zeta+h0)^{1+beta} (and the log monomial) <= (zeta+1)^3 <= e^{zeta}; J <= Jmax.  Tail <= e * coefsum * Jmax * e^{-40}.
    zt = iv.mpf(ZMAX)
    assert lo(sq2l / 3 * (1 - h0 / zt) ** iv.mpf('1.5') * iv.sqrt(zt) - 2) > 0
    assert lo(zt - 3 * iv.log(zt + 1)) > 0
    Jmax = sum((sum(W[al], iv.mpf(0)) for al in (0, 1, 2)), iv.mpf(0))
    coefsum = sum((m[0] for m in mon), iv.mpf(0))
    tail = iv.e * coefsum * Jmax * iv.exp(-zt)
    return idx, hi(C0 * total + C0 * tail)


def region2():
    h0 = H0g
    S2b = (1 / iv.sqrt(2 * iv.pi)) * (iv.mpf(2) / 3) * (1 + h0 ** 3) ** iv.mpf('1.5')
    lam0 = LN2 / (1 + h0 ** 3); sq2l = iv.sqrt(2 * lam0)
    A = ZM12_ABS * iv.sqrt(2 * LN2) * h0 ** iv.mpf('1.5')
    k1 = 2 / sq2l; k2 = (2 * lam0) ** iv.mpf('-1.5') * ZETA32; k1lin = 1 / (3 * (1 - EPS))
    zg = [iv.mpf(ZMAX) * c / NZ for c in range(NZ + 1)]
    tot = iv.mpf(0)
    for c in range(NZ):
        za, zb = zg[c], zg[c + 1]
        zsa = za - h0
        zsa = iv.mpf(0) if hi(zsa) <= 0 else iv.mpf(max(mpf(0), lo(zsa)))
        Pc = iv.exp(-sq2l * ((iv.mpf(2) / 3) * zsa ** iv.mpf('1.5') + zsa ** iv.mpf('0.5') * h0 / 2) + A + (LN2 / 3) * h0 * (zb + h0) * (zb + h0))   # sup over [zeta, zeta+h] (Riemann shift): increasing part at zb+h0
        zr = zb
        br = (iv.sqrt(h0) * (iv.mpf('1.5') * S1b + B * S2b + B * k2) + (iv.mpf('1.5') + 2 * B * S1b * h0 ** iv.mpf('1.5')) * (k1 * iv.sqrt(zr + h0) + k1lin * h0 * (zr + h0))
              + B * h0 * (k1 * iv.sqrt(zr + h0) + k1lin * h0 * (zr + h0)) ** 2
              + B * (iv.mpf('1.2') / (2 * lam0)) * h0 ** 2 * (1 + iv.log(1 / h0) + iv.mpf(max(mpf(0), hi(iv.log(zr + h0))))))
        zint = ((zb + h0) ** 2 - (za + h0) ** 2) / 2
        tot += Pc * br * zint
    # tail zeta > 40 as in piece(): Pi <= e*exp(-(1/3)sq2l(zeta-h0)^{3/2}) <= e*e^{-2zeta}; (zeta+h0)*br(zeta) <= br(41)(zeta+1)^3 e^{...}: crude
    br41 = (iv.sqrt(h0) * (iv.mpf('1.5') * S1b + B * S2b + B * k2) + (iv.mpf('1.5') + 2 * B * S1b * h0 ** iv.mpf('1.5')) * (k1 + k1lin * h0) * 2
            + B * h0 * ((k1 + k1lin * h0) * 2) ** 2 + B * (iv.mpf('1.2') / (2 * lam0)) * h0 ** 2 * (1 + iv.log(1 / h0) + 1))
    # for zeta>=40: br(zeta) <= br41 * (zeta+1)^2 (each piece grows at most like (zeta+1)^2, log <= zeta), so integrand <= e*br41*(zeta+1)^3 e^{-2 zeta} <= e*br41*e^{-zeta}
    tail = iv.e * br41 * iv.exp(-iv.mpf(ZMAX))
    assert lo(sq2l / 3 * (1 - h0 / iv.mpf(ZMAX)) ** iv.mpf('1.5') * iv.sqrt(iv.mpf(ZMAX)) - 2) > 0
    return hi(iv.exp(h0 ** 3 / 12) * (tot + tail))


if __name__ == '__main__':
    t0 = time.time()
    with Pool(NPROC) as pool:
        res = pool.map(piece, range(len(PIECES) - 1))
    CI = sum(v for _, v in res)
    CII = region2()
    CIII = mpf('1.3352092')     # c3_iv.py
    far = mpf('1e-10')
    h0 = hi(H0g)
    CE = CI + h0 * CII + CIII + far
    print(f"NZ={NZ} NK={NK}: C_I <= {mp.nstr(CI, 7)}  (pieces: {[mp.nstr(v, 4) for _, v in sorted(res)]})")
    print(f"  C_II <= {mp.nstr(CII, 7)},  H0*C_II <= {mp.nstr(h0 * CII, 6)},  C_III <= 1.3352092 (c3_iv.py),  far z <= 1e-10")
    print(f"  ==> C_E <= {mp.nstr(CE, 7)}   (interval arithmetic; time {time.time()-t0:.0f}s)")
