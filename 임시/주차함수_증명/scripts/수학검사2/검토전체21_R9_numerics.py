# -*- coding: utf-8 -*-
# R9 검산: 9.3 표의 문턱, 9.6 가족의 첫 열, 명제 check-na·check-ga 표의 명시 함수 값, 각 상수.
import math
def simpson(f, a, b, n=20000):
    if b <= a: return 0.0
    if n % 2: n += 1
    h = (b-a)/n; s = f(a)+f(b)
    for i in range(1, n):
        s += (4 if i % 2 else 2)*f(a+i*h)
    return s*h/3
PI = math.pi
# ---- 9.3 표 ----
print("== 9.3 표: 범위 조건")
for k in [6667, 6668, 8064, 8065, 9948, 9949, 9950]:
    numin = max(103, 20001-2*k); print(k, "nu_min=", numin, "3k-1=", 3*k-1, "0.48k=", 0.48*k, "띠 존재:", numin <= 0.48*k)
print("20001 > 2.48k  <=> k <", 20001/2.48)
# ---- 가족 첫 열 ----
print("== 가족 첫 열")
def first_k(cond, start=6668):
    k = start
    while not cond(k): k += 1
    return k
print("2  :", first_k(lambda k: max(103, 20001-2*k) <= 0.48*k))
print("1b :", first_k(lambda k: max(103, 20001-2*k) <= 2*k**(2/3)), " (9551: nu_min, 2k^{2/3}) =", 20001-2*9551, 2*9551**(2/3), " 9550:", 20001-2*9550, 2*9550**(2/3))
print("1a :", first_k(lambda k: max(103, 20001-2*k) <= 1.3*k**(2/3)), " (9705:", 20001-2*9705, 1.3*9705**(2/3), " 9704:", 20001-2*9704, 1.3*9704**(2/3), ")")
print("8065:", 20001-2*8065, 0.48*8065)
# ---- 기본 함수 ----
def u(k): return 3/0.35*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5
def BdT(k, nu): return (k+nu)*u(k)*(1/(k-1)+1/k)+3*(k+1)*(k-1)**-1.5
def DDL(k): return 14*(math.log(3*k)-1)/(5*math.sqrt(PI*k))+37.6/(5*math.sqrt(PI)*k)
def sup(d, y): return min(1.0, 1.15*(y+d)/d**1.5)
def ec(k, nup): return 3*nup**2/((k-1)*k)+4.8*math.sqrt(nup)/k+nup**2/(2*(k-1)**2)
def thetaf(x): return (2*math.exp(-x)-1)*math.exp(-x)
theta0 = thetaf(0.48)
def ebar(k):
    xi = (math.sqrt(5*k*math.log(k))+2)/k
    return math.exp(1.5/k)*(math.exp(math.sqrt(5*math.log(k)/k)+1/k)+2.40918*k**(1.5-2.5/(1+xi)))
def abar(k): return 3*1.15*(1.48*k+2)/(0.48*k+1)**1.5
def bbar(k): return 2*u(k)*(2*k-1)/(k-1)+3*(k+1)*(k-1)**-1.5
def dbar(k): return 72.217/math.sqrt(k)
def cAb(r): return 2*math.sqrt(r)/(1-r)+2*math.log((1+math.sqrt(r))/(1-math.sqrt(r)))
def Sub(k, nubar):
    xs = (nubar+4)/(k-1)
    if xs >= 0.6: return 0.0
    return (k-1)/k*simpson(lambda r: (r-xs)*(1+r)*r**-1.5*(1-r)**-2, xs, 0.6)
def Top(k, nubar):
    return simpson(lambda r: min(2, 2+(nubar+1)/k-r)*(1+r/3)*r**-1.5, 0.6-2.6/k, 1.0)
def Flat(y):
    ab = (1.15*(y+2*y**(2/3)))**(2/3); return 2*(ab-1)/(y+2-ab)
def Ab(y, k, nubar):
    z = 0.6+1/y
    return 1.15*(1+1/y)*(4*((1.15*y)**(2/3)-1)**-0.5+y**-0.5*(2*cAb(z)-4*z**-0.5-Sub(k, nubar)))
def StaysUp(k, nubar):
    return sum(Flat(y)+Ab(y, k, nubar) for y in (k-1, k))+2*16.54*k**-0.5*Top(k, nubar)
