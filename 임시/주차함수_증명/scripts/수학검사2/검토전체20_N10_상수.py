# 10.4-10.6절의 수치 상수 검산
from mpmath import mp, mpf, quad, log, sqrt, exp, pi, e, floor, ceil, gamma, inf
mp.dps=30
def Bor(m): return exp(-m)*mpf(m)**(m-1)/gamma(m+1)
def u_fn(k): k=mpf(k); return 3/mpf('0.35')*(mpf('1.35')+1/k)*(mpf('0.65')-1/k)**(-1.5)*k**(-0.5)
def BdT(k,nu): k=mpf(k); nu=mpf(nu); return (k+nu)*u_fn(k)*(1/(k-1)+1/k)+3*(k+1)*(k-1)**(-1.5)
def sup(d,y): return min(1, mpf('1.15')*(y+d)/mpf(d)**1.5)
def q_(r): return 1+mpf('0.7501')*r/(1+r)
def DDLnat(k):
    k=mpf(k); dn=2*k**(mpf(2)/3)
    j2=quad(lambda r: sqrt((1+r)/r)*mpf('0.70836')*q_(r)**3,[0,1])
    j1=quad(lambda r: sqrt((1+r)/r)*mpf('0.70836')*q_(r)**3*(mpf('2.528571')-log(q_(r))+mpf('1.5')*log(r)),[0,1])
    en=-log(1-sqrt(k+1)/(mpf('0.485917')*k)); enp=mpf('2.26')/k+mpf('0.47')/(dn-1)
    gn=mpf('2.6047')*(mpf('2.53')+log(k)/2+en+mpf('1.5')/k)/k
    first=mpf('0.457143')*(2*pi)**(-0.5)*q_(dn/k)*sqrt(1+dn/k)*(dn+1)**3.5/k**3
    second=2*(2*pi)**(-0.5)*k**(-0.5)*(1+enp)*(j1+(log(k)/2+en)*j2+gn)+mpf('3.9')*(2*pi)**(-0.5)/k
    return first+second, j1, j2
print("j1,j2 =", DDLnat(6668)[1], DDLnat(6668)[2])
for k in (6668,8065,9551,9705): print("DDL^nat(%d)="%k, DDLnat(k)[0])
# old-8-23 misc
print("rho0(6667)=", floor(2*mpf(6667)**(mpf(2)/3))/6667, " q(rho0)=", q_(floor(2*mpf(6667)**(mpf(2)/3))/6667))
print("2^(7/2)=", mpf(2)**3.5, " 3*sqrt2*0.16696=", 3*sqrt(2)*mpf('0.16696'), " 2.5-ln2-ln0.485917=", mpf('2.5')-log(2)-log(mpf('0.485917')), " (sqrt2*0.16696)^(1/2)=", sqrt(sqrt(2)*mpf('0.16696')))
print("(0.3k-1)(0.3k)/(2(1.3k+1)) at 6667:", (mpf('0.3')*6667-1)*(mpf('0.3')*6667)/(2*(mpf('1.3')*6667+1)))
k=mpf(6667); print("1+1.5 ln k - that:", 1+1.5*log(k)-(mpf('0.3')*k-1)*(mpf('0.3')*k)/(2*(mpf('1.3')*k+1)))
print("j1+j2(0.5 ln 6667 -1)=", DDLnat(6668)[1]+DDLnat(6668)[2]*(log(mpf(6667))/2-1))
# sigma_0, iota_0
print("sigma0=", exp(-mpf('3.4964')/mpf('1.5')), " 2*iota0-6-0.1728*sqrt(sigma0)=", 2*mpf('3.4964')-6-mpf('0.1728')*sqrt(exp(-mpf('3.4964')/mpf('1.5'))))
# old-8-32
cR=sqrt(2*pi)/2*exp(mpf(1)/12); print("cR=",cR, " beta0 min=", cR*mpf('1.04')**1.5/sqrt(2), " g^e(1.0216)=", exp(-mpf('1.0216'))*(1+1.5*mpf('1.0216')), " g^e(beta0min)=", exp(-cR*mpf('1.04')**1.5/sqrt(2))*(1+1.5*cR*mpf('1.04')**1.5/sqrt(2)))
print("iota q0 max=", cR*mpf(2)**(mpf(2)/3)*mpf(6669)**(-mpf(1)/3), " beta2 range=", cR*mpf('1.04')**1.5, cR*2, " sqrt(1/2+1/562)=", sqrt(mpf('0.5')+mpf(1)/562))
ge_p=lambda t: exp(-t)*(mpf('0.5')-1.5*t); print("|g^e'| at 1.02, 2.73:", ge_p(mpf('1.02')), ge_p(mpf('2.73')), " 0.234*0.2916*1.444=", mpf('0.234')*mpf('0.2916')*mpf('1.444'))
# old-8-33 constants
cAb=lambda r: 2*sqrt(r)/(1-r)+2*log((1+sqrt(r))/(1-sqrt(r)))
print("2cAb(0.6)-4/sqrt(0.6)=", 2*cAb(mpf('0.6'))-4/sqrt(mpf('0.6')), " Sub max=", quad(lambda r:(1+r)*r**(-0.5)*(1-r)**(-2),[0,mpf('0.6')]))
# old-8-25 constants
print("(1.15*6666)^(2/3)=", (mpf('1.15')*6666)**(mpf(2)/3), " 2/sqrt(pi)=", 2/sqrt(pi))
E=lambda ups,q: 2*(2*pi)**(-0.5)*(mpf('0.25')*(1-1/(2*q))**(-1.5)+(1+ups+ups**2)*(1-ups)**(-0.5)*(1+ups)**(-1.5))
F=lambda ups: 2*(2*pi)**(-0.5)*(1+2*ups**2)*sqrt(1-ups**2)
print("E coef at 0.9,0.99,0.9999 (q=389):", E(mpf('0.9'),389),E(mpf('0.99'),389),E(mpf('0.9999'),389), " F(0.99)=",F(mpf('0.99')), " 2*0.7979*3*sqrt(0.19)=", 2*(2*pi)**(-0.5)*3*sqrt(mpf('0.19')))
print("1.1284+2.82/389=", mpf('1.1284')+mpf('2.82')/389, " 1.28/sqrt50=", mpf('1.28')/sqrt(50), " 2(2pi)^-1/2 sqrt(50/0.77)=", 2*(2*pi)**(-0.5)*sqrt(50/mpf('0.77')))
# old-8-35 / bulk
print("theta0=", (2*exp(-mpf('0.48'))-1)*exp(-mpf('0.48')), " (2pi)^-1/2 e^-1 2^1.5=", (2*pi)**(-0.5)/e*2**1.5, " 1/0.41508=", 1/mpf('0.41508'))
def ebar(k):
    k=mpf(k); xi=(sqrt(5*k*log(k))+2)/k
    return exp(3/(2*k))*(exp(sqrt(5*log(k)/k)+1/k)+mpf('2.40918')*k**(1.5-2.5/(1+xi)))
