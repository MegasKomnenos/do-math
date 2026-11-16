# ---------- test function Omega ----------
# H1 (2026-11-14): Omega is the EXACT-definition test function shared with window_mass_env/ia.py (D.window-mass-env):
#   knots xi_i = i h with h = K^(-2/3) (interval enclosure), knot values y_i = (1 - g(xi_i)) w_i with the stored binary64
#   table w_i read as exact numbers and g evaluated at the exact knot (interval), Fritsch-Carlson slopes d_i computed in
#   interval arithmetic from the interval y and h.  ia.OmegaIA encloses y, h d and y_{i+1}-y_i; from these the cubic
#   coefficients of every piece are bracketed outward in binary64, each piece is checked to be non-increasing on [0,1]
#   (interval test of p_i' <= 0), and Om_lo(y) is a rigorous lower bound of Omega(y) (hence of Omega on [0, y]).
#   Before H1 this file re-built the record's binary64 PCHIP (cert_lib.PchipW) and read it as exact rationals, which is a
#   slightly different function from the one certified in D.window-mass-env.
sys.path.insert(0, os.path.normpath(os.path.join(HERE, '..', 'window_mass_env')))
import ia as _ia


def _build_omega():
    design, Om, T, changed = _ia.load_design(WORK)
    iv.dps = 34; mp.dps = 34                      # ia.load_design sets iv.dps = 50
    assert changed == 0, "cumulative-minimum step changed a knot value"
    assert Om.fc_ok, "Fritsch-Carlson slope ratios outside [0,3]"
    return Om


OM = _build_omega()
_NO = OM.n
OM_h_lo = float(OM.h.lo); OM_h_hi = float(OM.h.hi)
OM_y_lo = np.asarray(OM.y.lo, dtype=float)


def _omega_coeffs():
    """outward binary64 brackets of the cubic coefficients a0..a3 of p_i(t) = Omega(i h + t h), t in [0,1]:
    a0 = y_i, a1 = h d_i, a2 = 3(y_{i+1}-y_i) - 2 h d_i - h d_{i+1}, a3 = -2(y_{i+1}-y_i) + h d_i + h d_{i+1}
    (interval arithmetic of ia.IA on the interval knot data), and the list of pieces whose non-increase could not be verified."""
    y = OM.y; hd = OM.hd; dy = OM.dy
    hd0 = hd[:-1]; hd1 = hd[1:]
    a0 = y[:-1]; a1 = hd0
    a2 = 3.0 * dy - 2.0 * hd0 - hd1
    a3 = -2.0 * dy + hd0 + hd1
    lo = np.vstack([a0.lo, a1.lo, a2.lo, a3.lo]); hi = np.vstack([a0.hi, a1.hi, a2.hi, a3.hi])
    # p'(t) = a1 + 2 a2 t + 3 a3 t^2 <= 0 on [0,1]: endpoints, and the interior maximum when p' is concave (a3 < 0)
    IA = _ia.IA
    A1 = IA(lo[1], hi[1]); A2 = IA(lo[2], hi[2]); A3 = IA(lo[3], hi[3])
    bad = (A1.hi > 0) | ((A1 + 2.0 * A2 + 3.0 * A3).hi > 0)
    neg = A3.hi < 0
    A3s = IA(np.where(neg, A3.lo, -1.0), np.where(neg, A3.hi, -1.0))
    ts = (-A2) / (3.0 * A3s)
    inside = neg & (ts.hi > 0) & (ts.lo < 1)
    pv = A1 - (A2 * A2) / (3.0 * A3s)
    bad |= inside & (pv.hi > 0)
    amb = (A3.lo <= 0) & (A3.hi >= 0)              # concavity of p' unknown: conservative bound of max p'
    bad |= amb & ((A1.hi + 2.0 * np.maximum(A2.hi, 0.0) + 3.0 * np.maximum(A3.hi, 0.0)) > 0)
    return lo, hi, list(np.nonzero(bad)[0])


OM_lo, OM_hi, OM_bad = _omega_coeffs()
assert not OM_bad, "Omega piece not verified monotone: %s" % OM_bad[:10]


def Om_lo(y):
    """lower bound of Omega(y') for every y' <= y (y: float array >= 0); Omega is non-increasing, so this is a lower bound of
    Omega(y) obtained from an UPPER bound t_hi of the local coordinate t = (y - i h)/h (h in [h_lo, h_hi]) and the lower
    coefficient brackets (Horner with t >= 0).  If y may lie left of the chosen knot, the value at t = 0 (= y_i) is still a
    lower bound by monotonicity."""
    y = np.asarray(y, dtype=float)
    i = np.clip(np.floor(y / OM_h_hi).astype(np.int64), 0, _NO - 2)        # i h <= i h_hi <= y  (up to the division rounding)
    t_hi = up(up(y / OM_h_lo) - i)                                          # >= (y - i h)/h
    shift = (t_hi > 1.0) & (i < _NO - 2)
    i = np.where(shift, i + 1, i)
    t_hi = np.where(shift, up(t_hi - 1.0), t_hi)
    beyond = t_hi > 1.0                                                     # only at the last piece: y beyond the last knot
    t = np.clip(t_hi, 0.0, 1.0)
    rl = OM_lo[3, i].copy()
    for r in (2, 1, 0):
        rl = dn(dn(rl * t) + OM_lo[r, i])
    val = np.maximum(rl, OM_y_lo[i + 1])
    return np.where(beyond, OM_y_lo[-1], val)