print("== 상수")
print("theta0 =", theta0, " cR =", math.sqrt(2*PI)/2*math.exp(1/12), " f1 =", 4/(3*math.sqrt(2*PI)))
print("pi_two const (2pi)^-1/2 e^-1 2^1.5 =", (2*PI)**-0.5*math.exp(-1)*2**1.5, " ×exp(-1/(12·6667)-1/(12·3200)) =", (2*PI)**-0.5*math.exp(-1)*2**1.5*math.exp(-1/(12*6667)-1/(12*3200)), " 1/0.41508 =", 1/0.41508)
print("2cAb(0.6)-4/sqrt(0.6) =", 2*cAb(0.6)-4/math.sqrt(0.6), " Sub 상계 ∫_0^0.6 =", 2*math.sqrt(0.6)/(1-0.6))
br = 0.48**-0.5-1+(1-math.sqrt(0.48))/3; print("대괄호(0.48) =", br, " 132.32×=", 132.32*br, " 4·16.54·2 =", 4*16.54*2)
k=6667; m=math.ceil(math.sqrt(5*k*math.log(k))); print("m_hit(6667) =", m, " 0.09k =", 0.09*k, " 0.48k-1 =", 0.48*k-1)
print("== check-na 표")
for name, k0, nubar in [("벌크", 6668, None), ("2", 8065, 0.48*8065), ("1b", 9551, 2*9551**(2/3)), ("1a", 9705, 1.3*9705**(2/3))]:
    k = k0
    print("--", name, k0, " DDL=", DDL(k))
    if name == "벌크":
        print("  o_F = 4-ebar =", 4-ebar(k), " abar,bbar,dbar =", abar(k), bbar(k), dbar(k), " 합(상계) =", abar(k)+bbar(k)+DDL(k)+dbar(k), " 5항 합=", abar(k)+bbar(k)+DDL(k)+dbar(k)+ebar(k))
        Rs = abar(k)+bbar(k)+DDL(k)+dbar(k); print("  R#_F =", Rs)
    elif name == "2":
        d = 2*k**(2/3)+1; print("  3 s^up_{2k^{2/3}+1}(k+1) =", 3*sup(d, k+1), " theta0 =", theta0, " BdT(k,0.48k) =", BdT(k, 0.48*k))
        oF = 4-3*sup(d, k+1)+theta0-BdT(k, 0.48*k)-DDL(k); print("  o_F =", oF, " Stays^up(k;0.48k) =", StaysUp(k, nubar), " 여유=", oF-StaysUp(k, nubar))
        Rs = 3*sup(d, k+1)+BdT(k, 0.48*k)+DDL(k)+StaysUp(k, nubar); print("  R#_F =", Rs)
    elif name == "1b":
        d = 1.3*k**(2/3)+1; xi2 = 2*k**(2/3)/(k-1)
        print("  3 s^up_{1.3k^{2/3}+1}(k+1) =", 3*sup(d, k+1), " theta(xi2) =", thetaf(xi2), " BdT(k,2k^{2/3}) =", BdT(k, 2*k**(2/3)))
        oF = 4-3*sup(d, k+1)+thetaf(xi2)-BdT(k, 2*k**(2/3))-DDL(k); print("  o_F =", oF, " Stays^up =", StaysUp(k, nubar), " 여유=", oF-StaysUp(k, nubar))
        Rs = 3*sup(d, k+1)+BdT(k, 2*k**(2/3))+DDL(k)+StaysUp(k, nubar); Rp = BdT(k, nubar)+DDL(k)+StaysUp(k, nubar); print("  R#_F =", Rs, " R#'_F =", Rp)
    else:
        print("  e^c(k,1.3k^{2/3}) =", ec(k, 1.3*k**(2/3)), " BdT(k,1.3k^{2/3}) =", BdT(k, 1.3*k**(2/3)))
        oF = 2-ec(k, 1.3*k**(2/3))-BdT(k, 1.3*k**(2/3))-DDL(k); print("  o_F =", oF, " Stays^up =", StaysUp(k, nubar), " 여유=", oF-StaysUp(k, nubar))
        Rs = 3+BdT(k, 1.3*k**(2/3))+DDL(k)+StaysUp(k, nubar); Rp = BdT(k, nubar)+DDL(k)+StaysUp(k, nubar); print("  R#_F =", Rs, " R#'_F =", Rp)
    print("  eps0 =", math.floor(2**(2/3)*(k0+1)**(2/3)))
