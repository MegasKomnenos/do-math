# 검토전체7 M3: 보조정리 lemma-L (나)의 상수와 L(10^4), 5-5 증명의 하계 재계산
from mpmath import mp, mpf, quad, exp, sqrt, pi, findroot, inf, e as E
mp.dps = 30
def M(q): return quad(lambda y: y**q*exp(-y-y*y/2), [0, inf])
def M26(): return quad(lambda y: y**2*exp(-y-y*y/2), [0, 6])
def Mstar(q):
    # max of y^q e^{-y-y^2/2}: derivative q/y - 1 - y = 0 -> y^2 + y - q = 0
    y = (-1+sqrt(1+4*q))/2
    return y**q*exp(-y-y*y/2)
Ms = {q: M(q) for q in range(6)}
Mst = {q: Mstar(q) for q in range(2, 6)}
C1 = 2*Mst[2] + Ms[3]/2 + Ms[5]/3
C2 = Mst[3]/2 + Mst[5]/3 + Ms[4]/2
C3 = Mst[4]/2 + Ms[3]/6
C4 = Mst[3]/6
def L(r):
    s = sqrt(mpf(r))
    num = M26() - C1/s - C2/s**2 - C3/s**3 - C4/s**4
    den = Ms[1] + (Ms[0]+exp(-mpf(1)/2))/s + 1/s**2
    return num/den
for q in range(6): print("M_%d ="%q, Ms[q])
print("M_2^(6) =", M26())
for q in range(2,6): print("M*_%d ="%q, Mst[q])
print("C1..C4 =", C1, C2, C3, C4)
print("L(10^4) =", L(10**4), ">= 0.845204:", L(10**4) >= mpf('0.845204'))
print("L(144) =", L(144), " L(171) =", L(171))
# 직접 tm_{r-1}(rho_r) at r=10^4 for comparison (truncated sum)
import math
def tm(r, rho, J=4000):
    bt = mpf(1); Nu = mpf(0); De = mpf(0)
    for j in range(0, J):
        if j >= 1:
            bt *= (1 - mpf(j)/r)
            if bt <= 0: break
        w = (j+1)*rho**j*bt
        Nu += j*w; De += w
    return Nu/De
r = 10**4
kr = math.ceil(r**1.5 + 8*r)
rho_r = mpf(kr)/(kr+r)
print("k_r =", kr, " rho_r =", rho_r, " e^{-1/s} =", exp(-1/sqrt(mpf(r))))
t = tm(r, rho_r)
print("tm_{r-1}(rho_r) at r=10^4 =", t, " /s =", t/sqrt(mpf(r)))
t2 = tm(r, exp(-1/sqrt(mpf(r))))
print("tm_{r-1}(e^{-1/s}) =", t2, " /s =", t2/sqrt(mpf(r)), " >= L(10^4):", t2/sqrt(mpf(r)) >= L(10**4))
# Pc(k_r) with eb = 0.845204 s at r = 10^4
s = sqrt(mpf(r)); eb = mpf('0.845204')*s
Pc = kr*(mpf(1)/(2*r) - mpf(1)/(3*r*r)) - mpf(5)/2 + 2*eb*(1 - mpf(1)/kr) - mpf(kr)/(kr-1)*(1+sqrt(3*pi*(r-1)/2))
print("Pc(k_r) at r=10^4 =", Pc, " bound 0.0196 s + 0.496 =", mpf('0.0196')*s + mpf('0.496'))
# r = 171 ... 9999 spot check tm and Pc (unverifiable eb, use true tm)
for r in (171, 500, 2000, 9999):
    kr = math.ceil(r**1.5 + 8*r); rho_r = mpf(kr)/(kr+r)
    t = tm(r, rho_r, J=min(40000, 20*int(r**0.5)+200))
    Pc = kr*(mpf(1)/(2*r) - mpf(1)/(3*r*r)) - mpf(5)/2 + 2*t*(1 - mpf(1)/kr) - mpf(kr)/(kr-1)*(1+sqrt(3*pi*(r-1)/2))
    print("r", r, "k_r", kr, "tm", t, "Pc(k_r) with eb=tm:", Pc)
