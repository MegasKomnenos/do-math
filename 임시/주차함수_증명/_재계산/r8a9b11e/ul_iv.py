# Peer s637d3ec: interval-arithmetic certificate of the l-uniform window-mass constant s0 (producer Theorem U-L),
# rebuilt with rigorous lower sums.  Claim certified:  for all l >= L0,  Lambda_w(l, floor(6 l^{2/3})) >= S_int(l) >= s0_cert.
# Structure (exposition section 2.6):
#   S_int(l) >= sum_{z>=1} h g(zh) - h sum_{z>=2} h qbar(zh) - neg1(l),   h = l^{-1/3} <= H0,
#   g(zeta) = zeta * int_0^{6-zeta H0} Phi(zeta,kappa) dkappa  (Phi = producer's integrand with h -> H0),
#   sum_z h g(zh) >= int psi~ - H0 max psi~   (psi~ = unimodal step minorant of g built from cell infima),
#   sum_z h qbar(zh) <= int phi~ + H0 max phi~ (phi~ = unimodal step majorant of qbar).
# Every cell infimum/supremum is obtained from the monotonicity of each factor (stated beside the code) and evaluated
# in mpmath interval arithmetic; erf is evaluated by its alternating Taylor series with the first omitted term as remainder.
import sys, math, time
from multiprocessing import Pool
from mpmath import iv, mp, mpf

iv.dps = 40
mp.dps = 40
L0 = int(sys.argv[1]) if len(sys.argv) > 1 else 25000
N1 = int(sys.argv[2]) if len(sys.argv) > 2 else 800      # zeta cells on [0, ZMAX]
N2 = int(sys.argv[3]) if len(sys.argv) > 3 else 600      # s cells on [0, sqrt(6)]  (kappa = s^2)
DNU = mpf(sys.argv[4]) if len(sys.argv) > 4 else mpf('0.1')
NQ = int(sys.argv[5]) if len(sys.argv) > 5 else 3200     # qbar cells on [0, ZQ]
NPROC = int(sys.argv[6]) if len(sys.argv) > 6 else 4

H0s = '0.0342'                                           # H0 >= L0^{-1/3} checked below
ZMAX = mpf('4.1'); ZQ = mpf(12)
H0 = iv.mpf(H0s)
SQ2PI_INV = 1 / iv.sqrt(2 * iv.pi)
UMAX = iv.sqrt(6 * H0)
C1 = 1 / (2 * (1 - UMAX))
TWO_SQPI = 2 / iv.sqrt(iv.pi)


def lo(x):  # lower end of an interval as an mp number
    return mpf(x.a)


def hi(x):
    return mpf(x.b)


def erf_iv(X):
    """Rigorous enclosure of erf on the interval X (erf is increasing)."""
    def at(x):  # x: mpf point
        neg = x < 0
        x = abs(x)
        Xp = iv.mpf(x)
        x2 = Xp * Xp
        term = Xp            # x^{2n+1}/n!
        S = iv.mpf(0)
        n = 0
        xf = float(x)
        while True:
            t = term / (2 * n + 1)
            if n > xf * xf + 2 and float(abs(t).b) < 1e-42:
                rem = abs(t).b       # alternating, |terms| decreasing from here: |tail| <= first omitted term
                S = iv.mpf([S.a - rem, S.b + rem])
                break
            S = S + t if n % 2 == 0 else S - t
            n += 1
            term = term * x2 / n
        val = TWO_SQPI * S
        return -val if neg else val
    lo = at(X.a); hi = at(X.b)
    return iv.mpf([lo.a, hi.b])


def I_iv(a, b, nu):
    """Enclosure of I(a,b,nu)=int_nu^inf v^{-3/2} e^{-a v-b/v} dv (a>=0, b>0, nu>0), closed form via erf."""
    y = iv.sqrt(b / nu)
    if a.b <= 0:
        return iv.sqrt(iv.pi / b) * erf_iv(y)
    x = iv.sqrt(a * nu); r = 2 * iv.sqrt(a * b)
    e1 = 1 - erf_iv(x - y); e2 = 1 - erf_iv(x + y)
    return iv.sqrt(iv.pi / b) / 2 * (iv.exp(-r) * e1 - iv.exp(r) * e2)


def check_I():
    for (a, b, nu) in [('0.3', '0.5', '2.0'), ('1.2', '3.1', '4.4'), ('0.01', '0.08', '0.7'), ('0', '1.5', '3')]:
        A, B, NU = mpf(a), mpf(b), mpf(nu)
        q = mp.quad(lambda v: v ** -1.5 * mp.exp(-A * v - B / v), [NU, NU + 10, NU + 100, mp.inf])
        e = I_iv(iv.mpf(a), iv.mpf(b), iv.mpf(nu))
        assert e.a - mpf('1e-14') <= q <= e.b + mpf('1e-14'), (a, b, nu, q, e)   # sanity check of the closed form against quadrature
    # erf sanity
    for x in ['0.5', '2.3', '-1.7', '4.6']:
        e = erf_iv(iv.mpf(x)); v = mp.erf(mpf(x))
        assert e.a <= v <= e.b and float(e.delta) < 1e-25 * 1e5


