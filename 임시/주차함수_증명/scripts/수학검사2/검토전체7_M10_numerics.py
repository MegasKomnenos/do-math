# -*- coding: utf-8 -*-
"""M10 검토: 10장 상수·표값 재계산 (mpmath, 30자리). 보고용이며 본문을 고치지 않는다."""
from mpmath import mp, mpf, log, sqrt, exp, quad, pi, floor, ceil, factorial, findroot
mp.dps = 30


def g(x):
    return (x - 1) * log(1 + 1 / x)


def Bor(j):
    j = mpf(j)
    return exp(-j) * j ** (j - 1) / factorial(j)


def q_fun(r):
    return 1 + mpf('0.7501') * r / (1 + r)


print("== 10.5 명제 old-8-23 상수")
print("3*sqrt2*0.16696 =", 3 * sqrt(2) * mpf('0.16696'), " (text 0.70836)")
print("2.5-log2-log0.485917 =", mpf('2.5') - log(2) - log(mpf('0.485917')), " (text 2.528571)")
print("sqrt(sqrt2*0.16696) =", sqrt(sqrt(2) * mpf('0.16696')), " (text 0.4859188)")
k = mpf(6667)
print("A^crit factor at k=6667:", (1 + 1 / k) * (1 + 2 / k) / (1 - 3 / (4 * k)), " (<=1.00057)")
print("c_d coef: 1.00057^2(1+2/k)^2/6 =", mpf('1.00057') ** 2 * (1 + 2 / k) ** 2 / 6, " (<=0.16696)")
print("3*0.485917/2 =", 3 * mpf('0.485917') / 2, " (text 0.72888)")
print("2*0.8*2/7 =", 2 * mpf('0.8') * 2 / 7, " (text 0.457143)")
print("2^(7/2) =", 2 ** mpf(3.5), " (text 11.3137)")
for kk in [6667, 10000, 100000]:
    kk = mpf(kk)
    dn = 2 * kk ** (mpf(2) / 3)
    S = mpf(0)
    d = int(floor(dn)) + 1
    while d <= kk + 1:
        qd = 1 + mpf('0.7501') * (d - 1) / (kk - 1 + d)
        S += qd ** 2 * sqrt(kk - 1 + d)
        d += 1
    print(" k=%d: k*2*0.72888*S/k^{5/2} =" % int(kk), 2 * mpf('0.72888') * S / kk ** mpf(2.5) * kk, " (<=3.9)")
kk = mpf(6667)
print("sqrt2*0.70836*q(1+1/k)^3 =", sqrt(2) * mpf('0.70836') * q_fun(1 + 1 / kk) ** 3, " (<=2.6047)")
dn = 2 * kk ** (mpf(2) / 3)
rho0 = floor(dn) / kk
print("rho0(6667)=", rho0, " (<=0.10635); q(rho0)=", q_fun(rho0), " (<=1.0722)")
iota0 = mpf('2.528571') + log(2 ** mpf(1.5) * (1 - 1 / dn) ** mpf(1.5)) - log(mpf('1.0722'))
print("iota0 >=", iota0, " (text 3.4964)")
sig0 = exp(-mpf('3.4964') / mpf('1.5'))
print("sigma0=", sig0, " (text 0.0972)")
rr = rho0 * sig0
print("sqrt(1+rho)*q^3 at rho0*sigma0:", sqrt(1 + rr) * q_fun(rr) ** 3, " (<=1.0288)")
print("sign-lemma bracket:", (2 * mpf('3.4964') - 6 + 6 * sqrt(mpf('0.0972'))) - mpf('1.0288') * 6 * sqrt(mpf('0.0972')), " (text 0.938)")
print("far-region bracket at rho0 (k=6667):", mpf('2.528571') - log(q_fun(rho0)) + mpf(1.5) * log(rho0) + log(kk) / 2, " (>=3.246)")

print("== j1, j2 적분")
f2 = lambda s: 2 * sqrt(1 + s * s) * mpf('0.70836') * q_fun(s * s) ** 3
f1 = lambda s: 2 * sqrt(1 + s * s) * mpf('0.70836') * q_fun(s * s) ** 3 * (mpf('2.528571') - log(q_fun(s * s)) + 3 * log(s))
j2 = quad(f2, [0, mpf('1e-6'), mpf('0.01'), 1])
j1 = quad(f1, [0, mpf('1e-10'), mpf('1e-6'), mpf('0.01'), 1])
print("j2=", j2, " (text 2.7171998) ; j1=", j1, " (text 0.7998716)")


