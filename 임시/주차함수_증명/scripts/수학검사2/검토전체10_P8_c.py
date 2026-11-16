# P8: 8.2 봉투·단조성 정리들의 수치 상수 재계산
from mpmath import mp, mpf, sqrt, exp, log, zeta, pi, factorial, quad, diff
mp.dps=30
z12=zeta(mpf(1)/2); zm12=zeta(-mpf(1)/2); z32=zeta(mpf(3)/2); c=(2*pi)**(-mpf(1)/2); cP=-z12+z32/12
def Bor(m): return exp(-m)*mpf(m)**(m-1)/factorial(m)
def Ren(j): return mpf(1) if j==0 else exp(-j)*mpf(j)**j/factorial(j)
def g(x): x=mpf(x); return (x-1)*log(1+1/x)
def Plow(r):
    r=mpf(r); return mpf(0) if r<1 else c*(2*sqrt(r)-cP+1/(2*sqrt(r))-r**(-mpf(3)/2)/24)
def Lam(q):
    q=mpf(q); p=q-1; return q*(2*sqrt(p)+z12+1/(2*sqrt(p)))-(mpf(2)/3*p**1.5+sqrt(p)/2+zm12)
def Bp(q,k): return c*Lam(q)/(k+1)
def s_(q): return mpf(4)/15*q**2.5+mpf('0.385')*q**1.5
def Cr(q,k): return mpf(3)/2*c*(k+q)**1.5/(k+1)**3.5*s_(q)
k=mpf(6600)
# Jensen H: J(q,k) <= Bp+Cr (exact J via Bor/Ren) for sample q
bad=[]
for q in [2,3,5,10,30,70,100,300,700,1000,1500,2111]:
    kk=k+1; J=sum((q-r)*Ren(r)*Bor(kk+q-r)/Bor(kk+q) for r in range(1,q))/kk
    if not J<=Bp(q,k)+Cr(q,k): bad.append(q)
print("H viol",bad)
# envelope-HG dagger and pieces at k=6600,q=2111 ; exact pi0 and km vs E-R1-R2 and D's
def pieces(xi,k):
    q=xi*k**(mpf(2)/3); p=q-1; n=k+q; kk=k+1; eps=k**(-mpf(1)/3)
    E=2*c*exp(-1/(12*q))/sqrt(xi)*(1+xi*eps); R1=mpf(3)/2*c*(2*sqrt(p)-1)*k**(-mpf(2)/3)
    H=mpf(2)/3*p**1.5+sqrt(p)/2+zm12+1/(24*sqrt(p)); R2=mpf(15)/8*c*n**2.5*H/(kk**3.5*k**(mpf(2)/3))
    D1=p/k**(mpf(2)/3); D2=kk*sqrt(2/pi)/sqrt(p)/k**(mpf(2)/3); D3=mpf(3)/2*kk*Plow(p)/((n+1)*k**(mpf(2)/3))
    return E,R1,R2,D1,D2,D3
for q in [71,500,2111]:
    xi=mpf(q)/k**(mpf(2)/3); n=k+q; kk=k+1
    rho=[Bor(n+1-j)/Bor(n+1) for j in range(1,q)]
    bad=[j for j in range(1,q) if not rho[j-1]>=1+mpf(3)*j/(2*(n+1))]
    pi0=1-sum(Bor(j)*rho[j-1] for j in range(1,q)); km=sum(Bor(j)*rho[j-1]*kk/(n+1-j) for j in range(1,q))
    E,R1,R2,D1,D2,D3=pieces(xi,k); sc=n/k**(mpf(2)/3)
    print("q",q,"dagger viol",len(bad),"pi0*sc",pi0*sc,">=",E-R1-R2,"(1-km)*sc",(1-km)*sc,"<=",D1+D2-D3)
# closed-form numbers
def qkk(xi,k):
    E,R1,R2,D1,D2,D3=pieces(mpf(xi),k); return (E-R1-R2)/(D1+D2-D3)
