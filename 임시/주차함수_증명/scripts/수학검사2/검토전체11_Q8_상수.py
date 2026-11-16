# Q8: 8장 8.2절 수치 상수 재계산 (mpmath 50자리)
from mpmath import mp, mpf, sqrt, exp, log, pi, zeta, quad, inf
mp.dps = 50
C=1/sqrt(2*pi)
z12=zeta(mpf(1)/2); zm12=zeta(-mpf(1)/2); z32=zeta(mpf(3)/2)
cPsi=-z12+z32/12
print("z12",z12,"zm12",zm12,"z32",z32,"cPsi",cPsi)
k0=mpf(6600)
qmin=mpf('0.2')*k0**(mpf(2)/3); pmin=qmin-1
print("qmin",qmin,"pmin",pmin,"sqrt pmin",sqrt(pmin),"mu",1/qmin)
print("xi eps max",mpf('6.001')*k0**(-mpf(1)/3),"eps0",k0**(-mpf(1)/3),"k^-2/3",k0**(-mpf(2)/3))
mu=1/qmin
print("(1-mu)^-1/2",(1-mu)**(-mpf(1)/2),"(1-mu)^-3/2",(1-mu)**(-mpf(3)/2))
# E condition
print("E cond lhs",mpf('0.0533113')*mpf('1.32'),"rhs",6*mpf('0.04'))
# R2: 1.018072 and 3.49946
print("R2 second", (1+1/(4*pmin))/(1-mu), "third", mpf(7)/2*k0/(k0+1))
print("R2 total", mpf('2.5')+(1+1/(4*pmin))/(1-mu)-mpf(7)/2*k0/(k0+1)-mpf(2)/3)
# D3
print("1-cPsi/(2sqrt p)",1-cPsi/(2*sqrt(pmin)))
print("D3 total", mpf('0.319921')/3+1/(3*(1-mu)*(1-cPsi/(2*sqrt(pmin))))-mpf(2)/3)
# (나) 0.168623
v=mpf('0.2')-k0**(-mpf(2)/3)-3*C*sqrt(mpf('0.2'))*k0**(-mpf(1)/3)
print("(나)",v)
# (라) first term at xi=0.2,k'=6600
xi=mpf('0.2'); k=k0
t1=(mpf(3)/2*sqrt(xi)-mpf(1)/2/sqrt(xi)*k**(-mpf(2)/3))/(2*C)
t2=mpf(3)/4*k**(-mpf(1)/3)*(1+(1-1/(xi*k**(mpf(2)/3)))**(-mpf(1)/2))
t3=(k+1)/(2*k)*(1-1/(xi*k**(mpf(2)/3)))**(-mpf(3)/2)/(xi**2*k**(mpf(2)/3))
print("(라)",t1,t2,t3,t1-t2-t3)
# (마)
a=(1+xi*k**(-mpf(1)/3))/(12*xi**2*k**(mpf(1)/3)); b=3/(8*sqrt(xi)*k**(mpf(1)/3))
print("(마)",a,b,a+b,-mpf(1)/2+a+b)
# closed-form (가)
print("phi>",exp(-1/(12*qmin)))
xi=mpf('6.001')
print("rho1<",mpf(3)/2*xi*k**(-mpf(1)/3))
rho2=mpf(5)/8*(1+3/(4*pmin))*(1+xi*k**(-mpf(1)/3))**(mpf(5)/2)*xi**2*k**(-mpf(2)/3)
print("rho2<",rho2)
print("V>",exp(-1/(12*qmin))-mpf(3)/2*xi*k**(-mpf(1)/3)-rho2)
print("U<",xi**(mpf(3)/2)/(2*C),(k+1)/k*(1-mu)**(-mpf(1)/2),xi**(mpf(3)/2)/(2*C)+(k+1)/k*(1-mu)**(-mpf(1)/2))
print("q>",mpf('0.3895139')/mpf('19.43183'))
# (나) closed form
print("xi<=0.1:",abs(z12)-abs(zm12)/2-mpf(1)/24-(mpf('0.4')*mpf('0.1')**(mpf(3)/2)+mpf('0.5775')*sqrt(mpf('0.1'))*k**(-mpf(2)/3))*(1+mpf('0.1')*k**(-mpf(1)/3))**(mpf(3)/2))
print(" parts", abs(zm12)/2, mpf(1)/24, (mpf('0.4')*mpf('0.1')**(mpf(3)/2)+mpf('0.5775')*sqrt(mpf('0.1'))*k**(-mpf(2)/3))*(1+mpf('0.1')*k**(-mpf(1)/3))**(mpf(3)/2))
q01=mpf('0.1')*k**(mpf(2)/3); p01=q01-1
print("q at 0.1",q01, "zm12/q",abs(zm12)/q01, "p^-3/2/12q",p01**(-mpf(3)/2)/(12*q01))
xi=mpf('2.1')
print("bracket 2.1",(mpf('0.4')*xi**(mpf(3)/2)+mpf('0.5775')*sqrt(xi)*k**(-mpf(2)/3))*(1+xi*k**(-mpf(1)/3))**(mpf(3)/2))
# (다)
print("2*6600^(2/3)",2*k**(mpf(2)/3))
q2=2*k**(mpf(2)/3); p2=q2-1; mu2=1/q2
for xi in [mpf(2),mpf('6.001')]:
  val=mpf(1)/2*(sqrt(1-1/(xi*k**(mpf(2)/3)))-(1+(xi*k**(mpf(2)/3)-1)**(-mpf(1)/2))*k**(-mpf(1)/3)/sqrt(xi))
  print("rho1 deriv coeff xi",xi,val)
