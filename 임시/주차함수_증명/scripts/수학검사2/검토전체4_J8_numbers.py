# J8 검토: 장8 8.2절의 수치 상수 재계산 (mpmath 50자리)
from mpmath import mp, mpf, sqrt, exp, log, pi, zeta
mp.dps = 50

z12 = zeta(mpf('0.5')); zm12 = zeta(mpf('-0.5')); z32 = zeta(mpf('1.5'))
c = 1/sqrt(2*pi)
cPsi = -z12 + z32/12
print("z_{1/2}, z_{-1/2}, z_{3/2}:", z12, zm12, z32)
print("c_Psi =", cPsi)

k0 = mpf(6600)
k23 = k0**(mpf(2)/3); k13 = k0**(mpf(1)/3)
qmin = mpf('0.2')*k23; pmin = qmin-1
mu = 1/qmin
eps0 = 1/k13
print("6600^(2/3) =", k23, " q_min =", qmin, " p_min =", pmin, " sqrt(p_min) =", sqrt(pmin))
print("mu<=", mu, " xi*eps<=", mpf('6.001')*eps0, " eps0 =", eps0, " k^-2/3 =", 1/k23)
print("(1-mu)^-1/2 =", (1-mu)**(-mpf(1)/2), " (1-mu)^-3/2 =", (1-mu)**(-mpf(3)/2))

# pieces-k-monotone R_2
print("R2: (1+1/(4p_min))/(1-mu) =", (1+1/(4*pmin))/(1-mu), "  7/2*k/(k+1) =", mpf(7)/2*k0/(k0+1))
print("R2 sum:", mpf('2.5')+(1+1/(4*pmin))/(1-mu)-mpf(7)/2*k0/(k0+1)-mpf(2)/3)
# D_3
print("D3: 1-cPsi/(2 sqrt p_min) =", 1-cPsi/(2*sqrt(pmin)), " cPsi<1.678059?", cPsi<mpf('1.678059'))
print("D3 sum:", mpf('6.001')*eps0/3 + 1/(3*(1-mu)*(1-cPsi/(2*sqrt(pmin)))) - mpf(2)/3)
# E condition
print("E: eps(1+xi eps) at xi=6.001:", eps0*(1+mpf('6.001')*eps0), " 6xi^2 at 0.2:", 6*mpf('0.04'))

# escape-y-monotone (나)
xi = mpf('0.2')
print("(나) min D1-D3 >=", xi - 1/k23 - 3*c*sqrt(xi)*eps0)
# (라)
th1 = (mpf(3)/2*sqrt(xi) - mpf(1)/2/sqrt(xi)/k23)/(2*c)
th3 = mpf(3)/4*eps0*(1+(1-1/(xi*k23))**(-mpf(1)/2))
ups = (k0+1)/(2*k0)*(1-1/(xi*k23))**(-mpf(3)/2)/(xi**2*k23)
print("(라) th1', th3' bound, ups' :", th1, th3, ups, " U' >=", th1-th3-ups)
# (마)
t1 = (1+xi*eps0)/(12*xi**2*k13); t2 = 3/(8*sqrt(xi)*k13)
print("(마) terms:", t1, t2, t1+t2, " k^1/3 V' <=", -mpf(1)/2+t1+t2)

# jensen-H-ii
print("Lambda'(1) =", mpf('2.75')+z12, "  bracket at p=1:", -mpf(1)/6-mpf(2)/3*z12+zm12)

# table-lower-bound (가)
def s_fun(q): return mpf(4)/15*q**(mpf(5)/2)+mpf('0.385')*q**(mpf(3)/2)
def Cr(q,k): return mpf(3)/2*c*(k+q)**(mpf(3)/2)/(k+1)**(mpf(7)/2)*s_fun(q)
def jinf(x): return mpf(4)/3*c*x**(mpf(3)/2)
print("j_inf(0.2) =", jinf(xi), " Cr(q_min,6600) =", Cr(qmin,k0))
print("exp(-0.0477345) =", exp(-mpf('0.0477345')))
E02 = 2*c/sqrt(xi)*(1+xi*eps0)
print("E(0.2,6600) upper =", E02, " denom =", mpf('0.168623')+2*c/sqrt(xi), " ratio =", E02/(mpf('0.168623')+2*c/sqrt(xi)))

# envelope-code-monotone (나)
print("2c sqrt(0.0005)*0.0005 =", 2*c*sqrt(mpf('0.0005'))*mpf('0.0005'))
Ks = (2/mpf('0.0055'))**(mpf(3)/2)
print("K_s(0.0055) =", Ks, " s(2) =", s_fun(2), " Cr(2,K_s) =", Cr(2,Ks))
print("Cr(2e4, 6.6e9) =", Cr(mpf(2e4), mpf('6.6e9')))
print("2/6600^(2/3) =", 2/k23)

