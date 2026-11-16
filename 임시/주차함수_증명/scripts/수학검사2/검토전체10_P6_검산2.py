# P6 검산 2: 자기일관 상계 표(정리 self-consistent-S (다)), 따름정리 cor-S-prime의 세 값, polar-N·polar-W 수치, Riccati 반례, rho_2.
from fractions import Fraction as Fr
from math import factorial, ceil, sqrt, exp, log
import mpmath as mp
mp.mp.dps = 60
def F2m(f): return mp.mpf(f.numerator)/mp.mpf(f.denominator)
def a0(m): return Fr(1) if m==0 else Fr((m+1)**(m-1), factorial(m))
def egr(m): return a0(m+1)/a0(m)
print("== self-consistent-S table ==")
for (Ls,J,k0,yS) in [("267/100",25,501,Fr(13,100)),("27/10",70,1855,Fr(2,25)),("271/100",100,6098,Fr(11,200))]:
    L=Fr(Ls); j=0
    while egr(j+1)<L: j+=1
    jstar=j
    kR=max(2*jstar+2, ceil(L**(jstar+2)/a0(jstar+1)))
    Lm=F2m(L)
    E_und=sum(F2m(a0(J+i)/a0(J))*mp.e**(-i) for i in range(1,k0-jstar+1))
    Le=Lm/mp.e; E_inf=Le*(1-Le**k0)/(1-Le)
    RJ=max(1/(1+E_und),1/(1+E_inf))
    xb=[F2m(a0(v))*Lm**(-(v+1)) for v in range(J)]
    qu=[max(mp.mpf(0),1-sum(F2m(a0(jj))*Lm**(-(jj+1)) for jj in range(v))) for v in range(J)]
    Xi=sum(max(mp.mpf(0),xb[v]-RJ*qu[v]) for v in range(J))
    xk0=(mp.mpf(k0)/(k0+1))**(k0-1)
    Xik=sum(max(mp.mpf(0),F2m(a0(v))*xk0*Lm**(-v)-RJ*qu[v]) for v in range(J))
    A0=xk0+Xik/(Lm*(1-Xi)); B0=RJ*(1+Xik/(1-Xi))
    xi=mp.mpf(1)/k0; y=F2m(yS)
    g=(y-xi)*(y-2*xi-xi**2)-(1+xi)**2*(A0*xi+B0*y)
    vert=(3*xi+xi**2)/2+(1+xi)**2*B0/2
    print(f"L={Ls} J={J} k0={k0}: j*={jstar} kR={kR} RJ={mp.nstr(RJ,10)} Xi={mp.nstr(Xi,8)} Xik={mp.nstr(Xik,8)} A0={mp.nstr(A0,7)} B0={mp.nstr(B0,7)} g(exact A0,B0)={mp.nstr(g,5)} vert={mp.nstr(vert,5)} <= y: {vert<=y}")
    # with table rounded values
    A0t,B0t={"267/100":(1.4708,0.098505),"27/10":(2.5335,0.060259),"271/100":(2.7354,0.0422)}[Ls]
    gt=(y-xi)*(y-2*xi-xi**2)-(1+xi)**2*(mp.mpf(A0t)*xi+mp.mpf(B0t)*y)
    print("   g(table A0,B0)=",mp.nstr(gt,5), " x_k0=",mp.nstr(xk0,8))
print("== polar-N numerics ==")
k=2001
print("2/sqrt(2001)=",2/sqrt(2001), " e^{-1+2/2002}=",exp(-1+2/2002), " 0.75/sqrt(k)=",0.75/sqrt(k), " 2k^1.5+1=",2*k**1.5+1, " 0.3476k^2=",0.3476*k*k)
print("x_2001=",(2001/2002)**2000, " 0.955*0.991*0.3678=",0.955*0.991*0.3678, " e^-0.0448=",exp(-0.0448))
y=0.0448; print("y^2/(12(1-y^2))=",y*y/(12*(1-y*y)))
print("== polar-W k>=1e7 constants ==")
k=10**7
print("8(1+0.91/sqrt k)^3=",8*(1+0.91/sqrt(k))**3, " 8.344/sqrt(k)=",8.344/sqrt(k), " 0.001k+1.001>=2sqrt k:",0.001*k+1.001>=2*sqrt(k))
print("== riccati counterexample (k,z,n)=(3,1,2) ==")
import sympy as sp
X=sp.symbols('x')
Q2=2*X+X**2/2
Ex=sp.series(sp.exp(-Q2),X,0,5).removeO()
IEx=sp.integrate(Ex,(X,0,X))
Delta=1-3*IEx
Ak=sp.series(Ex/Delta,X,0,4).removeO()
O1=X
rhs=Ak*O1+3*Ex/Delta**2*sp.integrate(O1*Ex,(X,0,X))
print("A_{n,2} coeffs*n!:",[sp.series(Ex/Delta,X,0,4).removeO().coeff(X,n)*factorial(n) for n in range(4)])
print("rhs coeff x^2 * 2! =", sp.simplify(sp.series(rhs,X,0,3).removeO().coeff(X,2)*2))
print("== A_{n,1} (Fubini?) ==")
from itertools import permutations
def caps(sig):
    n=len(sig); h=[0]*n
    for i in range(n):
        j=i-1
        while j>=0 and sig[j]<sig[i]: j-=1
        h[i]=i-j
    return h
def A(n,l):
    if n==0: return 1
    s=0
    for sig in permutations(range(1,n+1)):
        p=1
        for x in caps(sig): p*=min(x,l+1)
        s+=p
    return s
print([A(n,1) for n in range(0,7)], "Fubini: 1,1,3,13,75,541,4683")
print("== old-6-8 k=2: n^sharp_2=8; check d_{n,2}>0 for n=8..9 ==")
print([A(n,2)-2*A(n,1)+A(n,0) for n in range(5,10)])
