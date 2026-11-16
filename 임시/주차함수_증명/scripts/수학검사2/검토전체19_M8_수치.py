from mpmath import mp, mpf, sqrt, exp, log, pi, zeta
mp.dps=30
c=1/sqrt(2*pi)
z12=zeta(mpf(1)/2); zm12=zeta(-mpf(1)/2); z32=zeta(mpf(3)/2)
cpsi=-z12+z32/12
k=mpf(6600); e0=k**(-mpf(1)/3)
print("z",z12,zm12,z32,"cpsi",cpsi)
qmin=mpf('0.2')*k**(mpf(2)/3); pmin=qmin-1
print("qmin",qmin,"pmin",pmin,"sqrt pmin",sqrt(pmin),"mu",1/qmin,"xi eps",mpf('6.001')*e0,"eps0",e0,"k^-2/3",k**(-mpf(2)/3))
mu=1/qmin
print("(1-mu)^-1/2",(1-mu)**(-mpf(1)/2),"(1-mu)^-3/2",(1-mu)**(-mpf(3)/2),"1-mu",1-mu)
print("2/6600^(2/3)",2/k**(mpf(2)/3))
# R2 derivative
print("R2 second",(1+1/(4*pmin))/(1-mu),"third",-mpf(7)/2*k/(k+1),"sum",2.5+(1+1/(4*pmin))/(1-mu)-mpf(7)/2*k/(k+1)-mpf(2)/3)
# D3
print("1-cpsi/(2sqrt p)",1-cpsi/(2*sqrt(pmin)),"D3 sum",mpf('0.319921')/3+1/(3*(1-mu)*(1-cpsi/(2*sqrt(pmin))))-mpf(2)/3)
# (나) 0.168623
xi=mpf('0.2')
print("D1-D3 min",xi-k**(-mpf(2)/3)-3*c*sqrt(xi)*e0)
# (라)
kp=k
first=(mpf(3)/2*sqrt(xi)-mpf(1)/2/sqrt(xi)*kp**(-mpf(2)/3))/(2*c)
second=mpf(3)/4*kp**(-mpf(1)/3)*(1+(1-1/(xi*kp**(mpf(2)/3)))**(-mpf(1)/2))
third=(k+1)/(2*k)*(1-1/(xi*k**(mpf(2)/3)))**(-mpf(3)/2)/(xi**2*k**(mpf(2)/3))
print("U' terms",first,second,third,first-second-third)
# (마)
t1=(1+xi*e0)/(12*xi**2*k**(mpf(1)/3)); t2=3/(8*sqrt(xi)*k**(mpf(1)/3))
print("V' terms",t1,t2,t1+t2,-mpf(1)/2+t1+t2)
# jensen-H-ii
print("Lambda'(1)",mpf('2.75')+z12,"bracket p=1",-mpf(1)/6-mpf(2)/3*z12+zm12)
# table-lower-bound
jinf=lambda x: mpf(4)/3*c*x**(mpf(3)/2)
def s_(q): return mpf(4)/15*q**(mpf(5)/2)+mpf('0.385')*q**(mpf(3)/2)
def Cr(q,kk): return mpf(3)/2*c*(kk+q)**(mpf(3)/2)/(kk+1)**(mpf(7)/2)*s_(q)
print("jinf(0.2)",jinf(mpf('0.2')),"Cr(qmin,6600)",Cr(qmin,k),"exp",exp(-(jinf(mpf('0.2'))+Cr(qmin,k))), exp(-mpf('0.0477345')))
E02=2*c/sqrt(xi)*(1+xi*e0)
print("E(0.2,6600) bound",E02,"denom",mpf('0.168623')+2*c/sqrt(xi),"ratio",E02/(mpf('0.168623')+2*c/sqrt(xi)))
# envelope-code-monotone
print("2c sqrt(.0005)*.0005",2*c*sqrt(mpf('0.0005'))*mpf('0.0005'),"Ks",(2/mpf('0.0055'))**(mpf(3)/2),"s(2)",s_(mpf(2)),"Cr(2,6934.2)",Cr(mpf(2),mpf('6934.2')))
print("Cr(2e4,6.6e9)",Cr(mpf(2e4),mpf(6.6e9)))
# closed-form (가)
print("phi min",exp(-1/(12*qmin)),"rho1 max",mpf(3)/2*mpf('6.001')*e0)
xi6=mpf('6.001')
rho2=mpf(5)/8*(1+3/(4*pmin))*(1+xi6*e0)**(mpf(5)/2)*xi6**2*k**(-mpf(2)/3)
print("rho2",rho2,"V",exp(-1/(12*qmin))-mpf(3)/2*xi6*e0-rho2)
U=xi6**(mpf(3)/2)/(2*c)+(k+1)/k*(1-mu)**(-mpf(1)/2)
print("U",xi6**(mpf(3)/2)/(2*c),(k+1)/k*(1-mu)**(-mpf(1)/2),U,"q",mpf('0.3895139')/mpf('19.43183'))
# (나)
for xi_,q_,p_ in [(mpf('0.1'),mpf(2),mpf(1)),(mpf('2.1'),mpf('2.1')*k**(mpf(2)/3),mpf('2.1')*k**(mpf(2)/3)-1)]:
    br=(mpf('0.4')*xi_**(mpf(3)/2)+mpf('0.5775')*sqrt(xi_)*k**(-mpf(2)/3))*(1+xi_*e0)**(mpf(3)/2)
    print("xi",xi_,"q",q_,"terms",abs(zm12)/q_,p_**(-mpf(3)/2)/(12*q_),br,"total",abs(z12)-abs(zm12)/q_-p_**(-mpf(3)/2)/(12*q_)-br)
