# S12 검산: D.critical-window-rig 「식」의 상수 몇 개와 D.newton-m170의 계수 수
from mpmath import mp, mpf, cot, sin, cos, exp, log, e, pi, mpc
mp.dps = 30
def et(phi): return e*phi*exp(-phi*cot(phi))/sin(phi)
print("log et(1/2) =", log(et(mpf(1)/2)))
print("1-cos(1) =", 1-cos(1), " >= 0.458:", (1-cos(1)) >= mpf('0.458'))
# min over ag' in (0,1] of max(Im xi, et(1/2)-|xi|), xi = pt' e^{1-pt'}, pt'=e^{i ag'}
best = None
for i in range(1, 100001):
    a = mpf(i)/100000
    xi = mpc(cos(a), sin(a))*exp(1-mpc(cos(a), sin(a)))
    v = max(xi.imag, et(mpf(1)/2)-abs(xi))
    if best is None or v < best[0]: best = (v, a)
print("min_ag' max(Im xi, et(1/2)-|xi|) =", best)
k = 10001
print("166 k^{-1/6} e^{-0.1267 k} at k=10001: exponent =", log(166) - log(k)/6 - mpf('0.1267')*k)
print("pi/0.019 =", pi/mpf('0.019'))
# newton coefficient counts
print("sum_{r=2}^{40}(r-1) =", sum(r-1 for r in range(2,41)), " sum_{r=2}^{170}(r-1) =", sum(r-1 for r in range(2,171)))
print("coeff count if degree 2r+2 stored:", sum((r-1)*(2*r+3) for r in range(2,41)))
print("coeff count if degree r+d+1 stored:", sum(sum(r+d+2 for d in range(1,r)) for r in range(2,41)))
print("780*45 =", 780*45)
# D.tail-T1 (B) inequality check
L = mpf('0.845204'); s = mpf(100)
lhs = s*(mpf(1)/2 + 2*L - (3*pi/2)**0.5) + mpf(1)/2 - (1/(3*s) + 8/(3*s**2) + mpf('2.507')/s**2 + (1+mpf('2.1709')*s)/s**3)
print("tail (B) lhs at s=100:", lhs, " rhs:", mpf('0.0196')*s+mpf('0.496'))
