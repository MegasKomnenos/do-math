# 검토전체4 J3: 장5A 수치 검산
from fractions import Fraction as F
from math import *
import sympy as sp

print("== 5.1 개수 ==")
print("둘째 조각 비교 수:", sum(ceil(n/2)-1 for n in range(10001,20001)))
print("넷째 조각 위치 수:", sum(n-2-ceil((n-1)/2) for n in range(5,20001)), 94192042+5777960)
print("C50 위치 수(ℓ≤n-3):", sum(n-2-ceil((n-1)/2) for n in range(20001,50001)))
print("C50 위치 수(ℓ≤n-2):", sum(n-1-ceil((n-1)/2) for n in range(20001,50001)))
print("27.14^3 =", 27.14**3, " 20001^(2/3)=", 20001**(2/3), " floor(0.75*20001^(2/3))=", floor(0.75*20001**(2/3)))
print("(149/200)^3 =", (149/200)**3, " (16/25)^2 =", (16/25)**2, " (3/4)^3=", (3/4)**3, " (13/20)^2=", (13/20)**2)

print("== cayley ratio k=1..9 ==")
for k in range(1,10):
    cr = F(k+1,k)**(k-2)
    v = cr*(1+F(5,2*k)+F(2,k*k))
    print(k, float(v), v > F(87,32))
print("e vs 65/24+1/100, 87/32:", e, 65/24+0.01, 87/32)
print("14365 =", sum(r-1 for r in range(2,171)))

print("== m(n) ==")
def mfun(n):
    m=171
    while (m+1)**1.5+9*(m+1) <= n: m+=1
    return max(170, m) if m**1.5+9*m<=n else 170
print("m(20001)=", mfun(20001), " m(50001)=", mfun(50001), " check 597:", 597**1.5+9*597, 598**1.5+9*598)
print("1/(1+9/sqrt(598))=", 1/(1+9/sqrt(598)))
print("24001.2^(2/3)=", (1.2*20001)**(2/3), " 832^1.5=",832**1.5," 833^1.5=",833**1.5)
print("(1.5*20001)^(2/3)=", (1.5*20001)**(2/3))
print("rq bounds:", 1.2/sqrt(598), 1.5/sqrt(833), 1.8/sqrt(966), 2.1/sqrt(2164), 2.4/100, 1/16)
print("1/sqrt(598)=", 1/sqrt(598))
print("(12/11)^1.5=", (12/11)**1.5, " 12/(110e)=", 12/(110*e), " 1/24=", 1/24, " (r+1)/n bound:", 2.4*(1+1/598)/sqrt(598))
print("log10(1.15*598^3)=", log10(1.15*598**3), " 598*log10(24)=", 598*log10(24))
print("10/2^(2/3)=", 10/2**(2/3), " (9/5)^(2/3)=", (9/5)**(2/3))

print("== lemma-L L(10^4) ==")
from mpmath import mp, quad, exp as mexp, inf, findroot, mpf, sqrt as msqrt
mp.dps = 30
G = lambda q: (lambda y: y**q*mexp(-y-y*y/2))
M = {q: quad(G(q),[0,inf]) for q in range(6)}
M26 = quad(G(2),[0,6])
def Mstar(q):
    # max of y^q e^{-y-y^2/2}: derivative q/y -1 - y =0 -> y^2+y-q=0
    y = (-1+msqrt(1+4*q))/2
    return G(q)(y)
Ms = {q: Mstar(q) for q in range(2,6)}
C1 = 2*Ms[2]+M[3]/2+M[5]/3
C2 = Ms[3]/2+Ms[5]/3+M[4]/2
C3 = Ms[4]/2+M[3]/6
C4 = Ms[3]/6
def L(r):
    s = msqrt(r)
    num = M26 - C1/s - C2/s**2 - C3/s**3 - C4/s**4
    den = M[1] + (M[0]+mexp(-0.5))/s + 1/s**2
    return num/den
print("L(10^4)=", L(10**4), " L(144)=", L(144))
print("1.2534 vs sqrt(pi/2):", sqrt(pi/2), " sqrt(3pi/2)=", sqrt(3*pi/2))
print("0.5+2*0.845204-sqrt(3pi/2)=", 0.5+2*0.845204-sqrt(3*pi/2))
s=100.0
print("bracket at s=100:", 1/(3*s)+8/(3*s*s)+2.507/s**2+(1+2.1709*s)/s**3)
# direct tm_{r-1}(rho) check for r=10^4
def tm(r, rho):
    bt = mpf(1); Nu=mpf(0); De=mpf(0)
    for j in range(0, r):
        w = (j+1)*rho**j*bt
        Nu += j*w; De += w
        bt *= (1-mpf(j+1)/r)
        if bt < mpf(10)**-40: break
    return Nu/De