# (다)
q703=2*k**(mpf(2)/3); mu7=1/q703; p7=q703-1
print("q703",q703,"rho1' bound",mpf(1)/2*(sqrt(1-mu7)-(1+p7**(-mpf(1)/2))*e0/sqrt(2)),"theta1'",e0/sqrt(2)/(3*c),"0.5(1+1/4p)",mpf(1)/2*(1+1/(4*p7)))
print("V<1 coeff",mpf(1)/2-mpf(3)/2*mu7-mpf(3)/4*e0/sqrt(2))
xi2=mpf(2)
print("U>",1+(xi2**(mpf(3)/2)-sqrt(xi2)*k**(-mpf(2)/3))/(2*c)-mpf(3)/2*xi2*e0, "final",mpf('0.146751')-mpf('0.5316752')/mpf('4.37993'))
print("e^-jinf(2)",exp(-jinf(mpf(2))),"e^-jinf(2.1)",exp(-jinf(mpf('2.1'))))
# table-tolerance
print("rG",mpf('0.38951')*mpf('0.7202')/mpf('19.4319')**2,"Lambda' diff",mpf('2.75')+z12-mpf('0.85')*sqrt(2),"0.85c k/(k+1)",mpf('0.85')*c*k/(k+1),"0.169524 check",mpf('0.339049')/2)
print("coef1",mpf('0.020044')*mpf('0.169524')*sqrt(mpf('0.2')),"coef2",mpf('0.953386')*mpf('0.169524')*sqrt(mpf('0.0005')),"rG w",mpf('7.429e-4')*mpf('0.0005'))
# hazard
kk=mpf(6667)
print("3/32-3/4 k^-1/3+0.53/k",mpf(3)/32-mpf(3)/4*kk**(-mpf(1)/3)+mpf('0.53')/kk)
G=lambda z: mpf(3)/2*(1-z)-mpf('1.1935')*log(2/(1+z))-1/(1+z)+mpf(1)/2
print("G(0.0537)",G(mpf('0.0537')),"G(0.49)",G(mpf('0.49')),"log2/1.0537",log(2/mpf('1.0537')),"1/1.0537",1/mpf('1.0537'),"log2/1.49",log(2/mpf('1.49')),"1/1.49",1/mpf('1.49'),"3.2/k",mpf('3.2')/kk)
print("1.5-0.307(1-3/2k) at k=921",mpf(3)/2-mpf('0.307')*(1-mpf(3)/(2*921)))
# escape 9i>=5(n+1) at k=422
for kk2 in [421,422]:
    kk2=mpf(kk2); print(kk2, 9*(kk2+2)-5*(kk2+6*kk2**(mpf(2)/3)+1))
# q_max checks
k8=mpf(6668); qmax=int(6*k8**(mpf(2)/3))
print("qmax(6668)",qmax,"k-2399>=qmax+300:",k8-2399-qmax-300,"3k/4-2398-qmax",3*k8/4-2398-qmax)
# 6:old-7-13 window
print("3k q^-3/2",3*k/int(6*k**(mpf(2)/3))**mpf(1.5))
# Bor_<=(100)
from mpmath import factorial, e as E_
Bor=lambda m: m**(m-1)*exp(-m)/factorial(m)
print("Bor_<=(100)",sum(Bor(mpf(j)) for j in range(1,101)), "sqrt(2/pi)/10",sqrt(2/pi)/10)
print("(2pi)^-1/3",(2*pi)**(-mpf(1)/3),"(4c)^(2/3)",(4*c)**(mpf(2)/3))
print("6.6e9^(2/3)*0.005684",mpf(6.6e9)**(mpf(2)/3)*mpf('0.005684'))
