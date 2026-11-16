# 검토전체8 N10: 10장 상수·표 값의 독립 재계산 (mpmath, 30자리 부동소수; 구간 산술 아님)
from mpmath import mp, mpf, sqrt, log, exp, pi, quad, floor, ceil
mp.dps = 30
def P(*a): print(*a)
two3 = mpf(2)/3

# --- 10.3 표: 경계 열 ---
for k in (8064, 8065, 9948, 9949, 6667):
    P("k", k, "20001-2k", 20001-2*k, "0.48k", mpf('0.48')*k, "3k", 3*k)

# --- 10.6 가족 첫 열 ---
def first_k(phi):
    k = 6668
    while 20001-2*k > phi*mpf(k)**two3: k += 1
    return k
P("1a k0", first_k(mpf('1.3')), "1b k0", first_k(mpf(2)))
k = 6668
while 20001-2*k > mpf('0.48')*k: k += 1
P("fam2 k0", k)
for k0 in (6668, 8065, 9551, 9705):
    P("eps0", k0, int(floor(mpf(2)**two3*(k0+1)**two3)))

# --- 상수 ---
P("theta0", (2*exp(-mpf('0.48'))-1)*exp(-mpf('0.48')))
cR = sqrt(2*pi)/2*exp(mpf(1)/12); P("cR", cR)
f1 = mpf(4)/(3*sqrt(2*pi)); P("f1", f1)
P("2/sqrt(pi)", 2/sqrt(pi))
ge = lambda t: exp(-t)*(1+mpf('1.5')*t)
P("beta0 min", cR*mpf('1.04')**mpf('1.5')/sqrt(2), "ge(1.0216)", ge(mpf('1.0216')))
P("iota q0 max", cR*mpf(2)**two3*mpf(6669)**(-mpf(1)/3))
P("beta2 range", cR*mpf('1.04')**mpf('1.5'), cR*2)
P("sqrt(1/2+1/562)", sqrt(mpf(1)/2+mpf(1)/562))
gp = lambda t: exp(-t)*(mpf('1.5')*t-mpf('0.5'))
P("ge-prime abs at 1.02, 2.73", gp(mpf('1.02')), gp(mpf('2.73')))
P("0.234*0.2916*1.444", mpf('0.234')*mpf('0.2916')*mpf('1.444'), "e^-1/564", exp(-1)/564)
c0 = (2*pi)**(-mpf(1)/2)*exp(-1)*2**mpf('1.5')
P("pi_two const", c0, "with robbins k=6667 nu=3201", c0*exp(-mpf(1)/(12*6667)-mpf(1)/(12*3201)))
P("1/0.41508", 1/mpf('0.41508'))
P("3sqrt2*0.16696", 3*sqrt(2)*mpf('0.16696'), "2.5-log2-log0.485917", mpf('2.5')-log(2)-log(mpf('0.485917')))
P("(sqrt2*0.16696)^(1/2)", sqrt(sqrt(2)*mpf('0.16696')), "0.485917^2 vs sqrt2*0.16696", mpf('0.485917')**2, sqrt(2)*mpf('0.16696'))
k = mpf(6667)
P("1.00057 check", (1+1/k)*(1+2/k)/(1-mpf(3)/(4*k)))
P("0.7501 check", (mpf(9)/4)*(1+exp(mpf(3)/(2*k)))/2/3)
P("0.16696 check", mpf('1.00057')**2*(1+2/k)**2/6)
q1 = 1+mpf('0.7501')*(1+1/k)/(2+1/k); P("2.6047 check", sqrt(2)*mpf('0.70836')*q1**3)
s = mpf(0); kk = 6667
for d in range(2, kk+2):
    qd = 1+mpf('0.7501')*(d-1)/(kk-1+d)
    s += mpf('0.72888')*qd**2*sqrt(kk-1+d)/mpf(kk)**mpf('2.5')
