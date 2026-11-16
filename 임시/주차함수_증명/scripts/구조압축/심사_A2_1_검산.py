# 심사 A2 검산 1: G4(Volterra 잔차 항등식)·G5(4.6 선형화 = 연쇄 해)·C9(용량 이동 비 일반형)·D4·3.6 수치
from fractions import Fraction as Fr
from math import comb, factorial
import sys

def series_mul(a,b,N):
    c=[Fr(0)]*(N+1)
    for i,ai in enumerate(a):
        if ai==0: continue
        for j in range(0,N+1-i):
            c[i+j]+=ai*b[j]
    return c
def series_exp(a,N):  # a[0]==0
    assert a[0]==0
    e=[Fr(0)]*(N+1); e[0]=Fr(1)
    # e' = a' e
    da=[(i+1)*a[i+1] for i in range(N)]+[Fr(0)]
    for n in range(1,N+1):
        s=Fr(0)
        for j in range(0,n):
            s+=da[j]*e[n-1-j]
        e[n]=s/n
    return e
def series_int(a,N):
    r=[Fr(0)]*(N+1)
    for i in range(N):
        r[i+1]=a[i]/(i+1)
    return r
def lowest(a):
    for i,x in enumerate(a):
        if x!=0: return i
    return None

def K_table(k,y,Nmax):
    # 얼린 용량 다항식 재귀(4.6 첫째 단계): K_n = sum_j C(n-1,j) W(j+1) K_j K_{n-1-j}
    W=lambda g: Fr(g) if g<=k else y
    K=[Fr(1)]
    for n in range(1,Nmax+1):
        s=Fr(0)
        for j in range(n):
            s+=comb(n-1,j)*W(j+1)*K[j]*K[n-1-j]
        K.append(s)
    return K

def check_G4_G5(k,y):
    N=3*k+4
    p=[Fr((n+1)**(n-1)) if n>=1 else Fr(1) for n in range(N+1)]
    T=[Fr(0)]+[Fr(t**(t-1),factorial(t)) for t in range(1,N+1)]
    B=series_exp(T,N)                         # e^T
    for n in range(N+1): assert B[n]==p[n]/factorial(n)
    E=[p[j]/factorial(j) if j<k else Fr(0) for j in range(N+1)]   # E_{<k}
    Tle=[T[t] if t<=k else Fr(0) for t in range(N+1)]
    Tgt=[T[t] if t>k else Fr(0) for t in range(N+1)]
    K=K_table(k,y,N)
    D=[K[n]/factorial(n) for n in range(N+1)]
    # (7.6) D = exp(T_{<=k} + y∫(D−E))
    DmE=[D[i]-E[i] for i in range(N+1)]
    delta=[y*v-Tgt[i] for i,v in enumerate(series_int(DmE,N))]
    assert delta[0]==0
    lhs=series_mul(B,series_exp(delta,N),N)
    assert lhs==D, "D = B e^delta 실패"
    assert lowest(delta)==k+1
    # 연쇄 해 G = B(1 − T_{>k} + y∫(G−E)) — 고정점 반복(적분이 차수를 올리므로 N번이면 수렴)
    G=[Fr(0)]*(N+1)
    for _ in range(N+2):
        inner=[Fr(1 if i==0 else 0)-Tgt[i]+y*v for i,v in enumerate(series_int([G[i]-E[i] for i in range(N+1)],N))]
        G=series_mul(B,inner,N)
    X=[D[i]-G[i] for i in range(N+1)]
    # F1 §4 항등식: X = B(y∫X + e^δ − 1 − δ)
    ed=series_exp(delta,N)
    rhs_in=[y*v+ed[i]-(1 if i==0 else 0)-delta[i] for i,v in enumerate(series_int(X,N))]
    assert series_mul(B,rhs_in,N)==X, "Volterra 잔차 항등식 실패"
    lo=lowest(X)
    # (7.7) mod x^{3k+3}: X ≡ e^{T_{<=k}}(y∫X + δ²/2)
    eTle=series_exp(Tle,N)
    d2=series_mul(delta,delta,N)
    r77=series_mul(eTle,[y*v+d2[i]/2 for i,v in enumerate(series_int(X,N))],N)
    ok77=all(r77[i]==X[i] for i in range(3*k+3))
    # 4.6 둘째·셋째 단계: F_y ≡ G mod x^{2k+2}
    ok46=all(D[i]==G[i] for i in range(2*k+2))
    return lo, ok77, ok46, (D[2*k+2]!=G[2*k+2])