def abar(k): k=mpf(k); return 3*mpf('1.15')*(mpf('1.48')*k+2)/(mpf('0.48')*k+1)**1.5
def bbar(k): k=mpf(k); return 2*u_fn(k)*(2*k-1)/(k-1)+3*(k+1)*(k-1)**(-1.5)
def dbar(k): return mpf('72.217')/sqrt(mpf(k))
k=6668; print("bulk k0=6668: 4-ebar=",4-ebar(k)," abar=",abar(k)," bbar=",bbar(k)," DDL=",DDLnat(k)[0]," dbar=",dbar(k)," sum=",abar(k)+bbar(k)+DDLnat(k)[0]+dbar(k), " total with ebar=", abar(k)+bbar(k)+DDLnat(k)[0]+dbar(k)+ebar(k))
print("mhit/k at 6667:", ceil(sqrt(5*6667*log(mpf(6667))))/6667)
# bulk-majorants bracket at 0.48
r=mpf('0.48'); print("bracket=", r**(-0.5)-1+(1-sqrt(r))/3, " *132.32=", mpf('132.32')*(r**(-0.5)-1+(1-sqrt(r))/3))
# o_F for families 2,1b,1a
k=mpf(8065); print("fam2: 3s_up(2k^{2/3}+1)=",3*sup(2*k**(mpf(2)/3)+1,k+1)," BdT(k,0.48k)=",BdT(k,mpf('0.48')*k)," DDL=",DDLnat(8065)[0])
k=mpf(9551); xi2=2*k**(mpf(2)/3)/(k-1); print("fam1b: 3s_up(1.3k^{2/3}+1)=",3*sup(mpf('1.3')*k**(mpf(2)/3)+1,k+1)," theta part=",(2*exp(-xi2)-1)*exp(-xi2)," BdT(k,2k^{2/3})=",BdT(k,2*k**(mpf(2)/3))," DDL=",DDLnat(9551)[0])
k=mpf(9705); nup=mpf('1.3')*k**(mpf(2)/3); ec=3*nup**2/((k-1)*k)+mpf('4.8')*sqrt(nup)/k+nup**2/(2*(k-1)**2); print("fam1a: e^c=",ec," BdT=",BdT(k,nup)," DDL=",DDLnat(9705)[0])
# family thresholds
for k in (9704,9705,9550,9551,8064,8065):
    k=mpf(k); print(k, "20001-2k=",20001-2*k," 1.3k^{2/3}=",mpf('1.3')*k**(mpf(2)/3)," 2k^{2/3}=",2*k**(mpf(2)/3)," 0.48k=",mpf('0.48')*k)
# 10.3 table
print("20001/2.48=", mpf(20001)/mpf('2.48'))
# Stays^up(k;nubar)
def StaysUp(k,nub):
    k=mpf(k); mS=mpf('1.15'); tot=mpf(0)
    for y in (k-1,k):
        ab=(mS*(y+2*y**(mpf(2)/3)))**(mpf(2)/3); Flat=2*(ab-1)/(y+2-ab)
        z=mpf('0.6')+1/y; xiS=(nub+4)/(k-1)
        Sub=0 if xiS>=mpf('0.6') else (k-1)/k*quad(lambda r:(r-xiS)*(1+r)*r**(-1.5)*(1-r)**(-2),[xiS,mpf('0.6')])
        Ab=mS*(1+1/y)*(4*((mS*y)**(mpf(2)/3)-1)**(-0.5)+y**(-0.5)*(2*cAb(z)-4*z**(-0.5)-Sub))
        tot+=Flat+Ab
    Top=quad(lambda r: min(2,2+(nub+1)/k-r)*(1+r/3)*r**(-1.5),[mpf('0.6')-mpf('2.6')/k,1])
    return tot+2*mpf('16.54')*k**(-0.5)*Top
print("StaysUp(8065;0.48k)=",StaysUp(8065,mpf('0.48')*8065)," StaysUp(9551;2k^{2/3})=",StaysUp(9551,2*mpf(9551)**(mpf(2)/3))," StaysUp(9705;1.3k^{2/3})=",StaysUp(9705,mpf('1.3')*mpf(9705)**(mpf(2)/3)))
# Pi^two lower bound factor
k=mpf(6667); nu=mpf('0.48')*k; print("pi_two*k^1.5 at nu=0.48k:", Bor(k)*Bor(nu-1)/(e*Bor(k+nu))*k**1.5)
