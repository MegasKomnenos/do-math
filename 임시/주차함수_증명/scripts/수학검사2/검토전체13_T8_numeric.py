# 검토전체13 T8: 장8 수치 상수 재계산 (mpmath 50자리)
from mpmath import mp, mpf, sqrt, exp, log, pi, zeta, floor, quad
mp.dps = 50
out = []
def P(name, val, claim=None):
    out.append(f"{name:42s} {mp.nstr(val, 15)}" + (f"   claim: {claim}" if claim else ""))

c = 1/sqrt(2*pi)
z12 = zeta(mpf(1)/2); zm12 = zeta(-mpf(1)/2); z32 = zeta(mpf(3)/2)
P("zeta(1/2)", z12, "[-1.46036,-1.46035]"); P("zeta(-1/2)", zm12, "[-0.20789,-0.20788]"); P("zeta(3/2)", z32, "[2.61237,2.61238]")
cPsi = -z12 + z32/12
P("c_Psi", cPsi, "<1.678059, >3/2")
k0 = mpf(6600)
eps0 = k0**(-mpf(1)/3)
P("eps0=6600^-1/3", eps0, "<=0.0533113")
P("6600^-2/3", k0**(-mpf(2)/3), "<=0.00284209")
qmin = mpf('0.2')*k0**(mpf(2)/3)
P("q_min", qmin, ">70.3708")
P("sqrt(p_min)", sqrt(qmin-1), ">=8.32891")
mu = 1/qmin
P("mu", mu, "<=0.0142105")
P("6.001*eps0", mpf('6.001')*eps0, "<0.319921")
P("(1-mu)^-1/2", (1-mu)**(-mpf(1)/2), "<=1.007182")
P("(1-mu)^-3/2", (1-mu)**(-mpf(3)/2), "<=1.021701")
# D1-D3 lower bound at xi=0.2,k=6600
xi = mpf('0.2')
P("0.2-k^-2/3-3c sqrt(.2) k^-1/3", xi - k0**(-mpf(2)/3) - 3*c*sqrt(xi)*eps0, ">0.168623")
# (라) U' pieces
first = (mpf(3)/2*sqrt(xi) - sqrt(xi)**-1/2*k0**(-mpf(2)/3))/(2*c)
P("U' first term", first, ">0.8367662")
second = mpf(3)/4*eps0*(1+(1-1/(xi*k0**(mpf(2)/3)))**(-mpf(1)/2))
P("U' second term", second, "<0.0802540")
third = (k0+1)/(2*k0)*(1-1/(xi*k0**(mpf(2)/3)))**(-mpf(3)/2)/(xi**2*k0**(mpf(2)/3))
P("U' third term", third, "<0.0363026")
P("U' sum", first-second-third, ">0.7202096")
# (마)
t1 = (1+xi*eps0)/(12*xi**2*k0**(mpf(1)/3)); t2 = 3/(8*sqrt(xi)*k0**(mpf(1)/3))
P("V' term1", t1, "<0.112250"); P("V' term2", t2, "<0.044703"); P("sum", t1+t2, "<0.156953")
# pieces-k-monotone R2 numbers
P("(1+1/(4p_min))/(1-mu)", (1+1/(4*(qmin-1)))/(1-mu), "<=1.018072")
P("3.5*6600/6601", mpf('3.5')*k0/(k0+1), ">=3.49946")
P("1-cPsi/(2 sqrt pmin)", 1-cPsi/(2*sqrt(qmin-1)), ">0.89926")
P("D3 log-deriv bound", mpf('0.319921')/3 + 1/(3*mpf('0.985789')*mpf('0.89926')) - mpf(2)/3, "<-0.184")
# jensen seam numbers
jinf = lambda x: mpf(4)/3*c*x**(mpf(3)/2)
P("j_inf(0.2)", jinf(xi), "<=0.0475767")
def s_frak(q): return mpf(4)/15*q**(mpf(5)/2) + mpf('0.385')*q**(mpf(3)/2)
def Cr(q,k): return mpf(3)/2*c*(k+q)**(mpf(3)/2)/(k+1)**(mpf(7)/2)*s_frak(q)
P("Cr(q_min,6600)", Cr(qmin,k0), "<=1.578e-4")
P("exp(-0.0477345)", exp(-mpf('0.0477345')), ">=0.953386")
E0 = lambda x: 2*c/sqrt(x)
num = E0(xi)*(1+xi*eps0); den = mpf('0.168623')+E0(xi)
P("E(0.2,6600) upper", num, "<1.803147"); P("denominator", den, ">1.952747"); P("ratio", num/den, "<0.92339")
# envelope-code-monotone (나)
P("2c sqrt(0.0005)*0.0005", 2*c*sqrt(mpf('0.0005'))*mpf('0.0005'), ">8.92e-6")
P("(2/0.0055)^1.5", (2/mpf('0.0055'))**(mpf(3)/2), ">=6934.2")
P("s(2)", s_frak(mpf(2)), "<2.59744")
P("Cr(2,6934.2)", Cr(mpf(2), mpf('6934.2')), "<=3.24e-8")
P("Cr(2e4,6.6e9)", Cr(mpf(2e4), mpf(6.6e9)), "<=2.08e-10")
# closed-form (가)
P("exp(-1/(12 q_min))", exp(-1/(12*qmin)), ">0.998816")
P("1.5*6.001*eps0", mpf('1.5')*mpf('6.001')*eps0, "<0.4798811 ??")
xi6 = mpf('6.001'); xe = xi6*eps0
rho2 = mpf(5)/8*(1+3/(4*(qmin-1)))*(1+xe)**(mpf(5)/2)*xi6**2*k0**(-mpf(2)/3)
P("rho2 bound (6.001,6600)", rho2, "<=0.129421 ??")
P("6.001^1.5/(2c)", xi6**(mpf(3)/2)/(2*c), "<=18.42449")
P("(k+1)/k (1-mu)^-1/2", (k0+1)/k0*(1-mu)**(-mpf(1)/2), "<=1.00734")
P("0.3895139/19.43183", mpf('0.3895139')/mpf('19.43183'), ">=0.020044")
# closed-form (나)
def bracket(x,k): return (mpf('0.4')*x**(mpf(3)/2)+mpf('0.5775')*sqrt(x)*k**(-mpf(2)/3))*(1+x*k**(-mpf(1)/3))**(mpf(3)/2)
P("bracket(0.1,6600)", bracket(mpf('0.1'),k0), "<=0.013274")
P("case xi<=0.1 total", -z12 - mpf('0.20789')/2 - mpf(1)/24 - bracket(mpf('0.1'),k0), ">1.3014")
q01 = mpf('0.1')*k0**(mpf(2)/3)
P("q at xi=0.1", q01, ">=35.1854")
P("|z-1/2|/q", mpf('0.20789')/q01, "<=0.005909")
P("p^-3/2/(12q)", (q01-1)**(-mpf(3)/2)/(12*q01), "<=0.000012")
P("bracket(2.1,6600)", bracket(mpf('2.1'),k0), "<=1.430101")
P("case 0.1-2.1 total", mpf('1.46035') - mpf('0.005909') - mpf('0.000012') - bracket(mpf('2.1'),k0), ">0.0243")
# closed-form (다)
q2 = 2*k0**(mpf(2)/3); mu2 = 1/q2; p2 = q2-1
P("2*6600^2/3", q2, ">703.708")
br = sqrt(1-mu2) - (1+p2**(-mpf(1)/2))*eps0/sqrt(mpf(2))
P("0.5*bracket (rho1')", br/2, ">=0.480085")
P("0.480085-1/3", mpf('0.480085')-mpf(1)/3, ">0.146751")
P("eps0/sqrt2/(3*(2c))", eps0/sqrt(mpf(2))/(3*2*c)*2, "<=0.0314973  [sqrt(xi)k^-5/3/(3c) = xi k^-4/3 * k^-1/3 xi^-1/2/(3c)]")
P("0.5*(1+1/(4p2))", (1+1/(4*p2))/2, "<=0.5001779")
P("V<1 bracket", mpf(1)/2 - mpf(3)/2*mu2 - mpf(3)/4*eps0/sqrt(mpf(2)), ">=0.46959")
U2 = 1 + (mpf(2)**(mpf(3)/2) - sqrt(mpf(2))*k0**(-mpf(2)/3))/(2*c) - mpf(3)/2*2*eps0
P("U lower at xi=2", U2, ">4.37993")
P("0.146751-0.5316752/4.37993", mpf('0.146751')-mpf('0.5316752')/mpf('4.37993'), ">=0.02536")
# closed-form (라) seam values: compute q_{6600,6600}(xi) exactly
def Psi_low(r):
    if r < 1: return mpf(0)
    return c*(2*sqrt(r) - cPsi + 1/(2*sqrt(r)) - r**(-mpf(3)/2)/24)
