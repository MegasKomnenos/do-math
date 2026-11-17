# R12: 시험 함수 Omega의 적분 ∫_0^6 Omega(s) sqrt(2s/pi) ds ≈ 0.744 검산 (절점 선형 보간; 안전 인자 포함)
import numpy as np, math, json, os
w = r"C:\math\임시\주차함수_증명\원고_자료\세션_재계산\r030ffae_window\work"
x = np.load(os.path.join(w, "xKrig.npy")); v = np.load(os.path.join(w, "wKrig.npy"))
print("xKrig len", len(x), x[:3], x[-3:]); print("wKrig len", len(v), v[:3], v[-3:])
K = 1e5; xs = np.arange(len(v))/K**(2/3)
def e(s):
    if s <= -0.1: return 0.0
    if abs(s) < 0.1: return (s+0.1)**2/0.4
    return s
g = np.array([min(1.0, 0.04+0.12*e(xx-1)) for xx in xs])
om = (1-g)*v
om = np.minimum.accumulate(om)
print("Omega(0)=", om[0], " at 0.5,1,2,3,4,6:", [float(np.interp(t, xs, om)) for t in (0.5,1,2,3,4,6)])
mask = xs <= 6
f = om[mask]*np.sqrt(2*xs[mask]/math.pi)
print("integral ~", np.trapezoid(f, xs[mask]))
# 0.744 vs stored table T-hat
qx = np.load(os.path.join(w, "qenv_fix_x.npy")); qv = np.load(os.path.join(w, "qenv_fix_v.npy"))
print("qenv len", len(qx), qx[:3], qx[-2:], qv[:2], qv[-1])
print("stored coordinate spacing range", (np.diff(qx).min(), np.diff(qx).max()))
xo = np.load(os.path.join(w, "xKrig_orig.npy")); vo = np.load(os.path.join(w, "wKrig_orig.npy"))
print("orig len", len(xo), len(vo)); n = min(len(v), len(vo))
print("first", n, "values bitwise equal:", np.array_equal(v[:n], vo[:n]), " first 12927 equal:", np.array_equal(v[:12927], vo[:12927]), " index of first diff:", int(np.argmax(v[:n] != vo[:n])) if not np.array_equal(v[:n], vo[:n]) else None)
