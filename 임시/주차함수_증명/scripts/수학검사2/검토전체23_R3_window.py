# R3 검산: 5.4.2절 — 보조정리 hat-normalization의 두 식, cut-rep(다)(라), 상수들을
# 작은 (n,k)에서 수치로 확인한다(e_n, B_{n,k-1}은 순열 열거로 정확히 센다). 배정밀도 격자 적분.
import itertools
import numpy as np
from math import factorial, e, pi, lgamma, log, exp
def caps(sig):
    n = len(sig); h = []
    for i in range(n):
        zz = -1
        for j in range(i-1, -1, -1):
            if sig[j] > sig[i]: zz = j; break
        h.append(i - zz)
    return h
def exact(n, k):
    en = 0; Kkm1 = 0; A = 0
    for sig in itertools.permutations(range(n)):
        h = caps(sig); base = 1; Z = 0
        for hi in h:
            if hi <= k: base *= hi
            else: Z += 1
        if Z >= 2: en += base*Z*(Z-1)*k**(Z-2)
        Kkm1 += base*(k-1)**Z
        a = 1
        for hi in h: a *= min(hi, k-1)
        A += a
    return en, Kkm1 - A
def Bor(j): return exp(-j + (j-1)*log(j) - lgamma(j+1))
def Btail(k, Zc):
    s = 0
    for j in range(1, k+1): s = s + np.exp(-j*Zc)*(j*Zc)**(j-1)/factorial(j)
    return 1 - s
def simpson(f, h):  # f over odd number of points along last axis
    return h/3*(f[..., 0] + f[..., -1] + 4*f[..., 1:-1:2].sum(-1) + 2*f[..., 2:-1:2].sum(-1))
def cumtrap(f, h):
    out = np.zeros_like(f); out[1:] = np.cumsum((f[1:]+f[:-1])/2)*h; return out
def check(n, k, N=200001):
    r = n-k; ku = k**(-1/3); xh = (r+1)*ku**2
    a = np.linspace(0, pi/ku, N); h = a[1]-a[0]
    Af = (1-np.exp(1j*ku*a))/ku
    ptp = np.exp(1j*ku*a)
    ph = k*(1j*ku*a + (1-ptp) + (1-ptp)**2/2)
    Om_e = (n+1)*(ptp-1) - 1j*(n+1)*ku*a + 1j*ku*a - k*(1-ptp)**2/2
    # series form of Omega_e at one point
    a0 = 0.7
    ser = 1j*ku*a0 - xh*a0**2/2 + sum((xh*ku**(m-2) - (2**(m-1)-2)*ku**(m-3))*(1j*a0)**m/factorial(m) for m in range(3, 40))
    p0 = np.exp(1j*ku*a0)
    assert abs(ser - ((n+1)*(p0-1) - 1j*(n+1)*ku*a0 + 1j*ku*a0 - k*(1-p0)**2/2)) < 1e-12
    Om_B = Om_e + ku**2*Af**2/2
    Bt = ku**2*Btail(k, ptp)*np.exp(k*(1-ptp)**2/2)/Bor(k)
    v = np.linspace(0, 1, 20001); hv = v[1]-v[0]
    bt = Btail(k, 1-v).real
    Wr = [simpson(v**2*bt*np.exp(k*v*v/2)*(v*v/2)**j, hv)/Bor(k) for j in range(3)]
    Wh = [Wr[j]/ku**(1+2*j) for j in range(3)]
    vv = v[:-1]
    f = np.zeros_like(v); f[:-1] = vv/(1-vv)*np.exp(-vv*vv/2)*np.exp(-k*(-np.log(1-vv)-vv-vv*vv/2))
    Ih = simpson(f, hv)/ku**2
    w = 1j*np.exp(1j*ku*a)
    Ce = [cumtrap(Af**(2+2*m)*Bt*w, h) for m in range(3)]
    Cb = cumtrap(np.exp((1-ku**3)*ph)*Af*np.exp(ku*Af)*w, h)
    ch0 = Wh[2] + 2*ku*Wh[1] + Ce[2]/4 + ku*Ce[1]
    ch1 = Wh[1] + ku*Wh[0] + Ce[1]/2 + ku*Ce[0]
    ch2 = (Wh[0] + Ce[0])/4
    Ue = simpson(Af*np.exp(Om_e)*(ch0 - Af**2*ch1 + Af**4*ch2), h).real
    UB = simpson(Af*np.exp(Om_B)*(Ih + Cb), h).real
    pn = (n+1)**(n-1); nn = factorial(n)*e**(n+1)/pn
    en, B = exact(n, k)
    print("n=%d k=%d  e_n/p_n exact=%.10f formula=%.10f | B/p_n exact=%.10f formula=%.10f" % (n, k, en/pn, nn*Bor(k)*ku**4*Ue/pi, B/pn, nn*Bor(k)*ku**4*UB/pi))
check(7, 4); check(8, 5); check(9, 5)
