# K5: 6.6 상수 검산
import math, os
from math import sqrt, exp, log, e, pi
out=[]
def Ren(j): return exp(j*log(j)-j-math.lgamma(j+1))
Psi14=sum(Ren(j) for j in range(1,15)); out.append(f"Psi(14)={Psi14:.6f} Psi14/(2e)={Psi14/(2*e):.6f}")
def Bor(n): return exp(-n+(n-1)*log(n)-math.lgamma(n+1))
k=3131
f1=sqrt(2*pi)*(k+15)**1.5*Bor(k+15); f2=(k/(k+15))**1.5; f3=(k+1)/(k+14)
out.append(f"first factor={f1:.6f} f2={f2:.6f} f3={f3:.6f} prod={f1*f2*f3:.6f} x Psi/(2e)={f1*f2*f3*Psi14/(2*e):.6f}")
ups=lambda k:0.5+2.5/k+1/(4*k*k); gW=2*exp(0.0031)/e
out.append(f"gamma_W={gW:.7f} ups*gW(3131)={ups(3131)*gW:.6f}; diff={f1*f2*f3*Psi14/(2*e)-ups(3131)*gW:.5f}")
def u(k): return 3/0.35*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5
def dd(k): return gW*ups(k)+u(k)/(e*2**1.5)
out.append(f"d(3131)={dd(3131):.7f} (parts {gW*ups(3131):.6f},{u(3131)/(e*2**1.5):.6f}); d(10001)={dd(10001):.7f}")
out.append(f"E3 bound: u(3131)/(e 2^1.5)={u(3131)/(e*2**1.5):.5f}; 0.0648*e*2^1.5={0.0648*e*2**1.5:.5f}")
def Low(k,rho):
    eps=k**(-1/3); c=1/sqrt(2*pi)
    A=c*k**(1/3)*(2*sqrt(rho)-2.218*eps)/(1+rho*eps)
    return A*exp(-1/(12*(k+1)))*exp(-rho**2*(1+rho*eps)**1.5*exp(1/(4*(k+1)))/(c*(2*sqrt(rho)-2.218*eps)))
out.append(f"Low(10001,1.4)={Low(10001,1.4):.5f}; Low(3131,0.75)={Low(3131,0.75):.5f}")
k=10001; out.append(f"Obar(10001,1.4)={dd(k)*exp(1+1/(12*k))*(1+1.4*k**(-1/3)+1/k)**1.5:.5f}")
k=3131; out.append(f"Obar(3131,0.75)={dd(k)*exp(1+1/(12*k))*(1+0.75*k**(-1/3)+1/k)**1.5:.5f}")
wp=lambda n:1.99+0.59963*(n+1)**(2/3)+1.24847*(n+1)**(1/3)
k=3131; uu=k**(1/3); out.append(f"u=k^(1/3)={uu:.4f}; quad={0.15037*uu**2-1.54829*uu-1.3314:.3f}; (6.49) diff={0.75*k**(2/3)-(wp(k+0.75*k**(2/3))-1):.3f}; root={(1.54829+sqrt(1.54829**2+4*0.15037*1.3314))/(2*0.15037):.3f}")
out.append(f"wp'(1)={2/3*0.59963*2**(-1/3)+1/3*1.24847*2**(-2/3):.4f}")
# (6.50) check at k=3131
k=3131
for d in (1,13,14):
    L=(k-1)*(e*Ren(d+1)-60*(d+1)/(k+d)); R=2*(1+sum(e*Ren(r+1)+60*(r+1)/(k+d) for r in range(1,d)))
    out.append(f"(6.50) d={d}: L={L:.2f} R={R:.2f}")
# prop-W (나) constants
out.append(f"(e+0.75)/3131={(e+0.75)/3131:.6f}; 0.5006*(3.469^2)/3131={0.5006*3.469**2/3131:.6f}; 3.51/3131={3.51/3131:.6f}")
mx=max((1-D)*(1+(e-2)*D)/(2-D) for D in [i/10000 for i in range(10001)]); out.append(f"max (1-D)(1+(e-2)D)/(2-D)={mx:.5f}; *(1+7/3131)={mx*(1+7/3131):.5f}")
# theorem D numerics
m=701; out.append(f"m=701: m^(2/3)/2/m={m**(2/3)/2/m:.4f}; 0.9437m={0.9437*m:.1f}; kfrak={ (m**(2/3)/2)**1.5/(0.9437*m):.4f}; N={exp(-1/(12*661)):.6f}; rhs={0.025*m**(-2/3):.6f}; upper rhs={1.1212*m**(-2/3)+1.3036*m**(-1/3):.5f}")
# upsilon_k and m*
out.append(f"ups(3131)={ups(3131):.8f}")
open(os.path.join(os.path.dirname(__file__),'검토전체17_K5_66.out'),'w',encoding='utf-8').write("\n".join(out))