def DDLn(k):
    k = mpf(k)
    dn = 2 * k ** (mpf(2) / 3)
    eps = -log(1 - sqrt(k + 1) / (mpf('0.485917') * k))
    epsp = mpf('2.26') / k + mpf('0.47') / (dn - 1)
    gam = mpf('2.6047') * (mpf('2.53') + log(k) / 2 + eps + mpf(1.5) / k) / k
    t1 = mpf('0.457143') / sqrt(2 * pi) * q_fun(dn / k) * sqrt(1 + dn / k) * (dn + 1) ** mpf(3.5) / k ** 3
    t2 = 2 / sqrt(2 * pi) / sqrt(k) * (1 + epsp) * (j1 + (log(k) / 2 + eps) * j2 + gam)
    t3 = mpf('3.9') / sqrt(2 * pi) / k
    return t1 + t2 + t3


for kk in [6667, 6668, 8065, 9551, 9705, 9949]:
    print(" DDL^nat(%d)=" % kk, DDLn(kk))
print("decrease cond j1+j2(log6667/2-1)=", j1 + j2 * (log(mpf(6667)) / 2 - 1), " (text 10.04)")

print("== 10.3 표 / 가족 첫 열")
for kk in [6667, 8064, 8065, 9550, 9551, 9704, 9705, 9948, 9949]:
    kk = mpf(kk)
    print(" k=%d: 20001-2k=%s 0.48k=%s 2k^(2/3)=%s 1.3k^(2/3)=%s" % (int(kk), 20001 - 2 * kk, mpf('0.48') * kk, 2 * kk ** (mpf(2) / 3), mpf('1.3') * kk ** (mpf(2) / 3)))

print("== 10.4/10.6 상수")
print("0.48^-1/2-1+(1-sqrt.48)/3 =", mpf('0.48') ** mpf(-0.5) - 1 + (1 - sqrt(mpf('0.48'))) / 3, " (text 0.54577)")
print("132.32*0.54577 =", mpf('132.32') * mpf('0.54577'), " (text 72.217); 4*16.54*2=", 4 * mpf('16.54') * 2)
print("theta0 =", (2 * exp(-mpf('0.48')) - 1) * exp(-mpf('0.48')), " (text 0.1470)")
pt = exp(-1) / sqrt(2 * pi) * 2 ** mpf(1.5)
print("e^-1 (2pi)^-1/2 2^1.5 =", pt, " ; with Robbins e^{-1/(12k)-1/(12(nu-1))}, k=6667, nu-1=3200:", pt * exp(-1 / (12 * mpf(6667)) - 1 / (12 * mpf(3200))), " (>=0.41508)")
print("1/0.41508=", 1 / mpf('0.41508'), " (text 2.40918)")
print("c_R=(sqrt(2pi)/2)e^{1/12}=", sqrt(2 * pi) / 2 * exp(mpf(1) / 12), " ; f1=4/(3 sqrt(2pi))=", 4 / (3 * sqrt(2 * pi)))


def u_of(k):
    k = mpf(k)
    return 3 / mpf('0.35') * (mpf('1.35') + 1 / k) * (mpf('0.65') - 1 / k) ** mpf(-1.5) / sqrt(k)


def BdT(k, nu):
    k = mpf(k); nu = mpf(nu)
    return (k + nu) * u_of(k) * (1 / (k - 1) + 1 / k) + 3 * (k + 1) * (k - 1) ** mpf(-1.5)


def sup(d, y):
    d = mpf(d); y = mpf(y)
    return min(mpf(1), mpf('1.15') * (y + d) / d ** mpf(1.5))


def ec(k, nu):
    k = mpf(k); nu = mpf(nu)
    return 3 * nu ** 2 / ((k - 1) * k) + mpf('4.8') * sqrt(nu) / k + nu ** 2 / (2 * (k - 1) ** 2)


