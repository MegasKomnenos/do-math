# 검토전체9 O8: 8장 수치 재계산 (python -I)
from mpmath import mp, mpf, sqrt, exp, log, pi, zeta, quad, inf
mp.dps = 30

c = 1/sqrt(2*pi)
z12 = zeta(mpf(1)/2); zm12 = zeta(-mpf(1)/2); z32 = zeta(mpf(3)/2)
cPsi = -z12 + z32/12
print("zeta", z12, zm12, z32, "cPsi", cPsi)

K0 = mpf(6600)
print("--- line 192 constants")
qmin = mpf('0.2')*K0**(mpf(2)/3); pmin = qmin-1
print("qmin", qmin, "pmin", pmin, "sqrt pmin", sqrt(pmin), "mu", 1/qmin)
print("xi eps max", mpf('6.001')*K0**(-mpf(1)/3), "eps0", K0**(-mpf(1)/3), "k^-2/3", K0**(-mpf(2)/3))
mu = 1/qmin
print("(1-mu)^-1/2", (1-mu)**(-mpf(1)/2), "(1-mu)^-3/2", (1-mu)**(-mpf(3)/2))
print("1.5*xi*eps", mpf('1.5')*mpf('6.001')*K0**(-mpf(1)/3))

def Psilow(r):
    r = mpf(r)
    if r < 1: return mpf(0)
    return c*(2*sqrt(r)-cPsi+1/(2*sqrt(r))-r**(-mpf(3)/2)/24)
def Hfun(p): return mpf(2)/3*p**(mpf(3)/2)+p**(mpf(1)/2)/2+zm12+p**(-mpf(1)/2)/24
def pieces(xi,k):
    xi=mpf(xi); k=mpf(k)
    q=xi*k**(mpf(2)/3); p=q-1; n=k+q; kk=k+1; eps=k**(-mpf(1)/3)
    E=2*c*exp(-1/(12*q))*xi**(-mpf(1)/2)*(1+xi*eps)
    R1=mpf(3)/2*c*(2*sqrt(p)-1)*k**(-mpf(2)/3)
    R2=mpf(15)/8*c*n**(mpf(5)/2)*Hfun(p)/(kk**(mpf(7)/2)*k**(mpf(2)/3))
    D1=p/k**(mpf(2)/3)
    D2=kk*sqrt(2/pi)*p**(-mpf(1)/2)*k**(-mpf(2)/3)
    D3=mpf(3)/2*kk*Psilow(p)/((n+1)*k**(mpf(2)/3))
    return E,R1,R2,D1,D2,D3
def qkk(xi,k):
    E,R1,R2,D1,D2,D3=pieces(xi,k)
    return (E-R1-R2)/(D1+D2-D3)
def jinf(xi): return mpf(4)/3*c*mpf(xi)**(mpf(3)/2)
def sfun(q): return mpf(4)/15*q**(mpf(5)/2)+mpf('0.385')*q**(mpf(3)/2)
def Lam(q):
    p=q-1
    return q*(2*sqrt(p)+z12+1/(2*sqrt(p)))-(mpf(2)/3*p**(mpf(3)/2)+sqrt(p)/2+zm12)
def Bp(q,k): return c*Lam(q)/(k+1)
def Cr(q,k): return mpf(3)/2*c*(k+q)**(mpf(3)/2)/(k+1)**(mpf(7)/2)*sfun(q)

print("--- table-lower-bound (가)")
print("jinf(0.2)", jinf('0.2'), "Cr(qmin,6600)", Cr(qmin,K0), "sum", jinf('0.2')+Cr(qmin,K0), "exp(-0.0477345)", exp(-mpf('0.0477345')))
E,R1,R2,D1,D2,D3=pieces('0.2',K0)
print("E(0.2,6600)", E, "bound 2c/sqrt(.2)(1+.2eps0)", 2*c/sqrt(mpf('0.2'))*(1+mpf('0.2')*K0**(-mpf(1)/3)))
print("D1-D3", D1-D3, "D2", D2, "E0", 2*c/sqrt(mpf('0.2')), "q(0.2,6600) actual", qkk('0.2',K0), "stated bound 1.803147/1.952747", mpf('1.803147')/mpf('1.952747'))
print("0.2-k^-2/3-3c sqrt(.2) eps0 =", mpf('0.2')-K0**(-mpf(2)/3)-3*c*sqrt(mpf('0.2'))*K0**(-mpf(1)/3))

print("--- escape-y-monotone (라)(마) at xi=0.2,k=6600")
xi=mpf('0.2'); k=K0
t1=(mpf(3)/2*sqrt(xi)-sqrt(xi)**-1/2*k**(-mpf(2)/3))/(2*c)
t2=mpf(3)/4*k**(-mpf(1)/3)*(1+(1-1/(xi*k**(mpf(2)/3)))**(-mpf(1)/2))
t3=(k+1)/(2*k)*(1-1/(xi*k**(mpf(2)/3)))**(-mpf(3)/2)/(xi**2*k**(mpf(2)/3))
print("U' parts", t1,t2,t3, "sum", t1-t2-t3)
a=(1+xi*k**(-mpf(1)/3))/(12*xi**2*k**(mpf(1)/3)); b=3/(8*sqrt(xi)*k**(mpf(1)/3))
print("V' parts", a,b,a+b, -mpf(1)/2+a+b)

