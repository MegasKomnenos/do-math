# -*- coding: utf-8 -*-
"""검토전체3 I10: 10장의 수치 재계산.
10.5 명제 M♮(DDL♮), 정리 S′ 오차 상수, 10.6 네 가족 검사(check-na, check-ga)의 값을 mpmath로 다시 센다.
"""
import mpmath as mp
mp.mp.dps = 30

def Bor(j):
    j = mp.mpf(j)
    return mp.e**(-j) * j**(j-1) / mp.factorial(j)

def logBor(j):
    j = mp.mpf(j)
    return -j + (j-1)*mp.log(j) - mp.loggamma(j+1)

sq2pi_inv = 1/mp.sqrt(2*mp.pi)
mS = mp.mpf('1.15')

# ---------- 10.5 명제 M♮ ----------
def qf(rho):
    return 1 + mp.mpf('0.7501')*rho/(1+rho)

def j2():
    f = lambda s: 2*mp.sqrt(1+s**2) * mp.mpf('0.70836') * qf(s**2)**3
    return mp.quad(f, [0, 0.01, 0.1, 1])

def j1():
    f = lambda s: 2*mp.sqrt(1+s**2) * mp.mpf('0.70836') * qf(s**2)**3 * (mp.mpf('2.528571') - mp.log(qf(s**2)) + 3*mp.log(s))
    return mp.quad(f, [0, 1e-8, 1e-4, 0.01, 0.1, 1])

J1, J2 = j1(), j2()

def DDLnat(k):
    k = mp.mpf(k)
    dn = 2*k**(mp.mpf(2)/3)
    eps = -mp.log(1 - mp.sqrt(k+1)/(mp.mpf('0.485917')*k))
    epsp = mp.mpf('2.26')/k + mp.mpf('0.47')/(dn-1)
    gam = mp.mpf('2.6047')*(mp.mpf('2.53') + mp.log(k)/2 + eps + mp.mpf('1.5')/k)/k
    t1 = mp.mpf('0.457143')*sq2pi_inv*qf(dn/k)*mp.sqrt(1+dn/k)*(dn+1)**mp.mpf('3.5')/k**3
    t2 = 2*sq2pi_inv*k**mp.mpf('-0.5')*(1+epsp)*(J1 + (mp.log(k)/2 + eps)*J2 + gam)
    t3 = mp.mpf('3.9')*sq2pi_inv/k
    return t1 + t2 + t3

print("j2 =", J2, " j1 =", J1)
for k in (6667, 6668, 8065, 9551, 9705):
    print("DDLnat(%d) = %s" % (k, mp.nstr(DDLnat(k), 10)))
print("decrease cond j1+j2(0.5 log 6667 -1) =", J1 + J2*(mp.log(6667)/2 - 1))

# 1단계 상수 점검
k = mp.mpf(6667)
print("Acrit factor (1+1/k)(1+2/k)/(1-3/(4k)) =", (1+1/k)*(1+2/k)/(1-3/(4*k)))
print("second cap coef 0.5*1.00114*(1+2/k)^2 =", mp.mpf('0.5')*mp.mpf('1.00114')*(1+2/k)**2, " vs 3*0.16696 =", 3*mp.mpf('0.16696'))
print("sqrt2*0.16696 =", mp.sqrt(2)*mp.mpf('0.16696'), " 0.485917^2 =", mp.mpf('0.485917')**2)
print("2.5-log2-log0.485917 =", mp.mpf('2.5')-mp.log(2)-mp.log(mp.mpf('0.485917')))
# 3단계 마지막 항: 2*0.72888*(2pi)^{-1/2} sum_d q_d^2 sqrt(k-1+d)/k^{5/2}  vs 3.9 (2pi)^{-1/2}/k
for kk in (6667, 10**4, 10**5):
    kk = mp.mpf(kk)
    dn = 2*kk**(mp.mpf(2)/3)
    s = mp.fsum((1+mp.mpf('0.7501')*(d-1)/(kk-1+d))**2*mp.sqrt(kk-1+d) for d in range(int(mp.floor(dn))+1, int(kk)+2))
    lhs = 2*mp.mpf('0.72888')*s/kk**mp.mpf('2.5')
    print("k=%s last-term sum coef %s vs 3.9/k=%s" % (kk, mp.nstr(lhs, 8), mp.nstr(mp.mpf('3.9')/kk, 8)))
