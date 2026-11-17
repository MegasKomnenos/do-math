# -*- coding: utf-8 -*-
"""R12: (8.23)의 LB^low(k,nu)를 본문 식 그대로(합 꼴) 배정밀도로 점 평가해 부록 D.band-boxes 의 상자 하계와 견준다(대조용)."""
import numpy as np, math, os, sys
W = r'C:\math\임시\주차함수_증명\원고_자료\세션_재계산\r030ffae_window\work'
Q = r'C:\math\임시\주차함수_증명\원고_자료\r030ffae'
w = np.load(os.path.join(W, 'wKrig.npy')); qv = np.load(os.path.join(Q, 'qenv_fix_v.npy'))
h = 1e5 ** (-2 / 3)
xi = np.arange(len(w)) * h
def e(s): return 0.0 if s <= -0.1 else ((s + 0.1) ** 2 / 0.4 if abs(s) < 0.1 else s)
y = (1 - np.array([min(1.0, 0.04 + 0.12 * e(t - 1)) for t in xi])) * w
D = np.diff(y) / h
d = np.empty(len(y)); d[1:-1] = 2 * D[:-1] * D[1:] / (D[:-1] + D[1:]); d[0] = min(0.0, (3 * D[0] - D[1]) / 2); d[-1] = min(0.0, (3 * D[-1] - D[-2]) / 2)
def Om(t):
    i = min(int(t / h), len(y) - 2); s = (t - i * h) / h
    return (2*s**3-3*s**2+1)*y[i] + (s**3-2*s**2+s)*h*d[i] + (-2*s**3+3*s**2)*y[i+1] + (s**3-s**2)*h*d[i+1]
def That(t):
    i = min(int(t / 0.0005), len(qv) - 2); s = t / 0.0005 - i
    return qv[i] * (1 - s) + qv[i + 1] * s
from math import lgamma, exp, log, floor, ceil
def Bor(m): return exp((m - 1) * log(m) - m - lgamma(m + 1))
NB = 40000
bor = np.array([0.0] + [Bor(m) for m in range(1, NB + 1)])
borle = np.cumsum(bor)
ren = bor * np.arange(NB + 1)
psi = np.cumsum(ren)
def hfun(k, nu): return k / (k + nu) - k / (2 * k - 1)
def c0(N, k):
    a = (1 - 1 / k) ** (N - k + 1)
    b = 1 - math.exp(7 / 6) * N ** 1.5 / (4 * (2 * math.pi) ** -0.5 * k * (2 * k - 1 - N))
    return max(a, b)
def LB(k, nu):
    n = 2 * k + nu; N = k + nu
    qmax = floor(6 * k ** (2 / 3)); qfb = floor((3 * (k - 1) / 4 - qmax - 3) / 8)
    if nu >= qmax + 1: case = 'i'; qw = qmax; qstar = 6 * k ** (2 / 3)
    elif nu - 1 >= k / 4: case = 'ii'; qw = nu - 1; qstar = nu - 1
    else: case = 'iii'; qw = qmax; qstar = None
    def R(kk, nn_):
        s = 0.0
        for q in range(1, qw + 1):
            x = (q - 1) / kk ** (2 / 3)
            s += (1 - q * nn_ / (kk * (kk + nn_))) ** 1.5 * kk / (kk + q) * (That(x) + psi[q - 1] * Om(x))
        return s / kk
    fbk = sum((k / n * borle[qfb]) ** i for i in range(8)); fbk1 = sum(((k - 1) / n * borle[qfb]) ** i for i in range(8))
    LOWk = LOWk1 = 0.0
    if case != 'iii':
        if nu >= qfb + 2:
            La = k / (n - k) - k / (2 * k + 2) * exp(-hfun(k, nu)); Lc = (k / (k + qfb + 1) - 0.5) if qfb >= qw else math.inf
            La1 = (k - 1) / (k + nu + 1) - (k - 1) / (2 * k) * exp(-hfun(k - 1, nu + 2)); Lc1 = ((k - 1) / (k + qfb + 1) - 0.5) if qfb >= qw else math.inf
        else:
            La = k / (n - k) - max(0.5, k / (n - qfb)); Lc = math.inf
            La1 = (k - 1) / (k + nu + 1) - max(0.5, (k - 1) / (n - qfb)); Lc1 = math.inf
        for i in range(8):
            Li = k / (k + qstar + 1) - k / (2 * k + 2 - (i + 1) * qfb)
            Li1 = (k - 1) / (k + qstar) - (k - 1) / (2 * k + 2 - (i + 1) * qfb)
            LOWk += (k / n * borle[qfb]) ** i * 0.5 * max(0.0, min(La, Lc, Li))
            LOWk1 += ((k - 1) / n * borle[qfb]) ** i * 0.5 * max(0.0, min(La1, Lc1, Li1))
    val = borle[nu - 1] * exp(-1 / (12 * (n + 1))) * k / n * (exp(-5 / (12 * k)) * R(k, nu) * fbk + LOWk + c0(N, k) * (exp(-5 / (12 * (k - 1))) * R(k - 1, nu + 2) * fbk1 + LOWk1))
    return val, case
for (k, nu) in [(6668, 3200), (6668, 3184), (6668, 2126), (6668, 2125), (6668, 1668), (6668, 1667), (6668, 103), (6935, 3328), (6800, 3264), (20000, 9600), (20000, 5000), (20000, 4421), (20000, 103)]:
    print(k, nu, LB(k, nu))
