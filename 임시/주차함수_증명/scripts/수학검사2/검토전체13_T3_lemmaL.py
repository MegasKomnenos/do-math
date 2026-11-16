# 보조정리 lemma-L (나)의 상수와 L(10^4), 정리 old-5-5 증명의 수치 검산
from mpmath import mp, quad, exp, sqrt, pi, findroot, mpf, inf, e
mp.dps = 30
f = lambda i: (lambda y: y**i*exp(-y-y*y/2))
M = [quad(f(i), [0, inf]) for i in range(6)]
M26 = quad(f(2), [0, 6])
def Mstar(i):
    # max of y^i e^{-y-y^2/2}: derivative i/y -1 - y =0 -> y^2+y-i=0
    y = (-1+sqrt(1+4*i))/2
    return f(i)(y)
Ms = {i: Mstar(i) for i in range(2,6)}
C1 = 2*Ms[2]+M[3]/2+M[5]/3
C2 = Ms[3]/2+Ms[5]/3+M[4]/2
C3 = Ms[4]/2+M[3]/6
C4 = Ms[3]/6
def L(r):
    s = sqrt(r); st = 1/s
    return (M26 - st*C1 - st**2*C2 - st**3*C3 - st**4*C4)/(M[1]+st*(M[0]+exp(-0.5))+st**2)
print("M_i", [mp.nstr(x,10) for x in M]); print("M2^(6)", mp.nstr(M26,10)); print("M*", {i: mp.nstr(v,10) for i,v in Ms.items()})
print("L(10^4)", mp.nstr(L(10**4),10), "L(144)", mp.nstr(L(144),10), "L(10^5)", mp.nstr(L(10**5),10))
print("sqrt(3pi/2)", mp.nstr(sqrt(3*pi/2),10), "sqrt(pi/2)", mp.nstr(sqrt(pi/2),10))
print("0.5+2*0.845204-sqrt(3pi/2)", mp.nstr(mpf('0.5')+2*mpf('0.845204')-sqrt(3*pi/2),10))
s=mpf(100); print("bracket at s=100", mp.nstr(1/(3*s)+8/(3*s*s)+mpf('2.507')/s**2+(1+mpf('2.1709')*s)/s**3,10))
# direct tm_{r-1}(rho_r) for a few r, compare with eb_r = 0.845204*s and with L(r)*s
from fractions import Fraction
def tm(r, rho, J=None):
    # tm_{r-1}(rho) = sum j (j+1) rho^j bt_j / sum (j+1) rho^j bt_j
    nu=mpf(0); de=mpf(0); bt=mpf(1)
    for j in range(0, r):
        w=(j+1)*rho**j*bt
        nu+=j*w; de+=w
        bt*= (1-mpf(j+1)/r)
        if bt==0: break
    return nu/de
import math
for r in (171, 500, 2000, 9999, 10000, 20000):
    kr = math.ceil(r**1.5+8*r); rho_r=mpf(kr)/(kr+r); s=sqrt(r)
    t = tm(r, rho_r)
    Pc = kr*(mpf(1)/(2*r)-mpf(1)/(3*r*r)) - mpf(5)/2 + 2*t*(1-mpf(1)/kr) - mpf(kr)/(kr-1)*(1+sqrt(3*pi*(r-1)/2))
    print(r, kr, "tm", mp.nstr(t,8), "tm/s", mp.nstr(t/s,8), "L(r)", mp.nstr(L(r),8) if r>=144 else None, "Pc with tm", mp.nstr(Pc,6))
