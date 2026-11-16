# S2b 검산 5: 보조정리 e-integral (4.1)·명제 4-6·(4.3)·정리 4-7의 수치 확인(작은 k)
import mpmath as mp
from itertools import permutations
from math import comb, factorial
mp.mp.dps=30
out=[]
def caps(sig):
    n=len(sig); h=[]
    for i in range(n):
        g=i+1
        for t in range(i-1,-1,-1):
            if sig[t]>sig[i]: g=i-t; break
        h.append(g)
    return h
def e_and_J(n,k):
    e=0;J=0
    for sig in permutations(range(1,n+1)):
        h=caps(sig); c=1;z=0;H=0;cz=1
        for g in h:
            if g<=k: c*=g
            else: z+=1
            if g<k: cz*=g
            elif g==k: H+=1
        e+=c*z*(z-1)*k**(z-2) if z>=2 else 0
        J+=cz*H*k**(H-1)*(k-1)**z if H>0 else 0
    return e,J
p=lambda m:(m+1)**(m-1)
def Bor(j): return mp.e**(-j)*mp.mpf(j)**(j-1)/mp.factorial(j)
def Bortail(k,Z): return 1-sum(mp.e**(-j*Z)*(j*Z)**(j-1)/mp.factorial(j) for j in range(1,k+1))
V=lambda x:(1-x)**2/2
def lagrange(g,n,R=0.5):
    # [x^n] g(T(x)) = (1/2pi i) oint g(Y)(1-Y)e^{nY} Y^{-n-1} dY on |Y|=R
    f=lambda th: g(R*mp.e**(1j*th))*(1-R*mp.e**(1j*th))*mp.e**(n*R*mp.e**(1j*th))*(R*mp.e**(1j*th))**(-n)
    return mp.re(mp.quad(f,[0,2*mp.pi]))/(2*mp.pi)
for k,ns in [(3,[4,5,6,7]),(4,[7,8,9])]:
    def Phi(Y):
        return mp.e**Y*mp.quad(lambda Z:(1-Z)**2*Bortail(k,Z)*mp.e**(k*(V(Z)-V(Y)))*(2*(V(Z)-V(Y))+k*(V(Z)-V(Y))**2),[0,Y])
    for n in ns:
        e,J=e_and_J(n,k)
        lhs=mp.mpf(e)/mp.factorial(n); rhs=lagrange(Phi,n)
        out.append(f"k={k} n={n}: e_n/n!={mp.nstr(lhs,12)} [x^n]Phi(T)={mp.nstr(rhs,12)} diff={mp.nstr(lhs-rhs,3)}")
        # 명제 4-6: J_n(k-1)/p_n = Bor(k) I_k M0^{(k-1,n)} + b_J  (n<=2k)
        if n<=2*k:
            eta=lambda v:-mp.log(1-v)-v-v**2/2
            Ik=mp.quad(lambda v: v/(1-v)*mp.e**(-v**2/2)*mp.e**(-k*eta(v)),[0,1])
            M0=mp.factorial(n)/p(n)*lagrange(lambda Y: mp.e**Y*mp.e**(-(k-1)*(1-Y)**2/2),n)
            Kf=lambda Y: -Bor(k)*mp.e**Y*mp.e**(-(k-1)*V(Y))*mp.quad(lambda Z:(1-Z)*Z**(k-1)*mp.e**(k*(1-Z)+(k-1)*V(Z)),[Y,1])
            bJ=mp.factorial(n)/p(n)*lagrange(Kf,n)
            out.append(f"   J_n(k-1)/p_n={mp.nstr(mp.mpf(J)/p(n),12)} vs Bor I M0+bJ={mp.nstr(Bor(k)*Ik*M0+bJ,12)}")
            # (4.3): A_{k,n} via Wi and M_r
            Wi=[mp.quad(lambda v: mp.e**(k*v**2/2)*v**2*Bortail(k,1-v)*(v**2/2)**j,[0,1]) for j in range(3)]
            Mr=[mp.factorial(n)/p(n)*lagrange(lambda Y,r=r: mp.e**Y*mp.e**(-k*(1-Y)**2/2)*(1-Y)**r,n) for r in (0,2,4)]
            A43=(2*Wi[1]+k*Wi[2])*Mr[0]-(Wi[0]+k*Wi[1])*Mr[1]+mp.mpf(k)/4*Wi[0]*Mr[2]
            Phiaux=lambda Y: mp.e**Y*mp.quad(lambda Z:(1-Z)**2*Bortail(k,Z)*mp.e**(k*(V(Z)-V(Y)))*(2*(V(Z)-V(Y))+k*(V(Z)-V(Y))**2),[0,1])
            Adir=mp.factorial(n)/p(n)*lagrange(Phiaux,n)
            out.append(f"   (4.3) A={mp.nstr(A43,12)} direct={mp.nstr(Adir,12)}")
# 정리 4-7 numeric check for moderate k
for k in [5,20,100,400]:
    eta=lambda v:-mp.log(1-v)-v-v**2/2
    Ik=mp.quad(lambda v: v/(1-v)*mp.e**(-v**2/2)*mp.e**(-k*eta(v)),[0,1])
    Wi=[mp.quad(lambda v: mp.e**(k*v**2/2)*v**2*Bortail(k,1-v)*(v**2/2)**j,[0,1]) for j in range(3)]
    a0=mp.quad(lambda w: mp.e**(-w**3/3),[0,mp.inf]); a1=mp.quad(lambda w: w*mp.e**(-w**3/3),[0,mp.inf])
    for om in [0,mp.mpf(699)/100,10]:
        R=k*Wi[2]+om*Wi[1]-Bor(k)*Ik
        lhs=k*R/Bor(k); rhs=om-mp.mpf(7)/2-(4*om+mp.mpf(1)/2)*a0*k**(-mp.mpf(1)/3)-mp.mpf(13)/2*om*a1*k**(-mp.mpf(2)/3)-12*om/k
        out.append(f"4-7 k={k} omega={mp.nstr(om,4)}: kR/Bor={mp.nstr(lhs,8)} >= bound {mp.nstr(rhs,8)} ? {lhs>=rhs}")
# borel-tail-arc first/second pieces
for k in [10,100,1000,5000]:
    tail=1-sum(Bor(j) for j in range(1,k+1)); c=(2*mp.pi)**-0.5; eps=mp.mpf(k)**-0.5
    d1=2*c*eps-tail
    s2=sum(j*Bor(j) for j in range(1,k+1)); d2=s2-(2*c*mp.sqrt(k)-mp.mpf(2)/3)
    out.append(f"tail k={k}: 2c eps - tail = {mp.nstr(d1,6)} in [0,{mp.nstr(mp.mpf(5)/9*c*eps**3,6)}]? ; sum jBor - (2c sqrt k - 2/3) = {mp.nstr(d2,6)} in [0,{mp.nstr(mp.mpf(2)/3*c*eps,6)}]?")
    # Robbins: 0 <= c j^-3/2 - Bor(j) <= c j^-5/2 /12
    mx=max((c*mp.mpf(j)**-1.5-Bor(j))/(c*mp.mpf(j)**-2.5/12) for j in range(1,k+1)); mn=min(c*mp.mpf(j)**-1.5-Bor(j) for j in range(1,k+1))
    out.append(f"   Robbins ratio max={mp.nstr(mx,5)} min diff={mp.nstr(mn,3)}")
open("C:/math/임시/주차함수_증명/대조v2/수학검사2/_S2b_5_out.txt","w",encoding="utf-8").write("\n".join(out))
print("\n".join(out))
