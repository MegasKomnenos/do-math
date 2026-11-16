# H8: 닫힌 꼴 정리·끼움 정리·허용 오차 보조정리의 수치 재계산
from mpmath import mp, mpf, sqrt, exp, pi, log
mp.dps = 30
c = 1/sqrt(2*pi)
z12 = mpf('-1.4603545088095868'); zm12 = mpf('-0.2078862249773545'); z32 = mpf('2.6123753486854883')
cpsi = -z12 + z32/12
def pieces(xi, k):
    k = mpf(k); xi = mpf(xi)
    q = xi*k**(mpf(2)/3); p = q-1; n = k+q; kk = k+1; eps = k**(-mpf(1)/3)
    E = 2*c*exp(-1/(12*q))*xi**(-mpf(1)/2)*(1+xi*eps)
    R1 = mpf(3)/2*c*(2*sqrt(p)-1)*k**(-mpf(2)/3)
    H = mpf(2)/3*p**mpf(1.5)+mpf(1)/2*sqrt(p)+zm12+1/(24*sqrt(p))
    R2 = mpf(15)/8*c*n**mpf(2.5)*H/(kk**mpf(3.5)*k**(mpf(2)/3))
    D1 = p/k**(mpf(2)/3)
    D2 = kk*sqrt(2/pi)/sqrt(p)/k**(mpf(2)/3)
    Psilow = c*(2*sqrt(p)-cpsi+1/(2*sqrt(p))-p**(-mpf(1.5))/24)
    D3 = mpf(3)/2*kk*Psilow/((n+1)*k**(mpf(2)/3))
    return E,R1,R2,D1,D2,D3
def qkk(xi,k):
    E,R1,R2,D1,D2,D3 = pieces(xi,k)
    return (E-R1-R2)/(D1+D2-D3)
def jinf(xi): return mpf(4)/3*c*mpf(xi)**mpf(1.5)
def Cr(q,k):
    q=mpf(q);k=mpf(k); s=mpf(4)/15*q**mpf(2.5)+mpf('0.385')*q**mpf(1.5)
    return mpf(3)/2*c*(k+q)**mpf(1.5)/(k+1)**mpf(3.5)*s
k=mpf(6600); k23=k**(mpf(2)/3); k13=k**(mpf(1)/3)
qmin=mpf('0.2')*k23; pmin=qmin-1
print("j_inf(0.2)", jinf('0.2'), "Cr(qmin,6600)", Cr(qmin,6600), "exp(-0.0477345)", exp(mpf('-0.0477345')))
print("E(0.2,6600) upper", 2*c*mpf('0.2')**-0.5*(1+mpf('0.2')/k13), "E0", 2*c*mpf('0.2')**-0.5, "ratio", mpf('1.803147')/mpf('1.952747'))
print("q6600(0.2)", qkk('0.2',6600), "q6600(2)", qkk(2,6600), "q6600(2.1)", qkk('2.1',6600))
print("e^-jinf(2)", exp(-jinf(2)), "e^-jinf(2.1)", exp(-jinf('2.1')))
# (가) rho2 bound
xi=mpf('6.001'); eps=1/k13
rho2 = mpf(5)/8*(1+3/(4*pmin))*(1+xi*eps)**mpf(2.5)*xi**2/k23
print("rho2 bound", rho2, "phi lower", exp(-1/(12*qmin)), "rho1 upper", mpf(3)/2*xi*eps)
print("V lower", exp(-1/(12*qmin)) - mpf(3)/2*xi*eps - rho2)
print("U upper", xi**mpf(1.5)/(2*c) + (k+1)/k*(1-1/qmin)**-0.5)
# (나) bracket
for xi in [mpf('0.1'), mpf('2.1')]:
    br = (mpf('0.4')*xi**mpf(1.5)+mpf('0.5775')*sqrt(xi)/k23)*(1+xi/k13)**mpf(1.5)
    print("bracket", xi, br)
q=mpf('0.1')*k23; p=q-1
print("q at 0.1", q, "|z-1/2|/q", 0.20789/q, "p^-3/2/(12q)", p**-1.5/(12*q))
print("0.1 case total", mpf('1.46035')-mpf('0.103945')-mpf('0.041667')-mpf('0.013274'))
print("2.1 case total", mpf('1.46035')-mpf('0.005909')-mpf('0.000012')-mpf('1.430101'))
# (다)
q2 = 2*k23; p2=q2-1; mu2=1/q2
print("q at 2", q2, "rho1' coeff", mpf(1)/2*(sqrt(1-mu2)-(1+p2**-0.5)/k13/sqrt(2)))
print("theta1' coeff", (1/k13/sqrt(2))/(3*c), "theta3 coeff", mpf(1)/2*(1+1/(4*p2)))
print("V<1 coeff", mpf(1)/2-mpf(3)/2*mu2-mpf(3)/4/k13/sqrt(2))
print("U lower at 2", 1+sqrt(2)*(2-1/k23)/(2*c)-mpf(3)/2*2/k13)
print("log q' coeff", mpf('0.146751')-mpf('0.5316752')/mpf('4.37993'))
# table-tolerance
print("r_G", mpf('0.38951')*mpf('0.7202')/mpf('19.4319')**2)
print("Lambda'(1)-0.85sqrt2", 2.75+z12-0.85*sqrt(2), "0.85 c k/(k+1)", 0.85*c*k/(k+1))
print("case2 coeffs", mpf('0.020044')*mpf('0.169524')*sqrt(mpf('0.2')), mpf('0.953386')*mpf('0.169524')*sqrt(mpf('0.0005')))
# envelope-code-monotone
print("2c sqrt(0.0005)*0.0005", 2*c*sqrt(mpf('0.0005'))*mpf('0.0005'), "Ks(0.0055)", (2/mpf('0.0055'))**1.5, "s(2)", mpf(4)/15*2**2.5+0.385*2**1.5, "Cr(2,6934.2)", Cr(2,mpf('6934.2')))
print("Cr(2e4,6.6e9)", Cr(2e4, 6.6e9), "q at 6.6e9 xi=0.005684", mpf('0.005684')*mpf(6.6e9)**(mpf(2)/3))
