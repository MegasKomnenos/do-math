# I8: 8장 8.2절·8.4절의 수치 상수 재계산 (binary64; 방향 반올림 아님, 자릿수 대조용)
import math
from math import sqrt, exp, log, pi
c=(2*pi)**-0.5
z12=-1.46036; z12u=-1.46035   # z_{1/2} in [-1.46036,-1.46035]
zm12=-0.20789; zm12u=-0.20788 # z_{-1/2}
z32=2.61237; z32u=2.61238
cPsi_up=-z12+z32u/12; cPsi_lo=-z12u+z32/12
print("cPsi in [%.6f,%.6f]"%(cPsi_lo,cPsi_up))
k0=6600.0
k23=k0**(2/3); k13=k0**(1/3)
qmin=0.2*k23; pmin=qmin-1
print("q_min",qmin,"p_min",pmin,"sqrt p_min",sqrt(pmin))
mu=1/qmin; print("mu",mu,"(1-mu)^-1/2",(1-mu)**-0.5,"(1-mu)^-3/2",(1-mu)**-1.5)
xe=6.001/k13; print("xi*eps max",xe,"eps0",1/k13,"k^-2/3",1/k23)
# pieces-k-monotone E
print("E bracket: lhs<=",(1/k13)*(1+xe),"rhs>=",6*0.04)
# R2
print("R2 second term",(1+1/(4*pmin))/(1-mu),"third",-3.5*k0/(k0+1),"sum",2.5+(1+1/(4*pmin))/(1-mu)-3.5*k0/(k0+1)-2/3)
# D3
print("D3: 1-mu",1-mu,"1-c/(2sqrt p)",1-cPsi_up/(2*sqrt(pmin)),"total",xe/3+1/(3*(1-mu)*(1-cPsi_up/(2*sqrt(pmin))))-2/3)
# escape-y-monotone (나)
print("(na) min",0.2-k0**(-2/3)-3*c*sqrt(0.2)/k13)
# (라)
xi=0.2;k=k0;kp=k0
t1=(1.5*sqrt(xi)-0.5*xi**-0.5*kp**(-2/3))/(2*c)
t2=0.75*kp**(-1/3)*(1+(1-1/(xi*kp**(2/3)))**-0.5)
t3=(k+1)/(2*k)*(1-1/(xi*k**(2/3)))**-1.5/(xi**2*k**(2/3))
print("(ra)",t1,t2,t3,t1-t2-t3)
# (마)
a=(1+xi/k13)/(12*xi**2*k13); b=3/(8*sqrt(xi)*k13)
print("(ma)",a,b,a+b,-0.5+a+b)
# table-lower-bound (가)
jinf=lambda x: (4/3)*c*x**1.5
def s_(q): return (4/15)*q**2.5+0.385*q**1.5
def Cr(q,k): return 1.5*c*(k+q)**1.5/(k+1)**3.5*s_(q)
print("j_inf(0.2)",jinf(0.2),"Cr(qmin,6600)",Cr(qmin,k0),"exp",exp(-(jinf(0.2)+Cr(qmin,k0))),exp(-0.0477345))
E0=lambda x: 2*c/sqrt(x)
num=E0(0.2)*(1+0.2/k13); den=0.168623+E0(0.2); print("seam q",num,den,num/den)
# envelope-code-monotone
print("8.92e-6:",2*c*sqrt(0.0005)*0.0005,"Ks(0.0055)",(2/0.0055)**1.5,"s(2)",s_(2),"Cr(2,6934.2)",Cr(2,6934.2),"Cr(2e4,6.6e9)",Cr(2e4,6.6e9))
# closed-form (가)
print("phi>=",exp(-1/(12*qmin)),"rho1<=",1.5*xe,"rho2<=",0.625*(1+3/(4*pmin))*(1+xe)**2.5*6.001**2/k23)
print("theta1(6.001)",6.001**1.5/(2*c),"upsilon",(k0+1)/k0*(1-mu)**-0.5, "V",exp(-1/(12*qmin))-1.5*xe-0.625*(1+3/(4*pmin))*(1+xe)**2.5*6.001**2/k23)
V=0.3895139;U=19.43183;print("q>=",V/U)
# (나)
br=lambda x,k: (0.4*x**1.5+0.5775*sqrt(x)*k**(-2/3))*(1+x/k**(1/3))**1.5
print("(na) xi<=0.1:",1.46035-0.20789/2-1/24-br(0.1,k0), "br",br(0.1,k0))
q1=0.1*k23;p1=q1-1
print("(na) 0.1..2.1:",q1,p1,0.20789/q1,p1**-1.5/(12*q1),br(2.1,k0),1.46035-0.20789/q1-p1**-1.5/(12*q1)-br(2.1,k0))
# (다)
q2=2*k23;p2=q2-1;mu2=1/q2
print("q2",q2,"0.480085:",0.5*(sqrt(1-mu2)-(1+p2**-0.5)/(k13*sqrt(2))))
print("0.0314973:",(1/(k13*sqrt(2)))/(3*c),"0.5001779:",0.5*(1+1/(4*p2)))
print("0.46959:",0.5-1.5*mu2-0.75/(k13*sqrt(2)))
print("4.37993:",1+(2**1.5-sqrt(2)/k23)/(2*c)-1.5*2/k13)
print("0.02536:",0.146751-0.5316752/4.37993)
# seams: q_{6600,6600}(xi)
def pieces(xi,k):
    q=xi*k**(2/3);p=q-1;n=k+q;kk=k+1
    E=2*c*exp(-1/(12*q))*xi**-0.5*(1+xi*k**(-1/3))
    R1=1.5*c*(2*sqrt(p)-1)*k**(-2/3)
    H=(2/3)*p**1.5+0.5*sqrt(p)+zm12+1/(24*sqrt(p))  # z_{-1/2} choose lower? use both ends later
    R2=(15/8)*c*n**2.5*H/(kk**3.5*k**(2/3))
    D1=p/k**(2/3)
    D2=kk*sqrt(2/pi)*p**-0.5*k**(-2/3)
    Psil=c*(2*sqrt(p)-cPsi_up+1/(2*sqrt(p))-p**-1.5/24)
    D3=1.5*kk*Psil/((n+1)*k**(2/3))
    return E,R1,R2,D1,D2,D3
