# Peer s637d3ec: improved v-uniform majorant for E*(y), y=v+1:  E*(y) <= C_E * v^{-1/3} for all v >= v0.
# Inputs proved in peer-uniform-E.md (Lemmas U1-U8).  Quadrature here is numerical (same standard as producer U-L).
import math, sys
import numpy as np

ZETA32 = 2.612375348685488
ZETA12 = -1.4603545088095868   # zeta(1/2)
ZETAm12 = -0.2078862250607212  # zeta(-1/2)
LN2 = math.log(2)

def simpson(f, x):
    n = len(x) - 1
    hs = (x[-1] - x[0]) / n
    return hs / 3 * (f[0] + f[-1] + 4 * f[1:-1:2].sum() + 2 * f[2:-1:2].sum())

def run(v0=25000, eps=0.05, b=1.3, pieces=(0, 0.125, 0.25, 0.5, 1, 2, 4, 8, 16, 32, 64),
        nz=2400, zmax=40.0, nk=400, riemann='shift', verbose=True):
    h0 = v0 ** (-1.0 / 3)
    K = pieces[-1]
    C0 = math.sqrt(2 / math.pi) * math.exp(h0 ** 3 / 12)
    S1b = math.sqrt(2 / math.pi)                      # S1 <= S1b h^{-3/2}
    S2b = (2 * math.pi) ** -0.5 * (2 / 3) * (1 + h0 ** 3) ** 1.5   # S2 <= S2b h^{-9/2}
    zg = np.linspace(0.0, zmax, nz + 1)
    zs = np.maximum(zg - h0, 0.0)
    CI = 0.0
    details = []
    H0 = h0
    for i in range(len(pieces) - 1):
        kl, kr = pieces[i], pieces[i + 1]
        h0 = min(H0, 1.0 / kl) if kl > 0 else H0
        C0 = math.sqrt(2 / math.pi) * math.exp(h0 ** 3 / 12)
        S2b = (2 * math.pi) ** -0.5 * (2 / 3) * (1 + h0 ** 3) ** 1.5
        zs = np.maximum(zg - h0, 0.0)
        xr = min(kr * h0 + h0 ** 3, 1.0)
        lam = LN2 / (1 + xr)                          # theta >= lam h^3 on the piece
        ui = min(kr * h0, 1.0)
        rho = math.log1p(ui) / ui                     # (1+k/(v+1))^{-(z-1)} <= exp(-rho kappa (zeta-h0)_+/(1+h0^3))
        sq2l = math.sqrt(2 * lam)
        # Pi_z <= exp(-sqrt(2lam)[(2/3)(z-h0)^{3/2} + (1/2)(z-h0)^{1/2} h0] + |zeta(-1/2)| sqrt(2 ln2) h0^{3/2} + (ln2/3) h0 zeta^2)
        Pib = np.exp(-sq2l * ((2 / 3) * zs ** 1.5 + 0.5 * zs ** 0.5 * h0) + abs(ZETAm12) * math.sqrt(2 * LN2) * h0 ** 1.5
                     + (LN2 / 3) * h0 * zg ** 2)
        # kappa1 <= h^{-2}[ 2 (2lam)^{-1/2} zeta^{1/2} - |zeta(1/2)| (2ln2)^{-1/2} h^{1/2} + zeta h/(3(1-eps)) ]
        k1 = 2 * (2 * lam) ** -0.5
        k1neg = abs(ZETA12) * (2 * LN2) ** -0.5
        k1lin = 1 / (3 * (1 - eps))
        # kappa2 <= h^{-9/2}[(2lam)^{-3/2} zeta(3/2)] + 1.2 (2lam)^{-1} h^{-3}(1+ln(zeta/h))
        k2 = (2 * lam) ** -1.5 * ZETA32
        k2log = 1.2 / (2 * lam)
        L0 = 1 + math.log(1 / h0)
        # Phi = c0/h + c1 kappa1/h + c2(kappa2+kappa1^2)/h, as monomials coef * kappa^al * zeta^be  (zeta exponents may be fractional)
        # c0/h <= 1.5 kappa + 1.5 S1b h^{1/2} + b kappa^2 h + 2 b S1b kappa h^{3/2} + b S2b h^{1/2}
        # c1 <= 1.5h^3 + 2b kappa h^4 + 2b S1b h^{9/2};  c1 >= 1.5 h^3/(1+h^3)
        # kappa1 pos part P1 = 2(2lam)^{-1/2} zeta^{1/2} + zeta h/(3(1-eps)) ; neg part = k1neg h^{1/2}
        # (kappa1)^2 <= h^{-4} P1^2
        A00 = 1.5 * S1b + b * S2b + b * k2 - 1.5 * 1.0 * (2 * lam) ** -0.5  # sum a^{-1/2} <= 2 sqrt(N) - 1
        assert A00 >= 0, A00
        mon = [(1.5, 1, 0.0), (h0 ** 0.5 * A00, 0, 0.0), (b * h0, 2, 0.0), (2 * b * S1b * h0 ** 1.5, 1, 0.0),
               (1.5 * k1, 0, 0.5), (1.5 * k1lin * h0, 0, 1.0),
               (2 * b * h0 * k1, 1, 0.5), (2 * b * h0 * k1lin * h0, 1, 1.0),
               (2 * b * S1b * h0 ** 1.5 * k1, 0, 0.5), (2 * b * S1b * h0 ** 1.5 * k1lin * h0, 0, 1.0),
               (b * h0 * k1 * k1, 0, 1.0), (b * h0 * 2 * k1 * k1lin * h0, 0, 1.5), (b * h0 * (k1lin * h0) ** 2, 0, 2.0),
               (b * k2log * h0 ** 2 * L0, 0, 0.0), (b * k2log * h0 ** 2, 0, 'log')]
        a_lo = max(kl - h0 * h0, 0.0)
        cE = rho * zs / (1 + h0 ** 3)
        piece_val = 0.0
        for (coef, al, be) in mon:
            delta = 0.0 if al == 0 else h0 * h0
            if al == 0:
                s = np.linspace(math.sqrt(a_lo), math.sqrt(kr), nk + 1)
                F = 2.0 * np.exp(-np.outer(cE, s * s))
                J = np.array([simpson(F[j], s) for j in range(len(zg))])
            else:
                kk = np.linspace(a_lo, kr, nk + 1)
                F = (kk + delta) ** (al - 0.5) * np.exp(-np.outer(cE, kk))
                J = np.array([simpson(F[j], kk) for j in range(len(zg))])
            if be == 'log':
                zpow = (zg + h0) * np.maximum(np.log(np.maximum(zg + h0, 1e-300)), 0.0)
            else:
                zpow = (zg + h0) ** (1 + be)
            val = C0 * coef * simpson(zpow * Pib * J, zg)
            piece_val += val
        details.append((kl, kr, piece_val))
        CI += piece_val
    h0 = H0
    zs = np.maximum(zg - h0, 0.0)
    S2b = (2 * math.pi) ** -0.5 * (2 / 3) * (1 + h0 ** 3) ** 1.5
    # Region II (k=0): total <= h * h0 * CII
    lam0 = LN2 / (1 + h0 ** 3); sq2l = math.sqrt(2 * lam0)
    Pib0 = np.exp(-sq2l * ((2 / 3) * zs ** 1.5 + 0.5 * zs ** 0.5 * h0) + abs(ZETAm12) * math.sqrt(2 * LN2) * h0 ** 1.5 + (LN2 / 3) * h0 * zg ** 2)
    k1 = 2 * (2 * lam0) ** -0.5; k2 = (2 * lam0) ** -1.5 * ZETA32; k1lin = 1 / (3 * (1 - eps))
    br = (h0 ** 0.5 * (1.5 * S1b + b * S2b + b * k2) + (1.5 + 2 * b * S1b * h0 ** 1.5) * (k1 * (zg + h0) ** 0.5 + k1lin * h0 * (zg + h0))
          + b * h0 * (k1 * (zg + h0) ** 0.5 + k1lin * h0 * (zg + h0)) ** 2 + b * (1.2 / (2 * lam0)) * h0 ** 2 * (1 + math.log(1 / h0) + np.maximum(np.log(zg + h0), 0)))
    CII = math.exp(h0 ** 3 / 12) * simpson((zg + h0) * Pib0 * br, zg)
    # Region III (kappa > K): sup over h in (0, min(h0, 1/K)] of explicit expression (each term monotone; evaluate on grid finely)
    def CIII_at(h):
        v = h ** -3.0
        k0 = math.floor(K * v ** (2 / 3))
        if k0 >= v - 2: return 0.0
        A1 = 2 / (1 - eps) / math.sqrt(LN2)
        A2 = (1 - eps) ** -3 * LN2 ** -1.5 * ZETA32
        sq = math.sqrt(2 / math.pi)
        S1 = S1b * v ** 0.5; S2 = (2 * math.pi) ** -0.5 * (2 / 3) * (v + 1) ** 1.5
        y = v + 1
        I32 = 2 * (k0 ** -0.5 - v ** -0.5)          # sum_{k0<k<=v} k^-3/2
        I52 = (2 / 3) * (k0 ** -1.5 - v ** -1.5)
        I12 = 2 * (v ** 0.5 - k0 ** 0.5)
        I_12up = (2 / 3) * ((v + 1) ** 1.5 - k0 ** 1.5)  # sum k^{1/2}
        I3 = 0.5 * (k0 ** -2.0); I2 = 1.0 / k0; I72 = 0.4 * k0 ** -2.5
        TA = 1.5 * sq * (I32 + S1 * I52 + I12 / (v + 1) + S1 * I32 / (v + 1))
        TB = b * sq / y * (I12 + I_12up / (v + 1) + 2 * S1 * (I32 + I12 / (v + 1)) + S2 * (I52 + I32 / (v + 1)))
        TC = sq * A1 * 4 * (1.5 / y * v * I3 + 2 * b / y ** 2 * v ** 2 * I2 + 2 * b * S1 / y ** 2 * v ** 2 * I3)
        TD = b / y ** 2 * A2 * v ** 1.5 * sq * 2 * v * I52
        TE = b / y ** 2 * A1 ** 2 * v * 2 * 4 * v ** 2 * sq * I72
        return math.exp(h ** 3 / 12) * (TA + TB + TC + TD + TE) / h
    hs = np.linspace(1e-6, min(h0, 1.0 / K), 2000)
    CIII = max(CIII_at(h) for h in hs)
    CE = CI + h0 * CII + CIII
    if verbose:
        print(f"v0={v0} h0={h0:.5f} b={b} K={K} riemann={riemann}: C_I={CI:.4f}  h0*C_II={h0*CII:.4f}  C_III(sup)={CIII:.4f}  ==> C_E={CE:.4f};  E*<= {CE*h0:.4f} at v0")
        print("   pieces:", ", ".join(f"[{a},{c}]:{v:.3f}" for a, c, v in details))
    return CE

if __name__ == '__main__':
    v0 = int(sys.argv[1]) if len(sys.argv) > 1 else 25000
    run(v0=v0)
