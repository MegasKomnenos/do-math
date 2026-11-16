from mpmath import mp, mpf, sqrt, exp, log, zeta, pi, floor
mp.dps=30
z12=zeta(mpf(1)/2); zm12=zeta(-mpf(1)/2); z32=zeta(mpf(3)/2)
c=1/sqrt(2*pi)
print("zetas",z12,zm12,z32)
cPsi=-z12+z32/12
print("cPsi",cPsi)
k=mpf(6600); e0=k**(-mpf(1)/3); k23=k**(mpf(2)/3)
qmin=mpf('0.2')*k23; pmin=qmin-1; mu=1/qmin
print("qmin",qmin,"pmin",pmin,"sqrt pmin",sqrt(pmin),"mu",mu,"xi eps max",mpf('6.001')*e0,"eps0",e0,"k^-2/3",1/k23)
print("(1-mu)^-1/2",(1-mu)**(-mpf(1)/2),"(1-mu)^-3/2",(1-mu)**(-mpf(3)/2))
# R2 constant
print("R2 second term", (1+1/(4*pmin))/(1-mu), "third", mpf(7)/2*k/(k+1))
print("R2 sum", 2.5+(1+1/(4*pmin))/(1-mu)-mpf(7)/2*k/(k+1)-mpf(2)/3)
# D3
print("cPsi/(2 sqrt pmin)",1-cPsi/(2*sqrt(pmin)))
print("D3 sum", mpf('0.319921')/3+1/(3*(1-mu)*(1-cPsi/(2*sqrt(pmin))))-mpf(2)/3)
# (나) 0.168623
xi=mpf('0.2')
print("D1-D3 min", xi-1/k23-3*c*sqrt(xi)*e0)
# U' terms
t1=(mpf(3)/2*sqrt(xi)-mpf(1)/2/sqrt(xi)/k23)/(2*c)
t2=mpf(3)/4*e0*(1+(1-1/(xi*k23))**(-mpf(1)/2))
t3=(k+1)/(2*k)*(1-1/(xi*k23))**(-mpf(3)/2)/(xi**2*k23)
print("U' terms",t1,t2,t3,t1-t2-t3)
# V' terms
print("V' terms",(1+xi*e0)/(12*xi**2*k**(mpf(1)/3)), 3/(8*sqrt(xi)*k**(mpf(1)/3)))
# closed form (가)
print("phi min",exp(-1/(12*qmin)))
print("rho1 max",mpf(3)/2*mpf('6.001')*e0)
xi=mpf('6.001')
print("rho2 max",mpf(5)/8*(1+3/(4*pmin))*(1+xi*e0)**(mpf(5)/2)*xi**2/k23)
print("theta1 max",xi**(mpf(3)/2)/(2*c),"upsilon max",(k+1)/k*(1-mu)**(-mpf(1)/2))
# (나) 0.0243 check
for xi in [mpf('0.1'),mpf('2.1')]:
    q=xi*k23; p=q-1
    br=(mpf('0.4')*xi**(mpf(3)/2)+mpf('0.5775')*sqrt(xi)/k23)*(1+xi*e0)**(mpf(3)/2)
    print("xi",xi,"q",q,"bracket",br,"zm/q",abs(zm12)/q,"p^-3/2/12q",p**(-mpf(3)/2)/(12*q),"total",abs(z12)-abs(zm12)/q-p**(-mpf(3)/2)/(12*q)-br)