def ebar(k):
    k = mpf(k)
    xi = (sqrt(5 * k * log(k)) + 2) / k
    return exp(3 / (2 * k)) * (exp(sqrt(5 * log(k) / k) + 1 / k) + mpf('2.40918') * k ** (mpf(1.5) - mpf(2.5) / (1 + xi)))


k0 = 6668
abar = 3 * mpf('1.15') * (mpf('1.48') * k0 + 2) / (mpf('0.48') * k0 + 1) ** mpf(1.5)
bbar = 2 * u_of(k0) * (2 * k0 - 1) / (k0 - 1) + 3 * (k0 + 1) * (k0 - 1) ** mpf(-1.5)
dbar = mpf('72.217') / sqrt(k0)
print("bulk k0=6668: abar=", abar, " bbar=", bbar, " dbar=", dbar, " ebar=", ebar(k0), " oF=", 4 - ebar(k0), " Stays^up_F=", abar + bbar + DDLn(k0) + dbar, " LHS(<=4):", abar + bbar + DDLn(k0) + dbar + ebar(k0))
kk = mpf(8065)
print("fam2: 3s^up=", 3 * sup(2 * kk ** (mpf(2) / 3) + 1, kk + 1), " BdT=", BdT(kk, mpf('0.48') * kk), " DDL=", DDLn(kk), " oF=", 4 - 3 * sup(2 * kk ** (mpf(2) / 3) + 1, kk + 1) + (2 * exp(-mpf('0.48')) - 1) * exp(-mpf('0.48')) - BdT(kk, mpf('0.48') * kk) - DDLn(kk))
kk = mpf(9551); xi2 = 2 * kk ** (mpf(2) / 3) / (kk - 1)
print("fam1b: 3s^up=", 3 * sup(mpf('1.3') * kk ** (mpf(2) / 3) + 1, kk + 1), " theta=", (2 * exp(-xi2) - 1) * exp(-xi2), " BdT=", BdT(kk, 2 * kk ** (mpf(2) / 3)), " DDL=", DDLn(kk), " oF=", 4 - 3 * sup(mpf('1.3') * kk ** (mpf(2) / 3) + 1, kk + 1) + (2 * exp(-xi2) - 1) * exp(-xi2) - BdT(kk, 2 * kk ** (mpf(2) / 3)) - DDLn(kk))
kk = mpf(9705)
print("fam1a: ec=", ec(kk, mpf('1.3') * kk ** (mpf(2) / 3)), " BdT=", BdT(kk, mpf('1.3') * kk ** (mpf(2) / 3)), " DDL=", DDLn(kk), " oF=", 2 - ec(kk, mpf('1.3') * kk ** (mpf(2) / 3)) - BdT(kk, mpf('1.3') * kk ** (mpf(2) / 3)) - DDLn(kk))
for kk in [6668, 8065, 9551, 9705]:
    kk = mpf(kk)
    print(" eps0(%d)=" % int(kk), floor(2 ** (mpf(2) / 3) * (kk + 1) ** (mpf(2) / 3)))
print("u(3131)=", u_of(3131), " (<0.3951); m_hit(6667)=", ceil(sqrt(5 * 6667 * log(mpf(6667)))), " 0.09k=", mpf('0.09') * 6667)

print("== 정리 old-8-25 상수")
print("2/sqrt(pi)=", 2 / sqrt(pi))
c = 2 / sqrt(2 * pi)
for ups, q in [(mpf('0.9'), 113), (mpf('0.99'), 113), (mpf('0.9999'), 113)]:
    E = c * (mpf(1) / 4 * (1 - 1 / (2 * mpf(q))) ** mpf(-1.5) + (1 + ups + ups ** 2) * (1 - ups) ** mpf(-0.5) * (1 + ups) ** mpf(-1.5))
    print(" ups=", ups, " E*q coef=", E)