# 5단계 상수
iota0 = mp.mpf('2.528571') + mp.mpf('1.5')*mp.log(2) + mp.mpf('1.5')*mp.log(1-1/mp.mpf(708)) - mp.log(qf(mp.mpf('0.10635')))
print("iota0 ~", iota0, " sigma0 =", mp.e**(-iota0/mp.mpf('1.5')))
sig0 = mp.e**(-iota0/mp.mpf('1.5'))
print("step5 bracket:", (2*iota0-6+6*mp.sqrt(sig0)) - mp.mpf('1.0288')*6*mp.sqrt(sig0))

# ---------- 정리 S′ 7단계 상수 ----------
def Ecoef(u, q):
    u = mp.mpf(u); q = mp.mpf(q)
    return 2*sq2pi_inv*(mp.mpf('0.25')*(1-1/(2*q))**mp.mpf('-1.5') + (1+u+u**2)*(1-u)**mp.mpf('-0.5')*(1+u)**mp.mpf('-1.5'))
for u in ('0.9', '0.99', '0.9999'):
    print("E coef at u=%s, q=113: %s" % (u, mp.nstr(Ecoef(u, 113), 6)))
print("F at u=0.9:", 2*sq2pi_inv*3*mp.sqrt(1-mp.mpf('0.81')), " F at 0.99:", 2*sq2pi_inv*3*mp.sqrt(1-mp.mpf('0.9801')))
print("0.34+85/113 =", mp.mpf('0.34')+mp.mpf(85)/113, " 1.044+9.3/113 =", mp.mpf('1.044')+mp.mpf('9.3')/113, " 1.1284+2.82/113 =", mp.mpf('1.1284')+mp.mpf('2.82')/113)
print("q lower bounds: (1.15*6666)^(2/3) =", (mS*6666)**(mp.mpf(2)/3), " (1.15*1000)^(2/3) =", (mS*1000)**(mp.mpf(2)/3))

# ---------- 10.6 명제 U 상수 ----------
cAb = lambda r: 2*mp.sqrt(r)/(1-r) + 2*mp.log((1+mp.sqrt(r))/(1-mp.sqrt(r)))
print("2cAb(0.6)-4/sqrt(0.6) =", 2*cAb(mp.mpf('0.6')) - 4/mp.sqrt(mp.mpf('0.6')))
print("int_0^0.6 (1+r) r^-1/2 (1-r)^-2 =", mp.quad(lambda r: (1+r)*r**mp.mpf('-0.5')*(1-r)**-2, [0, 0.6]))

# ---------- 10.6 가족 검사 (나) ----------
def u_of(k):
    k = mp.mpf(k)
    return 3/mp.mpf('0.35')*(mp.mpf('1.35')+1/k)*(mp.mpf('0.65')-1/k)**mp.mpf('-1.5')*k**mp.mpf('-0.5')

def BdT(k, nu):
    k = mp.mpf(k); nu = mp.mpf(nu)
    return (k+nu)*u_of(k)*(1/(k-1)+1/k) + 3*(k+1)*(k-1)**mp.mpf('-1.5')

def s_up(d, y):
    d = mp.mpf(d); y = mp.mpf(y)
    return min(mp.mpf(1), mS*(y+d)/d**mp.mpf('1.5'))

def ec(k, nup):
    k = mp.mpf(k); nup = mp.mpf(nup)
    return 3*nup**2/((k-1)*k) + mp.mpf('4.8')*mp.sqrt(nup)/k + nup**2/(2*(k-1)**2)