for xi in (2.0,2.1):
    E,R1,R2,D1,D2,D3=pieces(xi,k0)
    print("q6600(%.1f)=%.6f  exp(-jinf)=%.6f"%(xi,(E-R1-R2)/(D1+D2-D3),exp(-jinf(xi))))
# table-tolerance
print("rG",0.38951*0.7202/19.4319**2, "0.339049",0.85*c*k0/(k0+1), "1.51e-3",0.020044*0.169524*sqrt(0.2),"3.61e-3",0.953386*0.169524*sqrt(0.000499),"3.713e-7",7.429e-4*0.0004999)
# jensen-H-ii
print("Lambda'(1)",2.75+z12,"bracket p=1",-1/6-(2/3)*z12u+zm12, "0.85 diff",2.75+z12-0.85*sqrt(2))
# hazard-H1
G=lambda z: 1.5*(1-z)-1.1935*log(2/(1+z))-1/(1+z)+0.5
k=6667.0
print("zlow",3/32-0.75*k**(-1/3)+0.53/k,"G(0.0537)",G(0.0537),"G(0.571)",G(0.571),"3.2/k",3.2/k, "1.5-0.307(1-3/2k)",1.5-0.307*(1-1.5/k))
# old-6-29 (2) at k=6668
k=6668;qmax=math.floor(6*k**(2/3));print("qmax(6668)",qmax,"k-2399>=qmax+300:",k-2399,qmax+300,"3k/4>=2398+qmax:",0.75*k,2398+qmax)
# 1.5절/8.2 misc
print("(k/(k-1))^{2/3} at 6668",(6668/6667)**(2/3))
# positivity of Psi^low at 1
print("Psi^low(1)",c*(2-cPsi_up+0.5-1/24))
print("hazard front factor at nu=103,k=6667",1-0.798/sqrt(104)-0.81/sqrt(6667))