# ---- check-ga (b) 가장자리 ----
f1 = 4/(3*math.sqrt(2*PI)); cR = math.sqrt(2*PI)/2*math.exp(1/12)
def slow(d, y): return math.exp(-f1*((y+d-1)/y)**1.5*d**1.5/y)
def Q(y, xi):
    k = y-1; q0 = xi*y**(2/3)
    pref = k/(k+1)*(1-q0/(2*k))*2*(2*PI)**-0.5*math.exp(-1/12)*y/(cR*q0)
    A = math.exp(-q0/y)*slow(q0, y)*(math.exp(-cR*q0/y)-math.exp(-cR*q0*math.sqrt(q0/2)/y))
    B = math.exp(-q0/(2*y))*slow(q0/2, y)*(math.exp(-cR*q0*math.sqrt(q0/2+1)/y)-math.exp(-cR*q0**1.5/y))
    return pref*(A+B)
print("== check-ga (b) 가장자리")
def Rsharp(name, k):
    if name == "벌크": return abar(k)+bbar(k)+DDL(k)+dbar(k)
    if name == "2": return 3*sup(2*k**(2/3)+1, k+1)+BdT(k, 0.48*k)+DDL(k)+StaysUp(k, 0.48*k)
    if name == "1b": return 3*sup(1.3*k**(2/3)+1, k+1)+BdT(k, 2*k**(2/3))+DDL(k)+StaysUp(k, 2*k**(2/3))
    return 3+BdT(k, 1.3*k**(2/3))+DDL(k)+StaysUp(k, 1.3*k**(2/3))
def Rprime(name, k):
    nb = 2*k**(2/3) if name == "1b" else 1.3*k**(2/3)
    return BdT(k, nb)+DDL(k)+StaysUp(k, nb)
for name, k0 in [("벌크", 6668), ("2", 8065), ("1b", 9551), ("1a", 9705)]:
    xic = 1.3 if name == "1a" else 2**(2/3)
    y = k0+1
    val = 4*slow(xic*y**(2/3)+1, k0)+2*Q(y, xic)
    print(name, k0, " 4 s^low + 2Q =", val, " R# =", Rsharp(name, k0), " 여유 =", val-Rsharp(name, k0))
    if name in ("1a", "1b"):
        v2 = Q(y, 2**(2/3))+slow(2**(2/3)*y**(2/3)+1, k0)
        print("   m0>N:  Q+s^low =", v2, " R#' =", Rprime(name, k0), " 여유 =", v2-Rprime(name, k0))
# ---- old-8-32 (iii) 상수 ----
print("== old-8-32(iii) 상수")
ge = lambda t: math.exp(-t)*(1+1.5*t)
print("beta0 min =", cR*1.04**1.5/math.sqrt(2), " g^e(1.0216) =", ge(1.0216), " iota q0 max =", cR*2**(2/3)*6669**(-1/3), " e^-x(1+x) at 0.115 =", math.exp(-0.115)*1.115, " 1-x^2/2 =", 1-0.115**2/2)
print("beta2 range =", cR*1.04**1.5, cR*2, " sqrt(1/2+1/562) =", math.sqrt(0.5+1/562), " |g^e'|(1.02),(2.73) =", abs(math.exp(-1.02)*(0.5-1.5*1.02)), abs(math.exp(-2.73)*(0.5-1.5*2.73)), " 0.234*0.2916*1.444 =", 0.234*0.2916*1.444)
print("q0 at y=6669, xi=1.04:", 1.04*6669**(2/3), " xi y^{2/3} at y=6669,xi=1.3 :", 1.3*6669**(2/3))
# ---- 9.4 벌크 범위 조건 ----
print("0.48·6667 =", 0.48*6667, " 1.5(2k+3)^{2/3} at 6667 =", 1.5*(2*6667+3)**(2/3))
print("(2k)^{2/3} at k=6667 =", (2*6667)**(2/3), " 0.99+0.59963(2k+1)^{2/3}+1.24847(2k+1)^{1/3} =", 0.99+0.59963*(13335)**(2/3)+1.24847*13335**(1/3))