jinf=lambda xi: mpf(4)/3*c*mpf(xi)**1.5
print("q(2)",qkk(2,k),"e^-j(2)",exp(-jinf(2)),"q(2.1)",qkk('2.1',k),"e^-j(2.1)",exp(-jinf('2.1')))
# (가) V>=0.38951, U<=19.4319 at xi=6.001
xi=mpf('6.001'); eps=k**(-mpf(1)/3); q=xi*k**(mpf(2)/3); p=q-1; mu=1/q; pmin=mpf('0.2')*k**(mpf(2)/3)-1
print("phi>=",exp(-1/(12*(pmin+1))),"rho1<",1.5*xi*eps,"rho2<=",mpf(5)/8*(1+3/(4*pmin))*(1+xi*eps)**2.5*xi**2*k**(-mpf(2)/3))
print("U<=",xi**1.5/(2*c)+(k+1)/k*(1-1/(pmin+1))**-0.5)
# (라) U' at xi=0.2
xi=mpf('0.2'); kp=k
t1=(1.5*sqrt(xi)-0.5/sqrt(xi)*kp**(-mpf(2)/3))/(2*c); t2=0.75*kp**(-mpf(1)/3)*(1+(1-1/(xi*kp**(mpf(2)/3)))**-0.5); t3=(k+1)/(2*k)*(1-1/(xi*k**(mpf(2)/3)))**-1.5/(xi**2*k**(mpf(2)/3))
print("U' parts",t1,t2,t3,t1-t2-t3)
print("V' parts",(1+xi*eps)/(12*xi**2*k**(mpf(1)/3)), 3/(8*sqrt(xi)*k**(mpf(1)/3)))
# R2, D3 derivative constants
print("1.018072?",(1+1/(4*pmin))/(1-1/(pmin+1)),"3.49946?",3.5*k/(k+1),"0.985789?",1-1/(pmin+1),"0.89926?",1-cP/(2*sqrt(pmin)))
print("D3 total",mpf('0.319921')/3+1/(3*mpf('0.985789')*mpf('0.89926'))-mpf(2)/3)
# (나) numbers
print("Lam'(1)",2.75+z12, "(나) xi<=0.1:",-z12+zm12/2-mpf(1)/24-(0.4*mpf('0.1')**1.5+0.5775*sqrt(mpf('0.1'))*k**(-mpf(2)/3))*(1+mpf('0.1')*eps)**1.5)
q1=mpf('0.1')*k**(mpf(2)/3); print("q>=35.1854",q1,-z12+zm12/q1-(q1-1)**-1.5/(12*q1)-(0.4*mpf('2.1')**1.5+0.5775*sqrt(mpf('2.1'))*k**(-mpf(2)/3))*(1+mpf('2.1')*eps)**1.5)
# (다) numbers
q2=2*k**(mpf(2)/3); mu2=1/q2
print("0.480085?",0.5*(sqrt(1-mu2)-(1+(q2-1)**-0.5)*eps/sqrt(2)),"0.0314973?",eps/sqrt(2)/(3*c),"0.5001779?",0.5*(1+1/(4*(q2-1))))
print("0.46959?",0.5-1.5*mu2-0.75*eps/sqrt(2),"4.37993?",1+(mpf(2)**1.5-sqrt(2)*k**(-mpf(2)/3))/(2*c)-1.5*2*eps)
print("0.146751-0.5316752/4.37993",mpf('0.146751')-mpf('0.5316752')/mpf('4.37993'))
# table-tolerance
print("rG",mpf('0.38951')*mpf('0.7202')/mpf('19.4319')**2, "0.339049?",0.85*c*k/(k+1), "1.51e-3?",mpf('0.020044')*mpf('0.169524')*sqrt(mpf('0.2')),"3.61e-3?",mpf('0.953386')*mpf('0.169524')*sqrt(mpf('0.0005')))
# hazard-H1
def G(z): z=mpf(z); return 1.5*(1-z)-mpf('1.1935')*log(2/(1+z))-1/(1+z)+0.5
kk=mpf(6667); print("G",G('0.0537'),G('0.571'),"low end",mpf(3)/32-0.75*kk**(-mpf(1)/3)+mpf('0.53')/kk, "3.2/k",3.2/kk, "1.5-0.307(1-3/2k)",1.5-0.307*(1-1.5/kk))
# old-6-29 (2) at k=6668
k8=6668; print("k-2399>=qmax+300?",k8-2399, int(6*k8**(2/3))+300, "3k/4>=2398+qmax?",0.75*k8,2398+int(6*k8**(2/3)), "6k^2/3<=k+3? at 216",6*216**(2/3))
# dagger k>=422
import math
print("9(k+2)-5(k+6k^2/3+1) at 421,422:",[9*(kk+2)-5*(kk+6*kk**(2/3)+1) for kk in (421,422)])
# envelope-code-monotone (가) remark: s_env_G(0.2)<=0.9234 uses D2(k)>=E0: check D2(xi,k)>E0 ; also check s^env_G nonneg