# s-grid (shared by all zeta cells)
S_MAX = mp.sqrt(6)
SG = [S_MAX * j / N2 for j in range(N2 + 1)]        # grid points: fixed mp numbers (used exactly below)
PP = []; LL = []; KR = []; DS = []
for j in range(N2):
    sl = iv.mpf(SG[j]); sr = iv.mpf(SG[j + 1])
    # 2s*Pmin(s^2) = 2sqrt(2/pi) s (s^2+H0^2)^{-1/2} exp(-H0^2/(12(s^2+H0^2))) - 3.2 s^2 H0 ;
    # first part increasing in s (evaluate at sl), subtracted part increasing in s (evaluate at sr)
    A = 2 * iv.sqrt(2 / iv.pi) * sl / iv.sqrt(sl * sl + H0 * H0) * iv.exp(-H0 * H0 / (12 * (sl * sl + H0 * H0)))
    B = iv.mpf('3.2') * sr * sr * H0
    PP.append(max(mpf(0), lo(A - B)))
    kr = sr * sr                                   # kappa_{j+1} (interval)
    KR.append(kr)
    LL.append(lo(1 - kr * H0 - H0 ** 3))           # 1 - kappa H0 - H0^3 decreasing in kappa
    DS.append(lo(sr - sl))


def cell(i):
    za = ZMAX * i / N1; zb = ZMAX * (i + 1) / N1   # mp numbers
    if i == 0:
        return (i, mpf(0))
    Za = iv.mpf(za); Zb = iv.mpf(zb)
    # a' = (zeta-H0)_+/2 >= (za-H0)_+/2 ; b' = zeta^2/2 >= za^2/2.  I, exp(-a' nu), exp(-b'/nu) decrease in a', b'.
    dlo = max(mpf(0), lo(Za - H0))
    ap = iv.mpf(dlo) / 2
    bp = iv.mpf(lo(Za * Za / 2))
    Bmin = lo(iv.exp(-Zb ** iv.mpf('1.5') - C1 * Zb * Zb * H0))     # B_min decreasing in zeta
    pref = SQ2PI_INV * iv.exp(-iv.mpf(dlo) * Za / 2)                  # exp(-(zeta-H0)_+ zeta/2) decreasing in zeta
    g0 = hi(Zb * Zb / 3)                                              # validity: nu >= zeta^2/3 for every zeta in the cell
    Tcache = {}

    def Tcell(k):   # upper bound of T_max(zeta, nu) for zeta in cell, nu in [g_k, g_{k+1}]
        if k in Tcache: return Tcache[k]
        gk = iv.mpf(g0 + k * DNU); gk1 = iv.mpf(g0 + (k + 1) * DNU)
        f = H0 * H0 * Zb * gk ** iv.mpf('-1.5') * iv.exp(-ap * gk - bp / gk1)
        val = hi(pref * iv.exp(Zb ** 3 * H0 / (3 * gk * gk)) * (f + Zb * I_iv(ap, bp, gk)))
        Tcache[k] = val
        return val

    acc = iv.mpf(0)
    for j in range(N2):
        if PP[j] <= 0: continue
        nulo = lo(6 - KR[j] - Zb * H0)              # lower bound of nu over the cell
        if nulo < g0: break                          # nu_lo decreases in j; remaining cells dropped (integrand >= 0)
        k = int(math.floor(float((nulo - g0) / DNU)))
        while g0 + k * DNU > nulo: k -= 1            # g_k <= nu_lo (mp comparison of exact numbers)
        while g0 + (k + 1) * DNU <= nulo: k += 1
        G = lo(iv.mpf(Bmin) - iv.mpf(Tcell(k)))
        if G <= 0: continue
        E = iv.exp(-Zb * KR[j] - Zb * H0 * H0)       # decreasing in zeta, kappa: corner (zb, kappa_{j+1})
        acc += iv.mpf(DS[j]) * iv.mpf(PP[j]) * iv.mpf(LL[j]) * iv.mpf(lo(E)) * iv.mpf(G)
    return (i, lo(Za * acc))


