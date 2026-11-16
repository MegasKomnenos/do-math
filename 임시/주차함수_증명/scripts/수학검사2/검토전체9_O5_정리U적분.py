# numerical re-evaluation of the four integrals J_I(1), Y_I(1), J_X(Gamma*), Y_X(Gamma*) of theorem-U (plain quadrature, not rigorous)
from math import *
cc=1/sqrt(2*pi); V0=1/3130
def FI(L): return exp(1.5*L)*L*(1+0.75*L)
def FX(L): return exp(1.5*L)*L
def Lfun(F,sig):
    if sig<1e-12: return 1.0
    return F(-log(1-sig))/sig
def gl(n):
    # Gauss-Legendre nodes/weights on [-1,1]
    import numpy as np
    x,w=np.polynomial.legendre.leggauss(n); return x,w
X,W=gl(200)
def I_F(F,T):
    # int_0^1 u^{-1/2} L(T u) du ; substitute u=v^2: 2 int_0^1 L(T v^2) dv
    tot=0.0
    for xi,wi in zip(X,W):
        v=0.5*(xi+1); tot+=wi*0.5*2*Lfun(F,T*v*v)
    return tot
def integrals(F,G,EF,EpF):
    def In(U):
        Vh=min(U,V0)
        return sqrt(U+Vh)*I_F(F,(U+Vh)/(1+U))/(1+U-Vh)
    def om(U): return 1-cc+4*cc*sqrt(G*(G+U))/U
    def Ph(U):
        Vh=min(U,V0); return G*(G+U)*EF/(U*U*sqrt(1+U-Vh))
    def Gf(U): return sqrt(1+U)*EpF
    def Nh(U): return min(Ph(U)/sqrt(3130), sqrt(Ph(U)*Gf(U)))
    # integrate over [0,1+2V0]; integrand ~ U^{-1/2} near 0 for J (In~sqrt(2U)*..., om~1/U) => In*om ~ U^{-1/2}; substitute U=t^2
    def quad(f,a,b,n=4000):
        # composite GL in t where U=t^2
        ta,tb=sqrt(a),sqrt(b); tot=0.0
        h=(tb-ta)/n
        for i in range(n):
            t0=ta+i*h
            for xi,wi in zip(X[:20],W[:20]) if False else zip(*gl(8)):
                t=t0+0.5*(xi+1)*h; tot+=wi*0.5*h*f(t*t)*2*t
        return tot
    J=quad(lambda U:In(U)*om(U),1e-14,1+2*V0)
    Y=quad(lambda U:In(U)*Nh(U),1e-14,1+2*V0)
    return J,Y
JI,YI=integrals(FI,1.0,12.15,4.908)
JX,YX=integrals(FX,2.7323,7.25,2.75)
print("J_I(1)=",JI," (claim <=8.133; record 8.1250)")
print("Y_I(1)=",YI," (claim <=10.301; record 10.2786)")
print("J_X(G*)=",JX," (claim <=17.951; record 17.9336)")
print("Y_X(G*)=",YX," (claim <=23.462; record 23.4221)")
tot=3*cc*(JI+cc*YI)+1.5*2.7323*0.8051*cc*(JX+cc*YX)
print("assembled:",tot)
