# -*- coding: utf-8 -*-
"""R12: D.window-mass-env 의 시험 함수 Omega 값·도함수 상계·적분 0.744 를 배정밀도로 다시 센다(대조용, 읽기 전용)."""
import numpy as np, math, os
W = r'C:\math\임시\주차함수_증명\원고_자료\세션_재계산\r030ffae_window\work'
x = np.load(os.path.join(W, 'xKrig.npy')); w = np.load(os.path.join(W, 'wKrig.npy'))
print('knots', len(x), 'x[1]*K^(2/3)', x[1] * 1e5 ** (2 / 3), 'x[-1]', x[-1], 'w[0]', w[0])
h = 1e5 ** (-2 / 3)
xi = np.arange(len(w)) * h
def e(s):
    return 0.0 if s <= -0.1 else ((s + 0.1) ** 2 / 0.4 if abs(s) < 0.1 else s)
g = np.array([min(1.0, 0.04 + 0.12 * e(t - 1)) for t in xi])
y = (1 - g) * w
ym = np.minimum.accumulate(y)
print('cummin changed', int(np.sum(ym != y)))
D = np.diff(y) / h
d = np.empty(len(y))
d[1:-1] = 2 * D[:-1] * D[1:] / (D[:-1] + D[1:])
d[0] = (3 * D[0] - D[1]) / 2; d[-1] = (3 * D[-1] - D[-2]) / 2
print('end slopes', d[0], d[-1], 'all secants negative', bool(np.all(D < 0)))
d[0] = min(d[0], 0.0); d[-1] = min(d[-1], 0.0)
al = d[:-1] / D; be = d[1:] / D
print('alpha,beta max', al.max(), be.max(), 'min', al.min(), be.min())
def Om(t):
    i = min(int(t / h), len(y) - 2); s = (t - i * h) / h
    h00 = 2 * s**3 - 3 * s**2 + 1; h10 = s**3 - 2 * s**2 + s; h01 = -2 * s**3 + 3 * s**2; h11 = s**3 - s**2
    return h00 * y[i] + h10 * h * d[i] + h01 * y[i + 1] + h11 * h * d[i + 1]
print('Omega at 0,0.5,1,2,3,4,6:', [round(Om(t), 4) for t in (0, 0.5, 1, 2, 3, 4, 6)])
# max |Omega'| and sup s|Omega''| on a fine grid
ts = np.linspace(0, 6, 600001)
vals = np.array([Om(t) for t in ts[::20]])
# derivative per piece: endpoints and interior extremum
a = -6 * D + 3 * d[:-1] + 3 * d[1:]; b = 6 * D - 4 * d[:-1] - 2 * d[1:]; c = d[:-1]
n6 = int(6 / h) + 1
m1 = 0; k2 = 0
for i in range(n6):
    cand = [abs(c[i]), abs(a[i] + b[i] + c[i])]
    if a[i] != 0:
        s0 = -b[i] / (2 * a[i])
        if 0 < s0 < 1: cand.append(abs(a[i] * s0 * s0 + b[i] * s0 + c[i]))
    m1 = max(m1, max(cand))
    m2 = max(abs(b[i]), abs(2 * a[i] + b[i])) / h
    k2 = max(k2, (i + 1) * h * m2)
print('max|Omega\'| ~', m1, ' sup s|Omega\'\'| (piece bound) ~', k2)
# integral int_0^6 Omega(s) sqrt(2 s/pi) ds
N = 600000
tt = (np.arange(N) + 0.5) * 6 / N
I = sum(Om(t) * math.sqrt(2 * t / math.pi) for t in tt) * 6 / N
print('integral', I)
# table T: slopes
Q = r'C:\math\임시\주차함수_증명\원고_자료\r030ffae'
qx = np.load(os.path.join(Q, 'qenv_fix_x.npy')); qv = np.load(os.path.join(Q, 'qenv_fix_v.npy'))
print('T points', len(qx), 'max |x_i - i/2000|', np.max(np.abs(qx - np.arange(len(qx)) / 2000)), 'z0', qv[0], 'z_last', qv[-1])
sl = np.diff(qv) / 0.0005
print('max|T\'|', np.abs(sl).max(), 'TV(T\')', np.abs(np.diff(sl)).sum(), 'T(0.0005)', qv[1], 'T(0.001)', qv[2])
rx = np.load(os.path.join(Q, 'qenv_rig_x.npy')); rv = np.load(os.path.join(Q, 'qenv_rig_v.npy'))
print('rig vs fix: differing indices', np.nonzero(rv != qv)[0][:20], 'rig first values', rv[:12])
