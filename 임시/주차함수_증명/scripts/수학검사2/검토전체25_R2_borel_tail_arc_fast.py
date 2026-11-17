# R2 검산(빠른 판): (4.9)와 증명 조각의 상계 — numpy 배정밀도(표본 시험; 증명이 아니라 반례 탐색)
import numpy as np, math
from numpy.polynomial.legendre import leggauss
c = 1/math.sqrt(2*math.pi)
K = 5000
j = np.arange(1, K+1, dtype=float)
gammaln = np.vectorize(math.lgamma)
lb = -j + (j-1)*np.log(j) - gammaln(j+1)
Bor = np.exp(lb)
tail = 1 - np.cumsum(Bor)          # Bor^tail_k(1)
S = np.cumsum(j*Bor)
d1 = 2*c/np.sqrt(j) - tail
d2 = S - (2*c*np.sqrt(j) - 2/3)
print('piece1: min', d1.min(), 'max ratio', (d1/(5/9*c*j**-1.5))[:2000].max())
print('piece2: min', d2[:2000].min(), 'max ratio', (d2/(2/3*c*j**-0.5))[:2000].max())
xg, wg = leggauss(400)
def gl(f, a, b):
    x = 0.5*(b-a)*xg + 0.5*(b+a); return 0.5*(b-a)*np.sum(wg*f(x))
def h(w, phi):
    z = phi*w
    small = np.abs(z) < 1e-3
    val = np.where(small, phi**2*np.sqrt(w)*(0.5 - z/6 + z*z/24), w**-1.5*(np.exp(-z) - 1 + z))
    return val
worst = 0
for a in (0.01, 0.3, 1, 2, 4, 8, 15, 30):
    for fr in (0, 0.3, 0.6, 0.9, 1.0):
        phi = complex(-a, math.sqrt(3)*a*fr)
        w = np.linspace(1e-9, 1, 400001)
        tv = np.sum(np.abs(np.diff(h(w, phi))))
        worst = max(worst, tv/(abs(phi)**2*math.exp(a)))
print('TV/(|phi|^2 e^{-Re phi}) max:', worst)
def Bld(phi):
    f = lambda w: np.where(np.abs(phi*w) < 1e-6, phi*w**-0.5, w**-1.5*(1-np.exp(-phi*w)))
    # 치환 w=u^2 로 특이점 제거
    g = lambda u: 2*u*f(u*u)
    return 2 + sum(gl(g, a0, b0) for a0, b0 in ((1e-12, 0.25), (0.25, 0.5), (0.5, 0.75), (0.75, 1)))
worst = 0; arg = None
for k in (1, 2, 3, 5, 10, 30, 100, 400, 2000):
    for a in (0.0, 0.01, 0.3, 1, 3, 8, 20):
        for fr in (0, 0.5, 1.0):
            phi = complex(-a, math.sqrt(3)*a*fr)
            bs = np.sum(Bor[:k]*np.exp(-phi*j[:k]/k))
            lhs = abs(bs - 1 + c*k**-0.5*Bld(phi) - 2/3*phi/k)
            rhs = c*k**-1.5*math.exp(a)*(5/9 + 2/3*abs(phi) + 13/12*abs(phi)**2)
            if lhs/rhs > worst: worst = lhs/rhs; arg = (k, phi)
print('(4.9) lhs/rhs max', worst, 'at', arg)