r=10**4; kr = ceil(r**1.5+8*r); rho = mpf(kr)/(kr+r)
print("tm_{r-1}(rho_r)/s for r=1e4:", tm(r,rho)/msqrt(r), " tm(e^{-1/s})/s:", tm(r, mexp(-1/msqrt(r)))/msqrt(r))
# Pc check at r=171 with true tm
r=171; kr=ceil(r**1.5+8*r); rho=mpf(kr)/(kr+r); eb = tm(r,rho)
Pc = kr*(1/(2*mpf(r))-1/(3*mpf(r)**2)) - mpf(5)/2 + 2*eb*(1-1/mpf(kr)) - mpf(kr)/(kr-1)*(1+msqrt(3*pi*(r-1)/2))
print("r=171: k_r=",kr," eb=",eb," Pc=",Pc)
r=170; kr=ceil(r**1.5+8*r); rho=mpf(kr)/(kr+r); eb = tm(r,rho)
Pc = kr*(1/(2*mpf(r))-1/(3*mpf(r)**2)) - mpf(5)/2 + 2*eb*(1-1/mpf(kr)) - mpf(kr)/(kr-1)*(1+msqrt(3*pi*(r-1)/2))
print("r=170: Pc=",Pc)

print("== kernel-bounds 유리함수 항등식 ==")
P = sp.symbols('Psi')
th = 2*P/(1-P)
Lth = 2*sum(P**(2*i+1)/(2*i+1) for i in range(4))
Uth = Lth + 2*P**9/(9*(1-P**2))
um = 1+th/2-th**2/24; up = 1+th/2-th**2/44
num_plus = th**2*sp.diff(up,P)/sp.diff(th,P) - (th-Lth)*up
num_minus = th**2*sp.diff(um,P)/sp.diff(th,P) - (th-Uth)*um
PT = 175-665*P+581*P**2-427*P**3+375*P**4-309*P**5+150*P**6+15*P**7
QT = 945+42*P-252*P**2+66*P**3-108*P**4+42*P**5-60*P**6-10*P**7
print("P identity:", sp.simplify(num_plus - 2*P**3*PT/(1155*(1-P)**3)))
print("Q identity:", sp.simplify(num_minus + P**4*QT/(945*(1-P)**3*(1+P))))
# positivity on [0,1/3] numeric
import numpy as np
xs = np.linspace(0,1/3,1000)
print("P min:", min(float(PT.subs(P,x)) for x in xs[::50]), " Q min:", min(float(QT.subs(P,x)) for x in xs[::50]))
# W_m bounds numeric
for m in [1,2,3,5,10,100]:
    W = (m+1)*exp(-1)*(1+1/m)**m - m
    print(m, 0.5-1/(24*m) <= W <= 0.5-1/(44*m), W, 0.5-1/(24*m), 0.5-1/(44*m))
# Ren/cb bounds
for m in [1,2,3,5,6,10]:
    Ren = m**m*exp(-m)/factorial(m); cb = comb(2*m,m)/4**m
    q = Ren/(cb/sqrt(2))
    print("m",m," Ren/(o cb)=",q, " <=1+1/(12(2m-1))?", q<=1+1/(12*(2*m-1)), " <=1+1/(22m)?", q<=1+1/(22*m), " >=1+1/(25(2m-1))?", q>=1+1/(25*(2*m-1)))
print("log et(1/2):", log(e*0.5*exp(-0.5/tan(0.5))/sin(0.5)))
print("e^(1/23)=", exp(1/23), " e^(2/23)+21/80 e^(1/23)=", exp(2/23)+21/80*exp(1/23), " o e^(1/23)=", exp(1/23)/sqrt(2))
print("21/(40 sqrt2)=",21/(40*sqrt(2))," 1/e=",1/e, " 147/396=",147/396," 720/1957=",720/1957)
print("2sqrt2/e=",2*sqrt(2)/e, " 181/174=",181/174)
print("rq* at S=23:", 13/20*(1+3/529)/23, " (1+3/169)/25=", (1+3/169)/25, " 1/12=",1/12)
print("10001^(-1/3)=",10001**(-1/3)," 0.0015*1.25^-12=",0.0015/1.25**12, " 31*0.0015=",31*0.0015)
print("1-cos1=",1-cos(1))
print("hb check d=3: coefficients", [(j+1)*4**(3-j-1)/factorial(3-j) for j in range(4)], " hb_3(1)=", 4**3/6)
