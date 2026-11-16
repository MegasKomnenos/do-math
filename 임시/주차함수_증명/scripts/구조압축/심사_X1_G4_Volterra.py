# -*- coding: utf-8 -*-
"""X1 G4·G5 검산(정확 유리수, z를 여러 유리수에 넣어 다항식 항등식을 확인):
D=∑K_{n,k}(z)x^n/n!, 연쇄 해 G_*(4.6의 F_*), X=D-G_*, δ=z∫(D-E_<k)-T_>k 에 대해
X = e^T(z∫X+e^δ-1-δ) 정확; X=O(x^{2k+2}); (7.7) mod x^{3k+3}; 4.6 1–3단계 ≡ 5.5(가) 꼴 ≡ D mod x^{2k+2};
7.40(가) 지수 공식; J(정확, ∂_u)≡Green 해 mod x^{2k+1}; 두 변수 Riccati."""
from fractions import Fraction as Fr
from math import factorial, comb
out=[]
def log(s): out.append(s); print(s)
def p(n): return (n+1)**(n-1) if n>=1 else 1
# 급수: 리스트 c[0..N] (x^n 계수)
def S_add(a,b): return [x+y for x,y in zip(a,b)]
def S_sub(a,b): return [x-y for x,y in zip(a,b)]
def S_scale(a,s): return [s*x for x in a]
def S_mul(a,b):
    N=len(a)-1; c=[Fr(0)]*(N+1)
    for i,x in enumerate(a):
        if x==0: continue
        for j in range(N+1-i): c[i+j]+=x*b[j]
    return c
def S_int(a):
    N=len(a)-1; c=[Fr(0)]*(N+1)
    for i in range(N): c[i+1]=a[i]/(i+1)
    return c
def S_diff(a):
    N=len(a)-1; c=[Fr(0)]*(N+1)
    for i in range(1,N+1): c[i-1]=i*a[i]
    return c
def S_exp(c):
    N=len(c)-1; e=[Fr(0)]*(N+1); e[0]=Fr(1); d=S_diff(c)
    for n in range(1,N+1):
        s=Fr(0)
        for j in range(n): s+=d[j]*e[n-1-j]   # e'=c'e
        e[n]=s/n
    return e
def S_inv(a):  # 1/a, a[0]!=0
    N=len(a)-1; b=[Fr(0)]*(N+1); b[0]=1/a[0]
    for n in range(1,N+1):
        s=sum(a[i]*b[n-i] for i in range(1,n+1)); b[n]=-s/a[0]
    return b
def low(a):
    for i,x in enumerate(a):
        if x!=0: return i
    return None
def iszero_upto(a,M): return all(x==0 for x in a[:M+1])

