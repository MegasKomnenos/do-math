# -*- coding: utf-8 -*-
"""X1 G2·G3 검산: 두 변수 생성함수 F_{n,k}(u,z)와 닫힌 해 e^R/(1-z∫e^R),
K=F(k,z), A_{n,k-1}=F(k,k), J_n=∂_uF(k,z), B_{n,k-1}=F(k,k-1)-F(k-1,k-1),
유한 교대 항등식, H_k<=floor(n/k), k=2의 B EGF(G3), 2.8의 닫힌 꼴, 7.22의 표시 닫힌 꼴, 2.30(나)의 Green 표현 범위."""
import itertools, sympy as sp
from math import comb, factorial
u,z,x,phi=sp.symbols('u z x phi')
out=[]
def log(s): out.append(s); print(s)

def capacities(sigma):
    n=len(sigma); h=[]
    for i in range(n):
        j=i-1
        while j>=0 and sigma[j]<sigma[i]: j-=1
        h.append(i-j)
    return h
def p(n): return (n+1)**(n-1) if n>=1 else 1

NMAX=7
# 순열 쪽 열거 (용량 벡터만 저장)
caps={n:[capacities(s) for s in itertools.permutations(range(1,n+1))] for n in range(0,NMAX+1)}

def F_enum(n,k):
    s=0
    for h in caps[n]:
        term=1; H=0; Z=0
        for hi in h:
            if hi<k: term*=hi
            elif hi==k: H+=1
            else: Z+=1
        s+=term*u**H*z**Z
    return sp.expand(s)

def ser_int(f,N): return sp.integrate(f,x)  # 다항식 적분(상수 0)
def trunc(f,N): return sp.series(sp.expand(f),x,0,N+1).removeO()

def F_closed(k,N):
    C=sum((j+1-z)*p(j)*x**j/sp.factorial(j) for j in range(0,k-1))+(u-z)*p(k-1)*x**(k-1)/sp.factorial(k-1)
    R=sp.integrate(C,x)
    eR=trunc(sp.exp(R),N)
    I=sp.integrate(eR,x)
    F=trunc(eR*trunc(1/(1-z*I),N),N)
    return sp.expand(F)