print("== G4/G5: k, y, X 최저 차수(기대 2k+2), (7.7) mod x^{3k+3}, F_y≡G mod x^{2k+2}, 차수 2k+2에서 실제로 다름")
for k in (2,3,4,5):
    for y in (Fr(1),Fr(3,2),Fr(k),Fr(k)+Fr(1,3)):
        lo,ok77,ok46,diff=check_G4_G5(k,y)
        print(k, y, lo, ok77, ok46, diff)
        assert lo==2*k+2 and ok77 and ok46

# C9: A_{N,r-1}/A_{N,s-1} ≥ prod_{i≤N} min(i,r)/min(i,s) (모든 N), 마지막 차 재귀로 A 계산
def A_table(ell,Nmax):
    A=[1]
    for n in range(1,Nmax+1):
        A.append(sum(comb(n-1,j)*min(j+1,ell+1)*A[j]*A[n-1-j] for j in range(n)))
    return A
print("== C9: 모든 1≤r<s≤12, N≤60에서 A_{N,r-1}/A_{N,s-1} ≥ ∏min(i,r)/min(i,s)")
Nmax=60
tabs={ell:A_table(ell,Nmax) for ell in range(0,12)}
worst=None
for r in range(1,12):
    for s in range(r+1,13):
        Ar=tabs[r-1]; As=tabs[s-1]
        for Nn in range(0,Nmax+1):
            lhs=Fr(Ar[Nn],As[Nn])
            rhs=Fr(1)
            for i in range(1,Nn+1): rhs*=Fr(min(i,r),min(i,s))
            assert lhs>=rhs,(r,s,Nn)
            if Nn>=s:  # 8.24(가)의 꼴 (1-1/k)^{N-k+1}, r=k-1,s=k
                pass
            ratio=lhs/rhs
            if worst is None or ratio<worst[0]: worst=(ratio,r,s,Nn)
print("통과; 가장 빠듯한 비 lhs/rhs =", float(worst[0]), "at (r,s,N)=",worst[1:])
# 8.24(가) 꼴: N>2k-1에서도 (1-1/k)^{N-k+1}가 성립하는지
print("== 8.24(가) 꼴 s_N(k-1)/s_N(k) ≥ (1-1/k)^{N-k+1}, k=2..6, N≤60 (N>2k-1 포함)")
for k in range(2,7):
    Ak1=tabs[k-2]; Ak=tabs[k-1]
    bad=[Nn for Nn in range(k,Nmax+1) if Fr(Ak1[Nn],Ak[Nn])<Fr(k-1,k)**(Nn-k+1)]
    print(k, "위반 N:", bad)

# D4: 4.9(가)
import math
print("== D4: 4√2(1-26/k) at k=10000:", 4*math.sqrt(2)*(1-26/10000), " at 30000:", 4*math.sqrt(2)*(1-26/30000), " 11/2=5.5 < 5.642")
# 4.5 k≥10000 조립 수치
print("== 4.5 조립: 5.642*1.6809*0.39893-0.0163-3.554 =", 5.642*1.6809*0.39893-0.0163-3.554)
# 3.6 수치
lam=Fr(751,1000)
s1=lam**8; s2=sum(i*lam**(i-1) for i in range(1,9)); s3=sum((i-1)*lam**(i-1) for i in range(1,9))
print("== 3.6: lam^8=",float(s1)," sum i lam^{i-1}=",float(s2)," sum (i-1)lam^{i-1}=",float(s3)," total=",float(s1+s2/31+s3/1000))
# 3.6: E_n omega_n for n=1..5 (정확)
def Eomega(n):
    pn=(n+1)**(n-1) if n>=1 else 1
    return sum(Fr(comb(n,j)*j**j*((n-j+1)**(n-j-1) if n-j>=1 else 1),pn) for j in range(1,n//2+1))  # j*pi_n(j)=C(n,j) j^j p_{n-j}/p_n
print("== 3.6: E_n omega_n, n=1..5:", [str(Eomega(n)) for n in range(1,6)])