theta0 = (2*mp.e**mp.mpf('-0.48')-1)*mp.e**mp.mpf('-0.48')

def ebar(k):
    k = mp.mpf(k)
    xi = (mp.sqrt(5*k*mp.log(k))+2)/k
    return mp.e**(3/(2*k))*(mp.e**(mp.sqrt(5*mp.log(k)/k)+1/k) + mp.mpf('2.40918')*k**(mp.mpf('1.5')-mp.mpf('2.5')/(1+xi)))

def Flat(y):
    y = mp.mpf(y)
    ab = (mS*(y+2*y**(mp.mpf(2)/3)))**(mp.mpf(2)/3)
    return 2*(ab-1)/(y+2-ab)

def Sub(k, nubar):
    k = mp.mpf(k); xi = (mp.mpf(nubar)+4)/(k-1)
    if xi >= mp.mpf('0.6'):
        return mp.mpf(0)
    return (k-1)/k*mp.quad(lambda r: (r-xi)*(1+r)*r**mp.mpf('-1.5')*(1-r)**-2, [xi, mp.mpf('0.6')])

def Ab(y, k, nubar):
    y = mp.mpf(y); k = mp.mpf(k)
    z = mp.mpf('0.6') + 1/y
    return mS*(1+1/y)*(4*((mS*y)**(mp.mpf(2)/3)-1)**mp.mpf('-0.5') + y**mp.mpf('-0.5')*(2*cAb(z) - 4*z**mp.mpf('-0.5') - Sub(k, nubar)))

def Top(k, nubar):
    k = mp.mpf(k); nubar = mp.mpf(nubar)
    f = lambda r: min(mp.mpf(2), 2+(nubar+1)/k-r)*(1+r/3)*r**mp.mpf('-1.5')
    return mp.quad(f, [mp.mpf('0.6')-mp.mpf('2.6')/k, 1])

def Stays_up(k, nubar):
    k = mp.mpf(k)
    return mp.fsum(Flat(y)+Ab(y, k, nubar) for y in (k-1, k)) + 2*mp.mpf('16.54')*k**mp.mpf('-0.5')*Top(k, nubar)

def abar(k):
    k = mp.mpf(k); return 3*mS*(mp.mpf('1.48')*k+2)/(mp.mpf('0.48')*k+1)**mp.mpf('1.5')
def bbar(k):
    k = mp.mpf(k); return 2*u_of(k)*(2*k-1)/(k-1) + 3*(k+1)*(k-1)**mp.mpf('-1.5')
def dbar(k):
    return mp.mpf('72.217')/mp.sqrt(k)

