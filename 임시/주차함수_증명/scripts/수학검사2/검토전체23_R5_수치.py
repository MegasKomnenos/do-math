# 검토전체23 R5: 장6 수치 재계산 (부동소수; mpmath 없이 math와 fractions만 사용)
import math
from math import sqrt, pi, exp, log, e, floor

s2pi = (2*pi)**-0.5
print("== 6.1 ==")
# tau_1: (1-t)^{5/2} = 1-2t
lo, hi = 0.1, 0.45
f = lambda t: (1-t)**2.5 - 1 + 2*t
for _ in range(200):
    mid = (lo+hi)/2
    if f(mid) < 0: lo = mid
    else: hi = mid
print("tau_1", lo)
print("2/sqrt(pi)", 2/sqrt(pi), "2^-1.5", 2**-1.5)
print("(1.15*2000)^(2/3)", (1.15*2000)**(2/3))
def coef(chi, q):
    return 2*s2pi*(0.25*(1-1/(2*q))**-1.5 + (1+chi+chi*chi)*(1-chi)**-0.5*(1+chi)**-1.5)
for chi in (0.9, 0.99, 0.9999):
    print("coef chi", chi, coef(chi, 175))
# monotone of second term
prev = -1
ok = True
for i in range(1, 100000):
    chi = i/100000
    v = (1+chi+chi*chi)*(1-chi)**-0.5*(1+chi)**-1.5
    if v < prev: ok = False
    prev = v
print("second bracket term increasing in chi:", ok)
print("Mn bound (0.9]", 2*s2pi*3*sqrt(1-0.81), "(0.99]", 2*s2pi*3*sqrt(1-0.9801))
print("1.1284+2.82/175", 1.1284+2.82/175, "1.044+9.3/175", 1.044+9.3/175, "0.34+85/175", 0.34+85/175)
print("gain(0.02)/0.02", ((1-0.02)**-1.5-1)/0.02, "1.28/sqrt50", 1.28/sqrt(50), "2 s2pi sqrt(50/0.77)", 2*s2pi*sqrt(50/0.77))
print("1-0.9999^3", 1-0.9999**3)

print("== 6.2 ==")
def B2(k):
    return (1-1/e) + (exp(1.5+1/k)-1)*2*(sqrt(k+1)-1)/(sqrt(2*pi)*(k+1))
print("B2(43)", B2(43), "B2(2000)", B2(2000), "1-B2(2000)", 1-B2(2000))

print("== 6.3 ==")
X = (5-sqrt(7))/6
print("X*", X, X*(1-X)*(3-2*X), (10+7*sqrt(7))/54)
print("tl^-1 bound", 1/(1-0.75/51), "e^(1/24+1/612)", exp(1/24+1/612), "1+1/51", 1+1/51)
print("u bound", 1.0443*1.0150*1.01961*4/3, "M/G", 0.5282*1.449)
print("L/G V>=2", 1.5/53*(4/3)*0.5*1.01961*1.0150, "V=1", 1.5/52*2.02*0.51*1.01961*1.0150)
print("e^(3/102)", exp(3/102), "e^-2", exp(-2), "1.545/e", 1.545/e)
y=50
print("d=3 ratio at y=50", 0.0441*(y-1)*(y+2)**2/(1.2*(y+1)*(y+3)), "0.2*0.6/e", 0.2*0.6/e)
print("2e^-2+e^-1-1.03e^-2/51", 2*exp(-2)+exp(-1)-1.03*exp(-2)/51)
print("t/(y+1) ratio bound", exp(-1+3/(2*51))/2, "<=1/5")

print("== 6.4 ==")
def u(k): return 3/0.35*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5
def ub(k): return 1.15/0.35*(2+1/k)*(0.65-1/k)**-1.5*k**-0.5
print("u(2001)", u(2001), "ub(2001)", ub(2001), "u(10001)", u(10001), "ub(6667)", ub(6667))
wp = lambda n: 1.99+0.59963*(n+1)**(2/3)+1.24847*(n+1)**(1/3)
print("wp(20000)", wp(20000), "max wp on 4002..20000", max(wp(n) for n in range(4002,20001)))
print("(4002)^(2/3)", 4002**(2/3), "0.65*2001-1", 0.65*2001-1, "(20002)^(2/3)", 20002**(2/3), "0.65*10001-1", 0.65*10001-1)
print("9*(1.5)^1.5", 9*1.5**1.5, "*4/3", 12*1.5**1.5)

