# R11 검산: D.critical-window-rig — 호 |phi| = 1/2, -pi/8 <= arg phi <= 0 위의 상수와 호 기여의 상계 (수치 대조; 인증 아님)
from mpmath import mp, mpf, cos, sin, exp, log, pi, zeta, mpc, arg
mp.dps = 25
ls = [(2+mpf(1)/m)*zeta(2*m)/pi**(2*m) for m in range(1, 80)]
def ser(phi):
    s = 0; d = 0
    for m, l in enumerate(ls, 1):
        s += l*phi**(2*m); d += 2*m*l*phi**(2*m-2)
    return s, d
print("sum_{m>=2} l_m 4^{1-m} =", sum(l*mpf(4)**(1-m) for m, l in enumerate(ls, 1) if m >= 2))
rho = mpf(1)/2
arc = []
mxlg = 0; mnre = 9; mnabs_et = 9; mxim = -9
for i in range(0, 401):
    th = -pi/8*(1-mpf(i)/400)
    phi = rho*exp(mpc(0, th))
    L, lg = ser(phi)
    et = exp(L)
    arc.append(et)
    mxlg = max(mxlg, abs(lg)); mnre = min(mnre, L.real/rho**2); mnabs_et = min(mnabs_et, abs(et)); mxim = max(mxim, et.imag)
print("arc: max|lg| =", mxlg, " min Re log et/|phi|^2 =", mnre, " min|et| =", mnabs_et, " max Im et =", mxim)
# min over arc and ag' in (0,1] of |et - xi|
best = None
for j in range(1, 2001):
    a = mpf(j)/2000
    xi = mpc(cos(a), sin(a)); xi = xi*exp(1-xi)
    for et in arc[::4]:
        v = abs(et-xi)
        if best is None or v < best[0]: best = (v, a)
print("min |et - xi| over arc x (0,1] =", best)
# crude bound max(ag'^3/6, e^{0.085} - e^{1-cos ag'})
b2 = min(max(mpf(j)**3/2000**3/6, exp(mpf('0.085'))-exp(1-cos(mpf(j)/2000))) for j in range(1, 2001))
print("min max(ag'^3/6, e^{0.085}-|xi|) =", b2, "  1.8*10001^(-2/3) =", mpf('1.8')*mpf(10001)**(-mpf(2)/3))
k = mpf(10001); R0 = sqrt_k = k**mpf('0.5')/2
print("arc bound log at k=10001:", log(pi/8*mpf('1.03')*R0**3/mpf('1.8')) - mpf('0.34')*R0**2)
# whole sector check of the three ray constants (grid)
mx = 0; mn = 9
for i in range(1, 101):
    r = mpf(i)/200
    for jj in range(0, 41):
        th = -pi/8*jj/40
        L, lg = ser(r*exp(mpc(0, th)))
        mx = max(mx, abs(lg)); mn = min(mn, L.real/r**2)
print("sector |phi|<=1/2, -pi/8<=arg<=0: max|lg| =", mx, " min Re log et/|phi|^2 =", mn)