fam = {}
k0 = 6668; D = DDLnat(k0)
oF = 4 - ebar(k0); up = abar(k0)+bbar(k0)+D+dbar(k0)
print("\n[bulk k0=6668] oF=%s  abar=%s bbar=%s DDL=%s dbar=%s ebar=%s up=%s margin=%s  sum<=4: %s" % tuple(mp.nstr(x, 7) for x in (oF, abar(k0), bbar(k0), D, dbar(k0), ebar(k0), up, oF-up, up+ebar(k0))))
fam['bulk'] = dict(k0=k0, Rsharp=up, Rsharp2=None, xicap=2**(mp.mpf(2)/3))
k0 = 8065; D = DDLnat(k0); kk = mp.mpf(k0)
oF = 4 - 3*s_up(2*kk**(mp.mpf(2)/3)+1, kk+1) + theta0 - BdT(kk, mp.mpf('0.48')*kk) - D
up = Stays_up(kk, mp.mpf('0.48')*kk)
print("[fam2 k0=8065] 3sup=%s theta0=%s BdT=%s DDL=%s oF=%s Stays_up=%s margin=%s" % tuple(mp.nstr(x, 7) for x in (3*s_up(2*kk**(mp.mpf(2)/3)+1, kk+1), theta0, BdT(kk, mp.mpf('0.48')*kk), D, oF, up, oF-up)))
fam['2'] = dict(k0=k0, Rsharp=3*s_up(2*kk**(mp.mpf(2)/3)+1, kk+1)+BdT(kk, mp.mpf('0.48')*kk)+D+up, Rsharp2=None, xicap=2**(mp.mpf(2)/3))
k0 = 9551; D = DDLnat(k0); kk = mp.mpf(k0)
xs = 2*kk**(mp.mpf(2)/3)/(kk-1)
oF = 4 - 3*s_up(mp.mpf('1.3')*kk**(mp.mpf(2)/3)+1, kk+1) + (2*mp.e**(-xs)-1)*mp.e**(-xs) - BdT(kk, 2*kk**(mp.mpf(2)/3)) - D
up = Stays_up(kk, 2*kk**(mp.mpf(2)/3))
print("[fam1b k0=9551] 3sup=%s theta=%s BdT=%s DDL=%s oF=%s Stays_up=%s margin=%s" % tuple(mp.nstr(x, 7) for x in (3*s_up(mp.mpf('1.3')*kk**(mp.mpf(2)/3)+1, kk+1), (2*mp.e**(-xs)-1)*mp.e**(-xs), BdT(kk, 2*kk**(mp.mpf(2)/3)), D, oF, up, oF-up)))
fam['1b'] = dict(k0=k0, Rsharp=3*s_up(mp.mpf('1.3')*kk**(mp.mpf(2)/3)+1, kk+1)+BdT(kk, 2*kk**(mp.mpf(2)/3))+D+up, Rsharp2=BdT(kk, 2*kk**(mp.mpf(2)/3))+D+up, xicap=2**(mp.mpf(2)/3))
k0 = 9705; D = DDLnat(k0); kk = mp.mpf(k0)
oF = 2 - ec(kk, mp.mpf('1.3')*kk**(mp.mpf(2)/3)) - BdT(kk, mp.mpf('1.3')*kk**(mp.mpf(2)/3)) - D
up = Stays_up(kk, mp.mpf('1.3')*kk**(mp.mpf(2)/3))
print("[fam1a k0=9705] ec=%s BdT=%s DDL=%s oF=%s Stays_up=%s margin=%s  (Flat=%s Ab=%s Top-part=%s)" % tuple(mp.nstr(x, 7) for x in (ec(kk, mp.mpf('1.3')*kk**(mp.mpf(2)/3)), BdT(kk, mp.mpf('1.3')*kk**(mp.mpf(2)/3)), D, oF, up, oF-up, Flat(kk), Ab(kk, kk, mp.mpf('1.3')*kk**(mp.mpf(2)/3)), 2*mp.mpf('16.54')*kk**mp.mpf('-0.5')*Top(kk, mp.mpf('1.3')*kk**(mp.mpf(2)/3)))))
fam['1a'] = dict(k0=k0, Rsharp=3+BdT(kk, mp.mpf('1.3')*kk**(mp.mpf(2)/3))+D+up, Rsharp2=BdT(kk, mp.mpf('1.3')*kk**(mp.mpf(2)/3))+D+up, xicap=mp.mpf('1.3'))

# ---------- 10.6 가족 검사 (가) ----------
def chain_s(y, qmax):
    """𝔰_q(y) for q=1..qmax via first-step recursion; float-ish mpf with dps 30."""
    y = int(y)
    lB = [None] + [logBor(j) for j in range(1, qmax+1)]
    lBy = {q: logBor(y+q) for q in range(1, qmax+1)}
    s = [None, mp.mpf(1)]
    for q in range(2, qmax+1):
        tot = mp.mpf(0); acc = mp.mpf(0)
        for qp in range(1, q):
            P = mp.e**(lB[q-qp] + lBy[qp] - lBy[q])
            tot += P
            acc += P*mp.mpf(y)/(y+qp)*s[qp]
        s.append((1-tot) + acc)
    return s