print("--- pieces-k-monotone R2, D3 numerics")
print("(1+1/(4pmin))/(1-mu)", (1+1/(4*pmin))/(1-mu), "3.5*6600/6601", mpf('3.5')*K0/(K0+1))
print("sum R2", mpf('2.5')+mpf('1.018072')-mpf('3.49946')-mpf(2)/3)
cP_up = mpf('1.46036')+mpf('2.61238')/12
print("cPsi upper", cP_up, "1-cPsi/(2 sqrt pmin)", 1-cP_up/(2*sqrt(pmin)), "1-mu", 1-mu)
print("D3 sum", mpf('0.319921')/3+1/(3*mpf('0.985789')*mpf('0.89926'))-mpf(2)/3)
print("9i>=5(n+1) at k=421,422:", [(k_, 9*(k_+2)-5*(k_+6*mpf(k_)**(mpf(2)/3)+1)) for k_ in (420,421,422)])

print("--- jensen-H-ii")
print("Lam'(1)=2.75+z12", mpf('2.75')+z12, "bracket at p=1", -mpf(1)/6-mpf(2)/3*z12+zm12)

print("--- closed-form (가)")
print("exp(-1/(12 qmin))", exp(-1/(12*qmin)))
xi=mpf('6.001'); k=K0; eps=k**(-mpf(1)/3)
rho2=mpf(5)/8*(1+3/(4*pmin))*(1+xi*eps)**(mpf(5)/2)*xi**2*k**(-mpf(2)/3)
print("rho2 bound", rho2, "V low", exp(-1/(12*qmin))-mpf('0.4798811')-rho2)
print("theta1 max", xi**(mpf(3)/2)/(2*c), "upsilon max", (k+1)/k*(1-mu)**(-mpf(1)/2), "U up", xi**(mpf(3)/2)/(2*c)+(k+1)/k*(1-mu)**(-mpf(1)/2))
print("ratio", mpf('0.3895139')/mpf('19.43183'))
# actual V,U,q over grid for sanity
for xx in ('0.2','1','2','2.1','6.001'):
    E,R1,R2,D1,D2,D3=pieces(xx,K0); E0=2*c/sqrt(mpf(xx))
    print(" xi",xx,"V",(E-R1-R2)/E0,"U",(D1+D2-D3)/E0,"q",qkk(xx,K0))

print("--- closed-form (나)")
def br(xi,k):
    xi=mpf(xi);k=mpf(k)
    return (mpf('0.4')*xi**(mpf(3)/2)+mpf('0.5775')*xi**(mpf(1)/2)*k**(-mpf(2)/3))*(1+xi*k**(-mpf(1)/3))**(mpf(3)/2)
print("bracket(0.1,6600)", br('0.1',K0), "total", mpf('1.46035')-mpf('0.103945')-mpf('0.041667')-br('0.1',K0))
q21=mpf('2.1')*K0**(mpf(2)/3); p21=q21-1
print("q at 2.1", q21, "|zm12|/q", mpf('0.20789')/q21, "p^-3/2/(12q)", p21**(-mpf(3)/2)/(12*q21))
print("bracket(2.1,6600)", br('2.1',K0), "total", mpf('1.46035')-mpf('0.20789')/q21-p21**(-mpf(3)/2)/(12*q21)-br('2.1',K0))
# direct check of (나): jinf - Bp - Cr > 0 at several k, xi
for xx in ('0.05','0.1','1','2.1'):
    for kk_ in (6600, 10**4, 10**6, 10**9):
        q=mpf(xx)*mpf(kk_)**(mpf(2)/3)
        if q>=2: print("  xi",xx,"k",kk_,"jinf-Bp-Cr", jinf(xx)-Bp(q,mpf(kk_))-Cr(q,mpf(kk_)))