def pieces(x,k):
    q = x*k**(mpf(2)/3); p = q-1; n = k+q; kk = k+1; e = k**(-mpf(1)/3)
    H = mpf(2)/3*p**(mpf(3)/2) + p**(mpf(1)/2)/2 + zm12 + p**(-mpf(1)/2)/24
    E = 2*c*exp(-1/(12*q))/sqrt(x)*(1+x*e)
    R1 = mpf(3)/2*c*(2*sqrt(p)-1)*k**(-mpf(2)/3)
    R2 = mpf(15)/8*c*n**(mpf(5)/2)*H/(kk**(mpf(7)/2)*k**(mpf(2)/3))
    D1 = p/k**(mpf(2)/3)
    D2 = kk*sqrt(2/pi)/sqrt(p)/k**(mpf(2)/3)
    D3 = mpf(3)/2*kk*Psi_low(p)/((n+1)*k**(mpf(2)/3))
    return E,R1,R2,D1,D2,D3
def qkk(x,k):
    E,R1,R2,D1,D2,D3 = pieces(x,k); return (E-R1-R2)/(D1+D2-D3)
P("q_6600(2)", qkk(mpf(2),k0), "<=0.213721"); P("exp(-jinf(2))", exp(-jinf(mpf(2))), ">=0.222127")
P("q_6600(2.1)", qkk(mpf('2.1'),k0), ">=0.200904"); P("exp(-jinf(2.1))", exp(-jinf(mpf('2.1'))), "<=0.198148")
P("q_6600(0.2)", qkk(xi,k0), "<0.92339 (upper bound used)")
P("q_6600(6.001)", qkk(xi6,k0), ">=0.020044")
# table-tolerance (나)
P("0.38951*0.7202/19.4319^2", mpf('0.38951')*mpf('0.7202')/mpf('19.4319')**2, ">=7.429e-4")
P("0.85 c *6600/6601", mpf('0.85')*c*k0/(k0+1), ">=0.339049")
P("0.020044*0.169524*sqrt(.2)", mpf('0.020044')*mpf('0.169524')*sqrt(xi), ">=1.51e-3")
P("0.953386*0.169524*sqrt(.0005)", mpf('0.953386')*mpf('0.169524')*sqrt(mpf('0.0005')), ">=3.61e-3")
P("Lambda'(1)=2.75+z12", mpf('2.75')+z12, ">=1.28964")
P("-1/6-2/3 z12 + zm12", -mpf(1)/6 - mpf(2)/3*z12 + zm12, ">0.599")
P("2.75+z12-0.85*sqrt2", mpf('2.75')+z12-mpf('0.85')*sqrt(mpf(2)), ">0.087")
# explicit-bounds (나) r=1 consequences
P("Psi_low(1) = c(59/24 - cPsi)", c*(mpf(59)/24 - cPsi), ">0")
# hazard-H1
k1 = mpf(6667)
qmax1 = floor(6*k1**(mpf(2)/3)); qfb1 = floor((3*(k1-1)/4 - qmax1 - 3)/8)
P("q_max(6667)", qmax1); P("q_fb(6667)", qfb1)
P("(q_fb+2)/k at 6667", (qfb1+2)/k1, ">=0.0537")
P("3/32-3/4 k^-1/3+0.53/k", mpf(3)/32 - mpf(3)/4*k1**(-mpf(1)/3) + mpf('0.53')/k1, ">=0.0537")
def G(z): return mpf(3)/2*(1-z) - mpf('1.1935')*log(2/(1+z)) - 1/(1+z) + mpf(1)/2
P("G(0.0537)", G(mpf('0.0537')), ">0.205"); P("G(0.571)", G(mpf('0.571')), ">0.218")
P("log(2/1.0537)", log(2/mpf('1.0537')), "<0.64084"); P("1/1.0537", 1/mpf('1.0537'), "<0.94904")
P("log(2/1.571)", log(2/mpf('1.571')), "<0.24144"); P("1/1.571", 1/mpf('1.571'), "<0.63654")
P("3/2-0.307(1-3/(2*6667))", mpf(3)/2-mpf('0.307')*(1-3/(2*k1)), "<=1.1935")
P("3.2/6667", mpf('3.2')/k1, "<=0.0005")
# old-6-29 (2) numbers at k=6668
k2 = mpf(6668); qmax2 = floor(6*k2**(mpf(2)/3))
P("q_max(6668)", qmax2); P("k-2399-q_max-300", k2-2399-qmax2-300, ">=0")
P("k-2398-q_max - k/4", k2-2398-qmax2-k2/4, ">=0")
# envelope-HG: 9i>=5(n+1) threshold
for kk_ in [421,422]:
    kk_=mpf(kk_); P(f"4k+13-30k^(2/3) at k={int(kk_)}", 4*kk_+13-30*kk_**(mpf(2)/3), ">=0 ?")
# (8.15) xi threshold
P("2/6600^(2/3)", 2/k0**(mpf(2)/3), "~0.005684")
# (나) of explicit bounds: sqrt3/288 <= 1/24 check trivial
# 6600^{2/3}*0.2 etc done.
# table check seam 0.2: s_env_W(0.2) lower bound and j_inf
# (2 pi)^{-1/3}
P("(2pi)^-1/3", (2*pi)**(-mpf(1)/3), "~0.54")
P("(4c)^(2/3)", (4*c)**(mpf(2)/3), "~1.37")
P("(5+sqrt5)/2", (5+sqrt(mpf(5)))/2, "<3.62")
P("(6600/6599)^(2/3)", (k0/(k0-1))**(mpf(2)/3), "<=1.0002")
P("K^(2/3) for K=1e5, 12927/K^(2/3)", mpf(12927)/mpf(1e5)**(mpf(2)/3), ">6")
open(r"C:\math\임시\주차함수_증명\scripts\수학검사2\검토전체13_T8_numeric_out.txt","w",encoding="utf-8").write("\n".join(out))
print("\n".join(out))
