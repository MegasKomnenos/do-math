from fractions import Fraction as F
import math
# column-lemma constants
print("col:", (40/41)*(10/17)**2.1 > 0.3, 10**21*400**10 > 17**21*123**10, float(F(10**21*400**10, 17**21*123**10)))
for k in (41,):
    ok=-2*math.log(1-1/k)/math.log(1+1/k); print("o_k",ok, 2*(k+1)/(k-1), 1-2.1*(10/17)**3)
# a°_m = (m+1)^(m-1)/m!
def a0(m): return F(1) if m==0 else F((m+1)**(m-1), math.factorial(m))
def free_ratio(m): return a0(m+1)/a0(m)  # e^{g(m+1)}
def jstar(L):
    m=0
    while free_ratio(m)<L: m+=1
    return m-1
for L,J,k0 in ((F(267,100),25,501),(F(27,10),70,1855),(F(271,100),100,6098)):
    js=jstar(L)
    kR=max(2*js+2, math.ceil(L**(js+2)/a0(js+1)))
    # E_J lower, E_inf
    la=lambda m: 0.0 if m==0 else (m-1)*math.log(m+1)-math.lgamma(m+1)
    EJ=sum(math.exp(la(J+i)-la(J)-i) for i in range(1,k0-js+1))
    r=float(L)/math.e
    Einf=r*(1-r**k0)/(1-r)
    R=max(1/(1+EJ),1/(1+Einf))
    xk=lambda k:(k/(k+1))**(k-1)
    Lf=float(L)
    def qlow(kap): return max(0.0,1-sum(float(a0(j))*Lf**-(j+1) for j in range(kap)))
    Xi=sum(max(0.0,float(a0(kap))*Lf**-(kap+1)-R*qlow(kap)) for kap in range(J))
    Xik=sum(max(0.0,float(a0(kap))*xk(k0)*Lf**-kap-R*qlow(kap)) for kap in range(J))
    A0=xk(k0)+Xik/(Lf*(1-Xi)); B0=R*(1+Xik/(1-Xi))
    print(f"L={L} J={J} k0={k0}: j*={js} kR={kR} R={R:.6f} Xi={Xi:.6f} Xi(k0)={Xik:.6f} A0={A0:.5f} B0={B0:.6f}")
    y={501:0.13,1855:0.08,6098:0.055}[k0]; xi=1/k0
    g=(y-xi)*(y-2*xi-xi*xi)-(1+xi)**2*(A0*xi+B0*y)
    nv=(3*xi+xi*xi)/2+(1+xi)**2*B0/2
    print("   g_S/k^4=",g," n_v/k^2=",nv, " y k^2-2k-1>0:", y*k0*k0-2*k0-1>0)
# t_k check for a few k
def tk(k):
    j=0
    while not ((k+1)**j*k**(j+1)+(k-1)**(2*j+1) >= 2*k**(2*j+1)): j+=1
    return j
for k in (2,3,10,100,501,2000): print("k",k,"t_k",tk(k),"n#",k+(k+1)*tk(k))
