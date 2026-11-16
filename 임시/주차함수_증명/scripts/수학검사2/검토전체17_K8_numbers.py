
# 8장 수치 재검산 (K8). mpmath 50자리.
from mpmath import mp, mpf, sqrt, exp, log, pi, e, zeta, quad
mp.dps = 50
c = 1/sqrt(2*pi)
z12 = zeta(mpf(1)/2); zm12 = zeta(-mpf(1)/2); z32 = zeta(mpf(3)/2)
cPsi = -z12 + z32/12
out = []
def P(*a): out.append(" ".join(str(x) for x in a))

P("zeta", z12, zm12, z32, "cPsi", cPsi)
k0 = mpf(6600)
P("line192: qmin", mpf('0.2')*k0**(mpf(2)/3), "pmin", mpf('0.2')*k0**(mpf(2)/3)-1,
  "sqrt pmin", sqrt(mpf('0.2')*k0**(mpf(2)/3)-1), "mu", 1/(mpf('0.2')*k0**(mpf(2)/3)),
  "xi eps max", mpf('6.001')*k0**(-mpf(1)/3), "eps0", k0**(-mpf(1)/3), "k^-2/3", k0**(-mpf(2)/3))
mu = 1/(mpf('0.2')*k0**(mpf(2)/3))
P("(1-mu)^-1/2", (1-mu)**(-mpf(1)/2), "(1-mu)^-3/2", (1-mu)**(-mpf(3)/2))

# pieces
def qq(xi,k): return xi*k**(mpf(2)/3)
def E(xi,k):
    q=qq(xi,k); return 2*c*exp(-1/(12*q))*xi**(-mpf(1)/2)*(1+xi*k**(-mpf(1)/3))
def R1(xi,k):
    p=qq(xi,k)-1; return mpf(3)/2*c*(2*sqrt(p)-1)*k**(-mpf(2)/3)
def H(p): return mpf(2)/3*p**mpf(1.5)+p**mpf(0.5)/2+zm12+p**(-mpf(0.5))/24
def R2(xi,k):
    q=qq(xi,k); p=q-1; n=k+q; kk=k+1
    return mpf(15)/8*c*n**mpf(2.5)*H(p)/(kk**mpf(3.5)*k**(mpf(2)/3))
def D1(xi,k): return xi-k**(-mpf(2)/3)
def D2(xi,k):
    q=qq(xi,k); p=q-1; return (k+1)*sqrt(2/pi)*p**(-mpf(0.5))*k**(-mpf(2)/3)
def Psilow(r):
    if r<1: return mpf(0)
    return c*(2*sqrt(r)-cPsi+1/(2*sqrt(r))-r**(-mpf(1.5))/24)
def D3(xi,k):
    q=qq(xi,k); p=q-1; n=k+q
    return mpf(3)/2*(k+1)*Psilow(p)/((n+1)*k**(mpf(2)/3))
def qkk(xi,k,kp=None):
    if kp is None: kp=k
    return (E(xi,kp)-R1(xi,k)-R2(xi,k))/(D1(xi,kp)+D2(xi,k)-D3(xi,kp))
def jinf(xi): return mpf(4)/3*c*xi**mpf(1.5)
def Lam(q):
    p=q-1; return q*(2*sqrt(p)+z12+1/(2*sqrt(p)))-(mpf(2)/3*p**mpf(1.5)+p**mpf(0.5)/2+zm12)
def Bp(q,k): return c*Lam(q)/(k+1)
def s_(q): return mpf(4)/15*q**mpf(2.5)+mpf('0.385')*q**mpf(1.5)
def Cr(q,k): return mpf(3)/2*c*(k+q)**mpf(1.5)/(k+1)**mpf(3.5)*s_(q)

