# 저장된 봉투 표와 시험 함수 표의 거친 점검 (검토전체7 M8). python -I
import sys, numpy as np, math
base = r"C:/math/임시/주차함수_증명/원고_자료/세션_재계산/r030ffae_window/work/"
try:
    x = np.load(base+"qenv_fix_x.npy"); v = np.load(base+"qenv_fix_v.npy")
    print("table len", len(x), len(v), "x0,x1,x400,x12000", x[0], x[1], x[400], x[-1])
    d = v[:-1]-v[1:]
    print("strictly decreasing:", bool((d>0).all()), "min decrease", d.min(), "argmin", d.argmin())
    print("max slope |dz/dxi|", (d/np.diff(x)).max(), "z0", v[0], "z400", v[400], "z4200", v[4200], "z12000", v[-1])
except Exception as e:
    print("table load failed", e)
try:
    xk = np.load(base+"xKrig.npy"); wk = np.load(base+"wKrig.npy")
    print("Krig len", len(xk), len(wk), "x last", xk[-1], "w0", wk[0])
    def ramp(s):
        return np.where(s<=-0.1, 0.0, np.where(s<0.1, (s+0.1)**2/0.4, s))
    g = np.minimum(1.0, 0.04+0.12*ramp(xk-1))
    om = (1-g)*wk
    om_mono = np.minimum.accumulate(om)
    print("changed by cummin:", int((om_mono!=om).sum()), "Omega(0)", om[0], "Omega(6)", om[-1])
    sec = np.diff(om)/np.diff(xk)
    print("max |secant|", np.abs(sec).max(), "at xi", xk[np.abs(sec).argmax()])
    # Fritsch-Carlson interior slopes: harmonic mean of neighbouring secants (same sign)
    m = np.zeros_like(om)
    s1, s2 = sec[:-1], sec[1:]
    hm = np.where(s1*s2>0, 2*s1*s2/(s1+s2), 0.0)
    m[1:-1] = hm
    print("max |interior slope|", np.abs(m).max())
    # second derivative estimate from secant differences
    h = np.diff(xk)[0]
    dd = np.diff(sec)/h
    print("max xi*|Omega''| (secant-based)", (np.abs(dd)*xk[1:-1]).max(), "at", xk[1:-1][(np.abs(dd)*xk[1:-1]).argmax()])
except Exception as e:
    print("Krig load failed", e)