# j_inf
def jinf(xi): return mpf(4)/3*c*xi**(mpf(3)/2)
print("jinf(0.2)",jinf(mpf('0.2')),"jinf(2)",jinf(2),exp(-jinf(2)),"jinf(2.1)",jinf(mpf('2.1')),exp(-jinf(mpf('2.1'))))
def s_(q): return mpf(4)/15*q**(mpf(5)/2)+mpf('0.385')*q**(mpf(3)/2)
def Cr(q,k): return mpf(3)/2*c*(k+q)**(mpf(3)/2)/(k+1)**(mpf(7)/2)*s_(q)
print("Cr(qmin,6600)",Cr(qmin,k),"Cr(2,6934.2)",Cr(2,mpf('6934.2')),"Cr(2e4,6.6e9)",Cr(mpf(2e4),mpf(6.6e9)),"s(2)",s_(2))
print("exp(-0.0477345)",exp(-mpf('0.0477345')))
E0=2*c/sqrt(mpf('0.2'))
print("E(0.2,6600)<=",E0*(1+mpf('0.2')*e0),"denom",E0+mpf('0.168623'),"ratio",E0*(1+mpf('0.2')*e0)/(E0+mpf('0.168623')))
# q_{6600,6600}(xi)
def Psilow(r):
    if r<1: return mpf(0)
    return c*(2*sqrt(r)-cPsi+1/(2*sqrt(r))-r**(-mpf(3)/2)/24)
def pieces(xi,k):
    q=xi*k**(mpf(2)/3); p=q-1; n=k+q; kk=k+1; eps=k**(-mpf(1)/3); k23=k**(mpf(2)/3)
    H=mpf(2)/3*p**(mpf(3)/2)+p**(mpf(1)/2)/2+zm12+p**(-mpf(1)/2)/24
    E=2*c*exp(-1/(12*q))/sqrt(xi)*(1+xi*eps)
    R1=mpf(3)/2*c*(2*sqrt(p)-1)/k23
    R2=mpf(15)/8*c*n**(mpf(5)/2)*H/(kk**(mpf(7)/2)*k23)
    D1=p/k23
    D2=kk*sqrt(2/pi)/sqrt(p)/k23
    D3=mpf(3)/2*kk*Psilow(p)/((n+1)*k23)
    return E,R1,R2,D1,D2,D3
def qkk(xi,k):
    E,R1,R2,D1,D2,D3=pieces(xi,k)
    return (E-R1-R2)/(D1+D2-D3)
print("q6600(2)",qkk(mpf(2),k),"q6600(2.1)",qkk(mpf('2.1'),k),"q6600(0.2)",qkk(mpf('0.2'),k))
# G function hazard
def G(z): return mpf(3)/2*(1-z)-mpf('1.1935')*log(2/(1+z))-1/(1+z)+mpf(1)/2
print("G(0.0537)",G(mpf('0.0537')),"G(0.49)",G(mpf('0.49')),log(2/mpf('1.0537')),1/mpf('1.0537'),log(2/mpf('1.49')),1/mpf('1.49'))
kk=mpf(6667)
print("zlow at 6667",mpf(3)/32-mpf(3)/4*kk**(-mpf(1)/3)+mpf('0.53125')/kk)
print("q_fb at 6668",floor((3*(6668-1)/mpf(4)-floor(6*mpf(6668)**(mpf(2)/3))-3)/8), floor(6*mpf(6668)**(mpf(2)/3)))
print("3k q_max^-3/2 limit",3/mpf(6)**(mpf(3)/2))
print("U(2,6600) lower",1+(mpf(2)**(mpf(3)/2)-sqrt(2)/k23)/(2*c)-mpf(3)/2*2*e0)
print("0.480085 check",mpf(1)/2*(sqrt(1-1/(2*k23))-(1+1/sqrt(2*k23-1))*e0/sqrt(2)))
print("theta1' k",e0/sqrt(2)/(3*c))
print("Lambda'(1)",mpf('2.75')+z12,"bracket p=1",-mpf(1)/6-mpf(2)/3*z12+zm12)
print("(4(2pi)^-1/2)^(2/3)",(4*c)**(mpf(2)/3))
print("2/6600^(2/3)",2/k23,"(2/0.0055)^1.5",(2/mpf('0.0055'))**(mpf(3)/2))
print("first term 8.92e-6",2*c*sqrt(mpf('0.0005'))*mpf('0.0005'))
print("K_I",mp.ceil(log(1e6)/log(mpf('1.02'))))
