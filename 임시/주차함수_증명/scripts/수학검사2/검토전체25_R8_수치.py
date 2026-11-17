# 검토전체25 R8: 장8.md 8.2절·8.4절의 명시 수치 재계산 (mpmath 50자리)
from mpmath import mp, mpf, sqrt, exp, log, pi, zeta, floor
import math
mp.dps = 50
c0 = 1/sqrt(2*pi)            # (2pi)^{-1/2}
k = mpf(6600)
k13 = k**(mpf(1)/3); k23 = k13**2
print("6600^(2/3)", k23, " 6600^(-1/3)", 1/k13, " 6600^(-2/3)", 1/k23)
qmin = mpf("0.2")*k23; pmin = qmin-1
print("q_min", qmin, "(>70.3708?)", qmin > mpf("70.3708"))
print("p_min", pmin, "sqrt p_min", sqrt(pmin), "(>=8.32891?)", sqrt(pmin) >= mpf("8.32891"))
mu = 1/qmin
print("mu", mu, "<=0.0142105?", mu <= mpf("0.0142105"))
print("xi*eps max", mpf("6.001")/k13, "<0.319921?", mpf("6.001")/k13 < mpf("0.319921"))
print("eps0", 1/k13, "<=0.0533113?", 1/k13 <= mpf("0.0533113"))
print("k^-2/3", 1/k23, "<=0.00284209?", 1/k23 <= mpf("0.00284209"))
print("(1-mu)^-1/2", (1-mu)**mpf("-0.5"), "<=1.007182?", (1-mu)**mpf("-0.5") <= mpf("1.007182"))
print("(1-mu)^-3/2", (1-mu)**mpf("-1.5"), "<=1.021701?", (1-mu)**mpf("-1.5") <= mpf("1.021701"))
z12 = zeta(mpf("0.5")); zm12 = zeta(mpf("-0.5")); z32 = zeta(mpf("1.5"))
print("zeta(1/2)", z12, "zeta(-1/2)", zm12, "zeta(3/2)", z32)
cPsi = -z12 + z32/12
print("c_Psi", cPsi, " ub from intervals", mpf("1.46036")+mpf("2.61238")/12)
print("== pieces-k-monotone")
print("(ga) lhs", mpf("0.0533113")*mpf("1.32"))
t2 = (1+1/(4*pmin))/(1-mu); print("(na) second term coeff", t2, "<=1.018072?", t2 <= mpf("1.018072"))
t3 = mpf("3.5")*k/(k+1); print("(na) third", t3, ">=3.49946?", t3 >= mpf("3.49946"))
print("(na) sum", mpf("2.5")+mpf("1.018072")-mpf("3.49946")-mpf("0.666667"))
a = 1-mpf("1.678059")/(2*mpf("8.32891")); print("(da) 1-c/(2sqrt p)", a, ">0.89926?", a > mpf("0.89926"))
tot = mpf("0.319921")/3 + 1/(3*mpf("0.985789")*mpf("0.89926")) - mpf(2)/3
print("(da) total", tot, "<-0.184?", tot < mpf("-0.184"))
print("1-mu", 1-mu, ">=0.985789?", 1-mu >= mpf("0.985789"))
print("== escape-y-monotone")
v = mpf("0.2") - 1/k23 - 3*c0*sqrt(mpf("0.2"))/k13
print("first fact value", v, ">0.168623?", v > mpf("0.168623"))
v2 = mpf("0.2") - mpf("0.00284209") - 3*c0*sqrt(mpf("0.2"))*mpf("0.0533113")
print("first fact with rounded", v2, v2 > mpf("0.168623"))
print("3/2 c0 eps0", mpf("1.5")*c0/k13, "<=0.032?")
xi = mpf("0.2")
A = (1+xi/k13)/(12*xi**2*k13); B = 3/(8*sqrt(xi)*k13)
print("third fact terms", A, "<0.112250?", A < mpf("0.112250"), B, "<0.044703?", B < mpf("0.044703"), "sum", A+B)
T1 = (mpf("1.5")*sqrt(xi) - mpf("0.5")/sqrt(xi)/k23)/(2*c0)
T2 = mpf("0.75")/k13*(1+(1-1/(xi*k23))**mpf("-0.5"))
T3 = (k+1)/(2*k)*(1-1/(xi*k23))**mpf("-1.5")/(xi**2*k23)
print("U' terms", T1, ">0.8367662?", T1 > mpf("0.8367662"), T2, "<0.0802540?", T2 < mpf("0.0802540"), T3, "<0.0363026?", T3 < mpf("0.0363026"))
print("U' lower", T1-T2-T3)
print("== closed-form (ga)")
print("phi lb", exp(-1/(12*qmin)), ">0.998816?", exp(-1/(12*qmin)) > mpf("0.998816"))
r1 = mpf("1.5")*mpf("6.001")/k13; print("rho1 ub", r1, "<0.4798811?", r1 < mpf("0.4798811"))
xi = mpf("6.001")
r2 = mpf(5)/8*(1+3/(4*pmin))*(1+xi/k13)**mpf("2.5")*xi**2/k23
print("rho2 ub", r2, "<=0.129421?", r2 <= mpf("0.129421"))
print("V lb", mpf("0.998816")-mpf("0.4798811")-mpf("0.129421"))
u1 = xi**mpf("1.5")/(2*c0); u2 = (k+1)/k*(1-mu)**mpf("-0.5")
print("U ub parts", u1, "<=18.42449?", u1 <= mpf("18.42449"), u2, "<=1.00734?", u2 <= mpf("1.00734"))
print("quot", mpf("0.3895139")/mpf("19.43183"))
print("== closed-form (na)")
def br(xi, k):
    return (mpf("0.4")*xi**mpf("1.5") + mpf("0.5775")*sqrt(xi)*k**(-mpf(2)/3))*(1+xi*k**(-mpf(1)/3))**mpf("1.5")