print("== 6.5 ==")
def DDLn(k): return 14*(log(3*k)-1)/(5*sqrt(pi*k)) + 37.6/(5*sqrt(pi)*k)
for k in (2001, 6667, 6668, 8065, 9551, 9705):
    print("DDLn", k, DDLn(k))
print("7(3-log3)+42/sqrt3", 7*(3-log(3))+42/sqrt(3))
print("3*1.3752/sqrt(pi)", 3*1.3752*sqrt(2)*s2pi, "21/(5 sqrt pi)", 21/(5*sqrt(pi)))
print("1.3778^2 (1+2/2001)^2/6", 1.3778**2*(1+2/2001)**2/6)
print("Acrit const", (1+1/2001)*(1+2/2001)/(1-3/(4*2001))*1.3752)
print("0.5(e^(3/4002)+1)", 0.5*(exp(3/4002)+1), "1+0.7503/2", 1+0.7503/2)
def v(k): return 2-4.6/sqrt(k+1)-2*ub(k)-0.5*DDLn(k)
print("v(2001)", v(2001), "v(6667)", v(6667), "parts2001", 4.6/sqrt(2002), 2*ub(2001), 0.5*DDLn(2001), "parts6667", 4.6/sqrt(6668), 2*ub(6667), 0.5*DDLn(6667))

print("== 6.6 ==")
k=2001
eps = k**(-1/3)
Dbar = 3*eps/(6-2*eps)
UB = s2pi*(1+Dbar)**1.5*(4/3*(3/(6-2*eps))**1.5 + sqrt(Dbar)*eps**1.5)
sbar = 1.15*sqrt(2)*(3*k-1)*k**-1.5
print("eps", eps, "Dbar", Dbar, "UB", UB, "sbar", sbar, "pref", 4000/6002)
print("final", 0.6664*(1-0.2099-0.1091)-0.2808, "exact-ish", (2*(k-1)/(3*(k-1)+2))*(1-UB-sbar)-ub(k))
def dd(k): return 1/e + u(k)/(e*2**1.5)
print("d(2001)", dd(2001), "d(10001)", dd(10001), "u/(e 2^1.5)", u(2001)/(e*2**1.5), u(10001)/(e*2**1.5))
def Low(k, rho):
    eps = k**(-1/3)
    br = 2*sqrt(rho)-1.6781*eps
    return s2pi*k**(1/3)*br/(1+rho*eps)*exp(-1/(12*(k+1)))*exp(-rho**2*(1+rho*eps)**1.5*exp(1/(4*(k+1)))/(s2pi*br))
print("Low(10001,1.4)", Low(10001,1.4), "Low(2001,0.75)", Low(2001,0.75))
def Obar_far(k): return dd(k)*exp(1+1/(12*k))*(1+1.4*k**(-1/3)+1/k)**1.5
def Obar_far2(k): return dd(k)*exp(1+1/(12*k))*(1+1.4*k**(-1/3))**1.5
def Obar_small(k): return dd(k)*exp(1+1/(12*k))*(1+0.75*k**(-1/3)+1/k)**1.5
print("Obar far 10001", Obar_far(10001), "without 1/k", Obar_far2(10001), "Obar small 2001", Obar_small(2001))
B = 1.6781*2001**(-1/3)
print("B", B, "R(1/2)", 0.75-2*B*0.5**1.5-2*s2pi*sqrt(0.5)+s2pi*B, "0.18581-0.30817*0.1332", 0.18581-0.30817*0.1332)
uu = 2001**(1/3)
print("u", uu, "quad", 0.15037*uu**2-1.54829*uu-1.3365, "root", (1.54829+sqrt(1.54829**2+4*0.15037*1.3365))/(2*0.15037))
print("(6.45) diff at 2001", 0.75*2001**(2/3) - (wp(2001+0.75*2001**(2/3))-1))
print("min (6.45) diff over k 2001..10000", min(0.75*k**(2/3) - (wp(k+0.75*k**(2/3))-1) for k in range(2001,10001)))
print("wp'(1)", 2/3*0.59963*2**(-1/3)+1/3*1.24847*2**(-2/3))
print("10*10001^(2/3)", 10*10001**(2/3), "10/2^(2/3)", 10/2**(2/3))
print("0.39976/12.601+0.41616/12.601^2+1.30212", 0.39976/12.601+0.41616/12.601**2+1.30212)