print("F at ups<=0.99: c*3*sqrt(1-0.81)=", c * 3 * sqrt(1 - mpf('0.81')), "; F at ups=0.9999:", c * (1 + 2 * mpf('0.9999') ** 2) * sqrt(1 - mpf('0.9999') ** 2))
print("(1.15*6666)^(2/3)=", (mpf('1.15') * 6666) ** (mpf(2) / 3), " (1.15*1000)^(2/3)=", (mpf('1.15') * 1000) ** (mpf(2) / 3))
print("1.6*0.8/sqrt50=", mpf('1.6') * mpf('0.8') / sqrt(50), " ; c*sqrt(50/0.77)=", c * sqrt(50 / mpf('0.77')))
print("theta1 root of (1-t)^2.5-1+2t:", findroot(lambda t: (1 - t) ** mpf(2.5) - 1 + 2 * t, 0.28))
print("v(0.02)/0.02 =", ((1 - mpf('0.02')) ** mpf(-1.5) - 1) / mpf('0.02'), " (<=1.6)")
print("1.1284+2.82/389=", mpf('1.1284') + mpf('2.82') / 389, " 1.044+9.3/389=", mpf('1.044') + mpf('9.3') / 389, " 0.34+85/389=", mpf('0.34') + mpf(85) / 389)
print("1.1284+2.82/113=", mpf('1.1284') + mpf('2.82') / 113, " 1.044+9.3/113=", mpf('1.044') + mpf('9.3') / 113, " 0.34+85/113=", mpf('0.34') + mpf(85) / 113)

print("== 10.6 보조정리 old-8-32(iii) 상수")
cR = sqrt(2 * pi) / 2 * exp(mpf(1) / 12)
print("beta0 min=", cR * mpf('1.04') ** mpf(1.5) / sqrt(2), " g^e(1.0216)=", exp(-mpf('1.0216')) * (1 + 1.5 * mpf('1.0216')), " iota*q0 max=", cR * 2 ** (mpf(2) / 3) / mpf(6669) ** (mpf(1) / 3))
print("beta2 range:", cR * mpf('1.04') ** mpf(1.5), cR * 2, " sqrt(1/2+1/562)=", sqrt(mpf(0.5) + mpf(1) / 562))
ge_p = lambda t: exp(-t) * (1.5 * t - 0.5)
print("|ge'| at 1.02, 2.73:", ge_p(mpf('1.02')), ge_p(mpf('2.73')))
print("0.234*0.2916*1.444=", mpf('0.234') * mpf('0.2916') * mpf('1.444'), " e^-1/564=", exp(-1) / 564)

print("== 명제 old-8-33 상수")
cAb = lambda r: 2 * sqrt(r) / (1 - r) + 2 * log((1 + sqrt(r)) / (1 - sqrt(r)))
print("2cAb(0.6)-4/sqrt(0.6)=", 2 * cAb(mpf('0.6')) - 4 / sqrt(mpf('0.6')), " (text 10.836); Sub max=", 2 * sqrt(mpf('0.6')) / mpf('0.4'), " (text 3.873)")
print("== row-3k: 2*0.7654-1.3502=", 2 * mpf('0.7654') - mpf('1.3502'))
print("== 상쇄 보조정리: c*(1-1/206)^-1/2=", c * (1 - mpf(1) / 206) ** mpf(-0.5), " (<=0.7999)")
print("== 10.5 remark: inc^- - inc^+ <= inc^+ ? (small y0)")
for y0, q, d in [(2, 1, 2), (2, 1, 3), (2, 2, 3), (3, 1, 4), (5, 1, 6), (10, 1, 11)]:
    y0 = mpf(y0)
    incm = g(y0 - 1 + d) - g(y0 - 1 + q)
    incp = g(y0 + d) - g(y0 + q)
    print("  y0,q,d=", int(y0), q, d, " diff=", incm - incp, " inc+=", incp, " ok" if incm - incp <= incp else " VIOLATION")
print("== 10.4 (5): e^{0.48}=", exp(mpf('0.48')), " ; 0.48*6667=", mpf('0.48') * 6667, " 1.5(2*6667+3)^(2/3)=", mpf(1.5) * (2 * mpf(6667) + 3) ** (mpf(2) / 3))
print("== 10.6 reduction-ga (i): worst i=20000,k=6667: 0.99+0.59963*(20001)^(2/3)+1.24847*20001^(1/3)=", mpf('0.99') + mpf('0.59963') * mpf(20001) ** (mpf(2) / 3) + mpf('1.24847') * mpf(20001) ** (mpf(1) / 3), " vs (2k)^(2/3)=", mpf(13334) ** (mpf(2) / 3))
