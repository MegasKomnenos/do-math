# 검토전체18 L8: 8장 수치 상수 재계산 (python -I 로 실행)
import math, sys
from math import sqrt, exp, log, pi, lgamma, floor, ceil

c = (2*pi)**-0.5
z12, zm12, z32 = -1.4603545088095868, -0.2078862249773545, 2.6123753486854883
cpsi = -z12 + z32/12
out = []
def P(*a): out.append(" ".join(str(x) for x in a))

# --- 8.2 수치 블록
k0 = 6600.0
e0 = k0**(-1/3); qmin = 0.2*k0**(2/3); pmin = qmin-1; mu = 1/qmin
P("eps0", e0, "qmin", qmin, "pmin", pmin, "sqrt pmin", sqrt(pmin), "mu", mu)
P("xi*eps max", 6.001*e0, "k^-2/3", k0**(-2/3), "(1-mu)^-1/2", (1-mu)**-0.5, "(1-mu)^-3/2", (1-mu)**-1.5)
# escape-y-monotone (나)
P("(na) 0.2-k^-2/3-3c sqrt(.2) eps =", 0.2-0.00284209-3*c*sqrt(0.2)*0.0533113, "exact", 0.2-k0**(-2/3)-3*c*sqrt(0.2)*e0)
# (라) U' 세 항 at xi=.2,k=k'=6600
xi=0.2; k=k0
t1=(1.5*sqrt(xi)-0.5*xi**-0.5*k**(-2/3))/(2*c)
t2=0.75*k**(-1/3)*(1+(1-1/(xi*k**(2/3)))**-0.5)
t3=(k+1)/(2*k)*(1-1/(xi*k**(2/3)))**-1.5/(xi*xi*k**(2/3))
P("(ra) t1",t1,"t2",t2,"t3",t3,"sum",t1-t2-t3)
# (마)
a1=(1+xi*e0)/(12*xi*xi*k**(1/3)); a2=3/(8*sqrt(xi)*k**(1/3))
P("(ma) a1",a1,"a2",a2,"sum",a1+a2,"-0.5+",-0.5+a1+a2)
# closed-form (가)
P("(cf-ga) phi>=",exp(-1/(12*qmin)),"rho1<=",1.5*6.001*e0,"rho1 via 0.0533113",1.5*6.001*0.0533113)
xe=6.001*e0
rho2=(5/8)*(1+3/(4*pmin))*(1+xe)**2.5*6.001**2*k0**(-2/3)
P("rho2<=",rho2,"V>=",exp(-1/(12*qmin))-1.5*6.001*e0-rho2)
th1=6.001**1.5/(2*c); ups=(k0+1)/k0*(1-mu)**-0.5
P("theta1",th1,"upsilon",ups,"U<=",th1+ups,"q>=",(exp(-1/(12*qmin))-1.5*6.001*e0-rho2)/(th1+ups))
# table-lower-bound (가) seam
jinf=lambda x: (4/3)*c*x**1.5
def s_q(q): return (4/15)*q**2.5+0.385*q**1.5
def Cr(q,k): return 1.5*c*(k+q)**1.5/(k+1)**3.5*s_q(q)
P("jinf(0.2)",jinf(0.2),"Cr(qmin,6600)",Cr(qmin,k0),"sum",jinf(0.2)+Cr(qmin,k0),"exp(-)",exp(-(jinf(0.2)+Cr(qmin,k0))), "exp(-0.0477345)",exp(-0.0477345))
E0=2*c*0.2**-0.5
P("E(0.2,6600)<=",E0*(1+0.2*e0),"den>=",0.168623+E0,"ratio",E0*(1+0.2*e0)/(0.168623+E0))
# pieces-k-monotone R2, D3 numbers
P("R2: (1+1/(4pmin))/(1-mu)",(1+1/(4*pmin))/(1-mu),"3.5*k/(k+1)",3.5*k0/(k0+1),"sum",2.5+(1+1/(4*pmin))/(1-mu)-3.5*k0/(k0+1)-2/3)
P("D3: 1-mu",1-mu,"1-cpsi/(2sqrt p)",1-cpsi/(2*sqrt(pmin)),"cpsi",cpsi, "k dlogD3 <", 0.319921/3+1/(3*(1-mu)*(1-cpsi/(2*sqrt(pmin))))-2/3)
# explicit-bounds (라) constants
P("c_psi >= 35/24+1/12 =",35/24+1/12," Psi_low(1) factor 59/24-cpsi",59/24-cpsi)
# jensen-H-ii (가)
P("Lambda'(1)=2.75+z12",2.75+z12," bracket p=1:",-1/6-(2/3)*z12+zm12)
# closed-form (나)
def brk(xi,k): return (0.4*xi**1.5+0.5775*xi**0.5*k**(-2/3))*(1+xi*k**(-1/3))**1.5
P("(cf-na) xi<=.1:",1.46035-0.20789/2-1/24-brk(0.1,k0),"bracket",brk(0.1,k0))
q1=0.1*k0**(2/3); P("q at xi=.1",q1,"p",q1-1,"|zm|/q",0.20789/q1,"p^-1.5/(12q)",(q1-1)**-1.5/(12*q1),"bracket(2.1)",brk(2.1,k0),"val",1.46035-0.20789/q1-(q1-1)**-1.5/(12*q1)-brk(2.1,k0))
# closed-form (다)
q2=2*k0**(2/3); p2=q2-1; mu2=1/q2
P("(cf-da) q>=",q2," sqrt(1-mu)-(1+p^-1/2)k^-1/3 xi^-1/2 >=",sqrt(1-mu2)-(1+p2**-0.5)*e0/sqrt(2)," half",0.5*(sqrt(1-mu2)-(1+p2**-0.5)*e0/sqrt(2)))
P(" dtheta1 coef",(e0/sqrt(2))/(3*c)," dtheta3 coef",0.5*(1+1/(4*p2))," 0.5-1.5mu-0.75 k^-1/3 xi^-1/2",0.5-1.5*mu2-0.75*e0/sqrt(2))
P(" U(2,6600)>",1+(2**1.5-sqrt(2)*k0**(-2/3))/(2*c)-1.5*2*e0," 0.146751-0.5316752/4.37993",0.146751-0.5316752/4.37993)
# table-tolerance
P("(tt) 0.38951*0.7202/19.4319^2",0.38951*0.7202/19.4319**2," 0.85 c k/(k+1)",0.85*c*k0/(k0+1)," 0.020044*0.169524*sqrt(.2)",0.020044*0.169524*sqrt(0.2)," 0.953386*0.169524*sqrt(.0005)",0.953386*0.169524*sqrt(0.0005))
P(" Lambda'(1)-0.85sqrt2",2.75+z12-0.85*sqrt(2))
# envelope-code-monotone
P("(ecm) 2c sqrt(.0005)*.0005",2*c*sqrt(0.0005)*0.0005," Ks(0.0055)",(2/0.0055)**1.5," s(2)",s_q(2)," Cr(2,6934.2)",Cr(2,(2/0.0055)**1.5)," Cr(2e4,6.6e9)",Cr(2e4,6.6e9), " 2/6600^(2/3)", 2/k0**(2/3))
# hazard-H1
G=lambda z: 1.5*(1-z)-1.1935*log(2/(1+z))-1/(1+z)+0.5
P("(hz) G(.0537)",G(0.0537),"G(.49)",G(0.49),"log(2/1.0537)",log(2/1.0537),"1/1.0537",1/1.0537,"log(2/1.49)",log(2/1.49),"1/1.49",1/1.49)
k=6667; qmax=floor(6*k**(2/3)); qfb=floor((3*(k-1)/4-qmax-3)/8)
P(" k=6667 qmax",qmax,"qfb",qfb,"(qfb+2)/k",(qfb+2)/k," 3/32-3/4 k^-1/3",3/32-0.75*k**(-1/3), " 3.2/k",3.2/k, " 1.5-0.307(1-1.5/k)",1.5-0.307*(1-1.5/k))
# old-6-29 non-overlap at k=6668
k=6668; qmax=floor(6*k**(2/3)); P("k=6668 qmax",qmax,"k-2399>=qmax+300?",k-2399,qmax+300," k-2398-qmax>=k/4?",k-2398-qmax,k/4, " 6k^(2/3)<=k+3", 6*k**(2/3), " qfb", floor((3*(k-1)/4-qmax-3)/8), " 3.6k^(2/3)", 3.6*k**(2/3), " (k/(k-1))^(2/3)", (k/(k-1))**(2/3))
# closed-form seams: q_{6600,6600}(xi)
def Psilow(r):
    return 0.0 if r<1 else c*(2*sqrt(r)-cpsi+0.5/sqrt(r)-r**-1.5/24)
