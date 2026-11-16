# Peer s637d3ec: interval-arithmetic bound of the region-III constant C_III in Theorem E (exposition 4.5).
# The five terms TA..TE of c3sup.py are rewritten in h = v^{-1/3} so that every factor is bounded on [0, H0]
# (v = h^-3, k0 = 6h^-2 - 1, S1 = S1b h^{-3/2}, S2 = (2pi)^{-1/2}(2/3)h^{-9/2}(1+h^3)^{3/2}, y = h^-3(1+h^3)),
# and sup_{0<h<=H0} e^{h^3/12}(TA+...+TE)/h is bounded by evaluating the rewritten expression over h-cells.
# No monotonicity in h is used.
import sys, math
from mpmath import iv, mp, mpf

iv.dps = 30
NCELL = int(sys.argv[1]) if len(sys.argv) > 1 else 4000
H0 = iv.mpf('0.0342')            # >= 25000^{-1/3}
eps = iv.mpf('0.05'); b = iv.mpf('1.3'); LN2 = iv.log(2)
# zeta(3/2) = sum_{n<N} n^{-3/2} + tail;  f(x)=x^{-3/2} convex decreasing:
#   tail >= int_N^inf f + f(N)/2 (trapezoid over-estimates)  and  tail <= int_{N-1/2}^inf f (midpoint under-estimates)
_N = 2000
_s = iv.mpf(0)
for _n in range(1, _N): _s += iv.mpf(_n) ** iv.mpf('-1.5')
_lo = _s + 2 * iv.mpf(_N) ** iv.mpf('-0.5') + iv.mpf(_N) ** iv.mpf('-1.5') / 2
_hi = _s + 2 * (iv.mpf(_N) - iv.mpf('0.5')) ** iv.mpf('-0.5')
ZETA32 = iv.mpf([_lo.a, _hi.b])
S1b = iv.sqrt(2 / iv.pi); sq = iv.sqrt(2 / iv.pi)
A1 = 2 / (1 - eps) / iv.sqrt(LN2)
A2 = (1 - eps) ** -3 * LN2 ** iv.mpf('-1.5') * ZETA32
c2pi = 1 / iv.sqrt(2 * iv.pi)


def total(h):
    """e^{h^3/12}(TA+TB+TC+TD+TE)/h for h an interval inside [0, H0]."""
    q = 6 - h * h
    sh = iv.sqrt(h)
    a1 = q ** iv.mpf('-0.5') - sh            # (k0^{-1/2} - v^{-1/2})/h
    a2 = q ** iv.mpf('-1.5') - h * sh        # (k0^{-3/2} - v^{-3/2})/h^3
    c1 = 1 - sh * iv.sqrt(q)                 # (v^{1/2} - k0^{1/2}) h^{3/2}
    p = 1 + h ** 3
    TA = 1.5 * sq * (2 * a1 + (iv.mpf(2) / 3) * S1b * sh * a2 + 2 * sh * c1 / p + 2 * S1b * h * sh * a1 / p)
    # TB/h = b sq h^2/(1+h^3) * [I12 + I12up/(v+1) + 2S1(I32 + I12/(v+1)) + S2(I52 + I32/(v+1))]
    #  h^2*I12 = 2 h^{1/2} c1 ; h^2*I12up/(v+1) = (2/3)[h^{1/2}(1+h^3)^{1/2} - h^2 q^{3/2}/(1+h^3)]
    #  h^2*2S1 I32 = 4 S1b h^{3/2} a1 ; h^2*2S1 I12/(v+1) = 4 S1b h^2 c1/(1+h^3)
    #  h^2*S2 I52 = c2pi (4/9) h^{1/2}(1+h^3)^{3/2} a2 ; h^2*S2 I32/(v+1) = c2pi (4/3) h^{3/2} (1+h^3)^{1/2} a1
    TB = b * sq / p * (2 * sh * c1 + (iv.mpf(2) / 3) * (sh * iv.sqrt(p) - h * h * q ** iv.mpf('1.5') / p)
                       + 4 * S1b * h * sh * a1 + 4 * S1b * h * h * c1 / p
                       + c2pi * (iv.mpf(4) / 9) * sh * p ** iv.mpf('1.5') * a2 + c2pi * (iv.mpf(4) / 3) * h * sh * iv.sqrt(p) * a1)
    TC = sq * A1 * 4 * (iv.mpf('0.75') / (p * q * q) + 2 * b * h / (p * p * q) + b * S1b * h * sh / (p * p * q * q))
    TD = b * A2 * sq * (iv.mpf(4) / 3) * sh * a2 / (p * p)
    TE = 8 * b * A1 * A1 * sq * iv.mpf('0.4') * h * q ** iv.mpf('-2.5') / (p * p)
    return iv.exp(h ** 3 / 12) * (TA + TB + TC + TD + TE)


def check_against_float():
    # compare with the original float formulas of c3sup.py at a few points
    K = 6; e_ = 0.05; b_ = 1.3; L = math.log(2); Z = 2.612375348685488; S = math.sqrt(2 / math.pi)
    for hf in [0.005, 0.02, 0.0342]:
        v = hf ** -3.0; k0 = K * hf ** -2 - 1.0
        A1f = 2 / (1 - e_) / math.sqrt(L); A2f = (1 - e_) ** -3 * L ** -1.5 * Z
        S1 = S * v ** 0.5; S2 = (2 * math.pi) ** -0.5 * (2 / 3) * (v + 1) ** 1.5; y = v + 1
        I32 = 2 * (k0 ** -0.5 - v ** -0.5); I52 = (2 / 3) * (k0 ** -1.5 - v ** -1.5); I12 = 2 * (v ** 0.5 - k0 ** 0.5)
        I_12up = (2 / 3) * ((v + 1) ** 1.5 - k0 ** 1.5); I3 = 0.5 * k0 ** -2.0; I2 = 1.0 / k0; I72 = 0.4 * k0 ** -2.5
        TA = 1.5 * S * (I32 + S1 * I52 + I12 / (v + 1) + S1 * I32 / (v + 1))
        TB = b_ * S / y * (I12 + I_12up / (v + 1) + 2 * S1 * (I32 + I12 / (v + 1)) + S2 * (I52 + I32 / (v + 1)))
        TC = S * A1f * 4 * (1.5 / y * v * I3 + 2 * b_ / y ** 2 * v ** 2 * I2 + 2 * b_ * S1 / y ** 2 * v ** 2 * I3)
        TD = b_ / y ** 2 * A2f * v ** 1.5 * S * 2 * v * I52
        TE = b_ / y ** 2 * A1f ** 2 * v * 2 * 4 * v ** 2 * S * I72
        f = math.exp(hf ** 3 / 12) * (TA + TB + TC + TD + TE) / hf
        g = total(iv.mpf(hf))
        assert abs(f - float(g.mid)) < 1e-7 * f, (hf, f, g)
        print(f"  check h={hf}: float {f:.10f}  interval {mp.nstr(g.mid, 11)}")


if __name__ == '__main__':
    check_against_float()
    best = mpf(0); arg = None
    for i in range(NCELL):
        a = H0 * i / NCELL; c = H0 * (i + 1) / NCELL
        h = iv.mpf([a.a, c.b])
        t = total(h)
        if t.b > best:
            best = mpf(t.b); arg = i
    print(f"C_III <= {mp.nstr(best, 8)}  (sup over (0, 0.0342] by {NCELL} interval cells; worst cell {arg})")
