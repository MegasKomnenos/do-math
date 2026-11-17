# R2 검산: 중앙 상쇄 항등식(F_0의 전체 적분 0)과 F_1의 전체 적분 46*sqrt2-12, (라)의 산술
import numpy as np, math
from numpy.polynomial.legendre import leggauss
ninf = 2/math.sqrt(math.pi); c = 1/math.sqrt(2*math.pi)
xg, wg = leggauss(200)
def gl(f, a, b):
    x = 0.5*(b-a)*xg + 0.5*(b+a)
    return 0.5*(b-a)*np.sum(wg*f(x))
def Pq(z, r):
    m = 1-r*r; return m*z*z + m*m*z**4/4
def F1(z):
    return -ninf*z**4*math.exp(-z*z)*gl(lambda r: r*r*np.exp((1-r*r)*z*z/2)*Pq(z, r)*(4/3*r*r*z*z - 2/3*r*z**4), 0, 1)
I1 = 2*sum(gl(np.vectorize(F1), a, b) for a, b in ((0, 2), (2, 4), (4, 7), (7, 12), (12, 25)))
print('int F1 =', I1, ' 46*sqrt2-12 =', 46*math.sqrt(2)-12)
def Dw(b):
    return math.exp(-b*b/2)*gl(lambda v: np.exp(v*v/2), 0, b) if b > 0 else 0.0
def g(b): return 2 - 2*b*Dw(b)   # = BldR(b) e^{-b^2/2}
gv = np.vectorize(g)
def F0(z):
    # r^2 e^{mu z^2/2} Pq * c * BldR(rz) e^{-z^2} = r^2 Pq c g(rz) e^{-z^2/2}
    return -ninf*z**4*math.exp(-z*z/2)*gl(lambda r: r*r*Pq(z, r)*c*gv(r*z), 0, 1)
I0 = 2*sum(gl(np.vectorize(F0), a, b) for a, b in ((0, 2), (2, 4), (4, 7), (7, 12), (12, 30)))
I0abs = 2*sum(gl(np.vectorize(lambda z: abs(F0(z))), a, b) for a, b in ((0, 2), (2, 4), (4, 7), (7, 12), (12, 30)))
print('int F0 =', I0, ' (int |F0| =', I0abs, ')')
k = 10000.0; om = 6.98
c3 = om - 3.5 - (4*om+0.5)*1.2879*0.0464159 - 13*om/2*0.939*k**(-2/3) - 12*om/k
print('C3', c3, 'k^-1/3', k**(-1/3))
print('M0', 4*math.sqrt(2)*(1-23.75/k))
bD = (46*math.sqrt(2)-12-54.6828-1e-22)*math.exp(1/k)-1e-19
print('k^3 bD >=', bD, 'sum7', 183.51+2303.07+203.57+983.74+920.70+454.86+418.83)
bJ = 0.4503*3*math.sqrt(2*math.pi) + 1675.2/k + 2e-20
print('bJ <=', bJ, 'Bn', math.sqrt(2)/math.pi*math.exp(1/k), 'C5', c*(1-1/(12*k)))
print('total', 5.642*1.6809*0.39893 - 0.0163 - 3.554)
G = 1/8
print('y_k', (2*k-1)*math.log(math.sqrt(1+G*G)) - k*G*G/2, 63*k/8192 - 127/16384)
