# K3: numeric re-checks for chapter 5A (counts, constants, small identities)
from fractions import Fraction as F
from math import comb, factorial, ceil, floor, log, sqrt, exp, pi, e
import mpmath as mp
mp.mp.dps = 40

def kn(n): return (n+1)//2  # ceil(n/2)
# (a) counts
c2 = sum(kn(n)-1 for n in range(10001,20001))
c4 = sum(max(0, n-2-ceil((n-1)/2)) for n in range(5,20001))
c50 = sum(max(0, n-2-ceil((n-1)/2)) for n in range(20001,50001))
pairs50 = sum(max(0, n-1-ceil((n-1)/2)) for n in range(20001,50001))
pairs20 = sum(max(0, n-1-ceil((n-1)/2)) for n in range(5,20001))
print("74,995,000 ?", c2); print("99,970,002 ?", c4); print("524,955,000 ?", c50)
print("pairs C50 524,985,000 ?", pairs50, " pairs C20 99,989,998 ?", pairs20)
print("14365 ?", sum(r-1 for r in range(2,171)), " 9829 ?", 9999-171+1)
print("rows 50..20000:", 20000-50+1, " rows 50..900:", 900-50+1, " 901..20000:", 20000-901+1)
# (b) Cayley ratio small k
for k in range(1,10):
    cr = F(k+1,k)**(k-2)
    v = cr*(1+F(5,2*k)+F(2,k*k))
    print("k=%d  cr*(1+5/2k+2/k^2) = %.5f  >87/32=%.5f ? %s" % (k, float(v), 87/32, v>F(87,32)))
print("e < 65/24+1/100 ?", e < 65/24+0.01, 65/24+0.01, " 87/32=", 87/32)
# (c) m(n)
def mfun(n):
    m=170
    for mm in range(171, 100000):
        if mm**1.5+9*mm<=n: m=mm
        else: break
    return m
print("m(20001)=", mfun(20001), " m(50001)=", mfun(50001))
print("597:", 597**1.5+9*597, " 598:", 598**1.5+9*598)
# (d) lemma-L constants
Mq = lambda q: mp.quad(lambda y: y**q*mp.e**(-y-y*y/2), [0, mp.inf])
M = [Mq(q) for q in range(6)]
M26 = mp.quad(lambda y: y**2*mp.e**(-y-y*y/2), [0,6])
def Mstar(q):
    ys = (-1+mp.sqrt(1+4*q))/2
    return ys**q*mp.e**(-ys-ys*ys/2)
C1 = 2*Mstar(2)+M[3]/2+M[5]/3; C2 = Mstar(3)/2+Mstar(5)/3+M[4]/2; C3 = Mstar(4)/2+M[3]/6; C4 = Mstar(3)/6
def Lr(r):
    s = mp.sqrt(r)
    return (M26 - C1/s - C2/s**2 - C3/s**3 - C4/s**4)/(M[1] + (M[0]+mp.e**(-0.5))/s + 1/s**2)
print("M0..M5:", [mp.nstr(x,6) for x in M]); print("C1..C4:", mp.nstr(C1,6), mp.nstr(C2,6), mp.nstr(C3,6), mp.nstr(C4,6))
print("L(10^4)=", mp.nstr(Lr(10**4),8), " >=0.845204 ?", Lr(10**4) >= mp.mpf('0.845204'))
print("1/2+2*0.845204-sqrt(3pi/2) =", 0.5+2*0.845204-sqrt(3*pi/2), " sqrt(3pi/2)=", sqrt(3*pi/2))
s=100.0; br = 1/(3*s)+8/(3*s*s)+2.507/(s*s)+(1+2.1709*s)/s**3; print("bracket at s=100:", br)
# tm_{r-1}(rho) direct for check
def tm(d, rho):
    bt = [mp.mpf(1)]
    for j in range(1, d+1): bt.append(bt[-1]*(1-mp.mpf(j)/(d+1)))
    Nu = sum(j*(j+1)*rho**j*bt[j] for j in range(d+1)); De = sum((j+1)*rho**j*bt[j] for j in range(d+1))
    return Nu/De
for r in [10**4]:
    print("tm_{r-1}(e^{-1/sqrt r})/sqrt r at r=1e4:", mp.nstr(tm(r-1, mp.e**(-1/mp.sqrt(r)))/mp.sqrt(r),6))
# tm_d(1) <= sqrt(pi d/2)
for d in [1,2,5,20,100,1000]:
    print("d=%d tm_d(1)=%s sqrt(pi d/2)=%s" % (d, mp.nstr(tm(d,1),6), mp.nstr(mp.sqrt(mp.pi*d/2),6)))
# (e) misc constants in 5-11 proof, cover-edge, 5-15
print("27.14^3=", 27.14**3, " 27.14^2=", 27.14**2, " 0.75*736.5=", 0.75*736.5)
print("(149/200)^3=", (149/200)**3, " (16/25)^2=", (16/25)**2, " (3/4)^3=", 0.75**3, " (13/20)^2=", 0.65**2)
print("27/(4*27.14)=", 27/(4*27.14))
print("1/(1+9/sqrt598)=", 1/(1+9/sqrt(598)))
print("(1.2*20001)^(2/3)=", (1.2*20001)**(2/3), " (1.5*20001)^(2/3)=", (1.5*20001)**(2/3))
print("(9/5)^(2/3)=", 1.8**(2/3), " 10*2^(-2/3)=", 10*2**(-2/3))
print("rq bounds:", 1.2/sqrt(598), 1.5/sqrt(833), 1.8/sqrt(966), 2.1/sqrt(2164), 2.4/100, " 1/16=", 1/16)
print("5/12*sqrt(598)=", 5/12*sqrt(598))
print("omitted-tail: 2.4*(1+1/598)/sqrt(598)=", 2.4*(1+1/598)/sqrt(598), " 12/(110e)=", 12/(110*e), " 1/24=", 1/24)
print("(12/11)^1.5*(1+1/598)=", (12/11)**1.5*(1+1/598))
print("log10(1.15*598^3)=", log(1.15*598**3,10), " 598*log10(24)=", 598*log(24,10))
print("rq* = 13/20*(1+3/529)/23 =", 13/20*(1+3/529)/23, " 1/12=", 1/12)
print("0.64^(2/3), 0.65^(2/3):", 0.64**(2/3), 0.65**(2/3))
print("20/13*529^1.5=", 20/13*529**1.5)
print("log et(1/2) =", 0.5*0.25 + 0.0625/36 + 0.015625/405 + (2.25*mp.zeta(8)/mp.pi**8)*0.5**8)
print("l_m:", [mp.nstr((2+mp.mpf(1)/m)*mp.zeta(2*m)/mp.pi**(2*m),8) for m in (1,2,3)])
print("1/sqrt(598)=", 1/sqrt(598), " 10001^(-1/3)=", 10001**(-1/3), " 0.0015/1.25^12=", 0.0015/1.25**12)
print("2*sqrt2/e=", 2*sqrt(2)/e, " 181/174=", 181/174, " 26/25=", 1.04)
print("(63/32)=", 63/32)
# Robbins check of kernel bound at m=1..5
for m in range(1,6):
    Ren = F(m)**m/factorial(m)  # times e^{-m}
    cb = F(comb(2*m,m), 4**m)
    val = float(Ren)*exp(-m)/(float(cb)/sqrt(2))
    print("m=%d Ren/(o cb)=%.6f  in [1, 1+1/(12(2m-1))=%.6f]  >=1+1/(25(2m-1))=%.6f" % (m, val, 1+1/(12*(2*m-1)), 1+1/(25*(2*m-1))))