ZVALS=[Fr(i,3) for i in range(1,25)]+[Fr(-2,7),Fr(5,2)]   # 26개 값: 계수 다항식 차수 <= N=16 를 넘음
for k in (2,3):
    N=4*k+4
    T=[Fr(0)]+[Fr(t**(t-1),factorial(t)) for t in range(1,N+1)]
    Tle=[Fr(0)]*(N+1); 
    for t in range(1,k+1): Tle[t]=T[t]
    Tgt=S_sub(T,Tle)
    E=[Fr(0)]*(N+1)
    for j in range(k): E[j]=Fr(p(j),factorial(j))
    eT=S_exp(T); eTle=S_exp(Tle)
    one=[Fr(1)]+[Fr(0)]*N
    Q=S_mul(S_sub(one,T),S_sub(eT,E))
    Gr=S_sub(T,S_scale(S_mul(T,T),Fr(1,2)))
    F0=eTle
    res={'740a':True,'delta':True,'ident':True,'low':set(),'77':True,'77b':True,'46':True,'46b':True,'55':True,'55b':True,'EQ':True,'Q':True,'GS':True,'GSb':True,'J':True,'Jlow':set(),'ric':True}
    Jlowcoef=set()
    for zv in ZVALS:
        # K_n(z) 재귀 (G1(나)), w_t=t(t<=k), z(t>k)
        W=lambda t: Fr(t) if t<=k else zv
        K=[Fr(1)]
        for n in range(1,N+1):
            K.append(sum(comb(n-1,j)*W(j+1)*K[j]*K[n-1-j] for j in range(n)))
        D=[K[n]/factorial(n) for n in range(N+1)]
        ezG=S_exp(S_scale(Gr,zv)); emzG=S_exp(S_scale(Gr,-zv))
        SG=S_mul(ezG,S_int(S_mul(emzG,Q)))
        Gstar=S_add(S_add(E,Q),S_scale(S_mul(eT,SG),zv))
        # 7.40(가)
        rhs=S_exp(S_add(Tle,S_scale(S_int(S_sub(D,E)),zv)))
        if not iszero_upto(S_sub(D,rhs),N): res['740a']=False
        X=S_sub(D,Gstar)
        delta=S_sub(S_scale(S_int(S_sub(D,E)),zv),Tgt)
        bd=[Fr(0)]*(N+1)
        for t in range(k+1,N+1): bd[t]=(zv*K[t-1]-Fr(t**(t-1)))/factorial(t)
        if not iszero_upto(S_sub(delta,bd),N): res['delta']=False
        ed=S_exp(delta)
        inner=S_add(S_scale(S_int(X),zv),S_sub(S_sub(ed,one),delta))
        if not iszero_upto(S_sub(X,S_mul(eT,inner)),N): res['ident']=False
        res['low'].add(low(X))
        r77=S_sub(X,S_mul(eTle,S_add(S_scale(S_int(X),zv),S_scale(S_mul(bd,bd),Fr(1,2)))))
        if not iszero_upto(r77,3*k+2): res['77']=False
        if iszero_upto(r77,3*k+3): res['77b']=False   # 3k+3 차수에서는 일반적으로 어긋나야 함(참이면 기록)
        if not iszero_upto(X,2*k+1): res['46']=False
        if iszero_upto(X,2*k+2): res['46b']=False
        S55=S_add(F0,S_scale(S_mul(eT,S_mul(ezG,S_int(S_mul(emzG,S_sub(F0,E))))),zv))
        if not iszero_upto(S_sub(D,S55),2*k+1): res['55']=False
        if iszero_upto(S_sub(D,S55),2*k+2): res['55b']=False
        if not iszero_upto(S_sub(S_add(E,Q),F0),2*k+1): res['EQ']=False
        if not iszero_upto(S_sub(Q,S_sub(F0,E)),2*k+1): res['Q']=False
        if not iszero_upto(S_sub(Gstar,S55),2*k+1): res['GS']=False
        if iszero_upto(S_sub(Gstar,S55),2*k+2): res['GSb']=False
        # J: 두 변수 재귀의 u-미분을 수치 미분 대신 u에 대한 선형성으로: K_n(u,z)는 u의 다항식 — 차분으로 ∂_u 구하기 위해 u=k와 u=k+h 여러 점 보간 대신,
        # J_n = sum_sigma ... 는 u-다항식 차수<=n//k; 여기서는 u에 Fraction 값 k+1, k+2, ..., 를 넣고 Lagrange 보간으로 도함수를 구한다.
        def Ku(uv):
            Wu=lambda t: Fr(t) if t<k else (uv if t==k else zv)
            L=[Fr(1)]
            for n in range(1,N+1):
                L.append(sum(comb(n-1,j)*Wu(j+1)*L[j]*L[n-1-j] for j in range(n)))
            return L
        m=N//k+1  # 차수 상계
        pts=[Fr(k)+Fr(i) for i in range(0,m+1)]
        vals=[Ku(uv) for uv in pts]
        # 각 n에 대해 다항식 보간 후 u=k에서 도함수: 유한차분 Newton 형식
        Jn=[]
        for n in range(N+1):
            ys=[v[n] for v in vals]
            # Newton 전진 차분 계수
            coef=[]; tbl=ys[:]
            for i in range(len(ys)):
                coef.append(tbl[0]); tbl=[tbl[j+1]-tbl[j] for j in range(len(tbl)-1)]
            # p(u)=sum coef[i]*C(u-k,i) (step 1) → p'(k)=sum_{i>=1} coef[i]*(-1)^{i-1}/i
            Jn.append(sum(coef[i]*Fr((-1)**(i-1),i) for i in range(1,len(coef))))
        J=[Jn[n]/factorial(n) for n in range(N+1)]
        Y=S_scale(S_mul(eT,S_mul(ezG,S_int(S_mul(emzG,[Fr(1,factorial(k-1)) if i==k-1 else Fr(0) for i in range(N+1)])))),Fr(p(k-1)))
        dJ=S_sub(Y,J)
        if not iszero_upto(dJ,2*k): res['J']=False
        res['Jlow'].add(low(dJ)); Jlowcoef.add(dJ[2*k+1]*factorial(2*k+1) if low(dJ)==2*k+1 else None)
        # Riccati 확인 (u=k+1 한 점)
        Fu=[vals[1][n]/factorial(n) for n in range(N+1)]; uv=pts[1]
        C=[Fr(0)]*(N+1)
        for j in range(k-1): C[j]=(j+1-zv)*Fr(p(j),factorial(j))
        C[k-1]+=(uv-zv)*Fr(p(k-1),factorial(k-1))
        ode=S_sub(S_diff(Fu),S_add(S_scale(S_mul(Fu,Fu),zv),S_mul(C,Fu)))
        if not iszero_upto(ode,N-1): res['ric']=False
    log(f"[k={k}, N={N}, z 값 {len(ZVALS)}개] 7.40(가) D=exp(T_<=k+z∫(D-E)): {res['740a']}; δ==bd: {res['delta']}")
    log(f"  [G4] X == e^T(z∫X+e^δ-1-δ) (mod x^{N+1}): {res['ident']}; X 최저 차수 {res['low']} (주장 2k+2={2*k+2})")
    log(f"  (7.7) mod x^{3*k+3}: {res['77']}; mod x^{3*k+4}에서는 어긋남: {res['77b']}")
    log(f"  [4.6 1–3단계] D≡G_* mod x^{2*k+2}: {res['46']}; mod x^{2*k+3}에서는 어긋남: {res['46b']}")
    log(f"  [5.5(가) 꼴] D≡F_0+z e^T e^{{zGr}}∫e^{{-zGr}}(F_0-E) mod x^{2*k+2}: {res['55']}; mod x^{2*k+3} 어긋남: {res['55b']}; E+Q≡F_0: {res['EQ']}; Q≡F_0-E: {res['Q']}; G_*≡5.5꼴 mod x^{2*k+2}: {res['GS']}; mod x^{2*k+3} 어긋남: {res['GSb']}")
    log(f"  [2.30(나)·7.41] J≡Green 해 mod x^{2*k+1}: {res['J']}; (J^G-J) 최저 차수 {res['Jlow']} (주장 2k+1={2*k+1}); 그 계수(n!배, z별 값 집합의 크기 {len([c for c in Jlowcoef if c is not None])})")
    log(f"  두 변수 Riccati F'=zF^2+C_kF: {res['ric']}")
open("심사_X1_G4_Volterra_out.txt","w",encoding="utf-8").write("\n".join(out)+"\n")