P("2*sum last term *k (<=3.9?)", 2*s*kk)
dnat = 2*k**two3; rho0 = floor(dnat)/k
P("rho0", rho0, "log(floor(dnat)^1.5/k)", log(floor(dnat)**mpf('1.5')/k), "q(rho0)", 1+mpf('0.7501')*rho0/(1+rho0))
iota0 = mpf('2.528571')-log(1+mpf('0.7501')*rho0/(1+rho0))+log(floor(dnat)**mpf('1.5')/k)
sig0 = exp(-iota0/mpf('1.5'))
P("iota0", iota0, "sigma0", sig0)
rr = rho0*sig0; P("d q^3 at rho0*sig0", sqrt(1+rr)*(1+mpf('0.7501')*rr/(1+rr))**3)
P("0.938 check", (2*iota0-6+6*sqrt(sig0))-mpf('1.0288')*6*sqrt(sig0))
qf = lambda r: 1+mpf('0.7501')*r/(1+r)
j2 = quad(lambda r: sqrt((1+r)/r)*mpf('0.70836')*qf(r)**3, [0, mpf('1e-6'), mpf('0.01'), 1])
j1 = quad(lambda r: sqrt((1+r)/r)*mpf('0.70836')*qf(r)**3*(mpf('2.528571')-log(qf(r))+mpf('1.5')*log(r)), [0, mpf('1e-8'), mpf('1e-6'), mpf('0.01'), 1])
P("j2", j2, "j1", j1)
def DDL(k):
    k = mpf(k); dn = 2*k**two3
    eps = -log(1-sqrt(k+1)/(mpf('0.485917')*k)); epsp = mpf('2.26')/k+mpf('0.47')/(dn-1)
    gam = mpf('2.6047')*(mpf('2.53')+log(k)/2+eps+mpf('1.5')/k)/k
    return (mpf('0.457143')*(2*pi)**(-mpf(1)/2)*qf(dn/k)*sqrt(1+dn/k)*(dn+1)**mpf('3.5')/k**3
            + 2*(2*pi)**(-mpf(1)/2)*k**(-mpf(1)/2)*(1+epsp)*(j1+(log(k)/2+eps)*j2+gam)+mpf('3.9')*(2*pi)**(-mpf(1)/2)/k)
for kk in (6667, 6668, 8065, 9551, 9705):
    P("DDL", kk, DDL(kk))
P("decrease cond k=6667", j1+j2*(log(mpf(6667))/2-1), "2^3.5", mpf(2)**mpf('3.5'))
cAb = lambda r: 2*sqrt(r)/(1-r)+2*log((1+sqrt(r))/(1-sqrt(r)))
P("2cAb(0.6)-4/sqrt0.6", 2*cAb(mpf('0.6'))-4/sqrt(mpf('0.6')))
P("Sub max", quad(lambda r: (1+r)*r**(-mpf(1)/2)*(1-r)**(-2), [0, mpf('0.6')]))
b = lambda x: x**(-mpf(1)/2)-1+(1-sqrt(x))/3
P("bracket at 0.48", b(mpf('0.48')), "132.32*", mpf('132.32')*b(mpf('0.48')))
def u(k): k = mpf(k); return mpf(3)/mpf('0.35')*(mpf('1.35')+1/k)*(mpf('0.65')-1/k)**(-mpf('1.5'))*k**(-mpf('0.5'))
def BdT(k, nu): k = mpf(k); return (k+nu)*u(k)*(1/(k-1)+1/k)+3*(k+1)*(k-1)**(-mpf('1.5'))
def sup(d, y, mS=mpf('1.15')): return min(mpf(1), mS*(y+d)/d**mpf('1.5'))
k = mpf(6668)
abar = 3*mpf('1.15')*(mpf('1.48')*k+2)/(mpf('0.48')*k+1)**mpf('1.5'); bbar = 2*u(k)*(2*k-1)/(k-1)+3*(k+1)*(k-1)**(-mpf('1.5')); dbar = mpf('72.217')/sqrt(k)
P("abar,bbar,dbar,DDL", abar, bbar, dbar, DDL(6668), "sum", abar+bbar+dbar+DDL(6668))
xi_p = (sqrt(5*k*log(k))+2)/k
ebar = exp(mpf(3)/(2*k))*(exp(sqrt(5*log(k)/k)+1/k)+mpf('2.40918')*k**(mpf('1.5')-mpf('2.5')/(1+xi_p)))
P("ebar", ebar, "oF bulk", 4-ebar, "mhit", ceil(sqrt(5*k*log(k))), "0.09k", mpf('0.09')*k)
k = mpf(8065); k23 = k**two3
P("fam2 pieces", 3*sup(2*k23+1, k+1), BdT(k, mpf('0.48')*k), DDL(8065), "oF", 4-3*sup(2*k23+1, k+1)+(2*exp(-mpf('0.48'))-1)*exp(-mpf('0.48'))-BdT(k, mpf('0.48')*k)-DDL(8065))
k = mpf(9551); k23 = k**two3; xs = 2*k23/(k-1)
P("1b pieces", 3*sup(mpf('1.3')*k23+1, k+1), (2*exp(-xs)-1)*exp(-xs), BdT(k, 2*k23), DDL(9551), "oF", 4-3*sup(mpf('1.3')*k23+1, k+1)+(2*exp(-xs)-1)*exp(-xs)-BdT(k, 2*k23)-DDL(9551))
k = mpf(9705); k23 = k**two3; nup = mpf('1.3')*k23
ec = 3*nup**2/((k-1)*k)+mpf('4.8')*sqrt(nup)/k+nup**2/(2*(k-1)**2)
P("1a pieces", ec, BdT(k, nup), DDL(9705), "oF", 2-ec-BdT(k, nup)-DDL(9705))
def StaysUp(k, nubar, mS=mpf('1.15')):
    k = mpf(k); tot = mpf(0)
    for y in (k-1, k):
        abar_ = (mS*(y+2*y**two3))**two3
        Flat = 2*(abar_-1)/(y+2-abar_)
        z = mpf('0.6')+1/y
        xiS = (nubar+4)/(k-1)
        if xiS >= mpf('0.6'): Sub = mpf(0)
        else: Sub = (k-1)/k*quad(lambda r: (r-xiS)*(1+r)*r**(-mpf('1.5'))*(1-r)**(-2), [xiS, mpf('0.6')])
        Ab = mS*(1+1/y)*(4*((mS*y)**two3-1)**(-mpf('0.5'))+y**(-mpf('0.5'))*(2*cAb(z)-4*z**(-mpf('0.5'))-Sub))
        tot += Flat+Ab
        P("  y", y, "Flat", Flat, "Ab", Ab, "Sub", Sub)
    Top = quad(lambda r: min(mpf(2), 2+(nubar+1)/k-r)*(1+r/3)*r**(-mpf('1.5')), [mpf('0.6')-mpf('2.6')/k, 1])
    P("  Top", Top, "2*16.54/sqrt(k)*Top", 2*mpf('16.54')/sqrt(k)*Top)
    return tot+2*mpf('16.54')*k**(-mpf('0.5'))*Top
