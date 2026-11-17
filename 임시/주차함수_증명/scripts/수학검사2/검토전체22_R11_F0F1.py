# R11 검산: D.central-gap-rational-audit (ㅁ) — int F0 = 0, int F1 = 46 sqrt2 - 12, J 선도 적분 3 sqrt(2 pi)
from mpmath import mp, mpf, quad, exp, sqrt, pi, inf, erfi
mp.dps = 25
ninf = 2/sqrt(pi)
def Pq(z, r):
    mu = 1 - r*r
    return mu*z*z + mu*mu*z**4/4
def dawson_like(b):  # D(b) = e^{-b^2/2} int_0^b e^{v^2/2} dv
    return exp(-b*b/2)*sqrt(pi/2)*erfi(b/sqrt(2))
def BorldR(b):  # Bor^ld_R(b) e^{-b^2/2} = 2 - 2 b D(b)
    return (2 - 2*b*dawson_like(b))*exp(b*b/2)
def F0(z):
    f = lambda r: r*r*exp((1-r*r)*z*z/2)*Pq(z, r)*BorldR(r*z)/sqrt(2*pi)
    return -ninf*z**4*exp(-z*z)*quad(f, [0, 1])
def F1(z):
    f = lambda r: r*r*exp((1-r*r)*z*z/2)*Pq(z, r)*(mpf(4)/3*r*r*z*z - mpf(2)/3*r*z**4)
    return -ninf*z**4*exp(-z*z)*quad(f, [0, 1])
I0 = 2*quad(F0, [0, 2, 5, 10, 20, 40])   # F0 even in z
I1 = 2*quad(F1, [0, 2, 5, 10, 20, 40])
print("int F0 =", I0)
print("int F1 =", I1, " 46 sqrt2 - 12 =", 46*sqrt(2) - 12)
J = quad(lambda z: z**3*exp(-z*z/2)*quad(lambda r: r*((2-r**3)/3*z**3 - r*z), [0, 1]), [-inf, 0, inf])
print("J leading =", J, " 3 sqrt(2 pi) =", 3*sqrt(2*pi))