print("small: bracket(0.1)", br(mpf("0.1"), k), " total", mpf("1.46035")-mpf("0.20789")/2-mpf(1)/24-br(mpf("0.1"), k))
q = mpf("0.1")*k23; p = q-1
print("q>=", q, "p>=", p, "z/q", mpf("0.20789")/q, "p^-3/2/(12q)", p**mpf("-1.5")/(12*q), "bracket(2.1)", br(mpf("2.1"), k))
print("mid total", mpf("1.46035")-mpf("0.20789")/q-p**mpf("-1.5")/(12*q)-br(mpf("2.1"), k))
print("2/(3 sqrt3)", 2/(3*sqrt(3)), "3/2*0.385", mpf("1.5")*mpf("0.385"))
print("== closed-form (da)")
q2 = 2*k23; p2 = q2-1; mu2 = 1/q2
print("q>=", q2, ">703.708?", q2 > mpf("703.708"))
b = sqrt(1-mu2) - (1+1/sqrt(p2))/k13/sqrt(mpf(2))
print("rho1 bracket", b, "half", b/2, ">=0.480085?", b/2 >= mpf("0.480085"))
print("dtheta1", (1/k13/sqrt(mpf(2)))/(3*c0), "<=0.0314973?")
print("dtheta3", mpf("0.5")*(1+1/(4*p2)), "<=0.5001779?")
print("V bracket", mpf("0.5")-mpf("1.5")*mu2-mpf("0.75")/k13/sqrt(mpf(2)), ">=0.46959?")
xi = mpf(2)
Ul = 1 + (xi**mpf("1.5") - sqrt(xi)/k23)/(2*c0) - mpf("1.5")*xi/k13
print("U lb at 2", Ul, ">=4.37993?")
print("final", mpf("0.146751")-mpf("0.5316752")/mpf("4.37993"), ">=0.02536?")
print("== (ra) seams")
def jinf(x): return mpf(4)/3*c0*x**mpf("1.5")
print("e^-j(2)", exp(-jinf(mpf(2))), " e^-j(2.1)", exp(-jinf(mpf("2.1"))))
def Psilow(x):
    if x < 1: return mpf(0)
    return c0*(2*sqrt(x)-cPsi+1/(2*sqrt(x))-x**mpf("-1.5")/24)