P("StaysUp 1a", StaysUp(9705, mpf('1.3')*mpf(9705)**two3))
P("StaysUp 1b", StaysUp(9551, 2*mpf(9551)**two3))
P("StaysUp 2", StaysUp(8065, mpf('0.48')*8065))
k = mpf(6667)
P("0.48k vs 1.5(2k+3)^(2/3)", mpf('0.48')*k, mpf('1.5')*(2*k+3)**two3)
y = mpf(6666); P("0.6y-1 vs 1.5(2y+3)^(2/3)", mpf('0.6')*y-1, mpf('1.5')*(2*y+3)**two3)
P("q>= for y=6666: (1.15*6666)^(2/3)", (mpf('1.15')*6666)**two3, "(1200)^(2/3)", mpf(1200)**two3)
P("1.1284+2.82/389", mpf('1.1284')+mpf('2.82')/389, "1.044+9.3/389", mpf('1.044')+mpf('9.3')/389, "0.34+85/389", mpf('0.34')+85/mpf(389))
P("1.1284+2.82/113", mpf('1.1284')+mpf('2.82')/113, "1.044+9.3/113", mpf('1.044')+mpf('9.3')/113, "0.34+85/113", mpf('0.34')+85/mpf(113))
for up in (mpf('0.9'), mpf('0.99'), mpf('0.9999')):
    P("ups", up, "coef", 2*(2*pi)**(-mpf('0.5'))*(mpf(1)/4*(1-mpf(1)/226)**(-mpf('1.5'))+(1+up+up**2)*(1-up)**(-mpf('0.5'))*(1+up)**(-mpf('1.5'))), "F max crude", 2*(2*pi)**(-mpf('0.5'))*3*sqrt(1-up**2))
P("theta1 root", [(t, (1-t)**mpf('2.5')-1+2*t) for t in (mpf('0.28'), mpf('0.2802'), mpf('0.2805'))])
P("0.7999 check", 2*(2*pi)**(-mpf('0.5'))*(1-mpf(1)/206)**(-mpf('0.5')), "6.43 check", 2*(2*pi)**(-mpf('0.5'))*sqrt(50/mpf('0.77')), "1.28/sqrt50", mpf('1.28')/sqrt(50))
P("e^0.48", exp(mpf('0.48')), "(3(k+1))^(2/3) k=9705", (3*mpf(9706))**two3)
P("1.3*6669^(2/3)", mpf('1.3')*mpf(6669)**two3)
P("2*0.7654-1.3502", 2*mpf('0.7654')-mpf('1.3502'))
P("g(6667)", (k-1)*log(1+1/k), "1-3/(2k)", 1-mpf(3)/(2*k))
# 10.3 (가) 실제 내용: witness bound vs (2k)^{2/3}
for i in (20000, 13334):
    P("witness rhs", i, mpf('0.99')+mpf('0.59963')*(i+1)**two3+mpf('1.24847')*(i+1)**(mpf(1)/3), "(2k)^(2/3) k=6667", mpf(13334)**two3)
# 10.4 s^F useless threshold
P("(3(k+1))^(2/3) at k=6667", (3*mpf(6668))**two3)