print("0.0314973:",1/(3*2*C)*k**(-mpf(1)/3)/sqrt(2))
print("0.5001779:",mpf(1)/2*(1+1/(4*p2)))
xi=mpf(2)
print("V<1-c xi eps: c=",mpf(1)/2-mpf(3)/2*mu2-mpf(3)/4*k**(-mpf(1)/3)/sqrt(xi))
U=1+(xi**(mpf(3)/2)-sqrt(xi)*k**(-mpf(2)/3))/(2*C)-mpf(3)/2*xi*k**(-mpf(1)/3)
print("U>",U)
print("final",mpf('0.146751')-mpf('0.5316752')/mpf('4.37993'))
print("(4(2pi)^-1/2)^(2/3)",(4*C)**(mpf(2)/3))
# table-lower-bound (가)
jinf=lambda x: mpf(4)/3*C*x**(mpf(3)/2)
s=lambda q: mpf(4)/15*q**(mpf(5)/2)+mpf('0.385')*q**(mpf(3)/2)
Cr=lambda q,k: mpf(3)/2*C*(k+q)**(mpf(3)/2)/(k+1)**(mpf(7)/2)*s(q)
print("jinf(0.2)",jinf(mpf('0.2')),"Cr(qmin,6600)",Cr(qmin,k0),"exp",exp(-(jinf(mpf('0.2'))+Cr(qmin,k0))), exp(-mpf('0.0477345')))
eps0=k0**(-mpf(1)/3)
num=2*C*mpf('0.2')**(-mpf(1)/2)*(1+mpf('0.2')*eps0); den=mpf('0.168623')+2*C*mpf('0.2')**(-mpf(1)/2)
print("q6600(0.2)<",num,den,num/den)
# envelope-code-monotone
print("8.92e-6:",2*C*sqrt(mpf('0.0005'))*mpf('0.0005'))
Ks=(2/mpf('0.0055'))**(mpf(3)/2); print("Ks",Ks,"s(2)",s(2),"Cr(2,Ks)",Cr(2,Ks))
print("Cr(2e4,6.6e9)",Cr(mpf(2e4),mpf(6.6e9)))
# table-tolerance
print("rG",mpf('0.38951')*mpf('0.7202')/mpf('19.4319')**2)
print("0.339049",mpf('0.85')*C*k0/(k0+1))
print("1.51e-3",mpf('0.020044')*mpf('0.169524')*sqrt(mpf('0.2')),"3.61e-3",mpf('0.953386')*mpf('0.169524')*sqrt(mpf('0.0005')))
print("Lambda'(1)",2+1-mpf(1)/4+z12, "0.85sqrt2",mpf('0.85')*sqrt(2))
print("Psi_low(1)",C*(mpf(59)/24-cPsi))
# closed-form seams
def qkk(xi,k):
  q=xi*k**(mpf(2)/3); p=q-1; n=k+q; kk=k+1; eps=k**(-mpf(1)/3)
  E=2*C*exp(-1/(12*q))*xi**(-mpf(1)/2)*(1+xi*eps)
  R1=mpf(3)/2*C*(2*sqrt(p)-1)*k**(-mpf(2)/3)
  H=mpf(2)/3*p**(mpf(3)/2)+p**(mpf(1)/2)/2+zm12+p**(-mpf(1)/2)/24
  R2=mpf(15)/8*C*n**(mpf(5)/2)*H/(kk**(mpf(7)/2)*k**(mpf(2)/3))
  D1=xi-k**(-mpf(2)/3)
  D2=kk*sqrt(2/pi)*p**(-mpf(1)/2)*k**(-mpf(2)/3)
  Pl=C*(2*sqrt(p)-cPsi+1/(2*sqrt(p))-p**(-mpf(3)/2)/24)
  D3=mpf(3)/2*kk*Pl/((n+1)*k**(mpf(2)/3))
  return (E-R1-R2)/(D1+D2-D3)
print("q6600(2)",qkk(mpf(2),k0),"e^-jinf(2)",exp(-jinf(mpf(2))))
print("q6600(2.1)",qkk(mpf('2.1'),k0),"e^-jinf(2.1)",exp(-jinf(mpf('2.1'))))
print("q6600(0.2)",qkk(mpf('0.2'),k0),"q6600(6.001)",qkk(mpf('6.001'),k0))
# hazard
G=lambda z: mpf(3)/2*(1-z)-mpf('1.1935')*log(2/(1+z))-1/(1+z)+mpf(1)/2
print("G(0.0537)",G(mpf('0.0537')),"G(0.571)",G(mpf('0.571')))
print("1.5-0.307",mpf(3)/2-mpf('0.307'))
k=mpf(6667); qmax=6*k**(mpf(2)/3); qfb=((3*(k-1)/4-qmax-3)/8)
print("qfb+2 /k at 6667",(qfb-1+2)/k, "3/32-3/4 k^-1/3", mpf(3)/32-mpf(3)/4*k**(-mpf(1)/3))
print("3.2/k",mpf('3.2')/6667)
# old-6-29 (2): k-2399 >= qmax+300?
k=mpf(6668); print("k-2399",k-2399,"qmax+300",6*k**(mpf(2)/3)+300, "k-2398-qmax vs k/4",k-2398-6*k**(mpf(2)/3),k/4)
print("6k^(2/3)<=k+1 at 216:",6*mpf(216)**(mpf(2)/3), "3.6*(k/(k-1))^(2/3) at 6668", mpf('3.6')*(k/(k-1))**(mpf(2)/3))
# cPsi upper bound, Psi_low(1)
print("35/24+1/12",mpf(35)/24+mpf(1)/12)