# closed-form (가)
print("phi>=", exp(-1/(12*qmin)), " rho1<=", mpf(3)/2*mpf('6.001')*eps0)
xi6 = mpf('6.001')
rho2 = mpf(5)/8*(1+3/(4*pmin))*(1+xi6*eps0)**(mpf(5)/2)*xi6**2/k23
print("rho2<=", rho2, " V>=", exp(-1/(12*qmin))-mpf(3)/2*xi6*eps0-rho2)
U1 = xi6**(mpf(3)/2)/(2*c); U2 = (k0+1)/k0*(1-mu)**(-mpf(1)/2)
print("theta1<=", U1, " ups<=", U2, " U<=", U1+U2, " q>=", (exp(-1/(12*qmin))-mpf(3)/2*xi6*eps0-rho2)/(U1+U2))

# closed-form (나)
def brk(x,k): return (mpf('0.4')*x**(mpf(3)/2)+mpf('0.5775')*sqrt(x)*k**(-mpf(2)/3))*(1+x*k**(-mpf(1)/3))**(mpf(3)/2)
print("(나) xi<=0.1:", -z12 - (-zm12)/2 - mpf(1)/24 - brk(mpf('0.1'),k0))
q01 = mpf('0.1')*k23
print("(나) 0.1..2.1: q>=", q01, " terms:", (-zm12)/q01, (q01-1)**(-mpf(3)/2)/(12*q01), brk(mpf('2.1'),k0),
      " total:", -z12-(-zm12)/q01-(q01-1)**(-mpf(3)/2)/(12*q01)-brk(mpf('2.1'),k0))

# closed-form (다)
q2 = 2*k23; p2 = q2-1; mu2 = 1/q2
print("(다) q>=", q2, " bracket:", sqrt(1-mu2)-(1+p2**(-mpf(1)/2))*eps0/sqrt(2), " half:", (sqrt(1-mu2)-(1+p2**(-mpf(1)/2))*eps0/sqrt(2))/2)
print("(다) dtheta1 coeff:", eps0/sqrt(2)/(3*c), " dtheta3 coeff:", (1+1/(4*p2))/2)
print("(다) V<1 bracket:", mpf(1)/2-mpf(3)/2*mu2-mpf(3)/4*eps0/sqrt(2))
xi2 = mpf(2)
print("(다) U lower at xi=2:", (xi2**(mpf(3)/2)-sqrt(xi2)/k23)/(2*c)+1-mpf(3)/2*xi2*eps0)
print("(다) final:", mpf('0.146751')-mpf('0.5316752')/mpf('4.37993'))

# six pieces and q_{6600,6600}
def PsiLow(r):
    if r < 1: return mpf(0)
    return c*(2*sqrt(r)-cPsi+1/(2*sqrt(r))-r**(-mpf(3)/2)/24)
def pieces(x,k):
    q = x*k**(mpf(2)/3); p = q-1; n = k+q; kk = k+1; e = k**(-mpf(1)/3)
    E = 2*c*exp(-1/(12*q))/sqrt(x)*(1+x*e)
    R1 = mpf(3)/2*c*(2*sqrt(p)-1)/k**(mpf(2)/3)
    H = mpf(2)/3*p**(mpf(3)/2)+p**(mpf(1)/2)/2+zm12+p**(-mpf(1)/2)/24
    R2 = mpf(15)/8*c*n**(mpf(5)/2)*H/(kk**(mpf(7)/2)*k**(mpf(2)/3))
    D1 = p/k**(mpf(2)/3)
    D2 = kk*sqrt(2/pi)/sqrt(p)/k**(mpf(2)/3)
    D3 = mpf(3)/2*kk*PsiLow(p)/((n+1)*k**(mpf(2)/3))
    return E,R1,R2,D1,D2,D3
def qkk(x,k):
    E,R1,R2,D1,D2,D3 = pieces(x,k)
    return (E-R1-R2)/(D1+D2-D3)
for x in [mpf(2), mpf('2.1'), mpf('0.2'), mpf('6.001')]:
    print("q_6600,6600(%s) ="%x, qkk(x,k0), " e^{-j_inf} =", exp(-jinf(x)))
E,R1,R2,D1,D2,D3 = pieces(mpf('0.2'),k0)
print("pieces at 0.2:", E,R1,R2,D1,D2,D3, " D1-D3 =", D1-D3)

# table-tolerance
print("r_G: 0.38951*0.7202/19.4319^2 =", mpf('0.38951')*mpf('0.7202')/mpf('19.4319')**2)
print("0.85 c k/(k+1) =", mpf('0.85')*c*k0/(k0+1), " half:", mpf('0.85')*c*k0/(k0+1)/2)
print("Lambda'(1)-0.85 sqrt2 =", mpf('2.75')+z12-mpf('0.85')*sqrt(2))
print("coef1:", mpf('0.020044')*mpf('0.169524')*sqrt(mpf('0.2')), " coef2:", mpf('0.953386')*mpf('0.169524')*sqrt(mpf('0.000499')))
print("r_G*0.0004999 =", mpf('7.429e-4')*mpf('0.0004999'))
# remark
print("(4c)^(2/3) =", (4*c)**(mpf(2)/3))
# partition length
print("L-1 = ceil(log(1e6)/log(1.02)) =", log(mpf(1e6))/log(mpf('1.02')))