def pieces(xi,k):
    q=xi*k**(2/3); p=q-1; n=k+q; kk=k+1; eps=k**(-1/3)
    E=2*c*exp(-1/(12*q))*xi**-0.5*(1+xi*eps)
    R1=1.5*c*(2*sqrt(p)-1)*k**(-2/3)
    H=(2/3)*p**1.5+0.5*sqrt(p)+zm12+p**-0.5/24
    R2=(15/8)*c*n**2.5*H/(kk**3.5*k**(2/3))
    D1=p/k**(2/3); D2=kk*sqrt(2/pi)*p**-0.5*k**(-2/3); D3=1.5*kk*Psilow(p)/((n+1)*k**(2/3))
    return (E-R1-R2)/(D1+D2-D3)
P("q6600(2)",pieces(2,k0),"e^-jinf(2)",exp(-jinf(2)),"q6600(2.1)",pieces(2.1,k0),"e^-jinf(2.1)",exp(-jinf(2.1)))
P("q6600(0.2)",pieces(0.2,k0),"q6600(6)",pieces(6,k0),"e^-jinf(.2)",exp(-jinf(0.2)))
def scf(xi):
    v=[]
    if xi<=2.1: v.append(exp(-jinf(xi)))
    if xi>=2: v.append(pieces(xi,k0))
    return max(v)