def Esc(xi, k):
    k=mpf(k); xi=mpf(xi)
    q = xi*k**(mpf(2)/3); p=q-1; n=k+q; kk=k+1; eps=k**(-mpf(1)/3)
    E = 2*c0*exp(-1/(12*q))*xi**mpf("-0.5")*(1+xi*eps)
    R1 = mpf("1.5")*c0*(2*sqrt(p)-1)*k**(-mpf(2)/3)
    H = mpf(2)/3*p**mpf("1.5")+sqrt(p)/2+zm12+1/(24*sqrt(p))
    R2 = mpf(15)/8*c0*n**mpf("2.5")*H/(kk**mpf("3.5")*k**(mpf(2)/3))
    D1 = p/k**(mpf(2)/3)
    D2 = kk*sqrt(2/pi)/sqrt(p)/k**(mpf(2)/3)
    D3 = mpf("1.5")*kk*Psilow(p)/((n+1)*k**(mpf(2)/3))
    return (E-R1-R2)/(D1+D2-D3)
print("Esc6600(2)", Esc(2,6600), "<=0.213721<0.222127")
print("Esc6600(2.1)", Esc("2.1",6600), ">=0.200904>0.198148")
print("Esc6600(0.2)", Esc("0.2",6600), "Esc6600(6.001)", Esc("6.001",6600))
for x in ["0.5","1.0","1.37","2","4","6.001"]:
    print(x, [mp.nstr(Esc(x,kk),8) for kk in (6600,10**4,10**5,10**7,10**10)])
print("== 8.2 end")
print("1.15/6^1.5", mpf("1.15")/mpf(6)**mpf("1.5"))
print("== hazard-H1")
def G(z): z=mpf(z); return mpf("1.5")*(1-z)-mpf("1.1935")*log(2/(1+z))-1/(1+z)+mpf("0.5")
print("log(2/1.0537)", log(2/mpf("1.0537")), "1/1.0537", 1/mpf("1.0537"), "log(2/1.49)", log(2/mpf("1.49")), "1/1.49", 1/mpf("1.49"))
print("G(0.0537)", G("0.0537"), "G(0.49)", G("0.49"))
kk=mpf(6667); print("1.5-0.307(1-3/2k)", mpf("1.5")-mpf("0.307")*(1-3/(2*kk)), "47/24+1.1935", mpf(47)/24+mpf("1.1935"), "3.2/k", mpf("3.2")/kk)
print("nu/k lb at 6667", mpf(3)/32-mpf("0.75")*kk**(-mpf(1)/3)+mpf("0.53")/kk)
print("== misc")
K = mpf(10)**5; print("6*K^(2/3)", 6*K**(mpf(2)/3), "xi_12927", 12927/K**(mpf(2)/3))
print("(4 c0)^(2/3)", (4*c0)**(mpf(2)/3), "(2pi)^(-1/3)", (2*pi)**(-mpf(1)/3))
print("J16", 3000*2**16)
def qmax(k):
    return int(floor(6*mpf(k)**(mpf(2)/3)))
for kq in (6667,6668,7000,13824,14000,10**6):
    qm=qmax(kq); qfb = int(floor((mpf(3)*(kq-1)/4-qm-3)/8))
    print(kq, "qmax", qm, "qfb", qfb, "(qfb+2)/k", mpf(qfb+2)/kq, "mfb", math.ceil(5*kq/4)+qm, "2k+1-8qfb", 2*kq+1-8*qfb, "k/4+1", kq/4+1)
# 6k^{2/3}-6(k-1)^{2/3}<1 at k=6668
kq=mpf(6668); print("6k^(2/3)-6(k-1)^(2/3)", 6*kq**(mpf(2)/3)-6*(kq-1)**(mpf(2)/3))
# 9(k+2) >= 5(k+6k^{2/3}+1) threshold
for kq in (420,421,422):
    print(kq, 9*(kq+2) - 5*(kq+6*mpf(kq)**(mpf(2)/3)+1))
