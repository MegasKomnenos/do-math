# R11 검산: D.critical-window-rig의 구간 검증 상수 (수치 대조; 인증 아님)
from mpmath import mp, mpf, cos, sin, exp, log, pi, cot, zeta, sqrt, arg, mpc, findroot
mp.dps = 30
def loget(phi): return 1 - phi*cot(phi) + log(phi/sin(phi))
print("log et(1/2) =", loget(mpf(1)/2))
et12 = exp(loget(mpf(1)/2))
# min over ag' in (0,1] of max(Im xi, et(1/2)-|xi|)
best = None
N = 200000
for i in range(1, N+1):
    a = mpf(i)/N
    ax = exp(1-cos(a)); im = ax*sin(a-sin(a))
    v = max(im, et12-ax)
    if best is None or v < best[0]: best = (v, a)
print("min max(Im xi, et(1/2)-|xi|) =", best)
print("166 k^{-1/6} e^{-0.1267 k} at k=10001: log =", log(166) - log(mpf(10001))/6 - mpf('0.1267')*10001, " pi/0.019 =", pi/mpf('0.019'))
# xi-1 constants on 0<ag'<=1
lo = hi = None; imlo = None
for i in range(1, 20001):
    a = mpf(i)/20000
    pt = mpc(cos(a), sin(a)); xi = pt*exp(1-pt)
    r = abs(xi-1)/a**2; im = (xi-1).imag/a**3
    lo = r if lo is None else min(lo, r); hi = r if hi is None else max(hi, r); imlo = im if imlo is None else min(imlo, im)
print("|xi-1|/ag'^2 in [", lo, ",", hi, "]   Im(xi-1)/ag'^3 >=", imlo)
# ray constants: arg phihat = -pi/8, |phi| <= 1/2 ; lg, Re L/|phi|^2 (ku-free in phi variable), arg qy
def ser(phi, M=60):
    s = 0; d = 0
    for m in range(1, M+1):
        l = (2+mpf(1)/m)*zeta(2*m)/pi**(2*m)
        s += l*phi**(2*m); d += 2*m*l*phi**(2*m-2)
    return s, d
mxlg = 0; mnre = 9; mxabs = 0; mxq = 0; amin = 9; amax = -9
w = exp(mpc(0, -pi/8))
for i in range(1, 401):
    rho = mpf(i)/800
    phi = rho*w
    L, lg = ser(phi)
    mxlg = max(mxlg, abs(lg)); mnre = min(mnre, L.real/rho**2); mxabs = max(mxabs, abs(L)/rho**2)
    q = exp(L)-1
    mxq = max(mxq, abs(q)/rho**2); an = arg(q)*180/pi; amin = min(amin, an); amax = max(amax, an)
print("max|lg| =", mxlg, " min Re L/|phi|^2 =", mnre, " max|L|/|phi|^2 =", mxabs, " max|qy|/|phi|^2 =", mxq, " arg qy in [", amin, ",", amax, "] deg")
print("1-cos(1) =", 1-cos(1), " (>=0.458)")