for k in (2,3):
    Fc=F_closed(k,NMAX)
    allok=True
    for n in range(0,NMAX+1):
        lhs=F_enum(n,k); rhs=sp.expand(Fc.coeff(x,n)*sp.factorial(n))
        if sp.expand(lhs-rhs)!=0: allok=False; log(f"  불일치 n={n},k={k}: {lhs} vs {rhs}")
    log(f"[G2 닫힌 해] k={k}, n<=7: F_{{n,k}}(u,z) == n![x^n] e^R/(1-z∫e^R) : {allok}")
    # 특수화
    okK=okA=okJ=okB=okAlt=okH=True
    for n in range(1,NMAX+1):
        Fn=F_enum(n,k)
        # A_{n,k-1}=sum prod min(h,k); A_{n,k-2}
        A1=sum(sp.prod([min(h,k) for h in hh]) for hh in caps[n])
        A2=sum(sp.prod([min(h,k-1) for h in hh]) for hh in caps[n])
        if Fn.subs({u:k,z:k})!=A1: okA=False
        if Fn.subs({u:k-1,z:k-1})!=A2: okA=False
        # J_n(z) 정의
        J=0
        for hh in caps[n]:
            H=sum(1 for h in hh if h==k); Z=sum(1 for h in hh if h>k)
            pr=sp.prod([h for h in hh if h<k])
            J+=H*k**(H-1)*z**Z*pr if H>0 else 0
        Jd=sp.expand(sp.diff(Fn,u).subs(u,k))
        if sp.expand(J-Jd)!=0: okJ=False
        # B 직접(2.30 첫 식)과 F(k,k-1)-F(k-1,k-1)
        B=0
        for hh in caps[n]:
            H=sum(1 for h in hh if h==k); Z=sum(1 for h in hh if h>k)
            pr=sp.prod([h for h in hh if h<k])
            B+=pr*(k-1)**Z*(k**H-(k-1)**H)
        if Fn.subs({u:k,z:k-1})-Fn.subs({u:k-1,z:k-1})!=B: okB=False
        # 교대 항등식
        alt=sum(sp.Rational((-1)**(r-1),factorial(r))*sp.diff(Fn,u,r).subs({u:k,z:k-1}) for r in range(1,n//k+1))
        if sp.expand(alt-B)!=0: okAlt=False
        if sp.degree(Fn,u)>n//k: okH=False
    log(f"  k={k}: A_{{n,k-1}}=F(k,k), A_{{n,k-2}}=F(k-1,k-1): {okA}; J_n(z)=∂_uF(k,z): {okJ}; B=F(k,k-1)-F(k-1,k-1)(2.30 첫 식): {okB}; B=Σ_r(-1)^{{r-1}}/r! ∂_u^rF(k,k-1), r<=floor(n/k): {okAlt}; deg_u F<=floor(n/k): {okH}")

# B_{n,k-1}을 주차함수 직접 열거로 (k=2,3; n<=6): 정의 '최대 변위 k-1, 그 값을 내는 모든 차의 자리에서 h_i=k'
def park(pref):
    n=len(pref); spots=[0]*n; pos=[0]*n
    for car,a in enumerate(pref,1):
        s=a
        while s<=n and spots[s-1]!=0: s+=1
        if s>n: return None
        spots[s-1]=car; pos[car-1]=s
    return spots,pos
for k in (2,3):
    ok=True
    for n in range(1,7):
        Bcnt=0
        for pref in itertools.product(range(1,n+1),repeat=n):
            r=park(pref)
            if r is None: continue
            spots,pos=r
            disp=[pos[c]-pref[c] for c in range(n)]
            M=max(disp)
            if M!=k-1: continue
            h=capacities(spots)
            if all(h[pos[c]-1]==k for c in range(n) if disp[c]==M): Bcnt+=1
        Fn=F_enum(n,k)
        if Fn.subs({u:k,z:k-1})-Fn.subs({u:k-1,z:k-1})!=Bcnt: ok=False; log(f"  B 불일치 n={n} k={k}: {Bcnt}")
    log(f"[B 직접 열거] k={k}, n<=6: 막힌 주차함수 수 == F(k,k-1)-F(k-1,k-1): {ok}")

# G3: k=2의 EGF: sum B_{n,1} x^n/n! == e^{x^2/2}/(1-∫e^{t^2/2}) - 1/(1-x)
N=7
eR=trunc(sp.exp(x**2/2),N); G=trunc(eR*trunc(1/(1-sp.integrate(eR,x)),N),N)-trunc(1/(1-x),N)
Bvals=[sp.expand(G.coeff(x,n)*sp.factorial(n)) for n in range(N+1)]
Benum=[F_enum(n,2).subs({u:2,z:1})-F_enum(n,2).subs({u:1,z:1}) for n in range(N+1)]
log(f"[G3 k=2 예] B_{{n,1}} (n=0..7) 닫힌 EGF: {Bvals} ; 열거: {Benum} ; 일치 {Bvals==Benum}")

# 2.8: A_l(x)=e^{-Q_l}/(1-(l+1)∫e^{-Q_l}) == F_{l+1}(l+1,l+1)
for l in (1,2,3):
    k=l+1
    Q=sum((l-j)*p(j)*x**(j+1)/sp.factorial(j+1) for j in range(0,l))
    eQ=trunc(sp.exp(-Q),N); A=trunc(eQ*trunc(1/(1-(l+1)*sp.integrate(eQ,x)),N),N)
    Fc=F_closed(k,N).subs({u:k,z:k})
    log(f"[2.8 = G1(라)] l={l}: e^-Q/(1-(l+1)∫e^-Q) == F_{{l+1}}(l+1,l+1): {sp.expand(A-Fc)==0}")

# 7.22: w_t=min(t,k) phi^{[t=z0]}, z0>=k-1: N_phi = Ex_phi/(1-k∫Ex_phi), Ex_phi=e^{-Q_{k-1}} e^{(phi-1) O_{z0}}
def N_enum(n,k,z0):
    s=0
    for hh in caps[n]:
        term=1; e=0
        for h in hh:
            term*=min(h,k)
            if h==z0: e+=1
        s+=term*phi**e
    return sp.expand(s)
for (k,z0) in ((2,3),(3,2),(3,4),(3,1)):
    l=k-1
    Q=sum((l-j)*p(j)*x**(j+1)/sp.factorial(j+1) for j in range(0,l))
    # a_{z0-1}=A_{z0-1,k-1}/(z0-1)!
    a=sp.Rational(sum(sp.prod([min(h,k) for h in hh]) for hh in caps[z0-1]),factorial(z0-1))
    O=sp.Rational(min(z0,k),z0)*a*x**z0
    Ex=trunc(sp.exp(-Q+(phi-1)*O),N)
    Nc=trunc(Ex*trunc(1/(1-k*sp.integrate(Ex,x)),N),N)
    mism=[n for n in range(0,N+1) if sp.expand(Nc.coeff(x,n)*sp.factorial(n)-N_enum(n,k,z0))!=0]
    log(f"[7.22 = G1(라) 표시판] k={k}, z0={z0}: 일치하지 않는 n = {mism} (z0<k-1이면 어긋나야 함; 원고의 반례 (3,1,2))")

# 2.30(나) Green 표현: J_n(z) vs p_{k-1} n![x^n] e^T e^{zGr}∫e^{-zGr} s^{k-1}/(k-1)!  (n<=2k 등호, 그 뒤 상계 J<=J^G for 0<=z<=k+1)
T=sum(sp.Integer(t)**(t-1)*x**t/sp.factorial(t) for t in range(1,N+2))
Gr=trunc(T-T**2/2,N+1)
for k in (2,3):
    eT=trunc(sp.exp(T),N); ezG=trunc(sp.exp(z*Gr),N); emzG=trunc(sp.exp(-z*Gr),N)
    inner=sp.integrate(trunc(emzG*x**(k-1)/sp.factorial(k-1),N),x)
    JG=trunc(p(k-1)*eT*ezG*inner,N)
    res=[]
    for n in range(0,N+1):
        Jn=sp.expand(sp.diff(F_enum(n,k),u).subs(u,k)); JGn=sp.expand(JG.coeff(x,n)*sp.factorial(n))
        eq=sp.expand(Jn-JGn)==0
        diff=sp.expand(JGn-Jn)
        signs=[sp.sign(diff.subs(z,zz)) for zz in (0,sp.Rational(1,2),k-1,k,k+1)]
        res.append((n,eq,diff if not eq else 0,signs))
    log(f"[2.30(나)/7.41] k={k}: (n, J==J^G, J^G-J, 부호 at z=0,1/2,k-1,k,k+1) = {res}")
    # 정확 J의 모든 n 공식: ∂_u F 닫힌 해 — F_closed의 u-미분 계수와 J_n 비교
    Fc=F_closed(k,N); Jc=sp.diff(Fc,u).subs(u,k)
    ok=all(sp.expand(Jc.coeff(x,n)*sp.factorial(n)-sp.diff(F_enum(n,k),u).subs(u,k))==0 for n in range(N+1))
    log(f"  정확 J_n(z)=n![x^n]∂_u(e^R/(1-z∫e^R))|_{{u=k}} 모든 n<=7: {ok}")

open("심사_X1_G2_두변수_out.txt","w",encoding="utf-8").write("\n".join(out)+"\n")