# --- 창 합의 극한 0.744 검산: Omega 근사 (K 격자 재귀, 원천 T̂≈s^cf)
def logBor(m): return (m-1)*log(m)-m-lgamma(m+1)
K=20000; K23=K**(2/3); imax=int(6*K23)+1
Bor=[0.0]+[exp(logBor(m)) for m in range(1,imax+1)]
That=[scf(max(i/K23,1e-9)) for i in range(imax+1)]
r=[0.0]*(imax+1); Psi=[0.0]*(imax+1)
for i in range(1,imax+1): Psi[i]=Psi[i-1]+i*Bor[i]
try:
    import numpy as np
    B=np.array(Bor); T=np.array(That); R=np.zeros(imax+1)
    for i in range(1,imax+1):
        j=np.arange(1,i+1)
        R[i]=K/(K+i)*np.dot(B[1:i+1],T[i-j]+R[i-j])
    r=list(R)
except Exception as ex:
    P("numpy fail",ex)
    for i in range(1,imax+1):
        s=0.0
        for j in range(1,i+1): s+=Bor[j]*(That[i-j]+r[i-j])
        r[i]=K/(K+i)*s
def g_safe(xi):
    v=xi-1
    e=0.0 if v<=-0.1 else ((v+0.1)**2/0.4 if v<0.1 else v)
    return min(1.0,0.04+0.12*e)
w=[1.0]+[r[i]/Psi[i] for i in range(1,imax+1)]
Om=[(1-g_safe(i/K23))*w[i] for i in range(imax+1)]
# 누적 최솟값
for i in range(1,imax+1): Om[i]=min(Om[i],Om[i-1])
xs=[i/K23 for i in range(imax+1)]
P("Omega approx at xi=0,0.5,1,2,3,4,5,6:",[round(Om[min(int(x*K23),imax)],4) for x in [0,0.5,1,2,3,4,5,6]])
P("w (no safety) at 1,2,4,6:",[round(w[min(int(x*K23),imax)],4) for x in [1,2,4,6]])
integ=sum(Om[i]*sqrt(2*xs[i]/pi) for i in range(imax+1) if xs[i]<=6)/K23
P("int_0^6 Omega sqrt(2 xi/pi) dxi approx =",integ)
P("int_0^6 sqrt(2xi/pi) dxi =",sqrt(2/pi)*(2/3)*6**1.5)

# --- 정확한 창 수준 질량 합 Σ_q c_{k+q}(k) (k 보통 크기)
def exact_window(k):
    qmax=floor(6*k**(2/3)); y=k+1
    LB={m:logBor(m) for m in range(1,2*k+8)}
    def pi_N(N,m): return exp(LB[m]+LB[N+1-m]-LB[N+1])
    # s_N(y) for N<=2y+1 via chain recursion
    s={}
    for N in range(0,y+1): s[N]=1.0
    for N in range(y+1,k+qmax+1):
        tot=0.0; pis=0.0
        for m in range(y+1,N+1):
            pm=pi_N(N,m); pis+=pm; tot+=pm*y/m*s[m-1]
        s[N]=(1-pis)+tot
    # R_q via (8.4)
    R=[0.0]*(qmax+1)
    for q in range(1,qmax+1):
        tot=0.0
        for j in range(1,q+1):
            tot+=pi_N(k+q,k+j)*k/(k+j)*(s[k+j-1]+R[j-1])
        R[q]=tot
    # s_{k+qmax}(k): chain recursion with y=k
    s2={N:1.0 for N in range(0,k+1)}
    for N in range(k+1,k+qmax+1):
        tot=0.0; pis=0.0
        for m in range(k+1,N+1):
            pm=pi_N(N,m); pis+=pm; tot+=pm*k/m*s2[m-1]
        s2[N]=(1-pis)+tot
    PsiQ=[0.0]*(qmax+1)
    for q in range(1,qmax+1): PsiQ[q]=PsiQ[q-1]+q*exp(LB[q])
    return qmax, sum(R)/k, 1-s2[k+qmax], sum(PsiQ)/k, min(R[q]/PsiQ[q] for q in range(1,qmax+1)), R[qmax]/PsiQ[qmax]
for k in (300,1000):
    P("k",k,"(qmax, sum c, 1-s_{k+qmax}(k), sum Psi/k, min R/Psi, R/Psi at qmax):",exact_window(k))
open(sys.argv[1],"w",encoding="utf-8").write("\n".join(out)+"\n")