xi=mpf('0.2'); k=k0
P("(na) 0.168623:", xi-k**(-mpf(2)/3)-3*c*sqrt(xi)*k**(-mpf(1)/3), " D1-D3 actual", D1(xi,k)-D3(xi,k))
# (ra)
t1=(mpf(1.5)*sqrt(xi)-mpf(0.5)*xi**(-mpf(0.5))*k**(-mpf(2)/3))/(2*c)
t2=mpf(0.75)*k**(-mpf(1)/3)*(1+(1-1/qq(xi,k))**(-mpf(0.5)))
t3=(k+1)/(2*k)*(1-1/qq(xi,k))**(-mpf(1.5))/(xi**2*k**(mpf(2)/3))
P("(ra) terms", t1,t2,t3, t1-t2-t3)
# (ma)
P("(ma)", (1+xi*k**(-mpf(1)/3))/(12*xi**2*k**(mpf(1)/3)), 3/(8*sqrt(xi)*k**(mpf(1)/3)))
# pieces-k-monotone R2 numbers
pmin=mpf('0.2')*k0**(mpf(2)/3)-1
P("R2: (1+1/(4p))/(1-mu)", (1+1/(4*pmin))/(1-mu), " 3.5k/(k+1)", mpf(3.5)*k0/(k0+1))
P("D3: 1-cPsi/(2 sqrt pmin)", 1-cPsi/(2*sqrt(pmin)), " sum", mpf('0.319921')/3+1/(3*(1-mu)*(1-cPsi/(2*sqrt(pmin))))-mpf(2)/3)
P("R1 root (5+sqrt5)/2", (5+sqrt(5))/2)
# table-lower-bound
P("jinf(0.2)", jinf(mpf('0.2')), "Cr(qmin,6600)", Cr(mpf('0.2')*k0**(mpf(2)/3),k0), "exp", exp(-(jinf(mpf('0.2'))+Cr(mpf('0.2')*k0**(mpf(2)/3),k0))))
P("q6600(0.2) bound", 2*c*mpf('0.2')**(-mpf(0.5))*(1+mpf('0.2')*k0**(-mpf(1)/3)), 2*c*mpf('0.2')**(-mpf(0.5)), (2*c*mpf('0.2')**(-mpf(0.5))*(1+mpf('0.2')*k0**(-mpf(1)/3)))/(mpf('0.168623')+2*c*mpf('0.2')**(-mpf(0.5))), " actual q", qkk(mpf('0.2'),k0))
# closed form (ga)
xi=mpf('6.001')
P("(ga) phi", exp(-1/(12*(mpf('0.2')*k0**(mpf(2)/3)))), "rho1", mpf(1.5)*xi*k0**(-mpf(1)/3),
  "rho2", mpf(5)/8*(1+3/(4*pmin))*(1+xi*k0**(-mpf(1)/3))**mpf(2.5)*xi**2*k0**(-mpf(2)/3),
  "theta1", xi**mpf(1.5)/(2*c), "ups", (k0+1)/k0*(1-mu)**(-mpf(0.5)))