print("--- closed-form (다) constants")
q703=2*K0**(mpf(2)/3); p703=q703-1; mu703=1/q703
print("q>=", q703, "sqrt(1-mu)", sqrt(1-mu703), "p^-1/2", p703**(-mpf(1)/2), "eps0/sqrt2", K0**(-mpf(1)/3)/sqrt(2))
brk=sqrt(1-mu703)-(1+p703**(-mpf(1)/2))*K0**(-mpf(1)/3)/sqrt(2)
print("0.5*bracket", brk/2, "dV coef", brk/2-mpf(1)/3)
print("dtheta1 coef", K0**(-mpf(1)/3)/sqrt(2)/(3*c), "dtheta3 coef", (1+1/(4*p703))/2)
print("V<1 bracket", mpf(1)/2-mpf(3)/2*mu703-mpf(3)/4*K0**(-mpf(1)/3)/sqrt(2))
xi=mpf(2); k=K0
print("U>", 1+(xi**(mpf(3)/2)-sqrt(xi)*k**(-mpf(2)/3))/(2*c)-mpf(3)/2*xi*k**(-mpf(1)/3))
print("0.146751-0.5316752/4.37993", mpf('0.146751')-mpf('0.5316752')/mpf('4.37993'))
# monotonicity in k of q_{k,k} at xi=2 (numerical)
for xx in ('2','2.1','4','6'):
    vals=[qkk(xx,kk_) for kk_ in (6600,7000,10000,10**5,10**7)]
    print(" q_kk xi",xx, [mp.nstr(v,8) for v in vals])

print("--- closed-form (라) seams")
print("q(2,6600)", qkk(2,K0), "e^-jinf(2)", exp(-jinf(2)))
print("q(2.1,6600)", qkk('2.1',K0), "e^-jinf(2.1)", exp(-jinf('2.1')))

print("--- table-tolerance")
print("0.38951*0.7202/19.4319^2", mpf('0.38951')*mpf('0.7202')/mpf('19.4319')**2)
print("Lam'(1)-0.85 sqrt2", mpf('2.75')+z12-mpf('0.85')*sqrt(2))
print("0.85 c 6600/6601", mpf('0.85')*c*K0/(K0+1), "half", mpf('0.85')*c*K0/(K0+1)/2)
print("0.020044*0.169524*sqrt(0.2)", mpf('0.020044')*mpf('0.169524')*sqrt(mpf('0.2')))
print("0.953386*0.169524*sqrt(0.000499)", mpf('0.953386')*mpf('0.169524')*sqrt(mpf('0.000499')))
print("rG*0.0004999", mpf('7.429e-4')*mpf('0.0004999'))

print("--- envelope-code-monotone (나)")
print("2c sqrt(0.0005)*0.0005", 2*c*sqrt(mpf('0.0005'))*mpf('0.0005'))
print("(2/0.0055)^1.5", (2/mpf('0.0055'))**(mpf(3)/2), "s(2)", sfun(mpf(2)), "Cr(2,6934.2)", Cr(mpf(2),mpf('6934.2')))
print("Cr(2e4,6.6e9)", Cr(mpf(2e4),mpf(6.6e9)))

print("--- hazard-H1")
def G(z): z=mpf(z); return mpf(3)/2*(1-z)-mpf('1.1935')*log(2/(1+z))-1/(1+z)+mpf(1)/2
print("G(0.0537)", G('0.0537'), "G(0.571)", G('0.571'))
k=mpf(6667); print("3/32-3/4 k^-1/3 at 6667", mpf(3)/32-mpf(3)/4*k**(-mpf(1)/3), "+0.53/k", mpf(3)/32-mpf(3)/4*k**(-mpf(1)/3)+mpf('0.53')/k, "3.2/k", mpf('3.2')/k)
print("1.5-0.307(1-3/(2k))", mpf('1.5')-mpf('0.307')*(1-3/(2*k)))
# exact q_fb at k=6667,6668
import math
for kk_ in (6667,6668):
    qmax=math.floor(6*kk_**(2/3)); qfb=math.floor((3*(kk_-1)/4-qmax-3)/8)
    print(" k",kk_,"qmax",qmax,"qfb",qfb,"(qfb+2)/k",(qfb+2)/kk_, "mfb", math.ceil(5*kk_/4)+qmax, "2k+1-8qfb", 2*kk_+1-8*qfb, "k-2399 vs qmax+300", kk_-2399, qmax+300, "k-2398-qmax vs k/4", kk_-2398-qmax, kk_/4)
print("(6668/6667)^(2/3)", (mpf(6668)/6667)**(mpf(2)/3))
print("6k^(2/3)<=k+1 at 216:", 6*216**(2/3), 217)

print("--- explicit-bounds misc")
print("z12 in [-3/2,-35/24]?", -mpf(3)/2, z12, -mpf(35)/24, "cPsi>=37/24", mpf(37)/24, "cPsi<=7/4", mpf(7)/4, "59/24", mpf(59)/24)
print("(5+sqrt5)/2", (5+sqrt(5))/2, "2/(3sqrt3)", 2/(3*sqrt(3)), "sqrt3/216", sqrt(3)/216, "sqrt3/288", sqrt(3)/288, "sqrt3/864", sqrt(3)/864)
print("max B3 on [0,1]", max(( (x**3-1.5*x**2+0.5*x) for x in [i/10000 for i in range(10001)])), "sqrt3/36", sqrt(3)/36)
print("1/(2 pi)^(1/3)", (2*pi)**(-mpf(1)/3), "(4c)^(2/3)", (4*c)**(mpf(2)/3))
print("Psi lim check: (8.4) limit 0.73?  (informational)")