def qbar_cells():
    """Cell suprema of qbar on [0, ZQ].  For z>=2, h<=H0, z<=R:  zeta-h >= m(zeta):=max(zeta/2, zeta-H0),
    zeta h <= zeta^{1/2} UMAX and zeta h <= zeta H0, zeta h^2 <= min(zeta H0^2, 6 H0); hence
    qbar(zeta) = sqrt2 zeta^{3/2} exp(-zeta sqrt(m) + min(zeta^2 H0, UMAX zeta^{3/2})/3) (1+min(zeta H0^2, 6H0)) / (sqrt(m) - min(zeta H0, UMAX zeta^{1/2})/3)."""
    out = []
    for i in range(NQ):
        za = ZQ * i / NQ; zb = ZQ * (i + 1) / NQ
        Za = iv.mpf(za); Zb = iv.mpf(zb)
        if i == 0:
            # on (0, zb]: m >= zeta/2, exp(-zeta sqrt m) <= 1:  qbar <= 2 zeta (1+zeta H0^2) e^{zeta^2 H0/3} / (1 - sqrt(2 zeta) H0/3)
            v = 2 * Zb * (1 + Zb * H0 * H0) * iv.exp(Zb * Zb * H0 / 3) / (1 - iv.sqrt(2 * Zb) * H0 / 3)
            out.append(hi(v)); continue
        ma = iv.mpf(max(za / 2, lo(Za - H0)))                       # m increasing: lower end at za
        ex_up = min(hi(Zb * Zb * H0), hi(UMAX * Zb ** iv.mpf('1.5')))
        dd_up = min(hi(Zb * H0), hi(UMAX * iv.sqrt(Zb)))
        D = iv.sqrt(ma) - iv.mpf(dd_up) / 3
        assert lo(D) > 0
        fac = 1 + iv.mpf(min(hi(Zb * H0 * H0), hi(6 * H0)))
        v = iv.sqrt(2) * Zb ** iv.mpf('1.5') * iv.exp(-Za * iv.sqrt(ma) + iv.mpf(ex_up) / 3) * fac / D
        out.append(hi(v))
    return out


if __name__ == '__main__':
    t0 = time.time()
    assert lo(iv.mpf(H0s) ** 3 * L0) >= 1, "H0 must be >= L0^{-1/3}"
    assert 6 * mpf(L0) ** (mpf(2) / 3) <= mpf(L0) / 4, "R <= l/4 needed (l >= 13824)"
    check_I()
    with Pool(NPROC) as pool:
        res = pool.map(cell, range(N1), chunksize=4)
    res.sort()
    psi = [v for (_, v) in res]
    p = max(range(N1), key=lambda i: psi[i])
    env = list(psi)
    for i in range(p - 1, -1, -1): env[i] = min(env[i], env[i + 1])
    for i in range(p + 1, N1): env[i] = min(env[i], env[i - 1])
    dz = iv.mpf(ZMAX) / N1
    S_env = iv.mpf(0)
    for v in env: S_env += iv.mpf(v)
    integral = lo(dz * S_env)
    gmax = iv.mpf(max(env))
    pos = lo(iv.mpf(integral) - H0 * gmax)
    # negative term
    qs = qbar_cells()
    pq = max(range(NQ), key=lambda i: qs[i]); envq = list(qs)
    for i in range(1, pq + 1): envq[i] = max(envq[i], envq[i - 1])
    for i in range(NQ - 2, pq - 1, -1): envq[i] = max(envq[i], envq[i + 1])
    dq = iv.mpf(ZQ) / NQ
    Sq = iv.mpf(0)
    for v in envq: Sq += iv.mpf(v)
    # tail zeta >= ZQ=12: m >= zeta/2, so qbar <= sqrt2 zeta^{3/2}(1+6H0) exp(-zeta^{3/2}(1/sqrt2 - UMAX/3)) / (zeta^{1/2}(1/sqrt2 - UMAX/3))
    #  = c zeta e^{-c2 zeta^{3/2}};  c2 zeta^{3/2} - zeta - log(c zeta) is increasing on [12,inf) (derivative 1.5 c2 zeta^{1/2} - 1 - 1/zeta > 0)
    #  and positive at 12 (checked), so qbar <= e^{-zeta} there and sum_{zh>=12} h qbar(zh) <= e^{-12+H0}.
    c2 = 1 / iv.sqrt(2) - UMAX / 3
    cc = iv.sqrt(2) * (1 + 6 * H0) / c2
    zt = iv.mpf(12)
    assert lo(c2 * zt ** iv.mpf('1.5') - zt - iv.log(cc * zt)) > 0 and lo(iv.mpf('1.5') * c2 * iv.sqrt(zt) - 1 - 1 / zt) > 0
    sumq = hi(dq * Sq + H0 * iv.mpf(max(envq)) + iv.exp(-zt + H0))
    L = iv.mpf(L0)
    neg1 = hi(L ** -2 * iv.sqrt(2 / iv.pi) * iv.sqrt(6) * L ** (iv.mpf(1) / 3) * iv.sqrt(2 / L) * (L + 1))
    neg = hi(H0 * iv.mpf(sumq) + iv.mpf(neg1))
    s0 = lo(iv.mpf(pos) - iv.mpf(neg))
    print(f"L0={L0} H0={H0s} N1={N1} N2={N2} DNU={DNU} NQ={NQ}")
    print(f"  int psi~ >= {mp.nstr(integral, 8)},  max psi~ = {mp.nstr(hi(gmax), 6)} (peak cell {p}, zeta~{float(ZMAX*p/N1):.3f})")
    print(f"  positive part >= {mp.nstr(pos, 8)}")
    print(f"  sum_z h qbar <= {mp.nstr(sumq, 8)};  neg1 <= {mp.nstr(neg1, 4)};  negative part <= {mp.nstr(neg, 8)}")
    print(f"  ==> s0_cert = {mp.nstr(s0, 8)}   (interval arithmetic, dps={iv.dps});  time {time.time()-t0:.0f}s")