def Ren_star(j):
    j = mp.mpf(j); return sq2pi_inv*j**mp.mpf('-0.5')*mp.e**(-1/(12*j))

def Aup(q0, q):
    q0 = mp.mpf(q0); q = mp.mpf(q)
    return mp.sqrt(2*mp.pi)/4*mp.e**(1/(12*(q0-q)))*(q0+q)*mp.sqrt(q0-q)

def e_low_R(k0, q0, sy):
    y = mp.mpf(k0+1); k = mp.mpf(k0)
    zR = mp.fsum(Ren_star(q0-q)*mp.e**(-(q+Aup(q0, q))/y)*sy[q] for q in range(1, q0))
    PrB = 1 - mp.fsum(Bor(j) for j in range(1, q0))
    return k/(k+1)*(1-mp.mpf(q0)/(2*k))*(max(zR, sy[q0]-PrB) + Bor(q0))

f1 = 4/(3*mp.sqrt(2*mp.pi))
cR = mp.sqrt(2*mp.pi)/2*mp.e**(mp.mpf(1)/12)

def s_low(d, y):
    d = mp.mpf(d); y = mp.mpf(y)
    return mp.e**(-f1*((y+d-1)/y)**mp.mpf('1.5')*d**mp.mpf('1.5')/y)

def Qfun(y, xi):
    y = mp.mpf(y); xi = mp.mpf(xi); k = y-1
    q0 = xi*y**(mp.mpf(2)/3)
    pref = k/(k+1)*(1-q0/(2*k))*2*sq2pi_inv*mp.e**(-mp.mpf(1)/12)*y/(cR*q0)
    A = mp.e**(-q0/y)*s_low(q0, y)*(mp.e**(-cR*q0/y) - mp.e**(-cR*q0*mp.sqrt(q0/2)/y))
    B = mp.e**(-q0/(2*y))*s_low(q0/2, y)*(mp.e**(-cR*q0*mp.sqrt(q0/2+1)/y) - mp.e**(-cR*q0**mp.mpf('1.5')/y))
    return pref*(A+B)

for name in ('bulk', '2', '1b', '1a'):
    F = fam[name]; k0 = F['k0']
    eps0 = int(mp.floor(2**(mp.mpf(2)/3)*(k0+1)**(mp.mpf(2)/3)))
    sy = chain_s(k0+1, eps0+1)   # 𝔰_q(k0+1)
    sk = chain_s(k0, eps0+2)     # 𝔰_q(k0)
    best = None; bestq = None; best2 = None; best2q = None
    for q0 in range(2, eps0+1):
        eR = e_low_R(k0, q0, sy)
        val = 4*sk[q0+1] + 2*eR - F['Rsharp']
        if best is None or val < best:
            best, bestq = val, q0
        if F['Rsharp2'] is not None and q0 >= 104:
            v2 = eR + sk[q0+1] - F['Rsharp2']
            if best2 is None or v2 < best2:
                best2, best2q = v2, q0
    xc = F['xicap']
    edge = 4*s_low(xc*(k0+1)**(mp.mpf(2)/3)+1, k0) + 2*Qfun(k0+1, xc) - F['Rsharp']
    line = "[fam %s] eps0=%d Rsharp=%s  (a) min=%s at q0=%d  (b) edge=%s" % (name, eps0, mp.nstr(F['Rsharp'], 7), mp.nstr(best, 7), bestq, mp.nstr(edge, 7))
    if F['Rsharp2'] is not None:
        x2 = 2**(mp.mpf(2)/3)
        edge2 = Qfun(k0+1, x2) + s_low(x2*(k0+1)**(mp.mpf(2)/3)+1, k0) - F['Rsharp2']
        line += "  Rsharp2=%s (a,m0>N) min=%s at q0=%d (b,m0>N) edge=%s" % (mp.nstr(F['Rsharp2'], 7), mp.nstr(best2, 7), best2q, mp.nstr(edge2, 7))
    print(line)