V=exp(-1/(12*(mpf('0.2')*k0**(mpf(2)/3))))-mpf(1.5)*xi*k0**(-mpf(1)/3)-mpf(5)/8*(1+3/(4*pmin))*(1+xi*k0**(-mpf(1)/3))**mpf(2.5)*xi**2*k0**(-mpf(2)/3)
U=xi**mpf(1.5)/(2*c)+(k0+1)/k0*(1-mu)**(-mpf(0.5))
P("V,U,V/U", V,U,V/U)
# (na)
def brk(xi,k): return (mpf('0.4')*xi**mpf(1.5)+mpf('0.5775')*sqrt(xi)*k**(-mpf(2)/3))*(1+xi*k**(-mpf(1)/3))**mpf(1.5)
P("(na) xi<=0.1:", -z12 - (-zm12)/2 - mpf(1)/24 - brk(mpf('0.1'),k0), " brk", brk(mpf('0.1'),k0))
q21=mpf('0.1')*k0**(mpf(2)/3)
P("(na) 0.1..2.1:", q21, -z12 - (-zm12)/q21 - (q21-1)**(-mpf(1.5))/(12*q21) - brk(mpf('2.1'),k0), " terms", (-zm12)/q21, (q21-1)**(-mpf(1.5))/(12*q21), brk(mpf('2.1'),k0))
# (da)
q2=2*k0**(mpf(2)/3); mu2=1/q2; p2=q2-1
P("(da) 0.480085:", mpf(0.5)*(sqrt(1-mu2)-(1+p2**(-mpf(0.5)))*k0**(-mpf(1)/3)/sqrt(2)))
P("(da) 0.0314973:", k0**(-mpf(1)/3)/sqrt(2)/(3*c), " 0.5001779:", mpf(0.5)*(1+1/(4*p2)))
P("(da) 0.46959:", mpf(0.5)-mpf(1.5)*mu2-mpf(0.75)*k0**(-mpf(1)/3)/sqrt(2))
xi=mpf(2)
P("(da) 4.37993:", 1+(xi**mpf(1.5)-sqrt(xi)*k0**(-mpf(2)/3))/(2*c)-mpf(1.5)*xi*k0**(-mpf(1)/3), " 0.02536:", mpf('0.146751')-mpf('0.5316752')/mpf('4.37993'))
# (ra) seams
P("seam q(2)", qkk(mpf(2),k0), "e^-j(2)", exp(-jinf(mpf(2))), "q(2.1)", qkk(mpf('2.1'),k0), "e^-j(2.1)", exp(-jinf(mpf('2.1'))))
# table-tolerance
P("rG", mpf('0.38951')*mpf('0.7202')/mpf('19.4319')**2, " 0.339049:", mpf('0.85')*c*k0/(k0+1), " 1.51e-3:", mpf('0.020044')*mpf('0.169524')*sqrt(mpf('0.2')), " 3.61e-3:", mpf('0.953386')*mpf('0.169524')*sqrt(mpf('0.0005')))
P("Lambda'(1)", 2.75+z12, " 0.85 sqrt2", mpf('0.85')*sqrt(2))
# envelope-code-monotone (na)
P("8.92e-6:", 2*c*sqrt(mpf('0.0005'))*mpf('0.0005'), " Ks:", (2/mpf('0.0055'))**mpf(1.5), " s(2):", s_(mpf(2)), " Cr(2,6934.2):", Cr(mpf(2),(2/mpf('0.0055'))**mpf(1.5)))
P("2.08e-10:", Cr(mpf(2e4), mpf(6.6e9)), " Cr(xi K^2/3, K) at xi=0.0005", Cr(mpf('0.0005')*mpf(6.6e9)**(mpf(2)/3), mpf(6.6e9)))
# hazard
for zz in [mpf('0.0537'), mpf('0.49')]:
    G=mpf(1.5)*(1-zz)-mpf('1.1935')*log(2/(1+zz))-1/(1+zz)+mpf(0.5)
    P("G(",zz,")=",G, log(2/(1+zz)), 1/(1+zz))
k=mpf(6667)
P("lower z at 6667:", mpf(3)/32-mpf(0.75)*k**(-mpf(1)/3)+mpf('0.53')/k, " 1.5-0.307(1-1.5/k)", 1.5-mpf('0.307')*(1-1.5/k), " 3.2/k", mpf('3.2')/k)
# misc
k=mpf(6668); qmax=int(6*k**(mpf(2)/3))
P("k=6668 qmax", qmax, "k-2399", k-2399, " 3k qmax^-1.5", 3*k*mpf(qmax)**(-mpf(1.5)), " (k/(k-1))^(2/3)", (k/(k-1))**(mpf(2)/3), " 6k^2/3<=k+3 at 6600:", 6*k0**(mpf(2)/3), " 2/6600^(2/3)", 2/k0**(mpf(2)/3))
# 9i>=5(n+1) with i=k+2, n+1=k+6k^(2/3)+1
for kk in [421,422,423]:
    kk=mpf(kk); P("k",kk," 9(k+2)-5(k+6k^2/3+1)=", 9*(kk+2)-5*(kk+6*kk**(mpf(2)/3)+1))
# D1 numbers
P("qfb+2 over k at 6668:", (int((3*(k-1)/4-qmax-3)/8)+2)/k)
# integral 0.744 check needs Omega; skip
# Lambda check at p=1: -1/6-2/3 z12+zm12
P("bracket p=1:", -mpf(1)/6-mpf(2)/3*z12+zm12)
P("cPsi>3/2:", cPsi, " 35/24+1/12", mpf(35)/24+mpf(1)/12, " Psi_low(1)", Psilow(mpf(1)))
# (ra) explicit-bounds derivative check numerically at rho=3
r=mpf(3); h=mpf('1e-10')
P("Psilow'(3)", (Psilow(r+h)-Psilow(r-h))/(2*h), c*r**(-mpf(0.5))*(1-1/(4*r)+1/(16*r*r)))
open(r"C:\math\임시\주차함수_증명\scripts\수학검사2\검토전체17_K8_numbers.out","w",encoding="utf-8").write("\n".join(out))
print("\n".join(out))
